# 26_JC_H0_sirens — CosmoStat Journal Club

**Two papers, ~25 min:**
1. Santiago de Matos+ 2025 — arXiv:2512.15380 — "Peak Sirens" (GW × galaxies, first detection)
2. Coulon+ 2026 — arXiv:2601.04774 — GW × DES 3×2pt (adds weak lensing)

Companion methods paper for Peak Sirens: Ferri+ 2025 (arXiv:2412.00202).

---

## One-line thesis

Standard sirens don't need hosts. Cross-correlate the GW density field with LSS tracers — galaxies (paper 1), or galaxies+shear (paper 2) — and H₀ is the distance–redshift conversion that makes them line up.

## Deck state (13 slides, rendered)

1. Title
2. Waveform → $d_L$ (Schutz equation + chirp logic)
3. **Siren H₀ landscape** — table of best H₀ per channel + where today's two papers fit
4. Bright sirens (GW170817 + DECam panel, Holz)
5. Dark sirens / catalog method (GW170814 localization over DES, Holz)
6. **Spectral sirens** — $z$ from BBH mass function, detector-frame mass = (1+z) source, no catalog needed
7. Cross-correlation sirens — Ferri shell cartoon + $C_\ell^{gb}(z, d_L)$ cosmology-dependence panel
8. Paper 1 detection — Peak Sirens 5.9σ cross-power in $(z, d_L)$ plane
9. **GW bias** $b_\text{gw}$ — definition, orthogonality to $H_0$, first obs constraint <4.3
10. Paper 1 H₀ posterior — MCMC corner with GW170817 bright-siren boost
11. Paper 2 (Andrade-Oliveira) approach — spectral + DES 3×2pt + GW170817+jet, posterior-level combination. **Not cross-correlation.**
12. Paper 2 result — $H_0 = 67.9^{+4.4}_{-4.3}$, (H₀, Ωₘ) 2D contour + H₀ posterior
13. Takeaway — three complementary channels, both papers are methodology inflection points

## Original narrative beats (reference)

1. **Bright sirens** — GW170817 cartoon. Waveform → d_L, host → z. One event, then tiny sample.
2. **Dark sirens** — galaxy-catalog / `gwcosmo` approach. Per-event marginalization over candidate hosts in the localization volume. Dominant systematic: catalog incompleteness.
3. **Cross-correlation sirens** — don't ID hosts at all. Place GW events in a 3D map at assumed H₀, cross-correlate with galaxy field. If H₀ is wrong, shells don't overlap → no signal. (Ferri drawing_v2 cartoon — galaxy shell at z, BBH shell at d_L, three Hubble diagrams.)
    - Key equation on slide: $C_\ell^{gb}(z, d_L; H_0, \Omega_m)$ peaks when $d_L(z; H_0, \Omega_m)$ matches truth.
4. **GW bias** — new concept worth its own slide. BBHs form in galaxies, but which ones? Massive hosts? Old pops? b_gw parameterizes how BBHs trace matter vs galaxies: $\delta_{\rm gw} = b_{\rm gw}\, \delta_m$. Orthogonal to H₀ at linear order → can be co-fit. Peak Sirens gives the *first observational constraint*: b_gw < 4.3 (95% CI).
5. **Paper 1 result: first detection** — Peak Sirens cl_data figure: measured C_ℓ^{gb} from GWTC-3 × GLADE+, 5.9σ cross-correlation peak. Their key plot.
6. **Paper 1 result: H₀ + b_gw posterior** — MCMC chains (peaksirens_mcmc.pdf). H₀ = 67⁺¹⁸₋₁₅. Wide, but this is 90 events.
7. **Paper 2 (Andrade-Oliveira+, UZH) — different beast!** Not a cross-correlation. Three ingredients combined **at the posterior level**:
    - **Spectral sirens** from GWTC-4.0: per-event $z$ from the BBH mass function (detector-frame feature at $(1+z)m_s$).
    - **DES Y3 3×2pt** posterior on $(H_0, \Omega_m)$: standard photometric cosmology, independent of GW.
    - **GW170817** bright siren with jet-inclination prior from superluminal motion (boosts precision substantially — without jet info, error goes 6.4% → 9.9%).
8. **Paper 2 result** — h0_omm_2d_6_leg_nodes 2D contour (H₀ vs Ωₘ), and H₀ posterior. $H_0 = 67.9^{+4.4}_{-4.3}$ (6.4%), Ωₘ improved 22%. 142 CBCs from GWTC-4.0 + DES Y3 3×2pt + GW170817.
9. **Takeaway** — cross-correlation is a third path alongside bright/catalog-dark. Robust to incompleteness, gets tighter when paired with matter tracers. Both papers deliver in same 3 months → this is a methodology inflection point.
10. **(optional backup)** Forecast from Ferri methods: 1% H₀ with ET+CE.

## Figures I'm likely to steal

| slide | file | source |
|---|---|---|
| 1 bright | holz_bright_panel.png | Holz KICC slide, p10 |
| 2 dark | holz_dark_panel.png | Holz KICC slide, p10 |
| 3 x-corr cartoon | ferri_gwgal_shells_cartoon.pdf | Ferri+2412.00202 Fig 1 left |
| 3 x-corr cosmo-dep | ferri_clgb_cosmodep.pdf | Ferri+2412.00202 Fig 1 right |
| 5 detection | peaksirens_cl_data.pdf | Santiago de Matos+2512.15380 |
| 6 H₀+b_gw | peaksirens_mcmc.pdf | Santiago de Matos+2512.15380 |
| 8 H₀ vs Ωₘ | wlgw_h0_omm.pdf | Coulon+2601.04774 |
| 8 H₀ posterior | wlgw_h0.pdf | Coulon+2601.04774 |

## Open questions / things to check while reading

- Paper 1: what prior on b_gw? Is H₀ detection significance independent of the b_gw prior?
- Paper 2: they're using GWTC-4.0 — same event sample as paper 1 (GWTC-3.0) or bigger?
- Paper 2: does the 3×2pt prior on Ωₘ effectively *drive* the H₀ tightening, or is the GW×κ cross-correlation adding real info?
- Is peak-shape / BAO-like standard-ruler flavor actually exploited in paper 1, or just the amplitude of the cross-power?
- How does this compare to GW×photo-z catalog (DES Y6 × GWTC-4.0 — the Miller+2602.04766 paper already in my bib)?
