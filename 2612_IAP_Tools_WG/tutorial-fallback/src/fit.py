import argparse
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

C_KM_S = 299792.458
H0 = 70.0  # km/s/Mpc, matching Union2.1 header M(h=0.7)


def distmod_flat_lcdm(omega_lambda: float, z: np.ndarray) -> np.ndarray:
    omega_m = 1.0 - omega_lambda
    dl_mpc = np.empty_like(z, dtype=float)
    for i, zi in enumerate(z):
        val, _ = quad(lambda zp: 1.0 / np.sqrt(omega_m * (1.0 + zp) ** 3 + omega_lambda), 0.0, zi)
        dl_mpc[i] = (C_KM_S / H0) * (1.0 + zi) * val
    return 5.0 * np.log10(dl_mpc) + 25.0


def load_union21(path: str):
    z, mu, mu_err = [], [], []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            z.append(float(parts[1]))
            mu.append(float(parts[2]))
            mu_err.append(float(parts[3]))
    return np.array(z), np.array(mu), np.array(mu_err)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--cov-nosys", required=True)
    ap.add_argument("--cov-sys", required=True)
    ap.add_argument("--covariance", choices=["stat_only", "full"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    z, mu, mu_err = load_union21(args.data)
    n = len(z)
    cov_path = args.cov_nosys if args.covariance == "stat_only" else args.cov_sys
    cov = np.loadtxt(cov_path).reshape(n, n)
    cov_inv = np.linalg.inv(cov)

    def chi2(om_l: float) -> float:
        r = mu - distmod_flat_lcdm(om_l, z)
        return float(r @ cov_inv @ r)

    res = minimize_scalar(chi2, bounds=(0.01, 0.99), method="bounded", options={"xatol": 1e-8})
    om_best = float(res.x)
    chi2_min = float(res.fun)
    delta = 1e-4
    d2 = (chi2(om_best + delta) - 2.0 * chi2(om_best) + chi2(om_best - delta)) / delta**2
    sigma = float(np.sqrt(2.0 / d2))

    # Also check diagonal match against mu_err for diagnostic clarity
    diag_nosys = np.sqrt(np.diag(np.loadtxt(args.cov_nosys).reshape(n, n)))
    max_diag_rel_diff = float(np.max(np.abs(diag_nosys - mu_err) / mu_err))

    out = {
        "n_sne": n,
        "H0_fixed": H0,
        "covariance": args.covariance,
        "omega_lambda": om_best,
        "sigma": sigma,
        "chi2": chi2_min,
        "dof": n - 1,
        "chi2_per_dof": chi2_min / (n - 1),
        "max_diag_rel_diff_nosys_vs_table": max_diag_rel_diff,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
