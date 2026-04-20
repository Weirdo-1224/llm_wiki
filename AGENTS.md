## 项目概述

本仓库是一个由 LLM 持续维护的 Markdown 知识库（Wiki），名为 `llm_wiki`。核心目标是将原始资料沉淀为可演化、可追溯、可复审的结构化知识。仓库本身不是传统软件项目，没有编译构建步骤；它的"产物"是结构化的 Markdown 页面与可运行的自动化脚本。

## 技术栈与依赖

- **内容格式**: Markdown（UTF-8 编码）
- **自动化脚本**: PowerShell（`*.ps1`），要求 Windows PowerShell 或 PowerShell Core
- **Lint 工具**: Python 3（`scripts/lint_repo.py`），无第三方依赖，仅使用标准库
- **版本控制**: Git
- **可选 AI 工具链**: `query_and_settle.ps1` 内部调用 `codex exec`（OpenAI Codex CLI），但这不是强依赖；若未安装，相关脚本会报错并提示配置

**注意**: 本项目不存在 `pyproject.toml`、`package.json`、`Cargo.toml`、`Makefile` 等传统构建配置文件。也没有虚拟环境、依赖锁文件或包管理器配置。

## 目录结构与模块划分

```
llm_wiki/
├── raw/                    # 原始资料区（只读保护，除移动操作外不得修改）
│   ├── inbox/              # 待处理的原始资料
│   ├── processed/          # 已摄取的原始资料（ingest 后从 inbox 移入）
│   └── assets/             # 原始附件（图片、PDF 等）
├── wiki/                   # 知识沉淀区（核心内容）
│   ├── sources/            # 来源总结页（每个被 ingest 的原始资料对应一页）
│   ├── entities/           # 实体页（人物、组织、设备、地点等）
│   ├── concepts/           # 概念页（术语、方法论、理论等）
│   ├── syntheses/          # 综合页（跨来源的主题整合与结论）
│   ├── queries/            # 查询页（问题记录、调研过程与回答沉淀）
│   ├── index.md            # 全局索引（所有页面的入口汇总）
│   ├── overview.md         # 项目概览与当前焦点
│   └── log.md              # 变更日志（按日期记录关键操作）
├── templates/              # 五类页面模板
│   ├── source.md           # 来源模板
│   ├── entity.md           # 实体模板
│   ├── concept.md          # 概念模板
│   ├── synthesis.md        # 综合模板
│   └── query.md            # 查询模板
├── scripts/                # 自动化脚本
│   ├── ingest.ps1          # 摄取原始资料到 wiki/sources/
│   ├── query.ps1           # 新建查询页
│   ├── query_and_settle.ps1 # 新建查询 + 调用 codex 回答 + lint
│   ├── lint.ps1            # PowerShell 包装器，调用 Python lint
│   └── lint_repo.py        # 核心 lint 逻辑（Python）
├── AGENTS.md               # 本文件（AI 代理操作指南）
└── README.md               # 面向人类贡献者的快速开始指南
```

## 构建与测试命令

本项目没有编译构建过程。"测试"等价于运行 lint 检查仓库结构、链接和语言规范。

```bash
# 运行 lint（结构检查、链接检查、语言规范检查）
python scripts/lint_repo.py
```

Lint 检查项包括：
- 必需目录与文件是否存在
- Markdown 内部链接是否失效（包括相对路径链接）
- 孤儿页面（没有任何其他 wiki 页面链接到的页面，`index.md`/`log.md`/`overview.md` 除外）
- 重复页面标题
- `wiki/entities/`、`wiki/concepts/`、`wiki/syntheses/`、`wiki/queries/` 下的页面是否缺少指向 `sources/` 的关联链接
- 中文语言规范：禁止出现英文模板标题（如 `Source Template`、`Query Template` 等），且正文必须包含中文字符

Lint 失败时返回非零退出码；警告不影响退出码，但会打印输出。

## 核心工作流

### 1. 摄取工作流（Ingest）

将 `raw/inbox/` 中的原始资料转化为 `wiki/sources/` 中的结构化来源页。

```powershell
powershell -ExecutionPolicy Bypass -File scripts/ingest.ps1
```

执行逻辑：
1. 按文件名排序取 `raw/inbox/` 中第一个文件。
2. 在 `wiki/sources/` 创建新来源页，id 格式为 `source-XXXX`（四位数字自增）。
3. 基于 `templates/source.md` 填充元数据（id、title、type、created_at、accessed_at、tags）。
4. 在 `wiki/index.md` 的 `## 来源` 节追加链接。
5. 在 `wiki/log.md` 追加摄取记录。
6. 将原始文件从 `raw/inbox/` 移动到 `raw/processed/`（若重名则加时间戳前缀）。

**约束**: 除 ingest 成功后的移动操作外，**严禁修改 `raw/` 下的任何原文文件**。

### 2. 查询工作流（Query）

记录问题并沉淀答案。

```powershell
# 仅新建查询页
powershell -ExecutionPolicy Bypass -File scripts/query.ps1 -Title "你的问题"

# 新建查询 + 调用 codex 回答 + 运行 lint（需要本地安装 codex CLI）
powershell -ExecutionPolicy Bypass -File scripts/query_and_settle.ps1 -Title "你的问题"
```

查询页命名格式：`query-<yyyyMMdd-HHmmss>-<slug>.md`，存放于 `wiki/queries/`。

查询工作流规范：
1. 先阅读 `wiki/index.md`。
2. 优先读取 wiki 已有页面，再回溯 `raw/` 原文。
3. 回答完成后，把可复用结论沉淀到 `wiki/syntheses/` 或更新已有 wiki 页面。
4. 同步更新 `wiki/index.md` 和 `wiki/log.md`。

### 3. 内容维护工作流

来源页建好后，需人工或 LLM 补充：
- 摘要、要点、证据/引文
- 关联实体与概念
- **事实**、**解读**、**待解问题**三个区块

若发现新证据与旧结论冲突，**必须显式添加"冲突/修订"说明**，禁止静默覆盖。

## 代码与内容风格规范

### 语言规范
- 除 `raw/` 下的原始资料外，仓库内所有新增或修改的 Markdown 文件**默认使用中文**。
- 以下情况可保留英文：`id`、文件路径、命令、代码块、标准缩写。
- 禁止在标题中使用英文模板名（lint 会拦截如 `Source Template`、`Query Template` 等残留英文标题）。

### Markdown 规范
- 元数据使用 YAML 风格列表（`- key: value`），置于页面顶部。
- 链接使用相对路径，如 `[source-0004](sources/source-0004.md)` 或 `../sources/source-0004.md`。
- 页面一级标题格式：
  - 来源页：`# source-XXXX: <原始文件名>`
  - 查询页：`# 查询: <问题标题>`
  - 综合页：`# 综合: <综合标题>`
  - 实体/概念页：`# <实体/概念名称>`

### 内容区分规范
所有 wiki 页面（尤其是来源页、查询页、综合页）必须明确区分三类信息：
- **事实（Facts）**: 有原文或数据直接支撑的描述。
- **解读（Interpretations）**: 基于事实的推断、分析或观点。
- **待解问题（Open Questions）**: 当前证据不足以回答的疑问。

### 变更规范
- 优先更新已有 wiki 页面，避免重复创建同主题页面。
- 保持改动小而可审查，不要一次性大规模重写多个主题。
- 每次涉及来源的操作，必须同步更新 `wiki/index.md` 和 `wiki/log.md`。

## 安全与完整性考虑

- `raw/` 目录是知识库的"证据链"，其完整性直接决定 wiki 内容的可信度。**禁止编辑、删除或重命名 `raw/` 下的原始文件**（ingest 后的移动除外）。
- 脚本使用 `Set-StrictMode -Version Latest` 和 `$ErrorActionPreference = "Stop"`，失败即终止，避免半成状态。
- 所有文件写入均使用 UTF-8 编码，避免中文乱码。
- `lint_repo.py` 会校验链接有效性，防止因文件重命名或路径调整导致大量死链。
- `query_and_settle.py` 依赖外部 `codex exec` 命令，执行前会检查脚本存在性，失败时给出明确错误提示。

## 常用命令速查

```bash
# 摄取一条 inbox 资料（按文件名排序取第一条）
python scripts/ingest.py

# 新建查询页
python scripts/query.py --title "规则一致性检查"

# 查询并沉淀（调用 codex exec）
python scripts/query_and_settle.py --title "某个问题"

# 仓库 lint
python scripts/lint_repo.py
```

## 入口页面

- [Wiki 索引](wiki/index.md) — 全站页面目录
- [Wiki 概览](wiki/overview.md) — 项目目的、工作流与当前焦点
- [Wiki 日志](wiki/log.md) — 按日期记录的关键变更
