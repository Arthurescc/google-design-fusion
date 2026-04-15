# AI 前端设计常见反模式

以下内容是为 skill 前置钩子准备的压缩版研究结果。它的用途不是“做设计理论综述”，而是把最常见、最伤审美和最容易被 AI 误生成的问题提前拦掉。

## 1. 不要用小字注释给坏设计擦屁股

只有当小字是在解释：

- 输入格式
- 风险
- 术语
- 上下文限制

它才有存在价值。

以下情况应直接判错：

- 用小字解释模糊图标
- 用 tooltip 解释弱层级
- 用 helper text 弥补糟糕文案

参考：

- [PatternFly Help on Forms](https://pf3.patternfly.org/v3/pattern-library/forms-and-controls/help-on-forms/)
- [PatternFly Popover Guidelines](https://www.patternfly.org/components/popover/design-guidelines/)
- [Material Errors](https://m1.material.io/patterns/errors.html)

## 2. 低对比小灰字不是“高级感”

以下组合默认拒绝：

- 小字 + 细字
- 灰字 + 彩色底
- 灰字 + 渐变底
- 灰字 + 玻璃底

实操上可以把：

`有语义文本 < 12px`

视作高风险条件。

参考：

- [Apple UI Design Tips](https://developer.apple.com/design/tips/)
- [Material Accessibility](https://m1.material.io/usability/accessibility.html)
- [Material Color](https://m1.material.io/style/color.html)

## 3. 一个区块只能有一个主角

AI 很容易同时堆：

- 大标题
- 大数字
- 彩色 badge
- 边角标签
- 两个 CTA
- 多层卡片

结果是没有任何一个真正成为视觉主角。

技能里的硬规则应是：

`每个屏幕或主区块只允许一个视觉主任务。`

参考：

- [Material Accessibility / Hierarchy and focus](https://m1.material.io/usability/accessibility.html)
- [NN/g Visual Design Principles Poster](https://media.nngroup.com/media/articles/attachments/Visual-Design-Principles-Poster.pdf)
- [AlterSquare on visual emphasis without substance](https://altersquare.io/ui-patterns-dont-work-ai-powered-interfaces/)

## 4. 装饰元素必须有职责

以下元素如果不承担信息职责，就应删除：

- 发光
- 渐变
- 毛玻璃
- 阴影
- 分隔线
- 插图
- 图标
- 背景网格

允许它们存在的前提只能是：

- 表达层级
- 表达状态
- 引导交互
- 承担品牌表达

参考：

- [NN/g Images on Mobile](https://www.nngroup.com/videos/mobile-images/?lm=supporting-multiple-location-users&pt=article)
- [NN/g Designing for Young Adults](https://media.nngroup.com/media/reports/free/Designing_for_Young_Adults_3rd_Edition.pdf)
- [Data to Viz / Decluttering your chart](https://www.data-to-viz.com/caveat/declutter.html)

## 5. 禁止伪专业数据卡片

若没有以下信息，不要生成 KPI 卡、环形图、仪表盘、sparkline：

- 指标名
- 单位
- 时间范围
- 比较对象
- 数据用途

否则就只是“像后台”的空壳。

参考：

- [PatternFly Dashboard Guidelines](https://v5-archive.patternfly.org/patterns/dashboard/design-guidelines/)
- [PatternFly Utilization Trend Card](https://pf3.patternfly.org/v3/pattern-library/cards/utilization-trend-card/)
- [Why Dashboard Dials and Gauges Are Useless for KPIs](https://www.staceybarr.com/measure-up/why-dashboard-dials-and-gauges-are-useless-for-kpis/)

## 6. 默认组件不是视觉系统

`shadcn + 默认 Tailwind + sidebar + metric cards + badge`

不能直接当成成品。

必须补齐：

- typography scale
- spacing rhythm
- surface treatment
- state system
- focus / selection 规则

参考：

- [openstatus-template](https://github.com/openstatusHQ/openstatus-template)
- [UXMagic / token drift and inconsistent flows](https://uxmagic.ai/blog/ai-ui-quality-production-workflow)
- [shadcn-ui discussion #6229](https://github.com/shadcn-ui/ui/discussions/6229)

## 7. 选中态、当前态、焦点态必须一眼可见

不允许只靠轻微背景色差表达选中；
也不允许主题切换后出现图标消失、当前项不明显的问题。

参考：

- [shadcn-ui discussion #6229](https://github.com/shadcn-ui/ui/discussions/6229)
- [Material Selection](https://m1.material.io/patterns/selection.html)
- [Material Accessibility](https://m1.material.io/usability/accessibility.html)

## 8. 动效只服务因果与焦点

允许的动效目的只有：

- 引导视线
- 解释结构
- 确认输入
- 遮蔽加载

以下默认拒绝：

- 漂浮装饰
- 无因果发光
- 呼吸式 hover
- 抖动
- 循环炫技过场

参考：

- [Material Motion](https://m1.material.io/motion/material-motion.html)

## 9. 核心交互不能塞进小目标和短暂 UI

核心操作不能只存在于：

- tiny icon
- hover-only affordance
- tooltip
- popover
- snackbar

尤其在移动端，这类做法会直接伤害可发现性和可操作性。

参考：

- [Apple UI Design Tips](https://developer.apple.com/design/tips/)
- [Material Snackbars](https://m1.material.io/components/snackbars-toasts.html)
- [JupyterLab issue #9399](https://github.com/jupyterlab/jupyterlab/issues/9399)

## 10. 移动端先保一级层级，再谈丰富

小屏默认只保留一层主层级，不要同时塞：

- summary
- detail
- filters
- side panel
- secondary metrics

参考：

- [Material Responsive UI](https://m1.material.io/layout/responsive-ui.html)
- [Apple UI Design Tips](https://developer.apple.com/design/tips/)
- [JupyterLab issue #9399](https://github.com/jupyterlab/jupyterlab/issues/9399)

## 11. 可直接用于检测的负面词

以下词可以直接进入前置检测或审查清单：

- `purple-blue gradient`
- `glowing number`
- `cards nested inside cards`
- `gray text on colored background`
- `meaningless badge`
- `tiny caption`
- `progress ring for trivial metric`
- `default shadcn dashboard stack`
- `sidebar icon low contrast`
- `selection state unclear`

补充参考：

- [Emelia / AI slop UI](https://emelia.io/hub/impeccable-ai-design-skill)
- [BSWEN / AI coding poor UI UX](https://docs.bswen.com/blog/2026-03-10-ai-coding-poor-ui-ux/)

