---
name: fit-a-high-resolution-model-to-data
description: "把高分辨结构（晶体/CryoEM/AlphaFold）对照 SAXS 数据时用「计算即拟合」：不要先生成 minimal 理论曲线再比；CRYSOL（需 ATSAS）与 PDB2SAS（DENSS 内建、RAW 默认、不支持 .cif）二计算器分工。用于「理论曲线低 q 差很多是不是模型错了」「minimal 曲线拟合差」「PDB2SAS 拟合的 q 只到一半」「高长径比要不要调 harmonics」「默认计算器被改成 CRYSOL 了」「.cif 打不开」「哪个模型拟合得更好」；不负责重建形状（转 evaluate-a-shape-reconstruction），不负责 MW 方法选择（转 choose-a-molecular-weight-method）。"
source_book: BioXTAS RAW 官方文档 *Theoretical profiles and fitting from models – CRYSOL* / *– PDB2SAS (DENSS)*（v2.4.2）；方法学 *Bead model reconstructions*（对照组：用 CRYSOL/FoXS 直接拟合判优劣）；ATSAS（CRYSOL 路线需要）
source_chapter: 源A 40-tutorial.md · s2_crysol / s2_pdb2sas；源B 30-saxs.md · saxs/saxs_bead_models.rst（FAQ）
tags: [saxs, bioxtas-raw, crysol, pdb2sas, denss, theory-data, model-fitting]
related_skills:
  - slug: evaluate-a-shape-reconstruction
    relation: contrasts-with
  - slug: configure-bioxtas-raw-for-a-dataset
    relation: composes-with
---

# 理论曲线不是"算出来再比"，而是"算的时候就把数据拟合进去"

拿一条晶体/CryoEM/AlphaFold 结构去对照 SAXS 数据，最自然的想法是"独立地算出它的理论曲线，再和实验曲线叠一叠"。**文档明确说这条路经常失败——即使模型和溶液结构确实吻合。** 原因是溶剂项（水化层、排除体积）本身难以建模，而计算器把它们当**拟合参数**。所以正确做法是：生成理论曲线的过程**就是拟合数据的过程**。

## R — 原文 (Reading)

> you should actually fit the data as part of the process of generating the theoretical profile
> … rather than generating a 'minimal' theoretical profile and comparing to the data.
>
> 出处：源A s2_crysol [FILE: 40-tutorial.md · tutorial/s2_crysol.rst]

> this 'minimal' approach often fails to produce good fits even when the model and solution structure are in good agreement
> … there are contributions from the solvent, particularly the hydration layer and the excluded volume, that are hard to model
>
> 出处：源A 同上

> We will use RAW to run CRYSOL. Note that you need ATSAS installed
>
> 出处：源A 同上

> PDB2SAS allows you to fit the excluded solvent and hydration shell to best match experimental data.
> … .cif files are not currently supported in PDB2SAS.
>
> 出处：源A s2_pdb2sas [FILE: 40-tutorial.md · tutorial/s2_pdb2sas.rst]

> PDB2SAS is the default calculator in RAW. However, it is possible that it has been changed to CRYSOL by a user.
>
> 出处：源A 同上

> The Data, Chi^2, and Prob. fields are only calculated if the model is fit to data.
>
> 出处：源A s2_crysol [FILE: 40-tutorial.md · tutorial/s2_crysol.rst]

> The .abs is on an absolute scale of 1/(cm*(mg/ml)), while .int is on an arbitrary scale.
> … More harmonics are necessary to get accurate theoretical profiles from high aspect ratio objects.
>
> 出处：源A 同上

> the default number of samples (128) is too small. This protein is elongated causing the real space voxel size to be quite large
> … Setting the N samples to a power of 2 (64, 128, 256, etc.) is best for calculation speed, though any even number can be used.
> … You can explicitly set the voxel size in the Advanced Settings, which will override N samples.
>
> 出处：源A s2_pdb2sas [FILE: 40-tutorial.md · tutorial/s2_pdb2sas.rst]

> requires turning off the "Fit solvent" and "Fit hydration shell" options
>
> 出处：源A 同上

> the best way to compare your high resolution structure to SAXS data isn't by docking it in a bead model
> … If these fits are good, and the bead model doesn't agree with the high resolution structure, then the bead model is wrong.
>
> 出处：源B saxs_bead_models [FILE: 30-saxs.md · saxs/saxs_bead_models.rst]

## I — 骨架 (Interpretation)

**要把两件事分开：生成理论曲线（generation）与把理论曲线拟合到数据（fitting）。** 计算器默认两件都能做；RAW 的入口也一样——同一个窗口、同一个 Start。区别只在**实验数据有没有被加进去**：

- **加了数据** → 溶剂密度/水化层对比/排除体积被当作拟合参数，与数据一起解出；结果里出现 **Data / Chi² / Prob**（CRYSOL）或 **Data / Chi²**（PDB2SAS）字段，并画出理论曲线 + 数据 + 归一化残差。
- **没加数据**（把数据项全部取消勾选）→ 得到的是 **minimal 理论曲线**（CRYSOL 里显示为 `.abs` / `.int` 两条，差别只是整体标度：`.abs` 在 1/(cm·(mg/ml)) 的绝对刻度上、`.int` 是任意刻度）。官方的用词是这类结果**"常常即使模型与溶液结构吻合也拟合不好"**。

**由此推出四条操作性结论：**

1. **默认就加数据。** 想"严格地独立算一条曲线再叠图"是把难点（溶剂项）从拟合里拿掉，得到的差异里混着模型误差与溶剂模型误差，**无法归因**。
2. **`.cif` 与 `.pdb` 不是等价输入。** PDB2SAS **不支持 `.cif`**（须先转 `.pdb`）；CRYSOL 路线两者都能喂。
3. **默认计算器是被用户改过的可变量。** 文档点名"很可能是被某个用户改成了 CRYSOL"——所以**用前先核对** `Options → Advanced Options → General Settings` 的 `Default structure calculator`（可重置为 PDB2SAS）。默认值漂移会静默改变你得到的东西（曲线来源、标度、可用参数）。
4. **参数缺失本身就是信息。** 如果结果表里 **Data / Chi² / Prob 是空的**，那不是程序出错——是你这次算的是 minimal 曲线，数据根本没参与拟合。**判据：先看有没有 Chi²，再谈拟合好坏。**

**两个计算器的分工（按"能装什么"分，不是按谁更准）：**

| | CRYSOL | PDB2SAS |
|---|---|---|
| 来源 | ATSAS 包（**必须装 ATSAS**） | **DENSS 内建**（`denss.pdb2mrc.py` 的 GUI 形态） |
| RAW 里的默认 | 否（可能被用户设成默认） | **是**（除非被改过） |
| 输入结构 | `.pdb` 或 `.cif` | **只支持 `.pdb`**（`.cif` 不支持） |
| 思想 | 球谐展开：**harmonics 数是关键参数** | 先在实空间算原子/排除溶剂/水化层的电子密度图，再傅里叶变换 + 球平均：**实空间 N samples / voxel size 是关键参数** |
| 拟合标志量 | Data / **Chi² / Prob** | Data / **Chi²** |
| 独特产物 | `.abs`（绝对刻度）与 `.int`（任意刻度）成对出现 | 只出一条 `1XIB_4mer.dat` 形式的结果 |

**两类参数陷阱——症状与处方：**

- **症状 A：高长径比物体的拟合总差。** 处方：**加 harmonics**（官方示例直接把 harmonics 设到 **100**）。机制：高长径比物体需要更多球谐项才能准确展开；对球状蛋白（如 GI）几乎无差别，所以**这个参数只在细长体系上暴露**。
- **症状 B：PDB2SAS 的理论曲线在 q 上"够不到"实验数据的高 q 端。** 处方：把 **N samples（real space）默认的 128 改成 256**。机制：细长蛋白的实空间 voxel size 被迫变大 → 倒空间可达的 q_max 变小；样本数补上后曲线就能覆盖实验的全 q 范围。样本数**取 2 的幂（64/128/256…）速度最好**（任意偶数也行）；**在 Advanced Settings 里显式设 voxel size 会覆盖 N samples**（两者是同一件事的两种给法）。

**一条独立的第三方用途（本 skill 存在的第二个理由）：** 文档在珠模型的 FAQ 里给出方向性结论——比较高分辨结构与 SAXS 数据，**正确做法是直接拟合（CRYSOL/FoXS），而不是 dock 进珠模型**。推论：
- 拟合差 → **高分辨结构不匹配数据**（无论珠模型显示什么）；
- 拟合好而珠模型不吻合 → **错的是珠模型**。

一句话判据：**"我这次的 Chi² 是从哪来的？"——如果没有 Chi²，说明我算的还是 minimal 曲线，等于没做这件事。**

## A1 — 案例 (Past Application)

**1. `1XIB_4mer.pdb`（GI）：minimal 与 fit 的差别在结果表上是"有没有 Chi²"**（源A s2_crysol）

- 做法 A（最省事）：Files 面板里点 `1XIB_4mer.pdb` 的 Plot 按钮 → CRYSOL 用**默认参数**算 → Profiles 里出现两条曲线 `1XIB_4mer.abs` 与 `1XIB_4mer.int`。
- 做法 B（要控制参数）：`Tools → ATSAS → CRYSOL` 打开窗口 → models 区 Add 加 `1XIB_4mer.pdb` → Start → 结果表**部分参数不显示**（Data / Chi² / Prob 空）。
- 做法 C（拟合）：把 `glucose_isomerase.dat` 载进 RAW → CRYSOL 窗口 Experimental data 区 Add → 勾选该数据（**只有已载入 RAW 的数据才能加进列表**）→ Start → 右图出现理论曲线 + 数据 + 不确定度归一化残差，结果表**全部参数齐**（Data / Chi² / Prob 都有）。
- 结论：OK 关闭后，拟合曲线以 `1XIB_4mer_glucose_isomerase_FIT` 出现在 Profiles 里。**同名规律（`<模型>_<数据>_FIT`）就是"这是拟合结果"的标记。**

**2. `Brpt55_M_Zn.pdb`（长细棒，SASDP43 数据）：harmonics 100 明显更优**（源A s2_crysol）

- 做法：载 `SASDP43.dat` → 开两个 CRYSOL 窗口、加同一个模型与数据 → 第一个用默认设置跑；第二个把 **harmonics 设成 100** 再跑。
- 结果：**100 harmonics 的拟合更好。**
- 结论：官方点明这个蛋白是"long thin rod"，**高长径比物体需要更多 harmonics 才能得到准确的理论曲线**；球状蛋白（如 GI）应几乎无差别——可用 GI 数据自测这一点。另：Advanced Settings 里**溶剂密度与对比度需要先关掉 "Fit solvent"** 才能手改。

**3. `Brpt55_M_Zn.pdb` + SASDP43（PDB2SAS 侧）：N samples 128 → 256 把 q 范围补全**（源A s2_pdb2sas）

- 做法：载 `SASDP43.dat` → 开 PDB2SAS 窗口、加模型与数据 → 第一遍用默认设置跑 → 开第二个窗口，把 **N samples (real space) 改成 256** 再跑。
- 结果：默认 128 时**理论拟合的最大 q 值到不了实验的最大 q**（细长蛋白实空间 voxel 太大 → q_max 太小）；256 时覆盖实验数据的全 q 范围。
- 结论：这是"参数不够"而不是"模型错"的典型症状；样本数取 2 的幂最快，也可用 voxel size 直接指定（会覆盖 N samples）。

**4. 一模型对多数据 / 多模型对一数据：用拟合指标判优劣**（源A 两个教程）

- 做法：Profiles 面板选中多个 profile → 右键数据曲线 → `Other Analysis → Fit Model (CRYSOL)` 或 `Fit Model (DENSS PDB2SAS)` → 窗口自动带上选中的数据；models 列表里**只有被勾选的模型参与计算**（不勾选即停用，无需删除）。
- 结果：可以一次把一个模型拟合到多条数据、或把多个模型拟合到同一条数据，读各自的 Chi² 判断"哪个数据集/哪个模型拟合得更好"。
- 结论：模型比对（例如同源二聚体 vs 四聚体排布）就是在这层做的；CRYSOL 侧还能把结果表右键 Export Data 成 csv。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 手上有一条扣减好的 `.dat` 和一个晶体/CryoEM/AlphaFold 模型，想知道"这个模型配不配得上这条曲线"。
- 已经用 Plot 直接生成了理论曲线，发现低 q 差很多，怀疑是模型错了。
- 结果表里 Chi² / Data / Prob 是空的，不知道正不正常。
- PDB2SAS 算出来的理论曲线 q 范围比数据短一截。
- 拟合一个细长蛋白，怎么调都不好，不知道是参数问题还是模型问题。
- 打开 RAW 发现默认计算器不是 PDB2SAS（被改成了 CRYSOL），想知道该怎么处理。
- `.cif` 文件喂给 PDB2SAS 没有结果。
- 在几个候选结构之间选一个（或判断某结构是否代表溶液态）。

**语言信号**

- 「我算的理论曲线和实验曲线在低 q 差很多，是模型错了吗」
- 「minimal 曲线拟合差正常吗」「要不要先生成理论曲线再比较」
- 「Chi² 那一栏是空的」「Prob 没显示」
- 「PDB2SAS 的理论曲线只到一半 q」
- 「高长径比的蛋白拟合不好，harmonics 要调吗」
- 「默认计算器变成 CRYSOL 了」「.cif 打不开」
- 「哪个模型拟合得更好」

**与相邻 skill 的区别**

- 与 `evaluate-a-shape-reconstruction`：那边评估**从头算的形状重建**（DAMMIF/DENSS）能不能用；本 skill 评估**已有高分辨结构**配不配得上数据。两者的分界线是文档给的：**要比较高分辨结构与数据，用本 skill（直接拟合）；两者不一致时，以本 skill 的结论为准（珠模型错）**。
- 与 `choose-a-molecular-weight-method`：那边管"该报哪个 MW、用哪类方法"；本 skill 里出现 MW 只是模型比对的副产物。
- 与 `assess-guinier-fit-quality`：那边判低 q 的 Guinier 是否成立。本 skill 必须先有一条**可信的扣减曲线**——若低 q 差很多，第一嫌疑是缓冲液扣减/聚集，不是模型。
- 与去卷积/时间分辨类 skill：那些从混合体系里拆组分；本 skill 是把一个**已知结构**拟合到一条（或多条）曲线。

## E — 执行步骤 (Execution)

1. **先核对默认计算器。** `Options → Advanced Options → General Settings` → 看 `Default structure calculator`。
   完成标准：能说出本机默认是 PDB2SAS 还是被人改成了 CRYSOL，以及你这次要用哪个。判停点：想用 PDB2SAS 却被改成 CRYSOL → 在这里改回来（文档明说"可能已被用户改过"）。
2. **确认输入结构格式与计算器匹配。** PDB2SAS **只吃 `.pdb`**；`.cif` 须先转换。CRYSOL 路线 `.pdb`/`.cif` 都可。
   完成标准：能说出"我的文件是 .pdb 还是 .cif、走哪个计算器"。判停点：手里只有 `.cif` 又要用 PDB2SAS → 先转格式，别硬跑。
3. **准备一条可信的实验曲线。** 载入扣减好的 `.dat`（CRYSOL/PDB2SAS 窗口的 Experimental data 列表**只列已载入 RAW 的数据**）。
   完成标准：数据出现在 RAW 的 Profiles 列表里，且低 q 的 Guinier 结论是站住的。判停点：低 q 有聚集/坏扣减的迹象 → 先回 `assess-guinier-fit-quality` 与还原流程，别把诊断浪费在模型上。
4. **打开计算器窗口并加模型（+ 数据）。** `Tools → ATSAS → CRYSOL` 或 `Tools → DENSS → PDB2SAS`；也可以用 Files 面板直接 Plot 一个 `.pdb`（**走默认参数**），或右键数据曲线 → `Other Analysis → Fit Model (...)`（自动带上选中数据）。
   完成标准：models 列表里有目标结构，**且已被勾选**（未勾选的项不参与计算）。判停点：不需要的模型先取消勾选再跑。
5. **把数据加进拟合（本 skill 的核心动作）。** 在 Experimental data 区 Add 并勾选数据 → Start。
   完成标准：结果表出现 **Data / Chi² / Prob**（CRYSOL）或 **Data / Chi²**（PDB2SAS），右图同时画出理论曲线、数据与归一化残差。判停点：**这些字段还是空的 → 你算的仍是 minimal 曲线**，回去勾上数据重算。
6. **判拟合；不好时按症状调参。**
   - 细长/高长径比体系拟合差 → 提高 **harmonics**（官方示例 **100**）；球状体系应基本无变化（可自测）。
   - PDB2SAS 理论曲线 q_max 够不到实验最大 q → **N samples 128 → 256**（用 2 的幂 64/128/256；或在 Advanced Settings 显式设 voxel size，它会覆盖 N samples）。
   - 要看溶剂/水化层对比如何影响拟合 → 先**关掉 "Fit solvent"**（PDB2SAS 还要关 **"Fit hydration shell"**）才能手改溶剂密度与对比度。
   完成标准：能说出"我改了哪个参数、为什么、结果变好还是变差"。判停点：调参后仍差 → 见第 7 步，不要无限调参。
7. **把它当判据用（证伪优先）。** 拟合好 → 高分辨结构与数据相容；拟合差 → 该结构不匹配数据，**无论珠模型怎么说**；拟合好而珠模型不吻合 → **错的是珠模型**。
   完成标准：给出方向性结论（相容 / 不相容），而不是"看起来差不多"。
8. **多候选/多数据集的比较。** 一次加多个模型对一条数据，或一个模型对多条数据（用 `Fit Model` 右键入口自带选中项），比较 Chi²。
   完成标准：能排出"哪个模型/哪个数据集拟合更好"。判停点：模型数与数据数都大于 1 时不要混着下结论，逐对比较。
9. **交付并落盘。** OK 关闭窗口 → 拟合曲线以 `<模型>_<数据>_FIT` 出现在 Profiles；需要全部输出时勾 `Save all outputs to folder`（CRYSOL 出 `.log`/`.alm` 等，PDB2SAS 出 `.dat`/`.fit` 等）；结果表可右键 Export Data 存 csv；也可 `Save report` 出 pdf（含理论曲线参数汇总表）。
   完成标准：记录里能写清"用了哪个计算器、哪些参数、拟合的 Chi² 是多少、结论是什么"。

## B — 边界 (Boundary)

**不要用的场景**

- 低 q 差很多但**实验曲线本身不可信**（扣减/聚集/Guinier 未过）→ 先修数据，本 skill 的结论会跟着错。
- 企图用"高分辨模型 + 拟合"来**代替**从头算形状重建（或反之）→ 两者回答不同问题；不一致时的裁决次序由文档给出（拟合优先）。
- 幻想从 SAXS 拟合里读出**高分辨细节** → 本流程只判"相容性"，不做分辨率提升。
- 想用 PDB2SAS 读 `.cif` → 不支持，改 `.pdb` 或走 CRYSOL。
- 系综/多构象体系的整体评判（柔性蛋白的构象分布）→ 本流程判的是单个结构，多构象要靠系综方法（EOM/SASSIE/BilboMD 等），超出本 skill。

**源里明确警告过的失败模式**

- **生成 minimal 曲线再叠图**（源A）：官方明说这条路"即使模型与溶液结构吻合也常常拟合不好"，因为溶剂/水化层/排除体积难建模且本应作为拟合参数。
- **拿没加数据的 Chi² 下结论**（源A）：Data / Chi² / Prob **只在拟合数据时才有**——空值不是程序问题，是方法没用对。
- **以为默认计算器不变**（源A）：PDB2SAS 是默认，但**可能已被某个用户改成 CRYSOL**；默认值漂移会静默改变曲线来源与可用参数。
- **把 `.cif` 喂给 PDB2SAS**（源A）：不支持。
- **细长物体沿用默认 harmonics / 默认 N samples**（源A）：前者让拟合无谓地变差，后者让理论曲线的 q 范围够不到实验数据——两者都容易被误读成"模型错了"。
- **想改溶剂密度却忘了关 "Fit solvent"**（源A）：CRYSOL 需关 "Fit solvent"；PDB2SAS 需同时关 "Fit solvent" 与 "Fit hydration shell"。

**材料盲点**

- 官方给的是"该怎么做、踩过哪些坑"，**没有给"Chi² 多大算拟合好"的阈值**——两个教程都只做相对比较（harmonics 100 优于默认、256 优于 128）。本 skill 因此**不编 Chi² 阈值**；要阈值含义需回到 `evaluate-a-shape-reconstruction` 里 χ² 的讨论（那是珠模型语境，不可直接搬过来）。
- 文档**没有说明 `Prob` 的定义与判读方式**（只说它在拟合时出现）。不要替它编解释。
- **多模型/多数据的比较没有给出"该比哪些数"的规范**（除了 Chi² 是显式存在的字段）。
- **FoXS** 在方法学里被并列为"直接拟合"的推荐程序，但**不在 RAW 教程覆盖范围内**（RAW 只集成 CRYSOL 与 PDB2SAS）；提到它时要说明这是文档之外的选项。
- 引用要求：用 RAW 跑 CRYSOL 需引用 CRYSOL 手册给出的文献；用 PDB2SAS 需引用其论文（`https://www.cell.com/biophysj/abstract/S0006-3495(23)00670-7`）。

**参考文件**：两个计算器的逐项参数、症状—处方表、以及结果字段与文件产物清单见
`references/model-fitting-parameters.md`。

## 相关 skills

- **evaluate-a-shape-reconstruction** — `contrasts-with`（本 skill 与对方互为对照）：那边评从头算重建；本 skill 评高分辨结构对数据的相容性。**两者不一致时，以本 skill 的拟合结论为准**（文档明确：拟合好而珠模型不吻合 → 珠模型错）。
- **configure-bioxtas-raw-for-a-dataset** — `composes-with`（本 skill 指向对方）：模型计算需要 .pdb/.cif 输入与一条扣减好的曲线；配置未确证时 q 轴与强度整体不可信。另外 `Default structure calculator` 这类程序级默认值属于"配置"的范畴，可在那个 skill 的 Options 面板地图里核对。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/INDEX.md`（若已建）。
