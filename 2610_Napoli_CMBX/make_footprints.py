"""Footprint build-up for the Napoli CMBX talk: the Euclid DR1 wide regions with
the CMB lensing footprints laid over them one at a time (Planck PR4, ACT DR6,
SPT-3G Main), seen from the south and north celestial poles.

Four PNGs with an identical frame, written to the shared images/ pool:
  napoli_footprint_1_dr1.png     Euclid DR1-wide alone
  napoli_footprint_2_planck.png  + Planck PR4
  napoli_footprint_3_act.png     + ACT DR6
  napoli_footprint_4_spt.png     + SPT-3G Main
The slide stacks them, so each step adds exactly one layer. Both panels are
polar Lambert azimuthal equal-area views at one scale and one central RA.

DR1-wide is the two main regions of the DR1 observed VIS-mosaic footprint:
in each hemisphere, the largest connected group of pixels (8-neighbour, NSIDE
1024), plus any other group that comes within LINK_DEG of it. Smaller isolated
fields (equatorial patches, the fields around the north ecliptic pole, small
far-south pieces) are left out; their areas are printed.

Areas are measured at each mask's native NSIDE (DR1-wide is upgraded to 2048
for the overlaps; a binary map upgrades exactly):
  - a CMB footprint's area counts pixels with mask > 0.5 (within 0.4 % of the
    apodized mask's weighted sum), and the drawn fill uses the same threshold;
  - its overlap with DR1-wide is binary: mask > 0 and DR1-wide.
The maps are drawn at NSIDE 512.

Run in the cmbx container: app python make_footprints.py [--cache file.npz]
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
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

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
LINK_DEG = 1.0

# euclid theme (house/themes/euclid.css)
INK, MUTED = "#111418", "#535B67"
C_DR1, C_DR1_EDGE = "#435AA1", "#24366E"   # Euclid blue, opaque on top
COLOURS = {"planck": ("#8A93A3", 0.30),    # (colour, fill alpha): a grey wash for the near-full sky
           "act": ("#C08A1E", 0.50),       # ochre
           "spt": ("#1D8A8A", 0.62)}       # teal
# each CMB boundary where it crosses DR1, in its own hue, light enough to read on the blue
OUTLINE_ON_DR1 = {"planck": "#AEB5C2", "act": "#E0B04A", "spt": "#5FD0C8"}

# canvas: the figure layout's body box less the .source line, 1712 x 723 px, at 2x
W_PX, H_PX, DPI = 3424, 1446, 200
FS = 21          # legend and panel titles: 21 pt at 200 dpi, shown at half size = 29 px
FS_GRID = 19     # graticule labels: 26 px as shown


# ---------------------------------------------------------------- measurement
def dr1_wide(d, nside):
    """DR1-wide: per hemisphere, the largest connected group plus groups within LINK_DEG of it."""
    idx = np.flatnonzero(d)
    pos = np.full(d.size, -1)
    pos[idx] = np.arange(idx.size)
    nb = hp.get_all_neighbours(nside, idx)
    rows, cols = [], []
    for k in range(8):
        v = nb[k] >= 0
        v[v] &= d[nb[k][v]]
        rows.append(np.flatnonzero(v))
        cols.append(pos[nb[k][v]])
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    _, lab = connected_components(coo_matrix((np.ones(rows.size), (rows, cols)),
                                             shape=(idx.size, idx.size)), directed=False)
    size = np.bincount(lab)
    vec = np.array(hp.pix2vec(nside, idx)).T
    south = vec[:, 2] < 0
    keep = np.zeros(idx.size, bool)
    pa = hp.nside2pixarea(nside, degrees=True)
    for hemi in (south, ~south):
        comps = np.unique(lab[hemi])
        main = comps[np.argmax(size[comps])]
        tree = cKDTree(vec[lab == main])
        for c in comps:
            m = lab == c
            sep = 0.0 if c == main else np.degrees(tree.query(vec[m])[0].min())
            ra, dec = hp.pix2ang(nside, idx[m], lonlat=True)
            ra = (ra + 180) % 360 - 180
            kept = sep < LINK_DEG
            keep |= m & kept
            print(f"  DR1 group {size[c] * pa:7.1f} deg²  RA {ra.min():5.0f}..{ra.max():4.0f}  "
                  f"Dec {dec.min():4.0f}..{dec.max():4.0f}  {sep:6.2f}° from main  "
                  f"{'kept' if kept else 'dropped'}", flush=True)
    out = np.zeros_like(d)
    out[idx[keep]] = True
    return out


def upgrade_bool(b, nside_out):
    """Exact upgrade of a boolean RING map: each child pixel takes its parent's value."""
    nside_in = hp.npix2nside(b.size)
    f = (nside_out // nside_in) ** 2
    nest = b[hp.nest2ring(nside_in, np.arange(b.size))]
    return np.repeat(nest, f)[hp.ring2nest(nside_out, np.arange(hp.nside2npix(nside_out)))]


def measure():
    def read(p):
        return np.nan_to_num(hp.read_map(p, dtype=np.float64))

    d = read(DR1_PATH) > 0
    ns_d = hp.npix2nside(d.size)
    pa_d = hp.nside2pixarea(ns_d, degrees=True)
    wide = dr1_wide(d, ns_d)
    _, dec = hp.pix2ang(ns_d, np.arange(d.size), lonlat=True)
    A = {"dr1_all": d.sum() * pa_d,
         "dr1_wide_s": (wide & (dec < 0)).sum() * pa_d,
         "dr1_wide_n": (wide & (dec >= 0)).sum() * pa_d,
         "map_dr1": hp.ud_grade(wide.astype(float), NSIDE_PLOT) > 0.5}
    up = {}
    for k, (_, p) in CMB.items():
        m = read(p)
        ns = hp.npix2nside(m.size)
        pa = hp.nside2pixarea(ns, degrees=True)
        if ns not in up:
            w_up = upgrade_bool(wide, ns)
            _, dec2 = hp.pix2ang(ns, np.arange(w_up.size), lonlat=True)
            up[ns] = (w_up, upgrade_bool(d, ns), dec2 < 0)
        w_up, d_up, s_up = up[ns]
        A[f"{k}_area"] = (m > 0.5).sum() * pa
        A[f"{k}_area_w"] = m.sum() * pa
        A[f"{k}_cap"] = ((m > 0) & w_up).sum() * pa
        A[f"{k}_cap_s"] = ((m > 0) & w_up & s_up).sum() * pa
        A[f"{k}_cap_n"] = ((m > 0) & w_up & ~s_up).sum() * pa
        A[f"{k}_cap_all"] = ((m > 0) & d_up).sum() * pa
        A[f"map_{k}"] = hp.ud_grade(m, NSIDE_PLOT) > 0.5
        print(f"{k}: nside {ns}", flush=True)
    return A


# ---------------------------------------------------------------- projection
class Polar:
    """Polar Lambert azimuthal equal-area view, north up and east left as on the sky.
    South: the pole sits below the field (RA ra0 straight up); north: above it."""

    def __init__(self, hemi, ra0):
        self.s = -1 if hemi == "south" else 1
        self.ra0 = np.radians(ra0)

    def fwd(self, ra, dec):
        th = np.radians(90.0 - self.s * np.asarray(dec, float))
        r = 2 * np.sin(th / 2)
        ph = np.radians(ra) - self.ra0
        return -r * np.sin(ph), -self.s * r * np.cos(ph)

    def inv(self, x, y):
        r = np.hypot(x, y)
        ph = np.arctan2(-x, -self.s * y)
        with np.errstate(invalid="ignore"):
            th = 2 * np.arcsin(r / 2)
        dec = self.s * (90.0 - np.degrees(th))
        return np.degrees(ph + self.ra0) % 360.0, dec


class Panel:
    def __init__(self, proj, bbox, rect):
        """bbox (xmin, xmax, ymin, ymax) in projection units; rect (x0, y0, w, h) in figure pixels."""
        self.p, self.bbox, self.rect = proj, bbox, rect
        x0, y0, w, h = rect
        xmin, xmax, ymin, ymax = bbox
        X, Y = np.meshgrid(xmin + (np.arange(w) + 0.5) / w * (xmax - xmin),
                           ymax - (np.arange(h) + 0.5) / h * (ymax - ymin))
        ra, dec = proj.inv(X, Y)
        self.inside = np.isfinite(dec) & (proj.s * dec > 0)
        self.pix = np.full(X.shape, -1)
        self.pix[self.inside] = hp.ang2pix(NSIDE_PLOT, ra[self.inside], dec[self.inside], lonlat=True)

    def sample(self, hmap):
        out = np.zeros(self.pix.shape, bool)
        out[self.inside] = hmap[self.pix[self.inside]]
        return out

    def to_fig(self, ra, dec):
        x, y = self.p.fwd(ra, dec)
        x0, y0, w, h = self.rect
        xmin, xmax, ymin, ymax = self.bbox
        return x0 + (x - xmin) / (xmax - xmin) * w, y0 + (ymax - y) / (ymax - ymin) * h


def bbox_of(proj, hmaps, margin=0.06, extra=()):
    """Bounding box in projection units of the union of maps, plus any extra (RA, Dec) points."""
    b = np.zeros_like(hmaps[0])
    for m in hmaps:
        b |= m
    ra, dec = hp.pix2ang(NSIDE_PLOT, np.flatnonzero(b), lonlat=True)
    ra = np.concatenate([ra, [p[0] for p in extra]])
    dec = np.concatenate([dec, [p[1] for p in extra]])
    x, y = proj.fwd(ra, dec)
    dx, dy = x.max() - x.min(), y.max() - y.min()
    return (x.min() - margin * dx, x.max() + margin * dx, y.min() - margin * dy, y.max() + margin * dy)


def circ_mean_ra(hmap):
    ra, _ = hp.pix2ang(NSIDE_PLOT, np.flatnonzero(hmap), lonlat=True)
    r = np.radians(ra)
    return np.degrees(np.arctan2(np.sin(r).mean(), np.cos(r).mean())) % 360


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
        # the latin subset lacks ∩; DejaVu Serif supplies it
        plt.rcParams["font.family"] = [font_manager.FontProperties(fname=ttf).get_name(), "DejaVu Serif"]
    except Exception as e:  # noqa: BLE001
        print("EB Garamond unavailable, using DejaVu Serif:", e, flush=True)
        plt.rcParams["font.family"] = "DejaVu Serif"


def deg2(x):
    return f"{float(x):,.0f}".replace(",", " ")


def edge(b, width=2):
    """Boundary pixels of a boolean raster, about `width` pixels thick."""
    e = np.zeros_like(b)
    for s in range(1, width + 1):
        for ax in (0, 1):
            for sh in (s, -s):
                e |= b & ~np.roll(b, sh, axis=ax)
    return e


HALO = [patheffects.withStroke(linewidth=6, foreground="white")]


def crossings(px, py, rect):
    """Where a sampled curve crosses into the rect: (x, y, side) for each entry or exit."""
    x0, y0, w, h = rect
    ins = (px > x0) & (px < x0 + w) & (py > y0) & (py < y0 + h)
    out = []
    for i in np.flatnonzero(ins[1:] != ins[:-1]):
        j = i if ins[i] else i + 1
        x, y = px[j], py[j]
        side = min((abs(x - x0), "l"), (abs(x - x0 - w), "r"), (abs(y - y0), "t"), (abs(y - y0 - h), "b"))[1]
        out.append((x, y, side))
    return out


def draw_panel(ax, rgb, P, layers, A, title, dec_rings):
    x0, y0, w, h = P.rect
    sub = rgb[y0:y0 + h, x0:x0 + w]

    def over(mask, colour, alpha):
        sub[mask] = (1 - alpha) * sub[mask] + alpha * np.array(to_rgb(colour))

    edges = {}
    for k in layers:
        b = P.sample(A[f"map_{k}"])
        c, a = COLOURS[k]
        over(b, c, a)
        edges[k] = edge(b, 2) & P.inside
        over(edges[k], c, 0.95)
    dr1 = P.sample(A["map_dr1"])
    over(dr1, C_DR1, 1.0)
    over(edge(dr1, 2) & P.inside, C_DR1_EDGE, 1.0)
    for k in layers:            # CMB boundaries stay visible across the opaque DR1 layer
        over(edges[k] & dr1, OUTLINE_ON_DR1[k], 1.0)

    gl = dict(color=MUTED, lw=0.9, alpha=0.5, zorder=2)
    lab = dict(fontsize=FS_GRID, color=MUTED, zorder=5, path_effects=HALO)
    placed = [(x0 + 22, y0 + 18)]          # the title's corner; labels keep clear of each other

    # the side away from the pole carries RA, the side by the pole carries Dec, and both use the sides
    ra_sides, dec_sides = ("tlr", "blr") if P.p.s < 0 else ("blr", "lr")

    def label(x, y, text, side):
        near_corner = min(abs(x - x0), abs(x - x0 - w)) < 70 and min(abs(y - y0), abs(y - y0 - h)) < 70
        if near_corner or any(np.hypot(x - a, y - b) < 110 for a, b in placed):
            return
        placed.append((x, y))
        dx = {"l": 12, "r": -12}.get(side, 0)
        dy = {"t": 12, "b": -12}.get(side, 0)
        ax.text(x + dx, y + dy, text, ha={"l": "left", "r": "right"}.get(side, "center"),
                va={"t": "top", "b": "bottom"}.get(side, "center"), **lab)

    def curve(px, py):
        ins = (px >= x0) & (px <= x0 + w) & (py >= y0) & (py <= y0 + h)
        ax.plot(np.where(ins, px, np.nan), np.where(ins, py, np.nan), **gl)

    dd = np.linspace(-89.9, 89.9, 1500)
    dd = dd[P.p.s * dd > 0]
    rr = np.linspace(0, 360, 1441)
    pole = P.to_fig(0.0, P.p.s * 90.0)
    for r in range(0, 360, 30):
        px, py = P.to_fig(np.full_like(dd, r), dd)
        curve(px, py)
        for x, y, side in crossings(px, py, P.rect):
            if side in ra_sides and np.hypot(x - pole[0], y - pole[1]) > 300:   # spokes crowd at the pole
                label(x, y, f"{r}°", side)
    for d in dec_rings:
        px, py = P.to_fig(rr, np.full_like(rr, d))
        curve(px, py)
        for x, y, side in crossings(px, py, P.rect):
            if side in dec_sides:
                label(x, y, f"{d:+d}°".replace("-", "\u2212"), side)
    ax.add_patch(matplotlib.patches.Rectangle((x0, y0), w, h, fill=False, ec=MUTED, lw=1.4, zorder=6))
    ax.text(x0 + 22, y0 + 18, title, ha="left", va="top", fontsize=FS, color=INK, zorder=7,
            path_effects=HALO)


def render(panels, layers, A, path, legend_xy, height):
    rgb = np.ones((H_PX, W_PX, 3))   # white multiplies into the slide ground
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_PX)
    ax.set_ylim(H_PX, 0)
    ax.axis("off")
    for P, title, rings in panels:
        draw_panel(ax, rgb, P, layers, A, title, rings)
    ax.imshow(rgb, extent=(0, W_PX, H_PX, 0), interpolation="nearest", zorder=0)

    # legend: one fixed slot per entry, so each frame fills the next slot and nothing moves.
    # DR1 (DR1-wide) carries its own area; each CMB survey only its overlap with it.
    entries = [(C_DR1, C_DR1_EDGE, "Euclid DR1: "
                f"{deg2(float(A['dr1_wide_s']) + float(A['dr1_wide_n']))} deg²\n"
                f"(south {deg2(A['dr1_wide_s'])} + north {deg2(A['dr1_wide_n'])})")]
    for k in layers:
        c, a = COLOURS[k]
        entries.append((tuple((1 - a) + a * np.array(to_rgb(c))), c,
                        f"{CMB[k][0]} ∩ DR1: {deg2(A[f'{k}_cap'])} deg²"))
    lx, ly = legend_xy
    for (fc, ec, text), y in zip(entries, LEG_SLOTS):
        ax.add_patch(matplotlib.patches.Rectangle((lx, ly + y - 25), 90, 50, fc=fc, ec=ec, lw=1.5, zorder=8))
        two = "\n" in text      # a two-line entry hangs from the top of its swatch
        ax.text(lx + 115, ly + y - (32 if two else 0), text, ha="left", va="top" if two else "center_baseline",
                fontsize=FS, color=INK, zorder=8, linespacing=1.15)
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image          # trim the canvas to the panels' height; every frame alike
    Image.open(path).crop((0, 0, W_PX, height)).save(path)
    print("wrote", path, flush=True)


# legend slots (y of each entry's swatch centre, from the legend's top) and the legend box
LEG_SLOTS = (25, 185, 275, 365)
LEG_W, LEG_H = 1010, 400


def layout(A):
    """South panel on the left; on the right the north panel above the legend. Both panels share
    one scale and one orientation: north up and east left, as on the sky, with the same great
    circle vertical through both poles (RA0 above the south pole, RA0 + 180° below the north pole),
    so RA increases to the left in both."""
    ra0 = 5 * round(circ_mean_ra((A["map_dr1"] & south_mask()) | A["map_spt"]) / 5)
    sp, npj = Polar("south", ra0), Polar("north", ra0 + 180)
    sb = bbox_of(sp, [A["map_dr1"] & south_mask(), A["map_spt"]], margin=0.09)
    nb = bbox_of(npj, [A["map_dr1"] & ~south_mask()], margin=0.11,
                 extra=[(r, 84.0) for r in range(0, 360, 15)])   # the pole, with a 6° cap around it
    sw, sh = sb[1] - sb[0], sb[3] - sb[2]
    nw, nh = nb[1] - nb[0], nb[3] - nb[2]
    gap, pad = 40, 4
    W, H = W_PX - 2 * pad, H_PX - 2 * pad
    k = (W - gap) / (sw + nw)                      # right column as wide as the north panel
    if k * nw < LEG_W:                             # ... or as the legend, if that is wider
        k = (W - gap - LEG_W) / sw
    k = min(k, H / sh, (H - gap - LEG_H) / nh)
    sr = (pad, pad, int(k * sw), int(k * sh))
    col = sr[0] + sr[2] + gap
    nr = (col, pad, int(k * nw), int(k * nh))
    print(f"RA0 {ra0} / {ra0 + 180}  south {sr}  north {nr}", flush=True)
    panels = [(Panel(sp, sb, sr), "South", [-15, -30, -45, -60, -75]),
              (Panel(npj, nb, nr), "North", [45, 60, 75])]
    return panels, (col, sr[1] + sr[3] - LEG_H), sr[1] + sr[3] + pad


_SOUTH = None


def south_mask():
    global _SOUTH
    if _SOUTH is None:
        _, dec = hp.pix2ang(NSIDE_PLOT, np.arange(hp.nside2npix(NSIDE_PLOT)), lonlat=True)
        _SOUTH = dec < 0
    return _SOUTH


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
    print(f"DR1 observed: {float(A['dr1_all']):.1f} deg²; DR1-wide south {float(A['dr1_wide_s']):.1f}, "
          f"north {float(A['dr1_wide_n']):.1f} deg²")
    for k in CMB:
        print(f"{k}: >0.5 {float(A[k + '_area']):.1f}  weighted {float(A[k + '_area_w']):.1f}  "
              f"∩DR1-wide {float(A[k + '_cap']):.1f} (S {float(A[k + '_cap_s']):.1f}, N {float(A[k + '_cap_n']):.1f})  "
              f"∩DR1-all {float(A[k + '_cap_all']):.1f} deg²", flush=True)

    setup_font()
    panels, leg, height = layout(A)
    frames = [("1_dr1", []), ("2_planck", ["planck"]), ("3_act", ["planck", "act"]),
              ("4_spt", ["planck", "act", "spt"])]
    for name, layers in frames:
        render(panels, layers, A, os.path.join(OUT, f"napoli_footprint_{name}.png"), leg, height)


if __name__ == "__main__":
    main()
