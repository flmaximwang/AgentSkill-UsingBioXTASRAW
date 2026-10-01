# RAW 的落盘格式与相似性判据（.dat / .out / .ift / CSV + CorMap）

本文件是 `reduce-saxs-frames-to-curves` 的展开参考：还原产物存成什么格式、哪些能被读回、Excel 打开时的坑，以及"曲线相不相似"的统计判据与其边界。
证据来自 **B 级**官方文档：`40-tutorial.md · tutorial/s1_similarity.rst`、`tutorial/s4_external_data.rst`、`tutorial/s4_export_plots.rst`。绑定版本 **RAW v2.4.2**。
引用逐字取自英文原文，每条 ≤150 字，`[FILE: …]` 给出语料文件与 rst 节。

> **大原则**：**能否读回 RAW 决定该不该用它做交付**。`.dat` / `.ift` / `.hdf5` 是 RAW 认识的**保存**格式；各 plot 的 `Export Data as CSV` 是**单向出口**，导出后读不回 RAW。

---

## 1. `.dat` —— 曲线（profile）的交付格式

> "RAW saves profile data, including the q, I(q), and uncertainty data in .dat files."
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

> "These .dat files are standard text files with space separated values."
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

**段结构**：
- 头（和可能的尾）由**行首 `#`** 标出；数据是**三列**、空格分隔、科学计数法：`Q` / `I(Q)` / `Error`。
- 头里必有列标题行 `#      Q             I(Q)           Error` 与数据点数。
> "the numbers are in scientific format, e.g. 1.23E-04"
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]
- 大量附加信息（含分析结果）默认在**尾部**（也可在头部），其起点用 `### HEADER:` 标出：
> "the start of this information is distinguished by a \"### HEADER:\" line"
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]
- 把每行行首的 `#` 去掉后，这段附加信息即为 **json**：
> "if the leading \"#\" marks are removed from each line the extra data is in json format"
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

**互操作坑**：`.dat` 是多程序共用的扩展名，格式可能略有差异：
> "other programs, such as Primus, also produce .dat files which may have slightly different formats."
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

---

## 2. `.out` —— GNOM 的 IFT 输出，四段

> "RAW saves IFT data, including the P(r) function and fit to the data, produced by GNOM in .out files"
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

四段（`####  Configuration  ####` 这类节头分隔）：

| 段 | 内容 |
|---|---|
| **Configuration** | 生成 P(r) 用的输入参数 |
| **Results** | 正则化、perceptual criteria、实空间 Rg 与 I(0)、总估计结果 |
| **Experimental Data and Fit** | 5 列：`S`（外推到 q=0 的 q 向量）/ `J Exp` / `Error` / `J Reg` / `I Reg` |
| **Real Space Data** | P(r)，3 列：`R` / `P(R)` / `ERROR` |

---

## 3. `.ift` —— BIFT 输出，首行 `# BIFT`

> "RAW saves IFT data produced by BIFT in .ift files."
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

四段：**P(R)**（`R`/`P(R)`/`Error`）→ **实验数据与拟合**（`Q`/`I(Q)`/`Error`/`Fit`，4 列）→ **外推到 q=0 的拟合**（`Q_extrap`/`Fit_extrap`）→ **参数与派生值**（`### HEADER:` 后为 json）。
另注：BIFT 的 `.ift` **不兼容 DAMMIF/ATSAS**，但**兼容 DENSS**（见 `compute-and-validate-p-of-r`）。

---

## 4. 导出格式读不回 RAW

> "the export formats cannot be read back into RAW"
>
> [FILE: 40-tutorial.md · tutorial/s4_export_plots.rst]

- **可读回的保存格式**：曲线 `.dat`、IFT `.out`（GNOM）/ `.ift`（BIFT）、系列 `.hdf5`（或旧 `.sec`）。
- **不可读回的导出格式**：各 plot 右键 `Export Data as CSV`（Guinier / Dimensionless Kratky / Comparison / CRYSOL / IFT 各自导出；SVD / EFA / REGALS / Series 各有 Save）。

结论：**交付/归档一律走可读回的保存格式**；CSV 只用于外部绘图或分析，不要当成交付本体。

---

## 5. Excel / 外部程序导入的坑

- **`.dat`**：Import wizard → 选 `Delimited` → 勾 `Space`。导入后**列标题整体右移一列**，第一列 Q、第二列 I(q)、第三列 Error。
- **`.out`**：同样 `Delimited` + `Space`，但**部分 I Reg 值会落到错列**：
> "some of the I Reg values will be in the wrong column, due to how separators are handled"
>
> [FILE: 40-tutorial.md · tutorial/s4_external_data.rst]

  修正：滚到实验数据段，把第二列从顶端到"下一批三列开始前"的数据剪下、粘到第五列顶端——修正后五列依次是 `S` / `J Exp` / `Error` / `J Reg` / `I Reg`（列标题仍不在正确列）。
- **`.ift`**：列标题同样会右移一列（P(r) 段：`R` / `P(R)` / `Error`）。
- **`.csv`**：行首 `#` 为头信息；导入时勾 `Comma`。

---

## 6. 相似性：三视图与 CorMap 的边界

RAW 的比较窗口同时给三种视角（选中曲线 → 右击 → `Compare Profiles`）：

> "compare residuals, between profiles, ratios between profiles, and use statistical tests (currently only the Correlation Map test is implemented)"
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

### 6.1 残差（Residuals）
两条曲线之差，可按其中一条的不确定度归一化：
> "If normalized, you expect most of the residual values to be within +/- 2.5"
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

**归一化残差多数落在 ±2.5 内 = 两者在噪声水平内一致**（残差平坦、随机分布）。出现系统性走向（如高 q 偏高、中 q 偏低）= "大体上是好拟合，但不是完美拟合"。

### 6.2 比率（Ratios）
曲线之比；强度不同量级时先用 `Scale → "Scale, high q"` 按高 q 对齐。比值**恒为 1 = 同形**；低 q **系统性下凹 = 存在粒子间排斥**（浓度依赖效应）。

### 6.3 统计检验（Similarity Test / CorMap）
成对比较的概率**热图** + 概率**列表**；可设 `highlight with p-value <` 阈值、可开关**多次检验校正**。被比较的 `X`/`Y` 是 File #，`Prob.` 是"两者相同"的概率，`Test val` 是 CorMap 的 longest edge；热图对称、对角线恒为 1。

### 6.4 它驱动"平均只取相似帧"
平均时若弹 `not all the files are statistically the same` 警告，可点 `Average Only Similar Files`——**自动只平均与第一个文件统计相同的那些帧**：
> "This averages only those profiles found to the same as the first file, for the given statistical test."
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

### 6.5 判据：统计判定只与检验和阈值一样好；自动剔除更保守，必须目视 + Similarity Test 复核
> "This is only as good as the statistical test being used, and the cutoff threshold selected."
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

官方 damage_data 例：自动法剔 **8–10** 号帧（仅 3 帧），而按"辐射损伤随剂量增加"本应剔 **6–10**（5 帧）——自动法剔得**更少**（更保守）：
> "we should discard profiles 6-10, not just 8-10 as in the automated version."
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

所以：
> "it is generally good to double check your set of profiles both visually and using the Similarity Test panel"
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

**多次检验校正**：跑的成对检验越多，越该校正"期望之外的离群"：
> "a multiple testing correction attempts to correct for that factor."
>
> [FILE: 40-tutorial.md · tutorial/s1_similarity.rst]

---

## 7. 与 WAXS 合并的关系

WAXS/SAXS 合并出的 `M_` 曲线同样是 profile，同样按 `.dat` 交付；合并前两侧各自必须是"**各自 cfg 下已还原好的曲线**"（见主文档"WAXS 合并"段）。该段读者最常踩的坑是**处理 SAXS 时把含 PIL3 的 WAXS 帧一起载入**——两套帧的几何/cfg 不同，混载会让 SAXS 结果整段作废。
