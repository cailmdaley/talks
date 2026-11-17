"""Pen drawings for the blinding and CLOE segments of the Paris CMBX SWG deck.

Five drawings, each at 2x the slide's figure box (3424 x 1542 px), on white (the build
multiplies white into the theme ground):

  paris26_sketch_blindspot.png  how blindspot makes a 3x2pt blinding shift
  paris26_sketch_anatomy.png    the three levels of a chain: sampler, likelihood, theory
  paris26_sketch_swap.png       eDR1like + CCL against CLOE: what is shared, what is swapped
  paris26_sketch_jax.png        plain CLOE against CLOE with its slow pieces in JAX
  paris26_sketch_control_variates.png  CARPool for the SPT covariance: paired and unpaired mocks

Every number drawn is quoted, with its source, in the notes card of the slide that shows it.
The style is a fine-pen scientific plate: thin ink strokes whose weight swells and tapers
along their length, open arrowheads, braces and dimension lines instead of boxes, stippling
only where tone carries meaning, small EB Garamond lettering (the deck's face) with italics
for variables. The random seed is fixed, so a redraw is identical. Each drawing is audited
on save: a label that touches another label or a stroke is reported.

Run in the cmbx container: app python make_cloe_sketches.py [drawing ...]
"""
import os
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
GARAMOND = os.path.join(HERE, "..", "node_modules", "@fontsource-variable", "eb-garamond", "files")

# euclid theme (house/themes/euclid.css)
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
ACCENT = "#435AA1"
CORAL = "#B5523B"   # the warm accent for the JAX pieces, outside the data palette

W, H, DPI = 3424, 1542, 200
# Text sizes in pt. At 200 dpi a point is 2.78 px of the PNG, shown at half size on the slide,
# so 1 pt = 1.39 px displayed: 24 pt is 33 px, the floor being 32.
SMALL, BODY, HEAD = 25, 29, 35
# The hand: stroke weight (px of the PNG at the swell of a stroke), how far a stroke wanders
# from its path (px), and the density of stippled tone (dots per 10^4 px^2).
WEIGHT, WOBBLE, STIPPLE = 3.4, 1.6, 6.0
GAP = 10   # the clearance the audit asks between a label and anything else (px)


# --------------------------------------------------------------------------- #
# fonts

def setup_font():
    """EB Garamond at weight 400, Latin + Latin-ext + Greek merged into one face per style,
    so that both plain text and mathtext (Greek included) set in Garamond."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import merge
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    for style, sub in (("normal", "Regular"), ("italic", "Italic")):
        parts = []
        for block in ("latin", "latin-ext", "greek"):
            f = TTFont(os.path.join(GARAMOND, f"eb-garamond-{block}-wght-{style}.woff2"))
            f.flavor = None
            f = instancer.instantiateVariableFont(f, {"wght": 400})
            parts.append(os.path.join(tmp, f"{block}-{style}.ttf"))
            f.save(parts[-1])
        f = merge.Merger().merge(parts)
        for rec in f["name"].names:
            if rec.nameID in (1, 16):
                rec.string = "Garamond Plate"
            elif rec.nameID in (2, 17):
                rec.string = sub
            elif rec.nameID == 4:
                rec.string = f"Garamond Plate {sub}"
            elif rec.nameID == 6:
                rec.string = f"GaramondPlate-{sub}"
        out = os.path.join(tmp, f"GaramondPlate-{sub}.ttf")
        f.save(out)
        font_manager.fontManager.addfont(out)
    plt.rcParams["font.family"] = "Garamond Plate"
    plt.rcParams["mathtext.fontset"] = "custom"
    plt.rcParams["mathtext.rm"] = "Garamond Plate"
    plt.rcParams["mathtext.bf"] = "Garamond Plate"
    plt.rcParams["mathtext.it"] = "Garamond Plate:italic"
    plt.rcParams["mathtext.fallback"] = "stix"


# --------------------------------------------------------------------------- #
# the pen

class Plate:
    """One drawing: an axes in PNG pixel units (origin bottom left) and a seeded pen."""

    def __init__(self, seed, w=W, h=H):
        self.w, self.h = w, h
        self.fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(0, h)
        self.ax.axis("off")
        self.rng = np.random.default_rng(seed)
        self.marks = []   # centre lines of every stroke, for the audit
        self.texts = []

    def _smooth(self, t, amp, waves=3):
        out = np.zeros_like(t)
        for k in range(waves):
            f = self.rng.uniform(0.5, 1.6) * (k + 1)
            out += self.rng.normal(0, amp / (k + 1)) * np.sin(2 * np.pi * f * t + self.rng.uniform(0, 2 * np.pi))
        return out

    @staticmethod
    def _dense(pts, step=5):
        pts = np.asarray(pts, float)
        out = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            n = max(int(np.hypot(*(b - a)) / step), 1)
            out.extend(a + (b - a) * (i / n) for i in range(1, n + 1))
        return np.array(out)

    @staticmethod
    def _normals(pts):
        d = np.gradient(pts, axis=0)
        n = np.stack([-d[:, 1], d[:, 0]], 1)
        return n / np.maximum(np.hypot(*n.T), 1e-9)[:, None]

    def pen(self, pts, w=WEIGHT, color=INK, taper=0.3, z=3, alpha=1.0, audit=True):
        """One stroke of a fine nib: swells in the middle, tapers at both ends."""
        pts = self._dense(pts)
        if len(pts) < 3:
            return pts
        s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        t = s / max(s[-1], 1)
        nrm = self._normals(pts)
        pts = pts + nrm * self._smooth(t, WOBBLE * min(1.0, s[-1] / 500))[:, None]   # short strokes stay steady
        nrm = self._normals(pts)
        ends = np.clip(np.minimum(s, s[-1] - s) / 40, 0, 1) ** 0.6   # taper over the last 40 px
        width = w * (taper + (1 - taper) * ends) * (1 + 0.12 * self._smooth(t, 1.0, waves=2))
        half = np.maximum(width, 0.6)[:, None] / 2
        poly = np.vstack([pts + nrm * half, (pts - nrm * half)[::-1]])
        self.ax.add_patch(Polygon(poly, closed=True, facecolor=color, edgecolor="none",
                                  alpha=alpha, zorder=z))
        if audit:
            self.marks.append(pts)
        return pts

    def line(self, p0, p1, bow=0.0, **kw):
        t = np.linspace(0, 1, 40)[:, None]
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        d = p1 - p0
        n = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1e-9)
        return self.pen(p0 + d * t + n * (bow * np.hypot(*d)) * np.sin(np.pi * t), **kw)

    def dashed(self, pts, dash=26, gap=16, **kw):
        pts = self._dense(pts, step=2)
        s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        on = (s % (dash + gap)) < dash
        start = None
        for i, o in enumerate(np.append(on, False)):
            if o and start is None:
                start = i
            elif not o and start is not None:
                if i - start > 3:
                    self.pen(pts[start:i], taper=0.5, **kw)
                start = None

    def head(self, tip, back, color=INK, size=30):
        """An engraver's arrowhead: a slender barb, filled, with a notched back."""
        tip, back = np.asarray(tip, float), np.asarray(back, float)
        d = (tip - back) / np.hypot(*(tip - back))
        n = np.array([-d[1], d[0]])
        poly = [tip, tip - d * size + n * size * 0.28, tip - d * size * 0.72, tip - d * size - n * size * 0.28]
        self.ax.add_patch(Polygon(poly, closed=True, facecolor=color, edgecolor=color, lw=0.4, zorder=4))
        self.marks.append(np.array(poly))

    def arrow(self, p0, p1, bow=0.0, color=INK, w=WEIGHT, size=30):
        pts = self.line(p0, p1, bow=bow, color=color, w=w)
        self.head(p1, pts[-6], color=color, size=size)

    def loop_arc(self, cx, cy, rx, ry, a0, a1, color=INK, w=WEIGHT, size=34):
        """An arc of the ellipse (cx, cy, rx, ry) from angle a0 to a1 (degrees), headed at a1."""
        t = np.radians(np.linspace(a0, a1, 120))
        pts = np.stack([cx + rx * np.cos(t), cy + ry * np.sin(t)], 1)
        pts = self.pen(pts, color=color, w=w, taper=0.4)
        self.head(pts[-1], pts[-8], color=color, size=size)

    def ring(self, cx, cy, rx, ry=None, angle=0, dashed=False, **kw):
        ry = rx if ry is None else ry
        t = np.linspace(0, 2 * np.pi, 160) + self.rng.uniform(0, 2 * np.pi)
        t = np.append(t, t[-1] + 0.12)   # the pen overshoots where it closes
        a = np.radians(angle)
        x, y = rx * np.cos(t), ry * np.sin(t)
        pts = np.stack([cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a)], 1)
        if dashed:
            self.dashed(pts, **kw)
        else:
            self.pen(pts, taper=0.55, **kw)

    def brace(self, a, b, depth=40, side=1, **kw):
        """A curly brace from a to b; side=+1 puts its point to the left of the walk a -> b."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        L = np.hypot(*(b - a))
        u = (b - a) / L
        n = np.array([-u[1], u[0]]) * side
        r = depth / 2
        q = np.linspace(0, np.pi / 2, 12)
        local = []   # (along, out)
        local += [(r * np.sin(t), r * (1 - np.cos(t))) for t in q]                      # out of a
        local += [(L / 2 - r * np.cos(t), r + r * np.sin(t)) for t in q]                # into the point
        local += [(L / 2 + r * (1 - np.cos(t)), 2 * r - r * np.sin(t)) for t in q[::-1]][::-1]
        local += [(L - r * np.sin(t), r * (1 - np.cos(t))) for t in q[::-1]]
        local = sorted(local, key=lambda p: p[0])
        pts = np.array([a + u * s + n * o for s, o in local])
        self.pen(pts, taper=0.15, **kw)
        return a + u * L / 2 + n * depth   # the point

    def dimension(self, x0, x1, y, label, color=INK, size=SMALL):
        """An engineer's dimension line: a rule between two end ticks, its value under it."""
        self.line((x0, y), (x1, y), color=color, w=WEIGHT * 0.8)
        for x in (x0, x1):
            self.line((x, y - 18), (x, y + 18), color=color, w=WEIGHT * 0.8)
        self.text((x0 + x1) / 2, y - 55, label, size=size, color=color)

    def stipple(self, n, sampler, color=INK, r=2.6, alpha=0.85):
        """n dots placed by sampler(n) -> (n, 2); the plate's only way of laying tone."""
        p = sampler(n)
        self.ax.scatter(p[:, 0], p[:, 1], s=(2 * r * 72 / DPI) ** 2, color=color, alpha=alpha, lw=0, zorder=2)
        self.marks.append(p)
        return p

    def text(self, x, y, s, size=BODY, color=INK, ha="center", va="center", italic=False, z=5, **kw):
        t = self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=z,
                         fontstyle="italic" if italic else "normal", **kw)
        self.texts.append(t)
        return t

    def heading(self, x, y, s, ha="center", rule=True, color=INK):
        """A plate heading: italic, with a hairline under it."""
        t = self.text(x, y, s, size=HEAD, ha=ha, italic=True, color=color)
        if rule:
            self.fig.canvas.draw()
            bb = t.get_window_extent()
            self.line((bb.x0 - 10, bb.y0 - 22), (bb.x1 + 10, bb.y0 - 22), w=WEIGHT * 0.55, color=color)
        return t

    def audit(self, name):
        """Report labels that touch each other or a stroke, and labels below the type floor."""
        self.fig.canvas.draw()
        boxes = [(t, t.get_window_extent()) for t in self.texts]
        bad = []
        for i, (t, bb) in enumerate(boxes):
            pad = bb.padded(GAP)
            if t.get_fontsize() < 24:
                bad.append(f"small type: {t.get_text()!r}")
            if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > self.w or bb.y1 > self.h:
                bad.append(f"off the plate: {t.get_text()!r}")
            for u, cc in boxes[i + 1:]:
                if bb.overlaps(cc):
                    bad.append(f"labels touch: {t.get_text()!r} / {u.get_text()!r}")
            for m in self.marks:
                inside = (m[:, 0] > pad.x0) & (m[:, 0] < pad.x1) & (m[:, 1] > pad.y0) & (m[:, 1] < pad.y1)
                if inside.any():
                    bad.append(f"stroke through {t.get_text()!r} at {m[inside][0].round()}")
                    break
        for b in bad:
            print(f"  [{name}] {b}")
        return bad

    def save(self, name):
        self.audit(name)
        path = os.path.join(IMG, name)
        self.fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(self.fig)
        print("wrote", path)


def check(p, x, y, size=34, color=INK):
    """A pen tick."""
    p.pen([(x, y), (x + size * 0.35, y - size * 0.45), (x + size, y + size * 0.55)], w=WEIGHT * 1.1,
          color=color, taper=0.2)


# --------------------------------------------------------------------------- #
# drawings

def blindspot():
    p = Plate(5)
    # a. the drawn point among the candidate draws in (Omega_c, A_s), and the reference
    ox, oy, ex, ey = 230, 520, 960, 1330
    p.arrow((ox, oy), (ex, oy))
    p.arrow((ox, oy), (ox, ey))
    p.text(ex, oy - 60, r"$\Omega_\mathrm{c}$", size=BODY, ha="right")
    p.text(ox - 30, ey - 20, r"$A_\mathrm{s}$", size=BODY, ha="right")
    cx, cy = 590, 920
    cov = np.array([[95 ** 2, -0.75 * 95 * 150], [-0.75 * 95 * 150, 150 ** 2]])
    draws = p.stipple(100, lambda n: p.rng.multivariate_normal((cx, cy), cov, n), r=4.0)
    hid = draws[np.argmin(np.hypot(*(draws - (cx + 120, cy - 170)).T))]
    p.ring(*hid, 26, color=ACCENT, w=WEIGHT * 0.9)
    p.line(hid + (22, -18), (hid[0] + 110, hid[1] - 100), color=ACCENT, w=WEIGHT * 0.6)
    p.text(hid[0] + 120, hid[1] - 130, "drawn point", size=SMALL, ha="left", color=ACCENT, italic=True)
    rx, ry = cx - 60, cy + 120
    p.ring(rx, ry, 17, w=WEIGHT * 0.9)
    p.line((rx - 30, ry), (rx + 30, ry), w=WEIGHT * 0.6)
    p.line((rx, ry - 30), (rx, ry + 30), w=WEIGHT * 0.6)
    p.line((rx + 22, ry + 22), (rx + 150, ry + 150), w=WEIGHT * 0.6)
    p.text(rx + 165, ry + 175, "reference", size=SMALL, ha="left", italic=True)
    p.heading(590, 1450, "a hidden point")
    p.heading(1720, 1450, "cloelib theory")
    p.heading(2700, 1450, "one draw")

    # b. the shift: cloelib theory there minus theory at the reference
    mx = 1720
    f = p.text(mx, 1200, r"$T(\theta_\mathrm{drawn})\;-\;T(\theta_\mathrm{ref})$", size=HEAD + 2)
    p.fig.canvas.draw()
    bb = f.get_window_extent()
    tip = p.brace((bb.x1, bb.y0 - 25), (bb.x0, bb.y0 - 25), depth=44, w=WEIGHT * 0.9)
    shift = p.text(mx, tip[1] - 60, "the shift", size=HEAD, color=ACCENT, italic=True)
    p.arrow(hid + (40, 25), (bb.x0 - 30, bb.y0 + 20), bow=0.12, color=ACCENT)
    p.fig.canvas.draw()
    fan = np.array([shift.get_window_extent().x1 + 40, tip[1] - 60])

    # the tracers it is built from: shear and positions; kappa not yet
    ty = 610
    p.text(1730, ty + 150, "tracers", size=SMALL, color=MUTED, italic=True)
    for x, sym, name, built in [(1450, "γ", "shear", True), (1730, "δ", "positions", True),
                                (2010, "κ", None, False)]:
        p.ring(x, ty, 74, dashed=not built, w=WEIGHT * (0.8 if built else 1.0), color=INK if built else MUTED)
        p.text(x, ty + 4, sym, size=HEAD, color=INK if built else MUTED, italic=True)
        if name:
            p.text(x, ty - 125, name, size=SMALL)
    p.text(2100, ty + 30, "not yet;", size=SMALL, color=MUTED, ha="left")
    p.text(2100, ty - 40, "cloelib has one", size=SMALL, color=MUTED, ha="left")

    # c. one draw, every statistic, added to the measured data vector
    sx = 2480
    for y, stat in [(1250, r"$C_\ell$"), (fan[1], r"$\xi$"), (760, "COSEBIs")]:
        p.arrow(fan, (sx - 40, y + (fan[1] - y) * 0.06), size=26)
        p.text(sx, y, stat, size=HEAD, ha="left")
    tip = p.brace((2900, 1320), (2900, 690), depth=44, w=WEIGHT * 0.9)
    for i, line in enumerate(["added to", "the measured", "data vector"]):
        p.text(tip[0] + 40, tip[1] + 85 - i * 85, line, size=BODY, ha="left")

    # below the rule: the spectroscopic blind and the validation
    p.line((120, 360), (3300, 360), w=WEIGHT * 0.5, color=MUTED)
    p.text(130, 270, "GC spectro", size=SMALL, ha="left", italic=True)
    p.text(130, 190, "same formula, its own script and draws", size=SMALL, ha="left", color=MUTED)
    p.text(1750, 270, "validation", size=SMALL, ha="left", italic=True)
    p.text(1750, 190, "recover an injected shift on synthetic DR1 vectors,", size=SMALL, ha="left", color=MUTED)
    p.text(1750, 112, "posterior width unchanged", size=SMALL, ha="left", color=MUTED)
    p.save("paris26_sketch_blindspot.png")


def anatomy():
    """The three levels as one loop: the sampler proposes, the theory predicts, the likelihood
    returns ln L to the sampler, which proposes again."""
    p = Plate(11)
    cx, cy, rx, ry = 1712, 790, 1330, 560
    p.loop_arc(cx, cy, rx, ry, 146, 47, color=ACCENT)       # over the top, left to right
    p.loop_arc(cx, cy, rx, ry, -47, -72, color=ACCENT)      # down the right, to the bottom
    p.loop_arc(cx, cy, rx, ry, 252, 218, color=ACCENT)      # up the left, back to the start
    p.text(cx, cy + ry + 80, r"proposes $\theta$", size=HEAD, color=ACCENT, italic=True)
    p.text(2620, 175, r"predicts $t(\theta)$", size=HEAD, color=ACCENT, italic=True)
    p.text(800, 175, r"returns $\ln L$", size=HEAD, color=ACCENT, italic=True)

    # sampler: nested shells of live points
    sx, sy = 382, 830
    p.heading(sx, 1180, "sampler")
    for k, (a, b) in enumerate([(200, 140), (138, 96), (82, 57), (38, 27)]):
        p.ring(sx, sy, a, b, angle=18, w=WEIGHT * (0.6 + 0.12 * k))
    rot = np.radians(18)
    rot = np.array([[np.cos(rot), np.sin(rot)], [-np.sin(rot), np.cos(rot)]])

    def live(n):
        q = p.rng.normal(0, 1, (4 * n, 2)) * [95, 60]
        q = q[(q[:, 0] ** 2 / 188 ** 2 + q[:, 1] ** 2 / 128 ** 2) < 1][:n]
        return (sx, sy) + q @ rot
    p.stipple(50, live, r=3.4)
    p.text(sx, 590, "nautilus", size=BODY)
    p.text(sx, 515, "38 parameters", size=SMALL, color=MUTED)

    # theory: cosmology and nuisances through the Limber projection to the bandpowers
    tx = 3010
    p.heading(tx, 1300, "theory")
    p.text(tx, 1110, "cosmology + nuisances", size=BODY)
    p.arrow((tx, 1010), (tx, 920), size=24, w=WEIGHT * 0.8)
    p.ring(tx, 830, 180, 82, w=WEIGHT * 0.8)
    p.text(tx, 830, "Limber", size=BODY)
    p.arrow((tx, 745), (tx, 655), size=24, w=WEIGHT * 0.8)
    p.text(tx, 590, "5×2pt bandpowers", size=BODY)
    p.text(tx, 515, "90 pairs, 651 bands", size=SMALL, color=MUTED)
    p.text(tx, 438, r"no $\kappa\kappa$", size=SMALL, color=MUTED)

    # likelihood: the data vector and the covariance, compared with t(theta)
    p.heading(cx, 990, "likelihood")
    p.text(cx, 840, "Gaussian", size=BODY)
    p.text(cx, 760, r"$\chi^2$ of $d - t(\theta)$", size=SMALL, color=MUTED)
    vx, vy, vh = 1440, 330, 330
    for x in (vx, vx + 60):
        p.line((x, vy), (x, vy + vh), w=WEIGHT * 0.6)
    for i in range(8):
        yy = vy + 22 + i * 40
        p.line((vx + 10, yy), (vx + 10 + p.rng.uniform(12, 40), yy), w=WEIGHT, taper=0.7)
    p.text(vx + 30, vy - 70, "data $d$", size=BODY)
    cx0, cy0, cw = 1650, 330, 330

    for (x0, y0), (x1, y1) in [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]:
        p.line((cx0 + x0 * cw, cy0 + y0 * cw), (cx0 + x1 * cw, cy0 + y1 * cw), w=WEIGHT * 0.6)

    def band(n):   # the covariance: dense on the diagonal, thinning away from it
        u = p.rng.uniform(0.03, 0.97, n)
        off = p.rng.laplace(0, 0.045, n)
        q = np.stack([u + off / 2, 1 - u + off / 2], 1)
        q = q[(q > 0.025).all(1) & (q < 0.975).all(1)]
        return (cx0, cy0) + q * cw
    p.stipple(700, band, r=2.4)
    p.text(cx0 + cw / 2, cy0 - 70, "covariance $C$", size=BODY)
    p.text(cx0 + cw / 2, cy0 - 145, "Gaussian + SSC", size=SMALL, color=MUTED)
    p.save("paris26_sketch_anatomy.png")


def swap():
    p = Plate(23)
    # what both chains share
    p.heading(80, 1440, "the same in both", ha="left")
    items = [("data vector", "GLASS mock and blinded TR1"),
             ("covariance", "Gaussian + SSC"),
             ("priors and scale cuts", "DR1-document priors"),
             ("sampler", "nautilus nested sampling")]
    y = 1210
    for head, sub in items:
        check(p, 78, y + 2, size=56)
        p.text(160, y, head, size=BODY, ha="left")
        p.text(160, y - 82, sub, size=SMALL, ha="left", color=MUTED)
        y -= 265

    # the swapped box
    bx0, bx1, by0, by1 = 1150, 3390, 110, 1480
    p.arrow((990, 800), (bx0 - 25, 800))
    for a, b in [((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))]:
        p.line(a, b, w=WEIGHT * 0.7)
    p.text((bx0 + bx1) / 2, 190, "only this box is swapped", size=SMALL, italic=True)
    gx, cw = 1690, 420
    for i, h in enumerate(["background", r"$P(k)$", "Limber", r"Gaussian $\chi^2$"]):
        p.text(gx + cw * i + cw / 2, 1360, h, size=BODY, italic=True)
    p.line((1200, 1280), (bx1 - 40, 1280), w=WEIGHT * 0.5)
    # the row rule breaks under P(k), which is one entry across both rows
    p.line((1200, 740), (gx + cw - 20, 740), w=WEIGHT * 0.5, color=MUTED)
    p.line((gx + 2 * cw + 20, 740), (bx1 - 40, 740), w=WEIGHT * 0.5, color=MUTED)
    rows = [(1010, "dr1_cmbx", ["eDR1like + CCL"], ["CCL", None, "CCL", "eDR1like"]),
            (530, "CLOE", ["CLOElib 0.11", "+ CLOElike 0.3"], ["CAMB", None, "CLOElib", "CLOElike"])]
    for ry, name, subs, cells in rows:
        p.text(1420, ry + 50, name, size=HEAD)
        for k, sub in enumerate(subs):
            p.text(1420, ry - 35 - 70 * k, sub, size=SMALL, color=MUTED)
        for i, txt in enumerate(cells):
            if txt is not None:
                p.text(gx + cw * i + cw / 2, ry, txt, size=BODY + 2)
    px = gx + cw * 1.5
    p.text(px, 860, "CAMB", size=BODY + 2)
    p.text(px, 770, "HMCode-2020", size=SMALL)
    p.text(px, 660, "the same", size=SMALL, color=MUTED, italic=True)
    p.text(px, 580, "in both", size=SMALL, color=MUTED, italic=True)
    p.save("paris26_sketch_swap.png")


def chain(p, labels):
    """Small arrows from each label to the next: the order in which the pieces run."""
    p.fig.canvas.draw()
    for a, b in zip(labels[:-1], labels[1:]):
        ea, eb = a.get_window_extent(), b.get_window_extent()
        y = (ea.y0 + ea.y1) / 2
        p.arrow((ea.x1 + 35, y), (eb.x0 - 35, y), size=24, w=WEIGHT * 0.8)


def jax():
    p = Plate(37)
    names = []
    xs = [1000, 1540, 2080, 2620]
    ty, by = 1220, 640
    # plain CLOE: four pieces in a chain
    p.text(330, ty + 30, "CLOE", size=HEAD)
    p.text(330, ty - 60, "one point per call", size=SMALL, color=MUTED)
    for x, (h, sub) in zip(xs, [("background", "CAMB"), (r"$P(k)$", "emulator"), ("Limber", "CLOElib"),
                                (r"Gaussian $\chi^2$", "CLOElike")]):
        names.append(p.text(x, ty + 30, h, size=BODY))
        p.text(x, ty - 55, sub, size=SMALL, color=MUTED)
    chain(p, names)
    names = []
    # where its 8.0 s go
    p.dimension(xs[0] - 190, xs[1] + 190, 1060, "2.7 s")
    p.dimension(xs[2] - 190, xs[2] + 190, 1060, "5.3 s", color=CORAL)

    # CLOE in JAX: three pieces ported, all inside one compiled function
    p.text(330, by + 30, "CLOE in JAX", size=HEAD, color=CORAL)
    p.text(330, by - 60, "1000 points per call", size=SMALL, color=MUTED)
    for x, (h, subs, ported) in zip(xs, [("background", [r"closed-form $H(z)$,", "CAMB tables once"], True),
                                         (r"$P(k)$", ["emulator network", "called in JAX"], True),
                                         ("Limber", ["CLOElib's own", "code, compiled"], True),
                                         (r"Gaussian $\chi^2$", ["the same"], False)]):
        if ported:
            p.text(x, by + 125, "JAX", size=SMALL, color=CORAL)
        names.append(p.text(x, by + 30, h, size=BODY))
        for k, sub in enumerate(subs):
            p.text(x, by - 55 - 76 * k, sub, size=SMALL, color=MUTED)
    chain(p, names)
    fx0, fx1, fy0, fy1 = 700, 2890, 400, 860
    for a, b in [((fx0, fy0), (fx1, fy0)), ((fx1, fy0), (fx1, fy1)), ((fx1, fy1), (fx0, fy1)), ((fx0, fy1), (fx0, fy0))]:
        p.line(a, b, w=WEIGHT * 0.7, color=CORAL)
    p.text((fx0 + fx1) / 2, 320, "one compiled function (jit), 1000 points per call (vmap)", size=SMALL, color=CORAL)

    # per point, on one node
    cx = 3165
    p.text(cx, 1470, "per point,", size=SMALL, color=MUTED)
    p.text(cx, 1395, "one 112-core node", size=SMALL, color=MUTED)
    p.text(cx, ty + 20, "71 ms", size=HEAD + 10)
    p.text(cx, ty - 95, "8.0 core-s", size=SMALL, color=MUTED)
    p.arrow((cx, ty - 160), (cx, by + 120))
    p.text(cx, by + 30, "4 ms", size=HEAD + 10, color=CORAL)
    p.text(cx, by - 95, "batched", size=SMALL, color=MUTED)
    p.text((fx0 + fx1) / 2, 120, r"agrees with plain CLOE to $4\times10^{-4}\,\sigma$ in every band",
           size=SMALL, color=MUTED)
    p.save("paris26_sketch_jax.png")


def control_variates():
    """CARPool for the SPT covariance: a few SPT-constrained mocks, each paired with an SPT-like
    mock of the same sky, and many SPT-like mocks alone. Sized for the figure column of a
    figure-text slide; the estimator is set in the slide's text."""
    p = Plate(41, w=2000, h=1290)
    R, r = 96, 56

    def sky(n):
        """One realization: a few clumps over a uniform floor, in the unit disc."""
        centres = p.rng.uniform(-0.55, 0.55, (4, 2))
        q = np.vstack([c + p.rng.normal(0, 0.16, (n // 6, 2)) for c in centres]
                      + [p.rng.uniform(-1, 1, (n, 2))])
        q = q[np.hypot(*q.T) < 0.82]
        return q[p.rng.permutation(len(q))[:n]]

    # few and accurate: each SPT-constrained mock beside an SPT-like mock of the same sky
    xy, xc = 220, 780
    mid = (xy + xc) / 2
    p.heading(mid, 1210, "few, accurate")
    p.text(mid, 1050, r"SPT-constrained, $N \approx$ 350–400", size=SMALL, color=MUTED)
    rows = [880, 675, 405]
    for k, y in enumerate(rows):
        q = sky(30)
        p.ring(xy, y, R, color=ACCENT, w=WEIGHT * 1.15)
        p.stipple(len(q), lambda n: (xy, y) + q * R, r=3.2)
        p.ring(xc, y, R, w=WEIGHT * 0.7)
        p.stipple(len(q), lambda n: (xc, y) + q * R, r=3.2)
        p.dashed([(xy + R + 30, y), (xc - R - 30, y)], dash=16, gap=12, w=WEIGHT * 0.6, color=MUTED)
        if k == 0:
            p.text(mid, y + 55, "same sky", size=SMALL, color=MUTED, italic=True)
            p.text(mid, y - 55, r"correlation $\rho$", size=SMALL, color=ACCENT)
    for x in (xy, mid, xc):
        for j in range(3):
            p.stipple(1, lambda n: np.array([[x, 570 - j * 30]]), r=3.6)
    p.text(xy, 242, "$y$", size=HEAD, italic=True, color=ACCENT)
    p.text(xy, 150, "SPT's own", size=SMALL, color=MUTED)
    p.text(xy, 72, "reconstruction", size=SMALL, color=MUTED)
    p.text(xc, 242, "$c$", size=HEAD, italic=True)
    p.text(xc, 150, "generic", size=SMALL, color=MUTED)
    p.text(xc, 72, "reconstruction", size=SMALL, color=MUTED)

    # many and approximate: SPT-like mocks alone, each its own sky
    gx = [1210 + 152 * i for i in range(5)]
    gy = [890, 730, 570, 410]
    mx = (gx[0] + gx[-1]) / 2
    p.heading(mx, 1210, "many, approximate")
    p.text(mx, 1050, r"SPT-like, any number $M$", size=SMALL, color=MUTED)
    for y in gy:
        for x in gx:
            q = sky(12)
            p.ring(x, y, r, w=WEIGHT * 0.55)
            p.stipple(len(q), lambda n: (x, y) + q * r, r=2.6)
    p.text(mx, 242, "$c$", size=HEAD, italic=True)
    p.text(mx, 150, "generic reconstruction,", size=SMALL, color=MUTED)
    p.text(mx, 72, "each on its own sky", size=SMALL, color=MUTED)
    p.save("paris26_sketch_control_variates.png")


def main():
    import sys
    setup_font()
    drawings = {"blindspot": blindspot, "anatomy": anatomy, "swap": swap, "jax": jax,
                "control_variates": control_variates}
    for name in sys.argv[1:] or drawings:
        drawings[name]()


if __name__ == "__main__":
    main()
