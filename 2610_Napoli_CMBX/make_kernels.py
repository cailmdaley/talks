"""Lensing kernels for the Napoli CMBX talk: the six Euclid DR1 source bins and
the CMB lensing kernel on one redshift axis, with the source n(z) above them.

Top panel: the official Euclid DR1 weak-lensing tomographic n(z)
(DpdBinMeanRedshift, PHZ MergeNz 1.0.2, release DR1_WLSOUTH_R1, source bins
TOM_BIN, WEIGHT_METHOD = PHZ_WEIGHT; bin means 0.45-1.73), each bin normalised
to unit area.  The table's N_Z is a histogram on bins of width dz = 0.01 whose
centres are (i + 1/2) dz: that grid reproduces the header's MEAN_Z.  WLNORTH_R1
differs by at most 5 % in total variation per bin and 0.014 in mean z, which
does not show at this scale; South is drawn.  The top panel is drawn with the
analysis's Hann smoothing (nz_io.smooth_hann, width dz = 0.05) to calm the
histogram's bin-to-bin spikes; the kernels below use the unsmoothed n(z).

Bottom panel: the lensing efficiency per unit redshift, in the same units for
every tracer, so heights compare directly:
    W(z) = (3/2) Omega_m H0^2 / c^2 * chi (1+z) * g(chi) * dchi/dz
with g = int dz' n(z') (chi' - chi)/chi' for a galaxy bin and
g = (chi_* - chi)/chi_* for the CMB, whose single source plane is the last
scattering surface (z_* ~ 1090).  W(z) is dimensionless.

Cosmology: Planck 2018 TT,TE,EE+lowE+lensing best fit (flat LCDM; only the
background matters here).

Output: two frames of one plot, identical axes, for a slide stack:
  images/napoli_lensing_kernels_shear.png  the source bins alone
  images/napoli_lensing_kernels.png        + the CMB lensing kernel
at 2x the figure-text layout's
figure cell (1027 x 723 px displayed, the body less a .source line).

Run in the cmbx container: app python make_kernels.py
"""
import os
import sys
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyccl as ccl
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "napoli_lensing_kernels.png")
OUT_SHEAR = os.path.join(HERE, "..", "images", "napoli_lensing_kernels_shear.png")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
WL_NZ = ("/leonardo_work/EUHPC_E07_074/cmbx/inputs/euclid/dr1/nz_official_tombinz_20260523/"
         "EUC_PHZ_TOMBINZ__20260523T200621.112482Z_00.00.fits")   # WLSOUTH_R1, source, PHZ_WEIGHT
sys.path.insert(0, f"{CMBX}/workflow/scripts")
from nz_io import smooth_hann  # noqa: E402

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
CINNABAR = "#B0412E"   # the CMB kernel: one warm line against the cool bin ramp

W_PX, H_PX, DPI = 2054, 1446, 200
PT = DPI / 72 / 2      # displayed px per point
ZMAX = 4.0

COSMO = ccl.Cosmology(Omega_c=0.2607, Omega_b=0.04897, h=0.6766, sigma8=0.8102, n_s=0.9665)


def setup_font():
    """EB Garamond, the deck's face, from the deck's own node_modules (woff2 -> ttf)."""
    src = os.path.join(HERE, "..", "node_modules", "@fontsource-variable", "eb-garamond", "files",
                       "eb-garamond-latin-wght-normal.woff2")
    try:
        from fontTools.ttLib import TTFont
        ttf = os.path.join(tempfile.mkdtemp(), "EBGaramond.ttf")
        f = TTFont(src)
        f.flavor = None
        f.save(ttf)
        font_manager.fontManager.addfont(ttf)
        name = font_manager.FontProperties(fname=ttf).get_name()
        plt.rcParams["font.family"] = [name, "DejaVu Serif"]
        plt.rcParams["mathtext.fontset"] = "custom"
        for k in ("rm", "it", "bf"):
            plt.rcParams[f"mathtext.{k}"] = name + (":italic" if k == "it" else "")
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable, using DejaVu Serif:", e, flush=True)
        plt.rcParams["font.family"] = "DejaVu Serif"


def chi_of_z(z):
    return ccl.comoving_radial_distance(COSMO, 1.0 / (1.0 + np.asarray(z)))


def prefactor(z):
    """(3/2) Omega_m H0^2/c^2 * chi (1+z) * dchi/dz, in Mpc^-1 * Mpc * Mpc^-0 -> per unit g."""
    h0_c = COSMO["h"] / ccl.physical_constants.CLIGHT_HMPC   # H0/c in 1/Mpc
    om = COSMO["Omega_c"] + COSMO["Omega_b"]
    a = 1.0 / (1.0 + z)
    dchi_dz = 1.0 / (h0_c * ccl.h_over_h0(COSMO, a))
    return 1.5 * om * h0_c ** 2 * chi_of_z(z) * (1.0 + z) * dchi_dz


def galaxy_kernel(z, zs, nz):
    chi, chis = chi_of_z(z), chi_of_z(zs)
    g = np.array([np.trapezoid(np.where(chis > c, nz * (chis - c) / np.maximum(chis, 1e-9), 0.0), zs)
                  for c in chi])
    return prefactor(z) * g


def cmb_kernel(z):
    chi_star = chi_of_z(1090.0)
    return prefactor(z) * (chi_star - chi_of_z(z)) / chi_star


def load_nz(path):
    """{bin: (z, n(z) normalised to unit area)} and {bin: mean z} from a DpdBinMeanRedshift FITS."""
    from astropy.io import fits
    with fits.open(path) as h:
        hdr, d = h["BIN_INFO"].header, h["BIN_INFO"].data
        assert hdr["BIN_TYPE"].strip() == "TOM_BIN" and hdr["WEIGHT_METHOD"].strip() == "PHZ_WEIGHT"
        dz = float(hdr["Z_STEP"])
        out, mean_z = {}, {}
        for bid, n in zip(d["BIN_ID"], d["N_Z"]):
            z = (np.arange(n.size) + 0.5) * dz
            n = np.asarray(n, float) / np.trapezoid(n, z)
            out[int(bid)], mean_z[int(bid)] = (z, n), float(np.trapezoid(z * n, z))
    return out, mean_z


def main():
    setup_font()
    raw, mean_z = load_nz(WL_NZ)
    smooth = {b: (z, smooth_hann(z, n, 0.05)) for b, (z, n) in raw.items()}
    bins = sorted(raw)
    z = np.linspace(0.0, ZMAX, 401)
    zs, _ = raw[bins[0]]
    kern = {b: galaxy_kernel(z, zs, raw[b][1]) for b in bins}
    wk = cmb_kernel(z)
    zpk = z[np.argmax(wk)]
    print("mean z per bin:", {b: round(mean_z[b], 3) for b in bins})
    print(f"CMB kernel peaks at z = {zpk:.2f}; galaxy kernel peaks:",
          {b: round(float(z[np.argmax(kern[b])]), 2) for b in bins})
    for b in bins:
        zz_b, n_b = raw[b]
        print(f"  bin {b}: fraction of n(z) above z=2: {np.trapezoid(n_b[zz_b > 2], zz_b[zz_b > 2]):.3f}")

    for out, with_cmb in ((OUT_SHEAR, False), (OUT, True)):
        draw(out, with_cmb, bins, smooth, mean_z, z, kern, wk, zpk)


def draw(out, with_cmb, bins, smooth, mean_z, z, kern, wk, zpk):
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": 22, "ytick.labelsize": 22, "axes.labelsize": 25,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    print(f"tick labels ≈ {22 * PT:.0f} px, axis labels ≈ {25 * PT:.0f} px displayed")
    cmap = LinearSegmentedColormap.from_list("bins", [COBALT, TEAL, OCHRE])
    colours = [cmap(t) for t in np.linspace(0, 1, len(bins))]

    fig, (ax_n, ax_w) = plt.subplots(2, 1, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, sharex=True,
                                     gridspec_kw=dict(height_ratios=[1, 1.9], hspace=0.08, left=0.12,
                                                      right=0.97, top=0.95, bottom=0.115))
    for b, c in zip(bins, colours):
        zb, nb = smooth[b]
        ax_n.fill_between(zb, nb, color=c, alpha=0.18, lw=0)
        ax_n.plot(zb, nb, color=c, lw=2.2)
        ax_w.plot(z, kern[b], color=c, lw=2.6)
    ax_n.set_ylim(0, None)
    ax_n.set_yticks([])
    ax_n.set_ylabel(r"$n(z)$")
    ax_n.text(0.985, 0.88, "Euclid DR1 source bins", transform=ax_n.transAxes, ha="right", va="top",
              fontsize=24, color=INK)
    ax_w.set_xlim(0, ZMAX)
    ax_w.set_ylim(0, 1.12 * max(wk.max(), max(k.max() for k in kern.values())))
    ax_w.set_ylabel(r"lensing kernel $W(z)$")
    ax_w.set_xlabel(r"redshift $z$")
    ax_w.set_yticks([])
    kmax6 = kern[bins[-1]].max()
    ax_w.text(0.78, kmax6 * 1.04, "shear bins 1–6", fontsize=24, color=INK, ha="left", va="bottom")
    if with_cmb:
        ax_w.plot(z, wk, color=CINNABAR, lw=5.0, zorder=5)
        ax_w.text(1.1, 0.86 * wk.max(), r"CMB lensing $\kappa$", fontsize=28, color=CINNABAR,
                  ha="left", va="top")
        ax_w.text(ZMAX - 0.05, 0.62 * wk.max(), r"source plane at $z_* \approx 1100$ $\rightarrow$",
                  fontsize=22, color=CINNABAR, ha="right", va="top")
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
