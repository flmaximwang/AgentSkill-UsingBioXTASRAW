# candidates/glossary.md — 术语提取器（视角 5）

切片标识 `q5`。术语不独立成 skill，作为共享 reference 被引用。

---

```yaml
- id: q5-g01
  term: Series（系列）
  type: term
  source_chapter: A 引言 / B 引言 note
  author_definition: |
    "在 RAW 中，这称为Series分析，因为相同的工具可用于其他顺序采样的数据集。"
  key_distinction: |
    = "按时间/顺序采样的一整串数据"这个**对象类型**（带帧号轴）
    ≠ 一堆互不相干的曲线；≠ 只有 SEC 能用（时间分辨、多序列同理）
  why_it_matters: |
    只有 Series 对象才有"帧号"这根轴，后面所有"选哪一段"的判断都建立在这根轴上；
    用普通 Plot 载入会直接丢掉这个能力。
  tags: [term, series]
```

```yaml
- id: q5-g02
  term: 色谱图 / 散点图（chromatograph / scattergram）
  type: term
  source_chapter: A 引言 / B 引言
  author_definition: |
    "总散射强度与时间的关系图（即所谓的SAXS色谱图（或散点图））将显示一组类似于SEC系统的UV吸收曲线。"
  key_distinction: |
    = 每个数据点 = **一帧**散射曲线的积分强度（或平均强度/指定 q 区强度）
    ≠ 某一条散射曲线本身
  why_it_matters: |
    "峰"这个概念在这里指时间轴上的峰，不是 I(q) 曲线上的峰；
    与 UV 痕对齐比较的也是这张图。
  tags: [term, chromatograph]
```

```yaml
- id: q5-g03
  term: buffer 区 / sample 区（帧号区间）
  type: term
  source_chapter: A ⑦⑪ / B 12–19
  author_definition: |
    "给定缓冲液范围内的所有文件将被平均并用作缓冲液区。"
    "在"Data to profiles plot"部分中，输入感兴趣的帧范围。"
  key_distinction: |
    = 帧号区间（如 504–562 / 699–713），可多段
    ≠ 文件选择（批次实验里选的是文件）
  why_it_matters: |
    扣减结果 = 样品区平均 − 缓冲液区平均；两个区间的选择直接决定曲线，
    而它们都是主观判断 + 软件检查的组合。
  tags: [term, region-selection]
```

```yaml
- id: q5-g04
  term: 滑窗 / 平均窗口大小（window size）
  type: term
  source_chapter: A ⑨ / B 15
  author_definition: |
    "对于大小为 5 的窗口，将平均对应于帧 0-4、1-5、2-6 等的配置文件。"
  key_distinction: |
    = 逐帧参数计算时的滑动平均长度（帧数）
    ≠ 缓冲液平均的范围（那是 buffer 区）
  why_it_matters: |
    它是"平滑程度 vs 时间分辨"的旋钮：太小则 Rg 曲线噪声大、
    太大则把真实的变化（如寡聚体出现的边界）抹平。
  tags: [term, sliding-window]
```

```yaml
- id: q5-g05
  term: Unsubtracted / Subtracted / Baseline Corrected 三档图
  type: term
  source_chapter: B 14–16 / C 5、9、12
  author_definition: |
    "在该图上有一条新的强度与帧# 曲线，表示扣减过的数据。"
    "The 'Baseline Corrected' plot should automatically show."
  key_distinction: |
    = 同一份 series 的三种强度-帧号视图（原始 / 扣缓冲液 / 再扣基线）
    ≠ 三种不同的数据文件
  why_it_matters: |
    判断"基线要不要校正"必须在这三档之间来回切；只在 Subtracted 上看不出漂移性质。
  tags: [term, plots]
```

```yaml
- id: q5-g06
  term: Calc markers 与 Rg / I(0) / MW(Vc) / MW(Vp)
  type: term
  source_chapter: A ⑩ / B 16
  author_definition: |
    "计算的参数绘制在右侧 Y 轴上。可以显示通过相关体积 (Vc) 和调整后的 Porod 体积 (Vp) 方法计算的
     Rg、I(0) 和 MW。"
  key_distinction: |
    = 随帧号逐点算出的结构参数（画在右轴）
    ≠ 从最终那一条平均曲线做 Guinier 拟合得到的参数（那是下游步骤）
  why_it_matters: |
    平台判据用的是前者（整条曲线上的形状），报告里通常引用后者；
    两者应大致一致，不一致说明区间选得不好。
  tags: [term, parameters]
```

```yaml
- id: q5-g07
  term: Baseline correction: Linear / Integral
  type: term
  source_chapter: C 引言
  author_definition: |
    "The linear baseline method is best for instrumental drifts, while the integral baseline method is
     best for capillary fouling. Both baseline methods apply a distinct correction for each q value."
  key_distinction: |
    Linear = 在峰前/峰后各取一段平段连直线（允许负向校正）
    Integral = 只允许基线不下降的累积型校正（毛细管污垢；每 q 一条，易在高 q 过校正）
  why_it_matters: |
    选错方法会引入比漂移更糟的假结构；积分法与 EFA 分解互斥。
  tags: [term, baseline]
```

```yaml
- id: q5-g08
  term: CHROMIXS（ATSAS 中的同类工具）
  type: term
  source_chapter: A ④ / B 8
  author_definition: |
    "ATSAS 软件中的 CHROMIXS 显示 q 范围 0.01-0.08 Å-1 上的平均强度。…RAW 将显示该范围内的强度总和，
     而 CHROMIXS 显示该范围的平均强度，因此结果不会完全相同。"
  key_distinction: |
    = 同一件事的另一个实现，**默认显示口径不同**（RAW 求和 vs CHROMIXS 求平均）
    ≠ 数值可直接对照的两个图
  why_it_matters: |
    换软件/换合作者时，色谱图纵轴口径不同会造成"数据不一样"的误判；
    对齐口径（区间+求和/平均）再比较。
  tags: [term, chromixs, cross-software]
```

```yaml
- id: q5-g09
  term: UV 痕（SEC 的紫外吸收曲线）
  type: term
  source_chapter: A ⑧ tip / B 13 tip
  author_definition: |
    "如果 SAXS 数据不清晰（嘈杂、低信号等），检查与 SEC 洗脱相关的 UV 迹线以查看应从缓冲液选择中
     排除的次要洗脱组分会很有用。"
  key_distinction: |
    = 上游色谱系统的独立信号，用作**交叉参照**
    ≠ 可以替代 SAXS 色谱图的判据
  why_it_matters: |
    它能回答"这里到底有没有洗脱物"这个 SAXS 自己答不了的问题（低信号时），
    是选缓冲液区时唯一的外部证据。
  tags: [term, uv-trace, cross-check]
```

```yaml
- id: q5-g10
  term: 平台区（flat Rg / MW region）
  type: term
  source_chapter: B 17 / A ⑩
  author_definition: |
    "A monodisperse peak should display a region of flat Rg and MW near the center."
  key_distinction: |
    = 判"这段是单一物种"的**图形判据**（参数 vs 帧号上的一段平稳）
    ≠ "峰的顶点"或"峰最对称的一段"
  why_it_matters: |
    平台区是送 Samples Plot 的充分理由；只看峰形会引入多分散而不自知。
  tags: [term, monodispersity]
```

```yaml
- id: q5-g11
  term: `.hdf5` series 文件 / report
  type: term
  source_chapter: A ⑮ / B 46–48
  author_definition: |
    "Select both items in the Series control panel list, and save them in the series_data folder.
     This saves the series data in a form that can be quickly loaded by RAW."
  key_distinction: |
    = RAW 自己的 series 容器（含区域选择、基线设置）与导出物（CSV / PDF report）
    ≠ 原始探测器数据
  why_it_matters: |
    区域选择与基线设置是**分析结论的一部分**，存成 series 才能复现与交接；
    导出的 CSV 可与 UV 痕对齐、用于作图。
  tags: [term, persistence, reproducibility]
```

```yaml
- id: q5-g12
  term: 峰前小峰（高阶寡聚体 / 聚集体）
  type: term
  source_chapter: A ⑤ / B 9
  author_definition: |
    "请注意，左侧有两个较小的峰，可能对应于我们没有正确解析信号的高阶低聚物。"
  key_distinction: |
    = 属于**样品**的组分（分离不完全）
    ≠ 背景的一部分
  why_it_matters: |
    把它算进缓冲液区等于把寡聚体当基线扣掉——这是 SEC 里最隐蔽的一类假单分散。
  tags: [term, oligomers, aggregation]
```
