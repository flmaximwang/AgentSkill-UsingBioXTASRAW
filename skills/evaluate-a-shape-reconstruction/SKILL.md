---
name: evaluate-a-shape-reconstruction
description: "DAMMIF/DENSS 形状重建做完后评估能不能用：a-score/平均 NSD/被剔模型数/聚类数/各模型 χ²/模型 Rg·Dmax 对 P(r)/体积估 MW——七条判据逐条过，含 Fast↔Slow、对称↔各向异性对照、DENSS 的 FSC 分辨率与 CIFSUP/DENSS 对齐分支。用于「重建结果能不能用」「DAMCLUST 说有 2 个簇」「平均 NSD 0.8 算好吗」「a-score 2.8」「重建该跑几个模型」「DENSS 分辨率取多少」；不负责 P(r)/Dmax 本身（转 compute-and-validate-p-of-r），不负责把高分辨模型拟合到数据（转 fit-a-high-resolution-model-to-data）。"
source_book: BioXTAS RAW 官方文档 *Bead model reconstructions* / *3D reconstruction with bead models – DAMMIF/N and DAMAVER* / *3D reconstruction with electron density – DENSS* / *AMBIMETER* / *Aligning reconstructions with high resolution shapes*（v2.4.2）；ATSAS ≥3.1.1（DAMAVER/DAMCLUST/SASRES）、CIFSUP 需 ATSAS ≥3.1.0
source_chapter: 源A 30-saxs.md · saxs/saxs_bead_models.rst；源B 40-tutorial.md · s2_dammif / s2_denss / s2_ambimeter / s2_align
tags: [saxs, bioxtas-raw, reconstruction, bead-model, dammif, denss, ambimeter, evaluation]
related_skills:
  - slug: compute-and-validate-p-of-r
    relation: depends-on
  - slug: assess-guinier-fit-quality
    relation: depends-on
  - slug: fit-a-high-resolution-model-to-data
    relation: composes-with
---

# 重建的输出不是一个形状，而是一份带评估指标的模型集

单条散射曲线**不能唯一确定** 3D 形状——这不是数据不够好，是 SAXS 的物理信息上限。所以重建不是一个动作，而是一个**闭环**：造一批互不相同的模型 → 平均成共识 → 用一组判据判定这份重建能不能用。把"最好看的那张图"当结果，是这个流程里最常见也最贵的错误。

## R — 原文 (Reading)

> Because the shape reconstruction is not unique, a number of distinct reconstructions are generated
>
> … a Monte Carlo like approach is taken where a number (usually 10-20) of models are generated, and then averaged to give a consensus reconstruction.
>
> 出处：源B s2_dammif [FILE: 40-tutorial.md · tutorial/s2_dammif.rst]；源A saxs_bead_models [FILE: 30-saxs.md · saxs/saxs_bead_models.rst]

> we create 10-20 bead model reconstructions and then average them. I recommend 15 reconstructions.
>
> 出处：源A saxs_bead_models [FILE: 30-saxs.md · saxs/saxs_bead_models.rst]

> "Criteria for a good DAMMIF/N reconstruction"：
> Ambiguity score < 2.5 (preferably < 1.5)
> … NSD < 1.0
> … Few (0-2) models rejected from the average
> … Only one cluster of models
> … Model Rg and Dmax close to values from P(r) function for all models
> … M.W. estimated from model volume close to expected M.W.
>
> 出处：源A 同上

> high quality SAXS data is not a guarantee of a good bead model reconstruction
>
> 出处：源A 同上（原文以粗体强调）

> NSD < 0.6 - Good stability of reconstructions
> … NSD between 0.6 and 1.0 - Fair stability of reconstructions
> … NSD > 1.0 - Poor stability of reconstructions
>
> 出处：源A 同上

> If the average NSD of a given model is more than two standard deviations above the overall average NSD, that model is not included in the average.
> … If more than ~2 models are rejected (out of 15), that may be a sign of an unstable reconstruction.
>
> 出处：源A 同上

> (ambiguity score from AMBIMETER < 0.5) and yields a set of reconstructions with a very small average NSD (<0.5, typically)
> … NSD standard deviation (~0.01), I have seen several (often >5) clusters identified with DAMCLUST.
>
> 出处：源A 同上

> A \chi^2 value significantly larger than 1 (1.5-2 or larger) indicates either a poor fit to the data or that the uncertainty ... is underestimated
>
> 出处：源A 同上

> for high quality data Rg agrees to better than ~5% and Dmax to ~10%
>
> 出处：源A 同上

> M.W. is calculated by dividing the volume (nominally representing the sample's excluded volume) by an empirically determined constant [4] of 1.66
> … If the M.W. is different from the expected M.W. by more than 20-25% you should consider the reconstructions to be suspect.
>
> 出处：源A 同上

> I rarely see estimated model resolutions less than ~20 Angstroms, often they are much larger.
> … bead models tend to be less reliable for high aspect ratio objects, such as long rods or thin discs
> … objects with voids (such as a spherical shell), and rings
>
> 出处：源A 同上

> as little as 0.7% aggregate caused a significant change in the bead model.
>
> 出处：源A 同上

> For DENSS you want to use the full q range of the data.
> … It is generally recommended that you do at least 20 reconstructions.
>
> 出处：源B s2_denss [FILE: 40-tutorial.md · tutorial/s2_denss.rst]

> The reconstruction resolution is taken as the resolution in angstroms where the correlation first crosses 0.5.
>
> 出处：源B 同上

> Note that CIFSUP is only available in ATSAS >=3.1.0. For older versions of ATSAS a similar SUPCOMB window is available
>
> 出处：源B s2_align [FILE: 40-tutorial.md · tutorial/s2_align.rst]

> the different clusters should not be taken as representatives of different distinct shapes in solution
>
> 出处：源A saxs_bead_models [FILE: 30-saxs.md · saxs/saxs_bead_models.rst]

## I — 骨架 (Interpretation)

**为什么是闭环而不是一步：** 每个重建程序（DAMMIF/DAMMIN）都是一次随机退火——它被物理约束（连通性、不许过度延伸、按 Rg/Dmax 限制尺寸）拽着去拟合同一条 I(q)，而多条不同的形状都能拟合同一条曲线。所以"跑一次"得到的是**一个**解，不是**唯一**解。整个方法学就是为这个事实设计的：跑一批 → 用 DAMAVER 平均出共识 → 用 AMBIMETER/DAMCLUST/SASRES/χ²/模型参数去量化"这批解散不散"。

闭环分三段，后两段的产物才是可交付物：

1. **生成**：从 GNOM 的 `.out`（已按 `8/Rg` 或 0.25–0.30 1/Å 截断）出发，做 **10–20 个**重建，**推荐 15 个**（Fast 快而粗、Slow 细，论文终稿用 Slow）。
2. **平均 + 聚类**：DAMAVER 平均成共识（`damaver.pdb` / `damfilt.pdb`），给出平均 NSD、每个模型的平均 NSD、以及哪些模型被剔除；DAMCLUST 给出簇数。
3. **评估**：把七条判据逐条过，再决定这个形状配不配被称为"溶液中的形状"。

七条判据（源A 逐字清单，这里翻译成"看到什么、怎么处置"）：

| # | 判据 | 通过线 | 不通过意味着什么 / 怎么处置 |
|---|---|---|---|
| 1 | AMBIMETER 歧义度 a-score | **< 2.5，最好 < 1.5** | 1.5–2.5 需谨慎（或做簇分析）；> 2.5 基本注定歧义——重建前就该考虑不做 |
| 2 | 平均 NSD | **< 1.0**（< 0.6 好；0.6–1.0 fair） | > 1.0 = 重建不稳定，谨慎或干脆不用 |
| 3 | 被 DAMAVER 剔除的模型数 | **0–2 个** | 15 个里剔 > ~2 个 → 重建不稳定的信号 |
| 4 | 聚类数 | **只有 1 个簇** | 多簇 = 多个形状都能配上同一条曲线（例外见下） |
| 5 | 各模型 χ² | **≈ 1.0** | 显著大于 1（1.5–2 或更大）= 拟合差 **或** 数据不确定度被低估；靠归一化残差形态区分这两者 |
| 6 | 模型 Rg / Dmax 对上 P(r) | **Rg ~5%、Dmax ~10%**（高质量数据经验值） | 先复查 P(r)，再重做重建；仍不符 = 这个重建不代表溶液中的样子 |
| 7 | 模型体积估的 MW 对上预期 | **差 < 20–25%** | MW = volume / **1.66**（该常数随形状在 ~1.5–2.0 间变）→ 差 > 20–25% 即视为可疑 |

**三条最容易读错的判据：**

- **χ² 大不等于拟合坏。** 它有两个病因：真拟合差，或数据不确定度被低估。分诊靠归一化残差——**平坦随机分布 → 是不确定度被低估**；**有系统性偏离 → 才是拟合质量差**。
- **多簇不一定代表溶液里有多个形状。** 反向例外：数据极好时（a-score < 0.5、平均 NSD < 0.5、NSD 标准差 ~0.01），DAMCLUST 会误报多个簇（常 > 5 个）——模型间差异太小，算法被"骗"了。而且即便溶液里真有多个构象，每条曲线拟合的都是**各组分散射的平均**，单个重建无法只拟合其中一个组分，**所以簇不能当溶液里不同形状的代表**。
- **"数据好"不是通过条件。** 文档把这句话写成了结论：高质量数据**不保证**好重建。判据必须逐条过，不能替代成"我的数据很好所以没问题"。

**五条重建固有的局限（不是操作失误造成的）：**

- 分辨率低：**很少优于 ~20 Å**，常常大得多；模型表面的细小起伏无意义。
- 形状偏置：高长径比（长棒/薄盘）、有空隙（球壳）、环状物体都不可靠；**最可靠的是近球状**。
- 对痕量聚集极敏感：**0.7% 的聚集**就足以显著改变珠模型（非特异聚集的典型表现是主模型上伸出一个突起）。
- 不建模水化层与内部结构，所以珠模型输入要截断高 q（对照：DENSS 要用**全 q**，不截断）。
- 多电子密度体系（蛋白-核酸复合物、带去垢剂晕的膜蛋白）珠模型做不了 → 走 DENSS 电子密度分支。

**两条可选出口（本 skill 覆盖到"该怎么用、判据是什么"，不展开成独立流程）：**

- **DENSS 电子密度分支**：用**全 q**（`.ift` 或 `_full.out`，不要用给 DAMMIF 截断过的 `.out`）；重构数 **≥ 20**；分辨率读 **FSC 首次降到 0.5 所对应的 Å**；检查各模型 χ²/Rg/support volume 是否收敛；平均与对齐由 `denss_average` / `denss_align`（RAW 里的 electron density averaging / alignment）完成。
- **对齐分支**：把重建与高分辨结构（PDB/mmCIF）叠加。**CIFSUP 需 ATSAS ≥ 3.1.0**；更旧的 ATSAS 只有功能相近的 SUPCOMB 窗口。DENSS 侧用 DENSS 自带的 electron density alignment（`.mrc` ↔ PDB）。

一句话判据：**"我凭什么说这个形状是唯一的？"——答不上来，就把它交成"一个可能的解 + 它的一组评估指标"。**

## A1 — 案例 (Past Application)

**1. `gi_complete`：官方自己只用 5 次重建，但结论写的是 15–20**（源B s2_dammif；源A saxs_bead_models）

- 问题：DAMMIF/N 每次结果都不一样，跑几次才算数、用哪个模式。
- 做法：载 `glucose_isomerase.out`（已截断到 8/Rg）→ IFT 列表右键 → Bead Model (DAMMIF/N) → 建输出目录 `gi_dammif` → 把重构数改成 5、取消 "Refine average with dammin" → 勾 "Align output to PDB/mmCIF" 选 `1XIB_4mer.pdb` → Start。
- 结果：结果页顶部给 AMBIMETER、DAMAVER 的 NSD（均值+标准差）与"多少条进了平均"、≥3 条且 ATSAS ≥2.8.0 时给 SASRES 分辨率；底部逐模型的 χ²、Rg、Dmax、excluded volume、体积估 MW。
- 结论：**5 是演示值**——文档两处都写 "generally recommended that you do 15-20 reconstructions" / "I recommend 15 reconstructions"，论文终稿还要 Slow 模式。这条差距本身就是判据：**别把教程的省时设置当成出结果的设置**。

**2. AMBIMETER：先花几秒判断"值不值得重建"**（源B s2_ambimeter）

- 做法：载 `glucose_isomerase.out` → IFT 列表右键 → AMBIMETER。
- 结果：窗口给出与曲线相容的形状类别数、歧义度 a-score（类别数的 log₁₀）、以及官方对"能否得到唯一 3D 重建"的解释（< 1.5 基本唯一；1.5–2.5 需谨慎、可做簇分析；> 2.5 无限制的唯一重建极不可能）。
- 结论：a-score 是**重建前**的筛子。若它已经 > 2.5，后面七条判据再漂亮也救不回来。

**3. DENSS：教程同样跑 5 次，官方建议 ≥ 20**（源B s2_denss）

- 做法：载 `glucose_isomerase.ift`（**全 q**；不要用截断过的 `.out`）→ IFT 列表右键 → Electron Density (DENSS) → 建 `gi_denss` → 改成 5 次、Fast 模式 → 勾 "Align output to PDB/MRC" 选 `1XIB_4mer.pdb` → Start。
- 结果：结果页顶部给基于 **Fourier shell correlation** 的分辨率估计；models 汇总给 χ²、Rg、support volume、RSC；有平均时在 average 页看 **FSC vs 分辨率，分辨率取相关首次跨过 0.5 的 Å 数**。
- 结论：电子密度分支的复核动作与珠模型不同——看的是 **Rg 是否接近预期、χ² 与 support volume 在模型间是否相对一致、残差是否小、三条是否都已收敛**。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- DAMMIF/N 或 DENSS 已经跑完，面对一屏数字，想知道"这个重建能不能写进文章/能不能信"。
- 平均 NSD 落在 0.6–1.0、或 a-score 落在 1.5–2.5，卡在"谨慎"地带求一个明确答案。
- DAMCLUST 报了 2 个（或更多）簇，不知道是"溶液里真有两种形状"还是算法问题。
- 15 个重建被剔了 4 个，想问是不是白跑了。
- 模型 χ² 是 2.3，想判断是拟合坏还是误差被低估。
- 模型算出的 MW 与预期差了 30%，想知道还能不能用。
- DENSS 跑完不知道该报多少 Å 的分辨率、该跑多少次。
- 想把自己手上的晶体/CryoEM/AlphaFold 结构与重建叠起来看（对齐分支）。

**语言信号**

- 「DAMMIF 跑完了，怎么判断这个形状能不能用」
- 「平均 NSD 0.8 算好吗」「a-score 2.8 还能做重建吗」
- 「DAMCLUST 说有两个 cluster，是不是说明有两个构象」
- 「15 个模型剔了 4 个正常吗」
- 「模型 χ² 是 2 左右，是哪里出问题了」
- 「重建该跑几个模型」「DENSS 的分辨率是怎么读出来的」

**与相邻 skill 的区别**

- 与 `compute-and-validate-p-of-r`：那边负责产出**一个可信的 P(r)**（三法分工、Dmax 定法、判据、截断规则）；本 skill 的输入就是那个 `.out`/`.ift`。**判据 6（模型 Rg/Dmax 对上 P(r)）不通过时，第一动作是回那边复查 P(r)，不是调重建参数。**
- 与 `assess-guinier-fit-quality`：那边判低 q 的 Guinier 拟合是否成立、是否聚集/排斥。**聚集会同时毁掉 Guinier 和珠模型**（0.7% 即显著），所以本流程要先有可用的 Guinier 结论。
- 与 `fit-a-high-resolution-model-to-data`：那边回答"高分辨结构配不配得上这条曲线"（CRYSOL/PDB2SAS 直接拟合）。文档给的方向是**证伪优先**：要比较高分辨结构与 SAXS，直接用计算曲线去拟合数据，比把结构 dock 进珠模型更有判别力；**若 CRYSOL/PDB2SAS 拟合很好而珠模型不吻合，错的是珠模型**。本 skill 只负责"对齐"这个可视化步骤。
- 与去卷积/时间分辨类 skill：那些处理"一条 series 里有几个组分"；本 skill 处理"一个组分的一个形状能不能确定"。

## E — 执行步骤 (Execution)

1. **确认输入 P(r) 是可用的。** 珠模型链要求输入是 GNOM 生成的 `.out`，且已按 `8/Rg` 或 0.25–0.30 1/Å **截断**（取小者）——因为 DAMMIF 不建模水化层与内部结构，高 q 只会带进误差。DENSS 分支相反：**用全 q，不要截断**。
   完成标准：能说出手上这个文件是"给珠模型的截断版"还是"给 DENSS 的全 q 版"（`.out` vs `.ift`/`_full.out`）。判停点：只有一个截断过的 `.out` 却要跑 DENSS → 回 `compute-and-validate-p-of-r` 重新产出全 q 的 P(r)。
2. **重建前先跑 AMBIMETER。** 对同一个 `.out` 跑 AMBIMETER，读 a-score。
   完成标准：能说出 a-score 落在哪一档（< 1.5 / 1.5–2.5 / > 2.5）。判停点：> 2.5 → 如实告知"这个体系的形状重建很可能不唯一"，**别硬跑出一堆看起来漂亮的结果**。
3. **生成模型集。** 珠模型：DAMMIF/N，**10–20 个，推荐 15**；Fast 试水、**Slow 出终稿**。DENSS：**≥ 20 个**，终稿 Slow。
   完成标准：能报出"跑了几个、什么模式、用的哪份输入"。判停点：只跑了 3–5 个（教程演示值）→ 不足以做统计判定，重跑。
4. **跑对照实验，而不是只跑一组。** 已知对称性/各向异性时可以指定，但**始终建议再做一组 P1 / 无 anisometry 的重建**，用来验证约束没有过度收紧形状。
   完成标准：能说出"约束组 vs 无约束组的结果差多少"。判停点：约束组明显更"好看"而对照组散乱 → 先怀疑约束把答案写死了。
5. **平均 + 聚类。** DAMAVER 平均出共识（`damaver.pdb` / `damfilt.pdb`），同时读：平均 NSD、NSD 标准差、每模型平均 NSD、被剔除名单（结果表里被剔的模型显示红色）；DAMCLUST 读簇数。
   完成标准：能把"剔了几个、几个簇、平均 NSD 与标准差"写成一行。注意 DAMAVER 的两个平均模型**都不真正拟合数据**，一般不该拿来展示；不打算做 DAMMIN 精修时，用被高亮的"most probable"模型作为最终结果。
6. **逐模型过判据 5–7。** 对汇总表逐行看：χ² 是否 ≈ 1（显著 > 1 时用归一化残差形态分诊：平坦随机 = 不确定度低估；系统性偏离 = 拟合差）；Rg/Dmax 是否落在 P(r) 的 ~5% / ~10% 内；volume/1.66 估的 MW 是否在预期的 20–25% 内。
   完成标准：**七条判据逐条给出通过/不通过**，不是一句"看起来还行"。判停点：判据 6 不通过 → 回 `compute-and-validate-p-of-r` 复查 P(r) 与 Dmax，再重做重建；仍不符 → 如实说这个重建不可信。
7. **（DENSS 分支）读分辨率。** 有平均时看 average 页的 FSC 曲线，**分辨率 = 相关首次跨过 0.5 的 Å 数**；同时确认各模型的 χ²、Rg、support volume 在最终步都已收敛（plateau）、模型数据与原数据的残差小。
   完成标准：能报出分辨率值及其读法。判停点：Rg 与预期差很多、support volume 在模型间跳 → 先处理，不报分辨率。
8. **（对齐分支）叠到高分辨结构上。** ATSAS **≥ 3.1.0** → `Tools → ATSAS → Align (SUPCOMB/CIFSUP)`，Reference = 高分辨结构、Target = 重建模型，跑完在同目录得 `<target_name>_aligned.pdb`；ATSAS 更旧 → 用功能相近的 SUPCOMB 窗口。DENSS 侧 → `Tools → Electron Density (DENSS) Alignment`，默认会把 Reference 居中并写出 `<reference_name>_centered.pdb`，**要拿它与对齐后的文件比**。
   完成标准：能说清"Reference 是被对齐到的、Target 被移动"，以及拿哪两个文件相比。判停点：对齐结果不符 → 先回到 `fit-a-high-resolution-model-to-data` 用计算曲线拟合数据来判优劣，**不要靠叠图脑补**。
9. **交付：模型集 + 评估表。** 留存 `<prefix>_dammif_results.csv` / `<prefix>_denss_results.csv`（结果页自动落盘）与自动生成的多页 pdf，或把 csv 加进 `Save report` 的 pdf 报告。
   完成标准：别人能凭这些文件复现"哪几条判据通过、结论是什么"，而不是只拿到一个 `.pdb`。

## B — 边界 (Boundary)

**不要用的场景**

- 还没跑 AMBIMETER、也不打算做簇分析就直接报一个形状 → a-score > 2.5 时这个报法没有依据。
- 输入是截断过的 `.out` 却要跑 DENSS → 回 `compute-and-validate-p-of-r` 取全 q。
- 想问"高分辨结构配不配得上这条曲线" → 走 `fit-a-high-resolution-model-to-data`（CRYSOL/PDB2SAS 直接拟合）；本 skill 只覆盖对齐这个可视化步骤。
- 多电子密度体系（蛋白-核酸复合物、带去脂/去垢剂晕的膜蛋白）用珠模型 → 珠模型只有两三个 bead 密度，做不了；走 DENSS 分支。
- 体系本身是柔性/多构象 → 珠模型天然不适用；应考虑系综类方法（EOM/SASSIE/BilboMD 等），超出本 skill。
- P(r) 本身就不可信时 → 先解决 P(r)，本 skill 的所有判据都建在它之上。

**源里明确警告过的失败模式**

- **把"最好看的模型"当结果**（源A/源B）：DAMAVER 的两个平均模型都不拟合数据；不精修时该用的是 most probable 模型；展示与判定是两件事。
- **以为数据好就不必逐条评估**（源A）：`high quality SAXS data is not a guarantee of a good bead model reconstruction`。
- **把多簇解读为溶液里的多个形状**（源A）：簇不能代表不同形状；且极低歧义/极小 NSD 时 DAMCLUST 会误报（常 > 5 个簇）。
- **忽略痕量聚集**（源A）：0.7% 的聚集即可显著改变珠模型，表现为主模型上的伸展突起 → 重建前先把样品单分散性搞清楚（SEC-SAXS/离心）。
- **对高长径比/中空/环状物体报形状**（源A）：这些恰恰是珠模型最不可靠的类别。
- **用 χ² 单点判死**（源A）：χ² 1.5–2 或更大有两个可能的病因，必须看归一化残差的形态才能分诊。
- **把教程的 5 次重建 / Fast 模式当出结果的配置**（源B）：官方两处都写 15–20（珠模型）/ ≥ 20（DENSS）、论文终稿用 Slow。

**版本与依赖**

- DAMMIF/N、DAMAVER、DAMCLUST、SASRES、AMBIMETER 都来自 **ATSAS**；文档教程使用 **ATSAS 3.1.1**，更旧版本部分字段/行为不同（例如 DAMCLUST 在 ATSAS ≤ 3.1.0 给的簇信息更多，ATSAS ≥ 3.1.1 时有些字段会空；DAMMIN 在 ATSAS ≥ 3.1.0 不再给模型的 Dmax）。
- **CIFSUP 只在 ATSAS ≥ 3.1.0 提供**；更旧版本改用功能相近的 SUPCOMB 窗口。
- SASRES 分辨率信息只有在 **DAMAVER 跑在 ≥ 3 个重建上且 ATSAS ≥ 2.8.0** 时才出现。

**材料盲点**

- 官方给的是七条判据与分档，但**没有给"多条判据冲突时谁优先"的规则**——本 skill 因此把冲突情形写成"逐条给通过/不通过 + 不通过就说不通过"，不编造加权方案。
- **教程数字（5 次、Fast）与建议数字（15–20 次、Slow）并存**是文档自己的张力，本 skill 一律以"建议值"为出结果的配置，并注明教程值是演示用。
- 引用要求：用 RAW 跑 DAMMIF/DAMMIN/DAMAVER/SASRES/CIFSUP 时，除 RAW 论文外还需引用各自手册给出的文献；用 DENSS（含 DENSS 对齐）时需引用 T. D. Grant. *Nature Methods* (2018) 15, 191–193（DOI 10.1038/nmeth.4581）。

**参考文件**：判据清单的完整版、每条判据的例外、以及"对照实验该怎么设计/怎么记录"见
`references/reconstruction-evaluation-criteria.md`。

## 相关 skills

- **compute-and-validate-p-of-r** — `depends-on`（本 skill 依赖对方）：重建的输入必须是可信的 P(r)（且按下游选截断或全 q）；判据 6 不通过时的第一动作是回那边复查。
- **assess-guinier-fit-quality** — `depends-on`（本 skill 依赖对方）：痕量聚集会同时毁掉 Guinier 与珠模型，低 q 的结论必须先成立。
- **fit-a-high-resolution-model-to-data** — `composes-with`（本 skill 指向对方）：对齐只是可视化；要判别高分辨结构是否真的吻合溶液，用那边的计算曲线直接拟合数据。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/INDEX.md`（若已建）。
