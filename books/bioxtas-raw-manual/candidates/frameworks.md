# candidates/frameworks.md — 框架提取器（视角 1：可迁移的流程 / 结构）

源：《BioXTAS RAW程序使用说明》· 生物小角 · 刘广峰（2024-04-26）
切片标识：`p1`。原文引用 ≤150 字/条。

---

```yaml
- id: f01
  title: 2D→1D 还原流水线（配置 → 积分 → 平均 → 扣减 → 保存）
  type: framework
  source_chapter: §4 数据预处理（①–⑩）
  source_quote: |
    "④、单击绘图按钮以对所有图像进行积分并在 Profiles 图中绘制积分散射曲线图。"
    "⑦、使用"平均（Average）"按钮将收集到的所有散射曲线平均到一条曲线中。"
    "⑨、…给平均的缓冲液文件标星，并选择平均的蛋白质散射文件，然后单击"Subtract"按钮。"
    "⑩、选择所有散射曲线文件，然后单击"保存"按钮将它们保存在目标文件夹中。"
  summary: |
    一条四段式的降维—降噪—去背景—落盘流水线：
    2D 帧 →（积分，环形平均）→ 1D 曲线 →（平均同类帧，压噪）→ 代表曲线
    →（星标缓冲液 + 扣减）→ 净散射曲线 →（存 .dat）→ 交付物。
    每段的产物都在 Profiles 列表里以"前缀 + 颜色"留下状态痕迹，
    因此整条流水线的进度是可机检的（A_ / S_ / * / 颜色）。
    流水线的前置条件是"配置已加载"，后置条件是"能交给下游做结构分析"。
  tags: [framework, pipeline, reduction, saxs]
```

```yaml
- id: f02
  title: 配置文件四要素（定心 + 校准 + 掩膜 + 标度）
  type: framework
  source_chapter: §3 RAW 程序配置文件
  source_quote: |
    "配置文件允许RAW将2D图像积分为1D散射曲线。为了实现该功能，首先需要对散射图像进行定心和校准，
     即确定光斑中心即样品到探测器的距离，然后需要对探测器的坏点及Beamstop进行遮盖（Masking），
     让这些点不参与数据积分过程。针对特殊实验样品，还可以设置水或玻璃碳作为绝对标度，
     或一个分子量已知的标样作为分子量标准。"
  summary: |
    把"积分"拆开看，它需要的不是图像，而是四类几何/标度信息：光斑中心、
    样品到探测器距离（合起来决定 q 轴）、掩膜（决定哪些像素不进平均）、
    标度（决定强度是否绝对、能否推分子量）。这四件事与实验当天绑定，
    不与图像文件绑定——所以"换了数据不换配置"是一个无声错误：
    程序照常出曲线，只有 q 轴与 Rg 系统性错位。
    确证手段是把当天的标样当作可检验锚点。
  tags: [framework, configuration, calibration, mask]
```

```yaml
- id: f03
  title: Guinier 拟合的三旋钮判读（取点区间 / 残差 / q_max·Rg）
  type: framework
  source_chapter: §5 吉尼尔分析（①–④）
  source_quote: |
    "③、在"控制"面板中，可以看到 n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。
     …使用 n_min 框旁边的箭头按钮将其向下调整几个点并检查 Rg 是否发生变化。"
    "④、在"参数"面板中，请注意 q_max*Rg 为 ~1.27。…稍微调整 n_max，观察 Rg和残差的变化。"
  summary: |
    RAW 打开 Guinier 窗口时会自动找"最佳区域"，但那只是起点。判读靠三个可调旋钮：
    (1) n_min —— 最低 q 点常被束流杂散/聚合污染，跳过几点后 Rg 是否稳定；
    (2) 残差图 —— 直线拟合是否成立的第一手证据（看形态，不是看"像不像直线"）；
    (3) q_max·Rg —— 球状蛋白经验上限 ≈1.3，决定 n_max 该停在哪。
    三者冲突时优先保残差形态，并在报告里带上所用 q 区间与 n_min/n_max。
  tags: [framework, guinier, quality-control]
```

```yaml
- id: f04
  title: 绘图面板四选项卡 = 四类数据的四个视图
  type: framework
  source_chapter: §2 RAW 程序界面
  source_quote: |
    "绘图面板包含四个选项卡：主绘图（Profiles）、IFT绘图（IFTs）、图像绘图（Image）和SEC绘图（Series）。
     Profiles选项卡用于查看单个散射曲线。IFTs选项卡用于查看逆傅立叶变换，Image选项卡用于查看探测器图像，
     Series选项卡用于查看SEC-SAXS 数据。"
  summary: |
    界面按"数据形态"分视图：原始 2D 帧（Image）→ 单条/多条 1D 曲线（Profiles）→
    距离分布变换（IFTs）→ 层析序列（Series）。
    "该去哪儿看"这个问题的答案是"你现在手上是什么形态的数据"，
    于是它也隐含了流程顺序：Image 里看原始帧、Profiles 里做还原、IFTs/Series 是下游。
    文章本身只用到 Profiles（还原）与右键的 Guinier 窗口。
  tags: [framework, ui, navigation]
```

```yaml
- id: f05
  title: 分子量测定的多法交叉框架
  type: framework
  source_chapter: §0 引言（能力清单）
  source_quote: |
    "通过与标准样品的 I0 比较、绝对校准、相关体积 (Vc)、校正的 Porod 体积 (Vp)、
     ATSAS 程序包中的 Shape&Size 和 Bayesian 方法分析分子量（MW）"
  summary: |
    文章给出六条互相独立的分子量估计路线（标样 I0 比对 / 绝对校准 / Vc / Vp /
    Shape&Size / Bayesian），骨架是"同一物理量用多种互不依赖的方法各估一次，
    看它们是否收敛"。但文章只列了名称，没有给任何一条的操作步骤、输入要求或一致判据。
  tags: [framework, molecular-weight, multi-method]
```
