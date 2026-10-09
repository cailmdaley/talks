"""Redshift kernels for the Napoli CMBX talk: the six Euclid DR1 source bins'
n(z) and lensing kernels, and the CMB secondaries (lensing, CIB, tSZ) below
them, on one redshift axis running to z = 3.

Top panel: the source n(z), each bin normalised to unit area, drawn with the
analysis's Hann smoothing (nz_io.smooth_hann, width dz = 0.05) to calm the
histogram's bin-to-bin spikes; the kernels use the unsmoothed n(z).

Middle panel: the lensing efficiency per unit redshift of each Euclid DR1
weak-lensing source bin, from the official tomographic n(z)
(DpdBinMeanRedshift, PHZ MergeNz 1.0.2, release DR1_WLSOUTH_R1, source bins
TOM_BIN, WEIGHT_METHOD = PHZ_WEIGHT; bin means 0.45-1.73).  The table's N_Z is
a histogram on bins of width dz = 0.01 whose centres are (i + 1/2) dz: that
grid reproduces the header's MEAN_Z.

    W(z) = (3/2) Omega_m H0^2 / c^2 * chi (1+z) * g(chi) * dchi/dz,
    g = int dz' n(z') (chi' - chi)/chi',

in common units, so the bins' heights compare, scaled to the tallest.

Bottom panel: the CMB secondaries, each scaled to unit peak (their units differ):
  - CMB lensing: the same W(z) with g = (chi_* - chi)/chi_*, the single source
    plane at last scattering (z_* ~ 1090);
  - tSZ: dy/dz ~ dchi/dz * a * <b P_e>(z), the bias-weighted mean electron
    pressure (CCL halo model: Tinker08 mass function, Tinker10 bias, M200c,
    generalised-NFW pressure, Arnaud et al. 2010 with hydrostatic bias 0.8);
  - CIB at 545 GHz: dI/dz ~ dchi/dz * a * <b j_nu>(z), the bias-weighted
    emissivity of the Shang et al. 2012 halo model at CCL's default
    (Planck 2013-like) parameters.
Bias-weighted kernels are the ones a cross-correlation on linear scales sees.
The tSZ and CIB shapes are model-dependent (the CIB peak especially); they
are drawn as illustrations of where each signal comes from.

Cosmology: Planck 2018 TT,TE,EE+lowE+lensing best fit (flat LCDM).

The tSZ kernel is not a cluster selection function: a cluster's SZ decrement
does not dim with redshift, but the y signal per unit redshift follows the
abundance of massive, hot haloes, which falls steeply beyond z ~ 1.

Output: two frames of one plot, identical axes, for a slide stack:
  images/napoli_secondary_kernels_euclid.png  the source bins alone
  images/napoli_secondary_kernels.png         + the CMB secondaries
at 2x the figure-text layout's figure cell (1027 x 723 px displayed, the body
less a .source line).

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
OUT = os.path.join(HERE, "..", "images", "napoli_secondary_kernels.png")
OUT_EUCLID = os.path.join(HERE, "..", "images", "napoli_secondary_kernels_euclid.png")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
sys.path.insert(0, f"{CMBX}/workflow/scripts")
from nz_io import smooth_hann  # noqa: E402
WL_NZ = ("/leonardo_work/EUHPC_E07_074/cmbx/inputs/euclid/dr1/nz_official_tombinz_20260523/"
         "EUC_PHZ_TOMBINZ__20260523T200621.112482Z_00.00.fits")   # WLSOUTH_R1, source, PHZ_WEIGHT

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
CINNABAR = "#B0412E"   # CMB lensing
BIN_LO, BIN_HI = "#2E417C", "#9AABCF"   # the source bins: one cool ramp, under the secondaries

W_PX, H_PX, DPI = 2054, 1446, 200
PT = DPI / 72 / 2      # displayed px per point
ZMAX = 3.0

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


def secondary_kernels(z):
    """Bias-weighted tSZ and CIB (545 GHz) redshift kernels from CCL's halo model, unnormalised."""
    md = ccl.halos.MassDef200c
    hmc = ccl.halos.HMCalculator(mass_function=ccl.halos.MassFuncTinker08(mass_def=md),
                                 halo_bias=ccl.halos.HaloBiasTinker10(mass_def=md), mass_def=md)
    pressure = ccl.halos.HaloProfilePressureGNFW(mass_def=md)
    cib = ccl.halos.HaloProfileCIBShang12(mass_def=md, concentration=ccl.halos.ConcentrationDuffy08(mass_def=md),
                                          nu_GHz=545)
    a = 1.0 / (1.0 + z)
    dchi_dz = ccl.physical_constants.CLIGHT_HMPC / COSMO["h"] / ccl.h_over_h0(COSMO, a)
    k = np.array([1e-3])   # linear scales: the 1-point bias-weighted mean
    by = np.array([ccl.halos.halomod_bias_1pt(COSMO, hmc, k, ai, pressure)[0] for ai in a])
    bj = np.array([ccl.halos.halomod_bias_1pt(COSMO, hmc, k, ai, cib)[0] for ai in a])
    return dchi_dz * a * by, dchi_dz * a * bj


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

    zz = np.linspace(0.02, ZMAX, 150)
    wy, wc = secondary_kernels(zz)
    sec = {"kappa": (z, wk / wk.max()), "tsz": (zz, wy / wy.max()), "cib": (zz, wc / wc.max())}
    for n, (zn, wn) in sec.items():
        half = zn[wn > 0.5]
        print(f"{n}: peak z = {zn[np.argmax(wn)]:.2f}, half maximum over z = {half[0]:.2f}-{half[-1]:.2f}")
    smooth = {b: (zb, smooth_hann(zb, nb, 0.05)) for b, (zb, nb) in raw.items()}
    for out, with_sec in ((OUT_EUCLID, False), (OUT, True)):
        draw(out, with_sec, bins, z, kern, sec, smooth)


def draw(out, with_sec, bins, z, kern, sec, smooth):
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
    cmap = LinearSegmentedColormap.from_list("bins", [BIN_LO, BIN_HI])
    colours = [cmap(t) for t in np.linspace(0, 1, len(bins))]

    fig, (ax_n, ax_w, ax_s) = plt.subplots(3, 1, figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, sharex=True,
                                           gridspec_kw=dict(height_ratios=[1, 1, 1], hspace=0.12, left=0.08,
                                                            right=0.97, top=0.975, bottom=0.12))
    nmax = 0.0
    for b, c in zip(bins, colours):
        zb, nb = smooth[b]
        ax_n.fill_between(zb, nb, color=c, alpha=0.18, lw=0)
        ax_n.plot(zb, nb, color=c, lw=2.2)
        nmax = max(nmax, nb[zb <= ZMAX].max())
    ax_n.set_ylim(0, 1.15 * nmax)
    ax_n.set_yticks([])
    ax_n.set_ylabel(r"$n(z)$")
    ax_n.text(0.985, 0.92, "Euclid DR1 source bins 1–6", transform=ax_n.transAxes,
              ha="right", va="top", fontsize=24, color=INK)

    kmax = max(k.max() for k in kern.values())
    for b, c in zip(bins, colours):
        ax_w.plot(z, kern[b] / kmax, color=c, lw=2.6)
    ax_w.set_xlim(0, ZMAX)
    ax_w.set_ylim(0, 1.15)
    ax_w.set_yticks([])
    ax_w.set_ylabel(r"$W(z)$")
    ax_w.text(0.985, 0.92, "their shear lensing kernels", transform=ax_w.transAxes,
              ha="right", va="top", fontsize=24, color=INK)
    ax_s.set_xlabel(r"redshift $z$")

    ax_s.set_ylim(0, 1.22)
    ax_s.set_yticks([])
    ax_s.set_ylabel("CMB")
    if with_sec:
        # label, colour, line width, and where the label sits (z, y, ha, va), in clear space
        style = {"tsz": ("tSZ", TEAL, 3.6, (0.33, 1.04, "center", "bottom")),
                 "cib": ("CIB 545 GHz", OCHRE, 3.6, (2.62, 1.04, "center", "bottom")),
                 "kappa": (r"lensing $\kappa$", CINNABAR, 5.0, (1.35, 1.04, "center", "bottom"))}
        for n in ("tsz", "cib", "kappa"):
            zn, wn = sec[n]
            label, colour, lw, (zl, yl, ha, va) = style[n]
            ax_s.plot(zn, wn, color=colour, lw=lw, zorder=5 if n == "kappa" else 4)
            ax_s.text(zl, yl, label, fontsize=28, color=colour, ha=ha, va=va)
        ax_s.text(0.985, 0.42, "each scaled to its peak", transform=ax_s.transAxes,
                  ha="right", va="bottom", fontsize=22, color=MUTED)
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
