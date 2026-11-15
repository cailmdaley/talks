"""Sketch of the SPT-like public covariance inputs, for the Paris deck's cov-spt-public slide.

Three vignettes drawn from the real products, in a hand-drawn style (sketched ink lines,
watercolour washes in the euclid palette):
  footprints  SPT-3G Main, Summer A and Summer B box masks (public package, masks/*_binary)
              against the observed Euclid DR1 wide footprint (union of DR1_R1 + DR1_R2 MER VIS
              tiles, results/scratch/footprints/dr1_observed), in a Lambert azimuthal equal-area
              view about the south celestial pole; outlines are the masks' own, lightly smoothed.
              The overlap areas printed are computed here from the same maps.
  noise       beam-deconvolved per-band white+1/f noise model, T and P (noise_curves_main_d1.txt)
  check       public D1 PP lensing bandpower errors over the model's (checks/nl_variants.txt)

Run in the cmbx container: app python make_cov_figures.py
"""
import os

import healpy as hp
from astropy.io import fits
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from scipy.ndimage import gaussian_filter, gaussian_filter1d

from make_cloe_figures import setup_font, INK, MUTED, ACCENT, OCHRE, TEAL, COBALT, IMG

PKG = "/leonardo_work/EUHPC_E07_074/cmbx/inputs/spt/public_covariance_package"
DR1 = ("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/footprints/dr1_observed/"
       "euclid_dr1_observed_wide_nside1024.fits")
FIELDS = [("main", "Main"), ("summer_a", "Summer A"), ("summer_b", "Summer B")]

DPI = 200
W_PX, H_PX = 2 * 1712, 2 * 340   # 2x the figure box under the four bullets
TXT, SMALL = 28, 25              # pt; the figure shows at ~0.49 of 2x, so 25 pt is ~33 px
SKETCH = (2.2, 90, 2.5)          # path.sketch: scale, length, randomness
SPT_C, DR1_C = OCHRE, ACCENT
rng = np.random.default_rng(7)


# ------------------------------------------------------------------ projection
PHI0 = np.deg2rad(25.0)          # RA pointing straight down: the middle of the SPT fields


def project(ra, dec):
    r = 2 * np.sin(np.deg2rad(90 + dec) / 2)
    p = np.deg2rad(ra) - PHI0
    return -r * np.sin(p), -r * np.cos(p)          # RA increases to the left of "down"


def unproject(x, y):
    r = np.hypot(x, y)
    dec = np.rad2deg(2 * np.arcsin(np.clip(r / 2, 0, 1))) - 90
    ra = np.rad2deg(PHI0 + np.arctan2(-x, -y)) % 360
    return ra, dec


# ------------------------------------------------------------------ drawing
def wobble(xy, amp, rng):
    """Displace a closed outline by smooth noise, like a second pass of the brush."""
    n = len(xy)
    if n < 8:
        return xy
    d = gaussian_filter1d(rng.normal(size=(n, 2)), sigma=max(n / 40, 2), axis=0, mode="wrap")
    d *= amp / (np.abs(d).max() + 1e-12)
    return xy + d


def wash(ax, paths, color, alpha=0.11, layers=4, amp=0.018, edge=True, lw=2.6):
    for k in range(layers):
        for p in paths:
            verts = [wobble(v, amp, rng) for v in p]
            codes, allv = [], []
            for v in verts:
                allv.append(v)
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(v) - 2) + [MPath.CLOSEPOLY]
            ax.add_patch(PathPatch(MPath(np.vstack(allv), codes), fc=color, ec="none", alpha=alpha,
                                   zorder=1 + k * 0.01))
    if edge:
        for p in paths:
            for v in p:
                ax.plot(*v.T, color=color, lw=4 * lw, alpha=0.10, zorder=2, solid_capstyle="round")
                ax.plot(*v.T, color=color, lw=lw, alpha=0.9, zorder=3, solid_capstyle="round")


def outlines(img, ext):
    """Closed outlines (list per region of rings) of a 0/1 image at level 0.5."""
    fig = plt.figure()
    cs = plt.contour(np.linspace(ext[0], ext[1], img.shape[1]), np.linspace(ext[2], ext[3], img.shape[0]),
                     img, levels=[0.5])
    plt.close(fig)
    rings = [r for r in cs.allsegs[0] if len(r) > 20]
    return [[r] for r in rings]


# ------------------------------------------------------------------ vignettes
def read_ring(path):
    """A RING-ordered HEALPix map from its FITS table (healpy's read_map is slow on these)."""
    with fits.open(path) as f:
        assert f[1].header.get("ORDERING", "RING") == "RING"
        return np.asarray(f[1].data.field(0)).ravel()


def sky(ax):
    nside = 2048
    dr1 = hp.ud_grade(read_ring(DR1).astype(float), nside) > 0.5
    pix_area = hp.nside2pixarea(nside, degrees=True)

    ext = (-1.18, 1.18, -1.22, 0.06)
    nx, ny = 1600, int(1600 * (ext[3] - ext[2]) / (ext[1] - ext[0]))
    X, Y = np.meshgrid(np.linspace(ext[0], ext[1], nx), np.linspace(ext[2], ext[3], ny))
    ra, dec = unproject(X, Y)
    pix = hp.ang2pix(nside, ra, dec, lonlat=True)

    dimg = gaussian_filter(dr1[pix].astype(float), 3.0)
    wash(ax, outlines(dimg, ext), DR1_C, alpha=0.13, amp=0.006, lw=2.2)

    areas = {}
    for key, name in FIELDS:
        m = read_ring(f"{PKG}/masks/spt3g_{key}_binary.fits.gz").astype(bool)
        areas[key] = (m.sum() * pix_area, (m & dr1).sum() * pix_area)
        mimg = m[pix].astype(float)
        wash(ax, outlines(gaussian_filter(mimg, 1.0), ext), SPT_C, alpha=0.15, amp=0.008, lw=3.0)
        ov = mimg * (dimg > 0.5)
        yy, xx = np.nonzero(ov)
        areas[key] += (X[0, int(np.median(xx))], Y[int(np.median(yy)), 0])

    for key, name in FIELDS:
        tot, ov, x, y = areas[key]
        print(f"{name:9s} box {tot:7.1f} deg2   with DR1 observed wide {ov:6.1f} deg2")
    return areas


def noise(ax):
    d = np.loadtxt(f"{PKG}/noise_curves_main_d1.txt")
    ell = d[:, 0]
    sel = (ell >= 200) & (ell <= 4000)
    to_uk_arcmin = 180 * 60 / np.pi
    for i, (band, c) in enumerate([("95", TEAL), ("150", ACCENT), ("220", OCHRE)]):
        t = np.sqrt(d[sel, 1 + i]) * to_uk_arcmin
        p = np.sqrt(d[sel, 4 + i]) * to_uk_arcmin
        ax.plot(ell[sel], t, color=c, lw=3.2)
        ax.plot(ell[sel], p, color=c, lw=3.2, ls=(0, (5, 4)))
    ax.set_yscale("log")
    ax.set_xlim(200, 4000)
    ax.set_ylim(2, 400)
    return ell


def check(ax):
    d = np.loadtxt(f"{PKG}/checks/nl_variants.txt")
    L, pp = d[:, 0], d[:, 1]
    ax.axhspan(0.9, 1.1, color=TEAL, alpha=0.13, lw=0, zorder=0)
    ax.axhline(1, color=TEAL, lw=1.6, alpha=0.7, zorder=1)
    ax.plot(L, pp, color=INK, lw=3.0, zorder=3)
    ax.plot(L, pp, "o", color=INK, ms=8, zorder=4)
    ax.set_xscale("log")
    ax.set_xlim(30, 3000)
    ax.set_ylim(0.7, 1.45)


def main():
    setup_font()
    plt.rcParams["path.sketch"] = SKETCH
    plt.rcParams.update({"xtick.labelsize": SMALL, "ytick.labelsize": SMALL, "axes.labelsize": TXT,
                         "axes.linewidth": 2.0, "xtick.major.width": 2.0, "ytick.major.width": 2.0})
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)

    # footprints, left: equal-area so the washes compare as areas
    ax = fig.add_axes([0.0, 0.0, 0.43, 1.0])
    areas = sky(ax)
    ax.set_xlim(-1.18, 1.18)
    ax.set_ylim(-1.22, 0.06)
    ax.set_aspect("equal")
    ax.axis("off")
    NUDGE = {"summer_b": (0.15, -0.11)}
    for key, name in FIELDS:
        tot, ov, x, y = areas[key]
        dx, dy = NUDGE.get(key, (0, 0))
        ax.text(x + dx, y + dy, f"{ov:.0f}", color=INK, fontsize=TXT, ha="center", va="center", zorder=6)
    LABELS = {"main": (0.72, -0.03, "SPT-3G Main"), "summer_a": (-0.88, -0.1, "Summer A"),
              "summer_b": (0.0, -1.14, "Summer B")}
    for key, (x, y, s) in LABELS.items():
        ax.text(x, y, s, color="#6E5410", fontsize=TXT, ha="center", va="center", zorder=6)
    ax.text(0.98, -1.0, "Euclid DR1", color=COBALT, fontsize=TXT, ha="center", va="center", zorder=6)
    ax.text(0.98, -1.13, "overlap, deg²", color=INK, fontsize=SMALL, ha="center", va="center", zorder=6)

    # the two charts are drawn clean; only the footprint map is sketched
    plt.rcParams["path.sketch"] = None
    # noise per band
    ax = fig.add_axes([0.50, 0.30, 0.2, 0.55])
    noise(ax)
    ax.set_xticks([1000, 2000, 3000, 4000], ["1000", "", "3000", ""])
    ax.set_yticks([10, 100], ["10", "100"])
    ax.minorticks_off()
    ax.set_xlabel("$\\ell$", labelpad=0)
    ax.set_title("noise per band, μK′", fontsize=TXT, color=INK, loc="left", pad=10)
    ax.plot([], [], color=MUTED, lw=3.2, label="T")
    ax.plot([], [], color=MUTED, lw=3.2, ls=(0, (5, 4)), label="P")
    ax.legend(loc="upper right", ncol=2, frameon=False, fontsize=SMALL,
              handlelength=1.6, columnspacing=1.0, borderaxespad=0.1)
    ax.text(3950, 60, "220", color=OCHRE, fontsize=SMALL, ha="right", va="center")
    ax.text(3950, 3.0, "150", color=ACCENT, fontsize=SMALL, ha="right", va="center")
    ax.text(2500, 3.0, "95", color=TEAL, fontsize=SMALL, ha="right", va="center")

    # reconstruction-noise check
    ax = fig.add_axes([0.78, 0.30, 0.2, 0.55])
    check(ax)
    ax.set_xticks([100, 1000], ["100", "1000"])
    ax.set_yticks([0.8, 1.0, 1.2, 1.4])
    ax.minorticks_off()
    ax.set_xlabel("$L$", labelpad=0)
    ax.set_title("pol-only $\\sigma_\\mathrm{D1}\\,/\\,\\sigma_\\mathrm{model}$", fontsize=TXT, color=INK,
                 loc="left", pad=10)

    out = os.path.join(IMG, "paris26_cov_spt_public_sketch.png")
    fig.savefig(out, dpi=DPI)
    print("wrote", out)


if __name__ == "__main__":
    main()
