#!/usr/bin/env python3
"""SEC-SAXS 基线校正（BioXTAS RAW Python API）— correct-sec-saxs-baseline 的可执行入口。

安装（PyPI 上没有 bioxtasraw，官方要求从源码装）：
    git clone https://github.com/jbhopkins/bioxtasraw.git && cd bioxtasraw
    pip install .            # 不用 GUI 时无需 wx

用法（默认值见 --help；帧号一律指 series 的帧索引，与 RAW 界面显示的帧号一致）：
    python baseline_correction.py series.hdf5 --type integral
    python baseline_correction.py series.hdf5 --type linear --start 30 60 --end 900 930
    python baseline_correction.py first_profile.dat --buffer 504 562 --type integral --outdir ./api_results
"""

import argparse
import os
import sys


def parse_args():
    """单一来源：所有参数、默认值与单位在 argparse 里声明一次（不在 docstring 里另抄一份）。"""
    p = argparse.ArgumentParser(
        description="Apply a baseline correction to a SEC-SAXS series (BioXTAS RAW API).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("series",
                   help="输入：RAW 保存的 series (.hdf5)，或系列首个 profile 的路径 (.dat)")
    p.add_argument("--type", choices=["integral", "linear"], default="integral",
                   help="校正类型：integral=毛细管污垢/随剂量累积的漂移；linear=束流或仪器漂移")
    p.add_argument("--start", nargs=2, type=int, metavar=("BEGIN", "END"), default=None,
                   help="基线参考区①的帧号区间；linear 必填，integral 留空则自动搜索")
    p.add_argument("--end", nargs=2, type=int, metavar=("BEGIN", "END"), default=None,
                   help="基线参考区②的帧号区间；linear 必填，integral 留空则自动搜索")
    p.add_argument("--buffer", nargs=2, type=int, metavar=("BEGIN", "END"), default=None,
                   help="缓冲液帧区间；仅当 series 尚未做过缓冲液扣减时需要提供")
    p.add_argument("--window", type=int, default=5, metavar="N",
                   help="逐帧参数的滑动平均窗口长度 [帧]")
    p.add_argument("--outdir", default="./api_results", metavar="DIR",
                   help="输出目录")
    p.add_argument("--outname", default="series_bl.hdf5", metavar="FILE",
                   help="输出 series 文件名（含区域选择与基线设置，可被 RAW 直接重开）")
    return p.parse_args()


def main():
    args = parse_args()

    try:
        import bioxtasraw.RAWAPI as raw
    except ImportError:
        sys.exit("找不到 bioxtasraw：请在 RAW 源码目录执行 `pip install .`（PyPI 上没有该包）")

    # --- 1. 载入 series：.hdf5 直读；否则把同一系列的 .dat 一起载入再拼成 series -------------
    if args.series.lower().endswith(".hdf5"):
        series = raw.load_series([args.series])[0]
    else:
        import glob
        pattern = os.path.join(os.path.dirname(args.series), "*.dat")
        names = sorted(glob.glob(pattern))
        if not names:
            sys.exit(f"没有在 {os.path.dirname(args.series)} 找到 .dat 文件")
        series = raw.profiles_to_series(raw.load_profiles(names))

    # --- 2. 缓冲液扣减：只在系列尚未扣过时必须（官方 note） ------------------------------
    if args.buffer is not None:
        sub_profiles, rg, rger, i0, i0er, vcmw, vcmwer, vpmw = raw.set_buffer_range(
            series, [[args.buffer[0], args.buffer[1]]], window_size=args.window)

    # --- 3. 基线参考区：linear 必须人工给；integral 可自动找（find_baseline_range 只支持 integral）
    if args.start is None or args.end is None:
        if args.type == "linear":
            sys.exit("linear 校正必须显式给出 --start 与 --end（官方：自动搜索仅支持 integral）")
        start_found, end_found, start_range, end_range = raw.find_baseline_range(
            series, baseline_type="Integral")
        if not (start_found and end_found):
            sys.exit("自动搜索未能找到基线参考区，请用 --start/--end 手动指定")
        start_range, end_range = list(start_range), list(end_range)
        print(f"[auto] baseline start={start_range} end={end_range}")
    else:
        start_range, end_range = list(args.start), list(args.end)

    # --- 4. 参考区体检（integral 的自动搜索已内含；linear 的校验官方称为"用处不大"） -------
    ok, *details = raw.validate_baseline_range(series, start_range, end_range,
                                               args.type.capitalize())
    print(f"[validate] baseline range valid={ok}  details={details}")

    # --- 5. 做校正：返回逐帧 Rg/I(0)/MW(Vc)/MW(Vp) 与校正后的曲线 -------------------------
    (bl_profiles, rg, rger, i0, i0er, vcmw, vcmwer, vpmw,
     bl_corr, fit_results) = raw.set_baseline_correction(
        series, start_range, end_range, args.type.capitalize(),
        int_type="total", window_size=args.window)

    # --- 6. 在“已校正”曲线上重选样品区并出曲线 ------------------------------------------
    found, s, e = raw.find_sample_range(series, profile_type="baseline")
    if not found:
        print("[warn] 样品区自动搜索失败：请在 GUI 里确认平台区后再导出", file=sys.stderr)
    else:
        raw.set_sample_range(series, [[s, e]], profile_type="baseline")
        print(f"[sample] range={s}-{e}")

    # --- 7. 保存：series 里含区域选择与基线设置，谁都能重放这次判断 -----------------------
    os.makedirs(args.outdir, exist_ok=True)
    raw.save_series(series, args.outname, args.outdir)
    print(f"[save] {os.path.join(args.outdir, args.outname)}")

    # --- 8. 过校正自检（对应 skill 的第 6 步）：按 q 区间看校正量在高 q 是否异常 -----------
    print("[check] 过校正通常露在高 q：请在 RAW 里把强度显示切成 q 区间"
          "（0.01-0.02 / 0.05-0.06 / 0.1-0.2 / 0.2-0.27 Å⁻¹）逐段核对；"
          "若确认高 q 是噪声主导，先把曲线截断到较低 q 再重跑本脚本。")


if __name__ == "__main__":
    main()
