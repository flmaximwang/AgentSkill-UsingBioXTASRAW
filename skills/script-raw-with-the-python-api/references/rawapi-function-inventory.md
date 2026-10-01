# RAWAPI 函数清单（按类别分组）

**证据层级**：BioXTAS RAW 官方 API 参考的四页（`api/main_api.rst` / `profiles_and_ifts.rst` / `series.rst` / `settings.rst`）**只有标题、正文为空**。因此下表全部**来自 examples**——`api/ex_analyze_profile.rst`、`api/ex_batch_profile.rst`、`api/ex_sec_saxs.rst`、`api/getting_started.rst`、`api/installation.rst` 里的可运行代码（即 `50-api.md` 语料）。

**签名以实测为准**：下表的参数与返回元组顺序**逐字抄自示例**；未在示例里出现过的用法不做承诺——真正要确认时，读 `RAWAPI.py` 源码或先跑最小样例解包。
版本：RAW **2.4.2**。导入：`import bioxtasraw.RAWAPI as raw`。

---

## 一、load（载入）

| 函数 | 示例用法 / 关键参数 | 返回 | 来源 |
|---|---|---|---|
| `load_settings` | `raw.load_settings('./standards_data/SAXS.cfg')` | settings 对象（供其它函数当 `settings=` 传入） | getting_started |
| `load_profiles` | `raw.load_profiles(profile_names)` | profile **列表**（SASM） | getting_started / ex_analyze_profile / ex_sec_saxs |
| `load_and_integrate_images` | `raw.load_and_integrate_images(image_files, settings)` | `(profiles, imgs)` | getting_started / ex_batch_profile |
| `load_ifts` | `raw.load_ifts(ift_names)` | IFT 列表（IFTM） | getting_started |
| `load_series` | `raw.load_series(series_names)` | series **列表**（SECM）——示例取 `[0]` | getting_started / ex_sec_saxs |
| `profiles_to_series` | `raw.profiles_to_series(profiles)` | 单个 SECM（输入需按序列出现顺序） | getting_started / ex_sec_saxs |

---

## 二、profile 对象（SAM / SASM）——取数方法

| 方法 / 属性 | 含义 | 来源 |
|---|---|---|
| `getQ()` / `getI()` / `getErr()` | 按 profile settings **截断/缩放/偏移后**的 q、I、误差 | getting_started |
| `getQrange()` | 截断区间（`getQ() == profile.q[q_range[0]:q_range[1]]` 成立） | getting_started |
| `profile.q` / `.i` / `.err` | 缩放偏移后、**未截断**的数据（属性） | getting_started |
| `getRawQ()` / `getRawI()` / `getRawErr()` | **未截断、未缩放、未偏移**的原始数据 | getting_started |
| `getAllParameters()` / `getParameter(key)` | 全部 / 某一类元数据（如 `getParameter('analysis')['guinier']['Rg']`） | getting_started |

---

## 三、IFT 对象（IFTM）——属性与方法

| 成员 | 含义 | 来源 |
|---|---|---|
| `.p` / `.r` / `.err` | P(r) 及其不确定度 | getting_started |
| `.q_orig` / `.i_orig` / `.err_orig` | 原始数据 | getting_started |
| `.i_fit` | P(r) 对原始数据的拟合 | getting_started |
| `.q_extrap` / `.i_extrap` | 外推到 q=0 的拟合 | getting_started |
| `getAllParameters()` / `getParameter('dmax')` | 元数据 / Dmax | getting_started |

---

## 四、series 对象（SECM）——取数方法

| 方法 | 含义 | 来源 |
|---|---|---|
| `getFrames()` | 帧号 | getting_started |
| `getIntI()` / `getMeanI()` | 总 / 平均强度 vs 帧号（可带 `'sub'` / `'baseline'`） | getting_started |
| `getRg()` / `getI0()` | 逐帧 Rg / I(0) | getting_started |
| `getVcMW()` / `getVpMW()` | 逐帧 MW（相关体积 / Porod 体积）；示例取 `[0]` | getting_started |
| `getAllSASMs([type])` | 序列内全部曲线（可带类型） | getting_started |
| `getSASM(i[, type])` | 第 i 条（**零索引**） | getting_started |
| `getSASMList(a, b[, type])` | 区间 `[a, b)` 的曲线（**零索引**） | getting_started |
| `.buffer_range` / `.sample_range` | 已设的缓冲液 / 样品区间（属性） | getting_started |

**profile_type**：`'sub'`（扣减后）或 `'baseline'`（基线校正后）；**不写默认为未扣减**。有基线校正的曲线必须用 `'baseline'`。

---

## 五、分析 · Guinier 与分子量

| 函数 | 示例用法 | 返回元组（**顺序逐字照抄**） | 来源 |
|---|---|---|---|
| `auto_guinier` | `raw.auto_guinier(prof, settings=settings)` | `(rg, i0, rg_err, i0_err, qmin, qmax, qrg_min, qrg_max, idx_min, idx_max, r_sq)` — **11 元组** | ex_analyze_profile |
| `mw_ref` | `raw.mw_ref(prof, 0.47, settings=settings)` | `mw_ref` | ex_analyze_profile |
| `mw_abs` | `raw.mw_abs(prof, 0.47, settings=settings)` | `mw_abs` | ex_analyze_profile |
| `mw_vp` | `raw.mw_vp(prof, settings=settings)` | `(mw_vp, pvol_cor, pvol, vp_qmax)` | ex_analyze_profile |
| `mw_vc` | `raw.mw_vc(prof, settings=settings)` | `(mw_vc, vcor, mw_err, vc_qmax)` | ex_analyze_profile |
| `mw_bayes` | `raw.mw_bayes(prof)` | `(mw_bayes, mw_prob, ci_lower, ci_upper, ci_prob)` | ex_analyze_profile |
| `mw_datclass` | `raw.mw_datclass(prof)` | `(mw_datclass, shape, dmax_datclass)` | ex_analyze_profile |

---

## 六、分析 · IFT（P(r)）

| 函数 | 示例用法 | 返回元组 | 来源 |
|---|---|---|---|
| `bift` | `raw.bift(prof, settings=settings, single_proc=True)` | `(ift, dmax, rg, i0, dmax_err, rg_err, i0_err, chi_sq, log_alpha, log_alpha_err, evidence, evidence_err)` — **12 元组** | ex_analyze_profile |
| `datgnom` | `raw.datgnom(prof)` | `(ift, dmax, rg, i0, rg_err, i0_err, total_est, chi_sq, alpha, quality)` | ex_analyze_profile |
| `auto_dmax` | `dmax = raw.auto_dmax(prof)` | `dmax`（标量） | ex_analyze_profile |
| `gnom` | `raw.gnom(prof, dmax)` | `(ift, dmax, rg, i0, rg_err, i0_err, total_est, chi_sq, alpha, quality)` | ex_analyze_profile |

---

## 七、分析 · 珠模型 / 电子密度（多依赖 ATSAS）

| 函数 | 示例用法 | 返回元组 | 来源 |
|---|---|---|---|
| `ambimeter` | `raw.ambimeter(ift)` | `(a_score, a_cats, a_eval)` | ex_analyze_profile |
| `dammif` | `raw.dammif(ift, 'gi_01', dir, mode='Fast')` | `(chi_sq, rg, dmax, mw, ev)` | ex_analyze_profile |
| `damaver` | `raw.damaver(files, 'gi', dir)` | `(mean_nsd, stdev_nsd, rep_model, result_dict, res, res_err, res_unit, cluster_list)` | ex_analyze_profile |
| `dammin` | `raw.dammin(ift, 'refine_gi', dir, 'Fast', initial_dam='…cif')` | `(chi_sq, rg, dmax, mw, ev)` | ex_analyze_profile |
| `cifsup` | `raw.cifsup('refine_gi-1.cif', '1XIB_4mer.pdb', dir)` | —（文件操作） | ex_analyze_profile |
| `denss` | `raw.denss(ift, 'gi_01', dir, mode='Fast', initial_model=…)` | `(rho, chi_sq, rg, support_vol, side, q_fit, I_fit, I_extrap, err_extrap, all_chi_sq, all_rg, all_support_vol)` | ex_analyze_profile |
| `denss_average` | `raw.denss_average(rhos, side, 'gi_average', dir)` | `(average_rho, mean_cor, std_cor, threshold, res, scores, fsc)` | ex_analyze_profile |
| `denss_align` | `raw.denss_align(rho, side, '1XIB_4mer.pdb', dir, 'gi_refined_aligned', out_dir)` | `(aligned_density, score)` | ex_analyze_profile |

> ATSAS 系方法（`ambimeter` / `dammif` / `damaver` / `dammin` / `gnom` / `datgnom` / `cifsup`）要求 GNOM 的 IFTM；RAW 原生的 `denss` 对 GNOM 与 BIFT 的 IFTM 都可用。

---

## 八、批处理 · 相似性 / 平均 / 扣减

| 函数 | 示例用法 | 返回 | 来源 |
|---|---|---|---|
| `cormap` | `raw.cormap(profiles[1:], profiles[0])` | `(pvals, corrected_pvals, failed_comps)` | ex_batch_profile |
| `average` | `raw.average(buffers)` | 平均后的 SASM | ex_batch_profile |
| `subtract` | `raw.subtract([sam_avg], buf_avg)[0]` | 扣减后 profile 的**列表**（示例取 `[0]`） | ex_batch_profile |

---

## 九、SEC 区间与基线

| 函数 | 示例用法 | 返回元组 | 来源 |
|---|---|---|---|
| `find_buffer_range` | `raw.find_buffer_range(series)` | `(success, start_idx, end_idx)` | ex_sec_saxs / getting_started |
| `set_buffer_range` | `raw.set_buffer_range(series, [[start, end]])` | `(sub_profiles, rg, rger, i0, i0er, vcmw, vcmwer, vpmw)` | ex_sec_saxs |
| `find_sample_range` | `raw.find_sample_range(series, profile_type='baseline')` | `(success, start_idx, end_idx)` | ex_sec_saxs |
| `set_sample_range` | `raw.set_sample_range(series, [[start, end]], profile_type='baseline')` | 扣减后的单条 profile | ex_sec_saxs |
| `find_baseline_range` | `raw.find_baseline_range(series)` | `(start_found, end_found, start_range, end_range)` | ex_sec_saxs |
| `validate_buffer_range` | `raw.validate_buffer_range(series, buffer_range)` | `(valid, similarity_results, svd_results, intI_results)` | ex_sec_saxs |
| `validate_sample_range` | `raw.validate_sample_range(series, sample_range)` | `(valid, similarity_results, param_results, svd_results, sn_results)` | ex_sec_saxs |
| `validate_baseline_range` | `raw.validate_baseline_range(series, [0,10], [1132,1142], 'Linear')` | `(valid, valid_results, similarity_results, svd_results, intI_results, other_results)` | ex_sec_saxs |
| `set_baseline_correction` | `raw.set_baseline_correction(series, start_range, end_range, 'Linear')` | `(bl_cor_profiles, rg, rger, i0, i0er, vcmw, vcmwer, vpmw, bl_corr, fit_results)` — **10 元组** | ex_sec_saxs |

> 示例 note：**只有在尚未对 series 做过缓冲液扣减时，才需要设缓冲液区**。`validate_baseline_range` 对 Linear 基线"几乎总是返回 invalid、用处不大"；对 Integral 的校验已内含于 `find_baseline_range`。

---

## 十、分解 · SVD / EFA / REGALS

| 函数 | 示例用法 | 返回元组 | 来源 |
|---|---|---|---|
| `svd` | `raw.svd(series)` | `(svd_s, svd_U, svd_V)` | ex_sec_saxs |
| `efa` | `raw.efa(series, [[149, 197], [164, 321], [320, 364]])` | `(efa_profiles, efa_converged, efa_conv_data, efa_rotation_data)` | ex_sec_saxs |
| `regals` | `raw.regals(series, comp_settings)` | `(regals_profiles, regals_ifts, concs, reg_concs, mixture, params, residual)` | ex_sec_saxs |

`comp_settings` 是**逐分量**的 `(prof_settings, conc_settings)` 列表，每个是字典：

```python
prof1_settings = {'type': 'simple', 'lambda': 0.0, 'auto_lambda': True, 'kwargs': {}}
conc1_settings = {'type': 'smooth', 'lambda': 1.0, 'auto_lambda': True,
                  'kwargs': {'xmin': 145, 'xmax': 195, 'Nw': 50,
                             'is_zero_at_xmin': True, 'is_zero_at_xmax': True}}
comp_settings = [(prof1_settings, conc1_settings), (prof2_settings, conc2_settings), (prof3_settings, conc3_settings)]
```

`type` 可选 `'simple'` / `'smooth'`（浓度）/ realspace 正则化子；`lambda` 与 `auto_lambda` 对应 GUI 里逐分量的 λ 设置。

> **无 GUI 的缺口**：`efa` / `regals` **不替你选分量区间**，`efa_ranges` / `kwargs` 里的区间必须自己给（判据见 `deconvolve-overlapping-elution-peaks`）。

---

## 十一、save（保存）

| 函数 | 示例用法 | 说明 | 来源 |
|---|---|---|---|
| `save_profile` | `raw.save_profile(prof, 'gi.dat', './api_results')`；也可 `raw.save_profile(buf_avg, datadir='./api_results')` | 存 1D 曲线（`.dat`） | ex_analyze_profile / ex_batch_profile |
| `save_ift` | `raw.save_ift(ift, 'gi.ift', dir)` / `raw.save_ift(gnom_ift, 'gi.out', dir)` | **GNOM 用 `.out`，BIFT 用 `.ift`** | ex_analyze_profile |
| `save_series` | `raw.save_series(series, 'profile_series.hdf5', './api_results')` | 存 series（`.hdf5`；含区间选择与基线设置） | ex_sec_saxs |
| `save_report` | `raw.save_report('gi_report.pdf', dir, [prof], [gnom_ift, bift])` | 存 PDF 报告（给 profile 列表与 IFT 列表） | ex_analyze_profile |

---

## 十二、安装命令

```bash
git clone --branch v2.4.2 --depth 1 https://github.com/jbhopkins/bioxtasraw.git && cd bioxtasraw
pip install .
```

- `bioxtasraw` **不在 PyPI**，必须源码安装。
- 装完生成 **`bioxtas_raw`** 命令，可在命令行直接起 GUI。
