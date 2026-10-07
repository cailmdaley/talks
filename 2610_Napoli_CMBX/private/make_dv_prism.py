"""Blinded TR1 x SPT-3G data vector as the faces of a prism, for the Napoli CMBX talk.

PRIVATE: this file, its images and the slide that shows them (slides/dv-prism.html)
stay out of git (.git/info/exclude) until the blinded-data-vector release question
is settled.

Three faces, identical 3424 x 1446 frames (the figure layout's body less a .source
line, at 2x), shown by the house `data-prism` stack:

  dv_prism_1_gk.png   one row of six source bins: gamma_i x kappa
  dv_prism_2_dk.png   one row of six lens bins:   delta_i x kappa
  dv_prism_3_all.png  every pair of the 3x2pt + kappa vector as a triangle of
                      sparklines, with the kappa row (faces 1 and 2) at its base

Bands outside the placeholder scale cut are drawn grey and labelled so; they are
shown, not hidden. On face 3 each sparkline's y-range is set by the fiducial and
the in-cut bands, so excluded high-ell delta-delta bands are clipped at the panel
edge rather than drawing the eye.

Inputs, all blinded (blind cmbx_dr1_a):
  * results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.npz: the chair's
    export of all 90 pairs (ell_eff, data, sigma_G, windowed fiducial, fit mask,
    covariance indices, full covariance).
  * results/tr1/likelihood_product/likelihood_input.tar (lc, commit cd0d303) and
    datavector_vs_theory.tar (lc, commit 6c6c9f1) member check.json: the lc
    outputs the export came from. Every pair of the export is asserted equal to
    them (data, ell_eff, covariance indices, sigma_G from the diagonal of the full
    NaMaster Gaussian covariance, fiducial, fit mask) before anything is drawn.

The fiducial is the reference pushed through the bandpower windows, not a fit.
No amplitude, fit or goodness-of-fit enters these figures.

Run in the cmbx container:
  app python private/make_dv_prism.py
"""
import json
import os
import pickle
import tarfile
import tempfile

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
NPZ = f"{CMBX}/results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.npz"
INDEX = f"{CMBX}/results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.json"
LIKE = f"{CMBX}/results/tr1/likelihood_product/likelihood_input.tar"
DVT = f"{CMBX}/results/tr1/likelihood_product/datavector_vs_theory.tar"
BLIND = "cmbx_dr1_a"

INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, OCHRE = "#2E417C", "#9C7414"
GREY, GREY_LINE = "#A3ABB7", "#C9CFD8"
BAND_OUTER, BAND_INNER = "#DCE3EE", "#BFCADB"
TINT = "#E4E9F2"

# every face is the same frame: 1712 x 723 px displayed, drawn at 2x
W_PX, H_PX, DPI = 3424, 1446, 200
PX = DPI / 72 / 2          # displayed px per point
ELL_TICKS = [100, 300, 1000]
EXCLUDED = "outside placeholder scale cut"


def setup_font():
    src = os.path.join(HERE, "..", "..", "node_modules", "@fontsource-variable", "eb-garamond",
                       "files", "eb-garamond-latin-wght-normal.woff2")
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
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": 21, "ytick.labelsize": 21, "axes.labelsize": 24,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })


# ── data ─────────────────────────────────────────────────────────────────

def load():
    """All 90 pairs from the export, each asserted equal to the lc outputs."""
    npz = np.load(NPZ)
    index = json.load(open(INDEX))
    assert str(npz["blinded"]) == BLIND and index["blinded"] == BLIND
    with tarfile.open(LIKE) as tar:
        member = next(m for m in tar.getmembers()
                      if m.name.endswith(".pkl") and not m.name.endswith("_dndz.pkl"))
        payload = pickle.load(tar.extractfile(member))
    with tarfile.open(DVT) as tar:
        record = json.load(tar.extractfile("check.json"))
    blind = payload["metadata"].get("blind")
    assert BLIND in json.dumps(blind, default=str), f"payload blind stamp {blind!r} is not {BLIND}"
    assert record["metadata"].get("blind") == blind or BLIND in json.dumps(record["metadata"].get("blind"))
    assert payload["metadata"]["covariance"]["method"] == "namaster_gaussian"
    assert payload["metadata"]["covariance"]["full"] is True
    cov = np.asarray(payload["cov_all"])
    keys = list(payload["cls"])
    assert keys == [str(k) for k in npz["order"]] == index["order"]
    offsets, cursor = {}, 0
    for k in keys:
        n = len(payload["cls"][k]["cl"])
        offsets[k] = np.arange(cursor, cursor + n)
        cursor += n
    assert cov.shape == (cursor, cursor) == npz["cov"].shape
    assert np.array_equal(cov, npz["cov"])
    recs = {r["spectrum"]: r for r in record["spectra"]}
    pairs = {}
    for k in keys:
        rec = recs[k]
        ell = np.asarray(payload["cls"][k]["leff"], float)
        data = np.asarray(payload["cls"][k]["cl"], float)
        sigma = np.sqrt(np.diag(cov)[offsets[k]])
        theory = np.asarray(rec["theory_binned"], float)
        fit = np.asarray(rec["fit_mask"], bool)
        # the lc outputs agree with each other ...
        assert np.allclose(ell, rec["ell_eff"]) and np.allclose(data, rec["data"], rtol=1e-12, atol=0)
        assert np.allclose(sigma, rec["sigma_gaussian"], rtol=1e-12, atol=0)
        assert rec["covariance_indices"] == offsets[k].tolist()
        # ... and the export agrees with them
        assert np.array_equal(npz[f"{k}__cov_idx"], offsets[k])
        assert np.allclose(npz[f"{k}__ell_eff"], ell) and np.array_equal(npz[f"{k}__data"], data)
        assert np.allclose(npz[f"{k}__sigma_G"], sigma, rtol=1e-12, atol=0)
        assert np.array_equal(npz[f"{k}__theory_fid"], theory)
        assert np.array_equal(npz[f"{k}__fit_mask"].astype(bool), fit)
        assert index["pairs"][k]["family"] == rec["family"]
        pairs[k] = dict(key=k, family=rec["family"], ell=ell, data=data, sigma=sigma, theory=theory,
                        fit=fit, resid=(data - theory) / sigma)
    print(f"{len(pairs)} pairs, {cursor} bands, {sum(p['fit'].sum() for p in pairs.values())} inside the "
          "placeholder scale cut; export == lc outputs for every pair")
    return pairs


def kappa_row(pairs, letter):
    rows = [dict(pairs[f"kappa_{letter}{i}"], bin=i + 1) for i in range(6)]
    for r in rows:
        assert r["family"] == ("LK" if letter == "l" else "GK")
    return rows


# ── faces 1 and 2: one row of six bins against kappa ────────────────────

# shared geometry (image px), so faces 1 and 2 are frames of one plot
LEFT, RIGHT, TOP, BOTTOM = 232, 14, 132, 182
GAP = 30
MAIN_H, SPLIT, RESID_H = 790, 16, 326


def panel_boxes():
    w = (W_PX - LEFT - RIGHT - 5 * GAP) / 6
    y_resid = BOTTOM
    y_main = BOTTOM + RESID_H + SPLIT
    assert y_main + MAIN_H <= H_PX - TOP
    out = []
    for i in range(6):
        x = LEFT + i * (w + GAP)
        out.append(([x / W_PX, y_main / H_PX, w / W_PX, MAIN_H / H_PX],
                    [x / W_PX, y_resid / H_PX, w / W_PX, RESID_H / H_PX]))
    return out


def header(fig, title, handles, labels):
    fig.text(LEFT / W_PX, 1 - 62 / H_PX, title, fontsize=26, color=INK, ha="left", va="center")
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(1 - RIGHT / W_PX, 1 - 62 / H_PX),
               ncol=len(handles), frameon=False, fontsize=22, handlelength=1.4, columnspacing=1.3,
               handletextpad=0.5, labelcolor=INK)


def data_handle(color):
    return Line2D([], [], color=color, marker="o", ms=9, mec="white", lw=2.0, ls="-")


def kappa_face(rows, out, *, tracer, bin_name, title, exp):
    scale = 10.0 ** exp
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    lo = min((r["ell"] * (r["data"] - r["sigma"])).min() for r in rows) * scale
    hi = max((r["ell"] * (r["data"] + r["sigma"])).max() for r in rows) * scale
    pad = 0.06 * (hi - lo)
    ylim = (lo - pad, hi + 3.2 * pad)      # head-room for the bin label
    rlim = 3.9
    any_excluded = False
    for slot, ((bm, br), r) in enumerate(zip(panel_boxes(), rows)):
        ax = fig.add_axes(bm)
        ar = fig.add_axes(br, sharex=ax)
        ell, fit = r["ell"], r["fit"]
        any_excluded |= bool((~fit).any())
        ax.axhline(0, color=RULE, lw=1.2, zorder=0)
        ax.plot(ell, ell * r["theory"] * scale, "-", color=OCHRE, lw=2.6, zorder=2)
        for sel, color, z in ((~fit, GREY, 3), (fit, COBALT, 4)):
            if sel.any():
                ax.errorbar(ell[sel], (ell * r["data"] * scale)[sel], yerr=(ell * r["sigma"] * scale)[sel],
                            fmt="o", ms=7, color=color, mec="white", mew=1.0, elinewidth=2.0, capsize=0,
                            zorder=z)
                ar.plot(ell[sel], r["resid"][sel], "o", ms=7, color=color, mec="white", mew=1.0, zorder=z)
        ax.set_ylim(*ylim)
        ax.text(0.94, 0.965, f"{bin_name} {r['bin']}", transform=ax.transAxes, fontsize=24,
                color=INK, ha="right", va="top")
        ar.axhspan(-2, 2, color=BAND_OUTER, lw=0, zorder=0)
        ar.axhspan(-1, 1, color=BAND_INNER, lw=0, zorder=0)
        ar.axhline(0, color=MUTED, lw=1.2, zorder=1)
        ar.set_ylim(-rlim, rlim)
        ar.set_yticks([-2, 2])
        ar.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:+.0f}".replace("-", "−")))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}".replace("-", "−")))
        for a in (ax, ar):
            a.set_xscale("log")
            a.set_xlim(ell.min() / 1.18, ell.max() * 1.18)
            a.xaxis.set_major_locator(FixedLocator(ELL_TICKS))
            a.xaxis.set_minor_locator(NullLocator())
            a.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{int(v)}"))
        ax.tick_params(labelbottom=False)
        if slot:
            ax.tick_params(labelleft=False)
            ar.tick_params(labelleft=False)
        else:
            ax.set_ylabel(rf"$10^{{{exp}}}\,\ell C_\ell^{{{tracer}\kappa}}$", labelpad=8)
            ar.set_ylabel(r"$\Delta/\sigma_G$", labelpad=8)
    fig.text((LEFT + (W_PX - LEFT - RIGHT) / 2) / W_PX, 6 / H_PX, r"multipole $\ell$", fontsize=24,
             color=INK, ha="center", va="bottom")
    handles = [data_handle(COBALT)]
    labels = [r"blinded data $\pm\,\sigma_G$"]
    if any_excluded:
        handles.append(data_handle(GREY))
        labels.append(EXCLUDED)
    handles.append(Line2D([], [], color=OCHRE, lw=2.8))
    labels.append("windowed fiducial")
    header(fig, title, handles, labels)
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", out)


# ── face 3: every pair, a triangle of sparklines ─────────────────────────

# rows top to bottom: delta_1..6, gamma_1..6, kappa; columns: delta_1..6, gamma_1..6
TRACERS = [("g", i) for i in range(6)] + [("l", i) for i in range(6)]
SYM = {"g": r"\delta", "l": r"\gamma"}
G_LEFT, G_RIGHT, G_TOP, G_BOTTOM = 150, 14, 132, 84
G_GAP_X, G_GAP_Y, KAPPA_GAP = 14, 10, 30


def pair_key(a, b):
    """Export key for tracers a, b (each ('g'|'l', i) or 'kappa')."""
    if a == "kappa":
        return f"kappa_{b[0]}{b[1]}"
    rank = {"g": 0, "l": 1}
    (ta, ia), (tb, ib) = sorted([a, b], key=lambda t: (rank[t[0]], t[1]))
    return f"{ta}{ia}_{tb}{ib}"


def grid_cells():
    """(key, row, col) for the 90 cells, and the image-px geometry of a cell."""
    cells = []
    for r, a in enumerate(TRACERS):
        for c, b in enumerate(TRACERS[: r + 1]):
            cells.append((pair_key(a, b), r, c))
    for c, b in enumerate(TRACERS):
        cells.append((pair_key("kappa", b), 12, c))
    cw = (W_PX - G_LEFT - G_RIGHT - 11 * G_GAP_X) / 12
    ch = (H_PX - G_TOP - G_BOTTOM - 12 * G_GAP_Y - KAPPA_GAP) / 13

    def box(row, col):
        x = G_LEFT + col * (cw + G_GAP_X)
        y_top = G_TOP + row * (ch + G_GAP_Y) + (KAPPA_GAP if row == 12 else 0)
        return x, H_PX - y_top - ch, cw, ch
    return cells, box


def all_face(pairs, out):
    cells, box = grid_cells()
    assert sorted(k for k, _r, _c in cells) == sorted(pairs), "the triangle must hold every pair once"
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    # the kappa row is where faces 1 and 2 came from: a pale band behind it
    x0, y0, _w, h = box(12, 0)
    x1, _y, w1, _h = box(12, 11)
    fig.patches.append(Rectangle(((x0 - 8) / W_PX, (y0 - 6) / H_PX), (x1 + w1 - x0 + 16) / W_PX,
                                 (h + 12) / H_PX, transform=fig.transFigure, color=TINT, lw=0, zorder=-10))
    for key, row, col in cells:
        p = pairs[key]
        x, y, w, h = box(row, col)
        ax = fig.add_axes([x / W_PX, y / H_PX, w / W_PX, h / H_PX])
        ax.patch.set_alpha(0)
        ell, fit = p["ell"], p["fit"]
        yd, ys, yt = ell * p["data"], ell * p["sigma"], ell * p["theory"]
        # y-range from the fiducial and the in-cut bands only: excluded outliers clip at the edge
        lo = min(yt.min(), (yd - ys)[fit].min() if fit.any() else yt.min(), 0)
        hi = max(yt.max(), (yd + ys)[fit].max() if fit.any() else yt.max())
        span = hi - lo
        ax.set_ylim(lo - 0.25 * span, hi + 0.35 * span)
        ax.set_xscale("log")
        ax.set_xlim(ell.min() / 1.25, ell.max() * 1.25)
        ax.axhline(0, color=RULE, lw=0.9, zorder=0)
        ax.plot(ell, yt, "-", color=OCHRE, lw=2.0, zorder=2)
        for sel, color, z in ((~fit, GREY, 3), (fit, COBALT, 4)):
            if sel.any():
                ax.errorbar(ell[sel], yd[sel], yerr=ys[sel], fmt="o", ms=3.2, color=color,
                            mew=0, elinewidth=1.3, capsize=0, zorder=z)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ("left", "bottom"):
            ax.spines[s].set_color(RULE)
            ax.spines[s].set_linewidth(1.0)
    # tracer labels: rows on the left, columns along the bottom
    fs = 21
    for r, (t, i) in enumerate(TRACERS + [("kappa", None)]):
        x, y, w, h = box(r, 0)
        lab = r"$\kappa$" if t == "kappa" else rf"${SYM[t]}_{i + 1}$"
        fig.text((x - 22) / W_PX, (y + h / 2) / H_PX, lab, fontsize=fs, color=INK, ha="right", va="center")
    for c, (t, i) in enumerate(TRACERS):
        x, y, w, h = box(12, c)
        fig.text((x + w / 2) / W_PX, (y - 16) / H_PX, rf"${SYM[t]}_{i + 1}$", fontsize=fs, color=INK,
                 ha="center", va="top")
    n_bands = sum(len(p["ell"]) for p in pairs.values())
    n_fit = sum(int(p["fit"].sum()) for p in pairs.values())
    x, y, w, h = box(0, 3)
    fig.text((x + 0.5 * w) / W_PX, (y + h) / H_PX,
             f"{len(pairs)} spectra · {n_bands} bandpowers · {n_fit} inside the placeholder scale cut",
             fontsize=24, color=INK, ha="left", va="top")
    handles = [data_handle(COBALT), data_handle(GREY), Line2D([], [], color=OCHRE, lw=2.8)]
    labels = [r"blinded data $\pm\,\sigma_G$", EXCLUDED, "windowed fiducial"]
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(box(1, 6)[0] / W_PX, box(1, 6)[1] / H_PX),
               ncol=1, frameon=False, fontsize=22, handlelength=1.4, handletextpad=0.5, labelcolor=INK)
    fig.text(G_LEFT / W_PX, 1 - 62 / H_PX, r"TR1 × SPT-3G: the blinded 3×2pt + $\kappa$ data vector",
             fontsize=26, color=INK, ha="left", va="center")
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print("wrote", out)
    # data-zoom for face 3: the box face 2 shrinks into, at one scale so nothing
    # stretches: face 2's six panels span the six delta-kappa cells, centred on
    # their row (the box reaches past the bottom edge of the image)
    xa, ya, _w, ch = box(12, 0)
    xb, _y, wb, _h = box(12, 5)
    s = (xb + wb - xa) / (W_PX - LEFT - RIGHT)
    centre = H_PX - ya - ch / 2                               # cells' centre, from the top
    panels = TOP + (H_PX - TOP - BOTTOM) / 2                  # face 2's panel centre, from the top
    zoom = (100 * (xa - LEFT * s) / W_PX, 100 * (centre - panels * s) / H_PX, 100 * s, 100 * s)
    print('face 3 data-zoom="%.2f %.2f %.2f %.2f"' % zoom)

def main():
    setup_font()
    pairs = load()
    print(f"tick labels {21 * PX:.0f} px, axis labels {24 * PX:.0f} px displayed")
    kappa_face(kappa_row(pairs, "l"), os.path.join(HERE, "dv_prism_1_gk.png"), tracer=r"\gamma",
               bin_name="source bin", title="TR1 shear × SPT-3G κ · blinded", exp=6)
    kappa_face(kappa_row(pairs, "g"), os.path.join(HERE, "dv_prism_2_dk.png"), tracer=r"\delta",
               bin_name="lens bin", title="TR1 galaxies × SPT-3G κ · blinded", exp=5)
    all_face(pairs, os.path.join(HERE, "dv_prism_3_all.png"))


if __name__ == "__main__":
    main()
