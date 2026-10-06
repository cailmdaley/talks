"""Footprint build-up for the Napoli CMBX talk: Euclid DR1 with the CMB lensing
footprints laid over it one at a time (Planck PR4, ACT DR6, SPT-3G Main).

Four PNGs with an identical frame, written to the shared images/ pool:
  napoli_footprint_1_dr1.png     Euclid DR1 alone
  napoli_footprint_2_planck.png  + Planck PR4
  napoli_footprint_3_act.png     + ACT DR6
  napoli_footprint_4_spt.png     + SPT-3G Main
The slide stacks them, so each step adds exactly one layer.

Areas are measured at each mask's native NSIDE (DR1 is upgraded to 2048 for the
overlaps; a binary map upgrades exactly):
  - a CMB footprint's area counts pixels with mask > 0.5 (within 0.4 % of the
    apodized mask's weighted sum, sum(w) * pixel area), and the drawn fill uses
    the same threshold;
  - its overlap with DR1 is binary: mask > 0 and DR1.
The maps are drawn at NSIDE 512 in an equatorial Mollweide projection, RA
increasing to the left, centred on the DR1 south field.

Run in the cmbx container: app python make_footprints.py [--cache areas_and_maps.npz]
"""
import argparse
import os
import tempfile

import healpy as hp
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, patheffects
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images")
INPUTS = "/leonardo_work/EUHPC_E07_074/cmbx/inputs"
DR1_PATH = ("/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/footprints/"
            "dr1_observed/euclid_dr1_observed_wide_nside1024.fits")
CMB = {  # key: (label, path)
    "planck": ("Planck PR4", f"{INPUTS}/planck/masks/mask_rotated.fits"),
    "act": ("ACT DR6", f"{INPUTS}/act/masks/mask_act_dr6_lensing_v1_healpix_nside_2048_baseline.fits"),
    "spt": ("SPT-3G Main", f"{INPUTS}/spt/masks/lensing/winter/"
            "mask2048_border_apod_mask_threshold0.1_allghz_dense.fits"),
}
NSIDE_PLOT = 512

# euclid theme (house/themes/euclid.css)
INK, MUTED, GROUND = "#111418", "#535B67", "#EBF0F6"
C_DR1 = "#435AA1"                      # Euclid blue, opaque on top
COLOURS = {"planck": ("#8A93A3", 0.30),  # (colour, fill alpha): a grey wash for the near-full sky
           "act": ("#C08A1E", 0.50),     # ochre
           "spt": ("#1D8A8A", 0.62)}     # teal

# canvas: the figure layout's body box less the .source line, 1712 x 723 px, at 2x
W_PX, H_PX, DPI = 3424, 1446, 200


# ---------------------------------------------------------------- measurement
def measure():
    def read(p):
        return np.nan_to_num(hp.read_map(p, dtype=np.float64))

    d = read(DR1_PATH)
    ns_d = hp.npix2nside(d.size)
    out = {"dr1_area": (d > 0).sum() * hp.nside2pixarea(ns_d, degrees=True)}
    ra, dec = hp.pix2ang(ns_d, np.flatnonzero(d > 0), lonlat=True)
    out["dr1_south"] = (dec < 0).sum() * hp.nside2pixarea(ns_d, degrees=True)
    out["dr1_north"] = (dec >= 0).sum() * hp.nside2pixarea(ns_d, degrees=True)
    out["map_dr1"] = hp.ud_grade(d, NSIDE_PLOT) > 0.5
    d_up = {}
    for k, (_, p) in CMB.items():
        m = read(p)
        ns = hp.npix2nside(m.size)
        pa = hp.nside2pixarea(ns, degrees=True)
        if ns not in d_up:
            d_up[ns] = hp.ud_grade(d, ns) > 0.5
        out[f"{k}_area"] = (m > 0.5).sum() * pa
        out[f"{k}_area_gt0"] = (m > 0).sum() * pa
        out[f"{k}_area_w"] = m.sum() * pa
        out[f"{k}_cap"] = ((m > 0) & d_up[ns]).sum() * pa
        out[f"{k}_cap_half"] = ((m > 0.5) & d_up[ns]).sum() * pa
        out[f"map_{k}"] = hp.ud_grade(m, NSIDE_PLOT) > 0.5
        print(f"{k}: nside {ns}", flush=True)
    return out


# ---------------------------------------------------------------- projection
SQ2 = np.sqrt(2.0)


def moll_inverse(x, y):
    """Mollweide (x in [-2√2, 2√2], y in [-√2, √2]) -> lon, lat in radians; NaN outside."""
    with np.errstate(invalid="ignore"):
        th = np.arcsin(y / SQ2)
        lat = np.arcsin((2 * th + np.sin(2 * th)) / np.pi)
        lon = np.pi * x / (2 * SQ2 * np.cos(th))
    bad = ~(np.abs(lon) <= np.pi)
    lon[bad] = np.nan
    lat[bad] = np.nan
    return lon, lat


def moll_forward(lon, lat):
    lat = np.asarray(lat, float)
    th = lat.copy()
    for _ in range(50):
        f = 2 * th + np.sin(2 * th) - np.pi * np.sin(lat)
        th = th - f / (2 + 2 * np.cos(2 * th) + 1e-12)
    return 2 * SQ2 / np.pi * lon * np.cos(th), SQ2 * np.sin(th)


# ---------------------------------------------------------------- drawing
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
        plt.rcParams["font.family"] = name
        # the latin subset lacks ∩ and ²; fall back to DejaVu for those glyphs
        plt.rcParams["font.family"] = [name, "DejaVu Serif"]
        print("font:", name, flush=True)
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable, using DejaVu Serif:", e, flush=True)
        plt.rcParams["font.family"] = "DejaVu Serif"


def deg2(x):
    return f"{x:,.0f}".replace(",", " ")


class Map:
    def __init__(self, ra0_deg, rect):
        """Centred on RA ra0_deg; rect: the ellipse's box (x0, y0, w, h) in figure pixels from the top-left."""
        self.ra0_deg = ra0_deg
        self.ra0 = np.radians(ra0_deg)
        x0, y0, w, h = rect
        self.rect = rect
        # pixel centres -> Mollweide plane
        xs = (np.arange(w) + 0.5) / w * 4 * SQ2 - 2 * SQ2
        ys = SQ2 - (np.arange(h) + 0.5) / h * 2 * SQ2
        X, Y = np.meshgrid(xs, ys)
        lon, lat = moll_inverse(X, Y)
        self.inside = np.isfinite(lon)
        ra = np.degrees(self.ra0 - lon) % 360.0    # RA increases to the left
        dec = np.degrees(lat)
        self.pix = np.full(lon.shape, -1)
        self.pix[self.inside] = hp.ang2pix(NSIDE_PLOT, ra[self.inside], dec[self.inside], lonlat=True)

    def sample(self, hmap):
        out = np.zeros(self.pix.shape, bool)
        out[self.inside] = hmap[self.pix[self.inside]]
        return out

    def to_fig(self, ra, dec):
        """RA, Dec in degrees -> figure pixel coordinates (from the top-left)."""
        lon = (self.ra0 - np.radians(ra) + np.pi) % (2 * np.pi) - np.pi
        x, y = moll_forward(lon, np.radians(dec))
        x0, y0, w, h = self.rect
        return x0 + (x + 2 * SQ2) / (4 * SQ2) * w, y0 + (SQ2 - y) / (2 * SQ2) * h


def edge(b, width=2):
    """Boundary pixels of a boolean raster, about `width` pixels thick."""
    e = np.zeros_like(b)
    for s in range(1, width + 1):
        for ax in (0, 1):
            for sh in (s, -s):
                e |= b & ~np.roll(b, sh, axis=ax)
    return e


def render(m, layers, A, path):
    """layers: CMB keys drawn this frame, bottom to top."""
    rgb = np.ones((H_PX, W_PX, 3))
    x0, y0, w, h = m.rect
    sub = rgb[y0:y0 + h, x0:x0 + w]
    sub[m.inside] = 1.0                       # white sky; white multiplies into the ground

    def over(mask, colour, alpha):
        c = np.array(to_rgb(colour))
        sub[mask] = (1 - alpha) * sub[mask] + alpha * c

    for k in layers:
        b = m.sample(A[f"map_{k}"])
        c, a = COLOURS[k]
        over(b, c, a)
        over(edge(b, 2) & m.inside, c, 0.95)
    dr1 = m.sample(A["map_dr1"])
    over(dr1, C_DR1, 1.0)
    over(edge(dr1, 2) & m.inside, "#24366E", 1.0)

    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_PX)
    ax.set_ylim(H_PX, 0)
    ax.axis("off")
    ax.imshow(rgb, extent=(0, W_PX, H_PX, 0), interpolation="nearest", zorder=0)

    # graticule: light, under nothing important
    gl = dict(color=MUTED, lw=0.9, alpha=0.45, zorder=2)
    dd = np.linspace(-90, 90, 361)
    for r in range(0, 360, 60):
        ax.plot(*m.to_fig(np.full_like(dd, r), dd), **gl)
    rr = np.linspace(m.ra0_deg - 179.999, m.ra0_deg + 179.999, 721)
    for d in (-60, -30, 0, 30, 60):
        ax.plot(*m.to_fig(rr, np.full_like(rr, d)), **gl)
    # ellipse outline
    ax.plot(*m.to_fig(np.full_like(dd, m.ra0_deg + 179.999), dd), color=MUTED, lw=1.4, zorder=3)
    ax.plot(*m.to_fig(np.full_like(dd, m.ra0_deg - 179.999), dd), color=MUTED, lw=1.4, zorder=3)
    lab = dict(fontsize=19, color=MUTED, zorder=4)
    for r in range(0, 360, 60):
        if abs(((r - m.ra0_deg + 180) % 360) - 180) > 165:
            continue
        x, y = m.to_fig(r, 0.0)
        ax.text(x + 10, y + 8, f"{r}°", ha="left", va="top", **lab)
    for d in (-30, 30, 60):     # Dec on the left limb; -60 on the right, clear of the legend
        x, y = m.to_fig(m.ra0_deg + 179.999, d)
        ax.text(x - 22, y, f"{d:+d}°".replace("-", "−"), ha="right", va="center", **lab)
    x, y = m.to_fig(m.ra0_deg - 179.999, -60)
    ax.text(x + 22, y, "−60°", ha="left", va="center", **lab)

    # legend: DR1 first, then the CMB layers in the order they arrive; the top is fixed
    # so each frame only adds a line beneath (four lines end at the bottom edge)
    hs = [Patch(facecolor=C_DR1, edgecolor="#24366E", lw=1.5,
                label=f"Euclid DR1 ({deg2(A['dr1_area'])} deg²)")]
    for k in layers:
        c, a = COLOURS[k]
        fc = tuple((1 - a) * 1.0 + a * np.array(to_rgb(c)))
        hs.append(Patch(facecolor=fc, edgecolor=c, lw=1.5,
                        label=f"{CMB[k][0]} ({deg2(A[f'{k}_area'])} deg²; ∩ DR1 {deg2(A[f'{k}_cap'])} deg²)"))
    leg = ax.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.0, 0.283), frameon=False,
                    fontsize=21, handlelength=1.6, handleheight=1.0, handletextpad=0.6,
                    labelspacing=0.45, borderaxespad=0.2, borderpad=0.5, fancybox=False)
    for t in leg.get_texts():   # a white halo keeps the text clean where it crosses the sky
        t.set_color(INK)
        t.set_path_effects([patheffects.withStroke(linewidth=7, foreground="white")])
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    print("wrote", path, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", help="npz holding the measured areas and plot maps (made if missing)")
    args = ap.parse_args()
    if args.cache and os.path.exists(args.cache):
        A = dict(np.load(args.cache))
    else:
        A = measure()
        if args.cache:
            np.savez(args.cache, **A)
    for k in ("dr1_area", "dr1_south", "dr1_north"):
        print(f"{k}: {float(A[k]):.1f} deg²")
    for k in CMB:
        print(f"{k}: >0.5 {float(A[k + '_area']):.1f}  >0 {float(A[k + '_area_gt0']):.1f}  "
              f"weighted {float(A[k + '_area_w']):.1f}  ∩DR1 (>0) {float(A[k + '_cap']):.1f}  "
              f"∩DR1 (>0.5) {float(A[k + '_cap_half']):.1f} deg²", flush=True)

    setup_font()
    # centre on the DR1 south field
    ra, dec = hp.pix2ang(NSIDE_PLOT, np.flatnonzero(A["map_dr1"]), lonlat=True)
    s = dec < 0
    ra0 = np.degrees(np.arctan2(np.sin(np.radians(ra[s])).mean(), np.cos(np.radians(ra[s])).mean())) % 360
    ra0 = 15 * round(ra0 / 15)
    print("centre RA", ra0)
    # the map ellipse, right-aligned; the legend sits in the empty lower-left corner
    h = int(0.92 * H_PX)
    w = 2 * h
    m = Map(ra0, (W_PX - w - 8, 6, w, h))
    frames = [("1_dr1", []), ("2_planck", ["planck"]), ("3_act", ["planck", "act"]),
              ("4_spt", ["planck", "act", "spt"])]
    for name, layers in frames:
        render(m, layers, A, os.path.join(OUT, f"napoli_footprint_{name}.png"))


if __name__ == "__main__":
    main()
