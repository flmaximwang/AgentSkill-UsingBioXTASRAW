---
name: assess-guinier-fit-quality
description: "从一条扣减过的 SAXS 曲线读 Rg/I0，并判断这次 Guinier 拟合信不信得过：n_min 低 q 取点、q_min·Rg < 0.65 下界、残差形态（smile=聚集 / frown=排斥）、按形状分档的 q_max·Rg 上界（棒≈1.0 / 球≈1.3 / 盘≈1.7），Rg 必须连 q 区间一起报；含 Kratky 交叉验证（坏 buffer 扣减会伪装有柔性）。仅适用于球状单分散粒子；不覆盖 IFT/GNOM、分子量测定与形状重建。"
source_book: 《BioXTAS RAW程序使用说明》· 刘广峰（公众号「生物小角」）· 2024-04-26；BioXTAS RAW 官方文档 v2.4.2 · saxs/saxs_guinier.rst + tutorial/s1_guinier.rst / s1_kratky.rst（扩写源）
source_chapter: §5 吉尼尔分析（①–④）+ saxs_guinier 四条判据 & Kratky 交叉验证
tags: [saxs, bioxtas-raw, guinier, rg, quality-control, kratky]
related_skills:
  - slug: reduce-saxs-frames-to-curves
    relation: depends-on
  - slug: configure-bioxtas-raw-for-a-dataset
    relation: composes-with
  - slug: compute-and-validate-p-of-r
    relation: composes-with
---

# 这个 Rg 值信不信得过（Guinier 拟合的取点与判读）

Guinier 分析的全部内容是**在小 q 区画一条直线**，而它成立有前提（q·Rg 足够小）。RAW 打开窗口时会自动选一段"最佳区域"——那是个起点，不是结论。这个 skill 教的是：把几个旋钮（取点下界、取点上界、残差、低 q 点的取舍）调到能自证，然后用 **Kratky 交叉验证**排除"坏扣减伪装柔性"，最后**带着区间报数字**。

## R — 原文 (Reading)

> ①、在 RAW 中，在 Profiles 列表中的扣减过的lyz2散射文件上单击鼠标右键并选择"Guinier fit"。 Guinier 拟合窗口将打开。
>
> 出处：§5 第①步

> 注意：第一次打开 Guinier 窗口时，RAW 会自动尝试找到最佳的 Guinier 区域。
>
> 出处：§5 第②步注意

> ③、在"控制"面板中，可以看到 n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。可以看到最低的 q 值略有下降，这可能是它被跳过的原因。使用 n_min 框旁边的箭头按钮将其向下调整几个点并检查 Rg 是否发生变化。完成后，将 n_min 返回到 8。
>
> 出处：§5 第③步

> ④、在"参数"面板中，请注意 q_max*Rg 为 ~1.27。回想一下，对于像 lyz 这样的球状蛋白质，q_max*Rg 通常约为 1.3。稍微调整 n_max，观察 Rg和残差的变化。
>
> 出处：§5 第④步

> 注意：Rg 值的单位为 1/q（例如，如果 q 的单位为 Å-1，则Rg 的单位为 Å）。
>
> 出处：§5 第②步注意

> The minimum q of your fit, q min, times the Rg of your fit should be less than 0.65.
> For globular particles (sphere- or disk-like), you can get away with q_{min}R_g<1.0.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> the rod only agrees with the Guinier approximation until qR_g ~ 1.0, the sphere until qR_g ~ 1.3, and the disc until qR_g ~ 1.7.
> These values were chosen to have <10% error resulting from the deviation of actual shape from the Guinier approximation.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> If your residuals have a 'smile' (above zero near start and end of fit, below in the middle) … it indicates you have non-ideal data.
> The 'smile' is characteristic of aggregation, the 'frown' characteristic of interparticle repulsion.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> Having to exclude more than 3-5 points at the low *q* may indicate a problem with your data.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> Even small amounts of aggregation (<1%) can affect things like the measured maximum dimension, and three dimensional reconstructions.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> start out by fitting to a maximum qRg of 1.3. If that has a non-flat residual, reduce the fitting range to a maximum qRg of 1.0.
> If the residual becomes flat upon reducing the maximum qRg, then your particle is likely more extended than globular.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> Spin down your sample in a centrifuge at high speeds (~16000 g) for 5-10 minutes before data collection.
> Add 1-5% glycerol. … Add salt to the buffer to reduce repulsion … Change the pH of your buffer.
>
> [FILE: 30-saxs.md · saxs/saxs_guinier.rst]

> peak position should be at qR_g=\sqrt{3}\approx 1.73, while peak height should be 3/e\approx 1.1
>
> [FILE: 40-tutorial.md · tutorial/s1_kratky.rst]

> Bad buffer subtraction can also result in a Kratky plot that appears to show some degree of flexibility.
>
> [FILE: 40-tutorial.md · tutorial/s1_kratky.rst]

## I — 骨架 (Interpretation)

Guinier 近似是小 q 展开：`ln I(q) ≈ ln I(0) − q²Rg²/3`。它只在 **q·Rg 足够小**时成立，于是"拟合得好不好"不是一个软件状态，而是四件可以检查的事：

1. **取点下界 `n_min` = 我丢掉了几点低 q。** 最低的几个 q 点常常是最脏的：Beamstop 边缘、束流杂散、少量聚集（聚集在小 q 处贡献极大）。RAW 的自动选区会**替你丢掉**它们——本例丢了 11 个点。丢掉本身没问题，问题是"你知不知道你丢了什么"。下调 n_min 看 Rg 是否随之变化，就是在探测"低 q 到底脏到什么程度"。
   - **下界硬判据 `q_min·Rg < 0.65`**：拟合的最低声 q（`q_min`）乘以拟合的 Rg 应 **小于 0.65**，这保证你有足够的 q 范围算准 Rg/I(0)；**球/盘状（sphere- or disk-like globular）可放宽到 < 1.0**。阈值与体系大小绑定——体系越大，最低 q 越难达到，可能得**专门去找能测到足够低 q 的线站**。
2. **残差图 = 直线假设成不成立的直接证据。** 看的是形态：残差若有系统性弯曲（U 形、单调漂移），说明该区间内曲线不是一条直线——此时 Rg 是"被拟合出来的"而不是"被读出来的"。残差是比任何 R² 更可控的判据，因为它把偏差放在 q 轴上给你看。
   - **形态归因**：**smile（两端高于零、中间低于零）= 聚集**；**frown（两端低于零、中间高于零）= 粒子间排斥**（多由静电引起，可加盐/降浓度/改 pH 补救）。
   - **易混点**：**坏 buffer 扣减也会在低 q 造成下沉（过扣）或上扬（欠扣），形似聚集/排斥**——不可仅凭残差判因。
3. **取点上界 `q_max·Rg` = 近似本身的有效边界，且上界随形状分档。** 官方按形状给出经验界：**盘（disc）≈ 1.7、球（sphere）≈ 1.3、棒（rod）≈ 1.0**；实操折中作两条——球状（含盘状）拟合到 **1.3**，高度延伸（棒状）只到 **1.0**。这些取值是**为使形状偏离 Guinier 近似带来的误差 < 10%**，在"近似好坏"与"可拟合点数"之间取平衡（取到 1.3 而不是更小，正是用它换更多点）。
   - **形状未知时的降档判停序列**：**先拟合到 1.3 → 若残差非平坦，把拟合范围降到 1.0 → 降到 1.0 后残差变平坦，说明粒子偏 extended（保留 1.0）；若降到 1.0 仍非平坦，则数据有聚集/排斥等问题**。
4. **拟合是否延伸到最低可用 q 点。** 只有紧邻 beamstop 的**两三点**可因统计差/仪器背景高而安全忽略；**要排除 > 3–5 个低 q 点，基本等于数据有问题**（聚集、辐射损伤、粒子间作用或缓冲液不匹配），**通常不应继续分析**，且须始终在图上展示全数据范围。数量级意识：**即使 < 1% 的聚集也会影响测得的最大尺寸与三维重建**，因此坏 Guinier 的一般建议是**重新收数据**。
   - **补救清单**（重采前可试）：固有聚集 → **~16000 g 离心 5–10 分钟**（必要时超速离心）、改用 SEC-SAXS 在线纯化、降浓度、临测前再过一次体积排阻/离子交换；辐射损伤（常表现为聚集）→ **加 1–5% 甘油**、提高流动/振荡速度、减少曝光时间或张数、加自由基清除剂（如 DTT）、衰减入射束；排斥 → **加盐**、降浓度、改 pH；坏 buffer 扣减 → **透析配匹配缓冲液**、过脱盐柱换液。

**单位这条单独记住**：Rg 的单位是 1/q。q 用 Å⁻¹ → Rg 用 Å；q 用 nm⁻¹ → Rg 用 nm。**"Rg 差了 10 倍"最常见的解释是单位，不是数据。**

判据汇总：报告一个 Rg 时，必须同时给出 **q 区间 / n_min 与 n_max / q_min·Rg 与 q_max·Rg / 单位**；缺一则该数字不可比。

### Kratky 交叉验证：是柔性，还是坏扣减？

当 Guinier 残差指向"聚集"，或你想判"这个体系有没有柔性/解折叠"时，用 **Kratky 图**（`q²I(q)` vs `q`）交叉验证：

- **无量纲 Kratky**（`(qRg)²I(q)/I(0)` vs `qRg`）对**球状折叠蛋白**的判据：**峰位应在 `qRg = √3 ≈ 1.73`、峰高应为 `3/e ≈ 1.1`**（RAW 图上画了这两条灰色参考线）。偏离这两条线（高 q 出现平台、或钟形被拉高/拉宽）是**柔性/部分解折叠**的信号。折叠完全的 GI 与溶菌酶都呈经典钟形。
- **必须先把坏扣减证伪**：**坏 buffer 扣减会让 Kratky 图"看起来有柔性"**。Kratky 柔性判读要求**极好的 buffer 扣减**。所以次序是：先确认 buffer 匹配（透析/过柱），再用 Guinier 残差（smile=聚集）与 P(r) 交叉验证，**别单凭 Kratky 下"部分解折叠"的结论**。
- 高 q 噪声大时可勾 **"Rebin profiles for plot"**（对数分箱、factor 2）——**分箱只作用于该图，不写回主窗口的曲线**。

## A1 — 操作案例 (Past Application)

**1. lyz2：自动选区跳过了前 11 个低 q 点**（§5 ①–④，候选 `p3/a02`）

- 问题：一条扣减过的溶菌酶曲线（lyz2），要读出 Rg 并说明可信度。
- 做法：在 Profiles 列表里右键该曲线 → **Guinier fit**（也可用面板底部的 **Guinier** 按钮）→ 观察自动选区给出 `n_min = 11`（即跳过了 11 个最低 q 点），并注意到"最低的 q 值略有下降"（这正是被跳过的原因）→ 用 n_min 旁的箭头**下调几个点**，看 Rg 是否变化 → 完成后把 n_min 调回 8 → 在参数面板核对 `q_max·Rg ≈ 1.27`（球状蛋白约 1.3）→ 微调 n_max，观察 Rg 与残差如何变。
- 结论：自动选区只是起点；**低 q 点的取舍会改变 Rg**，必须显式检查而不是接受默认值。
- 结果：原文演示的是**检查动作**，没有给出"调整后的 Rg 是多少"——这正是这份材料的性质：它给动作，不给判停标准（蒸馏者补上，见 E 第 9 步）。

**2. glucose isomerase：n_min=8、q_max·Rg≈1.32、文献 Rg=32.7 Å**（候选 `p3/a03`、`f04`）

- 问题：要从扣背景曲线里读出 Rg，先判断自动选区和拟合上界对不对。
- 做法：右击曲线 → **Guinier fit** → Control 面板 `n_min` 默认 **8** → 观察最低 q 点的凹陷，用箭头把 n_min 下调几点看 Rg 是否变化，之后回到 **8** → 在 Parameters 面板把 n_max 下调到 `q_max·Rg ≈ 1.3`。
- 结果：官方三个参照数——`n_min` 默认 **8**；GI 实测 `q_max·Rg ≈ 1.32`（球状蛋白典型 **~1.3**）；文献 `Rg = 32.7 Å`，用来和拟合值对比。
- 结论：**有了文献 Rg 这个锚点，"取点上界对不对"就变成可检验的事实。**

**3. Kratky：折叠完全 vs 柔性，以及坏扣减的伪装**（候选 `p3/a05`、`ce04`）

- 问题：想用 Kratky 图区分"完全折叠"与"有柔性"。
- 做法：选全部曲线 → 右击 → **Dimensionless Kratky Plot**（缺 Guinier 结果时点 **Proceed using AutoRg**）→ 在 Plot 下拉切 Dimensionless Rg / Normalized / Dimensionless Vc。
- 结果：GI 与溶菌酶都呈经典**钟形**（完全折叠），落在灰色参考线附近（峰位 `qRg=√3≈1.73`、峰高 `3/e≈1.1`）；载入的 unfolded / partially_folded 曲线偏离参考线。
- 结论：**Kratky 偏离参考线 = 柔性信号，但"坏 buffer 扣减也会让 Kratky 看似有柔性"**——所以下结论前必须先排除坏扣减，并与 Guinier、P(r) 交叉验证。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 曲线已经扣减好了，要读出 Rg / I0 写进报告或论文。
- Rg 的数值与预期（文献值、同批对照）差得离谱，怀疑单位或数据。
- 打开 Guinier 窗口后看到 n_min 是个非零的数，不确定该不该动它。
- 想知道"要报一个 Rg，需要交代哪些参数"。
- 想让别人判断自己的拟合是否可信（发图、发数字给别人看）。
- 残差不是平的（两头翘或两头塌），不知道意味着什么。
- 不知道粒子形状，纠结 `q_max·Rg` 该取 1.3 还是 1.0。
- Kratky 图上翘，想知道是不是"部分解折叠/柔性"。
- 已经排除了好几个低 q 点，想知道还能不能继续用这份数据。

**语言信号**

- 「Rg 怎么读／在哪里看？」
- 「我这个 Rg 是 X Å，文献里是 Y，正常吗？」
- 「Guinier 窗口里那个 n_min=11 是什么意思，能改吗？」
- 「q_max*Rg = 1.4 会不会太高了？」
- 「报 Rg 的时候要写区间吗？」
- 「残差两头高中间低（smile），说明什么？」
- 「不知道形状，q_max·Rg 取 1.3 还是 1.0？」
- 「我排除了 6 个低 q 点才拟合线性，可以接受吗？」
- 「Kratky 图低 q 上翘，是不是部分解折叠？」

**与相邻 skill 的区别**

- 与 `reduce-saxs-frames-to-curves`：那边负责"曲线是怎么来的"（积分/平均/扣减/落盘）。本 skill 的前提是**已经有一条扣减过的曲线**；输入不合法（没扣减、有坏帧混入）时要退回去。
- 与 `configure-bioxtas-raw-for-a-dataset`：**Rg 不对有两种来源**——配置错是"整条 q 轴系统性偏移（所有样品一起错）"，取点错是"单条曲线内 Rg 随区间跳动"。本 skill 负责后者；发现是前者时转过去。
- 与 `compute-and-validate-p-of-r`：本 skill 的输出（Rg、I(0)、q 区间）是 IFT 的输入（IFT 的起始 q 要对齐 Guinier）。**残差不干净、Rg 不稳时，先在这里解决，再去做 P(r)。**

## E — 执行步骤 (Execution)

1. **确认输入合法**：用的是**扣减过的**曲线（`S_` 前缀），不是原始曲线、也不是未扣减的平均曲线。
   完成标准：曲线来源清楚（哪一次扣减、扣的哪条缓冲液）。
   - 判停点：拿的是未扣减曲线 → **停止**，回 `reduce-saxs-frames-to-curves`；在含缓冲液背景的曲线上做 Guinier 变换没有意义。
2. **打开拟合**：在 Profiles 列表里右键该曲线 → **Guinier fit**（或面板底部 **Guinier** 按钮）。
   完成标准：窗口上方是 Guinier 图与拟合，下方是**残差图**；注意 RAW 已自动选了一段区域。
3. **第一眼看残差**（不要先看 Rg）。
   完成标准：能说出残差是否呈系统性弯曲/U 形，并**按形态归因**——smile（两端高中间低）= 聚集、frown（两端低中间高）= 排斥。
   - 判停点：明显系统性弯曲 → 自动区域不可信，进第 4 步手动调；若调完仍弯曲 → 进第 9 步的判停。先别下结论——**坏 buffer 扣减也会形似 smile/frown**。
4. **调下界 `n_min`**：用箭头逐步下移（把更多低 q 点纳入），每次看 Rg 与残差是否变化——本例的做法是 11 → 8 再回落，因为要判断"低 q 点脏不脏"。
   完成标准：能说出 Rg 对 n_min 的敏感度（几乎不变 / 单调漂移 / 剧烈跳动三种之一），并核对 **`q_min·Rg < 0.65`**（球/盘可放宽到 < 1.0）。
   - 判停点：低 q 点一纳入 Rg 就大幅变大 → 低 q 受聚集或束流杂散污染，保持跳过，并在报告里写明"低 q 段不可用"；若必须跳过很多点才能满足 q_min·Rg，说明数据缺低 q 或体系太大。
5. **调上界 `n_max`**：把 `q_max·Rg` 放到 **1.3**（球状，含盘状；本例 1.27），延伸棒状放 **1.0**，同时观察 Rg 与残差。**形状未知时先试 1.3**。
   完成标准：q_max·Rg 落在所选形状对应的界附近，且残差在该区间内形态可接受。
   - 判停点（形状未知的降档序列）：残差要求更短的区间 → 把上界降到 **1.0**；降到 1.0 后残差变平坦 → 粒子偏 **extended**，保留 1.0；降到 1.0 仍非平坦 → 数据有**聚集/排斥**问题（进第 9 步）。无论如何**优先保残差**，并在报告里说明实际用了多少。
6. **查低 q 点的排除数量**：拟合应延伸到最低可用 q；只有紧邻 beamstop 的 2–3 点可安全忽略。
   完成标准：能说出被排除的点数。
   - 判停点：**要排除 > 3–5 个低 q 点** → 等于数据有问题，**通常不应继续分析**；记住 **< 1% 的聚集已足以污染 Dmax 与三维重建**。此时不要"压着用"（见第 9 步的补救清单）。
7. **Kratky 交叉验证（判柔性 / 排坏扣减）**：右击 → **Dimensionless Kratky Plot**（缺 Guinier 结果时点 **Proceed using AutoRg**），看球状参考线（峰位 `qRg=√3≈1.73`、峰高 `3/e≈1.1`）。
   完成标准：能说出曲线是经典钟形还是偏离到高 q 平台；若像是柔性，**先证伪**——确认 buffer 匹配（透析/过柱）、看 Guinier 残差（smile=聚集）、并用 P(r) 交叉验证，**别单凭 Kratky 说"部分解折叠"**。
8. **读值**：记下 Rg（含单位）与 I0。
   完成标准：数字带单位；单位与 q 的单位制度自洽（q Å⁻¹ → Rg Å）。
9. **判停与报告**：Rg 在合理取点范围内是否稳定？
   - 稳定（区间微调下变化小）→ 报告：`Rg = X ±（区间变化量）`，附 q 区间、n_min/n_max、q_min·Rg 与 q_max·Rg、单位、以及 Kratky/残差自洽性。
   - 不稳定（随区间变化 >10–20%，本例这种量级的跳动应被视为不稳定）→ 明确告诉用户：**这条曲线不适合给单一 Rg 值**；若残差为 smile/frown 或排除了 >3–5 个低 q 点，先按补救清单处理（**~16000 g 离心 5–10 分钟**、加 **1–5% 甘油**、降浓度、改 pH、加盐、换匹配 buffer），坏 Guinier 的一般建议是**重新收数据**；进一步该做 IFT/距离分布分析（→ `compute-and-validate-p-of-r`）。
   完成标准：报告里参数齐全，且"信不信得过"有明确结论——不以一个裸数字收尾。

## B — 边界 (Boundary)

**不要用的场景**

- 曲线没有扣减过缓冲液——先走还原流水线。
- 样品明显**不是球状单分散**（IDP、多聚体、明显聚集）：`q_max·Rg ≈ 1.3` 这条经验界不成立（棒只到 1.0，盘可到 1.7），本 skill 的取点判据随之失效。原文写的是"像 lyz 这样的球状蛋白质"，**这是条件式规则，不是定律**（阶段 0 批判第 6 条）。
- 想问**绝对分子量**：那要靠标样 I0 比对、绝对校准、Vc、Vp、Shape&Size、Bayesian 等多法交叉，本文只列了名称，没有流程（rejected 组 `measure-molecular-weight-from-saxs`；正式版见本卷 MW 选择 skill）。本 skill 只给 Rg/I0。
- 想做 IFT/GNOM、形状重建、3D 重建 → 不在覆盖范围（转 `compute-and-validate-p-of-r` 与重建评估 skill）。
- **单凭 Kratky 图判柔性**：坏 buffer 扣减会让 Kratky 看似有柔性——必须先排除坏扣减，并与 Guinier、P(r) 交叉验证。
- 用户问的是"我的蛋白是不是二聚体/什么形状"——Rg 一个数回答不了这类问题。

**作者警告过的失败模式**

- **盲信自动选区**（`p4/ce02`）：自动选区不知道低 q 处的污染与"应当丢弃"在形态上相似；它会给出一个看起来干净、实际由丢弃策略决定的 Rg。头号反例。
- **只报数字不报区间**：使结论看起来比实际确定（术语 `g10`）。
- **单位混用**（术语 `g09`）：Å 与 nm 相差 10 倍，最常见的"数据看起来坏了"。
- **把 smile/frown 直接当成聚集/排斥**：**坏 buffer 扣减也形似两者**（过扣像排斥、欠扣像聚集）——先排除扣减问题再判因。
- **勉强使用坏拟合**：排除 >3–5 个低 q 点、或残差明显不干净还接着做 IFT 与重建，会把误差传进 **Dmax 与三维重建**（官方明说 <1% 聚集已足够）。

**作者盲点（阶段 0 批判第 6、7 条；官方文档扩写补充）**

- 文章把 q_max·Rg ≈ 1.3 作为通用判据陈述，只在一处提到"像 lyz 这样的球状蛋白质"；本 skill 把它还原为**条件式**规则，并补上官方文档的**形状分档（棒 1.0 / 球 1.3 / 盘 1.7）**与**下界 `q_min·Rg < 0.65`**。
- 文章开头就声明"这不是关于进行吉尼尔分析的基本原则和最佳实践的教程"——所以本 skill 覆盖的是**RAW 内的操作与判读**，不替代 SAXS 理论；原则性问题（什么时候不该做 Guinier 分析）本 skill 只能点到边界。
- **证据分级**：本 skill 的扩充判据来自 **B 级**官方文档（`30-saxs` / `40-tutorial`）；**A 级 `20-manual` 不作依据**（自承落后数个版本）。相关行为随版本漂移，**绑定 RAW v2.4.2**。

**术语**：Rg/q 单位、q_max·Rg、n_min/n_max 与残差不通过字典义理解的，见
`../configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md`（`g09`、`g10`）。
界面问题（哪个面板、哪个选项卡、`S_` 是什么意思）见
`../reduce-saxs-frames-to-curves/references/raw-workspace-and-naming.md`。
Kratky 与柔性的展开（无量纲 Kratky 推导、坏扣减的证伪次序、与 P(r) 的交叉验证）见
`references/kratky-and-flexibility.md`。

## 相关 skills

- **reduce-saxs-frames-to-curves** — `depends-on`（本 skill 依赖对方）：拟合的输入是那边产出的 `S_` 曲线；本 skill 第 1 步的判停直接退回那边。
- **configure-bioxtas-raw-for-a-dataset** — `composes-with`（本 skill 指向对方）：Rg 系统性偏移（所有样品一起错）要先排除配置问题，再谈取点问题。
- **compute-and-validate-p-of-r** — `composes-with`（本 skill 指向对方）：这里的 Rg/I(0) 与 q 区间是 IFT 的输入（IFT 起始 q 需对齐 Guinier）；Rg 不稳/残差不干净时先别去做 P(r)。

完整关系图与推荐顺序见 `books/bioxtas-raw-manual/INDEX.md`。
