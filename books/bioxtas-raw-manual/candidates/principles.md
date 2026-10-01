# candidates/principles.md — 原则提取器（视角 2：规则 / 清单 / 断言）

源：《BioXTAS RAW程序使用说明》· 生物小角 · 刘广峰（2024-04-26）
切片标识：`p2`。原文引用 ≤150 字/条。

---

```yaml
- id: p2-01
  title: 配置先行——处理任何图像前都要加载适当的配置
  type: principle
  source_chapter: §3 RAW 程序配置文件（加粗提示）
  source_quote: |
    "注意：任何时候要处理图像，都需要加载适当的配置！"
  summary: |
    无条件规则：积分的前置条件不是"打开图像"，而是"当前会话里装的是哪套几何/掩膜"。
    违反的代价不是报错，而是静默的错误结果——曲线照出，q 轴与 Rg 错。
    因此这条规则的可执行形式是"开机先 File-Load Setting / 双击当天 .cfg，再用标样核对"。
  tags: [principle, precondition, silent-failure]
```

```yaml
- id: p2-02
  title: 换数据就要确认配置是否仍然对应那一天
  type: principle
  source_chapter: §3（线站做法）与 §4 第①步
  source_quote: |
    "在BL19U2进行实验之前，线站工作人员会将当前实验参数设定好，导入RAW程序。
     如果在自己的计算机上使用RAW程序，只需点击File-Load Setting，找到实验当天对应的cfg文件导入，
     即可完成程序的配置工作。"
  summary: |
    配置的正确性判据是"实验当天"，不是"昨天"。因此每次换数据集时的自检动作是：
    先确认这个数据集属于哪一天/哪台仪器，再确认加载的 cfg 与之对应。
    线站把这一步做掉了，自己做数据处理的人必须自己补上。
  tags: [principle, configuration, checklist]
```

```yaml
- id: p2-03
  title: 先平均同类帧，再扣减缓冲液（且缓冲液必须单独测、单独平均）
  type: principle
  source_chapter: §4 第⑦⑧⑨步
  source_quote: |
    "⑦、使用"平均（Average）"按钮将收集到的所有散射曲线平均到一条曲线中。"
    "⑨、接下来，需要从测量的蛋白质散射（实际上是蛋白质的散射加上缓冲液的散射）中减去缓冲液散射曲线。
     给平均的缓冲液文件标星，并选择平均的蛋白质散射文件，然后单击"Subtract"按钮。"
  summary: |
    两步有固定次序：先把同类帧各自收敛成一条代表曲线（蛋白一份、缓冲液一份），
    再做一次减法。扣减的双方都必须是"代表曲线"，用单帧去减平均曲线会把
    那单帧的噪声一起带进结果。角色分配靠星标：星标的是缓冲液，选中的是样品。
  tags: [principle, averaging, buffer-subtraction, order]
```

```yaml
- id: p2-04
  title: 前缀与颜色是流水线状态机，必须会读
  type: principle
  source_chapter: §4 第⑦⑨⑩步
  source_quote: |
    "文件名将以绿色显示，并以 A_ 开头，表示它是平均散射曲线。"
    "新散射文件应显示在散射文件列表中，名称为红色，并带有 S_ 前缀，表示它是一个扣减过的曲线文件。"
    "请注意，在 Profiles 列表中的文件名中，前面的 * 消失了，这表明这些散射曲线没有未保存的更改。"
  summary: |
    三条机检信号：A_ = 平均产物；S_ = 扣减产物；文件名前的 * = 有未保存改动。
    另有一条交互信号：被选中的文件名背景变蓝。会用这三个信号，
    就能在不解开每一步的情况下判断流水线走到哪、有没有漏保存。
  tags: [principle, convention, state-machine]
```

```yaml
- id: p2-05
  title: 曲线是必需品，图像只是保险
  type: principle
  source_chapter: §4 第④步注意
  source_quote: |
    "注意：通常，一旦图像被积分，我们只使用散射曲线文件。但是，如果想重新处理数据，保留图像很有用。"
  summary: |
    交付物是 .dat 曲线；2D 帧的价值只在"想用另一套配置重做"时兑现。
    推论：做完当场就把曲线存下来（存 .dat 是标准格式），而不是留在会话里；
    是否保留图像取决于"这台机器/这个掩膜还会不会变"。
  tags: [principle, data-management, artifacts]
```

```yaml
- id: p2-06
  title: Rg 的单位是 1/q——报告必须带单位
  type: principle
  source_chapter: §5 第②步注意
  source_quote: |
    "注意：Rg 值的单位为 1/q（例如，如果 q 的单位为 Å-1，则Rg 的单位为 Å）。"
  summary: |
    Rg 的数值与 q 的单位制度绑定：q 用 Å⁻¹ 则 Rg 用 Å，q 用 nm⁻¹ 则 Rg 用 nm，
    两者相差 10 倍。因此任何 Rg 数字都必须连单位与所用 q 区间一起报告，
    否则无法与文献比较，也无法判断"差 10 倍"是数据问题还是单位问题。
  tags: [principle, units, reporting]
```

```yaml
- id: p2-07
  title: 球状蛋白的拟合上界 q_max·Rg ≈ 1.3
  type: principle
  source_chapter: §5 第④步
  source_quote: |
    "④、在"参数"面板中，请注意 q_max*Rg 为 ~1.27。回想一下，对于像 lyz 这样的球状蛋白质，
     q_max*Rg 通常约为 1.3。稍微调整 n_max，观察 Rg和残差的变化。"
  summary: |
    取点区间的上界不由"数据到哪结束"决定，而由 q_max·Rg≈1.3 这条经验线决定：
    超过它，Guinier 近似（低 q 展开）本身就不成立。
    注意作者给的是"像 lyz 这样的球状蛋白质"——这是条件式规则，不是通用定律。
  tags: [principle, guinier, empirical-limit]
```

```yaml
- id: p2-08
  title: 用标样把"校准对不对"变成一个可检验的事实
  type: principle
  source_chapter: §3（BL19U2 标样）
  source_quote: |
    "BL19U2使用山嵛酸银（Silver Behenate，二十二酸银盐）作为SAXS标样，
     该样品具有5.8 nm的周期结构，第一个峰的q值为1.076 nm-1。"
    "线站使用的探测器为Pilatus 2M，该探测器具有1679*1475像素，单个像素尺寸为172*172微米。"
  summary: |
    标样的作用是把"我以为几何设对了"变成"第一个峰确实落在 1.076 nm⁻¹"。
    因此每次换配置后，正确动作是拿当天标样帧做一次积分并核对峰位。
    探测器型号/像素尺寸这类参数只有在需要反推几何时才用得上，属于背景事实。
  tags: [principle, standard, verification]
```

```yaml
- id: p2-09
  title: 安装用预构建包（稳定性与速度优于源码编译）
  type: principle
  source_chapter: §1 RAW 的安装
  source_quote: |
    "最简单的方法是使用预构建的安装程序（.msi 文件），强烈推荐使用此方法安装，
     程序的稳定性及运行速度比源码安装都要好。"
  summary: |
    平台上能拿到预构建包就用预构建包，只有在没有对应版本时才回到源码编译。
    这是安装期的一次性经验，不构成需要沉淀的方法论（→ 降级为背景事实）。
  tags: [principle, installation, one-off]
```
