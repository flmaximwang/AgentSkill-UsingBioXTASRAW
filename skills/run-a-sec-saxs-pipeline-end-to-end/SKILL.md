---
name: run-a-sec-saxs-pipeline-end-to-end
description: "端到端跑一条 SEC-SAXS 系列（图像→报告，全在 RAW 里做）：补出每帧 BL19U2 header txt 让 RAW 逐帧归一化（不写归一化 tif）、裁剪区归一化视频、buffer/sample 区与扣减、多区间 Guinier 结果、IFT、分子量、DAMMIF/DENSS 形状重建，每个节点都落 .dat + 表格 + RAW PDF 报告。用于「把这条 SEC-SAXS 数据端到端跑一遍」「一千多帧怎么变成曲线和报告」「归一化视频怎么做」「珠模怎么出」「要各节点 profile 的 dat」；不负责单点判据（Guinier 取点→assess-guinier-fit-quality，P(r)/Dmax→compute-and-validate-p-of-r，MW 方法选择→choose-a-molecular-weight-method，重建评估→evaluate-a-shape-reconstruction）。"
version: 1.0.0
author: hermes
license: MIT
tags: [saxs, sec-saxs, bioxtas-raw, pipeline, normalization, bl19u2, video, guinier, ift, dammif, denss]
metadata:
  hermes:
    tags: [saxs, sec-saxs, bioxtas-raw, pipeline, normalization, bl19u2, video, guinier, ift, dammif, denss]
    related_skills:
      - slug: process-sec-saxs-series
        relation: composes-with
      - slug: script-raw-with-the-python-api
        relation: composes-with
      - slug: correct-sec-saxs-baseline
        relation: composes-with
      - slug: configure-bioxtas-raw-for-a-dataset
        relation: composes-with
      - slug: fit-a-high-resolution-model-to-data
        relation: composes-with
---

# 端到端跑一条 SEC-SAXS 系列（全程 RAW）

这条任务是**串流程**，不是教你判据：输入一个目录（SEC 的连续洗脱 tif + 监视器 + 采集日志），
输出「归一化视频 + 一条扣减曲线 + 多区间拟合结果 + IFT + 形状模型 + RAW 报告 + 每个节点的 .dat」。
中间**所有计算都由 RAW 完成**——脚本只负责拼参数与落盘。用户明确的要求：**不自己写积分/拟合/P(r)/重建算法，只调参数。**

一句话定位：**它回答"这条 SEC 系列怎么从图像一路跑到报告、每一步留什么文件"，不回答"这段 q 该不该取、这个 Rg 能不能信"（后者转判据类 skill）。**

## When to Use（什么时候用）

- 一整个 SEC-SAXS 系列要端到端跑一遍，还要视频 / 拟合图 / 珠模 / 各节点数据。
- 用户问「这批 SEC 数据怎么处理完」「一千多帧怎么变成一条曲线」「归一化视频怎么做」「珠模怎么出」「各节点的 dat 都要」。
- 线站只给了 `.Iochamber` + `.log`（SEC 模式没有逐帧 header txt），而 RAW 恰恰要靠这个 txt 归一化。

**不负责**：单点判据。Rg 取点与可信度 → `assess-guinier-fit-quality`；P(r)/Dmax/GNOM 选择 →
`compute-and-validate-p-of-r`；分子量方法选择 → `choose-a-molecular-weight-method`；重建结果评估 →
`evaluate-a-shape-reconstruction`；基线该用 Linear 还是 Integral → `correct-sec-saxs-baseline`。

## 数据形状（BL19U2 的两种模式，差别就在 txt）

| 模式 | 每帧图像 | 配套文件 |
|---|---|---|
| batch / 管式 | `<系列>_<run>_<帧号>.tif` | 每帧一份 `<同名>.txt`（头里 `Transmitted_Beam`、`SR Current`、`Exposure time`）+ `<系列>_<run>.Intensity` + `_00001.log` |
| **SEC（连续洗脱）** | `<系列>_<帧号>.tif` | **只有** `<系列>_1.Iochamber`（监视器时间序列）+ `<系列>_00001.log`（每帧 endTime） |

两个必须记住的实测事实：

- **监视器文件的"行"和"帧"不是一一对应**：本机实测 `bsa_1.Iochamber` 19651 行 / 2000 帧 ≈ **9.83 采样/帧**
  （6.5 点/s × 1.5 s 曝光）。所以只能**按时间窗口取中位数**，不能按行号对帧。
- **监视器开头有几行 `~1e-13` 的野值**（未开束流），正常值是 **`2.6e-08`** 量级；这些行必须丢掉，
  否则窗口落进这段的帧因子会爆掉。

## 核心机制：RAW 自己就会用逐帧 txt 归一化（别自己写）

1. RAW 的 header 格式清单里就有 **`BL19U2, SSRF`**（`SASFileIO.py:909` `parseBL19U2HeaderFile`），
   它按 **`<图像路径去掉扩展名>.txt`** 读取——**txt 必须和 tif 同名同目录**。
2. 归一化由 settings 驱动（`SASImage.integrateCalibrateNormalize` → `calcExpression`）：
   - `ImageHdrFormat = 'BL19U2, SSRF'`
   - `EnableNormalization = True`
   - `NormalizationList = [['/', 'Transmitted_Beam']]` —— 把每帧**除以该帧 txt 里的 `Transmitted_Beam`**
     （`SASImage.py:366-380` 多乘性项合并成一个 factor，`:520-545` 对非乘性项逐项 `scaleRawIntensity`）。
3. 线站下机的 `.cfg` 里通常**已经**是这套（本机 `20261001.cfg`：`NormalizationList=[["/","Transmitted_Beam"]]`），
   只有 `ImageHdrFormat` 是 `None`、`EnableNormalization` 是 `false` —— 两个值改掉即可。
4. 实测（bsa 前 5 帧）：开启归一化后 I(q) 恰好是原来的 **1/TB**（比率 3.894e7 = 1/2.568e-8，逐帧对上）。

**推论：不需要写归一化后的 tif。** 逐帧 txt 是 KB 级，归一化在积分时发生——省掉 2000 帧 × 9 MB ≈ 18 GB。

## 执行步骤

### Step 0 — 前置核对

- 用**装了 RAW 的 python**（本机 `/Applications/BioXTASRAW/bin/python`），且**不要站在 RAW 源码目录里**跑
  （源码树会遮蔽 site-packages 里编译好的 `sascalc_exts`，直接 ImportError）。
- 核对该会话的 `.cfg`（定心/距离/掩膜/标样）→ `configure-bioxtas-raw-for-a-dataset`。

### Step 1 — 补出逐帧 header txt（`emit-bl19u2-header-txt.py`）

```bash
python emit-bl19u2-header-txt.py \
  --series-dir <原始 tif 目录> --monitor <系列>_1.Iochamber --log <系列>_00001.log \
  --out-dir <产物根> [--lag-auto]
```

- 每帧的 `Transmitted_Beam` = 该帧曝光窗口 `[endTime − 曝光, endTime]`（含时钟偏移 lag）内**监视器中位数**；
- 低于 `--monitor-min-frac`（默认 5%）× 全局中位的采样点按"无束流"丢弃，个别窗口没采样则线性插值（会打印条数）；
- **txt 直接写进源数据目录**（与 tif 并排，RAW 才找得到）；因子表与元数据写 `<out>/norm/`；
- 线站原件保护：目录里已有同名 txt 时默认**拒绝覆盖**，确认要盖再加 `--force`；
- 时钟偏移：`--lag-auto` 用"检测器总计数 vs 监视器"的相关系数扫（本机 bsa 实测 **−32 帧 ≈ −48 s，corr 0.869**）。

完成标准：`<系列目录>/<帧名>.txt` 份数 = 帧数；`normalization_factors.csv` 里 TB 的 1–99 百分位展宽是合理的
通量起伏量级（本机 5%），没有离群帧（>20% 偏离要回头看 lag 与野值过滤）。

### Step 2 — 归一化裁剪视频（`crop-video-normalized.py`）

```bash
python crop-video-normalized.py --series-dir <tif 目录> --norm-csv <out>/norm/normalization_factors.csv \
  --out <out>/video/<系列>_crop_x<x1>-<x2>_y<y1>-<y2>_cols<c1>-<c2>_rows<r1>-<r2>_8x_20fps.mp4 \
  --x1 .. --x2 .. --y1 .. --y2 ..       # x/y 都从"大的那头"数（见下）
```

**坐标约定（别猜，用旧帧标定）**：BL19U2 视图给的 x/y **两个轴都从大的那头数** → 数组下标
`row = H-1-y`、`col = W-1-x`（`--x-origin right` 为默认；从左数才用 `--x-origin left`）。
标定法：拿一张**已被接受过的旧视频帧**，把候选读法各裁一份、按同一条渲染链渲出来算相关系数——
本机实测 `col=x` **0.11** vs `col=W-1-x` **0.66**，行向扫描峰值落在 `rows 708-768 = H-1-y`。

- 因子 `median(TB)/TB_i` 在**读入内存时**乘上，直接喂 ffmpeg —— 全程不落归一化 tif；
- 灰阶窗口用抽样帧定死后**逐帧不再自动拉伸**（自动拉伸会把要看的漂移抹平）；
- 帧号与因子烧在左上角；副产物 = 逐帧 `sum`/质心 CSV（束斑漂移监测）+（可选）`.npy` 堆栈 + 预览 PNG；
- 裁剪坐标约定：给的是左下原点 `(x, y)` → 数组 `row = H−1−y, col = x`。

完成标准：`ffmpeg -i out.mp4 -f null -` 的 `frame=` 等于帧数（或帧数/步长）；抽一帧看确实落在束斑/束挡区。

### Step 3 — RAW 端到端（`run-raw-sec-pipeline.py`）

```bash
python run-raw-sec-pipeline.py --series-dir <tif 目录> --out-dir <产物根> --cfg <日期>.cfg \
  [--steps integrate,series,guinier,ift,mw,shape,report] \
  [--buffer-range "s,e[;s,e]"] [--sample-range s,e] [--baseline none|linear|integral] \
  [--trim-qmin q] \
  [--guinier-ranges "qlo:qhi,..."] \
  [--model-engine auto|denss|dammif|both|none] [--denss-mode Fast|Slow|Custom] \
  [--n-models 4] [--symmetry P1] [--atsas-dir <ATSAS>/bin]
```

内部只调用 `bioxtasraw.RAWAPI`（= GUI 面板背后的同一套实现）：

| 节点 | RAW 入口 | 产物 |
|---|---|---|
| 积分（含逐帧归一化） | `load_and_integrate_images(files, settings)` | `profiles/01_integrated/<帧名>.dat` × N + `tables/frames_integrated.csv` |
| series + buffer 区 + 扣减 | `profiles_to_series` → `find_buffer_range` → `set_buffer_range` | `series/<前缀>_series.hdf5`、`profiles/02_buffer/buffer_avg.dat`、`profiles/03_subtracted/<帧名>_sub.dat` × N |
| （可选）基线 | `find_baseline_range` / `set_baseline_correction` | `profiles/05_baseline/*.dat`；之后 `profile_type='baseline'` |
| 样品区 + 样品平均 | `find_sample_range` → `set_sample_range` | `profiles/04_sample/sample_avg.dat`、`series/ranges.json` |
| 逐帧参数 | `series.getFrames/getRg/getI0/getVcMW/getVpMW/getIntI` | `tables/frame_params.csv`、`series/series_plot.png` |
| 多区间 Guinier | `auto_guinier` + `guinier_fit(idx_min, idx_max)` | `profiles/06_guinier/guinier_<标签>.dat`、`tables/guinier_multi_range.csv` + `.png` |
| IFT | `bift`（原生）/ `auto_dmax`+`gnom`（需 ATSAS） | `ifts/<前缀>_bift.ift` / `_gnom.out`、`tables/ift_summary.csv` |
| 分子量 | `mw_vc` / `mw_vp` / `mw_bayes` | `tables/mw.csv` |
| 形状重建 | `denss`（**电子云，RAW 原生，默认总跑**）+ `dammif`/`damaver`（**珠模，有 ATSAS 才跑**） | `models/<前缀>_denss.mrc`（+`_support.mrc`/`_map.fit`/`_stats_by_step.dat`/`_denss.log`）；有 ATSAS 时另有 `models/<前缀>_dammif_*.pdb` + `_damaver` |
| 报告 | `save_report(pdf, dir, profiles, ifts, series)` | `reports/<前缀>_raw_report.pdf` |

**形状重建两个都要**（`--model-engine auto`）：**电子云（DENSS，`.mrc`）与珠模（DAMMIF，`.pdb`）是同一份 IFT 的两种重建，互不替代**——
DENSS 是 RAW 原生（numba），`Fast` 模式实测几秒到几十秒就出；DAMMIF 是 ATSAS 可执行文件的外壳，**没装 ATSAS 时自动只出电子云**（并在日志里明说），不要因此把 `models/` 留空。

**多区间 Guinier 是"让用户复核拟合过程"的主产物**：不传 `--guinier-ranges` 时，脚本以 `auto_guinier` 的 Rg 为锚
铺一条跨判据边界的阶梯（qRg 0.3–0.6 / 0.4–0.8 / 0.5–1.0 / 0.6–1.3），每个区间**一份 profile 副本**
（`setQrange` 截到该区间）单独存 `.dat` 并进 RAW 报告，同框图用 **RAW 返回的 Rg/I0** 画模型线（不是自写拟合）。
表里给全 `Rg / I0 / rg_err / i0_err / q_min / q_max / qRg_min / qRg_max / r²`，据此判断"哪段才合适"。

## 复核点（跑完先看这几处，再看数字）

1. `tables/guinier_multi_range.csv`：区间之间 Rg 是否稳定；`qRg_max` 是否越过形状对应的上界（球≈1.3）；
   `r²` 与 `rg_err` 是否随区间缩窄而恶化。判据细节 → `assess-guinier-fit-quality`。
2. `series/series_plot.png`：峰上 `Rg/I0` 是否成平台（不成平台说明多组分/聚集）；
   buffer/sample 两条阴影就是脚本用的区间。
3. `tables/ift_summary.csv`：BIFT 的 `chi²`、`log_alpha`、`evidence`；GNOM 的 `dmax` 是自动定的，要复核。
4. `tables/mw.csv`：Vc/Vp（浓度无关）是否互相一致；SEC 峰内浓度未知，**不要**用 I0 标样/绝对刻度那几法
   → `choose-a-molecular-weight-method`。
5. `models/`：DAMMIF 至少 4 个模型看 a-score/平均 NSD；DENSS 看 FSC 分辨率 → `evaluate-a-shape-reconstruction`。

## 坑（都是实测撞出来的）

- **在 RAW 源码目录里跑会 ImportError `bioxtasraw.sascalc_exts`**：源码树遮蔽 site-packages 里编译好的包。
  要么换目录跑，要么在源码树里 `build_ext --inplace`。
- **`find_buffer_range` / `find_sample_range` 在"截断的系列"上会失败**（返回 `success=False`、区间为 `None`）：
  只取峰前的帧、或系列里没有可识别洗脱峰时必然如此 → 用 `--buffer-range/--sample-range` 手工给（0 基帧号）。
- **ATSAS 不在 = DAMMIF/GNOM/DATGNOM/CIFSUP 全不可用**：RAW 的 DAMMIF 是**外壳**，
  `RAW.py:1232-1242` 拼的是 `os.path.join(atsas_dir, 'dammif')`，`RAWAPI.dammif` 会抛 `NoATSASError`。
  没有 ATSAS 时跑 RAW 原生 `denss` + `bift`（都可用），装好 ATSAS（`https://biosaxs.com/download`，学术免费，
  需个性化 license）后加 `--atsas-dir <ATSAS>/bin` 即切到 DAMMIF/GNOM。
- **有的 SEC 系列根本没有监视器/日志**（本机 `4LI2-676`：1464 个 tif，无 `.Iochamber`、无 `_00001.log`）：
  这时 Step 1 无法执行 → 用 `--no-header-normalization` 跑（RAW 的 `ImageHdrFormat=None`、不启用归一化），
  视频也省略 `--norm-csv`（因子全 1）。**要在报告里写明"这条系列没有通量归一化"**，别让读者以为做了。
- **逐帧 txt 写进源数据目录**是刻意的（RAW 只在同目录找 `<帧名>.txt`）；写之前目录里若已有同名 txt 会被拒绝，
  真要覆盖才 `--force`——线站原件优先。
- **系列没有监视器 / 采集日志时不能做逐帧归一化**（本机 `4LI2-676` 就是这种：目录里只有 1464 个 tif，
  没有 `.Iochamber` 也没有 `.log`）。这时第 1 步无从做起，跑 RAW 要加 `--no-header-normalization`
  （否则 RAW 会去找不存在的 `<帧名>.txt`），视频也不给 `--norm-csv`（因子全 1）。产物里要写明"本系列未做通量归一化"。
- **`--buffer-range` 优先给峰前 + 峰后两段**（`"560,620;800,880"`）：SEC 峰后的基线常不等于峰前
  （窗口污染 / 束位漂移）。本机实测同一条 BSA 曲线，只用峰前一段时 Guinier 的 Rg 在 38–117 Å 之间随区间乱跳；
  换成峰前+峰后两段后落到 **23.7–27.4 Å、r² 0.91–0.99**（BSA 单体理论 ≈29 Å）。
- **低 q 被寄生散射污染会把 IFT 的 Dmax 拖到离谱值**：同一曲线未裁 q 时 BIFT 给 **Dmax=417 Å / Rg=149 Å**。
  用 `--trim-qmin 0.017` 显式裁掉低 q 段（内部就是 RAW 自己的 `setQrange`，不是自写拟合），再跑 IFT/MW。
- **ATSAS 接线三件事**（装好 ATSAS 后要一次对上）：① `--atsas-dir` 必须指到 **`bin` 这一级**
  （RAW 用 `os.path.split(atsas_dir)[0]` 反推 `ATSAS` 变量；本机实测 `/Applications/ATSAS-4.1.4-1/bin`）；
  ② `dammif` 写出的模型名是 **`<prefix>-1.<model_format>`**（默认 `cif`），而 `damaver` **只接受文件名、
  不接受路径**、且 `model_format` 必须与 dammif 一致 —— 对不上就报
  `FileNotFoundError: <prefix>-damaver-distances.txt`（看着像 DAMAVER 坏了，其实是输入清单错了）；
  ③ `mw_bayes` / `mw_datclass` **没有 `settings` 参数**（签名是 `profile, rg, i0, first, atsas_dir, ...`），
  传 `atsas_dir` 才生效，否则一直报 TypeError 被误当"没装 ATSAS"。
- **`--dammif-mode Fast` 实测约 8–20 s/模型**（本机 4 模型 ~40 s）；`Slow` 会显著更久，先 Fast 看 χ²，
  只有要做正式交付才换 Slow 重跑。
- **χ² 大 = 这组数据还不配做从头建模**，别在重建参数里找答案：本机对照两套数据——bsa DAMMIF 四模型
  `χ²=2.08 / Rg 28.0 Å / Dmax≈88 Å / MW 63 kDa`、DAMAVER `NSD=0.06`（单一聚类，模型一致，可用）；
  4LI2-676 同样流程 `χ²=27.7`、DAMAVER 分出 3 个聚类、GNOM Dmax 146 Å（Guinier 只给 15.9 Å）、DENSS 直接失败
  → 结论是**曲线本身还不够干净**（弱峰 + 无监视器归一 + 低 q 污染），先回去修曲线，不要交付模型。
- **DENSS 报 `DENSS failed to run properly` / `IndexError: index -1 is out of bounds ... labeled_support == feature` = 它的输入 IFT 不可用**，不是 DENSS 参数没调好：那个下标来自 `DENSS.py:1931` —— 收缩包络把 support 压成**空**（`num_features == 0`）时 `sums` 长度为 0。
  根因几乎总是 IFT 被低 q 拖出**离谱的 Dmax**（本机 4LI2-676 实测：Guinier Rg=15.9 Å，BIFT 却给 Dmax=189–357 Å，
  DENSS 盒子 side>1000 Å、密度摊薄 → 塌陷）。处置顺序：① 先把 q 裁到 qRg_min ≈ 0.4–0.5（`--trim-qmin`）；
  ② 仍不对就用**显式 Dmax** 走 RAW 原生 DIFT 喂 DENSS（`--ift-dmax 55`，经验起手 Dmax ≈ 3×Guinier Rg）；
  ③ 只在 ① ② 之后才考虑 DENSS 自己的步骤/盒子参数。**不要在 IFT 坏的时候去调 DENSS 参数。**
- **`models/` 空着 = 没跑 `shape` 步，或缺 ATSAS 又被当成"珠模出不来就什么都不出"**：正确姿势是
  `--model-engine auto` —— 电子云（DENSS）总出，珠模（DAMMIF）有 ATSAS 才出；两者都缺才叫失败。
- **表里 `rg = -1` 不是负数，是 RAW 的失败哨兵值**（该区间的 Guinier 拟合没收敛/点数不够）——按"此区间不可用"读，
  不要当成数值；同理 `r² < 0` 表示拟合比取平均还差。
- **裁剪坐标是"左下角为原点"**：`row = H−1−y`。裁出来一片均匀背景说明约定错了，别微调数字，回
  `frame-sequence-to-video` 的重定坐标法。
- **ffmpeg 的 libx264 + yuv420p 要求偶数边长**：61×71 的裁块靠整数放大（8×）顺带解决。
- 视频的 `-pix_fmt rgb24` 必须与写进管道的字节一致（写 RGB 就声明 rgb24），否则帧数会变 3 倍。

## 相关 skills

- **process-sec-saxs-series** — 本 skill 的"判据版"：区间怎么选、峰上 Rg 平台怎么看、SEC 为什么不能用绝对刻度。
- **script-raw-with-the-python-api** — RAWAPI 的骨架与返回元组顺序（本 skill 的脚本就是它的落点）。
- **correct-sec-saxs-baseline** — 扣减后仍漂移时选 Linear/Integral，以及本 skill 用的监视器归一套路。
- **configure-bioxtas-raw-for-a-dataset** — 换实验日/仪器时先核对 `.cfg`。
- **evaluate-a-shape-reconstruction** / **fit-a-high-resolution-model-to-data** — 重建与高分辨模型对照。
