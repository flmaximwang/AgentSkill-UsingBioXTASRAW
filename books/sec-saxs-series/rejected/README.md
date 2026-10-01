# rejected/ — 淘汰与降级记录（第 2 本：SEC-SAXS 系列，审计用）

依据见 `../verified.md`。候选原文留在 `../candidates/`。

---

## `deconvolve-sec-saxs-series` — SVD / EFA / REGALS 分解

- **判决**: V2 预测力不通过（材料不足以外推）+ 可执行性不通过
- **条数**: 0 条实抽候选（只在源中出现为**能力名称**）

源 A 完全没提；源 B 只在"高级处理"小节列出 `s2_svd` / `s2_efa` / `s2_regals` 三个教程链接，
本包未抓取其正文。以现有材料做不出"什么时候该分解、分解几个组分、结果怎么看"的任何判据，
只能复述"RAW 能做分解"。

**处置**：不成 skill。**唯一的残留价值是一条边界**，已写进 `correct-sec-saxs-baseline` 的 B 段：
"做了积分基线校正后不要叠加 EFA 分解"（候选 `q4-ce06`，另有官方原话支撑）。
**重启条件**：抓取官方 `s2_svd` / `s2_efa` / `s2_regals` 三页后重开该单元。

---

## `multi-series-and-waxs-processing` — 多序列分析 / WAXS 合并

- **判决**: V1 跨域不通过（本包材料只有一句能力描述）
- **条数**: 0 条实抽候选

源 A 未提；源 B 的教程目录里有 `s2_multiseries`、`s1_waxs` 两节，本包未抓取。
时间分辨/多序列平均的逻辑与 SEC 相似但**区间选择的对象不同**（时间点 vs 洗脱峰），
照抄 SEC 的判据会误导。

**处置**：不成 skill 也不在现有 skill 中留边界句（与 SEC 主线无判据冲突）。
**重启条件**：抓到官方两节正文后单独成包。

---

## `raw-sec-ui-navigation` — Series / LC Analysis 面板巡览

- **判决**: V2 / V3 不通过（信息检索，非可外推方法论）
- **条数**: 6
- **候选 id**: `q5-g01`, `q5-g02`, `q5-g05`, `q5-g06`, `q1-f05`（界面部分）, `q2-11`（检查项清单本身）

"哪个按钮在哪、三档图各叫什么"查一次就会。有信息量的部分不是按钮位置，而是
**它们的语义**（Series=带帧号的对象、三档图对应三种物理量、calc markers 与下游 Guinier 的区别），
这部分已作为术语保留。

**处置**：降级为共享 reference——写入
`skills/process-sec-saxs-series/references/sec-saxs-series-workspace.md`
（含 Series 面板 / LC Analysis 面板 / 三档图 / 与 CHROMIXS 的口径差异 / `.hdf5` 与导出）。
被两个新 skill 引用。

---

## 降级为术语或流程分支（不构成 skill，也不属淘汰）

- `q5-g01–g12` 共 12 条术语（Series、色谱图、buffer/sample 区、滑窗、三档图、calc markers、
  baseline 两分支、CHROMIXS、UV 痕、平台区、`.hdf5`/report、峰前小峰）→ 写入
  `skills/process-sec-saxs-series/references/sec-saxs-series-workspace.md` 的术语节，
  由两个新 skill 交叉引用。
- `q1-f05` 手动替代路径 → **不是**独立 skill，作为 `process-sec-saxs-series` 的 E 段一条分支
  （并标明它失去什么：没有平台判据）。
- `q2-06`（浓度未知 ⇒ 不能用绝对校准/I0 标样）→ 写进 `process-sec-saxs-series` 的 B 段，
  并与 `assess-guinier-fit-quality` 的 MW 边界互相引用。
