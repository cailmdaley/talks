"""Napoli: does tracer x extinction share the l-shape of CIB x extinction?

Reads results/scratch/napoli/cib_shape/cib_shape.json (made by that directory's compute.py)
and draws, per tracer family, every tracer x extinction cross divided by its best-fit
amplitude against the Lenz et al. (2019) CIB x extinction shape, with that shape in bold.

Run: app python docs/talks/2610_Napoli_CMBX/make_cib_shape.py [--rho]
--rho draws napoli_cib_rho.png from cib_rho.json: measured r(T, extinction) against the
parameter-free CIB-route prediction r(T, CIB) r(CIB, extinction), per band.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = Path(HERE).parents[2]
DEFAULT_INPUT = ROOT / 'results/scratch/napoli/cib_shape/cib_shape.json'
DEFAULT_OUTPUT = Path(HERE).parent / 'images/napoli_cib_shape.png'
ROUTE_OUTPUT = Path(HERE).parent / 'images/napoli_cib_route.png'
INK, MUTED = '#111418', '#535B67'
COBALT, TEAL, OCHRE = '#2E417C', '#1D6C78', '#9C7414'
RULE = '#C6CEDA'
W_PX, H_PX, DPI = 3840, 1900, 200
TICK, LABEL = 23, 25
TAG = '857_2.5e+20_gp20'
PIVOT = 1087.5
DETECT = 2.0   # A/sigma_A below which a bin is drawn as a dotted trace only
FAMILIES = {
    'gamma': (r'Shear $\gamma_i$ × extinction', LinearSegmentedColormap.from_list('g', ['#E8A3A0', '#7A1712'])),
    'delta': (r'Density $\delta_i$ × extinction (visibility-corrected)',
              LinearSegmentedColormap.from_list('d', ['#9FC3E6', '#14305E'])),
}


def setup_font():
    """Execute the deck's unchanged font function, not the module's science imports."""
    source = Path(HERE) / 'make_mock_recovery.py'
    tree = ast.parse(source.read_text())
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'setup_font')
    namespace = {'os': os, 'tempfile': tempfile, 'font_manager': font_manager,
                 'plt': plt, 'HERE': HERE}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
    namespace['setup_font']()


def style():
    setup_font()
    plt.rcParams['mathtext.cal'] = plt.rcParams['mathtext.rm']
    plt.rcParams.update({
        'font.size': LABEL, 'axes.labelsize': LABEL,
        'xtick.labelsize': TICK, 'ytick.labelsize': TICK,
        'axes.linewidth': 1.4, 'axes.edgecolor': MUTED,
        'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'xtick.major.size': 7, 'ytick.major.size': 7,
        'xtick.major.width': 1.4, 'ytick.major.width': 1.4,
        'axes.spines.top': False, 'axes.spines.right': False,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
    })


def amplitude(d, C, s, Cs):
    """GLS amplitude of shape s in d, with s's own covariance at that amplitude."""
    A = float(s @ np.linalg.solve(C, d) / (s @ np.linalg.solve(C, s)))
    for _ in range(20):
        Ct = C + A * A * Cs
        A = float(s @ np.linalg.solve(Ct, d) / (s @ np.linalg.solve(Ct, s)))
    return A, float(1 / np.sqrt(s @ np.linalg.solve(C + A * A * Cs, s)))


def draw(data, output, tag=TAG):
    style()
    ell = np.asarray(data['ell'])
    cib = data['cib'][tag]
    s = np.asarray(cib['cib_x_extinction']['cross'])
    Cs = np.asarray(cib['cib_x_extinction']['covariance'])
    ss = np.sqrt(np.diag(Cs))
    ip = int(np.argmin(np.abs(ell - PIVOT)))
    norm = ell[ip] * s[ip]
    dust = np.asarray(cib['extinction_auto']['cross'])
    Cd = np.asarray(cib['extinction_auto']['covariance'])
    Ad, _ = amplitude(dust, Cd, s, Cs)       # dust shape scaled onto CIB x ext
    fits = cib['shape_fits']

    fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
    lefts = [.075, .545]
    width, top_y, top_h, bot_y, bot_h = .345, .475, .375, .225, .2
    for col, (fam, (title, cmap)) in enumerate(FAMILIES.items()):
        top = fig.add_axes([lefts[col], top_y, width, top_h])
        bot = fig.add_axes([lefts[col], bot_y, width, bot_h], sharex=top)
        bnorm = BoundaryNorm(np.arange(.5, 7.5), cmap.N)
        offsets = np.linspace(-.035, .035, 6)
        ticklabels = []
        for i in range(6):
            name = f'{fam}{i+1}'
            d = np.asarray(data['tracers'][name]['cross'])
            C = np.asarray(data['tracers'][name]['covariance'])
            f = fits[name]['cib_x_extinction']
            A, sA = f['A'], f['sigma_A']
            ticklabels.append(f'{i+1}:  {A / sA:+.1f}' + r'$\sigma$')
            color = cmap(bnorm(i + 1))
            x = ell * 10 ** offsets[i]
            y = ell * d / A / norm
            e = ell * np.sqrt(np.diag(C)) / abs(A) / norm
            if A / sA < DETECT:
                # Amplitude not detected: dividing by A is meaningless, so draw it as a trace only.
                top.plot(x, y, color=color, lw=1.4, ls=':', alpha=.55, zorder=1)
                continue
            top.fill_between(x, y - e, y + e, color=color, alpha=.13, lw=0, zorder=1)
            top.plot(x, y, color=color, lw=2.2, alpha=.85, zorder=2, marker='o', ms=5)
            r = d / (A * s)
            re = np.sqrt(np.diag(C)) / abs(A * s)
            bot.errorbar(x, r, yerr=re, color=color, fmt='o', ms=6, lw=1.4, alpha=.85, capsize=0, zorder=2)
        # Bold: CIB x extinction itself, and the dust (extinction auto) shape for reference.
        top.fill_between(ell, ell * (s - ss) / norm, ell * (s + ss) / norm, color=INK, alpha=.18, lw=0, zorder=3)
        top.plot(ell, ell * s / norm, color=INK, lw=4, zorder=4, marker='o', ms=7)
        top.plot(ell, ell * Ad * dust / norm, color=OCHRE, lw=2.6, ls='--', zorder=4)
        bot.axhline(1, color=INK, lw=3, zorder=3)
        bot.fill_between(ell, 1 - ss / np.abs(s), 1 + ss / np.abs(s), color=INK, alpha=.15, lw=0, zorder=1)
        bot.plot(ell, Ad * dust / s, color=OCHRE, lw=2.6, ls='--', zorder=4)
        top.axhline(0, color=MUTED, lw=1)
        bot.axhline(0, color=MUTED, lw=1)
        top.set_xscale('log')
        top.set_xlim(95, 3200)
        top.set_ylim(-2.5, 6.5)
        bot.set_ylim(-2.5, 4.5)
        bot.set_xticks([100, 300, 1000, 3000], ['100', '300', '1000', '3000'])
        bot.xaxis.set_minor_formatter(NullFormatter())
        plt.setp(top.get_xticklabels(), visible=False)
        bot.set_xlabel(r'Multipole $\ell$', labelpad=6)
        if col == 0:
            top.set_ylabel(r'$\ell C_\ell\,/\,A$  (normalised)', labelpad=8)
            bot.set_ylabel(r'$C_\ell\,/\,(A\,C_\ell^{\mathrm{CIB}\times\mathrm{ext}})$', labelpad=8)
        top.set_title(title, loc='left', fontsize=LABEL, color=INK, pad=12)
        sm = ScalarMappable(norm=bnorm, cmap=cmap)
        cb = fig.colorbar(sm, ax=top, fraction=.04, pad=.01, ticks=range(1, 7))
        cb.set_ticklabels(ticklabels)
        cb.set_label(r'bin: $A/\sigma_A$', fontsize=TICK)
        cb.ax.tick_params(labelsize=TICK)
        cb.outline.set_visible(False)
    handles = [Line2D([], [], color=INK, lw=4, marker='o', ms=7,
                      label=r'CIB × extinction (Lenz+19, 857 GHz, $N_\mathrm{HI}<2.5\times10^{20}$)'),
               Line2D([], [], color=OCHRE, lw=2.6, ls='--', label='Extinction auto (dust shape), scaled')]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.07, .995), ncol=2, frameon=False,
               fontsize=LABEL, handlelength=2.2, columnspacing=1.6)
    fig.text(.075, .055,
             r'Each tracer cross ÷ its best-fit amplitude $A$ against the bold shape (15 bands, full Gaussian covariance); '
             r'bold ÷ its $\ell C_\ell$ at $\ell\approx1090$.',
             fontsize=TICK, color=MUTED, ha='left', va='bottom')
    fig.text(.075, .012,
             r'Dotted: $A/\sigma_A<2$, too noisy to normalise (omitted below). Bands, bars: $1\sigma$. '
             r'TR1 LensMC × SPT-3G masks.',
             fontsize=TICK, color=MUTED, ha='left', va='bottom')
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=DPI)
    plt.close(fig)
    print('wrote', output, W_PX, H_PX)


def draw_route(data, output, tag=TAG):
    """B per bin: tracer x extinction against epsilon_l x (tracer x CIB)."""
    style()
    route = data['cib'][tag]['cib_route']
    fig = plt.figure(figsize=(W_PX / DPI, 1500 / DPI), dpi=DPI)
    ax = fig.add_axes([.085, .25, .62, .6])
    ax.axhline(1, color=INK, lw=3, zorder=1)
    ax.axhline(0, color=MUTED, lw=1, zorder=1)
    for k, (fam, (title, cmap)) in enumerate(FAMILIES.items()):
        bnorm = BoundaryNorm(np.arange(.5, 7.5), cmap.N)
        for i in range(6):
            r = route[f'{fam}{i+1}']
            x = k * 7 + i
            color = cmap(bnorm(i + 1))
            ax.errorbar(x, r['B'], yerr=r['sigma_B'], fmt='o', ms=13, color=color, mec='white', mew=1,
                        elinewidth=2.6, capsize=0, zorder=3)
            if fam == 'delta':
                ax.errorbar(x + .3, r['B_uncorrected_delta'], yerr=r['sigma_B_uncorrected_delta'], fmt='o',
                            ms=11, mfc='white', mec=color, mew=2.2, color=color, elinewidth=1.8, capsize=0, zorder=3)
    ax.set_xticks([*range(6), *range(7, 13)],
                  [*[rf'$\gamma_{i}$' for i in range(1, 7)], *[rf'$\delta_{i}$' for i in range(1, 7)]])
    ax.set_xlim(-.7, 13)
    ax.set_ylim(-.6, 3.2)
    ax.set_ylabel(r'$B$', labelpad=8)
    handles = [Line2D([], [], color=MUTED, marker='o', ls='', ms=13, label=r'$\gamma$; $\delta$ visibility-corrected'),
               Line2D([], [], color=MUTED, marker='o', ls='', ms=11, mfc='white', mew=2.2,
                      label=r'$\delta$ coverage-only (no visibility correction)')]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.2), ncol=2, frameon=False,
              fontsize=LABEL, handletextpad=.3, columnspacing=1.5)
    eps = data['cib'][tag]['epsilon']
    fig.text(.735, .84, r'$C^{\,T\times\mathrm{ext}}_\ell = B\;\epsilon_\ell\;C^{\,T\times\mathrm{CIB}}_\ell$',
             fontsize=LABEL + 4, color=INK, va='top')
    fig.text(.735, .70,
             r'$\epsilon_\ell = C^{\mathrm{CIB}\times\mathrm{ext}}_\ell / C^{\mathrm{CIB}\times\mathrm{CIB}}_\ell$' '\n'
             r'(odd × even halves; no noise bias)' '\n\n'
             r'$B=1$: the CIB in the extinction' '\n' r'map carries the whole cross.' '\n'
             r'$B$ fitted over 15 bands;' '\n' r'bars $1\sigma$, conservative.',
             fontsize=TICK, color=MUTED, va='top', linespacing=1.35)
    fig.text(.085, .04, r'Lenz+19 CIB 857 GHz, $N_\mathrm{HI}<2.5\times10^{20}$; same TR1 masks and 15 bands as the template nulls.',
             fontsize=TICK, color=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=DPI)
    plt.close(fig)
    print('wrote', output)


RHO_INPUT = ROOT / 'results/scratch/napoli/cib_shape/cib_rho.json'
RHO_OUTPUT = Path(HERE).parent / 'images/napoli_cib_rho.png'
# Rows read low z -> high z: density (visibility-corrected) on top, shear below.
RHO_PANELS = [('delta1_vis', r'$\delta_1$'), ('delta5_vis', r'$\delta_5$'), ('delta6', r'$\delta_6$'),
              ('gamma1', r'$\gamma_1$'), ('gamma5', r'$\gamma_5$'), ('gamma6', r'$\gamma_6$')]


def draw_rho(data, output, slide=False):
    """slide=True: 2x the 1712x771 slide body, type sized for >= 32 px on screen, footnotes left to the slide notes."""
    style()
    if slide:
        plt.rcParams.update({'font.size': 30, 'axes.labelsize': 30, 'xtick.labelsize': 28, 'ytick.labelsize': 28})
    tick_fs, label_fs = (28, 30) if slide else (TICK, LABEL)
    ell = np.asarray(data['ell'])
    w_px, h_px = (3424, 1542) if slide else (W_PX, 2000)
    fig = plt.figure(figsize=(w_px / DPI, h_px / DPI), dpi=DPI)
    gcol = FAMILIES['gamma'][1](.85)
    dcol = FAMILIES['delta'][1](.85)
    x0, y0, w, h, gx, gy = (.06, .15, .29, .31, .027, .08) if slide else (.075, .215, .285, .3, .025, .075)
    axes = []
    for k, (key, label) in enumerate(RHO_PANELS):
        row, col = divmod(k, 3)
        ax = fig.add_axes([x0 + col * (w + gx), y0 + (1 - row) * (h + gy), w, h],
                          sharey=axes[0] if axes else None, sharex=axes[0] if axes else None)
        axes.append(ax)
        ax.axhline(0, color=MUTED, lw=1)
        series = ([('delta6_raw', '#B07A2A', 'before', -.025), ('delta6_vis', dcol, 'after', .025)]
                  if key == 'delta6' else [(key, gcol if key.startswith('gamma') else dcol, None, 0)])
        for name, color, tag, off in series:
            b = data['bins'][name]
            p, sp = np.asarray(b['r_predicted']), np.asarray(b['sigma_predicted'])
            m, sm = np.asarray(b['r_measured']), np.asarray(b['sigma_measured'])
            ax.fill_between(ell, p - sp, p + sp, color=color, alpha=.22, lw=0, step=None, zorder=1)
            ax.plot(ell, p, color=color, lw=2, alpha=.9, zorder=2)
            ax.errorbar(ell * 10 ** off, m, yerr=sm, fmt='o', ms=8, color=color, mec='white', mew=.8,
                        elinewidth=1.8, capsize=0, zorder=3)
        ax.set_title(label, loc='left', fontsize=label_fs + 2, color=INK, pad=6)
        if key == 'delta6':
            ax.text(*((.2, .99, 'unweighted') if slide else (.98, .97, 'before visibility weighting')), transform=ax.transAxes, ha='left' if slide else 'right', va='top',
                    fontsize=tick_fs, color='#B07A2A')
            ax.text(*((.2, .84, 'visibility-weighted') if slide else (.98, .85, 'after visibility weighting')), transform=ax.transAxes, ha='left' if slide else 'right', va='top',
                    fontsize=tick_fs, color=dcol)
        ax.set_xscale('log')
        ax.set_xlim(95, 3200)
        ax.set_xticks(*(([100, 300, 1000], ['100', '300', '1000']) if slide else
                        ([100, 300, 1000, 3000], ['100', '300', '1000', '3000'])))
        ax.xaxis.set_minor_formatter(NullFormatter())
        if row == 1:
            ax.set_xlabel(r'Multipole $\ell$', labelpad=6)
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
        if col == 0:
            ax.set_ylabel(r'$r_\ell$', labelpad=8)
        else:
            plt.setp(ax.get_yticklabels(), visible=False)
    axes[0].set_ylim(-.12, .42 if slide else .32)
    handles = [Line2D([], [], color=MUTED, marker='o', ls='', ms=9,
                      label=r'measured $r(\mathrm{tracer},\mathrm{ext})$' if slide else r'measured $r(T,\mathrm{ext})$'),
               plt.Rectangle((0, 0), 1, 1, color=MUTED, alpha=.35,
                             label=(r'via the CIB: $r(\mathrm{tracer},\mathrm{CIB})\,r(\mathrm{CIB},\mathrm{ext})$'
                                    if slide else
                                    r'predicted contribution from CIB × extinction, $r(T,\mathrm{CIB})\,r(\mathrm{CIB},\mathrm{ext})$'))]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.065 if slide else .07, 1.0 if slide else .995), ncol=2, frameon=False,
               fontsize=label_fs, handletextpad=.4, columnspacing=1.6)
    if not slide:
      fig.text(.075, .065,
             r'$r(a,b)=C^{ab}/\sqrt{C^{aa}C^{bb}}$, no free parameter. Tracer, extinction autos: total observed power; '
             r'CIB auto: odd × even halves.', fontsize=tick_fs, color=MUTED)
    if not slide:
      fig.text(.075, .018,
             r'Lenz+19 CIB 857 GHz, $N_\mathrm{HI}<2.5\times10^{20}$; $\delta$ visibility-weighted unless marked. '
             r'Bars and bands: $1\sigma$.', fontsize=tick_fs, color=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=DPI)
    plt.close(fig)
    print('wrote', output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--tag', default=TAG)
    parser.add_argument('--rho', action='store_true', help='draw the correlation-coefficient figure only')
    parser.add_argument('--rho-output', type=Path, default=RHO_OUTPUT)
    parser.add_argument('--slide', action='store_true', help='with --rho: the slide-sized version, napoli_cib_rho_slide.png')
    parser.add_argument('--route-output', type=Path, default=ROUTE_OUTPUT,
                        help='second figure: amplitude through the CIB route (empty string to skip)')
    args = parser.parse_args()
    if args.rho:
        out = args.rho_output.with_name('napoli_cib_rho_slide.png') if args.slide else args.rho_output
        draw_rho(json.loads(RHO_INPUT.read_text()), out, slide=args.slide)
        return
    parser_data = json.loads(args.input.read_text())
    draw(parser_data, args.output, args.tag)
    if args.route_output:
        draw_route(parser_data, args.route_output, args.tag)


if __name__ == '__main__':
    main()
