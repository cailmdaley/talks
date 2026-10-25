#!/usr/bin/env python3
"""Cheap algebraic and provenance checks for the exploratory rho collection."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'results/scratch/gc8/rho'
x=json.loads((OUT/'rho.json').read_text());checks=[]
for key,r in x['rows'].items():
    c=np.array(r['cross']);C=np.array(r['covariance_cross']);rho=np.array(r['rho']);R=np.array(r['covariance_rho']);norm=np.array(r['normalization'])
    assert c.shape==(15,) and C.shape==(15,15)
    np.testing.assert_allclose(rho*norm,c,rtol=1e-13)
    np.testing.assert_allclose(R*np.outer(norm,norm),C,rtol=1e-12,atol=1e-30)
    np.testing.assert_allclose(np.sqrt(np.diag(R)),r['sigma_rho'],rtol=1e-13)
    np.testing.assert_allclose(float(c@np.linalg.solve(C,c)),r['chi2'],rtol=1e-12)
    np.linalg.cholesky(R)
    one=np.ones(15);w=np.linalg.solve(R,one);w/=w.sum()
    np.testing.assert_allclose(w@rho,r['mean_rho'],rtol=1e-12)
    np.testing.assert_allclose(np.sqrt(w@R@w),r['mean_rho_error'],rtol=1e-12)
    assert np.count_nonzero(R-np.diag(np.diag(R)))>0
    checks.append(key)
for key,p in x['cib_route'].items():
    np.testing.assert_allclose(np.array(p['rho_delta_cib'])*p['rho_cib_ext'],p['rho_pred'],rtol=1e-13)
    np.testing.assert_allclose(np.array(p['compression_weights'])@p['rho_pred'],p['mean_rho_pred'],rtol=1e-13)
report=dict(passed=True,test_rows=len(checks),route_rows=len(x['cib_route']),checks=['all 15x15 blocks positive definite; nonzero off-diagonals retained','cross and normalized chi2 exactly invariant','GLS mean/error reproduced','route identity and same-compression weights reproduced'],pending=[str(p) for p in ['c2_vmpz_kappa.pkl','c2_sfd_wl_kappa.pkl','c2_csfd_wl_kappa.pkl'] if not (OUT/p).exists()])
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
