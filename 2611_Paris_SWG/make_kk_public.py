"""Published CMB-lensing bandpowers for the kappa-kappa blinding slide: Fig. "clkk_main" of the SPT-3G D1
lensing paper (Omori, Wu et al., arXiv:2608.31136), which shows SPT-3G D1 (GMV, PP, MUSE) with Planck PR4
and ACT DR6. The paper's own figure is rendered from its PDF; nothing is redrawn.

    python make_kk_public.py        (needs pdftocairo on PATH)
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "papers", "2608.31136_omori_spt3g_d1_lensing", "work", "reference",
                   "source", "Figures", "fig_mainbandpowers.pdf")
OUT = os.path.join(HERE, "..", "images", "paris26_spt3g_d1_lensing_bandpowers")

if __name__ == "__main__":
    subprocess.run(["pdftocairo", "-png", "-r", "400", "-singlefile", SRC, OUT], check=True)
    print(OUT + ".png")
