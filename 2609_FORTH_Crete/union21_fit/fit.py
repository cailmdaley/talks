# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "astropy"]
# ///
import numpy as np
from scipy.optimize import minimize_scalar
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u
import json

data_path = "data/SCPUnion2.1_mu_vs_z.txt"
sys_path = "data/SCPUnion2.1_covmat_sys.txt"
nosys_path = "data/SCPUnion2.1_covmat_nosys.txt"

names, z, mu, mu_err, p_lowmass = [], [], [], [], []
with open(data_path) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        names.append(parts[0])
        z.append(float(parts[1]))
        mu.append(float(parts[2]))
        mu_err.append(float(parts[3]))
        p_lowmass.append(float(parts[4]))

z = np.array(z)
mu = np.array(mu)
mu_err = np.array(mu_err)
n = len(z)
print(f"N supernovae: {n}")

H0 = 70.0  # km/s/Mpc, per file header calibration

def model_mu(omega_lambda, z):
    cosmo = FlatLambdaCDM(H0=H0, Om0=1 - omega_lambda)
    return cosmo.distmod(z).value

def chi2_diag(omega_lambda):
    resid = mu - model_mu(omega_lambda, z)
    return np.sum((resid / mu_err) ** 2)

def load_cov(path, n):
    vals = np.loadtxt(path)
    return vals.reshape(n, n)

cov_nosys = load_cov(nosys_path, n)
cov_sys = load_cov(sys_path, n)

# sanity: check nosys diagonal matches mu_err^2
diag_nosys = np.sqrt(np.diag(cov_nosys))
match = np.allclose(diag_nosys, mu_err, rtol=1e-3)
print(f"nosys diagonal sqrt matches mu_err column: {match}, max rel diff = {np.max(np.abs(diag_nosys - mu_err) / mu_err):.2e}")

def chi2_cov(omega_lambda, cov_inv):
    resid = mu - model_mu(omega_lambda, z)
    return resid @ cov_inv @ resid

cov_nosys_inv = np.linalg.inv(cov_nosys)
cov_sys_inv = np.linalg.inv(cov_sys)

def fit(chi2_func):
    res = minimize_scalar(chi2_func, bounds=(0.01, 0.99), method="bounded",
                           options={"xatol": 1e-8})
    om_l_best = res.x
    chi2_min = res.fun
    # error from delta chi2 = 1
    delta = 1e-4
    d2 = (chi2_func(om_l_best + delta) - 2 * chi2_func(om_l_best) + chi2_func(om_l_best - delta)) / delta**2
    sigma = np.sqrt(2.0 / d2)
    return om_l_best, sigma, chi2_min

om_diag, sig_diag, chi2_diag_min = fit(chi2_diag)
om_nosys, sig_nosys, chi2_nosys_min = fit(lambda x: chi2_cov(x, cov_nosys_inv))
om_sys, sig_sys, chi2_sys_min = fit(lambda x: chi2_cov(x, cov_sys_inv))

dof = n - 1

results = {
    "n_sne": n,
    "H0_fixed": H0,
    "diagonal": {"omega_lambda": om_diag, "sigma": sig_diag, "chi2": chi2_diag_min, "dof": dof, "chi2_per_dof": chi2_diag_min / dof},
    "nosys_cov": {"omega_lambda": om_nosys, "sigma": sig_nosys, "chi2": chi2_nosys_min, "dof": dof, "chi2_per_dof": chi2_nosys_min / dof},
    "sys_cov": {"omega_lambda": om_sys, "sigma": sig_sys, "chi2": chi2_sys_min, "dof": dof, "chi2_per_dof": chi2_sys_min / dof},
}

print(json.dumps(results, indent=2))

with open("results/fit.json", "w") as f:
    json.dump(results, f, indent=2)

# save best fit for plotting (use sys_cov as the reported "best" fit for the figure curve? use nosys stat-only for main line, but let's export both)
np.savez("results/fit_arrays.npz", om_diag=om_diag, om_nosys=om_nosys, om_sys=om_sys,
          sig_diag=sig_diag, sig_nosys=sig_nosys, sig_sys=sig_sys, H0=H0)
