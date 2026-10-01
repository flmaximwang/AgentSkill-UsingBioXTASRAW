---
name: choose-a-molecular-weight-method
description: "分子量六法怎么选、能不能信（SEC 用它判低聚态/单体二聚体）：两轴定位（RAW 原生 4 法 vs ATSAS 2 法；浓度依赖 vs 浓度无关）——SEC 峰内浓度未知，只能用浓度无关法（Vc / Vp / Shape&Size / Bayesian）；通则 ~10% 不确定度、不应用 SAXS 定分子量（要 MALS / AUC，最好 SEC-MALS-SAXS），SAXS 的用途是判低聚态；含各法不确定度与失效域、Vc 常数（蛋白 c=0.1231 k=1 / RNA c=0.00934 k=0.808）、Porod 默认密度 0.83 kDa/Å³、结合化学计量（250 vs 270 kDa）判不了。用于「SEC 的分子量怎么算 / 该报哪个」「SAXS 能定分子量吗」「Vc 和 Vp 哪个准」「Bayesian 分子量」「<15–20 kDa 能用 Vc 吗」「蛋白-核酸复合物算 MW」；不负责 SEC 系列怎么切帧（转 process-sec-saxs-series），也不负责曲线 Rg/I(0) 可信度（转 assess-guinier-fit-quality）。"
source_book: BioXTAS RAW 官方文档 v2.4.2 · *Molecular weight calculation*（SAXS 方法学，`saxs/saxs_mw.rst`）+ *Molecular weight analysis*（教程，`tutorial/s1_mw.rst`）
source_chapter: saxs/saxs_mw.rst 全篇 / tutorial/s1_mw.rst 全篇
tags: [saxs, bioxtas-raw, molecular-weight, sec-saxs, method-selection]
related_skills:
  - slug: process-sec-saxs-series
    relation: depends-on
  - slug: assess-guinier-fit-quality
    relation: depends-on
---

# 分子量不是"一个数"：先判哪一类方法能用，再谈它有多准

SAXS 给了好几个分子量，它们不是"同一个数的几种实现"，而是**几条互不替代的估计**。选法的第一条轴不是"哪个更准"，而是"我手上有没有浓度"——**能不能用这一类方法，由数据形态决定，不由精度决定**。

## R — 原文 (Reading)

> "RAW supports four of the most common methods natively"
> [FILE: saxs/saxs_mw.rst]

> "There are two additional methods supported in the ATSAS software, which RAW will show if ATSAS is installed"
> [FILE: saxs/saxs_mw.rst]

> "Generally speaking the methods can be broken up into two categories: concentration dependent and concentration independent."
> [FILE: saxs/saxs_mw.rst]

> "The concentration dependent methods require knowing the concentration ... which often means they are incompatible with SEC-SAXS measurements."
> [FILE: saxs/saxs_mw.rst]

> "a usual rule of thumb is ~10% uncertainty (or more). For this reasons, SAXS should not be used to determine the molecular weight of your sample"
> [FILE: saxs/saxs_mw.rst]

> "The main reason to calculate molecular weight from SAXS data is to determine the oligomeric state of the protein in solution."
> [FILE: saxs/saxs_mw.rst]

> "For proteins, c=0.1231 and k=1 while for RNA c=0.00934 and k=0.808"
> [FILE: saxs/saxs_mw.rst]

> "Large uncertainty for macromolecules less than ~15-20 kDa"
> [FILE: saxs/saxs_mw.rst]

> "Doesn't work for protein nucleic acid complexes."
> [FILE: saxs/saxs_mw.rst]

> "May need to have the protein density adjusted in some cases (default: 0.83 kDa/Å³)"
> [FILE: saxs/saxs_mw.rst]

> "Every method requires a good determination of I(0), and all of the concentration independent methods require Rg"
> [FILE: saxs/saxs_mw.rst]

> "SAXS data is unlikely to be reliable enough to accurately determine the difference between bound and unbound (250 kDa or 270 kDa)"
> [FILE: saxs/saxs_mw.rst]

> "Neither the I(0) Ref. MW panel nor the Abs. MW panel should be reporting a MW."
> [FILE: tutorial/s1_mw.rst]

> "The expected MW value for GI is 172 kDa."
> [FILE: tutorial/s1_mw.rst]

> "The expected MW of lysozyme is 14.3 kDa."
> [FILE: tutorial/s1_mw.rst]

## I — 骨架 (Interpretation)

RAW 把分子量拆成**六个互相独立的估计**，用两条轴定位（教程 `s1_mw` 与 `saxs_mw` 一致）：

- **轴一「原生 4 法 / ATSAS 2 法」**：装不装 ATSAS 决定面板数是 4 个还是 6 个。原生四法 = 绝对标定 I(0)、参比标准品、Porod 体积（SAXSMoW 2）、相关体积 Vc；ATSAS 两法 = 与已知结构比对（Shape&Size）、Bayesian 推断。
- **轴二「浓度依赖 / 浓度无关」**——**这条轴才是选法的判据**：
  - 浓度依赖：绝对标定 I(0)、参比标准品。**需要 SAXS 池中浓度**，而 SEC 洗脱峰内浓度随时间变化且未知 → **与 SEC-SAXS 不兼容**。
  - 浓度无关：Porod 体积 Vp、相关体积 Vc、Shape&Size、Bayesian。**适用于 SEC-SAXS**。

由此推出五条操作性结论：

1. **SEC-SAXS 只能用浓度无关法**（Vc / Vp / Shape&Size / Bayesian）。这不是精度取舍，而是数据形态限制——SEC 里浓度未知。教程印证：不填浓度框时，I(0) Ref. MW 与 Abs. MW 两个面板**不出数**。
2. **不应用 SAXS 定分子量。** 通则 ~10% 不确定度（或更大），不足以区分相邻低聚态。要"定"分子量用 **MALS 或 AUC**，最好做 **SEC-MALS-SAXS**（在同一洗脱上同时收 MALS 与 SAXS，排除两次测量间样品变化）。
3. **SAXS 分子量的用途是判低聚态**：同源二聚体及更高阶——分得开就够；分不开就换方法，别硬报。
4. **所有方法都要求好的 I(0)；所有浓度无关方法还要求好的 Rg**（即好的 Guinier 拟合）。Rg/I(0) 不可信时，MW 的讨论无从谈起（转 `assess-guinier-fit-quality`）。
5. **同一个蛋白"该报哪个 MW"没有唯一答案**：应**并列各法**并说明哪些方法 eligible（浓度依赖 vs 无关），而不是挑一个最像期望值的。官方自己也用已知标样（GI、lysozyme）给各法做量级校验。

**失效域必须先于数值被检查**（六法对照表见 `references/mw-methods-comparison.md`）：

| 方法 | 类别 | 关键失效点 |
|---|---|---|
| 绝对标定 I(0) | 浓度依赖 | 需准确浓度 + 准确绝对刻度；需已知对比度/偏比容 |
| 参比标准品 | 浓度依赖 | 需准确浓度；标样须同对比度（同缓冲液）、同形状（同偏比容） |
| Porod 体积 Vp | 浓度无关 | 默认密度 0.83 kDa/Å³；非蛋白失败；对扣减误差敏感 |
| 相关体积 Vc | 浓度无关 | <~15–20 kDa 不确定度大；蛋白-核酸复合物失效；∫qI(q) 须收敛 |
| Shape&Size | 浓度无关 | 柔性体系无结果；只对蛋白 |
| Bayesian | 浓度无关 | 对显著扣减误差敏感；只对蛋白 |

一句话判据：**"我手上有浓度吗？"** → 有（批次、浓度已知）→ 浓度依赖法可用；没有（SEC 峰内）→ 只能用浓度无关法。第二条问题才是"这类方法在这个分子上会不会失效"。

## A1 — 案例 (Past Application)

**1. 两个已知答案的标样**（a04；源 `tutorial/s1_mw.rst`）

- 问题：六种方法一次算出好几个数，怎么知道哪个可信。
- 做法：右键扣减后的 GI 曲线 → Molecular weight（或 Profiles 面板底部 `Mol. Weight`）→ 在浓度框填 `0.47 mg/ml` → 六个（装 ATSAS）面板同时出结果。
- 结果：**GI 期望 172 kDa（0.47 mg/ml）**；再对 lysozyme 重复，**期望 14.3 kDa（4.27 mg/ml）**。
- 结论：这两个数是各法是否给出合理量级的锚点。教程特意追问一句 "Does the Vc method work for the lysozyme data?"——因为 **14.3 kDa 正落在 Vc 的失效区（<~15–20 kDa）**，是设计好的反例。

**2. SEC-SAXS 场景：浓度未知 ⇒ 只有一半方法能用**（f14 / p2o-09）

- 问题：SEC 联用的峰里怎么算 MW、能不能用绝对刻度法。
- 结论：不能——浓度依赖法（绝对刻度 I(0)、参比标准品）与 SEC-SAXS 不兼容；只能用 Vc / Vp / Shape&Size / Bayesian。这是 `process-sec-saxs-series` 里"浓度未知 ⇒ 不能用 I0 标样"那条限制在 MW 上的落地。

**3. 反例：把 SAXS 的 MW 当定量结论**（ce08）

- 症状：用 SAXS MW 去区分 250 vs 270 kDa（结合/未结合），或 1:1 vs 2:1（270 vs 290 kDa）。
- 为什么不行：通则 ~10% 不确定度，不足以分辨这个量级的差；各法 MW 还会分散、对扣减/浓度敏感。
- 正确处置：MW 只用于判低聚态趋势；要准确分子量用 **MALS / AUC**，最好 **SEC-MALS-SAXS**。

**4. 反例：Vc 用在小分子或蛋白-核酸复合物上**（ce09）

- 症状：<15–20 kDa 的小蛋白 MW 不确定度大（经验系数由 ≥20 kDa 尺寸段拟合）；蛋白-核酸复合物直接失效。
- 识别：∫qI(q) 是否在高 q 收敛（曲线变平）；分子是否含核酸。
- 处置：换其它途径并以 MALS 为准。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 拿到了 SEC-SAXS 的曲线，要报分子量，但不知道用哪个方法。
- 同一批数据里六种方法给了不同的数，想知道哪个可信。
- 想"用 SAXS 定分子量"，或想用它区分结合态/寡聚态。
- 小蛋白（<20 kDa）或含核酸的复合物，不确定 Vc 还能不能用。
- 已知浓度、想做绝对刻度法，但不确定前提是否满足。

**语言信号**

- 「SEC-SAXS 的分子量怎么算 / 该报哪一个」
- 「SAXS 能不能定分子量」
- 「Vc 和 Vp 哪个准 / 不一致该怎么办」
- 「Bayesian 分子量怎么来的」
- 「不到 20 kDa 的蛋白能用 Vc 吗」
- 「蛋白-核酸复合物的 MW 算出来不对」
- 「250 kDa 和 270 kDa 能区分吗」

**与相邻 skill 的区别**

- 与 `process-sec-saxs-series`：那边负责"把洗脱过程切成一段可信曲线"，并在剖面里给逐帧 MW(Vc)/MW(Vp) 平台判据；本 skill 只在**要报哪个 MW、能不能信**时接手。
- 与 `assess-guinier-fit-quality`：本 skill 的所有方法都以好 I(0)/好 Rg 为前提；那条曲线可不可信归那边。若 Rg/I(0) 本身存疑，先回那边。
- 与 `configure-bioxtas-raw-for-a-dataset`：浓度依赖法要求绝对刻度已正确标定；常数错会让 Abs. MW 面板出错，那属配置问题。

## E — 执行步骤 (Execution)

1. **先判数据形态**：曲线来自 SEC 洗脱峰（浓度未知）还是批次测量（浓度已知）？
   完成标准：能说出这次用得上"浓度依赖法"还是只能用"浓度无关法"。判停点：SEC → 直接排除绝对刻度与参比标准品。
2. **确认前置**：是否已有可信的 Rg 与 I(0)（好的 Guinier 拟合）？
   完成标准：能报出 Rg 的 q 区间与不确定度。判停点：Guinier 存疑 → 转 `assess-guinier-fit-quality`。
3. **（浓度依赖法）准备参数**：在浓度框内填 SAXS 池中浓度（如 GI `0.47 mg/ml`）；确认绝对刻度已正确标定（否则 Abs. MW 面板不出数）。
   完成标准：填完浓度后所有方法面板都出结果。
4. **打开 Molecular weight 面板**：右键扣减曲线 → `Molecular weight`，或点 Profiles 面板底部 `Mol. Weight`。
   完成标准：面板顶部显示 Guinier 结果，下方显示各法 MW。装 ATSAS 才有 6 个面板；没有则少最右一列（4 个）。
5. **读结果**：**未填浓度时不报 Abs. MW 与 I(0) Ref. MW 的数**（官方 note）。对 Vc/Vp 可点 `Show Details` 看 ∫qI(q) 是否收敛 / cutoff 位置。
   完成标准：能列出各法数值 + 每个数属于哪一类（依赖/无关浓度）。
6. **交叉核对量级**：用已知锚点（GI 172 kDa、lysozyme 14.3 kDa）判断各法是否给出合理量级；不一致时对照失效域定位原因（小分子 / 复合物 / 扣减误差 / 柔性 / 非蛋白）。
   完成标准：能说清"哪个数为什么偏了"，而不是只挑一个最像期望值的。
7. **报结论**：**并列**各法 MW + 说明哪些方法本次 eligible（浓度依赖 vs 无关）+ 给不确定度量级（~10%）。不要只报一个数当定量结论。
   完成标准：报告里能区分"判低聚态够用"与"要准分子量"两种情况。
8. **要"定"分子量或判结合化学计量时** → 明确改用 MALS / AUC，最好 SEC-MALS-SAXS。
   完成标准：能说出为什么 SAXS 这一层到此为止。

## B — 边界 (Boundary)

**不要用的场景**

- 想问"这条曲线的 Rg/I(0) 是多少、信不信得过" → 走 `assess-guinier-fit-quality`。
- 想问"SEC 洗脱过程里哪一段是一个样品、怎么变成一条曲线" → 走 `process-sec-saxs-series`。
- 想用 SAXS MW 区分相邻低聚态/结合化学计量 → 本 skill 的结论是"做不到，换 MALS/AUC/SEC-MALS-SAXS"。
- 绝对刻度常数是否正确 → 属配置问题（`configure-bioxtas-raw-for-a-dataset`），不是本 skill 能修的。

**源里明确警告过的失败模式**

- **把 SAXS MW 当定量结论**（ce08）：通则是 ~10% 不确定度（或更大），不足以分辨 250 vs 270 kDa 或 1:1 vs 2:1（270 vs 290 kDa）。
- **在 SEC-SAXS 上用浓度依赖法**（p2o-09）：峰内浓度未知，绝对刻度/参比标准品不成立。
- **把 Vc 用在 <15–20 kDa 或蛋白-核酸复合物上**（ce09 / p2o-11）：经验系数由 ≥20 kDa 段拟合；复合物直接失效。Vc 还要求 ∫qI(q) 在高 q 收敛。
- **Porod 法用默认密度不去核对**（p2o-12）：默认 0.83 kDa/Å³，非蛋白会失败，且对扣减误差敏感。
- **拿小分子/复合物去套 Shape&Size 或 Bayesian**：两者都只对蛋白，且柔性体系上 Shape&Size 无结果。

**材料盲点 / 版本约束**

- **绑定 RAW v2.4.2**：菜单文字、面板数量、`More Info` 文案随版本变化；本 skill 的常数与阈值以该版本文档为准，找不到控件时以程序自带 `docs/` 或在线文档核对。
- 文档**不给"各法 MW 差多少才该怀疑"的统一阈值**，只给各法自身的经验不确定度与失效域；判读只能逐法对照。
- **参比标准品法没有给不确定度数字**，只给"相似标样与样品、同条件下可高度准确"的定性说明——本 skill 不编造数字。
- 六法对照表、不确定度来源与常数汇总见 `references/mw-methods-comparison.md`。

## 相关 skills

- **process-sec-saxs-series** — `depends-on`（本 skill 依赖对方）：本 skill 处理的是"一条已经取好的扣减曲线"；曲线由哪些帧构成、峰内浓度为何未知，都在那边定性。
- **assess-guinier-fit-quality** — `depends-on`（本 skill 依赖对方）：六法共同前提是好 I(0)，浓度无关法还要求好 Rg。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/BOOK_OVERVIEW.md`。
