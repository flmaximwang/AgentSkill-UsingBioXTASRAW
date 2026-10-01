#!/usr/bin/env python3
"""SEC-SAXS 分块台阶校正（每 N 帧整体偏移）— BioXTAS RAW API。

适用症状：强度-帧号曲线上每隔固定帧数（例如每 300 帧）出现一次**整体台阶**。
阶梯不是平滑漂移：RAW 的 Linear（一条直线）与 Integral（只允许单调不降）都不是为它设计的，
而 RAW 的多个缓冲液区会被平均成**一条**全局缓冲液，也不是"块内缓冲液"。
本脚本按块估计该块自身的水平，再对整块做乘性或加性校正。

估计水平用的帧：默认**自动排除洗脱峰**（按总积分强度 median+3×MAD 判峰），
也可用 --est-frames 显式给定"只有背景"的帧区间；--buffer 只用于最后重算扣减。

安装 RAW API（PyPI 上没有 bioxtasraw）见 ../references/sec-saxs-baseline-api.md。

用法（默认值与单位见 --help）：
    python block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --dry-run
    python block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --mode scale --buffer 0 250
    python block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --est-frames 0 260 --mode offset
"""

import argparse
import os
import statistics
import sys


def parse_args():
    """所有参数、默认值与单位在 argparse 里声明一次（不在 docstring 里另抄一份）。"""
    p = argparse.ArgumentParser(
        description="Correct per-block step offsets in a SEC-SAXS series (BioXTAS RAW API).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("series", help="输入：RAW 保存的 series (.hdf5)，或系列首个 profile 的路径 (.dat)")
    p.add_argument("--block", type=int, default=300, metavar="N",
                   help="每块帧数（台阶周期）[帧]")
    p.add_argument("--mode", choices=["scale", "offset"], default="scale",
                   help="校正类型：scale=乘性（束流强度变化，各 q 同比例）；offset=加性（常数平移）")
    p.add_argument("--q-ref", type=float, default=0.20, metavar="Q",
                   help="估计每块水平的参考 q [Å⁻¹]（挑背景主导、不含样品信号的 q）")
    p.add_argument("--est-frames", nargs=2, type=int, metavar=("BEGIN", "END"), default=None,
                   help="估计水平时只用的帧区间；不给则自动排除洗脱峰")
    p.add_argument("--peak-mad", type=float, default=3.0, metavar="K",
                   help="自动判峰的阈值：总积分强度 > median + K×MAD 的帧视为峰内帧并排除")
    p.add_argument("--ref-block", type=int, default=1, metavar="B",
                   help="以第几块为基准（校正后该块不变）")
    p.add_argument("--buffer", nargs=2, type=int, metavar=("BEGIN", "END"), default=None,
                   help="缓冲液帧区间；给了就在校正后按它重算扣减曲线")
    p.add_argument("--window", type=int, default=5, metavar="N",
                   help="扣减时的滑动平均窗口长度 [帧]")
    p.add_argument("--dry-run", action="store_true",
                   help="只打印每块水平与校正量，不修改、不写文件")
    p.add_argument("--outdir", default="./api_results", metavar="DIR", help="输出目录")
    p.add_argument("--outname", default="series_stepfix.hdf5", metavar="FILE", help="输出 series 文件名")
    return p.parse_args()


def estimator_frames(series, args):
    """返回用于估水平的帧索引列表：显式区间优先，否则自动排除洗脱峰。"""
    n = len(series.getAllSASMs(int_type="unsub"))
    if args.est_frames is not None:
        return [i for i in range(n) if args.est_frames[0] <= i <= args.est_frames[1]]
    ints = list(series.getIntI(int_type="unsub"))
    med = statistics.median(ints)
    mad = statistics.median([abs(v - med) for v in ints]) or 1.0
    thr = med + args.peak_mad * mad
    keep = [i for i, v in enumerate(ints) if v <= thr]
    print(f"[peak] 总强度 median={med:.6g} MAD={mad:.6g} 阈值={thr:.6g} "
          f"→ 排除 {n - len(keep)} 帧，保留 {len(keep)} 帧用于估水平")
    return keep


def block_levels(sasms, q_ref, block, keep):
    """每块的水平（中位数）与估计帧数；块内无可用帧时为 None。"""
    levels, counts = [], []
    for start in range(0, len(sasms), block):
        idx = [i for i in range(start, min(start + block, len(sasms))) if i in keep]
        vals = [sasms[i].getIofQ(q_ref) for i in idx]
        vals = [v for v in vals if v is not None and v == v]  # 去 NaN
        levels.append(statistics.median(vals) if vals else None)
        counts.append(len(vals))
    return levels, counts


def fill_missing(levels):
    """没有可用帧的块，用相邻有估计的块线性插值；返回 (levels, 被插值的块序号)。"""
    filled, gap = list(levels), []
    known = [i for i, v in enumerate(levels) if v is not None]
    if not known:
        return filled, gap
    for i, v in enumerate(filled):
        if v is not None:
            continue
        lo = max([k for k in known if k < i], default=None)
        hi = min([k for k in known if k > i], default=None)
        if lo is None or hi is None:
            v = levels[lo if hi is None else hi]
        else:
            w = (i - lo) / (hi - lo)
            v = levels[lo] * (1 - w) + levels[hi] * w
        filled[i] = v
        gap.append(i)
    return filled, gap


def main():
    args = parse_args()

    try:
        import bioxtasraw.RAWAPI as raw
    except ImportError:
        sys.exit("找不到 bioxtasraw：请按 references/sec-saxs-baseline-api.md 从源码安装 RAW API（PyPI 上没有该包）")

    # --- 1. 载入 series ---------------------------------------------------------------
    if args.series.lower().endswith(".hdf5"):
        series = raw.load_series([args.series])[0]
    else:
        import glob
        names = sorted(glob.glob(os.path.join(os.path.dirname(args.series), "*.dat")))
        if not names:
            sys.exit(f"没有在 {os.path.dirname(args.series)} 找到 .dat 文件")
        series = raw.profiles_to_series(raw.load_profiles(names))

    sasms = series.getAllSASMs(int_type="unsub")
    n_block = (len(sasms) + args.block - 1) // args.block
    print(f"[load] 帧数={len(sasms)}  每块={args.block} 帧  共 {n_block} 块  "
          f"参考 q={args.q_ref} Å⁻¹  模式={args.mode}")

    # --- 2. 逐块估水平（自动排除峰） ---------------------------------------------------
    keep = set(estimator_frames(series, args))
    levels, counts = block_levels(sasms, args.q_ref, args.block, keep)
    levels, gap = fill_missing(levels)
    if gap:
        print(f"[warn] 这些块没有可用估计帧，水平由相邻块插值：{[b + 1 for b in gap]}")
    if len([c for c in counts if c]) < 2:
        print("[warn] 只有不到两块有估计帧：无法可靠区分'台阶'与'渐变'，"
              "请用 --est-frames 指定更广的背景帧区间，或核对 --q-ref 是否被样品信号污染")

    ref_idx = min(max(args.ref_block - 1, 0), len(levels) - 1)
    ref = levels[ref_idx]
    print(f"[levels] 基准为第 {ref_idx + 1} 块：I(q={args.q_ref}) = {ref:.6g}")
    print("  block  frames          level          correction")
    for b, (lv, cnt) in enumerate(zip(levels, counts)):
        s0, s1 = b * args.block, min((b + 1) * args.block, len(sasms)) - 1
        corr = (f"scale ×{ref / lv:.6f}" if args.mode == "scale" else f"offset {ref - lv:+.6g}")
        tag = "  (基准)" if b == ref_idx else ""
        print(f"  {b + 1:5d}  [{s0:5d},{s1:5d}]  {lv:12.6g}  {corr}   (n={cnt}){tag}")

    if args.dry_run:
        print("[dry-run] 未做任何修改。判型提示：若台阶在**透射/入射通量**曲线里出现在同样的帧号上，"
              "说明是束流强度变化 → 逐帧按通量归一化才是正解（本脚本只是替代手段）；"
              "若高 q 与低 q 的台阶绝对高度相同 → 用 --mode offset。")
        return

    # --- 3. 应用校正（写进 raw 强度） --------------------------------------------------
    for b, lv in enumerate(levels):
        s0, s1 = b * args.block, min((b + 1) * args.block, len(sasms))
        for i in range(s0, s1):
            if args.mode == "scale":
                sasms[i].scaleRelative(ref / lv)
            else:
                sasms[i].offsetRawIntensity(ref - lv)

    # --- 4. 重算扣减（unsub 变了，sub 必须重来） --------------------------------------
    if args.buffer is not None:
        raw.set_buffer_range(series, [list(args.buffer)], window_size=args.window)
        print("[subtract] 已按原缓冲液区重算扣减曲线")
    else:
        print("[warn] 未给 --buffer：只改了原始曲线，扣减曲线未重算（请在 GUI 或 API 里重设缓冲液区）")

    # --- 5. 保存 ---------------------------------------------------------------------
    os.makedirs(args.outdir, exist_ok=True)
    raw.save_series(series, args.outname, args.outdir)
    print(f"[save] {os.path.join(args.outdir, args.outname)}")
    print("[next] 1) 若块级水平本身仍在平滑漂移 → 再上 RAW 的 Linear 基线校正；"
          "2) 若台阶与通量曲线同位置 → 回到逐帧通量归一化（本脚本治不了）")


if __name__ == "__main__":
    main()
