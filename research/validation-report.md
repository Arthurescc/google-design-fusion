# 验证报告

## 1. 当前真实构建结果

全量构建命令：

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

当前数值来自：

- `google-design-vector-db/manifest.json`
- `google-design-vector-db/crawl-summary.json`

当前结果：

- `design.google` sitemap URL：`328`
- `design.google` crawl 结果记录：`328`
- `design.google` 原站可索引页面：`248`
- `design.google` 外部高价值参考：`32`
- `design.google` 总 indexable 语料：`280`
- `awesome-design-md` 样本：`54`
- `galaxy-motion` 记录：`3802`
- 最终 chunk：`14066`
- 未入索引入口：`48`

当前未入索引入口分类：

- `external_redirect`: `35`
- `fetch_error`: `10`
- `redirect_to_home`: `3`

## 2. 覆盖率口径

本项目现在明确区分两层口径：

1. `crawl 记录`
   表示 sitemap 入口是否已经进入结构化审计账本。
2. `indexable 语料`
   表示该入口最终是否进入向量检索语料。

因此，当前统一使用：

- `328` 条 `design.google` crawl 记录
- `248` 条可索引 `design.google` 原站语料
- `32` 条可索引 `design.google-external` 学习语料
- `280` 条总 indexable `design.google` 语料

当前覆盖率：

- `indexable_ratio`: `0.8537`
- `ok_ratio`: `0.7561`

## 3. 外部理念学习层

当前被选择性纳入本地学习层的外部来源主要包括：

- `m3.material.io`
- `m2.material.io`
- `fonts.googleblog.com`
- `research.google`
- `developers.google.com`
- `developers.googleblog.com`
- `pair.withgoogle.com`
- `medium / r.jina.ai` 文章型内容

纳入原则是：

- 必须能稳定抽到正文
- 必须有明确设计学习价值
- 不允许把视频壳、栏目页、主页壳直接混进索引

## 4. 当前未入索引入口的含义

### A. `external_redirect` (`35`)

这些入口会跳到：

- YouTube
- 播客首页或栏目页
- 通用外部主页

它们只保留结构化跳转记录，不进入本地索引。

### B. `fetch_error` (`10`)

这部分仍是当前最值得继续追的高价值缺口，典型原因包括：

- 旧入口已失效
- 远端返回 403 / 404
- 当前映射表仍未覆盖

### C. `redirect_to_home` (`3`)

这些入口会被软/硬重定向回 `design.google` 首页。现在它们不会再被误写成“成功抓到了首页内容”。

## 5. Skill 与 Harness 校验

已执行：

```bash
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/google-design-fusion
python skills/google-design-fusion/scripts/validate_skill_contract.py
python skills/google-design-fusion/scripts/validate_harness.py
python skills/google-design-fusion/scripts/validate_workspace_docs.py
python skills/google-design-fusion/scripts/run_full_validation.py
```

校验面：

- `quick_validate.py`
  skill 结构与 frontmatter 基础合法性
- `validate_skill_contract.py`
  skill markdown 引用、prompt 约束、缓存污染
- `validate_harness.py`
  phase 区分、每页去重上限、basic family skew
- `validate_workspace_docs.py`
  workspace 文档与 manifest / crawl-summary 数字闭环
- `run_full_validation.py`
  串行执行上述本地验证链

## 6. Harness 现在真正验证了什么

当前可以确认：

1. `audit` phase 有独立检索策略，不再只是换文案。
2. 同一路径不会无限刷屏；默认每页上限 `2`，`audit` 为 `1`。
3. 检索不会再只因为 `design.google` 的共享 tag 系统性刷分。
4. `ui` 与 `audit` 的结果必须有基本区分度，否则校验失败。
5. 校验不再只看“有没有某个 source family”，还会检查重复占位和 aggregate skew。
6. `polish` 阶段只有在查询本身需要动效且检到 `galaxy-motion` 证据时，`motion_strategy.enabled` 才会打开。

## 7. 当前可放心使用的链路

1. `build_design_fusion_vector_db.py`
   重建 crawl ledger、原站语料、外部学习语料、manifest、crawl-summary。
2. `design_harness.py`
   按 `phase` 检索并输出 guardrails + evidence packet。
3. `SKILL.md`
   约束模型先做 anti-pattern preflight，再做检索、融合与输出。
4. `research/*.md`
   作为人工复核与后续扩写材料。

## 8. 当前剩余风险

1. 仍有 `35` 个 `external_redirect` 入口只保留了跳转记录，没有纳入本地语料。
2. `fetch_error` 的 `10` 个入口仍值得继续追。
3. 当前向量库仍然是本地 sparse retrieval，不是外部 embedding 服务；已经够用，但不是极限召回方案。
