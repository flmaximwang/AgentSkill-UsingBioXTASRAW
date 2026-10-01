#!/usr/bin/env python
"""End-to-end SAXS pipeline for TUBE / static samples (BL19U2 batch mode), driven
entirely by BioXTAS RAW's own algorithms through bioxtasraw.RAWAPI.

    frames -> integrate -> average -> control scaling -> subtract
           -> multi-range Guinier (gated) -> IFT/P(r) (gated) -> MW -> 3D -> report

Every node is written to disk; every profile is written as .dat.

    python run-raw-tube-pipeline.py --sample-dir <dir> --cfg <day>.cfg --out-dir <out> \
        [--steps integrate,average,subtract,guinier,ift,mw,shape,report,workspace]

The sibling skill `run-a-sec-saxs-pipeline-end-to-end` covers SEC elution series;
this one covers static/tube datasets where each sample run sits next to its own
control runs in the same directory.

Nothing here re-implements integration / Guinier / IFT / reconstruction: the script
only sets parameters and writes files.  RAW does the maths.
"""
from __future__ import annotations

import argparse, glob, json, os, re, shutil, sys, time
from collections import Counter

import numpy as np
import bioxtasraw.RAWAPI as raw


# --------------------------------------------------------------------------- helpers
def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def jdump(obj, path):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def mkdirs(root, *subs):
    for s in subs:
        os.makedirs(os.path.join(root, s), exist_ok=True)


class Ctx:
    """RAW settings + output layout shared by all nodes."""

    def __init__(self, cfg, out, hdr_format, atsas_dir=None, save_frames=False):
        self.out = os.path.abspath(os.path.expanduser(out))
        self.save_frames = save_frames
        mkdirs(self.out, "frames", "norm", "profiles", "profiles/01_control",
               "profiles/02_sample", "profiles/03_subtracted", "profiles/04_guinier",
               "profiles/06_ift", "tables", "ifts", "models", "reports")
        self.s = raw.load_settings(cfg)
        # A .cfg saved at the beamline usually has ImageHdrFormat=None and
        # EnableNormalization=False, so the per-frame .txt is never parsed and the
        # transmission normalization silently does nothing.  Force both.
        self.s.set("ImageHdrFormat", hdr_format)
        self.s.set("EnableNormalization", True)
        self.s.set("NormalizationList", [["/", "Transmitted_Beam"]])
        if atsas_dir:
            self.s.set("ATSASDir", atsas_dir)
        self.atsas_dir = self.s.get("ATSASDir") or ""
        self.has_atsas = bool(self.atsas_dir) and all(
            shutil.which(x) or os.path.exists(os.path.join(self.atsas_dir, x))
            for x in ("gnom", "dammif"))

    def set(self, key, value):
        self.s.set(key, value)

    def save(self, profile, name, *sub):
        raw.save_profile(profile, name, os.path.join(self.out, *sub), settings=self.s)


def classify(files, sample_key, control_keys):
    """Sample frames = prefix matching the sample key; everything else = control."""
    key = re.sub(r"[^0-9A-Za-z]", "", sample_key).lower()
    sam, ctl = [], []
    for f in files:
        b = re.sub(r"[^0-9A-Za-z]", "", os.path.basename(f).split("_")[0]).lower()
        if control_keys:
            (ctl if b in control_keys else sam).append(f)
        else:
            (sam if b == key else ctl).append(f)
    return sorted(sam), sorted(ctl)


# ------------------------------------------------------------------- node 1: frames
def node_integrate(ctx, sam_files, ctl_files):
    log("integrate %d sample + %d control frames" % (len(sam_files), len(ctl_files)))
    t = time.time()
    sam, _ = raw.load_and_integrate_images(sam_files, settings=ctx.s)
    ctl, _ = raw.load_and_integrate_images(ctl_files, settings=ctx.s)
    rows = []
    for i, p in enumerate(list(sam) + list(ctl)):
        h = p.getParameter("counters") or {}
        q, I = p.getQ(), p.getI()
        rows.append(dict(file=p.getParameter("filename"),
                         kind="sample" if i < len(sam) else "control",
                         description=h.get("Description", ""),
                         transmission=h.get("Transmitted_Beam", ""),
                         sr_current=h.get("SR_Current", ""),
                         exposure=h.get("Exposure_time_s", ""),
                         i_lowq=float(I[0]),
                         i_midq=float(I[int(np.argmin(abs(q - 0.2)))])))
        if ctx.save_frames:
            kind = "sample" if i < len(sam) else "control"
            ctx.save(p, "%s_%s.dat" % (kind, os.path.splitext(p.getParameter("filename"))[0]),
                     "frames")
    log("  integrated in %.1fs" % (time.time() - t))
    for kind in ("sample", "control"):
        vals = np.array([r["i_lowq"] for r in rows if r["kind"] == kind])
        if vals.size:
            med = float(np.median(vals))
            for r in rows:
                if r["kind"] == kind:
                    r["dev_from_median"] = r["i_lowq"] / med - 1.0
                    r["outlier"] = bool(abs(r["i_lowq"] / med - 1.0) > 0.15)
    with open(os.path.join(ctx.out, "norm", "frame_qc.csv"), "w") as fh:
        fh.write("file,kind,description,transmission,sr_current,exposure,i_lowq,i_midq,"
                 "dev_from_median,outlier\n")
        for r in rows:
            fh.write("%s,%s,%s,%s,%s,%s,%.6g,%.6g,%.4f,%d\n" % (
                r["file"], r["kind"], r["description"], r["transmission"], r["sr_current"],
                r["exposure"], r["i_lowq"], r["i_midq"], r.get("dev_from_median", float("nan")),
                int(r.get("outlier", False))))
    jdump(rows, os.path.join(ctx.out, "norm", "frame_qc.json"))
    bad = [r["file"] for r in rows if r.get("outlier")]
    log("  frames deviating >15%% from their run median: %s" % (bad if bad else "none"))
    return sam, ctl, rows


# ------------------------------------------------- node 2-4: average + subtract
def node_average_subtract(ctx, sam, ctl, scale_window=(0.30, 0.44), do_scale=True):
    sam_avg = raw.average(sam)
    ctl_avg = raw.average(ctl)
    ctx.save(ctl_avg, "control_avg.dat", "profiles", "01_control")
    ctx.save(sam_avg, "sample_avg.dat", "profiles", "02_sample")

    # The control runs are not measured at exactly the same flux/position as the
    # sample runs, so a 1-3 % level difference survives transmission normalization
    # and leaves a constant residual at high q which wrecks the IFT.  Read the
    # factor off the q window where the particle does not scatter and apply it with
    # RAW's own relative-scale operation.
    factor = 1.0
    q = ctl_avg.getQ()
    m = (q >= scale_window[0]) & (q <= scale_window[1])
    if do_scale and m.sum() >= 5:
        factor = float(np.mean(sam_avg.getI()[m] / ctl_avg.getI()[m]))
        if abs(factor - 1.0) > 1e-4:
            ctl_avg = ctl_avg.copy()
            ctl_avg.scaleRelative(factor)
            ctx.save(ctl_avg, "control_avg_scaled.dat", "profiles", "01_control")

    sub = raw.subtract([sam_avg], ctl_avg)[0]
    ctx.save(sub, "subtracted.dat", "profiles", "03_subtracted")
    q, I = sub.getQ(), sub.getI()
    i_sam = sam_avg.getI()
    hi = slice(int(len(q) * 0.6), int(len(q) * 0.8))
    info = dict(n_points=len(q), qmin=float(q[0]), qmax=float(q[-1]),
                control_scale_factor=factor, scale_window=list(scale_window),
                contrast_lowq=float(I[0] / i_sam[0]) if i_sam[0] else None,
                sample_over_control_midq=float(np.mean(i_sam[hi] / ctl_avg.getI()[hi])),
                negative_kratky_frac=float(np.mean((q ** 2 * I)[hi] < 0)))
    log("subtraction: control scale %.4f (q %.2f-%.2f) | contrast %.3f of sample I(q_min)"
        % (factor, scale_window[0], scale_window[1], info["contrast_lowq"]))
    if abs(factor - 1.0) > 0.05:
        log("  WARNING: scale factor %.3f deviates >5%% from 1 - check the control run"
            % factor)
    return sub, info


def pick_analysis_window(sub, snr_min=2.0, qmax_cap=0.35, run=20):
    """Largest q ending a contiguous run of points with I>0 and I/err >= snr_min."""
    q, I, E = sub.getQ(), sub.getI(), sub.getErr()
    snr = np.divide(I, E, out=np.zeros_like(I), where=E > 0)
    good = (snr >= snr_min) & (I > 0)
    cap = int(np.argmin(abs(q - qmax_cap)))
    for i in range(cap, -1, -1):
        if good[max(0, i - run + 1):i + 1].all():
            return 0, i
    return 0, 0


# --------------------------------------------------- node 5: multi-range Guinier
def _chi2_red(q, I, E, rg, i0, i0idx, i1idx):
    """Error-weighted reduced chi^2 of RAW's own fit line (residual statistic)."""
    m = slice(i0idx, i1idx + 1)
    fit = np.log(i0) - (rg ** 2 / 3.0) * q[m] ** 2
    res = np.log(I[m]) - fit
    sig = np.divide(E[m], I[m], out=np.full_like(res, np.nan), where=I[m] > 0)
    ok = np.isfinite(sig) & (sig > 0)
    if ok.sum() < 5:
        return np.nan, np.nan
    chi2 = float(np.sum((res[ok] / sig[ok]) ** 2) / (ok.sum() - 2))
    half = ok.sum() // 2
    curv = float(np.mean(res[ok][:half]) - np.mean(res[ok][half:]))   # >0 smile
    return chi2, curv


def node_guinier(ctx, sub, qmax_idx, r_gate_qrg, min_pts=10, chi2_max=3.0,
                 qrg_rungs=(0.8, 1.0, 1.2, 1.3), start_fracs=(0.05, 0.10, 0.15, 0.20)):
    q, I, E = sub.getQ(), sub.getI(), sub.getErr()
    auto = raw.auto_guinier(sub, settings=ctx.s)
    rg0 = auto[0] if auto[0] > 0 else 30.0

    starts = sorted({0,
                     int(np.argmin(abs(q - auto[4]))) if auto[4] > 0 else 0,
                     *[int(qmax_idx * f) for f in start_fracs]})
    ends = sorted({int(np.argmin(abs(q - min(qrg / rg0, q[qmax_idx])))) for qrg in qrg_rungs})

    rows = []
    for i0 in starts:
        for i1 in ends:
            if i1 <= i0 or i1 - i0 + 1 < min_pts:
                continue
            try:
                r = raw.guinier_fit(sub, i0, i1, settings=ctx.s)
            except Exception as e:
                rows.append(dict(idx_min=i0, idx_max=i1, failed=str(e)))
                continue
            rg, i0v, rg_e, i0_e, qmin, qmax, qrg_min, qrg_max, r2 = (
                r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
            chi2r, curv = _chi2_red(q, I, E, rg, i0v, i0, i1)
            half = (i0 + i1) // 2
            try:
                rg_split = abs(raw.guinier_fit(sub, i0, half, settings=ctx.s)[0] -
                               raw.guinier_fit(sub, half, i1, settings=ctx.s)[0]) / rg
            except Exception:
                rg_split = np.nan
            rows.append(dict(idx_min=i0, idx_max=i1, n_pts=i1 - i0 + 1, qmin=float(qmin),
                             qmax=float(qmax), rg=float(rg), rg_err=float(rg_e),
                             i0=float(i0v), i0_err=float(i0_e), qrg_min=float(qrg_min),
                             qrg_max=float(qrg_max), r_sqr=float(r2), chi2_red=chi2r,
                             curvature=curv, rg_split_rel=float(rg_split),
                             gates=dict(n_pts=i1 - i0 + 1 >= min_pts,
                                        qrg=(qrg_max <= r_gate_qrg),
                                        chi2=(np.isfinite(chi2r) and chi2r <= chi2_max),
                                        stable=(np.isfinite(rg_split) and rg_split <= 0.05))))

    ok_rows = [r for r in rows if "failed" not in r]
    good = [r for r in ok_rows if all(r["gates"].values())]
    rec = None
    if good:
        med = float(np.median([r["rg"] for r in good]))
        rec = sorted(good, key=lambda r: (-r["n_pts"], abs(r["rg"] - med)))[0]
        rec["reason"] = ("passes every gate; widest passing range with Rg at the median "
                         "of the passing set (Rg %.2f vs median %.2f)" % (rec["rg"], med))
    elif ok_rows:
        rec = sorted(ok_rows, key=lambda r: (r["chi2_red"], -r["n_pts"]))[0]
        fails = [k for k, v in rec["gates"].items() if not v]
        rec["reason"] = ("NOT recommended - no range passes all gates (failed: %s). Best "
                         "chi2_red=%.2f at q %.4f-%.4f, but Rg drifts %.2f-%.2f A across "
                         "ranges => the curve does not follow a single Guinier law "
                         "(polydispersity / residual background / wrong control)."
                         % (",".join(fails), rec["chi2_red"], rec["qmin"], rec["qmax"],
                            min(r["rg"] for r in ok_rows), max(r["rg"] for r in ok_rows)))

    # one profile copy per range, trimmed with RAW's own setQrange
    off = sub.getQrange()[0]
    for r in ok_rows:
        p = sub.copy()
        p.setQrange((off + r["idx_min"], off + r["idx_max"] + 1))
        ctx.save(p, "guinier_%.5f-%.5f.dat" % (r["qmin"], r["qmax"]), "profiles", "04_guinier")
    if rec:
        p = sub.copy()
        p.setQrange((off + rec["idx_min"], off + rec["idx_max"] + 1))
        ctx.save(p, "recommended_range.dat", "profiles", "04_guinier")

    jdump(dict(auto=dict(rg=float(auto[0]), i0=float(auto[1]), rg_err=float(auto[2]),
                         i0_err=float(auto[3]), qmin=float(auto[4]), qmax=float(auto[5]),
                         qrg_max=float(auto[7]), r_sqr=float(auto[10])),
               ranges=rows, recommended=rec, n_ranges=len(rows), n_passing=len(good)),
          os.path.join(ctx.out, "tables", "guinier_results.json"))
    with open(os.path.join(ctx.out, "tables", "guinier_multi_range.csv"), "w") as fh:
        fh.write("idx_min,idx_max,n_pts,qmin,qmax,Rg,Rg_err,I0,qRg_min,qRg_max,R2,chi2_red,"
                 "curvature,rg_split_rel,pass_n,pass_qRg,pass_chi2,pass_stable\n")
        for r in rows:
            if "failed" in r:
                fh.write("%d,%d,-,-,-,-,-,-,-,-,-,-,-,-,,,,\n" % (r["idx_min"], r["idx_max"]))
                continue
            g = r["gates"]
            fh.write("%d,%d,%d,%.5f,%.5f,%.3f,%.3f,%.2f,%.3f,%.3f,%.5f,%.3f,%.4f,%.4f,"
                     "%d,%d,%d,%d\n" % (r["idx_min"], r["idx_max"], r["n_pts"], r["qmin"],
                                        r["qmax"], r["rg"], r["rg_err"], r["i0"], r["qrg_min"],
                                        r["qrg_max"], r["r_sqr"], r["chi2_red"], r["curvature"],
                                        r["rg_split_rel"], g["n_pts"], g["qrg"], g["chi2"],
                                        g["stable"]))
    log("Guinier: auto Rg=%.2f (q %.4f-%.4f, R2=%.3f) | %d ranges, %d pass gates"
        % (auto[0], auto[4], auto[5], auto[10], len(rows), len(good)))
    log("  %s" % (rec["reason"] if rec else "no usable range"))
    return auto, rows, rec


# --------------------------------------------------------------- node 6: IFT / P(r)
def node_ift(ctx, sub, rec, i0, i1, dmax_scale=3.1, dmax_pts=10):
    """Run RAW's BIFT twice - once from the start of the analysis window, once from the
    Guinier fit's own start index - then keep the trusted one.

    Why both: BIFT's minDmax/maxDmax only bound the *grid search*; the joint optimiser may
    return a much larger Dmax (RAWAPI.bift docstring: "The value of Dmax can go beyond this
    bound in the optimization step").  Feeding the contaminated low-q points in is what makes
    it run away (measured: A5-05-6 gave Dmax=741 A from a 48-109 A window, chisq 1.09 - a
    perfect-looking fit to a meaningless P(r)).  RAW's own hint is `use_guinier_start`, i.e.
    start the IFT where the Guinier fit says the data become usable.
    """
    rg = rec["rg"] if rec else raw.auto_guinier(sub, settings=ctx.s)[0]
    lo, hi = max(10.0, 0.7 * dmax_scale * rg), max(30.0, 1.6 * dmax_scale * rg)
    ctx.set("minDmax", lo)
    ctx.set("maxDmax", hi)
    ctx.set("DmaxPoints", dmax_pts)
    ctx.set("PrPoints", 100)

    starts = [(i0, "window-start")]
    if rec and rec["idx_min"] > i0:
        starts.append((rec["idx_min"], "guinier-fit-start"))

    rows, ifts = [], {}
    for idx_min, tag in starts:
        log("IFT [%s]: q idx %d-%d, Dmax grid %.0f-%.0f A" % (tag, idx_min, i1, lo, hi))
        t = time.time()
        res = raw.bift(sub, idx_min=idx_min, idx_max=i1, settings=ctx.s, single_proc=True)
        ift = res[0]
        if ift is None or not (res[1] > 0):
            rows.append(dict(tag=tag, idx_min=idx_min, failed="BIFT returned no solution"))
            log("  failed")
            continue
        dmax, rgr, i0r, dmax_e, rgr_e = res[1], res[2], res[3], res[4], res[5]
        chisq = res[7]
        gates = dict(rg_vs_guinier=abs(rgr - rg) / rg <= 0.10,
                     dmax_over_rg=(dmax / rg) <= 4.5,
                     dmax_within_grid=(dmax <= 1.5 * hi))
        row = dict(tag=tag, idx_min=idx_min, qmin=float(sub.getQ()[idx_min]), qmax=float(sub.getQ()[i1]),
                   dmax=float(dmax), dmax_err=float(dmax_e), rg_realspace=float(rgr),
                   rg_err=float(rgr_e), i0=float(i0r), chisq=float(chisq),
                   seconds=time.time() - t, gates=gates, trusted=all(gates.values()))
        rows.append(row)
        ifts[tag] = ift
        log("  Dmax=%.1f+-%.1f  Rg(real)=%.1f  chisq=%.2f  trusted=%s  %s  (%.0fs)"
            % (dmax, dmax_e, rgr, chisq, row["trusted"], gates, row["seconds"]))

    trusted = [r for r in rows if r.get("trusted")]
    best = (min(trusted, key=lambda r: r["chisq"]) if trusted
            else (min([r for r in rows if "failed" not in r], key=lambda r: r["chisq"])
                  if any("failed" not in r for r in rows) else None))
    out = dict(runs=rows, chosen=best["tag"] if best else None,
               trusted=bool(best and best.get("trusted")))
    if not best:
        log("IFT: no usable solution - 3D will be skipped")
    elif not best.get("trusted"):
        log("IFT: no *trusted* solution (see gates); best is %s - 3D will be skipped and the "
            "P(r) must not be reported" % best["tag"])
    ift = ifts.get(best["tag"]) if best else None
    if ift is not None:
        raw.save_ift(ift, "bift.ift", os.path.join(ctx.out, "ifts"))
        np.savetxt(os.path.join(ctx.out, "ifts", "pr.dat"),
                   np.column_stack([ift.r, ift.p, ift.err]),
                   header="r(A)\tP(r)\terr\t[RAW BIFT, start=%s]" % best["tag"])
        np.savetxt(os.path.join(ctx.out, "ifts", "ift_fit.dat"),
                   np.column_stack([ift.q_orig, ift.i_orig, ift.err_orig, ift.i_fit]),
                   header="q\tI_measured\terr\tI_fit(BIFT)")
    jdump(out, os.path.join(ctx.out, "tables", "ift_summary.json"))
    with open(os.path.join(ctx.out, "tables", "ift_summary.csv"), "w") as fh:
        fh.write("tag,idx_min,qmin,qmax,Dmax,Dmax_err,Rg_realspace,Rg_err,I0,chisq,"
                 "pass_rg,pass_dmax_over_rg,pass_dmax_within_grid,trusted,seconds\n")
        for r in rows:
            if "failed" in r:
                fh.write("%s,%d,-,-,-,-,-,-,-,-,,,,,0\n" % (r["tag"], r["idx_min"]))
                continue
            g = r["gates"]
            fh.write("%s,%d,%.5f,%.5f,%.2f,%.2f,%.2f,%.2f,%.2f,%.4f,%d,%d,%d,%d,%.0f\n"
                     % (r["tag"], r["idx_min"], r["qmin"], r["qmax"], r["dmax"], r["dmax_err"],
                        r["rg_realspace"], r["rg_err"], r["i0"], r["chisq"], g["rg_vs_guinier"],
                        g["dmax_over_rg"], g["dmax_within_grid"], r["trusted"], r["seconds"]))
    return (ift if (best and best.get("trusted")) else None), out


def node_ift_sweep(ctx, sub, i0, i1, rg, n=5, span=0.35):
    center = 3.1 * rg
    rows = []
    for f in np.linspace(1.0 - span, 1.0 + span, n):
        d = center * f
        ctx.set("minDmax", max(10.0, d - 5.0))
        ctx.set("maxDmax", d + 5.0)
        try:
            r = raw.bift(sub, idx_min=i0, idx_max=i1, settings=ctx.s, single_proc=True)
            rows.append(dict(dmax_target=float(d), dmax=float(r[1]), rg=float(r[2]),
                             chisq=float(r[7])))
        except Exception as e:
            rows.append(dict(dmax_target=float(d), failed=str(e)))
        log("  Dmax sweep %.0f A -> %s" % (d, rows[-1].get("chisq", rows[-1].get("failed"))))
    with open(os.path.join(ctx.out, "tables", "ift_dmax_sweep.csv"), "w") as fh:
        fh.write("dmax_target,dmax,Rg_realspace,chisq\n")
        for r in rows:
            if "failed" in r:
                fh.write("%.1f,-,-,- (%s)\n" % (r["dmax_target"], r["failed"]))
            else:
                fh.write("%.1f,%.1f,%.2f,%.4f\n" % (r["dmax_target"], r["dmax"], r["rg"],
                                                    r["chisq"]))
    return rows


# ---------------------------------------------------------------------- node 7: MW
def node_mw(ctx, sub, vp_mw=None):
    mw = {}
    for name, fn in (("Vp_porod", raw.mw_vp), ("Vc", raw.mw_vc)):
        try:
            v = fn(sub, settings=ctx.s)
            mw[name] = dict(mw=float(v[0]), aux=[float(x) for x in v[1:]])
        except Exception as e:
            mw[name] = dict(failed=str(e))
    if ctx.has_atsas:
        for name, fn in (("datmw_bayes", raw.mw_bayes), ("datclass", raw.mw_datclass)):
            try:
                v = fn(sub)
                mw[name] = dict(mw=float(v[0]), aux=[float(x) for x in v[1:]])
            except Exception as e:
                mw[name] = dict(failed=str(e))
    else:
        mw["note"] = ("datmw/datclass/GNOM/DAMMIF need ATSAS (not found) - RAW native "
                      "Vp/Vc/BIFT/DENSS only")
    with open(os.path.join(ctx.out, "tables", "mw.csv"), "w") as fh:
        fh.write("method,MW_kDa,aux,note\n")
        for k, v in mw.items():
            if isinstance(v, dict):
                fh.write("%s,%s,%s,%s\n" % (k, v.get("mw", ""), v.get("aux", ""),
                                            v.get("failed", "")))
            else:
                fh.write("%s,,,,%s\n" % (k, v))
    log("MW: %s" % json.dumps({k: (v.get("mw") if isinstance(v, dict) else v)
                               for k, v in mw.items()}))
    return mw


# -------------------------------------------------------------------- node 8: 3D
def node_shape(ctx, ift, engine="denss", mode="Fast", n_electrons=None, symmetry=0,
               n_models=1):
    """3D node.  Only DENSS is available here: it is the sole solver bundled with RAW and
    it accepts BIFT or GNOM IFTs.  DAMMIF/DAMMIN are ATSAS executables (bead models) and
    only eat GNOM .out IFTs - run those from the RAW GUI (Tools -> ATSAS) once ATSAS is
    installed; this script does not fake that path."""
    if engine == "none" or ift is None:
        log("3D: skipped (%s)" % ("no IFT" if ift is None else "engine=none"))
        return None
    out = {"dammif": ("not run - requires ATSAS (gnom IFT + dammif binary); use the RAW GUI "
                      "or extend this script once ATSAS is installed")}
    os.makedirs(os.path.join(ctx.out, "models"), exist_ok=True)
    t = time.time()
    try:
        res = raw.denss(ift, "denss", os.path.join(ctx.out, "models"), mode=mode,
                        n_electrons=n_electrons or 10000, symmetry=symmetry,
                        settings=ctx.s)
        out["denss"] = dict(mode=mode, chi2=float(res[1]), rg_model=float(res[2]),
                            support_volume=float(res[3]), side=int(res[4]),
                            n_electrons=int(n_electrons or 10000),
                            seconds=time.time() - t,
                            map=os.path.join(ctx.out, "models", "denss.mrc"))
        log("3D DENSS (%s): chi2=%.3f Rg_model=%.1f A support=%.0f A^3 (%.0fs)"
            % (mode, res[1], res[2], res[3], time.time() - t))
    except Exception as e:
        out["denss"] = "failed: %s" % e
        log("3D DENSS failed: %s" % e)
    jdump(out, os.path.join(ctx.out, "tables", "shape_results.json"))
    return out


# ------------------------------------------------------------------ node 9: report
def node_report(ctx, sub, ift, denss_paths=None):
    try:
        raw.save_report("raw_report.pdf", os.path.join(ctx.out, "reports"),
                        profiles=[sub], ifts=[ift] if ift else [],
                        denss_data=denss_paths or [])
        log("report -> reports/raw_report.pdf")
    except Exception as e:
        log("report failed: %s" % e)


def node_workspace(ctx, sub, ift, key):
    """One .hdf5 workspace so the whole chain can be inspected in the RAW GUI."""
    try:
        raw.save_workspace("%s_workspace" % key, ctx.out, profiles=[sub],
                           ifts=[ift] if ift else [])
        p = os.path.join(ctx.out, "%s_workspace.hdf5" % key)
        log("workspace -> %s (%d bytes)" % (p, os.path.getsize(p)))
    except Exception as e:
        log("workspace failed: %s" % e)


# ------------------------------------------------------------------------- plots
def plots(ctx, sub, rows, rec, ift, sweep=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    q, I, E = sub.getQ(), sub.getI(), sub.getErr()
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(2, 3, 1)
    ax.errorbar(q, I, yerr=E, fmt=".-", ms=2)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("q (1/A)"); ax.set_ylabel("I")
    ax.set_title("subtracted (log-log)")
    ax = fig.add_subplot(2, 3, 2)
    ax.errorbar(q, q ** 2 * I, yerr=q ** 2 * E, fmt=".-", ms=2)
    ax.set_xlabel("q"); ax.set_ylabel("q^2 I"); ax.set_title("Kratky")
    ax = fig.add_subplot(2, 3, 3)
    for r in rows:
        if "failed" in r:
            continue
        m = (q >= r["qmin"]) & (q <= r["qmax"])
        ax.errorbar(q[m] ** 2, np.log(I[m]), fmt=".", ms=2, alpha=0.25)
    if rec:
        m = (q >= rec["qmin"]) & (q <= rec["qmax"])
        ax.errorbar(q[m] ** 2, np.log(I[m]), yerr=E[m] / I[m], fmt="o", ms=3,
                    label="recommended")
        xx = np.linspace(0, rec["qmax"] ** 2, 10)
        ax.plot(xx, np.log(rec["i0"]) - xx * rec["rg"] ** 2 / 3, "r-")
        ax.legend(fontsize=8)
    ax.set_xlabel("q^2"); ax.set_ylabel("ln I"); ax.set_title("Guinier fan (all ranges)")
    if ift is not None:
        ax = fig.add_subplot(2, 3, 4)
        ax.errorbar(ift.r, ift.p, yerr=ift.err, fmt=".-", ms=2)
        ax.set_xlabel("r (A)"); ax.set_ylabel("P(r)"); ax.set_title("P(r) [RAW BIFT]")
        ax = fig.add_subplot(2, 3, 5)
        ax.errorbar(ift.q_orig, ift.i_orig, yerr=ift.err_orig, fmt=".", ms=2, label="data")
        ax.plot(ift.q_orig, ift.i_fit, "-", label="IFT fit")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("q"); ax.set_ylabel("I")
        ax.legend(fontsize=8); ax.set_title("IFT fit")
    if sweep:
        ax = fig.add_subplot(2, 3, 6)
        ax.plot([r["dmax"] for r in sweep if "failed" not in r],
                [r["chisq"] for r in sweep if "failed" not in r], "o-")
        ax.set_yscale("log"); ax.set_xlabel("Dmax (A)"); ax.set_ylabel("chi^2")
        ax.set_title("IFT Dmax sweep")
    plt.tight_layout()
    plt.savefig(os.path.join(ctx.out, "qc.png"), dpi=110)
    log("plots -> qc.png")


# -------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--sample-dir", required=True,
                    help="directory holding the sample frames and the control frames")
    ap.add_argument("--cfg", required=True, help="RAW .cfg saved for this dataset")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--sample-key", default=None,
                    help="file-name prefix of the sample (default: directory name)")
    ap.add_argument("--control-key", default=None,
                    help="comma separated prefixes treated as control (default: everything "
                         "that is not the sample prefix)")
    ap.add_argument("--hdr-format", default="BL19U2, SSRF",
                    help="RAW image-header reader (per-frame .txt must sit next to the tif)")
    ap.add_argument("--scale-window", type=float, nargs=2, default=[0.30, 0.44],
                    metavar=("QMIN", "QMAX"), help="q window for the control scale factor")
    ap.add_argument("--no-scale", action="store_true", help="skip the control scale factor")
    ap.add_argument("--qrg-max", type=float, default=1.3, help="Guinier gate on q*Rg")
    ap.add_argument("--snr-min", type=float, default=2.0, help="I/err cut for the q window")
    ap.add_argument("--ift-sweep", type=int, default=0, help="sweep Dmax over N values")
    ap.add_argument("--model-engine", default="denss", choices=["none", "denss"],
                    help="3D back-end.  DENSS is the only solver bundled with RAW; DAMMIF "
                         "needs ATSAS - run it from the RAW GUI (Tools -> ATSAS) or ask for "
                         "the GNOM+DAMMIF path to be added once ATSAS is installed")
    ap.add_argument("--denss-mode", default="Fast", choices=["Fast", "Slow", "Custom"])
    ap.add_argument("--symmetry", type=int, default=0, help="n-fold symmetry for DENSS")
    ap.add_argument("--n-models", type=int, default=1, help="DAMMIF models (needs ATSAS)")
    ap.add_argument("--atsas-dir", default=None, help="ATSAS bin directory (enables GNOM/DAMMIF)")
    ap.add_argument("--save-frames", action="store_true", help="write every frame as .dat")
    ap.add_argument("--steps", default="ift,mw,shape,report,workspace",
                    help="optional nodes to run; the backbone (integrate, average, "
                         "control scaling, subtract, multi-range Guinier) always runs")
    args = ap.parse_args()
    steps = {s.strip() for s in args.steps.split(",") if s.strip()}

    sample_dir = os.path.abspath(os.path.expanduser(args.sample_dir))
    key = args.sample_key or os.path.basename(sample_dir.rstrip("/"))
    files = sorted(glob.glob(os.path.join(sample_dir, "*.tif")))
    control_keys = None
    if args.control_key:
        control_keys = {re.sub(r"[^0-9A-Za-z]", "", c).lower()
                        for c in args.control_key.split(",") if c.strip()}
    sam_files, ctl_files = classify(files, key, control_keys)
    if not sam_files or not ctl_files:
        sys.exit("need both sample and control frames in %s" % sample_dir)

    ctx = Ctx(args.cfg, args.out_dir, args.hdr_format, args.atsas_dir, args.save_frames)
    log("sample '%s': %d frames | controls: %d from %s | ATSAS: %s"
        % (key, len(sam_files), len(ctl_files),
           dict(Counter(os.path.basename(f).split("_")[0] for f in ctl_files)), ctx.has_atsas))

    sam, ctl, frames = node_integrate(ctx, sam_files, ctl_files)
    sub, sub_info = node_average_subtract(ctx, sam, ctl, tuple(args.scale_window),
                                          do_scale=not args.no_scale)
    i0, i1 = pick_analysis_window(sub, snr_min=args.snr_min)
    log("analysis q window: idx %d-%d (q %.4f-%.4f)"
        % (i0, i1, sub.getQ()[i0], sub.getQ()[i1]))
    auto, rows, rec = node_guinier(ctx, sub, i1, args.qrg_max)
    ift, ift_res, sweep, denss_res = None, None, None, None
    if "ift" in steps:
        ift, ift_res = node_ift(ctx, sub, rec, i0, i1)
        if args.ift_sweep > 0:
            sweep = node_ift_sweep(ctx, sub, i0, i1, (rec["rg"] if rec else float(auto[0])),
                                   n=args.ift_sweep)
    mw = node_mw(ctx, sub) if "mw" in steps else {}
    if "shape" in steps and args.model_engine != "none":
        ne = None
        vp = (mw.get("Vp_porod") or {}).get("mw") if isinstance(mw.get("Vp_porod"), dict) else None
        if vp:
            ne = int(round(vp * 537))       # ~0.537 electrons per Da (protein)
            log("  DENSS n_electrons from Vp MW %.1f kDa -> %d" % (vp, ne))
        denss_res = node_shape(ctx, ift, engine=args.model_engine, mode=args.denss_mode,
                               n_electrons=ne, symmetry=args.symmetry)
    if "report" in steps:
        node_report(ctx, sub, ift)
    if "workspace" in steps:
        node_workspace(ctx, sub, ift, key)
    plots(ctx, sub, rows, rec, ift, sweep)
    jdump(dict(sample=key, sample_dir=sample_dir, cfg=args.cfg, subtraction=sub_info,
               guinier_auto=dict(rg=float(auto[0]), qmin=float(auto[4]), qmax=float(auto[5]),
                                 r_sqr=float(auto[10])),
               guinier_recommended=rec, ift=ift_res, ift_dmax_sweep=sweep, mw=mw,
               shape=denss_res, n_frames=len(sam_files) + len(ctl_files),
               n_frame_outliers=sum(1 for r in frames if r.get("outlier"))),
          os.path.join(ctx.out, "summary.json"))
    log("done -> %s" % ctx.out)


if __name__ == "__main__":
    main()
