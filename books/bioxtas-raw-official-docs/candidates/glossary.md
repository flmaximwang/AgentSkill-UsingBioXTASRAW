# BioXTAS RAW 官方文档 · 术语候选池（视角 5 / 术语提取器）

- 来源语料：BioXTAS RAW 官方文档 v2.4.2（readthedocs）纯文本化产物 —— `00-root.md` / `10-install.md` / `20-manual.md` / `30-saxs.md` / `40-tutorial.md` / `50-api.md`
- 产出：cangjie-skill（book2skill）RIA-TV++ 流水线的**术语提取器**候选池
- 每条结构：`source_quote` 为语料**逐字**原文；`summary` 给「文档原义定义 + 在哪被当判据用 + 与常见误解的区别」三段。
- 纪律：定义必须有语料支撑，数值逐字准确，不推测。
- `landing`：`new` = 本册新词典条目；`extend:<skill>` = 应并入现有同名 skill 的词典。

---

```yaml
id: g01
term: I(q)（散射强度曲线）
type: glossary
source_chapter: 30-saxs（saxs_ift）
source_quote: >-
  The SAXS scattering profile is measured in reciprocal distance space, as I(q)
  where *q* has units of one over distance (usually 1/Angstrom or 1/nm).
summary: |
  定义：一维散射强度随 q 变化的曲线，是 SAXS 的观测量，测量于「倒易距离空间」。
  判据位置：一切下游分析（Guinier、MW、IFT、拟合残差）的输入；残差是否「平坦且随机」就是在比对模型 I(q) 与实测 I(q)。
  易误解：I(q) 是方位角平均后的曲线（2D→1D），不是探测器图像本身，也不是「积分面积」；RAW 全程假定 q 为 1/Å。
tags: [scattering, data-model, core]
landing: new
```

```yaml
id: g02
term: q（散射矢量）
type: glossary
source_chapter: 20-manual（Manipulation panel）
source_quote: >-
  All of the processing in RAW assumes that the scattering profiles are in
  inverse angstroms.
summary: |
  定义：q 为散射矢量模长，单位是长度的倒数（1/Å 或 1/nm）；RAW 全程假定用 1/Å。
  判据位置：q 轴是一切判据（Rg 单位 1/q、q_min·Rg、q_max·Rg、Shannon 极限）的自变量；比较两条不同 q 标度曲线时可用 "Convert q-scale" 乘以/除以 10。
  易误解：q 没有「隐含单位」；1/Å 与 1/nm 相差 10 倍，混用会让 Rg/MW 整体差 10 倍而不报错。
tags: [scattering, units, core]
landing: extend:assess-guinier-fit-quality
```

```yaml
id: g03
term: I(0)（前向散射强度）
type: glossary
source_chapter: 30-saxs（saxs_guinier）
source_quote: >-
  I(0) is the intensity at zero scattering angle (q=0).
summary: |
  定义：外推到零角度（q=0）的散射强度，由 Guinier 线性拟合在 ln(I) vs q² 上的截距给出。
  判据位置：正比于「分子量×浓度」，是所有 MW 方法的前提（绝对标度、参照标样、Porod、Vc 都要用到）；与 P(r) 反算的 I(0) 是否一致是一条 P(r) 好坏判据。
  易误解：I(0) 不是直接测得的点（q=0 被束流挡掉），必须外推；浓度未知时它只能说相对大小。
tags: [scattering, guinier, mol-weight]
landing: extend:assess-guinier-fit-quality
```

```yaml
id: g04
term: Rg（回转半径）
type: glossary
source_chapter: 30-saxs（saxs_guinier）
source_quote: >-
  The |Rg tells you about the overall size of the molecule, while I(0) depends
  on the molecular weight times the concentration.
summary: |
  定义：分子整体尺寸的度量；单位是 1/q（q 用 Å⁻¹ 时 Rg 用 Å），由 Guinier 拟合得到，也可由 P(r) 在实空间算出。
  判据位置：q_min·Rg、q_max·Rg 取点判据的核心变量；P(r) 与 Guinier 两个 Rg 是否一致是 P(r)/重建可信度判据（高质量数据 ~5%）。
  易误解：Rg 没有「默认单位」；数值差 10 倍通常是 q 用了 1/Å 还是 1/nm，而非数据错误。
tags: [scattering, guinier, core]
landing: extend:assess-guinier-fit-quality
```

```yaml
id: g05
term: Guinier 近似（Guinier 图 / Guinier 区间）
type: glossary
source_chapter: 30-saxs（saxs_guinier）
source_quote: >-
  Guinier’s approximation states that at low-*q* the scattering profile can be
  approximated as follows: I(q)\approx I(0) e^{-q^2 R_g^2 /3}
summary: |
  定义：低 q 区散射可用高斯式近似，对 ln(I) vs q² 做线性拟合即得 Rg 与 I(0)；用于拟合的区间叫「Guinier region」。
  判据位置：四条判据——q_min·Rg<0.65（球状可放宽到 <1.0）、q_max·Rg~1.3（球状）或 ~1.0（长条形）、残差平坦随机、拟合延伸到最低可用 q 点。
  易误解：Guinier 拟合不是「越宽越好」，超出线性区会系统性偏大 Rg（'smile' 提示聚集，'frown' 提示排斥）。
tags: [guinier, method, criteria]
landing: extend:assess-guinier-fit-quality
```

```yaml
id: g06
term: P(r)（对距离分布函数）
type: glossary
source_chapter: 30-saxs（saxs_ift）
source_quote: >-
  This produces the P(r) function, also called the pair distance distribution
  function.
summary: |
  定义：实空间的电子对距离直方图，由 I(q) 经间接傅立叶变换（IFT）反解得到。
  判据位置：由它给出 Dmax、更准的 Rg 与 I(0)；是 DAMMIF、AMBIMETER、DENSS 等高级分析的必需输入。
  易误解：不能由 I(q) 直接做傅立叶变换得到（直变换会因有限 q 范围而失真），必须先选 Dmax 与 α 做正则化拟合。
tags: [ift, realspace, core]
landing: new
```

```yaml
id: g07
term: Dmax（最大尺寸）
type: glossary
source_chapter: 30-saxs（saxs_ift）
source_quote: >-
  First, in doing the P(r) function we get an estimate of the maximum dimension
  of the macromolecule (|Dmax|).
summary: |
  定义：分子内任意两电子点之间的最大距离，即 P(r) 的尾部截断位置。
  判据位置：IFT 求解的三个待定量之一（Dmax、α、最优 P(r)）；好的 P(r) 应在 Dmax 处「平滑趋零」；重建得到的 Dmax 应与 P(r) 的 Dmax 接近（高质数据 ~10%）。
  易误解：Dmax 不是精确唯一的，柔性分子尤其模糊（文档口径：一般好于 5%，有时接近 10%）；截断太早会压零 P(r)，太晚则 χ² 上升。
tags: [ift, realspace, criteria]
landing: new
```

```yaml
id: g08
term: Vc（volume of correlation，相关体积）
type: glossary
source_chapter: 30-saxs（saxs_mw）/ 20-manual
source_quote: >-
  In [3] they defined the volume of correlation as V_c =
  \frac{I(0)}{\int_0^{\infty}qI(q)dq}
summary: |
  定义：Vc = I(0) / ∫qI(q)dq，可理解为「每自相关长度的粒子体积」，单位 Å²；由 Vc²/Rg 与 MW 的对数关系推算分子量。
  判据位置：MW（Vc MW 面板）方法之一；蛋白用 c=0.1231、k=1，RNA 用 c=0.00934、k=0.808。
  易误解：与 Porod 体积不同，Vc 对紧凑与柔性分子都应收敛；但若 ∫qI(q)dq 不收敛（q 不够高或缓冲失配）则不准，且对蛋白-核酸复合物无效。
tags: [mol-weight, vc, criteria]
landing: new
```

```yaml
id: g09
term: Vp（Porod volume，Porod 体积）
type: glossary
source_chapter: 30-saxs（saxs_mw）
source_quote: >-
  The Porod volume is nominally the excluded volume of the macromolecule in
  solution.
summary: |
  定义：名义上等于分子在溶液中的排阻体积；由 Porod 不变量算得，再乘分子密度即得 MW。
  判据位置：MW（Vp MW 面板）方法之一；RAW 用 SAXSMoW 2 对 Porod 体积做数据范围修正（Corrected Vp）。
  易误解：真值需要 I(q) 积到 ∞，实测必须近似；该方法对信噪比好的数据比 Vc 更准，但对延伸型分子不如 Vc。
tags: [mol-weight, porod, criteria]
landing: new
```

```yaml
id: g10
term: Qp（Porod 不变量）
type: glossary
source_chapter: 30-saxs（saxs_mw）
source_quote: >-
  It can be calculated directly from the scattering profile, first by
  calculating the Porod invariant: Q_p = \int^\infty_0 q^2 I(q) dq
summary: |
  定义：Qp = ∫q²I(q)dq，由散射曲线直接积分得到；Vp = 2π²I(0)/Qp。
  判据位置：Porod 体积与 Porod 体积法 MW 的中间量；要求积分在高 q 收敛（曲线趋平）。
  易误解：Qp 是「积分量」而非某个单点的强度；有限 q 范围导致积分需近似（ATSAS datmw 的 'Porod'/'Qp' 法，RAW 用 SAXSMoW 2 修正）。
tags: [mol-weight, porod, invariant]
landing: new
```

```yaml
id: g11
term: χ²（卡方 / 拟合优度）
type: glossary
source_chapter: 30-saxs（saxs_bead_models）/ 40-tutorial（s2_multiseries）
source_quote: >-
  For a good fit to the data, the model \chi^2 should be close to 1.
summary: |
  定义：模型与数据的加权残差平方和；接近 1 视为「好拟合」。
  判据位置：P(r) 拟合、DAMMIF 模型、REGALS 收敛（默认默认收敛=Chi² 1000 次迭代）都用它当判据。
  易误解：χ² 约等于 1 只是必要条件；显著大于 1（文档口径 1.5–2 或更大）要么拟合差、要么误差被低估——要靠残差形态区分（残差平坦随机 ⇒ 误差被低估）。
tags: [statistics, fit, criteria]
landing: new
```

```yaml
id: g12
term: α（正则化权重）
type: glossary
source_chapter: 30-saxs（saxs_ift）
source_quote: >-
  The weighting parameter, usually called \alpha, that determines the relative
  contribution of \chi^2 and the perceptual criteria.
summary: |
  定义：IFT 正则化中权衡「拟合数据（χ²）」与「感知准则（平滑性、非负性）」的权重；BIFT 状态下界面显示的是 log10(α)。
  判据位置：IFT 求解三要素之一；残差系统性偏差过大时可把 α 手动调到自动值的一半再微调。
  易误解：α 越大越平滑（更信正则化、可能过平滑），越小越贴数据（可能引入伪振荡）；α 不是可忽略的默认值。
tags: [ift, regularization, criteria]
landing: new
```

```yaml
id: g13
term: NSD（归一化空间差异）
type: glossary
source_chapter: 30-saxs（saxs_bead_models）
source_quote: >-
  The most useful is the normalized spatial discrepancy (NSD). This is
  essentially a size normalized metric for comparing how similar two different…
summary: |
  定义：DAMAVER 输出的、尺寸归一化后的模型相似度指标（比较两个模型有多像）。
  判据位置：重建稳定性判据——NSD<0.6 好、0.6–1.0 尚可、>1.0 差；也用于决定哪些模型进入平均。
  易误解：NSD 小不代表模型唯一（可能多个簇）；NSD 大也不必然意味着数据差，可能只是形状本身对 SAXS 高度模糊。
tags: [bead-model, dammif, criteria]
landing: new
```

```yaml
id: g14
term: NSD 剔除的 2σ 规则
type: glossary
source_chapter: 30-saxs（saxs_bead_models）
source_quote: >-
  If the average NSD of a given model is more than two standard deviations above
  the overall average NSD, that model is not included in the average.
summary: |
  定义：某模型的平均 NSD 若比全体平均 NSD 高出两个标准差以上，就被踢出平均模型集合。
  判据位置：DAMAVER 自动挑选进入平均的模型；若 15 个里被剔除多于 ~2 个，是重建不稳定的信号。
  易误解：这是自动规则，不是「随便剔几个」；被剔除模型在 RAW 结果表里显示为红色，仍需人工复核簇结构。
tags: [bead-model, dammif, rule, criteria]
landing: new
```

```yaml
id: g15
term: a-score（ambiguity score，模糊度分数）
type: glossary
source_chapter: 40-tutorial（s2_ambimeter）
source_quote: >-
  an a-score below 1.5 practically guarantees a unique ab initio shape
  determination, whereas when the a-score is in the range 1.5–2.5 care should
  be…
summary: |
  定义：AMBIMETER 给出的模糊度分数 = 与你的曲线相容的形状类别数的 log10。
  判据位置：做重建之前就能预判能不能得到唯一形状：<1.5 基本唯一；1.5–2.5 需小心（配合簇分析）；>2.5 几乎不可能无约束唯一重建。
  易误解：a-score 是「重建可行性」判据，不是数据质量分数；高分不一定是数据差，而是该形状本身对 SAXS 模糊。
tags: [ambimeter, bead-model, criteria]
landing: new
```

```yaml
id: g16
term: Shannon 极限（Dmax < π/q_min）
type: glossary
source_chapter: 40-tutorial（s2_regals）
source_quote: >-
  Because of the q range of the data, the largest dimension of an object
summary: |
  定义：数据的 q_min 决定可测的最大尺寸上限 Dmax < π/q_min；文例中由 q 范围推得最大可测 ~300 Å。
  判据位置：REGALS 里给未知聚集体设 Dmax 时用（设为 300 Å）；也是判断「数据是否支持你想要的 Dmax」的物理上限。
  易误解：Shannon 极限给的是「上界」不是「最佳值」；设到极限附近通常偏大，实际 Dmax 常由 P(r) 平滑趋零来定。
tags: [ift, shannon, limit, criteria]
landing: new
```

```yaml
id: g17
term: 过采样（oversampling，相对 Shannon 采样频率）
type: glossary
source_chapter: 20-manual（Manipulation panel / Rebinning）
source_quote: >-
  As most scattering profiles are significantly oversampled (compared to the
  Shannon sampling frequency), there is no loss of information from doing…
summary: |
  定义：散射曲线点数远多于 Shannon 采样频率所需，因此可重分箱（rebin）以提升单点信噪比而不丢信息。
  判据位置：决定「能不能安全 rebin」的依据；也解释了导出的曲线点可少于原始测量点。
  易误解：不是「点越多越好」；过采样下的密集点其实高噪声，rebin 是降噪手段而非丢数据。
tags: [rebin, sampling, method]
landing: new
```

```yaml
id: g18
term: .dat（曲线文件）
type: glossary
source_chapter: 20-manual（File_types）
source_quote: >-
  .dat – These are files containing three column scattering profile data with a
  “header” at the start or end of the file for additional information.
summary: |
  定义：三列（q, I, Error）+ 头信息的散射曲线文件，可被 RAW 存也可被 ATSAS 等下游读。
  判据位置：交付/归档格式；tutorial 明确「这是 SAXS 散射曲线的标准格式，也是人类可读的」。
  易误解：.dat 是 1D 曲线（交付物），不是原始探测器图像；两者在归档策略里要分开对待。
tags: [file-type, output, human-readable]
landing: new
```

```yaml
id: g19
term: .out（GNOM IFT / P(r) 文件）
type: glossary
source_chapter: 20-manual（File_types）
source_quote: >-
  .out – These are files containing GNOM P(r) data and are written in the
  standard format described in the ATSAS manual for GNOM.
summary: |
  定义：GNOM 生成的 P(r) 数据文件，采用 ATSAS GNOM 标准格式。
  判据位置：GNOM 产生的 IFT 条目一律带 .out 扩展名；DAMMIF、AMBIMETER 只吃 .out 文件；可直喂任何需要 GNOM .out 的 ATSAS 程序。
  易误解：.out 与 .ift 都装 P(r)，但来源/格式不同（GNOM vs BIFT/RAW），且 ATSAS 系方法只认 .out。
tags: [file-type, ift, gnom, atsas]
landing: new
```

```yaml
id: g20
term: .ift（BIFT IFT 文件）
type: glossary
source_chapter: 20-manual（File_types）
source_quote: >-
  .ift – These are files containing three column BIFT data followed by four
  column scattering profile data, with a “header” at the start or end of the…
summary: |
  定义：BIFT 生成的三列 IFT 数据，后接四列散射曲线数据，带头信息，人类可读。
  判据位置：BIFT 产生的 IFT 条目带 .ift 扩展名；保存 IFT 时用 .out 存 GNOM、.ift 存 BIFT。
  易误解：.ift 只代表 RAW/BIFT 系 IFT；误把它喂给需要 GNOM .out 的 ATSAS 程序会失败。
tags: [file-type, ift, bift]
landing: new
```

```yaml
id: g21
term: .csv（逗号分隔导出）
type: glossary
source_chapter: 20-manual（File_types）
source_quote: >-
  .csv – If data is in a 3 column csv format, it is loaded assuming the columns
  are q, I, Error.
summary: |
  定义：逗号分隔文本；作为输入时按三列解析为 q, I, Error；作为输出用于把分析结果（相似性配对表、EFA 浓度、基线拟合等）导出到电子表格。
  判据位置：读 .csv 时的列序假定（q, I, Error）本身就是判据——列序错就静默读错。
  易误解：.csv 不是 RAW 的原生分析文件，只是交换/查看格式；列序约定必须严格遵守。
tags: [file-type, io, csv]
landing: new
```

```yaml
id: g22
term: .hdf5 / .sec（SEC-SAXS 序列文件）
type: glossary
source_chapter: 20-manual（File_types）/ 50-api
source_quote: >-
  .sec – These are files containing SEC-SAXS curves, which can be loaded back
  into RAW and contain all of the relevant scattering profiles
summary: |
  定义：SEC-SAXS 序列的保存格式，含全部相关散射曲线与结构参数；可被 RAW 重新载入。API 里同一序列文件用 .hdf5（如 phehc_sec.hdf5），也可用 .sec。
  判据位置：序列的「全量存档」格式（唯一非人类可读的数据文件之一）。
  易误解：.sec 只能被 RAW 读（不人类可读）；它与单条曲线的 .dat 不是一回事，序列里含成百上千条曲线。
tags: [file-type, sec, series, output]
landing: extend:process-sec-saxs-series
```

```yaml
id: g23
term: A_ 前缀（平均曲线）
type: glossary
source_chapter: 40-tutorial（s1_basic）/ 20-manual
source_quote: >-
  The filename will be in green, and will start with **A_**, indicating it is an
  averaged scattering profile.
summary: |
  定义：平均后的散射曲线文件名以 A_ 开头、在列表中以绿色显示。
  判据位置：这是「我这条是平均曲线」的唯一 UI 判据——扣减时应选择平均后的样品曲线，背景应给平均后的缓冲液标星。
  易误解：A_ 只表示「这是平均」，不代表已剔帧；平均会降噪也会掩盖辐射损伤/流动不稳。
tags: [ui-marker, average, naming]
landing: extend:reduce-saxs-frames-to-curves
```

```yaml
id: g24
term: S_ 前缀（扣减曲线）
type: glossary
source_chapter: 40-tutorial（s1_basic）
source_quote: >-
  A new profile should be shown in the Profiles list with the name in red and a
  **S_** prefix indicating it is a subtracted file.
summary: |
  定义：缓冲液扣减后得到的曲线，文件名以 S_ 开头、在列表中以红色显示。
  判据位置：识别「这是已扣减的样品曲线」；S_A_... 表示扣减的是平均样品与平均缓冲液（例：S_A_GI2_A9_19_001_0000.dat）。
  易误解：S_ 表示「已做缓冲液扣减」，不等于已做浓度归一或绝对标度；红/绿颜色只是 UI 提示，不影响数值。
tags: [ui-marker, subtract, naming]
landing: extend:reduce-saxs-frames-to-curves
```

```yaml
id: g25
term: '`*` 未保存标记（unsaved marker）'
type: glossary
source_chapter: 20-manual（IFT panel）
source_quote: >-
  If there is a \* to the left of the item name (between the checkbox and the
  item name), it indicates there are unsaved changes to the item.
summary: |
  定义：条目名左侧的星号表示该条目有未保存改动（新建的 IFT、改过名字等）；保存后星号消失。
  判据位置：判断「分析结果是否已落盘」的唯一 UI 依据（tutorial：「the * at the front goes away. This indicates there are no unsaved changes」）。
  易误解：星号与数据质量无关；它只表示保存状态，退出 RAW 时未保存的改动会丢失。
tags: [ui-marker, save-state]
landing: extend:process-sec-saxs-series
```

```yaml
id: g26
term: profile_type（unsub / sub / baseline）
type: glossary
source_chapter: 50-api（getting_started）
source_quote: >-
  The intensity for subtracted of baseline corrected data is accessed by
  specifying the data type
summary: |
  定义：序列内曲线的数据类型开关——未扣减（unsub）、已扣减（'sub'）、基线校正（'baseline'）；getIntI/getMeanI/getAllSASMs/getSASM/getSASMList 都可带该参数。
  判据位置：取序列数据时必须声明类型，否则默认取未扣减数据；文档明示「有基线校正的曲线要用 'baseline'」。
  易误解：'sub' 与 'baseline' 不是同一种数据；给基线校正后的序列取 'sub' 会拿到非预期曲线。
tags: [api, series, profile-type]
landing: extend:process-sec-saxs-series
```

```yaml
id: g27
term: SAM / SASM（SAS measurement 对象）
type: glossary
source_chapter: 50-api（getting_started）
source_quote: >-
  RAW uses a custom defined class called a SASM (SAS measurement) to contain
  information about scattering profiles, including the q, I,
summary: |
  定义：RAW 中承载单条散射曲线的类，存 q、I、误差及分析元数据；方法有 getQ/getI/getErr/getQrange/getRawQ/getRawI/getRawErr/getAllParameters/getParameter。
  判据位置：API 里一切单曲线分析（auto_guinier、mw_*、bift、gnom）的输入对象类型。
  易误解：getQ() 返回的是截断/缩放后的数据，原始未截断数据要用 profile.q 或 getRawQ()——直接混用会得到长度不匹配的曲线。
tags: [api, object, sam]
landing: new
```

```yaml
id: g28
term: IFTM（IFT measurement 对象）
type: glossary
source_chapter: 50-api（getting_started）
source_quote: >-
  RAW uses a custom defined class called a IFTM (IFT measurement) to contain
  information about IFTs, including the P(r) function, the fit of the P(r)…
summary: |
  定义：承载 IFT/P(r) 结果的对象；属性有 p、r、err（P(r) 本身）、q_orig/i_orig/err_orig、i_fit、q_extrap/i_extrap；方法 getAllParameters/getParameter（如 getParameter('dmax')）。
  判据位置：AMBIMETER 与各 3D 重建方法的输入对象。
  易误解：ATSAS 系方法（DAMMIF、AMBIMETER、GNOM）要求 GNOM 的 IFTM，而 RAW 原生 DENSS 对 GNOM/BIFT 的 IFTM 都可用。
tags: [api, object, ift]
landing: new
```

```yaml
id: g29
term: SECM（SEC measurement 对象）
type: glossary
source_chapter: 50-api（getting_started）
source_quote: >-
  RAW uses a custom defined class called a SECM (SEC measurement, a slightly
  outdated name) to contain information about series, including the…
summary: |
  定义：承载 SEC-SAXS（及一般序列）数据的对象，含各帧曲线、总/平均强度随帧号变化、以及 Rg 等逐帧参数。
  判据位置：序列分析（找缓冲液区、扣减、基线校正、EFA/SVD/REGALS）的全套输入对象。
  易误解：名字带 SEC 但 RAW 里同一套工具也用于其他顺序采样数据（文档：「In RAW, this is called Series analysis」）。
tags: [api, object, series, sec]
landing: extend:process-sec-saxs-series
```

```yaml
id: g30
term: SECM 方法（getFrames/getIntI/getMeanI/getRg/getI0/getVcMW/getVpMW/getAllSASMs/getSASM/getSASMList）
type: glossary
source_chapter: 50-api（getting_started）
source_quote: >-
  rg = my_series.getRg() i0 = my_series.getI0() mw_vc = my_series.getVcMW()[0]
  mw_vp = my_series.getVpMW()[0]
summary: |
  定义：读取序列各量的方法——getFrames 帧号、getIntI/getMeanI 总/平均强度、getRg/getI0 逐帧参数、getVcMW/getVpMW 逐帧 MW、getAllSASMs 全部曲线、getSASM(i) 单条（零索引）、getSASMList(a,b) 区间曲线；后四者可带 'sub'/'baseline'。
  判据位置：画 SAXS 色谱图（强度 vs 帧号）和挑样区域的 API 入口。
  易误解：getSASM/getSASMList 是零索引；带类型参数才能拿到扣减/基线校正后的曲线。
tags: [api, methods, series]
landing: extend:process-sec-saxs-series
```

```yaml
id: g31
term: ATSAS（外部程序套件）
type: glossary
source_chapter: 20-manual（IFT panel）
source_quote: >-
  If the GNOM option is unavailable in the right click menu for a data item, it
  indicates
summary: |
  定义：BioSAXS 领域的外部程序套件（含 GNOM、DATGNOM、DAMMIF、DAMMIN、DAMAVER、AMBIMETER、CRYSOL、CIFSUP 等），RAW 通过接口调用它。
  判据位置：是否有 GNOM/DAMMIF/AMBIMETER/CRYSOL 等右键菜单项，取决于 RAW 能否找到 ATSAS 安装位置；找不到时在 Options→Advanced Options→ATSAS 手动指定 bin 路径。
  易误解：RAW 原生只有 BIFT/DIFT/DENSS/PDB2SAS；任何「需要 ATSAS」的功能是外部依赖，未装则整段功能不可用。
tags: [atsas, dependency, external]
landing: new
```

```yaml
id: g32
term: GNOM
type: glossary
source_chapter: 40-tutorial（s2_gnom）
source_quote: >-
  The most common such method is implemented in the GNOM program from the ATSAS
  package.
summary: |
  定义：ATSAS 里最常用的 IFT 程序，用于求 P(r)；RAW 提供界面（q_min/q_max/Dmax 可调，n_min/n_max 为取点索引）。
  判据位置：产生 .out 文件，是 DAMMIF/AMBIMETER 的必需前置；其 Rg/I(0)/Total Estimate 作为分析参数被保存。
  易误解：GNOM 需要手动定 Dmax（RAW 会先自动找）；界面里改 q_min/q_max/Dmax 会即时重算 P(r)。
tags: [ift, gnom, atsas]
landing: new
```

```yaml
id: g33
term: DATGNOM
type: glossary
source_chapter: 20-manual（IFT panel）
source_quote: >-
  The “DATGNOM” button runs the DATGNOM program from the ATSAS software package.
summary: |
  定义：ATSAS 里自动定 Dmax 的程序；打开 GNOM 窗口且无既往分析时，RAW 会先跑 DATGNOM。
  判据位置：为 GNOM 提供起始 Dmax；有 Guinier 得到的 Rg 时 DATGNOM 结果通常更好。
  易误解：DATGNOM 只是「定 Dmax 并起跑 GNOM」，不是独立的 P(r) 求解器的另一套物理；其 Dmax 会四舍五入为整数。
tags: [ift, datgnom, atsas, automation]
landing: new
```

```yaml
id: g34
term: BIFT（贝叶斯间接傅立叶变换）
type: glossary
source_chapter: 40-tutorial（s2_bift）
source_quote: >-
  RAW has a built in method for determining the P(r) function using a Bayesian
  IFT method (BIFT).
summary: |
  定义：RAW 原生（内建）的 IFT 方法，全自动确定 Dmax 与 α。
  判据位置：示例数据上提供「Dmax 变化 ~99–104（5%）」这类不确定度基准；产物为 .ift 文件。
  易误解：BIFT「只有一个解」指其算法不依赖用户手选 Dmax/α，不代表物理上唯一；与 GNOM 结果应互相印证。
tags: [ift, bift, automated]
landing: new
```

```yaml
id: g35
term: DIFT（DENSS IFT）
type: glossary
source_chapter: 40-tutorial（s2_dift）
source_quote: >-
  In addition to GNOM and BIFT, RAW has another built-in method for calculating
  the P(r) curve called DIFT. DIFT is the IFT calculator from DENSS.
summary: |
  定义：RAW 内建的第三种 IFT 方法，即 DENSS 的 IFT 计算器（对应命令行 denss.fit_data.py），不需另行安装 DENSS。
  判据位置：像 GNOM 一样可自动或手动选 Dmax/α；但 DIFT 不能选择强制 P(r=0) 或 P(r=Dmax) 为零，且没有 GNOM 的 "Total Estimate"。
  易误解：DIFT ≠ DENSS 的 3D 重建；它只算 P(r)。「与 GNOM 相似但有重要差异」是文档明确提醒。
tags: [ift, dift, denss]
landing: new
```

```yaml
id: g36
term: DENSS
type: glossary
source_chapter: 40-tutorial（s2_denss）
source_quote: >-
  A new, exciting method for doing 3D shape reconstructions in SAXS yields
  actual electron density, rather than bead models.
summary: |
  定义：在 RAW 中已完整实现的 3D 重建方法，产出电子密度（而非串珠模型）；天然支持多个电子密度（如 RNA-蛋白复合物、带去垢剂环的膜蛋白）。
  判据位置：重建输出的 χ²、Rg、支撑体体积（support volume）等作为评估指标；DENSS 对齐工具用于与高分辨结构比对；适合用全 q 范围数据（不应截断到 8/Rg）。
  易误解：DENSS 与串珠模型是两类方法，不要混用；DENSS 需要把 P(r) 截断去掉（文档：「Don't truncate your P(r) function for electron density reconstructions with DENSS」）。
tags: [densis, 3d-reconstruction, method]
landing: new
```

```yaml
id: g37
term: DAMMIF / DAMMIN（串珠重建）
type: glossary
source_chapter: 40-tutorial（s2_dammif）
source_quote: >-
  Shape reconstruction in SAXS is typically done using bead models (also called
  dummy atom models, or DAMs).
summary: |
  定义：串珠/虚拟原子（dummy atom）模型的从头（ab initio）重建程序，DAMMIF 生成多个独立重建，DAMMIN 用于精修或单独重建。
  判据位置：需 P(r)（.out）作输入并写成磁盘文件；出图给出每个模型的 χ²、Rg、Dmax、体积、体积估 MW、平均 NSD。
  易误解：DAMMIF 默认 Fast 模式（教程够用），出论文应跑 Slow；建库重建常需 15–20 个重建，且重建不唯一（需按判据挑共识）。
tags: [bead-model, dammif, dammin, atsas]
landing: new
```

```yaml
id: g38
term: DAMAVER
type: glossary
source_chapter: 40-tutorial（s2_dammif）
source_quote: >-
  The program DAMAVER from the ATSAS package is the most commonly used program
  for building consensus shapes.
summary: |
  定义：把多个串珠重建对齐、聚类、平均出「共识形状」的程序。
  判据位置：输出平均/标准差 NSD、被纳入平均的模型数；模型若平均 NSD 超全体两倍标准差以上则被剔除（红色显示）。
  易误解：DAMAVER 的产物是共识模型，不代表溶液中唯一形状；其簇数需要结合 AMBIMETER 的 a-score 一起看。
tags: [bead-model, damaver, consensus, atsas]
landing: new
```

```yaml
id: g39
term: DAMCLUST
type: glossary
source_chapter: 30-saxs（saxs_bead_models）
source_quote: >-
  DAMCLUST creates clusters of models that are more similar to each other than
  they are to the rest of the models.
summary: |
  定义：把重建集合按相似度聚成簇（DAMAVER 的一部分）。
  判据位置：多于一个簇 ⇒ 可能多个形状都能生成同一曲线 ⇒ 高度模糊；但文档提醒低 NSD(<0.5)+极小标准差时会出现「假簇」（>5 个簇），属算法被欺骗。
  易误解：不同簇不能当作溶液中不同构象的代表——每条重建只是对实测曲线（各组分散射的加权平均）做拟合。
tags: [bead-model, damclust, clusters, atsas]
landing: new
```

```yaml
id: g40
term: SASRES
type: glossary
source_chapter: 40-tutorial（s2_dammif）
source_quote: >-
  If DAMAVER was run on 3 or more reconstructions, and ATSAS >=2.8.0 is
  installed, there will be the output of SASRES
summary: |
  定义：评估重建分辨率的程序（作为 DAMAVER 的一部分运行，需 ≥3 个重建）。
  判据位置：给出「这次重建的分辨率大约多少」；一般很难低于 ~20 Å。
  易误解：分辨率是「模型表面细节能到多细」，不是拟合优度；低分辨率是串珠法的固有属性。
tags: [bead-model, sasres, resolution, atsas]
landing: new
```

```yaml
id: g41
term: AMBIMETER
type: glossary
source_chapter: 30-saxs（saxs_bead_models）
source_quote: >-
  The AMBIMETER program in the ATSAS package can be run on P(r) functions from
  GNOM to assess how likely you are to get a good reconstruction.
summary: |
  定义：在 P(r)（GNOM .out）上运行、评估重建模糊度的程序；用最多 7 个珠子枚举形状的数据库比对，报告匹配形状数与 a-score。
  判据位置：重建前的可行性初筛（a-score <1.5 唯一 / 1.5–2.5 小心 / >2.5 大概率模糊）；只吃 GNOM 的 .out。
  易误解：AMBIMETER 只对 GNOM IFT 工作；匹配形状数越多不代表重建越好，恰恰相反。
tags: [ambimeter, bead-model, atsas]
landing: new
```

```yaml
id: g42
term: SUPCOMB / CIFSUP（结构对齐）
type: glossary
source_chapter: 40-tutorial（s2_align）
source_quote: >-
  CIFSUP from the ATSAS suite can be used to align two PDB/mmCIF files.
summary: |
  定义：把两个 PDB/mmCIF 文件对齐的程序，用于把重建模型与高分辨结构比对。
  判据位置：CIFSUP 仅 ATSAS ≥3.1.0 可用，更旧版本用功能类似的 SUPCOMB 窗口（Tools→ATSAS→Align (SUPCOMB/CIFSUP)）。
  易误解：CIFSUP/SUPCOMB 只做对齐，不判断构象是否一致；对齐得分反映几何契合，不改变重建本身。
tags: [alignment, cifsup, supcomb, atsas]
landing: new
```

```yaml
id: g43
term: CRYSOL
type: glossary
source_chapter: 40-tutorial（s2_crysol）
source_quote: >-
  One of the most common programs to generate theoretical scattering profiles is
  the CRYSOL program in the ATSAS package.
summary: |
  定义：由高分辨模型（pdb/cif，如晶体、CryoEM、AlphaFold）生成理论散射曲线并拟合实测数据的常用程序。
  判据位置：生成的 _FIT 曲线与实验数据一起读入 RAW（例 2pol_polymerase.fit / _FIT），用残差判断模型与溶液结构是否一致。
  易误解：文档提醒「最小化」独立生成理论曲线常拟合很差（溶剂、水化层、排阻体积难建模），应把拟合作为生成过程的一部分。
tags: [crysol, theoretical, fit, atsas]
landing: new
```

```yaml
id: g44
term: PDB2SAS（DENSS 理论曲线）
type: glossary
source_chapter: 40-tutorial（s2_pdb2sas）
source_quote: >-
  The purpose and output of PDB2SAS is similar to that of CRYSOL, but uses a
  fundamentally different algorithm.
summary: |
  定义：RAW 内建的、基于 DENSS PDB2SAS 计算器（命令行 denss.pdb2mrc.py）的理论曲线方法；先算实空间电子密度（真空原子、排除溶剂、水化层），再做傅立叶变换与球面平均。
  判据位置：PDB2SAS 是 RAW 的默认结构计算器（可在 Options→General Settings 改回 CRYSOL）；不支持 .cif，只支持 .pdb。
  易误解：功能与 CRYSOL 类似但算法不同；不能互相假定结果等价——换默认计算器会改变理论曲线。
tags: [pdb2sas, theoretical, denss, default]
landing: new
```

```yaml
id: g45
term: REGALS（正则化交替最小二乘）
type: glossary
source_chapter: 40-tutorial（s2_regals）
source_quote: >-
  REGALS is an algorithm for deconvolution of mixtures in small angle scattering
  data.
summary: |
  定义：用于 SAXS 混合体系解卷积的算法，可处理 SEC 重叠峰、IEC-SAXS 变化基线、时间分辨/滴定序列等；可视为 EFA 在「非严格首进首出」条件下的推广。
  判据位置：需设显著 SV 数、各分量范围、Dmax（受 Shannon 极限约束）、浓度正则化等；以 χ² 迭代收敛（默认 1000 次）。
  易误解：标准 SEC-SAXS 用 EFA 即可，复杂情形（IEC、时间分辨、滴定、斜基线）才该用 REGALS；它对各分量 profile 用 realspace 正则（按 P(r)），所以必须设 Dmax。
tags: [regals, deconvolution, series, method]
landing: new
```

```yaml
id: g46
term: EFA（演进因子分析）
type: glossary
source_chapter: 40-tutorial（s2_efa）
source_quote: >-
  Evolving factor analysis (EFA) is an extension of SVD that can extract
  individual components from overlapping SEC-SAXS peaks.
summary: |
  定义：SVD 的扩展，用于从 SEC-SAXS 重叠峰中提取各组分曲线；其第一步本身就是做 SVD，且完全在 EFA 窗口内完成。
  判据位置：看 Forward/Backward EFA 图中奇异值随帧号出现与回落的位置来划定各组分范围。
  易误解：做 EFA 前不需要先开 SVD 窗口；EFA 要求组分严格首进首出，否则失败（该用 REGALS）。
tags: [efa, svd, deconvolution, series]
landing: new
```

```yaml
id: g47
term: SVD（奇异值分解）
type: glossary
source_chapter: 40-tutorial（s2_svd）
source_quote: >-
  Singular value decomposition (SVD) can be used to help determine how many
  distinct scatterers are in a SEC-SAXS peak.
summary: |
  定义：用来判断一个 SEC-SAXS 峰里有多少个不同散射物种的数学方法；输出奇异值及左右奇异矢量（自相关）。
  判据位置：显著高于基线的奇异值个数 = 显著组分数（RAW 可自动判定，需人工确认）。
  易误解：SVD 只告诉你「有几个」，不分离出曲线；分离要靠 EFA（或 REGALS）。RAW 里 SVD 用截断 SVD 等变体。
tags: [svd, series, math]
landing: new
```

```yaml
id: g48
term: CorMap（相关图检验）
type: glossary
source_chapter: 40-tutorial（s1_similarity）
source_quote: >-
  Currently, only one test is available: the Correlation Map test.
summary: |
  定义：RAW 目前唯一的统计相似性检验；比较两条曲线是否统计学上「相同」，输出热图与配对概率，检验量为 CorMap longest edge。
  判据位置：平均曲线时自动检测并警告不一致；可关多重检验校正、调 p 值阈值（如 0.15）来标记可疑帧（辐射损伤等）。
  易误解：CorMap 判「是否同」不等于判「哪个好」；自动剔除的帧数取决于所选阈值，需人工复核（文档示例中自动剔 3 帧、手动可能剔 5 帧）。
tags: [cormap, statistics, similarity, series]
landing: extend:process-sec-saxs-series
```

```yaml
id: g49
term: SAXSMoW 2
type: glossary
source_chapter: 30-saxs（saxs_mw）
source_quote: >-
  RAW uses the SAXSMoW 2 approach described in [2], which applies a correction
  factor to the Porod volume based on the available range of data in the…
summary: |
  定义：Porod 体积法 MW 中，对 Porod 体积按可用 q 范围施加校正因子的方法（RAW 的默认 Porod 体积实现）。
  判据位置：给出 Corrected Vp；[2] 报道球状蛋白 MW 中位不确定度 12%。
  易误解：SAXSMoW 2 ≠ 直接积分 Vp（那是未校正的 Vp）；数值需按可用数据范围而非全 q 积分。
tags: [mol-weight, saxsmoW, porod]
landing: new
```

```yaml
id: g50
term: Shape&Size
type: glossary
source_chapter: 30-saxs（saxs_mw）
source_quote: >-
  By finding the nearest structures in shape and size (also the name of the
  method: Shape&Size), they can obtain estimates for the molecular weight of…
summary: |
  定义：机器学习方法，把 SAXS 数据按形状归类（对照 PDB 已知结构目录），找到形状与尺寸最接近的结构从而估计 MW。
  判据位置：MW 方法之一（ATSAS 提供）；测试集中 90% 理论曲线 MW 落在 ±10% 内，中位偏差 4%。
  易误解：它估的是「最像的已知结构的 MW」，不解析实际结构；名字本身就是方法名。
tags: [mol-weight, shape-size, machine-learning]
landing: new
```

```yaml
id: g51
term: cfg（SAXS.cfg / WAXS.cfg 配置文件）
type: glossary
source_chapter: 20-manual（File_types）
source_quote: >-
  .cfg – These are files containing all of RAW’s settings (configuration files).
  This file type is not human readable.
summary: |
  定义：承载 RAW 全部设置（定心/校准、掩膜、归一化、绝对标度、MW 标样、ATSAS 路径等）的配置文件；教程中即 SAXS.cfg，WAXS 对应 WAXS.cfg。
  判据位置：图像能否被正确积分完全取决于此；未加载配置就打开图像不会提示不匹配。
  易误解：.cfg 不是数据文件的一部分、也不会随图像走；它是「会话/束线级」设置，换天换仪器就需重新校准并另存。
tags: [config, cfg, settings]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g52
term: mask（掩膜）
type: glossary
source_chapter: 40-tutorial（s3_masking）
source_quote: >-
  The first step in creating a calibraiton file is to to mask out unwanted
  portions of your image, such as the beamstop and bad detector pixels.
summary: |
  定义：把探测器上不该参与积分的区域（beamstop、坏点、面板间隙）标掉。
  判据位置：Pilatus 坏点值通常为 -2（Mask All Pixels = -2）；面板间隙用 "pilatus_1m" 的 Mask detector 自动生成；做掩膜建议用水的图像（亮图如 AgBh/玻璃碳会因 beamstop 边缘溢光而掩膜不足）。
  易误解：掩膜 ≠ 扣背景；"Save to File/Load from file" 只存取掩膜文件，要生效必须点 "Set"（掩膜随设置保存）。
tags: [mask, config, image-reduction]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g53
term: centering / calibration（定心 / 校准）
type: glossary
source_chapter: 40-tutorial（s3_autocenter）
source_quote: >-
  The goal of centering and calibration is to find a beam center position,
  sample to detector distance,
summary: |
  定义：确定束斑中心、样品-探测器距离、探测器旋转（倾角），使计算出的 AgBh 环与图像上的环重合。
  判据位置：三者共同决定 q 轴；AgBh 环对齐是「配置是否正确」的可检验判据（计算环以红色虚线显示、束心为红点）。
  易误解：不是软件安装参数或探测器出厂参数；若探测器明显偏离束法向，计算环（不含倾角）不会与实测环重合。
tags: [calibration, centering, config, q-axis]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g54
term: normalization（归一化）
type: glossary
source_chapter: 20-manual（Normalization panel）
source_quote: >-
  The normalization panel allows you to normalize integrated scattering profiles
  by some value.
summary: |
  定义：按某个值（通常是正比于透射束强的计数器，如 beamstop 计数 I1）归一积分后的散射曲线；也可按曝光时间、ROI 求和或任意 header 表达式。
  判据位置：不同帧/不同样品强度可比性的前提；计算绝对标度常数后**不得再改归一化设置**（否则常数作废）。
  易误解：归一化（除以束强）≠ 绝对标度（换成 cm⁻¹ 单位）；绝对标度时归一化全部在 Absolute Scale 面板完成，Normalization 面板应清空。
tags: [normalization, config, reduction]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g55
term: absolute scale（绝对标度）
type: glossary
source_chapter: 20-manual（Absolute scale panel）
source_quote: >-
  RAW is able to scale loaded image data to absolute scale using water as a
  standard.
summary: |
  定义：把强度换算为有单位（约定 cm⁻¹）的绝对标度；用已知 I(0) 的标样（水或玻璃碳）标定绝对标度常数。
  判据位置：只有绝对标度下 I(0) 才能直接对应电子数、浓度与衬度（由此可算 MW）；水法用曲线中间 1/3 段平均估计 I(0)。
  易误解：标样与水必须与样品用**完全相同**的归一化；计算常数前必须关闭绝对标度、且标样文件不得已带绝对标度（否则得到坏常数）。
tags: [absolute-scale, config, mol-weight]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g56
term: MW standard（分子量标样）
type: glossary
source_chapter: 40-tutorial（s3_mwstd）
source_quote: >-
  One method for determining molecular weight from a scattering profile is
  comparison to a known scattering profile with known molecular weight.
summary: |
  定义：以已知 MW 的样品散射曲线作参照来算未知样 MW（需已知浓度）；在 RAW 中右击曲线 →"Other Operations→Use as MW Standard"，再填标样 MW（kDa）。
  判据位置：参照标样法 MW 的输入；教程标样为溶菌酶，MW = 14.3 kDa，浓度 4.14 mg/ml。
  易误解：标样法要求参照与样品的衬度一致且样品单分散；只把「已知 MW」填进去不够，必须先做 Guinier 拟合给出 I(0)。
tags: [mol-weight, standard, config]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g57
term: glassy carbon（玻璃碳 NIST SRM 3600）
type: glossary
source_chapter: 40-tutorial（s3_abscarbon）
source_quote: >-
  This section teaches you how to set up absolute scale using glassy carbon
  (NIST SRM 3600) as a reference.
summary: |
  定义：用于绝对标度的参照标样（NIST SRM 3600）；两种用法——NIST 协议（最准，需上下游通量测量与准确背景）与「忽略背景」的简化法（类似水法，只需常规归一化 + 单次背景）。
  判据位置：绝对标度常数计算的标样；例中简化法得 ~324，NIST 全法得 ~198，两法在示例数据上一致到 ~1.5%。
  易误解：玻璃碳比水更准（若可得）；「设置常数前必须关闭绝对标度、之后不得改归一化」这条约束同样适用。
tags: [absolute-scale, standard, glassy-carbon]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g58
term: water standard（水标样）
type: glossary
source_chapter: 40-tutorial（s3_abswater）
source_quote: >-
  This section teaches you how to set up absolute scale using water as a
  reference.
summary: |
  定义：用水作绝对标度参照；因水散射曲线相对平坦，可用其平均强度估计前向散射 I(0)（需从水样中减去空池）。
  判据位置：绝对标度常数计算的另一种标样（例中得 ~0.00077）；水温度需用户输入（例中 4 °C）。
  易误解：水法精度不如玻璃碳；用图像计算会比用平均曲线噪声更大（文档建议用平均曲线）。
tags: [absolute-scale, standard, water]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g59
term: beamstop（束流挡块）
type: glossary
source_chapter: 40-tutorial（s3_masking）
source_quote: >-
  The beamstop is the blue bar in the upper right of the detector.
summary: |
  定义：挡住直射/强前向束的部件，在图像上是右上角的蓝色条（另一处描述为「从探测器右上边缘伸出的蓝/绿色条」）。
  判据位置：必须被掩膜；曲线起始处被挡掉的 q 点值为零，需用「Start plots at q-point number」跳过（例中约第 13 点）。
  易误解：beamstop 保护的像素不是「坏点」，但在积分中同样不能参与平均；掩膜不足常因在亮图（AgBh/玻璃碳）上做膜被边缘溢光欺骗。
tags: [beamstop, mask, geometry]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g60
term: pilatus_1m（探测器类型）
type: glossary
source_chapter: 40-tutorial（s3_masking）
source_quote: >-
  Go to the "Radial Averaging" section. Set the Detector to "pilatus_1m"
summary: |
  定义：探测器类型选项名，选中后 RAW 自动填入像素尺寸并生成面板间隙掩膜。
  判据位置：Radial Averaging 面板中设 Detector，Centering/Calibration 面板会验证其为 "pilatus_1m"；"Mask detector" 用该类型自动生成间隙掩膜。
  易误解：若探测器设为 "Other"，则像素尺寸/掩膜不会自动填入，必须手动；"pilatus_1m" 是 RAW 的枚举名而非任意字符串。
tags: [detector, config, mask]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g61
term: AgBh（山嵛酸银 / silver behenate 标样）
type: glossary
source_chapter: 40-tutorial（s3_autocenter）
source_quote: >-
  We will use silver behenate to calibrate the sample to detector distance, the
  beam center on the detector, and the detector rotation.
summary: |
  定义：几何校准用标样（silver behenate），有已知的环状衍射图样；Centering/Calibration 面板中 "standard" 设为 AgBh。
  判据位置：通过让计算环与图像环重合来同时定出束心、样品-探测器距离与探测器旋转；例中能量 12.0 keV、像素 172.0×172.0 µm。
  易误解：AgBh 用于**几何校准**，不用于绝对强度标度（那是水/玻璃碳）；文档另给出其环位 q = 0.1076, 0.2152, 0.3229, 0.4305, 0.538 Å⁻¹（前 5 环）。
tags: [calibration, standard, agbh, geometry]
landing: extend:configure-bioxtas-raw-for-a-dataset
```

```yaml
id: g62
term: 基线校正（baseline correction：Linear / Integral）
type: glossary
source_chapter: 40-tutorial（s2_baseline）
source_quote: >-
  RAW provides the ability to correct for these forms of baseline drift using
  either a linear or integral baseline method.
summary: |
  定义：校正 SEC 数据的基线漂移；线性法适合仪器漂移，积分法适合毛细管污染；两种方法对每个 q 值分别施加校正。
  判据位置：做基线校正时只应有缓冲液区；校正后的序列曲线要用 profile_type='baseline' 访问。
  易误解：基线校正 ≠ 缓冲液扣减；线性基线校正在 API 里几乎总是返回「无效」（validate_baseline_range 的已知现象）。
tags: [baseline, sec, series, method]
landing: extend:correct-sec-saxs-baseline
```

```yaml
id: g63
term: 缓冲液区 / 样品区（buffer range / sample range）
type: glossary
source_chapter: 50-api（ex_sec_saxs）
source_quote: >-
  Find an appropriate buffer range for subtraction
summary: |
  定义：序列中用于计算背景（缓冲液区）和用于扣减取样（样品区）的帧区间；可自动寻找（find_buffer_range/find_sample_range）或手动给定。
  判据位置：扣减的成败取决于这两个区间是否选对；设置缓冲液区会对区间内曲线平均并逐帧计算 Rg/MW/I(0)（窗口滑动）。
  易误解：只有未扣减的序列才必须先设缓冲液区（API 原文：「setting a buffer range is only necessary if buffer subtraction has not already been performed on the series」）；缓冲液区选在峰上会污染背景。
tags: [sec, series, subtraction]
landing: extend:process-sec-saxs-series
```

```yaml
id: g64
term: 串珠模型 / 虚拟原子（bead model / DAM）
type: glossary
source_chapter: 30-saxs（saxs_bead_models）
source_quote: >-
  Bead models are low resolution. Small variations of the surface of the model
  are likely insignificant.
summary: |
  定义：用虚拟原子（DAM）堆出的低分辨 3D 形状模型；对一般球状物体最可靠。
  判据位置：需截断到最大 q = 8/Rg 或 ~0.25–0.30 1/Å（取小者，因为不含水化层与内部结构）；高纵横比（长棒/薄盘）、有空洞（球壳）、环状可靠性差。
  易误解：高质量 SAXS 数据不保证好重建（形状本身可能模糊）；串珠模型不模拟水化层、内部结构或多电子密度（后者需 MONSA/Memprot）。
tags: [bead-model, 3d-reconstruction, limitations]
landing: new
```

```yaml
id: g65
term: 反算参数的交叉验证（Rg/I(0) 一致性）
type: glossary
source_chapter: 30-saxs（saxs_ift）
source_quote: >-
  **The** \mathbf{R_{g}} **and I(0) from the Guinier fit and the P(r) function
  agree well.**
summary: |
  定义：P(r) 给出的 Rg/I(0) 应与 Guinier 拟合得到的吻合，这是「好的 P(r)」的附加判据之一。
  判据位置：判定 P(r) 好坏（另两条：P(r) 在 Dmax 平滑趋零；P(r) 在 r=0 与 r=Dmax 处为零；且始终非负）；重建模型 Rg/Dmax 也应与 P(r) 接近（高质数据 Rg 好于 ~5%、Dmax 好于 ~10%）。
  易误解：不一致时该重做 P(r) 与重建；「一致」不是看数值相等，而是在各自不确定度内一致。
tags: [ift, validation, criteria]
landing: new
```

```yaml
id: g66
term: M_ 前缀（合并曲线）
type: glossary
source_chapter: 40-tutorial（s1_waxs）
source_quote: >-
  prefix **M_** to indicate it is a merged file.
summary: |
  定义：把不同探测器（如 SAXS + WAXS）的曲线合并成一条后，文件名带 M_ 前缀（与 A_ 平均、S_ 扣减并列的命名约定）。
  判据位置：多探测器束线（如 MacCHESS G1 用双 Pilatus，q ~0.008–0.75）做 SAXS/WAXS 拼接时的产物标识。
  易误解：合并（拼接不同 q 段）与平均（同 q 段多帧合成）是两件事，前缀不同（M_ vs A_）。
tags: [ui-marker, merge, waxs, naming]
landing: new
```

```yaml
id: g67
term: Series（序列）与 SAXS 色谱图
type: glossary
source_chapter: 40-tutorial（s1_sec）
source_quote: >-
  In RAW, this is called Series analysis, as the same tools can be used for
  other sequentially sampled data sets.
summary: |
  定义：RAW 中对顺序采样数据（最常见是 SEC-SAXS）的统一分析框架；把每帧强度对帧号作图得到 SAXS 色谱图（散射色谱/scattergram），形似 UV 色谱。
  判据位置：用色谱图找缓冲液区/样品区并提取曲线；系列里可有成千上万帧但仍是一个数据条目。
  易误解：Series 不等于「多条曲线」，它是专门承载逐帧序列的视图/对象（区别于 Profiles/IFTs 选项卡）。
tags: [series, sec, ui]
landing: extend:process-sec-saxs-series
```
