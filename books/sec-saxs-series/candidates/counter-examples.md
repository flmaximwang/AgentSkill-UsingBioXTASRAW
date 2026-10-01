# candidates/counter-examples.md — 反例提取器（视角 4）

切片标识 `q4`。这是 B（边界）段的主要素材。

---

```yaml
- id: q4-ce01
  title: 相信自动选出的缓冲液区
  type: counter-example
  source_chapter: A ⑧ / B 13
  source_quote: |
    "警告：自动选择缓冲液可能是错误的！始终手动检查程序选择的区域。特别是，主峰旁边的大而平坦的前缘肩部
     可能看起来像算法的基线区域，并且经常会被错误地挑选出来。"
  failure_mode: |
    点一下 Auto 就用它给的区间去 Set buffer，结果峰前的高阶寡聚体小峰/肩部被当成缓冲液，
    被当作背景扣掉——主峰会显得比实际更单分散、Rg/MW 平台更漂亮。
  mechanism: |
    自动算法判据是"强度低 + 形状平"，而部分分离的寡聚体前肩恰好同时满足这两条；
    算法没有"这是不是缓冲液"的物理概念，只有几何/强度概念。
  warning_signs:
    - Auto 之后没放大到基线处逐帧看过
    - 缓冲液区紧挨着主峰左侧的肩部
    - UV 痕上在主峰前有小峰，而缓冲液区把它包含了
  bound_to: ["自动必复核（q2-03）", "小峰是寡聚体（q2-10）"]
  tags: [counter-example, automation-bias, baseline]
```

```yaml
- id: q4-ce02
  title: 先逐帧扣减、再把结果平均
  type: counter-example
  source_chapter: B 19（note） / A ⑨（note）
  source_quote: |
    "RAW first averages the selected sample and buffer regions in the unsubtracted data, then subtracts.
     This avoids the possibility of correlated noise that would arise from averaging the subtracted files."
  failure_mode: |
    手工路线下先把每帧都扣一遍缓冲液、再对这些"已扣减帧"求平均：
    各帧的噪声因为共用了同一份缓冲液而变得相关，平均不再按 √N 降噪。
  mechanism: |
    平均能降噪的前提是各样本的误差互相独立；共用同一条缓冲液平均曲线，
    就把这条缓冲液自身的误差复制到了每一帧里，变成不可平均的系统偏差。
  warning_signs:
    - 用 Profiles 列表里已有的 S_ 曲线（已扣减）去做 Average
    - 结果对缓冲液区长度异常敏感
  bound_to: ["先平均后扣减（q2-04）", "手动替代路径（q1-f05）"]
  tags: [counter-example, noise, order-of-operations]
```

```yaml
- id: q4-ce03
  title: 用峰前单侧缓冲液，忽略峰后基线已经不同
  type: counter-example
  source_chapter: A ⑤ / B 23–33
  source_quote: |
    "另请注意，峰后的基线与峰前的基线不同。发生这种情况的原因有多种，例如粘附在样品池窗口上的受损蛋白质。"
  failure_mode: |
    只取峰前一段缓冲液就做完扣减：峰后区域出现上下偏移，
    低 q 处（对基线最敏感）出现假的"上扬/下坠"。
  mechanism: |
    基线变化来自仪器漂移或样品池窗口污染，是随时间累积的——一个平均值无法代表全程。
  warning_signs:
    - 扣减后强度在峰的右侧不回到 0 附近
    - 同一峰在前后两个不同缓冲液区下扣出的曲线不同（教程明确说 Guinier 拟合会有"细微但可察觉"的差别）
  bound_to: ["双侧缓冲液或基线校正（q2-08）", "基线校正选型（q2-09）"]
  tags: [counter-example, baseline, drift]
```

```yaml
- id: q4-ce04
  title: 把批次实验的习惯（标样 I0/绝对校准）搬到 SEC 上
  type: counter-example
  source_chapter: B 22（note，源 A 未收录）
  source_quote: |
    "The I(0) reference and absolute calibration will not be accurate for SEC-SAXS data,
     as the concentration is not accurately known."
  failure_mode: |
    用已知标样把 SEC 峰的 I(0) 折算成浓度/分子量，得到看起来精确但没有意义的数字。
  mechanism: |
    绝对校准的前提是"测的时候浓度已知且恒定"；SEC 峰内浓度随时间变化且未知，
    于是 I(0) 的绝对标定失去基准。相对比较（同一峰内不同帧之间、Vc/Vp）仍然成立。
  warning_signs:
    - 报告里给出"绝对浓度"或"由标样折算的 MW"
    - 只报一个 MW 数字、不说它来自 Vc 还是 Vp
  bound_to: ["浓度未知限制（q2-06）", "MW 两法并列（q2-07）"]
  tags: [counter-example, absolute-calibration, molecular-weight]
```

```yaml
- id: q4-ce05
  title: 以为手动路径与 LC Analysis 等价
  type: counter-example
  source_chapter: A ⑫–⑮
  source_quote: |
    "如果不想使用LC Analysis，也可以进行如下操作：…在"Data to profiles plot"部分中，输入感兴趣的帧范围…
     然后单击"Average"按钮。"
  failure_mode: |
    直接用手动路径（输入帧范围 → Average → 扣减），跳过逐帧 Rg/MW 曲线，
    于是"这段是不是一个物种"没有任何证据，只凭"峰看起来是个单峰"。
  mechanism: |
    手动路径产出的是一条曲线，而平台判据需要的是"参数随帧号的变化"这一整条信息。
    丢掉的信息无法在事后补（除非重跑）。
  warning_signs:
    - 说"我看峰挺对称的"就定了帧范围
    - 没有 Subtracted 图，也没有 Calc markers
  bound_to: ["手动替代路径（q1-f05）", "平台判据（q2-05）"]
  tags: [counter-example, manual-path, missing-evidence]
```

```yaml
- id: q4-ce06
  title: 在做过积分基线校正的数据上做 EFA 分解
  type: counter-example
  source_chapter: B 33（note）/ C 引言
  source_quote: |
    "If you want to do EFA deconvolution, it is best to not use a baseline correction, however in other
     cases it will be more accurate as it doesn't assume a single average buffer across the peak."
  failure_mode: |
    先做积分基线校正，再做 EFA/SVD 类分解：分解算法会把"校正本身引入的形状"当成一个组分。
  mechanism: |
    积分校正对基线只允许不降，会在数据里留下一个单调的、与 q 相关的变形；
    分解算法假定观测 = 各组分光谱 × 浓度的线性组合，于是把这个变形也拟合成了"物种"。
  warning_signs:
    - 分解得到 3 个以上组分、其中一个是"缓慢单调的"
    - 同一数据不做基线校正时组分数不同
  bound_to: ["基线选型规则（q2-09）", "校正两分支（q1-f04）"]
  tags: [counter-example, efa, baseline-correction]
```

```yaml
- id: q4-ce07
  title: 把首帧/末帧留在分析里
  type: counter-example
  source_chapter: A ③
  source_quote: |
    "第一帧的强度明显低于其余帧。…在19U2，如果需要进行强度校正，则由于统计规则，最后一帧不能用。"
  failure_mode: |
    两端异常帧混在 series 里：首帧把整条曲线的基线压低、影响目视判断与自动 buffer 选择；
    BL19U2 的末帧参与强度校正会引入偏差。
  mechanism: |
    端点帧的异常来自采集时序（shutter 未及时开启）或统计规则（末帧计数不完整），
    不是样品的性质，但它们落在"基线区"里，会直接改变基线与归一化的取值。
  warning_signs:
    - 色谱图最左端有一个孤立低点
    - 未确认过首帧是否需要剔除
  bound_to: ["端点帧先剔（q2-02）"]
  tags: [counter-example, frame-selection, bl19u2]
```
