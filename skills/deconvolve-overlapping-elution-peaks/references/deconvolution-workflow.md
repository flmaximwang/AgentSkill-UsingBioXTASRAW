# 重叠峰去卷积：阶梯选法 · 四步调参 · 复核清单（reference）

源 = BioXTAS RAW 官方教程 **v2.4.2**：*Advanced Series processing* → **SVD**（`tutorial/s2_svd.rst`）、**EFA**（`tutorial/s2_efa.rst`）、**REGALS**（`tutorial/s2_regals.rst`）；文件引用见 SKILL.md 的 `[FILE: 40-tutorial.md · …]`。
本文件是 `deconvolve-overlapping-elution-peaks` 的**速查表**：把正文的判据压缩成可照着走的表。所有数字都来自官方示例，换数据必须自己重扫。

> 版本警告：区间默认值、按钮文字随 RAW 版本变化；对不上时以程序自带 `docs/` 或在线文档为准。

---

## 一、方法阶梯：按"组分进出的次序"选

| 数据情形 | 用什么 | 它回答什么 | 关键前提 |
|---|---|---|---|
| 只想数"峰里有几个散射体" | **SVD** | 显著奇异值个数 + 自相关≈1 的向量个数 | 只看相对高序号平坦基线；**不改数据，只数** |
| 标准 SEC-SAXS（组分严格先进先出 FIFO） | **EFA** | 各分量散射曲线 + 浓度曲线 | 打开 EFA 即内含 SVD 第一步，无需先开 SVD 窗口 |
| IEC-SAXS（盐梯度→背景随时间变） | **REGALS** | 同上，且能把变化的缓冲背景拆成背景分量 | 组分非 FIFO |
| 时间分辨 / 滴定序列 | **REGALS** | 同上（滴定常用 realspace 正则化 + Dmax） | 点少/非等间距时**不要**用 EFA 找区间 |
| SEC 但基线倾斜 | **REGALS** | 可同时处理倾斜基线 | 这是 REGALS 内建背景分量，不是先做基线校正 |

**升级规则**：能在 FIFO 下解释就用 EFA；只要出现"非先进先出"或"背景本身在变"，就升到 REGALS。分量越多越难做——数据量与分量数之间要自己找平衡（症状：区间怎么调 χ² 都不平）。

**不可跳过的一步**：无论走 EFA 还是 REGALS，**先用 SVD 独立核对分量数**；RAW 自动判定可能错，改数据范围/数据类型后**不会自动更新**。

---

## 二、四步调参（由粗到细，层层依赖）

### 第 ① 步 · 分量数
- 看两件事：**显著高于高序号平坦基线的奇异值个数** 与 **左右奇异向量自相关都接近 1（约 >0.6–0.7）的向量个数**。
- 期望两者**相等**；不等 → 通常有一个弱/分辨不良组分：先按较小的数试，再按较大的数试。
- 改过帧范围/数据类型后，**再对一次** SVD 图与自动值。
- 官方示例：`phehc_sec.hdf5`（EFA）自动判 **3** 个 SV，正确；`nrde_iec.hdf5`（REGALS）自动判 **4** 个 SV，正确；`pheh_titration.hdf5` 自动判 **4**（实测 ~4–5），据先验知识**手动设为 3**（两构象 + 一聚集体）。

### 第 ② 步 · 区间（Forward/Backward 起点 → Component Range）
- **Forward EFA**：SVD 依次取"前 2 帧、前 3 帧…"；起点拖到**奇异值首次快速上升**处 = 该分量在此进入数据。
- **Backward EFA**：SVD 依次取"后 2 帧、后 3 帧…"；起点拖到**奇异值落回基线**处 = 该分量在此离开数据。
- 用起点圈出各分量帧范围；再到 **Component Range Controls** 微调，直到 **χ² 均匀≈1、无大尖峰**。
- 区间微调手法：先把区间设回默认看 χ² 尖峰，再收窄/外移；"**收窄到刚出现 χ² 尖峰、再退回上一个好值**"是官方推荐的最小化策略（减少他分量污染）。
- 官方示例值见下表 §四。

### 第 ③ 步 · lambda（仅 REGALS）
- 逐分量操作：**lambda 是浓度曲线的平滑度**（Tip：注意设的是 concentration 的 lambda，不是 profile 的）。
- 强分量 / 测量点多的分量（峰）：关 Auto lambda，**设 0**。
- 缓冲分量：关 Auto lambda，每次把 lambda **乘以一个数量级**（更小的调整几乎没有效果），直到出现过平滑，再回退。
- **过平滑信号**：各分量**高 q 背景先趋于一致**，随后**某分量（示例是 component 1）散射曲线突然剧变** → 回退到 last good value。
- **χ² 校验**：λ 设得特别差时 χ² 图会偏离 ~1；χ² 仍接近 1 说明 λ 大概率没问题。
- 官方示例：缓冲分量 last good value ≈ **4e8**。

### 第 ④ 步 · 保证可复现的最终运行
- REGALS：**不自动重算**——改了区间/λ 必须手动 **Run REGALS**；按钮**黄底**才表示"有未运行的改动"。
- EFA：迭代时可用 "Start with previous results" 加速，但**最终一次必须关掉**——否则旋转被前次结果引导，得到 path dependent、不可复现的解。
- 收尾：存分析数据（见 §三"交付"）并记录分量数/区间/λ/Dmax。

---

## 三、复核清单（交付前逐条打勾）

**EFA 三步复核对（官方要求每次 EFA 都做）**
- [ ] 所选分量区间 = Forward/Backward EFA 的起点（回图核对）。
- [ ] **χ² 图均匀接近 1、无大尖峰**。
- [ ] **取消正性约束（C>=0）后浓度峰不显著变化**；若显著变化 → EFA 差，不可信。
- [ ] 最终运行**未**勾选 "Start with previous results"。

**REGALS**
- [ ] 每次改动后都重新 Run 过；无"按钮黄底"的未运行状态。
- [ ] 背景分量数由 Background Components 区域估出（示例：0–100 帧 + 末 100 帧各含 1 个强分量 → # Significant SVs = 1）。
- [ ] 无过平滑信号（高 q 背景趋同 + 某分量 profile 突变）。
- [ ] χ² 维持 ~1。

**通用**
- [ ] 分量数经过 SVD 图交叉核对（不是直接采信自动值）。
- [ ] 没有把**浓度峰的绝对高度**当物理量（各峰归一化到面积 1，高度任意）。
- [ ] 结果有**其它方法 / 生化数据**佐证（旋转不保证成功）。
- [ ] 记录文件已存，别人能据此重放。

**交付产物**
- EFA："Save EFA Data (not profiles)" → SVD、Forward/Backward、χ²、浓度、所选区间、旋转方法。
- REGALS："Save REGALS data (not profiles)" → .csv：各分量设置、浓度、χ²、P(r)、平滑浓度曲线。
- "Done" → 各分量散射曲线进 Profiles Plot（标签 `_0/_1/_2…`）。
- 报 PDF：若 series 做过 EFA，报告里会附 EFA 摘要与各图。

---

## 四、官方示例数字速查

| 数据集 | 方法 | 分量数 | 帧范围 | Forward 起点 | Backward 起点 | 最终分量区间 | 其它 |
|---|---|---|---|---|---|---|---|
| `phehc_sec.hdf5` | SVD | 2（峰段，Subtracted） | 100 → 近 300 | — | — | — | 未扣减数据正常会多 1 个缓冲分量，本例已扣故无差别 |
| `phehc_sec.hdf5` | EFA | 3 | 0–385 | 147, 164, 322 | 383, 360, 200 | 142–198 / 161–322 / 319–360 | RAW 默认 151–193 / 164–322 / 319–347（会出 χ² 尖峰） |
| `nrde_iec.hdf5` | REGALS | 4 | 全段 | 0, 350, 750, 1195 | 700, 1325, 1600, 1736 | comp3 起点 1150→1125→1100→**1125** | comp2 浓度终点 1300→**1275**；缓冲 λ last good **≈4e8**；背景区 0–100 + 末 100 帧，SVs=1 |
| `pheh_titration.hdf5` | REGALS | **3**（自动4/实测4-5，手动设3） | 全段 | —（取消 Use EFA） | — | 实验类型 Titration；X 轴 Log10；首点 0→**10.0 µM** | 聚集体 Dmax **300**；两构象 Dmax 110→160（步 10–20），~130–150 χ² 稳，取 **130** |

补充判据（滴定）：P(r) 被**逼零**=Dmax 偏小；χ² 随 Dmax 上升而明显上升=Dmax 偏大；不同分量的 Dmax 不必然一致。

**Shannon 限**：给定数据 q_min，最大可测尺寸 **Dmax < π/q_min**（示例数据集据此把聚集体 Dmax 上界定为 ~300 Å）——为无从先验知识的对象（如聚集体）选 Dmax 上界时用它。

---

## 五、API 对应（无 GUI 时的入口）

- `raw.svd(series)` → `(svd_s, svd_U, svd_V)`
- `raw.efa(series, efa_ranges)` → `(efa_profiles, efa_converged, efa_conv_data, efa_rotation_data)`；`efa_ranges` 形如 `[[149, 197], [164, 321], [320, 364]]`
- `raw.regals(series, comp_settings)` → `(regals_profiles, regals_ifts, concs, reg_concs, mixture, params, residual)`；`comp_settings` 是逐分量的 `(prof_settings, conc_settings)` 列表，含 `type`（`'simple'`/`'smooth'`/realspace）、`lambda`、`auto_lambda`、`kwargs`（`xmin`/`xmax`/`Nw`/`is_zero_at_xmin`/`is_zero_at_xmax`）

**注意**：官方原话——无 GUI 时 `efa`/`regals` **不替你选区间**，每个分量的区间必须作为输入给出。详细签名见 `../script-raw-with-the-python-api/references/rawapi-function-inventory.md`。

**引用义务**：用 EFA 除 RAW 论文外需引 Meisburger et al., *JACS* (2016) 138(20), 6506-6516（DOI 10.1021/jacs.6b01563）；用 REGALS 需引 Meisburger, Xu & Ando, *IUCrJ* (2021) 8(2), 225-237（DOI 10.1107/S2052252521000555）。
