from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "raw/inbox",
    "raw/processed",
    "raw/assets",
    "wiki/sources",
    "wiki/entities",
    "wiki/concepts",
    "wiki/syntheses",
    "wiki/queries",
    "scripts",
    "templates",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/overview.md",
    "templates/source.md",
    "templates/entity.md",
    "templates/concept.md",
    "templates/synthesis.md",
    "templates/query.md",
]

FORBIDDEN_HEADINGS = [
    r"^#{1,6}\s+Source Template\s*$",
    r"^#{1,6}\s+Query Template\s*$",
    r"^#{1,6}\s+Synthesis Template\s*$",
    r"^#{1,6}\s+Entity Template\s*$",
    r"^#{1,6}\s+Concept Template\s*$",
    r"^##\s+Metadata\s*$",
    r"^##\s+Summary\s*$",
    r"^##\s+Key Points\s*$",
    r"^##\s+Evidence\s*/\s*Quotes\s*$",
    r"^##\s+Linked Entities\s*$",
    r"^##\s+Linked Concepts\s*$",
    r"^##\s+Notes\s*$",
    r"^##\s+Question\s*$",
    r"^##\s+Why It Matters\s*$",
    r"^##\s+Hypotheses\s*$",
    r"^##\s+Required Evidence\s*$",
    r"^##\s+Progress Log\s*$",
    r"^##\s+Answer\s*\(when ready\)\s*$",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_md_links(content: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content)]


def is_chinese_present(text: str) -> bool:
    return re.search(r"[\u4e00-\u9fff]", text) is not None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_DIRS:
        if not (ROOT / rel).is_dir():
            errors.append(f"Missing directory: {rel}")

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"Missing file: {rel}")

    wiki_root = ROOT / "wiki"
    wiki_pages = list(wiki_root.rglob("*.md"))
    inbound: dict[Path, int] = {p.resolve(): 0 for p in wiki_pages}

    for page in wiki_pages:
        content = read_text(page)
        for target in iter_md_links(content):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"Broken link: {page} -> {target}")
                continue
            if resolved.suffix.lower() == ".md" and str(resolved).startswith(str(wiki_root.resolve())):
                inbound[resolved] = inbound.get(resolved, 0) + 1

    skip_orphan = {
        (ROOT / "wiki/index.md").resolve(),
        (ROOT / "wiki/log.md").resolve(),
        (ROOT / "wiki/overview.md").resolve(),
    }
    for page in wiki_pages:
        p = page.resolve()
        if p not in skip_orphan and inbound.get(p, 0) == 0:
            warnings.append(f"Orphan page: {page}")

    title_map: dict[str, list[Path]] = {}
    for page in wiki_pages:
        content = read_text(page)
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if not m:
            continue
        key = m.group(1).strip().lower()
        title_map.setdefault(key, []).append(page)
    for title, pages in title_map.items():
        if len(pages) > 1:
            warnings.append(f"Duplicate page title '{title}': {', '.join(str(p) for p in pages)}")

    for rel in ["wiki/entities", "wiki/concepts", "wiki/syntheses", "wiki/queries"]:
        folder = ROOT / rel
        if not folder.is_dir():
            continue
        for page in folder.glob("*.md"):
            content = read_text(page)
            if not re.search(r"\((\.\./)?sources/[^)]+\.md\)", content):
                warnings.append(f"Missing related source link: {page}")

    md_targets = [ROOT / "AGENTS.md", ROOT / "README.md"]
    md_targets.extend((ROOT / "wiki").rglob("*.md"))
    md_targets.extend((ROOT / "templates").rglob("*.md"))

    heading_patterns = [re.compile(p, re.MULTILINE) for p in FORBIDDEN_HEADINGS]
    for file in md_targets:
        content = read_text(file)
        for pat in heading_patterns:
            if pat.search(content):
                errors.append(f"Language policy failed (English headings): {file}")
                break
        stripped = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        if not is_chinese_present(stripped):
            errors.append(f"Language policy failed (no Chinese text): {file}")

    if errors:
        print("Lint failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    if warnings:
        print("Lint warnings:")
        for item in warnings:
            print(f"  - {item}")

    print("Lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

