# design.google 全站梳理

## 1. 采集范围与覆盖率

- 采集时间：2026-04-14
- 来源：`https://design.google/sitemap.xml`
- sitemap URL 总数：`328`
- 已纳入 crawl 审计账本的 `design.google` 入口：`328`
- 实际进入本地索引的 `design.google` 原站页面：`248`
- 选择性纳入的外部高价值设计参考：`32`
- 并入的 `awesome-design-md` 风格样本：`54`
- 最终本地检索 chunk：`6457`

本次解析优先走 `design.google` 页面的 Next.js `__NEXT_DATA__` 结构化数据；对于旧页面、外链重定向页和非 Next 页面，则降级为通用 HTML/Markdown 抽取。外链中只有“能稳定抽到正文、且设计学习价值高”的来源会进入本地索引，其余外链只保留结构化跳转记录，不会污染本地语料边界。

## 2. 站点主结构

从站点信息架构上看，`design.google` 并不是一个单纯的博客，而是一个“设计编辑平台 + 资源分发入口 + 历史专题库”。

核心入口可以分成 5 层：

1. 首页  
   承担编辑选题与主题导航功能，按精选文章、专题、分类和 Archive 组织内容。
2. 说明页  
   `About`、`Community`。
3. 大型专题页  
   当前最重要的是 `M10 / Ten Years of Material`。
4. 分类页  
   `Conversations`、`Spotlight`、`Perspectives`、`Guides`、`Podcasts`、`Video`、`Gallery`。
5. `library/*` 深页  
   占绝大多数，是设计文章、访谈、专题合集、活动页、播客/视频着陆页的主体内容区。

## 3. 内容簇

站点内容虽然横跨多年，但核心主题非常稳定，可以归纳为以下 9 个簇：

1. `Material / 设计系统`  
   Material 历史、Material 3 / Expressive、组件、颜色、运动、声学与触觉。
2. `Typography / Google Fonts`  
   字体设计、可读性、多语种排印、可变字体、品牌字体演进。
3. `AI / ML / HCI`  
   AI 界面、可解释性、公平性、人机协同、提示式交互、AI 图形符号。
4. `Accessibility / Inclusive Design`  
   全球可访问性、包容性研究、Lookout 等辅助产品设计。
5. `Brand / Identity / Art Direction`  
   Google 自身品牌、YouTube 红色演化、品牌在 Material 中的表达。
6. `Motion / Sound / Haptics`  
   动效如何服务注意力，声音与触觉如何进入系统语言。
7. `Hardware / Ambient / XR`  
   Google Home、硬件设计、透明屏与 AI 眼镜、环境式计算。
8. `Research / Career / Culture`  
   UX 研究方法、设计招聘、设计文化、设计领导力。
9. `Podcasts / Events / Archives`  
   Method、Design Notes、Centered、SPAN、I/O 等沉淀下来的历史内容。

## 4. 近期站点重心

从已解析的近年页面来看，Google Design 最近几期明显在强调以下方向：

1. `AI 不是独立主题，而是被拉回到视觉语言、信任与可理解性里`  
   代表页：`Illustrating the Gemini App`、`All That Sparkles Is AI`。
2. `Material 从“规范系统”走向“表达系统”`  
   代表页：`Inside M3 Expressive`、`Better, Easier, Emotional UX`。
3. `字体与品牌正在重新成为系统设计的核心层`  
   代表页：`Making Google Sans Flex`、`When Brand Fonts are Open Source`。
4. `硬件与环境式界面正在重新定义 UI 的物理前提`  
   代表页：`Designing for Transparent Screens`、`Unboxing a New Collaboration`。
5. `可访问性不再是合规补丁，而是主叙事的一部分`  
   代表页：`Evolving Lookout`。

## 5. 外部高价值理念层

除了 `design.google` 原站页面，本地索引现在还选择性纳入了 `32` 条外部高价值设计参考，主要来自：

- `m3.material.io`
- `m2.material.io`
- `fonts.googleblog.com`
- `research.google`
- `developers.google.com`
- `developers.googleblog.com`
- `pair.withgoogle.com`
- `medium / r.jina.ai` 文章型内容

这样做的目的不是“扩充互联网噪声”，而是补回 `design.google` 老页面外跳后仍然有正文价值的设计理念内容。

## 6. 站点本质判断

如果只用一句话描述 `design.google`，它更像：

`Google 设计体系的公开研究层和叙事层`

它不是单纯“教你做出什么样式”，而是在持续回答这些问题：

- 设计系统为什么要这样演化？
- 当介质、设备、文化和 AI 发生变化时，哪些原则应该先变，哪些不该变？
- 视觉语言怎样与真实的人类感知、注意力、身体和环境重新对齐？

这也是为什么在融合 `awesome-design-md` 时，最适合把 `design.google` 放在“原则与判断层”，而不是直接拿它当落地样式库。

## 7. 对后续 skill 的意义

对本项目来说，`design.google` 提供的最高价值不是“照着抄页面”，而是 4 件事：

1. 给 UI 生成提供原则锚点，而不是只给风格词。
2. 给 AI 时代的前端生成提供反模板化的审美约束。
3. 给复杂界面提供人因和上下文优先的决策依据。
4. 给 `awesome-design-md` 这类样式样本提供“为什么这样做”的上层解释。
