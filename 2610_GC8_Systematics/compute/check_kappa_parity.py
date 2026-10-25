#!/usr/bin/env python3
"""Compare exploratory full-SPT controls with the production C2 family."""
import json,tarfile
import numpy as np
from kappa_common import ROOT
out=ROOT/'results/scratch/gc8/kappa_common/tr1_v2'
with tarfile.open(ROOT/'results/tr1_v2/systematics/gaussian_null_family.tar') as tar:
    summary=json.load(tar.extractfile('summary.json'))
    with np.load(tar.extractfile('joint.npz')) as z:cov=z['covariance'];obs=z['observed']
rows=[]
for path in out.glob('*_full.json'):
    r=json.loads(path.read_text()); i=summary['test_names'].index(r['template']+'/kappa');c=cov[i*15:(i+1)*15,i*15:(i+1)*15];v=obs[i]
    cv=np.array(r['covariance']);meas=np.array(r['values'])
    rows.append(dict(template=r['template'],max_vector_difference_over_production_sigma=float(np.max(abs(meas-v)/np.sqrt(np.diag(c)))),max_covariance_relative_difference=float(np.max(abs(cv-c)/np.sqrt(np.diag(c)[:,None]*np.diag(c)[None,:])))))
(out/'production_parity.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
