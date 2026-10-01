# candidates/frameworks.md — 框架提取器（视角 1）

源 A = 微信《利用BioXTAS RAW程序处理SEC-SAXS数据》（`A`）；源 B = 官方 *Basic SEC-SAXS processing*（`B`）；源 C = 官方 *Baseline correction*（`C`）。
切片标识 `q1`。引用 ≤150 字/条。

---

```yaml
- id: q1-f01
  title: SEC 数据的三段式判读流程（色谱图 → 区域 → 一条曲线）
  type: framework
  source_chapter: A ①–⑪ / B 1–22
  source_quote: |
    "在典型的SEC-SAXS实验中，当色谱柱的洗脱液（流出物）流过SAXS样品池时，会连续收集图像…
     RAW包含对SEC-SAXS数据进行处理的功能：可以根据数据创建SAXS色谱图，在峰上绘制Rg，MW和I(0)，
     以及提取特定帧以进行进一步分析。"（A 引言）
  summary: |
    与批次还原的根本差别：先看整个洗脱过程，再决定拿哪一段当"一个样品"。
    三段是：(1) 读色谱图（强度-帧号）确定峰的位置与形状；
    (2) 在峰上用 Rg/MW 的平台区判定哪一段是单一物种，并同时定出缓冲液区；
    (3) 只把那段样品 + 那段缓冲液平均、扣减，得到一条可交付的曲线。
    中间任何一段的判断错了，最后那条曲线看起来都"正常"。
  tags: [framework, sec-saxs, pipeline]
```

```yaml
- id: q1-f02
  title: 缓冲液区-样品区：一次判断里两个互相牵制的选择
  type: framework
  source_chapter: A ⑦–⑪ / B 12–19
  source_quote: |
    "为了计算 Rg 和其他参数作为洗脱时间（帧#）的函数，需要定义一个缓冲区。RAW 可以自动执行此操作。"
    "注意：给定缓冲液范围内的所有文件将被平均并用作缓冲液区。然后在 SEC 曲线上移动一个滑动平均窗口…"（A ⑦⑨）
  summary: |
    缓冲液区与样品区不是两个独立步骤：扣减结果 = 样品区平均 − 缓冲液区平均，
    所以缓冲液区选错（把峰前肩部/小峰当基线）会污染整条曲线，而样品区选错
    （把非平台区纳入）会把多分散混进平均值。两区都要人工复核，且判断依据不同：
    缓冲液区靠"是不是真的缓冲液"（帧间相似性、低/高 q 行为、无多组分），
    样品区靠"Rg/MW 是否成平台 + 信噪比"。
  tags: [framework, buffer-selection, sample-selection]
```

```yaml
- id: q1-f03
  title: 滑窗逐帧参数：把"这条数据是几个物种"变成一个可看的曲线
  type: framework
  source_chapter: A ⑨⑩ / B 15–17
  source_quote: |
    "对于大小为 5 的窗口，将平均对应于帧 0-4、1-5、2-6 等的配置文件。从每组平均曲线中减去
     平均缓冲液强度，RAW 将尝试计算 Rg、MW 和 I(0)。然后将这些值绘制为帧数的函数。"
  summary: |
    不直接对单帧做扣减（信噪比不够），而是用大小 N 的滑动窗口逐段平均后再扣减，
    从而得到 Rg(帧)、MW(帧)、I(0)(帧)。于是"峰里是不是一个物种"这个问题
    被转换成"Rg/MW 在峰中心有没有一段平台"——一个可以肉眼检查的图形判据。
    N 越大越平滑（也越抹掉真实变化），N 越小越噪。
  tags: [framework, sliding-window, monodispersity]
```

```yaml
- id: q1-f04
  title: 基线校正的两分支决策（线性 vs 积分）
  type: framework
  source_chapter: C 全篇（含引言）
  source_quote: |
    "Sometimes SEC data shows a baseline drift. This can be due either to instrumental changes
     (such as beam drift), or changes in the measured system, such as capillary fouling.
     RAW provides the ability to correct for these forms of baseline drift using either a linear
     or integral baseline method… Both baseline methods apply a distinct correction for each q value."
  summary: |
    扣减之后若"强度-帧号"仍有系统性漂移，先判性质再选方法：
    仪器/束流漂移 → 线性校正（在峰前后各取一段无基线变化的平段，连直线）；
    毛细管污垢（样品池窗口被污染，基线随累积剂量上升）→ 积分校正（只允许基线单调不降，
    每个 q 各算一条）。二者都对每个 q 施加**各自不同**的校正，因此低 q 与高 q 的行为可能不同。
  tags: [framework, baseline-correction, drift]
```

```yaml
- id: q1-f05
  title: 手动替代路径（绕开 LC Analysis）
  type: framework
  source_chapter: A ⑫–⑮
  source_quote: |
    "如果不想使用LC Analysis，也可以进行如下操作：…在"Data to profiles plot"部分中，输入感兴趣的帧范围。
     对于此数据集，请尝试选择的缓冲区范围：539 到 568。然后单击"Average"按钮。"
  summary: |
    不打开 LC Analysis 面板，也可以：给目标 series 加星 → 在 "Data to Profiles plot" 输入帧范围
    → Average 送到 Profiles → 再用批次还原的老办法（星标缓冲液 + Subtract）得到净散射。
    代价：没有逐帧 Rg/MW 曲线可看，**平台判据失去支撑**——等于放弃了"这段是不是一个物种"的证据。
  tags: [framework, manual-path, tradeoff]
```
