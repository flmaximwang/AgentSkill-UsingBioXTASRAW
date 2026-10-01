# candidates/cases.md — 案例提取器（视角 3）

切片标识 `q3`。案例不独立成 skill，供 V1 跨域证据与 A1 素材。

---

```yaml
- id: q3-a01
  title: sec_sample_1：965 帧的完整演练（含首帧异常与双缓冲液区）
  type: case
  source_chapter: A ①–⑪、⑫–⑮ / B 1–37
  source_quote: |
    "单击第一个数据文件 profile_001_0000.dat，按住Shift向下滚动到文件列表的底部，然后单击最后一个文件
     profile_001_0964.dat。"（A ②）
    "重置缓冲液范围，输入 504 到 562 …"（B 14）
    "对于此数据集，请尝试选择的缓冲区范围：539 到 568。"（A ⑭）
  summary: |
    问题：一条 965 帧的 SEC-SAXS 系列，要得到"这个峰里是什么"的结论。
    做法：Plot Series 载入 → 发现首帧强度异常低（MacCHESS G1 shutte 未及时开启）→
    从第 1 帧重新载入 → 看色谱图（发现峰前两个小峰=高阶寡聚体、峰后基线与峰前不等）→
    LC Analysis → Buffer Auto（504–562）→ 人工复核后 Set buffer →
    Subtracted 图上出现 Rg/MW/I(0) 随帧号 → Sample Auto（699–713；本包另一处示例 690–719）→
    确认平台 → To Profiles Plot → 得到一条扣减曲线。
    结论：一条 SEC 曲线是"色谱图 + 两个区间选择 + 平台判据"三件事的产物，不是一条命令。
  bound_to: ["三段式判读（q1-f01）", "两区互牵（q1-f02）", "先平均后扣减（q2-04）"]
  outcome: |
    官方教程给出该数据集的平台区约 699–713；源 A 同一数据给 690–719（译文版本/参数不同）。
    两处数字**不一致**，本身就是"区间选择有主观余量"的证据。
  tags: [case, sec-saxs, frames, bl19u2]
```

```yaml
- id: q3-a02
  title: BSA 的 SEC-SAXS：从平台区到 Rg/MW 的收敛
  type: case
  source_chapter: B 39–45
  source_quote: |
    "Find the useful region of the peak (constant Rg/MW), and send the buffer and sample data to the
     Profiles plot. Carry out the standard Rg and MW analysis on the subtracted scattering profile.
     For BSA, we expect Rg ~28 Å and MW ~66 kDa."
  summary: |
    问题：验证整套流程给出的曲线是否合理。
    做法：载入 sec_sample_2（BSA）→ 选出好的缓冲液区 → 算峰值处的 Rg/MW →
    取平台区送 Profiles → 做标准 Rg 与 MW 分析。
    结论：BSA 的期望值 Rg ≈ 28 Å、MW ≈ 66 kDa 构成一个"已知答案的检验点"——
    若流程正确，从 SEC 峰里提出的曲线应复现这两个数。
  bound_to: ["单分散平台判据（q2-05）", "MW 两法并列（q2-07）"]
  outcome: "教程给出期望值（Rg ~28 Å / MW ~66 kDa）作为流程正确性的锚点。"
  tags: [case, bsa, validation, molecular-weight]
```

```yaml
- id: q3-a03
  title: xylanase：积分强度呈明显线性上漂 → 线性基线校正
  type: case
  source_chapter: C 1–11
  source_quote: |
    "When it loads in, you will see there is a distinct constant upward slope in the integrated intensity.
     This usually happens due to instrumental drift, and can often be mostly corrected for."
  summary: |
    问题：扣减后"强度-帧号"仍有一段持续的上扬。
    做法：LC Analysis → 只保留峰前的缓冲液区 → Baseline correction = Linear →
    拖出峰前/峰后各约 30–50 帧的参考区 → Set baseline and calculate
    （会出现"前后两段斜率在所有 q 上不一致"的警告，属常见，可继续）。
    结论：上漂基本消失；切换回 Subtracted 图能看到橙色画出的拟校正线。
  bound_to: ["基线校正两分支（q1-f04）", "只保留峰前缓冲液（q2-09）"]
  outcome: "线性校正后上漂基本消除；低 q 处的曲线与未校正版本有明显差异（B 15）。"
  tags: [case, baseline, linear, drift]
```

```yaml
- id: q3-a04
  title: baseline.hdf5：积分校正会过校正，且过校正露在高 q
  type: case
  source_chapter: C 积分节 1–11
  source_quote: |
    "you should see that the baseline is actually a little overcorrected. This is because the integral
     baseline correction only allows for positive or no change in the baseline, so if some q values need
     a negative correction the total baseline ends up overcorrected."
  summary: |
    问题：毛细管污垢型漂移，用积分校正后基线看起来"过头了"。
    做法：把强度显示切成"某个 q 区间的强度"逐个试（推荐 0.01-0.02 / 0.05-0.06 / 0.1-0.2 / 0.2-0.27），
    定位是哪些 q 被过校正。
    结论：过校正集中在高 q——提示该 q 段基本是噪声；正确处置是先截断到较低 q 再做基线校正。
  bound_to: ["基线校正两分支（q1-f04）", "基线选型规则（q2-09）"]
  outcome: "识别出高 q 段为噪声主导，处置办法是把曲线截断到低 q 后再校正。"
  tags: [case, baseline, integral, overcorrection]
```
