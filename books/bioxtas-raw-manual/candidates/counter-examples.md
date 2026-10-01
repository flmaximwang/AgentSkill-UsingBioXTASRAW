# candidates/counter-examples.md — 反例提取器（视角 4：失败模式 / 陷阱 / 警告）

源：《BioXTAS RAW程序使用说明》· 生物小角 · 刘广峰（2024-04-26）
切片标识：`p4`。原文引用 ≤150 字/条。这是 B（边界）段的主要素材来源。

---

```yaml
- id: ce01
  title: 没加载配置就积分——不报错，但结果全错
  type: counter-example
  source_chapter: §3 RAW 程序配置文件
  source_quote: |
    "注意：任何时候要处理图像，都需要加载适当的配置！"
  failure_mode: |
    会话里没有当天几何（定心 / 样品-探测器距离）与掩膜，直接 Plot 积分：
    程序不报错、照常给出曲线，但 q 轴标定与坏点/Beamstop 处理都是错的。
  mechanism: |
    配置不属于图像文件，而属于会话状态（.cfg）。所以"打开图像"这个动作
    完全不会提示配置是否匹配；错误的入口是**沉默的**——
    曲线上看不出异常，只有与标样峰位/文献值对照才会暴露。
  warning_signs:
    - 刚启动 RAW 就直接打开数据文件夹开始 Plot
    - 换了实验日/线站/探测器，但没重新 File-Load Setting
    - q 轴数值与预期范围差一个倍数，Rg 直接差 10 倍
    - 曲线在 beamstop 阴影区出现异常突起或负值（掩膜没生效）
  bound_to:
    - "配置先行（p2-01、p2-02）"
    - "2D→1D 还原流水线（f01）"
  tags: [counter-example, silent-failure, configuration]
```

```yaml
- id: ce02
  title: 把 RAW 自动选出的 Guinier 区域当成结论
  type: counter-example
  source_chapter: §5 第②③步
  source_quote: |
    "注意：第一次打开 Guinier 窗口时，RAW 会自动尝试找到最佳的 Guinier 区域。"
    "③、…可以看到 n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。"
  failure_mode: |
    打开窗口、读走 Rg、不问 n_min/n_max 用了哪些点、不看残差。
    实例中自动选区跳过了 11 个最低 q 点——即用户并不知道自己丢掉了什么信息。
  mechanism: |
    自动选区是一个"最佳拟合"的数值器，它不知道低 q 处的物理污染
    （束流杂散、聚合、beamstop 边缘）与"被正确丢弃"在形态上很像。
    于是它会给出一个看起来干净、实际上由丢弃策略决定的 Rg。
  warning_signs:
    - Rg 只报了一个数字，没有 q 区间与 n_min/n_max
    - 残差图有明显系统弯曲但没人看
    - 轻微改变取点范围，Rg 就大幅跳动（说明并不稳定）
  bound_to:
    - "Guinier 三旋钮判读（f03）"
    - "q_max·Rg ≈ 1.3（p2-07）"
  tags: [counter-example, automation-bias, guinier]
```

```yaml
- id: ce03
  title: 不隐藏单帧曲线，平均曲线被埋在图里
  type: counter-example
  source_chapter: §4 第⑧步
  source_quote: |
    "⑧、为了清楚地看到平均散射曲线，需要从图中隐藏各个曲线。单击文件名左侧的眼睛将显示/隐藏散射曲线文件。
     …隐藏除两条平均曲线之外的所有轮廓。"
  failure_mode: |
    20 多条单帧曲线叠在一起，目视无法判断平均曲线是否异常
    （小 q 上扬、掉点、负值都被淹没在曲线丛里）。
  mechanism: |
    绘图面板是一个共享画布，所有可见文件都画在同一张图上；
    "能看见"与"看得清"是两件事，需要主动做减法。
  warning_signs:
    - 图上是一团"面条"，看不清单条曲线的走向
    - 只靠"看起来还行"下结论，没有单独看平均曲线
  bound_to:
    - "2D→1D 还原流水线（f01）"
    - "前缀与颜色状态机（p2-04）"
  tags: [counter-example, visualization, attention]
```

```yaml
- id: ce04
  title: 平均/扣减后的曲线不落盘就清理
  type: counter-example
  source_chapter: §4 第⑩步
  source_quote: |
    "⑩、选择所有散射曲线文件，然后单击"保存"按钮将它们保存在目标文件夹中。请注意，在 Profiles 列表中的
     文件名中，前面的 * 消失了，这表明这些散射曲线没有未保存的更改。现在可以删除它们。"
  failure_mode: |
    看到列表里有曲线就以为数据已经"存在"了，删掉文件或关掉会话；
    实际上未保存的曲线只活在当前会话里。
  mechanism: |
    列表里同时存在三种状态（未保存 * / 已保存 / 图像与曲线的引用），
    删除动作与保存动作在界面上并不相邻。判断能否安全删除的唯一信号是 * 是否已消失。
  warning_signs:
    - 文件名前还有 *
    - 想删曲线但不确定存过没有
    - 只保留了图（截图），没有 .dat 文件
  bound_to:
    - "曲线是必需品，图像只是保险（p2-05）"
    - "前缀与颜色状态机（p2-04）"
  tags: [counter-example, data-loss, artifacts]
```

```yaml
- id: ce05
  title: 把"功能列表"当成"我会做"——高级分析只给了链接
  type: counter-example
  source_chapter: §6 总结
  source_quote: |
    "RAW的功能还有很多，这里只是给出了基本操作。对于高级处理，如使用 GNOM 和 BIFT 方法进行对距离分布分析、
     形状重建的模糊性评估、使用串珠模型和电子密度的 3D 重建、将 3D 重建与 PDB 文件对齐等。
     可以参考 RAW 程序的在线文档"
  failure_mode: |
    读了本文就以为可以处理 IFT/GNOM、Shape&Size、贝叶斯 MW、3D 重建；
    实际上这些只有名称与一个外链，没有输入要求、判据或流程。
  mechanism: |
    操作手册的"能力清单"与"操作教程"是两种文本。能力清单告诉你软件边界，
    不构成可调用知识；把它当成教程会在真正高级的分析里空手撞墙。
  warning_signs:
    - 用户问"怎么做 GNOM/IFT/Shape&Size/3D 重建"，而手上只有这篇文章
    - 想找一个"该用哪种方法"的判据，而文章只给了方法名
  bound_to:
    - "分子量多法交叉（f05）"
    - "界面上限：本 skill 只覆盖基本还原与 Guinier 判读"
  tags: [counter-example, scope-creep, advanced-analysis]
```
