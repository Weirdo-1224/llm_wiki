# LLM Wiki（最小脚手架）

一个最小可运行的 Markdown Wiki 结构，用于维护长期知识库。

## 目录结构
- `raw/`: 原始来源与附件
- `wiki/`: 可维护知识层
- `templates/`: 新条目模板
- `scripts/`: 自动化脚本

## 快速开始
1. 将新资料放入 `raw/inbox/`。
2. 在 `wiki/sources/` 建立来源页（基于 `templates/source.md`）。
3. 抽取实体/概念到 `wiki/entities/`、`wiki/concepts/`。
4. 在 `wiki/syntheses/` 形成阶段性总结。
5. 在 `wiki/log.md` 记录关键变更。

## 入口
- [Wiki 索引](wiki/index.md)
- [Wiki 概览](wiki/overview.md)
- [Wiki 日志](wiki/log.md)
