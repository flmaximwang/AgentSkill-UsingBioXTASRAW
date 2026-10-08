---
name: script-raw-with-the-python-api
description: "用 RAW 的 Python API（RAWAPI）写脚本批量处理 SAXS：load→analyse→save 三段骨架、函数签名与返回元组顺序、SAM/IFTM/SECM 对象访问。用于「批量跑 Guinier 出报告」「脚本怎么载入 series」「auto_guinier 返回什么」「SEC 全流程怎么用脚本做」「无 GUI 怎么跑 EFA」；不做 GUI 点击流程（转对应 skill）。"
source_book: "BioXTAS RAW 官方文档 v2.4.2 — *The API*（api/getting_started · ex_analyze_profile · ex_batch_profile · ex_sec_saxs · installation）"
source_chapter: "50-api.md · api/getting_started.rst + api/ex_analyze_profile.rst + api/ex_batch_profile.rst + api/ex_sec_saxs.rst + api/installation.rst"
tags: [saxs, bioxtas-raw, api, python, scripting, automation, reproducibility]
related_skills:
  - slug: process-sec-saxs-series
    relation: composes-with
  - slug: deconvolve-overlapping-elution-peaks
    relation: composes-with
  - slug: reduce-saxs-frames-to-curves
    relation: composes-with
  - slug: correct-sec-saxs-baseline
    relation: composes-with
---

# 用脚本跑 RAW：load → analyse → save 三段骨架

GUI 里点三十次 Guinier 和用脚本跑三十条曲线，**用的是同一套实现**——`RAWAPI.py` 就是面板背后的函数。这个 skill 把"想批量 / 想可复现 / 想接进流程"的需求，落成一个三段骨架：**先 `load_settings(SAXS.cfg)`，再 load 数据，analyse，save**。核心难点不是算法，而是**官方 API 参考页是空壳**——函数名、参数顺序、返回元组顺序只存在于三个官方示例脚本里，签名以实测为准。

一句话定位：**它回答"这个分析怎么写成脚本、函数返回什么、对象怎么取数"，不替你做分析决策**（判据在对应的 GUI skill 里）。

## R — 原文 (Reading)

三段骨架与"先载配置"：

> Many functions in the API use RAW settings to provide certain parameters for the function…
>
> [FILE: 50-api.md · api/getting_started.rst]

> So it is a good idea to load a settings file at the start of your program.
>
> [FILE: 50-api.md · api/getting_started.rst]

> While settings can be created and saved using the API, we recommend using the RAW GUI to create and save your settings, then importing them…
>
> [FILE: 50-api.md · api/getting_started.rst]

> We recommend that you import just the RAWAPI package, as in the following example.
>
> [FILE: 50-api.md · api/getting_started.rst]

能力对等与无 GUI 的缺口：

> Any analysis you can do on series in the GUI can be done with the API.
>
> [FILE: 50-api.md · api/getting_started.rst]

> You can carry out SVD, EFA, and REGALS from the API (though without the GUI you have to know what the appropriate ranges are…
>
> [FILE: 50-api.md · api/ex_sec_saxs.rst]

对象访问：

> The intensity for subtracted of baseline corrected data is accessed by specifying the data type
>
> [FILE: 50-api.md · api/getting_started.rst]

保存与格式：

> Note that you use the .out extension for GNOM IFTs, and the .ift extension for BIFT IFTs.
>
> [FILE: 50-api.md · api/getting_started.rst]

> Note that setting a buffer range is only necessary if buffer subtraction has not already been performed on the series.
>
> [FILE: 50-api.md · api/ex_sec_saxs.rst]

安装与命令入口：

> When you install the RAW package, it creates a bioxtas_raw script that should be in the system path.
>
> [FILE: 50-api.md · api/installation.rst]

> Install the RAW API using pip with the command pip install .
>
> [FILE: 50-api.md · api/installation.rst]

## I — 骨架 (Interpretation)

### 一、三段骨架（所有脚本共享）

```
import bioxtasraw.RAWAPI as raw
settings = raw.load_settings('./standards_data/SAXS.cfg')   # ① load：先配置
profiles = raw.load_profiles([...])                          #    再 load 数据
…分析（auto_guinier / mw_* / bift / svd / efa / regals…）     # ② analyse
raw.save_profile(prof, 'x.dat', './out')                     # ③ save
```

- **① load 必须先 `load_settings`**：径向积分用到的**校准参数与掩膜**等由 settings 供给；不传 settings，涉及图像的函数就没有这些参数。
- **② analyse**：与 GUI 面板一一对应——Guinier/MW、IFT、3D 重建、SEC 的区间搜索与 SVD/EFA/REGALS。
- **③ save**：`save_profile` / `save_ift` / `save_series` / `save_report`。

### 二、三个对象——一切从对象的取数方法进

| 对象 | 是什么 | 关键访问 |
|---|---|---|
| **SAM / SASM**（SAS measurement） | 单条散射曲线 | `getQ()/getI()/getErr()`（截断+缩放后的数据）、`getQrange()`、`getRawQ()/getRawI()/getRawErr()`（未截断缩放）、属性 `.q/.i/.err`、`getAllParameters()/getParameter(key)` |
| **IFTM**（IFT measurement） | IFT/P(r) 结果 | 属性 `.p/.r/.err`；原始数据与拟合 `.q_orig/.i_orig/.err_orig/.i_fit`；外推到 q=0 的 `.q_extrap/.i_extrap`；`getParameter('dmax')` |
| **SECM**（SEC measurement） | 整条 series | `getFrames()/getIntI()/getMeanI()/getRg()/getI0()/getVcMW()/getVpMW()`、`getAllSASMs()/getSASM(i)/getSASMList(a,b)`、属性 `.buffer_range/.sample_range` |

两个易踩点：
- `getQ()` 返回的是**截断、缩放、偏移后**的数据；要原始未截断数据用 `profile.q` 或 `getRawQ()`——两者长度可能不同，混用会不匹配。
- 取序列数据要**声明 profile_type**：扣减用 `'sub'`，基线校正后的用 `'baseline'`；`getSASM/getSASMList` 是**零索引**。

### 三、签名与返回元组只能靠示例脚本（文档正文是空壳）

官方 API 参考的四页——`api/main_api.rst` / `profiles_and_ifts.rst` / `series.rst` / `settings.rst`——**只有标题、正文为空**。真正可用的函数清单来自三个示例脚本（`ex_analyze_profile` / `ex_batch_profile` / `ex_sec_saxs`），**返回元组的元素顺序必须逐字照抄**。典型如：

- `auto_guinier(...)` 返回 **11 元组** `(rg, i0, rg_err, i0_err, qmin, qmax, qrg_min, qrg_max, idx_min, idx_max, r_sq)`；
- `set_baseline_correction(...)` 返回 **10 元组**；
- `mw_vp` 返回 `(mw_vp, pvol_cor, pvol, vp_qmax)`，`mw_vc` 返回 `(mw_vc, vcor, mw_err, vc_qmax)`。

**完整清单**（按类别分组、含返回元组、标注"来自 examples"）见 `references/rawapi-function-inventory.md`。

一句话判据：**"这个函数到底返回几个值、什么顺序？"——查示例脚本，不要凭函数名猜；写脚本时先按元组解包跑通最小样例，再往上叠。**

## A1 — 案例 (Past Application)

**1. `ex_analyze_profile`：单条曲线的全流程（Guinier → MW → IFT → 3D）**（50-api.md · api/ex_analyze_profile.rst）

- 骨架：`load_settings('./standards_data/SAXS.cfg')` → `load_profiles(['./reconstruction_data/glucose_isomerase.dat'])` → 分析 → 保存。
- Guinier/MW：`auto_guinier(gi_prof, settings=settings)` 拿 11 元组；六法 `mw_ref(gi_prof, 0.47, settings=settings)`、`mw_abs(gi_prof, 0.47, …)`、`mw_vp(gi_prof, …)`、`mw_vc(gi_prof, …)`、`mw_bayes(gi_prof)`、`mw_datclass(gi_prof)`。
- IFT：`bift(gi_prof, settings=settings, single_proc=True)`（12 元组）、`datgnom(gi_prof)`（10 元组）、`auto_dmax(gi_prof)` → `gnom(gi_prof, dmax)`（10 元组）。
- 保存：`save_profile(gi_prof, 'gi.dat', './api_results')`、`save_ift(gi_bift, 'gi.ift', …)`、`save_ift(gi_gnom_ift, 'gi.out', …)`、`save_report('gi_report.pdf', './api_results', [gi_prof], [gi_gnom_ift, gi_bift])`。
- 3D：`ambimeter(ift)` → `dammif(...)`（循环 3 次）→ `damaver(files, 'gi', dir)` → `dammin(...)` → `cifsup(...)`；或 `denss(...)` → `denss_average(...)` → `denss(...)`（refine）→ `denss_align(...)`。
- 结论：**同一骨架从一条曲线一直贯到 3D 重建**，中间每一步都是"接上一个函数返回的元组"。

**2. `ex_batch_profile`：批量扣背景 + CorMap**（50-api.md · api/ex_batch_profile.rst）

- 做法：`load_and_integrate_images(buffer_files, settings)`、`load_and_integrate_images(sample_files, settings)` 得到 `(profiles, imgs)` → `cormap(buffers[1:], buffers[0])` 检验相似性 → `average(buffers)` / `average(samples)` → `subtract([sam_avg], buf_avg)[0]` → `save_profile(...)`。
- 结论：**批处理的"图 → 曲线 → 平均 → 扣减 → 存盘"全程可由脚本完成**；`cormap` 返回 `(pvals, corrected_pvals, failed_comps)`。

**3. `ex_sec_saxs`：SEC 全流程（区间 → 扣减/基线 → SVD/EFA/REGALS）**（50-api.md · api/ex_sec_saxs.rst）

- 载入：`load_profiles(profile_names)` → `profiles_to_series(profiles)`，或 `load_series(['./series_data/phehc_sec.hdf5'])[0]`。
- 区间与扣减：`find_buffer_range(series)` → `(success, start_idx, end_idx)`；`set_buffer_range(series, [[start, end]])`（8 元组）；`find_sample_range(series)` → `set_sample_range(series, [[start, end]])`。
- 基线校正变体：`validate_baseline_range(...)` → `set_baseline_correction(series, start_range, end_range, 'Linear')`（10 元组）→ 之后一律 `profile_type='baseline'`。
- 分解：`svd(series)` → `(svd_s, svd_U, svd_V)`；`efa(series, [[149, 197], [164, 321], [320, 364]])` → 4 元组；`regals(series, comp_settings)` → 7 元组（comp_settings 是逐分量的 `(prof, conc)` 设置字典）。
- 保存：`save_series(series, 'profile_series.hdf5', './api_results')`。
- 结论：**GUI 能对 series 做的，API 都能做**；唯一缺口是无 GUI 时 `efa`/`regals` 的**分量区间要你自己给**（与 `deconvolve-overlapping-elution-peaks` 的判据对接）。

## A2 — 触发场景 (Future Trigger)

**用户会在什么情境下遇到这类问题**

- 有几十上百条曲线，要批量跑 Guinier/IFT 并出一份报告，GUI 点不过来。
- 想把 RAW 的处理接进自己的 Python 流程（含 CI / 自动化 / 大规模复现）。
- 想知道某个函数（`auto_guinier`、`bift`、`set_baseline_correction`、`efa`…）的参数与返回顺序。
- 要读 series 的逐帧 Rg/MW/强度来画图或挑区间。
- 没有 GUI（服务器/headless），想跑 SEC 处理或分解。

**语言信号**

- 「用脚本批量把 30 条曲线都跑 Guinier 并出报告」
- 「RAWAPI 怎么载入一批 dat / 怎么载入 series」
- 「auto_guinier 返回的是什么 / 返回几个值」
- 「SEC 的 buffer/sample 区能不能用脚本自动找」
- 「服务器上没界面，怎么跑 EFA」

**与相邻 skill 的区别**

- 本 skill 只给**入口与骨架**，不给判据：Guinier 的取点/判读归 `assess-guinier-fit-quality`，SEC 区间与平台归 `process-sec-saxs-series`，基线方法选择归 `correct-sec-saxs-baseline`，分解的分量数/区间/lambda 归 `deconvolve-overlapping-elution-peaks`。用脚本时，这些决策**仍要先在脑子里定好**再写进参数。
- 与 GUI：两者同一套实现；选脚本是因为要**批量 / 可复现**，不是因为脚本能做面板做不到的事。

## E — 执行步骤 (Execution)

1. **安装**：源码安装（`bioxtasraw` 不在 PyPI）。
   ```bash
   git clone --branch v2.4.2 --depth 1 https://github.com/jbhopkins/bioxtasraw.git && cd bioxtasraw
   pip install .
   ```
   完成标准：`import bioxtasraw.RAWAPI` 成功；`bioxtas_raw` 命令能起 GUI（安装时生成）。
2. **准备 settings**：先用 GUI 生成并保存 `.cfg`（例如 `SAXS.cfg`），再在脚本里 `load_settings` 导入。
   完成标准：能说出脚本用的是哪份 cfg。判停点：涉及图像积分却没有 cfg → 先转 `configure-bioxtas-raw-for-a-dataset`。
3. **导入**：`import bioxtasraw.RAWAPI as raw`（只导 RAWAPI 包）。
4. **① load**：按数据形态选入口——图像 `load_and_integrate_images(files, settings)`；曲线 `load_profiles(names)`；IFT `load_ifts(names)`；series `load_series(names)` 或 `profiles_to_series(profiles)`。
   完成标准：拿到 SAM 列表 / IFTM 列表 / SECM 对象。
5. **② analyse**：按任务接对应函数；**先跑最小样例**确认返回元组能正确解包，再批量循环。
   - 批量 Guinier 报告：`load_settings` → `load_profiles` → 循环 `auto_guinier` → `save_report`。
   - SEC：`find_buffer_range` → `set_buffer_range` → `find_sample_range` → `set_sample_range`（必要时先 `validate_*`）。
   - 分解：`svd` / `efa(ranges)` / `regals(comp_settings)`——**区间必须自己给**。
   完成标准：每一步的返回值被正确使用；不确定签名/顺序时回 `references/rawapi-function-inventory.md` 核。
6. **③ save**：`save_profile` / `save_ift`（GNOM 用 `.out`、BIFT 用 `.ift`）/ `save_series`（`.hdf5`）/ `save_report`。
   完成标准：产物文件落盘，能被 RAW 或下游读回。
7. **记录**：脚本 + cfg + 输入清单一起存档，别人能复跑。
   完成标准：换台机器只改路径就能重放。

## B — 边界 (Boundary)

**不要用的场景**

- 只是**一次性处理一两条曲线**：用 GUI 更快，脚本的收益在批量与可复现。
- 想要的是**判据**（Rg 取哪段、区间怎么选、基线选哪种、分量数几个）→ 转对应 skill；本 skill 只把判据落成参数。
- 实验中需要交互（看峰、拖起点、肉眼定平台）→ 先 GUI 定好，再脚本化。
- **多序列精修 / WAXS 合并 / 绝对刻度标定的完整流程**不在本 skill 覆盖（各自超出）。

**源里明确警告过的失败模式 / 边界**

- **官方 API 参考正文是空壳**：`api/main_api.rst` / `profiles_and_ifts.rst` / `series.rst` / `settings.rst` 四页**只有标题、零正文**。所以本 skill 的**函数清单来自 examples**（三个示例脚本 + getting_started），**未在示例里出现过的签名不做承诺**；参数与返回顺序**以实测（`RAWAPI.py` 源码 / 实际运行）为准**。写脚本不要凭函数名猜返回。
- **不传 settings 的后果**：涉及图像径向积分的函数（`load_and_integrate_images` 等）依赖 settings 提供校准与掩膜；忘记先 `load_settings` 会缺参数。
- **无 GUI 时 EFA/REGALS 要自己给区间**（官方明说）——这是从 GUI 转脚本时最容易丢的东西。
- **ATSAS 依赖**：`ambimeter` / `dammif` / `damaver` / `dammin` / `gnom` / `datgnom` / `cifsup` 等调用 ATSAS；未装则不可用。RAW 原生（如 DENSS）对 GNOM 与 BIFT 的 IFTM 都可用，而 ATSAS 系方法要求 GNOM 的 IFTM。
- **版本**：绑定 RAW **2.4.2**；`pip install .` 会生成 `bioxtas_raw` 命令。官方 API 文档以 latest 为准，函数可能随版本增删。
- **`getQ()` vs 原始数据**：混用会长度不匹配（见 I 段）。

**并发模型（v2.4.2 源级；本机实测）**

- 判据：**别指望 `nprocs` 加速 Series 的平均/扣减——它默认 1，串行是设计**；要并行只有走下面点名的少数入口。
- 源级事实：主窗口所有 Series 操作（`to_plot_series → _plotSeries → _sendSECMToPlot`）都排在唯一的 `MainWorkerThread`（`RAW.py:4371`）命令队列里、**串行**执行；SASCalc 的 numba 内核**全部** `parallel=False`；设置项 `'nprocs'` 默认 **1**（`RAW.py:463`）；平均/扣减是普通 Python + numpy（`SASProc.average:102`、`SECM.averageFrames:1433`），**没有 pool**。
- 真正的多核只在这几处：Multi-Series 工具（`RAWMultiSeriesAnalysis.py:1130-1136`，Pool 上限 `min(cpu, 3)`）、批量图像积分（`RAWAnalysis.py:9169/9443`）、Number of simultaneous runs（`RAWAnalysis.py:13720/13815-13819`）、`BIFT.py`、`DENSS.py`（唯一的 `njit parallel=True`）。
- 含义：写脚本时对"一条 series 的平均/扣减"做好**串行、按预期慢**的准备——那不是没配好，是 RAW 的设计。要并行就去用 Multi-Series 工具、批量图像积分或 simultaneous runs，而不是去调 `nprocs`。

**参考文件**：按类别分组的函数名 + 一句话 + 返回元组（标"来自 examples"）见 `references/rawapi-function-inventory.md`。对象与术语（SAM/IFTM/SECM/profile_type）见该文件，以及 `../configure-bioxtas-raw-for-a-dataset/references/bioxtas-raw-glossary.md`。

## 相关 skills

- **process-sec-saxs-series** — `composes-with`：用脚本做 SEC 时，区间/平台判据取自那边（`find_/set_buffer_range` 等就是它的 API 落点）。
- **deconvolve-overlapping-elution-peaks** — `composes-with`：`raw.svd/efa/regals` 是那条流水线的脚本入口；无 GUI 时区间要按那边的判据自己定。
- **reduce-saxs-frames-to-curves** — `composes-with`：`load_and_integrate_images` → `average` → `subtract` → `save_profile` 是那条流水线的脚本版。
- **correct-sec-saxs-baseline** — `composes-with`：`set_baseline_correction(series, start, end, 'Linear'|'Integral')` 是它的脚本入口，注意 `profile_type='baseline'`。
