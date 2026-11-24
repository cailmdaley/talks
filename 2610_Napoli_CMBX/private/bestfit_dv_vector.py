"""Best fit of the blinded TR1 production 5x2pt chains, windowed onto every band, for the dv-vector slide.

For each production chain (nested_full: LensMC x SPT-3G and LensMC x ACT DR6, pure CLOE through its JAX
adapter, 15 Nov) this
  * rebuilds the chain's own Cobaya model (nested_model.Spec on the chain's model.json and input product) and
    asserts its scientific identity equals the one the chain recorded (same config, product, code);
  * takes the highest-posterior sample (max log L + log prior) of posterior.npz and polishes it with L-BFGS-B
    on the JAX adapter's chi^2 plus the Gaussian prior terms (gradients from JAX, uniform priors as bounds);
  * evaluates both points with the exact CLOE model, for all 90 pairs and all bands through the product's
    bandpower windows, and checks the chi^2 of (data - that vector) under the chain's own cut covariance
    against the chain's stored log L (the sample) and the adapter's (the polished point);
  * reports how the chain's data and sigma differ band by band from --figure's (make_dv_vector's JSON); the
    chains fit the Nov likelihood product, whose density data and covariance differ from the Oct rerun's.
MetaCal x ACT DR6 has no chain: its curve is the LensMC x ACT DR6 best fit pushed through the MetaCal
product's windows (the same model and point, the MetaCal likelihood_input).

Writes --out/bestfit.json: per variant the point, chi^2 bookkeeping, per-family chi^2 and amplitudes, and the
best-fit theory and fit mask of every pair. make_dv_vector.py --bestfit reads it.

Run in the cmbx container on a compute node, the lane code on PYTHONPATH:
  L=/leonardo_scratch/large/userexternal/cdaley00/cmbx-lanes/fp-spt
  PYTHONPATH=$L/code/dr1_cmbx/src:$L/code/dr1_notebooks/src COBAYA_NOMPI=1 \
    python bestfit_dv_vector.py --figure dv_vector_spt.json --out DIR
"""
import argparse
import json
import os
import pickle
import sys
import tarfile
from types import SimpleNamespace

import numpy as np

LANES = "/leonardo_scratch/large/userexternal/cdaley00/cmbx-lanes"
CMBX = "/leonardo_work/EUHPC_E07_074/cdaley00/cmbx"
CHAINS = {"lensmc|spt": ("fp-spt", "tr1_v2", "spt_winter_gmvbhttprf"),
          "lensmc|act": ("fp-act", "tr1_v2_act", "act_dr6")}
METACAL = ("metacal|act", "lensmc|act", f"{CMBX}/results/tr1_v2_act_metacal/likelihood_product/likelihood_input.tar")
FAMILIES = ("gg", "gd", "dd", "gk", "dk")   # gamma-gamma, gamma-delta, delta-delta, gamma-kappa, delta-kappa


def family(key):
    """Probe family of a product key ('l<i>' source/shear, 'g<i>' lens/density, 'kappa')."""
    a, b = key.split("_")
    if "kappa" in (a, b):
        return "gk" if "l" in (a[0], b[0]) else "dk"
    return {"ll": "gg", "gg": "dd"}.get(a[0] + b[0], "gd")


def spec(lane, universe, product):
    import nested_model
    run = f"{LANES}/{lane}/results/cache/{universe}/production_chains/nested_full"
    return nested_model.Spec(SimpleNamespace(root=f"{LANES}/{lane}", universe=universe, variant="full", out=None,
                                             config=f"{run}/model.json", product=product, kappa_tag=None, scripts=None))


def exact(model, point):
    """-2 log L of the exact CLOE model at point, and its windowed theory for every pair and band."""
    lp = model.logposterior(point, make_finite=False)
    lik = model.likelihood["cmbx"]
    fast = [n for n in lik._vector_nuisance_names()[0] if n in point]
    bands = lik.get_band_theory(**{n: point[n] for n in fast})
    return float(-2 * np.sum(lp.loglikes)), {k: np.asarray(v, float) for k, v in bands.items()}


def pairs_of(like):
    """Data and fit mask of every pair as the likelihood holds them, and each retained band's pair."""
    out, owner = {}, []
    for i, key in enumerate(like.order_data):
        d = np.asarray(like.data_spectra[i], float)
        fit = (np.arange(len(d)) >= like.bpmin[i]) & (np.arange(len(d)) <= like.bpmax[i])
        out[key] = dict(data=d, fit=fit)
        owner += [key] * int(fit.sum())
    return out, np.array(owner)


def chi2_report(like, pairs, owner, theory):
    """chi^2 of (data - theory) on the retained bands under the likelihood's own covariance (solved, not its
    stored inverse), in total and per family (each family's own covariance block), with each family's
    best amplitude A (data ~ A theory) and its error."""
    cov = np.asarray(like.cov, float)
    d = np.concatenate([pairs[k]["data"][pairs[k]["fit"]] for k in like.order_data])
    t = np.concatenate([theory[k][pairs[k]["fit"]] for k in like.order_data])
    assert np.array_equal(d, np.asarray(like.bps_data_vec, float)), "retained data differ from the likelihood's"
    r = d - t
    out = dict(chi2=float(r @ np.linalg.solve(cov, r)), n=len(r), family={})
    fam = np.array([family(k) for k in owner])
    for f in FAMILIES:
        s = fam == f
        c = cov[np.ix_(s, s)]
        ct, cr = np.linalg.solve(c, t[s]), np.linalg.solve(c, r[s])
        out["family"][f] = dict(n=int(s.sum()), chi2=float(r[s] @ cr),
                                A=float(ct @ d[s] / (ct @ t[s])), sigma_A=float(1 / np.sqrt(ct @ t[s])))
    return out


def polish(jv, model, x0):
    """L-BFGS-B from x0 on chi^2 + the Gaussian prior terms (-2 log posterior up to a constant)."""
    import jax
    import jax.numpy as jnp
    from scipy.optimize import minimize
    kind, loc, scale = jv._prior_kind, jv._prior_loc, jv._prior_scale
    assert set(kind.tolist()) <= {0, 1}, "only uniform and normal priors are handled"
    norm = kind == 1

    def objective(theta):
        chi2, valid, _ = jv._chi2_with_status(theta)
        return chi2 + jnp.sum(jnp.where(norm, ((theta - loc) / scale) ** 2, 0.0)), valid

    vg = jax.jit(jax.value_and_grad(objective, has_aux=True))

    def f(x):
        (v, valid), g = vg(jnp.asarray(x, dtype=float))
        if not bool(valid):
            return 1e30, np.zeros_like(x)
        return float(v), np.asarray(g, float)

    bounds = [(l, l + s) if k == 0 else (None, None) for k, l, s in zip(kind, loc, scale)]
    # scale each parameter by its prior width so the problem is well conditioned
    w = np.where(norm, scale, scale / np.sqrt(12))
    res = minimize(lambda z: (lambda v, g: (v, g * w))(*f(x0 + z * w)), np.zeros_like(x0), jac=True,
                   method="L-BFGS-B", bounds=[((lo - x) / s if lo is not None else None,
                                                (hi - x) / s if hi is not None else None)
                                               for (lo, hi), x, s in zip(bounds, x0, w)],
                   options=dict(maxiter=500, ftol=1e-12, gtol=1e-6))
    return x0 + res.x * w, res


def run_chain(vk, figure, args):
    from dr1_cmbx.eDR1like.jax_vector import JaxVector
    lane, universe, tag = CHAINS[vk]
    run = f"{LANES}/{lane}/results/cache/{universe}/production_chains/nested_full"
    sp = spec(lane, universe, f"{run}/input/likelihood_input_{tag}.pkl")
    stored = json.load(open(f"{run}/nested/scientific_identity.json"))
    mine = sp.identity(None, algorithm=stored["payload"]["algorithm"])
    for part in ("config", "files", "sources", "algorithm"):
        assert mine["payload"][part] == stored["payload"][part], f"{vk}: model {part} differs from the chain's"
    env = {k: (v, mine["payload"]["environment"].get(k)) for k, v in stored["payload"]["environment"].items()
           if mine["payload"]["environment"].get(k) != v}
    print(f"{vk}: identity {'equal' if mine['sha256'] == stored['sha256'] else 'differs in environment ' + str(env)}",
          flush=True)
    model = sp.model()
    names = sp.names()
    like = model.likelihood["cmbx"].like
    pairs, owner = pairs_of(like)

    # the chain's data against the figure's, band by band
    payload = pickle.load(open(sp.product, "rb"))
    cov_all = np.asarray(payload["cov_all"])
    off, worst_cl, worst_sig = 0, 0.0, 0.0
    fig = figure["variants"][vk]
    assert set(fig) == set(pairs), f"{vk}: pairs differ from the figure's"
    for k in like.order_data:
        n = len(pairs[k]["data"])
        sig = np.sqrt(np.diag(cov_all)[off:off + n])
        off += n
        worst_cl = max(worst_cl, float(np.max(np.abs(np.asarray(fig[k]["cl"]) / pairs[k]["data"] - 1))))
        worst_sig = max(worst_sig, float(np.max(np.abs(np.asarray(fig[k]["sig"]) / sig - 1))))
        assert np.array_equal(np.asarray(fig[k]["fit"], bool), pairs[k]["fit"]), f"{vk} {k}: cut differs"
    print(f"{vk}: chain data vs --figure: max |rel diff| cl {worst_cl:.2e}, sigma {worst_sig:.2e}; "
          f"cuts equal ({len(owner)} bands)", flush=True)

    # highest-posterior sample
    post = np.load(f"{run}/nested/posterior.npz", allow_pickle=True)
    assert list(post["names"]) == names
    X, log_l = post["points"], post["log_l"]
    log_pi = np.sum([pdf.logpdf(X[:, i]) for i, pdf in enumerate(model.prior.pdf)], axis=0)
    i_map, i_ml = int(np.argmax(log_l + log_pi)), int(np.argmax(log_l))
    x_map = X[i_map]
    w = np.exp(post["log_w"] - post["log_w"].max())
    w /= w.sum()
    mean = w @ X
    sd = np.sqrt(w @ (X - mean) ** 2)
    derived_names = [str(n) for n in post["derived_names"]]

    jv = JaxVector.from_cobaya_model(model)
    cached = os.path.join(args.out, f"polished_{lane}.npy")
    if os.path.exists(cached):
        x_pol = np.load(cached)
    else:
        x_pol, res = polish(jv, model, x_map)
        np.save(cached, x_pol)
        print(f"{vk}: polish {res.message} after {res.nit} iterations, {res.nfev} evaluations", flush=True)

    import jax.numpy as jnp
    out = dict(chain=run, product=sp.product, names=names, n_samples=len(X),
               chain_sample=dict(index=i_map, chi2_stored=float(-2 * log_l[i_map]),
                           log_prior=float(log_pi[i_map]), chi2_max_likelihood_sample=float(-2 * log_l[i_ml])),
               posterior_mean=dict(zip(names, mean.tolist())), posterior_sd=dict(zip(names, sd.tolist())),
               posterior_derived_mean=dict(zip(derived_names, (w @ post["derived"]).tolist())))
    best = None
    for label, x in (("sample", x_map), ("polished", x_pol)):
        point = dict(zip(names, map(float, x)))
        chi2_cloe, theory = exact(model, point)
        rep = chi2_report(like, pairs, owner, theory)
        chi2_jax = float(jv.chi2(jnp.asarray(x)))
        derived = dict(zip(jv.DERIVED, np.asarray(jv._jit_derived(jnp.asarray(x))).tolist()))
        lp = float(np.sum([pdf.logpdf(v) for pdf, v in zip(model.prior.pdf, x)]))
        out[label] = dict(point=point, derived=derived, chi2_cloe=chi2_cloe, chi2_jax=chi2_jax, log_prior=lp,
                          minus2_log_post=chi2_cloe - 2 * lp, **rep)
        print(f"{vk} {label}: chi2 recomputed {rep['chi2']:.4f} | CLOE -2logL {chi2_cloe:.4f} | JAX {chi2_jax:.4f}"
              + (f" | chain stored {out['chain_sample']['chi2_stored']:.4f}" if label == "sample" else "")
              + f" | n {rep['n']} | -2 log post {chi2_cloe - 2 * lp:.3f}", flush=True)
        assert abs(rep["chi2"] - chi2_cloe) < 1e-6 * rep["chi2"], "chi2 of the drawn vector is not CLOE's"
        if label == "sample":
            assert abs(rep["chi2"] - out["chain_sample"]["chi2_stored"]) < 0.05, "chi2 does not reproduce the chain's log L"
        if best is None or out[label]["minus2_log_post"] < out[best]["minus2_log_post"]:
            best, best_theory = label, theory
    out["best"] = best
    out["theory"] = {k: best_theory[k].tolist() for k in like.order_data}
    out["fit"] = {k: pairs[k]["fit"].astype(int).tolist() for k in like.order_data}
    out["data"] = {k: pairs[k]["data"].tolist() for k in like.order_data}
    # the amplitudes the earlier fixed reference gave (the figure's curve), on the same bands and covariance
    out["reference"] = chi2_report(like, pairs, owner, {k: np.asarray(fig[k]["th"], float) for k in like.order_data})
    return out, model


def run_metacal(act, act_model, figure, args):
    vk, ref_vk, tar = METACAL
    lane, universe, tag = CHAINS[ref_vk]
    where = os.path.join(args.out, "metacal_input")
    os.makedirs(where, exist_ok=True)
    with tarfile.open(tar) as t:
        t.extractall(where)
    sp = spec(lane, universe, os.path.join(where, f"likelihood_input_{tag}.pkl"))
    model = sp.model()
    like = model.likelihood["cmbx"].like
    pairs, owner = pairs_of(like)
    fig = figure["variants"][vk]
    for k in like.order_data:
        assert np.allclose(np.asarray(fig[k]["cl"]), pairs[k]["data"], rtol=1e-5, atol=0), f"{vk} {k}: data differ"
        assert pairs[k]["fit"].tolist() == act["fit"][k], f"{vk} {k}: cut differs from {ref_vk}'s"
    point = act[act["best"]]["point"]
    chi2_cloe, theory = exact(model, point)
    rep = chi2_report(like, pairs, owner, theory)
    print(f"{vk}: {ref_vk} best fit through MetaCal windows: chi2 {rep['chi2']:.2f} / {rep['n']} (CLOE {chi2_cloe:.2f})",
          flush=True)
    return dict(borrowed=ref_vk, product=sp.product, point=point, **rep,
                theory={k: theory[k].tolist() for k in like.order_data},
                fit={k: pairs[k]["fit"].astype(int).tolist() for k in like.order_data},
                reference=chi2_report(like, pairs, owner, {k: np.asarray(fig[k]["th"], float) for k in like.order_data}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure", required=True, help="make_dv_vector.py's data JSON the slide plots")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    sys.path.insert(0, f"{LANES}/fp-spt/workflow/scripts")
    os.environ.setdefault("COBAYA_NOMPI", "1")
    figure = json.load(open(args.figure))
    out = {}
    for vk in CHAINS:
        out[vk], model = run_chain(vk, figure, args)
    out[METACAL[0]] = run_metacal(out[METACAL[1]], model, figure, args)
    path = os.path.join(args.out, "bestfit.json")
    json.dump(dict(blind=figure["blind"], variants=out), open(path, "w"))
    print("wrote", path)


if __name__ == "__main__":
    main()
