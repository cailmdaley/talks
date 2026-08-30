# Does the (i)NKA's off-diagonal error dominate the projected real-space covariance?

A 1D numerical test of the diagnosis in Nagura, Terasawa, Terawaki & Takada 2026
(arXiv:2605.16186). Their claim: iNKA is built to be right on the *diagonal* of
Cov(C̃_ℓ, C̃_ℓ′) — good to 10% — but the Legendre projection into ξ(θ) is a double sum
that eats the off-diagonal structure, where iNKA's errors live, giving a 25–30%
underestimate of the Cov(ξ,ξ) diagonal. Section 5 of the brief flags that they never
*demonstrate* this: Fig. 4's ratio panel divides by a noisy sample covariance, and the
obvious clean test — keep only the first *N* off-diagonal bands and project — is not done.

This note runs that test in a toy where the exact answer is computable.

**Answer: the diagnosis holds, and sharply.** With iNKA's off-diagonals replaced by the
exact ones, the projected error falls from **−18.6% to −0.6%**. Restoring them band by
band brings most of it back by the time *N* reaches the mode-coupling kernel width. The
diagonal is innocent; the error lives in the off-diagonal bands, and mostly inside the
kernel.

Everything below is from `projection_experiment.py` in this directory (`uv run` it; ~20 s).

---

## 1. The toy

Real Gaussian field on a periodic 1D box of length L, NX = 2048 samples, mask w(x),
pseudo-spectrum estimator Ĉ_k = |ã_k|², ã_k = Σ_q W_{k−q} a_q. Modes k = 1…200.
Input spectrum C_k = (1 + k/8)^−1.8 — smooth, featureless, so geometry is the only
thing under test.

**Exact Gaussian covariance**, both Wick pairings (the 1D analogue of the two Wigner-3j
terms in the pseudo-Cℓ covariance):

    Cov(k,k') = |S1(k,k')|² + |S2(k,k')|²,  normalised by <w²>²
    S1 = Σ_q W_{k−q} W*_{k'−q} C_q          ( <ã_k ã*_k'> )
    S2 = Σ_q W_{k−q} W_{k'+q} C_q           ( <ã_k ã_k'>  )

Every sum is a matrix product, so "exact" is cheap here — that is the whole point of
working in 1D. Full sky reduces it to Cov = C_k² δ_kk′, as it must.

**NKA**: pull C out of the sum at k̄ = (k+k′)/2, leaving the transform of the mask
*product*: S1 → C_k̄ Ξ1(k−k′), S2 → C_k̄ Ξ2(k+k′).

**iNKA**: same, but with the *coupled* spectrum ⟨Ĉ⟩/⟨w²⟩ in place of C_k̄ — the
García-García+ improvement that exists specifically to fix the harmonic diagonal.

**Projection**, the 1D analogue of the Legendre transform (cosine kernels):

    ξ(θ) = Σ_{k>0} P_k(θ) Ĉ_k,  P_k(θ) = 2 cos(2πkθ/L)
    Cov(ξ,ξ') = P Cov Pᵀ

**Masks**: `nhole` disjoint cosine-tapered top-hats summing to a chosen area fraction.
One patch = a compact survey; six patches = the HSC-Y3 situation. For more than one
patch the widths and gaps are **randomised** (fixed seed): equally-spaced equal-width
patches make the mask a periodic comb, whose transform is a comb of spikes and whose
covariance reads as periodic stripes rather than a band — an artefact of the regularity,
not of disjointness. Real disjoint footprints are irregular.

**Kernel width** is quoted as the full width of the smallest symmetric window in |W_m|²
holding half the kernel power. Half-maximum is useless for an irregular disjoint mask —
the kernel is a narrow spike on a broad skirt, so FWHM reports 1 while modes tens apart
are still strongly coupled.

**A caveat on the error metric.** For a disjoint mask the exact Cov(ξ,ξ) diagonal
passes through near-zero at intermediate θ, where a fractional error diverges for
reasons that have nothing to do with the NKA. All quoted "worst" numbers are restricted
to θ where the exact covariance is above 20% of its peak; the plots show the excluded
region faded. My first pass at this reported +212% errors that were entirely this
artefact.

---

## 2. iNKA fixes the harmonic diagonal and does not fix ξ

`fig1_baseline_f20.png` (1 patch), `fig1_baseline_f20_6patch.png` (6 patches).

Fractional error on the covariance, footprint area 20%:

| mask | kernel width | harmonic diag, NKA | harmonic diag, iNKA | ξ diag at θ_min, NKA | ξ diag at θ_min, iNKA |
|---|---|---|---|---|---|
| 1 patch  |  2 |  −1.9% | −0.0% |  −6.9% |  −7.6% |
| 3 patches |  7 |  −5.3% | −0.0% | −10.3% | −14.4% |
| 6 patches | 15 |  −9.9% | −0.0% | −12.5% | −18.6% |

iNKA's harmonic diagonal is exact here — **too** exact: in this toy the coupled spectrum
*is* precisely what enters the diagonal, so iNKA nails it by construction where the real
thing manages 10%. That makes the toy a clean, if flattering, version of the paper's
setup. And it makes the point unmistakable: **a covariance that is exactly right on the
harmonic diagonal is still 8–19% low on the real-space diagonal, and iNKA is *worse*
than plain NKA on ξ in almost every configuration tested.** Harmonic diagonal accuracy
carries no information about real space. That is Nagura's moral, reproduced.

Bandpower binning does not rescue it either (`fig1_*`, middle panel): binning at the
kernel width changes the harmonic diagonal error from −9.9% to −8.4% for the 6-patch
mask. The error is coherent, not noise, so averaging does nothing to it.

## 3. The truncation test — where the error lives

`fig3_truncation_f20_6patch.png` (iNKA), `..._nka.png` (plain NKA). Footprint 20%,
6 patches, kernel width 15 modes. Keep (i)NKA only within |k−k′| ≤ n and fill the rest
with the exact covariance (left panel) or with zero (right panel), then project.

iNKA, error on the Cov(ξ,ξ) diagonal at the smallest θ:

| n | 0 | 8 | 16 | 24 | 32 | 48 | full |
|---|---|---|---|---|---|---|---|
| iNKA inside, **exact** outside | −0.6% | −10.4% | −14.5% | −15.7% | −16.9% | −18.1% | −18.6% |
| iNKA inside, **zero** outside | −80.9% | −43.6% | −23.8% | −19.6% | −19.0% | −18.7% | −18.6% |

Two things fall out.

**The error is in the off-diagonals, and it is made inside the kernel width.** Give
iNKA the exact off-diagonals and its −18.6% real-space error collapses to −0.6%.
Restoring iNKA's own off-diagonals band by band recovers ~78% of the full error by
n ≈ 16 and ~84% by n ≈ 24, against a kernel width of 15; the remaining ~15% accumulates
slowly out to n ≈ 48, so the cutoff is soft rather than sharp. The zero-filled variant
converges harder — it is within 1 point of the full value by n = 24 and flat after.
This is the measurement the brief's question 1 asks for, and the answer is the one the
paper asserts without showing: the damage is done by off-diagonal bands, the bulk of it
within the coupling kernel.

**The off-diagonals also carry most of the signal.** Zeroing them entirely costs 81% of
the ξ covariance amplitude. So the projection is not "eating" a small correction — the
off-diagonal band *is* the real-space covariance, which is why an approximation tuned on
the diagonal has no purchase on it.

## 4. Geometry is the driver — HSC's disjointness, not iNKA as such

`fig4_holes.png`, `fig2_sweep_1patch.png`, `fig2_sweep_6patch.png`.

Same total area (20%), split into more patches — the perimeter-to-area lever that the
brief's question 2 says the paper cannot address:

| patches | kernel width | harmonic diag (NKA) | ξ at θ_min (NKA) | ξ at θ_min (iNKA) |
|---|---|---|---|---|
| 1 |  2 |  −1.9% |  −6.9% |  −7.6% |
| 3 |  7 |  −5.3% | −10.3% | −14.4% |
| 6 | 15 |  −9.9% | −12.5% | −18.6% |

Splitting one patch into six at fixed area widens the kernel ~7× and takes the iNKA
real-space error from −7.6% (a level nobody would write a paper about) to −18.6%. The
footprint sweep says the same thing: for a contiguous mask above ~25% area the error is
a couple of percent at most, while the 6-patch mask is still at −5.3% (NKA) with half
the sky covered.

So the honest reading is that **Nagura's headline is a statement about HSC-Y3's geometry
at least as much as about iNKA.** For a contiguous Rubin-like footprint this toy says
the effect largely goes away. That is question 2, answered in the direction the paper
could not.

## 5. What I got wrong going in

The hypothesis I was handed — iNKA stays decent near the diagonal while the *exact*
band's wings pull away, an asymmetry between the two matrices — is not what happens.
Both matrices have a band of the same width; iNKA's is wrong *throughout* the band, with
no asymmetry between diagonal and wings once you look at the projected quantity. The
real asymmetry is different and more interesting: **iNKA is right where it was fitted
(the harmonic diagonal) and wrong everywhere the fit did not reach**, and real space
happens to weight exactly the part it did not reach.

## 6. Limits of the toy

1D, not 2D — cosine kernels, not Legendre; no spin-2, so no E/B leakage and none of the
EE–BB cross-covariance that the paper's appendix finds is load-bearing. No shape noise,
so this is the sample-variance term only. Gaussian by construction. iNKA's harmonic
diagonal is exact here rather than 10%-accurate, which flatters the setup. And the
disjoint-mask ξ covariance crosses zero, so intermediate-θ ratios are fragile (§1).
None of these seem likely to reverse the truncation result, which is the load-bearing
one, but they mean the *numbers* here are illustrative and the paper's are the ones to
quote.
