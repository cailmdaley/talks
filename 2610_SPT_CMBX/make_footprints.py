"""Footprint build-up for the SPT analysis call: the Euclid DR1 effective coverage, with
Euclid TR1 marked inside it, and the CMB lensing footprints laid over them one at a time
(Planck PR4, ACT DR6, SPT-3G Main, SPT-3G Summer), seen from the south and north
celestial poles.

Five PNGs with an identical frame, written to the shared images/ pool:
  spt_footprint_1_dr1.png         Euclid DR1, with TR1 inside it
  spt_footprint_2_planck.png      + Planck PR4
  spt_footprint_3_act.png         + ACT DR6
  spt_footprint_4_spt_main.png    + SPT-3G Main
  spt_footprint_5_spt_summer.png  + SPT-3G Summer (the summer-a and summer-b fields)
The slide stacks them, so each step adds exactly one layer. Both panels are polar
Lambert azimuthal equal-area views at one scale and one central RA. The south panel is
framed on DR1 south and both SPT fields, so every frame shares it.

Euclid DR1 is a DR1_R2 VMPZ WL effective-coverage map, chosen with --coverage:
  r2          all 8964 wide tiles (Aug 2025)
  validtiles  the 8389 tiles on the LE3-WL VALID list (F006), the slide's map
Euclid TR1 is the region the TR1 data vectors are measured on: the LE3 TR1 WL effective
coverage (HPEFFECTIVECOVERAGE-WL TR1 V1-1) degraded onto the closed TR1 South WL region at
NSIDE 2048 (analyses/glass_6x2pt_mocks/src/derive_tr1_wl_coverage.py).
Each pixel of both maps holds the fraction of it that is effectively covered; a footprint
is drawn where that fraction is > 0. Every area is effective, Σ effcov × pixel area:
DR1's and TR1's own, and each CMB footprint's overlap with DR1 (DR1 effcov summed over the
pixels where the CMB mask is > 0, with effcov upgraded from NSIDE 1024 to the mask's 2048
by giving each child its parent's value). The CMB footprints are drawn where the mask is
> 0.5. The maps are drawn at NSIDE 512.

The script also prints the areas the frames do not show: SPT-3G Main and Summer together
with DR1, Main ∩ Summer, each CMB footprint with TR1 (effective, TR1 effcov summed over
mask > 0), and the same overlaps with the RR2 photometric footprint at NSIDE 512 with both
maps > 1e-6 (the convention of results/scratch/footprints/footprint_areas.py, behind the
TR1 ∩ SPT Main = 149 deg² quoted before).

Run in the cmbx container (map loading wants a compute node, about 30 GB):
  app python make_footprints.py [--coverage r2|validtiles] [--preview] [--cache file.npz]
--preview renders only the last frame, to images/spt_footprint_<coverage>_preview.png.
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
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images")
INPUTS = "/leonardo_work/EUHPC_E07_074/cmbx/inputs"
COVERAGE = {"r2": f"{INPUTS}/euclid/dr1/vmpz/effcov/effcov_wl_dr1r2_nside1024.fits",
            "validtiles": f"{INPUTS}/euclid/dr1/vmpz/effcov/effcov_wl_dr1r2_validF006_nside1024.fits"}
TR1 = f"{INPUTS}/euclid/masks/tr1_wl_coverage_south_nside2048.fits"
RR2_PHOTO = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/footprints/RR2_Footprint_4096_photo.fits"
CMB = {  # key: (label, path)
    "planck": ("Planck PR4", f"{INPUTS}/planck/masks/mask_rotated.fits"),
    "act": ("ACT DR6", f"{INPUTS}/act/masks/mask_act_dr6_lensing_v1_healpix_nside_2048_baseline.fits"),
    "spt": ("SPT-3G Main", f"{INPUTS}/spt/masks/lensing/winter/"
            "mask2048_border_apod_mask_threshold0.1_allghz_dense.fits"),
    "summer": ("SPT-3G Summer", f"{INPUTS}/spt/masks/lensing/summer/"
               "spt3g_summer-a_summer-b_mask_apodized.fits"),
}
NSIDE_PLOT = 512
RA0 = 30.0   # central RA: the middle of DR1 south and SPT-3G Main together, as in the Napoli deck

# euclid theme (house/themes/euclid.css)
INK, MUTED = "#111418", "#535B67"
C_DR1, C_DR1_EDGE = "#435AA1", "#24366E"   # Euclid blue, opaque on top
C_TR1, C_TR1_EDGE = "#1C2756", "#0E1433"   # TR1: deep navy inside it
COLOURS = {"planck": ("#8A93A3", 0.30),    # (colour, fill alpha): a grey wash for the near-full sky
           "act": ("#C08A1E", 0.50),       # ochre
           "spt": ("#0E5E62", 0.66),       # dark teal
           "summer": ("#2F8F5B", 0.50)}    # sea green, Main's neighbour
# each CMB boundary where it crosses DR1, in its own hue, light enough to read on the blue
OUTLINE_ON_DR1 = {"planck": "#AEB5C2", "act": "#E0B04A", "spt": "#5FD0C8", "summer": "#A6E8A0"}

# canvas: the figure layout's body box less the .source line, 1712 x 723 px, at 2x
W_PX, H_PX, DPI = 3424, 1446, 200
FS = 24          # all type: 24 pt at 200 dpi, shown at half size = 33 px, over the 32 px floor
FS_GRID = 24


# ---------------------------------------------------------------- measurement
def upgrade(b, nside_out):
    """Upgrade a RING map by giving each child pixel its parent's value."""
    nside_in = hp.npix2nside(b.size)
    f = (nside_out // nside_in) ** 2
    nest = b[hp.nest2ring(nside_in, np.arange(b.size))]
    return np.repeat(nest, f)[hp.ring2nest(nside_out, np.arange(hp.nside2npix(nside_out)))]


def read(p):
    m = np.nan_to_num(hp.read_map(p, dtype=np.float64))
    m[m < 0] = 0.0                       # UNSEEN outside a footprint reads as zero
    return m


def measure(dr1_path):
    e = read(dr1_path)
    ns_e = hp.npix2nside(e.size)
    pa_e = hp.nside2pixarea(ns_e, degrees=True)
    _, dec = hp.pix2ang(ns_e, np.arange(e.size), lonlat=True)
    A = {"dr1_eff": e.sum() * pa_e,
         "dr1_eff_s": e[dec < 0].sum() * pa_e,
         "dr1_eff_n": e[dec >= 0].sum() * pa_e,
         "dr1_geom": (e > 0).sum() * pa_e,
         "map_dr1": hp.ud_grade((e > 0).astype(float), NSIDE_PLOT) > 0.5}
    t = read(TR1)
    ns = hp.npix2nside(t.size)
    pa = hp.nside2pixarea(ns, degrees=True)
    e_up = upgrade(e, ns)
    A.update(tr1_eff=t.sum() * pa, tr1_geom=(t > 0).sum() * pa,
             tr1_outside_dr1=((t > 0) & (e_up == 0)).sum() * pa,
             map_tr1=hp.ud_grade((t > 0).astype(float), NSIDE_PLOT) > 0.5)
    on = {}
    for k, (_, p) in CMB.items():
        m = read(p)
        assert hp.npix2nside(m.size) == ns, (k, hp.npix2nside(m.size))
        on[k] = m > 0
        A[f"{k}_area"] = (m > 0.5).sum() * pa
        A[f"{k}_cap"] = e_up[on[k]].sum() * pa
        A[f"{k}_cap_geom"] = (on[k] & (e_up > 0)).sum() * pa
        A[f"{k}_tr1"] = t[on[k]].sum() * pa
        A[f"{k}_tr1_geom"] = (on[k] & (t > 0)).sum() * pa
        A[f"map_{k}"] = hp.ud_grade(m, NSIDE_PLOT) > 0.5
        A[f"b512_{k}"] = hp.ud_grade(m, 512) > 1e-6
        print(f"{k}: nside {ns}", flush=True)
    both = on["spt"] | on["summer"]
    A.update(sptboth_cap=e_up[both].sum() * pa, sptboth_cap_geom=(both & (e_up > 0)).sum() * pa,
             sptboth_tr1=t[both].sum() * pa, sptboth_tr1_geom=(both & (t > 0)).sum() * pa,
             main_summer=(on["spt"] & on["summer"]).sum() * pa,
             sptboth_tr1_act=t[both & on["act"]].sum() * pa,
             spt_tr1_act=t[on["spt"] & on["act"]].sum() * pa)
    # the RR2 photometric footprint, at NSIDE 512 with both maps > 1e-6
    r = hp.ud_grade(read(RR2_PHOTO), 512) > 1e-6
    pa5 = hp.nside2pixarea(512, degrees=True)
    _, dec5 = hp.pix2ang(512, np.arange(r.size), lonlat=True)
    t5 = hp.ud_grade((t > 0).astype(float), 512) > 1e-6
    A.update(rr2_area=r.sum() * pa5, rr2_area_s=(r & (dec5 < 0)).sum() * pa5,
             rr2_and_tr1=(r & t5).sum() * pa5, tr1_512=t5.sum() * pa5)
    for k in CMB:
        A[f"{k}_rr2"] = (A[f"b512_{k}"] & r).sum() * pa5
    A["sptboth_rr2"] = ((A["b512_spt"] | A["b512_summer"]) & r).sum() * pa5
    A["spt_act_rr2"] = (A["b512_spt"] & A["b512_act"] & r).sum() * pa5
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
        # the projection is equal-area with unit radius, so every pixel covers the same solid angle
        self.pix_deg2 = ((xmax - xmin) / w) * ((ymax - ymin) / h) * np.degrees(1) ** 2
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
    return f"{float(x):,.0f}".replace(",", " ")


OUTLINE_PX = 4        # CMB outlines: 4 figure pixels, 2 px as shown
HOLE_DEG2 = 10.0      # holes smaller than this (point-source cuts) get no outline


def fill_small_holes(b, pix_deg2):
    """b with its holes smaller than HOLE_DEG2 filled, so only the outer boundary is outlined."""
    lab, n = ndimage.label(~b)
    size = np.bincount(lab.ravel(), minlength=n + 1) * pix_deg2
    small = size < HOLE_DEG2
    small[0] = False
    return b | small[lab]


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
        edges[k] = edge(fill_small_holes(b, P.pix_deg2), OUTLINE_PX) & P.inside
        over(edges[k], c, 0.95)
    dr1 = P.sample(A["map_dr1"])
    over(dr1, C_DR1, 1.0)
    over(edge(dr1, 2) & P.inside, C_DR1_EDGE, 1.0)
    tr1 = P.sample(A["map_tr1"])
    over(tr1, C_TR1, 1.0)
    over(edge(tr1, 2) & P.inside, C_TR1_EDGE, 1.0)
    euclid = dr1 | tr1
    fills = {k: P.sample(A[f"map_{k}"]) for k in layers}
    for i, k in enumerate(layers):   # CMB boundaries stay visible across the opaque Euclid layers,
        over(edges[k] & euclid, OUTLINE_ON_DR1[k], 1.0)
        for j in layers[i + 1:]:     # and each later footprint's wash dims the earlier boundaries it covers
            over(edges[k] & euclid & fills[j], *COLOURS[j])

    gl = dict(color=MUTED, lw=0.9, alpha=0.5, zorder=2)
    lab = dict(fontsize=FS_GRID, color=MUTED, zorder=5, path_effects=HALO)
    placed = [(x0 + 22, y0 + 18)]          # the title's corner; labels keep clear of each other

    # the side away from the pole carries RA, the side by the pole carries Dec, and both use the sides
    ra_sides, dec_sides = ("tlr", "blr") if P.p.s < 0 else ("blr", "lr")

    def label(x, y, text, side):
        near_corner = min(abs(x - x0), abs(x - x0 - w)) < 80 and min(abs(y - y0), abs(y - y0 - h)) < 80
        if near_corner or any(np.hypot(x - a, y - b) < 130 for a, b in placed):
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
                label(x, y, f"{d:+d}°".replace("-", "−"), side)
    ax.add_patch(matplotlib.patches.Rectangle((x0, y0), w, h, fill=False, ec=MUTED, lw=1.4, zorder=6))
    ax.text(x0 + 22, y0 + 18, title, ha="left", va="top", fontsize=FS, color=INK, zorder=7,
            path_effects=HALO)


# legend: fixed slots, so each frame fills the next one and nothing moves. The Euclid key
# (DR1 with its south and north parts, then TR1) sits under the north panel; the CMB key is a
# 2 x 2 grid under the south panel, filled row by row as the surveys arrive. Euclid rows carry
# their own effective area; each CMB survey carries only its effective overlap with DR1.
EUC_SLOTS = (0, 74, 142, 232)        # row centres, from the Euclid key's first row
CMB_ROWS = (0, 97)                   # row centres of the CMB grid, from its first row
ROW_HALF = 34                        # half a row's height, for spacing the keys from the panels
SWATCH_W, SWATCH_H = 100, 56


def legend_row(ax, x, rx, y, fc, ec, name, area, ink):
    if fc is not None:
        ax.add_patch(matplotlib.patches.Rectangle((x, y - SWATCH_H / 2), SWATCH_W, SWATCH_H,
                                                  fc=fc, ec=ec, lw=1.5, zorder=8))
    ax.text(x + (SWATCH_W + 28 if fc is not None else SWATCH_W + 60), y, name, ha="left",
            va="center_baseline", fontsize=FS, color=ink, zorder=8)
    ax.text(rx, y, f"{deg2(area)} deg²", ha="right", va="center_baseline", fontsize=FS, color=ink, zorder=8)


def render(panels, layers, A, path, leg, height):
    rgb = np.ones((H_PX, W_PX, 3))   # white multiplies into the slide ground
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_PX)
    ax.set_ylim(H_PX, 0)
    ax.axis("off")
    for P, title, rings in panels:
        draw_panel(ax, rgb, P, layers, A, title, rings)
    ax.imshow(rgb, extent=(0, W_PX, H_PX, 0), interpolation="nearest", zorder=0)

    euc = [(C_DR1, C_DR1_EDGE, "Euclid DR1", A["dr1_eff"], INK),
           (None, None, "south", A["dr1_eff_s"], MUTED),
           (None, None, "north", A["dr1_eff_n"], MUTED),
           (C_TR1, C_TR1_EDGE, "Euclid TR1", A["tr1_eff"], INK)]
    (ex, erx, ey), cmb_slots = leg
    for row, dy in zip(euc, EUC_SLOTS):
        legend_row(ax, ex, erx, ey + dy, *row)
    for k, (x, rx, y) in zip(layers, cmb_slots):
        c, a = COLOURS[k]
        legend_row(ax, x, rx, y, tuple((1 - a) + a * np.array(to_rgb(c))), c, CMB[k][0], A[f"{k}_cap"], INK)
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image          # trim the canvas to the content's height; every frame alike
    Image.open(path).crop((0, 0, W_PX, height)).save(path)
    print("wrote", path, flush=True)


def layout(A):
    """South panel on the left with the CMB key under it; on the right the north panel with the
    Euclid key under it. Both panels share one scale and one orientation: north up and east
    left, as on the sky, with the same great circle vertical through both poles (RA0 above the
    south pole, RA0 + 180° below the north pole), so RA increases to the left in both. The
    south panel holds DR1 south and both SPT fields, so every frame shares it."""
    ra0 = RA0
    sp, npj = Polar("south", ra0), Polar("north", ra0 + 180)
    sb = bbox_of(sp, [A["map_dr1"] & south_mask(), A["map_spt"], A["map_summer"]], margin=0.05)
    nb = bbox_of(npj, [A["map_dr1"] & ~south_mask()], margin=0.11,
                 extra=[(r, 84.0) for r in range(0, 360, 15)])   # the pole, with a 6° cap around it
    sw, sh = sb[1] - sb[0], sb[3] - sb[2]
    nw, nh = nb[1] - nb[0], nb[3] - nb[2]
    gap, pad = 40, 4
    cmb_h = CMB_ROWS[-1] + 2 * ROW_HALF
    euc_h = EUC_SLOTS[-1] + 2 * ROW_HALF
    W, H = W_PX - 2 * pad, H_PX - 2 * pad
    k = min((W - gap) / (sw + nw), (H - gap - cmb_h) / sh, (H - gap - euc_h) / nh)
    sr = (pad, pad, int(k * sw), int(k * sh))
    col = sr[0] + sr[2] + gap
    nr = (col, pad, int(k * nw), int(k * nh))
    # the CMB grid: two columns under the south panel
    y0 = sr[1] + sr[3] + gap + ROW_HALF
    half = sr[2] // 2
    cmb_slots = [(sr[0] + c * half + (60 if c else 0), sr[0] + (c + 1) * half - (60 if not c else 8),
                  y0 + dy) for dy in CMB_ROWS for c in (0, 1)]
    # the Euclid key: its last row (TR1) level with the CMB grid's last row, unless that would
    # bring it up against the north panel
    ey = max(cmb_slots[-1][2] - EUC_SLOTS[-1], nr[1] + nr[3] + gap + ROW_HALF)
    height = max(cmb_slots[-1][2], ey + EUC_SLOTS[-1]) + ROW_HALF + 16
    print(f"RA0 {ra0} / {ra0 + 180}  south {sr}  north {nr}  CMB key y {y0}  Euclid key y {ey}  "
          f"height {height}", flush=True)
    panels = [(Panel(sp, sb, sr), "South", [-15, -30, -45, -60, -75]),
              (Panel(npj, nb, nr), "North", [45, 60, 75])]
    return panels, ((col, col + nr[2] - 8, ey), cmb_slots), height


_SOUTH = None


def south_mask():
    global _SOUTH
    if _SOUTH is None:
        _, dec = hp.pix2ang(NSIDE_PLOT, np.arange(hp.nside2npix(NSIDE_PLOT)), lonlat=True)
        _SOUTH = dec < 0
    return _SOUTH


def report(A):
    f = {k: float(v) for k, v in A.items() if np.ndim(v) == 0}
    print(f"DR1 effective {f['dr1_eff']:.1f} deg² (south {f['dr1_eff_s']:.1f}, north {f['dr1_eff_n']:.1f}); "
          f"effcov > 0 covers {f['dr1_geom']:.1f} deg²")
    print(f"TR1 effective {f['tr1_eff']:.1f}, effcov > 0 {f['tr1_geom']:.1f} deg², "
          f"of it outside DR1 {f['tr1_outside_dr1']:.1f} deg²")
    print(f"RR2 photometric footprint (512, > 1e-6) {f['rr2_area']:.1f} deg² (south {f['rr2_area_s']:.1f}); "
          f"TR1 at 512 {f['tr1_512']:.1f}; RR2 ∩ TR1 {f['rr2_and_tr1']:.1f}")
    for k in list(CMB) + ["sptboth"]:
        area = f"mask > 0.5 {f[k + '_area']:.1f}  " if k in CMB else ""
        print(f"{k}: {area}∩DR1 effective {f[k + '_cap']:.1f} geometric {f[k + '_cap_geom']:.1f} | "
              f"∩TR1 effective {f[k + '_tr1']:.1f} geometric {f[k + '_tr1_geom']:.1f} | "
              f"∩RR2-photo {f[k + '_rr2']:.1f} deg²", flush=True)
    print(f"Main ∩ Summer (masks > 0) {f['main_summer']:.1f} deg²; ∩TR1 effective: Main ∩ ACT "
          f"{f['spt_tr1_act']:.1f}, (Main ∪ Summer) ∩ ACT {f['sptboth_tr1_act']:.1f}; "
          f"RR2-photo ∩ Main ∩ ACT {f['spt_act_rr2']:.1f} deg²")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", choices=COVERAGE, default="validtiles", help="the Euclid DR1 coverage map")
    ap.add_argument("--preview", action="store_true",
                    help="render only the last frame, as spt_footprint_<coverage>_preview.png")
    ap.add_argument("--cache", help="npz holding the measured areas and plot maps (made if missing); "
                                    "one per coverage")
    args = ap.parse_args()
    if args.cache and os.path.exists(args.cache):
        A = dict(np.load(args.cache))
    else:
        A = measure(COVERAGE[args.coverage])
        if args.cache:
            np.savez(args.cache, **A)
    report(A)

    setup_font()
    panels, leg, height = layout(A)
    frames = [("1_dr1", []), ("2_planck", ["planck"]), ("3_act", ["planck", "act"]),
              ("4_spt_main", ["planck", "act", "spt"]),
              ("5_spt_summer", ["planck", "act", "spt", "summer"])]
    if args.preview:
        frames = [(f"{args.coverage}_preview", frames[-1][1])]
    for name, layers in frames:
        render(panels, layers, A, os.path.join(OUT, f"spt_footprint_{name}.png"), leg, height)


if __name__ == "__main__":
    main()
