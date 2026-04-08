## 使命
本仓库是一个由 LLM 持续维护的 Wiki，用于把原始资料沉淀为可演化知识库。

## 核心规则
1. 除了在成功摄取后将文件从 `raw/inbox/` 移到 `raw/processed/`，不得修改 `raw/` 下文件。
2. 优先更新已有 wiki 页面，避免重复创建同主题页面。
3. 每次 ingest 必须更新：
   - 一个来源总结页
   - `wiki/index.md`
   - `wiki/log.md`
4. 明确区分事实（Facts）、解读（Interpretations）和待解问题（Open Questions）。
5. 新证据与旧结论冲突时，必须添加“冲突/修订”说明，禁止静默覆盖。
6. 保持改动小而可审查。
7. 除 `raw/` 原文资料外，仓库内新增或修改的 Markdown 默认使用中文；`id`、路径、命令、代码块、标准缩写可保留英文。

## 查询工作流
1. 先阅读 `wiki/index.md`。
2. 优先读取 wiki 页面，再回溯 raw 原文。
3. 合适时把可复用结论沉淀到 `wiki/queries/` 或 `wiki/syntheses/`。

## Lint 工作流
检查：
- 失效链接
- 孤儿页面
- 重复页面
- 缺少相关来源链接的页面
- 中文写作规范（标题/正文）
