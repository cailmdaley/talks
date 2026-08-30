# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""1D analogue of Nagura+ 2026: does the NKA's off-diagonal error dominate the
projected real-space covariance?

Toy: real Gaussian field on a periodic 1D box, length L=1, NX samples.
Mask w(x). Pseudo-spectrum estimator  Chat_k = |atilde_k|^2,  atilde_k = sum_q W_{k-q} a_q.

Exact Gaussian covariance (both Wick pairings, the 1D analogue of the two
Wigner-3j terms in the pseudo-Cl covariance):
    Cov(k,k') = |S1(k,k')|^2 + |S2(k,k')|^2
    S1(k,k') = sum_q W_{k-q} W*_{k'-q} C_q          (<atilde_k atilde_k'^*>)
    S2(k,k') = sum_q W_{k-q} W_{k'+q} C_q           (<atilde_k atilde_k'>)
NKA: pull C out at kbar=(k+k')/2, leaving the transform of the mask *product*:
    S1_NKA = C_kbar * Xi1(k-k'),  S2_NKA = C_kbar * Xi2(k+k')
Both normalised by <w^2>^2 so that full sky gives Cov = C_k^2 delta_kk'.

Real-space analogue of the Legendre projection (cosine kernels):
    xi(theta) = sum_{k>0} P_k(theta) Chat_k,   P_k(theta) = 2 cos(2 pi k theta / L)
    Cov(xi,xi') = P Cov P^T
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent
NX = 2048                       # real-space samples
KMAX = 200                      # modes used in the estimator / projection
K = np.arange(1, KMAX + 1)      # k > 0
Q = np.fft.fftshift(np.fft.fftfreq(NX, d=1.0 / NX)).astype(int)   # -NX/2 .. NX/2-1


def C_of_k(k):
    """Smooth falling spectrum, no features — geometry is the only thing under test."""
    k = np.abs(np.asarray(k, dtype=float))
    return (1.0 + k / 8.0) ** -1.8


def mask_tophat(frac, nhole=1, taper=0.004, seed=7):
    """`nhole` cosine-tapered top-hats with total covered fraction `frac`.

    For nhole > 1 the patch widths and the gaps between them are randomised
    (fixed seed, so the mask is reproducible). Equally-spaced equal-width patches
    make the mask a periodic comb, whose transform is a comb of delta-like spikes
    and whose covariance reads as periodic stripes rather than a band — an artefact
    of the regularity, not of disjointness. Real disjoint footprints (HSC-Y3's six
    fields) are irregular, and give a broad kernel with modest sidelobes.
    """
    x = np.arange(NX) / NX
    w = np.zeros(NX)
    if nhole == 1:
        widths, gaps = np.array([frac]), np.array([1.0 - frac])
    else:
        rng = np.random.default_rng(seed)
        widths = rng.uniform(0.45, 1.55, nhole)
        widths *= frac / widths.sum()
        gaps = rng.uniform(0.45, 1.55, nhole)
        gaps *= (1.0 - frac) / gaps.sum()
    edge = 0.5 * gaps[0]
    for i in range(len(widths)):
        c = edge + widths[i] / 2
        d = np.abs(((x - c + 0.5) % 1.0) - 0.5)
        half = widths[i] / 2
        w += np.clip((half + taper - d) / (2 * taper), 0, 1)
        edge += widths[i] + (gaps[(i + 1) % len(gaps)] if i + 1 < len(widths) else 0)
    return np.clip(w, 0, 1)


def W_of(w):
    """W_m for m in Q (m = 0 at centre), plus a lookup that returns 0 outside the band."""
    Wfull = np.fft.fftshift(np.fft.fft(w)) / NX     # index i <-> mode Q[i]
    lut = np.zeros(4 * NX, dtype=complex)           # offset lookup, index m + 2*NX
    lut[Q + 2 * NX] = Wfull
    return Wfull, lut


def coupled_spectrum(w):
    """<Chat_k> = sum_q (|W_{k-q}|^2 + W_{k-q}W_{k+q}...) C_q — the 1D pseudo-spectrum,
    normalised by <w^2> so it reduces to C_k on the full sky. iNKA uses this in place
    of the true C_k inside the kernel sum."""
    Wfull, lut = W_of(w)
    Cq = C_of_k(Q)
    A = lut[(K[:, None] - Q[None, :]) + 2 * NX]
    norm = np.sum(np.abs(Wfull) ** 2)
    return (np.abs(A) ** 2 @ Cq) / norm


def covariances(w, inka=False):
    """Return exact and (i)NKA Cov(k,k') for k,k' in K.

    NKA  : C evaluated at kbar = (k+k')/2, pulled out of the kernel sum.
    iNKA : same, but with the *coupled* spectrum <Chat>/<w^2> in place of C — the
           García-García+ improvement that makes the harmonic diagonal accurate."""
    Wfull, lut = W_of(w)
    Cq = C_of_k(Q)
    norm = (np.sum(np.abs(Wfull) ** 2)) ** 2        # = <w^2>^2

    A = lut[(K[:, None] - Q[None, :]) + 2 * NX]     # A[k,q] = W_{k-q}
    B = lut[(K[:, None] + Q[None, :]) + 2 * NX]     # B[k,q] = W_{k+q}

    S1 = (A * Cq) @ A.conj().T
    S2 = (A * Cq) @ B.T
    exact = (np.abs(S1) ** 2 + np.abs(S2) ** 2) / norm

    # NKA: C pulled out at kbar, the remaining sums are the mask-product kernels
    Xi1 = A @ A.conj().T                            # = sum_q W_{k-q} W*_{k'-q}
    Xi2 = A @ B.T                                   # = sum_q W_{k-q} W_{k'+q}
    if inka:
        Ck = coupled_spectrum(w)                 # on the integer grid K
        kbar = np.interp((K[:, None] + K[None, :]) / 2.0, K, Ck)
    else:
        kbar = C_of_k((K[:, None] + K[None, :]) / 2.0)
    nka = (np.abs(kbar * Xi1) ** 2 + np.abs(kbar * Xi2) ** 2) / norm
    return exact, nka


def kernel_width(w, keep=0.5):
    """Effective coupling width: the full width of the smallest symmetric window in
    |W_m|^2 holding `keep` of the total kernel power, in modes.

    Half-maximum is useless for an irregular disjoint mask — the kernel is a narrow
    spike on a broad skirt, so FWHM reports 1 while modes tens apart are still
    strongly coupled. Power containment measures how far a mode actually talks.
    """
    Wfull, _ = W_of(w)
    p = np.abs(Wfull) ** 2
    c = p[np.argsort(np.abs(Q), kind="stable")].cumsum()
    n = int(np.searchsorted(c, keep * p.sum()))
    return max(n, 1)


THETA = np.logspace(np.log10(2e-3), np.log10(0.25), 48)   # in units of L


def project(cov):
    P = 2 * np.cos(2 * np.pi * K[None, :] * THETA[:, None])
    return P @ cov @ P.T


def bandpower_diag(cov, width):
    """Diagonal of the covariance of bandpower-averaged Chat, bins of `width` modes."""
    nb = len(K) // width
    out = np.empty(nb)
    for b in range(nb):
        s = slice(b * width, (b + 1) * width)
        out[b] = cov[s, s].sum() / width ** 2
    return out


def frac(a, b):
    return a / b - 1.0


def sig_mask(xe, thresh=0.20):
    """theta values where the exact xi-covariance is above `thresh` x its peak.
    Outside this the fractional error is a small-denominator artefact."""
    return np.abs(xe) > thresh * np.abs(xe).max()


def xi_metrics(ex, nk):
    """Error at the smallest theta, and the worst error over the theta range where
    the exact xi-covariance is still >20% of its peak. Beyond that the exact
    covariance passes through zero (real, for a disjoint mask) and the ratio
    diverges for reasons that have nothing to do with the NKA."""
    xe, xn = np.diag(project(ex)), np.diag(project(nk))
    m = sig_mask(xe)
    f = frac(xn, xe)
    return f[0], f[m][np.argmax(np.abs(f[m]))], f, xe, m


# ----------------------------------------------------------------- experiments
def fig_baseline(frac_cov=0.20, nhole=1, tag="f20"):
    w = mask_tophat(frac_cov, nhole)
    ex, nk = covariances(w)
    _, ink = covariances(w, inka=True)
    kw = kernel_width(w)
    dh = frac(np.diag(nk), np.diag(ex))
    dhi = frac(np.diag(ink), np.diag(ex))
    dxi_i = frac(np.diag(project(ink)), np.diag(project(ex)))
    bw = max(int(round(kw)), 1)
    db = frac(bandpower_diag(nk, bw), bandpower_diag(ex, bw))
    xe, xn = project(ex), project(nk)
    dx = frac(np.diag(xn), np.diag(xe))
    x0, xw, _, xed, msk = xi_metrics(ex, nk)

    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    ax[0].axhline(0, c="0.7", lw=1); ax[0].plot(K, 100 * dh, c="C3", label="NKA")
    ax[0].plot(K, 100 * dhi, c="C2", label="iNKA"); ax[0].legend(fontsize=8)
    ax[0].set(xlabel="k", ylabel="NKA error [%]",
              title=f"harmonic diagonal (kernel width {kw} modes)")
    kb = (np.arange(len(db)) + 0.5) * bw
    ax[1].axhline(0, c="0.7", lw=1); ax[1].plot(kb, 100 * db, c="C0")
    ax[1].set(xlabel="band centre k", title=f"bandpower diagonal (width {bw})")
    ax[2].axhline(0, c="0.7", lw=1)
    ax[2].semilogx(THETA, 100 * dx, c="0.75", lw=1)
    ax[2].semilogx(THETA[msk], 100 * dx[msk], c="C1", lw=2, label="NKA")
    ax[2].semilogx(THETA, 100 * dxi_i, c="C2", lw=1, alpha=.3)
    ax[2].semilogx(THETA[msk], 100 * dxi_i[msk], c="C2", lw=2, label="iNKA")
    ax[2].legend(fontsize=8)
    ax[2].set_ylim(min(-15, 100 * dx[msk].min() - 5), max(15, 100 * dx[msk].max() + 5))
    ax[2].set(xlabel=r"$\theta / L$", title=r"projected $\mathrm{Cov}(\xi,\xi)$ diagonal")
    for a in ax: a.grid(alpha=.25)
    fig.suptitle(f"footprint {frac_cov:.0%}, {nhole} patch(es)", y=1.02)
    fig.tight_layout(); fig.savefig(OUT / f"fig1_baseline_{tag}.png", dpi=140,
                                    bbox_inches="tight")
    plt.close(fig)
    return dict(kw=kw, harm=dh, band=db, xi=dx, xiworst=xw)


def fig_sweep(nhole=1, tag="1patch"):
    fracs = np.array([0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.9])
    rows = []
    for f in fracs:
        w = mask_tophat(f, nhole)
        ex, nk = covariances(w)
        kw = kernel_width(w)
        bw = max(int(round(kw)), 1)
        x0, xw, _, _, _ = xi_metrics(ex, nk)
        rows.append((f, kw,
                     np.median(frac(np.diag(nk), np.diag(ex))),
                     np.median(frac(bandpower_diag(nk, bw), bandpower_diag(ex, bw))),
                     x0, xw))
    r = np.array(rows)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.axhline(0, c="0.7", lw=1)
    ax.plot(r[:, 0], 100 * r[:, 2], "o-", label="harmonic diagonal")
    ax.plot(r[:, 0], 100 * r[:, 3], "s-", label="bandpower diagonal")
    ax.plot(r[:, 0], 100 * r[:, 4], "^-", label=r"$\xi$ diagonal, smallest $\theta$")
    ax.plot(r[:, 0], 100 * r[:, 5], "v-", label=r"$\xi$ diagonal, worst (significant $\theta$)")
    ax.set(xlabel="footprint fraction", ylabel="NKA error [%]",
           title=f"{nhole} patch(es)"); ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(OUT / f"fig2_sweep_{tag}.png", dpi=140)
    plt.close(fig)
    return r


def fig_truncation(frac_cov=0.20, nhole=1, tag="f20", inka=True):
    """Keep (i)NKA only within |k-k'| <= n; outside use exact (A) or zero (B)."""
    w = mask_tophat(frac_cov, nhole)
    ex, nk = covariances(w, inka=inka)
    kw = kernel_width(w)
    xe = np.diag(project(ex))
    msk = sig_mask(xe)
    d = np.abs(K[:, None] - K[None, :])
    ns = np.arange(0, 61, 2)
    A, B = [], []
    for n in ns:
        m = d <= n
        A.append(frac(np.diag(project(np.where(m, nk, ex))), xe))
        B.append(frac(np.diag(project(np.where(m, nk, 0.0))), xe))
    A, B = np.array(A), np.array(B)
    full = frac(np.diag(project(nk)), xe)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    lbl = "iNKA" if inka else "NKA"
    for a, M, t in ((ax[0], A, f"{lbl} inside band, exact outside"),
                    (ax[1], B, f"{lbl} inside band, zero outside")):
        a.axhline(0, c="0.7", lw=1)
        a.plot(ns, 100 * M[:, 0], "o-", label=r"smallest $\theta$")
        a.plot(ns, 100 * np.abs(M[:, msk]).max(1), "v-",
               label=r"worst (significant $\theta$)")
        a.axhline(100 * full[0], ls="--", c="C0", lw=1)
        a.axhline(100 * np.abs(full[msk]).max(), ls="--", c="C1", lw=1)
        a.axvline(kw, c="0.4", ls=":", label=f"kernel width = {kw}")
        a.set(xlabel="bands retained  n  (|k−k'| ≤ n)", title=t); a.grid(alpha=.25)
        a.legend(fontsize=8)
    ax[0].set_ylabel(r"error on $\mathrm{Cov}(\xi,\xi)$ diagonal [%]")
    fig.suptitle(f"footprint {frac_cov:.0%}, {nhole} patch(es), "
                 f"{'iNKA' if inka else 'NKA'}; dashed = untruncated")
    fig.tight_layout(); fig.savefig(OUT / f"fig3_truncation_{tag}.png", dpi=140)
    plt.close(fig)
    return ns, A, B, full, kw, msk


def fig_holes(frac_cov=0.20):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    res = {}
    for nh, c in zip((1, 3, 6), ("C0", "C1", "C3")):
        w = mask_tophat(frac_cov, nh)
        ex, nk = covariances(w)
        kw = kernel_width(w)
        ax[0].axhline(0, c="0.9", lw=1)
        ax[0].plot(K, 100 * frac(np.diag(nk), np.diag(ex)), c=c,
                   label=f"{nh} patch(es), width {kw}")

        x0, xw, f, xe, m = xi_metrics(ex, nk)
        ax[1].semilogx(THETA, 100 * f, c=c, lw=1, alpha=.25)
        ax[1].semilogx(THETA[m], 100 * f[m], c=c, lw=2)
        res[nh] = (kw, np.median(frac(np.diag(nk), np.diag(ex))), x0, xw)
    for a, t, xl in ((ax[0], "harmonic diagonal", "k"),
                     (ax[1], r"projected $\xi$ diagonal", r"$\theta/L$")):
        a.axhline(0, c="0.7", lw=1); a.set(title=t, xlabel=xl,
                                           ylabel="NKA error [%]"); a.grid(alpha=.25)
    ax[1].set_ylim(-40, 120)
    ax[0].set_ylim(-70, 60)
    ax[0].legend(fontsize=8)
    fig.suptitle(f"same total area ({frac_cov:.0%}), split into disjoint patches")
    fig.tight_layout(); fig.savefig(OUT / "fig4_holes.png", dpi=140)
    plt.close(fig)
    return res


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True)
    b = fig_baseline(0.20, 1, "f20")
    fig_baseline(0.20, 6, "f20_6patch")
    print(f"[f=20%, 1 patch] kernel width {b['kw']} modes")
    print(f"  harmonic diag  median {100*np.median(b['harm']):+.1f}%   "
          f"k<20 {100*np.median(b['harm'][:20]):+.1f}%  k>100 {100*np.median(b['harm'][100:]):+.1f}%")
    print(f"  bandpower diag median {100*np.median(b['band']):+.1f}%")
    print(f"  xi diag  theta_min {100*b['xi'][0]:+.1f}%   "
          f"worst over significant theta {100*b['xiworst']:+.1f}%")

    print("\n[sweep, 1 patch]  f, FWHM, harm, band, xi_small, xi_large")
    print(fig_sweep(1, "1patch"))
    print("\n[sweep, 6 patches]")
    print(fig_sweep(6, "6patch"))

    fig_truncation(0.20, 6, "f20_6patch_nka", inka=False)
    ns, A, B, full, kw, msk = fig_truncation(0.20, 6, "f20_6patch")
    print(f"\n[truncation, f=20%, 6 patches] kernel width {kw}")
    print("  n :  A(th_min, worst)  B(th_min, worst)   [%]")
    for i, n in enumerate(ns):
        if n % 8 == 0:
            print(f"  {n:3d}: {100*A[i,0]:+7.2f} {100*np.abs(A[i,msk]).max():+7.2f}  "
                  f"{100*B[i,0]:+7.2f} {100*np.abs(B[i,msk]).max():+7.2f}")
    print(f"  full NKA: {100*full[0]:+.2f}  {100*np.abs(full[msk]).max():+.2f}")

    print("\n[holes, f=20%]")
    for nh, (kwid, hm, x0, xw) in fig_holes(0.20).items():
        print(f"  {nh} patch(es): width {kwid:3d}  harm median {100*hm:+6.2f}%  "
              f"xi(theta_min) {100*x0:+6.2f}%  xi worst {100*xw:+7.2f}%")
