"""Published CMB-lensing power spectra side by side, for the kappa-kappa blinding slide:
ACT DR6 (Qu et al., arXiv:2304.05202, Fig. 1) and SPT-3G 2019/20 MUSE (Ge et al., arXiv:2411.06000,
the phi-phi panels of the spectra figure). The papers' own figures are rendered from their PDFs
(papers/<id>/work/reference/figures) and pasted on one white canvas; nothing is redrawn.

    pdftocairo -png -r 300 -singlefile <pdf> $TMPDIR/kk/{act,spt}     (the script does this)
Run in the cmbx container: app python make_kk_public.py
"""
import os
import subprocess
import tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS = os.path.join(HERE, "..", "..", "..", "papers")
SRC = {"act": "2304.05202_act_dr6_lensing_power/work/reference/figures/fig1paper.pdf",
       "spt": "2411.06000_ge_spt3g_lensing/work/reference/figures/muse_spectra_bestfit_w_sidelobe_marged_def2.pdf"}
tmp = os.environ.get("KK_RENDERS") or tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
im = {}
for k, pdf in SRC.items():
    png = os.path.join(tmp, k)
    if not os.path.exists(png + ".png"):
        subprocess.run(["pdftocairo", "-png", "-r", "300", "-singlefile", os.path.join(PAPERS, pdf), png], check=True)
    im[k] = Image.open(png + ".png").convert("RGB")
spt = im["spt"].crop((0, 0, int(0.492 * im["spt"].width), im["spt"].height))   # the phi-phi column
h = im["act"].height
spt = spt.resize((round(spt.width * h / spt.height), h), Image.LANCZOS)
gap = 260
out = Image.new("RGB", (im["act"].width + gap + spt.width, h), "white")
out.paste(im["act"], (0, 0))
out.paste(spt, (im["act"].width + gap, 0))
out.save(os.path.join(HERE, "..", "images", "paris26_public_lensing_spectra.png"))
print(out.size)
