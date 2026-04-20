#!/usr/bin/env python3
"""摄取原始资料到 wiki/sources/。"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ensure_utf8_stdout() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    _ensure_utf8_stdout()
    inbox_dir = ROOT / "raw" / "inbox"
    processed_dir = ROOT / "raw" / "processed"
    sources_dir = ROOT / "wiki" / "sources"
    template_path = ROOT / "templates" / "source.md"
    index_path = ROOT / "wiki" / "index.md"
    log_path = ROOT / "wiki" / "log.md"

    required = [inbox_dir, processed_dir, sources_dir, template_path, index_path, log_path]
    for p in required:
        if not p.exists():
            print(f"缺少必要路径: {p.relative_to(ROOT)}", file=sys.stderr)
            return 1

    candidates = sorted([f for f in inbox_dir.iterdir() if f.is_file()], key=lambda x: x.name)
    if not candidates:
        print("raw/inbox 中没有可处理文件。")
        return 0

    candidate = candidates[0]

    existing = list(sources_dir.glob("source-*.md"))
    max_id = 0
    for f in existing:
        m = re.match(r"^source-(\d+)$", f.stem)
        if m:
            max_id = max(max_id, int(m.group(1)))

    next_id = max_id + 1
    source_id = f"source-{next_id:04d}"
    source_file = f"{source_id}.md"
    source_path = sources_dir / source_file

    title = candidate.stem
    template_content = template_path.read_text(encoding="utf-8").lstrip("\ufeff")

    template_content = re.sub(r"(?m)^#\s+来源模板\s*$", f"# {source_id}: {title}", template_content)
    template_content = re.sub(r"(?m)^- id:\s*$", f"- id: {source_id}", template_content)
    template_content = re.sub(r"(?m)^- title:\s*$", f"- title: {title}", template_content)
    template_content = re.sub(r"(?m)^- type:\s*.*$", "- type: note", template_content)
    today = datetime.now().strftime("%Y-%m-%d")
    template_content = re.sub(r"(?m)^- created_at:\s*$", f"- created_at: {today}", template_content)
    template_content = re.sub(r"(?m)^- accessed_at:\s*$", f"- accessed_at: {today}", template_content)
    template_content = re.sub(r"(?m)^- tags:\s*$", "- tags: [ingested]", template_content)

    source_path.write_text(template_content, encoding="utf-8")

    source_link = f"- [{source_id}](sources/{source_file})"
    index_content = index_path.read_text(encoding="utf-8")
    if source_link not in index_content:
        if re.search(r"(?m)^## 来源\s*$", index_content):
            index_content = re.sub(
                r"(?m)^## 来源\s*$",
                f"## 来源\n{source_link}",
                index_content,
                count=1,
            )
        else:
            index_content = index_content.rstrip() + f"\n\n## 来源\n{source_link}\n"
        index_path.write_text(index_content, encoding="utf-8")

    processed_path = processed_dir / candidate.name
    if processed_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        processed_path = processed_dir / f"{timestamp}-{candidate.name}"
    shutil.move(str(candidate), str(processed_path))

    log_line = f"- 摄取来源: [{source_id}](sources/{source_file})，源文件 `{candidate.name}`。\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line)

    print(f"已摄取: {candidate.name}")
    print(f"已创建: {source_path}")
    print(f"已移动到: {processed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
