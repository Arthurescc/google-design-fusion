<div align="center">
  <img src="./assets/logo.svg" width="124" alt="Google Design Fusion logo" />
  <h1>Google Design Fusion</h1>
  <p><strong>一个面向多种 agent 客户端的开源可移植 skill / workflow 包：把 <code>design.google</code> 的完整设计思想体系，与精选的 <code>awesome-design-md</code> / <code>DESIGN.md</code> 风格参考库融合起来，再通过检索驱动的方式打通前端设计工作流。</strong></p>
  <p><a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a></p>
</div>

![前后对比图](./assets/screenshots/comparison.png)

## 它是什么

`google-design-fusion` 不是一个简单的提示词包装器，也不是一堆零散笔记。

它是一套完整封装的 skill 系统，包含：

- 基于 `design.google` 构建的本地设计语料库
- 基于 `awesome-design-md` 融合出来的风格层
- 基于 vendored `uiverse-io/galaxy` 快照整理出的本地动效层
- 能按设计阶段切换行为的检索 harness
- 针对常见 AI 前端错误的 anti-AI-slop guardrails
- 用于保证 skill、harness 和文档一致性的校验脚本

目标很直接：让 AI 生成的前端结果更有设计判断力、更可复核，也更少“套壳感”。

## 怎么使用

大多数用户并不需要先重建语料库。这个仓库已经把 skill 和本地向量库一起准备好了，正常使用时直接安装并调用即可。

你可以分三层来用：

### 1. 先接入你的 agent 客户端

1. 克隆这个仓库。
2. 让你的 agent runtime 指向 [skills/google-design-fusion/](./skills/google-design-fusion/)。
3. 保持 [google-design-vector-db/](./google-design-vector-db/) 与 skill 在同一个工作区。

核心可复用面是：

- [skills/google-design-fusion/SKILL.md](./skills/google-design-fusion/SKILL.md)
- [skills/google-design-fusion/references/](./skills/google-design-fusion/references/)
- [skills/google-design-fusion/scripts/](./skills/google-design-fusion/scripts/)
- [google-design-vector-db/](./google-design-vector-db/)

这个仓库现在内置两套协同 skill：

- [skills/google-design-fusion/](./skills/google-design-fusion/) = 检索引擎（`design.google` + 精选风格/动效语料，输出 retrieval packet）。
- [skills/huashu-fusion-studio/](./skills/huashu-fusion-studio/) = execution-first 编排器（packet -> 可执行 execution brief -> artifact 路由）。

架构关系说明（详见 [research/huashu-fusion-architecture.md](./research/huashu-fusion-architecture.md)）：

- `google-design-fusion` = retrieval engine。
- `huashu-fusion-studio` = orchestrator。
- 来自 [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) 且在需要时本地同步到 `skills/huashu-fusion-studio/vendor/huashu-derived/` 的 huashu 派生子集 = execution doctrine。

许可证边界说明：

- 仓库代码/文档默认遵循 MIT（除非另有说明）。
- `skills/huashu-fusion-studio/vendor/huashu-derived/` 是一个可选的本地同步输出，来源于 `alchaincyf/huashu-design`；一旦你在本地生成它，就继续遵循上游 `Personal Use License`，不被重新授权为 MIT。
- 顶层第三方/例外清单见 [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md)。
- 本地同步得到的 huashu-derived doctrine 文档是上游的受限子集，可能会引用本仓库未包含的上游文件路径。

### 兼容性矩阵

| 客户端 | 支持方式 | 推荐接入方式 | 说明 |
| --- | --- | --- | --- |
| `Codex` | 已验证适配 | 复制或软链接到 `~/.codex/skills/` | 这个仓库里的原生适配层已经在 Codex 上校验过。 |
| `Claude Code` | 可移植工作流支持 | 如果客户端支持本地 skill / prompt 包，就加载 [skills/google-design-fusion/](./skills/google-design-fusion/)；否则把仓库保留在工作区里，直接调用 harness 脚本 | 复用同一套 `SKILL.md`、references、scripts 和已检入的向量库。 |
| `OpenClaw` | 可移植工作流支持 | 把仓库保留在工作区里，并把同一个 skill 文件夹或 harness 脚本接进你的本地流程 | 核心运行面是仓库内本地资源，不依赖 Codex 专属提示层。 |
| `OpenCode` | 可移植工作流支持 | 如果你的配置支持本地 prompt 包，就加载同一个 skill 文件夹；否则从工作区直接调用 harness 脚本 | 适合先拿 retrieval-backed design packet，再进入代码生成。 |

Codex 的 PowerShell 示例：

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.codex\skills\google-design-fusion" `
  -Target (Resolve-Path ".\skills\google-design-fusion")
```

如果你只是想直接使用 skill，那么仓库里已经附带可用的 [google-design-vector-db/](./google-design-vector-db/)，不需要先重建。

### 2. 在提示里明确要求 agent 使用它

最稳妥的提示结构是：

```text
Use google-design-fusion for [任务]. Phase: [research|concept|wireframe|ui|polish|audit]. Return a retrieval-backed design packet first, then the final direction.
```

你也可以直接这样说：

- `Use google-design-fusion for an AI finance landing page. Phase: concept. Give me 3 distinct theses before any UI code.`
- `Use google-design-fusion to redesign this dashboard. Phase: ui. Keep one dominant task, cut fake metrics, and define motion only where it improves feedback.`
- `Use google-design-fusion to critique this existing mockup. Phase: audit. Flag hierarchy problems, tiny helper text, AI slop, and motion misuse.`
- `Use google-design-fusion for a premium Apple-style glassmorphism hero. Phase: polish. Keep the typography restrained and the motion secondary.`

### 3. 如果你想先看证据包，就直接跑 harness

如果你希望先检查检索到的来源，再决定如何出图或写前端，可以直接运行 harness：

```bash
python skills/google-design-fusion/scripts/design_harness.py "premium glassmorphism landing page with calmer hierarchy" --phase ui --top-k 8
python skills/google-design-fusion/scripts/design_harness.py "AI glasses notification motion" --phase research --top-k 8 --format json
python skills/google-design-fusion/scripts/design_harness.py "audit this enterprise dashboard for fake KPI clutter" --phase audit --top-k 8
```

这些 phase 的含义分别是：

- `research`：先收集原则、先例和约束
- `concept`：先确定设计命题并做方向对比
- `wireframe`：先锁定层级、流程和交互节奏
- `ui`：定义字体、表面系统和组件语言
- `polish`：打磨状态、文案密度、完成度和动效
- `audit`：审查现有设计或提示词

### Huashu 导出工具前置条件（最小集）

如果你要运行 huashu-derived 导出脚本，先把可选本地子集同步到 `skills/huashu-fusion-studio/vendor/huashu-derived/`，再确认：

- 同步命令：

```bash
git clone https://github.com/alchaincyf/huashu-design.git ../huashu-design-upstream
python skills/huashu-fusion-studio/scripts/sync_huashu_subset.py --source-root ../huashu-design-upstream --output-root skills/huashu-fusion-studio/vendor/huashu-derived --source-ref <40位上游SHA>
```

- 已安装 Node.js，并基于 `skills/huashu-fusion-studio/vendor/huashu-derived/package.json` 安装本地生成脚本依赖（`playwright@1.59.1`、`sharp@0.34.5`），例如：`cd skills/huashu-fusion-studio/vendor/huashu-derived && npm install`。
- 若走视频/动效导出（`mp4`/`gif`），`PATH` 中可用 `ffmpeg`。
- 若外部工具缺失，execution brief 仍可生成，但导出步骤可能失败或被跳过。

## 它来自哪里

这个仓库是有意识地把两套来源系统融合在一起。

### 1. 判断层

来源：

- `design.google` 的完整可抓取内容面
- 旧版 `design.google` 页面中链接出去的高价值外部文章

这一层提供：

- 层级与注意力设计
- 把动效当作意义表达，而不是装饰
- 排版、可读性与可访问性判断
- AI 信任、可解释性与以人为中心的交互思路
- 在需要时覆盖 ambient、硬件和 XR 场景约束

### 2. 风格层

来源：

- `awesome-design-md`

这一层提供：

- 视觉氛围
- 字体个性
- 密度与节奏
- 表面语言
- 组件气质与构图参考

一句话概括：

`design.google` 提供判断，`awesome-design-md` 提供风格种子，这个 skill 负责把两者融合成一个检索驱动的设计工作流。

### 3. 动效层

来源：

- 仓库内 vendored 的 `uiverse-io/galaxy` 快照
- 派生整理后的 `skills/google-design-fusion/galaxy-motion/`

这一层提供：

- hover 与 transition 参考
- CTA 反馈模式
- loading 与 notification 的动效样本
- 能够在 `ui / polish` 阶段隐式参与的微交互参考

## 为什么要做这个

大多数 AI 前端结果还在反复掉进同一批坑里：

- 没有产品意义的假 KPI 卡片
- 用很小的说明文字去弥补层级问题
- 一个页面里同时出现太多视觉焦点
- 靠装饰性渐变来承担解释工作
- 把动效当装饰，不当引导
- 看起来像组件库拼装，却被当作“完成版设计”

这个 skill 做的是把设计工作前移：

1. 先检索更强的设计证据
2. 先拦截常见反模式
3. 把“原则判断”和“风格参考”拆开
4. 再返回一个能用于 concept、UI、polish、audit 的可用设计包

## 已验证价值

当前仓库内置的语料规模：

- `328` 条来自 `design.google` 站点地图与补充恢复流程的抓取记录
- `248` 个已索引的 `design.google` 页面
- `32` 个已索引的高价值外部参考页面
- `54` 个 `awesome-design-md` 样本
- `3802` 个 `galaxy-motion` 记录
- `14066` 个本地检索 chunk

生成后的本地向量库被直接纳入仓库，是因为它本身就是这个 skill 的实际价值组成部分，而不只是构建产物。

## 前后对照

仓库里包含以下演示素材：

- 不使用 skill 的示例页：[examples/without-skill/index.html](./examples/without-skill/index.html)
- 使用 skill 的示例页：[examples/with-skill/index.html](./examples/with-skill/index.html)
- 对照展示页：[examples/comparison/index.html](./examples/comparison/index.html)
- 渲染后的对照图：[assets/screenshots/comparison.png](./assets/screenshots/comparison.png)

可观察到的差异：

| 不使用 skill | 使用 `google-design-fusion` |
| --- | --- |
| 信息噪音堆叠、假指标、装饰性说明字过多 | 单一主叙事更明确，层级更清楚，支撑信息更克制 |
| 风格主要靠默认猜测 | 风格由检索到的参考进行引导 |
| 没有来源链路 | 结果可以回溯到证据包 |
| 很容易滑向 AI slop | guardrails 会显式拦截常见错误 |

## 架构

整个仓库按分层 skill runtime 来组织。

### Corpus Builder

实现位置：

- [skills/google-design-fusion/scripts/build_design_fusion_vector_db.py](./skills/google-design-fusion/scripts/build_design_fusion_vector_db.py)

职责：

- 抓取 `design.google`
- 保留 canonical 与 redirect 信息
- 选择性纳入稳定的高价值外部设计参考
- 纳入 `awesome-design-md`
- 纳入派生后的 `galaxy-motion`
- 构建 chunk 化的稀疏检索索引和 manifest 元数据

### Retrieval Harness

实现位置：

- [skills/google-design-fusion/scripts/design_harness.py](./skills/google-design-fusion/scripts/design_harness.py)

职责：

- 按设计阶段分类请求
- 查询融合后的本地语料
- 结合阶段 profile 对结果加权
- 注入 anti-pattern guardrails
- 返回可复用的设计 packet，并在需要时给出 `motion_strategy`

### Skill Surface

实现位置：

- [skills/google-design-fusion/SKILL.md](./skills/google-design-fusion/SKILL.md)
- [skills/google-design-fusion/agents/openai.yaml](./skills/google-design-fusion/agents/openai.yaml)

职责：

- 教会模型何时以及如何使用语料库
- 区分 research、concept、wireframe、ui、polish、audit 的不同行为
- 让基于来源的设计推理保持可见

### Validation Layer

实现位置：

- [skills/google-design-fusion/scripts/validate_skill_contract.py](./skills/google-design-fusion/scripts/validate_skill_contract.py)
- [skills/google-design-fusion/scripts/validate_harness.py](./skills/google-design-fusion/scripts/validate_harness.py)
- [skills/google-design-fusion/scripts/validate_workspace_docs.py](./skills/google-design-fusion/scripts/validate_workspace_docs.py)
- [skills/google-design-fusion/scripts/run_full_validation.py](./skills/google-design-fusion/scripts/run_full_validation.py)

职责：

- 校验 skill 打包是否正确
- 校验 harness 行为是否符合预期
- 校验文档是否与真实语料输出一致

## Harness 机制

harness 是这个 skill 的运行核心。

它按四步工作：

1. **先构建本地库**
   corpus builder 会把 `design.google`、筛选后的外部参考，以及 `awesome-design-md` 融合成本地索引。

2. **按阶段分类请求**
   请求会被映射到 `research`、`concept`、`wireframe`、`ui`、`polish` 或 `audit`。

3. **按阶段规则检索**
   harness 会应用阶段 profile、来源权重和每页上限控制，因此 `audit` 不会像 `ui` 一样检索，`polish` 也不会像 `research` 一样工作。如果请求本身需要动效，`galaxy-motion` 会被隐式拉进检索，而不是要求用户手动声明。

4. **返回设计 packet**
   输出里会包含阶段目标、排序后的证据、anti-pattern guardrails，以及按页面去重后的参考来源。

这也是它和普通 prompt template 的核心区别：模型不是只靠“感觉”生成，而是被检索结果实质性地约束。

## Anti-Pattern Guardrails

这个 skill 显式约束了多类常见 AI 前端错误，包括：

- 没有意义的 KPI 数字
- 破坏审美平衡的小号解释文字
- 过度密集的卡片网格
- 没有产品角色的装饰性动效
- 缺乏层级纪律的风格混搭
- 看起来精致但没有来源依据的输出
- 因为处于 `polish` 阶段就无差别加动效

相关研究：

- [research/ai-design-antipatterns.md](./research/ai-design-antipatterns.md)

## 仓库结构

```text
skills/google-design-fusion/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
skills/huashu-fusion-studio/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  vendor/
    README.md
google-design-vector-db/
research/
examples/
  motion-fusion/
assets/
README.md
README.zh-CN.md
```

## 快速开始

克隆仓库，然后让你的 agent runtime 指向 [skills/google-design-fusion/](./skills/google-design-fusion/)。

如果你只是消费这个 skill，到这里就可以开始用了，直接按上面的提示方式向你的 agent 发任务即可。

只有在你想刷新来源语料、检查检索流程、或者重建本地动效层时，才需要重建。

如果你想在本地重建或检查：

```bash
git clone https://github.com/Arthurescc/google-design-fusion.git
git clone https://github.com/Arthurescc/awesome-design-md.git ../awesome-design-md
python skills/google-design-fusion/scripts/snapshot_galaxy_repo.py --output-root vendor --ref main
python skills/google-design-fusion/scripts/build_galaxy_motion_index.py --input-root vendor/galaxy --output-root skills/google-design-fusion/galaxy-motion
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
python skills/google-design-fusion/scripts/design_harness.py "premium glassmorphism landing page with calmer hierarchy" --phase ui --top-k 8
python skills/google-design-fusion/scripts/run_full_validation.py
```

## 研究文档

关键支撑文档包括：

- [research/design-google-site-map.md](./research/design-google-site-map.md)
- [research/design-google-principles.md](./research/design-google-principles.md)
- [research/google-design-awesome-fusion.md](./research/google-design-awesome-fusion.md)
- [research/ai-design-antipatterns.md](./research/ai-design-antipatterns.md)
- [research/huashu-fusion-architecture.md](./research/huashu-fusion-architecture.md)
- [research/validation-report.md](./research/validation-report.md)

## 发布说明

外部参考只会在满足更高标准时才被纳入：

- 访问稳定
- 具有明确的设计学习价值
- 文本抽取质量可用

视频壳页、弱重定向页、低信息量 landing page 不会进入索引语料。

## 贡献

参见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 许可证

仓库代码与文档遵循 MIT，详见 [LICENSE](./LICENSE)。

例外：如果你本地用同步脚本生成 `skills/huashu-fusion-studio/vendor/huashu-derived/`，那部分本地输出遵循 `alchaincyf/huashu-design` 的上游条款，不会被重新授权为 MIT。

顶层例外清单见 [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md)。
