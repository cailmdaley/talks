"""Shared ℓ-axis styling for the SPT-summer harmonic figures.

A default matplotlib log x-axis over ℓ∈[100,3000] labels only the decade ticks
(100, 1000) — leaving the whole range where the bandpowers live unreadable.
``style_ell_axis`` sets a log axis with explicitly labelled integer ticks at
100, 200, 300, 500, 1000, 2000, 3000 plus unlabelled minor ticks for the grid, so
intermediate ℓ are legible at a glance. Imported by every harmonic figure script
(run as ``app python docs/talks/2606_SPT_summer/make_*.py``, so this file's dir is
on ``sys.path``).
"""
import numpy as np
import matplotlib.ticker as mticker

ELL_TICKS = [100, 200, 300, 500, 1000, 2000, 3000]


def style_ell_axis(ax, lo=95, hi=3050, label=None):
    """Log ℓ-axis with labelled integer ticks (the in-range subset of ELL_TICKS)."""
    ax.set_xscale("log")
    ax.set_xlim(lo, hi)
    ticks = [t for t in ELL_TICKS if lo <= t <= hi]
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.xaxis.set_major_formatter(mticker.FixedFormatter([str(t) for t in ticks]))
    ax.xaxis.set_minor_locator(mticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    if label is not None:
        ax.set_xlabel(label)
    return ax
