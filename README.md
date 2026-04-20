# LLM Wiki

用于把原始资料持续沉淀为可演化知识库的 Markdown 仓库。  
该仓库面向 LLM 协作维护，强调可追溯、可复审和小步更新。

## 项目目标
- 让原始资料在 `raw/` 中保留原貌，知识沉淀在 `wiki/` 中演进。
- 用统一模板和流程，保持新增内容结构一致。
- 通过日志与索引管理，降低后续查询与维护成本。

## 目录说明
- `raw/`：原始资料区（`inbox/` 待处理，`processed/` 已处理，`assets/` 附件）
- `wiki/`：知识区（`sources/`、`entities/`、`concepts/`、`syntheses/`、`queries/`）
- `templates/`：来源、实体、概念、综合、查询模板
- `scripts/`：自动化脚本（ingest、query、lint）
- `AGENTS.md`：项目操作规则与工作流约束

## 核心约束
- 除 ingest 成功后从 `raw/inbox/` 移动到 `raw/processed/` 外，不修改 `raw/` 原文。
- 优先更新已有页面，避免同主题重复建页。
- 每次 ingest 必须同步更新来源页、`wiki/index.md`、`wiki/log.md`。
- 内容需区分 Facts、Interpretations、Open Questions。
- 新证据与旧结论冲突时，必须显式记录“冲突/修订”。
- 除 `raw/` 原文外，新增或修改 Markdown 默认使用中文。

## 快速开始
1. 把新资料放入 `raw/inbox/`。
2. 执行 ingest：
   `python scripts/ingest.py`
3. 在 `wiki/sources/` 新来源页基础上补全事实、解读与待解问题。
4. 视需要更新 `wiki/entities/`、`wiki/concepts/`、`wiki/syntheses/`。
5. 检查 `wiki/index.md` 与 `wiki/log.md` 是否已反映本次变更。
6. 执行 lint：
   `python scripts/lint_repo.py`

## 查询工作流
1. 新建查询：
   `python scripts/query.py --title "你的问题"`
2. 一次性执行“建查询 + 回答沉淀 + lint”：
   `python scripts/query_and_settle.py --title "你的问题"`
3. 查询时遵循顺序：先读 `wiki/index.md`，优先读 wiki 页面，再回溯 `raw/`。

## 常用命令
```bash
# ingest 一条 inbox 资料（按文件名排序取第一条）
python scripts/ingest.py

# 新建查询页
python scripts/query.py --title "规则一致性检查"

# 查询并沉淀（调用 codex exec）
python scripts/query_and_settle.py --title "某个问题"

# 仓库 lint（链接、孤儿页、重复页、来源关联、中文规范）
python scripts/lint_repo.py
```

## 入口页面
- [Wiki 索引](wiki/index.md)
- [Wiki 概览](wiki/overview.md)
- [Wiki 日志](wiki/log.md)
