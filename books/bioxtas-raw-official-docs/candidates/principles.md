# candidates/principles.md — 原则提取器（视角 2：规则 / 判据 / 阈值 / 清单）

源：BioXTAS RAW v2.4.2 官方文档（纯文本化语料：00-root / 10-install / 20-manual / 30-saxs / 40-tutorial / 50-api）
证据分级硬规则：**40-tutorial > 50-api = 30-saxs > 00-root**；`20-manual.md` 为 A 级（自承落后数个版本），本文件**不引用**。
已存在 5 个 skill（判据已被覆盖，本文件不重复）：`assess-guinier-fit-quality`、`correct-sec-saxs-baseline`、`configure-bioxtas-raw-for-a-dataset`、`process-sec-saxs-series`、`reduce-saxs-frames-to-curves`。
切片标识：`p2o`。`source_quote` 逐字抄自语料（≤150 字/条）。`landing` = `new` | `extend:<现有 skill>`。

---

```yaml
- id: p2o-01
  title: Guinier 取点下界——q_min·Rg < 0.65（球状可放宽到 1.0）
  type: principle
  source_chapter: saxs/saxs_guinier.rst《Guinier analysis》· 30-saxs.md
  source_quote: |
    "The minimum q of your fit, q\ min, times the |Rg  of your fit should be less than 0.65."
  summary: |
    Guinier 四条判据的第 1 条：拟合区间的下界不是"数据从哪开始"，而是"q_min×Rg 够不够小"。
    默认阈 0.65；球状/盘状（sphere- or disk-like globular）可放宽到 q_min·Rg < 1.0。
    适用：任何 Guinier 拟合，且阈值与体系大小绑定——体系越大，最低 q 越难达到（可能需专门找低 q 线站）。
    失效点：q_min·Rg 过大 → 拟合 q 范围不足，Rg/I(0) 不可靠。
  landing: extend:assess-guinier-fit-quality
  tags: [principle, guinier, qmin, threshold, saxs]
```

```yaml
- id: p2o-02
  title: 按形状分档的 Guinier 上界——棒 qRg≈1.0 / 球≈1.3 / 盘≈1.7
  type: principle
  source_chapter: saxs/saxs_guinier.rst《Guinier analysis》· 30-saxs.md
  source_quote: |
    "the rod only agrees with the Guinier approximation until qR_g\sim 1.0, the sphere until qR_g\sim 1.3, and the disc until qR_g\sim 1.7."
  summary: |
    q_max·Rg 上界随形状分档：盘（disc）可达 ~1.7、球（sphere）~1.3、棒（rod）只到 ~1.0。
    实操折中：球状（含盘状）拟合到 1.3，高度延伸（棒状）只到 1.0；这些取值是为使形状偏离 Guinier 近似
    带来的误差 <10%，在"近似好坏"与"可拟合点数"之间取平衡。
    例外/判据：形状未知时先拟合到 1.3，残差非平坦再降到 1.0；降到 1.0 后残差变平坦说明粒子偏 extended，
    可保留 1.0；若仍非平坦 → 数据有聚集/排斥等问题。
  landing: extend:assess-guinier-fit-quality
  tags: [principle, guinier, qmax, shape, threshold]
```

```yaml
- id: p2o-03
  title: Guinier 残差形态诊断——smile = 聚集，frown = 排斥
  type: principle
  source_chapter: saxs/saxs_guinier.rst《Guinier analysis》· 30-saxs.md
  source_quote: |
    "The ‘smile’ is characteristic of aggregation, the ‘frown’ characteristic of interparticle repulsion."
  summary: |
    好拟合的残差应平坦且随机分布于零附近。残差形态是低 q 病理的指纹：
    smile（两端高于零、中间低于零）→ 聚集（aggregation，含辐射损伤诱导的聚集）；
    frown（两端低于零、中间高于零）→ 粒子间排斥（interparticle repulsion，多由静电引起，可加盐/降浓度/改 pH 补救）。
    易混点/例外：缓冲液扣减不准也会在低 q 造成下沉（过扣）或上扬（欠扣），形似聚集/排斥，不可仅凭残差判因。
  landing: extend:assess-guinier-fit-quality
  tags: [principle, guinier, residual, aggregation, diagnostic]
```

```yaml
- id: p2o-04
  title: 排除 >3–5 个低 q 点即报警；<1% 聚集已足以毁掉 Dmax 与 3D 重建
  type: principle
  source_chapter: saxs/saxs_guinier.rst《Guinier analysis》· 30-saxs.md
  source_quote: |
    "Having to exclude more than 3-5 points at the low *q* may indicate a problem with your data."
  summary: |
    拟合必须延伸到最低可用 q；只有紧邻 beamstop 的两三点可因统计差/仪器背景高而安全忽略。
    要排除 >3–5 个低 q 点，基本等于数据有问题（聚集、辐射损伤、粒子间作用或缓冲液不匹配），
    通常不应继续分析；且须始终在图上展示全数据范围。
    数量级意识：即使 <1% 的聚集也会影响测得的最大尺寸与三维重建，因此坏 Guinier 的一般建议是重新收数据。
  landing: extend:assess-guinier-fit-quality
  tags: [principle, guinier, outlier-exclusion, threshold, aggregation]
```

```yaml
- id: p2o-05
  title: 好 P(r) 的三条硬判据 + 两条常用判据
  type: principle
  source_chapter: saxs/saxs_ift.rst《IFT and the P(r) function》· 30-saxs.md
  source_quote: |
    "The P(r) function falls gradually to zero at"
    "the \chi^2 value of the fit, which should be close to 1"
  summary: |
    硬判据：① P(r) 在 Dmax 处平滑渐降为零（最重要也最主观）；② P(r) 正变换回 I(q) 能拟合实测曲线
    （χ² 应接近 1，归一化残差平坦且随机分布于零附近）；③ P(r) 在 r=0 与 r=Dmax 处为零
    （通常由 IFT 计算中的约束强制）。常用判据：④ Guinier 与 P(r) 给出的 Rg、I(0) 应吻合良好
    （刚性体系；柔性/无序体系观察到 P(r) 的 Rg、I(0) 特征性地更大且更可靠）；
    ⑤ P(r) 恒为正——例外：膜蛋白被 lipid/detergent 包封（如 lipid nanodisc）时脂/去污剂电子密度低于缓冲液，
    会出现负 dip。判据不满足通常意味着数据有聚集或粒子间干涉，不应继续分析。
  landing: new
  tags: [principle, ift, pr-function, chi2, criteria]
```

```yaml
- id: p2o-06
  title: Dmax 的定值法（欠估→陡降，过估→振荡）与不确定度（≥5%，有时 ~10%）
  type: principle
  source_chapter: saxs/saxs_ift.rst《IFT and the P(r) function》· 30-saxs.md
  source_quote: |
    "If you underestimate the |Dmax|, then the P(r) function has an abrupt descent to zero"
    "an overestimated |Dmax usually shows an oscillation about zero."
  summary: |
    判 Dmax：P(r) 被"逼"陡降 = Dmax 低估；到零后围绕零振荡 = 高估；平滑趋零 = 合适。
    GNOM 流程：先设初始值的 2–3 倍 → 观察 P(r) 自然落零处并设到该点 → 关 "force to zero at Dmax" 上下微调
    → 再打开该条件（若用于 DAMMIF/N 再截断，见 p2o-07）。
    不确定度：经验规则是 Dmax 通常绝不可能优于 5%，有时不确定度接近 10%；即使葡萄糖异构酶这种好数据，
    合理区间也约 ~99–104（5% 变化），柔性体系更差。辅助：增大 Dmax 会同时增大 P(r) 的 Rg 与 I(0)。
  landing: new
  tags: [principle, ift, dmax, gnom, uncertainty]
```

```yaml
- id: p2o-07
  title: DAMMIF/N 输入的 P(r) 须截断到 max q = 8/Rg 或 0.25–0.30 1/Å（取小者）；DENSS 不截断
  type: principle
  source_chapter: saxs/saxs_ift.rst + saxs/saxs_bead_models.rst · 30-saxs.md
  source_quote: |
    "truncate the P(r) function to a maximum q of 8/R\ g, or 0.25-0.3 1/Angstrom, whichever is smaller"
  summary: |
    珠模型（DAMMIF/N）重建用的 P(r)，须把数据截断到最大 q = 8/Rg 或 0.25–0.30 1/Å，取较小者；
    原因：DAMMIF 不建模水化层与内部结构，高 q 数据会引入误差。截断后可能需再微调 Dmax。
    对照/例外：用 DENSS 做电子密度重建时不要截断 P(r)（DENSS 要用全 q 范围；教程实例中 GNOM 的
    "Truncate for DAMMIF/N" 把 q_max 从 0.283 降到 0.238）。
  landing: new
  tags: [principle, ift, bead-model, truncation, dammif, denss]
```

```yaml
- id: p2o-08
  title: P(r) 坏数据的两类病理：聚集 vs 粒子间干涉，靠"把 Dmax 拉远"分辨
  type: principle
  source_chapter: saxs/saxs_ift.rst《IFT and the P(r) function》· 30-saxs.md
  source_quote: |
    "a significantly extended tail on the P(r) distribution, which does not fall to zero naturally regardless of the chosen |Dmax|."
  summary: |
    坏 P(r) 有两类：① 找不到好 Dmax（一直增大却不平滑趋零）；② 增大 Dmax 时 P(r) 变负。
    诊断动作：把 Dmax 延伸远超"以为正确"的值——靠近零的小振荡 = 好；持续为负 = 排斥性粒子间干涉
    （Dmax 被人为压小、算得的 Rg/I(0) 偏低）；保持略正 = 聚集（尾显著延长、算得的 Rg/I(0) 偏大）。
    辅助交叉验证：轻聚集可能形似柔性体系，须用 Guinier（查聚集）与 Kratky（查柔性）判断真实状态。
  landing: new
  tags: [principle, ift, pr-function, dmax, diagnostic]
```

```yaml
- id: p2o-09
  title: MW 通则——~10% 不确定度；不应用 SAXS 定分子量（用 MALS）；分浓度依赖/无关两类
  type: principle
  source_chapter: saxs/saxs_mw.rst《Molecular weight calculation》· 30-saxs.md
  source_quote: |
    "a usual rule of thumb is ~10% uncertainty (or more). For this reasons, SAXS should not be used to determine the molecular weight of your sample"
  summary: |
    通则：SAXS 测 MW 通常 ~10% 不确定度（或更大），因此不应用 SAXS 定分子量——精度更好的选择是 MALS。
    SAXS 算 MW 的主要用途是判断低聚态（homodimer 及更高阶）。
    分类：concentration dependent（需知道池中浓度，常与 SEC-SAXS 不兼容）vs concentration independent
    （不需浓度，适用于 SEC-SAXS）。前提：所有方法都需好的 I(0)；所有浓度无关方法都需 Rg，一般即需好的 Guinier 拟合。
  landing: new
  tags: [principle, molecular-weight, uncertainty, mals, sec-saxs]
```

```yaml
- id: p2o-10
  title: 各 MW 方法的不确定度（绝对<~10%、Porod 12%、Vc ~5–10%、Shape&Size 90%、Bayesian 4%）
  type: principle
  source_chapter: saxs/saxs_mw.rst《Molecular weight calculation》· 30-saxs.md
  source_quote: |
    "In [2] they found a median uncertain of 12% for calculated molecular weight from globular proteins."
  summary: |
    分法不确定度（[n] 为文档参考文献）：绝对标定 I(0)[1] <~10%（多数蛋白）。
    Porod volume/SAXSMoW 2[2]：球状蛋白中位不确定度 12%；[5] 模拟得中位值偏高 3%、中位绝对偏差 5%，有噪声时更高，总体约 ~10%。
    Volume of correlation[3]：理论曲线 ~5%、实验曲线 ~10%；[5] 模拟中位值偏低 2%、中位绝对偏差 7%。
    与已知结构比较（Shape&Size）[4]：[4] 中 90% 测试数据在预期值 10% 内；[5] 中位值正确、中位绝对偏差 4%。
    Bayesian[5]：中位值准确、中位绝对偏差 4%，比任一单独方法更准，不确定度可能更接近 ~5%。
  landing: new
  tags: [principle, molecular-weight, uncertainty, porod, volume-of-correlation]
```

```yaml
- id: p2o-11
  title: Volume of correlation 的常数与小分子/复合物失效点
  type: principle
  source_chapter: saxs/saxs_mw.rst《Molecular weight calculation》· 30-saxs.md
  source_quote: |
    "For proteins, c=0.1231 and k=1 while for RNA c=0.00934 and k=0.808"
  summary: |
    经验常数：蛋白 c=0.1231、k=1；RNA c=0.00934、k=0.808（原文注：c、k 在原论文中定义略有不同）。
    前提：qI(q) 的积分必须收敛（高 q 处积分值不再上升）；否则 MW 不准。
    失效点：经验系数取自 ≥20 kDa 的尺寸范围，<~15–20 kDa 时不确定度大；对蛋白-核酸复合物不适用；
    对高信噪比数据不如他法；对延伸分子不如 Porod volume 法。
  landing: new
  tags: [principle, molecular-weight, vc, constants, limits]
```

```yaml
- id: p2o-12
  title: Porod volume 法的默认蛋白密度 0.83 kDa/Å³ 与失效点
  type: principle
  source_chapter: saxs/saxs_mw.rst《Molecular weight calculation》· 30-saxs.md
  source_quote: |
    "May need to have the protein density adjusted in some cases (default: 0.83 kDa/\ 3)"
  summary: |
    Porod volume（SAXSMoW 2）法默认蛋白密度 0.83 kDa/Å³，必要时可调整该密度提高精度
    （对已知更准确密度的体系）。
    失效点：对柔性/延伸分子应表现不佳（[5] 发现并不总是如此）；样品非蛋白时失败；对扣减误差敏感。
    优点：对多数分子形状准确，且信噪比合理时比 volume of correlation 更准。
  landing: new
  tags: [principle, molecular-weight, porod, density, protein]
```

```yaml
- id: p2o-13
  title: 好珠模型重建的七条判据清单
  type: principle
  source_chapter: saxs/saxs_bead_models.rst《Bead model reconstructions》· 30-saxs.md
  source_quote: |
    "Ambiguity score < 2.5 (preferably < 1.5)"
    "NSD < 1.0"
    "Model \chi^2 near 1.0 for all models"
  summary: |
    七条"好重建"判据：① Ambiguity score < 2.5（最好 < 1.5）；② NSD < 1.0；
    ③ 被平均剔除的模型很少（0–2 个）；④ 只有一个模型聚类；⑤ 所有模型 χ² 接近 1.0；
    ⑥ 所有模型 Rg 与 Dmax 接近 P(r) 给出的值（高质量数据经验：Rg 吻合到 ~5% 以内、Dmax ~10% 以内）；
    ⑦ 由模型体积估算的 MW 接近预期。判据不齐不得使用该重建。
  landing: new
  tags: [principle, bead-model, checklist, nsd, chi2]
```

```yaml
- id: p2o-14
  title: AMBIMETER 歧义度（a-score）分档：<1.5 / 1.5–2.5 / >2.5
  type: principle
  source_chapter: tutorial/s2_ambimeter.rst · 40-tutorial.md（同 30-saxs 措辞）
  source_quote: |
    "Ambiguity score < 1.5 - Reconstruction is likely unique"
    "Ambiguity score of 1.5-2.5 - Take care when doing the reconstruction"
  summary: |
    a-score = 匹配形状类别数的 log₁₀（在 GNOM 的 P(r) 上运行，数据库含最多 7 个 bead 的所有形状）。
    分档：<1.5 → 重建很可能唯一；1.5–2.5 → 需谨慎（或做簇分析）；>2.5 → 重建很可能是歧义的。
    判据用途：重建前先评估是否值得做形状重建；AMBIMETER 也可在 RAW 内运行。
  landing: new
  tags: [principle, bead-model, ambimeter, ambiguity, threshold]
```

```yaml
- id: p2o-15
  title: NSD 分档与 2σ 剔除规则（>~2/15 被剔除即不稳定）
  type: principle
  source_chapter: saxs/saxs_bead_models.rst《Bead model reconstructions》· 30-saxs.md
  source_quote: |
    "If the average NSD of a given model is more than two standard deviations above the overall average NSD, that model is not included in the average."
  summary: |
    平均 NSD 判稳定性：<0.6 好；0.6–1.0 一般（fair）；>1.0 差（poor，应谨慎或不用）。一般 <1.0 且其它指标也达标才可信任。
    剔除规则：某模型平均 NSD 比总体平均 NSD 高出 2 个标准差以上则不入平均；若 15 个中被剔除 >~2 个，
    可能是重建不稳定的信号。
    相关例外：数据极好时（AMBIMETER 歧义度 <0.5、平均 NSD <0.5、NSD 标准差 ~0.01），DAMCLUST 可能误报多（常 >5）个聚类；
    不同 cluster 也不能当作溶液中不同形状的代表。
  landing: new
  tags: [principle, bead-model, nsd, outlier, stability]
```

```yaml
- id: p2o-16
  title: 珠模型体积推 MW——除以常数 1.66（随形状 1.5–2.0）；差 >20–25% 即可疑
  type: principle
  source_chapter: saxs/saxs_bead_models.rst《Bead model reconstructions》· 30-saxs.md
  source_quote: |
    "M.W. is calculated by dividing the volume (nominally representing the sample's excluded volume) by an empirically determined constant [4] of 1.66"
  summary: |
    由模型体积估 MW：M.W. = volume / 1.66（RAW 所用经验常数；其它程序可能不同）。
    该常数随形状在 ~1.5–2.0 之间变化，故此 MW 比其它 SAXS MW 方法更不确定，只宜用于"总体尺寸是否大致相符"的判断。
    判据：若 MW 与预期相差 >20–25%，应视该重建可疑。
  landing: new
  tags: [principle, bead-model, molecular-weight, constant, threshold]
```

```yaml
- id: p2o-17
  title: 重建数 10–20（推荐 15）、Slow 用于最终、对称/各向异性须做对照，分辨率 ≳20 Å
  type: principle
  source_chapter: saxs/saxs_bead_models.rst《Bead model reconstructions》· 30-saxs.md
  source_quote: |
    "we create 10-20 bead model reconstructions and then average them. I recommend 15 reconstructions."
  summary: |
    生成 10–20 个重建再平均，推荐 15 个。Mode：Fast 快但细节少，Slow 反之；最终重建用 Slow。
    Symmetry / Anisometry：已知时可指定，但始终建议各再做一组 P1 / 无 anisometry 的重建以验证约束未过度。
    只想快速看形状（如束线收数据）时：Fast 模式做 3 个即可。
    局限与失效点：分辨率很少优于 ~20 Å（常更大）；对高长径比（长棒/薄盘）、有空隙（球壳）、环状物体不可靠，
    最可靠的是近球状；对较大粒子/聚集极敏感（0.7% 聚集即显著改变模型）；高质量数据不保证好重建。
  landing: new
  tags: [principle, bead-model, reconstruction-count, limitations]
```

```yaml
- id: p2o-18
  title: SVD/EFA 显著性判据——自相关 >0.6–0.7 为显著分量
  type: principle
  source_chapter: tutorial/s2_svd.rst + tutorial/s2_efa.rst · 40-tutorial.md
  source_quote: |
    "Vectors corresponding to significant components will tend to have autocorrelations near 1 (roughly, >0.6-0.7)"
  summary: |
    判峰内组分数：奇异值须"相对"于高序号奇异值的平坦基线看，而非绝对值；显著分量的（左右）奇异向量自相关约 >0.6–0.7
    （接近 1），不显著分量接近 0。SVD 是 EFA 的第一步（EFA 窗口内自动完成）。
    注意：Unsubtracted↔Subtracted 切换通常应去掉一个对应缓冲液散射的显著分量；若数据本就已扣背景则无差别。
  landing: new
  tags: [principle, svd, efa, autocorrelation, threshold]
```

```yaml
- id: p2o-19
  title: EFA 结果的三步复核（χ²≈1、正性约束不改变浓度、终解不沿用前次结果）
  type: principle
  source_chapter: tutorial/s2_efa.rst · 40-tutorial.md
  source_quote: |
    "Examine the chi-squared plot. It should be uniformly close to 1 for good EFA."
  summary: |
    EFA 每次做完须走三步复核：① 所选分量范围对应 Forward/Backward EFA 的起点；② χ² 图应均匀接近 1、无大尖峰；
    ③ 取消集中浓度 C>=0（正性）约束后浓度峰不应显著变化——若显著变化则 EFA 差、不可信。
    另：用 "Start with previous results" 会引入路径依赖偏差，最终一次运行必须关掉该选项以保证可复现。
    浓度峰高度本身是任意的（均归一化到面积 1）。
  landing: new
  tags: [principle, efa, deconvolution, chi2, verification]
```

```yaml
- id: p2o-20
  title: REGALS 的 lambda 按数量级调；λ 之坏由 χ² 偏离 ~1 暴露
  type: principle
  source_chapter: tutorial/s2_regals.rst · 40-tutorial.md
  source_quote: |
    "Generally you want to adjust lambda by an order of magnitude or more. Smaller adjustments will have minimal effect on the deconvolution."
  summary: |
    lambda 控制平滑度：调整应按 ≥1 个数量级（更小的调整对解卷积几乎无效）；强分量/测量点多的分量 λ 可小（甚至 0），
    缓冲分量的 λ 需增大使其浓度更平滑（示例最优 ~4e8）。
    过平滑信号：各分量高 q 背景趋于一致 + 某分量散射曲线突然大幅变化 → 回到上一个"好的" λ。
    λ 设得特别差时 χ² 图会偏离 ~1；χ² 仍接近 1 说明 λ 大概率没问题。REGALS 不自动重算，改设置后必须手动 Run。
  landing: new
  tags: [principle, regals, deconvolution, lambda, chi2]
```

```yaml
- id: p2o-21
  title: 最大可测尺寸的 Shannon 限——Dmax < π/q_min
  type: principle
  source_chapter: tutorial/s2_regals.rst · 40-tutorial.md
  source_quote: |
    "the largest dimension of an object that can be measured is ~300 Å, based on the Shannon limit of D_{max}<\pi/q_{min}."
  summary: |
    给定数据的 q_min，能测的最大尺寸受 Shannon 限约束：Dmax < π/q_min。
    用途：为无从先验知识的对象（如聚集体）选一个合理的 Dmax 上界；教程数据由此把聚集体分量 Dmax 设为 ~300 Å。
    相关判据（同节）：两构象 Dmax 在 ~130–150 时 χ² 稳定、~120 以上 P(r) 不再被逼零、160 时 χ² 明显上升 → 取 ~130。
  landing: new
  tags: [principle, regals, dmax, shannon, qmin]
```

```yaml
- id: p2o-22
  title: 绝对刻度的顺序约束——先关绝对刻度再算常数，算完不得再改归一化
  type: principle
  source_chapter: tutorial/s3_abscarbon.rst + tutorial/s3_abswater.rst · 40-tutorial.md
  source_quote: |
    "It is important that you not change your normalization settings once you have set the absolute scaling constant."
  summary: |
    两条顺序约束（违反 → 常数错误，需重算）：① 算绝对刻度常数前必须关掉绝对刻度，否则得到坏常数；
    ② 一旦设好绝对刻度常数，就不得再改动归一化设置（包括通量/透射等），否则必须重算该常数。
    NIST Full 玻碳法额外前提：所有归一化（含通量、透射）都经由 Absolute Scale 面板完成，
    Normalization 面板应清空（除非做常数 pedestal 扣除）。
    方法选择：玻碳比水更准（有则优先）；示例中玻碳的 Simple（厚度 1.0 mm，常数约 324）与
    NIST Full（厚度 1.5 mm，上下游 I1/I3，常数 ~198）两种方法在示例数据上一致到 ~1.5%；水法常数应近 0.00077（4 °C）。
  landing: new
  tags: [principle, absolute-scale, normalization, order, calibration]
```

---

## 备注（提取纪律）

- 22 条全部有逐字 `source_quote` 可回溯（grep 归一化空白后可在语料命中）；未引用 `20-manual.md`。
- 5 个已有 skill 覆盖的判据（n_min 取点、q_max·Rg≈1.3、Rg 单位、A_/S_/* 状态、buffer/sample 区选择、Linear/Integral 选择、过校正识别）
  未重复提取；仅在 Guinier 判据上做**扩展**（p2o-01…04 → `extend:assess-guinier-fit-quality`）。
- 建议新建：`assess-ift-pr-dmax`（p2o-05…08）、`compare-mw-methods`（p2o-09…12）、
  `evaluate-bead-model-reconstruction`（p2o-13…17）、`validate-deconvolution-components`（p2o-18…21）、
  `set-absolute-scale-in-order`（p2o-22）。
