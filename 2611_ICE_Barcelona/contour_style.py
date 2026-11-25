"""The deck's type and axes for posterior figures, and the shared contour module (pando, data-visualization practice)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path.home() / 'pando/.felt/practices/data-visualization/plot-scripts'))
from contours import Chain, joint  # noqa: E402,F401

spec = importlib.util.spec_from_file_location('chains_style', HERE.parent / '2610_KP23_Napoli/make_chains.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
style.setup_font()
style.plt.rcParams.update({
    'font.size': 28, 'axes.labelsize': 30, 'xtick.labelsize': 27, 'ytick.labelsize': 27, 'axes.linewidth': 2.4,
    'axes.edgecolor': style.MUTED, 'axes.labelcolor': style.INK, 'xtick.color': style.MUTED,
    'ytick.color': style.MUTED, 'xtick.major.size': 12, 'ytick.major.size': 12, 'xtick.major.width': 2.4,
    'ytick.major.width': 2.4, 'axes.spines.top': False, 'axes.spines.right': False})
IMAGES = HERE.parent / 'images'
D = {'Omega_m': r'$\Delta\Omega_\mathrm{m}$', 'S8': r'$\Delta S_8$'}


def save(fig, name):
    out = IMAGES / name
    fig.savefig(out); style.plt.close(fig)
    print('wrote', out)
