# Google Design Fusion Galaxy Motion Integration Spec

**Date:** 2026-04-21

**Target:** `E:\AI素材\前端设计\goole design`

## Goal

把 `uiverse-io/galaxy` 的全量动效相关代码和仓库快照纳入 `google-design-fusion` 项目本体，在不改变项目核心定位的前提下，把动效作为新的资源层、证据层和 harness 融合层接入现有 skill，使用户在正常发起前端设计请求时，动效可以被 **默认隐式融入** 到 `concept / ui / polish / audit` 流程中。

最终交付不是一个独立 motion skill，而是一个升级后的 `google-design-fusion`：

- `design.google` 继续提供原则判断层
- `awesome-design-md` 继续提供视觉风格层
- `Galaxy` 新增为动效资源层与动效证据层
- harness 继续是项目核心，负责决定何时、如何、以多大权重把动效融入前端设计

## Context

当前项目已经具备：

- 本地设计向量库 `google-design-vector-db/`
- `google-design-fusion` skill 本体 `skills/google-design-fusion/`
- 构建脚本 `build_design_fusion_vector_db.py`
- 检索 harness `design_harness.py`
- 校验脚本 `run_full_validation.py` 等

当前 harness 形态已经明确为一个“窄而稳”的 Tier 2 检索 harness：

- 语料构建
- 检索
- guardrail 注入
- 验证

这次集成不能把它做偏成“素材堆积仓”或“独立动效项目”。动效必须成为设计流程中的一个新维度，而不是主角。

## Source-backed external facts

本次设计基于以下外部事实：

1. `uiverse-io/galaxy` README 明确说明它是一个来自 Uiverse 平台的自动归档仓库，包含 `3000+` UI 元素。
2. 该仓库 README 明确说明所有 UI 元素以 **MIT License** 提供。
3. Galaxy 的组织方式是组件/模式目录 + 单文件 HTML/CSS/Tailwind 片段，不是一个已经整理好的“动效知识库”。

这些事实决定了本次集成必须分为 **原始快照层** 与 **派生整理层** 两层，而不能把 Galaxy 原始代码直接裸并入现有检索库。

## Core product decision

用户已经明确确认以下产品边界：

1. `Galaxy` 的资源要 **全量拿到自己手里**
2. 要先做 **完整快照与建库**
3. 动效要 **默认隐式融入** 前端设计流程
4. 项目必须继续保持为 `google-design-fusion`，不能演变成独立 motion skill

因此，本次设计采用：

**全量快照 + 派生动效层 + motion-aware harness + 统一验证链路**

## Architecture

### Layer 1. Principle Layer

保留现状：

- 来源：`design.google`
- 作用：层级、可访问性、注意力管理、动效语义、AI 交互可信度、Material 历史与系统判断

这一层仍然回答：

- 什么时候该有动效
- 动效的作用是什么
- 哪些动效会损伤语义、清晰度、可访问性或任务聚焦

### Layer 2. Style Layer

保留现状：

- 来源：`awesome-design-md`
- 作用：视觉语言、品牌气质、字体性格、密度、几何和组件表面风格

这一层仍然回答：

- 页面“长什么样”
- 表面气质如何落地

### Layer 3. Motion Resource Layer

新增：

- 来源：`uiverse-io/galaxy`
- 作用：提供全量可追溯的动效实现样本、交互动画片段、状态切换、hover/load/notification 等微交互代码

这一层回答：

- 某类动效有哪些实现原型
- 哪些动效适合作为 CTA、hover、loading、notification、empty state 的参考
- 哪些代码片段可以被抽取为可检索动效模式

### Layer 4. Motion Evidence Layer

新增：

- 由 Galaxy 原始代码提炼出的结构化索引层
- 对每个条目补充组件类型、动效类型、触发方式、强度、节奏、适用场景、风险标签

这一层不保存“原样代码快照”，而保存：

- 结构化元数据
- 检索友好的文本摘要
- 代码特征和动效标签

### Layer 5. Retrieval Harness Layer

升级现有 harness，但保持它仍是 Tier 2：

- query + phase 入口不变
- 新增 motion-aware 权重逻辑
- 新增“是否需要动效参与”的隐式判断
- 新增 motion strategy 输出块

这一层回答：

- 当前请求是否应该引入动效
- 应该引入哪一类动效
- 动效在本次设计中应该扮演什么角色
- 如何把动效放进设计输出而不压过原则层

## Repository shape

本次集成后，仓库新增两个关键区域。

### A. 原始快照层

建议新增：

```text
vendor/galaxy/
```

职责：

- 保存 Galaxy 上游全量快照
- 保留目录结构、LICENSE、来源说明
- 提供“全量持有”的事实基础
- 作为后续同步和差异检查基线

原则：

- 原始快照不直接作为高权重检索来源
- 原始快照不直接写进 skill prompt
- 原始快照优先服务于“派生整理层”的生成

### B. 派生整理层

建议新增：

```text
skills/google-design-fusion/galaxy-motion/
  index/
  manifests/
  samples/
  tests/
```

职责：

- 把 Galaxy 原始条目转成可检索的 motion records
- 做动效类型、组件类型、触发方式、适用场景的标签化
- 为 harness 提供 motion-specific 证据层
- 为最终效果验证提供测试页和基准样例

原则：

- 派生层是项目内部语义层，不是简单复制上游目录
- 派生层服务于 `google-design-fusion` 的工作流，而不是独立存在

## Module boundaries

### 1. Snapshot ingestion

建议新增脚本：

```text
skills/google-design-fusion/scripts/snapshot_galaxy_repo.py
```

职责：

- 获取并写入 Galaxy 全量快照
- 记录同步时间、commit hash、来源 URL、license 信息
- 保持 vendor 层结构稳定

### 2. Motion indexing

建议新增脚本：

```text
skills/google-design-fusion/scripts/build_galaxy_motion_index.py
```

职责：

- 从 `vendor/galaxy/` 读取原始组件文件
- 解析 HTML/CSS/Tailwind 内容
- 识别动效类型、触发方式和交互语义
- 输出结构化 motion records 和检索摘要

### 3. Unified corpus builder

修改现有：

```text
skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

职责升级为三源融合：

- `design.google`
- `awesome-design-md`
- `galaxy-motion` 派生层

但必须坚持：

- `Galaxy` 不以原始 HTML/CSS 噪声直接高权重入库
- 仅通过整理后的 motion evidence 进入主检索库

### 4. Motion-aware harness

修改现有：

```text
skills/google-design-fusion/scripts/design_harness.py
```

新增能力：

- 自动判断请求是否需要动效参与
- 针对 `concept / ui / polish / audit` 做不同的 motion 权重策略
- 输出 motion strategy / motion references / motion guardrails

### 5. Skill prompt and references

建议新增或扩展：

```text
skills/google-design-fusion/references/motion-fusion.md
skills/google-design-fusion/references/motion-guardrails.md
skills/google-design-fusion/references/galaxy-source-policy.md
```

职责：

- 规定什么时候应引入动效
- 规定动效如何服务层级、响应、状态切换和反馈
- 规定什么时候禁止动效过量
- 规定如何在提示词中自然融入动效，而不是把页面做成“特效展板”

## Harness behavior

### Default behavior

动效默认 **隐式融入**，用户不需要显式说出 `motion-heavy`、`microinteraction`、`animation` 等关键词。

harness 在检索前先做一次轻量判断：

- 当前请求是否包含品牌感、交互反馈、加载状态、hover 状态、空状态、通知、转场、polish 信号
- 如果是，则提高 Galaxy 动效层参与度
- 如果不是，则保持 Galaxy 权重很低，只作为边缘参考

### Phase-specific behavior

#### `concept`

- 使用 Galaxy 识别“动效气质方向”
- 输出应偏“动效角色定义”，不是直接给代码

#### `ui`

- 使用 Galaxy 选择组件级动效参考
- 输出应偏“哪些部件该动、如何动、动多重”

#### `polish`

- Galaxy 权重最高
- 输出应偏“hover、transition、loading、feedback、microinteraction”的具体融合策略

#### `audit`

- 不把 Galaxy 当灵感源，而当对照源
- 用来判断当前设计是否存在“炫技动效”“无意义循环”“负担型 hover”“干扰型 loading”

## Prompt-engineering contract

动效不能以“额外特效建议”形式附着在输出后面，而必须以设计结构的一部分出现。

因此最终输出 contract 增加：

1. `motion role`
   说明动效服务什么：层级、因果、反馈、等待、状态切换、强调

2. `motion placement`
   指出哪些区域可动，哪些区域必须静止

3. `motion references`
   给出来自 Galaxy 的检索依据

4. `motion guardrails`
   明确禁止无意义发光、无限循环、视觉疲劳型 hover、与核心任务无关的炫技动画

## Safety and quality rules

新增质量底线：

1. 动效必须为任务或状态服务，不能只为“好看”
2. 动效不能压过信息层级
3. 动效不能破坏可读性、可点击性、对比度或可访问性
4. loading、hover、notification、button feedback 要分开处理，不能混为一类
5. 同一页面不同时叠加多种动效语言
6. Galaxy 样式片段不能直接高置信度照搬，必须经过原则层和风格层约束

## Validation

### A. Snapshot validation

- Galaxy 快照目录完整
- LICENSE 和来源信息保留
- 快照 manifest 与实际文件数量一致

### B. Index validation

- 派生 motion records 可构建
- 关键目录都能被识别和标签化
- 无法解析的文件会进入错误报告而不是静默丢失

### C. Harness validation

- 对同一 query，在 `ui` 与 `polish` 阶段，Galaxy 参与度不同
- 对明显不需要动效的 query，Galaxy 权重自动降低
- `audit` 阶段可以输出 motion guardrails

### D. Visual flow validation

新增至少一组最终 demo：

- 不融合动效资源
- 融合动效资源

验证目标：

- 动效确实改变了输出质量
- 动效没有使页面滑向噪声化和特效化
- prompt / harness / demo 三者的结果相互一致

## Risks

### 1. Noise takeover

Galaxy 的代码量远大于现有 skill 的单一 UI 样例层，如果不做派生整理层，主检索会被代码噪声污染。

### 2. Style takeover

如果不给 Galaxy 降权并设置 phase-aware 策略，它会把 `google-design-fusion` 从“原则引导的设计 skill”带偏成“特效组件 skill”。

### 3. Prompt collapse

如果只把动效资源加进库里、不改 output contract，最终模型只会“偶尔提到动画”，而不是把动效真正融入设计决策。

### 4. Validation gap

如果没有最终 demo 和视觉校验，动效层即便技术接入成功，也可能在用户体验上没有真实提升。

## Success Criteria

1. Galaxy 全量快照进入项目仓库并可追溯。
2. 派生 motion layer 成功建立，可供 harness 检索。
3. `google-design-fusion` 在不显式声明动效的前提下，能默认把动效融入设计流程。
4. 动效不会压过 `design.google` 的原则层与 `awesome-design-md` 的风格层。
5. 校验链路可以证明：动效确实进入了最终前端设计效果，而不是只进入了仓库。

## Non-goals

- 不把 `google-design-fusion` 改造成独立动效组件库项目。
- 不把 Galaxy 每个组件都手工重写成统一代码风格。
- 不把 harness 扩展成多 agent 编排系统。
- 不在本轮解决所有 Galaxy 组件的生产级可访问性问题，只做检索与融合层约束。

## Review Output Contract

本轮设计获批后，后续 implementation plan 必须覆盖：

1. Galaxy 快照同步流程
2. motion 派生索引流程
3. 主语料构建脚本扩展
4. harness 动效融合逻辑
5. skill references 与 prompt contract 更新
6. 最终 demo、测试与校验链路
