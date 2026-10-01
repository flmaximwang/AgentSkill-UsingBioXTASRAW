#!/usr/bin/env python3
"""按入射光强监视器逐帧归一化 tif 序列（BL19U2 / Ionchamber 风格）。

把两个**必须分开**的时长作为显式参数：
  * --exposure：每帧曝光时长（决定取监视器的窗口有多宽）
  * --interval：帧与帧之间的采样间隔（含曝光后的空白，如 1.5 s 曝光 + 0.01 s 空白 = 1.51 s）
两者不可混用：窗口宽度用 exposure，时间轴推进/lag 换算用 interval。

另两个实测得来、必须暴露的参数：
  * --smooth：监视器滑动中位数窗口（帧）。监视器的逐帧快抖动是仪表噪声，直接逐帧除会把噪声灌进数据。
  * --lag-frames / --lag-auto：监视器时间轴相对采集日志的偏移。两端时钟可能不同步
    （本机实测 BL19U2 上差 48 s），--lag-auto 会扫描并给出建议值。
"""
import argparse
import csv
import datetime as dt
import glob
import os
import sys

import numpy as np

WORKERS = 6
FMT = argparse.ArgumentDefaultsHelpFormatter


# ---------------------------------------------------------------- 解析
def parse_monitor(path):
    """监视器文件：'#Time:YYYY-MM-DD hh:mm:ss' 头 + 'hh:mm:ss  value' 行（时间可能只有整秒）。"""
    t, v, date = [], [], None
    for line in open(path, errors="ignore"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            if s.startswith("#Time:"):
                date = dt.datetime.fromisoformat(s.split(":", 1)[1].strip()).date()
            continue
        p = s.split()
        try:
            hh, mm, ss = p[0].split(":")
            if date is None:
                raise SystemExit(f"监视器文件缺少 '#Time:YYYY-MM-DD ...' 头，无法定位日期: {path}")
            t.append(dt.datetime.combine(date, dt.time(int(hh), int(mm), int(float(ss)))).timestamp())
            v.append(float(p[-1]))
        except (ValueError, IndexError):
            continue
    if not t:
        raise SystemExit(f"监视器文件没有解析出数据点: {path}")
    return np.array(t), np.array(v)


def parse_log(path):
    """采集日志：'t_req t_meas endTime  /path/to/file.tif'。返回每帧 endTime（秒）与文件名。"""
    end, names = [], []
    for ln in open(path, errors="ignore"):
        p = ln.split()
        if len(p) >= 4 and ln.rstrip().endswith(".tif"):
            try:
                end.append(dt.datetime.fromisoformat(p[2]).timestamp())
            except ValueError:
                continue
            names.append(os.path.basename(p[-1]))
    if not end:
        raise SystemExit(f"采集日志没有解析出帧: {path}")
    return np.array(end), names


def runmed(x, w):
    h = max(0, w // 2)
    return np.array([np.median(x[max(0, i - h):min(len(x), i + h + 1)]) for i in range(len(x))])


def monitor_per_frame(tmon, vmon, end, exposure, interval, lag_frames, n):
    """每帧曝光窗口 [te-exposure, te] 内监视器的中位数；te = endTime + lag*interval。"""
    raw = np.full(n, np.nan)
    for i in range(n):
        te = end[i] + lag_frames * interval
        m = (tmon >= te - exposure) & (tmon <= te)
        raw[i] = np.median(vmon[m]) if m.any() else np.nan
    idx = np.arange(n)
    ok = np.isfinite(raw)
    if ok.sum() < n:
        print(f"  警告: {n - ok.sum()} 帧的曝光窗口内没有监视器采样，已线性插值")
    return np.interp(idx, idx[ok], raw[ok])


def process_one(args):
    from PIL import Image
    import fabio
    i, src, dst, fac = args
    img = fabio.open(src).data
    x = img.astype(np.float64) * fac
    rng = np.random.default_rng(1000000 + i)
    out = np.floor(x + rng.random(x.shape)).astype(np.int32)
    Image.fromarray(out).save(dst, format="TIFF")
    return i, float(img.sum()), float(out.sum())


# ---------------------------------------------------------------- 主流程
def scan_lag(tot, tmon, vmon, end, exposure, interval, smooth, metric="corr",
             scan=60, step=2, subsample=4):
    """扫 lag。两个判据都打印：
      corr = 平滑后（检测器总计数 vs 监视器）的相关系数 —— 细粒度、稳健，默认用它；
      step = 归一化后最大相邻块台阶（块=48 帧）—— 粒度粗（一个块 72 s），只作交叉核对。
    """
    n = len(tot)
    sub = np.arange(0, n, subsample)
    d_sub = runmed(tot, smooth)[sub]
    d_sub = d_sub / d_sub.mean()
    B = max(10, (n // subsample) // 40)
    rows = []
    for lag in range(-scan, scan + 1, step):
        sm_full = runmed(monitor_per_frame(tmon, vmon, end, exposure, interval, lag, n), smooth)
        sm = sm_full[sub]
        sm = sm / sm.mean()
        c = float(np.corrcoef(d_sub, sm)[0, 1])
        r = tot / sm_full
        lv = np.array([np.median(r[i:i + B]) for i in range(0, n - B + 1, B)])
        lv = lv / np.median(lv)
        rows.append((lag, c, float(np.abs(np.diff(lv)).max() * 100)))
    print(f"\n=== lag 扫描（步长 {step} 帧；corr 越高越好，max step 越低越好）===")
    print(f"{'lag(帧)':>9}{'lag*interval (s)':>18}{'corr':>9}{'max step %':>12}")
    for lag, c, st in rows:
        print(f"{lag:>9}{lag * interval:>18.0f}{c:>9.4f}{st:>12.2f}")
    by_corr = max(rows, key=lambda r: r[1])
    by_step = min(rows, key=lambda r: r[2])
    print(f"→ corr 最优: --lag-frames {by_corr[0]} ({by_corr[0]*interval:.0f} s, corr {by_corr[1]:.4f}, max step {by_corr[2]:.2f}%)")
    print(f"→ step 最优: --lag-frames {by_step[0]} ({by_step[0]*interval:.0f} s, corr {by_step[1]:.4f}, max step {by_step[2]:.2f}%)")
    if abs(by_corr[0] - by_step[0]) > 6:
        print(f"   注意: 两个判据相差 {by_corr[0]-by_step[0]} 帧（>6 帧）——建议以 corr 为准（细粒度），"
              f"step 判据的粒度就是一个块（{B} 帧）")
    best = by_corr if metric == "corr" else by_step
    print(f"→ 采用 --lag-frames {best[0]}  (≈ {best[0]*interval:.0f} s，判据 {metric})")
    return best[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=FMT)
    ap.add_argument("--src", required=True, help="原始 tif 所在目录")
    ap.add_argument("--monitor", required=True, help="入射光强监视器文件（如 bsa_1.Iochamber）")
    ap.add_argument("--log", required=True, help="采集日志（提供每帧 endTime）")
    ap.add_argument("--dst", default=None, help="输出目录（默认 <src>_norm_ionchamber）")
    ap.add_argument("--exposure", type=float, default=1.5, help="每帧曝光时长（s）；决定监视器取值窗口宽度")
    ap.add_argument("--interval", type=float, default=1.51, help="帧采样间隔（s，含曝光后的空白）；用于时间轴推进与 lag 换算")
    ap.add_argument("--lag-frames", type=int, default=0, help="监视器时间轴相对日志的偏移（帧）；正=监视器时间轴后移")
    ap.add_argument("--lag-auto", action="store_true", help="扫描 lag 并采用判据最优值（覆盖 --lag-frames）")
    ap.add_argument("--lag-metric", choices=["corr", "step"], default="corr",
                    help="lag 自动选择的判据：corr=相关系数（细粒度、默认）/ step=最大相邻块台阶（粒度粗）")
    ap.add_argument("--smooth", type=int, default=15, help="监视器滑动中位数窗口（帧）")
    ap.add_argument("--workers", type=int, default=WORKERS, help="写盘并行进程数")
    ap.add_argument("--limit", type=int, default=None, help="只处理前 N 帧（试跑用）")
    ap.add_argument("--dry-run", action="store_true", help="只做诊断与 lag 扫描，不写文件")
    args = ap.parse_args()

    dst = args.dst or os.path.join(os.path.dirname(os.path.normpath(args.src)),
                                   os.path.basename(os.path.normpath(args.src)) + "_norm_ionchamber")
    files = sorted(glob.glob(os.path.join(args.src, "*.tif")))
    if not files:
        raise SystemExit(f"{args.src} 下没有 tif")
    tmon, vmon = parse_monitor(args.monitor)
    end, _ = parse_log(args.log)
    n = min(len(files), len(end))
    if args.limit:
        n = min(n, args.limit)
    files = files[:n]

    # 前置检查：帧间隔与监视器采样密度（这两件事必须先量出来）
    d = np.diff(end[:n])
    npts = ((tmon >= end[0] - args.exposure) & (tmon <= end[-1] + 1e-6)).sum()
    print("=== 前置检查 ===")
    print(f"帧数 {n} | endTime 间隔: 中位 {np.median(d):.4f} s (min {d.min():.4f} / max {d.max():.4f})"
          f" | 与 --interval {args.interval} s {'一致' if abs(np.median(d) - args.interval) < 0.02 else '**不一致**'}")
    print(f"曝光 --exposure {args.exposure} s → 每帧空白 {np.median(d) - args.exposure:.4f} s")
    print(f"监视器 {len(tmon)} 点 / {(tmon[-1]-tmon[0]):.0f} s = {len(tmon)/(tmon[-1]-tmon[0]):.2f} 点/s"
          f" → 每帧窗口内约 {len(tmon)/(tmon[-1]-tmon[0])*args.exposure:.1f} 点")

    def collect_totals(idxs):
        import fabio
        return np.array([float(fabio.open(files[i]).data.sum()) for i in idxs])

    lag = args.lag_frames
    if args.lag_auto or args.dry_run:
        sub = np.arange(0, n, 4)
        tot_sub = collect_totals(sub)
        full = np.zeros(n)
        full[sub] = tot_sub
        interp = np.interp(np.arange(n), sub, tot_sub)
        tot_for_scan = np.where(full > 0, full, interp)
        lag = scan_lag(tot_for_scan, tmon, vmon, end, args.exposure, args.interval, args.smooth,
                       metric=args.lag_metric)
        if args.dry_run:
            print("\ndry-run：不写文件")
            return

    raw = monitor_per_frame(tmon, vmon, end, args.exposure, args.interval, lag, n)
    sm = runmed(raw, args.smooth)
    factor = np.median(sm) / sm
    print(f"\n采用 lag = {lag} 帧 (≈ {lag*args.interval:.0f} s) | 因子 {factor.min():.4f}~{factor.max():.4f} (中位 {np.median(factor):.4f})")

    os.makedirs(dst, exist_ok=True)
    tot_before = np.zeros(n); tot_after = np.zeros(n)
    from concurrent.futures import ProcessPoolExecutor
    tasks = [(i, files[i], os.path.join(dst, os.path.basename(files[i])), float(factor[i])) for i in range(n)]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for k, (i, b, a) in enumerate(ex.map(process_one, tasks, chunksize=8), 1):
            tot_before[i], tot_after[i] = b, a
            if k % 200 == 0:
                print(f"  {k}/{n}", flush=True)

    with open(os.path.join(dst, "normalization_factors.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "end_time", "monitor_raw", "monitor_smooth", "factor",
                    "det_total_before", "det_total_after"])
        for i in range(n):
            w.writerow([i + 1, dt.datetime.fromtimestamp(end[i]).isoformat(), f"{raw[i]:.6e}",
                        f"{sm[i]:.6e}", f"{factor[i]:.6f}", f"{tot_before[i]:.1f}", f"{tot_after[i]:.1f}"])

    B = 50
    nb = n // B
    lv = lambda x: np.array([np.median(x[i * B:(i + 1) * B]) for i in range(nb)])
    lb, la = lv(tot_before), lv(tot_after)
    lb_r, la_r = lb / np.median(lb), la / np.median(la)
    hf = lambda x: float((x / runmed(x, 21) - 1).std() * 100)
    print(f"\n最大相邻块台阶: 前 {np.abs(np.diff(lb_r)).max()*100:.2f}%  后 {np.abs(np.diff(la_r)).max()*100:.2f}%")
    print(f"块间峰谷: 前 {(lb_r.max()-lb_r.min())*100:.2f}%  后 {(la_r.max()-la_r.min())*100:.2f}%")
    print(f"逐帧高频σ: 前 {hf(tot_before):.3f}%  后 {hf(tot_after):.3f}%  (应基本不变)")
    r = tot_after / tot_before / factor
    print(f"随机取整保真: mean((after/before)/factor)={np.mean(r):.6f} (应≈1)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    x = np.arange(1, n + 1)
    ax[0].plot(x, tot_before / np.median(tot_before), lw=0.6, label="detector total (before)")
    ax[0].plot(x, sm / np.median(sm), lw=1.4, label=f"monitor (smoothed, lag={lag})")
    ax[0].legend(); ax[0].set_ylabel("relative"); ax[0].set_title("Before normalization")
    ax[1].plot(x, tot_after / np.median(tot_after), lw=0.6, color="C2", label="detector total (after)")
    ax[1].plot(x, sm / np.median(sm), lw=1.4, label="monitor (smoothed)")
    ax[1].legend(); ax[1].set_ylabel("relative"); ax[1].set_title("After normalization")
    ax[2].plot(x, factor, lw=0.8, color="C3"); ax[2].set_ylabel("factor"); ax[2].set_xlabel("frame")
    ax[2].set_title(f"Per-frame factor (exposure={args.exposure}s, interval={args.interval}s, lag={lag} frames)")
    for a in ax:
        a.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(dst, "normalization_report.png"), dpi=130)

    with open(os.path.join(dst, "README.txt"), "w") as f:
        f.write(f"""归一化说明（frame_flux_normalization.py）
源目录  : {args.src}
监视器  : {args.monitor}
采集日志: {args.log}
参数    : exposure={args.exposure} s, interval={args.interval} s, smooth={args.smooth} 帧, lag={lag} 帧 (≈{lag*args.interval:.0f} s)
方法    : factor_i = median(smooth(monitor)) / smooth(monitor)_i，monitor_i = 该帧曝光窗口 [{args.exposure}s] 内监视器中位数
输出    : 与原图同名的 int32 tif（缩放后随机取整，E[out]=原值×因子）；normalization_factors.csv；normalization_report.png
边界    : 只修“通量乘性起伏”；未扣缓冲液（请在 RAW 里对归一化后的序列扣减）；
          残余台阶若仍可见，来源是束位/几何（非通量）
""")
    print("完成 ->", dst)


if __name__ == "__main__":
    main()
