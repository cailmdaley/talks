"""The DR1 blinding tests: how a shift is drawn, and whether a chain recovers it.

draws.npz: shift draws in (logA, omch2, h) and what each means in (S8, Omega_m), for four recipes.
slim.npz, ens.npz: 30 shifts drawn flat in (A_s, omch2, h), kept within 3 sigma of the 3x2pt (S8, Omega_m); for each a
chain on the shifted noiseless DR1 vector. Recovery = posterior mean(shifted) - mean(unshifted) - injected, in units of
the unshifted chain's sigma, for (Omega_m, S8). map/*.npz (mapfit.py): the same at the posterior's maximum, for five probe
sets with noise, with the blind's reference fixed or at the best fit of the vector. Writes images/ice_blind_draws.png, images/ice_blind_recovery_<k>.png
and blind_ensemble.json.

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_blind_ensemble.py --src ~/scratch/dr1fc
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt

NAMES = ['sigma8', 'S8', 'Omega_m']
ARMS = [('3x2_m', 'dr1_3x2', '3×2pt with the truth at the reference', '#535B67', 'o'),
        ('5x2_m', 'dr1_MS_5x2', '5×2pt with the truth at the reference', '#9C7414', 's'),
        ('5x2_x', 'ens_base_5x2_s', '5×2pt with the truth off the reference', '#C0392B', 'D')]


def moments(z, n):
    d, w = z[n + '|d'].astype(float), z[n + '|w'].astype(float)
    w /= w.sum()
    d = d[:, [NAMES.index('S8'), NAMES.index('Omega_m')]]
    m = w @ d
    return m, np.sqrt(w @ (d - m) ** 2)


def recovery(z, D, ref, arm, base):
    mb, sb = moments(z, base)
    have = {k.split('|')[0] for k in z.files}
    rows = []
    for i in range(len(D)):
        n = f'ens_{arm}_{i:02d}'
        if n in have:
            m, s = moments(z, n)
            rows.append(np.r_[(m - mb - (D[i] - ref)) / sb, s / sb, (D[i] - ref) / sb])
    return np.array(rows)


def rc():
    style.setup_font()
    plt.rcParams.update({'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27,
                         'axes.linewidth': 2.4, 'axes.edgecolor': style.MUTED, 'axes.labelcolor': style.INK,
                         'xtick.color': style.MUTED, 'ytick.color': style.MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'axes.spines.top': False, 'axes.spines.right': False})


def fig_draws(d, out):
    s = np.sqrt(np.diag(d['C3']))
    kept = np.abs((d['flat3_D'] - d['ref']) / s)[d['flat3_chi2'] < 9][:, 0]
    rows = [(r'$(\omega_c, A_s)$ from the posterior', np.abs((d['marg2_D'] - d['ref']) / s)[:, 0]),
            (r'flat in $(A_s,\omega_c,h)$, $\pm3\sigma$', np.abs((d['flat3_D'] - d['ref']) / s)[:, 0]),
            (r'the same, kept within $3\sigma$ in $(S_8,\Omega_\mathrm{m})$', kept),
            (r'$(\omega_c, A_s)$ set by $(S_8,\Omega_\mathrm{m})$', np.abs((d['jac_D'] - d['ref']) / s)[:, 0])]
    fig = plt.figure(figsize=(style.W_PX / style.DPI, style.H_PX / style.DPI), dpi=style.DPI)
    ax = fig.add_axes([0.07, 0.17, 0.90, 0.78])
    rng = np.random.default_rng(0)
    colors = ['#C0392B', '#2E6F95', '#2E6F95', '#535B67']
    for k, ((label, v), c) in enumerate(zip(rows, colors)):
        y = len(rows) - 1 - k
        v = np.clip(v, 0.03, 90)
        pick = rng.permutation(len(v))[:250]
        ax.scatter(v[pick], y + rng.uniform(-.16, .16, len(pick)), s=40, color=c, alpha=.28, lw=0, zorder=2)
        ax.plot([np.median(v)] * 2, [y - .28, y + .28], color=style.INK, lw=4, zorder=4)
        ax.text(0.032, y + .30, label, fontsize=26, color=style.INK, va='bottom')
    ax.axvline(3, color=style.MUTED, lw=2.4, ls='--', zorder=1)
    ax.set_xscale('log'); ax.set_xlim(.03, 90); ax.set_ylim(-.5, len(rows) - .05)
    ax.set_xticks([.1, 1, 10]); ax.set_xticklabels(['0.1', '1', '10'])
    ax.set_yticks([]); ax.spines['left'].set_visible(False)
    ax.set_xlabel(r'shift in $S_8$ / $\sigma(S_8)$ of the 3×2pt')
    fig.savefig(out, dpi=style.DPI); plt.close(fig)
    return {lab: dict(sd=float(np.std(v)), median=float(np.median(v)), n=int(len(v))) for lab, v in rows}


def maps(src):
    """Recovered minus injected at the posterior's maximum, in units of that probe's Laplace sigma, per case."""
    out = {}
    for f in sorted((src / 'map').glob('*.npz')):
        z = np.load(f)
        s = np.sqrt(np.diag(z['lap']))
        inj = z['shift'] - z['ref']
        out[f.stem] = ((z['derived'][1:] - z['derived'][:1] - inj) / s)[:, [1, 2]], s[[1, 2]], (inj / s)[:, [1, 2]]
    return out


PROBES = [('1x2', 'cosmic shear'), ('2x2', '2×2pt'), ('3x2', '3×2pt'), ('5x2', '5×2pt'), ('6x2', '6×2pt')]
ADD, REFIT = '#C0392B', '#2E6F95'


def fig_recovery(z, ens, M, outdir):
    D, ref = ens['D'], ens['ref']
    res = {arm: recovery(z, D, ref, arm, base) for arm, base, *_ in ARMS}
    W, H, LIM = 3424, 1446, 0.85
    for k in (1, 2, 3):
        fig = plt.figure(figsize=(W / style.DPI, H / style.DPI), dpi=style.DPI)
        ax = fig.add_axes([0.10, 0.19, 0.245, 0.58])
        t = np.linspace(0, 2 * np.pi, 200)
        ax.plot(.3 * np.cos(t), .3 * np.sin(t), color=style.MUTED, lw=2.4, ls='--', zorder=1)
        ax.axhline(0, color=style.MUTED, lw=1.2, zorder=0); ax.axvline(0, color=style.MUTED, lw=1.2, zorder=0)
        for (arm, base, label, c, m) in ARMS[:(2 if k == 1 else 3)]:
            r = res[arm]
            ax.scatter(r[:, 1], r[:, 0], s=170, color=c, alpha=.75, marker=m, lw=0, label=label, zorder=3)
        ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM)
        ax.set_xticks([-.6, 0, .6]); ax.set_yticks([-.6, -.3, 0, .3, .6])
        ax.set_xlabel(r'recovered $-$ injected $\Omega_\mathrm{m}$  [$\sigma$]')
        ax.set_ylabel(r'recovered $-$ injected $S_8$  [$\sigma$]')
        ax.legend(loc='lower left', bbox_to_anchor=(-.36, 1.01), ncol=1, frameon=False, fontsize=26,
                  handletextpad=.1, borderaxespad=0, labelspacing=.1)
        if k == 3:
            bx = fig.add_axes([0.60, 0.19, 0.39, 0.58])
            rng = np.random.default_rng(0)
            for j, (p, label) in enumerate(PROBES):
                y = len(PROBES) - 1 - j
                for mode, c, off in (('add', ADD, .17), ('refit', REFIT, -.17)):
                    v = np.concatenate([M[f'stress_{p}_{mode}_n{n}'][0][:, 0] for n in (1, 2)])
                    bx.scatter(v, y + off + rng.uniform(-.07, .07, len(v)), s=75, color=c, alpha=.5, lw=0, zorder=3)
                    bx.plot([-v.std(), v.std()], [y + off] * 2, color=c, lw=5, alpha=.9, zorder=2, solid_capstyle='butt')
                bx.text(-1.18, y, label, ha='right', va='center', fontsize=28, color=style.INK)
            bx.axvspan(-.3, .3, color=style.MUTED, alpha=.10, lw=0, zorder=0)
            bx.axvline(0, color=style.MUTED, lw=1.2, zorder=0)
            bx.set_xlim(-1.1, 1.1); bx.set_ylim(-.55, len(PROBES) - .45)
            bx.set_xticks([-1, -.5, 0, .5, 1]); bx.set_yticks([]); bx.spines['left'].set_visible(False)
            bx.set_xlabel(r'recovered $-$ injected $S_8$  [$\sigma$ of each probe]')
            for txt, c in (('fixed reference off the truth', ADD), ('reference at the fit to the vector', REFIT)):
                bx.scatter([], [], s=170, color=c, label=txt, lw=0)
            bx.legend(loc='lower left', bbox_to_anchor=(-.33, 1.01), frameon=False, fontsize=26, handletextpad=.1,
                      borderaxespad=0, labelspacing=.1)
        fig.savefig(outdir / f'ice_blind_recovery_{k}.png', dpi=style.DPI); plt.close(fig)
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', required=True)
    args = p.parse_args()
    src = Path(args.src).expanduser()
    rc()
    out = HERE.parent / 'images'
    draws = fig_draws(np.load(src / 'draws.npz'), out / 'ice_blind_draws.png')
    z, ens = np.load(src / 'slim.npz'), np.load(src / 'ens.npz')
    M = maps(src)
    res = fig_recovery(z, ens, M, out)
    summary = {'draws': draws, 'recovery': {}, 'best_fit': {
        n: dict(S8_mean=float(r[:, 0].mean()), S8_sd=float(r[:, 0].std()), S8_max=float(np.abs(r[:, 0]).max()),
                Om_mean=float(r[:, 1].mean()), Om_sd=float(r[:, 1].std()), Om_max=float(np.abs(r[:, 1]).max()),
                sigma_S8=float(s[0]), sigma_Om=float(s[1])) for n, (r, s, _) in M.items()}}
    for arm, r in res.items():
        if len(r):
            summary['recovery'][arm] = dict(n=len(r), S8_mean=float(r[:, 0].mean()), S8_sd=float(r[:, 0].std()),
                                            S8_max=float(np.abs(r[:, 0]).max()), Om_mean=float(r[:, 1].mean()),
                                            Om_sd=float(r[:, 1].std()), Om_max=float(np.abs(r[:, 1]).max()),
                                            frac_within_0p3=float(np.mean(np.hypot(r[:, 0], r[:, 1]) < .3)),
                                            width_S8=[float(r[:, 2].min()), float(r[:, 2].max())],
                                            width_Om=[float(r[:, 3].min()), float(r[:, 3].max())])
    (HERE / 'blind_ensemble.json').write_text(json.dumps(summary, indent=1) + '\n')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
