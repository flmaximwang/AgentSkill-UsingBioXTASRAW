# candidates/counter-examples.md — 反例提取器（视角 4：警告 / 失败模式 / 误用 / 静默出错点）

源：**BioXTAS RAW 官方文档（v2.4.2）** 纯文本语料
`rawdocs/{00-root,10-install,20-manual,30-saxs,40-tutorial,50-api}.md`（以 `### FILE:` 定位分节）。
证据分级：`30-saxs` / `40-tutorial` / `50-api` 为 **B 级**（当前权威）；`20-manual.md` 为 **A 级**（19 节全部自承「落后若干版本」）——**A 级只作对照，不作为事实依据**。
原文引用为**语料逐字**（≤150 字/条）；方括号内为中文补注，非原文。
`landing`：`new`（拟新建）或 `extend:<现有 skill slug>`（扩写现有 5 个 skill）。

现有 skill：`configure-bioxtas-raw-for-a-dataset`、`reduce-saxs-frames-to-curves`、`assess-guinier-fit-quality`、`process-sec-saxs-series`、`correct-sec-saxs-baseline`。

---

```yaml
- id: ce01
  title: 没加载配置就直接积分图像——不报错，但结果全错
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s1_basic.rst（B 级）
  source_quote: |
    "*Note:* Any time you are going to process images, you need to load the
    appropriate configuration!"
  summary: |
    情况：刚启动 RAW、换了实验日/线站/探测器，或者只打开图像文件夹就直接 Plot。
    症状：程序不报错、照常画出曲线，但 beam center、样品-探测器距离、掩膜、归一化
    都没生效，q 轴标定与 Rg/I(0) 全错。识别：q 范围与预期差一个倍数、曲线上找不到
    标样（AgBh）应有的峰位、Rg 与文献值差 10 倍级。避免：处理图像前先
    File→Load Settings 载入当天的 .cfg；用山嵛酸银一级峰把「配置对不对」变成
    可检验事实。
  tags: [counter-example, silent-failure, configuration]
  landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
- id: ce02
  title: 掩膜只按 Save to File 没按 Set——掩膜不生效
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s3_masking.rst（B 级；20-manual.md The_Masking_panel.rst 同义，A 级对照）
  source_quote: |
    These do not save or set the mask in RAW. To do that you need to use the
    "Set" button as described above. The mask is then saved with the settings.
  summary: |
    情况：画完 beamstop/多边形掩膜后点了 "Save to File" 存 .msk，以为已生效。
    症状：不报错，但积分时坏点/beamstop 阴影照旧进曲线——掩膜其实没进内存。
    识别：曲线在 beamstop 阴影区仍出现异常突起/负值；重新打开面板看不到掩膜。
    避免：生效必须按 "Set"（随设置保存）；"Save to File"/"Load from file" 只是
    磁盘 .msk 文件；载入后还要选类型再按 Set。Clear 之后同样须 Set。
  tags: [counter-example, silent-failure, masking]
  landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
- id: ce03
  title: 绝对刻度：算常数前没关刻度、改归一化后没重算
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s3_abscarbon.rst 与 s3_abswater.rst（B 级）
  source_quote: |
    "make sure absolute scale is turned off before you calculate the scale
    constant, otherwise you will get a bad scaling constant"
  summary: |
    情况：在已经勾选绝对刻度归一化的会话里点 Calculate 定常数；或定完常数后又
    改了归一化设置。症状：不报错，但绝对刻度常数错、所有强度整体偏移，MW 与
    I(0) 跟着错。识别：常数与预期值（玻碳 ~324 / 水 ~0.00077）对不上；改了
    归一化后没回头重算。避免：算常数前先关掉绝对刻度；一旦改动归一化设置
    （含通量/透射等）就必须重算绝对刻度常数，不能沿用旧的。
  tags: [counter-example, silent-failure, absolute-scale]
  landing: new
```

```yaml
- id: ce04
  title: 坏 buffer 扣减让 Kratky 图看似有柔性
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s1_kratky.rst（B 级）
  source_quote: |
    "Bad buffer subtraction can also result in a Kratky plot that appears to show
    some degree of flexibility."
  summary: |
    情况：buffer 与样品不匹配（未透析/未脱盐换液）就做 Kratky / 无量纲 Kratky
    判柔性。症状：本该钟形的折叠蛋白曲线出现上翘，被误读成「部分解折叠/柔性」。
    识别：同一数据低 q 过扣/欠扣，Guinier 残差也不干净；换正确匹配 buffer 后
    形态改变。避免：Kratky 柔性判读要求极好的 buffer 扣减；先保证 buffer
    匹配（透析/过柱），并与 Guinier、P(r) 交叉验证，别单凭 Kratky 下结论。
  tags: [counter-example, kratky, buffer-subtraction]
  landing: new
```

```yaml
- id: ce05
  title: 不到 1% 的聚集就足以污染最大尺寸与三维重建
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_guinier.rst（B 级）
  source_quote: |
    "Even small amounts of aggregation (<1%) can affect things like the measured
    maximum dimension, and three dimensional reconstructions."
  summary: |
    情况：低 q 上扬但 Guinier 拟合「勉强能用」，于是把数据带进 IFT 与重建。
    症状：Dmax 偏大、P(r) 长尾、珠模型出现伸展突起，重建不可信。识别：
    Guinier 残差呈 smile（两端高于零）、排除 >3–5 个低 q 点才线性。避免：
    Guinier 差一般应重采数据；固有聚集用高速离心/SEC-SAXS/降浓度，辐射损伤
    加甘油/降曝光/加自由基清除剂。
  tags: [counter-example, aggregation, guinier]
  landing: extend:assess-guinier-fit-quality
```

```yaml
- id: ce06
  title: 0.7% 的聚集体就能显著改变珠模型
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_bead_models.rst（B 级）
  source_quote: |
    "In one simple simulation I've seen, as little as 0.7% aggregate caused a
    significant change in the bead model."
  summary: |
    情况：样品含少量寡聚体/非特异聚集，仍照常做 DAMMIF/N。症状：重建结果
    带一个伸出的突起（非特异聚集的典型表现），形状被判成哑铃/延长体。
    识别：模型比 P(r) 暗示的更延伸、MW 与预期差 >20–25%。避免：重建前先
    确认样品单分散（SEC-SAXS / 离心）；把聚集当作重建的先决条件而非事后解释。
  tags: [counter-example, aggregation, bead-model]
  landing: new
```

```yaml
- id: ce07
  title: Dmax 低估会强迫 P(r) 陡降，高估则绕零振荡
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_ift.rst（B 级）
  source_quote: |
    If you underestimate the |Dmax|, then the P(r) function has an abrupt descent
    to zero
  summary: |
    情况：直接取自动/默认 Dmax 或凭直觉调参。症状：Dmax 偏小→P(r) 末端被
    硬生生压到零（数据被截断）；Dmax 偏大→P(r) 到零后围绕零上下振荡。
    识别：把 Dmax 从初值 2–3 倍起扫，关掉 "force to zero at Dmax" 看它是否
    自然趋零。避免：Dmax 通常不优于 5%（有时近 10%）；GNOM 步骤为「设大→
    看自然落零→设该点→关 force→微调→重开 force」，用于 DAMMIF/N 时再截断
    到 8/Rg 或 0.25–0.30 1/Å 取小者。
  tags: [counter-example, ift, dmax]
  landing: new
```

```yaml
- id: ce08
  title: 用 SAXS 定分子量本身就越界
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_mw.rst（B 级）
  source_quote: |
    "SAXS should not be used to determine the molecular weight of your sample"
  summary: |
    情况：把 SAXS 算出的 MW 当作定量结论（甚至用来区分 250 vs 270 kDa、
    1:1 vs 2:1）。症状：SAXS MW 通则 ~10% 不确定度（或更大），不足以区分
    相邻低聚态。识别：各方法 MW 分散、对扣减/浓度敏感。避免：MW 只用于判断
    样品在溶液中的低聚态趋势；要准确分子量用 MALS/AUC，最好 SEC-MALS-SAXS
    在同一洗脱上同时测。
  tags: [counter-example, molecular-weight, method-boundary]
  landing: new
```

```yaml
- id: ce09
  title: Volume of correlation 法：小分子与蛋白-核酸复合物不适用
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_mw.rst（B 级）
  source_quote: |
    "Large uncertainty for macromolecules less than ~15-20 kDa"
  summary: |
    情况：把 Vc 法 MW 用在 <15–20 kDa 的小蛋白，或蛋白-核酸复合物上。
    症状：小分子 MW 不确定度大（经验系数由 ≥20 kDa 尺寸段拟合）；复合物
    直接失效。识别：∫qI(q)dq 是否在高 q 收敛（曲线变平）；分子是否含核酸。
    避免：小分子/复合物换用其它 MW 途径并以 MALS 为准；Vc 法要求 qI(q)
    积分收敛、I(0) 与 Rg 准确，且对高信噪比数据不如他法。
  tags: [counter-example, molecular-weight, vc-method]
  landing: new
```

```yaml
- id: ce10
  title: 珠模型的形状、分辨率与「数据好≠重建好」
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_bead_models.rst（B 级）
  source_quote: |
    "bead models tend to be less reliable for high aspect ratio objects"
    "high quality SAXS data is not a guarantee of a good bead model reconstruction"
  summary: |
    情况：对高长径比物体（长棒、薄盘）、有空洞物体（球壳）、环状物体做珠模型，
    或以为数据质量高就无需逐模型评审。症状：形状不可靠；同一曲线可对应多个
    形状，重建可能只是「一个」解而非「唯一」解。识别：AMBIMETER a-score、
    NSD、聚类数、χ²、模型 Rg/Dmax 与 P(r) 的吻合度。避免：珠模型最可靠于近
    球状物体；分辨率很少优于 ~20 Å（常更差）；每个重建都要按判据严格评估。
  tags: [counter-example, bead-model, ambiguity]
  landing: new
```

```yaml
- id: ce11
  title: 积分基线只允许正向校正——需负校正的 q 会被整体过校
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s2_baseline.rst（B 级；correct-sec-saxs-baseline 已部分覆盖）
  source_quote: |
    "the integral baseline correction only allows for positive or no change in the
    baseline"
    "the total baseline ends up overcorrected"
  summary: |
    情况：SEC-SAXS 用 Integral 法基线校正，而某些 q 实际需要负校正。
    症状：校正后基线整体被下拉、峰底过校（常在 q 值上不一致）。识别：切
    "Intensity in q range" 逐段看，高 q 段往往被过校（该段可能本就以噪声为主）。
    避免：确认若该区是噪声，先把 profile 截断到较低 q 再做基线校正；需要负
    校正时不要硬用 Integral 法。
  tags: [counter-example, baseline-correction, sec-saxs]
  landing: extend:correct-sec-saxs-baseline
```

```yaml
- id: ce12
  title: 玻碳 NIST（Full）法要求可靠通量与准确背景
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s3_abscarbon.rst（B 级）
  source_quote: |
    "This approach will only work if the .dat files you select for the glassy
    carbon"
    "contain the upstream and downstream counter values"
  summary: |
    情况：用 Full (NIST) 法定绝对刻度却选错了文件或没把 Normalization 列表
    清空、没关掉已有绝对刻度。症状：常数错（示例应近 198），定标整体偏移。
    识别：所选 .dat 是否带 upstream/downstream 计数（I1/I3）；否则改用图像
    （噪声更大但能自动找到计数值）。避免：Full 法要求可靠的上/下游通量测量
    与准确背景；Simple 法忽略背景、要求较低但精度略差。
  tags: [counter-example, absolute-scale, nist]
  landing: new
```

```yaml
- id: ce13
  title: 给 DENSS 做电子密度重建时不要截断 P(r)
  type: counter-example
  source_chapter: 30-saxs.md · saxs/saxs_ift.rst（B 级）
  source_quote: |
    "Don't truncate your P(r) function for electron density reconstructions
    with DENSS."
  summary: |
    情况：沿用「用于 DAMMIF/N 的 P(r) 要截断到 8/Rg 或 0.25–0.30 1/Å」，
    对同一 P(r) 也截断后再喂给 DENSS。症状：不报错，但电子密度重建质量
    下降。识别：重建用的是截断后的 .out（常被截到 8/Rg ~0.23）还是全 q 的
    .ift / _full.out。避免：截断规则只在 bead model（DAMMIF/N）下适用；
    DENSS 要用全 q 范围、不要截断 P(r)。
  tags: [counter-example, denss, ift]
  landing: new
```

```yaml
- id: ce14
  title: BIFT 输出不兼容 DAMMIF/其它 ATSAS 程序（但兼容 DENSS）
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s2_bift.rst（B 级）
  source_quote: |
    "BIFT output from RAW is not compatible with DAMMIF or other ATSAS programs"
    "it is compatible with electron density determination via DENSS"
  summary: |
    情况：用 RAW 原生 BIFT 得到 .ift 后，想直接丢给 DAMMIF/AMBIMETER（ATSAS）
    或按 .out 流程走。症状：下游程序读不了 / 结果无效（AMBIMETER 与 DAMMIF
    只吃 GNOM 生成的 .out）。识别：上游是 BIFT 还是 GNOM。避免：要跑 ATSAS
    珠模型链，先经 GNOM 生成 .out；BIFT 的 .ift 只用于 DENSS 电子密度路线。
  tags: [counter-example, ift, formats]
  landing: new
```

```yaml
- id: ce15
  title: EFA 分量数自动判定可能错，且改范围不自动更新
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s2_efa.rst（B 级）
  source_quote: |
    "RAW can find the wrong number of components automatically"
    "double check this automatic determination against the SVD results in the plots"
  summary: |
    情况：直接采信 RAW 自动判定的显著分量数；或改了数据范围/数据型后没重设
    分量数。症状：不报错，但分量数错→解卷积结果无意义（χ² 尖峰、浓度出现
    负值）。识别：与 SVD 图核对；改范围后分量数不会自动更新，须手动检查。
    另外用 "Start with previous results" 只是加速迭代，会引入路径依赖偏差
    （"path dependent and thus isn't reproducible later"），最终运行必须关掉。
  tags: [counter-example, efa, deconvolution, path-dependence]
  landing: new
```

```yaml
- id: ce16
  title: REGALS 不自动更新结果；过平滑缓冲分量会让高 q 背景突变
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s2_regals.rst（B 级）
  source_quote: |
    "REGALS does not automatically update the results."
    "it means you're oversmoothing the buffer components"
  summary: |
    情况：改了分量范围/lambda 后没按 "Run REGALS"（按钮变黄底才表示结果未更新）；
    或一味增大缓冲分量 lambda 追求平滑。症状：GUI 显示旧结果却被当成新结果；
    过平滑时高 q 背景先趋同、随后 component 1 profile 突然剧变。识别：按钮
    是否黄底、lambda 数值是否未随自动更新同步。避免：每次改动后手动 Run；
    出现「高 q 背景匹配 + profile 突变」即回调到最后 good 值（约 4e8），
    lambda 按数量级调整。
  tags: [counter-example, regals, deconvolution]
  landing: new
```

```yaml
- id: ce17
  title: PDB2SAS 是默认但可被改成 CRYSOL；.cif 不支持
  type: counter-example
  source_chapter: 40-tutorial.md · tutorial/s2_pdb2sas.rst 与 s2_align.rst（B 级）
  source_quote: |
    "PDB2SAS is the default calculator in RAW. However, it is possible that it
    has been changed to CRYSOL by a user."
  summary: |
    情况：照着别处写的「默认 PDB2SAS」操作，但本机已被改成 CRYSOL；或用
    PDB2SAS 打开 .cif（该计算器不支持 .cif，须用 .pdb）。症状：理论曲线
    来源/尺度与预期不符；.cif 报错或无结果。识别：Options→Advanced
    Options→General Settings 的 "Default structure calculator"。避免：用前
    核对默认计算器（可重置为 PDB2SAS）；另：CIFSUP 只在 ATSAS ≥3.1.0 提供，
    更旧版本改用 SUPCOMB 窗口。
  tags: [counter-example, theory-data, version-drift]
  landing: new
```

```yaml
- id: ce18
  title: 【A 级对照】手册称 SEC 存 .sec，现行实际用 .hdf5
  type: counter-example
  source_chapter: 20-manual.md · File_types.rst（A 级，作对照）；对照 40-tutorial.md / 50-api.md（B 级）
  source_quote: |
    "SEC items are saved as “.sec” files, and is the only data that RAW does not save
    in a human readable format."
  summary: |
    情况：按旧手册去找/存 .sec 序列文件。症状：与 tutorial/API 的实际用法
    不一致——现行教程与 API 一致使用 .hdf5（`load_series` 文档写 "a .hdf5
    or .sec"）。识别：手上文件到底是 .sec 还是 .hdf5；是否需要被其它工具读。
    避免：以 tutorial/API 为准；.sec 是 RAW 私有、非人类可读且只能被 RAW
    读取，跨工具交换应走 .hdf5。
  tags: [counter-example, a-level-contrast, file-format, sec-saxs]
  landing: extend:process-sec-saxs-series
```

```yaml
- id: ce19
  title: 【A 级对照】手册称 RAW 仅兼容 Python 2.7，平台要求也过期
  type: counter-example
  source_chapter: 20-manual.md · Installing_RAW.rst（A 级，作对照）；对照 10-install.md / 00-root.md（B 级）
  source_quote: |
    "**NOTE:** As of writing, the RAW is **only** compatible with Python version 2.7
    and not the newer 3.x versions."
  summary: |
    情况：照旧手册判断环境是否可用。症状：结论与现行事实相反——install 文档
    三处写 "As of version 2.0.0, RAW is Python 3 compatible"；手册的平台
    要求（Win 7/8.1/10、macOS 10.9–10.12）也被现行 install/index 取代
    （macOS 13+ / Windows 11）。识别：以哪份文档为准。避免：安装与兼容性
    一律以 10-install.md + index.rst 为准，manual 的该页彻底失效。
  tags: [counter-example, a-level-contrast, python, platform]
  landing: new
```

```yaml
- id: ce20
  title: 【A 级对照】手册的 MW 方法数、校准标准与 ATSAS 清单整体滞后
  type: counter-example
  source_chapter: 20-manual.md · Analysis_windows.rst / RAW_Settings_and_the_Options_window.rst（A 级，作对照）；对照 40-tutorial.md / 30-saxs.md（B 级）
  source_quote: |
    "Four different methods are used to calculate the molecular weight of the macromolecule"
  summary: |
    情况：按手册核对「RAW 能做什么」。症状：多处与现行文档冲突——手册只写
    四法（tutorial/30-saxs：原生四法 + ATSAS 两法 = 六法）、绝对校准只讲
    water 而 tutorial 有 glassy carbon（"Glassy carbon is the more accurate
    approach"）、ATSAS 清单只到 GNOM/DAMMIF/AMBIMETER 且要求 ≥2.7.1
    （tutorial 用到 CIFSUP，需 ≥3.1.0/用 3.1.1）、特性表与窗口清单缺
    DENSS/DIFT/REGALS/Eiger/Similarity。识别：以 tutorial + api + saxs 为准。
    避免：manual 仅作历史对照，其罗列与参数不作为操作依据。
  tags: [counter-example, a-level-contrast, version-drift, method-boundary]
  landing: new
```
