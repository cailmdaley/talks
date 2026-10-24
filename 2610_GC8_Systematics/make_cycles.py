"""GC-8 deck figures, drawn for either data cycle from one function each.

Every figure function takes a cycle ('c1' or 'c2') and draws on a canvas and axis ranges that
are common to both cycles, so the deck's Cycle toggle changes only the data. Where a cycle's
inputs have not been materialized, the same canvas is drawn empty with a "Cycle 2 pending" note
naming the missing output.

Inputs (all read-only):
  Cycle 1 (TR1 v1.1, VMPZ v1.1 templates)
    results/tr1/tr1_systematics/<template>.tar   measurement.json: GC (coverage-only delta), WL,
                                                 template_kappa; NaMaster Gaussian covariance per test
    results/scratch/napoli/visibility_check/<template>.json   delta / visibility weight ("after")
    results/scratch/napoli/cib_shape/cib_rho_<freq>.json        the CIB route (compute.py rho)
  Cycle 2 (tr1_v2 selection, DR1 R2 templates; delta maps already visibility-corrected)
    results/tr1_v2/systematics/gaussian_null_family.tar   summary.json + joint.npz (78 tests,
                                                          joint Gaussian covariance)
    results/tr1_v2/systematics/<template>.tar             measurement.json nulls (fallback)

Conventions: chi^2 and PTE over the 15 bands (100 < l < 3000) against zero with the test's
Gaussian covariance block. Cycle 1 kappa uses the diagonal only (as in the KP2-3 deck); Cycle 2
kappa uses its block of the joint Gaussian covariance.

Writes images/gc8_heatmap_<cycle>.png, gc8_extinction_<cycle>.png,
gc8_cib_rho_<stage>_<freq>_<cycle>.png, and prints every number the slides and notes quote.

Run in the cmbx container:  app python docs/talks/2610_GC8_Systematics/make_cycles.py [figures...]
(figures: heatmap extinction cib; default all)
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGES = HERE.parent / 'images'
C1_DIR = ROOT / 'results/tr1/tr1_systematics'
C1_VIS = ROOT / 'results/scratch/napoli/visibility_check'
C2_DIR = ROOT / 'results/tr1_v2/systematics'
CIB_DIR = ROOT / 'results/scratch/napoli/cib_shape'

CYCLES = {'c1': 'Cycle 1 (TR1 v1.1)', 'c2': 'Cycle 2 (tr1_v2)'}
# (Cycle-1 archive / Cycle-2 archive, Cycle-2 stem, column label)
TEMPLATES = [('extinction_vis', 'GALACTICEXTINCTION_VIS', 'Extinction'),
             ('exposures_vis', 'EXPOSURES_VIS', 'Exposures'),
             ('noise_vis', 'NOISE_VIS', 'Noise'),
             ('psf_vis', 'PSF_VIS', 'PSF'),
             ('zodiacal_vis', 'ZODIACALLIGHT_VIS', 'Zodiacal\nlight'),
             ('stars_gaia', 'STARNUMBERDENSITY_GAIACAM', 'Stars')]
TRACERS = [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)] + ['kappa']
ROW_LABELS = ([rf'$\delta_{i}$' for i in range(1, 7)] + [rf'$\gamma_{i}$' for i in range(1, 7)]
              + [r'$\kappa$'])
NBANDS = 15
# three l-ranges of five bands each: 100-311, 311-965, 965-3000
RANGES = [(0, 5), (5, 10), (10, 15)]

INK, MUTED, RULE = '#111418', '#535B67', '#C6CEDA'
DPI = 200


# ── style ────────────────────────────────────────────────────────────────────

def setup_font():
    """Execute the Napoli deck's font function (EB Garamond from node_modules)."""
    source = HERE.parent / '2610_Napoli_CMBX/make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'setup_font')
    ns = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager, 'plt': plt,
          'HERE': str(HERE.parent / '2610_Napoli_CMBX')}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), ns)
    ns['setup_font']()
    plt.rcParams['mathtext.fallback'] = 'cm'
    plt.rcParams.update({
        'axes.linewidth': 1.4, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
        'xtick.color': INK, 'ytick.color': INK,
        'xtick.major.size': 8, 'ytick.major.size': 8,
        'xtick.major.width': 1.4, 'ytick.major.width': 1.4,
        'axes.spines.top': False, 'axes.spines.right': False,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
    })


def pending_note(fig, what, x=0.5, y=0.5, size=44, w=0.62, h=0.30):
    """A 'Cycle 2 pending' card over the empty canvas, naming what has not landed."""
    from matplotlib.patches import FancyBboxPatch
    fig.patches.append(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.02',
                                      transform=fig.transFigure, fc='white', ec=RULE, lw=2, zorder=10))
    fig.text(x, y + h * 0.18, 'Cycle 2 pending', ha='center', va='center', fontsize=size * 1.4,
             color=INK, zorder=11)
    fig.text(x, y - h * 0.22, what, ha='center', va='center', fontsize=size * 0.8, color=MUTED,
             zorder=11, linespacing=1.1)


# ── data ─────────────────────────────────────────────────────────────────────

def _c1_measurement(name):
    path = C1_DIR / f'{name}.tar'
    with tarfile.open(path) as t:
        return json.load(t.extractfile('measurement.json'))


def nulls(cycle, delta='vis'):
    """{template: {tracer: (cross[15], cov[15,15])}} for the cycle, or None where not landed.

    delta: 'vis' (visibility-weighted) or 'raw' (coverage-only); Cycle 1 only, since the Cycle-2
    density maps are visibility-corrected at the source."""
    out = {}
    if cycle == 'c1':
        for name, _, _ in TEMPLATES:
            m = _c1_measurement(name)
            d = {}
            vis = json.load(open(C1_VIS / f'{name}.json'))['GC'] if delta == 'vis' else None
            for k in m['GC']:
                r = vis[k]['after'] if vis else m['GC'][k]
                d[k] = (np.asarray(r['cross']), np.asarray(r['covariance']))
            for k, r in m['WL'].items():
                d[k] = (np.asarray(r['cross']), np.asarray(r['covariance']))
            r = m['template_kappa']
            d['kappa'] = (np.asarray(r['cross']), np.diag(np.diag(np.asarray(r['covariance']))))
            out[name] = d
        return out
    fam = C2_DIR / 'gaussian_null_family.tar'
    if fam.exists() and fam.stat().st_size > 0:
        with tarfile.open(fam) as t:
            s = json.load(t.extractfile('summary.json'))
            j = np.load(io.BytesIO(t.extractfile('joint.npz').read()))
            cov, obs = j['covariance'], j['observed']
        index = {n: i for i, n in enumerate(s['test_names'])}
        for name, stem, _ in TEMPLATES:
            d = {}
            for k in TRACERS:
                i = index[f'{stem}/{k}']
                d[k] = (obs[i], cov[i * NBANDS:(i + 1) * NBANDS, i * NBANDS:(i + 1) * NBANDS])
            out[name] = d
        return out
    for name, stem, _ in TEMPLATES:
        path = C2_DIR / f'{name}.tar'
        if not (path.exists() and path.stat().st_size > 0):
            out[name] = None
            continue
        with tarfile.open(path) as t:
            m = json.load(t.extractfile('measurement.json'))
        out[name] = {k: (np.asarray(r['cross']), np.asarray(r['covariance'])) for k, r in m['nulls'].items()}
    return out


def chi2(cross, cov):
    q = float(cross @ np.linalg.solve(cov, cross))
    return q, float(stats.chi2.sf(q, cross.size))


def coherent(cross, cov, sl=slice(None)):
    """Signed coherent amplitude in sigma over a band range: the GLS mean of the band pulls with
    their Gaussian correlation matrix (Sum pull / sqrt(n) when the bands are uncorrelated)."""
    c, C = cross[sl], cov[sl, sl]
    s = np.sqrt(np.diag(C))
    p, R = c / s, C / np.outer(s, s)
    one = np.ones_like(p)
    Ri1 = np.linalg.solve(R, one)
    return float(Ri1 @ p / np.sqrt(Ri1 @ one))


# ── heatmap (slide 2) ────────────────────────────────────────────────────────

def fmt(p):
    if p >= 0.01:
        return f'{p:.2f}'
    if p < 1e-6:
        return r'$<\!10^{-6}$'
    m, e = f'{p:.1e}'.split('e')
    return rf'${m}\!\times\!10^{{{int(e)}}}$'


def heatmap(cycle):
    """chi^2 PTE of each tracer x template cross against zero: 13 rows, 6 templates."""
    data = nulls(cycle, 'vis')
    out = IMAGES / f'gc8_heatmap_{cycle}.png'
    have = all(v is not None for v in data.values())
    P = np.full((13, len(TEMPLATES)), np.nan)
    if have:
        for a, (name, _, _) in enumerate(TEMPLATES):
            for j, k in enumerate(TRACERS):
                P[j, a] = chi2(*data[name][k])[1]
    cmap = LinearSegmentedColormap.from_list(
        'calm', [(0, '#FFFFFF'), (1.3 / 6, '#FBF6EA'), (2.0 / 6, '#F1DFB8'), (3.2 / 6, '#D9A85A'),
                 (4.6 / 6, '#A8542B'), (1, '#7A2318')])
    fig = plt.figure(figsize=(10.0, 7.6), dpi=DPI)
    ax = fig.add_axes([0.085, 0.015, 0.905, 0.79])
    Z = np.clip(-np.log10(np.maximum(np.nan_to_num(P, nan=1.0), 1e-300)), 0, 6)
    ax.imshow(Z, cmap=cmap, vmin=0, vmax=6, aspect='auto')
    if have:
        for (i, j), p in np.ndenumerate(P):
            z = Z[i, j]
            ax.text(j, i, fmt(p), ha='center', va='center', fontsize=23,
                    color='white' if z > 4.0 else (INK if z > 1.3 else MUTED))
    ax.set_yticks(range(13), ROW_LABELS, fontsize=26)
    ax.xaxis.tick_top()
    ax.set_xticks(range(len(TEMPLATES)), [t[2] for t in TEMPLATES], fontsize=23, linespacing=0.95)
    ax.tick_params(length=0, colors=INK, pad=6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for y in (5.5, 11.5):
        ax.axhline(y, color='white' if have else RULE, lw=6 if have else 2)
    fig.text(0.075, 0.985, r'$\chi^2$ PTE against zero; darker = smaller', fontsize=24, color=INK,
             ha='left', va='top')
    if not have:
        missing = [n for n, v in data.items() if v is None]
        pending_note(fig, 'tr1_v2 systematics.gaussian_null_family\nnot yet materialized',
                     x=0.53, y=0.26, size=36, w=0.86, h=0.34)
        print(f'{cycle}: pending ({len(missing)} of 6 templates missing)')
    fig.savefig(out, dpi=DPI, facecolor='white')
    plt.close(fig)
    print('wrote', out)
    if have:
        for a, (name, _, _) in enumerate(TEMPLATES):
            print(f'  {name:15s} ' + ' '.join(f'{p:.2g}' for p in P[:, a]))
            for k in TRACERS:
                cross, cov = data[name][k]
                pulls = cross / np.sqrt(np.diag(cov))
                j = int(np.argmax(np.abs(pulls)))
                q, p = chi2(cross, cov)
                if cycle == 'c1':
                    ell = np.asarray(_c1_measurement(name)['GC']['g0']['ell'])
                elif (C2_DIR / 'gaussian_null_family.tar').exists():
                    with tarfile.open(C2_DIR / 'gaussian_null_family.tar') as tar:
                        ell = np.asarray(json.load(tar.extractfile('summary.json'))['ell'])
                else:
                    with tarfile.open(C2_DIR / f'{name}.tar') as tar:
                        ell = np.asarray(json.load(tar.extractfile('measurement.json'))['nulls'][k]['ell'])
                print(f'    {k}: chi2={q:.5f}/15 PTE={p:.8g}; worst band={j}, ell={ell[j]:.2f}, Gaussian pull={pulls[j]:+.4f}')
    return P


# ── extinction coherent amplitudes (slide 4) ────────────────────────────────

RANGE_COLORS = ['#A9BCD6', '#5A7BB0', '#1E3566']
RANGE_LABELS = [r'$100<\ell<311$', r'$311<\ell<965$', r'$965<\ell<3000$']


def extinction(cycle, ylim=(-4.2, 10.2)):
    """Each tracer x extinction cross as a signed coherent amplitude in Gaussian sigma, in three
    l-ranges, tracers grouped by class and ordered by redshift within each class."""
    delta = 'raw' if cycle == 'c1' else 'vis'
    data = nulls(cycle, delta)['extinction_vis']
    out = IMAGES / f'gc8_extinction_{cycle}.png'
    fig = plt.figure(figsize=(3424 / DPI, 1400 / DPI), dpi=DPI)
    ax = fig.add_axes([0.085, 0.13, 0.905, 0.75])
    x = np.r_[np.arange(6), np.arange(6) + 7, [14]].astype(float)
    ax.axhline(0, color=MUTED, lw=1.4, zorder=1)
    ax.axhspan(-2, 2, color='#EEF1F5', lw=0, zorder=0)
    for xb in (6, 13):
        ax.axvline(xb, color=RULE, lw=2)
    rows = {}
    if data is not None:
        for j, k in enumerate(TRACERS):
            c, C = data[k]
            vals = [coherent(c, C, slice(a, b)) for a, b in RANGES]
            rows[k] = dict(ranges=vals, full=coherent(c, C), chi2=chi2(c, C))
            for r, v in enumerate(vals):
                ax.plot(x[j] + (r - 1) * 0.24, v, 'o', ms=17, color=RANGE_COLORS[r], mec='white',
                        mew=1.5, zorder=3)
    ax.set_xlim(-0.7, 14.7)
    ax.set_ylim(*ylim)
    ax.set_xticks(x, ROW_LABELS)
    ax.tick_params(axis='x', length=0, labelsize=44, pad=10)
    ax.tick_params(axis='y', labelsize=36)
    ax.set_ylabel(r'amplitude / Gaussian $\sigma$', fontsize=38)
    dlab = 'Density, coverage-only' if cycle == 'c1' else 'Density, visibility-corrected'
    for xc, lab in ((2.5, dlab), (9.5, 'Shear (LensMC)'), (14, 'CMB\nlensing')):
        ax.text(xc, ylim[1] - 0.3, lab, ha='center', va='top', fontsize=36, color=MUTED,
                transform=ax.transData, linespacing=0.9)
    handles = [Line2D([], [], marker='o', ls='', ms=17, color=c, mec='white', label=l)
               for c, l in zip(RANGE_COLORS, RANGE_LABELS)]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.08, 1.005), ncol=3, frameon=False,
               fontsize=36, handletextpad=0.2, columnspacing=1.2)
    if data is None:
        pending_note(fig, 'tr1_v2 systematics.gaussian_null_family not yet materialized',
                     x=0.54, y=0.50, size=40, w=0.66, h=0.36)
    fig.savefig(out, dpi=DPI, facecolor='white')
    plt.close(fig)
    print('wrote', out)
    for k, r in rows.items():
        print(f'  {k:6s} chi2 {r["chi2"][0]:6.1f} PTE {r["chi2"][1]:.2g}  coherent {r["full"]:+.2f}  '
              'ranges ' + ' '.join(f'{v:+.2f}' for v in r['ranges']))
    return rows


# ── the CIB route in rho_l (slide 5) ─────────────────────────────────────────

FREQS = ('857', '545', '353')
FRAMES = [('points', '857'), ('bands', '857'), ('full', '857'), ('full', '545'), ('full', '353')]
RHO_PANELS = [('delta1', r'$\delta_1$'), ('delta5', r'$\delta_5$'), ('delta6', r'$\delta_6$'),
              ('gamma1', r'$\gamma_1$'), ('gamma5', r'$\gamma_5$'), ('gamma6', r'$\gamma_6$')]
DCOL, GCOL, RAW = '#1F3F73', '#8A2A22', '#B07A2A'


def cib_input(cycle, freq):
    """The CIB-route numbers: compute.py rho output. Cycle 2 has no such scratch product yet."""
    if cycle == 'c1':
        return json.loads((CIB_DIR / f'cib_rho_{freq}.json').read_text())
    path = ROOT / f'results/scratch/gc8/cib_shape_c2/cib_rho_{freq}.json'
    return json.loads(path.read_text()) if path.exists() else None


def cib_ylim():
    lo, hi = -0.12, 0.42
    for cycle in CYCLES:
        for f in FREQS:
            d = cib_input(cycle, f)
            if d is None:
                continue
            for name in ('delta1_vis', 'delta5_vis', 'delta6_vis', 'delta1_raw', 'delta5_raw',
                         'delta6_raw', 'gamma1', 'gamma5', 'gamma6'):
                if name not in d['bins']:
                    continue  # Cycle 2 has no coverage-only delta arm.
                b = d['bins'][name]
                for v, err in (('r_measured', 'sigma_measured'), ('r_predicted', 'sigma_predicted')):
                    a, s = np.asarray(b[v]), np.asarray(b[err])
                    lo, hi = min(lo, (a - s).min() - .03), max(hi, (a + s).max() + .04)
    return lo, hi


def cib_frame(cycle, stage, freq, ylim):
    """One build frame of rho_l(tracer, ext) against the CIB route, at 2x the 1712x771 body.

    Error bars: sigma_G(C^{T,ext}) / sqrt(C^TT C^ee), the NaMaster Gaussian error of the cross with
    the total observed autos fixed. The full Gaussian propagation through the two autos multiplies
    it by (1 - rho^2) / sqrt(1 + rho^2) (Gaussian fields, one mode count): at the predicted rho,
    |rho| <= 0.17, that is 0.955-1, so the bars are the Gaussian error of rho_l to within 5 %
    and on the large side (the factor at the largest predicted rho is printed below)."""
    data = cib_input(cycle, freq)
    out = IMAGES / f'gc8_cib_rho_{stage}_{freq}_{cycle}.png'
    plt.rcParams.update({'font.size': 30, 'axes.labelsize': 30, 'xtick.labelsize': 28,
                         'ytick.labelsize': 28})
    show_bands, show_raw = stage != 'points', stage == 'full' and cycle == 'c1'
    fig = plt.figure(figsize=(3424 / DPI, 1542 / DPI), dpi=DPI)
    x0, y0, w, h, gx, gy = .06, .15, .29, .31, .027, .08
    axes = []
    for k, (key, label) in enumerate(RHO_PANELS):
        row, col = divmod(k, 3)
        ax = fig.add_axes([x0 + col * (w + gx), y0 + (1 - row) * (h + gy), w, h],
                          sharey=axes[0] if axes else None, sharex=axes[0] if axes else None)
        axes.append(ax)
        ax.axhline(0, color=MUTED, lw=1)
        if data is not None:
            ell = np.asarray(data['ell'])
            series = (([(f'{key}_raw', RAW, -.025)] if show_raw else []) + [(f'{key}_vis', DCOL, .025)]
                      if key.startswith('delta') else [(key, GCOL, 0)])
            for name, color, off in series:
                b = data['bins'][name]
                p, sp = np.asarray(b['r_predicted']), np.asarray(b['sigma_predicted'])
                m, sm = np.asarray(b['r_measured']), np.asarray(b['sigma_measured'])
                if show_bands:
                    ax.fill_between(ell, p - sp, p + sp, color=color, alpha=.22, lw=0, zorder=1)
                    ax.plot(ell, p, color=color, lw=2, alpha=.9, zorder=2)
                ax.errorbar(ell * 10 ** off, m, yerr=sm, fmt='o', ms=8, color=color, mec='white', mew=.8,
                            elinewidth=1.8, capsize=0, zorder=3)
        ax.set_title(label, loc='left', fontsize=34, color=INK, pad=6)
        if key == 'delta1':
            ax.text(.98, .84, 'visibility-weighted' if cycle == 'c1' else 'visibility-corrected',
                    transform=ax.transAxes, ha='right', va='top',
                    fontsize=28, color=DCOL)
            ax.text(.98, .99, 'unweighted', transform=ax.transAxes, ha='right', va='top',
                    fontsize=28, color=RAW, alpha=1 if show_raw else 0)
        ax.set_xscale('log')
        ax.set_xlim(95, 3200)
        ax.set_xticks([100, 300, 1000], ['100', '300', '1000'])
        ax.xaxis.set_minor_formatter(NullFormatter())
        if row == 1:
            ax.set_xlabel(r'Multipole $\ell$', labelpad=6)
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
        if col == 0:
            ax.set_ylabel(r'$\rho_\ell$', labelpad=8)
        else:
            plt.setp(ax.get_yticklabels(), visible=False)
    axes[0].set_ylim(ylim)
    handles = [Line2D([], [], color=MUTED, marker='o', ls='', ms=9,
                      label=r'measured $\rho_\ell(\mathrm{tracer},\mathrm{ext})$'),
               plt.Rectangle((0, 0), 1, 1, color=MUTED, alpha=.35,
                             label=rf'via the {freq} GHz CIB: $\rho_\ell(\mathrm{{tracer}},\mathrm{{CIB}})\,'
                                   rf'\rho_\ell(\mathrm{{CIB}},\mathrm{{ext}})$')]
    legend = fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.065, 1.0), ncol=2,
                        frameon=False, fontsize=30, handletextpad=.4, columnspacing=1.6)
    if not show_bands:
        legend.legend_handles[1].set_alpha(0)
        legend.get_texts()[1].set_alpha(0)
    if data is None:
        pending_note(fig, 'the CIB route is a scratch analysis on the Cycle-1 maps;\n'
                     'its tracer × CIB crosses have not been run on tr1_v2', x=0.52, y=0.50, size=34,
                     w=0.56, h=0.36)
    fig.savefig(out, dpi=DPI, facecolor='white')
    plt.close(fig)
    print('wrote', out)
    if data is not None and stage == 'full':
        worst = 0.0
        for name in ('delta1_vis', 'delta5_vis', 'delta6_vis', 'delta1_raw', 'delta5_raw', 'delta6_raw',
                     'gamma1', 'gamma5', 'gamma6'):
            if name in data['bins']:
                worst = max(worst, float(np.abs(np.asarray(data['bins'][name]['r_predicted'])).max()))
        print(f'  {freq}: max |rho| predicted {worst:.3f}; Gaussian auto-term factor there '
              f'{(1 - worst ** 2) / np.sqrt(1 + worst ** 2):.4f}')


def cib(cycle):
    ylim = cib_ylim()
    for stage, freq in FRAMES:
        cib_frame(cycle, stage, freq, ylim)


def main():
    setup_font()
    which = sys.argv[1:] or ['heatmap', 'extinction', 'cib']
    for cycle in CYCLES:
        print(f'== {cycle}: {CYCLES[cycle]}')
        if 'heatmap' in which:
            heatmap(cycle)
        if 'extinction' in which:
            extinction(cycle)
        if 'cib' in which:
            cib(cycle)


if __name__ == '__main__':
    main()
