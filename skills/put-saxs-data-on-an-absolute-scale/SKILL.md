---
name: put-saxs-data-on-an-absolute-scale
description: "SAXS 强度要放到绝对刻度（cm⁻¹）、算水/玻碳绝对标度常数时用它：按可用条件在水、玻碳 Simple、玻碳 Full(NIST) 三法里选，不按偏好；写清两条顺序约束（算常数前先关绝对刻度、算完不得再改归一化含通量/透射）与三个基准校验值（水 4 °C≈0.00077 / 玻碳 Simple 1.0 mm≈324 / NIST 1.5 mm+I1/I3≈198）。不覆盖：标样图像本身的定心/掩膜/归一化设置（转 configure-bioxtas-raw-for-a-dataset）；浓度未知的 SEC 数据不能这样做，转 process-sec-saxs-series；不负责 MW 方法选择。"
source_book: BioXTAS RAW 官方教程 *Setting absolute scale with water / with glassy carbon*（v2.4.2）
source_chapter: tutorial/s3_abswater.rst + tutorial/s3_abscarbon.rst
tags: [saxs, bioxtas-raw, absolute-scale, calibration, glassy-carbon, water, normalization]
related_skills:
  - slug: configure-bioxtas-raw-for-a-dataset
    relation: depends-on
  - slug: assess-guinier-fit-quality
    relation: composes-with
  - slug: process-sec-saxs-series
    relation: contrasts-with
---

# 把强度钉到绝对刻度：三法分叉 + 两条顺序约束

任意刻度上的 SAXS 曲线可以做形状、Rg、MW 的**相对**判断，但报不了绝对 `I(0)`/浓度。绝对刻度就是在标样上量一个**比例因子**，把整条曲线乘到 cm⁻¹。这个 skill 只解决一件事：**用哪种标样、以什么顺序算这个常数、算完怎么知道它对不对**。

三法不是"哪个更好"的排序题，而是**按你手上有哪些可用条件**分叉。而且有两条反直觉的**顺序约束**——违反它们不会报错，只会得到一个坏的常数。

> 版本绑定 **RAW 2.4.2**；本节判据全部来自 B 级 `40-tutorial`（tutorial/s3_abswater 与 s3_abscarbon）。**A 级 `20-manual` 不得作事实依据**：旧手册只讲水法、且自承落后多个版本（文档内部矛盾 C3）。

## R — 原文 (Reading)

> "Glassy carbon is the more accurate approach, if available."
>
> [FILE: tutorial/s3_abscarbon.rst]

> "There are two ways to use glassy carbon as a standard in RAW. One way follows the NIST protocol, and will deliver the most accurate results."
>
> [FILE: tutorial/s3_abscarbon.rst]

> "This method depends on all measurements having reliable flux measurements upstream and downstream of the sample."
>
> [FILE: tutorial/s3_abscarbon.rst]

> "The second way is more similar to that used by water, in that it essentially ignores the background (assumes it to be small)."
>
> [FILE: tutorial/s3_abscarbon.rst]

> "It is important that you not change your normalization settings once you have set the absolute scaling constant. If you do, you will have to recalculate the absolute scaling constant."
>
> [FILE: tutorial/s3_abswater.rst · s3_abscarbon.rst]

> "make sure absolute scale is turned off before you calculate the scale constant, otherwise you will get a bad scaling constant"
>
> [FILE: tutorial/s3_abswater.rst · s3_abscarbon.rst]

> "All of the normalization (including flux, transmission, etc) happens through the absolute scale panel. You shouldn't have anything set in the Normalization panel"
>
> [FILE: tutorial/s3_abscarbon.rst（Full/NIST 节）]

> "This approach will only work if the .dat files you select ... contain the upstream and downstream counter values."
>
> [FILE: tutorial/s3_abscarbon.rst（Full/NIST 节）]

> "You should get a value near 0.00077. … You should get about 324. … You should get an absolute scaling constant near 198."
>
> [FILE: tutorial/s3_abswater.rst · s3_abscarbon.rst]

> "the two methods of glassy carbon calibration agree within ~1.5%"
>
> [FILE: tutorial/s3_abscarbon.rst（Comparison note）]

## I — 骨架 (Interpretation)

把这件事看成**给整条曲线乘一个因子**：`I_abs(q) = I(q) × 常数`。于是问题只有两个——常数从哪来、它算得对不对。

**1. 三法分叉：按「可用条件」选，不按偏好。**

| 方法 | 触发条件（你手上有什么） | 代价 |
|---|---|---|
| **水** | 只有水标样数据 | 最简，但精度最低 |
| **玻碳 Simple** | 有玻碳数据，但背景未知/很小，只有常规归一化 | 忽略背景（假定它很小），需一次背景测量 |
| **玻碳 Full (NIST)** | 有玻碳数据，且**上下游通量测量可靠、背景测量准确** | 最准，但依赖可靠的上/下游通量（I1/I3）与准确背景 |

一句话：**有玻碳就用玻碳**（比水准）；有玻碳后再看「背景/上下游通量是否可靠」决定 Simple 还是 Full。官方在示例数据上报告两种玻碳法**一致到约 1.5%**——所以别把它们当两个数量级的差别。

**2. 共享骨架（三法一模一样，只是多填少填几个字段）。**

```
Absolute Scale 面板 → 选标样（水法设水温；玻碳法设厚度；Full 法设背景与上下游计数器）
                    → Calculate 得常数 → 勾选 “Normalize processed data to absolute scale …”
```

**3. 两条顺序约束（这才是本 skill 的独有知识，且违反不报错）。**

- **约束 A：算常数前必须关掉绝对刻度。** 否则得到坏常数（原文 `otherwise you will get a bad scaling constant`）。
- **约束 B：设好常数后不得再改归一化设置（含通量/透射）。** 改了就必须**重算**常数，不能沿用旧的。
  - 原因：常数是**在当时的归一化设置下**标定的；归一化一变，同一批数据的绝对强度就差一个因子，而 RAW 不会提示"常数已失效"。
  - Full（NIST）法还有附加版：**Normalization 面板应清空**，所有归一化统一经 Absolute Scale 面板完成。

**4. 常数对不对，靠基准值核对（校准链是否接对的独立校验点）。**

| 校准 | 条件 | 官方期望值 |
|---|---|---|
| 水 | 4 °C | ≈ **0.00077** |
| 玻碳 Simple | 厚度 1.0 mm | ≈ **324** |
| 玻碳 Full (NIST) | 厚度 1.5 mm，I1/I3 | ≈ **198** |

一句话判据：**先问「我有什么数据」定方法，再问「算出的常数离基准值远不远」定对错**；对不上先查两条顺序约束，而不是先怀疑数据。

## A1 — 案例 (Past Application)

**1. 水法：得到 ~0.00077**（源 a19；[FILE: tutorial/s3_abswater.rst]）

- 问题：要把任意刻度换成绝对刻度，且手上只有水标样。
- 做法：载 `calibration_data/extra` 的 **SAXS.cfg** → 平均 `MT2_48_001_000x.tiff`（空池）与 `water2_49_001_000x.tiff` 并**存盘** → Advanced Options → `Absolute Scale` → `Empty cell`=A_MT2_48_001_0000.dat、`Water sample`=A_water2_49_001_0000.dat、`Water temperature`=**4 °C** → `Calculate`。
- 结果：应得到 **near 0.00077**。勾选 “Normalize processed data to absolute scale”。
- 附带提示：也可以直接用图像定标，但**信噪比更差**——平均后的文件优于单帧。

**2. 玻碳 Simple：得到 ~324**（源 a19；[FILE: tutorial/s3_abscarbon.rst]）

- 问题：有玻碳数据，走"忽略背景"的简单路线。
- 做法：载/用第 3 部分的设置（**尚未用水定过绝对刻度**）→ 画 `glassy_carbon2_011_000x.tif`（x=1–2）→ 平均并存盘 → `Absolute Scale` → `Glassy carbon` Set=**A_glassy_carbon2_011__0001.dat** → `Sample thickness`=**1.0 mm** → `Calculate`。
- 结果：应得到 **about 324**。

**3. 玻碳 Full（NIST）：得到 ~198，且要求文件带 I1/I3**（源 a19 + ce12；[FILE: tutorial/s3_abscarbon.rst]）

- 问题：要最准的定标，且上下游通量、背景都可靠。
- 前置：载 `calibration_data/extra` 的 **SAXS.cfg** → 在 `Normalization` 面板**删光所有条目** → 在 `Absolute Scale` 面板**关掉已有绝对刻度**。
- 做法：画并保存玻碳 `glassy_carbon_41_001_0000.tiff`、以及 `vac_37_001_0000.tiff`、`MT2_48_001_0000.tiff` → `Absolute Scale` → **取消 `Ignore background`** → `Glassy carbon`=glassy_carbon_41_001_0000.dat、`Glassy carbon background`=vac_37_001_0000.dat、`Sample background`=MT2_48_001_0000.dat → `Sample thickness`=**1.5 mm** → `Upstream counter`=**I1**、`Downstream counter`=**I3** → `Calculate`。
- 结果：应得到 **near 198**。
- 前提警告（ce12）：**只有当选的 `.dat` 含上下游计数值时这法才成立**；`.dat` 通常自动带（RAW 默认），否则改用**图像**——噪声更大，但 RAW 能自动找到所有计数。
- 比较说明：示例数据上，Simple 与 Full 两种玻碳法**一致到约 1.5%**；最佳选择取决于背景散射相对总散射的强弱。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 曲线还是任意刻度，想换成**绝对刻度（cm⁻¹）**，以便报绝对 `I(0)`/浓度/做绝对强度比较。
- 手上有水标样或玻碳标样，问**该用哪一个**、区别是什么。
- 按教程算玻碳常数，却得到 **400 多**（而非 ~324/~198），怀疑是不是数据坏了。
- 已经在 Advanced Options 里填了 `Absolute Scale`，但**不确定顺序对不对**（有没有先关掉刻度、填完还能不能改归一化）。
- 想知道 **0.00077 / 324 / 198** 这些数字是不是该有的期望值、能拿来核对什么。
- 问“绝对刻度常数算完改了归一化要不要重算”。

**语言信号**

- 「怎么把 SAXS 强度放到绝对刻度 / absolute scale」
- 「绝对标度常数怎么算、算多少才对」
- 「用水还是用玻碳定标」
- 「我算出来 400 多，正常吗」
- 「绝对刻度算完了，我还能改归一化/通量吗」
- 「玻碳 Simple 和 NIST 有什么区别」

**与相邻 skill 的区别**

- 与 `configure-bioxtas-raw-for-a-dataset`：配置就绪是**前提**（掩膜/定心/归一化先到位），绝对刻度是配置链的**后一环**；本 skill 假设标样图像已经被正确地定心、掩膜、归一化。
- 与 `process-sec-saxs-series`：**SEC 数据不能用本法**——洗脱峰内浓度未知，绝对刻度给出的浓度不可靠。
- 与 MW 方法选择（`choose-a-molecular-weight-method`）：本 skill 只把**强度**放上绝对刻度；"用哪个方法报 MW" 是另一个决策点。

## E — 执行步骤 (Execution)

1. **确认标样数据齐备且已平均存盘。** 水法需空池图 + 水样图；玻碳 Simple 需玻碳测量 + 一次背景；Full 需玻碳 + 玻碳背景 + 样品背景。
   完成标准：每个标样都已 Average 并存成 `A_*.dat`（可直接被 `Set` 选中的文件）。
2. **按可用条件选方法**（不要按"哪个更高级"选）：
   - 只有水 → **水法**；有玻碳 → 优先玻碳；玻碳 + 可靠上下游通量 + 准确背景 → **Full (NIST)**；玻碳但背景未知/只需常规归一 → **Simple**。
   完成标准：能说出"我为什么只能/该用这条法"。
3. **【顺序约束 A】先关掉绝对刻度。** Advanced Options → `Absolute Scale`：清除/取消已有的绝对刻度。
   Full 法**再加一步**：到 `Normalization` 面板**删光所有条目**。
   完成标准：当前会话**没有**处于"已勾选绝对刻度归一化"的状态。判停点：这一步没做 → 后面必得坏常数，返回重做。
4. **在 `Absolute Scale` 面板填字段**：
   - 水法：`Empty cell`=空池 `.dat`、`Water sample`=水样 `.dat`、`Water temperature`=**4 °C**。
   - 玻碳 Simple：`Glassy carbon` Set=玻碳 `.dat`、`Sample thickness`=**1.0 mm**（保持 `Ignore background`）。
   - 玻碳 Full：取消 `Ignore background`；三个 Set（玻碳 / 玻碳背景 / 样品背景）；`Sample thickness`=**1.5 mm**；`Upstream counter`=**I1**、`Downstream counter`=**I3**。
   完成标准：与所选方法对应的字段全部填对（厚度、计数器、背景别漏）。
5. **点 `Calculate`，用基准值核对常数。** 期望：水 4 °C≈**0.00077**、玻碳 Simple 1.0 mm≈**324**、玻碳 Full 1.5 mm+I1/I3≈**198**。
   完成标准：算出的常数与对应基准同量级且接近。判停点：数量级不对 / 离基准很远 → 回第 3 步查两条顺序约束，再查是否选错文件/漏填字段（ce03、ce12）。
6. **勾选 “Normalize processed data to absolute scale using <标样>”，再 `OK` 保存设置。**
   完成标准：复选框已勾、面板退出时保留了改动。
7. **【顺序约束 B】冻结归一化。** 此后**不得**再改归一化设置（含通量/透射等）；一旦改了，必须回到第 3 步**重算**常数。
   完成标准：能明确说出"本次常数对应的是哪一套归一化设置"。
8. **把设置存进 `.cfg`** 供本次实验复用。
   完成标准：重开时绝对刻度常数与勾选状态仍在。

## B — 边界 (Boundary)

**不要用的场景**

- 只是做**相对**比较（形状、Rg、曲线间比对）→ 不必上绝对刻度。
- 手上有的是 **SEC-SAXS** 数据（浓度未知）→ 转 `process-sec-saxs-series`；SEC 的 I(0) 与绝对校准**不准确**。
- 问题其实是**标样图像的定心/掩膜/归一化**没设对（q 轴全错）→ 转 `configure-bioxtas-raw-for-a-dataset`；绝对刻度只是配置链末端的一环。
- 要决定**报哪个 MW / 用哪条 MW 法** → 转 `choose-a-molecular-weight-method`，本 skill 不管。
- 没有**任何**标样数据 → 本法无从执行；先补齐标样或明确只做相对刻度。

**源里明确警告过的失败模式**

- **算常数前没关掉绝对刻度**（ce03）：不报错，但得到坏常数、`I(q)` 整体偏移、MW 与 `I(0)` 跟着错。
- **算完常数又改了归一化**（ce03 / p2o-22）：同样不报错；必须重算，不能沿用旧常数。
- **用 Full(NIST) 法却没满足前提**（ce12）：所选 `.dat` 不带上下游计数值，或没清空 `Normalization` 列表、没关掉已有绝对刻度 → 常数错（示例应近 198）。
- **把三法当选优排序**：它们的分叉依据是**可用条件**；在条件不满足时硬上 Full 法，得到的是比 Simple 更不可信的常数。

**材料盲点（阶段 0 批判）**

- 旧 **`20-manual` 只讲水法**（矛盾 C3），玻碳内容**只存在于 tutorial**；凡涉及玻碳的回答都应注明来自官方教程。
- tutorial 的绝对刻度细节又写「see the manual for details」，而 manual 已过时（**循环引用**）→ 本 skill 因此把操作路径写成可执行步骤、把对错判据落成**基准常数**，不依赖 manual。
- 官方**没给"常数差多少算失败"的定量阈值**，只给"near/about"级别；本 skill 因此只承诺"同量级且接近基准"，不编百分比。

**参考文件**：三法对照表、两条顺序约束的完整表述、三个基准常数与「不得再改归一化」的后果见
`references/absolute-scale-and-normalization.md`。

## 相关 skills

- **configure-bioxtas-raw-for-a-dataset** — `depends-on`（本 skill 依赖对方）：掩膜/定心/归一化没到位时，绝对刻度是在错误的基础上定标。
- **assess-guinier-fit-quality** — `composes-with`（本 skill 指向对方）：绝对刻度让 `I(0)` 有了物理单位，读取与可信度仍归那边。
- **process-sec-saxs-series** — `contrasts-with`（本 skill 指向对方）：SEC 浓度未知，是"绝对刻度不适用"的典型反例。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/`（本卷阶段 1.5 `verified.md` 的 N1 单元）。
