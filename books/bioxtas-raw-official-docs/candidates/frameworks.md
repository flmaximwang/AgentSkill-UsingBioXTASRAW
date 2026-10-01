# candidates/frameworks.md — 框架提取器（视角 1：可迁移的流程 / 结构）

源：BioXTAS RAW v2.4.2 官方文档（tutorial / api / saxs / install，B 级）。
语料：`~/.hermes/cache/scratch/rawdocs/{00-root,10-install,20-manual,30-saxs,40-tutorial,50-api}.md`。
纪律：`source_quote` 逐字取自语料（英文原文，可 grep 命中）；A 级 `20-manual` 仅作矛盾对照，不作依据；manual 与 tutorial 冲突处一律采 tutorial。引用 ≤150 字/条。
`landing`：`new` = 建议新建 skill；`extend:<现有 skill 名>` = 并入既有 skill。现有 5 个 skill：`configure-bioxtas-raw-for-a-dataset` / `reduce-saxs-frames-to-curves` / `assess-guinier-fit-quality` / `process-sec-saxs-series` / `correct-sec-saxs-baseline`。

---

```yaml
- id: f01
  title: 2D→1D 还原四段流水线（积分 → 平均 → 扣减 → 落盘）
  type: framework
  source_chapter: tutorial/s1_basic.rst
  source_quote: |
    "Click the plot button to integrate all of the images and plot the integrated scattering profiles on the Profiles plot."
    "Use the average button to average all of the scattering profiles collected into a single curve."
    "Star the averaged buffer file, and select the averaged protein file, then click the subtract button."
  summary: |
    把一批 2D 帧变成一条净散射曲线，骨架是四段、每段只降一个误差源：
    积分（环形平均 2D→1D）→ 平均（同类帧压噪成代表曲线）→ 星标 buffer 后 subtract（去溶剂背景）→ Save 成 .dat。
    四段各在 Profiles 列表留下可机检痕迹：A_（绿，平均）、S_（红，扣减）、文件名前 *（有未存改动）。
    前置条件：本会话已载入与该数据匹配的 .cfg（文档明写「Any time you are going to process images, you need to load the appropriate configuration」）。
    后置条件：得到可交给下游 Guinier / IFT / 重建的净曲线。
  landing: extend:reduce-saxs-frames-to-curves
  tags: [framework, pipeline, reduction, saxs]
```

```yaml
- id: f02
  title: 造一份配置文件（cfg）的六步链（掩膜 → 定心标定 → 归一化 → 绝对刻度 → MW 标准）
  type: framework
  source_chapter: tutorial/section3.rst + s3_masking/s3_autocenter/s3_normalization/s3_abswater/s3_abscarbon/s3_mwstd
  source_quote: |
    "This section will guide you through creating a configuration file for RAW that allows you to integrate 2D images into 1D scattering profiles."
    "The first step in creating a calibraiton file is to to mask out unwanted portions of your image, such as the beamstop and bad detector pixels."
  summary: |
    s3 把「造 cfg」拆成固定顺序的六节：掩膜（beamstop/坏点/面板缝）→ 定心与几何标定（束心、波长、像素尺寸、样品-探测器距离）→ 归一化 → 绝对刻度（水或玻碳）→ 分子量标准 → Save Settings 成 SAXS.cfg。
    顺序不可换，因为存在依赖：改了归一化设置必须重算绝对刻度常数；算常数前必须先关掉绝对刻度，否则得到坏常数。
    前置条件：有一台仪器的原始图像（掩膜宜在水/buffer 图上做，避免被亮图的 beamstop 溢漏欺骗）。
    后置条件：一份可复用的 SAXS.cfg，把 2D 图像变成 1D 曲线时永不报错但会静默决定 q 轴正确与否。
  landing: extend:configure-bioxtas-raw-for-a-dataset
  tags: [framework, configuration, calibration, mask]
```

```yaml
- id: f03
  title: 绝对刻度的三法分叉（水 / 玻碳 Simple / 玻碳 Full NIST）
  type: framework
  source_chapter: tutorial/s3_abswater.rst + tutorial/s3_abscarbon.rst
  source_quote: |
    "Glassy carbon is the more accurate approach, if available."
    "There are two ways to use glassy carbon as a standard in RAW. One way follows the NIST protocol, and will deliver the most accurate results."
  summary: |
    要把强度钉到绝对刻度（惯例单位 cm⁻¹），三条路按「可用条件」分叉而非按偏好选：
    水（最简单）、玻碳 Simple（只需常规归一 + 单次背景、忽略背景）、玻碳 Full NIST（最准，但要求上下游可靠通量测量与准确背景）。
    三者共享同一骨架：Absolute Scale → 选标样（+ 厚度、计数器）→ Calculate 得常数 → 勾选归一。
    前置条件：标样已平均存盘；算常数前绝对刻度必须处于关闭状态。
    后置条件：常数写入 cfg（文档示例期望值约为 0.00077 / 324 / 198，两种玻碳法在示例数据上一致到约 1.5%）。
  landing: new
  tags: [framework, absolute-scale, calibration, glassy-carbon]
```

```yaml
- id: f04
  title: Guinier 三旋钮判读（n_min 取点 / 残差形态 / q_max·Rg 上界）
  type: framework
  source_chapter: tutorial/s1_guinier.rst + saxs/saxs_guinier.rst
  source_quote: |
    "This means RAW has skipped the first few low q points for the Guinier fit."
    "note that q_{max}R_g is  ~1.32. Recall that for globular proteins like GI, it is typical to have q_{max}R_g ~1.3. Adjust n_max down slightly until that is the case, watching what happens to the |Rg| and the residual."
  summary: |
    RAW 打开 Guinier 窗口会自动找「最佳区域」，那只是起点；判读靠三个可调旋钮：
    (1) n_min —— 最低 q 点常被杂散/聚合污染，跳过几点后 Rg 是否仍稳定；
    (2) 残差图（下 plot）—— 线性拟合是否成立的直接证据，看形态而非「像不像直线」；
    (3) q_max·Rg —— 球状蛋白经验上界约 1.3，决定 n_max 停在哪。
    文档还给出形状分档：globular ~1.3、extended/棒 ~1.0、盘可到 ~1.7，以及 q_min·Rg < 0.65 的下限。
    后置条件：报告 Rg/I(0) 时必须连带所用 q 区间与 n_min/n_max，并给出 Uncertainty 段的不确定度。
  landing: extend:assess-guinier-fit-quality
  tags: [framework, guinier, quality-control, rg]
```

```yaml
- id: f05
  title: SEC-SAXS 系列处理（色谱 → buffer/sample 区 → 扣减 → 送 Profiles）
  type: framework
  source_chapter: tutorial/s1_sec.rst
  source_quote: |
    "In a typical SEC-SAXS run, images are continuously collected while the eluate (outflow) of a size exclusion column flows through the SAXS sample cell."
    "This includes creating the SAXS chromatograph from the data, plotting |Rg|, MW, and I(0) across the peaks, and extracting specific frames for further analysis."
  summary: |
    连续洗脱帧先被当作一整条 Series（色谱图），而不是「一个样品的 N 帧」，骨架为四步：
    载入系列并看积分强度 vs 帧号 → 定 buffer 区（Auto 后人工复核）→ 定 sample 区（Auto 后人工复核）→ To Profiles Plot（先平均未扣样品与 buffer 再相减）。
    平台判据：峰上 Rg/MW 应在峰顶形成一段平台，平台段才是可当作「一个样品」的区间。
    失败模式：Auto 可能把峰旁的大平坦前肩误判为 buffer；Rg/MW 在峰缘因低浓度噪声大；分子量只能用 Vc/Vp 等浓度无关法。
    前置条件：已载匹配配置；后置条件：一条或多条送入 Profiles 做 Guinier/MW 的净曲线。
  landing: extend:process-sec-saxs-series
  tags: [framework, sec-saxs, series, chromatography]
```

```yaml
- id: f06
  title: 基线校正的二选一（Linear / Integral + 起止区选取）
  type: framework
  source_chapter: tutorial/s2_baseline.rst
  source_quote: |
    "Sometimes SEC data shows a baseline drift. This can be due either to instrumental changes (such as beam drift), or changes in the measured system, such as capillary fouling."
    "The linear baseline method is best for instrumental drifts, while the integral baseline method is best for capillary fouling."
  summary: |
    扣减后强度-帧号仍系统性漂移时，先判漂移「性质」再选方法：
    仪器/束流漂移 → Linear；毛细管污垢（随 q 变化）→ Integral，两者都按每个 q 各做一条校正。
    骨架为：展开 Baseline Correction → 选类型 → Pick 起止区（起止各约 30–50 帧）→ Set baseline and calculate → 切到校正后 plot 核验。
    失败模式：Integral 只允许正向或不校正，需要负校正的 q 会被整体过校；线性校正的警告（起止区斜率跨 q 不一致）通常可忽略。
    前置条件：buffer 区已定；后置条件：校正后曲线可继续送 Profiles/去卷积（注意若要做 EFA 解卷积，最好不做基线校正）。
  landing: extend:correct-sec-saxs-baseline
  tags: [framework, sec-saxs, baseline-correction, drift]
```

```yaml
- id: f07
  title: IFT 三法的分工（GNOM / DIFT / BIFT）
  type: framework
  source_chapter: tutorial/s2_gnom.rst + s2_dift.rst + s2_bift.rst + saxs/saxs_ift.rst
  source_quote: |
    "indirect Fourier transform (IFT) methods are typically used. In addition to GNOM and BIFT, RAW has another built-in method for calculating the P(r) curve called DIFT."
    "RAW has a built in method for determining the P(r) function using a Bayesian IFT method (BIFT). This has the advantage of only have one possible solution."
    "The most common such method is implemented in the GNOM program from the ATSAS package."
  summary: |
    从 I(q) 到 P(r) 不能直接傅里叶变换（有限 q 范围+噪声会引入截断伪影），必须用间接变换——RAW 提供三条互补路线：
    GNOM（ATSAS，最通用，可强制 P(0)=P(Dmax)=0，输出 .out，兼容 DAMMIF/ATSAS）；
    DIFT（DENSS 内建，与 GNOM 类似但可自动找 Dmax 与 alpha，不兼容强制端点）；
    BIFT（Bayesian 内建，唯一解、自动定 Dmax，输出 .ift，兼容 DENSS 但不兼容 DAMMIF）。
    选法的判据是「下游要用哪个重建程序」，而不是哪个更准。
    前置条件：一条好的扣减曲线（好的 Guinier）；后置条件：一个带 q 区间与 Dmax 的 P(r) 文件。
  landing: new
  tags: [framework, ift, p-r, gnom, bift, dift]
```

```yaml
- id: f08
  title: P(r) 的 Dmax 八步定法（先放大 → 关约束 → 找自然落零 → 回开约束 → 按需截断）
  type: framework
  source_chapter: saxs/saxs_ift.rst + tutorial/s2_gnom.rst
  source_quote: |
    "there is a set of steps that I regularly follow when creating a P(r) function using GNOM via the RAW interface:"
    "Set the |Dmax value to 2-3 times larger than the initial value."
    "Turn off the force to zero at |Dmax condition."
  summary: |
    定 Dmax 的可迁移骨架是「先解除约束、让数据自己说话，再恢复约束」：① 打开界面（默认给一个 datgnom 的合理 Dmax）；② 起始 q 与 Guinier 对齐；③ 把 Dmax 设成初始值的 2–3 倍；④ 看 P(r) 自然落到 0 的位置并设为该点；⑤ 关闭 force-to-zero；⑥ 在关约束下上下微调至自然趋零；⑦ 重新打开 force-to-zero；⑧ 若要给 DAMMIF/N 用，再把 q 截断到 8/Rg 或 0.25–0.3 1/Å（取较小者）。
    判据：Dmax 处平滑趋零为好；被迫陡降=低估、到零后围绕零振荡=高估；Dmax 精度不优于 5%（有时约 10%）。
    前置条件：好 Guinier + 好扣减；后置条件：可用于重建且（按需）截断过的 P(r)。
  landing: new
  tags: [framework, p-r, dmax, gnom]
```

```yaml
- id: f09
  title: 重建→评估闭环（生成多个模型 → 平均成共识 → 用一组判据判定可信）
  type: framework
  source_chapter: saxs/saxs_bead_models.rst + tutorial/s2_dammif.rst/s2_denss.rst/s2_ambimeter.rst/s2_align.rst
  source_quote: |
    "Because the shape reconstruction is not unique, a number of distinct reconstructions are generated, and then a consensus shape is made from the average of these reconstructions."
    "a Monte Carlo like approach is taken where a number (usually 10-20) of models are generated, and then averaged to give a consensus"
  summary: |
    单条散射曲线不能唯一确定 3D 形状，于是重建被组织成一个闭环：生成一批互不相同模型（一般 10–20 个，推荐 15）→ 用 DAMAVER 平均成共识形状（并给出 NSD 统计与剔除名单）→ 用一组判据判定可信度。
    评估判据骨架（逐条）：AMBIMETER 歧义度 a-score（<1.5 基本唯一、1.5–2.5 需谨慎、>2.5 极难唯一）→ 平均 NSD（<0.6 好、>1.0 差）→ 剔除模型少（0–2 个）→ 单一聚类 → 各模型 χ²≈1 → 模型 Rg/Dmax 对上 P(r)（Rg ~5%、Dmax ~10%）→ 体积估 MW 与预期差 >20–25% 则可疑。
    闭环还有两个可选出口：DENSS 电子密度重建（用于多电子密度体系）与 CIFSUP/DENSS 对齐到高分辨结构。
    前置/后置：输入必须是 GNOM 的 .out（或 .ift）；输出是带评估指标的模型集，而不是「那张最好看的图」。
  landing: new
  tags: [framework, reconstruction, bead-model, evaluation, ambiguity]
```

```yaml
- id: f10
  title: 去卷积的方法阶梯（SVD 判数 → EFA 标准 SEC → REGALS 复杂/滴定）
  type: framework
  source_chapter: tutorial/s2_svd.rst + s2_efa.rst + s2_regals.rst
  source_quote: |
    "Evolving factor analysis (EFA) is an extension of SVD that can extract individual components from overlapping SEC-SAXS peaks."
    "EFA is recommended for standard SEC-SAXS data, but for more complex data, such as ion exchange chromatography, or time resolved or titration data you should use REGALS."
  summary: |
    当 SEC 峰重叠时，方法按数据复杂度阶梯式升级，而不是任选一个：
    SVD 只回答「峰内有多少个独立散射体」（看高于基线的奇异值数与自相关 >0.6–0.7 的向量数）；
    EFA 是 SVD 的扩展，在标准 SEC-SAXS（组分严格先进先出）下提取各分量曲线；
    REGALS 用于组分非先进先出的场景（IEC-SAXS、时间分辨、滴定量热），也能处理倾斜基线。
    关键分工：EFA 之前必须先用 SVD 独立核对分量数（RAW 自动判定可能出错，改数据范围后不自动更新）。
    前置条件：一条扣减好的 Series（做 EFA 时最好不做基线校正）；后置条件：各分量曲线 + 一份浓度/分量范围记录。
  landing: new
  tags: [framework, deconvolution, svd, efa, regals]
```

```yaml
- id: f11
  title: 去卷积的三阶调参（分量数 → 区间/Forward-Backward → 正则化 lambda）
  type: framework
  source_chapter: tutorial/s2_efa.rst + s2_regals.rst
  source_quote: |
    "RAW attempts to automatically determine how many significant singular values (SVs) there are in the selected range. This corresponds to the number of significant scattering components in solution that EFA will attempt to deconvolve."
    "In the User Input panel, tweak the "Forward" value start frames so that the frame"
    "Turn off "Auto lambda" for"
  summary: |
    去卷积的参数并非一次调一个，而是三层、由粗到细、层层依赖：
    第一阶「分量数」——RAW 自动判定的显著 SV 数只是起点，必须与 SVD 图/自相关交叉核对；
    第二阶「区间」——用 Forward/Backward EFA 起点（奇异值首次升离基线 / 落回基线处）圈出各分量范围，再在 Component Range Controls 微调至 χ² 均匀接近 1；
    第三阶「正则化」——REGALS 里逐分量关掉 Auto lambda 后按数量级调 lambda（过平滑会让高 q 背景突变）。
    三个旋钮改任何一个后，RAW 不自动更新结果，必须手动 Run（有改动时按钮黄底）；最终运行必须关掉 "Start with previous results" 以免路径依赖。
    后置条件：各分量曲线 + 可复核的区间/分量数/lambda 记录，且任何结果须用其它方法或生化数据佐证。
  landing: new
  tags: [framework, deconvolution, efa, regals, parameter-tuning]
```

```yaml
- id: f12
  title: 多序列的精修流程（校准 → q 裁剪/rebin → 排除帧 → 帧合并）
  type: framework
  source_chapter: tutorial/s2_multiseries.rst
  source_quote: |
    "Once a subtracted series is created, you can then carry out further data refinement including truncating and binning q ranges, averaging together multiple points in a series to improve signal to noise, removing particular profiles from the series, and calibrating the series."
  summary: |
    当一批 series 需要一起做逐点平均/扣减（时间分辨、空白梯度）时，骨架是一条固定的精修流水线：
    载入多 series（按文件名模板 + 编号/补零）→ 定义 buffer/sample 区（可跨 series）→ 逐点平均与扣减 → 时间校准（Load Calibration，x→time）→ q 裁剪/rebin（低 q 常为寄生散射、最高 q 处约半数点为负=无信号）→ 排除帧（如首帧）→ 帧合并（Rebin series 降噪，时点数减半）。
    参数与设置可存成 json 再 Load 复用（Auto select 换一组数据，校准自动套用）。
    前置条件：搞清本设施的文件命名约定（各设施不同）；后置条件：一条时间轴可读、已降噪的多 series 结果 + 导出 CSV。
  landing: new
  tags: [framework, multi-series, time-resolved, rebin]
```

```yaml
- id: f13
  title: RAWAPI 的 load → analyse → save 三段骨架
  type: framework
  source_chapter: api/getting_started.rst + api/ex_analyze_profile.rst + ex_batch_profile.rst + ex_sec_saxs.rst
  source_quote: |
    "Many functions in the API use RAW settings to provide certain parameters for the function (e.g. the calibration parameters and mask used to radially average images). So it is a good idea to load a settings file at the start of your program."
    "Here's an example of how that might be done, from Guinier analysis through creating a 3D reconstruction."
  summary: |
    所有 RAWAPI 脚本共享同一三段骨架：
    ① load——先 load_settings(SAXS.cfg)（校准/掩膜等参数由此供给），再 load_and_integrate_images / load_profiles / load_ifts / load_series（或 profiles_to_series）；
    ② analyse——Guinier（auto_guinier）→ mw_*（六法）→ IFT（bift/datgnom/gnom）→ ambimeter / dammif+damaver / denss，或 SEC 的 find_buffer_range→set_buffer_range→find_sample_range→set_sample_range→svd/efa/regals；
    ③ save——save_profile / save_ift / save_series / save_report。
    可迁移点：GUI 里能对 series 做的分析 API 都能做；但无 GUI 时 EFA 需自行给出各分量区间。
    前置条件：建议先用 GUI 生成并保存 settings 再导入；后置条件：可复现的分析产物（曲线/IFT/report/pdf）。
  landing: new
  tags: [framework, api, scripting, pipeline, reproducibility]
```

```yaml
- id: f14
  title: 分子量六法的两轴分类（浓度依赖 vs 浓度无关；4 原生 + 2 ATSAS）
  type: framework
  source_chapter: saxs/saxs_mw.rst + tutorial/s1_mw.rst
  source_quote: |
    "RAW supports four of the most common methods natively:"
    "There are two additional methods supported in the ATSAS software, which RAW will show if ATSAS is installed:"
    "Generally speaking the methods can be broken up into two categories: concentration dependent and concentration independent."
  summary: |
    分子量不是一个数，而是一组互相独立的估计，选法按两条轴定位：
    轴一「原生还是 ATSAS」——RAW 原生 4 法（绝对刻度 I(0)、参比标准品、Porod 体积 Vp、相关体积 Vc），装 ATSAS 后多 2 法（对比已知结构 Shape&Size、Bayesian 推断）；
    轴二「浓度依赖还是浓度无关」——绝对刻度法与参比标准品法需要池中浓度，因而与 SEC-SAXS 不兼容；Vp/Vc/已知结构/Bayesian 不需浓度，适用于 SEC-SAXS。
    所有方法都要求好的 I(0)，浓度无关法还都要求好的 Rg。
    通则：SAXS 分子量通常 ~10% 不确定度，不该用来定分子量（该用 MALS），其主要用途是判断寡聚态。
  landing: new
  tags: [framework, molecular-weight, method-selection]
```

```yaml
- id: f15
  title: 曲线相似性的三视图（残差 / 比率 / 统计检验）
  type: framework
  source_chapter: tutorial/s1_similarity.rst
  source_quote: |
    "RAW has a dedicated comparison window that allows you to compare residuals, between profiles, ratios between profiles, and use statistical tests (currently only the Correlation Map test is implemented) to check for differences between profiles."
  summary: |
    「这些曲线一样不一样」被拆成三个互补视角，从定性强到定量：
    残差（选参考曲线做差，归一化残差多数应在 ±2.5 内）→ 比率（多条曲线按高 q 区对齐后看是否恒为 1）→ 统计检验（CorMap 概率热图/成对 p 列表，可设 highlight p-value 阈值）。
    这套三视图同时驱动「平均只取相似帧」：平均时若报 not all statistically the same，可点 Average Only Similar Files 用 CorMap 自动剔除。
    失败模式：统计判定只与所用检验和阈值一样好；自动剔除比人工目视更保守，须再目视+Similarity Test 复核（文档例：自动剔 8–10，人工宜剔 6–10）。
  landing: new
  tags: [framework, similarity, cormap, comparison]
```

```yaml
- id: f16
  title: WAXS 处理与 SAXS/WAXS 合并（双探测器 → 各自还原 → 按 scale 归并）
  type: framework
  source_chapter: tutorial/s1_waxs.rst
  source_quote: |
    "Several SAXS beamlines use two (or more) detectors to collect different q regions."
    "The WAXS data is not on the same scale as the SAXS data. For this data, the known scale factor to apply is 0.000014 to the WAXS data."
  summary: |
    当束线用两个探测器覆盖不同 q 区时，骨架是「先各自还原、再按标度归并」：
    载 WAXS.cfg → 单独把 WAXS（PIL3）图平均并扣背景 → 载已存的 SAXS 扣减曲线 → 把其一移到下 plot → 设 WAXS scale factor（文档示例 0.000014）→ 给 WAXS 标星后对 SAXS 曲线做 Merge（生成 M_ 前缀合并曲线）。
    关键陷阱：处理 SAXS 时绝不能把含 PIL3 的 WAXS 文件一起载入。
    前置条件：两套 cfg 与两条各自还原好的曲线；后置条件：一条横跨 SAXS+WAXS 的合并曲线。
  landing: extend:reduce-saxs-frames-to-curves
  tags: [framework, waxs, merging, dual-detector]
```

```yaml
- id: f17
  title: 理论曲线的「计算即拟合」流程（CRYSOL / PDB2SAS 二计算器）
  type: framework
  source_chapter: tutorial/s2_crysol.rst + s2_pdb2sas.rst
  source_quote: |
    "you should actually fit the data as part of the process of generating the theoretical profile, rather than generating a 'minimal' theoretical profile and comparing to the data."
    "PDB2SAS allows you to fit the excluded solvent and hydration shell to best match experimental data."
  summary: |
    拿高分辨模型（晶体/CryoEM/AlphaFold）对照 SAXS 的骨架是「计算即拟合」：
    不是先生成一条与数据无关的 minimal 理论曲线再比较（溶剂、水化层、排除体积难建模，minimal 常拟合差），而是在生成理论曲线的同时把实验数据纳入拟合。
    二计算器分工：CRYSOL（ATSAS，需安装）与 PDB2SAS（DENSS 内建且为 RAW 默认，.cif 暂不支持）。
    骨架：plot .pdb（或 Tools 菜单）→ Add 模型（+ Add 实验数据）→ Start → 得 *_FIT 与 Chi²/Prob（仅在拟合数据时才有）。
    参数注意：高长径比需更多 harmonics（如 100）；PDB2SAS 的 N samples 默认 128 对细长蛋白不足，改 256（用 2 的幂）。
  landing: new
  tags: [framework, crysol, pdb2sas, model-fitting]
```

```yaml
- id: f18
  title: 数据落盘与外部互操作（.dat / .out / .ift 三格式 + 绘图 CSV 导出）
  type: framework
  source_chapter: tutorial/s4_external_data.rst + s4_export_plots.rst
  source_quote: |
    "This is intended to be distinct from saving data in formats that RAW knows how to read (e.g. .dat, .ift, .hdf5 for profiles, IFTs, and series respectively), as the export formats cannot be read back into RAW."
    "These .dat files are standard text files with space separated values."
  summary: |
    出数据被分成两条互不混用的出口，骨架按「能否读回 RAW」划线：
    可读回的保存格式——曲线 .dat（三列 Q/I(Q)/Error，'#' 开头为头尾，### HEADER: 后去 # 即 json）、IFT .out（GNOM，四段：Configuration/Results/Experimental Data and Fit/Real Space Data）或 .ift（BIFT，首行 "# BIFT"）、系列 .hdf5/.sec；
    不可读回的导出格式——各 plot 右键 Export Data as CSV（Guinier/Dimensionless Kratky/Comparison/CRYSOL/IFT 分开导出；SVD/EFA/REGALS/Series 各有 Save）。
    失败模式：.dat 扩展名被多程序（如 Primus）共用、格式可能略异；Excel 导入 .out 时部分 I Reg 会落到错列。
  landing: new
  tags: [framework, export, file-format, interoperability]
```
