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

* ``sn_row`` — a horizontal, colour-matched detection-S/N row anchored in an axes
  (default bottom centre), so every figure states its per-series S/N the same way.

* ``blinding_watermark`` — a reusable background blinding stamp: a faint EB Garamond
  ``BLINDED`` centred on a blinded figure, or the loud ``PRELIMINARY — UNBLINDED``.

Survey identity is fixed deck-wide by ``SPT_COLOR`` / ``ACT_COLOR`` so SPT-3G and
ACT DR6 read as the same colour on every panel that compares them.
"""
from pathlib import Path

import numpy as np
import matplotlib.ticker as mticker
from matplotlib import font_manager as _fm
from matplotlib.offsetbox import TextArea, HPacker, AnchoredOffsetbox

ELL_TICKS = [100, 200, 500, 1000, 3000]

# Deck-wide survey identity — keep constant so people recognise "the SPT/ACT plot".
SPT_COLOR = "#c0392b"   # SPT-3G — red (same red as the profile-hardened default series)
ACT_COLOR = "#2a8c8c"   # ACT DR6 — teal, the constant "ACT colour" across the deck

# EB Garamond (the deck's display face) for the blinding watermark; bundled under
# assets/fonts/. Falls back to a generic serif if the file is ever missing.
_FONT = Path(__file__).with_name("assets") / "fonts" / "EBGaramond.ttf"
BLIND_FONT = "DejaVu Serif"
if _FONT.exists():
    try:
        _fm.fontManager.addfont(str(_FONT))
        BLIND_FONT = _fm.FontProperties(fname=str(_FONT)).get_name()
    except Exception:
        pass


def style_ell_axis(ax, lo=95, hi=3050, label=None, rotate=45):
    """Log ℓ-axis with labelled integer ticks (the in-range subset of ELL_TICKS).

    ``rotate`` tilts the x-tick labels (default 45°, right-anchored) so the labelled
    ℓ-ticks stay legible once the per-panel font is bumped up for a talk; pass
    ``rotate=0`` to keep them horizontal.
    """
    ax.set_xscale("log")
    ax.set_xlim(lo, hi)
    ticks = [t for t in ELL_TICKS if lo <= t <= hi]
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.xaxis.set_major_formatter(mticker.FixedFormatter([str(t) for t in ticks]))
    ax.xaxis.set_minor_locator(mticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    if rotate:
        for lbl in ax.get_xticklabels():
            lbl.set(rotation=rotate, ha="right", rotation_mode="anchor")
    if label is not None:
        ax.set_xlabel(label)
    return ax


def fold_yscale(ax, label, exp=None, nbins=None):
    """Fold the y-axis sci-notation offset into the axis label.

    Replaces matplotlib's ``1e-6``-style offset text (drawn above the axis) with a
    clean ``× 10^exp`` factor in the y-label and plain-mantissa tick labels. ``exp``
    defaults to the order of magnitude of the axis's current data range, so call it
    *after* plotting / setting ``ylim``. ``exp == 0`` just sets the label (no factor).
    ``nbins`` (optional) caps the number of major y-ticks via ``MaxNLocator`` — use it
    when a bumped font crowds the y-axis; ``None`` keeps matplotlib's default density.
    Returns the exponent used.
    """
    if exp is None:
        ymax = max(abs(v) for v in ax.get_ylim())
        exp = int(np.floor(np.log10(ymax))) if ymax > 0 else 0
    scale = 10.0 ** exp
    if nbins is not None:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=nbins))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _pos: f"{v / scale:.3g}"))
    ax.set_ylabel(label + (rf"  $[\times 10^{{{exp}}}]$" if exp else ""))
    return exp


def sn_row(ax, segments, *, loc="lower center", fontsize=22, sep=20, borderpad=0.6,
           weight="bold", zorder=6):
    """Horizontal, colour-matched detection-S/N row anchored in the axes (bottom centre
    by default), where there is usually clear room above the axis frame.

    ``segments`` is ``[(text, colour), …]`` or ``[(text, colour, weight), …]`` — each
    becomes one coloured token laid out left-to-right and centred as a block, so the
    per-series S/N is read off the colour (matched to the markers/legend). Reusable so
    every talk figure states detection S/N the same way.
    """
    children = [TextArea(s[0], textprops=dict(color=s[1], fontsize=fontsize,
                         weight=(s[2] if len(s) > 2 else weight)))
                for s in segments]
    box = AnchoredOffsetbox(loc=loc, frameon=False, borderpad=borderpad,
                            child=HPacker(children=children, align="center", pad=0, sep=sep))
    box.set_zorder(zorder)
    ax.add_artist(box)
    return box


def legend_right(fig, handles, labels, *, title=None, fontsize=22, title_fontsize=22,
                  axes_right=0.72, pad=0.015):
    """Legend in a FIXED right margin, so the saved canvas is the SAME size regardless
    of legend content — this is what makes side-by-side deck figures (e.g. the
    estimator / cross-survey / kappa-constraints slides) come out at identical pixel
    dimensions. The old pattern (``fig.legend(...)`` then ``savefig(bbox_inches="tight")``)
    let the tight crop grow or shrink with the longest label, so panels with a longer
    legend (e.g. "GMV profile-hardened") rendered at a different aspect ratio than a
    neighbour with shorter labels — same slide width, different height on screen.

    Call this AFTER ``fig.tight_layout()``, then ``savefig(..., dpi=...)`` WITHOUT
    ``bbox_inches="tight"`` — that combination is what keeps the canvas fixed at
    exactly ``fig.get_size_inches() * dpi``. ``axes_right`` (fraction of figure width)
    is deck-wide constant across the scripts that call this, sized to fit the longest
    legend label in the deck at ``fontsize``; keep it constant when adding a script so
    new figures stay drop-in size-matched with the existing ones.
    """
    fig.subplots_adjust(right=axes_right)
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(axes_right + pad, 0.5),
               frameon=False, fontsize=fontsize, title=title, title_fontsize=title_fontsize)


def blinding_watermark(fig, blinded, text="Blinded"):
    """Background blinding stamp for a talk figure (reusable across the deck).

    ``blinded=True`` → a large, very transparent EB Garamond word centred on the figure
    ('noticeable but not distracting'), marking the panel as read under the blind.
    ``blinded=False`` → the loud ``PRELIMINARY — UNBLINDED`` stamp (the deliberate
    ``--unblinded`` path). Drawn at ``zorder=0`` so the data always sits on top.
    """
    if blinded:
        fig.text(0.5, 0.5, text.upper(), ha="center", va="center", zorder=0,
                 fontfamily=BLIND_FONT, fontsize=170, color="0.15", alpha=0.05, rotation=16)
    else:
        fig.text(0.5, 0.5, "PRELIMINARY — UNBLINDED", ha="center", va="center", zorder=0,
                 fontsize=52, color="0.85", weight="bold", rotation=18, alpha=0.5)
