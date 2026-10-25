#!/usr/bin/env python3
"""Collect talk-only signal-normalized rho, keeping full Gaussian test blocks.

All tracer denominators use the release's fiducial signal model (GC, EE, kk),
not noisy measured autos. This avoids negative noise-subtracted EE bandpowers.
The signal model is uniformly averaged over the exact integer science bins.
Template autos are measured, CIB auto is odd x even, transfer corrected.
Errors condition on these denominators: Cov(rho)=Cov(CXT)/outer(norm,norm).
No denominator variance or covariance is propagated. No Knox approximation.
"""
import hashlib, io, json, pickle, tarfile
from pathlib import Path
import numpy as np
from scipy.stats import chi2
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'results/scratch/gc8/rho'
C1=ROOT/'results/scratch/napoli/cib_shape/products'
C2=ROOT/'results/scratch/gc8/cib_shape_c2'
RECEIPTS={}

def receipt(path):
    p=Path(path).resolve()
    key=str(p)
    if key not in RECEIPTS:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
        RECEIPTS[key]=dict(path=str(path),resolved_path=key,sha256=h.hexdigest(),bytes=p.stat().st_size)
    return RECEIPTS[key]

def load(path):
    receipt(path)
    if str(path).endswith('.pkl'):
        with open(path,'rb') as f:return pickle.load(f)
    return json.loads(Path(path).read_text())

def archive(path,name='measurement.json'):
    receipt(path)
    with tarfile.open(path) as t:return json.load(t.extractfile(name))

def vec(p,k):return np.asarray(p['cls'][k]['cl']).reshape(-1,15)[0]
def block(p,k):return np.asarray(p['cls'][k]['cov']).reshape(15,15)
def safe(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)

DEFINITION=__doc__

def row(cross,cov,xx,tt,ell,**metadata):
    cross,cov,xx,tt,ell=map(np.asarray,(cross,cov,xx,tt,ell))
    if not (np.all(xx>0) and np.all(tt>0)):raise ValueError('nonpositive normalization')
    norm=np.sqrt(xx*tt);r=cross/norm;C=cov/np.outer(norm,norm);C=(C+C.T)/2
    np.linalg.cholesky(C)
    ix=(ell>100)&(ell<3000);q=float(r[ix]@np.linalg.solve(C[np.ix_(ix,ix)],r[ix]));one=np.ones(ix.sum());invone=np.linalg.solve(C[np.ix_(ix,ix)],one)
    mean=float(invone@r[ix]/(one@invone));err=float(1/np.sqrt(one@invone))
    sig=np.sqrt(np.diag(C));pull=r/sig;j=int(np.argmax(abs(pull)))
    return dict(ell=ell,rho=r,sigma_rho=sig,covariance_rho=C,cross=cross,covariance_cross=cov,normalization=norm,tracer_signal_auto=xx,template_auto=tt,chi2=q,dof=int(ix.sum()),pte=float(chi2.sf(q,ix.sum())),mean_rho=mean,mean_rho_error=err,mean_range='100 < ell < 3000; GLS constant-rho fit, not an absolute correlation amplitude fit',worst_band=dict(ell=float(ell[j]),rho=float(r[j]),sigma_rho=float(sig[j]),signed_pull=float(pull[j])),**metadata)

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    rows={};route={}
    models={c:load(ROOT/f'results/{u}/redshift_distributions/fiducial_theory_cls.pkl') for c,u in [('c1','tr1'),('c2','tr1_v2')]}
    edges=np.unique(np.geomspace(100,3000,16).astype(int));edges[-1]=3001
    ell=np.array([(a+b-1)/2 for a,b in zip(edges[:-1],edges[1:])])
    def model(c,key):
        f,i=('k',0) if key=='kappa' else (('g',int(key[1:])+1) if key[0]=='g' else ('e',int(key[1:])+1))
        v=np.asarray(models[c]['cls'][f,f,i,i])
        return np.array([v[a:b].mean() for a,b in zip(edges[:-1],edges[1:])])
    m1=archive(ROOT/'results/tr1/tr1_systematics/extinction_vis.tar')
    v1=load(ROOT/'results/scratch/napoli/visibility_check/extinction_vis.json')
    e1=load(C1/'857_2.5e+20_gp20_cross.pkl');h1=load(C1/'857_2.5e+20_gp20_halves.pkl')
    e2=load(C2/'857_extinction.pkl');h2=load(C2/'857_halves.pkl');te2=load(C2/'extinction_tracers.pkl')
    fam=ROOT/'results/tr1_v2/systematics/gaussian_null_family.tar';receipt(fam)
    with tarfile.open(fam) as t:
        summary=json.load(t.extractfile('summary.json'));joint=np.load(io.BytesIO(t.extractfile('joint.npz').read()));obs=joint['observed'];fcov=joint['covariance']
    for c in ['c1','c2']:
        ee=vec(e1 if c=='c1' else e2,'y_y')
        for key in [f'g{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['kappa']:
            for state in (['raw','vis'] if key[0]=='g' else ['native']):
                if c=='c1':
                    d=v1['GC'][key]['before' if state=='raw' else 'after'] if key[0]=='g' else m1['WL'][key] if key[0]=='l' else m1['template_kappa']
                    cross,cov=d['cross'],d['covariance'];source='C1 extinction archive or visibility_check before/after';prescription='observed iNKA Gaussian, including measured cross Wick'
                elif state=='raw':
                    p=OUT/'c2_raw_extinction.pkl'
                    if not p.exists():continue
                    d=load(p);cross,cov=vec(d,'y_'+key),block(d,'y_'+key);source=str(p);prescription='observed iNKA Gaussian, including measured cross Wick'
                else:
                    j=summary['test_names'].index('GALACTICEXTINCTION_VIS/'+key);cross,cov=obs[j],fcov[j*15:(j+1)*15,j*15:(j+1)*15];source=str(fam);prescription='production null Gaussian: template-data Wick zero; observed auto signal+noise'
                production_null=None
                if c=='c2' and state!='raw':
                    nullcross=np.asarray(cross);nullcov=np.asarray(cov)
                    nq=float(nullcross@np.linalg.solve(nullcov,nullcross))
                    production_null=dict(chi2=nq,pte=float(chi2.sf(nq,15)),covariance_cross=nullcov,source=str(fam),prescription='zero template-data Wick Gaussian; official production null policy')
                    op=(OUT/'c2_vmpz_kappa.pkl') if key=='kappa' else C2/'extinction_tracers.pkl'
                    if op.exists():
                        observed=load(op);ck='kappa_y' if key=='kappa' else 'y_'+key
                        np.testing.assert_allclose(vec(observed,ck),cross,rtol=1e-10,atol=1e-24)
                        cov=block(observed,ck);source=str(op);prescription='observed iNKA Gaussian, including measured cross Wick; production zero-Wick null retained separately'
                rows[f'{c}/vmpz/{key}/{state}']=row(cross,cov,model(c,key),ee,ell,cycle=c,template='vmpz',tracer=key,visibility=state,source=source,covariance_prescription=prescription,production_null=production_null)
    # Public-dust GC already measured with the same native C2 windows.
    for dust in ['sfd','csfd']:
        for i in range(6):
            key=f'g{i}';p=ROOT/f'results/scratch/gc8/{dust}-bin{i+1}.json';d=load(p)
            rows[f'c2/{dust}/{key}/vis']=row(d['cl'],d['covariance_cl'],model('c2',key),d['observed_auto_template'],ell,cycle='c2',template=dust,tracer=key,visibility='vis',source=str(p),covariance_prescription='observed iNKA Gaussian; fixed-denominator rho replaces old joint-delta-method r')
        p=OUT/f'c2_{dust}_wl_kappa.pkl'
        if p.exists():
            d=load(p)
            dustauto=np.asarray(load(ROOT/f'results/scratch/gc8/{dust}-bin1.json')['observed_auto_template'])
            for key in [f'l{i}' for i in range(6)]+['kappa']:
                k='kappa_y' if key=='kappa' else 'y_'+key
                rows[f'c2/{dust}/{key}/native']=row(vec(d,k),block(d,k),model('c2',key),dustauto,ell,cycle='c2',template=dust,tracer=key,visibility='native',source=str(p),covariance_prescription='observed iNKA Gaussian, measured cross Wick')
    # CIB and the CIB-mediated prediction, each on the identical delta state.
    tb=np.asarray(load(ROOT/'results/scratch/napoli/cib_shape/interp_transfer.json')['band_mean'])
    for c,ep,hp in [('c1',e1,h1),('c2',e2,h2)]:
        ce=vec(ep,'kappa_y')/tb;Ce=block(ep,'kappa_y')/np.outer(tb,tb)
        cc=vec(hp,'kappa_y')/tb**2;Cc=block(hp,'kappa_y')/np.outer(tb**2,tb**2);ee=vec(ep,'y_y')
        for state in ['raw','vis']:
            p=(C1/f'857_2.5e+20_gp20_tracers_gc{"_raw" if state=="raw" else ""}.pkl') if c=='c1' else OUT/'c2_raw_cib857.pkl' if state=='raw' else C2/'857_tracers.pkl'
            if not p.exists():continue
            d=load(p)
            for i in range(6):
                key=f'g{i}';tc=vec(d,'y_'+key)/tb;Ct=block(d,'y_'+key)/np.outer(tb,tb);xx=model(c,key)
                ident=f'{c}/cib857/{key}/{state}'
                rows[ident]=row(tc,Ct,xx,cc,ell,cycle=c,template='cib857',tracer=key,visibility=state,source=str(p),covariance_prescription='observed iNKA Gaussian full block; CIB transfer correction retained')
                norm=np.sqrt(xx*ee);pred=tc*ce/cc/norm
                jac=[np.diag(ce/cc/norm),np.diag(tc/cc/norm),np.diag(-tc*ce/cc**2/norm)]
                Cp=sum(J@C@J.T for J,C in zip(jac,[Ct,Ce,Cc]))
                one=np.ones(15)
                measured=rows[f'{c}/vmpz/{key}/{state}'];Cm=np.asarray(measured['covariance_rho'])
                iv=np.linalg.solve(Cm,one);weights=iv/(one@iv)
                mean=float(weights@pred);err=float(np.sqrt(weights@Cp@weights))
                route[f'{c}/{key}/{state}']=dict(ell=ell,rho_pred=pred,sigma_rho_pred=np.sqrt(np.diag(Cp)),covariance_rho_pred=Cp,rho_delta_cib=tc/np.sqrt(xx*cc),rho_cib_ext=ce/np.sqrt(cc*ee),mean_rho_pred=mean,mean_rho_pred_error=err,measured_key=f'{c}/vmpz/{key}/{state}',compression_weights=weights,definition='rho_pred=rho(delta,CIB)*rho(CIB,ext); mean uses EXACT SAME GLS weights as the measured extinction mean, not an independent prediction-weighted mean. Independent full Gaussian blocks for three numerator spectra; their mutual cross-covariance and denominator scatter omitted. No residual chi2/PTE claimed.')
    # Hash original inputs of the reused public-dust rotation, plus direct source products.
    for p in [ROOT/'results/tr1_v2/map_products/gc_density_maps.pkl',ROOT/'results/tr1_v2/map_products/wl_shear_maps_coverage.tar',ROOT/'results/tr1/map_products/gc_density_maps.pkl',ROOT/'results/scratch/napoli/visibility_check/corrected.pkl',ROOT/'results/tr1_v2/systematics/template_bundle.tar',ROOT/'results/tr1/tr1_systematics/template_bundle.tar',ROOT/'results/scratch/gc8/run_dust.py',Path(__file__),Path(__file__).with_name('rho_missing.py'),Path(__file__).with_name('rho_plot.py')]:
        if p.exists():receipt(p)
    for dust in ['sfd','csfd']:receipt(Path('/leonardo_work/EUHPC_E07_074/cmbx/inputs/external/dust')/f'{dust}_ebv.fits');receipt(ROOT/f'results/scratch/gc8/{dust}.npy')
    kr=ROOT/'results/tr1_v2/survey/kappa.json';mr=ROOT/'results/tr1_v2/map_products/pair_apodized_masks.json'
    kd=load(kr);md=load(mr);receipt(kd['map']['path']);receipt(Path(md['root'])/next(x['path'] for x in md['files'] if x['path'].endswith('_apod_mask.fits')))
    receipt(ROOT/'results/scratch/gc8/union_support.fits')
    for p in Path(__file__).parent.glob('rho_*.py'):receipt(p)
    data=dict(definition=DEFINITION,exploratory=True,normalization='All XX are fiducial release-specific signal models, uniformly averaged on exact integer science bins. No shot/shape/reconstruction noise in denominator. TT is measured dust auto, or Lenz odd x even for CIB. Errors keep denominator fixed.',caveats=['C1 systematics operators retain their legacy response/window convention; C2 uses production response/window corrections. This is a release comparison, not an isolated template change.','All final comparison rows use observed Gaussian Wick terms; archived C2 zero-cross-Wick production null blocks and statistics are retained separately as production_null. A missing c2_vmpz_kappa.pkl temporarily falls back to the production-null block, explicitly labelled.','GLS mean assumes constant rho; it summarizes bands, never substitutes for the null chi2 or worst-band check.','No cross-state, cross-cycle, cross-template or prediction-measurement covariance: visual differences are not difference significances.','C2 raw reconstructs counts/mean(counts)-1 on the SAME supported catalogue pixels, removes selection mask weights; the removed visibility-excluded area is not restored.','No matched-mock calibration.'],rows=rows,cib_route=route,inputs=list(RECEIPTS.values()))
    (OUT/'rho.json').write_text(json.dumps(data,default=safe,indent=2,allow_nan=False)+'\n')
    for k,r in rows.items():print(k,f'mean {r["mean_rho"]:+.6f} +/- {r["mean_rho_error"]:.6f}; chi2 {r["chi2"]:.3f}/15 PTE {r["pte"]:.4g}; worst {r["worst_band"]}')
    print('Rows',len(rows),'routes',len(route))
if __name__=='__main__':main()
