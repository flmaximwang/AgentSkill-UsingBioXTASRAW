# Kratky 交叉验证：柔性、折叠，以及"坏扣减伪装柔性"

本文件是 `assess-guinier-fit-quality` 的展开参考。证据来自 **B 级**官方文档：
`40-tutorial.md · tutorial/s1_kratky.rst`（操作）与 `30-saxs.md · saxs/saxs_guinier.rst`（判据）。
绑定版本 **RAW v2.4.2**。**A 级 `20-manual` 不作依据。**

---

## 1. 三种 Kratky 图是什么

| 图 | 纵轴 vs 横轴 | 作用 |
|---|---|---|
| Kratky | `q²I(q)` vs `q` | 定性判柔性/解折叠程度 |
| Normalized Kratky | `q²I(q)/I(0)` vs `q` | 按质量与浓度归一，便于跨样品比较 |
| **Dimensionless Kratky** | `(qRg)²I(q)/I(0)` vs `qRg`（备用：`(q²Vc)I(q)/I(0)` vs `q(Vc)^{1/2}`） | 半定量判柔性/无序；RAW 默认此图 |

**形态解读**：折叠完全的紧凑球状蛋白 → **钟形（Gaussian）峰**；高度灵活/展开 → 高 q 出现**平台**；部分解折叠 → 钟形与平台的混合，或缓慢衰减到零的平台。

---

## 2. 球状蛋白的定量判据

RAW 的无量纲 Kratky 图上画了**两条灰色参考线**，对球状折叠蛋白：

- **峰位**：`qRg = √3 ≈ 1.73`
- **峰高**：`3/e ≈ 1.1`

> peak position should be at qR_g=\sqrt{3}\approx 1.73, while peak height should be 3/e\approx 1.1
>
> [FILE: 40-tutorial.md · tutorial/s1_kratky.rst]

**偏离这两条线 = 柔性/无序的信号。** 官方实例：GI 与溶菌酶都落在参考线附近（经典钟形，完全折叠）；载入的 folded/unfolded 对照曲线明显偏移。

---

## 3. RAW 里的操作

1. 在 Profiles 列表**选中曲线** → 右击 → **Dimensionless Kratky Plot**。
2. Normalized / Dimensionless Kratky 需要先有 Guinier 结果；有曲线缺 Rg 时 RAW 弹窗——可 Cancel 手动补做，或点 **Proceed using AutoRg** 用自动拟合的 Rg。
3. 顶部 **Plot** 下拉切换 **Dimensionless Rg / Normalized / Dimensionless Vc** 三种。
4. 高 q 噪声大（低信号）时可勾 **"Rebin profiles for plot"**（对数分箱，factor 2）。
   - **注意**：分箱**只作用于该图**，不写回主窗口的曲线。
5. 右击 → **Export Data As CSV** 导出（只导出图上显示的曲线；若已分箱则导出分箱后的）。

---

## 4. 头号坑：坏 buffer 扣减会让 Kratky 看似有柔性

> Bad buffer subtraction can also result in a Kratky plot that appears to show some degree of flexibility.
>
> [FILE: 40-tutorial.md · tutorial/s1_kratky.rst]

**Kratky 柔性判读要求极好的 buffer 扣减。** 若 buffer 与样品不匹配（未透析/未脱盐换液），本该钟形的折叠蛋白曲线会**上翘**，被误读成"部分解折叠/柔性"。

**证伪次序（不要跳步）**：

1. **先确认 buffer 匹配**：用**透析**配制匹配缓冲液，或**过体积排阻柱 / 脱盐柱换液**。
2. **看 Guinier 残差**：坏扣减会在低 q 造成下沉（过扣）或上扬（欠扣），**形似**排斥（frown）或聚集（smile）。
3. **做 P(r)**：用 `compute-and-validate-p-of-r` 交叉验证——真柔性会表现为 P(r) 的 Rg/I(0) 比 Guinier 的更大且更可靠；聚集会表现为 P(r) 长尾、Dmax 找不到。
4. **都排除后**，才可把 Kratky 的上翘当成柔性证据。

> 一句话：**Kratky 说"柔性"之前，先用 Guinier 与 P(r) 证伪"坏扣减"。**

---

## 5. 与 Guinier / P(r) 的判据对照

| 症状 | Guinier 残差 | Kratky | P(r) |
|---|---|---|---|
| 聚集 | smile（两端高中间低） | 可形似柔性 | 长尾、Dmax 找不到、Rg/I0 偏大 |
| 粒子间排斥 | frown（两端低中间高） | — | Dmax 被人为压小、Rg/I0 偏低、延伸后持续为负 |
| 真柔性/无序 | — | 偏离钟形（高 q 平台） | Rg/I0 比 Guinier 更大且更可靠 |
| **坏 buffer 扣减** | **形似 smile 或 frown** | **可形似柔性** | 一同被污染 |

**结论**：三者是互相独立的证伪工具；任何单一图的结论都要被另外两个交叉验证（官方明说"少量聚集在 P(r) 上像柔性体系"）。

---

## 6. 数值备忘（逐字）

- 无量纲 Kratky 球状峰位：`qRg = √3 ≈ 1.73`
- 无量纲 Kratky 球状峰高：`3/e ≈ 1.1`
- 高 q 分箱 factor：**2**（对数分箱，仅作用于图）
