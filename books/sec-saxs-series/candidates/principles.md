# candidates/principles.md — 原则提取器（视角 2）

切片标识 `q2`。引用 ≤150 字/条。

---

```yaml
- id: q2-01
  title: 连续采集的数据用 Plot Series 载入，不是 Plot
  type: principle
  source_chapter: A ①② / B 2–3
  source_quote: |
    "单击第一个数据文件 profile_001_0000.dat，按住Shift向下滚动到文件列表的底部，然后单击最后一个文件
     profile_001_0964.dat。单击"Plot Series"按钮将系列加载到 RAW。"
  summary: |
    Series 与普通曲线是两种对象：Plot 只能给你"一堆曲线"，Plot Series 才建立"帧号"这根轴。
    没有帧号轴，后面所有关于"哪一段"的判断都无从谈起。
  tags: [principle, loading, series]
```

```yaml
- id: q2-02
  title: 端点帧先剔掉（首帧强度异常、BL19U2 末帧不可用于强度校正）
  type: principle
  source_chapter: A ③ / B 5–7
  source_quote: |
    "拖动绘图，可以清楚地看到第一帧的强度明显低于其余帧。这是因为数据是在 MacCHESS G1 光束线收集的，
     有时候shutter开启不及时，这不利于判断数据。"（A）
    "在19U2，如果需要进行强度校正，则由于统计规则，最后一帧不能用。"（A，线站增补）
  summary: |
    series 的两个端点有固定的技术性例外：首帧可能因 shutter 未及时开启而整帧偏弱；
    BL19U2 上末帧因统计规则不能用于强度校正。两者都会污染"基线"和"峰形"的目视判断，
    所以载入/分析时要显式排除，而不是留着让眼睛适应它。
  tags: [principle, frame-selection, bl19u2]
```

```yaml
- id: q2-03
  title: 自动选出的缓冲液区必须人工复核（峰前平肩是陷阱）
  type: principle
  source_chapter: A ⑦⑧ / B 12–13
  source_quote: |
    "警告：自动选择缓冲液可能是错误的！始终手动检查程序选择的区域。特别是，主峰旁边的大而平坦的前缘肩部
     可能看起来像算法的基线区域，并且经常会被错误地挑选出来。"
  summary: |
    自动算法只认"平"与"低"，不认"是不是缓冲液"。主峰左侧的高阶寡聚体/聚集体小峰
    恰恰长得像平缓基线。必须放大到基线处逐帧核对，必要时用上下箭头微调，
    或对照 UV 痕确认有没有被漏掉的次要洗脱组分。
  tags: [principle, automation-bias, buffer-selection]
```

```yaml
- id: q2-04
  title: 先平均、后扣减（顺序不可交换）
  type: principle
  source_chapter: A ⑨ / B 19 note
  source_quote: |
    "RAW first averages the selected sample and buffer regions in the unsubtracted data, then subtracts.
     This avoids the possibility of correlated noise that would arise from averaging the subtracted files."
  summary: |
    正确顺序：① 缓冲液区内所有帧先平均成一条缓冲液曲线；② 样品区帧按窗口平均后，
    再与那条平均缓冲液相减。反过来（先逐帧扣减再平均）会让各帧的噪声相关化，
    平均无法按 √N 降噪——误差被"平均"进结果里而不是被压掉。
  tags: [principle, order-of-operations, noise]
```

```yaml
- id: q2-05
  title: 单分散的判据是"平台"，不是"峰看起来干净"
  type: principle
  source_chapter: A ⑩⑪ / B 16–18
  source_quote: |
    "一旦对选择的区域（应该是 690-719）感到满意，请单击"到 Profiles Plot"按钮。"（A）
    "A monodisperse peak should display a region of flat Rg and MW near the center."（B 17）
  summary: |
    判定"这一段是一个物种"的依据是 Rg 与 MW 在峰中心形成一段平稳区间；不是峰对称、
    也不看曲线好不好看。两侧的起伏各有来源：低信噪比（浓度低）、肩峰（其他组分）、
    左右基线不等（损伤蛋白粘窗）。选样品的动作就是把那段平台圈出来。
  tags: [principle, monodispersity, judgement]
```

```yaml
- id: q2-06
  title: SEC 数据不能用绝对校准/I0 标样来定浓度
  type: principle
  source_chapter: B 22 note（源 A 未提）
  source_quote: |
    "The I(0) reference and absolute calibration will not be accurate for SEC-SAXS data,
     as the concentration is not accurately known."
  summary: |
    批次实验里浓度已知，可以用已知标样把 I(0) 折算成分子量；SEC 里样品是边洗脱边测的，
    峰内浓度未知，所以 I(0) 的绝对值不可用。MW 只能走 Vc / Vp 这类由形状与体积出发的路线，
    并且两法结果不一致属正常，应并列报告。
  tags: [principle, molecular-weight, limitation]
```

```yaml
- id: q2-07
  title: MW 的两种估计要一起看
  type: principle
  source_chapter: A ⑩ / B 16
  source_quote: |
    "可以显示通过相关体积 (Vc) 和调整后的 Porod 体积 (Vp) 方法计算的 Rg、I(0) 和 MW。
     单击"计算值"菜单可在不同显示之间切换。"
  summary: |
    Vc 与 Vp 是两条独立的估计路线，数值常常不同。单看一个会给人"精确"的错觉；
    两个都看，差异本身就是信息（形状偏离球状、基线残留、信噪比不足都会让它们分道扬镳）。
  tags: [principle, multi-method, molecular-weight]
```

```yaml
- id: q2-08
  title: 峰两侧基线不等 → 用双侧缓冲液，或改用基线校正
  type: principle
  source_chapter: A ⑤ / B 23–33、33 note
  source_quote: |
    "另请注意，峰后的基线与峰前的基线不同。发生这种情况的原因有多种，例如粘附在样品池窗口上的受损蛋白质。"（A）
    "An alternative approach to using several buffer regions is to use a single buffer region and apply
     a baseline correction. Both approaches have advantages and disadvantages."（B）
  summary: |
    单缓冲液区（只取峰前）在基线漂移时会系统性偏移。两条正路：
    (a) 峰前 + 峰后各取一段缓冲液（RAW 会提示两个区间不一致——此时应当"继续"而不是取消）；
    (b) 单个缓冲液区 + 基线校正。
    二者不是等价的：基线校正不假设"全峰同一个缓冲液"，但在做 EFA 分解时不能叠加使用。
  tags: [principle, buffer-selection, baseline-correction]
```

```yaml
- id: q2-09
  title: 基线校正的选型规则与互斥条件
  type: principle
  source_chapter: C 引言、3–4、14
  source_quote: |
    "The linear baseline method is best for instrumental drifts, while the integral baseline method is
     best for capillary fouling. … To baseline correct data, you should only have buffer regions selected
     before the peak."
  summary: |
    选型看漂移的性质：仪器/束流漂移 → Linear；毛细管污垢（污染随剂量累积）→ Integral。
    两条前置条件：(1) 校正前只保留峰前的缓冲液区；(2) 起止参考区必须落在真正平的基线段里，
    否则 RAW 会警告（且积分法过校正会在高 q 露出来）。
    互斥：要做 EFA 分解就不要用基线校正（尤其积分法）。
  tags: [principle, baseline-correction, decision-rule]
```

```yaml
- id: q2-10
  title: 峰前的小峰当寡聚体处理，不要塞进缓冲液区
  type: principle
  source_chapter: A ⑤ / B 9、15 warning
  source_quote: |
    "请注意，左侧有两个较小的峰，可能对应于我们没有正确解析信号的高阶低聚物。"
    "It is important that the buffer range actually be buffer! In this case, we need to make sure
     to not include the small peaks before the main peak."
  summary: |
    SEC 峰前的小峰通常是被部分分开的高阶寡聚体/聚集体——它们是"样品"而不是"背景"。
    把它们算进缓冲液区，等于把寡聚体的散射当作基线扣掉，会让主峰看起来更单分散。
    正确做法是把缓冲液区限制在真正无样品洗脱的平段（必要时靠 UV 痕确认）。
  tags: [principle, oligomers, buffer-selection]
```

```yaml
- id: q2-11
  title: 区间可以被软件"体检"，警告不要当成噪音
  type: principle
  source_chapter: B 20
  source_quote: |
    "For buffer regions, RAW checks frame-wise similarity across the whole q range and at low and high q,
     correlations in intensity, and whether there are multiple singular values in the selected region."
  summary: |
    RAW 对选中的 buffer 区做四项检查（全 q 范围帧间相似度、低/高 q 各自行为、强度相关性、
    是否出现多个奇异值），对 sample 区还检查 Rg/MW 的相关性与是否有个别帧拉低信噪比。
    这些警告指向的是"这一段的物理假设被破坏"，不是界面唠叨——应读警告内容再决定是否继续。
  tags: [principle, quality-check, warnings]
```
