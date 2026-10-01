# 多序列 / 时间分辨：面板地图、设置 json 与 cytc 全套数值（reference）

源：BioXTAS RAW v2.4.2 官方文档 · `tutorial/s2_multiseries.rst`（40-tutorial）。
此文件是**参考**（操作地图 + 数值表），供 `analyze-time-resolved-series` 引用；不单独成 skill。

> 版本警告：界面文字与 `Auto select` 可用条件随 RAW 版本与线站变化；以程序自带 `docs/` 或在线文档为准。

---

## 一、流水线一览

```
载入多 series（模板 <s>/<f> + 编号/补零）
   → 跨 series 定 buffer / sample 区（series 层，非 profile 层）
   → 逐点平均 + 扣减（每时点一条曲线，自动算 Rg/MW）
   → 时间校准（Load Calibration：两列 CSV；input key / output key / offset）
   → Rebin q（降噪，可选）
   → 裁 q 范围（低 q 寄生散射 / 高 q 半数点为负）
   → （多次重复测量一起平均）
   → 排除坏帧（如首帧）
   → Rebin series（factor 2，时点数减半）
   → Save analysis settings(json) / Export CSV
```

## 二、面板与控件地图

| 窗口 / 控件 | 作用 |
|---|---|
| Tools → **Multi-Series Analysis** | 打开多序列分析窗 |
| `Select from disk` | 主载入方式：目录 + 文件名模板 + Series#/Profiles# + 零填充 |
| `Add from series panel` | 从已载入的 Series 面板取 series |
| `Auto select` | 按兼容命名（如 BioCAT）自动识别并载入，需选任一 profile |
| 文件名模板 | 含 `<s>`（series 号）与 `<f>`（profile 号）；必要时 `<f>` 出现两次；支持 linux `*` / `?` 通配（较慢） |
| Series # / zero pad | series 号范围 + 零填充位数（pad4 → 0001、0010） |
| Profiles # / zero pad | profile 号范围 + 零填充位数（pad5 → 00001、00010） |
| 系列 buffer / sample 区窗 | 每个点是一条 series 的总强度；`Add region` 加 buffer（绿）/ sample（紫）区 |
| `Load Calibration` | 载入两列 CSV（input, output；`#` 开头为注释） |
| `Cal. input key` | 选 profile 头里用于校准的键（本例 `x`） |
| `Cal. output key` | 校准值写入 profile 头的键名（本例 `time`） |
| `Cal offset` | 加到 input 上的偏移（`cal_val = f(input+offset)`） |
| `Calibration in header` | 校准已存在于头里、直接用它（配合多次测量平均） |
| `Rebin q` | Q bin（type `Linear`/`Log`；mode `Factor`/`Points`） |
| `Q range` | q_min / q_max 裁剪 |
| `Exclude profiles` | 排除帧号（多帧逗号列表） |
| `Rebin series` / `Series bin factor` | 相邻 profile 平均，时点数 ÷ factor |
| `Series average window` | 对 Rg/I(0)/MW 值做滚动平均（保留逐 profile 采样） |
| `Plot multiple profiles` | 同时绘多条 profile（`Plot every` / `Last profile`） |
| Save / Load analysis settings | 存/读 json（载入模板 + 区间 + 校准 + 后续窗口设置） |

## 三、判据表（何时动哪个参数）

| 观察 | 判据 | 动作 |
|---|---|---|
| 低 q 有负值/下凹 | 混合器窗口寄生散射 | 抬 q_min（本例 0.01 → 0.015）；可用低 q 很少到 ~0.01 以下 |
| 高 q 约半数点为负 | 无信号（样品未显著高于背景） | 把 q_max 设到这里（本例 ~0.5–0.55 1/Å） |
| 曲线整体噪声大 | 单次测量信噪不足 | 先 Rebin q（如 Points=150）；或平均多次测量 |
| 自动 Rg/MW 算不出 | 信噪不足（cytc 小分子 + 0.45 M 胍为最坏情况） | 平均重复测量；不要硬报 |
| Rg 首点为 0 / 首帧异常 | 首帧贴近混合器边缘有额外散射 | `Exclude profiles` 填首帧号（本例 `0`） |
| Rg 随时间平缓变化、无快过程 | 过采样 | `Rebin series` factor 2（时点数减半） |
| 某时点有灰尘型强背景 | 坏帧（可能扫曲线看不出） | 回看该时点 2D 图像确认后排除 |
| 想把设置套到新数据 | — | Load settings + `Auto select`；校准随设置自动套用 |

## 四、cytc 实例：全套数值（`tutorial/s2_multiseries.rst`）

**载入（cytc_01）**
- 文件名模板：`cytc_01_005_<s>_data_0<f>_<f>.dat`
- 前缀 `cytc_01_005_` 固定；`_data_0` 固定；`<f>_<f>` 因文件名末尾两段数字同步递增而用两次
- Series #：**1–90**，zero pad **4**（0001 … 0090）
- Profiles #：**1–40**，zero pad **5**（00001 … 00040）
- 规模：**90 条 series × 40 个时点**

**buffer / sample 区（series 层）**
- buffer：约 **1–30** 与 **70–90**（后段取小以避开注入拖尾）
- sample：约 **32–44**（`cytc_03` 时为 **32–49**，buffer 75–90）

**时间校准**
- CSV：`time_8_ml_min.csv`（距离 mm ↔ 时间 ms）
- `Cal. input key` = **x**；`Cal. output key` = **time**；**Cal. offset = 71.13**
- 产物：x 轴单位变为 **ms**；本数据集所有时间 < 1 ms

**q 处理**
- Rebin q：`Linear` / `Points` = **150**
- q_min：**0.01 → 0.015** 1/Å
- q_max：**~0.5–0.55** 1/Å

**排除帧**
- 排除 **frame 0**（首帧，混合器边缘）；多帧示例写法 `0,5,15,30`

**Rebin series**
- factor **2**；时点数减半；帧号报段首帧（1 与 2 → 报 1）；校准值取段内平均

**多次测量平均**
- 5 次重复测量一起载入 → 跨全部 series 的 sample 区 → `Calibration in header` = `time`
- 科学结论：完全变性态 **Rg ~31 Å**、下一中间态 **Rg ~24 Å**；Rg 由 **~23–24 Å → ~18–19 Å**；最早时点 **45 微秒**，快于已发表研究的最早时点 **~150 微秒**，故未捕捉到更快塌缩相

**保存与导出**
- 设置：`cytc_01.json`（再 Load + Auto select 处理 cytc_03）；最终 `cytc_avg.json`
- 数据：`cytc_avg_timeseries.csv`（Rg/I(0)/MW 逐时点；也可从 Series 面板导出）

## 五、术语

| 术语 | 含义 |
|---|---|
| series（本例） | 沿混合通道的**一次扫描**；每个 profile = 一个**时点** |
| `<s>` / `<f>` | 文件名模板里的 series 号 / profile 号变量 |
| zero pad | 编号在文件名里的字符长度，不足补零 |
| 逐点平均（point-by-point） | 对 buffer 区（或 sample 区）各 series 的**同一 profile 号**求平均 |
| 时间校准 | 把 profile 头里的位置量经 CSV 与 offset 换算成时间 |
| Rebin q / Rebin series | q 方向分箱 / 时点方向相邻合并 |
| Exclude profiles | 按帧号剔除坏时点 |
| Auto select | 借兼容命名自动载入（依赖设施命名约定） |

## 六、本次未覆盖

SVD / EFA / REGALS 分解（`s2_svd` / `s2_efa` / `s2_regals`）在本流水线之后单独进行；单条 SEC 系列处理见 `process-sec-saxs-series`；基线校正见 `correct-sec-saxs-baseline`。
