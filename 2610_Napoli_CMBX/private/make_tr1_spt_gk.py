"""Blinded TR1 shear x SPT-3G kappa (gamma-kappa) data vector, for the Napoli CMBX talk.

PRIVATE: this file, its image and the slide that shows it stay out of git
(.git/info/exclude) until the blinded-data-vector release question is settled.

Inputs, both blinded (blind cmbx_dr1_a) lc outputs of the cmbx tr1 universe:
  * results/tr1/likelihood_product/likelihood_input.tar (cmbx commit cd0d303):
    the delivered blinded vector. Data C_l, ell_eff and the full NaMaster
    Gaussian covariance cov_all are read from it here.
  * results/tr1/likelihood_product/datavector_vs_theory.tar (commit 6c6c9f1),
    member check.json: the windowed fiducial reference bands that
    workflow/scripts/plot_datavector_vs_theory.py computed from that same input
    with the live TheoryVector operator. The script asserts that check.json's
    data and sigma agree with the payload before using its theory column.

sigma_G is the square root of the diagonal of the full Gaussian covariance.
The residual is (data - reference) / sigma_G per band. No fit and no amplitude
enter this figure.

Output: private/tr1_spt_gk.png at 2x the figure layout's body box less a .source
line (1712 x 723 px displayed).

Run in the cmbx container:
  singularity exec --bind /leonardo_work <container> python private/make_tr1_spt_gk.py
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
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tr1_spt_gk.png")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
LIKE = f"{CMBX}/results/tr1/likelihood_product/likelihood_input.tar"
DVT = f"{CMBX}/results/tr1/likelihood_product/datavector_vs_theory.tar"
BLIND = "cmbx_dr1_a"

INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, ACCENT, OCHRE = "#2E417C", "#435AA1", "#9C7414"
BAND_OUTER, BAND_INNER = "#DCE3EE", "#BFCADB"

W_PX, H_PX, DPI = 3424, 1446, 200
PT = DPI / 72 / 2
ELL_TICKS = [100, 300, 1000]
SCALE = 1e6


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


def load():
    with tarfile.open(LIKE) as tar:
        member = next(m for m in tar.getmembers()
                      if m.name.endswith(".pkl") and not m.name.endswith("_dndz.pkl"))
        payload = pickle.load(tar.extractfile(member))
    with tarfile.open(DVT) as tar:
        record = json.load(tar.extractfile("check.json"))
    blind = payload["metadata"].get("blind")
    assert BLIND in json.dumps(blind, default=str), f"payload blind stamp {blind!r} is not {BLIND}"
    assert record["metadata"].get("blind") == blind or BLIND in json.dumps(record["metadata"].get("blind"))
    cov = np.asarray(payload["cov_all"])
    assert payload["metadata"]["covariance"]["method"] == "namaster_gaussian"
    assert payload["metadata"]["covariance"]["full"] is True
    keys = list(payload["cls"])
    offsets, cursor = {}, 0
    for k in keys:
        n = len(payload["cls"][k]["cl"])
        offsets[k] = np.arange(cursor, cursor + n)
        cursor += n
    assert cov.shape == (cursor, cursor)
    rows = []
    for rec in record["spectra"]:
        if rec["family"] != "LK":
            continue
        key = rec["spectrum"]
        ell = np.asarray(payload["cls"][key]["leff"], float)
        data = np.asarray(payload["cls"][key]["cl"], float)
        sigma = np.sqrt(np.diag(cov)[offsets[key]])
        theory = np.asarray(rec["theory_binned"], float)
        assert np.allclose(ell, rec["ell_eff"]) and np.allclose(data, rec["data"], rtol=1e-12, atol=0)
        assert np.allclose(sigma, rec["sigma_gaussian"], rtol=1e-12, atol=0)
        assert rec["covariance_indices"] == offsets[key].tolist()
        source_bin = int(next(t for t in rec["tracers"] if t[0] == "L")[1:]) + 1
        rows.append(dict(bin=source_bin, ell=ell, data=data, sigma=sigma, theory=theory,
                         resid=(data - theory) / sigma, fitted=np.asarray(rec["fit_mask"], bool)))
    rows.sort(key=lambda r: r["bin"])
    assert [r["bin"] for r in rows] == [1, 2, 3, 4, 5, 6]
    return rows


def summarize(rows):
    allr = np.concatenate([r["resid"] for r in rows])
    n = allr.size
    print(f"gamma-kappa: {len(rows)} spectra, {n} bands, all fitted: {all(r['fitted'].all() for r in rows)}")
    for r in rows:
        i = np.argmax(np.abs(r["resid"]))
        print(f"  bin {r['bin']}: worst {r['resid'][i]:+.2f} sigma_G at ell={r['ell'][i]:.1f}; "
              f"|r|>2: {(np.abs(r['resid']) > 2).sum()}")
    b = max(rows, key=lambda r: np.abs(r["resid"]).max())
    i = np.argmax(np.abs(b["resid"]))
    print(f"worst overall: bin {b['bin']}, ell={b['ell'][i]:.1f}, {b['resid'][i]:+.3f} sigma_G")
    print(f"|r|>2: {(np.abs(allr) > 2).sum()} (Gaussian expectation {0.0455 * n:.1f}); "
          f"|r|>3: {(np.abs(allr) > 3).sum()} (expectation {0.0027 * n:.2f})")
    print(f"tick labels {22 * PT:.0f} px, axis labels {25 * PT:.0f} px displayed")


def draw(rows):
    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "xtick.labelsize": 22, "ytick.labelsize": 22, "axes.labelsize": 25,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4,
        "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    outer = fig.add_gridspec(2, 3, left=0.078, right=0.995, top=0.885, bottom=0.115,
                             hspace=0.30, wspace=0.07)
    row_ylim = [(-1.6, 3.5), (-1.6, 5.9)]
    row_yticks = [[0, 2], [0, 2, 4]]
    rlim = 3.9
    for slot, r in enumerate(rows):
        row, col = divmod(slot, 3)
        cell = outer[slot].subgridspec(2, 1, height_ratios=[2.0, 1.15], hspace=0.07)
        ax = fig.add_subplot(cell[0])
        ar = fig.add_subplot(cell[1], sharex=ax)
        ell = r["ell"]
        ax.axhline(0, color=RULE, lw=1.2, zorder=0)
        ax.plot(ell, ell * r["theory"] * SCALE, "-", color=OCHRE, lw=2.6, zorder=2)
        ax.errorbar(ell, ell * r["data"] * SCALE, yerr=ell * r["sigma"] * SCALE, fmt="o", ms=7,
                    color=COBALT, mec="white", mew=1.0, elinewidth=2.0, capsize=0, zorder=3)
        ax.set_ylim(*row_ylim[row])
        ax.set_yticks(row_yticks[row])
        ax.text(0.97, 0.95, f"source bin {r['bin']}", transform=ax.transAxes, fontsize=25,
                color=INK, ha="right", va="top")
        ar.axhspan(-2, 2, color=BAND_OUTER, lw=0, zorder=0)
        ar.axhspan(-1, 1, color=BAND_INNER, lw=0, zorder=0)
        ar.axhline(0, color=MUTED, lw=1.2, zorder=1)
        ar.plot(ell, r["resid"], "o", ms=7, color=COBALT, mec="white", mew=1.0, zorder=3)
        ar.set_ylim(-rlim, rlim)
        ar.set_yticks([-2, 2])
        ar.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _p: f"{v:+.0f}".replace("-", "−") if v else "0"))
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _p: f"{v:.0f}".replace("-", "−")))
        for a in (ax, ar):
            a.set_xscale("log")
            a.set_xlim(ell.min() / 1.15, ell.max() * 1.15)
            a.xaxis.set_major_locator(FixedLocator(ELL_TICKS))
            a.xaxis.set_minor_locator(NullLocator())
            a.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{int(v)}"))
        ax.tick_params(labelbottom=False)
        if col:
            ax.tick_params(labelleft=False)
            ar.tick_params(labelleft=False)
        else:
            ax.set_ylabel(r"$10^6\,\ell C_\ell^{\gamma\kappa}$", labelpad=6)
            ar.set_ylabel(r"$\Delta/\sigma_G$", labelpad=6)
        if row == 1:
            ar.set_xlabel(r"multipole $\ell$", labelpad=2)
        else:
            ar.tick_params(labelbottom=False)
    # header: title left, key right
    fig.text(0.078, 0.955, "TR1 shear × SPT-3G Main κ (blinded)", fontsize=27, color=INK,
             ha="left", va="center")
    handles = [Line2D([], [], color=COBALT, marker="o", ms=9, mec="white", lw=2.0, ls="-"),
               Line2D([], [], color=OCHRE, lw=2.8)]
    labels = [r"blinded data $\pm\,\sigma_G$", "windowed fiducial reference"]
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(0.995, 0.955), ncol=2,
               frameon=False, fontsize=23, handlelength=1.6, columnspacing=1.6,
               labelcolor=INK)
    fig.savefig(OUT, dpi=DPI)
    plt.close(fig)
    print("wrote", OUT)


def main():
    setup_font()
    rows = load()
    summarize(rows)
    draw(rows)


if __name__ == "__main__":
    main()
