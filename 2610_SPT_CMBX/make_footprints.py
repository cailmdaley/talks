"""Footprint build-up for the SPT analysis call: the Napoli build (Euclid DR1 effective
coverage, then Planck PR4, ACT DR6 and SPT-3G Main) with the SPT-3G Summer fields as a
fifth frame.

Five PNGs with an identical frame, written to the shared images/ pool:
  spt_footprint_1_dr1.png         Euclid DR1 alone
  spt_footprint_2_planck.png      + Planck PR4
  spt_footprint_3_act.png         + ACT DR6
  spt_footprint_4_spt_main.png    + SPT-3G Main
  spt_footprint_5_spt_summer.png  + SPT-3G Summer (summer-a and summer-b)
The drawing and every convention come from ../2610_Napoli_CMBX/make_footprints.py, which
this script imports and extends: one more CMB layer, one more legend slot, a south panel
framed on the union of all frames' maps, and type at the house 32 px floor.

Areas are effective, as in the Napoli script: DR1 effcov summed over the pixels where the
CMB mask is > 0, effcov upgraded from NSIDE 1024 to the mask's 2048. The script also
prints the overlap of SPT-3G Main and Summer together with DR1, the Main ∩ Summer area,
and the overlaps with Euclid TR1 in two conventions: effective, over the TR1 WL
effective-coverage map of the analysis (south patch, NSIDE 2048); and geometric, over the
RR2 photometric footprint at NSIDE 512 with both maps > 1e-6 (the convention of
results/scratch/footprints/footprint_areas.py).

Run in the cmbx container:
  app python make_footprints.py [--coverage r2|validtiles] [--preview] [--cache file.npz]
--preview renders only the last frame, to images/spt_footprint_<coverage>_preview.png.
"""
import argparse
import importlib.util
import os

import healpy as hp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "napoli_footprints", os.path.join(HERE, "..", "2610_Napoli_CMBX", "make_footprints.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

OUT = fp.OUT
SUMMER = f"{fp.INPUTS}/spt/masks/lensing/summer/spt3g_summer-a_summer-b_mask_apodized.fits"
TR1_EFFCOV = f"{fp.INPUTS}/euclid/masks/tr1_wl_coverage_south_nside2048.fits"
RR2_PHOTO = ("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/footprints/"
             "RR2_Footprint_4096_photo.fits")

# the fifth layer: SPT-3G Summer, a sea green beside Main's dark teal
fp.CMB["spt"] = ("SPT-3G Main", fp.CMB["spt"][1])
fp.CMB["summer"] = ("SPT-3G Summer", SUMMER)
fp.COLOURS["summer"] = ("#2F8F5B", 0.50)
fp.OUTLINE_ON_DR1["summer"] = "#A6E8A0"

# type at the 32 px floor: 24 pt at 200 dpi, shown at half size, is 33 px; the legend's rows,
# swatch offsets and width scale with it
fp.FS = fp.FS_GRID = 24
_S = 24 / 21
fp.LEG_SLOTS = tuple(round(_S * y) for y in (60, 125, 185, 275, 360, 445, 530))
fp.LEG_W, fp.LEG_H = round(_S * 1010), round(_S * 570)


def read(p):
    m = np.nan_to_num(hp.read_map(p, dtype=np.float64))
    m[m < 0] = 0.0                       # UNSEEN outside a partial map reads as zero
    return m


def measure_extra(dr1_path):
    """Overlaps the frames do not show: Main and Summer together with DR1, Main ∩ Summer,
    and each SPT field with TR1."""
    main, summer = read(fp.CMB["spt"][1]), read(SUMMER)
    ns = hp.npix2nside(main.size)
    assert hp.npix2nside(summer.size) == ns
    pa = hp.nside2pixarea(ns, degrees=True)
    e = fp.upgrade(read(dr1_path), ns)
    t = read(TR1_EFFCOV)
    assert hp.npix2nside(t.size) == ns
    fields = {"spt": main > 0, "summer": summer > 0, "spt+summer": (main > 0) | (summer > 0)}
    X = {"main_summer_area": ((main > 0) & (summer > 0)).sum() * pa,
         "main_summer_area_05": ((main > 0.5) & (summer > 0.5)).sum() * pa,
         "spt+summer_area": ((main > 0.5) | (summer > 0.5)).sum() * pa,
         "tr1_eff": t.sum() * pa, "tr1_support": (t > 0).sum() * pa}
    for k, on in fields.items():
        X[f"{k}_cap"] = e[on].sum() * pa
        X[f"{k}_cap_geom"] = (on & (e > 0)).sum() * pa
        X[f"{k}_tr1_eff"] = t[on].sum() * pa
        X[f"{k}_tr1_geom"] = (on & (t > 0)).sum() * pa
    # geometric, at NSIDE 512 with maps > 1e-6 (footprint_areas.py)
    def b512(m):
        return hp.ud_grade(m, 512) > 1e-6
    r = b512(read(RR2_PHOTO))
    pa5 = hp.nside2pixarea(512, degrees=True)
    m5, s5 = b512(main), b512(summer)
    X["rr2_area"] = r.sum() * pa5
    for k, on in {"spt": m5, "summer": s5, "spt+summer": m5 | s5}.items():
        X[f"{k}_rr2"] = (on & r).sum() * pa5
    return X


def layout(A):
    """The Napoli layout, with the south panel framed on DR1 south and both SPT fields, so
    every frame shares it."""
    ra0 = fp.RA0
    sp, npj = fp.Polar("south", ra0), fp.Polar("north", ra0 + 180)
    south = fp.south_mask()
    sb = fp.bbox_of(sp, [A["map_dr1"] & south, A["map_spt"], A["map_summer"]], margin=0.09)
    nb = fp.bbox_of(npj, [A["map_dr1"] & ~south], margin=0.11,
                    extra=[(r, 84.0) for r in range(0, 360, 15)])
    sw, sh = sb[1] - sb[0], sb[3] - sb[2]
    nw, nh = nb[1] - nb[0], nb[3] - nb[2]
    gap, pad = 40, 4
    W, H = fp.W_PX - 2 * pad, fp.H_PX - 2 * pad
    k = (W - gap) / (sw + nw)
    if k * nw < fp.LEG_W:
        k = (W - gap - fp.LEG_W) / sw
    k = min(k, H / sh, (H - gap - fp.LEG_H) / nh)
    sr = (pad, pad, int(k * sw), int(k * sh))
    col = sr[0] + sr[2] + gap
    nr = (col, pad, int(k * nw), int(k * nh))
    print(f"RA0 {ra0} / {ra0 + 180}  south {sr}  north {nr}", flush=True)
    panels = [(fp.Panel(sp, sb, sr), "South", [-15, -30, -45, -60, -75]),
              (fp.Panel(npj, nb, nr), "North", [45, 60, 75])]
    return panels, (col, sr[1] + sr[3] - fp.LEG_H, col + max(nr[2], fp.LEG_W) - 8), sr[1] + sr[3] + pad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", choices=fp.COVERAGE, default="validtiles", help="the Euclid DR1 coverage map")
    ap.add_argument("--preview", action="store_true",
                    help="render only the last frame, as spt_footprint_<coverage>_preview.png")
    ap.add_argument("--cache", help="npz holding the measured areas and plot maps (made if missing); "
                                    "one per coverage")
    args = ap.parse_args()
    if args.cache and os.path.exists(args.cache):
        A = dict(np.load(args.cache))
    else:
        A = fp.measure(fp.COVERAGE[args.coverage])
        A.update(measure_extra(fp.COVERAGE[args.coverage]))
        if args.cache:
            np.savez(args.cache, **A)
    f = {k: float(v) for k, v in A.items() if np.ndim(v) == 0}
    print(f"DR1 effective {f['dr1_eff']:.1f} deg² (south {f['dr1_eff_s']:.1f}, north {f['dr1_eff_n']:.1f})")
    for k in fp.CMB:
        print(f"{k}: mask > 0.5 {f[k + '_area']:.1f}  ∩DR1 effective {f[k + '_cap']:.1f} "
              f"(S {f[k + '_cap_s']:.1f}, N {f[k + '_cap_n']:.1f})  ∩DR1 geometric {f[k + '_cap_geom']:.1f} deg²")
    print(f"Main ∩ Summer: masks > 0 {f['main_summer_area']:.1f}, > 0.5 {f['main_summer_area_05']:.1f} deg²; "
          f"Main ∪ Summer > 0.5 {f['spt+summer_area']:.1f} deg²")
    print(f"TR1 WL coverage: effective {f['tr1_eff']:.1f}, support {f['tr1_support']:.1f} deg²; "
          f"RR2 photometric footprint {f['rr2_area']:.1f} deg²")
    for k in ("spt", "summer", "spt+summer"):
        print(f"{k}: ∩DR1 effective {f[k + '_cap']:.1f} geometric {f[k + '_cap_geom']:.1f} | "
              f"∩TR1 effective {f[k + '_tr1_eff']:.1f} geometric {f[k + '_tr1_geom']:.1f} | "
              f"∩RR2-photo (512, >1e-6) {f[k + '_rr2']:.1f} deg²", flush=True)

    fp.setup_font()
    panels, leg, height = layout(A)
    frames = [("1_dr1", []), ("2_planck", ["planck"]), ("3_act", ["planck", "act"]),
              ("4_spt_main", ["planck", "act", "spt"]), ("5_spt_summer", ["planck", "act", "spt", "summer"])]
    if args.preview:
        frames = [(f"{args.coverage}_preview", frames[-1][1])]
    for name, layers in frames:
        fp.render(panels, layers, A, os.path.join(OUT, f"spt_footprint_{name}.png"), leg, height)


if __name__ == "__main__":
    main()
