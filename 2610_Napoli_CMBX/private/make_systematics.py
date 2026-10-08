"""Data for the Napoli systematics-triangle slide: template contamination of every pair.

For each systematics template S and each (shear method, CMB survey) variant whose
template crosses are materialized (results/<universe>/tr1_systematics/<template>.tar),
the contamination a template would add to each data-vector pair if its measured
cross with each tracer were all leakage,

    X_l^{ab} = C_l^{aS} C_l^{bS} / C_l^{SS},

in units of sigma_G, the Gaussian error of C^{ab} in the blinded data vector of that
variant (private/dv_vector.json, from the lc likelihood input). sigma_X is first-order
error propagation: the two crosses' own sigma_G (their covariance with each other
ignored) and a Knox error on C^{SS} with the template support's f_sky, which treats a
fixed map as a Gaussian field. C^{SS} is measured on the same mask, apodization and
bands as the crosses (results/scratch/napoli/systematics/template_autos.json).

Writes private/systematics.json:
  templates  [[id, label], ...] in display order
  variants   {"lensmc|spt": {template: {"x": {pair: [X/sigma_G]}, "sx": {pair: [sigma_X/sigma_G]},
                                        "c": {tracer: [l C^{aS}]}, "s": {tracer: [l sigma]}}}}
  ell        the 15 band centres
Pairs are keyed as in dv_vector.json (kappa_*, g*_g*, g*_l*, l*_l*); tracers are
g0..g5 (lens bins), l0..l5 (source bins) and kappa.

Run in the cmbx container, after make_dv_vector.py:
  app python private/make_systematics.py
"""
import json
import os
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
DV = os.path.join(HERE, "dv_vector.json")
AUTOS = f"{CMBX}/results/scratch/napoli/systematics/template_autos.json"
OUT = os.path.join(HERE, "systematics.json")
TEMPLATES = [("extinction_vis", "Extinction"), ("exposures_vis", "Exposures"), ("noise_vis", "Noise"),
             ("psf_vis", "PSF"), ("zodiacal_vis", "Zodiacal light"), ("stars_gaia", "Stars")]
UNIVERSES = {"lensmc|spt": "tr1", "lensmc|act": "tr1_act", "metacal|spt": "tr1_metacal",
             "metacal|act": "tr1_act_metacal"}
EDGES = np.geomspace(100, 3000, 16)


def sig(x, n=5):
    return [float(f"{v:.{n}g}") for v in np.asarray(x, float)]


def measurement(universe, template):
    # ACT universes name their archives <template>_act (the SPT ids stay as they are)
    for name in (template, f"{template}_act"):
        path = f"{CMBX}/results/{universe}/tr1_systematics/{name}.tar"
        if os.path.exists(path):
            break
    else:
        return None
    with tarfile.open(path) as t:
        return json.load(t.extractfile("measurement.json"))


def crosses(m):
    out = {k: (np.asarray(r["cross"]), np.asarray(r["sigma"]), np.asarray(r["ell"]))
           for fam in ("GC", "WL") for k, r in m[fam].items()}
    r = m["template_kappa"]
    out["kappa"] = (np.asarray(r["cross"]), np.asarray(r["sigma"]), np.asarray(r["ell"]))
    return out


def xell(c, auto, a, b):
    css = np.asarray(auto["cl"])
    sss = css * np.sqrt(2 / (auto["fsky_support"] * (EDGES[1:] ** 2 - EDGES[:-1] ** 2)))
    ca, sa, _ = c[a]
    cb, sb, _ = c[b]
    x = ca * cb / css
    if a == b:
        var = (2 * ca / css * sa) ** 2 + (x * sss / css) ** 2
    else:
        var = (cb / css * sa) ** 2 + (ca / css * sb) ** 2 + (x * sss / css) ** 2
    return x, np.sqrt(var)


def main():
    dv = json.load(open(DV))
    autos = json.load(open(AUTOS))
    out = dict(templates=[list(t) for t in TEMPLATES], variants={}, ell=None, blind=dv["blind"])
    for vk, universe in UNIVERSES.items():
        if vk not in dv["variants"]:
            print(f"{vk}: no data vector, left out")
            continue
        pairs = dv["variants"][vk]
        per = {}
        for t, _ in TEMPLATES:
            m = measurement(universe, t)
            if m is None:
                continue
            c = crosses(m)
            ell = c["g0"][2]
            if out["ell"] is None:
                out["ell"] = sig(ell, 5)
            x, sx = {}, {}
            for k, p in pairs.items():
                a, b = p["t"]
                assert np.allclose(np.asarray(p["ell"]), ell, rtol=1e-3), (vk, k)
                xv, sv = xell(c, autos[t], a, b)
                sg = np.asarray(p["sig"])
                x[k], sx[k] = sig(xv / sg, 4), sig(sv / sg, 4)
            per[t] = dict(x=x, sx=sx, c={k: sig(ell * v[0]) for k, v in c.items()},
                          s={k: sig(ell * v[1]) for k, v in c.items()})
        if len(per) == len(TEMPLATES):
            out["variants"][vk] = per
            worst = max((abs(v), t, k) for t, d in per.items() for k, xs in d["x"].items() for v in xs)
            print(f"{vk} ({universe}): 6 templates; largest nominal |X/sigma_G| {worst[0]:.2f} ({worst[1]}, {worst[2]})")
        elif per:
            print(f"{vk} ({universe}): only {sorted(per)} measured, left out until all six land")
        else:
            print(f"{vk} ({universe}): no template crosses yet, left out")
    text = json.dumps(out, separators=(",", ":"))
    open(OUT, "w").write(text)
    print(f"wrote {OUT} ({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
