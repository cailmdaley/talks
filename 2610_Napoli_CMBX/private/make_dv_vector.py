"""Blinded TR1 x SPT-3G 3x2pt + kappa data vector as JSON, for the Napoli dv-vector slide.

Writes private/dv_vector.json: every pair's ell_eff, data C_ell, sigma_G, windowed
fiducial C_ell and scale-cut mask. The slide draws it client-side with
private/dv_vector.js (the house `data-app` figure), so nothing here is a picture.

Inputs, all blinded (blind cmbx_dr1_a):
  * results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.npz: the export of
    all 90 pairs (ell_eff, data, sigma_G, windowed fiducial, fit mask, covariance
    indices, full covariance).
  * results/tr1/likelihood_product/likelihood_input.tar (lc, commit cd0d303) and
    datavector_vs_theory.tar (lc, commit 6c6c9f1) member check.json: the lc
    outputs the export came from. Every pair of the export is asserted equal to
    them (data, ell_eff, covariance indices, sigma_G from the diagonal of the full
    NaMaster Gaussian covariance, fiducial, fit mask) before anything is written.

The scale cut drawn is the validated linear-bias cut (the export's
fit_mask_validated): k_max 0.2 h/Mpc for delta-delta (a cross takes the lower
lens ell_max), 0.15 for gamma-delta and delta-kappa, no lens cut for
gamma-gamma and gamma-kappa, all within 100 < ell < 3000; its PT contamination
test shifts S8-Omega_m by under 0.3 sigma_2D. The export computed it with the
likelihood's own resolver; here it is checked against the export's per-pair
counts and bounds, and every universe's lc figure carries the same cut as its own fit
mask (the PT-validated default), asserted pair by pair. The fiducial is the reference pushed through the bandpower
windows, not a fit. No amplitude, fit or goodness-of-fit is computed here.

Variants beyond LensMC x SPT-3G come straight from their universe's lc outputs
(results/<universe>/likelihood_product/{likelihood_input,datavector_vs_theory}.tar),
checked against each other and stamped with the same blind. Their validated cut is the
SPT export's per-pair ell bounds: the cut depends only on the lens bins (k_max chi at
each lens bin's mean redshift), so it carries over to any CMB map, and the bands'
ell_eff are asserted equal before it is applied.
Run in the cmbx container:
  app python private/make_dv_vector.py
"""
import json
import os
import pickle
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dv_vector.json")
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
NPZ = f"{CMBX}/results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.npz"
INDEX = f"{CMBX}/results/scratch/napoli/crosses/arrays/tr1_spt_blinded_dvt.json"
LIKE = f"{CMBX}/results/tr1/likelihood_product/likelihood_input.tar"
DVT = f"{CMBX}/results/tr1/likelihood_product/datavector_vs_theory.tar"
# (shear method, CMB survey) -> the universe holding it, or None when not yet measured.
# The first is the export the cut was validated on; the toggles follow this order.
SHEARS = {"lensmc": "LensMC", "metacal": "MetaCal"}
CMBS = {"spt": "SPT-3G", "act": "ACT DR6"}
UNIVERSES = {("lensmc", "spt"): "tr1", ("lensmc", "act"): "tr1_act",
             ("metacal", "spt"): "tr1_metacal", ("metacal", "act"): "tr1_act_metacal"}
BLIND = "cmbx_dr1_a"


def load():
    """All 90 pairs from the export, each asserted equal to the lc outputs."""
    npz = np.load(NPZ)
    index = json.load(open(INDEX))
    assert str(npz["blinded"]) == BLIND and index["blinded"] == BLIND
    with tarfile.open(LIKE) as tar:
        member = next(m for m in tar.getmembers()
                      if m.name.endswith(".pkl") and not m.name.endswith("_dndz.pkl"))
        payload = pickle.load(tar.extractfile(member))
    with tarfile.open(DVT) as tar:
        record = json.load(tar.extractfile("check.json"))
    blind = payload["metadata"].get("blind")
    assert BLIND in json.dumps(blind, default=str), f"payload blind stamp {blind!r} is not {BLIND}"
    assert record["metadata"].get("blind") == blind or BLIND in json.dumps(record["metadata"].get("blind"))
    assert payload["metadata"]["covariance"]["method"] == "namaster_gaussian"
    assert payload["metadata"]["covariance"]["full"] is True
    cov = np.asarray(payload["cov_all"])
    keys = list(payload["cls"])
    assert keys == [str(k) for k in npz["order"]] == index["order"]
    offsets, cursor = {}, 0
    for k in keys:
        n = len(payload["cls"][k]["cl"])
        offsets[k] = np.arange(cursor, cursor + n)
        cursor += n
    assert cov.shape == (cursor, cursor) == npz["cov"].shape
    assert np.array_equal(cov, npz["cov"])
    recs = {r["spectrum"]: r for r in record["spectra"]}
    pairs = {}
    for k in keys:
        rec = recs[k]
        ell = np.asarray(payload["cls"][k]["leff"], float)
        data = np.asarray(payload["cls"][k]["cl"], float)
        sigma = np.sqrt(np.diag(cov)[offsets[k]])
        theory = np.asarray(rec["theory_binned"], float)
        fit = np.asarray(rec["fit_mask"], bool)
        # the lc outputs agree with each other ...
        assert np.allclose(ell, rec["ell_eff"]) and np.allclose(data, rec["data"], rtol=1e-12, atol=0)
        assert np.allclose(sigma, rec["sigma_gaussian"], rtol=1e-12, atol=0)
        assert rec["covariance_indices"] == offsets[k].tolist()
        # ... and the export agrees with them
        assert np.array_equal(npz[f"{k}__cov_idx"], offsets[k])
        assert np.allclose(npz[f"{k}__ell_eff"], ell) and np.array_equal(npz[f"{k}__data"], data)
        assert np.allclose(npz[f"{k}__sigma_G"], sigma, rtol=1e-12, atol=0)
        assert np.array_equal(npz[f"{k}__theory_fid"], theory)
        assert index["pairs"][k]["family"] == rec["family"]
        # the validated cut: per-pair count and ell bounds as the export records them, and the
        # lc figure's own fit mask (the PT-validated default) equal to it
        cut = npz[f"{k}__fit_mask_validated"].astype(bool)
        assert np.array_equal(fit, cut), k
        meta = index["pairs"][k]
        assert int(cut.sum()) == meta["n_fit_validated"], k
        lo, hi = meta["fit_bounds_validated"]
        assert np.array_equal(cut, (ell >= lo) & (ell <= hi)), (k, lo, hi)
        pairs[k] = dict(family=rec["family"], ell=ell, data=data, sigma=sigma, theory=theory, fit=cut)
    kept = index["fit_mask_validated"]["retained_bands"]["validated"]
    for fam, n in kept.items():
        if fam != "total":
            assert sum(int(p["fit"].sum()) for p in pairs.values() if p["family"] == fam) == n, fam
    total = sum(int(p["fit"].sum()) for p in pairs.values())
    assert total == kept["total"] and not index["fit_mask_validated"]["empty_pairs"]
    assert all(p["fit"].any() for p in pairs.values())
    print(f"{len(pairs)} pairs, {cursor} bands, {total} inside the validated linear-bias cut; "
          "export == lc outputs for every pair")
    return pairs, index


def sig(x, n=6):
    return [float(f"{v:.{n}g}") for v in np.asarray(x, float)]


def tracers(key):
    """('kappa' | 'l<i>' | 'g<i>') pair from an export key: l = source (gamma), g = lens (delta)."""
    a, b = key.split("_")
    return [a, b]


def load_universe(universe, index):
    """All pairs of one universe's lc likelihood product, blinded, with the validated cut
    carried over from the SPT export's per-pair ell bounds. None when not materialized."""
    like = f"{CMBX}/results/{universe}/likelihood_product/likelihood_input.tar"
    dvt = f"{CMBX}/results/{universe}/likelihood_product/datavector_vs_theory.tar"
    if not (os.path.exists(like) and os.path.exists(dvt)):
        print(f"{universe}: likelihood product not materialized, left out")
        return None
    with tarfile.open(like) as tar:
        member = next(m for m in tar.getmembers()
                      if m.name.endswith(".pkl") and not m.name.endswith("_dndz.pkl"))
        payload = pickle.load(tar.extractfile(member))
    with tarfile.open(dvt) as tar:
        record = json.load(tar.extractfile("check.json"))
    for meta in (payload["metadata"].get("blind"), record["metadata"].get("blind")):
        assert BLIND in json.dumps(meta, default=str), f"{universe}: blind stamp {meta!r} is not {BLIND}"
    assert payload["metadata"]["covariance"]["method"] == "namaster_gaussian"
    assert payload["metadata"]["covariance"]["full"] is True
    cov = np.asarray(payload["cov_all"])
    recs = {r["spectrum"]: r for r in record["spectra"]}
    pairs, cursor = {}, 0
    for k in payload["cls"]:
        rec, n = recs[k], len(payload["cls"][k]["cl"])
        idx = np.arange(cursor, cursor + n)
        cursor += n
        ell = np.asarray(payload["cls"][k]["leff"], float)
        data = np.asarray(payload["cls"][k]["cl"], float)
        sigma = np.sqrt(np.diag(cov)[idx])
        assert np.allclose(ell, rec["ell_eff"]) and np.allclose(data, rec["data"], rtol=1e-12, atol=0)
        assert np.allclose(sigma, rec["sigma_gaussian"], rtol=1e-12, atol=0)
        assert rec["covariance_indices"] == idx.tolist()
        ref = index["pairs"][k]
        assert np.allclose(ell, np.load(NPZ)[f"{k}__ell_eff"]), f"{universe} {k}: bands differ from the export"
        lo, hi = ref["fit_bounds_validated"]
        fit = (ell >= lo) & (ell <= hi)
        assert int(fit.sum()) == ref["n_fit_validated"], k
        assert np.array_equal(fit, np.asarray(rec["fit_mask"], bool)), (universe, k)
        pairs[k] = dict(family=rec["family"], ell=ell, data=data, sigma=sigma,
                        theory=np.asarray(rec["theory_binned"], float), fit=fit)
    assert cov.shape == (cursor, cursor) and set(pairs) == set(index["order"])
    print(f"{universe}: {len(pairs)} pairs, {cursor} bands, blinded {BLIND}")
    return pairs


def packed(pairs):
    return {k: {"t": tracers(k), "family": p["family"], "ell": sig(p["ell"], 5),
                "cl": sig(p["data"]), "sig": sig(p["sigma"]), "th": sig(p["theory"]),
                "fit": [int(v) for v in p["fit"]]}
            for k, p in pairs.items()}


def main():
    pairs, index = load()
    variants = {"lensmc|spt": packed(pairs)}
    for (shear, cmb), universe in UNIVERSES.items():
        if (shear, cmb) == ("lensmc", "spt"):
            continue
        got = load_universe(universe, index)
        if got is not None:
            variants[f"{shear}|{cmb}"] = packed(got)
    out = {
        "blind": BLIND,
        "source": index["source"],
        "cut": "validated linear-bias cut (k_max 0.2 h/Mpc delta-delta, 0.15 h/Mpc gamma-delta and "
               "delta-kappa; PT contamination test < 0.3 sigma_2D)",
        "shears": SHEARS,
        "cmbs": CMBS,
        "variants": variants,
    }
    text = json.dumps(out, separators=(",", ":"))
    open(OUT, "w").write(text)
    print(f"wrote {OUT} ({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
