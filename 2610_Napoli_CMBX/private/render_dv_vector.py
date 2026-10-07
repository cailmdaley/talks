"""Pre-rendered matplotlib figures for the Napoli dv-vector slide.

Reads private/dv_vector.json (the validated, blinded data that make_dv_vector.py
writes) and writes private/dv_vector_app.json, which the slide's app
(private/dv_vector.js) inlines. For every (shear method, CMB survey) variant on disk:

  over     the overview: all 90 spectra as a lower triangle of panels (columns
           gamma_1..6 then delta_1..6, the CMB lensing row at its base), in "world"
           coordinates, the figure box at rest. Each row segment (a row's gamma
           columns, or its delta columns) shares one y range.
  near     the close-up of the CMB lensing row, with residual strips, drawn in
           the close-up camera's screen units; its columns sit exactly over the
           overview's columns, so the two crossfade in register during the zoom.
  details  one SVG per pair, the panel a click opens.
  glyphs   every glyph and marker path the SVGs use, once; the SVGs reference
           them by id, and their inline styles become shared CSS classes.

Every y axis, in every view, has the same two major ticks: 0 and the largest of
1, 2 or 5 x 10^k below the top of its range, labelled in units of 10^-e, where
10^-e is set once per block of rows (gamma-gamma, gamma-delta, delta-delta, and
each half of the CMB lensing row). Residual strips span +-3 sigma with ticks at
-2, 0 and 2; a band beyond the strip is drawn as a triangle on its edge.

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
from matplotlib.ticker import FixedLocator, LogLocator, NullFormatter, NullLocator  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "dv_vector.json")
OUT = os.path.join(HERE, "dv_vector_app.json")

# ── style: a paper figure ───────────────────────────────────────────────────
INK, DATA, FRAME, MUTED = "#16191F", "#2B4A8B", "#3A3F47", "#4A505A"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "svg.hashsalt": "dv-vector", "svg.fonttype": "path",
    "axes.linewidth": 0.6, "axes.edgecolor": FRAME, "text.color": INK,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.color": FRAME, "ytick.color": FRAME, "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
})

# ── overview geometry (world units: SVG user units = pt = px at rest) ───────
W, H = 1712.0, 771.0
GUT, G, MG, RM = 60.0, 6.0, 60.0, 34.0      # left gutter, column gap, gamma|delta gap, right
CW = (W - GUT - 10 * G - MG - RM) / 12
T0, RG, MR, KG, BOT = 8.0, 3.0, 8.0, 10.0, 34.0
RH = (H - T0 - BOT - 11 * RG - MR - KG) / 13.5        # a 3x2pt row; the kappa row is 1.5 of them
KH = 1.5 * RH
TR = [f"l{i}" for i in range(6)] + [f"g{i}" for i in range(6)]
R = 3.0                                                # residual strip half-range, sigma
XLIM = (100 / 1.12, 3000 * 1.12)


def col_x(c):
    return GUT + c * (CW + G) + (MG - G if c >= 6 else 0)


def row_y(r):
    if r == 12:
        return row_y(11) + RH + KG
    return T0 + r * (RH + RG) + (MR if r >= 6 else 0)


def row_h(r):
    return KH if r == 12 else RH


# ── close-up camera: the kappa row's halves, columns in register ────────────
VW = GUT + 6 * CW + 5 * G + 8                          # world width each close-up view shows
S_CLOSE = W / VW
VH = H / S_CLOSE
V0X = 0.0
V1X = col_x(6) - MG + 3                                # clear of gamma_6's right spine
# vertically, the close-up's main panels sit over the overview's kappa row
NM_TOP, NM_H, NS_GAP, NS_H = 200.0, 352.0, 12.0, 92.0  # close-up main and strip, screen px
VY = row_y(12) + KH / 2 - (NM_TOP + NM_H / 2) / S_CLOSE
VIEWS = [dict(x=V0X, y=VY, w=VW, h=VH), dict(x=V1X, y=VY, w=VW, h=VH), dict(x=0.0, y=0.0, w=W, h=H)]
NEAR_W = S_CLOSE * (V1X + VW - V0X)                    # the close-up drawing, screen px


def nx(world_x):
    """World x to close-up screen x."""
    return S_CLOSE * (world_x - V0X)


# ── labels ──────────────────────────────────────────────────────────────────
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


def fmt(v):
    return f"${0.0 if abs(v) < 1e-12 else v:g}$"


# ── data and axes ───────────────────────────────────────────────────────────
def prep(p, e):
    ell = np.asarray(p["ell"], float)
    f = 10.0 ** e
    return dict(ell=ell, v=ell * np.asarray(p["cl"]) * f, s=ell * np.asarray(p["sig"]) * f,
                t=ell * np.asarray(p["th"]) * f,
                r=(np.asarray(p["cl"]) - np.asarray(p["th"])) / np.asarray(p["sig"]))


def exponent(pairs, keys):
    m = max(np.max(np.abs(np.asarray(pairs[k]["ell"]) * np.asarray(pairs[k]["th"]))) for k in keys)
    return int(-np.floor(np.log10(m)))


def span(ds):
    """The data range of some panels: every band +- sigma and the fiducial."""
    lo = min(min(np.min(d["t"]), np.min(d["v"] - d["s"])) for d in ds)
    hi = max(max(np.max(d["t"]), np.max(d["v"] + d["s"])) for d in ds)
    return lo, hi


def yaxis(lo, hi):
    """Limits and the two major ticks: 0 and the largest 1, 2 or 5 x 10^k below the top."""
    top = max(hi, 1e-30)
    k = np.floor(np.log10(0.9 * top))
    tick = max(m * 10 ** k for m in (1, 2, 5) if m * 10 ** k <= 0.9 * top)
    lo = min(lo, 0.0)
    pad = 0.06 * (top - lo)
    return (lo - pad, top + pad), [0.0, float(f"{tick:.6g}")]


def errorbars(ax, x, y, s, lw, ms):
    xs = np.repeat(x, 3)
    ys = np.column_stack([y - s, y + s, np.full_like(y, np.nan)]).ravel()
    ax.plot(xs, ys, color=DATA, lw=lw, solid_capstyle="butt", zorder=3)
    ax.plot(x, y, "o", color=DATA, ms=ms, mew=0, zorder=4)


def frame(ax, ylim, yticks, *, tick_len, lw_frame, minor=True):
    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(FixedLocator([100, 1000]))
    if minor:
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10)))
    else:
        ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_locator(FixedLocator(yticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.tick_params(which="major", length=tick_len, width=lw_frame)
    ax.tick_params(which="minor", length=tick_len * 0.55, width=lw_frame * 0.8)
    ax.tick_params(which="both", labelbottom=False, labelleft=False)
    for sp in ax.spines.values():
        sp.set_linewidth(lw_frame)


def draw_panel(ax, d, ylim, yticks, *, lw_bar, ms, lw_th, tick_len, lw_frame, minor=True):
    frame(ax, ylim, yticks, tick_len=tick_len, lw_frame=lw_frame, minor=minor)
    ax.axhline(0, color=FRAME, lw=lw_frame * 0.6, alpha=0.45, zorder=1)
    ax.plot(d["ell"], d["t"], color=INK, lw=lw_th, zorder=2, solid_joinstyle="round")
    errorbars(ax, d["ell"], d["v"], d["s"], lw_bar, ms)


def draw_strip(ax, d, *, ms, tick_len, lw_frame):
    frame(ax, (-R, R), [-2, 0, 2], tick_len=tick_len, lw_frame=lw_frame)
    ax.axhspan(-1, 1, color="#CDD3DC", alpha=0.45, lw=0, zorder=0.5)
    ax.axhline(0, color=INK, lw=lw_frame, zorder=1)
    r, edge = d["r"], 0.9 * R
    inside = np.abs(r) <= edge
    ax.plot(d["ell"][inside], r[inside], "o", color=DATA, ms=ms, mew=0, zorder=4)
    for sgn, mk in ((1, "^"), (-1, "v")):
        m = sgn * r > edge
        if m.any():
            ax.plot(d["ell"][m], np.full(m.sum(), sgn * edge), mk, color=DATA, ms=ms * 1.25, mew=0, zorder=4)


def axes_at(fig, x, y, w, h, fw, fh):
    return fig.add_axes([x / fw, 1 - (y + h) / fh, w / fw, h / fh])


def text_at(fig, x, y, s, fw, fh, **kw):
    return fig.text(x / fw, 1 - y / fh, s, **kw)


def key(fig, x, y, fs, fw, fh):
    """Two entries in a row: blinded data, fiducial model."""
    u = fs / 12
    ax = axes_at(fig, x, y, 330 * u, 18 * u, fw, fh)
    ax.set_axis_off()
    ax.set_xlim(0, 330 * u)
    ax.set_ylim(0, 1)
    ax.plot([8 * u, 8 * u], [0.1, 0.9], color=DATA, lw=0.8 * u)
    ax.plot([8 * u], [0.5], "o", color=DATA, ms=3.2 * u, mew=0)
    ax.text(20 * u, 0.5, r"blinded data $\pm\,\sigma$", va="center", fontsize=fs)
    ax.plot([175 * u, 205 * u], [0.5, 0.5], color=INK, lw=0.9 * u)
    ax.text(213 * u, 0.5, "fiducial model", va="center", fontsize=fs)


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


# ── the variant's panels, and their axes ────────────────────────────────────
def segments(pairs):
    """Every row segment (row, half) with its cells, block exponent, y limits and ticks."""
    cells = {}
    for r, a in enumerate(TR):
        for c, b in enumerate(TR[: r + 1]):
            cells[(r, c)] = key_of(a, b)
    for c, b in enumerate(TR):
        cells[(12, c)] = key_of("kappa", b)
    block = lambda r, h: ("kappa" if r == 12 else "a" if r < 6 else "b", h)  # noqa: E731
    blocks = {}
    for (r, c), k in cells.items():
        blocks.setdefault(block(r, c // 6), []).append(k)
    e_of = {b: exponent(pairs, ks) for b, ks in blocks.items()}
    segs = {}
    for (r, c), k in cells.items():
        segs.setdefault((r, c // 6), []).append((c, k))
    out = {}
    for (r, h), cs in segs.items():
        e = e_of[block(r, h)]
        ylim, ticks = yaxis(*span([prep(pairs[k], e) for _, k in cs]))
        out[(r, h)] = dict(cols=sorted(cs), e=e, ylim=ylim, ticks=ticks)
    return cells, out, e_of


def overview(pairs, title, glyphs, segs, e_of):
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
    fs_tick, fs_name = 16.0, 21.0
    for (r, h), sg in segs.items():
        for c, k in sg["cols"]:
            d = prep(pairs[k], sg["e"])
            ax = axes_at(fig, col_x(c), row_y(r), CW, row_h(r), W, H)
            draw_panel(ax, d, sg["ylim"], sg["ticks"], lw_bar=0.7, ms=2.5, lw_th=0.85,
                       tick_len=2.4, lw_frame=0.5, minor=False)
        # tick labels on the segment's leftmost panel only
        c0 = sg["cols"][0][0]
        lo, hi = sg["ylim"]
        for v in sg["ticks"]:
            y = row_y(r) + row_h(r) * (hi - v) / (hi - lo)
            text_at(fig, col_x(c0) - 4, y, fmt(v), W, H, ha="right", va="center", fontsize=fs_tick)
    # one unit per block, rotated, in the gutter beside its rows
    spans = {("a", 0): (0, 5), ("b", 0): (6, 11), ("b", 1): (6, 11), ("kappa", 0): (12, 12), ("kappa", 1): (12, 12)}
    for (b, h), (r0, r1) in spans.items():
        y0, y1 = row_y(r0), row_y(r1) + row_h(r1)
        text_at(fig, col_x(6 * h) - 42, (y0 + y1) / 2, rf"$\times 10^{{-{e_of[(b, h)]}}}$", W, H,
                rotation=90, ha="center", va="center", fontsize=fs_tick)
    # row names at the row's end, column names under the kappa row
    for r, t in enumerate(TR + ["kappa"]):
        last = r if r < 12 else 11
        text_at(fig, col_x(last) + CW + 6, row_y(r) + row_h(r) / 2, f"${sym(t)}$", W, H,
                ha="left", va="center", fontsize=fs_name)
    for c, t in enumerate(TR):
        text_at(fig, col_x(c) + CW / 2, row_y(12) + KH + 6, f"${sym(t)}$", W, H, ha="center",
                va="top", fontsize=fs_name)
    x0 = col_x(3) + 30
    text_at(fig, x0, T0 + 4, title, W, H, ha="left", va="top", fontsize=fs_name + 3)
    nb = sum(len(p["ell"]) for p in pairs.values())
    text_at(fig, x0, T0 + 38, rf"$\ell C_\ell$ of 90 spectra, {nb} bandpowers", W, H,
            ha="left", va="top", fontsize=fs_name - 2, color=MUTED)
    key(fig, x0, T0 + 78, fs_name - 2, W, H)
    return svg_of(fig, W, H, glyphs)


def near(pairs, title, glyphs, segs):
    """The kappa row close up, in the close-up camera's screen px; columns over the overview's."""
    fw, fh = NEAR_W, H
    fig = plt.figure(figsize=(fw / 72, fh / 72), dpi=72)
    fs = 23.0
    for h in (0, 1):
        sg = segs[(12, h)]
        lo, hi = sg["ylim"]
        for c, k in sg["cols"]:
            d = prep(pairs[k], sg["e"])
            x, w = nx(col_x(c)), S_CLOSE * CW
            m = axes_at(fig, x, NM_TOP, w, NM_H, fw, fh)
            draw_panel(m, d, sg["ylim"], sg["ticks"], lw_bar=1.3, ms=5.5, lw_th=1.6, tick_len=6, lw_frame=0.9)
            s = axes_at(fig, x, NM_TOP + NM_H + NS_GAP, w, NS_H, fw, fh)
            draw_strip(s, d, ms=5.0, tick_len=6, lw_frame=0.9)
            text_at(fig, x + w - 12, NM_TOP + 12, rf"${sym(TR[c])}\times\kappa$", fw, fh, ha="right",
                    va="top", fontsize=fs + 2)
            for ell in (100, 1000):
                xx = x + w * (np.log10(ell) - np.log10(XLIM[0])) / (np.log10(XLIM[1]) - np.log10(XLIM[0]))
                text_at(fig, xx, NM_TOP + NM_H + NS_GAP + NS_H + 8, f"$10^{{{int(np.log10(ell))}}}$", fw, fh,
                        ha="center", va="top", fontsize=fs)
        x0 = nx(col_x(6 * h))
        for v in sg["ticks"]:
            text_at(fig, x0 - 8, NM_TOP + NM_H * (hi - v) / (hi - lo), fmt(v), fw, fh, ha="right",
                    va="center", fontsize=fs)
        for v in (-2, 0, 2):
            text_at(fig, x0 - 8, NM_TOP + NM_H + NS_GAP + NS_H * (R - v) / (2 * R), fmt(v), fw, fh,
                    ha="right", va="center", fontsize=fs)
        text_at(fig, x0 - 66, NM_TOP + NM_H / 2, rf"$\ell C_\ell\;[10^{{-{sg['e']}}}]$", fw, fh,
                rotation=90, ha="center", va="center", fontsize=fs + 1)
        text_at(fig, x0 - 66, NM_TOP + NM_H + NS_GAP + NS_H / 2, r"$\Delta/\sigma$", fw, fh,
                rotation=90, ha="center", va="center", fontsize=fs + 1)
        mid = (nx(col_x(6 * h)) + nx(col_x(6 * h + 5) + CW)) / 2
        text_at(fig, mid, NM_TOP + NM_H + NS_GAP + NS_H + 44, r"$\ell$", fw, fh, ha="center", va="top",
                fontsize=fs + 2)
        # title and key at the top of this half's view
        left = nx((V0X if h == 0 else V1X) + GUT)
        text_at(fig, left, 40, title, fw, fh, ha="left", va="top", fontsize=fs + 3)
        key(fig, left, 96, fs - 1, fw, fh)
    return svg_of(fig, fw, fh, glyphs)


# ── details: one panel per pair ─────────────────────────────────────────────
DW, DH = 1320.0, 600.0


def detail(pairs, k, a, b, glyphs, e):
    p = pairs[k]
    d = prep(p, e)
    fig = plt.figure(figsize=(DW / 72, DH / 72), dpi=72)
    fs = 21.0
    m = axes_at(fig, 150, 96, DW - 190, 300, DW, DH)
    s = axes_at(fig, 150, 408, DW - 190, 110, DW, DH)
    ylim, ticks = yaxis(*span([d]))
    draw_panel(m, d, ylim, ticks, lw_bar=1.4, ms=6.5, lw_th=1.6, tick_len=7, lw_frame=1.0)
    draw_strip(s, d, ms=6.0, tick_len=7, lw_frame=1.0)
    for ax in (m, s):
        ax.tick_params(labelsize=fs, labelleft=True)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    s.tick_params(labelbottom=True)
    s.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"$10^{{{int(round(np.log10(v)))}}}$"))
    m.set_ylabel(rf"$\ell C_\ell\;[10^{{-{e}}}]$", fontsize=fs + 2, labelpad=10)
    s.set_ylabel(r"$\Delta/\sigma$", fontsize=fs + 2, labelpad=10)
    s.set_xlabel(r"$\ell$", fontsize=fs + 2, labelpad=4)
    # name a pair source side first, lower bin first, CMB lensing last
    a, b = sorted((a, b), key=lambda t: (2, 0) if t == "kappa" else (0 if t[0] == "l" else 1, int(t[1:])))
    fig.text(150 / DW, 1 - 22 / DH, rf"${sym(a)}\times{sym(b)}$", fontsize=fs + 9, va="top")
    fig.text(150 / DW, 1 - 62 / DH, f"{name(a)} $\\times$ {name(b)}, blinded", fontsize=fs - 2,
             va="top", color=MUTED)
    off = int(np.sum(np.abs(d["r"]) > 0.9 * R))
    if off:
        fig.text((DW - 40) / DW, 1 - 62 / DH,
                 f"{off} {'band lies' if off == 1 else 'bands lie'} beyond the strip, marked on its edge",
                 fontsize=fs - 4, va="top", ha="right", color=MUTED, style="italic")
    return svg_of(fig, DW, DH, glyphs)


def main():
    src = json.load(open(SRC))
    out = dict(blind=src["blind"], shears=src["shears"], cmbs=src["cmbs"], world=dict(w=W, h=H),
               detail=dict(w=DW, h=DH), views=VIEWS,
               near=dict(x=V0X, y=VY, s=S_CLOSE, w=NEAR_W, h=H), variants={})
    glyphs, cells_out = {}, None
    for vk, pairs in src["variants"].items():
        shear, cmb = vk.split("|")
        title = f"TR1 {src['shears'][shear]} $\\times$ {src['cmbs'][cmb]}, blinded"
        cells, segs, e_of = segments(pairs)
        lay = dict(over=overview(pairs, title, glyphs, segs, e_of), near=near(pairs, title, glyphs, segs))
        det = {}
        for (r, c), k in cells.items():
            a, b = ("kappa", TR[c]) if r == 12 else (TR[r], TR[c])
            det[k] = detail(pairs, k, a, b, glyphs, segs[(r, c // 6)]["e"])
        out["variants"][vk] = dict(layers=lay, details=det)
        cells_out = [dict(key=k, x=round(col_x(c), 2), y=round(row_y(r), 2), w=round(CW, 2), h=round(row_h(r), 2))
                     for (r, c), k in sorted(cells.items())]
        print(vk, {k: f"{len(v) / 1024:.0f} kB" for k, v in lay.items()},
              f"details {sum(len(v) for v in det.values()) / 1024:.0f} kB")
    out["cells"] = cells_out
    out["glyphs"] = "".join(glyphs.values()).replace("xlink:href=", "href=")
    out["css"] = "".join(f".{c}{{{s}}}" for s, c in STYLES.items())
    text = json.dumps(out, separators=(",", ":"))
    open(OUT, "w").write(text)
    print(f"glyphs {len(out['glyphs']) / 1024:.0f} kB; wrote {OUT} ({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
