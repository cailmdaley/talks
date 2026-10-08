"""Pre-rendered matplotlib figures for the Napoli systematics-triangle slide.

Reads private/systematics.json (make_systematics.py) and writes
private/systematics_app.json, which the slide's app (private/systematics.js)
inlines, plus the report's fallback image images/napoli_systematics_triangle.png.
The geometry, style and SVG plumbing are the dv-vector slide's
(render_dv_vector.py), so the two triangles lie cell for cell in the same places.

For every template S and variant:
  over    the whole data vector as a lower triangle of panels, each showing the
          contamination X_l^{ab} / sigma_G of its pair, +- sigma_X / sigma_G, on one
          fixed scale (+-YR) with the +-1 sigma_G band shaded; a band beyond the
          scale is a triangle on its edge.
A detail card is composed by the app from two kinds of panel, each rendered once
for every variant part it depends on (a shear tracer on the shear method, kappa on
the CMB map, a lens bin on neither):
  xcard   the card itself: the pair's name and its X / sigma_G panel along the bottom
  cross   one tracer's measured cross with the template, l C_l^{aS} +- sigma, for
          the card's top row (two for a cross-pair, one for an auto)
Every axis is the union over the variants on disk, so the deck's toggles move only
the points.

Run in the cmbx container, after make_systematics.py:
  app python private/render_systematics.py
"""
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import render_dv_vector as rdv  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "systematics.json")
OUT = os.path.join(HERE, "systematics_app.json")
FALLBACK = os.path.join(HERE, "..", "..", "images", "napoli_systematics_triangle.png")
plt.rcParams["svg.hashsalt"] = "systematics"

# the SVGs' inline styles become CSS classes of this slide's own (the dv-vector slide's
# classes are dv*, and both slides' styles live in the one deck page)
STYLES = {}


def style_class(style):
    style = style.strip().rstrip(";")
    if style not in STYLES:
        STYLES[style] = f"sy{len(STYLES):x}"
    return STYLES[style]


rdv.style_class = style_class

INK, DATA, FRAME, MUTED = rdv.INK, rdv.DATA, rdv.FRAME, rdv.MUTED
BAND = "#CDD3DC"
W, H, TR = rdv.W, rdv.H, rdv.TR
YR = 1.5                    # every X / sigma_G panel spans +-YR
DW, DH = rdv.DW, rdv.DH     # the card
CROSS_W, CROSS_H = 560.0, 262.0
SLOTS = [(118.0, 96.0), (712.0, 96.0)]     # the cross panels' places on the card
XP = dict(x=150.0, y=388.0, w=DW - 190, h=150.0)


def dep(tracers, vk):
    """The variant parts a set of tracers depends on, as the id suffix."""
    shear, cmb = vk.split("|")
    s = shear if any(t[0] == "l" for t in tracers) else "-"
    c = cmb if "kappa" in tracers else "-"
    return f"{s}|{c}"


def xaxis(ax, ell, *, tick_len, lw_frame, labels=False, fs=None):
    rdv.frame(ax, (-YR, YR), [-1, 0, 1], tick_len=tick_len, lw_frame=lw_frame, minor=labels)
    ax.axhspan(-1, 1, color=BAND, alpha=0.45, lw=0, zorder=0.5)
    ax.axhline(0, color=INK, lw=lw_frame, zorder=1)


def x_points(ax, ell, x, sx, *, lw, ms):
    """X / sigma_G with its bars clipped at the frame; beyond the scale, a triangle on the edge."""
    x, sx = np.asarray(x), np.asarray(sx)
    edge = 0.92 * YR
    inside = np.abs(x) <= edge
    lo, hi = np.clip(x - sx, -YR, YR), np.clip(x + sx, -YR, YR)
    xs = np.repeat(ell[inside], 3)
    ys = np.column_stack([lo[inside], hi[inside], np.full(inside.sum(), np.nan)]).ravel()
    ax.plot(xs, ys, color=DATA, lw=lw, solid_capstyle="butt", zorder=3, clip_on=True)
    ax.plot(ell[inside], x[inside], "o", color=DATA, ms=ms, mew=0, zorder=4)
    for sgn, mk in ((1, "^"), (-1, "v")):
        m = sgn * x > edge
        if m.any():
            ax.plot(ell[m], np.full(m.sum(), sgn * edge), mk, color=DATA, ms=ms * 1.3, mew=0, zorder=4)


def overview(per, ell, title, label, glyphs):
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
    fs_name = 21.0
    cells = {}
    for r, a in enumerate(TR):
        for c, b in enumerate(TR[: r + 1]):
            cells[(r, c)] = rdv.key_of(a, b)
    for c, b in enumerate(TR):
        cells[(12, c)] = rdv.key_of("kappa", b)
    for (r, c), k in cells.items():
        ax = rdv.axes_at(fig, rdv.col_x(c), rdv.row_y(r), rdv.CW, rdv.row_h(r), W, H)
        xaxis(ax, ell, tick_len=2.4, lw_frame=0.5)
        x_points(ax, ell, per["x"][k], per["sx"][k], lw=0.7, ms=2.5)
    for r, t in enumerate(TR + ["kappa"]):
        last = r if r < 12 else 11
        rdv.text_at(fig, rdv.col_x(last) + rdv.CW + 6, rdv.row_y(r) + rdv.row_h(r) / 2, f"${rdv.sym(t)}$", W, H,
                    ha="left", va="center", fontsize=fs_name)
    for c, t in enumerate(TR):
        rdv.text_at(fig, rdv.col_x(c) + rdv.CW / 2, rdv.row_y(12) + rdv.KH + 6, f"${rdv.sym(t)}$", W, H,
                    ha="center", va="top", fontsize=fs_name)
    x0 = rdv.col_x(3) + 30
    rdv.text_at(fig, x0, rdv.T0 + 4, title, W, H, ha="left", va="top", fontsize=fs_name + 3)
    rdv.text_at(fig, x0, rdv.T0 + 40,
                r"$X_\ell^{ab} = C_\ell^{aS}\,C_\ell^{bS}/C_\ell^{SS}$ in units of $\sigma_G$ of $C_\ell^{ab}$",
                W, H, ha="left", va="top", fontsize=fs_name - 2, color=MUTED)
    rdv.text_at(fig, x0, rdv.T0 + 74,
                rf"each panel spans $\pm{YR:g}\,\sigma_G$; shaded $\pm1\,\sigma_G$; bars $\sigma_X/\sigma_G$",
                W, H, ha="left", va="top", fontsize=fs_name - 2, color=MUTED)
    rdv.text_at(fig, x0, rdv.T0 + 150, label, W, H, ha="left", va="top", fontsize=fs_name + 1, color=INK)
    return fig


def sym_axis(lo, hi):
    """Limits and major ticks for a cross that may sit either side of zero: multiples of
    one round step s (1, 2 or 5 x 10^k), at most two on each side, zero always marked."""
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    m = max(-lo, hi)
    k = np.floor(np.log10(0.45 * m))
    s = max(f * 10 ** k for f in (1, 2, 5) if f * 10 ** k <= 0.45 * m)
    ticks = [float(f"{j * s:.6g}") for j in range(-2, 3) if lo - 1e-12 <= j * s <= hi + 1e-12]
    pad = 0.06 * (hi - lo)
    return (lo - pad, hi + pad), ticks


def cross_panel(ell, c, s, ylim, ticks, e, tracer, tlabel, glyphs):
    fw, fh = CROSS_W, CROSS_H
    fig = plt.figure(figsize=(fw / 72, fh / 72), dpi=72)
    fs = 19.0
    f = 10.0 ** e
    ax = rdv.axes_at(fig, 104, 40, fw - 124, fh - 92, fw, fh)
    rdv.frame(ax, ylim, ticks, tick_len=6, lw_frame=0.9)
    ax.axhline(0, color=FRAME, lw=0.9 * 0.6, alpha=0.45, zorder=1)
    rdv.errorbars(ax, ell, np.asarray(c) * f, np.asarray(s) * f, 1.2, 5.2)
    ax.tick_params(labelsize=fs, labelleft=True, labelbottom=True)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: rdv.fmt(v)))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"$10^{{{int(round(np.log10(v)))}}}$"))
    ax.set_ylabel(rf"$\ell C_\ell\;[10^{{-{e}}}]$", fontsize=fs, labelpad=6)
    fig.text(104 / fw, 1 - 6 / fh, rf"${rdv.sym(tracer)}\times S$, {tlabel.lower()}", fontsize=fs + 1, va="top")
    return rdv.svg_of(fig, fw, fh, glyphs)


def xcard(ell, x, sx, a, b, tlabel, glyphs):
    fig = plt.figure(figsize=(DW / 72, DH / 72), dpi=72)
    fs = 21.0
    a, b = sorted((a, b), key=lambda t: (2, 0) if t == "kappa" else (0 if t[0] == "l" else 1, int(t[1:])))
    fig.text(150 / DW, 1 - 22 / DH, rf"${rdv.sym(a)}\times{rdv.sym(b)}$", fontsize=fs + 9, va="top")
    fig.text(150 / DW, 1 - 62 / DH, f"{tlabel} template: contamination of {rdv.name(a)} $\\times$ {rdv.name(b)}",
             fontsize=fs - 2, va="top", color=MUTED)
    ax = rdv.axes_at(fig, XP["x"], XP["y"], XP["w"], XP["h"], DW, DH)
    xaxis(ax, ell, tick_len=7, lw_frame=1.0, labels=True)
    x_points(ax, ell, x, sx, lw=1.4, ms=6.5)
    ax.tick_params(labelsize=fs, labelleft=True, labelbottom=True)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: rdv.fmt(v)))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"$10^{{{int(round(np.log10(v)))}}}$"))
    ax.set_ylabel(r"$X_\ell/\sigma_G$", fontsize=fs + 2, labelpad=10)
    ax.set_xlabel(r"$\ell$", fontsize=fs + 2, labelpad=4)
    if a == b:
        fig.text(SLOTS[1][0] / DW, 1 - (SLOTS[1][1] + 70) / DH,
                 "An auto-spectrum: one cross,\n" + r"$X_\ell = (C_\ell^{aS})^2 / C_\ell^{SS}$.",
                 fontsize=fs, va="top", color=MUTED, linespacing=1.4)
    return rdv.svg_of(fig, DW, DH, glyphs)


def main():
    src = json.load(open(SRC))
    ell = np.asarray(src["ell"], float)
    variants = list(src["variants"])
    assert variants, "no variant has all six template crosses"
    labels = dict(src["templates"])
    out = dict(world=dict(w=W, h=H), detail=dict(w=DW, h=DH), cross=dict(w=CROSS_W, h=CROSS_H),
               slots=[list(s) for s in SLOTS], templates=src["templates"], variants=variants,
               blind=src["blind"], over={}, xcard={}, crossp={})
    glyphs = {}
    tracers = TR + ["kappa"]
    for t, tlabel in src["templates"]:
        out["over"][t], out["xcard"][t], out["crossp"][t] = {}, {}, {}
        # each tracer's cross axis: the union over the variants on disk
        ax_of = {}
        for tr in tracers:
            cs = [np.asarray(src["variants"][vk][t]["c"][tr]) for vk in variants]
            ss = [np.asarray(src["variants"][vk][t]["s"][tr]) for vk in variants]
            m = max(np.max(np.abs(c) + s) for c, s in zip(cs, ss))
            e = int(-np.floor(np.log10(m)))
            lo = min(np.min(c - s) for c, s in zip(cs, ss)) * 10 ** e
            hi = max(np.max(c + s) for c, s in zip(cs, ss)) * 10 ** e
            ylim, ticks = sym_axis(lo, hi)
            ax_of[tr] = (e, ylim, ticks)
        for vk in variants:
            per = src["variants"][vk][t]
            shear, cmb = vk.split("|")
            title = f"TR1 {rdv_name(shear, cmb)}, contamination by one template"
            fig = overview(per, ell, title, "", glyphs)
            out["over"][t][vk] = rdv.svg_of(fig, W, H, glyphs)
            if t == src["templates"][0][0] and vk == variants[0]:
                fig = overview(per, ell, title, f"Template: {tlabel.lower()}", {})
                fig.savefig(FALLBACK, dpi=144, transparent=False, facecolor="white")
                plt.close(fig)
            for k in per["x"]:
                a, b = k.split("_")
                cid = f"{k}|{dep((a, b), vk)}"
                if cid not in out["xcard"][t]:
                    out["xcard"][t][cid] = xcard(ell, per["x"][k], per["sx"][k], a, b, tlabel, glyphs)
            for tr in tracers:
                cid = f"{tr}|{dep((tr,), vk)}"
                if cid not in out["crossp"][t]:
                    e, ylim, ticks = ax_of[tr]
                    out["crossp"][t][cid] = cross_panel(ell, per["c"][tr], per["s"][tr], ylim, ticks, e, tr,
                                                        tlabel, glyphs)
        print(t, f"over {sum(len(v) for v in out['over'][t].values()) / 1024:.0f} kB,",
              f"cards {sum(len(v) for v in out['xcard'][t].values()) / 1024:.0f} kB,",
              f"crosses {sum(len(v) for v in out['crossp'][t].values()) / 1024:.0f} kB")
    cells = {}
    for r, a in enumerate(TR):
        for c, b in enumerate(TR[: r + 1]):
            cells[(r, c)] = rdv.key_of(a, b)
    for c, b in enumerate(TR):
        cells[(12, c)] = rdv.key_of("kappa", b)
    out["cells"] = [dict(key=k, x=round(rdv.col_x(c), 2), y=round(rdv.row_y(r), 2), w=round(rdv.CW, 2),
                         h=round(rdv.row_h(r), 2)) for (r, c), k in sorted(cells.items())]
    out["choice"] = dict(x=round(rdv.col_x(3) + 30, 2), y=round(rdv.T0 + 112, 2))
    out["glyphs"] = "".join(glyphs.values()).replace("xlink:href=", "href=")
    out["css"] = "".join(f".{c}{{{s}}}" for s, c in STYLES.items())
    text = json.dumps(out, separators=(",", ":"))
    open(OUT, "w").write(text)
    print(f"glyphs {len(out['glyphs']) / 1024:.0f} kB; wrote {OUT} ({len(text) / 1024:.0f} kB); "
          f"fallback {os.path.normpath(FALLBACK)}")


def rdv_name(shear, cmb):
    return {"lensmc": "LensMC", "metacal": "MetaCal"}[shear] + " $\\times$ " + {"spt": "SPT-3G", "act": "ACT DR6"}[cmb]


if __name__ == "__main__":
    main()
