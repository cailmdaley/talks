#!/usr/bin/env python3
"""Talk-only redraws of saved evidence; no production writes or spectral transforms."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import make_cycles as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
NB=st.SCRATCH/'newbins'  # Cycle 2 on the 26 Oct official-bin catalogues; C1 rows carried unchanged
R=NB/'rho'; W=st.SCRATCH/'window-leakage'  # template support identical across bin versions, so the template autos carry over
BAND_COLORS=[plt.get_cmap('plasma')(x) for x in np.linspace(0,.82,6)]  # bin 1 (low z) → bin 6 (high z)
KAPPA_COLOR='#23776d'
RHO_LABEL=r'$\bar\rho_{X,\,\rm ext}$'
def save(fig,name):
 fig.savefig(st.IMAGES/f'gc8r5_{name}.png',dpi=170,facecolor='white');plt.close(fig)
def bands():
 d=st.read(R/'rho.json'); allrows={}
 for cy in ['c1','c2']:
  for sh in ['lensmc','metacal']:
   for cm in ['spt','act']:
    rows=[]
    if cy=='c1':
     u='tr1'+('_act' if cm=='act' else '')+('_metacal' if sh=='metacal' else '')
     folder=st.ROOT/f'results/{u}/tr1_systematics'
     p=folder/'extinction_vis.tar'
     if not p.exists():p=folder/'extinction_vis_act.tar'
     m=st.archive(p)
     rows=[st.row(d,cy,f'g{i}',visibility='raw') for i in range(6)]+[m['WL'][f'l{i}'] for i in range(6)]+[m['template_kappa']]
    else:
     rows=[st.row(d,cy,f'g{i}',visibility='raw') for i in range(6)]
     rows += [st.row(d,cy,f'l{i}') if sh=='lensmc' else {**st.read(NB/f'metacal/GALACTICEXTINCTION_VIS_bin{i+1}.json')['components']['E'],'ell':st.row(d,cy,f'l{i}')['ell']} for i in range(6)]
     rows += [st.row(d,cy,'kappa') if cm=='spt' else st.read(NB/'kappa_common/tr1_v2_act/GALACTICEXTINCTION_VIS_full.json')]
    allrows[f'{cy}_{sh}_{cm}']=rows
 lim=max(float(np.max(np.abs(np.asarray(v.get('cross',v.get('values'))) / np.sqrt(np.diag(v.get('covariance_cross',v.get('covariance'))))))) for rows in allrows.values() for v in rows)+1.4
 for key,rows in allrows.items():
  fig,axes=plt.subplots(1,3,figsize=(18,7),sharex=True,sharey=True);fig.subplots_adjust(left=.075,right=.985,top=.80,bottom=.17,wspace=.13)
  for ax,ids,label in zip(axes,[range(6),range(6,12),range(12,13)],[r'$\delta$',r'$\gamma_E$',r'$\kappa$']):
   ax.axhspan(-1,1,color='#edf0f4');ax.axhline(0,color=st.MUTED,lw=1)
   for j,i in enumerate(ids):
    v=rows[i];c=np.asarray(v.get('cross',v.get('values')));cov=np.asarray(v.get('covariance_cross',v.get('covariance')));y=c/np.sqrt(np.diag(cov))
    ax.errorbar(np.asarray(v['ell'])*(1+(j-2.5)*.016),y,yerr=np.ones(15),fmt='o-',color=BAND_COLORS[j] if i<12 else KAPPA_COLOR,ms=4,lw=1.1,capsize=2,elinewidth=.8)
   ax.set_xscale('log');ax.set_xlim(100,3000);ax.set_ylim(-lim,lim);ax.set_xticks([100,300,1000,3000],['100','300','1000','3000']);ax.get_xticklabels()[0].set_ha('left');ax.get_xticklabels()[-1].set_ha('right');ax.tick_params(labelsize=24);ax.set_xlabel(r'$\ell$',fontsize=30);ax.set_title(label,fontsize=34,loc='left')
  axes[0].set_ylabel(r'$C_\ell^{X\,\rm ext}/\sigma_\ell$',fontsize=30)
  fig.legend([Line2D([],[],color=BAND_COLORS[i],marker='o',lw=1) for i in range(6)],['Bin 1 (low $z$)']+[f'Bin {i+1}' for i in range(1,5)]+['Bin 6 (high $z$)'],ncol=6,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.0),fontsize=24,handletextpad=.4,columnspacing=1.6)
  save(fig,'bands_'+key)
 print('band sigma limits',lim)
def rho():
 import round4_figures as r4
 d=st.read(R/'rho.json');l=st.read(R/'ladder.json');routes={**d['cib_route'],**l['cib_route_shear']}
 for cy in ['c1','c2']:
  for pred in [False,True]:
   fig,ax=r4.axes();fig.set_size_inches(17,5.7);fig.subplots_adjust(left=.08,right=.99,bottom=.17,top=.84);ax.set_ylabel(RHO_LABEL,fontsize=29)
   for i,k in enumerate(st.TRACERS):
    v=st.row(d,cy,k);ax.errorbar(i-.06,v['mean_rho'],yerr=v['mean_rho_error'],fmt='o',color=r4.C[i],capsize=4,ms=9)
    p=routes.get(f'{cy}/{k}/'+('raw' if k[0]=='g' else 'native'))
    if p and pred:ax.errorbar(i+.06,p['mean_rho_pred'],yerr=p['mean_rho_pred_error'],fmt='o',mfc='white',color=r4.C[i],capsize=4,ms=9)
   hs=[Line2D([],[],marker='o',ls='none',color='black',label='Measured')]+([Line2D([],[],marker='o',mfc='white',color='black',ls='none',label='CIB-predicted (δ, γE)')] if pred else [])
   ax.legend(handles=hs,loc='upper left',bbox_to_anchor=(0,1.25),ncol=2,frameon=False,fontsize=26)
   save(fig,'rho_'+cy+('_pred' if pred else ''))
 d=st.read(R/'rho_four_dust.json');fig,ax=r4.axes();ax.set_ylabel(RHO_LABEL,fontsize=29);entries=[]
 for j,(t,col,m,lab) in enumerate([('vmpz','#234979','o','VMPZ / Planck13'),('sfd','#a8542b','s','SFD'),('csfd','#23776d','^','CSFD')]):
  for a,b in [(0,6),(6,12),(12,13)]:
   vals=[d['rows'][f'c2/{t}/{k}/'+('vis' if k[0]=='g' else 'native')] for k in st.TRACERS[a:b]];entries+=vals
   ax.errorbar(np.arange(a,b)+(j-1)*.18,[v['mean_rho'] for v in vals],yerr=[v['mean_rho_error'] for v in vals],fmt=m+'-',color=col,ms=8,lw=1.5,capsize=3,label=lab if a==0 else None)
 lo=min(v['mean_rho']-v['mean_rho_error'] for v in entries);hi=max(v['mean_rho']+v['mean_rho_error'] for v in entries);ax.set_ylim(lo-.015,hi+.015)
 ax.legend(loc='upper left',bbox_to_anchor=(0,1.25),ncol=3,frameon=False,fontsize=26);save(fig,'dust_rho')
def window():
 """Main-deck window slide: frame 1 Cycle 1 alone, frame 2 adds Cycle 2, on fixed axes."""
 d=st.read(R/'rho.json');a=st.read(W/'auto.json')
 cyc=[('c1','#234979','Cycle 1'),('c2','#a8542b','Cycle 2')]
 rows={cy:st.row(d,cy,'g5') for cy,_,_ in cyc}
 def cross(cy):
  v=rows[cy];ell=np.asarray(v['ell']);ok=ell>300
  return ell[ok],(ell**2*np.asarray(v['cross']))[ok]*1e3,(ell**2*np.sqrt(np.diag(v['covariance_cross'])))[ok]*1e3
 ell_a=np.asarray(a['ell'])
 auto={cy:ell_a**2*np.asarray(a['tests'][cy+'_original']['values'])*1e3 for cy,_,_ in cyc}
 ymax_a=1.08*max(v.max() for v in auto.values())
 lo=min((c-e).min() for c,e in [cross(cy)[1:] for cy,_,_ in cyc]);hi=max((c+e).max() for c,e in [cross(cy)[1:] for cy,_,_ in cyc])
 for n in [1,2]:
  fig,axes=plt.subplots(1,2,figsize=(18,7));fig.subplots_adjust(left=.075,right=.985,bottom=.17,top=.84,wspace=.22)
  for cy,col,lab in cyc[:n]:
   axes[0].plot(ell_a,auto[cy],'o-',color=col,lw=2.2,ms=7,label=lab)
   l,c,e=cross(cy);axes[1].fill_between(l,c-e,c+e,color=col,alpha=.25,lw=0);axes[1].plot(l,c,'o-',color=col,lw=2.2,ms=7)
  axes[0].set_ylim(0,ymax_a);axes[1].set_ylim(min(0,lo)-.05*(hi-lo),hi+.05*(hi-lo));axes[1].axhline(0,color=st.MUTED,lw=1)
  axes[0].set_ylabel(r'$\ell^2 C_\ell^{\,\rm ext\,ext}$  [$10^{-3}$ mag$^2$]',fontsize=29);axes[0].set_title('Extinction auto',fontsize=30)
  axes[1].set_ylabel(r'$\ell^2 C_\ell^{\,\rm ext\,\delta_6}$  [$10^{-3}$ mag]',fontsize=29);axes[1].set_title(r'Extinction $\times\ \delta_6$, $\pm1\sigma$',fontsize=30)
  for ax in axes:
   ax.set_xscale('log');ax.set_xlabel(r'$\ell$',fontsize=30);ax.tick_params(labelsize=24)
  axes[0].set_xticks([100,300,1000,3000],['100','300','1000','3000'])
  axes[1].set_xlim(320,3000);axes[1].set_xticks([400,1000,3000],['400','1000','3000'])
  from matplotlib.ticker import NullFormatter
  for ax in axes:ax.xaxis.set_minor_formatter(NullFormatter())
  hs=[Line2D([],[],color=col,marker='o',lw=2.2,label=lab) for _,col,lab in cyc[:n]]
  fig.legend(handles=hs,loc='upper center',ncol=2,frameon=False,fontsize=27)
  save(fig,f'window_step{n}')
def window_cycles():
 """Backup window slide: Cycle 1 and Cycle 2, each on its own template window."""
 d=st.read(R/'rho.json');a=st.read(W/'auto.json');fig,axes=plt.subplots(1,2,figsize=(18,7));fig.subplots_adjust(left=.085,right=.985,bottom=.17,top=.84,wspace=.25)
 for cy,col,lab in [('c1','#234979','Cycle 1'),('c2','#a8542b','Cycle 2')]:
  axes[0].plot(a['ell'],a['tests'][cy+'_original']['values'],'o-',color=col,label=lab)
  v=st.row(d,cy,'g5');ell=np.asarray(v['ell']);ok=ell>300;axes[1].errorbar(ell[ok],(1e6*ell*np.asarray(v['cross']))[ok],yerr=(1e6*ell*np.sqrt(np.diag(v['covariance_cross'])))[ok],fmt='o-',color=col,capsize=3)
 axes[0].set_yscale('log');axes[0].set_ylabel(r'$C_\ell^{ext\,ext}$ [mag$^2$]',fontsize=29);axes[0].set_title('Extinction auto',fontsize=29)
 axes[1].set_ylabel(r'$\ell C_\ell^{ext\,\delta_6}$ [$10^{-6}$ mag]',fontsize=29);axes[1].set_title(r'Extinction × raw $\delta_6$ · $\ell>300$',fontsize=29);axes[1].axhline(0,color=st.MUTED,lw=1)
 for ax in axes:
  ax.set_xscale('log');ax.set_xlabel(r'$\ell$',fontsize=30);ax.set_xticks([100,300,1000,3000],['100','300','1000','3000']);ax.tick_params(labelsize=24)
 axes[1].set_xlim(320,3000);axes[1].set_xticks([400,1000,3000],['400','1000','3000'])
 from matplotlib.ticker import NullFormatter
 axes[1].xaxis.set_minor_formatter(NullFormatter());axes[1].get_xticklabels()[-1].set_ha('right')
 fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,fontsize=27);save(fig,'window_cycles')
def rho_vis():
 """Slide-5 ρ̄ steps: visibility-corrected δ (with native γE, κ) per cycle, then Cycle 2 with δ before correction added."""
 import round4_figures as r4
 d=st.read(R/'rho.json');AFTER,BEFORE='#234979','#d0702c'
 vals=[st.row(d,cy,k,visibility=vs) for cy in ['c1','c2'] for vs in ['vis','raw'] for k in st.TRACERS]
 lo=min(v['mean_rho']-v['mean_rho_error'] for v in vals);hi=max(v['mean_rho']+v['mean_rho_error'] for v in vals)
 for cy,raw in [("c1",False),("c2",False),("c1",True),("c2",True)]:
  fig,ax=r4.axes();fig.set_size_inches(17,5.7);fig.subplots_adjust(left=.08,right=.99,bottom=.17,top=.84);ax.set_ylabel(RHO_LABEL,fontsize=29);ax.set_ylim(lo-.015,hi+.015)
  for i,k in enumerate(st.TRACERS):
   v=st.row(d,cy,k,visibility='vis');ax.errorbar(i-(.09 if raw and i<6 else 0),v['mean_rho'],yerr=v['mean_rho_error'],fmt='o',color=AFTER,capsize=4,ms=9)
   if raw and i<6:
    v=st.row(d,cy,k,visibility='raw');ax.errorbar(i+.09,v['mean_rho'],yerr=v['mean_rho_error'],fmt='o',color=BEFORE,capsize=4,ms=9)
  hs=[Line2D([],[],marker='o',ls='none',color=AFTER,label='With visibility correction')]+([Line2D([],[],marker='o',ls='none',color=BEFORE,label='Before visibility correction')] if raw else [])
  ax.legend(handles=hs,loc='upper left',bbox_to_anchor=(0,1.25),ncol=2,frameon=False,fontsize=26)
  save(fig,f'rho_vis_{cy}'+('_raw' if raw else ''))
 for cy in ['c1','c2']:
  for k in st.TRACERS[:6]:
   a,b=st.row(d,cy,k,visibility='vis'),st.row(d,cy,k,visibility='raw');print(cy,k,'vis %.4f±%.4f raw %.4f±%.4f'%(a['mean_rho'],a['mean_rho_error'],b['mean_rho'],b['mean_rho_error']))
def maps():
 import healpy as hp
 # Read prepared bundle arrays, preserving their distinct supports. Restore only
 # the removed monopole, using the exact common-pixel source mean from the audit.
 arrays=[];masks=[];base=W
 for cy in [1,2]:
  p=base/f'bundle{cy}/bundle';arrays.append(np.load(p/'GALACTICEXTINCTION_VIS.npy',mmap_mode='r'));masks.append(np.load(p/'GALACTICEXTINCTION_VIS.mask.npy',mmap_mode='r').astype(bool))
 common=masks[0]&masks[1];audit=json.loads((Path.home()/'loom/.felt/science/cmbx/gc8-systematics-update/extinction-provenance/stats.json').read_text());offsets=[audit['c1_mean']-float(np.mean(v[common],dtype=np.float64)) for v in arrays]
 union=masks[0]|masks[1];pix=np.flatnonzero(union);ra,dec=hp.pix2ang(2048,pix,lonlat=True);center=np.rad2deg(np.angle(np.mean(np.exp(1j*np.deg2rad(ra)))));ra=center+(ra-center+180)%360-180
 bounds=[ra.min()-1,ra.max()+1,dec.min()-1,dec.max()+1];rg,dg=np.meshgrid(np.linspace(bounds[0],bounds[1],1100),np.linspace(bounds[2],bounds[3],850));ip=hp.ang2pix(2048,rg%360,dg,lonlat=True)
 cmap=plt.get_cmap('magma').copy();cmap.set_bad('white');rmap=plt.get_cmap('RdBu_r').copy();rmap.set_bad('white')
 for i in range(2):
  img=np.asarray(arrays[i][ip],dtype=float)+offsets[i];img[~masks[i][ip]]=np.nan
  fig,ax=plt.subplots(figsize=(9,8));fig.subplots_adjust(left=.14,right=.96,bottom=.20,top=.92);im=ax.imshow(img,origin='lower',extent=bounds,cmap=cmap,vmin=0,vmax=.18,aspect='auto');ax.set_title(f'Cycle {i+1}',fontsize=30);ax.set_axis_off()
  cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.03,fraction=.055,extend='max');cb.set_label(r'$A_{\rm VIS}$ [mag]',fontsize=27);cb.ax.tick_params(labelsize=23);save(fig,f'map_c{i+1}')
 # Matched E(B-V) units, with an affine local SFD calibration for Planck.
 support=masks[1];pix=np.flatnonzero(support);sfd=np.load(st.SCRATCH/'sfd.npy',mmap_mode='r');csfd=np.load(st.SCRATCH/'csfd.npy',mmap_mode='r');ref=np.asarray(sfd[pix]);v=np.asarray(arrays[1][pix])+offsets[1];slope=float((ref-ref.mean())@(v-v.mean())/np.sum((ref-ref.mean())**2));intercept=float(v.mean()-slope*ref.mean())
 absolute=(arrays[1][ip]+offsets[1])/2.108
 residual=((arrays[1][ip]+offsets[1]-intercept)/slope-sfd[ip]);cres=csfd[ip]-sfd[ip]
 fig,axes=plt.subplots(1,3,figsize=(18,7.7),sharex=True,sharey=True);fig.subplots_adjust(left=.07,right=.985,bottom=.29,top=.86,wspace=.14)
 for ax,img,title,cm,lo,hi in zip(axes,[absolute,residual,cres],['VMPZ (Planck 2013)','VMPZ − SFD','CSFD − SFD'],[cmap,rmap,rmap],[0,-.006,-.002],[.085,.006,.002]):
  img=np.asarray(img,dtype=float);img[~support[ip]]=np.nan;im=ax.imshow(img,origin='lower',extent=bounds,cmap=cm,vmin=lo,vmax=hi,aspect='auto');ax.set_title(title,fontsize=28);ax.set_axis_off();cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.03,fraction=.05,extend='both');cb.set_label('E(B−V) [mag]',fontsize=25);cb.ax.tick_params(labelsize=22)
 # Trim unused canvas below the colourbars, preserving all map/axis content.
 fig.savefig(st.IMAGES/'gc8r5_dust_maps.png',dpi=170,facecolor='white',bbox_inches='tight',pad_inches=.12);plt.close(fig)
 receipt=dict(offsets_mag=offsets,bounds=bounds,absolute_AVIS_stretch=[0,.18],calibration=dict(slope_AVIS_per_SFD=slope,intercept_AVIS=intercept,VMPZ_absolute='AVIS / 2.108',residual='(AVIS - intercept) / slope - SFD',CSFD='CSFD - SFD; original SFD calibration'),residual_stretches_EBV=[[-.006,.006],[-.002,.002]],support_pixels=[int(x.sum()) for x in masks],common_pixels=int(common.sum()))
 (st.SCRATCH/'round5-map-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
if __name__=='__main__':
 st.setup_font()
 if 'maps' in sys.argv:maps()
 elif "r8" in sys.argv:window_cycles();rho_vis()
 else:bands();rho();window();window_cycles();rho_vis()
