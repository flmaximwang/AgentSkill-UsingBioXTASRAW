# 造一份配置文件（.cfg）的六步链

本文件是 `configure-bioxtas-raw-for-a-dataset` 的展开参考：当手上**没有**现成的当天 `.cfg`、却有一套自带标样与背景的数据时，怎么把配置**造出来**。
证据来自 **B 级**官方文档 `tutorial/section3`（s3_masking / s3_autocenter / s3_normalization / s3_abswater / s3_abscarbon / s3_mwstd）。绑定版本 **RAW v2.4.2**；**A 级 `20-manual` 不作依据**（旧手册只讲水法、且自承过时）。
引用逐字取自英文原文，每条 ≤150 字，`[FILE: …]` 给出语料文件与 rst 节。

> **顺序警告（本链最容易静默出错的地方）**：六步的顺序由依赖锁死——
> ① **掩膜在定心之前**（定心的自动寻峰"只在连续区域找点、被遮区域不算数"）；
> ② **归一化在绝对刻度之前**（算常数前必须关掉绝对刻度、定完常数不得再改归一化）。
> 违反任一条都不报错，只会得到坏几何或坏常数。

---

## 0. 这份 cfg 是什么

> "This section will guide you through creating a configuration file for RAW that allows you to integrate 2D images into 1D scattering profiles."
>
> [FILE: 40-tutorial.md · tutorial/section3.rst]

> "The first step in creating a calibraiton file is to to mask out unwanted portions of your image, such as the beamstop and bad detector pixels."
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

（原文把 calibration 拼作 `calibraiton`，照抄会找不到。）

---

## 1. 掩膜（masking）——先遮，再定心

**判据：在哪张图上画？**
> "It's usually best to make a mask on a water or buffer image."
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

原因（同节）：在低强度的**仪器背景**上画，看不清 beamstop 边缘；在**亮图**（AgBh / 玻碳）上画，会被 beamstop 边缘的一点点溢漏骗成"遮小了"：
> "you can get fooled by a small amount of bleed onto the pixels at the edge of the beamstop"
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

**掩掉什么**：beamstop（圆 + 方杆）、坏点、面板缝。Pilatus 的坏点通常是 -2：
> "On a Pilatus detector, bad pixels usually have a value of -2."
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

> "This control automatically creates masks of panel gaps for any known detector type."
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

**顺序约束（掩膜 → 定心）**：定心的自动寻峰只在连续区域找峰，**被遮的区域不算数**；先在掩膜里遮掉面板缝，定心时才能在各块面板里都找到标样环点：
> "the autofind algorithm will only find peaks in contiguous regions. However, masked regions don't count"
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

**⚠ 两个保存语义（本 skill 第二号静默失效）**：
> "These do not save or set the mask in RAW. To do that you need to use the \"Set\" button as described above. The mask is then saved with the settings."
>
> [FILE: 40-tutorial.md · tutorial/s3_masking.rst]

- `Save to File` / `Load from file`：只在磁盘上写/读一个 `.msk` 文件，**不改变内存里的掩膜**。
- 生效必须按 `Set`（先在 Mask Creation 下拉里选 `Beamstop mask`，再 `Set`）。载入 `.msk`、或 `Clear` 之后，**同样要再按 `Set`**。
- 识别不生效：曲线在 beamstop 阴影区仍出现异常突起/负值；重开掩膜面板看不到刚画的掩膜。

---

## 2. 定心 / 几何标定（centering & calibration）

**目标**：找一组束心、样品-探测器距离、探测器倾角，使算出的 AgBh 环与图上实测环重合：
> "a beam center position, sample to detector distance, and detector rotation that causes the calculated Silver Behenate ring pattern to match the rings"
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

**参数字段（官方实例数字）**：
> "set the Energy to 12.0 keV. Verify that the Detector Pixel Size is 172.0 x 172.0 micron."
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

> "Verify that the Detector is set to \"pilatus_1m\". Verify that the standard is set to AgBh."
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

**环号是零基**（0 = 最内侧环）；最内侧几环可能不在探测器上，此时把 ring# 设成第一个可见环的序号：
> "if the third ring was the first one on the detector, the Ring # would be set to 2 (the ring number is zero index"
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

**判据 / 例外**：
> "Calculated rings are displayed without detector tilt angles"
>
> [FILE: 40-tutorial.md · tutorial/s3_autocenter.rst]

即：探测器明显偏离光束法线时，算出的环（不含 tilt）会对不上实测环，此时倾角需人工介入核对。

---

## 3. 归一化（normalization）

**做法**：先 `Load Image` 把头文件里的计数值载进来 → `Apply`；再到 Normalization 面板选 `/` 并填计数器名（BioCAT/BL19U2 的 beamstop counter 叫 I1）：
> "make sure \"/\" is selected in the left drop-down menu, and enter I1 in the large field."
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

> "It is typical in SAXS to normalize by the transmitted intensity. At the BioCAT beamline, the beamstop counter is name I1"
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

**判据（官方硬数字）**：
> "Click the Calc button to evaluate the expression for the counter values loaded in the Image/Header Format tab. You should get a value of 7200.0."
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

对不上 = 文件/头格式没设对，**不是数据坏**。

**附带：径向积分起点**——把 q Min 设到曲线峰处（遮罩内的 q 点值为 0），官方实例约 **point 13**；把它填进 "Start plots at q-point number" 后，之后每条曲线默认都不显示被 beamstop 盖住的前几个点：
> "Set q Min so that the first point is the peak of the curve on the main plot. This should be around point 13"
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

---

## 4. 绝对刻度（水 / 玻碳）——两条顺序约束

完整方法学（三法分叉、各字段、基准复核）见 skill `put-saxs-data-on-an-absolute-scale`；这里只列与"造配置"直接相关的顺序约束与基准常数。

**顺序约束 A —— 算常数前先关掉绝对刻度**：
> "make sure absolute scale is turned off before you calculate the scale constant, otherwise you will get a bad scaling constant"
>
> [FILE: 40-tutorial.md · tutorial/s3_abswater.rst · s3_abscarbon.rst]

**顺序约束 B —— 定完常数不得再改归一化**：
> "It is important that you not change your normalization settings once you have set the absolute scaling constant."
>
> [FILE: 40-tutorial.md · tutorial/s3_abswater.rst · s3_abscarbon.rst]

**三个基准常数（官方"应该得到"的值，用来判断校准链有没有接对）**：
> "You should get a value near 0.00077. … You should get about 324. … You should get an absolute scaling constant near 198."
>
> [FILE: 40-tutorial.md · tutorial/s3_abswater.rst · s3_abscarbon.rst]

| 校准 | 条件 | 期望值 |
|---|---|---|
| 水 | 4 °C | ≈ **0.00077** |
| 玻碳 Simple | 厚度 1.0 mm | ≈ **324** |
| 玻碳 Full (NIST) | 厚度 1.5 mm，I1/I3 | ≈ **198** |

> "the two methods of glassy carbon calibration agree within ~1.5%"
>
> [FILE: 40-tutorial.md · tutorial/s3_abscarbon.rst（Comparison note）]

另注（Full/NIST 法前提）：所选 `.dat` 必须含上下游计数值 I1/I3，否则改用图像；Simple 法忽略背景。细节见 `put-saxs-data-on-an-absolute-scale`。

---

## 5. MW 标准（molecular weight standard）

> "One method for determining molecular weight from a scattering profile is comparison to a known scattering profile with known molecular weight."
>
> [FILE: 40-tutorial.md · tutorial/s3_mwstd.rst]

判据：标样曲线必须与样品在**同一次会话、同一套几何与归一化**下测得——"参比标准品"法（见 `choose-a-molecular-weight-method`）的可比性以此为前提。

---

## 6. Save Settings → `.cfg`

> "You have configured everything necessary, and are now ready to save your settings. Go to the File menu and select \"Save Settings\"."
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

> "These settings can now be used to process images, and can be reloaded when you open RAW by selecting \"Load Settings\" from the File menu."
>
> [FILE: 40-tutorial.md · tutorial/s3_normalization.rst]

存成如 **SAXS.cfg**；之后 `File → Load Settings` 复用——这正是本 skill 主文档 A1 说的"载入当天 cfg"的来源，也让配置**可复现、可移交**。

---

## 附：实例数字速查（官方示例，非通用事实）

| 项 | 值 | 出处 |
|---|---|---|
| Energy | 12.0 keV | s3_autocenter |
| Detector Pixel Size | 172.0 × 172.0 micron | s3_autocenter |
| Detector | "pilatus_1m" | s3_autocenter |
| standard | AgBh | s3_autocenter |
| 归一化 `/I1` 求值 | **7200.0** | s3_normalization |
| 径向积分起点 | ~point 13 | s3_normalization |
| 水（4 °C）常数 | ≈ **0.00077** | s3_abswater |
| 玻碳 Simple（1.0 mm） | ≈ **324** | s3_abscarbon |
| 玻碳 Full（1.5 mm, I1/I3） | ≈ **198** | s3_abscarbon |
| 两玻碳法一致性 | ~1.5% | s3_abscarbon |

## 边界

本链针对的是"**有成套标样与背景记录的已有数据集**"。完全没有标样、没有几何记录的陌生仪器 / 自建台，**仍不在覆盖范围**（标定工作联系仪器负责人或参考官方文档）；此时只能明确告知用户"q 轴绝对值不可信"。
