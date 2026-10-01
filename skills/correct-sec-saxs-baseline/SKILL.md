---
name: correct-sec-saxs-baseline
description: "扣减后强度-帧号仍漂移时按性质选基线校正：束流/仪器漂移→Linear，毛细管污垢→Integral；含过校正识别与 EFA 互斥。用于「SEC 扣减完基线还在抬/在漂」「峰后基线回不到零」「该用哪种基线校正」「校正完高 q 更怪了」「有没有现成脚本做基线校正」；不负责区间选择（转 process-sec-saxs-series）。"
source_book: BioXTAS RAW 官方文档 *Advanced Series processing – Baseline correction*（v2.4.1）；《利用BioXTAS RAW程序处理SEC-SAXS数据》· 刘广峰
source_chapter: 源C 全篇 / 源B 第 23–33 步
tags: [saxs, bioxtas-raw, sec-saxs, baseline-correction, drift]
related_skills:
  - slug: process-sec-saxs-series
    relation: depends-on
  - slug: assess-guinier-fit-quality
    relation: composes-with
---

# 扣减之后还在漂：按性质选基线校正

扣减缓冲液消除的是"溶剂的散射"，不是"基线随时间的变化"。当强度-帧号在扣减后仍有系统性漂移时，**先判漂移的性质，再选校正方法**——选错的代价是往数据里塞进一个假结构，比不校正更难发现。

## R — 原文 (Reading)

> Sometimes SEC data shows a baseline drift. This can be due either to instrumental changes (such as beam drift), or changes in the measured system, such as capillary fouling. RAW provides the ability to correct for these forms of baseline drift using either a linear or integral baseline method. The linear baseline method is best for instrumental drifts, while the integral baseline method is best for capillary fouling. Both baseline methods apply a distinct correction for each q value.
>
> 出处：源C 引言

> *Note:* To baseline correct data, you should only have buffer regions selected before the peak.
>
> 出处：源C 第 3 步 note

> you should see that the baseline is actually a little overcorrected. This is because the integral baseline correction only allows for positive or no change in the baseline, so if some q values need a negative correction the total baseline ends up overcorrected, as the positive values are brought down but the negative values are not brought up.
>
> 出处：源C 积分节 第 7 步

> An alternative approach to using several buffer regions is to use a single buffer region and apply a baseline correction. Both approaches have advantages and disadvantages. If you want to do EFA deconvolution, it is best to not use a baseline correction, however in other cases it will be more accurate as it doesn't assume a single average buffer across the peak.
>
> 出处：源B 第 33 步 note

## I — 骨架 (Interpretation)

先把"漂移"这个词拆成两种物理过程，因为它们对数据的作用方式不同：

- **仪器/束流漂移（instrumental drift）**：束流位置/强度随时间缓慢变化 → 基线近似**线性**上下移动，且对各个 q 的影响接近一致。
  → 用 **Linear**：在峰前、峰后各取一段"无基线变化"的平段，连一条直线，把这条直线从数据里减掉。
- **毛细管污垢（capillary fouling）**：样品池窗口被逐渐污染（尤其是受损/聚集的蛋白吸附），基线**随时间单调上升**，而且**在不同 q 上上升幅度不同**（散射贡献随 q 衰减）。
  → 用 **Integral**：允许基线单调不降的累积型校正，对**每个 q 各算一条**校正曲线。

由此推出四条操作性结论，它们才是这个 skill 的主要内容：

1. **每个 q 有各自的校正线。** 所以"只在低 q 做校正"在物理上等于"高 q 完全不校正"，会在 q 方向上留下一个折点（kink）——不能那么做。
2. **积分法只能往上抬（或不动），于是会过校正。** 若某些 q 本该往下校正，那些 q 没被拉下来，总和就显得抬过头。**过校正通常露在高 q**——因为高 q 段往往已经接近噪声水平。
3. **诊断过校正的仪器方法是把强度显示切成 q 区间逐段看**（官方示例试 0.01-0.02 / 0.05-0.06 / 0.1-0.2 / 0.2-0.27 Å⁻¹）。如果确认是高 q 噪声主导，正确处置是**先把曲线截断到较低 q，再做基线校正**，而不是加大校正力度。
4. **校正与分解是互斥的（在积分法上尤其明确）**：要做 EFA/SVD 分解就不要叠加基线校正——分解算法会把校正引入的单调变形当成一个"组分"。反过来，不做分解时基线校正通常比"假设全峰同一个缓冲液"更准。

一句话判据：**漂移是随时间线性来的（仪器），还是随剂量累积来的（污垢）？** 前者 Linear，后者 Integral；分不清就先看峰前后两段基线的**形状**（直线 vs 单调上弯）。

## A1 — 案例 (Past Application)

**1. `xylanase`：线性上漂 → 线性校正**（源C 1–11）

- 问题：数据一载入就看到积分强度有一段持续向上的斜率。
- 做法：LC Analysis → `Buffer → Auto`（校正时只保留**峰前**缓冲液区）→ 展开 Baseline Correction → 选 `Linear` → 在 Subtracted 图上拖出**开始区**与**结束区**（各约 30–50 帧），开始区要选得靠近峰（序列最前端基线其实已经趋平）→ `Set baseline and calculate`。
- 结果：会出现"前后两段斜率并非在所有 q 上一致"的警告——官方明说这通常就是如此，可以继续。校正后上漂基本消失，切回 Subtracted 图能看到橙色画出的校正线。
- 结论：线性校正适合"整体恒定斜率"的漂移；校正幅度由你选的两段参考区决定，所以参考区必须落在真正平的基线段上。

**2. `baseline.hdf5`：积分校正过校正，露在高 q**（源C 积分节 1–11）

- 问题：毛细管污垢型漂移，用 `Integral` 校正后基线的**底部反而被抬过头**。
- 做法：把强度显示切成 `Intensity in q range`，在若干 q 区间里逐个试（官方建议 0.01-0.02、0.05-0.06、0.1-0.2、0.2-0.27 Å⁻¹）→ 定位到过校正集中在高 q。
- 结论：这提示该 q 范围基本是噪声；处置是**先截断曲线到低 q 再做积分校正**。
- 附带证据：源 B 第 33 步给出另一条独立路线（峰前 + 峰后各取一段缓冲液），并说明两者取舍——若要做 EFA 分解就不要用基线校正。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 扣减完缓冲液，强度-帧号图上仍有整体上扬/下坠。
- 峰的右侧回不到基线（峰后整体抬高），低 q 出现假的抬升。
- 已经知道要校正，但不确定该选 Linear 还是 Integral。
- 校正之后高 q 变得更"怪"，想确认是不是校正过头。
- 计划做 EFA/SVD 分解，想知道还能不能同时做基线校正。

**语言信号**

- 「SEC 扣完缓冲液基线还在漂，怎么办」
- 「峰后面基线回不去零」
- 「linear 还是 integral 基线校正？」
- 「积分校正之后低 q 翘起来了 / 高 q 更糟了」
- 「我要做 EFA，能不能先做基线校正」

**与相邻 skill 的区别**

- 与 `process-sec-saxs-series`：那边负责"选哪一段是样品/缓冲液"（区间与平台判据）；本 skill 只在**扣减后仍有系统性漂移**时接手。若问题其实是缓冲液区选错（选了肩部/小峰），答案是回那边，不是校正。
- 与"多做几段缓冲液"：双缓冲液区（源 B 23–33）与本 skill 是**同一问题的两条路**，取舍写在第 4 条结论里（要分解 → 不要校正）。
- 与 `assess-guinier-fit-quality`：低 q 的假上扬会直接污染 Guinier 区；本 skill 的产出是"可被判读的曲线"，判读本身归那边。

## E — 执行步骤 (Execution)

1. **确认漂移存在且是系统性的**：在 Subtracted 图上，峰前后两段基线的水平不一样，或整条曲线呈现单调斜率。
   完成标准：能说出漂移是"直线型"还是"单调上弯型"。判停点：只是噪声起伏 → 不需要基线校正，回 `process-sec-saxs-series` 检查区间。
2. **回落缓冲液区选择**：校正的前提是**只保留主峰之前的缓冲液区**（源C 第 3 步 note）。
   完成标准：缓冲液区全部位于峰前。
3. **选方法**：直线型 → `Linear`；单调累积型（怀疑窗口污染）→ `Integral`。
   完成标准：能给出选它的理由（对应哪一类物理过程）。
4. **划参考区**：
   - Linear：在峰前、峰后各划一段"无基线变化"的平段（官方示例各约 30–50 帧）。
   - Integral：在峰前、峰后各划一段平段（官方示例约 460–480 与 860–880；Auto 给的会偏靠峰，需人工外推）。
   完成标准：两段参考区都在真正平的基线上。
5. **`Set baseline and calculate`**：出现"两段斜率/基线不一致"的警告时，**读懂它**再决定继续（Linear 的这条警告通常可忽略；Integral 的警告意味着起止点选在了仍在变化的区域，应外移）。
   完成标准：Baseline Corrected 图上漂移基本消失；Subtracted 图上能看到橙色画出的校正线。
6. **查过校正**：把强度显示切成 q 区间逐段看（试 0.01-0.02 / 0.05-0.06 / 0.1-0.2 / 0.2-0.27 Å⁻¹）。
   完成标准：能说出"是哪个 q 段被过度校正"。
   - 判停点：确认是高 q 噪声主导 → **先把曲线截断到较低 q**，再做基线校正并重新检查；不要靠调参考区硬压。
7. **重选样品区并交付**：清掉旧样品区 → `Auto` 重新找 → 目视确认平台 → `To Profiles Plot`。
   完成标准：新曲线与未校正版本的差别**能说清楚**（低 q 处应有可见差异，教程明确提示这一点）。
8. **记录与保存**：把"用了哪种校正、参考区帧号、是否截断 q"写进记录；`Save series` 会连同校正设置一起保存。
   完成标准：重开 LC 窗口时校正设置仍在（说明已随 series 保存）。

## B — 边界 (Boundary)

**不要用的场景**

- 漂移其实来自**缓冲液区选错**（含了肩部/小峰）→ 先修区间，校正只会把错误固化。
- 数据只是噪声大、没有系统性斜率 → 不需要校正。
- 打算做 **EFA/SVD/REGALS 分解**：不要叠加基线校正（源B 第 33 步 note）。此时改用峰前+峰后双缓冲液区。
- 需要判断"这条曲线的 Rg 可信吗" → 转 `assess-guinier-fit-quality`。
- **只对部分 q 做校正**（例如"只在低 q 校"）→ 会制造 q 方向折点，不做。

**源里明确警告过的失败模式**

- **积分校正的过校正**（源C 积分节第 7 步）：它只允许基线不降，所以本该向下的校正没有发生，总和被抬过头；识别点是高 q。
- **参考区没落在平坦基线上**（源C 积分节第 6 步）：RAW 会警告；警告意味着"这两点本身还在变"，此时校正没有意义。
- **把校正当成"让曲线好看"**：源C 的演示明确要求比较校正前后的差异（低 q 处本来就应有差别），说明它不是无痕操作。

**材料盲点（阶段 0 批判第 1、3 条）**

- 微信那篇（源A）**完全没有提基线校正**，所以凡涉及这一节的回答都必须注明来自官方教程——这也是本 skill 存在的直接原因。
- 官方教程给的是"两种方法 + 一个过校正现象"，**没有给"漂移多大才值得校正"的阈值**；本 skill 因此把判据写成定性的（形状与性质），不编数字。
- 引用要求：使用积分基线校正时，除 RAW 论文外还需引用 Brookes, Vachette, Rocco & Pérez, *J. Appl. Cryst.* (2016) 49, 1827-1841（DOI 10.1107/S1600576716011201）——这是源C 明确要求的。

**参考文件**：三档图（Unsubtracted / Subtracted / Baseline Corrected）、LC Analysis 面板的基线区控制、术语见
`../process-sec-saxs-series/references/sec-saxs-series-workspace.md`。

**脚本入口**：GUI 的 LC Analysis 面板与 Python API 是同一套实现。要离开界面用脚本跑（可复现、可批处理）时，用
`references/sec-saxs-baseline-api.md`（已核对 `RAWAPI.py` 源码签名的函数清单 + 四条只有读源码才看得出的约束）与
可执行脚本 `scripts/baseline_correction.py`（argparse，`--help` 里有全部默认值与单位）。

## 相关 skills

- **process-sec-saxs-series** — `depends-on`（本 skill 依赖对方）：样品/缓冲液区必须先选对，校正才有对象；第 1 步的判停会退回去。
- **assess-guinier-fit-quality** — `composes-with`（本 skill 指向对方）：校正的目的就是让低 q 可被判读，交付后由那边读 Rg/I0 与区间。

完整关系图与推荐顺序见 `books/sec-saxs-series/INDEX.md`。
