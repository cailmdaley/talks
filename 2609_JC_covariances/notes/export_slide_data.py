# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Precompute everything the deck's slides 4 and 5 animate, as JSON."""
import json, base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
from projection_experiment import (
    mask_tophat, covariances, kernel_width, project, THETA, K, W_of, Q, frac,
)

OUT = "/Users/cd280747/Documents/projects/talks/2609_JC_covariances/nka_data.html"
FRAC, NPATCH = 0.20, 6
NS = list(range(0, 61, 2))
KM = 96                      # matrix shown: k = K[0] .. K[KM-1]


def kernel_profile(w, npts=161):
    """|W_m|^2 normalised to peak 1, for m = -80..80."""
    Wfull, _ = W_of(w)
    p = np.abs(Wfull) ** 2
    m = np.arange(-(npts // 2), npts // 2 + 1)
    idx = np.searchsorted(Q, m)
    v = p[idx]
    return (v / v.max()).round(4).tolist()


def corr(cov):
    d = np.sqrt(np.diag(cov))
    return cov / np.outer(d, d)


data = {}

# ---------------- slide 4: truncation sweep, HSC-like mask ----------------
w = mask_tophat(FRAC, NPATCH)
ex, ink = covariances(w), covariances(w, inka=True)[1]
ex = ex[0] if isinstance(ex, tuple) else ex
kw = int(kernel_width(w))

xe = np.diag(project(ex))
sig = np.abs(xe) > 0.20 * np.abs(xe).max()
th = THETA[sig]

d = np.abs(K[:, None] - K[None, :])
ratios = []
for n in NS:
    m = d <= n
    xn = np.diag(project(np.where(m, ink, ex)))
    ratios.append((xn / xe)[sig].round(4).tolist())

# iNKA correlation matrix, quantised to uint8 for compact transport
C = corr(ink)[:KM, :KM]
img = np.clip(C / C.max(), 0, 1)
data["slide4"] = dict(
    frac=FRAC, npatch=NPATCH, fwhm=kw, ns=NS, km=KM,
    theta=th.round(5).tolist(),
    ratios=ratios,
    err_thmin=[round(float(r[0] - 1), 5) for r in ratios],
    matrix=base64.b64encode((img * 255).astype(np.uint8).tobytes()).decode(),
)

# ---------------- slide 5: same area, split into patches ----------------
s5 = []
for nh in (1, 3, 6):
    w = mask_tophat(FRAC, nh)
    exn, inkn = covariances(w)[0], covariances(w, inka=True)[1]
    xen = np.diag(project(exn))
    sg = np.abs(xen) > 0.20 * np.abs(xen).max()
    s5.append(dict(
        npatch=nh, fwhm=int(kernel_width(w)),
        mask=w[::8].round(3).tolist(),
        kernel=kernel_profile(w),
        theta=THETA[sg].round(5).tolist(),
        ratio=(np.diag(project(inkn)) / xen)[sg].round(4).tolist(),
    ))
data["slide5"] = dict(frac=FRAC, cases=s5)

with open(OUT, "w") as fh:
    fh.write("<script>window.NKA_DATA=")
    json.dump(data, fh, separators=(",", ":"))
    fh.write(";</script>\n")
print("wrote", OUT)
print("  slide4: width", kw, "ns", len(NS), "theta", len(th),
      "err_thmin[0]=%.4f full=%.4f" % (data["slide4"]["err_thmin"][0],
                                       data["slide4"]["err_thmin"][-1]))
for c in s5:
    print(f"  slide5 npatch={c['npatch']} width={c['fwhm']} "
          f"ratio[0]={c['ratio'][0]:.3f} npts={len(c['theta'])}")
