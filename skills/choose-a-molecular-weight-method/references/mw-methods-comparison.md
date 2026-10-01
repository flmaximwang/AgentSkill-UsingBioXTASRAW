# 分子量六法对照表（reference）

源：BioXTAS RAW v2.4.2 官方文档 · `saxs/saxs_mw.rst`（方法学，30-saxs）与 `tutorial/s1_mw.rst`（操作，40-tutorial）。
本文件供 `choose-a-molecular-weight-method` 引用；是**参考**（查表与核对），不单独成 skill。
所有不确定度与常数逐字取自上述两节；方括号 `[n]` 为文档原文的参考文献编号（见文末）。

> 版本警告：面板名与控件随 RAW 版本变化；数字与公式以 v2.4.2 为准。

---

## 一、两轴定位表

| # | 方法（RAW 面板名） | 来源 | 浓度依赖? | 适用 SEC-SAXS? | 一句话定位 |
|---|---|---|---|---|---|
| 1 | 绝对标定 I(0)（Abs. MW） | RAW 原生 | **是** | ✗ | 需已知浓度 + 绝对刻度；参数全知时可高度准确 |
| 2 | 参比标准品（I(0) Ref. MW） | RAW 原生 | **是** | ✗ | 用已知标样标定；要求标样同对比度、同形状 |
| 3 | Porod 体积（Vp，SAXSMoW 2） | RAW 原生 | 否 | ✓ | 由 Porod 不变量算排除体积 × 密度 |
| 4 | 相关体积（Vc，Rambo–Tainer） | RAW 原生 | 否 | ✓ | 由 Vc²/Rg 的对数关系；含经验常数 c、k |
| 5 | 与已知结构比对（Shape&Size，ATSAS datclass） | ATSAS | 否 | ✓ | 机器学习按形状/尺寸从 PDB 目录找最近结构 |
| 6 | Bayesian 推断（ATSAS datmw bayes） | ATSAS | 否 | ✓ | 以 3/4/5 为证据做概率合成；通常最准 |

- 装 ATSAS 前只有 4 个面板；装后 6 个（缺最右一列即未装）。
- **未填浓度时，方法 1 与方法 2 不报 MW**（原文 note："Neither the I(0) Ref. MW panel nor the Abs. MW panel should be reporting a MW."）。

## 二、公式与常数

| 量 | 公式 / 值 | 出处 |
|---|---|---|
| 绝对标定 I(0) | MW = N_A·I(0) / (c·Δρ²_M) | saxs/saxs_mw.rst |
| 参比标准品 | MW_m = (I(0)_m / c_m) · [ MM_st / (I(0)_st / c_st) ] | saxs/saxs_mw.rst |
| Porod 不变量 | Q_p = ∫₀^∞ q²I(q) dq | saxs/saxs_mw.rst |
| Porod 体积 | V_p = 2π²I(0) / Q_p → ×密度 | saxs/saxs_mw.rst |
| Porod 默认蛋白密度 | **0.83 kDa/Å³** | saxs/saxs_mw.rst |
| 相关体积 | V_c = I(0) / ∫₀^∞ qI(q) dq | saxs/saxs_mw.rst |
| Vc → MW | MW = ( (V_c²/Rg) / c )^k | saxs/saxs_mw.rst |
| Vc 常数·蛋白 | **c = 0.1231，k = 1** | saxs/saxs_mw.rst |
| Vc 常数·RNA | **c = 0.00934，k = 0.808** | saxs/saxs_mw.rst |
| 珠模型体积估 MW（对照用） | M.W. = volume / 1.66（随形状 1.5–2.0） | saxs/saxs_bead_models.rst |

> 原文注：Vc 的 c、k 在原论文中定义略有不同。

## 三、不确定度汇总（逐字数值）

| 方法 | 文档给的不确定度 | 出处 |
|---|---|---|
| 绝对标定 I(0) | `[1]` 中 <~10%（多数蛋白） | saxs/saxs_mw.rst |
| 参比标准品 | 无数字；"Can be highly accurate for similar standards and samples under the same conditions" | saxs/saxs_mw.rst |
| Porod 体积 / SAXSMoW 2 | `[2]` 球状蛋白**中位不确定度 12%**；`[5]` 模拟：**中位值偏高 3%、中位绝对偏差 5%**（有噪声时更高）→ 总体 ~10% | saxs/saxs_mw.rst |
| 相关体积 Vc | `[3]` 理论曲线 ~5%、实验曲线 ~10%；`[5]` 模拟：**中位值偏低 2%、中位绝对偏差 7%** → 总体 ~10% | saxs/saxs_mw.rst |
| Shape&Size | `[4]` **90% 测试数据在期望值 10% 内**；`[5]` 中位值正确、**中位绝对偏差 4%** | saxs/saxs_mw.rst |
| Bayesian | `[5]` 中位值准确、**中位绝对偏差 4%**；比任一单独方法更准，"uncertainty ... closer to ~5% than 10%" | saxs/saxs_mw.rst |
| **通则** | **~10% uncertainty (or more)**；低信噪数据可显著更差 | saxs/saxs_mw.rst |

## 四、失效域与优缺点（逐条）

**方法 1 · 绝对标定 I(0)**
- 优点：参数全知时可高度准确；参数正确时可用于蛋白或 RNA/DNA。
- 缺点：需准确样品浓度；需准确绝对刻度；最好已知对比度与偏比容。

**方法 2 · 参比标准品**
- 优点：相似标样与样品、同条件下可高度准确；标样正确时可用于蛋白或 RNA/DNA。
- 缺点：需准确样品浓度；标样须与样品同对比度（同缓冲液）；须同形状（同偏比容）。

**方法 3 · Porod 体积**
- 优点：对多数分子形状准确 `[5]`；信噪合理时比 Vc 更准 `[5]`。
- 缺点：柔性/延伸分子"应表现不佳"（`[5]` 发现并不总是如此）；可能需调蛋白密度（默认 0.83 kDa/Å³）；**非蛋白会失败**；对扣减误差敏感。

**方法 4 · 相关体积 Vc**
- 优点：低信噪时比其他方法准 `[5]`；有扣减误差时也更准 `[5]`；对柔性/延伸分子应准确 `[3]`（`[5]` 不总成立）；蛋白与 RNA/DNA 都可用。
- 缺点：高信噪数据不如他法 `[5]`；延伸分子不如 Porod 法 `[5]`；**<~15–20 kDa 不确定度大**（经验系数由 ≥20 kDa 段拟合）；**蛋白-核酸复合物失效**；∫qI(q) 必须收敛。

**方法 5 · Shape&Size**
- 优点：除低信噪外，最准的单个浓度无关方法 `[5]`；有扣减误差时相对准确。
- 缺点：柔性体系无结果；**只对蛋白**。

**方法 6 · Bayesian**
- 优点：多数情况下比任一单独浓度无关方法更准 `[5]`。
- 缺点：对显著扣减误差敏感；**只对蛋白**。

**所有方法的共同前提**（原文§strengths/weaknesses）
- 每个方法都需要**好的 I(0)**；
- 所有浓度无关方法都需要 **Rg**，一般意味着**需要好的 Guinier 拟合**；
- `[5]` 报告：所有浓度无关方法在**平坦/环状（flat and ring-shaped）蛋白**上都吃力。

## 五、判读决策清单（本 skill 的落地顺序）

1. 数据是 SEC 峰内（浓度未知）还是批次（浓度已知）？→ 决定可用方法集。
2. 有没有好 Guinier（可信 Rg、I(0)）？没有 → 先修曲线。
3. 浓度依赖法：填了浓度吗？绝对刻度标定过吗？→ 否则 Abs./Ref. 面板不出数。
4. 逐法对照失效域：小分子 / 复合物 / 非蛋白 / 柔性 / 扣减误差。
5. 用锚点校量级：GI 172 kDa（0.47 mg/ml）、lysozyme 14.3 kDa（4.27 mg/ml）。
6. 报结论：并列 + 标注 eligible 方法 + ~10% 量级；要定量分子量 → MALS / AUC / SEC-MALS-SAXS。

## 六、结合化学计量：为什么判不了

原文 FAQ（`saxs/saxs_mw.rst`）：
> "if you have something that's small, say ~20 kDa, and something much larger, say ~250 kDa, SAXS data is unlikely to be reliable enough to accurately determine the difference between bound and unbound (250 kDa or 270 kDa), or between 1:1 and 2:1 binding (270 kDa or 290 kDa)."

要准 → 做 **SEC-MALS-SAXS**（同一洗脱上同时收 MALS 与 SAXS）。

## 七、参考文献（文档原文编号）

1. Mylonas, E. & Svergun, D. I. (2007). *J. Appl. Crystallogr.* 40, s245–s249. DOI 10.1107/S002188980700252X
2. Piiadov, V. et al. (2018). *Protein Sci.* DOI 10.1002/pro.3528（SAXSMoW 2）
3. Rambo, R. P. & Tainer, J. A. (2013). *Nature* 496, 477–481. DOI 10.1038/nature12070（Volume of correlation）
4. Franke, D., Jeffries, C. M. & Svergun, D. I. (2018). *Biophys. J.* 114, 2485–2492. DOI 10.1016/j.bpj.2018.04.018（Shape&Size）
5. Hajizadeh, N. R. et al. (2018). *Sci. Rep.* 8, 7204. DOI 10.1038/s41598-018-25355-2（Bayesian）
6. Orthaber, D., Bergmann, A. & Glatter, O. (2000). *J. Appl. Crystallogr.* 33, 218–225. DOI 10.1107/S0021889899015216
