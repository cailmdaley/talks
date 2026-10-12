"""Lensing efficiency and why source bin 1 is the sensitive one: a teaching figure.

Three panels on the TR1 source/lens n(z) (the blinded likelihood input's n(z),
as delivered) and a Planck-like flat LCDM (pyccl):

  a  one source plane at z_s = 1: the geometric factor q(z_l) = (chi_s - chi_l)/chi_s,
     and the full lensing weight  ~ chi_l q(z_l)/a(z_l)  (normalised), which peaks
     roughly halfway to the sources.
  b  q_i(z) = int dz' n_i(z') (chi' - chi)/chi' for the six source bins and
     q_*(z) = (chi_* - chi)/chi_* for the CMB, over the six lens-bin n(z).
  c  % change in <q_i>_j (averaged over lens bin j) when source bin i's n(z) moves up
     by 0.01, at every lens bin the lens-ratio fit uses (zbar_s - zbar_l >= 0.2).

Output: images/napoli_lensing_efficiency.png (3424 x 1400 px).
Run in the cmbx container: app python make_lensing_efficiency.py
"""
import os, pickle, sys, tempfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyccl as ccl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_blind_rehearsal import setup_font  # noqa: E402

OUT = os.path.join(HERE, "..", "images", "napoli_lensing_efficiency.png")
DNDZ = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx/results/scratch/napoli/crosses/input/likelihood_input_spt_winter_gmvbhttprf_dndz.pkl"
INK, MUTED, RULE = "#111418", "#535B67", "#C6CEDA"
COBALT, TEAL, OCHRE = "#2E417C", "#1D6C78", "#9C7414"
GREY = "#A7AFBB"
LENSFILL = "#DCE3EC"
FRONT = {0: [0], 1: [0, 1], 2: [0, 1, 2], 3: [0, 1, 2, 3, 4], 4: range(6), 5: range(6)}
DPI = 200
TICK, LABEL = 21, 23


def main():
    setup_font()
    nz = pickle.load(open(DNDZ, "rb"))
    cosmo = ccl.Cosmology(Omega_c=0.2607, Omega_b=0.04897, h=0.6766, sigma8=0.8102, n_s=0.9665)
    zg = np.linspace(0.005, 3.0, 700)
    chi = ccl.comoving_radial_distance(cosmo, 1 / (1 + zg))
    chis = ccl.comoving_radial_distance(cosmo, 1 / (1 + 1090.0))

    def norm(z, n):
        m = np.interp(zg, z, n, left=0, right=0)
        return m / np.trapezoid(m, zg)

    def q_of(n):
        return np.array([np.trapezoid(np.where(chi > c, n * (chi - c) / chi, 0.0), zg) for c in chi])

    src = [norm(*(np.asarray(v, float) for v in nz[f"l{i}"])) for i in range(6)]
    lens = [norm(*(np.asarray(v, float) for v in nz[f"g{j}"])) for j in range(6)]
    zbar_s = [np.trapezoid(zg * n, zg) for n in src]
    zbar_l = [np.trapezoid(zg * n, zg) for n in lens]
    q = [q_of(n) for n in src]
    qstar = (chis - chi) / chis

    def shifted(i, dz):
        z, n = (np.asarray(v, float) for v in nz[f"l{i}"])
        return norm(z + dz, n)

    sens = {}
    for i in range(6):
        qp, qm = q_of(shifted(i, 0.01)), q_of(shifted(i, -0.01))
        sens[i] = [(zbar_l[j], 100 * 0.5 * (np.log(np.trapezoid(lens[j] * qp, zg)) - np.log(np.trapezoid(lens[j] * qm, zg))))
                   for j in FRONT[i]]
        print(f"source {i+1}: " + " ".join(f"l{j+1} {s:.2f}%" for j, (_, s) in zip(FRONT[i], sens[i])))

    plt.rcParams.update({
        "axes.linewidth": 1.4, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.labelcolor": INK, "xtick.labelsize": TICK, "ytick.labelsize": TICK, "axes.labelsize": LABEL,
        "xtick.major.width": 1.4, "ytick.major.width": 1.4, "xtick.major.size": 7, "ytick.major.size": 7,
        "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig, axs = plt.subplots(1, 3, figsize=(3424 / DPI, 1400 / DPI), dpi=DPI,
                            gridspec_kw=dict(width_ratios=[0.8, 1.15, 1], wspace=0.32, left=0.065, right=0.985,
                                             top=0.86, bottom=0.14))
    colour = {0: OCHRE, 5: COBALT}

    # a: one source plane
    ax = axs[0]
    zs = 1.0
    cs = ccl.comoving_radial_distance(cosmo, 1 / (1 + zs))
    m = zg < zs
    qa = np.where(m, (cs - chi) / cs, 0)
    w = chi * qa * (1 + zg)
    ax.plot(zg[m], qa[m], color=INK, lw=3)
    ax.plot(zg[m], (w / w.max())[m], color=TEAL, lw=3, ls=(0, (5, 3)))
    ax.axvline(zs, color=MUTED, lw=1.4, ls=(0, (2, 3)))
    ax.text(zs + 0.03, 0.3, "sources", color=MUTED, fontsize=LABEL - 2, ha="left", va="center", rotation=90)
    ax.text(1.18, 1.36, r"$q = \dfrac{\chi_s-\chi_l}{\chi_s}$", color=INK, fontsize=LABEL + 2, ha="right", va="center")
    ax.text(0.5, 1.04, "lensing weight " + r"$\propto \chi_l\, q\,/\,a$", color=TEAL, fontsize=LABEL - 1, ha="center", va="bottom")
    ax.set_xlim(0, 1.2); ax.set_ylim(0, 1.5); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"lens redshift $z_l$"); ax.set_ylabel("efficiency")
    ax.set_title("a · one source plane at $z_s = 1$", fontsize=LABEL, color=MUTED, loc="left", pad=14)

    # b: q_i and q_* over the lens bins
    ax = axs[1]
    for j, n in enumerate(lens):
        ax.fill_between(zg, 0, 0.32 * n / max(l.max() for l in lens), color=LENSFILL, lw=0, zorder=0)
    ax.annotate("lens bins δ1–δ6", xy=(1.0, 0.06), xytext=(2.55, 0.32), color=MUTED, fontsize=LABEL - 3, ha="right", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2))
    ax.plot(zg, qstar, color=INK, lw=3, zorder=3)
    ax.text(2.0, qstar[np.searchsorted(zg, 2.0)] + 0.03, "CMB  $q_*$", color=INK, fontsize=LABEL, ha="left", va="bottom")
    for i in range(6):
        c = colour.get(i, GREY)
        ax.plot(zg, q[i], color=c, lw=3 if i in colour else 1.8, zorder=2 if i not in colour else 4)
    ax.text(0.03, q[0][0] + 0.005, "source bin 1", color=OCHRE, fontsize=LABEL - 1, ha="left", va="bottom")
    ax.text(1.45, q[5][np.searchsorted(zg, 1.45)] + 0.02, "source bin 6", color=COBALT, fontsize=LABEL - 1, ha="left", va="bottom")
    ax.text(1.0, 0.38, "bins 2–5", color=MUTED, fontsize=LABEL - 3, ha="left")
    # q_1 / q_* at lens bin 1
    j = 0
    zl = zbar_l[j]
    q1, qs1 = np.interp(zl, zg, q[0]), np.interp(zl, zg, qstar)
    ax.annotate("", xy=(zl, q1), xytext=(zl, qs1), arrowprops=dict(arrowstyle="<->", color=OCHRE, lw=1.8))
    ax.annotate(f"at mean of $\\delta_1$:  $q_1/q_* = {q1/qs1:.2f}$", xy=(zl, 0.55 * (q1 + qs1)), xytext=(1.0, 0.95), color=OCHRE,
                fontsize=LABEL - 3, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=OCHRE, lw=1.2))
    ax.set_xlim(0, 2.6); ax.set_ylim(0, 1.02)
    ax.set_xlabel(r"lens redshift $z_l$"); ax.set_ylabel("efficiency $q(z_l)$")
    ax.set_title("b · six Euclid source bins against the CMB", fontsize=LABEL, color=MUTED, loc="left", pad=14)

    # c: sensitivity to a source shift
    ax = axs[2]
    for i in range(6):
        x, y = zip(*sens[i])
        c = colour.get(i, GREY)
        ax.plot(x, y, color=c, lw=3 if i in colour else 1.8, marker="o", ms=9 if i in colour else 6,
                mec="white", mew=1.4, zorder=3 if i in colour else 2)
        ax.text(x[-1] + 0.02, y[-1], f"s{i+1}", color=c if i in colour else MUTED, fontsize=TICK - 2, ha="left", va="center")
    ax.axhline(1.0, color=TEAL, lw=1.6, ls=(0, (5, 3)))
    ax.text(0.97, 3.85, "dashed: $m = +0.01$ moves\nevery $\\mu_i$ by 1 %", color=TEAL, fontsize=LABEL - 3, ha="right", va="top")
    ax.set_xlim(0.25, 0.98); ax.set_ylim(0, 4.0)
    ax.set_xlabel(r"lens bin $\bar z_l$"); ax.set_ylabel(r"change in $\mu_i$ per $\Delta z_s = +0.01$  [%]")
    ax.set_title("c · sensitivity to a source shift", fontsize=LABEL, color=MUTED, loc="left", pad=14)
    fig.savefig(OUT, dpi=DPI)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
