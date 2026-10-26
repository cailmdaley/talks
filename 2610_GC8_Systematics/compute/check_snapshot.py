import json,pickle,tarfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
r=json.loads((ROOT/'results/scratch/gc8/rho/rho.json').read_text())
item=next(x for x in r['inputs'] if x['path'].endswith('tr1_v2/map_products/wl_shear_maps_coverage.tar'))
old=next(p for p in (ROOT/'.git/annex/objects').glob('*/*/*'+item['sha256']+'*/*') if p.is_file())
new=ROOT/'results/tr1_v2/map_products/wl_shear_maps_coverage.tar'
result={}
with tarfile.open(old) as a,tarfile.open(new) as b:
 for name in a.getnames():
  da=pickle.load(a.extractfile(name));db=pickle.load(b.extractfile(name));key=next(k for k in da if k.startswith('bin'))
  result[name]={k:bool(np.array_equal(v,db[key][k])) for k,v in da[key].items()}
print(json.dumps(dict(old=str(old),equal=result),indent=2))
(ROOT/'results/scratch/gc8/rho/shear_snapshot_parity.json').write_text(json.dumps(result,indent=2))
