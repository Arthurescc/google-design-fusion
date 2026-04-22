# Google Design × awesome-design-md 融合方法

## 1. 角色分工

两套资料不要混着用，要先分清职责：

- `design.google`
  负责原则、判断、人因、系统演化、AI 与新媒介语境。
- `awesome-design-md`
  负责样式样本、品牌气质、排版个性、布局节奏、组件表情。

一句话说：

`Google Design 管“为什么这样设计”，awesome-design-md 管“这样设计长什么样”，galaxy-motion 管“它在交互里怎么动”。`

## 2. 融合入口

任何设计任务都先从问题类型入手，而不是先挑品牌样本。

### A. 原则型任务

例如：

- AI 助手界面
- 新媒介 / XR / 透明屏
- 强可访问性诉求
- 复杂系统表达

先定 `design.google` 原则簇，再补 `awesome-design-md` 样式种子。

### B. 表达型任务

例如：

- 品牌站
- landing page
- 宣传页
- 高辨识产品首页

先定 `awesome-design-md` 基础气质，再用 `design.google` 约束其可读性、动效、注意力与层级。

## 3. 推荐融合配方

推荐使用：

- `1` 个 Google Design 原则锚
- `2` 个主样式种子
- `1` 个拉伸样本（可选）

不要平均混 5 到 8 个品牌样本，那会让结果只剩“像 AI 混出来的综合风格”。

## 4. 风格轴翻译

从 `awesome-design-md` 提取风格时，不要只记品牌名，要翻译成风格轴。

建议固定这 11 个轴：

1. `brand_archetype`
2. `atmosphere_keywords`
3. `color_strategy`
4. `typography_signature`
5. `geometry_signature`
6. `depth_strategy`
7. `layout_rhythm`
8. `density_profile`
9. `component_signatures`
10. `imagery_strategy`
11. `motion_behavior`

只有把品牌样本转成这些轴，skill 才能稳定复用，而不是每次重新猜“Notion 风到底是什么”。

## 5. 高价值主样本

最适合做高价值融合基座的样本：

1. `linear.app`
   精密、克制、偏开发者、高信息密度。
2. `stripe`
   高端、清晰、轻字重、强品牌秩序。
3. `notion`
   温和、编辑感、留白强、边界低噪。
4. `clay`
   彩度更高，更有玩味，适合拉开温度。
5. `vercel`
   黑白系统化、纪律强、极简工程气质。
6. `ibm`
   企业级 token 感最强，适合系统语义对齐。

推荐作为拉伸样本的：

- `apple`
- `spotify`
- `clickhouse`
- `airbnb`

## 6. 推荐融合模板

### 模板 A：AI 产品主页

- Google Design 锚点：
  `AI clarity + attention management`
- 主样式种子：
  `Linear + Vercel`
- 拉伸样本：
  `Clay`

适合：
清晰、可信、现代，但不呆板的 AI 产品。

### 模板 B：高端工具型官网

- Google Design 锚点：
  `Material expressiveness + typography clarity`
- 主样式种子：
  `Stripe + Apple`
- 拉伸样本：
  `Notion`

适合：
需要高级感、秩序感、轻奢表达，但不想显得冷硬。

### 模板 C：未来感但不失可读性的科技界面

- Google Design 锚点：
  `ambient / hardware / motion guidance`
- 主样式种子：
  `Spotify + ClickHouse`
- 拉伸样本：
  `Vercel`

适合：
新媒介、硬件、XR、视觉实验型产品。

## 7. 最终落到 skill 的方式

这个融合方法在 skill 里应该被固化为：

1. 先检索原则，不先出样式。
2. 再检索 2 到 3 个样式种子。
3. 把样式样本翻译成风格轴。
4. 用 anti-pattern 钩子先做一次负面筛查。
5. 如果请求涉及反馈、CTA、loading、hover 或 polish，再引入 `galaxy-motion`。
6. 最后才输出设计方向、prompt 包或实现建议。

这样做的结果，不是把 Google Design “做成另一个模板库”，而是把它变成你整个设计生成流程里的判断引擎。
