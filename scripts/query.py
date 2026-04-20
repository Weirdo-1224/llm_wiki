#!/usr/bin/env python3
"""新建查询页。"""

import argparse
import re
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


def slugify(title: str) -> str:
    lowered = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    if not slug:
        slug = "untitled-query"
    return slug


def main() -> int:
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="新建查询页")
    parser.add_argument("--title", "-t", required=True, help="查询标题")
    args = parser.parse_args()

    template_path = ROOT / "templates" / "query.md"
    queries_dir = ROOT / "wiki" / "queries"
    index_path = ROOT / "wiki" / "index.md"
    log_path = ROOT / "wiki" / "log.md"

    if not template_path.exists():
        print(f"模板不存在: {template_path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if not queries_dir.exists():
        print(f"目录不存在: {queries_dir.relative_to(ROOT)}", file=sys.stderr)
        return 1

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(args.title)
    file_name = f"query-{stamp}-{slug}.md"
    target_path = queries_dir / file_name

    template_content = template_path.read_text(encoding="utf-8").lstrip("\ufeff")
    template_content = re.sub(r"(?m)^#\s+查询模板\s*$", f"# 查询: {args.title}", template_content)
    template_content = re.sub(r"(?m)^- id:\s*$", f"- id: query-{stamp}", template_content)
    template_content = re.sub(r"(?m)^- title:\s*$", f"- title: {args.title}", template_content)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_content = re.sub(r"(?m)^- created_at:\s*$", f"- created_at: {now_str}", template_content)

    target_path.write_text(template_content, encoding="utf-8")

    if index_path.exists():
        index_content = index_path.read_text(encoding="utf-8")
        link_line = f"- [{file_name}](queries/{file_name})"
        if re.search(r"(?m)^## 查询\s*$", index_content):
            index_content = re.sub(
                r"(?m)^## 查询\s*$",
                f"## 查询\n{link_line}",
                index_content,
                count=1,
            )
        else:
            index_content = index_content.rstrip() + f"\n\n## 查询\n{link_line}\n"
        index_path.write_text(index_content, encoding="utf-8")

    log_line = f"- 新建查询: [{file_name}](queries/{file_name})\n"
    if log_path.exists():
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line)

    print(f"已创建: {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
