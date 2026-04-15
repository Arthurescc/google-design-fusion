# Google Design Fusion Audit Spec

**Date:** 2026-04-14

**Target:** `E:\AI素材\前端设计\goole design\skills\google-design-fusion`

## Goal

对 `google-design-fusion` skill 做一轮完整审查，覆盖语料构建、检索 harness、skill 说明、references、验证链路、工作区产物一致性，并修复发现的高价值问题。

## Context

当前工作区已经具备：

- 本地向量库 `google-design-vector-db/`
- 中文研究文档 `research/`
- skill 本体 `skills/google-design-fusion/`
- 构建脚本、检索脚本与验证脚本

当前已知遗留：

1. `design.google` sitemap 仍有 `13` 个入口未完全解析。
2. skill 经过一轮快速构建后，需要一次“从可用到可信”的审查。
3. 当前目录不是 git 仓库，无法使用 `using-git-worktrees` 的标准隔离流；本次以 `docs + subagents + validation` 代替 worktree 隔离。

## Audit Scope

### A. Source Coverage

- 检查 `design.google` 采集脚本是否对剩余 `13` 个页面给出更稳健的降级处理。
- 检查向量库 manifest、records、chunks 是否相互一致。
- 检查 `awesome-design-md` 样本计数、目录引用和 README 说明是否一致。

### B. Harness Quality

- 检查 `build_design_fusion_vector_db.py` 的抓取与降级逻辑。
- 检查 `design_harness.py` 的打分、去重、guardrail 注入和 phase 行为。
- 检查 `validate_harness.py` 是否覆盖关键检索场景。

### C. Skill Contract

- 检查 `SKILL.md` 触发描述是否准确。
- 检查 `openai.yaml` 是否符合 skill-creator 约束。
- 检查 `references/*.md` 是否完整闭环。
- 检查 skill 中引用到的文件是否真实存在。

### D. Documentation Quality

- 检查 `README.md`、`research/*.md`、`validation-report.md` 是否与真实构建结果一致。
- 检查是否存在过期数字、空目录、缓存目录、误导性描述。

### E. Execution Hygiene

- 检查是否残留 `__pycache__`、空目录或不应纳入交付的中间产物。
- 检查验证命令是否可以从当前工作区直接执行。

## Audit Checklist

- [ ] 向量库构建脚本可成功执行。
- [ ] 向量库输出的计数与文档描述一致。
- [ ] 对剩余未解析页面给出明确处理策略。
- [ ] harness 检索对 `research / ui / audit` 场景都能返回合理来源。
- [ ] skill 文案不存在 TODO、失效引用、错误 prompt。
- [ ] references 与 scripts 的边界清晰。
- [ ] README 与研究文档不夸大覆盖率。
- [ ] 工作区无明显缓存和空壳产物。
- [ ] 整套验证链路可重复执行并通过。

## Success Criteria

1. 所有本地校验命令通过。
2. 至少减少一部分剩余未解析页面，或者把其失败类型收敛为“不可恢复外链”。
3. skill 审查单中的高优先级问题全部修复。
4. 最终验证报告更新为本轮真实结果。

## Non-Goals

- 不在本轮把 skill 扩展成真正的多 agent 持久化系统。
- 不在本轮为每一篇 `design.google` 文章手工写摘要。
- 不在本轮引入外部 embedding 服务或数据库。

## Review Output Contract

本轮执行结束后必须产出：

1. 修复后的代码与文档。
2. 更新后的验证报告。
3. 对剩余未恢复页面的明确说明。
4. 简明的风险与下一步建议。
