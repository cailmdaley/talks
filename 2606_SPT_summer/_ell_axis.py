"""Shared figure styling for the SPT-summer harmonic figures.

Two helpers, imported by every figure script (run as
``app python docs/talks/2606_SPT_summer/make_*.py``, so this file's dir is on
``sys.path``):

* ``style_ell_axis`` — a log ℓ-axis with a small set of *labelled* integer ticks
  (100, 200, 500, 1000, 3000) plus unlabelled minor ticks. A default matplotlib
  log axis labels only the decades (100, 1000), leaving the range where the
  bandpowers live unreadable; a denser labelled set (…300…2000…) overlaps on a
  talk-sized panel — five well-spaced labels read cleanly. The seaborn ``ticks``
  style draws the tick *marks* themselves.

* ``fold_yscale`` — folds matplotlib's ``1e-6``-style y-axis offset text into the
  axis label as a ``× 10^n`` factor, with plain-mantissa tick labels, so the scale
  reads in the label (``ℓ Cℓ  [× 10⁻⁶]``) rather than floating above the panel.
"""
import numpy as np
import matplotlib.ticker as mticker

ELL_TICKS = [100, 200, 500, 1000, 3000]


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


def fold_yscale(ax, label, exp=None):
    """Fold the y-axis sci-notation offset into the axis label.

    Replaces matplotlib's ``1e-6``-style offset text (drawn above the axis) with a
    clean ``× 10^exp`` factor in the y-label and plain-mantissa tick labels. ``exp``
    defaults to the order of magnitude of the axis's current data range, so call it
    *after* plotting / setting ``ylim``. ``exp == 0`` just sets the label (no factor).
    Returns the exponent used.
    """
    if exp is None:
        ymax = max(abs(v) for v in ax.get_ylim())
        exp = int(np.floor(np.log10(ymax))) if ymax > 0 else 0
    scale = 10.0 ** exp
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _pos: f"{v / scale:.3g}"))
    ax.set_ylabel(label + (rf"  $[\times 10^{{{exp}}}]$" if exp else ""))
    return exp
