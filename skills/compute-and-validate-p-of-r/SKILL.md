---
name: compute-and-validate-p-of-r
description: "要算 P(r)/距离分布、定 Dmax、选 GNOM/DIFT/BIFT 时用：三法按下游重建程序选，Dmax 八步定法，P(r) 判据与截断规则。用于「P(r) 末端被压到零/绕零振荡」「Dmax 取多大」「用 GNOM 还是 BIFT/DIFT」「GNOM 的 .out 能不能给 DENSS/DAMMIF」「P(r) 出负值/长尾」；不覆盖 Guinier 取点（转 assess-guinier-fit-quality）与重建评估（转 evaluate-a-shape-reconstruction）。"
source_book: BioXTAS RAW 官方文档 v2.4.2 · *Indirect Fourier Transform (IFT) and the P(r) function*（30-saxs）；tutorial *s2_gnom / s2_dift / s2_bift*（40-tutorial）
source_chapter: saxs/saxs_ift.rst + tutorial/s2_gnom.rst + s2_dift.rst + s2_bift.rst
tags: [saxs, bioxtas-raw, ift, p-r, dmax, gnom, dift, bift]
related_skills:
  - slug: assess-guinier-fit-quality
    relation: depends-on
  - slug: evaluate-a-shape-reconstruction
    relation: composes-with
---

# 从 I(q) 到 P(r)：三法分工、Dmax 怎么定、结果怎么判

**P(r) 不能对 I(q) 直接做傅里叶变换**：数据的有限 q 范围加噪声会让直接变换引入截断伪影，所以必须用**间接傅里叶变换（IFT）**——反过来拟合一个 P(r)，使其正变换回 I(q) 最好地拟合实测曲线。IFT 要同时定三件东西：**Dmax、α、以及在此二者下最优的 P(r)**。RAW 给三条路线，而**选哪条要看下游用哪个重建程序，不是看哪条"更准"**。

## R — 原文 (Reading)

> a direct Fourier transform of I(q) will distort the true P(r) function by introducing truncation artifacts.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> In addition to GNOM and BIFT, RAW has another built-in method for calculating the P(r) curve called DIFT.
>
> [FILE: 40-tutorial.md · tutorial/s2_dift.rst]

> RAW has a built in method for determining the P(r) function using a Bayesian IFT method (BIFT).
> This has the advantage of only have one possible solution.
>
> [FILE: 40-tutorial.md · tutorial/s2_bift.rst]

> The most common such method is implemented in the GNOM program from the ATSAS package.
>
> [FILE: 40-tutorial.md · tutorial/s2_gnom.rst]

> Set the |Dmax value to 2-3 times larger than the initial value.
> Turn off the force to zero at |Dmax condition.
> Look for where the P(r) function drops to 0 naturally.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> If you underestimate the |Dmax|, then the P(r) function has an abrupt descent to zero
> while an overestimated |Dmax usually shows an oscillation about zero.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> As a rule of thumb, |Dmax is usually never determined to better than 5%, sometimes the uncertainty is closer to 10%.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> truncate the P(r) function to a maximum q of 8/R g, or 0.25-0.3 1/Angstrom, whichever is smaller
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> Don't truncate your P(r) function for electron density reconstructions with DENSS.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

> BIFT output from RAW is not compatible with DAMMIF or other ATSAS programs. However, it is compatible with electron density determination via DENSS.
>
> [FILE: 40-tutorial.md · tutorial/s2_bift.rst]

> The P(r) function falls gradually to zero at |Dmax|
> the χ² value of the fit, which should be close to 1
> The P(r) function goes to zero at r=0 and r=Dmax.
>
> [FILE: 30-saxs.md · saxs/saxs_ift.rst]

## I — 骨架 (Interpretation)

### 1. 为什么必须 IFT，以及要一起定的三件事

直接对 I(q) 做积分变换在数学上是"对的"，但你的数据不是 I(q) 的无穷全貌：q 有下限、有上限、还有噪声。这三者都让直接变换产生**截断伪影**，把真实的 P(r) 扭曲掉。IFT 的做法是把问题反过来：**造一个 P(r)，用它的正变换去拟合实测 I(q)**，拟合的标准既包括实际拟合优度（χ²），也包括一组**正则化项**（P(r) 的平滑度、正性、以及"改变正则化权重时解是否剧变"）。

于是 IFT 必须同时确定三样东西，它们**互相耦合**：

1. 最大尺寸 **Dmax**（决定上面积分的上限）；
2. 权重 **α**（决定 χ² 与正则化项各占多少）；
3. 在给定 Dmax、α 下最优的那个 **P(r)**。

"P(r) 好不好"从来不是某一个数对不对，而是这三件事是否自洽。

### 2. 三法分工：按下游重建程序选，不按精度选

RAW 提供三条互不依赖的 IFT 路线，它们的适用性由**产出的文件格式**和**下游程序**决定：

| 方法 | 出处 | 定 Dmax/α | 端点约束 | 输出格式 | 下游兼容 |
|---|---|---|---|---|---|
| **GNOM** | ATSAS 包（需安装） | 手动 + `Auto Dmax`；默认 `Force to 0 at Dmax`=Y | 可强制 P(0)=P(Dmax)=0（可关） | **`.out`**（GNOM 格式全文） | **所有要 GNOM `.out` 的程序**：DAMMIF/N、AMBIMETER、ATSAS 链 |
| **DIFT** | DENSS 内建（Python，无需装 DENSS） | 自动或手动选 Dmax/α；`Scan Alpha` 扫 40 个数量级 | **不可**选/取消端点强制为零（数学上已限制为零） | **`.ift`**（与 BIFT 同格式） | **DENSS**（电子密度）；**不**产生 GNOM `.out` |
| **BIFT** | RAW 原生 Bayesian | **完全自动**定 Dmax 与 α；改 q 范围后必须重按 `Run` | 自带 | **`.ift`** | **DENSS**；**不兼容** DAMMIF/其它 ATSAS（见 R 最后一段） |

**判据一句话**：要跑 **DAMMIF/N 或任何 ATSAS 珠模型链** → 走 **GNOM** 拿 `.out`；要跑 **DENSS 电子密度重建** → **BIFT 或 DIFT** 的 `.ift` 都能用（DIFT 的 `.ift` 与 BIFT 同格式）。BIFT 的卖点是**唯一解**（"only have one possible solution"）——它把 Dmax 与 α 都替你定了，代价是你不控制 Dmax、也没有 GNOM 的 "Total Estimate" 质量指标。

三个方法对**同一份好数据**给的 Dmax 会有差异但应互相吻合（官方实例见 A1），可互为 sanity check。

### 3. Dmax 八步定法：先解除约束，让数据自己说话，再恢复约束

Dmax 是 IFT 里最主观的参数，官方给出的可迁移骨架是"**先放大 → 关约束 → 找自然落零 → 回开约束 → 按需截断**"：

1. 打开界面（默认给一个 `datgnom` 算出的合理 Dmax）；
2. 起始 q 对齐 Guinier 拟合（新版本 RAW 自动；旧版本手动）；
3. **把 Dmax 设成初始值的 2–3 倍**（故意放大）；
4. 看 P(r) 在哪里**自然落到 0**，把 Dmax 设到该点；
5. **关闭 force-to-zero**；
6. 在关掉约束的条件下上下微调 Dmax，直到 P(r) 自然趋零（此时不看被强制的假像）；
7. **重新打开 force-to-zero**；
8. 若给 DAMMIF/N 用，再截断 q（见第 5 节）；截断后可能需再微调 Dmax。

### 4. P(r) 判据：三条硬判据 + 两条常用判据

- **硬判据 ①（最重要也最主观）：P(r) 在 Dmax 处平滑渐降为零。** 大分子没有绝对锐利的边界（侧链外伸、溶液中有柔性），所以是"渐降"不是"被截断"。**逼出来的陡降 = Dmax 低估；到零后围绕零振荡 = Dmax 高估；平滑趋零 = 合适。**
- **硬判据 ②：P(r) 正变换回 I(q) 能拟合实测曲线。** 看 `χ² ≈ 1`，且归一化残差平坦、随机分布于零附近。
- **硬判据 ③：P(r) 在 r=0 与 r=Dmax 处为零。** r=0 处无电子对；超过最大尺寸也无电子对。这一条通常由 IFT 内部的约束强制。
- **常用判据 ④：Guinier 与 P(r) 给出的 Rg、I(0) 应吻合。** 对刚性体系两者应一致；**柔性/无序体系里 P(r) 的 Rg、I(0) 特征性地更大且更可靠**。不一致提示 Guinier 或 P(r) 有一处出问题。
- **常用判据 ⑤：P(r) 恒为正。** **例外**：膜蛋白被脂/去污剂包封（如 lipid nanodisc）时，脂/去污剂的电子密度低于缓冲液，会看到**负 dip**——此时恒正判据不成立。

**Dmax 的不确定度**：经验规则是 **Dmax 绝不可能优于 5%**，有时接近 **10%**；柔性体系更差。官方实例里 glucose isomerase 这种好数据，合理区间约 **99–104（5% 变化）**。辅助技巧：**增大 Dmax 会同时增大 P(r) 的 Rg 与 I(0)**，可据此判断方向。

### 5. 截断规则与".out / .ift"兼容性

- 给 **DAMMIF/N**（珠模型）的 P(r)：**截断到 max q = 8/Rg，或 0.25–0.30 1/Å，取较小者**。原因是 DAMMIF 不建模水化层与内部结构，高 q 数据会引入误差。截断后可能需再微调 Dmax。
- 给 **DENSS**（电子密度）的 P(r)：**不要截断**，DENSS 要用全 q 范围（教程里 GNOM 的 "Truncate for DAMMIF/N" 把 q_max 从 0.283 降到 0.238；那个被截断的 `.out` 不该喂给 DENSS，应改用全 q 的 `.ift` 或 `_full.out`）。

### 6. 坏 P(r) 的两类病理：靠"把 Dmax 拉远"分辨

坏 P(r) 就是两件事之一：**① 一直找不到好 Dmax**（怎么增大 Dmax，P(r) 都不平滑趋零）；**② 增大 Dmax 时 P(r) 变负**。诊断动作只有一个：**把 Dmax 延伸远超你以为正确的值**，看它落在哪一档：

- **小振荡、贴近零** → 好（图 J）。
- **持续为负** → **排斥性粒子间干涉**：Dmax 被人为压小，算得的 Rg/I(0) **偏低**。
- **保持略正、有显著长尾** → **聚集**：尾显著延长、算得的 Rg/I(0) **偏大**。

注意：**少量聚集在 P(r) 上"像柔性体系"**，不能单凭 P(r) 判因——须用 Guinier（查聚集）与 Kratky（查柔性）交叉验证。

## A1 — 案例 (Past Application)

**1. glucose isomerase 的 GNOM：Auto Dmax = 102，截断后 q_max 0.283 → 0.238**（候选 `f08`、`p3/a08`）

- 问题：要从一条扣减好的曲线得到 P(r)，并判断 Dmax。
- 做法：右击 `glucose_isomerase.dat` → **IFT (GNOM)** → 在 **80–110** 之间上下试 Dmax，观察 P(r) 是否自然趋零 → 点 `Auto Dmax` 回到自动值（应得 **102**，默认 `Force to 0 at Dmax`=Y）→ 若要给 DAMMIF/N 用，勾 **"Truncate for DAMMIF/N"**。
- 结果：勾截断后 **q_max 由 0.283 降到 0.238**（取 8/Rg 或 0.30 中较小者）；存 `glucose_isomerase.out`。DENSS 重建则相反，要用全 q 范围、不要截断。
- 结论：**Auto Dmax 只是起点**；"先放大再找自然落零"才是判断依据。

**2. 同一份数据的三个 Dmax：GNOM 102 / BIFT ~100 / DIFT 115**（候选 `f07`、`p3/a09`）

- 问题：同一份 GI 数据有三种 IFT 方法，它们给的 Dmax 该不该一致？
- 做法：DIFT——右击 → **IFT (DENSS)** → 在 **80–120** 之间试 → `Auto Dmax`（应得 **115**）；改 q 范围后要点 `Scan Alpha`（`Auto Dmax` 不受 α 影响，但 DIFT 会自动扫 α，取"能给出好拟合的最高 α"）。BIFT——右击 → **IFT (BIFT)**，Dmax 由方法自动定（**~100**，改 q 范围必须重按 `Run`）。
- 结果：文档明说 BIFT 的 ~100 与 GNOM 的结果 **in good agreement**。
- 结论：**三个数互为 sanity check**；它们落在 Dmax 的 5–10% 不确定度量级内属正常。另注：**BIFT 输出不兼容 DAMMIF/ATSAS，但兼容 DENSS**。

**3. Dmax 83 / 103 / 123 的三条 P(r)**（候选 `p2o-06`）

- 问题：怎么直观看出 Dmax 低估/高估？
- 做法：对同一蛋白（glucose isomerase）取 Dmax = 83（蓝）、103（橙）、123（绿）三条 P(r) 对比。
- 结果：**83 → P(r) 被强迫陡降；103 → 平滑趋零；123 → 到零后绕零振荡。** 由此判定 103 合适、83 低估、123 高估。
- 结论：判 Dmax 看的**不是"拟合好看"，而是末端形态**。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 要算距离分布 P(r)，或要读 Dmax / 更准的 Rg、I(0)。
- 已经在 GNOM/DIFT/BIFT 窗口里，不知道 Dmax 该填多少、`Auto Dmax` 能不能直接信。
- 拿到 P(r) 图，末端形态可疑（陡降、振荡、长尾、负值），不知道是不是数据坏了。
- 要送 3D 重建，不确定 P(r) 该不该截断、截到多少、能不能喂给 DAMMIF 或 DENSS。
- 同一份数据几个方法给了不同的 Dmax，想判断哪个可信。

**语言信号**

- 「我的 P(r) 末端掉得太陡 / 绕零振荡，是不是 Dmax 取小了/大了？」
- 「Dmax 到底取多大？」
- 「用 GNOM 还是 BIFT / DIFT？有什么区别？」
- 「GNOM 的 `.out` 能不能直接给 DENSS / DAMMIF？」
- 「P(r) 出现负值 / 一条长尾，正常吗？」
- 「给 DAMMIF 的 P(r) 要不要截断到 8/Rg？」

**与相邻 skill 的区别**

- 与 `assess-guinier-fit-quality`：那边负责**低 q 取点**、q_min·Rg/q_max·Rg 与残差形态，产出"一条可信的低 q 拟合（Rg、I(0)、q 区间）"。本 skill 的**前置**就是那条拟合（IFT 的起始 q 要对齐 Guinier）；Guinier 不合格时先退回去。
- 与 `evaluate-a-shape-reconstruction`：本 skill 只负责"**算出并验证一个 P(r)**"；P(r) 之后的珠模型/DENSS 重建、以及重建质量判据（NSD、a-score、χ²、聚类）归那边。二者的接口就是这里的 `.out` / `.ift`。
- 与 `correct-sec-saxs-baseline`：坏 buffer 扣减会让 Guinier 与 P(r) 同时出问题；若症状起源是基线漂移，先修基线。

## E — 执行步骤 (Execution)

1. **确认输入合法**：一条**扣减过**的好曲线，且已有一次可信的 Guinier（有 q 区间与 Rg）。
   完成标准：能说出这条曲线来自哪次扣减、Guinier 的 q 区间。
   - 判停点：Guinier 不合格（残差 smile/frown、排除 >3–5 个低 q 点）→ **停止**，先回 `assess-guinier-fit-quality`；坏拟合上的 P(r) 没有意义。
2. **按下游程序选方法**：要 DAMMIF/N 或 ATSAS 链 → **GNOM**（出 `.out`）；要 DENSS 电子密度 → **BIFT 或 DIFT**（出 `.ift`）。
   完成标准：能说出选它的理由对应哪个下游格式。
3. **打开 IFT 面板**：Profiles 列表里右击该曲线 → 选 `IFT (GNOM)`（需装 ATSAS；菜单里没有就去 Options→Advanced Options 的 ATSAS 设置里手动指路）/ `IFT (DENSS)`（DIFT）/ `IFT (BIFT)`。
   完成标准：右侧出现 P(r)（上）、数据与拟合线（中）、拟合残差（下）三个面板。
4. **起始 q 对齐 Guinier**：新版本 RAW 自动对齐；旧版本需手动把 P(r) 的起始 q 设成与 Guinier 拟合一致。
   完成标准：IFT 的 q 范围与 Guinier 的 q 区间自洽。
5. **放大 Dmax**：把 Dmax 设成初始值的 **2–3 倍**。
   完成标准：P(r) 长尾被完全展开，末端明显落在零附近或穿过零。
6. **关 force-to-zero 找自然落零**：关闭 `force to zero at Dmax`，看 P(r) 在哪里自然落到 0，把 Dmax 设到该点；再上下微调直到自然趋零。
   完成标准：末端**平滑渐降**趋零（不是陡降、不是振荡）。
   - 判停点：怎么调都不平滑、或一直为负/一直略正 → 进第 9 步（坏 P(r) 病理）。
7. **重开 force-to-zero**，查判据：χ² ≈ 1（残差平坦随机）；P(0)=P(Dmax)=0；Guinier 与 P(r) 的 Rg、I(0) 吻合（刚性体系）；P(r) 恒正（膜蛋白/纳米盘例外）；GNOM 另看 `Total Estimate`（0–1，1 理想，至少 "REASONABLE"）。残差系统性偏差大时，可把 **α 设为自动值的一半**再调。
   完成标准：五条判据逐条说清；DIFT 无 "Total Estimate"、且不可关端点强制，别套用 GNOM 的这两项。
8. **按下游决定截断**：给 DAMMIF/N → 截断到 **8/Rg 或 0.25–0.30 1/Å（取小者）**，截断后可能再微调 Dmax；给 DENSS → **不截断**。
   完成标准：能说出"给谁用、截没截、截到多少"。
9. **判停与报告**：P(r) 是坏的吗？把 Dmax 延伸远超"以为正确"的值——持续为负 = 排斥（Rg/I(0) 偏低）；略正长尾 = 聚集（Rg/I(0) 偏大）；小振荡贴零 = 好。
   - 好 → 报告：**Dmax ±（≥5%，有时 ~10% 的不确定度）、χ²、Rg/I0 与 Guinier 的一致性、q 区间、所用 IFT 方法**。
   - 坏 → 明确说**不可用于重建**，并交叉验证（Guinier 查聚集、Kratky 查柔性），必要时重采数据。
   完成标准：结论不以一个裸 Dmax 数字收尾，必须带不确定度与适用性说明。

## B — 边界 (Boundary)

**不要用的场景**

- **对 I(q) 直接做傅里叶变换**求 P(r)：数学上诱人，但有限 q 范围与噪声会引入截断伪影——要的是 IFT。
- 拿**未扣减**或坏拟合的曲线做 IFT：P(r) 判据全部建立在好数据上，先回 `assess-guinier-fit-quality` 或还原流水线。
- 想用 P(r) 判**绝对分子量**：本 skill 只给 Dmax、以及更可靠的 Rg/I(0)；分子量走 MW 方法（本卷另有 skill）。
- 要把 P(r) 之后的**重建质量**判定（NSD、a-score、χ²、聚类、体积估 MW）放在这里：归 `evaluate-a-shape-reconstruction`。
- 给 **DENSS** 的 P(r) 做 DAMMIF 式截断：错，DENSS 要全 q。

**源里明确警告过的失败模式**

- **把 `Auto Dmax` 当结论**：自动值只是起点；实测要把 Dmax 放大 2–3 倍、关 force-to-zero 看自然落零。
- **误读末端形态**：陡降 = Dmax 低估；绕零振荡 = 高估——两者都提示你没找到自然趋零点。
- **忽视不确定度**：Dmax 绝不可能优于 **5%**，柔性体系接近 **10%**；报一个精确到个位的 Dmax 是虚假精度。
- **BIFT/DIFT 的 `.ift` 丢给 DAMMIF/ATSAS**：读不了；要 ATSAS 链就先经 GNOM 生成 `.out`。
- **把"P(r) 好看"当作数据没问题的证据**：少量聚集在 P(r) 上**像柔性**；P(r) 判据不满足通常意味着数据有聚集或粒子间干涉。

**材料盲点与证据分级（阶段 0 批判）**

- 本 skill 依据 **B 级**来源（tutorial / 30-saxs）；**A 级 `20-manual` 不作依据**（全 19 节自承落后数个版本，且在 MW 方法数、序列格式等处与 tutorial 冲突——本仓库一律以 tutorial/30-saxs 为准）。
- `30-saxs` 自承行为随版本漂移（"newer versions of RAW do this automatically" 指起始 q 对齐）；相关 skill 因此**绑定 RAW v2.4.2**并给出"不一致时怎么核对"。
- 官方把 Dmax 判据写给"mostly rigid globular macromolecule"（如 glucose isomerase）；柔性与多分散体系上，Dmax 定义本身更差，本 skill 的数值不确定度只增不减。

**术语**：IFT / Dmax / P(r) / α / Total Estimate / q_min·Rg 等不通过字典义理解的，见
`../configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md`。
三法对照、八步、判据、截断/兼容性矩阵与两类坏 P(r) 病理展开见
`references/ift-methods-and-dmax.md`。

## 相关 skills

- **assess-guinier-fit-quality** — `depends-on`（本 skill 依赖对方）：IFT 的起始 q 要对齐 Guinier，且 P(r) 的 Rg/I(0) 要与其自洽；第 1 步的判停直接退回那边。
- **evaluate-a-shape-reconstruction** — `composes-with`（本 skill 指向对方）：本 skill 交出的 `.out`/`.ift` 是重建的输入，重建质量判定归那边。

完整关系图与推荐顺序见 `books/bioxtas-raw-official-docs/INDEX.md`（若尚未生成，见 `BOOK_OVERVIEW.md` §4.1）。
