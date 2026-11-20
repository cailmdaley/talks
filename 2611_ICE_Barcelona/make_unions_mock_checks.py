"""UNIONS v2 mock checks, drawn at slide size from unions_mock_checks.json.

1. images/unions_bmode_mocks.png: the C_ell^BB additive-template amplitude of the blinded v2
   tomographic data vector (first bins) against 69 sampled GLASS mocks matched to it.
2. images/unions_leakage_xisys.png: the relative error of xi_sys+ propagated from (alpha, beta, eta)
   fitted on 58 realizations with known injected PSF leakage, standard least squares against the
   errors-in-variables fits.

The JSON holds the numbers as the analyses wrote them (sources inside it).

Run: uv run --with numpy --with scipy --with matplotlib --with fonttools --with brotli \
       python 2611_ICE_Barcelona/make_unions_mock_checks.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
plt = style.plt

INK, MUTED, RULE = '#1B1611', '#685D4B', '#C5B89E'
ACCENT, TEAL = '#B03E32', '#33746B'
OUT = HERE.parent / 'images'


def rc():
    style.setup_font()
    plt.rcParams.update({'font.size': 30, 'axes.labelsize': 32, 'xtick.labelsize': 29, 'ytick.labelsize': 29,
                         'axes.linewidth': 2.4, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.size': 12,
                         'ytick.major.size': 12, 'xtick.major.width': 2.4, 'ytick.major.width': 2.4,
                         'xtick.minor.size': 6, 'xtick.minor.width': 1.6,
                         'axes.spines.top': False, 'axes.spines.right': False})


def bmode(d):
    fig = plt.figure(figsize=(2000 / 200, 1500 / 200), dpi=200)
    ax = fig.add_axes([0.06, 0.21, 0.9, 0.75])
    mocks = np.array(d['mocks'])
    ax.hist(mocks, bins=np.arange(-0.5, 1.01, 0.1), color=RULE, edgecolor='white', linewidth=2)
    ax.axvline(d['data'], color=ACCENT, lw=5)
    ax.axvline(0, color=MUTED, lw=1.6, ls=':')
    ax.text(d['data'] - 0.03, 13.6, 'blinded\nv2 data', color=ACCENT, ha='right', va='top', fontsize=32)
    ax.text(-0.47, 13.6, f'{len(mocks)} GLASS\nmocks', color=MUTED, ha='left', va='top', fontsize=32)
    ax.set_xlim(-0.5, 1.0); ax.set_ylim(0, 14)
    ax.set_yticks([]); ax.set_xticks([-0.5, 0, 0.5, 1.0])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel(r'additive $C_\ell^{BB}$ template amplitude')
    out = OUT / 'unions_bmode_mocks.png'
    fig.savefig(out, dpi=200); plt.close(fig)
    print('wrote', out)


def leakage(d):
    fig = plt.figure(figsize=(2000 / 200, 1500 / 200), dpi=200)
    ax = fig.add_axes([0.17, 0.21, 0.79, 0.75])
    th = np.array(d['theta_arcmin'], float)
    ax.axhline(0, color=MUTED, lw=1.6, ls=':')
    for name, v in d['arms'].items():
        lsq = name.startswith('lsq')
        ax.plot(th, 100 * np.array(v), color=ACCENT if lsq else TEAL, lw=5 if lsq else 3,
                marker='o', ms=13 if lsq else 9, alpha=1 if lsq else 0.85)
    ax.text(2.2, -19, 'standard least squares', color=ACCENT, fontsize=32, va='bottom')
    ax.text(2.2, 10.5, 'errors in variables (three variants)', color=TEAL, fontsize=32, va='bottom')
    ax.set_xscale('log')
    ax.set_xticks([1, 10, 100]); ax.set_xticklabels(['1', '10', '100'])
    ax.set_xlim(0.8, 300); ax.set_ylim(-40, 15)
    ax.set_xlabel(r'$\theta$ [arcmin]')
    ax.set_ylabel(r'error in $\xi_{\rm sys}$ [%]')
    out = OUT / 'unions_leakage_xisys.png'
    fig.savefig(out, dpi=200); plt.close(fig)
    print('wrote', out)


def main():
    rc()
    d = json.loads((HERE / 'unions_mock_checks.json').read_text())
    bmode(d['bmode_template'])
    leakage(d['leakage_xi_sys'])


if __name__ == '__main__':
    main()
