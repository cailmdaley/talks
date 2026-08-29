# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib", "astropy", "scipy"]
# ///
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from astropy.cosmology import FlatLambdaCDM
import json

INK = "#1B1611"
MUTED = "#7A6F5C"
FIT_COLOR = "#BC4538"
EDS_COLOR = "#3D5BA0"

# font
available = {f.name for f in fm.fontManager.ttflist}
font_family = "EB Garamond" if "EB Garamond" in available else "serif"
plt.rcParams["font.family"] = font_family
plt.rcParams["text.color"] = INK
plt.rcParams["axes.edgecolor"] = INK
plt.rcParams["axes.labelcolor"] = INK
plt.rcParams["xtick.color"] = INK
plt.rcParams["ytick.color"] = INK
plt.rcParams["xtick.labelsize"] = 16
plt.rcParams["ytick.labelsize"] = 16
plt.rcParams["axes.labelsize"] = 20

data_path = "data/SCPUnion2.1_mu_vs_z.txt"
z, mu, mu_err = [], [], []
with open(data_path) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        z.append(float(parts[1]))
        mu.append(float(parts[2]))
        mu_err.append(float(parts[3]))
z = np.array(z)
mu = np.array(mu)
mu_err = np.array(mu_err)

with open("results/fit.json") as f:
    fit = json.load(f)

H0 = fit["H0_fixed"]
om_l = fit["diagonal"]["omega_lambda"]  # best available (stat+sys) fit for the curve

zgrid = np.linspace(z.min(), z.max(), 400)

def distmod(om_l_val, zg):
    cosmo = FlatLambdaCDM(H0=H0, Om0=1 - om_l_val)
    return cosmo.distmod(zg).value

mu_fit_grid = distmod(om_l, zgrid)
mu_eds_grid = distmod(0.0, zgrid)  # Einstein-de Sitter, Omega_Lambda = 0

mu_fit_data = distmod(om_l, z)
resid = mu - mu_fit_data

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(14, 8), sharex=True,
    gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08},
)
fig.patch.set_alpha(0.0)
for ax in (ax1, ax2):
    ax.patch.set_alpha(0.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xscale("log")

ax1.errorbar(z, mu, yerr=mu_err, fmt="o", ms=3.5, elinewidth=0.7, capsize=0,
             color=MUTED, ecolor=MUTED, alpha=0.6, label="Union2.1 SNe Ia (580)")
ax1.plot(zgrid, mu_fit_grid, color=FIT_COLOR, lw=2.5,
          label=rf"Flat $\Lambda$CDM, $\Omega_\Lambda={om_l:.3f}$")
ax1.plot(zgrid, mu_eds_grid, color=EDS_COLOR, lw=2, ls="--",
          label=r"Einstein–de Sitter, $\Omega_\Lambda=0$")
ax1.set_ylabel(r"Distance modulus $\mu$")
ax1.legend(frameon=False, fontsize=14, loc="lower right", labelcolor=INK)

ax2.axhline(0, color=INK, lw=1, alpha=0.5)
ax2.errorbar(z, resid, yerr=mu_err, fmt="o", ms=3.5, elinewidth=0.7, capsize=0,
             color=MUTED, ecolor=MUTED, alpha=0.6)
ax2.set_ylabel(r"$\mu - \mu_{\rm model}$")
ax2.set_xlabel("Redshift $z$")

plt.savefig("results/hubble_diagram.png", dpi=200, transparent=True, bbox_inches="tight")
print("saved results/hubble_diagram.png")
print(f"font used: {font_family}")
