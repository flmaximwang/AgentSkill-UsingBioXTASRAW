# candidates/glossary.md — 术语提取器（视角 5：关键概念词典）

源：《BioXTAS RAW程序使用说明》· 生物小角 · 刘广峰（2024-04-26）
切片标识：`p5`。词典不独立成 skill，作为共享 reference 被引用。

---

```yaml
- id: g01
  term: 配置文件（.cfg）
  type: term
  source_chapter: §3
  author_definition: |
    "配置文件允许RAW将2D图像积分为1D散射曲线。"（内含定心、校准、掩膜、标度）
  key_distinction: |
    ≠ 数据文件的一部分；≠ 每个数据集自带
    = 会话级设置，与"实验当天/那台仪器"绑定，换数据要重新确认
  why_it_matters: |
    "为什么会静默出错"的答案全在这个区分里：配置不在图像里，
    所以打开图像不会提示配置不匹配。
  tags: [term, configuration]
```

```yaml
- id: g02
  term: 定心 / 校准（centering / calibration）
  type: term
  source_chapter: §3
  author_definition: |
    "首先需要对散射图像进行定心和校准，即确定光斑中心即样品到探测器的距离"
  key_distinction: |
    = 两个几何量（光斑中心 + 样品-探测器距离）共同决定 q 轴
    ≠ 软件安装参数；≠ 探测器出厂参数
  why_it_matters: |
    所有 q 轴数值、Rg、q_max·Rg 判据都建立在这两个量之上；
    它们错了，下游判据全部无意义。
  tags: [term, geometry]
```

```yaml
- id: g03
  term: 掩膜（Masking）
  type: term
  source_chapter: §3
  author_definition: |
    "对探测器的坏点及Beamstop进行遮盖（Masking），让这些点不参与数据积分过程"
  key_distinction: |
    = 把像素标记为"不参与平均"，不是把像素从图像里抹掉
    ≠ 背景扣减（那是 Subtract 干的事）
  why_it_matters: |
    常见的把"扣背景"与"遮像素"混为一谈；两者在流水线上是不同步骤，
    一个在配置里做、一个在 Profiles 列表里做。
  tags: [term, mask]
```

```yaml
- id: g04
  term: 积分（Integrate / Plot）
  type: term
  source_chapter: §2 导航栏、§4 第④步
  author_definition: |
    "单击绘图按钮以对所有图像进行积分并在 Profiles 图中绘制积分散射曲线图。"
  key_distinction: |
    = 2D 图像 → 1D 曲线（环形平均）；方向是降维，不是"求积分面积"
    ≠ 吉尼尔拟合（那是从曲线上读 Rg）
  why_it_matters: |
    用户说"积分"时可能指两件完全不同的事；先确认是 2D→1D 还是拟合。
  tags: [term, reduction]
```

```yaml
- id: g05
  term: 平均（Average）/ A_ 前缀
  type: term
  source_chapter: §4 第⑦步
  author_definition: |
    "文件名将以绿色显示，并以 A_ 开头，表示它是平均散射曲线。"
  key_distinction: |
    = 把 N 条曲线合成一条（随机噪声按 √N 下降）
    ≠ 逐帧筛选后再平均——作者未讨论要不要剔帧
  why_it_matters: |
    平均既是降噪手段也是掩盖手段（辐射损伤、流动不稳会被平掉）。
    这条区分是 skill 边界的关键。
  tags: [term, averaging]
```

```yaml
- id: g06
  term: 扣减（Subtract）/ S_ 前缀
  type: term
  source_chapter: §4 第⑨步
  author_definition: |
    "从测量的蛋白质散射（实际上是蛋白质的散射加上缓冲液的散射）中减去缓冲液散射曲线"
    "新散射文件…名称为红色，并带有 S_ 前缀"
  key_distinction: |
    = 减去匹配缓冲液的散射；扣减双方都应是"平均曲线"
    ≠ 减去"上一次实验的缓冲液"或通用背景
  why_it_matters: |
    Subtracting 的输入选择靠星标+选中两个动作完成，
    搞错角色（把蛋白当背景）会得到符号相反的曲线而不报错。
  tags: [term, subtraction]
```

```yaml
- id: g07
  term: 星标（marking）与选中（selection）
  type: term
  source_chapter: §4 第⑥⑨步
  author_definition: |
    "单击文件名以选择散射配置文件。背景应变为蓝色，表明它已被选中。"
    "给平均的缓冲液文件标星，并选择平均的蛋白质散射文件"
  key_distinction: |
    = 星标表示"我是背景"；蓝色选中表示"我是被操作对象"
    ≠ 两者可混用
  why_it_matters: |
    Subtract 的角色分配完全由这两个 UI 状态决定，是"操作错但无报错"的高发点。
  tags: [term, ui]
```

```yaml
- id: g08
  term: 标样 / 山嵛酸银（Silver Behenate）
  type: term
  source_chapter: §3
  author_definition: |
    "BL19U2使用山嵛酸银（Silver Behenate，二十二酸银盐）作为SAXS标样，
     该样品具有5.8 nm的周期结构，第一个峰的q值为1.076 nm-1。"
  key_distinction: |
    = 用于核对几何校准的"刻度尺"（周期 5.8 nm，一级峰 q = 1.076 nm⁻¹）
    ≠ 用于绝对强度校准的标样（水/玻璃碳那类作用）
  why_it_matters: |
    这是把"配置是否正确"转成可检验事实的唯一手段；
    峰位数字是硬判据，写错就无法核对。
  tags: [term, standard, bl19u2]
```

```yaml
- id: g09
  term: q、q_max·Rg 与 Guinier 近似
  type: term
  source_chapter: §5 第②③④步
  author_definition: |
    "Rg 值的单位为 1/q（例如，如果 q 的单位为 Å-1，则Rg 的单位为 Å）。"
    "对于像 lyz 这样的球状蛋白质，q_max*Rg 通常约为 1.3。"
  key_distinction: |
    = q 是散射矢量模长（单位 Å⁻¹ 或 nm⁻¹）；q_max·Rg 是无量纲的适用范围指标
    ≠ Rg 有"默认单位"
  why_it_matters: |
    "我的 Rg 差了 10 倍"通常是单位换算问题而不是数据问题；
    q_max·Rg 决定取点区间该停在哪。
  tags: [term, guinier, units]
```

```yaml
- id: g10
  term: n_min / n_max 与残差
  type: term
  source_chapter: §5 第③④步
  author_definition: |
    "n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。"
    "底部图显示了拟合的残差。"
  key_distinction: |
    = n_min/n_max 是取点的起止索引（与"丢弃低 q 点"等价）
    ≠ 数据质量指标；残差才是
  why_it_matters: |
    只报 Rg 不报区间，等于隐藏了结论对取点策略的依赖。
  tags: [term, guinier, quality-control]
```

```yaml
- id: g11
  term: .dat 曲线文件
  type: term
  source_chapter: §4 第⑩步注意
  author_definition: |
    "注意：这会将它们保存为 .dat 扩展名。这是 SAXS 散射曲线的标准格式。"
  key_distinction: |
    = 1D 曲线的交付格式（交给 ATSAS 等下游）
    ≠ 原始数据（原始数据是探测器图像 tif/cbf）
  why_it_matters: |
    区分"原始数据"与"交付物"决定了要不要保留图像、以及归档该存什么。
  tags: [term, format, artifacts]
```

```yaml
- id: g12
  term: 绘图选项卡（Profiles / IFTs / Image / Series）
  type: term
  source_chapter: §2
  author_definition: |
    "Profiles选项卡用于查看单个散射曲线。IFTs选项卡用于查看逆傅立叶变换，
     Image选项卡用于查看探测器图像，Series选项卡用于查看SEC-SAXS 数据。"
  key_distinction: |
    = 按数据形态分的视图；Series 是 SEC-SAXS 专用，不是"多条曲线"
    ≠ 功能菜单（功能在菜单栏与按钮上）
  why_it_matters: |
    被问"该在哪里看什么"时，答案是数据形态而不是功能名称。
  tags: [term, ui]
```
