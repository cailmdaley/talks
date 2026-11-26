import argparse
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad

C_KM_S = 299792.458


def distmod_flat_lcdm(omega_lambda: float, h0: float, z: np.ndarray) -> np.ndarray:
    omega_m = 1.0 - omega_lambda
    dl_mpc = np.empty_like(z, dtype=float)
    for i, zi in enumerate(z):
        val, _ = quad(lambda zp: 1.0 / np.sqrt(omega_m * (1.0 + zp) ** 3 + omega_lambda), 0.0, zi)
        dl_mpc[i] = (C_KM_S / h0) * (1.0 + zi) * val
    return 5.0 * np.log10(dl_mpc) + 25.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--fit", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    z, mu, mu_err = [], [], []
    with open(args.data) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.split()
            z.append(float(p[1]))
            mu.append(float(p[2]))
            mu_err.append(float(p[3]))
    z, mu, mu_err = np.array(z), np.array(mu), np.array(mu_err)

    with open(args.fit) as f:
        fit = json.load(f)

    om_l = fit["omega_lambda"]
    sig = fit["sigma"]
    h0 = fit["H0_fixed"]
    cov_label = "stat + sys" if fit["covariance"] == "full" else "stat only"

    zgrid = np.geomspace(z.min(), z.max(), 300)
    mu_fit_grid = distmod_flat_lcdm(om_l, h0, zgrid)
    mu_eds_grid = distmod_flat_lcdm(0.0, h0, zgrid)
    resid = mu - distmod_flat_lcdm(om_l, h0, z)

    plt.rcParams.update({
        "font.family": "serif",
        "axes.edgecolor": "#211C17",
        "axes.labelcolor": "#211C17",
        "xtick.color": "#211C17",
        "ytick.color": "#211C17",
        "text.color": "#211C17",
    })

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 6.6), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08},
    )
    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xscale("log")

    ax1.errorbar(z, mu, yerr=mu_err, fmt="o", ms=3.5, elinewidth=0.7, color="#675D4F", alpha=0.55, label="Union2.1 SNe Ia (580)")
    ax1.plot(zgrid, mu_fit_grid, color="#A8403A", lw=2.6, label=rf"Flat $\Lambda$CDM ({cov_label}): $\Omega_\Lambda = {om_l:.3f} \pm {sig:.3f}$")
    ax1.plot(zgrid, mu_eds_grid, color="#3D5BA0", lw=2.0, ls="--", label=r"Einstein–de Sitter ($\Omega_\Lambda = 0$)")
    ax1.set_ylabel(r"Distance modulus $\mu$", fontsize=16)
    ax1.tick_params(labelsize=13)
    ax1.legend(frameon=False, fontsize=13, loc="lower right")

    ax2.axhline(0, color="#211C17", lw=1.0, alpha=0.5)
    ax2.errorbar(z, resid, yerr=mu_err, fmt="o", ms=3.5, elinewidth=0.7, color="#675D4F", alpha=0.55)
    ax2.set_ylabel(r"$\Delta\mu$", fontsize=16)
    ax2.set_xlabel(r"Redshift $z$", fontsize=16)
    ax2.tick_params(labelsize=13)

    fig.savefig(args.out, dpi=200, bbox_inches="tight", facecolor="white")


if __name__ == "__main__":
    main()
