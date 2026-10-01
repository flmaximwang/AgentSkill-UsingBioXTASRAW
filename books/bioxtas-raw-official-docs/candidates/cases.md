# candidates/cases.md — 案例提取器（视角 3：官方亲自做过的实例）

源：**BioXTAS RAW v2.4.2 官方文档全站**（`40-tutorial` 37 节 / `30-saxs` 5 节 / `50-api` 11 节 / `00-root` 索引）。
证据分级：`40-tutorial`（操作权威）> `50-api` = `30-saxs` > `00-root`；`20-manual` 为 A 级（自承过时），**不作依据**。
`source_quote` 一律为**语料逐字原文（英文）**，多段以 ` … ` 连接；每条 ≤150 字。`summary`/数字为中文转述，数字逐字照抄不得改动。
案例本身不独立成 skill，用于 V1 跨域证据与 A1 素材。切片标识：`p3`。
`landing`：`new` = 需要新 skill；`extend:<skill>` = 可并入现有 skill。

现有 skill 目录（`landing` 的可选目标）：
`reduce-saxs-frames-to-curves`、`configure-bioxtas-raw-for-a-dataset`、`assess-guinier-fit-quality`、
`process-sec-saxs-series`、`correct-sec-saxs-baseline`。

---

```yaml
- id: a01
  title: GI 0.47 mg/ml 十帧图像积分后应得 20 条曲线
  type: case
  source_chapter: 40-tutorial.md · s1_basic.rst（Section 1 Part 1）
  source_quote: |
    "These files are measured scattering from 0.47 mg/ml GI. … you should see twenty scattering profiles in the profiles list"
  summary: |
    遇到的问题：手上是 CHESS G1 的一批 2D 帧，不知道积分后列表里该出现多少条曲线才算载对。
    怎么用：选 GI2_A9_19_001_xxxx.tiff（xxxx=0000..0009，共 10 帧）→ Plot 积分；同样绘匹配 buffer GIbuf2；
    进 Profiles 控制页签核对 Checkpoint。
    结论：官方给的实例判据是——10 帧 GI + 10 帧 buffer 积分后，Profiles 列表应有 twenty(20) 条曲线，
    文件名形如 GI2_A9_19_001_0000.tiff / GIbuf2_A9_18_001_0000.tif；GI 浓度 0.47 mg/ml。
    两个数字（10 帧/样品、20 条总数）就是"积分有没有漏"的参照。
  landing: extend:reduce-saxs-frames-to-curves
  tags: [case, reduction, glucose-isomerase, g1]
```

```yaml
- id: a02
  title: lysozyme 4.27 mg/ml——扣背景后得到 S_ 曲线的第二个样品
  type: case
  source_chapter: 40-tutorial.md · s1_basic.rst
  source_quote: |
    "The concentration of this sample was 4.27 mg/ml."
  summary: |
    遇到的问题：GI 之外还要再走一个"载图→平均→扣背景"循环，验证流水线可重复。
    怎么用：载 lys2 与 lysbuf2 → 各平均 → star buffer + 选样品 → Subtract → 得到红色 S_ 曲线 → 存 .dat。
    结论：官方示例里 lysozyme 样品浓度 4.27 mg/ml；这条曲线是后续 Guinier/MW/Kratky 三节的共同输入，
    也是"4.27 mg/ml → 14.3 kDa"这条 MW 校验链的起点。
  landing: extend:reduce-saxs-frames-to-curves
  tags: [case, reduction, lysozyme]
```

```yaml
- id: a03
  title: GI 的 Guinier：n_min=8、q_max·Rg≈1.32、文献 Rg=32.7 Å
  type: case
  source_chapter: 40-tutorial.md · s1_guinier.rst
  source_quote: |
    "In the "Control" panel, you’ll see that n_min is 8. … note that q_{max}R_g is ~1.32 … The literature radius of gyration for GI is 32.7 Å."
  summary: |
    遇到的问题：要从扣背景曲线里读出 Rg，得先判断自动选区和拟合上界对不对。
    怎么用：右击曲线 → Guinier fit → 看 Control 面板 n_min 默认 8 → 观察最低 q 点的凹陷，
    用箭头把 n_min 下调几点看 Rg 是否变化，之后回到 8 → 在 Parameters 面板把 n_max 下调到 q_max·R_g≈1.3。
    结论：官方实例的三个参照数——n_min 默认 8；GI 实测 q_max·R_g≈1.32（球状蛋白典型 ~1.3）；
    文献 Rg=32.7 Å，用来和拟合出的 Rg 对比。
  landing: extend:assess-guinier-fit-quality
  tags: [case, guinier, glucose-isomerase, quality-control]
```

```yaml
- id: a04
  title: 两个标样的预期分子量：GI 172 kDa、lysozyme 14.3 kDa
  type: case
  source_chapter: 40-tutorial.md · s1_mw.rst
  source_quote: |
    "enter the sample concentration of 0.47 mg/ml. … The expected MW value for GI is 172 kDa. … The expected MW of lysozyme is 14.3 kDa."
  summary: |
    遇到的问题：六种 MW 方法一次性算出好几个数，怎么知道哪个可信。
    怎么用：右击曲线 → Molecular weight → 在浓度框里填浓度 → 四个（装 ATSAS 则六个）面板同时出结果；
    GI 填 0.47 mg/ml，lysozyme 填 4.27 mg/ml。
    结论：官方给的预期值是——GI 172 kDa（0.47 mg/ml）、lysozyme 14.3 kDa（4.27 mg/ml）。
    这两个数就是判断各 MW 方法是否给出合理量级的锚点。
  landing: new
  tags: [case, molecular-weight, calibration-anchor]
```

```yaml
- id: a05
  title: 无量纲 Kratky 的球状蛋白判据：峰位 1.73、峰高 1.1
  type: case
  source_chapter: 40-tutorial.md · s1_kratky.rst
  source_quote: |
    "peak position should be at qR_g=\sqrt{3}\approx 1.73, while peak height should be 3/e\approx 1.1"
  summary: |
    遇到的问题：想用 Kratky 图区分"完全折叠"与"有柔性"。
    怎么用：选全部曲线 → 右击 → Dimensionless Kratky Plot →（缺 Guinier 结果时点 Proceed using AutoRg）
    → 在 Plot 下拉切 Dimensionless Rg / Normalized / Dimensionless Vc。
    结论：官方在图里画了两条灰色参考线，并给出具体数——球状蛋白无量纲 Kratky 峰位应在
    qR_g=√3≈1.73、峰高 3/e≈1.1。偏离这两条线就是柔性/无序的信号。
  landing: extend:assess-guinier-fit-quality
  tags: [case, kratky, flexibility, threshold]
```

```yaml
- id: a06
  title: SEC 三个区间的具体帧号：buffer 504–562、sample 699–713、第二 buffer ~840–896
  type: case
  source_chapter: 40-tutorial.md · s1_sec.rst
  source_quote: |
    "Reset the buffer range to 504 to 562 … Once you are satisfied with the region picked (should be 699-713) … A range like ~840-896 is reasonable."
  summary: |
    遇到的问题：LC Analysis 里要手动指认哪些帧是缓冲液、哪些是样品，没有唯一答案。
    怎么用：Buffer 区点 Auto 得绿色区间 → 改成 504-562 → Set buffer；Sample 区 Auto → 应落在 699-713 → To Profiles Plot；
    遇到第二个 buffer（双 buffer 情形）→ Add region → Pick → ~840-896 → Set buffer → 警告处点 Continue。
    结论：官方示例的帧号区间就是"选对了"的参照：buffer 504–562、sample 699–713、第二 buffer ~840–896。
    故意把 buffer start 改 450 或 sample start 改 680 都会触发 RAW 的区间校验警告。
  landing: extend:process-sec-saxs-series
  tags: [case, sec-saxs, frame-selection]
```

```yaml
- id: a07
  title: BSA 的预期 Rg~28 Å / MW~66 kDa 与 series scale 1800
  type: case
  source_chapter: 40-tutorial.md · s1_sec.rst
  source_quote: |
    "For BSA, we expect |Rg ~28 Å and MW ~66 kDa. … Set the scale to 1800 and click "OK"."
  summary: |
    遇到的问题：两条 series 强度不在一个量级，且要判断扣背景后参数是否合理。
    怎么用：右击 profile_001 → "Adjust scale, offset, q range" → scale 设 1800（作用于整条 series）；
    隐藏 profile_001，用 buffer 区算出 BSA 的 Rg/MW。
    结论：官方给出的实例值——profile_001 的 scale 取 1800；BSA 预期 Rg~28 Å、MW~66 kDa。
    这是一条"参数算出来对不对"的独立校验线（SEC-SAXS 的 I(0) 参考与绝对校准本身不准）。
  landing: extend:process-sec-saxs-series
  tags: [case, sec-saxs, bsa, scale]
```

```yaml
- id: a08
  title: GNOM：Auto Dmax 应 102（试 80–110）、截断后 q_max 0.283→0.238
  type: case
  source_chapter: 40-tutorial.md · s2_gnom.rst
  source_quote: |
    "Try varying the |Dmax value up and down in the range of 80-110. … |Dmax should be 102. … The q\ max goes from 0.283 to 0.238 when you check the box."
  summary: |
    遇到的问题：GNOM 要输入 Dmax，而 Dmax 是 IFT 最主观的一个参数。
    怎么用：右击 glucose_isomerase.dat → IFT (GNOM) → 先在 80-110 之间上下试 Dmax 看 P(r) 是否自然趋零
    → 点 Auto Dmax 回到自动值 → 若要给 DAMMIF/N 用，勾 "Truncate for DAMMIF/N"（q_max 取 8/Rg 或 0.30 中较小者）。
    结论：官方实例值——本例 Auto Dmax 应得 102；勾截断后 q_max 由 0.283 降到 0.238；
    DENSS 电子密度重建时反而要用全 q 范围、不要截断。
  landing: new
  tags: [case, gnom, dmax, ift]
```

```yaml
- id: a09
  title: DIFT 的 Auto Dmax 应 115；BIFT 找到 ~100，与 GNOM 一致
  type: case
  source_chapter: 40-tutorial.md · s2_dift.rst / s2_bift.rst
  source_quote: |
    "|Dmax should be 115. … BIFT has found a |Dmax value around 100"
  summary: |
    遇到的问题：同一份 GI 数据有三种 IFT 方法，想知道它们给的 Dmax 该不该一致。
    怎么用：DIFT——右击曲线 → IFT (DENSS) → 在 80-120 之间试 → Auto Dmax；改 q 范围后要点 Scan Alpha。
    BIFT——右击 → IFT (BIFT)，Dmax 由方法自动定（改了 q 范围必须按 Run 重跑）。
    结论：官方实例值——同一份数据 DIFT 的 Auto Dmax 应得 115；BIFT 自动找到 ~100，
    文档明说这与 GNOM 的结果 in good agreement。三个数（GNOM 102 / BIFT ~100 / DIFT 115）可互为 sanity check。
    另注：BIFT 输出不兼容 DAMMIF/ATSAS，但兼容 DENSS。
  landing: new
  tags: [case, dift, bift, dmax, cross-check]
```

```yaml
- id: a10
  title: 珠模型重构：教程跑 5 次，官方建议 15–20 次、论文用 Slow
  type: case
  source_chapter: 40-tutorial.md · s2_dammif.rst（30-saxs.md 同源）
  source_quote: |
    "It is generally recommended that you do 15-20 reconstructions. … For final reconstructions for a paper, DAMMIF should be run in Slow mode."
  summary: |
    遇到的问题：DAMMIF/N 每次结果都不一样，跑几次才算数、用哪个模式。
    怎么用：IFT 列表右击 → Bead Model (DAMMIF/N) → 建输出目录 → 设重构数 → Fast 快速试、Slow 出终稿
    → 取消 Refine with dammin → 勾 Align 到 1XIB_4mer.pdb → Start。
    结论：官方数字——教程为省时间把重构数改成 5，但明确写 generally recommended that you do 15-20 reconstructions；
    30-saxs 方法页同样写生成 10-20 个、推荐 15 个，并且终稿要用 Slow 模式。
    即：5 是演示值，15-20/Slow 才是出结果的配置。
  landing: new
  tags: [case, dammif, bead-model, reconstruction-count]
```

```yaml
- id: a11
  title: DENSS：教程跑 5 次重建，官方建议 ≥20 次；分辨率取 FSC 首次过 0.5 的 Å
  type: case
  source_chapter: 40-tutorial.md · s2_denss.rst
  source_quote: |
    "It is generally recommended that you do at least 20 reconstructions. … the resolution in angstroms where the correlation first crosses 0.5"
  summary: |
    遇到的问题：电子密度重建（DENSS）同样有跑几次、怎么读分辨率的问题。
    怎么用：IFT 列表右击 → Electron Density (DENSS) → 设输出目录与重构数、模式 → Start → 看 Results 里的 FSC 曲线
    → 检查各模型 chi²/Rg/support volume 是否收敛。DENSS 用全 q 范围（.ift 或 _full.out，别用被截断的 .out）。
    结论：官方数字——教程用 5 次，但 generally recommended that you do at least 20 reconstructions、论文用 Slow；
    重建分辨率定义为 correlation 首次降到 0.5 所对应的 Å 数。
  landing: new
  tags: [case, denss, fsc, reconstruction-count]
```

```yaml
- id: a12
  title: EFA 的自动判分量（3 个 SV）与 Forward/Backward 起点具体帧号
  type: case
  source_chapter: 40-tutorial.md · s2_efa.rst
  source_quote: |
    "RAW thinks there are three significant SVs … This should be around 147, 164, and 322. … This should be around 383, 360, and 200."
  summary: |
    遇到的问题：重叠峰里到底有几个散射组分，EFA 的 Forward/Backward 起点该点在哪。
    怎么用：载 phehc_sec.hdf5 → 右击 series → EFA → 帧范围用 0-385（Subtracted，buffer 前后各留一段）
    → 读 RAW 自动判定的显著 SV 数 → 在 Forward EFA 图上把起点拖到奇异值开始快速上升处，
    在 Backward EFA 图上拖到落回基线处。
    结论：官方实例值——本例 RAW 自动判 3 个显著 SV（文档说 that is accurate）；
    Forward 起点应为 147、164、322；Backward 起点应为 383、360、200。
  landing: new
  tags: [case, efa, svd, deconvolution]
```

```yaml
- id: a13
  title: EFA 终解区间 142–198 / 161–322 / 319–360（对照 RAW 默认 151–193 / 164–322 / 319–347）
  type: case
  source_chapter: 40-tutorial.md · s2_efa.rst
  source_quote: |
    "Range 0 should be about 142 to 198, Range 1 from 161 to 322, and Range 2 from 319 to 360."
  summary: |
    遇到的问题：EFA 转动后 chi² 出现尖峰，说明分量区间选错了。
    怎么用：先把 Component Range 设回 RAW 默认值（151-193、164-322、319-347）看 chi² 尖峰 →
    再微调 Range 0/1 的起止与 Range 2 的终点，直到 chi² 变平。
    结论：官方实例值——调好后 Range 0 应约 142-198、Range 1 为 161-322、Range 2 为 319-360；
    判据是 chi-squared plot 应 close to 1、without any major spikes，且最终运行必须关掉
    Start with previous results（否则有路径依赖偏差）。
  landing: new
  tags: [case, efa, component-range, chi2]
```

```yaml
- id: a14
  title: IEC-SAXS 的 REGALS：4 个显著 SV，Forward 0/350/750/1195、Backward 700/1325/1600/1736
  type: case
  source_chapter: 40-tutorial.md · s2_regals.rst
  source_quote: |
    "RAW thinks there are four significant SVs (scattering components) in our data. … This should be around 0, 350, 750, and 1195."
  summary: |
    遇到的问题：离子交换（盐梯度）数据的 buffer 背景在变，需要 REGALS 解卷积，但起点难定。
    怎么用：载 nrde_iec.hdf5 → 右击 series → REGALS → 实验类型默认 'IEC/SEC-SAXS' → 保留 Use EFA → Next
    → 在 Forward/Backward 图上拖起点 → Next → 调分量区间 → Run REGALS。
    结论：官方实例值——本例 RAW 自动判 4 个显著 SV（文档说 that is accurate）；
    Forward 起点应为 0、350、750、1195；Backward 起点应为 700、1325、1600、1736。
    同节还给了背景分量区（先 Add Region 0-100，再加最后 100 帧，# Significant SVs 设 1）。
  landing: new
  tags: [case, regals, iec-saxs, deconvolution]
```

```yaml
- id: a15
  title: REGALS 调参三例：comp3 起点 1150→1125→1100→回 1125；缓冲 lambda 过平滑点 ~4e8
  type: case
  source_chapter: 40-tutorial.md · s2_regals.rst
  source_quote: |
    "set the start of component 3 to 1150 and run REGALS. … Try 1125 and 1100 for the component 3 start. … the last good value, which would be ~4e8"
  summary: |
    遇到的问题：REGALS 的结果对分量区间与 lambda 很敏感，怎么判"调够了"。
    怎么用：comp3 起点由 1150 → 试 1125、1100（结果差别很小）→ 回到 1125；comp2/3 浓度关 Auto lambda 设 0；
    缓冲分量 0/1 关 Auto lambda 后每次把 lambda 乘一个数量级，直到高 q 背景突变或 comp1 profile 剧变=过平滑。
    结论：官方实例值——comp3 最终起点定 1125；缓冲分量 lambda 的 last good value 约 4e8；
    另有 comp2 浓度终点由 1300 试到 1275。判据是 chi² 图应维持 ~1、浓度曲线形状不再明显变化。
  landing: new
  tags: [case, regals, lambda, tuning]
```

```yaml
- id: a16
  title: 滴定 REGALS：16 个浓度点（0–80 mM）、首点改 10.0、聚集体 Dmax=300、两构象 Dmax=130
  type: case
  source_chapter: 40-tutorial.md · s2_regals.rst
  source_quote: |
    "16 different concentration points were collected, ranging from 0 to 80 mM L-phe. … we want to pick a |Dmax value near 130"
  summary: |
    遇到的问题：滴定量热（batch）序列点少、又含聚集体，常规 EFA 不适用。
    怎么用：载 pheh_titration.hdf5 → REGALS → # Significant SVs 设 3（RAW 自动找到 4，实测 ~4-5）
    → 实验类型 Titration → 取消 Use EFA → Calibrate X axis 载 pheh_titration_conc.txt
    → Use for X axis 选 Log10(X) → 设各分量 Dmax → Run REGALS。
    结论：官方实例数字——16 个浓度点、0 到 80 mM L-phe；因 log(0) 未定义，首点浓度由 0 改 10.0（µM）；
    聚集体（component 2）Dmax 设 300（Shannon 限 Dmax<π/q_min，据 q 范围最大可测 ~300 Å）；
    两构象 Dmax 从 110 起步、每步加 10-20 到 160，其中 ~130-150 chi² 稳定、>~120 P(r) 不再被压零、
    160 时 chi² 上升，最终取 130（与先前分析一致）。
  landing: new
  tags: [case, regals, titration, dmax]
```

```yaml
- id: a17
  title: 多序列文件名模板：Series# 1–90 / pad 4、Profiles# 1–40 / pad 5、Cal offset 71.13
  type: case
  source_chapter: 40-tutorial.md · s2_multiseries.rst
  source_quote: |
    "enter *cytc_01_005_<s>_data_0<f>_<f>.dat* … Enter 71.13 for this value."
  summary: |
    遇到的问题：时间分辨实验有 90 条 series × 40 个 profile，文件名里哪几位是 series 号、哪几位是 profile 号。
    怎么用：Tools → Multi-Series Analysis → Browse 到 cytc_01 → 文件名栏填模板 → 填 Series#/Profiles# 及零填充位数
    → Select files → 定 buffer/sample 区 → Next → 载入时间校准 csv（time_8_ml_min.csv）。
    结论：官方实例值——文件名模板 *cytc_01_005_<s>_data_0<f>_<f>.dat*；Series # 填 1 与 90、zero pad 4
    （1 写成 0001、10 写成 0010）；Profiles # 填 1 与 40、zero pad 5（1 写成 00001）；
    Cal. input key 选 x、Cal. output key 填 time、Cal offset 填 71.13（x 轴随之变成 ms）。
  landing: new
  tags: [case, multi-series, time-resolved, filename-template]
```

```yaml
- id: a18
  title: 细胞色素 c 折叠：Rg 从 ~23–24 Å 降到 ~18–19 Å，最早时点 45 微秒
  type: case
  source_chapter: 40-tutorial.md · s2_multiseries.rst
  source_quote: |
    "there's a gradual change from an |Rg of ~23-24 Å to an |Rg| … of ~18-19 Å over the measured timepoints … our earliest timepoint (45 microseconds)"
  summary: |
    遇到的问题：混流时间分辨数据要判断时间点是否过采样、以及数据能回答什么问题。
    怎么用：看 Rg vs time 曲线 → 若变化平缓就勾 Rebin series、Series bin factor 设 2（时点数减半、信噪改善）；
    悬停 Rg 首点记帧号 → 在 Exclude profiles 里排除异常帧。
    结论：官方实例值——cytochrome c 复性过程中 Rg 由 ~23-24 Å 逐渐变到 ~18-19 Å（无快速变化，故可 bin）；
    完全变性态 Rg~31 Å、下一个中间态 Rg~24 Å；本数据集最早时点为 45 微秒，
    而文献 SAXS 折叠研究最早约 150 微秒——官方据此判断这份数据没能捕捉到更快的塌缩相。
  landing: new
  tags: [case, multi-series, time-resolved, cytochrome-c, rg]
```

```yaml
- id: a19
  title: 绝对刻度的三个基准常数：水 4 C→~0.00077、玻碳 Simple→~324、玻碳 NIST→~198
  type: case
  source_chapter: 40-tutorial.md · s3_abswater.rst / s3_abscarbon.rst
  source_quote: |
    "You should get a value near 0.00077. … You should get about 324. … You should get an absolute scaling constant near 198."
  summary: |
    遇到的问题：要把强度从任意刻度换成绝对刻度，但算出来的常数对不对无从判断。
    怎么用：水——载 SAXS.cfg，平均 MT2 与 water2，Absolute Scale 里 Empty cell=A_MT2_48_001_0000.dat、
    Water sample=A_water2_49_001_0000.dat、Water temperature 设 4 C → Calculate。
    玻碳 Simple——Glassy carbon Set=A_glassy_carbon2_011__0001.dat、Sample thickness 设 1.0 mm → Calculate。
    玻碳 Full(NIST)——清空 Normalization 列表、关掉已有绝对刻度，Set glassy carbon / 其背景 / 样品背景，
    Sample thickness 设 1.5 mm、Upstream counter 选 I1、Downstream counter 选 I3 → Calculate。
    结论：官方给出的"应该得到"的常数——水（4 C）≈0.00077；玻碳 Simple（1.0 mm）≈324；
    玻碳 NIST 法（1.5 mm，I1/I3）≈198。三条是校准链是否接对的独立校验点。
  landing: extend:configure-bioxtas-raw-for-a-dataset
  tags: [case, absolute-scale, water, glassy-carbon, calibration]
```

```yaml
- id: a20
  title: 定心/标定与归一化：Energy 12.0 keV、pixel 172.0×172.0 micron、AgBh；归一化 /I1 得 7200.0
  type: case
  source_chapter: 40-tutorial.md · s3_autocenter.rst / s3_normalization.rst
  source_quote: |
    "set the Energy to 12.0 keV. Verify that the Detector Pixel Size is 172.0 x 172.0 micron. … Verify that the standard is set to AgBh."
  summary: |
    遇到的问题：几何标定与归一化都靠数值核对，填错了不会报错但 q 轴/强度全错。
    怎么用：Centering/Calibration——显示 agbe 图（对数标度）→ Tools → Centering/Calibration → 填 Energy、
    Detector Pixel Size、Detector、standard → Start → 在图上依次点 Ring# 0/1/2 的强点 → Done。
    Normalization——Advanced Options 载 agbe_008_0001.tif → Apply → 左侧选 "/"、大字段填 I1 → Calc。
    结论：官方实例值——Energy 12.0 keV、Detector Pixel Size 172.0 x 172.0 micron、Detector "pilatus_1m"、
    standard AgBh；归一化表达式 "/" 对 I1 求值应得 7200.0；随后把 q Min 调到曲线峰（约 point 13）作为径向积分起点。
  landing: extend:configure-bioxtas-raw-for-a-dataset
  tags: [case, calibration, normalization, agbh]
```

