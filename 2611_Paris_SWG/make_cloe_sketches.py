"""Hand-sketched diagrams of the CLOE segment of the Paris CMBX SWG deck.

Four drawings, each at 2x the slide's figure box (3424 x 1542 px), on white (the build
multiplies white into the theme ground):

  paris26_sketch_anatomy.png   the three levels of a chain: sampler, likelihood, theory
  paris26_sketch_swap.png      eDR1like + CCL against CLOE: what is shared, what is swapped
  paris26_sketch_jax.png       plain CLOE against CLOE with its slow pieces in JAX
  paris26_sketch_chain.png     where one chain's wall time goes, before and after

Every number drawn is quoted, with its source, in the notes card of the slide that shows it.
Lines are drawn twice with smooth random wobble and fills are layered translucent washes, so
the figures look sketched; the random seed is fixed, so a redraw is identical. Lettering is
Patrick Hand (SIL Open Font License, private/fonts/), with EB Garamond for the Greek letters.

Run in the cmbx container: app python make_cloe_sketches.py
"""
import os
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, patheffects
from matplotlib.patches import Polygon, Ellipse

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
FONTS = os.path.join(HERE, "private", "fonts")
GARAMOND = os.path.join(HERE, "..", "node_modules", "@fontsource-variable", "eb-garamond", "files")

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT, COBALT, TEAL, OCHRE = "#435AA1", "#2E417C", "#1D6C78", "#9C7414"
CORAL = "#B5523B"   # one warm accent for the JAX pieces, outside the data palette

W, H, DPI = 3424, 1542, 200
# Text sizes in pt. At 200 dpi a point is 2.78 px of the PNG, shown at half size on the slide,
# so 1 pt = 1.39 px displayed: 24 pt is 33 px, the floor being 32.
SMALL, BODY, HEAD, TITLE = 27, 31, 37, 45


# --------------------------------------------------------------------------- #
# fonts

def _ttf(src, family, tmp):
    """woff2 -> ttf under a family name of its own, so matplotlib can fall back glyph by glyph."""
    from fontTools.ttLib import TTFont
    f = TTFont(src)
    f.flavor = None
    for rec in f["name"].names:
        if rec.nameID in (1, 4, 16):
            rec.string = family
        elif rec.nameID == 6:
            rec.string = family.replace(" ", "")
    out = os.path.join(tmp, family.replace(" ", "") + ".ttf")
    f.save(out)
    font_manager.fontManager.addfont(out)
    return family


def setup_font():
    tmp = tempfile.mkdtemp()
    fams = [_ttf(os.path.join(FONTS, "patrick-hand-latin-400-normal.woff2"), "Hand Sketch", tmp),
            _ttf(os.path.join(FONTS, "patrick-hand-latin-ext-400-normal.woff2"), "Hand Sketch Ext", tmp),
            _ttf(os.path.join(GARAMOND, "eb-garamond-greek-wght-normal.woff2"), "Garamond Greek", tmp),
            _ttf(os.path.join(GARAMOND, "eb-garamond-latin-wght-normal.woff2"), "Garamond Latin", tmp),
            _ttf(os.path.join(GARAMOND, "eb-garamond-latin-ext-wght-normal.woff2"), "Garamond Ext", tmp)]
    plt.rcParams["font.family"] = fams
    plt.rcParams["mathtext.fontset"] = "custom"
    for k in ("rm", "it", "bf"):
        plt.rcParams[f"mathtext.{k}"] = "Hand Sketch"
    plt.rcParams["mathtext.fallback"] = "stix"




# --------------------------------------------------------------------------- #
# the sketching kit

class Sketch:
    """One drawing: an axes in PNG pixel units (origin bottom left) and a seeded hand."""

    def __init__(self, seed):
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.axis("off")
        self.rng = np.random.default_rng(seed)

    # -- noise ------------------------------------------------------------ #
    def _smooth(self, t, amp, waves=3):
        out = np.zeros_like(t)
        for k in range(waves):
            f = self.rng.uniform(0.6, 2.2) * (k + 1)
            out += self.rng.normal(0, amp / (k + 1)) * np.sin(2 * np.pi * f * t + self.rng.uniform(0, 2 * np.pi))
        return out

    def _wobble(self, pts, amp):
        pts = np.asarray(pts, float)
        seg = np.diff(pts, axis=0)
        s = np.concatenate([[0], np.cumsum(np.hypot(*seg.T))])
        t = s / max(s[-1], 1)
        d = np.gradient(pts, axis=0)
        n = np.stack([-d[:, 1], d[:, 0]], 1)
        n /= np.maximum(np.hypot(*n.T), 1e-9)[:, None]
        return pts + n * self._smooth(t, amp)[:, None]

    @staticmethod
    def _dense(pts, step=12):
        pts = np.asarray(pts, float)
        out = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            n = max(int(np.hypot(*(b - a)) / step), 1)
            out.extend(a + (b - a) * (i / n) for i in range(1, n + 1))
        return np.array(out)

    # -- strokes ---------------------------------------------------------- #
    def stroke(self, pts, color=INK, lw=3.0, amp=3.0, passes=2, alpha=1.0, z=3, overshoot=0.0):
        pts = self._dense(pts)
        if overshoot:
            a, b = pts[1] - pts[0], pts[-1] - pts[-2]
            pts = np.vstack([pts[0] - a / np.hypot(*a) * self.rng.uniform(0, overshoot), pts,
                             pts[-1] + b / np.hypot(*b) * self.rng.uniform(0, overshoot)])
        for p in range(passes):
            q = self._wobble(pts, amp * (1 + 0.4 * p))
            self.ax.plot(q[:, 0], q[:, 1], color=color, lw=lw * (1 - 0.3 * p),
                         alpha=alpha * (1 - 0.45 * p), solid_capstyle="round", solid_joinstyle="round", zorder=z)

    def line(self, p0, p1, bow=0.0, **kw):
        t = np.linspace(0, 1, 30)[:, None]
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        d = p1 - p0
        n = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1e-9)
        pts = p0 + d * t + n * (bow * np.hypot(*d)) * np.sin(np.pi * t)
        self.stroke(pts, **kw)
        return pts

    def arrow(self, p0, p1, color=INK, lw=3.2, bow=0.06, head=34, **kw):
        pts = self.line(p0, p1, bow=bow, color=color, lw=lw, **kw)
        tip, back = pts[-1], pts[-4]
        d = (tip - back) / np.hypot(*(tip - back))
        for ang in (0.45, -0.45):
            r = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
            self.stroke([tip, tip - head * (r @ d)], color=color, lw=lw, amp=1.0, passes=1)

    def box(self, x, y, w, h, color=INK, lw=3.0, wash=None, wash_alpha=0.5, z=3, r=18):
        """A box drawn side by side with overshooting corners, over an optional wash."""
        if wash is not None:
            self.wash(x, y, w, h, wash, alpha=wash_alpha, r=r)
        o = 14
        sides = [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)),
                 ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]
        for a, b in sides:
            self.line(a, b, bow=self.rng.uniform(-0.006, 0.006), color=color, lw=lw, amp=2.2,
                      overshoot=o, z=z)

    def rounded(self, x, y, w, h, r, n=14):
        c = [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]
        pts = []
        for cx, cy, a0 in c:
            a = np.radians(np.linspace(a0, a0 + 90, n))
            pts.extend(zip(cx + r * np.cos(a), cy + r * np.sin(a)))
        return np.array(pts)

    def wash(self, x, y, w, h, color, alpha=0.5, r=30, spread=10, layers=3):
        """Watercolour: translucent layers with independently wobbling edges, so edges pool."""
        base = self._dense(np.vstack([self.rounded(x, y, w, h, r), self.rounded(x, y, w, h, r)[:1]]), step=18)
        c = base.mean(0)
        for _ in range(layers):
            t = np.linspace(0, 1, len(base))
            radial = (base - c) / np.maximum(np.hypot(*(base - c).T), 1)[:, None]
            jitter = self._smooth(t, spread, waves=4)
            jitter[-1] = jitter[0]
            q = base + radial * jitter[:, None] + self.rng.normal(0, spread * 0.4, 2)
            self.ax.add_patch(Polygon(q, closed=True, facecolor=color, edgecolor=color,
                                      lw=1.5, alpha=alpha / layers * 1.6, zorder=1))

    def ellipse(self, cx, cy, rx, ry, angle=0, color=INK, lw=2.6, amp=3, z=3, passes=2):
        t = np.linspace(0, 2 * np.pi + 0.35, 90)
        a = np.radians(angle)
        x, y = rx * np.cos(t), ry * np.sin(t)
        pts = np.stack([cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a)], 1)
        self.stroke(pts, color=color, lw=lw, amp=amp, passes=passes, z=z)

    def text(self, x, y, s, size=BODY, color=INK, ha="center", va="center", bold=False, z=5, **kw):
        return self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=z,
                            path_effects=[patheffects.withStroke(linewidth=1.1, foreground=color)] if bold else None,
                            rotation=kw.pop("rotation", self.rng.uniform(-0.6, 0.6)),
                            **kw)

    def underline(self, x0, x1, y, color=INK, lw=3.0):
        self.line((x0, y), (x1, y), bow=self.rng.uniform(-0.01, 0.01), color=color, lw=lw, amp=2)

    def save(self, name):
        path = os.path.join(IMG, name)
        self.fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(self.fig)
        print("wrote", path)


def tint(color, f):
    """Mix ``color`` toward white: f = 0 is the colour, 1 is white."""
    c = np.array(matplotlib.colors.to_rgb(color))
    return tuple(c + (1 - c) * f)


# --------------------------------------------------------------------------- #
# drawings

def anatomy():
    s = Sketch(11)
    top, bot = 1440, 80
    # the three levels
    cols = {"sampler": (30, 620, COBALT), "likelihood": (790, 720, TEAL), "theory": (1650, 1745, OCHRE)}
    for name, (x, w, c) in cols.items():
        s.box(x, bot, w, top - bot, color=c, lw=3.4, wash=tint(c, 0.82), wash_alpha=0.55)
        s.text(x + w / 2, top - 70, name, size=TITLE, color=c, bold=True)

    # sampler: nested shells of live points
    sx, sy = 340, 860
    for k, (rx, ry) in enumerate([(250, 180), (180, 126), (112, 80), (55, 38)]):
        s.ellipse(sx, sy, rx, ry, angle=18, color=tint(COBALT, 0.15 + 0.15 * k), lw=2.6)
    pts = s.rng.normal(0, 1, (70, 2)) * [115, 72]
    a = np.radians(18)
    pts = pts @ np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    pts = pts[(pts[:, 0] ** 2 / 240 ** 2 + pts[:, 1] ** 2 / 170 ** 2) < 1]
    s.ax.scatter(sx + pts[:, 0], sy + pts[:, 1], s=26, color=COBALT, alpha=0.75, zorder=4, lw=0)
    s.text(340, 500, "nautilus", size=HEAD, color=INK)
    s.text(340, 410, "nested sampling", size=BODY, color=MUTED)
    s.text(340, 250, "draws θ in", size=BODY, color=INK)
    s.text(340, 165, "38 parameters", size=BODY, color=INK)

    # likelihood
    lx = 790 + 360
    s.text(lx, 1170, r"$\ln L = -\frac{1}{2}\,\chi^2$", size=HEAD, color=INK)
    s.text(lx, 1050, "Gaussian", size=BODY, color=MUTED)
    vx, vy = 860, 520
    s.box(vx, vy, 90, 380, color=TEAL, lw=2.6)
    for i in range(9):
        yy = vy + 25 + i * 40
        s.line((vx + 15, yy), (vx + 15 + s.rng.uniform(20, 60), yy), color=TEAL, lw=5, amp=1, passes=1)
    s.text(vx + 45, vy - 70, "data d", size=BODY, color=INK)
    cx0, cy0, cw = 1085, 540, 360
    s.box(cx0, cy0, cw, cw, color=TEAL, lw=2.6)
    for i in range(6):
        for j in range(6):
            d = abs(i - j)
            if d <= 1:
                s.wash(cx0 + 12 + j * 57, cy0 + cw - 68 - i * 57, 51, 51, TEAL,
                       alpha=0.65 if d == 0 else 0.25, r=10, spread=3, layers=2)
    s.text(cx0 + cw / 2, cy0 - 70, "covariance C", size=BODY, color=INK)
    s.text(cx0 + cw / 2, cy0 - 145, "Gaussian + SSC", size=SMALL, color=MUTED)
    s.text(lx, 210, "χ² of d − t(θ)", size=BODY, color=MUTED)

    # theory: cosmology above, nuisances below, into the projection
    tx, tw = 1700, 860
    s.box(tx, 880, tw, 400, color=OCHRE, lw=2.8, wash=tint(OCHRE, 0.7), wash_alpha=0.45)
    s.text(tx + tw / 2, 1215, "cosmology", size=HEAD, color=OCHRE, bold=True)
    s.text(tx + 40, 1110, "background  H(z), χ(z)", size=BODY, ha="left")
    s.text(tx + 40, 1015, "P(k, z)", size=BODY, ha="left")
    s.text(tx + 40, 935, "CAMB HMCode or emulator", size=SMALL, ha="left", color=MUTED)

    s.box(tx, 150, tw, 640, color=OCHRE, lw=2.8, wash=tint(OCHRE, 0.7), wash_alpha=0.45)
    s.text(tx + tw / 2, 725, "nuisances", size=HEAD, color=OCHRE, bold=True)
    for i, item in enumerate(["intrinsic alignment", "source, lens  Δz", "shear  m",
                              "magnification", "galaxy bias"]):
        s.text(tx + 50, 620 - i * 98, "·  " + item, size=BODY, ha="left")

    px, pw = 2680, 480
    oc = px + pw / 2
    s.box(px, 820, pw, 300, color=INK, lw=3.2, wash=tint(OCHRE, 0.45), wash_alpha=0.5)
    s.text(oc, 1010, "Limber", size=HEAD, bold=True)
    s.text(oc, 920, "projection", size=HEAD, bold=True)
    s.arrow((tx + tw + 10, 1080), (px - 10, 1000), color=INK)
    s.arrow((tx + tw + 10, 560), (px - 10, 850), color=INK, bow=0.1)
    s.arrow((oc, 805), (oc, 660), color=INK, bow=0.0)
    s.text(oc, 590, r"$C_\ell \rightarrow$ bandpowers", size=BODY)
    s.text(oc, 480, "5×2pt", size=HEAD, bold=True)
    s.text(oc, 390, "γγ  γδ  δδ  κγ  κδ", size=BODY)
    s.text(oc, 290, "90 pairs, 651 bands", size=SMALL, color=MUTED)
    s.text(oc, 210, "no κκ", size=SMALL, color=MUTED)

    # the calls between levels
    s.arrow((660, 1020), (780, 1020), color=COBALT, bow=-0.15)
    s.text(720, 1100, "θ", size=HEAD, color=COBALT)
    s.arrow((780, 230), (660, 230), color=TEAL, bow=-0.15)
    s.text(720, 315, "ln L", size=SMALL, color=TEAL)
    s.arrow((1520, 1020), (1640, 1020), color=TEAL, bow=-0.15)
    s.text(1580, 1100, "θ", size=HEAD, color=TEAL)
    s.arrow((1640, 230), (1520, 230), color=OCHRE, bow=-0.15)
    s.text(1580, 315, "t(θ)", size=SMALL, color=OCHRE)
    s.save("paris26_sketch_anatomy.png")


def swap():
    s = Sketch(23)
    # what both chains share
    x0, w0 = 30, 960
    s.box(x0, 80, w0, 1360, color=MUTED, lw=3.2, wash=tint(MUTED, 0.85), wash_alpha=0.55)
    s.text(x0 + w0 / 2, 1360, "the same in both", size=TITLE, color=MUTED, bold=True)
    items = [("data vector", "GLASS mock and blinded TR1"),
             ("covariance", "Gaussian + SSC"),
             ("priors and scale cuts", "DR1-document priors"),
             ("sampler: nautilus", "on a JAX explorer; each point\nreweighted to the exact one")]
    y = 1180
    for head, sub in items:
        s.line((x0 + 50, y + 4), (x0 + 72, y - 18), color=TEAL, lw=4, amp=1, passes=1)
        s.line((x0 + 72, y - 18), (x0 + 110, y + 30), color=TEAL, lw=4, amp=1, passes=1)
        s.text(x0 + 140, y, head, size=BODY, ha="left")
        s.text(x0 + 140, y - 60, sub, size=SMALL, ha="left", va="top", color=MUTED, linespacing=1.25)
        y -= 270

    # the swapped box
    bx, by, bw, bh = 1140, 80, 2255, 1360
    s.box(bx, by, bw, bh, color=INK, lw=2.6, wash=None)
    s.text(bx + bw / 2, 155, "only this box is swapped", size=BODY, color=INK)
    gx, cw = 1650, 435
    heads = ["background", "P(k)", "Limber", "Gaussian χ²"]
    for i, h in enumerate(heads):
        s.text(gx + cw * i + cw / 2, 1350, h, size=HEAD, color=INK)
    rows = [("dr1_cmbx", "eDR1like + CCL", 840, COBALT, ["CCL", None, "CCL", "eDR1like"]),
            ("CLOE", "CLOElib 0.11\n+ CLOElike 0.3", 300, OCHRE, ["CAMB", None, "CLOElib", "CLOElike"])]
    rh = 380
    for name, sub, ry, c, cells in rows:
        s.text(1395, ry + rh / 2 + 60, name, size=HEAD + 4, color=c, bold=True)
        s.text(1395, ry + rh / 2 - 10, sub, size=SMALL, color=MUTED, va="top", linespacing=1.25)
        for i, txt in enumerate(cells):
            if txt is None:
                continue
            s.box(gx + cw * i + 14, ry, cw - 28, rh, color=c, lw=3.0, wash=tint(c, 0.72), wash_alpha=0.55)
            s.text(gx + cw * i + cw / 2, ry + rh / 2, txt, size=HEAD + 4, bold=True, color=INK)
    # P(k): one cell across both rows
    s.box(gx + cw + 14, 300, cw - 28, 920, color=MUTED, lw=3.0, wash=tint(MUTED, 0.85), wash_alpha=0.55)
    s.text(gx + cw * 1.5, 810, "CAMB", size=HEAD + 4, bold=True)
    s.text(gx + cw * 1.5, 720, "HMCode-2020", size=SMALL)
    s.text(gx + cw * 1.5, 470, "the same\nin both", size=SMALL, color=MUTED, linespacing=1.25)

    # the fork from the shared inputs into either row
    s.arrow((x0 + w0 + 12, 760), (bx - 12, 760), color=INK, bow=0.1, head=30)
    s.save("paris26_sketch_swap.png")


def stamp(s, x, y, r=62):
    """A coral JAX badge."""
    s.ax.add_patch(Ellipse((x, y), 2 * r, 2 * r, facecolor=tint(CORAL, 0.55), edgecolor="none", alpha=0.9, zorder=6))
    s.ellipse(x, y, r, r, color=CORAL, lw=3, amp=2, z=7)
    s.text(x, y, "JAX", size=SMALL, color=INK, bold=True, z=8)


def jax():
    s = Sketch(37)
    xs, bw = 690, 535
    top_y, bot_y, rh = 930, 230, 330
    heads = [("background", "CAMB"), ("P(k)", "emulator"), ("Limber", "CLOElib"), (r"Gaussian $\chi^2$", "CLOElike")]
    jaxed = [("background", "closed-form H(z),\nCAMB tables once"), ("P(k)", "emulator network\ncalled in JAX"),
             ("Limber", "CLOElib's own\ncode, compiled"), (r"Gaussian $\chi^2$", "the same")]
    # plain CLOE
    s.text(330, top_y + rh / 2 + 55, "CLOE", size=TITLE, color=OCHRE, bold=True)
    s.text(330, top_y + rh / 2 - 35, "one point per call", size=SMALL, color=MUTED)
    for i, (h, sub) in enumerate(heads):
        x = xs + i * bw
        s.box(x + 12, top_y, bw - 24, rh, color=OCHRE, lw=3, wash=tint(OCHRE, 0.72), wash_alpha=0.55)
        s.text(x + bw / 2, top_y + rh - 95, h, size=HEAD, bold=True)
        s.text(x + bw / 2, top_y + 105, sub, size=BODY, color=INK)
    # where its 8.0 s go
    yb = top_y - 40
    s.line((xs + 20, yb), (xs + 2 * bw - 20, yb), color=OCHRE, lw=3, amp=2)
    s.text(xs + bw, yb - 65, "2.7 s", size=BODY, color=OCHRE)
    s.line((xs + 2 * bw + 20, yb), (xs + 3 * bw - 20, yb), color=CORAL, lw=5, amp=2)
    s.text(xs + 2.5 * bw, yb - 65, "5.3 s", size=BODY, color=CORAL, bold=True)

    # CLOE in JAX
    s.wash(xs - 10, bot_y - 60, 4 * bw + 20, rh + 140, CORAL, alpha=0.14, r=40, spread=12)
    s.box(xs - 10, bot_y - 60, 4 * bw + 20, rh + 140, color=CORAL, lw=3.4)
    s.text(xs + 2 * bw, bot_y + rh + 150, "one compiled function (jit), 1000 points per call (vmap)",
           size=BODY, color=CORAL)
    s.text(330, bot_y + rh / 2 + 55, "CLOE in JAX", size=TITLE, color=CORAL, bold=True)
    s.text(330, bot_y + rh / 2 - 35, "1000 points per call", size=SMALL, color=MUTED)
    for i, (h, sub) in enumerate(jaxed):
        x = xs + i * bw
        ported = i < 3
        s.box(x + 12, bot_y, bw - 24, rh, color=CORAL if ported else MUTED, lw=3,
              wash=tint(CORAL, 0.78) if ported else tint(MUTED, 0.85), wash_alpha=0.55)
        s.text(x + bw / 2, bot_y + rh - 80, h, size=HEAD, bold=True)
        s.text(x + bw / 2, bot_y + 110, sub, size=SMALL - 2, color=INK, linespacing=1.2)
        if ported:
            stamp(s, x + bw - 30, bot_y + rh + 40)

    # per point, on one node
    cx = 3110
    s.text(cx, 1390, "per point,", size=SMALL, color=MUTED)
    s.text(cx, 1320, "one 112-core node", size=SMALL, color=MUTED)
    s.text(cx, top_y + rh / 2 + 30, "71 ms", size=TITLE + 6, color=OCHRE, bold=True)
    s.text(cx, top_y + rh / 2 - 60, "8.0 core-s", size=SMALL, color=MUTED)
    s.text(cx, bot_y + rh / 2 + 30, "4 ms", size=TITLE + 6, color=CORAL, bold=True)
    s.text(cx, bot_y + rh / 2 - 60, "batched", size=SMALL, color=MUTED)
    s.arrow((cx, top_y - 30), (cx, bot_y + rh + 60), color=INK, bow=0.0)
    s.text(xs + 2 * bw, 80, r"agrees with plain CLOE to $4\times10^{-4}\,\sigma$ in every band",
           size=SMALL, color=MUTED)
    s.save("paris26_sketch_jax.png")


def chain():
    s = Sketch(53)
    x0, x1, m1 = 900, 3230, 120.0           # minutes 0..120 across the drawing
    X = lambda m: x0 + (x1 - x0) * m / m1
    rh = 170

    def bar(m_a, m_b, y, color, alpha=0.6, edge=True):
        s.wash(X(m_a), y - rh / 2, X(m_b) - X(m_a), rh, color, alpha=alpha, r=14, spread=6)
        if edge:
            s.box(X(m_a), y - rh / 2, X(m_b) - X(m_a), rh, color=color, lw=2.6, r=14)

    # axis
    ya = 150
    s.line((X(0), ya), (X(120), ya), color=MUTED, lw=2.6, amp=1.5)
    for m in (0, 30, 60, 90, 120):
        s.line((X(m), ya - 18), (X(m), ya + 18), color=MUTED, lw=2.4, amp=0.5, passes=1)
        s.text(X(m), ya - 70, f"{m} min" if m == 120 else f"{m}", size=SMALL, color=MUTED)

    # CLOE + emulator sampled directly: estimated, off the scale
    y = 1270
    s.text(60, y + 40, "CLOE + emulator,", size=BODY, ha="left")
    s.text(60, y - 45, "sampled directly", size=BODY, ha="left")
    s.wash(X(0), y - rh / 2, X(112) - X(0), rh, MUTED, alpha=0.22, r=14, spread=6)
    for k in np.arange(X(0) + 30, X(112), 55):
        s.line((k, y - rh / 2 + 10), (k + 60, y + rh / 2 - 10), color=MUTED, lw=1.8, amp=0.6, passes=1, alpha=0.6)
    s.arrow((X(100), y), (X(122), y), color=INK, bow=0.0)
    s.text(X(56), y, "4–5 h, estimated", size=HEAD, bold=True, color=INK,
           bbox=dict(boxstyle="round,pad=0.25", fc=tint(MUTED, 0.9), ec="none"))

    # the explore-and-reweight path of the comparison chains
    y = 830
    s.text(60, y + 40, "JAX explorer +", size=BODY, ha="left")
    s.text(60, y - 45, "exact reweight", size=BODY, ha="left")
    bar(0, 22, y, TEAL, alpha=0.55)
    bar(22, 72, y, OCHRE, alpha=0.6)
    s.wash(X(72), y - rh / 2, X(114) - X(72), rh, OCHRE, alpha=0.25, r=14, spread=10)
    s.text(X(11), y, "explore", size=SMALL)
    s.text(X(47), y, "exact reweight", size=BODY)
    s.text(X(93), y + rh / 2 + 55, "1.2–1.9 h", size=HEAD, bold=True, color=OCHRE)

    # CLOE in JAX, no reweight
    y = 420
    s.text(60, y + 40, "CLOE in JAX,", size=BODY, ha="left", color=CORAL)
    s.text(60, y - 45, "no reweight", size=BODY, ha="left", color=CORAL)
    bar(0, 16.4, y, CORAL, alpha=0.6)
    bar(16.4, 32.3, y, COBALT, alpha=0.4)
    s.text(X(8.2), y + rh / 2 + 55, "likelihood", size=SMALL, color=CORAL)
    s.text(X(24.4), y + rh / 2 + 55, "nautilus", size=SMALL, color=COBALT)
    s.text(X(8.2), y, "16", size=BODY, bold=True)
    s.text(X(24.4), y, "16", size=BODY, bold=True)
    s.text(X(34), y, "32 min", size=HEAD, bold=True, color=CORAL, ha="left")
    s.text(X(52), y - 10, "247 000 points, in 247 calls of 1000", size=SMALL, color=MUTED, ha="left")
    s.save("paris26_sketch_chain.png")


def main():
    setup_font()
    anatomy()
    swap()
    jax()
    chain()


if __name__ == "__main__":
    main()
