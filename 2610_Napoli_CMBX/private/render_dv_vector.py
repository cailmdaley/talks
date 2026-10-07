"""Pre-rendered matplotlib figures for the Napoli dv-vector slide.

Reads private/dv_vector.json (the validated, blinded data that make_dv_vector.py
writes) and writes private/dv_vector_app.json, which the slide's app
(private/dv_vector.js) inlines: for every (shear method, CMB survey) variant on disk,

  layers   one drawing of the whole data vector, a lower triangle of panels
           (columns gamma_1..6 then delta_1..6, the CMB lensing row at its base),
           split into four SVG layers that share one coordinate system ("world",
           W x H, the figure box at rest on the overview):
             tri    the 78 3x2pt panels: data, fiducial, scale cut
             krow   the 12 kappa panels with their residual strips
             close  the kappa row's tick labels, axis labels, panel names and key,
                    sized for the close-up camera
             far    row and column names and the key, sized for the overview
  details  one SVG per pair, the panel a click opens: data, fiducial, cut,
           residual strip, axes
  glyphs   every glyph and marker path the SVGs use, once; the SVGs reference
           them by id, so a glyph is stored once for the whole slide

and the geometry the app needs: the three cameras and the cells' rectangles.
The app only moves and fades these layers; nothing is drawn in the browser.

Run in the cmbx container, after make_dv_vector.py:
  app python private/render_dv_vector.py
"""
import io
import json
import os
import re
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator, LogLocator, NullFormatter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "dv_vector.json")
OUT = os.path.join(HERE, "dv_vector_app.json")

# ── style: a paper figure ───────────────────────────────────────────────────
INK, DATA = "#16191F", "#2B4A8B"
CUT_FILL, CUT_PT, FRAME = "#E3E7EE", "#9BA3AF", "#3A3F47"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "svg.hashsalt": "dv-vector", "svg.fonttype": "path",
    "axes.linewidth": 0.6, "axes.edgecolor": FRAME, "text.color": INK,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.color": FRAME, "ytick.color": FRAME, "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
})

# ── world geometry (units: SVG user units = pt in the figure = px at rest) ──
W, H = 1712.0, 771.0
GUT, G, MG, RM = 50.0, 6.0, 50.0, 8.0                 # left gutter, column gap, gamma|delta gap, right
CW = (W - GUT - 10 * G - MG - RM) / 12
T0, RG, MR = 8.0, 3.0, 8.0                            # top, row gap, gamma|delta row gap
KT, KM, KG, KS = 482.0, 190.0, 5.0, 48.0              # kappa row: top, main, gap, strip
RH = (KT - 16 - T0 - 11 * RG - MR) / 12
S_CLOSE = W / 861.0                                   # the close-up camera's zoom
VIEW_H = H / S_CLOSE
TR = [f"l{i}" for i in range(6)] + [f"g{i}" for i in range(6)]
R = 3.0                                                # residual strip half-range, sigma


def col_x(c):
    return GUT + c * (CW + G) + (MG - G if c >= 6 else 0)


def row_y(r):
    return KT if r == 12 else T0 + r * (RH + RG) + (MR if r >= 6 else 0)


def key_of(a, b):
    if a == "kappa" or b == "kappa":
        return "kappa_" + (b if a == "kappa" else a)
    rank = lambda t: (0 if t[0] == "g" else 10) + int(t[1:])  # noqa: E731
    a, b = sorted((a, b), key=rank)
    return f"{a}_{b}"


def sym(t):
    if t == "kappa":
        return r"\kappa"
    return (r"\gamma" if t[0] == "l" else r"\delta") + f"_{{{int(t[1:]) + 1}}}"


def name(t):
    return "CMB lensing" if t == "kappa" else ("source bin " if t[0] == "l" else "lens bin ") + str(int(t[1:]) + 1)


# ── data helpers ────────────────────────────────────────────────────────────
def prep(p, e):
    ell = np.asarray(p["ell"], float)
    f = 10.0 ** e
    return dict(ell=ell, v=ell * np.asarray(p["cl"]) * f, s=ell * np.asarray(p["sig"]) * f,
                t=ell * np.asarray(p["th"]) * f, fit=np.asarray(p["fit"], bool),
                r=(np.asarray(p["cl"]) - np.asarray(p["th"])) / np.asarray(p["sig"]))


def exponent(pairs, keys):
    m = max(np.max(np.abs(np.asarray(pairs[k]["ell"]) * np.asarray(pairs[k]["th"]))) for k in keys)
    return int(-np.floor(np.log10(m)))


def cut_spans(ell, fit):
    """ell intervals outside the cut, split halfway between bands (log)."""
    le = np.log10(ell)
    edges = np.concatenate([[le[0] - (le[1] - le[0]) / 2], (le[1:] + le[:-1]) / 2,
                            [le[-1] + (le[-1] - le[-2]) / 2]])
    out, i = [], 0
    while i < len(fit):
        if fit[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(fit) and not fit[j + 1]:
            j += 1
        lo = XLIM[0] if i == 0 else 10 ** edges[i]           # a cut reaching the end runs to the frame
        hi = XLIM[1] if j == len(fit) - 1 else 10 ** edges[j + 1]
        out.append((lo, hi))
        i = j + 1
    return out


XLIM = (100 / 1.12, 3000 * 1.12)


def ylim_of(d, pad=(0.08, 0.12)):
    vals = list(d["t"]) + [d["v"][i] + sg * d["s"][i] for i in np.flatnonzero(d["fit"]) for sg in (-1, 1)]
    lo, hi = min(min(vals), 0.0), max(vals)
    span = hi - lo
    return lo - pad[0] * span, hi + pad[1] * span


def errorbars(ax, x, y, s, color, lw, ms, z=3):
    xs = np.repeat(x, 3)
    ys = np.column_stack([y - s, y + s, np.full_like(y, np.nan)]).ravel()
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="butt", zorder=z)
    ax.plot(x, y, "o", color=color, ms=ms, mew=0, zorder=z + 0.1)


def draw_panel(ax, d, ylim, *, lw_bar, ms, lw_th, show_cut=True):
    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.set_ylim(*ylim)
    if show_cut:
        for a, b in cut_spans(d["ell"], d["fit"]):
            ax.axvspan(max(a, XLIM[0]), min(b, XLIM[1]), color=CUT_FILL, lw=0, zorder=0)
    ax.axhline(0, color=FRAME, lw=0.35, alpha=0.5, zorder=1)
    ax.plot(d["ell"], d["t"], color=INK, lw=lw_th, zorder=2, solid_joinstyle="round")
    out, inn = ~d["fit"], d["fit"]
    if out.any():
        errorbars(ax, d["ell"][out], d["v"][out], d["s"][out], CUT_PT, lw_bar, ms)
    if inn.any():
        errorbars(ax, d["ell"][inn], d["v"][inn], d["s"][inn], DATA, lw_bar, ms, z=4)


def draw_strip(ax, d, *, lw_bar, ms, rng=R):
    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.set_ylim(-rng, rng)
    for a, b in cut_spans(d["ell"], d["fit"]):
        ax.axvspan(max(a, XLIM[0]), min(b, XLIM[1]), color=CUT_FILL, lw=0, zorder=0)
    ax.axhspan(-1, 1, color="#CDD3DC", alpha=0.45, lw=0, zorder=0.5)
    ax.axhline(0, color=INK, lw=0.5, zorder=1)
    r = np.clip(d["r"], -rng * 0.94, rng * 0.94)
    for m, c, z in ((~d["fit"], CUT_PT, 3), (d["fit"], DATA, 4)):
        if m.any():
            ax.plot(d["ell"][m], r[m], "o", color=c, ms=ms, mew=0, zorder=z)


def bare(ax):
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    ax.xaxis.set_minor_formatter(NullFormatter())


def log_ticks(ax, major, minor):
    ax.xaxis.set_major_locator(FixedLocator([100, 1000]))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which="major", length=major, width=0.5)
    ax.tick_params(which="minor", length=minor, width=0.4)


def nice_ticks(lo, hi, n=3):
    raw = (hi - lo) / n
    mag = 10 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    return [round(v, 6) for v in np.arange(np.ceil(lo / step) * step, hi + 1e-12, step)]


def fmt(v):
    s = f"{0.0 if abs(v) < 1e-9 else v:g}"
    return f"${s}$"


def axes_at(fig, x, y, w, h):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def text_at(fig, x, y, s, **kw):
    return fig.text(x / W, 1 - y / H, s, **kw)


# ── SVG plumbing ────────────────────────────────────────────────────────────
SVG_NS, XL_NS = "http://www.w3.org/2000/svg", "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XL_NS)
NUM = re.compile(r"(-?\d+\.\d)\d+")


def svg_of(fig, w, h, glyphs):
    """The figure as compact SVG markup, its glyph and marker paths moved into `glyphs`."""
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True)
    plt.close(fig)
    root = ET.fromstring(buf.getvalue())
    for md in root.findall(f"{{{SVG_NS}}}metadata"):
        root.remove(md)
    for parent in list(root.iter()):
        for defs in [c for c in parent if c.tag == f"{{{SVG_NS}}}defs"]:
            for child in list(defs):
                if child.tag == f"{{{SVG_NS}}}path" and child.get("id"):
                    glyphs.setdefault(child.get("id"), ET.tostring(child, encoding="unicode"))
                    defs.remove(child)
            if not len(defs):
                parent.remove(defs)
    compact(root)
    for k in ("width", "height", "version"):
        root.attrib.pop(k, None)
    root.set("viewBox", f"0 0 {w:g} {h:g}")
    out = ET.tostring(root, encoding="unicode")
    # coordinates to 0.1 unit; scale() factors (glyph sizes) stay exact
    parts = re.split(r"(scale\([^)]*\))", out)
    out = "".join(s if s.startswith("scale(") else re.sub(r"(\d)\.0\b", r"\1", NUM.sub(r"\1", s)) for s in parts)
    out = re.sub(r">\s+<", "><", out)
    out = re.sub(r'd="([^"]*)"', lambda m: 'd="' + re.sub(r"\s*([MLZzCQ])\s*", r"\1", " ".join(m.group(1).split())) + '"', out)
    out = re.sub(r";\s+", ";", out).replace(": ", ":")
    out = out.replace("xlink:href=", "href=").replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', "")
    out = re.sub(r'style="([^"]*)"', lambda m: f'class="{style_class(m.group(1))}"', out)
    return out


STYLES = {}


def style_class(style):
    """One CSS class per distinct inline style, shared by every SVG of the slide."""
    style = style.strip().rstrip(";")
    if style not in STYLES:
        STYLES[style] = f"dv{len(STYLES):x}"
    return STYLES[style]


def compact(node):
    """Drop matplotlib's ids and wrapper groups and its invisible background patches."""
    g, path = f"{{{SVG_NS}}}g", f"{{{SVG_NS}}}path"
    for child in list(node):
        if child.tag == f"{{{SVG_NS}}}style":      # matplotlib's global joins; the app sets them per layer
            node.remove(child)
            continue
        compact(child)
        if child.tag == g:
            child.attrib.pop("id", None)
        if child.tag == path and child.get("style", "").replace(" ", "") in ("fill:none", "fill:none;"):
            node.remove(child)
            continue
    i = 0
    while i < len(node):
        child = node[i]
        if child.tag == g and not child.attrib:
            node.remove(child)
            for j, gc in enumerate(list(child)):
                node.insert(i + j, gc)
            i += len(child)
        elif child.tag == g and not len(child):
            node.remove(child)
        else:
            i += 1


# ── the world drawing, in layers ────────────────────────────────────────────
def world_fig():
    return plt.figure(figsize=(W / 72, H / 72), dpi=72)


def cell_rect(r, c):
    return dict(x=col_x(c), y=row_y(r), w=CW, h=KM if r == 12 else RH)


def kappa_strip(c):
    return dict(x=col_x(c), y=KT + KM + KG, w=CW, h=KS)


def layers(pairs, title, glyphs):
    cells = []
    for r, a in enumerate(TR):
        for c, b in enumerate(TR[: r + 1]):
            cells.append(dict(key=key_of(a, b), row=r, col=c, a=a, b=b))
    for c, b in enumerate(TR):
        cells.append(dict(key=key_of("kappa", b), row=12, col=c, a="kappa", b=b))
    fam_e = {f: exponent(pairs, [k for k in pairs if pairs[k]["family"] == f])
             for f in {p["family"] for p in pairs.values()}}

    # tri: each panel on its own y-range; frames only, no ticks
    fig = world_fig()
    for cl in cells:
        if cl["row"] == 12:
            continue
        p = pairs[cl["key"]]
        d = prep(p, fam_e[p["family"]])
        rc = cell_rect(cl["row"], cl["col"])
        ax = axes_at(fig, rc["x"], rc["y"], rc["w"], rc["h"])
        draw_panel(ax, d, ylim_of(d, (0.12, 0.12)), lw_bar=0.7, ms=2.6, lw_th=0.9)
        bare(ax)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
            sp.set_color("#7C838E")
    tri = svg_of(fig, W, H, glyphs)

    # krow: shared y per half, residual strips; tick marks here, labels in `close`
    half_keys = {h: [key_of("kappa", t) for t in TR[6 * h: 6 * h + 6]] for h in (0, 1)}
    half_ylim, half_e = {}, {}
    for h, keys in half_keys.items():
        e = exponent(pairs, keys)
        ds = [prep(pairs[k], e) for k in keys]
        lo = min(ylim_of(d)[0] for d in ds)
        hi = max(ylim_of(d)[1] for d in ds)
        half_ylim[h], half_e[h] = (lo, hi), e
    fig = world_fig()
    krow_axes = {}
    for c, t in enumerate(TR):
        k = key_of("kappa", t)
        h = c // 6
        d = prep(pairs[k], half_e[h])
        rc, st = cell_rect(12, c), kappa_strip(c)
        ax = axes_at(fig, rc["x"], rc["y"], rc["w"], rc["h"])
        draw_panel(ax, d, half_ylim[h], lw_bar=0.65, ms=2.9, lw_th=0.8)
        log_ticks(ax, 3.0, 1.6)
        ax.yaxis.set_major_locator(FixedLocator(nice_ticks(*half_ylim[h])))
        ax.tick_params(which="both", labelbottom=False, labelleft=False)
        axs = axes_at(fig, st["x"], st["y"], st["w"], st["h"])
        draw_strip(axs, d, lw_bar=0.65, ms=2.6)
        log_ticks(axs, 3.0, 1.6)
        axs.yaxis.set_major_locator(FixedLocator([-2, 0, 2]))
        axs.tick_params(which="both", labelbottom=False, labelleft=False)
        krow_axes[c] = (ax, axs)
    krow = svg_of(fig, W, H, glyphs)

    # close: the kappa row's labels at close-up size (seen at S_CLOSE)
    fs = 12.0
    fig = world_fig()
    for h in (0, 1):
        x0 = col_x(6 * h)
        e, (lo, hi) = half_e[h], half_ylim[h]
        Y = lambda v: KT + KM * (hi - v) / (hi - lo)  # noqa: E731
        for v in nice_ticks(lo, hi):
            text_at(fig, x0 - 4, Y(v), fmt(v), ha="right", va="center", fontsize=fs)
        RY = lambda v: KT + KM + KG + KS * (R - v) / (2 * R)  # noqa: E731
        for v in (-2, 0, 2):
            text_at(fig, x0 - 4, RY(v), f"${v:+d}$" if v else "$0$", ha="right", va="center", fontsize=fs)
        text_at(fig, x0 - 33, KT + KM / 2, rf"$\ell C_\ell\;[10^{{-{e}}}]$", rotation=90,
                ha="center", va="center", fontsize=fs + 1)
        text_at(fig, x0 - 33, KT + KM + KG + KS / 2, r"$\Delta/\sigma$", rotation=90,
                ha="center", va="center", fontsize=fs + 1)
        for c in range(6 * h, 6 * h + 6):
            st, rc = kappa_strip(c), cell_rect(12, c)
            for ell in (100, 1000):
                xx = st["x"] + st["w"] * (np.log10(ell) - np.log10(XLIM[0])) / (np.log10(XLIM[1]) - np.log10(XLIM[0]))
                text_at(fig, xx, st["y"] + st["h"] + 4, f"$10^{{{int(np.log10(ell))}}}$",
                        ha="center", va="top", fontsize=fs)
            text_at(fig, rc["x"] + rc["w"] - 6, rc["y"] + 6,
                    rf"${sym(TR[c])}\times\kappa$", ha="right", va="top", fontsize=fs + 2)
        mid = (col_x(6 * h) + col_x(6 * h + 5) + CW) / 2
        text_at(fig, mid, KT + KM + KG + KS + 22, r"$\ell$", ha="center", va="top", fontsize=fs + 2)
        # title and key at the top of this half's close-up view
        vx0 = 0.0 if h == 0 else col_x(6) - MG
        vy0 = H - VIEW_H
        text_at(fig, vx0 + GUT, vy0 + 26, title, ha="left", va="top", fontsize=fs + 2)
        key(fig, vx0 + GUT, vy0 + 52, fs)
    close = svg_of(fig, W, H, glyphs)

    # far: names of rows and columns, title and key, at overview size
    ff = 21.0
    fig = world_fig()
    for r, t in enumerate(TR + ["kappa"]):
        rc = cell_rect(r, 0)
        text_at(fig, GUT - 10, rc["y"] + rc["h"] / 2, f"${sym(t)}$", ha="right", va="center", fontsize=ff)
    for c, t in enumerate(TR):
        st = kappa_strip(c)
        text_at(fig, st["x"] + st["w"] / 2, st["y"] + st["h"] + 6, f"${sym(t)}$", ha="center",
                va="top", fontsize=ff)
    text_at(fig, col_x(5) + 30, T0 + 10, title, ha="left", va="top", fontsize=ff + 3)
    nb = sum(len(p["ell"]) for p in pairs.values())
    nf = sum(sum(p["fit"]) for p in pairs.values())
    text_at(fig, col_x(5) + 30, T0 + 42, f"90 spectra, {nb} bandpowers, {nf} inside the scale cut",
            ha="left", va="top", fontsize=ff - 2, color="#4A505A")
    key(fig, col_x(5) + 30, T0 + 82, ff - 2)
    far = svg_of(fig, W, H, glyphs)

    rects = []
    for cl in cells:
        rc = cell_rect(cl["row"], cl["col"])
        if cl["row"] == 12:
            rc = dict(rc, h=KM + KG + KS)
        rects.append(dict(key=cl["key"], a=cl["a"], b=cl["b"], **{k: round(v, 2) for k, v in rc.items()}))
    return dict(tri=tri, krow=krow, close=close, far=far), rects


def key(fig, x, y, fs):
    """Three entries in a row: blinded data, fiducial model, outside the scale cut."""
    u = fs / 12
    ax = axes_at(fig, x, y, 520 * u, 18 * u)
    ax.set_axis_off()
    ax.set_xlim(0, 520 * u)
    ax.set_ylim(0, 1)
    ax.plot([8 * u, 8 * u], [0.1, 0.9], color=DATA, lw=0.8 * u)
    ax.plot([8 * u], [0.5], "o", color=DATA, ms=3.2 * u, mew=0)
    ax.text(20 * u, 0.5, r"blinded data $\pm\,\sigma$", va="center", fontsize=fs)
    ax.plot([175 * u, 205 * u], [0.5, 0.5], color=INK, lw=0.9 * u)
    ax.text(213 * u, 0.5, "fiducial model", va="center", fontsize=fs)
    ax.add_patch(matplotlib.patches.Rectangle((330 * u, 0.05), 22 * u, 0.9, color=CUT_FILL, lw=0))
    ax.text(360 * u, 0.5, "outside the scale cut", va="center", fontsize=fs)


# ── details: one panel per pair ─────────────────────────────────────────────
DW, DH = 1320.0, 600.0


def detail(pairs, k, a, b, glyphs):
    p = pairs[k]
    e = exponent(pairs, [k])
    d = prep(p, e)
    fig = plt.figure(figsize=(DW / 72, DH / 72), dpi=72)
    ax_ = lambda x, y, w, h: fig.add_axes([x / DW, 1 - (y + h) / DH, w / DW, h / DH])  # noqa: E731
    fs = 21.0
    m = ax_(150, 96, DW - 190, 300)
    s = ax_(150, 404, DW - 190, 110)
    vals = list(d["t"]) + [d["v"][i] + sg * d["s"][i] for i in range(len(d["v"]))
                           if d["fit"][i] or abs(d["r"][i]) <= 4 for sg in (-1, 1)]
    lo, hi = min(min(vals), 0.0), max(vals)
    yl = (lo - 0.06 * (hi - lo), hi + 0.12 * (hi - lo))
    draw_panel(m, d, yl, lw_bar=1.4, ms=6.5, lw_th=1.6)
    # the strip spans every band up to +-12 sigma, at least +-3
    rng = float(min(12.0, max(R, np.ceil(1.1 * np.max(np.abs(d["r"]))))))
    draw_strip(s, d, lw_bar=1.4, ms=6.0, rng=rng)
    for ax in (m, s):
        log_ticks(ax, 7, 4)
        ax.tick_params(labelsize=fs)
        for sp in ax.spines.values():
            sp.set_linewidth(1.0)
    m.yaxis.set_major_locator(FixedLocator(nice_ticks(*yl)))
    m.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    m.tick_params(labelbottom=False)
    st = 2 if rng <= 4 else 5 if rng <= 10 else 10
    s.yaxis.set_major_locator(FixedLocator([v for v in range(-int(rng), int(rng) + 1) if v % st == 0 and abs(v) < rng]))
    s.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"$10^{{{int(round(np.log10(v)))}}}$"))
    m.set_ylabel(rf"$\ell C_\ell\;[10^{{-{e}}}]$", fontsize=fs + 2, labelpad=10)
    s.set_ylabel(r"$\Delta/\sigma$", fontsize=fs + 2, labelpad=10)
    s.set_xlabel(r"$\ell$", fontsize=fs + 2, labelpad=4)
    if a == "kappa":                                   # name a kappa cross galaxy-side first
        a, b = b, a
    fig.text(150 / DW, 1 - 22 / DH, rf"${sym(a)}\times{sym(b)}$", fontsize=fs + 9, va="top")
    nfit, n = int(sum(p["fit"])), len(p["fit"])
    note = ("all bands inside the scale cut" if nfit == n else "all bands outside the scale cut" if nfit == 0
            else f"{nfit} of {n} bands inside the scale cut")
    fig.text(150 / DW, 1 - 62 / DH, f"{name(a)} $\\times$ {name(b)}, blinded; {note}", fontsize=fs - 2,
             va="top", color="#4A505A")
    off = int(np.sum(np.abs(d["r"]) > rng * 0.94))
    if off:
        fig.text((DW - 40) / DW, 1 - 62 / DH, f"{off} {'band lies' if off == 1 else 'bands lie'} beyond the strip, drawn at its edge",
                 fontsize=fs - 4, va="top", ha="right", color="#4A505A", style="italic")
    return svg_of(fig, DW, DH, glyphs)


def main():
    src = json.load(open(SRC))
    out = dict(blind=src["blind"], shears=src["shears"], cmbs=src["cmbs"],
               world=dict(w=W, h=H), detail=dict(w=DW, h=DH), variants={})
    glyphs = {}
    rects = None
    for vk, pairs in src["variants"].items():
        shear, cmb = vk.split("|")
        title = f"TR1 {src['shears'][shear]} $\\times$ {src['cmbs'][cmb]}, blinded"
        lay, rects = layers(pairs, title, glyphs)
        det = {r["key"]: detail(pairs, r["key"], r["a"], r["b"], glyphs) for r in rects}
        out["variants"][vk] = dict(layers=lay, details=det)
        print(vk, {k: f"{len(v) / 1024:.0f} kB" for k, v in lay.items()},
              f"details {sum(len(v) for v in det.values()) / 1024:.0f} kB")
    v0 = dict(x=0.0, y=H - VIEW_H, w=W / S_CLOSE, h=VIEW_H)
    v1 = dict(x=col_x(6) - MG + 3, y=H - VIEW_H, w=W / S_CLOSE, h=VIEW_H)
    out["views"] = [v0, v1, dict(x=0.0, y=0.0, w=W, h=H)]
    out["cells"] = rects
    out["glyphs"] = "".join(glyphs.values()).replace("xlink:href=", "href=")
    out["css"] = "".join(f".{c}{{{s}}}" for s, c in STYLES.items())
    text = json.dumps(out, separators=(",", ":"))
    open(OUT, "w").write(text)
    print(f"glyphs {len(out['glyphs']) / 1024:.0f} kB; wrote {OUT} ({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
