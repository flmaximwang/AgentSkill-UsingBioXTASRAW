# 重建评估判据：清单、例外、对照实验设计（reference）

源：BioXTAS RAW 官方文档 v2.4.2 —— 方法学 *Bead model reconstructions*（`30-saxs.md · saxs/saxs_bead_models.rst`）与教程 *DAMMIF/N and DAMAVER* / *DENSS* / *AMBIMETER* / *Aligning reconstructions*（`40-tutorial.md`）。所有阈值逐字取自源，不做外推。
供 `evaluate-a-shape-reconstruction` 引用；上游 P(r) 的产出与判据见 `compute-and-validate-p-of-r`。

> 版本：本文的 ATSAS 行为按教程所用的 **ATSAS 3.1.1** 描述；版本差异单列在 §5。

---

## 一、七条判据的完整清单（源A 逐字 → 操作形式）

| # | 判据（原文） | 阈值 | 读数位置 | 不通过的第一动作 |
|---|---|---|---|---|
| 1 | Ambiguity score | **< 2.5（最好 < 1.5）** | AMBIMETER 窗口 / 结果页顶部 | > 2.5：如实说明形状很可能不唯一，别硬报 |
| 2 | NSD（平均） | **< 1.0**；< 0.6 好 / 0.6–1.0 fair / > 1.0 poor | DAMAVER 输出 / 结果页 NSD 行 | > 1.0：谨慎或不用；先查单分散性与 P(r) |
| 3 | Few (0-2) models rejected | **0–2 个** | 结果 summary tab（被剔模型红色） | 剔 > ~2/15：视为不稳定信号 |
| 4 | Only one cluster | **1 个簇** | DAMCLUST 输出 / 结果页簇信息 | 多簇：先排除 §2 的误报例外，否则视为歧义 |
| 5 | Model χ² near 1.0 for all models | **≈ 1.0** | 逐模型 summary tab / 每模型页 | 1.5–2 或更大：用归一化残差形态分诊（§3） |
| 6 | Model Rg and Dmax close to values from P(r) | **Rg ~5%、Dmax ~10%**（高质量数据经验值） | summary tab 的 Rg/Dmax vs P(r) | 复查 P(r)（→ 上游 skill），再重做重建 |
| 7 | M.W. from model volume close to expected | **差 < 20–25%** | summary tab 的 MW（= volume / 1.66） | 差 > 20–25%：视为可疑 |

**判据 6 的注意点（源A 原文）**：没有硬性规定要多接近——~5%（Rg）/ ~10%（Dmax）是"高质量数据下的经验值"；持续不符就是"这个重建不是溶液中的好代表，不该信"，而不是"再调参数压过去"。

**判据 7 的注意点**：常数 **1.66** 是 RAW 用的经验值，其它程序可能不同；该常数随形状在 **~1.5–2.0** 间变化，所以这个 MW 比其它 SAXS MW 方法更不确定，**只宜用于"总体尺寸大致相符"的判断**。

**七条全部通过才是通过**——源A 用的是"criteria for a good reconstruction"这个整体表达；没有给"几条通过就够"的加权规则（材料盲点，见 §6）。

---

## 二、例外与反直觉条目

### 2.1 DAMCLUST 的误报例外（判据 4 的唯一例外）

触发条件（三者同时）：**a-score（AMBIMETER）< 0.5**、**平均 NSD < 0.5**、**NSD 标准差 ~0.01**。
现象：**DAMCLUST 会报出多个簇，常 > 5 个**。
官方解释：此时其实不存在多个簇，是模型间偏差极小把 DAMCLUST 算法骗了。
处置：**不因此判该重建歧义**；记录这一例外的触发条件即可。

### 2.2 簇 ≠ 溶液里的不同形状（判据 4 的语义约束）

即使溶液里真有有限个不同形状（例如某蛋白的开/闭态），也不可用簇来代表：每条重建拟合的都是**各组分散射的平均曲线**，单个重建无法只拟合其中一个组分。所以簇只是"歧义度"的一个指标，不是"组分识别"工具。

### 2.3 χ² 的两个病因（判据 5 的分诊）

χ² 显著大于 1（1.5–2 或更大）= ① 拟合差 **或** ② 数据不确定度被低估。
分诊判据：看**归一化残差**——
- 平坦、随机分布于零附近 → **不确定度被低估**（拟合本身没问题）；
- 有系统性偏离 → **拟合质量差**。

补充（源A）：实践中归一化残差常出现小的系统性偏离，这一点不必过度担心；官方给的判据是"显著"的偏离。

### 2.4 多电子密度体系（判据体系本身的适用边界）

珠模型（DAMMIF/N）通常只有 2 个（分子/溶剂）、最多 3 个 bead 密度，**无法**重建蛋白-核酸复合物或带去垢剂/脂晕的膜蛋白 → 走 DENSS 电子密度分支（DENSS 能处理多电子密度）。

### 2.5 "数据好"不是通过条件

原文以粗体给出的结论：**高质量 SAXS 数据不保证好的珠模型重建**，因此无论数据质量如何都要逐条评估每一个重建。理由：多条不同形状能产生同一条（在实验噪声内不可区分的）曲线；若样品柔性或有多个构象/寡聚态，重建直接变得困难或不可能。

---

## 三、对照实验设计（把"约束有没有过度"变成可检验的）

官方在 Mode / Symmetry / Anisometry 三处给了对照思想，可整理成三条可执行对照：

| 对照 | 变量 | 保持不变的 | 判读 |
|---|---|---|---|
| **模式对照** | Fast vs Slow | 其余参数 | Slow 细节更多；**终稿用 Slow**；Fast 只用于"快速看形状"（如束线现场，3 个即可） |
| **对称性对照** | 指定对称性 vs P1 | 同一 P(r)、同模式 | 若指定组明显"更好看"而 P1 组散乱 → 先怀疑对称性把形状写死了 |
| **各向异性对照** | 指定 anisometry vs 无 anisometry | 同上 | 同上 |

**记录要求**：把"跑了几组、每组几个模型、什么模式、约束是什么、a-score/NSD/剔除数/簇数/χ²/Rg/Dmax/MW"写进同一张表——判据是**跨组比较**时才显出意义的，单组数字无法回答"约束有没有过度"。

**重建数量是硬前提，不是省时项**：

- 珠模型：**10–20 个，推荐 15**；对照实验意味着这个数要按"组"给（约束组 15 + 对照组 15）。
- DENSS：**≥ 20 个**。
- < ~3 个模型时 DAMAVER/SASRES 的统计量不成立（SASRES 分辨率信息需要 DAMAVER 跑在 **≥3 个重建**上，且 ATSAS ≥ 2.8.0）。

---

## 四、DENSS 分支与对齐分支的差异表

| 项 | 珠模型（DAMMIF/N + DAMAVER） | DENSS 电子密度 |
|---|---|---|
| 输入 | GNOM 的 `.out`，**已截断**到 `8/Rg` 或 0.25–0.30 1/Å（取小者） | **全 q**：`.ift` 或 `_full.out`，**不截断** |
| 重构数 | 10–20（推荐 15） | **≥ 20** |
| 平均/聚类 | DAMAVER（平均 + NSD + 剔除）→ DAMCLUST（簇） | `denss_average`（含 enantiomer filtering）与 `denss_align`；RAW 里表现为 densities 的 align & average |
| 分辨率 | SASRES（ATSAS ≥ 2.8.0 且 ≥3 个重建） | **FSC（Fourier shell correlation）相关首次跨过 0.5 的 Å** |
| 逐模型复核 | χ²、Rg、Dmax、excluded volume、MW | χ²、Rg、support volume、RSC；并确认三者随精修步已 plateau |
| 输出文件 | `<prefix>_xx-1.cif`、`damfilt`/`damaver` cif、`refine_<prefix>` | `<prefix>_xx.mrc`、`<prefix>_aver.mrc`、`<prefix>_refine.mrc` |
| 对齐输出去向 | CIFSUP：`<target_name>_aligned.pdb/cif` | DENSS align：`<target_name>_aligned.mrc` + `<reference_name>_centered.pdb` |

**对齐的语义（两个窗口一致）**：`Reference` = 被对齐到的模型（不动）；`Target` = 被移动去对齐的模型。DENSS 对齐默认**把 Reference 居中**并写出 `<reference_name>_centered.pdb`，**要比较的是它**（或关掉 Advanced Settings 里的 "Center reference"）。

---

## 五、版本与依赖

| 组件 | 要求 / 差异 |
|---|---|
| DAMMIF / DAMMIN / DAMAVER / DAMCLUST / SASRES / AMBIMETER | 全部来自 **ATSAS**；教程用 **ATSAS 3.1.1**，更旧版本部分行为不同 |
| DAMCLUST 信息量 | ATSAS **≤ 3.1.0** 给的簇信息更多；**≥ 3.1.1** 时结果页部分字段会空 |
| DAMMIN 的 Dmax | ATSAS **≥ 3.1.0** 不再为模型提供 Dmax |
| SASRES | 需 **ATSAS ≥ 2.8.0** 且 DAMAVER 跑在 **≥3 个重建**上 |
| **CIFSUP** | **只在 ATSAS ≥ 3.1.0 提供**；更旧版本用功能相近的 **SUPCOMB** 窗口（`Tools → ATSAS → Align (SUPCOMB/CIFSUP)`） |
| DENSS | RAW 已完整内建；教程 ATSAS ≥ 2.7.1 亦需 |

**引用要求**：跑 DAMMIF/DAMMIN/DAMAVER/SASRES/CIFSUP 时分别引用各自手册给出的文献；用 DENSS（含 DENSS 对齐）时引用 **T. D. Grant. *Nature Methods* (2018) 15, 191–193**（DOI 10.1038/nmeth.4581）。

---

## 六、材料盲点（不要在回答里补造的部分）

- **判据冲突时谁优先**：官方只给清单，没给优先级或加权。处置：逐条给通过/不通过，不通过就说不通过；需要"因为 A 所以忽略 B"时必须说明这是操作者的判断，不是文档规定。
- **阈值的不确定度**：判据 6 的 5% / 10% 明确写作"经验值"，不是硬阈值。
- **"最 probable 模型"之外的展示选择**：文档只说 DAMAVER 的两个平均模型（`damaver.pdb`/`damfilt.pdb`）不拟合数据、一般不该用于展示；它没有规定论文该展示哪个模型。
- **快速试做阈值**：给不出"什么情况下 3 个 Fast 模型就够交付"的判据（官方只把它限定在"束线现场快速看形状"）。
