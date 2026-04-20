#!/usr/bin/env python3
"""新建查询 + 调用 codex 回答 + lint。"""

import argparse
import subprocess
import sys
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
    parser = argparse.ArgumentParser(description="新建查询并沉淀回答")
    parser.add_argument("--title", "-t", required=True, help="查询标题")
    args = parser.parse_args()

    query_script = ROOT / "scripts" / "query.py"
    lint_script = ROOT / "scripts" / "lint_repo.py"

    if not query_script.exists():
        print("Missing script: scripts/query.py", file=sys.stderr)
        return 1
    if not lint_script.exists():
        print("Missing script: scripts/lint_repo.py", file=sys.stderr)
        return 1

    # 1) 创建查询页
    result = subprocess.run(
        [sys.executable, str(query_script), "--title", args.title],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        print("query.py failed", file=sys.stderr)
        return 1
    print(result.stdout, end="")

    # 2) 定位最新查询
    queries_dir = ROOT / "wiki" / "queries"
    query_files = sorted(
        [f for f in queries_dir.glob("query-*.md") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if not query_files:
        print("No new query file found.", file=sys.stderr)
        return 1

    latest = query_files[0]

    # 3) 调用 codex exec
    prompt = f"""Follow AGENTS.md strictly and complete answer-and-settle workflow:
1. Read wiki/index.md first.
2. Focus on this query file: {latest}
3. Answer the question and write the result to section '回答（完成后）'.
4. If needed, create or update a page in wiki/syntheses/ for reusable synthesis.
5. Update wiki/index.md and wiki/log.md.
6. All new/updated Markdown headings and body text must be Chinese; id/path/commands/code blocks may stay English.
7. Distinguish facts, interpretations, and open questions; if conflicting with older claims, add conflict/revision notes.
8. Output changed file list and next suggestions.
"""

    try:
        subprocess.run(["codex", "exec", prompt], cwd=ROOT, check=True)
    except FileNotFoundError:
        print(
            "codex exec failed: command not found. Please install and configure Codex CLI.",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as e:
        print(
            f"codex exec failed. Please fix local Codex config and retry. Original error: {e}",
            file=sys.stderr,
        )
        return 1

    # 4) 运行 lint
    lint_result = subprocess.run(
        [sys.executable, str(lint_script)],
        cwd=ROOT,
    )
    return lint_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
