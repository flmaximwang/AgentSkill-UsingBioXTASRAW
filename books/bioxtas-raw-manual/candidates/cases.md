# candidates/cases.md — 案例提取器（视角 3：作者亲自操作的实例）

源：《BioXTAS RAW程序使用说明》· 生物小角 · 刘广峰（2024-04-26）
切片标识：`p3`。原文引用 ≤150 字/条。案例本身不独立成 skill，用于 V1 跨域证据与 A1 素材。

---

```yaml
- id: a01
  title: BSA 十个 mg/ml 的 20 帧走完整条还原流水线
  type: case
  source_chapter: §4 数据预处理 ①–⑩
  source_quote: |
    "③、在BL19U2线站，通常会从给定样本中收集约 20 张图像。要加载牛血清蛋白 (BSA) 样本的 20 个图像，
     首先选择文件 bsa10_0002_000xx.tif，其中 xx 的范围为 01 到 20。这些文件是从 10 mg/ml BSA
     散射测量的。"
  summary: |
    遇到的问题：手上是一批 2D 探测器帧，需要得到可用于下游的 1D 曲线。
    怎么用：文件选项卡定位目录 → 文件类型过滤设成 TIF → 多选 20 帧（xx=01..20）
    → Plot 积分 → 在 Profiles 列表里选中文件（变蓝）→ Average 得到绿色 A_ 曲线
    → 用眼睛图标隐藏各单帧，只留两条平均曲线 → 给缓冲液平均文件标星、选中蛋白平均文件
    → Subtract 得到红色 S_ 曲线 → 全选保存为 .dat（文件名前的 * 消失）。
    结论：一条曲线 = 若干帧 + 一次平均 + 一次扣减 + 一次落盘，缺任一步都不算完成。
  bound_to:
    - "2D→1D 还原流水线（f01）"
    - "先平均再扣减（p2-03）"
    - "前缀与颜色状态机（p2-04）"
  outcome: |
    文中未给数值结果；产出物是 .dat 曲线（SAXS 曲线的标准格式）。
    作者另提示：图像被积分后通常只使用曲线文件，保留图像只是为了重新处理。
  tags: [case, reduction, bsa, bl19u2]
```

```yaml
- id: a02
  title: lyz2 的 Guinier 拟合——自动选区把前 11 个低 q 点跳过了
  type: case
  source_chapter: §5 吉尼尔分析 ①–④
  source_quote: |
    "③、在"控制"面板中，可以看到 n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。
     可以看到最低的 q 值略有下降，这可能是它被跳过的原因。使用 n_min 框旁边的箭头按钮将其向下调整
     几个点并检查 Rg 是否发生变化。完成后，将 n_min 返回到 8。"
  summary: |
    遇到的问题：一条扣减过的溶菌酶（lyz2）曲线，要从 Guinier 区读出 Rg。
    怎么用：右键曲线 → Guinier fit（或底部 Guinier 按钮）→ RAW 自动选区（n_min=11）
    → 观察最低 q 点略有下降 → 手动把 n_min 下调到 8，看 Rg 是否随之变化
    → 在参数面板核对 q_max·Rg（实例为 ~1.27，球状蛋白经验值 ~1.3）→ 调 n_max 观察 Rg 与残差的变化。
    结论：自动选区只是起点；低 q 点的取舍会改变 Rg，必须显式检查而不是接受默认值。
  bound_to:
    - "Guinier 三旋钮判读（f03）"
    - "q_max·Rg ≈ 1.3 上界（p2-07）"
    - "Rg 单位 = 1/q（p2-06）"
  outcome: |
    文中演示了"把 n_min 从 11 调回 8"这一动作，但没有给出调整后的 Rg 数值——
    这正是该案例的用途：它示范的是**检查动作**，不是最终答案。
  tags: [case, guinier, lysozyme, quality-control]
```

```yaml
- id: a03
  title: BL19U2 的日常做法——实验前把当天参数导入 RAW
  type: case
  source_chapter: §3 配置文件
  source_quote: |
    "在BL19U2进行实验之前，线站工作人员会将当前实验参数设定好，导入RAW程序。"
  summary: |
    遇到的问题：几何/掩膜参数随线站状态变化，用户不该自己去猜。
    怎么用：线站工作人员在实验前把当天参数设好并导入 RAW；用户在自己的机器上处理时，
    用 File-Load Setting 找到"实验当天对应的 cfg 文件"导入，或用双击 .cfg 的方式加载。
    结论：cfg 与"实验当天"一一对应，这是一条运维惯例而非算法。
  bound_to:
    - "配置先行（p2-01、p2-02）"
  outcome: |
    文章明确把"其他设置问题"的处置权交给线站工作人员——即这条惯例的边界：
    离开该线站就要自己承担标定责任。
  tags: [case, configuration, bl19u2, practice]
```
