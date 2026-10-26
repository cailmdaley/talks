"""Read-only audit of the archived maps actually used in the cycle comparison."""
import json
import pickle
import tarfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
out={}
for cycle,universe in [('c1','tr1'),('c2','tr1_v2')]:
    out[cycle]=[]
    with tarfile.open(ROOT/f'results/{universe}/map_products/wl_shear_maps_coverage.tar') as tar:
        for name in tar.getnames():
            if not name.endswith('.pkl'):continue
            d=pickle.load(tar.extractfile(name))
            provenance=d.get('provenance')
            d=d[next(k for k in d if k.startswith('bin'))]
            print(cycle,name,'keys',list(d),'provenance',provenance,flush=True)
            for key,value in d.items():
                if not isinstance(value,(np.ndarray,list,dict)):print(key,repr(value),flush=True)
            row=dict(file=name)
            for key in ['ipix','footprint','weights','map','counts_per_pixel']:
                if key in d:
                    v=np.asarray(d[key]);row[key]=dict(shape=list(v.shape),min=float(np.min(v)),max=float(np.max(v)),sum=float(v.sum()))
            row['fsky']=float(d['fsky'])
            row['area_deg2']=float(d['fsky']*4*np.pi*(180/np.pi)**2)
            row['source_catalog']=provenance.get('source_catalog')
            row['pixel_count']=int(len(d['ipix']))
            row['weight_sum']=float(np.sum(d['weights']))
            out[cycle].append(row)
(ROOT/'results/scratch/gc8/rho/shear_input_audit.json').write_text(json.dumps(out,indent=2))
