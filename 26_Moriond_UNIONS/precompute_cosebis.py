"""Precompute COSEBIS B_n/sigma_n for config-space and harmonic-space paths."""
import numpy as np
import treecorr
from astropy.io import fits
import sys

sys.path.insert(0, "/automnt/n17data/cdaley/unions/pure_eb/workflow/scripts")
sys.path.insert(0, "/automnt/n17data/cdaley/unions/pure_eb/code/sp_validation")

from sp_validation.b_modes import calculate_cosebis
from cosmo_numba.B_modes.cosebis import COSEBIS

VERSION = "SP_v1.4.6.3_leak_corr"
BASE = "/n17data/cdaley/unions/pure_eb/code/sp_validation"
nmodes = 20
scale_cuts = {"fiducial": (12.0, 83.0), "full": (1.0, 250.0)}

# ── Config-space ─────────────────────────────────────────────────────
xi_path = f"{BASE}/notebooks/cosmo_val/output/{VERSION}_xi_minsep=0.5_maxsep=300.0_nbins=1000_npatch=1.txt"
cov_path = f"{BASE}/cosmo_inference/data/covariance/covariance_{VERSION}_A_g_minsep=0.5_maxsep=300.0_nbins=1000_masked/covariance_{VERSION}_A_g_minsep=0.5_maxsep=300.0_nbins=1000_masked_processed.txt"

gg = treecorr.GGCorrelation(min_sep=0.5, max_sep=300.0, nbins=1000, sep_units="arcmin")
gg.read(xi_path)

save = {}
for key, cut in scale_cuts.items():
    results = calculate_cosebis(gg, nmodes=nmodes, scale_cuts=[cut], cov_path=cov_path)
    r = results[cut]
    cov = r["cov"]
    sigma_B = np.sqrt(np.diag(cov[nmodes:, nmodes:]))
    save[f"config_Bn_{key}"] = r["Bn"]
    save[f"config_sigma_B_{key}"] = sigma_B
    print(f"Config {key}: Bn/sigma range [{(r['Bn']/sigma_B).min():.2f}, {(r['Bn']/sigma_B).max():.2f}]")

# ── Harmonic-space ───────────────────────────────────────────────────
pseudo_cl_path = f"{BASE}/notebooks/cosmo_val/output/pseudo_cl_{VERSION}_blind=A_powspace_nbins=96.fits"
pseudo_cov_path = f"{BASE}/notebooks/cosmo_val/output/pseudo_cl_cov_{VERSION}_blind=A_powspace_nbins=96.fits"

with fits.open(pseudo_cl_path) as hdul:
    data = hdul["PSEUDO_CELL"].data
    ell = np.asarray(data["ELL"], dtype=float)
    cl_bb = np.asarray(data["BB"], dtype=float)

with fits.open(pseudo_cov_path) as hdul:
    cov_bb_bb = hdul["COVAR_BB_BB"].data

n_ell = len(ell)
zeros = np.zeros(n_ell)

for key, cut in scale_cuts.items():
    cosebis_obj = COSEBIS(cut[0], cut[1], nmodes)
    _, cb_harm = cosebis_obj.cosebis_from_Cell(ell=ell, Cell_E=zeros, Cell_B=cl_bb, cache=True)

    # Build transform matrix via basis vectors
    T_B = np.zeros((nmodes, n_ell))
    for idx in range(n_ell):
        basis = np.zeros(n_ell)
        basis[idx] = 1.0
        _, cb_basis = cosebis_obj.cosebis_from_Cell(ell=ell, Cell_E=zeros, Cell_B=basis, cache=True)
        T_B[:, idx] = cb_basis

    cov_harm_B = T_B @ cov_bb_bb @ T_B.T
    sigma_harm_B = np.sqrt(np.maximum(np.diag(cov_harm_B), 0))
    sigma_harm_B = np.where(sigma_harm_B > 0, sigma_harm_B, 1.0)

    save[f"harm_Bn_{key}"] = cb_harm
    save[f"harm_sigma_B_{key}"] = sigma_harm_B
    print(f"Harmonic {key}: Bn/sigma range [{(cb_harm/sigma_harm_B).min():.2f}, {(cb_harm/sigma_harm_B).max():.2f}]")

# ── Save ─────────────────────────────────────────────────────────────
save["modes"] = np.arange(1, nmodes + 1)
out = "images/cosebis_precomputed.npz"
np.savez(out, **save)
print(f"Saved {out}")
