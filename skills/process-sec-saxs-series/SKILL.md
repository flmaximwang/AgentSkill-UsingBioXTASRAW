---
name: process-sec-saxs-series
description: "处理 SEC-SAXS 系列（连续洗脱帧）→Rg/MW 平台判据与 MW(Vc/Vp) 成一条曲线：色谱图→buffer/sample 区→扣减→送 Profiles。用于「一千多帧怎么变成一条曲线」「Auto 选的 buffer 能信吗」「峰上 Rg 随帧号不平、该取哪一段」「SEC 的分子量怎么算」「峰前小峰要不要算进样品」；SEC 不能用 I0 标样/绝对校准定浓度。不做基线校正（转 correct-sec-saxs-baseline），不做 SVD/EFA 分解。"
source_book: 《利用BioXTAS RAW程序处理SEC-SAXS数据》· 刘广峰（公众号「生物小角」）· 2024-04-28 ；BioXTAS RAW 官方文档 *Basic SEC-SAXS processing*（v2.4.1）
source_chapter: 源A ①–⑮ / 源B 1–22、39–45
tags: [saxs, bioxtas-raw, sec-saxs, series, chromatography, bl19u2]
related_skills:
  - slug: configure-bioxtas-raw-for-a-dataset
    relation: depends-on
  - slug: assess-guinier-fit-quality
    relation: composes-with
  - slug: correct-sec-saxs-baseline
    relation: contrasts-with
  - slug: reduce-saxs-frames-to-curves
    relation: contrasts-with
---

# SEC 系列 → 一条可信曲线

批次实验的直觉在这里会害人：SEC 数据不是"一个样品的 20 帧"，而是**上千帧的整个洗脱过程**。要不要把某一段当作"一个样品"，本身就是一个需要证据的判断——这个 skill 干的就是给出那份证据（Rg/MW 平台）并把选定区间变成一条曲线。

## R — 原文 (Reading)

**源 A（微信文章，译文 + BL19U2 增补）**

> 在典型的SEC-SAXS实验中中，当色谱柱的洗脱液（流出物）流过SAXS样品池时，会连续收集图像。由于蛋白质比缓冲液的散射更强烈，因此总散射强度与时间的关系图（即所谓的SAXS色谱图（或散点图））将显示一组类似于SEC系统的UV吸收曲线。
>
> 出处：源A 引言

> 警告：自动选择缓冲液可能是错误的！始终手动检查程序选择的区域。特别是，主峰旁边的大而平坦的前缘肩部可能看起来像算法的基线区域，并且经常会被错误地挑选出来。
>
> 出处：源A ⑧

> 在19U2，如果需要进行强度校正，则由于统计规则，最后一帧不能用。
>
> 出处：源A ③（BL19U2 线站增补）

**源 B（官方教程，权威原文）**

> RAW first averages the selected sample and buffer regions in the unsubtracted data, then subtracts. This avoids the possibility of correlated noise that would arise from averaging the subtracted files.
>
> 出处：源B 第 19 步 note

> A monodisperse peak should display a region of flat Rg and MW near the center. Note that some spread on either edge can come from small shoulders of other components, bad buffer selection, or just the low signal to noise in the tails of the peak.
>
> 出处：源B 第 17 步

> The I(0) reference and absolute calibration will not be accurate for SEC-SAXS data, as the concentration is not accurately known.
>
> 出处：源B 第 22 步 note

## I — 骨架 (Interpretation)

与批次还原（`reduce-saxs-frames-to-curves`）的根本差别只有一句话：**"一条曲线"的边界不再是文件，而是要自己从洗脱过程里判出来。**

整件事是三段，且每段的产物都是下一段的输入：

1. **读色谱图** —— 载入 Series（`Plot Series`）之后，每个数据点是**一帧**散射曲线的积分强度，横轴是帧号。这张图和 SEC 的 UV 吸收曲线形状可比，所以你能用"峰"这种语言说话：主峰、前肩、拖尾。
   - 纵轴可以换成平均强度，或某个 q / 某个 q 区间的强度。**看某个 q 区间的强度比看总强度更能分辨小组分**（低 q 区对聚集体敏感，高 q 区对噪声敏感）。
   - 端点帧有固定的技术性例外：首帧可能因 shutter 未及时开启整帧偏弱；BL19U2 上末帧按统计规则不能用于强度校正。它们落在基线区里，会直接改变基线取值，先剔。
2. **判"哪一段是一个物种"** —— 在 LC Analysis 里定缓冲液区、`Set buffer` 之后，RAW 用**滑窗**（window size=N：帧 0-4、1-5、2-6…）逐段平均再扣减，给出 Rg / I(0) / MW(Vc) / MW(Vp) 随帧号的曲线。
   **判据是平台**：峰中心应有一段 Rg 与 MW 平稳的区间；两侧的起伏分别来自低信噪比（浓度低）、肩峰（其他组分）、左右基线不等（损伤蛋白粘窗）。所以"选样品区"这个动作 = 把那段平台圈出来。
3. **变成一条曲线** —— 把选定区间送 Profiles（`To Profiles Plot`），再做标准 Guinier/MW 分析（转 `assess-guinier-fit-quality`）。

三条不可交换的次序/限制：

- **先平均、后扣减**：缓冲液区内所有帧先平均成一条，样品区按窗口平均后再相减。反过来（先逐帧扣再平均）会让各帧误差相关化，平均不再按 √N 降噪。
- **缓冲液区必须真的是缓冲液**：自动选择只认"低而平"，而部分分离的高阶寡聚体前肩恰好低而平。自动之后必须放大到基线处人工复核；SAXS 信号弱时去对照 SEC 的 **UV 痕**，看有没有被包含进来的次要洗脱组分。
- **浓度未知**：SEC 峰内浓度随时间变化且未知，所以**不能用标样 I(0) 比对或绝对校准**，MW 只能走 Vc / Vp 这类体积法；两法结果不一致是正常的，要并列看。

一句话判据：**"我凭什么说这 20 帧是一个物种？"——答不上来就不该把它们平均。**

## A1 — 案例 (Past Application)

**1. `sec_sample_1`：965 帧走完一整轮**（源A ①–⑪；源B 1–22、36）

- 问题：一条 965 帧的 SEC 系列，要得到"这个峰里是什么"。
- 做法：Files 里选中 `profile_001_0000.dat` → Shift 点最后一个 → **Plot Series** → 发现首帧强度明显偏低（MacCHESS G1 shutter 开启不及时）→ 从第 1 帧重新载入 → 读色谱图（看到峰前两个小峰 = 未能解析的高阶寡聚体；峰后基线与峰前不同）→ LC Analysis → Buffer **Auto**（示例落在 504–562）→ 人工复核 → `Set buffer` → Subtracted 图上出现 Rg/MW/I(0) 随帧号 → Sample **Auto**（示例 699–713）→ 确认平台 → `To Profiles Plot`。
- 结论：一条 SEC 曲线是"色谱图 + 两次区间选择 + 平台判据"的产物，不是一条命令。
- 注：源 A 对同一数据集给的是 690–719，官方给 699–713——**两处数字不同**，这本身就说明区间选择有主观余量，必须自己看平台。

**2. BSA：有期望值的检验点**（源B 39–45）

- 问题：怎么知道整套流程给出的曲线是对的？
- 做法：载入 `sec_sample_2`（BSA）→ 选好缓冲液区 → 算峰上 Rg/MW → 取平台区送 Profiles → 做标准 Rg/MW 分析。
- 结论：BSA 的期望值是 **Rg ≈ 28 Å、MW ≈ 66 kDa**；流程正确时应能复现这两个数。这是本 skill 唯一一个"已知答案"的锚点。

**3. 手动路径（它失去了什么）**（源A ⑫–⑮）

- 做法：不打开 LC Analysis，给 series 加星 → 在 "Data to Profiles plot" 输入帧范围（示例 539–568 是缓冲液）→ `Average` → 再用批次还原的老办法（星标缓冲液 + Subtract）。
- 结论：能得到一条曲线，但**没有逐帧 Rg/MW 曲线可看**，于是"这段是不是一个物种"完全没有证据。所以它是**应急分支**，不是等价路线。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- BL19U2（或别的线站）做了 SEC-SAXS，拿回几百到上千帧的数据，要出一条可交付的曲线。
- 已经跑了 LC Analysis，但不确定 Auto 选的 buffer/sample 区对不对，或者 Rg 曲线看着不平。
- 想知道"该取峰顶几帧还是整个峰"。
- 峰前有小峰、峰后基线比峰前高，不知道该算到哪。
- 想报 MW，但不知道该用哪个数值/方法。

**语言信号**

- 「SEC 联用的数据怎么处理 / 这批 series 怎么变成一条曲线」
- 「LC Analysis 里 buffer 自动选的区间能信吗」
- 「Rg 在峰上不平，是不是我选错区间了」
- 「峰前面那两个小峰是什么，要不要扣掉」
- 「SEC 的分子量怎么算出来」

**与相邻 skill 的区别**

- 与 `reduce-saxs-frames-to-curves`：那边处理"一个样品的一批帧"（选文件 → 平均 → 扣减），**这里处理"一整段洗脱过程"**（选帧号区间 → 判平台 → 平均扣减）。判断对象不同：文件的边界 vs 物种的边界。若用户手上就是一批等条件的帧，走那边。
- 与 `correct-sec-saxs-baseline`：本 skill 到"扣减后的一条曲线（+ 平台证据）"为止；**扣减后基线仍有系统性漂移**时转过去。
- 与 `configure-bioxtas-raw-for-a-dataset`：本 skill 的第 1 步依赖它——配置没确证时，Series 载入后 RAW 可能直接报错（缺 cfg），且 q 轴与 Rg 整体不可信。
- 与 `assess-guinier-fit-quality`：那边读"这一条曲线"的 Rg/I0 与可信度；本 skill 决定"这条曲线由哪些帧构成"。

## E — 执行步骤 (Execution)

1. **确认配置**：会话里已加载当天 `.cfg`（RAW 在 Series 载入/参数计算时报错，通常就是缺配置）。
   完成标准：能说出用的是哪份 cfg。判停点：不确定 → 转 `configure-bioxtas-raw-for-a-dataset`。
2. **载入 Series**：Files 选项卡 → 选中系列首文件 → Shift 点末文件 → 按 **Plot Series**（不是 Plot）。
   完成标准：Series 面板与"强度-帧号"图出现。
   - 若使用自动载入（"Select" 一个文件名由 RAW 自行展开）→ 只在 cfg 为 BioCAT/MacCHESS 时可用；BL19U2 用不上，改用手选或 `.hdf5`。
3. **剔端点帧**：检查首帧是否离群（shutter 未及时开启 → 整帧偏弱），BL19U2 上末帧不参与强度校正。
   完成标准：能明确说出"首帧留/剔、末帧留/剔"及其依据（源A ③）。
4. **读色谱图**：先看总积分强度；再切到**低 q 区间**强度看峰（Series 面板 `Plot Controls` → `Intensity:` 选 `Intensity in q range`，右边填起止 q；或菜单 `View → Series Plot Left Y Axis`）。
   完成标准：能指出主峰范围、峰前小峰（若存在）、以及峰前后基线是否等高。
5. **打开 LC Analysis**：Series 面板底部 `LC Analysis`（或右键系列名 → LC Series analysis）；在 Series info 里按样品类型设分子类型（蛋白/RNA）、窗口大小。
6. **定缓冲液区**：`Buffer → Auto`，然后**人工复核**：放大到基线，确认区间内没有肩部/小峰（1–4 步的观察在此兑现），必要时用上下箭头微调。
   完成标准：能说出"这个区间为什么真的是缓冲液"（必要时引用 UV 痕）。判停点：数据噪声大、无法判断 → 先拿 UV 痕对齐再定。
7. **`Set buffer`**：得到 Subtracted 图 + 逐帧 Rg / I(0) / MW(Vc) / MW(Vp)（滑窗 N 由 Series info 决定）。
   完成标准：Subtracted 图出现随帧号的参数曲线。
8. **选样品区（平台判据）**：在 Rg 与 MW 上找到峰中心那段平稳区间，用 `Sample → Auto` 取起点再人工确认。
   完成标准：**在图上指出平台区**，并说明两侧起伏的来源（低信噪/肩峰/基线不等）之一。
   - 判停点：找不到平台（Rg 单调变化或剧烈跳动）→ 不要硬选一段送出去；回到第 6 步检查缓冲液区，或考虑存在未分开的组分（分解类方法超出本 skill，见 B 段）。
9. **送 Profiles**：`To Profiles Plot`（RAW 先平均后扣减）。
   完成标准：Profiles 里出现一条扣减过的曲线，`*` 提示未保存。
   - 判停点：RAW 弹出区间质量警告（帧间相似度、低/高 q 行为、多奇异值、Rg/MW 相关性等）→ **读警告内容再决定**，不要习惯性点继续。
10. **下游分析**：转 `assess-guinier-fit-quality` 读 Rg/I0；MW 只报 Vc/Vp 且并列。
    完成标准：报告里能说出这条曲线由哪段帧号构成、缓冲液来自哪段帧号。
11. **保存记录**：Save series（`.hdf5`，含区间选择与基线设置）、Export data（CSV：帧号/积分强度/Rg/MW/文件名）
    完成标准：别人能凭这两个文件重放你的区间判断。
    - 应急分支：如果 LC Analysis 不可用，走手动路径（源A ⑫–⑮：星标 series → 输入帧范围 → Average → 再 Subtract）。**明确告知用户代价**：没有逐帧参数曲线，等于放弃平台证据。

## B — 边界 (Boundary)

**不要用的场景**

- 手上是"一个样品的一批等条件帧"（批次实验）→ 走 `reduce-saxs-frames-to-curves`。
- 已经在问"这条曲线的 Rg 是多少、信不信得过" → 走 `assess-guinier-fit-quality`。
- **SVD / EFA / REGALS 分解、多序列（时间分辨）分析、WAXS 合并**：官方有独立章节，本包未收录，不成 skill——不要拿本 skill 的区间判据去套（分解的判据是组分数与浓度曲线，不是平台）。
- 要做**基线校正**（扣减后仍有漂移）→ 走 `correct-sec-saxs-baseline`。
- 线段整体的实验设计问题（柱子选择、上样量、缓冲液匹配）不在覆盖范围。

**源里明确警告过的失败模式**

- **相信自动选出的缓冲液区**（源A ⑧、源B 第 13 步）：主峰旁大而平的前肩最容易被误选，会把寡聚体当背景扣掉，制造"假单分散"。
- **把峰前小峰算进缓冲液区**（源B 第 9、15 步）：那两个小峰往往是未解析的高阶寡聚体，属于样品。
- **先逐帧扣减再平均**（源B 第 19 步 note）：噪声相关化，降噪失效——用 `S_` 曲线去做 Average 就是这个错误。
- **只用峰前单侧缓冲液**（源A ⑤、源B 第 23–33 步）：峰后基线往往已经不同（损伤蛋白粘窗），会引起低 q 假信号；解法是双缓冲液区或基线校正。
- **把批次实验的习惯搬过来**（源B 第 22 步 note）：SEC 不能用标样 I(0)/绝对校准定浓度，MW 只能走 Vc/Vp。
- **用"峰看起来对称"代替平台判据**（源A ⑫–⑮ 的手动路径最容易这样）。

**作者/材料盲点（阶段 0 批判第 6、7 条）**

- 两源都**不给"该不该相信这次分离"的上位判据**（柱子分得开吗、缓冲液匹配吗）。本 skill 只能保证"在你给的洗脱过程里，取出的这一段是自洽的"。
- **对帧的取舍没有系统规则**：只有两个端点例外，没有"如何发现辐照损伤帧/坏帧"的方法。若用户在这一点上要结论，必须明说材料不覆盖。
- 源 A（译文）**省略了区间质量警告、双缓冲液区，以及"浓度未知"这条限制**；本 skill 的 B 段把这三条补回并标注来源，凡引用它们的回答都应说明"这句来自官方教程而非那篇文章"。

**参考文件**：Series / LC Analysis 面板、三档图（Unsubtracted / Subtracted / Baseline Corrected）、calc markers、CHROMIXS 口径差异、`.hdf5`/CSV/report、12 条术语的"作者用法 vs 常识"见
`references/sec-saxs-series-workspace.md`。共享术语（Rg/q 单位、n_min、掩膜、cfg）见
`../configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md`。

## 相关 skills

- **configure-bioxtas-raw-for-a-dataset** — `depends-on`（本 skill 依赖对方）：Series 载入与参数计算都要求当天 cfg；缺配置时 RAW 直接报错，且 q 轴/Rg 整体不可信。
- **assess-guinier-fit-quality** — `composes-with`（本 skill 指向对方）：本 skill 交付一条扣减过的曲线，那边负责读 Rg/I0 与报告区间；SEC 的 I0 不能做绝对标度，这条限制在两边都写明。
- **correct-sec-saxs-baseline** — `contrasts-with`（本 skill 指向对方）：扣减后基线仍有系统性漂移时，二选一：双缓冲液区（本 skill 第 6 步的延伸）或基线校正（那边）；二者不等价，且与 EFA 分解的兼容性不同。
- **reduce-saxs-frames-to-curves** — `contrasts-with`（本 skill 指向对方）：同为"造一条曲线"，但"一条曲线的边界"来源不同（文件的批次 vs 洗脱过程里的物种平台）。

完整关系图与推荐顺序见 `books/sec-saxs-series/INDEX.md`。
