# SEC-SAXS 基线校正：RAW Python API（脚本路径）

本文件把 `correct-sec-saxs-baseline` 的**判据**接到**可执行入口**上：GUI 的 LC Analysis 面板与这里的 API 是同一套实现，
面板上那两个按钮对应的就是 `set_baseline_correction()`。

**证据层级**（本仓库的规矩）：函数名与签名来自 **RAWAPI.py 源码核对**（`jbhopkins/bioxtasraw` master 分支，
函数定义行号见下表）+ 官方 API 文档的示例；**不是**微信文章的译文内容。

## 一、安装

```bash
git clone https://github.com/jbhopkins/bioxtasraw.git && cd bioxtasraw
pip install .        # 不用 GUI 时无需 wx
```

> 实测：`bioxtasraw` **不在 PyPI** 上（`uv pip install bioxtasraw` → "not found in the package registry"），
> 必须走源码 `pip install .`。装完也会生成 `bioxtas_raw` 命令可直接起 GUI。

## 二、函数清单（已核对签名）

| 函数 | 签名（关键参数） | 源码行 |
|---|---|---|
| `load_series` | `(filename_list, settings=None)` | 294 |
| `profiles_to_series` | `(profiles, settings=None)` | 621 |
| `save_series` | `(series, fname=None, datadir='.')` | 756 |
| `find_buffer_range` | `(series, profile_type='unsub', int_type='total', q_val=None, …)` | 6169 |
| `set_buffer_range` | `(series, buffer_range, int_type='total', q_val=None, q_range=None, already_subtracted=False, window_size=5, …)` | 6390 |
| `find_sample_range` | `(series, profile_type='sub', window_size=5, …)` | 6762 |
| `set_sample_range` | `(series, sample_range, profile_type='sub', header_avg_keys=[])` | 7027 |
| `find_baseline_range` | `(series, baseline_type='Integral', profile_type='sub', window_size=5, …)` | 7105 |
| `validate_baseline_range` | `(series, start_range, end_range, baseline_type='Integral', profile_type='sub', …)` | 7218 |
| `set_baseline_correction` | `(series, start_range, end_range, baseline_type, bl_extrap=True, int_type='total', window_size=5, …)` | 7418 |

**返回值**

- `find_baseline_range` → `(start_found, end_found, start_range, end_range)`（找不到时区间返回 `-1`）
- `set_baseline_correction` → `(bl_cor_profiles, rg, rger, i0, i0er, vcmw, vcmwer, vpmw, bl_corr, fit_results)`

## 三、四条只有读源码才看得出来的约束

1. **`find_baseline_range` 只支持 Integral**："Currently only works for integral baseline corrections."
   → Linear 的起止参考区必须人工给（和 GUI 里"手动划两段"完全对应）。
2. **`validate_baseline_range` 对 Linear 几乎没用**："the validation for linear baselines almost always returns false, and is of little use."
   → 这解释了 GUI 里那条"前后两段斜率不一致"的警告为什么常见、且可以忽略（Integral 的校验有实质意义，它的自动搜索已内含校验）。
3. **缓冲液区只在必要时才设**："setting a buffer range is only necessary if buffer subtraction has not already been performed on the series."
   → 已经扣过缓冲液的 series（例如从 GUI 存出来的 `.hdf5`）直接做基线校正。
4. **做完校正要换 profile_type**：样品区搜索与导出都要用 `profile_type='baseline'`，否则读的是未校正的扣减曲线。

## 四、与 skill 判据的对应

| skill 里的判据 | API 里的落点 |
|---|---|
| 按漂移性质选方法（Linear=仪器，Integral=污垢） | `baseline_type` 参数：`'Linear'` / `'Integral'` |
| 只保留峰前的缓冲液区 | 由你给的 `start_range`/`end_range`（Integral 自动搜索会自己处理） |
| 参考区必须落在真正平的基线上 | `validate_baseline_range()` + 人工看（Integral 的 `find` 会偏靠峰，官方教程要求外推） |
| 过校正露在高 q | `set_baseline_correction` 返回的 `bl_cor_profiles` / `bl_corr`，按 q 区间逐段核对；确认高 q 是噪声就**先截断 q 再重跑** |
| 做 EFA 就不要叠加积分校正 | `raw.efa(series, ranges)` / `raw.regals(...)` 与 `set_baseline_correction` 不要叠加使用 |
| 引用义务 | 用 Integral 时除 RAW 论文外需引 Brookes, Vachette, Rocco & Pérez, *J. Appl. Cryst.* (2016) 49, 1827-1841 |

## 五、可执行脚本

`scripts/baseline_correction.py`（argparse，默认值与单位在 `--help` 里一处声明）：

```bash
python scripts/baseline_correction.py series.hdf5 --type integral
python scripts/baseline_correction.py series.hdf5 --type linear --start 30 60 --end 900 930
python scripts/baseline_correction.py first_profile.dat --buffer 504 562 --type integral
```

脚本按"载入 → （可选）扣缓冲液 → 定参考区 → 校验 → 校正 → 换 profile_type 重选样品区 → 存 `.hdf5`"串起来，
并在末尾打印过校正自检提示。

> **未在本机实跑**：本机未安装 RAW（也没有任何 SEC-SAXS 数据）。已完成的验证是**源码级**（上表的签名与返回值逐条核对）
> 与**入口级**（`--help` 实跑通过，见 `python baseline_correction.py --help`）。装好 RAW 后用真实数据跑一遍前请先核对帧号区间。
