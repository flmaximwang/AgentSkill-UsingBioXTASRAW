---
name: deconvolve-overlapping-elution-peaks
description: "重叠洗脱峰去卷积（SEC 主峰有肩、IEC 盐梯度、滴定/时间分辨）按复杂度选 SVD/EFA/REGALS：判分量数、圈 Forward/Backward 区间、按数量级调 lambda，再用 χ²≈1 与取消正性约束复核。用于「峰里到底有几个组分」「EFA 起点怎么定」「REGALS lambda 调到多少」「自动判定的分量数能信吗」「去卷积结果怎么算可信」；不做区间选择（转 process-sec-saxs-series）、不做基线校正（转 correct-sec-saxs-baseline）。"
source_book: "BioXTAS RAW 官方文档 v2.4.2 — *Advanced Series processing*：SVD / EFA / REGALS（tutorial/s2_svd · s2_efa · s2_regals）"
source_chapter: "40-tutorial.md · tutorial/s2_svd.rst + s2_efa.rst + s2_regals.rst；50-api.md · api/ex_sec_saxs.rst"
tags: [saxs, bioxtas-raw, deconvolution, svd, efa, regals, sec-saxs, iec-saxs, titration]
related_skills:
  - slug: process-sec-saxs-series
    relation: depends-on
  - slug: correct-sec-saxs-baseline
    relation: contrasts-with
  - slug: assess-guinier-fit-quality
    relation: composes-with
  - slug: script-raw-with-the-python-api
    relation: composes-with
---

# 峰叠在一起：先数几个组分，再谈分解

SEC 没把物种分开时，**"峰里是什么"这个问题不能靠看曲线的肩来回答**——肩只是没分干净的组分的投影。这个 skill 干三件事：用 SVD 独立数出峰里有几个散射体，按数据复杂度选 EFA 或 REGALS 把峰拆成各自的散射曲线与浓度曲线，再用可复现的判据决定"这次分解能不能信"。

一句话定位：**它回答"峰里有几个组分、各长什么样"，不回答"哪几帧算一个样品"（那是 `process-sec-saxs-series`），也不回答"基线怎么校正"（那是 `correct-sec-saxs-baseline`）。**

## R — 原文 (Reading)

方法阶梯：

> Evolving factor analysis (EFA) is an extension of SVD that can extract individual components from overlapping SEC-SAXS peaks.
>
> [FILE: 40-tutorial.md · tutorial/s2_svd.rst]

> …for more complex data, such as ion exchange chromatography, or time resolved or titration data you should use REGALS.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

分量数判据：

> Vectors corresponding to significant components will tend to have autocorrelations near 1 (roughly, >0.6-0.7)…insignificant … near 0.
>
> [FILE: 40-tutorial.md · tutorial/s2_svd.rst]

> What matters is the relative magnitude, that is, whether the value is large relative to the mostly flat/unchanging value of high index singular values
>
> [FILE: 40-tutorial.md · tutorial/s2_svd.rst]

自动判定可能错、改范围不自动更新：

> RAW can find the wrong number of components automatically.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> You will always want to double check this automatic determination against the SVD results in the plots.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> If you change the data range used (or data type), the number of components will not automatically update…
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

EFA 复核三步与路径依赖：

> Examine the chi-squared plot. It should be uniformly close to 1 for good EFA.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> If this results in a significant change in the peak, your EFA analysis is likely poor, and you should not trust your results.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> The height of the concentration peaks is arbitrary, all peaks are normalized to have an area of 1.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> you can bias the rotation with the previous results and guide the EFA into a solution that is path dependent and thus isn't reproducible later.
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

分解结果的性质与外部佐证：

> Any data obtained via this method should be supported in other ways, either using other methods of deconvolving the peak…
>
> [FILE: 40-tutorial.md · tutorial/s2_efa.rst]

> If you want to do EFA deconvolution, it is best to not use a baseline correction
>
> [FILE: 40-tutorial.md · tutorial/s2_baseline.rst]

REGALS 调参、过平滑与否：

> Generally you want to adjust lambda by an order of magnitude or more. Smaller adjustments will have minimal effect on the deconvolution.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

> You will also see a sudden and dramatic change in the component 1 profile at some point.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

> Once you see the high q backgrounds match … it means you're oversmoothing the buffer components.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

> Reduce the lambda for both buffer components to the last good value, which would be ~4e8.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

> Because it can take a while to run, REGALS does not automatically update the results.
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

> When you have changes to your deconvolution settings and REGALS hasn't been run with those settings the "Run REGALS" button will have a yellow…
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

可测尺寸的 Shannon 限：

> the largest dimension of an object that can be measured is ~300 Å, based on the Shannon limit of D_{max}<\pi/q_{min}
>
> [FILE: 40-tutorial.md · tutorial/s2_regals.rst]

## I — 骨架 (Interpretation)

### 一、方法不是任选，是随数据复杂度阶梯升级

三档工具对应三种"组分进出数据的次序"：

- **SVD（只数，不拆）**：回答"峰里有几个独立散射体"。它只看奇异值相对高序号平坦基线是否显著，以及左右奇异向量的自相关是否接近 1（**约 >0.6–0.7 才算显著**）。SVD 是 EFA 的第一步，而且这一步**在 EFA 窗口内自动完成**，不需要先单独开 SVD 窗口。
- **EFA（标准 SEC 用）**：前提是组分**严格先进先出**（FIFO）——先洗脱的先进、先出。SEC 正是这种情形，所以官方推荐标准 SEC-SAXS 用 EFA。EFA 在 SVD 基础上把奇异向量旋转成每个真实组分的散射曲线 + 浓度曲线。
- **REGALS（非 FIFO / 复杂数据用）**：用于**组分不满足先进先出**的场景——IEC-SAXS（盐梯度让缓冲背景随时间变）、时间分辨、滴定序列；它**还能处理倾斜基线**的 SEC 数据。REGALS 可看作 EFA 向更复杂条件的推广，代价是参数更多、每改一次必须手动 Run。

**不可交换的主次**：EFA 与 REGALS 都要先有一个"分量数"的起点，而这个起点由 SVD 逻辑给出——**不要跳过"独立核对分量数"这一步直接调区间**。自动判定可能错，改了数据范围/数据类型它也不会自动更新。

### 二、三阶调参：由粗到细，层层依赖

参数不是一个一个试，而是**三阶**，上一阶没定就不要动下一阶：

1. **分量数**——RAW 自动判定的显著 SV 数只是起点，必须与 SVD 图的奇异值基线 + 自相关交叉核对；两者不一致（奇异值个数 ≠ 自相关≈1 的向量个数）通常说明有一个弱/分辨不良的组分，先按**较小**的数试，再按较大的数试。
2. **区间（Forward/Backward 起点）**——在 Forward EFA 图上把起点拖到**奇异值首次快速上升**处，在 Backward EFA 图上拖到**落回基线**处，用它们圈出各分量的帧范围；再到 Component Range Controls 微调区间，直到 **χ² 均匀接近 1、无大尖峰**。
3. **正则化 lambda**——REGALS 里逐分量关掉 Auto lambda 后按 **≥1 个数量级**调；对强分量/测量点多的分量（峰）lambda 可以很小甚至 0，对缓冲分量要增大使其浓度更平滑。

外加**第 4 个动作保证可复现**：最终一次运行必须关掉 "Start with previous results"（它只用于快速迭代，会引入路径依赖偏差，使结果不可复现）。

### 三、复核：把"看起来对"变成可检验

EFA 每次做完必须走**三步复核**（官方"每做一次 EFA 都要做"）：

1. 所选分量区间确实对应 Forward/Backward EFA 的起点；
2. **χ² 图应均匀接近 1、无大尖峰**；
3. **取消正性约束（C>=0）后浓度不应显著变化**——若显著变化，说明 EFA 差、结果不可信。

REGALS 的对应复核：λ 若设得特别差，χ² 图会偏离 ~1；χ² 仍接近 1 说明 λ 大概率没问题。另两条硬事实：**浓度峰高度本身是任意的**（各峰都归一化到面积 1，不要读绝对高度）；**任何去卷积结果都需要其它方法/生化数据佐证**——旋转不保证成功，也不保证给出有效的散射向量。

一句话判据：**"我凭什么说这几个分量是真的？"——数对（SVD 交叉核对）、χ² 平、去掉正性约束浓度不变，三条齐全才交付；缺一条就只能作为线索。**

## A1 — 案例 (Past Application)

**1. `phehc_sec.hdf5`：标准 SEC 用 EFA**（40-tutorial.md · s2_svd.rst / s2_efa.rst）

- 数据：苯丙氨酸羟化酶（PheH）的 SEC-SAXS 重叠峰。
- 做法：SVD 窗口里把起始帧设 100、结束帧设近 300、切到 Subtracted——只看这一段峰，看到 **2 个显著奇异值**（若用未扣减数据，正常还应多出一个对应缓冲散射的分量；本例数据本就扣过背景，所以无差别）。
- 结论：SVD 只数出"这段峰里有 2 个散射体"。要做完整分解则用 EFA。

**2. `phehc_sec.hdf5`：EFA 三阶调参的官方实例值**（40-tutorial.md · s2_efa.rst）

- 帧范围：用整段 **0–385**（前后各留缓冲液区）。
- 分量数：RAW 自动判 **3 个显著 SV**，文档说 for this data set, that is accurate。
- Forward 起点：应约 **147、164、322**；Backward 起点：应约 **383、360、200**。
- 区间微调：先设回 RAW 默认 **151–193 / 164–322 / 319–347** 看 χ² 尖峰，再微调至 **Range 0 ≈ 142–198、Range 1 = 161–322、Range 2 = 319–360**（判据是 chi² 尖峰消失）。
- 复核：χ² 均匀接近 1；取消 Range 0 的 C>=0 后浓度峰无显著变化 → 可信。最终运行关掉 "Start with previous results"。
- 结论：EFA 的每个数字都是**可复现的官方锚点**；三阶顺序（数 → 区间 → 复核）在实例里完整走了一遍。

**3. `nrde_iec.hdf5`：IEC-SAXS 用 REGALS**（40-tutorial.md · s2_regals.rst）

- 数据：离子交换（盐梯度）SAXS，缓冲背景随时间变，常规 EFA 不适用。
- 做法：实验类型保持默认 **'IEC/SEC-SAXS'**，保留 "Use EFA" → 在 **Background Components** 窗口里 Add Region **0–100**、再 Add 最后 100 帧，看到各只有 1 个强分量 → **# Significant SVs = 1** → 在 Forward/Backward 图上定起点 → 调分量区间 → 调 lambda → 每次手动 Run REGALS。
- 分量数：RAW 自动判 **4 个显著 SV**，文档说 that is accurate。Forward 起点应约 **0、350、750、1195**；Backward 起点应约 **700、1325、1600、1736**。
- 区间调参：component 3 起点 **1150 → 试 1125、1100（差别很小）→ 回到 1125**；component 2 浓度终点 **1300 → 试 1275**（消除负向小凹陷）。
- lambda：强分量（峰）浓度 lambda 关掉 Auto 设为 **0**；缓冲分量（0/1）每次**乘一个数量级**，直到出现"高 q 背景趋同 + component 1 profile 剧变"的过平滑信号，再回调到 **last good value ≈ 4e8**。
- 结论：REGALS 的每个旋钮都有官方实例值；过平滑的识别信号是**高 q 背景先趋同、随后某分量 profile 突变**。

**4. `pheh_titration.hdf5`：滴定序列用 REGALS（含 Dmax 判据）**（40-tutorial.md · s2_regals.rst）

- 数据：16 个浓度点、0–80 mM L-phe，含聚集体，点少且非等间距。
- 做法：**# Significant SVs 设为 3**（RAW 自动找到 4，实测约 4–5；据先验知识只要两个构象 + 一个聚集体）→ 实验类型选 **Titration** → **取消 "Use EFA"**（点太少，EFA 起点不可用）→ Calibrate X axis 载入 `pheh_titration_conc.txt` → "Use for X axis" 选 **Log10(X)** → 因 log(0) 未定义，把首点浓度由 0 改为 **10.0 µM** → 设各分量 Dmax → Run REGALS。
- Dmax 判据：聚集体（component 2）Dmax 设 **300**（Shannon 限 Dmax<π/q_min，据 q 范围最大可测 ~300 Å）；两构象 Dmax 由 **110** 起步、每步加 **10–20** 到 **160**——其中 **~130–150 χ² 稳定、>~120 P(r) 不再被逼零、160 时 χ² 明显上升** → 最终取 **130**（与先前分析一致）。
- 结论：分量数、X 轴反式、Dmax 都可以**从先验知识/物理上限**入手，再靠 χ² 与 P(r) 形状收敛；不同分量的 Dmax 不必然一致。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- SEC-SAXS 主峰有明显肩部，想知道峰里到底是不是一个物种/有几个物种。
- 已经确定要用 EFA/REGALS，但卡在"几个分量""起点拖到哪""lambda 是多少"。
- REGALS 调了 lambda，某个分量的曲线突然大变或高 q 变怪，判断自己是不是调过头。
- 拿到一份别人做的去卷积结果，要判断它可不可信。
- 数据是 IEC-SAXS、时间分辨或滴定序列，不确定该不该用 EFA。

**语言信号**

- 「这个峰里到底有几个组分 / SVD 上那几个奇异值算显著吗」
- 「EFA 的 Forward/Backward 起点该点在哪」
- 「REGALS 的 lambda 调到多少合适 / 调到 1e10 结果就崩了」
- 「RAW 自动判的分量数能信吗 / 我改了帧范围它怎么没变」
- 「去卷积出来的三条曲线能发文章吗 / 怎么证明它是对的」

**与相邻 skill 的区别**

- 与 `process-sec-saxs-series`：那边负责"选哪几帧是一个样品"（区间与平台判据），产出**一条**扣减曲线；本 skill 从"一条曲线不足以描述这个重叠峰"开始，产出**多条**分量曲线 + 浓度曲线。若峰其实没重叠、只要一条曲线，别用本 skill。
- 与 `correct-sec-saxs-baseline`：做过基线校正的数据**不要**再叠加 EFA（官方："做 EFA 最好不做基线校正"）；REGALS 虽有处理倾斜基线之能，但那是 REGALS 内部的背景分量建模，不是先做 `Integral` 校正。二者取舍写在本 skill B 段。
- 与 `assess-guinier-fit-quality`：本 skill 交付各分量的散射曲线；每条分量曲线的 Rg/I0 是否可信仍归那边判读。
- 与 `script-raw-with-the-python-api`：GUI 能做的这里都能用 API 做（`raw.svd/efa/regals`）；但无 GUI 时 EFA 要**自行给出每个分量的区间**——即本 skill 第 2 步的产物必须由你先想清楚。

## E — 执行步骤 (Execution)

1. **前置确认**：手上是一条**扣减好的 Series**；若数据做过基线校正，先想清楚是不是必须做（做 EFA 最好不做）。
   完成标准：能说出这条 series 的来源与是否做过基线校正。判停点：还没定 buffer/sample 区 → 先转 `process-sec-saxs-series`。
2. **用 SVD 独立数分量（不看自动值先自己看）**：打开 SVD 窗口，把帧范围缩到峰所在的一段，切 Subtracted；数"显著高于高序号平坦基线的奇异值"个数，以及"左右奇异向量自相关都接近 1（约 >0.6–0.7）"的向量个数。
   完成标准：写下你自己数的两个数（奇异值个数、自相关≈1 的向量个数）及其一致性。判停点：两者不等 → 大概率有弱/分辨不良组分，先按较小的数试，再按较大的数试。
3. **选方法**：组分严格先进先出（标准 SEC）→ **EFA**；IEC-SAXS / 时间分辨 / 滴定 / 倾斜基线 → **REGALS**。
   完成标准：能给出选它的理由（对应"次序是否 FIFO"）。
4. **核对 RAW 自动判定的分量数**：与第 2 步的结果对照；改了数据范围/类型后**手动重查**它是否仍正确。
   完成标准：分量数是你"交叉核对过"的数，不是直接采信的默认值。
5. **EFA 路径**：
   - 设帧范围（前后各留缓冲液区；示例用整段 0–385）；
   - 在 Forward/Backward 图上把起点拖到"奇异值首次快速上升 / 落回基线"处（示例 Forward 147、164、322；Backward 383、360、200）；
   - 在 Component Range Controls 微调各区间（示例最终 142–198 / 161–322 / 319–360），直到 **χ² 均匀接近 1、无大尖峰**；
   - 走**三步复核**（区间对应起点、χ²≈1、取消 C>=0 后浓度不变）；
   - 关掉 "Start with previous results" 做**最终运行**。
   完成标准：三步复核全过，且最终运行未使用前次结果。判停点：找不到让 χ² 变平的区间 → 回查分量数，或考虑改用 REGALS。
6. **REGALS 路径**：
   - 选实验类型（标准 SEC/IEC → 'IEC/SEC-SAXS'；滴定 → 'Titration'）；
   - 若要背景分量，打开 Background Components 窗口，用"0–100 + 末 100 帧"这类区域估背景分量数，设 "# Significant SVs"；
   - 定 Forward/Backward 起点与各分量区间（chi² 出现尖峰=区间限制过度，往外放）；
   - 逐分量关 Auto lambda：强分量设 0，缓冲分量每次**乘一个数量级**，直到**高 q 背景趋同 + 某分量 profile 突变**=过平滑，回调 last good value（示例 ~4e8）；
   - 每次改动**手动 Run REGALS**（按钮黄底=结果未更新）；
   - 滴定数据额外：Calibrate X axis（首点 log 问题改非零）、设各分量 Dmax（Shannon 限 & χ²/P(r) 收敛）。
   完成标准：χ² 维持 ~1、浓度曲线不再明显变化，且每次改动都重新 Run 过。
7. **交付与记录**：
   - 保存分析数据：EFA 用 "Save EFA Data (not profiles)"（存 SVD、Forward/Backward、χ²、浓度、区间与旋转方法）；REGALS 用 "Save REGALS data (not profiles)"（存储分量设置、浓度、χ²、P(r)、平滑浓度曲线）。
   - Done 把各分量散射曲线送到 Profiles Plot（标签 _0/_1/_2…）。
   - 记录分量数、各分量区间、lambda/Dmax、实验类型——别人要凭这些重放你的分解。
   完成标准：分析数据 .csv 已存，且记录里能说清"为什么是这几个分量"。
8. **写结论**：用其它方法或生化数据佐证，并把佐证写进结论（官方明说本方法结果**必须**被支持）。
   完成标准：报告里对每个分量给出"数对 + χ² 平 + 去正性约束不变 + 外部佐证"中最少可得的证据链。

## B — 边界 (Boundary)

**不要用的场景**

- 峰其实没有重叠、只要"一条曲线" → 走 `process-sec-saxs-series`。
- 还没选好 buffer/sample 区 → 先在那边定区间，再回来分解。
- 要做**基线校正**（扣减后仍有系统性漂移）→ 走 `correct-sec-saxs-baseline`；且**做 EFA 就不要叠加基线校正**（与 `Integral` 尤其冲突：分解算法会把校正引入的单调变形当成一个组分）。
- 问"这条分量曲线的 Rg 是多少、信不信得过" → 转 `assess-guinier-fit-quality`。
- **多序列精修**（时间校准、q 裁剪/rebin、排除帧、帧合并）与 **WAXS 合并**不在覆盖范围。

**源里明确警告过的失败模式**

- **直接采信自动判定的分量数**：RAW 会数错；改范围/类型后它**不会**自动更新（s2_efa/s2_regals 两处 note 都写）。
- **用 "Start with previous results" 做最终运行**：会引入路径依赖、不可复现（s2_efa 第 18 步；REGALS 的 Dmax 迭代也用同一坑）。
- **REGALS 改完不 Run**：REGALS 不自动更新，按钮黄底才表示结果未更新；把旧结果当新结果（s2_regals 第 17 步）。
- **一味增大缓冲分量 lambda**：过平滑会让高 q 背景先趋同、某分量 profile 随后剧变，必须回退（s2_regals 第 22–23 步）。
- **相信浓度峰的绝对高度**：各峰都归一化到面积 1，高度是任意的（s2_efa 第 17 步 note）。
- **把去卷积结果当唯一证据**：旋转不保证成功，结果必须被其它方法/生化数据支持（s2_efa 第 15 步）。

**材料盲点（阶段 0 批判）**

- 官方只给"怎么把这两条曲线拆开"，**不给"这叠在一起的物种在物理上存不存在"的上位判据**——那要靠先验知识/正交实验，本 skill 不能替代。
- **lambda 没有通用最优值**：文档只给"按数量级调"的原则和本例的 ~4e8；换数据必须自己扫。
- **分量区间没有自动确定法**：Forward/Backward 是人工拖的，官方承认"确定起止点的算法并不特别先进，有的数据集需要更多调整"。
- 官方 API 里 EFA/REGALS **不替你选区间**——无 GUI 时这些数必须由你给出。
- 边界声明：本 skill 的方法论与数字**绑定 RAW 2.4.2**；界面文字、默认区间随版本变化，以程序自带 `docs/` 或在线文档为准。

**参考文件**：方法阶梯选择表、四步调参（分量数 → 区间 → lambda → 关路径依赖的最终运行）、复核清单、官方示例数字见
`references/deconvolution-workflow.md`。Series / 三档图 / 界面控件见 `../process-sec-saxs-series/references/sec-saxs-series-workspace.md`。API 入口（`raw.svd/efa/regals` 与 REGALS 组件字典）见 `../script-raw-with-the-python-api/references/rawapi-function-inventory.md`。

## 相关 skills

- **process-sec-saxs-series** — `depends-on`（本 skill 依赖对方）：必须先有一条扣减好的 series 与选好的帧范围，分解才有对象；第 1 步的判停会退回去。
- **correct-sec-saxs-baseline** — `contrasts-with`（本 skill 指向对方）：基线校正与 EFA 不兼容（要做 EFA 就别做基线校正）；REGALS 处理斜基线的能力是它自己的背景分量建模，不等于先做校正。
- **assess-guinier-fit-quality** — `composes-with`（本 skill 指向对方）：本 skill 产出各分量曲线，Rg/I0 判读归那边。
- **script-raw-with-the-python-api** — `composes-with`（本 skill 指向对方）：要把分解变成可复现脚本时用 `raw.svd` / `raw.efa` / `raw.regals`；但无 GUI 时分量区间要自己给。
