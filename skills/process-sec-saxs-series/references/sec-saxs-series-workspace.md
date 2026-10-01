# SEC-SAXS 系列：面板地图与术语（reference）

源 A = 微信《利用BioXTAS RAW程序处理SEC-SAXS数据》· 刘广峰；源 B/C = BioXTAS RAW 官方教程 *Basic SEC-SAXS processing* / *Baseline correction*（v2.4.1）。
此文件是**参考**（候选组 `raw-sec-ui-navigation` 被阶段 1.5 判为不成 skill：信息检索而非可外推方法论），供 `process-sec-saxs-series` 与 `correct-sec-saxs-baseline` 引用。

> 版本警告：界面文字随 RAW 版本变化；定位不到时以程序自带 `docs/` 或在线文档为准。

---

## 一、两个面板

| 面板 | 打开方式 | 放什么 |
|---|---|---|
| **Series 面板**（控制） | 载入 series 后自动出现；否则点控制面板的 Series 选项卡 | 系列列表（每条 series 一行，可加星/改颜色）、`Series Info`（分子类型、平均窗口大小）、`Data to Profiles plot`（输入帧范围 → `Average` / `Plot`） |
| **LC Series analysis 面板** | Series 面板底部 `LC Analysis` 按钮，或右键系列名 → `LC Series analysis` | `Buffer` 区（`Auto`/`Pick`/`Add region`/`Set buffer`）、`Sample` 区（`Auto`/`Set`/`To Profiles Plot`）、`Baseline Correction`（`None`/`Linear`/`Integral` + 起止参考区 + `Set baseline and calculate`） |

绘图面板同时多出 **Series 选项卡**（色谱图）；载入系列后 RAW 通常自动切过去。

## 二、三档图（同一个 series 的三种视图，不是三份数据）

| 图 | 纵轴含义 | 用来判断 |
|---|---|---|
| **Unsubtracted** | 原始（未扣缓冲液）积分强度 vs 帧号 | 峰在哪、峰前小峰、首帧异常、缓冲液区落点 |
| **Subtracted** | 扣减缓冲液后的强度 vs 帧号（+ 橙色画出拟校正线） | **漂移性质**、样品区平台、校正效果 |
| **Baseline Corrected** | 再扣掉基线后的强度 vs 帧号 | 漂移是否消除、是否过校正 |

**怎么切纵轴**（RAW 2.4.2 实测；两条等价路径）：

- **Series 面板的 `Plot Controls` 框** → **`Intensity:` 下拉框**，四个选项：
  `Total Intensity` / `Mean Intensity` / `Intensity at specific q` / `Intensity in q range`。
  选后两档时，同排右边出现 `q = [起点] to [终点]`（**从当前 q 列表里挑**，不是自由输入；单位 Å⁻¹）。
  同一框里的 **`Calculated value:` 下拉框**（`Rg` / `MW (Vc)` / `MW (Vp)` / `I0`）决定**右 Y 轴**画哪个逐帧参数。
- **菜单栏 `View`** → `Series Plot Left Y Axis`（同四个选项）；`View` → `Series Plot Intensity Type` → `Unsubtracted` / `Subtracted` / `Baseline Corrected`（切三档图）。
- **低 q 看聚集体、高 q 看噪声**，切 q 区间是诊断手段而不仅是显示偏好。

> 控件位置核对自源码：`RAWAnalysis.py` `create_layout()` 的 `intensity_type`（wx.Choice）与 `q_range_start` / `q_range_end`（FloatSpinCtrlList）；
> 菜单项见 `RAW.py` 的 `viewSECLeft` / `viewSECInt` 子菜单定义。

## 三、Calc markers

画在右 Y 轴的逐帧参数：`Rg`、`I(0)`、`MW(Vc)`（相关体积法）、`MW(Vp)`（校正 Porod 体积法）。
它们与"从最终那条平均曲线做 Guinier 拟合"得到的参数**不是同一件事**：前者用于判断平台、后者用于报告；两者应大致一致。

## 四、与 ATSAS CHROMIXS 的口径差异

CHROMIXS 默认显示 q 区间 **0.01–0.08 Å⁻¹ 的平均强度**；RAW 显示同一区间的**强度和**。
所以同一份数据在两个软件里的色谱图纵轴数值不同——比较前先对齐"区间 + 求平均/求和"。

## 五、保存与导出

| 动作 | 产物 | 含什么 |
|---|---|---|
| `Save series` | `.hdf5` | 系列数据 + **区域选择 + 基线设置**（重开即可复现判断） |
| `Export data`（右键系列名） | `.csv` | 帧号、积分强度、Rg、MW、每帧文件名等（用于作图 / 与 UV 痕对齐） |
| `Save report` | `.pdf` | series 图 + 平均后的扣减曲线 |

> 区域选择与基线设置本身是**分析结论的一部分**：不存 series 的话，别人（或三个月后的你）无法知道这条曲线是怎么圈出来的。

## 六、术语（作者/官方用法 vs 常识）

| 术语 | 作者/官方用法 | ≠ 常识理解 |
|---|---|---|
| Series | "按顺序采样的一整串数据"这个**对象类型**（带帧号轴）；SEC 只是其中一类 | 不是"一堆互不相干的曲线"；也不是 SEC 专属 |
| 色谱图 / 散点图 | 每个点 = **一帧**散射曲线的（积分/平均/q 区间）强度 | 不是某条 I(q) 曲线上的峰 |
| buffer 区 / sample 区 | **帧号区间**（可多段），如 504–562 / 699–713 | 不是"选文件" |
| 滑窗 / window size | 逐帧参数计算时的滑动平均长度（N=5 → 帧 0-4、1-5…） | 不是缓冲液平均的范围 |
| 手动路径 | 星标 series → 输入帧范围 → `Average` → 再 Subtract | 它与 LC Analysis **不等价**（失去平台判据） |
| 平台区 | Rg/MW 在峰中心平稳的一段（判"单一物种"的图形判据） | 不是"峰顶"或"最对称的一段" |
| 峰前小峰 | 未完全分开的高阶寡聚体/聚集体 → **属于样品** | 不是背景（把它算进缓冲液区会造成假单分散） |
| UV 痕 | 上游色谱的独立信号，用作选缓冲液区时的**交叉参照** | 不能替代 SAXS 色谱图作判据 |
| Baseline correction | Linear（仪器/束流漂移）/ Integral（毛细管污垢），**每个 q 各一条校正线** | 不是"让曲线好看的平滑"；积分法会过校正 |
| `.hdf5` / report | RAW 自己的 series 容器 / 导出报告 | 不是原始探测器数据 |

## 七、BL19U2 相关与线站差异

- 源 A 明确：**在 19U2，如果需要做强度校正，最后一帧不能用**（统计规则）——这是线站特有例外。
- RAW 的"自动载入 series"（Series 面板 `Select` 一个文件名让 RAW 自行展开整列）
  **只在 cfg 为 BioCAT / MacCHESS 时可用**（靠文件名规则认系列）；BL19U2 需手选文件或用 `.hdf5`。
- 缺配置时载入/计算会直接报错——这正是 `configure-bioxtas-raw-for-a-dataset` 在 SEC 流程里仍然适用的原因。

## 八、本次未覆盖（官方有独立章节）

SVD / EFA / REGALS 分解（`s2_svd` / `s2_efa` / `s2_regals`）、多序列与时间分辨分析（`s2_multiseries`）、WAXS 处理与合并（`s1_waxs`）。
边界说明见 `books/sec-saxs-series/rejected/README.md`。
