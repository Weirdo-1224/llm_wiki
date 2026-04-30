import importlib
import io
import shutil
import sys
import unittest
import uuid
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class RepoFixture:
    def __enter__(self):
        self.tmp_root = ROOT / "tests" / ".tmp"
        self.tmp_root.mkdir(parents=True, exist_ok=True)
        self.root = self.tmp_root / f"repo-{uuid.uuid4().hex}"
        self.root.mkdir()
        for rel in [
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
        ]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "AGENTS.md").write_text("# 代理说明\n", encoding="utf-8")
        (self.root / "README.md").write_text("# 说明\n", encoding="utf-8")
        (self.root / "wiki/index.md").write_text("# 索引\n\n## 来源\n\n## 查询\n", encoding="utf-8")
        (self.root / "wiki/log.md").write_text("# 日志\n", encoding="utf-8")
        (self.root / "wiki/overview.md").write_text("# 概览\n", encoding="utf-8")
        shutil.copy(ROOT / "templates/source.md", self.root / "templates/source.md")
        shutil.copy(ROOT / "templates/query.md", self.root / "templates/query.md")
        for name in ["entity.md", "concept.md", "synthesis.md"]:
            (self.root / "templates" / name).write_text("# 模板\n", encoding="utf-8")
        return self.root

    def __exit__(self, exc_type, exc, tb):
        shutil.rmtree(self.root, ignore_errors=True)


class ReviewRegressionTests(unittest.TestCase):
    def test_lint_accepts_relative_markdown_links_with_fragments(self):
        lint_repo = importlib.import_module("scripts.lint_repo")

        with RepoFixture() as root:
            (root / "wiki/sources/source-0001.md").write_text("# source-0001: 来源\n", encoding="utf-8")
            (root / "wiki/syntheses/test.md").write_text(
                "# 综合: 测试\n\n见 [事实](../sources/source-0001.md#事实)。\n",
                encoding="utf-8",
            )

            with mock.patch.object(lint_repo, "ROOT", root):
                self.assertEqual(lint_repo.main(), 0)

    def test_ingest_does_not_write_wiki_files_when_move_fails(self):
        ingest = importlib.import_module("scripts.ingest")

        with RepoFixture() as root:
            (root / "raw/inbox/input.txt").write_text("原始资料\n", encoding="utf-8")
            before_index = (root / "wiki/index.md").read_text(encoding="utf-8")
            before_log = (root / "wiki/log.md").read_text(encoding="utf-8")

            with mock.patch.object(ingest, "ROOT", root), mock.patch.object(
                ingest.shutil, "move", side_effect=OSError("move failed")
            ):
                with self.assertRaises(OSError):
                    ingest.main()

            self.assertEqual((root / "wiki/index.md").read_text(encoding="utf-8"), before_index)
            self.assertEqual((root / "wiki/log.md").read_text(encoding="utf-8"), before_log)
            self.assertFalse((root / "wiki/sources/source-0001.md").exists())

    def test_query_and_settle_checks_codex_before_creating_query(self):
        query_and_settle = importlib.import_module("scripts.query_and_settle")

        with RepoFixture() as root:
            (root / "scripts/query.py").write_text("# 查询脚本占位\n", encoding="utf-8")
            (root / "scripts/lint_repo.py").write_text("# lint 脚本占位\n", encoding="utf-8")
            before_index = (root / "wiki/index.md").read_text(encoding="utf-8")
            before_log = (root / "wiki/log.md").read_text(encoding="utf-8")

            def fake_run(args, **kwargs):
                if args[:2] == ["codex", "--version"]:
                    raise FileNotFoundError("codex")
                raise AssertionError(f"unexpected subprocess call: {args}")

            with mock.patch.object(query_and_settle, "ROOT", root), mock.patch.object(
                query_and_settle.subprocess, "run", side_effect=fake_run
            ):
                stderr = io.StringIO()
                with redirect_stderr(stderr), mock.patch.object(
                    sys, "argv", ["query_and_settle.py", "--title", "测试问题"]
                ):
                    self.assertEqual(query_and_settle.main(), 1)

            self.assertEqual(list((root / "wiki/queries").glob("*.md")), [])
            self.assertEqual((root / "wiki/index.md").read_text(encoding="utf-8"), before_index)
            self.assertEqual((root / "wiki/log.md").read_text(encoding="utf-8"), before_log)


if __name__ == "__main__":
    unittest.main()
