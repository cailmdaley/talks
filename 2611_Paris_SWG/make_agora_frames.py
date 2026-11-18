# /// script
# dependencies = ["pymupdf"]
# ///
"""Two frames on one 16:9 white canvas for the Agora slide, so they stack: Fig. 1 of the Agora paper
(Omori 2022, arXiv:2212.07420) and Fig. 6 of Ouellette et al. (arXiv:2606.26223). The papers' own PDFs
are placed unchanged, as large as fits.

    uv run make_agora_frames.py
"""
import os
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS = os.path.join(HERE, "..", "..", "..", "papers")
SRC = {"paris26_agora_1_maps": "2212.07420_omori_agora/work/reference/source/agora_maps.pdf",
       "paris26_agora_2_bias": "2606.26223_ouellette_spt3g_d1_des_y3/work/reference/source/figures/agora_cross_cl_noiseless_bpw_tests.pdf"}
W, H = 1600, 760   # the figure cell's shape

for name, pdf in SRC.items():
    src = pymupdf.open(os.path.join(PAPERS, pdf))
    r = src[0].rect
    k = min(W / r.width, H / r.height)
    w, h = r.width * k, r.height * k
    doc = pymupdf.open()
    page = doc.new_page(width=W, height=H)
    page.show_pdf_page(pymupdf.Rect((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2), src, 0)
    page.get_pixmap(dpi=180, alpha=False).save(os.path.join(HERE, "..", "images", name + ".jpg"), jpg_quality=90)
    print(name, round(r.width), round(r.height))
