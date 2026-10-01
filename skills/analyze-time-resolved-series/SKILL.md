---
name: analyze-time-resolved-series
description: "时间分辨/多序列 SAXS 精修（一批 series 要一起逐点平均与扣减）：多 series 载入（文件名模板 <s>/<f> + 零填充）→ 跨 series 定 buffer/sample 区 → 逐点平均与扣减 → 时间校准（Load Calibration：x→time + offset）→ q 裁剪/rebin → 排除帧 → Rebin series 降噪（时点数减半，帧号报段首帧）；含判据（低 q 常为寄生散射、最高 q 约半数点为负=无信号、单次测量 S/N 常不足、建议 ≥3 次测量）与设置存 json 复用。用于「时间分辨数据怎么一起平均」「Rg 曲线第一个点是 0」「低 q 是负的 / 最高 q 一堆负点」「rebin 后帧号为什么报段首帧」「cytc 多 series 分析」「设置怎么套到新数据」；不负责单条 SEC 系列（转 process-sec-saxs-series），也不做 SVD/EFA/REGALS 分解。"
source_book: BioXTAS RAW 官方文档 v2.4.2 · *Multi-series (time resolved) analysis*（教程，`tutorial/s2_multiseries.rst`）
source_chapter: tutorial/s2_multiseries.rst 全篇
tags: [saxs, bioxtas-raw, multi-series, time-resolved, rebin, calibration]
related_skills:
  - slug: process-sec-saxs-series
    relation: contrasts-with
  - slug: reduce-saxs-frames-to-curves
    relation: depends-on
---

# 一批 series 一起精修：先接上时间轴，再降噪，再排除坏帧

时间分辨（或浓度梯度）数据的处理对象不是"一个 series"，而是**多个 series 在每个时点上同时平均**。整条流水线只有一条判据贯穿始终：**"这个 q 范围 / 这个时点里还有没有信号？"**——低 q 的负值可能是寄生散射，高 q 的半数负点是"没信号"，首帧可能是混合器边缘的假信号。

## R — 原文 (Reading)

> "...loading in multiple series at once and carrying out point-by-point averaging and subtraction across series."
> [FILE: tutorial/s2_multiseries.rst]

> "further data refinement including truncating and binning q ranges, ... removing particular profiles from the series, and calibrating the series."
> [FILE: tutorial/s2_multiseries.rst]

> "A calibration file should consist of two columns in csv format. The first column is the input value and the second the output value."
> [FILE: tutorial/s2_multiseries.rst]

> "The 'Cal offset' field allows you to provide an offset value that will be added to the value from the profile header"
> [FILE: tutorial/s2_multiseries.rst]

> "Because of strong parasitic scattering from the mixer window at some positions, the usable q range does not necessarily extend to the lowest q point"
> [FILE: tutorial/s2_multiseries.rst]

> "look for the q range where about half the data points are negative, indicating the sample signal is not significantly above the background."
> [FILE: tutorial/s2_multiseries.rst]

> "A single time resolved measurement doesn't always yield great signal to noise data."
> [FILE: tutorial/s2_multiseries.rst]

> "Typically, at least 3 such measurements are made for a given sample."
> [FILE: tutorial/s2_multiseries.rst]

> "Check the 'Rebin series' box and set the 'Series bin factor' to 2. This will average together every two adjacent profiles."
> [FILE: tutorial/s2_multiseries.rst]

> "The frame number is reported as the first frame number of the averaged profiles, e.g. an average of profiles 1 and 2 will report frame 1"
> [FILE: tutorial/s2_multiseries.rst]

> "there's a gradual change from an Rg of ~23-24 Å to an Rg of ~18-19 Å over the measured timepoints, but there is no fast change observed"
> [FILE: tutorial/s2_multiseries.rst]

> "rapid collapse seems to be faster than our earliest timepoint (45 microseconds)"
> [FILE: tutorial/s2_multiseries.rst]

## I — 骨架 (Interpretation)

与 `process-sec-saxs-series`（单条 series，在帧号轴内选区间）的根本差别：**这次是在"series 轴"上做选择**——每个 series 整体被声明为 buffer 或 sample，然后**跨 series 逐点平均**。一段话概括骨架：

**载入多 series（文件名模板 + 编号/补零）→ 跨 series 定 buffer/sample 区 → 逐点平均并扣减 → 接时间轴（校准）→ q 裁剪/rebin → 排除坏帧 → Rebin series 降噪。**

七条不可交换的操作性结论：

1. **载入靠文件名模板，不靠逐个挑文件。** 模板里有两个变量：series 号 `<s>`、profile 号 `<f>`，还要给各自的取值范围与**零填充位数**（`<s>` 用 pad4 → 1 写成 0001；`<f>` 用 pad5 → 1 写成 00001）。命名约定**随设施不同**，必须先弄清自己数据里哪几位是 series、哪几位是 profile。
2. **buffer/sample 区定义在 series 层，不是 profile 层。** 与 LC Analysis 不同：这里说"某条 series 整条是 buffer / sample"。buffer 区通常取**样品注入前 + 注入后**两段（后段因注入拖尾常取小一些）。
3. **扣减是"逐点平均后再相减"**：RAW 对 buffer 区各 series 的同一 profile 号求平均、对 sample 区同样求平均，再相减，得到**每个时点一条**扣减曲线；随后自动算逐点 Rg/MW。
4. **时间轴要靠校准接上，且需要两样东西**：① profile 文件头里有一个可校准的键（本例是束在混合器上的位置 `x`）；② 一份两列 CSV（第一列输入值、第二列输出值，`#` 开头为注释行）。另给 **Cal offset**（加到文件头值上，本例 = 混合区在 x 上的实测位置），最终 `cal_val = f(input+offset)`。
5. **q 两端都要裁**：
   - **低 q**：混合器窗口在部分位置有强寄生散射 → 最低 q 常有负值/下凹，可用 q 范围**未必延伸到最低 q 点**。做法是逐时点看曲线，把 q_min 抬到信号干净处（本例 0.01 → 0.015）。高信噪场合**很少能拿到 ~0.01 1/Å 以下的可用低 q**。
   - **高 q**：找"**约半数数据点为负**"的地方——按噪声统计，当样品与 buffer 的未扣减曲线重合（无信号）时，扣减后恰好一半点略负、一半略正。那里就是可用 q 的上界（本例 ~0.5–0.55 1/Å）。
6. **排除坏帧要看帧号、必要时看图像**：首帧常因贴近混合器边缘而有额外散射（本例排除 frame 0）；某时点也可能有灰尘造成的强背景。**"不能只靠扫曲线看出来"**——必要时回看该时点的 2D 图像。排除多个帧用逗号列表（如 `0,5,15,30`）。
7. **Rebin series 是"降噪换时间分辨率"**：只有当数据**明显过采样**、且 Rg 变化平缓（没有快过程）才做；`Series bin factor = 2` 把每两个相邻 profile 平均，**时点数减半**。此时**帧号报的是该段首帧**（profile 1 与 2 平均 → 报 frame 1），时间值取被平均各点的平均——不这样理解会把时点报错。

一句话判据：**"这个时点/这个 q 里，信号到底有没有高于背景？"** 答不上来就不要把它算进结果。

## A1 — 案例 (Past Application)

**1. `cytc` 时间分辨：90 条 series × 40 个 profile**（a17；源 `tutorial/s2_multiseries.rst`）

- 数据：cytochrome c 复性，微流混合，共 **90 条 series**（每条是一次沿混合通道的扫描）× **40 个时点**。
- 载入：Tools → Multi-Series Analysis → Browse 到 `cytc_01` → 文件名栏填 **`cytc_01_005_<s>_data_0<f>_<f>.dat`**（`<f>` 出现两次，因为文件名里最后两个数字同步递增）→ **Series # 填 1 与 90、zero pad 4**；**Profiles # 填 1 与 40、zero pad 5** → Select files → 核对左栏 90 条 series。
- 定区：buffer 区约 **series 1–30 与 70–90**（后段取小以避开注入拖尾），sample 区约 **series 32–44**。
- 校准：Load Calibration → `time_8_ml_min.csv`（距离 mm ↔ 时间 ms）→ **Cal. input key 选 `x`、Cal. output key 填 `time`、Cal offset 填 `71.13`** → Process data，x 轴变成 **ms**。
- 结论：官方示例值就是这条流水线的"标准答案"。

**2. 单次测量不够，要把多次重复平均**（源 `tutorial/s2_multiseries.rst`）

- 现象：单次时间分辨测量的扣减曲线很噪，自动 Rg/MW **算不出来**（cytc 分子小、缓冲液含 0.45 M 胍，对比度低，是"最坏情况"）。
- 做法：把 5 次重复测量的 series 全部载入 → 加一个跨全部 series 的 sample 区 → 勾 **`Calibration in header`** 并选 `time`（校准已在文件头里，无需再算）→ Process data。
- 结果：5 次平均后信噪显著改善，自动方法能在**多数时点**算出 Rg/MW。
- 结论：**"至少 3 次测量"**是有理由的默认；单次测量是否可用取决于分子大小/浓度/缓冲液。

**3. q 裁剪：低 q 寄生、高 q 无信号**（源 `tutorial/s2_multiseries.rst`）

- 低 q：曲线在 ~0.01 1/Å 以下变化大且有负值 → q min 设 0.01 → 仍偏噪 → 设 **0.015**。
- 高 q：切回 Log-lin，找约半数点为负处 → q max 设 **~0.5–0.55 1/Å**。
- 顺手：先做 **q binning**（勾 `Rebin q`，Q bin type `Linear`，Q bin mode `Points`，points **150**）能明显降噪。

**4. 排除首帧 + Rebin series**（a18；源 `tutorial/s2_multiseries.rst`）

- 首帧：悬停 Rg 首个数据点读出**帧号（应为 0）**，在 `Exclude profiles` 填 `0` → 重算后首帧变 1。
- Rebin：Rg 从 **~23–24 Å** 平缓变到 **~18–19 Å**（无快过程）→ 勾 `Rebin series`、`Series bin factor = 2` → 时点数减半，信噪改善。
- 判读：帧号报段首帧；校准值取段内平均。

**5. 设置存 json 再复用**（源 `tutorial/s2_multiseries.rst`）

- 存：Save analysis settings → `cytc_01.json`（含载入模板 + 区间 + 校准）。
- 用：Load analysis settings 载回 → 点 **`Auto select`** 换到 `cytc_03` 文件夹 → 范围默认沿用（本例微调为 buffer 1–30/75–90、sample 32–49）→ **时间校准自动套用**，无需重填。

**6. 这份数据回答了什么问题**（a18）

- 目标：捕捉完全变性态（**Rg ~31 Å**）到下一中间态（**Rg ~24 Å**）之间的 burst phase。
- 结论：**最早时点 45 微秒**，而快速塌缩比它更快；已发表的 cytc SAXS 复性研究最早时点 ~**150 微秒**——所以这份数据没能提供关于更快塌缩相的新信息。这说明"时间轴接对之后，才谈得上科学结论"。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 做的是时间分辨（微流混合、停流）或浓度梯度实验，一批 series 要一起逐点平均/扣减。
- 文件名里 series 号与 profile 号分不清，不知道模板怎么填。
- 扣减后 Rg 曲线的**第一个点是 0**，或整体不可信。
- 低 q 出现负值/下凹，高 q 有一堆负点，不知道 q 范围该裁到哪。
- 想知道 Rebin series 之后**帧号为什么变了**。
- 想把同一套处理设置套到另一批数据上。

**语言信号**

- 「时间分辨数据怎么一起平均 / 多序列分析怎么做」
- 「cytc 那套 90×40 的数据怎么载入」
- 「Rg 曲线第一个点是 0，正常吗」
- 「低 q 是负的 / 最高 q 那边一半点都是负的」
- 「rebin 之后帧号为什么报的是段首帧」
- 「上次的 json 设置怎么套到新数据」

**与相邻 skill 的区别**

- 与 `process-sec-saxs-series`：那边处理**一条** SEC 洗脱 series（在帧号轴内选 buffer/sample 区间）；这里处理**多条** series（在 series 轴上选 buffer/sample，再逐点平均）。判断对象不同。
- 与 `reduce-saxs-frames-to-curves`：那边是批次帧的还原主线（积分/平均/扣减/落盘），是本 skill 的数据来源。
- 与 `correct-sec-saxs-baseline`：本 skill 到"接好时间轴、裁好 q、排好帧的净曲线序列"为止；基线漂移校正不在此列。
- 与 **SVD/EFA/REGALS 分解**：分解在本流水线**之后**（把各时点曲线送出去做分量分析）；本 skill 不做分解。

## E — 执行步骤 (Execution)

1. **确认命名约定**：先看清自己数据里哪几位是 series 号、哪几位是 profile 号。
   完成标准：能写出本设施的文件名模板（含 `<s>`、`<f>` 位置）。判停点：分不清 → 不要盲填，逐文件核对（命名约定随设施不同）。
2. **打开 Multi-Series Analysis 窗**（Tools 菜单），选载入方式：主用 `Select from disk`（目录 + 模板）；也可 `Add from series panel`；BioCAT 等兼容命名可 `Auto select`。
   完成标准：能说清本次用哪种载入方式、为什么。
3. **填目录 + 文件名模板 + 编号/补零**：模板含 `<s>` 与 `<f>`（必要时 `<f>` 出现两次）；填 Series # 起止与 zero pad、Profiles # 起止与 zero pad → `Select files`。
   完成标准：左栏出现预期数量的 series，抽几条核对 profile 号连续。判停点：数量不对 → 回查 ranges 与 pad（如把 4 写成 3 会得到 `001`/`010` 而非 `0001`/`0010`）。
4. **Next → 定 buffer/sample 区（series 层）**：`Add region` 加 buffer 区（通常前 + 后两段）、加 sample 区（数据峰处）。
   完成标准：能说出"哪些 series 整条是 buffer、哪些是 sample"，并解释后段 buffer 为何取小。判停点：数据若已扣减过 → 此步可跳过，直接 Next。
5. **Next → 扣减**：RAW 逐点平均 buffer 与 sample 后相减，得到每时点一条曲线 + 逐点 Rg/MW。
   完成标准：出现"每条时点一条曲线"的窗口；若自动 Rg/MW 算不出，判定为信噪不足（见第 9 步）。
6. **接时间轴**：Load Calibration 载入两列 CSV → Cal. input key 选可校准的键（本例 `x`）→ Cal. output key 填输出名（本例 `time`）→ Cal offset 填混合区实测位置（本例 `71.13`）→ `Process data`。
   完成标准：x 轴变成校准单位（本例 ms），能说出输入键与 offset 的物理含义。
7. **q binning（可选，先降噪）**：勾 `Rebin q`，选 Q bin type（`Linear`/`Log`）与 Q bin mode（`Factor`/`Points`，本例 `Points = 150`）→ Process data。
   完成标准：曲线噪声明显下降。
8. **裁 q 范围**：逐时点看曲线，抬 q_min 到信号干净处（本例 0.01 → 0.015）；切 Log-lin 找约半数点为负的 q 作为 q_max（本例 ~0.5–0.55 1/Å）→ Process data。
   完成标准：能说出"为什么 q_min / q_max 定在这里"（寄生散射 / 无信号判据）。判停点：低 q 全为负且抬高后仍不可用 → 数据在该 q 段不可用，放弃而不是硬留。
9. **必要时先平均多次重复测量**：把重复测量的 series 一起载入 → 加跨全部 series 的 sample 区 → 勾 `Calibration in header` 选 `time` → Process data。
   完成标准：信噪改善到多数时点能算 Rg/MW；单次测量本就够好时不必做。
10. **排除坏帧**：悬停 Rg 首点读出帧号（本例 0）→ 在 `Exclude profiles` 填写（多帧用逗号列表）→ Process data。
    完成标准：图上验证首个可用帧已变。
11. **Rebin series（若过采样）**：勾 `Rebin series`、`Series bin factor = 2` → Process data。
    完成标准：时点数减半；能解释"帧号报段首帧、时间取段内平均"。判停点：存在快过程时**不要** bin（会抹掉变化）。
12. **保存与导出**：Save analysis settings（json）→ 需要时 Load settings + `Auto select` 换数据复用；右键 Rg/I(0)/MW 图 `Export data as CSV`。
    完成标准：json 能复现区间与校准；CSV 含逐时点参数。判停点：若忘了存，可对单条已处理 series 重开窗口、设 sample 区为单条、用 `Calibration in header` 重建图并导出（但无法回退 q/series binning）。

## B — 边界 (Boundary)

**不要用的场景**

- 手上是**一条** SEC 洗脱 series → 走 `process-sec-saxs-series`。
- 一开始就是批次帧（一个样品的 N 帧等条件）→ 走 `reduce-saxs-frames-to-curves`。
- 要做 **SVD / EFA / REGALS** 提取分量 → 那在本流水线之后，是独立决策点，本 skill 不覆盖（REGALS 可用于时间分辨/滴定数据）。
- 扣减后仍有基线漂移 → 走 `correct-sec-saxs-baseline`。
- 实验设计问题（混合器、流速标定 CSV 怎么产生）不在覆盖范围。

**源里明确警告过的失败模式**

- **单次测量信噪不足就下结论**：cytc 教程明确单次可能算不出 Rg/MW；"Typically, at least 3 such measurements are made"。
- **把低 q 负值当成正常数据**：混合器窗口寄生散射会污染低 q，可用范围未必到最低 q 点。
- **在高 q 把无信号区当信号**：约半数点为负就是"没有显著高于背景"的标志。
- **误读 rebin 后的帧号**：帧号报的是被平均段的**首帧**；把它当成"中点/新时点"会报错时间。
- **对存在快过程的数据做 Rebin series**：会抹掉变化（本例之所以能 bin，正是因为 Rg 平缓、无快过程）。
- **只凭扫曲线找坏帧**：教程明说"不能总靠随便看一眼曲线看出来"，必要时看 2D 图像。

**材料盲点 / 版本约束**

- **绑定 RAW v2.4.2**：面板名、`Auto select` 的可用条件（依赖 BioCAT 兼容命名）随版本与线站变化，找不到控件时以程序自带 `docs/` 或在线文档核对。
- 文件名命名约定**没有通用规则**——文档只给"随设施不同，务必先弄清本设施约定"。
- 校准 CSV 本身怎么来（几何/流速）不在文档覆盖内；本 skill 只负责"有了 CSV 怎么接上时间轴"。
- 面板/参数地图、设置 json 字段与 cytc 全套数值见 `references/multi-series-workflow.md`。

## 相关 skills

- **process-sec-saxs-series** — `contrasts-with`（本 skill 指向对方）：同为"造扣减曲线"，但对象不同——**一条洗脱 series**（帧号轴内选物种区间）vs **一批 series**（series 轴上定 buffer/sample 后逐点平均）。
- **reduce-saxs-frames-to-curves** — `depends-on`（本 skill 依赖对方）：多序列处理的输入是还原好的 1D 曲线，其主线（积分/平均/扣减/落盘）在那边。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/BOOK_OVERVIEW.md`。
