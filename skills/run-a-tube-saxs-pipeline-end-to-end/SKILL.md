---
name: run-a-tube-saxs-pipeline-end-to-end
description: "管式/静态 SAXS 一批帧端到端出全套结果（目录内样品+control→扣减→多区间 Guinier→P(r)→MW→3D），全程只用 RAW 自己的函数、每节点落 .dat。用于「一批 tif 怎么变成整套结果」「control 帧怎么定/要不要缩放」「多个 q 区间都拟合一遍给我看」「Dmax 怎么定」「珠模怎么出」；不负责单序列判据（Rg 取点→assess-guinier-fit-quality，P(r)/Dmax→compute-and-validate-p-of-r，MW 方法选择→choose-a-molecular-weight-method，重建评估→evaluate-a-shape-reconstruction）；SEC 连续洗脱帧走 run-a-sec-saxs-pipeline-end-to-end。"
version: 1.0.0
author: hermes
license: MIT
tags: [saxs, tube-saxs, static-saxs, bioxtas-raw, pipeline, bl19u2, normalization, guinier, ift, denss]
metadata:
  hermes:
    tags: [saxs, tube-saxs, static-saxs, bioxtas-raw, pipeline, bl19u2, normalization, guinier, ift, denss]
    related_skills:
      - slug: reduce-saxs-frames-to-curves
        relation: composes-with
      - slug: assess-guinier-fit-quality
        relation: composes-with
      - slug: compute-and-validate-p-of-r
        relation: composes-with
      - slug: choose-a-molecular-weight-method
        relation: composes-with
      - slug: evaluate-a-shape-reconstruction
        relation: composes-with
      - slug: script-raw-with-the-python-api
        relation: composes-with
      - slug: run-a-sec-saxs-pipeline-end-to-end
        relation: sibling
      - slug: organize-batch-saxs-dataset
        relation: composes-with
---

# 端到端跑一批管式/静态 SAXS 帧（全程 RAW）

这条任务是**串流程**，不是教你判据：输入**一个目录**（里面既是样品帧、也是这次实验的 control 帧），
输出「扣减曲线 + 每个 q 区间的拟合结果 + P(r)/Dmax + 分子量 + 3D 模型 + RAW PDF 报告 + 每个节点的 .dat」。
中间**所有计算都由 RAW 完成**——脚本只拼参数、落盘。用户明确的要求：**不自己写积分/拟合/P(r)/重建算法，只调参数。**

一句话定位：**它回答"这批管式数据怎么从图像一路跑到报告、每一步留什么文件"，不回答"这段 q 该不该取、这个 Rg 能不能信"（后者转判据类 skill）。**

## When to Use（什么时候用）

- 一个样品（或一条稀释序列）的 tif 要端到端跑完，还要多区间拟合图、P(r)、3D、各节点数据。
- 用户问「这批 tif 怎么变成一套结果」「control 帧怎么配」「多个区间都拟合给我看」「Dmax 怎么定」「珠模怎么出」。
- 线站按 batch/管式模式出数：每个样品 run 前后**夹着自己那份 blank run**（buffer / 水）。

**不负责**：Rg 取点与可信度 → `assess-guinier-fit-quality`；P(r)/Dmax/GNOM 选择 → `compute-and-validate-p-of-r`；
MW 方法选择 → `choose-a-molecular-weight-method`；重建结果评估 → `evaluate-a-shape-reconstruction`；
`.cfg` 本身对不对（定心/距离/掩膜）→ `configure-bioxtas-raw-for-a-dataset`；**SEC 连续洗脱帧** → `run-a-sec-saxs-pipeline-end-to-end`。

## 数据形状（管式 vs SEC：差别在"control 在哪"）

| 模式 | 每帧图像 | 配套文件 | control 从哪来 |
|---|---|---|---|
| **管式 / batch（本 skill）** | `<系列>_<run4>_<帧5>.tif` | 每帧 `<同名>.txt`（`Transmitted_Beam` / `SR Current` / `Exposure time`）+ `<系列>_<run4>.Intensity` + `_00001.log` | **同目录里别的 run**（前缀不同的那些） |
| SEC（连续洗脱） | `<系列>_<帧5>.tif` | 只有 `<系列>_1.Iochamber` + `.log` | series 里峰的**前若干帧** |

实测（`DataProcess_2026.10.01/data/Tube-SAXS/`）：线站已经把**样品 run + 夹着它的 control run** 分进同一个目录，
目录里前缀 != 样品名的那几个 run 就是 control：

| 目录 | 帧构成 | control |
|---|---|---|
| `A5-05-1` … `A5-05-6` | `ddh2o_00XX` + `A5-05-N_00YY`（+ 后一个 `ddh2o`） | **ddh2o** |
| `BSA` | `pb7_0001` + `BSA_0002` + `pb7_0003` | **pb7** |
| `5705` / `97df` / `877-*-pb7` | `pb7_00XX` 夹着样品 | **pb7** |

所以脚本的默认规则是"**文件名前缀 = 样品名（默认取目录名）的是样品，其余都是 control**"（前缀**精确相等**，不做子串匹配——
`877-apo-pb7` 里的 "pb7" 是缓冲液后缀，不是背景）；前缀不一致时用 `--sample-key` / `--control-key` 手工指定。
目录还没归类（一堆 series 平铺在一个目录里）时，先走 `organize-batch-saxs-dataset` 拆成"每样品一个文件夹 + 夹着它的背景"。

**产物落点约定（本项目）**：原始帧在 `<项目>/data/<模式>/<样品>/`，结果放**同级的** `<项目>/processed/<模式>/<样品>/`
（本机实测结构：`DataProcess_2026.10.01/{data,processed}/{Tube-SAXS,SEC-SAXS}/<样品>/`）。
`--out-dir` 指到 `processed/<模式>/<样品>`，整批跑时再在其上一层做 `_summary/` 与 `_logs/`。

## 核心机制（四条，都是实测撞出来的）

**① 归一化：RAW 自己会读逐帧 txt，但 cfg 里两个开关默认是关的。**
`ImageHdrFormat='BL19U2, SSRF'`（`SASFileIO.parseBL19U2HeaderFile` 按 `<图像名去扩展>.txt` 读）+ `EnableNormalization=True`
+ `NormalizationList=[['/','Transmitted_Beam']]`。下机 `.cfg` 里通常只有这两处要改（本机 `20261001.cfg`:
`ImageHdrFormat=None`、`EnableNormalization=False`）。不修就是**静默**不归一化：本机实测 I(q=0.01) 差 **1/TB = 1/0.4447 = 2.25 倍**。

**② control 要再乘一个相对比例（1–3%），否则高 q 留常数残差、把 IFT 带坏。**
样品 run 与 control run 的通量/管位不同，透射归一化之后仍差 ~2%，多出来的是一个**近常数**的高 q 残留
（`q²I` 在高 q 翘起来就是它）。用 **RAW 自己的相对缩放**（`profile.scaleRelative(f)`）在校正：
因子 = `mean(I_sample/I_control)`，取**粒子不散射的高 q 窗**（默认 q 0.30–0.44 Å⁻¹；小蛋白 q·Rg>4 基本无信号）。
实测 `A5-05-1`：因子 1.0236 → auto-Guinier 的 R² 从 **0.873 → 0.960**，高 q 残差归零；
因子偏离 1 超过 5% 时脚本会 WARNING（那是 control 配错了的信号，别硬缩放）。

**③ BIFT 的 Dmax 搜索域必须按 Rg 收窄，否则出来的 Dmax 是垃圾。**
RAW 默认 `minDmax/maxDmax = 10/400 Å`。对 Rg≈17 Å 的样品，BIFT 会在 400 Å 处交出一个
`chisq≈20–70` 的假解。脚本按 `Dmax ∈ [0.7, 1.6] × 3.1·Rg` 写进 settings（`DmaxPoints=10`、`PrPoints=100`），
本机随即给出 `Dmax=48 Å`、实空间 Rg=18.3 Å（与 Guinier 的 17.2 Å 对得上）。要自己看趋势就 `--ift-sweep N`。

**④ ATSAS 边界：RAW 里"珠模"这一支全是 ATSAS 外壳。**
`RAWAPI.dammif/dammin/gnom/datgnom/datmw/datclass/cifsup/crysol` 全部要 ATSAS；
包里**自带实现**的求解器只有 `BIFT.py` / `DENSS.py` / `REGALS.py`。GUI 菜单里永远能看到那些选项，
但它们不是内置算法：`RAW.showDAMMIFFrame`（RAW.py:1209）**先**判定 IFT 类型必须是 GNOM（否则弹 "Wrong IFT type"），
走到 RAW.py:1289 才判定有没有 ATSAS。且 DAMMIF 只吃 **GNOM 的 `.out`**（BIFT 的 `.ift` 连写都写不出来）。
所以本机（无 ATSAS）的可行组合是：**BIFT(IFT) + DENSS(3D) + Vp/Vc(MW)**；装好 ATSAS（`--atsas-dir <ATSAS>/bin`）后
GNOM/DAMMIF/DATMW/DATCLASS 才上线。

## 执行步骤

### Step 0 — 前置核对

- 用**装了 RAW 的 python**（本机 `/Applications/BioXTASRAW/bin/python`），且**不要站在 RAW 源码目录里**跑
  （源码树会遮蔽 site-packages 里编译好的 `sascalc_exts`，直接 ImportError）。
- 核对当天的 `.cfg`（定心/距离/掩膜/标样）→ `configure-bioxtas-raw-for-a-dataset`。
- 确认目录里的 **control 是哪一个 run**（看 `.txt` 的 `Description`/时间戳顺序，或问用户）。

### Step 1 — 端到端（`run-raw-tube-pipeline.py`）

```bash
python run-raw-tube-pipeline.py --sample-dir <目录> --cfg <日期>.cfg --out-dir <产物根> \
  [--sample-key <样品前缀>] [--control-key ddh2o,pb7] \
  [--scale-window 0.30 0.44] [--no-scale] \
  [--qrg-max 1.3] [--snr-min 2.0] [--ift-sweep 5] \
  [--model-engine none|denss] [--denss-mode Fast|Slow] [--symmetry 0] \
  [--atsas-dir <ATSAS>/bin] [--save-frames] \
  [--steps ift,mw,shape,report,workspace]      # 主干（积分/平均/缩放/扣减/多区间 Guinier）总是跑
```

内部只调 `bioxtasraw.RAWAPI`（= GUI 面板背后的同一套实现）：

| 节点 | RAW 入口 | 产物 |
|---|---|---|
| 积分（含逐帧归一化） | `load_and_integrate_images(files, settings)` | `profiles/frames/*.dat`（可选）、`norm/frame_qc.csv`（逐帧 TB/SR/低 q 强度/离群标记） |
| 平均 | `average()` | `profiles/01_control/control_avg.dat`、`profiles/02_sample/sample_avg.dat` |
| control 相对缩放 | `scaleRelative(f)` | `profiles/01_control/control_avg_scaled.dat` |
| 扣减 | `subtract()` | `profiles/03_subtracted/subtracted.dat` |
| 多区间 Guinier | `auto_guinier` + `guinier_fit(idx_min, idx_max)` | `profiles/04_guinier/guinier_<qlo>-<qhi>.dat` × N + `recommended_range.dat`、`tables/guinier_multi_range.csv` + `guinier_results.json` |
| IFT / P(r) | `bift(idx_min, idx_max, settings)`（设 `minDmax/maxDmax/DmaxPoints/PrPoints`）**跑两次**：起点=分析窗起点 / 起点=Guinier 拟合自己的起点；按闸门挑可信的一次 | `ifts/bift.ift`、`ifts/pr.dat`、`ifts/ift_fit.dat`、`tables/ift_summary.csv`（两次都给）+ `ift_dmax_sweep.csv`（`--ift-sweep N`） |
| 分子量 | `mw_vp` / `mw_vc`（+ ATSAS 时 `mw_bayes`/`mw_datclass`） | `tables/mw.csv` |
| 3D | `denss`（原生，唯一内置；**IFT 不可信时直接跳过**，不拿坏 P(r) 去建模型）/ `dammif`（ATSAS，GUI 里跑） | `models/denss.mrc`(+support/stats)、`tables/shape_results.json` |
| 报告 / 工作区 | `save_report` / `save_workspace` | `reports/raw_report.pdf`、`<样品>_workspace.hdf5`（GUI 直接打开看） |
| 总览图 | matplotlib（只画 RAW 返回的数与拟合线） | `qc.png`（log-log / Kratky / Guinier fan / P(r) / IFT fit / Dmax sweep）、`summary.json` |

**多区间 Guinier 是"让用户复核拟合过程"的主产物**：不给区间时，脚本以 `auto_guinier` 的 Rg 为锚，
起点取 {第 0 点, auto 的 qmin, 窗口的 5/10/15/20%}、终点取 qRg ∈ {0.8, 1.0, 1.2, 1.3} 的笛卡尔积，
**每个区间一份 `setQrange` 截断后的 profile 副本**（`.dat`）+ 表里 14 列判据，拟合线一律用 RAW 返回的 Rg/I0 画。
脚本自己只做**残差统计**（`chi2_red` 与 smile/frown 符号），不做拟合。

完成标准：`summary.json` 里每个节点都有值或明确的失败原因；`profiles/04_guinier/` 的份数 = 表里的区间数。

### Step 2 — 一批样品一起跑 + 汇总（整条稀释序列/整批数据）

```bash
RAW=<项目>/data/Tube-SAXS            # 原始帧
PRO=<项目>/processed/Tube-SAXS       # 产物根（与 data/ 同级）
for d in "$RAW"/*/; do               # 3 个并行足够（BIFT 单进程、DENSS Fast 几秒）
  python run-raw-tube-pipeline.py --sample-dir "$d" --cfg <项目>/data/<日期>.cfg \
    --out-dir "$PRO/$(basename "$d")" --model-engine denss --denss-mode Fast \
    > "$PRO/_logs/$(basename "$d").log" 2>&1
done
python summarize-tube-run.py "$PRO"        # → $PRO/_summary/summary.csv + summary.md
python plot-tube-overview.py "$PRO"        # → $PRO/_summary/overview.png
```

`summarize-tube-run.py` 只读各目录已产出的 `summary.json` / `tables/*.json` / `tables/*.csv`，
一行一个样品（31 列：control 缩放因子、contrast、auto-Guinier 的 I0/Rg/q/R²、推荐区间与四条闸门、
区间 Rg 跨度、IFT 两次的 Dmax/Rg_real/chisq/是否可信、MW Vp·Vc、DENSS 的 chi²/Rg_model/体积），
并对**编号连续的同名系列**（如 `A5-05-*`）额外加一节稀释检查（I0 与 I0/I0(首)、Rg、是否通过闸门）。
`plot-tube-overview.py` 出四联图：全部扣减曲线（log-log）/ Kratky / I(0) 柱状 / Rg（auto 与 IFT 对照，绿圈=IFT 可信）。
两个脚本都**不做任何拟合**，只搬运产物里的数。

## 复核点（先看这几处，再看数字）

1. `tables/guinier_multi_range.csv`：**Rg 是否随区间漂移**、`chi2_red` 是否≈1、`curvature` 的符号（>0 smile=聚集 / <0 frown=排斥）、
   `qRg_max` 是否越过形状上界（球≈1.3）。脚本给的 `recommended` 只是"在通过闸门的区间里最宽的那个"，
   不通过时会明确写 **NOT recommended** 并给漂移范围——这时**没有可信 Rg**，别报数。判据细节 → `assess-guinier-fit-quality`。
2. `qc.png` 的 Kratky：高 q 翘起来 = control 残留（回 Step 1 看 scale 因子）；峰位对应 `q·Rg≈1.7–2` 可做 Rg 的交叉验证。
3. `tables/ift_summary.csv`：`chisq` 与 `Rg_realspace` 是否和 Guinier 的 Rg 对得上（差 >10% 说明 IFT 的 q 范围或 Dmax 域不对）。
4. `tables/mw.csv`：Vp 与 Vc 是否一个量级；浓度未知（管式 `.txt` 里 `Concentration` 常是空的）→ 只能用浓度无关法 → `choose-a-molecular-weight-method`。
5. `models/`：DENSS 看 `chi2`、模型 Rg 与 `support_volume`；DAMMIF 要 ≥4 个模型看 a-score/NSD → `evaluate-a-shape-reconstruction`。
6. **跨样品一致性（一批数据最有用的判据）**：同一条稀释序列里 **I(0) 应随浓度成比例、Vc-MW 应恒定**——
   本机实测 `A5-05-1…6`：I0 = 64.1/35.4/19.8/10.4/5.1/2.3（每步≈减半，共 28 倍），而 **Vc-MW 恒定在 18.5–20.9 kDa**，
   这两条一起说明"同一物种、浓度在变"，比任何单条曲线的 Rg 都可信；反之若 Vc-MW 随稀释漂移，就是浓度/对照出了问题（→ `choose-a-molecular-weight-method`）。

## 坑（都是实测撞出来的）

- **`.cfg` 的两处默认值**：`ImageHdrFormat=None` + `EnableNormalization=False` → 逐帧 txt 根本没读，**静默**不归一化。
  脚本强制改掉；手工用 GUI 时记得在 Advanced Options 里改。
- **在 RAW 源码目录里跑会 ImportError `bioxtasraw.sascalc_exts`**：源码树遮蔽 site-packages。
- **control 缩放因子要取"粒子不散射"的 q 窗**：窗取得太低（比如 q 0.15–0.25）会把蛋白自己的信号当背景扣掉
  （本机 A5-05-1 实测：q 0.15–0.25 给 1.09，q 0.30–0.44 给 1.024 —— 前者明显偏大）。
- **`save_workspace` 会把扩展名换成 `.hdf5`**（传 `xx.rwa` 得到 `xx.hdf5`），别以为没写成功。
- **BIFT 的 Dmax 会跑出搜索域**（RAWAPI 文档原文：*"The value of Dmax can go beyond this bound in the optimization step"*）：
  实测 `A5-05-6` 用 48–109 Å 的网格交出 **Dmax=741 Å、chisq=1.09**——一个看着完美的假解；之前直接拿去建 DENSS，
  得到 `Rg_model=266 Å / support 6.95e7 Å³` 的垃圾。本 skill 的对策：BIFT **跑两次**（分析窗起点 / Guinier 拟合自己的起点），
  三条闸门判可信（Rg 与 Guinier 对得上、`Dmax ≤ 4.5·Rg`、Dmax 未越出搜索网格 1.5 倍；Guinier 自身没通过闸门时 Rg 那条放宽到 25% 并标 `rg_ref_soft`）；
  **不可信就不建 3D、不报 P(r)**，只留 `ifts/*_untrusted_*.ift` 供目视。修正后同一条数据变成 `Rg_model=22.5 Å / 6.7e4 Å³`。
- **BIFT 失败的样子**也可能是 `dmax` 顶在搜索域上限、`chisq` 几十：先看 Dmax 域是不是太宽，再看 q 上界是不是把噪声区也喂进去了。
- **ATSAS 不在**：`GNOM/DAMMIF/DAMMIN/DATGNOM/DATMW/DATCLASS/CIFSUP/CRYSOL` 全不可用；
  GUI 菜单仍然显示这些项，`Tools → ATSAS → GNOM` 会直接弹 "Can't find ATSAS"（这就是无 ATSAS 的判定点）。
  装好后 `--atsas-dir <ATSAS>/bin` 即可切换；ATSAS 学术免费但要个性化 license。
- **稀释序列不要只看最稀那条**：本机 A5-05-1…6 是 2 倍稀释序列（I0 65.5/35.8/20.2/10.9/5.3/2.4），
  最稀的一条低 q 信噪比最差、区间选择最不稳；判 Rg 要沿序列看一致性。

## 相关 skills

- **organize-batch-saxs-dataset** — 上游第 0 步：把平铺的下机 batch 拆成"每样品一个文件夹 + 前后背景"（样品身份取帧 1 的 `Description`，不靠文件名子串猜）。
- **run-a-sec-saxs-pipeline-end-to-end** — 姐妹 skill：SEC 连续洗脱帧走那条（差别在 control 来自 series 的峰前帧、要补逐帧 txt、要归一化视频）。
- **reduce-saxs-frames-to-curves** — 单点版本：帧→曲线这一步的判据（`A_`/`S_`/`*` 自检信号、CorMap 相似性）。
- **assess-guinier-fit-quality** — 本 skill 表的读法：q·Rg 上下界、残差形态、Kratky 交叉验证。
- **compute-and-validate-p-of-r** — BIFT/GNOM/DIFT 怎么选、Dmax 怎么定、P(r) 判据。
- **choose-a-molecular-weight-method** — 浓度未知时哪几法能用。
- **evaluate-a-shape-reconstruction** / **script-raw-with-the-python-api** — 重建评估 / RAWAPI 骨架与返回元组。
