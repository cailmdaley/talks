"""Data for the Napoli systematics-triangle slide: template contamination of every pair.

For each systematics template S and each (shear method, CMB survey) variant whose
template crosses are materialized (results/<universe>/tr1_systematics/<template>.tar),
with the lens-bin crosses taken from delta weighted by the VMPZ test visibility maps,
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
  flags      per template and variant, each tracer's {"pte", "coh"}: the chi^2 PTE of its template
             cross against zero and its coherent offset sum(pull)/sqrt(15); a tracer is flagged
             when PTE < PTE_FLAG (about 1 % family-wise over the ~100 template crosses), and a
             pair when either tracer is
  harmonics  per template, the band centres where the template's own power peaks (its
             tiling harmonics), where l C^SS exceeds HARM_FLAG x its median for 300 < l < 2000
Pairs are keyed as in dv_vector.json (kappa_*, g*_g*, g*_l*, l*_l*); tracers are
g0..g5 (lens bins), l0..l5 (source bins) and kappa.

Run in the cmbx container, after make_dv_vector.py:
  app python private/make_systematics.py
"""
import argparse
import csv
import io
import json
import os
import pickle
import tarfile

import numpy as np
from scipy import stats

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
PTE_FLAG = 1e-4                      # a template cross that fails: ~1 % family-wise over ~100 tests
HARM_FLAG = 2.4                      # template power this far above its median marks a harmonic


VIS = f"{CMBX}/results/scratch/napoli/visibility_check"


def visibility_corrected(m, template):
    """Swap the lens-bin crosses for those of delta divided by the VMPZ v1.1 test
    visibility weight, w = (1 + WEIGHT) / <1 + WEIGHT> (results/scratch/napoli/visibility_check,
    same templates, masks, estimator and bands; its Gaussian covariance recomputed)."""
    gc = json.load(open(f"{VIS}/{template}.json"))["GC"]
    for k, r in gc.items():
        a = dict(r["after"])
        a["sigma"] = list(np.sqrt(np.diag(np.asarray(a["covariance"]))))
        m["GC"][k] = a
    return m


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
        return visibility_corrected(json.load(t.extractfile("measurement.json")), template)


def crosses(m):
    out = {k: (np.asarray(r["cross"]), np.asarray(r["sigma"]), np.asarray(r["ell"]))
           for fam in ("GC", "WL") for k, r in m[fam].items()}
    r = m["template_kappa"]
    out["kappa"] = (np.asarray(r["cross"]), np.asarray(r["sigma"]), np.asarray(r["ell"]))
    return out


def null_chi2(m):
    """chi^2 of each tracer's template cross against zero over the 15 bands: the full
    Gaussian covariance for the Euclid tracers, the diagonal only for kappa."""
    out = {}
    for fam in ("GC", "WL"):
        for k, r in m[fam].items():
            cl = np.asarray(r["cross"])
            out[k] = float(cl @ np.linalg.solve(np.asarray(r["covariance"]), cl))
    out["kappa"] = float(np.sum(np.asarray(m["template_kappa"]["signed_pull"]) ** 2))
    return out


def coherent(m):
    """Each tracer's coherent offset: the sum of its band pulls over sqrt(n), which a
    same-sign shift raises and random scatter does not."""
    out = {k: float(np.sum(r["signed_pull"]) / np.sqrt(len(r["signed_pull"])))
           for fam in ("GC", "WL") for k, r in m[fam].items()}
    p = np.asarray(m["template_kappa"]["signed_pull"])
    out["kappa"] = float(p.sum() / np.sqrt(p.size))
    return out


def harmonics(auto):
    ell, cl = np.asarray(auto["ell"]), np.asarray(auto["cl"])
    r = ell * cl / np.median(ell * cl)
    return [float(round(l)) for l, v in zip(ell, r) if 300 < l < 2000 and v > HARM_FLAG]


def xell(c, auto, a, b):
    css = np.asarray(auto["cl"])
    # Cycle 2 conditions on the delivered fixed template: no Knox error.
    # Preserve the explicitly labelled legacy Cycle-1 auto term.
    sss = (css * np.sqrt(2 / (auto["fsky_support"] * (EDGES[1:] ** 2 - EDGES[:-1] ** 2)))
           if "fsky_support" in auto else np.zeros_like(css))
    ca, sa, _ = c[a]
    cb, sb, _ = c[b]
    x = ca * cb / css
    if a == b:
        var = (2 * ca / css * sa) ** 2 + (x * sss / css) ** 2
    else:
        var = (cb / css * sa) ** 2 + (ca / css * sb) ** 2 + (x * sss / css) ** 2
    return x, np.sqrt(var)


def cycle2_inputs():
    """Read canonical Cycle-2 nulls, fixed template autos and Gaussian DV errors."""
    root = f"{CMBX}/results/tr1_v2"
    paths = [f"{root}/systematics/{t}.tar" for t, _ in TEMPLATES]
    family = f"{root}/systematics/gaussian_null_family.tar"
    if not all(os.path.exists(p) for p in paths + [family]):
        print("Cycle 2: waiting for family and all six per-template archives")
        return None
    with tarfile.open(family) as tar:
        summary = json.load(tar.extractfile('summary.json'))
        joint = np.load(io.BytesIO(tar.extractfile('joint.npz').read()))
        obs, cov = joint['observed'], joint['covariance']
    ell = np.asarray(summary['ell'])
    assert len(ell) == 15
    with tarfile.open(f"{root}/likelihood_product/likelihood_input.tar") as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith('.pkl') and not m.name.endswith('_dndz.pkl'))
        dv = pickle.load(tar.extractfile(member))
    assert dv['metadata']['covariance']['method'] == 'namaster_gaussian'
    assert dv['metadata']['covariance']['full'] is True
    C = np.asarray(dv['cov_all'])
    pairs, cursor = {}, 0
    for key, row in dv['cls'].items():
        n = len(row['cl'])
        assert n == 15 and np.allclose(row['leff'], ell)
        pairs[key] = dict(t=key.split('_'), ell=ell, sig=np.sqrt(np.diag(C)[cursor:cursor+n]))
        cursor += n
    assert C.shape == (cursor, cursor)
    per = {}
    for (template, _), path in zip(TEMPLATES, paths):
        with tarfile.open(path) as tar:
            m = json.load(tar.extractfile('measurement.json'))
            rows = list(csv.DictReader(io.StringIO(tar.extractfile('contamination.csv').read().decode())))
        auto_rows = rows[:15]
        assert np.allclose([float(r['ell']) for r in auto_rows], ell)
        css = np.asarray([float(r['c_extinction_extinction']) for r in auto_rows])
        assert np.all(css > 0)
        for offset in range(0, len(rows), 15):
            assert np.allclose([float(r['c_extinction_extinction']) for r in rows[offset:offset+15]], css)
        c, qs, cohs = {}, {}, {}
        for tracer in ['kappa'] + [f'g{i}' for i in range(6)] + [f'l{i}' for i in range(6)]:
            idx = summary['test_names'].index(f"{m['template']}/{tracer}")
            y, block = obs[idx], cov[idx*15:(idx+1)*15, idx*15:(idx+1)*15]
            assert np.allclose(m['nulls'][tracer]['cross'], y)
            sigma = np.sqrt(np.diag(block))
            c[tracer] = y, sigma, ell
            qs[tracer] = float(y @ np.linalg.solve(block, y))
            corr = block/np.outer(sigma, sigma)
            ri = np.linalg.solve(corr, np.ones(15))
            cohs[tracer] = float(ri @ (y/sigma) / np.sqrt(ri.sum()))
        x, sx = {}, {}
        for key, pair in pairs.items():
            xv, sv = xell(c, dict(cl=css), *pair['t'])
            x[key], sx[key] = sig(xv/pair['sig'], 4), sig(sv/pair['sig'], 4)
        per[template] = dict(x=x, sx=sx, c={k:sig(ell*v[0]) for k,v in c.items()},
                             s={k:sig(ell*v[1]) for k,v in c.items()}, chi2=qs, coh=cohs,
                             flag=sorted(k for k,q in qs.items() if stats.chi2.sf(q,15)<PTE_FLAG))
        worst = max((abs(v), key, i, v, sx[key][i]) for key, vals in x.items() for i,v in enumerate(vals))
        print(f'Cycle 2 {template}: worst |X/sigma_G|={worst[0]:.5g}, pair={worst[1]}, ell={ell[worst[2]]:.2f}, signed={worst[3]:+.5g} +/- {worst[4]:.5g}; fixed-template conditional propagated Gaussian cross errors')
    return per, ell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cycle2', action='store_true')
    parser.add_argument('--output', default=OUT)
    args = parser.parse_args()
    dv = json.load(open(DV))
    autos = json.load(open(AUTOS))
    out = dict(templates=[list(t) for t in TEMPLATES], variants={}, ell=None, blind=dv["blind"],
               harmonics={t: harmonics(autos[t]) for t, _ in TEMPLATES})
    print("harmonics:", out["harmonics"])
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
                          s={k: sig(ell * v[1]) for k, v in c.items()},
                          chi2={k: round(v, 2) for k, v in null_chi2(m).items()},
                          coh={k: round(v, 2) for k, v in coherent(m).items()})
            per[t]["flag"] = sorted(k for k in per[t]["chi2"]
                                    if stats.chi2.sf(per[t]["chi2"][k], 15) < PTE_FLAG)
        if len(per) == len(TEMPLATES):
            out["variants"][vk] = per
            worst = max((abs(v), t, k) for t, d in per.items() for k, xs in d["x"].items() for v in xs)
            print(f"{vk} ({universe}): 6 templates; largest nominal |X/sigma_G| {worst[0]:.2f} ({worst[1]}, {worst[2]})")
            for t, d in per.items():
                print(f"   {t:15s} flagged: {' '.join(d['flag']) or '-'}")
        elif per:
            print(f"{vk} ({universe}): only {sorted(per)} measured, left out until all six land")
        else:
            print(f"{vk} ({universe}): no template crosses yet, left out")
    if args.cycle2:
        got = cycle2_inputs()
        if got is not None:
            per, ell = got
            assert np.allclose(out['ell'], ell, rtol=1e-3)
            out['variants']['cycle2|spt2'] = per
            out['cycle2_error_contract'] = 'Fixed template auto; Gaussian null cross errors propagated independently; cross-cross covariance omitted. No Knox term.'
    text = json.dumps(out, separators=(",", ":"))
    open(args.output, "w").write(text)
    print(f"wrote {args.output} ({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
