# rejected/ — 淘汰与降级记录（审计用）

阶段 1.5 三重验证未通过、或通过但**不独立成 skill**的候选组。保留原文引用，允许事后捞回。

依据见 `../verified.md`。候选原文一律留在 `../candidates/`。

---

## `raw-workspace-navigation` — RAW 界面巡览（三面板 / 四选项卡 / 菜单）

- **判决**: V2 预测力不通过 + V3 独特性不通过
- **条数**: 6
- **候选 id**: `p1/f04`, `p1/f01（导航栏按钮部分）`, `p5/g12`, `p5/g07`, `p5/g04`, `p2/p2-04（颜色语义部分）`

界面巡览回答的是"某个东西在哪个面板/哪个选项卡里"。用它无法回答任何手册没写的新问题——查不到就再看一遍图，属于**信息检索**而不是**可外推的方法论**。V3：对任何用过 GUI 的人来说"按数据形态分视图"不是作者的差异化见解。

**处置**：不成 skill；**降级为共享 reference**，写入
`skills/reduce-saxs-frames-to-curves/references/raw-workspace-and-naming.md`
（三面板 / 四绘制选项卡 / 菜单 / 导航栏共享按钮 / 前缀与颜色状态机）。
被 `reduce-saxs-frames-to-curves` 与 `assess-guinier-fit-quality` 引用。

---

## `measure-molecular-weight-from-saxs` — 分子量测定的多法交叉

- **判决**: V2 预测力不通过（主）+ V3 独特性不通过
- **条数**: 2
- **候选 id**: `p1/f05`, `p4/ce05`

文章只列了六条路线（标样 I0 比对、绝对校准、Vc、校正的 Vp、ATSAS Shape&Size、Bayesian），没有任何一条的输入要求、操作步骤或"几法不一致时怎么办"的判据。用它们无法推出新结论——最多能复述"可以多法估 MW"。V3：方法名本身是领域常识；有信息量的部分（收敛性判读）文章没写。

**处置**：不成 skill。方法名清单保留在术语表 `g-` 系列的邻居条目中（见
`skills/configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md` 的"高级分析"小节）；
若日后拿到 ATSAS 教程可重启该单元。

**被淘汰候选一览**

- `p1/f05` (framework) **分子量多法交叉框架** — §0 引言能力清单（`source/article.md` §0）
- `p4/ce05` (counter-example) **把"功能列表"当成"我会做"** — §6 总结（`source/article.md` §6）

---

## `install-raw-on-your-platform` — RAW 的安装与平台选择

- **判决**: V2 / V3 均不通过（一次性操作 + 通用软件安装常识）
- **条数**: 1
- **候选 id**: `p2/p2-09`

"优先用预构建安装程序，没有对应版本才回源码编译"是一条平台安装经验，随版本与平台变化，且不需要 skill 承载（CLAUDE/agent 遇到时读官方下载页即可）。V1 也无法成立：全文只有一处出现。

**处置**：不成 skill。安装信息（SourceForge 地址、平台支持矩阵）作为事实写在
`skills/configure-bioxtas-raw-for-a-dataset/SKILL.md` 的 B 段"不适用场景"里，一句话带过。

---

## `sec-saxs-series-processing` — SEC-SAXS 数据处理

- **判决**: V2 预测力不通过（材料不足）
- **条数**: 2
- **候选 id**: `p5/g12（Series 部分）`, `p1/f04（Series 部分）`

文章只在界面一节写了"Series选项卡用于查看SEC-SAXS 数据"，没有一个 SEC-SAXS 采集/处理步骤、没有判据。用它推不出任何新问题的答案（例如"哪个 frame 该丢"）。

**处置**：不成 skill，**明确列为边界**———
`reduce-saxs-frames-to-curves` 的 B 段点名 SEC-SAXS 走 Series 选项卡、本 skill 不覆盖逐帧平均之外的 SEC 判读。等有专门的 SEC-SAXS 材料时重开。

---

## 降级为术语（不构成 skill，也不属淘汰）

`p5/g01–g12` 共 12 条术语（配置、定心/校准、掩膜、积分、平均、扣减、星标、标样、q 与 q_max·Rg、n_min/n_max 与残差、.dat、绘图选项卡）按方法论约定**不独立成 skill**，
作为共享词典落到
`skills/configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md`，
由三个 skill 交叉引用（解释的是"作者怎么用这个词"，不是字典义）。
