# 绝对刻度与归一化的顺序约束（reference）

本文件是 `put-saxs-data-on-an-absolute-scale` 的**查表 + 顺序说明**。
证据级别：**B 级**（`40-tutorial`）——`tutorial/s3_abswater.rst` 与 `tutorial/s3_abscarbon.rst`，版本钉 **RAW 2.4.2**。
**A 级（`20-manual`）不得作事实依据**：旧手册只讲水法、且自承落后多个版本；玻碳相关内容在 tutorial 命中、在其余文件为 0（文档内部矛盾 C3）。

> 循环引用提醒：tutorial 的绝对刻度节写「see the manual for details」，而 manual 已过时。因此**操作路径以 tutorial 为准**，常数对错以第 4 节的**基准值**核对，不依赖 manual 的细节。

---

## 一、三法对照表（按「可用条件」分叉，不按偏好）

| 方法 | 什么时候只能用/该用它 | 需要的数据 | 面板里要设什么 | 示例常数 | 相对精度 |
|---|---|---|---|---|---|
| **水（water）** | 只有水标样数据时 | 空样品池图 + 水样图（各自**平均并存盘**）；常规归一化 | `Empty cell`=A_MT2_48_001_0000.dat、`Water sample`=A_water2_49_001_0000.dat、`Water temperature`=**4 °C** | 4 °C ≈ **0.00077** | 最低 |
| **玻碳 Simple（忽略背景）** | 有玻碳数据；背景未知或很小；只需常规归一化 + 单次背景测量 | 玻碳测量（平均存盘）+ 一次背景 | `Glassy carbon` Set=A_glassy_carbon2_011__0001.dat、`Sample thickness`=**1.0 mm**、保持 `Ignore background` 勾选 | ≈ **324** | 中 |
| **玻碳 Full（NIST recommended）** | 有玻碳数据；**上下游通量测量可靠**、背景测量准确 | 玻碳 + 玻碳背景 + 样品背景；所选 `.dat` **必须带上游/下游计数值** | 取消 `Ignore background`；三个 Set（玻碳 / 玻碳背景 / 样品背景）；`Sample thickness`=**1.5 mm**；`Upstream counter`=**I1**；`Downstream counter`=**I3**；**Normalization 列表清空** | ≈ **198** | 最高 |

**选法一句话**：玻碳比水更准（有则优先）；玻碳内部再按「背景/上下游通量是否可靠」在 Simple 与 Full 之间分叉。
**实测对照**：官方在示例数据上报告两种玻碳法**一致到约 1.5%**；最佳选择取决于**背景散射相对总散射的强弱**。

---

## 二、共享骨架（三法完全相同）

```
Absolute Scale 面板 → 选标样（水法另设水温；玻碳法另设厚度；Full 法另设背景与上下游计数器）
                    → 点 Calculate 得到绝对标度常数
                    → 勾选 “Normalize processed data to absolute scale using <标样>” 复选框
                    → OK 退出并保存设置
```

差异只在**填哪几个字段**，不在流程顺序。

---

## 三、两条顺序约束（违反 → 常数错 / 必须重算）

> 这两条是三法**共享**的；官方在 water / abscarbon(Simple) / abscarbon(Full) 三处各写了一遍同一段 note。

1. **算常数前必须先关掉绝对刻度。**
   否则得到的是一个坏常数（`otherwise you will get a bad scaling constant`）。
2. **一旦设好绝对标度常数，就不得再改动归一化设置（含通量、透射等）。**
   如果改了，必须**重算**绝对标度常数，不能沿用旧的（`If you do, you will have to recalculate the absolute scaling constant.`）。

**Full（NIST）法的附加约束**：全部归一化（**including flux, transmission, etc**）都经由 Absolute Scale 面板完成，**Normalization 面板里不应留任何条目**——除非你在做“从图像里扣掉一个常数 pedestal”这类操作。

---

## 四、基准常数（校准链是否接对的三个独立校验点）

| 校准 | 条件 | 官方“应该得到”的值 |
|---|---|---|
| 水 | 4 °C | 近 **0.00077** |
| 玻碳 Simple | 厚度 1.0 mm | 约 **324** |
| 玻碳 Full (NIST) | 厚度 1.5 mm，Upstream=I1 / Downstream=I3 | 近 **198** |

**判据**：算出的常数只要与对应基准**同量级且接近**，校链接对了；数量级都不对、或与基准差很多 → 先回去查第三节的两条顺序约束，再查数据/字段（厚度、计数器、是否选错文件）。

---

## 五、“不得再改归一化”的后果

- 绝对标度常数是**在当时的归一化设置下**标定出来的；归一化一变，同一批数据的 `I(q)` 就整体偏移一个因子。
- 症状：**不报错**。RAW 不会因为你改了归一化而提示“常数已失效”。
- 连带后果：绝对刻度上的 `I(0)`、由绝对强度推的浓度、以及依赖比例的 MW 估计**一起错**。
- 正确动作：改动归一化（含通量/透射）后**立即重算**常数；重算前照样要先关掉绝对刻度（第 1 条）。

---

## 六、本文件未覆盖 / 相关

- 标样图像本身的**定心、掩膜、归一化表达式**怎么设 → `configure-bioxtas-raw-for-a-dataset`。
- **SEC-SAXS** 数据：洗脱峰内浓度未知，绝对刻度给出的浓度不可靠 → `process-sec-saxs-series`（其正文写明“I(0) 标样/绝对校准对 SEC 不准确”）。
- 拿到绝对刻度之后如何**报 MW** → `choose-a-molecular-weight-method`（分子量方法选择，不在本 skill）。
