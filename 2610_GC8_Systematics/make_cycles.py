"""Presentation-only GC-8 redraws from saved measurements; never writes results/.

Run from the cmbx root: app python docs/talks/2610_GC8_Systematics/make_cycles.py
All errors use NaMaster Gaussian cross blocks, fixed normalization/template autos.
"""
from __future__ import annotations

import ast
import io
import json
import os
import tarfile
import tempfile
from functools import cache
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import numpy as np
from scipy.stats import chi2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGES = HERE.parent / 'images'
SCRATCH = ROOT / 'results/scratch/gc8'
TEMPLATES = [('extinction_vis', 'GALACTICEXTINCTION_VIS', 'Extinction'),
             ('exposures_vis', 'EXPOSURES_VIS', 'Exposures'),
             ('noise_vis', 'NOISE_VIS', 'Noise'), ('psf_vis', 'PSF_VIS', 'PSF'),
             ('zodiacal_vis', 'ZODIACALLIGHT_VIS', 'Zodiacal'),
             ('stars_gaia', 'STARNUMBERDENSITY_GAIACAM', 'Stars')]
TRACERS = [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)] + ['kappa']
LABELS = ([rf'$\delta_{i}$' for i in range(1, 7)] +
          [rf'$\gamma_{{E{i}}}$' for i in range(1, 7)] + [r'$\kappa$'])
INK, MUTED, RULE = '#111418', '#535B67', '#C6CEDA'
COLORS = ['#799fc9', '#628dbb', '#4c7bac', '#35649c', '#234979', '#102e53']
DPI = 200


@cache
def read(path):
    return json.loads(Path(path).read_text())


@cache
def archive(path):
    with tarfile.open(path) as t:
        return json.load(t.extractfile('measurement.json'))


def setup_font():
    source = HERE.parent / '2610_Napoli_CMBX/make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'setup_font')
    ns = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager, 'plt': plt,
          'HERE': str(source.parent)}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), ns)
    ns['setup_font']()
    plt.rcParams.update({'font.size': 25, 'axes.labelsize': 32, 'xtick.labelsize': 32,
                         'ytick.labelsize': 32, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.edgecolor': MUTED,
                         'mathtext.fallback': 'cm', 'figure.facecolor': 'white'})


def save(fig, name):
    fig.savefig(IMAGES / f'gc8r2_{name}.png', dpi=DPI, facecolor='white')
    plt.close(fig)
    print('wrote', name)


def qtest(row):
    c = np.asarray(row.get('cross', row.get('values')))
    cov = np.asarray(row['covariance'])
    assert c.shape == (15,) and cov.shape == (15, 15)
    return float(chi2.sf(c @ np.linalg.solve(cov, c), 15))


def family():
    with tarfile.open(ROOT / 'results/tr1_v2/systematics/gaussian_null_family.tar') as t:
        s = json.load(t.extractfile('summary.json'))
        j = np.load(io.BytesIO(t.extractfile('joint.npz').read()))
        return {name: {'cross': j['observed'][i],
                       'covariance': j['covariance'][i*15:(i+1)*15, i*15:(i+1)*15]}
                for i, name in enumerate(s['test_names'])}


def heatmaps():
    fam = family()
    b = {c: read(SCRATCH / f'shear-b/cycle{c}.json')['tests'] for c in (1, 2)}
    for cycle in ('c1', 'c2'):
        for shear in ('lensmc', 'metacal'):
            for cmb in ('spt', 'act'):
                P = np.full((19, 6), np.nan)
                for col, (name, stem, _) in enumerate(TEMPLATES):
                    if cycle == 'c1':
                        universe = 'tr1' + ('_act' if cmb == 'act' else '') + ('_metacal' if shear == 'metacal' else '')
                        directory = ROOT / f'results/{universe}/tr1_systematics'
                        paths = [directory / f'{name}{suffix}.tar' for suffix in ('', '_act')]
                        path = next((p for p in paths if p.exists()), None)
                        if path:
                            m = archive(path)
                            vis = read(ROOT / f'results/scratch/napoli/visibility_check/{name}.json')['GC']
                            for i in range(6):
                                P[i, col] = qtest(vis[f'g{i}']['after'])
                                P[i+6, col] = qtest(m['WL'][f'l{i}'])
                            P[18, col] = qtest(m['template_kappa'])
                        if shear == 'lensmc':
                            for i in range(6):
                                P[i+12, col] = qtest(b[1][f'{name}/l{i}']['B'])
                    else:
                        for i in range(6):
                            P[i, col] = qtest(fam[f'{stem}/g{i}'])
                            if shear == 'lensmc':
                                P[i+6, col] = qtest(fam[f'{stem}/l{i}'])
                                P[i+12, col] = qtest(b[2][f'{name}/l{i}']['B'])
                            else:
                                m = read(SCRATCH / f'metacal/{stem}_bin{i+1}.json')['components']
                                for comp, offset in [('E', 6), ('B', 12)]:
                                    P[i+offset, col] = qtest(m[comp])
                        if cmb == 'spt':
                            P[18, col] = qtest(fam[f'{stem}/kappa'])
                        else:
                            P[18, col] = qtest(read(SCRATCH / f'kappa_common/tr1_v2_act/{stem}_full.json'))
                fig, ax = plt.subplots(figsize=(10, 8.1))
                fig.subplots_adjust(left=.12, right=.99, top=.88, bottom=.02)
                Z = np.clip(-np.log10(np.maximum(P, 1e-300)), 0, 6)
                cmap = LinearSegmentedColormap.from_list('pte', ['#ffffff', '#f1dfb8', '#d9a85a', '#7a2318'])
                ax.imshow(Z, cmap=cmap, vmin=0, vmax=6, aspect='auto')
                for (i, j), p in np.ndenumerate(P):
                    if np.isnan(p):
                        ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, facecolor='#f3f5f8', edgecolor=RULE, hatch='///'))
                        text = 'not run'
                    else:
                        text = (f'{p:.2f}' if p >= .01 else (r'$<10^{-6}$' if p < 1e-6 else f'{p:.0e}'))
                    ax.text(j, i, text, ha='center', va='center', fontsize=28,
                            color='white' if np.isfinite(p) and p < 1e-4 else INK)
                labels = LABELS[:12] + [rf'$\gamma_{{B{i}}}$' for i in range(1, 7)] + LABELS[-1:]
                ax.set_yticks(range(19), labels, fontsize=28)
                ax.set_xticks(range(6), [t[2] for t in TEMPLATES], fontsize=23)
                ax.xaxis.tick_top()
                ax.tick_params(length=0)
                for y in (5.5, 11.5, 17.5):
                    ax.axhline(y, color=RULE, lw=2)
                for sp in ax.spines.values():
                    sp.set_visible(False)
                fig.text(.12, .985, r'$\chi^2$ PTE vs zero · darker = smaller', va='top', fontsize=25)
                save(fig, f'heatmap_{cycle}_{shear}_{cmb}')
                print(cycle, shear, cmb, 'B minimum', np.nanmin(P[12:18]) if np.isfinite(P[12:18]).any() else 'missing')
                print('  PTE rows:', P.tolist())


def row(r, cycle, tracer, template='vmpz', visibility='raw'):
    stage = visibility if tracer.startswith('g') else 'native'
    return r['rows'][f'{cycle}/{template}/{tracer}/{stage}']


def summary_axes():
    fig, ax = plt.subplots(figsize=(16, 7.7))
    fig.subplots_adjust(left=.09, right=.99, bottom=.15, top=.88)
    ax.axhline(0, color=MUTED, lw=1)
    for x in (5.5, 11.5):
        ax.axvline(x, color=RULE, lw=1)
    ax.set_xticks(range(13), LABELS, fontsize=32)
    ax.set_ylabel(r'$\bar\rho\quad(100<\ell<3000)$')
    ax.set_ylim(-.10, .23)
    return fig, ax


def rho_figures():
    r = read(SCRATCH / 'rho/rho.json')
    # Same limits for each panel across cycles, including every displayed error bar.
    groups = [TRACERS[:6], TRACERS[6:12], TRACERS[12:]]
    limits = []
    for group in groups:
        allrows = [row(r, c, k) for c in ('c1', 'c2') for k in group]
        lo = min(np.min(np.array(d['rho'])-d['sigma_rho']) for d in allrows)
        hi = max(np.max(np.array(d['rho'])+d['sigma_rho']) for d in allrows)
        limits.append((min(0, lo)-.02, hi+.03))
    for c in ('c1', 'c2'):
        fig, axes = plt.subplots(1, 3, figsize=(16, 7.7))
        fig.subplots_adjust(left=.07, right=.965, bottom=.18, top=.82, wspace=.37)
        for ax, group, title, lim in zip(axes, groups, ['Density', 'Shear E', 'CMB lensing'], limits):
            ax.axhline(0, color=MUTED, lw=1)
            for i, k in enumerate(group):
                d = row(r, c, k)
                ax.errorbar(np.array(d['ell'])*np.exp((i-2.5)*.009), d['rho'], yerr=d['sigma_rho'],
                            fmt='o', ms=6.5, elinewidth=1.3, color=COLORS[i] if len(group)>1 else COLORS[-1],
                            label=f'bin {i+1}' if len(group)>1 else r'$\kappa$')
            ax.set(xscale='log', xlim=(100, 3000), ylim=lim, xlabel=r'Multipole $\ell$')
            ax.set_title(title, loc='left', fontsize=32)
            ax.set_xticks([100, 1000, 3000], ['100', '1000', '3000'])
        axes[0].set_ylabel(r'$\rho_\ell$')
        handles, labs = axes[0].get_legend_handles_labels()
        fig.legend(handles, labs, ncol=6, loc='upper center', frameon=False, fontsize=32)
        save(fig, f'spectra_{c}')
        fig, ax = summary_axes()
        for i, k in enumerate(TRACERS):
            d = row(r, c, k)
            ax.errorbar(i, d['mean_rho'], yerr=d['mean_rho_error'], fmt='o', ms=10,
                        color=COLORS[i%6] if i<12 else '#8a2a22', capsize=4)
        fig.text(.1, .97, 'Full-range summary · density without visibility correction', va='top', fontsize=27)
        save(fig, f'means_{c}')
        fig, axes = plt.subplots(1, 2, figsize=(14.5, 7), sharey=True)
        fig.subplots_adjust(left=.09, right=.99, bottom=.15, top=.83, wspace=.13)
        for ax, stage, title in zip(axes, ['raw', 'vis'], ['Without visibility correction', 'With visibility correction']):
            ax.axhline(0, color=MUTED, lw=1)
            for kind, off, color, label in [('measured', -.1, '#234979', 'Measured extinction'), ('predicted', .1, '#a8542b', '857 GHz CIB route')]:
                vals, errs = [], []
                for i in range(6):
                    d = row(r, c, f'g{i}', visibility=stage) if kind=='measured' else r['cib_route'][f'{c}/g{i}/{stage}']
                    prefix = 'mean_rho' if kind=='measured' else 'mean_rho_pred'
                    vals.append(d[prefix]); errs.append(d[prefix+'_error'])
                ax.errorbar(np.arange(6)+off, vals, yerr=errs, fmt='o', ms=9, capsize=4, color=color, label=label)
            ax.set_xticks(range(6), [rf'$\delta_{i}$' for i in range(1, 7)])
            ax.set_title(title, fontsize=27)
            ax.set_ylim(-.02, .17)
        axes[0].set_ylabel(r'$\bar\rho\quad(100<\ell<3000)$')
        handles, labs = axes[0].get_legend_handles_labels()
        fig.legend(handles, labs, loc='upper center', frameon=False, ncol=2, fontsize=27)
        save(fig, f'route_{c}')
    fig, ax = summary_axes()
    for template, off, color, label in [('vmpz', -.19, '#234979', 'VMPZ / Planck13'), ('sfd', 0, '#a8542b', 'SFD'), ('csfd', .19, '#23776d', 'CSFD')]:
        rows = [row(r, 'c2', k, template=template, visibility='vis') for k in TRACERS]
        ax.errorbar(np.arange(13)+off, [d['mean_rho'] for d in rows], yerr=[d['mean_rho_error'] for d in rows],
                    fmt='o', ms=8, capsize=3, color=color, label=label)
    ax.legend(loc='upper left', ncol=3, frameon=False, fontsize=26)
    save(fig, 'dust_c2')


def leakage():
    base = SCRATCH / 'window-leakage'
    a, low, crosses = [read(base / f'{n}.json') for n in ('auto', 'lowell', 'crosses')]
    r = read(SCRATCH / 'rho/rho.json')
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5))
    fig.subplots_adjust(left=.13, right=.98, bottom=.24, top=.72, wspace=.42)
    for c, color, label in [('c1', '#a8542b', 'C1 window'), ('c2', '#234979', 'C2 window')]:
        axes[0].plot(a['ell'], a['tests'][c+'_original']['values'], color=color, lw=2.5, label=f'{c.upper()} total')
        y=np.array(low['tests'][c+'_low']['values'])
        # Negative low-only deconvolved bands cannot appear on a logarithmic ordinate.
        axes[0].plot(low['ell'], np.where(y>0,y,np.nan), '--o', color=color, lw=2.5, ms=4, label=f'{c.upper()} low-only')
    axes[0].set(xscale='log', yscale='log', xlabel=r'Multipole $\ell$', ylabel=r'$C_\ell^{TT}\;[\mathrm{mag}^2]$')
    axes[0].set_yticks([1e-11, 1e-9, 1e-7, 1e-5])
    axes[0].legend(frameon=False, fontsize=25, ncol=2, loc='lower left', bbox_to_anchor=(0, 1.04), columnspacing=.8, handlelength=1.2)
    keys = ['kappa'] + [f'g{i}' for i in range(6)]
    for j, (label, color) in enumerate([('C1 original', '#a8542b'), ('C1 rewindowed', '#23776d'), ('C2', '#234979')]):
        vals=[]
        for k in keys:
            if j==0:
                path = ROOT / 'results/tr1/tr1_systematics/extinction_vis.tar'
                m=archive(path)
                d=m['template_kappa'] if k=='kappa' else read(ROOT/'results/scratch/napoli/visibility_check/extinction_vis.json')['GC'][k]['after']
                c=np.array(d['cross']); cov=np.array(d['covariance'])
                val=float(c@np.linalg.solve(cov,c))
            elif j==1:
                key=f'c1_rewindowed/{k}' if k=='kappa' else f'c1_vis_rewindowed/{k}'
                d=crosses['tests'][key]
                # Records store rerun and original summaries separately.
                val=d['scalar']['chi2']
            else:
                val=row(r,'c2',k,visibility='vis')['production_null']['chi2']
            vals.append(val/15)
        axes[1].plot(np.arange(7)+(j-1)*.14,vals,'o',ms=9,color=color,label=label)
    axes[1].set_xticks(range(7), [r'$\kappa$']+[rf'$\delta_{i}$' for i in range(1,7)])
    axes[1].set_ylabel(r'$\chi^2/15$ vs zero')
    axes[1].axhline(1,color=RULE,lw=1)
    axes[1].set_yticks([0, 10, 20])
    axes[1].legend(frameon=False, fontsize=25, ncol=2, loc='lower left', bbox_to_anchor=(0, 1.04), columnspacing=.8, handlelength=1.0)
    save(fig,'window')


def triangle():
    """Static backup, fixed-auto Gaussian propagation in BOTH cycles (no Knox term)."""
    d=read(HERE/'private/systematics_gc8.json')
    for cycle, variant in [('c1','lensmc|spt'),('c2','cycle2|spt2')]:
        t=d['variants'][variant]['extinction_vis']
        fig, axes=plt.subplots(13,13,figsize=(17,9))
        fig.subplots_adjust(left=.08,right=.99,bottom=.06,top=.94,hspace=.18,wspace=.12)
        for i,a in enumerate(TRACERS):
            for j,b in enumerate(TRACERS):
                ax=axes[i,j]
                pair=next((p for p in (f'{a}_{b}',f'{b}_{a}') if p in t['x']),None)
                if j>i or not pair:
                    ax.axis('off');continue
                x=np.array(t['x'][pair]);ca=np.array(t['c'][a]);cb=np.array(t['c'][b]);sa=np.array(t['s'][a]);sb=np.array(t['s'][b])
                sx=abs(x)*np.sqrt((2*sa/ca)**2 if a==b else (sa/ca)**2+(sb/cb)**2)
                ax.axhline(0,color=RULE,lw=.5)
                ax.errorbar(d['ell'],x,yerr=sx,fmt='.',ms=2,lw=.4,color='#234979')
                ax.set(xscale='log',ylim=(-1.25,1.25));ax.set_xticks([]);ax.set_yticks([])
                if j==0:ax.set_ylabel(LABELS[i],rotation=0,labelpad=20,fontsize=28)
                if i==12:ax.set_xlabel(LABELS[j],fontsize=28)
        fig.text(.08,.99,r'Extinction · $X_\ell^{ab}/\sigma_G(C_\ell^{ab})$ · fixed-template Gaussian errors',va='top',fontsize=28)
        save(fig,f'triangle_{cycle}')


def main():
    setup_font()
    heatmaps()
    rho_figures()
    leakage()
    triangle()


if __name__ == '__main__':
    main()
