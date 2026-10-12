"""Frames for Davide Luchina's FLASK slides (contributions deck, 12 Oct), redrawn only in layout.

His figures are carried unchanged at native resolution.  The spectra figures get a header
strip with his own label ("ACT-constrained", "Planck-like (unconstrained)") in the deck's
face, so one figure slide can step from one to the other.  The kappa-kappa block figures are
padded with white to the aspect of the full-covariance figures, so each pair can share a
frame in a figure stack.

Outputs (images/): napoli_kp23_flask_spectra_{act,planck}_lab.png,
napoli_kp23_flask_cov_kk_{act,planck}_pad.png.  Run: app python make_flask_frames.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
sys.path.insert(0, HERE)
from make_mock_recovery import setup_font  # noqa: E402  the deck's face

INK = "#111418"


def labelled(src, out, label):
    im = np.asarray(Image.open(os.path.join(IMG, src)).convert("RGB"))
    h, w = im.shape[:2]
    strip = int(0.09 * h)
    dpi = 200
    fig = plt.figure(figsize=(w / dpi, (h + strip) / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, h / (h + strip)])
    ax.imshow(im, interpolation="none")
    ax.axis("off")
    fig.text(0.5, 1 - 0.5 * strip / (h + strip), label, ha="center", va="center", color=INK,
             fontsize=strip / dpi * 72 * 0.62)
    fig.savefig(os.path.join(IMG, out), dpi=dpi, facecolor="white")
    plt.close(fig)
    print("wrote", out)


def padded(src, ref, out):
    im = Image.open(os.path.join(IMG, src)).convert("RGB")
    W, H = Image.open(os.path.join(IMG, ref)).size
    s = min(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im
    canvas = Image.new("RGB", (W, H), "white")
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    canvas.save(os.path.join(IMG, out))
    print("wrote", out)


if __name__ == "__main__":
    setup_font()
    labelled("napoli_kp23_flask_spectra_act.jpg", "napoli_kp23_flask_spectra_act_lab.png", "ACT-constrained")
    labelled("napoli_kp23_flask_spectra_planck.jpg", "napoli_kp23_flask_spectra_planck_lab.png",
             "Planck-like (unconstrained)")
    for k in ("act", "planck"):
        padded(f"napoli_kp23_flask_cov_kk_{k}.jpg", f"napoli_kp23_flask_cov_{k}.jpg",
               f"napoli_kp23_flask_cov_kk_{k}_pad.png")
