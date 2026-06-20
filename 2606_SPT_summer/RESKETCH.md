# 2606_SPT_summer — deck re-sketch (Cail, 2026-06-20)

A **10-minute** talk → **~10 slides max, ≤1 slide of background**. Reframed from a
detection-result deck to a **status report** on the Euclid MoU CMB-lensing ×
cross-correlation project (Cail Daley + Margherita Lembo). Audience knows CMB
lensing × Euclid cold — **do not motivate why**; report status. Way less text than
the current deck — one transferable message per slide, figures carry the weight.

The "robust detection / amplitude" arc is **dropped for now** (blinded, in progress).

## New arc

1. **Title.**
2. **Overview (one slide).** "A status report on the Euclid MoU CMB-lensing ×
   cross-correlation project, led by Cail Daley & Margherita Lembo." Quick talk
   overview. **Timeline bullets** (Cail narrates): Euclid cosmology products now
   scheduled **June 2027** [CONFIRM the prior/delayed date — dictation was unclear].
   **Outline**: footprints & field definitions · blinding · data vectors ·
   likelihood & bias plans · systematics · simulations.
3. **Footprints & field definitions.** The maps — the 3-fragment reveal
   (Euclid TR1→DR1 → +SPT-3G main → +ACT DR6), already built. DONE.
4. **Blinding.** What our blinding strategy is. Brief; comes right after the maps.
   Figure: `spt26_selfblind_shift.png`.
5. **Data vectors — all three crosses.** Show only the crosses, but **all three**:
   δ×γ (galaxy–galaxy lensing), δ×κ, γ×κ. One plot with all the data vectors.
   (`spt26_cross_spectra.png` currently shows the two κ-crosses; the δ×γ third
   cross may need a new plot — flag TBD.)
6. **Estimator consistency.** The three crosses (single bin, or all bins combined —
   doesn't matter) showing **consistency across estimators**. Figure:
   `spt26_estimator_comparison.png` (SPT GMV vs profile-hardened).
7. **SPT vs ACT.** Two angles: (a) data points over-plotted on theory; (b) a
   **relative error-bar comparison** — plot the size of the error bars for SPT and
   ACT for our bins (best as: overplot theory, show error-bar sizes for both).
   Figure: `spt26_cross_survey.png` for (a); the error-bar comparison is likely a
   **new plot** — flag TBD.
8. **Likelihood & bias plans.** What's being done for the likelihood and bias
   parameters. Mostly **undefined** — a forward-looking sketch slide (bullets).
9. **Systematics** (cross-correlations). One slide. Figure TBD (extinction work
   exists under `results/.../systematics/`, not yet a deck figure).
10. **Simulations.** GLASS mocks. Figure: `spt26_glass_recovery.png`.
11. **Summary / next steps / thanks.** Brief.

## Claim discipline still binds

The wording rules in `CLAUDE.md` (this dir) remain in force for any number that
appears: amplitude conventions, "estimator-robust not foreground-clean-safe," the
family-split caveat. When the detection arc is dropped, those numbers mostly leave
the deck — but if any return, the discipline holds.
