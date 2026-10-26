#!/usr/bin/env python3
"""Talk-only figure frames, from saved measurements."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import make_cycles as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R=st.SCRATCH/'rho';HERE=st.HERE
C=['#234979']*6+['#a8542b']*6+['#23776d']
def save(fig,name):
 fig.savefig(st.IMAGES/f'gc8r4_{name}.png',dpi=180,facecolor='white');plt.close(fig)
def axes():
 fig,ax=plt.subplots(figsize=(17,7));fig.subplots_adjust(left=.09,right=.99,bottom=.17,top=.82)
 ax.axhline(0,color=st.MUTED,lw=1)
 for x in [5.5,11.5]:ax.axvline(x,color=st.RULE)
 ax.set_xticks(range(13),st.LABELS,fontsize=29);ax.set_ylim(-.10,.235);ax.set_ylabel(r'$\bar\rho\quad(100<\ell<3000)$',fontsize=29)
 return fig,ax
def rho():
 d=st.read(R/'rho.json');l=st.read(R/'ladder.json');routes={**d['cib_route'],**l['cib_route_shear']}
 for cy in ['c1','c2']:
  for step in range(3):
   state='vis' if step==2 else 'raw';fig,ax=axes()
   for i,k in enumerate(st.TRACERS):
    v=st.row(d,cy,k,visibility=state);ax.errorbar(i-.10,v['mean_rho'],yerr=v['mean_rho_error'],fmt='o',color=C[i],capsize=4,ms=9)
    key=f'{cy}/{k}/'+(state if k[0]=='g' else 'native')
    if step and key in routes:
     v=routes[key];ax.errorbar(i+.12,v['mean_rho_pred'],yerr=v['mean_rho_pred_error'],fmt='o',mfc='white',mec=C[i],color=C[i],capsize=4,ms=9)
   handles=[Line2D([],[],marker='o',color='black',ls='none',label='Measured')]
   if step:handles.append(Line2D([],[],marker='o',mfc='white',color='black',ls='none',label='857 GHz CIB prediction (δ, γE)'))
   ax.legend(handles=handles,loc='upper left',bbox_to_anchor=(0,1.25),ncol=2,frameon=False,fontsize=26)
   fig.text(.11,.85,('With' if state=='vis' else 'Without')+' density visibility correction',fontsize=26)
   save(fig,f'rho_{cy}_{step}')
 # Same cycle ladder, raw and vis frame; same three colours, shape = processing arm.
 for state in ['raw','vis']:
  fig,ax=axes()
  for j,(key,marker,label) in enumerate([('c1_original','o','Cycle 1'),('c1_rewindowed','s','C1 + C2 template window'),('c2','^','Cycle 2')]):
   for i,k in enumerate(st.TRACERS):
    r=l['rows'][f'{k}/'+(state if k[0]=='g' else 'native')][key]
    ax.errorbar(i+(j-1)*.20,r['mean_rho'],yerr=r['mean_rho_error'],fmt=marker,color=C[i],capsize=3,ms=8)
  ax.legend(handles=[Line2D([],[],marker=m,ls='none',color='black',label=lab) for m,lab in [('o','Cycle 1'),('s','C1 + C2 template window'),('^','Cycle 2')]],ncol=3,loc='upper left',bbox_to_anchor=(0,1.25),frameon=False,fontsize=25)
  fig.text(.11,.85,('With' if state=='vis' else 'Without')+' density visibility correction · LensMC · SPT-3G',fontsize=25)
  save(fig,f'ladder_{state}')
def dust_rho():
 d=st.read(R/'rho_four_dust.json');fig,ax=axes();ax.set_ylim(-.03,.225)
 for j,(t,color,marker,label) in enumerate([('vmpz','#234979','o','VMPZ / Planck13'),('sfd','#a8542b','s','SFD'),('csfd','#23776d','^','CSFD'),('gnilc','#9751a5','D','GNILC 545 GHz')]):
  for start,end in [(0,6),(6,12),(12,13)]:
   vals=[d['rows'][f'c2/{t}/{k}/'+('vis' if k[0]=='g' else 'native')] for k in st.TRACERS[start:end]]
   ax.errorbar(np.arange(start,end)+(j-1.5)*.15,[v['mean_rho'] for v in vals],yerr=[v['mean_rho_error'] for v in vals],fmt=marker+'-',color=color,ms=7,lw=1.5,capsize=3,label=label if start==0 else None)
 ax.legend(loc='upper left',bbox_to_anchor=(0,1.25),ncol=4,frameon=False,fontsize=24);save(fig,'dust_rho')
def maps():
 import healpy as hp,pickle
 support=hp.read_map(st.SCRATCH/'union_support.fits')>0;pix=np.flatnonzero(support)
 ra,dec=hp.pix2ang(2048,pix,lonlat=True);center=np.rad2deg(np.angle(np.mean(np.exp(1j*np.deg2rad(ra)))));ra=center+(ra-center+180)%360-180
 bounds=[ra.min()-2,ra.max()+2,dec.min()-2,dec.max()+2];rg,dg=np.meshgrid(np.linspace(bounds[0],bounds[1],650),np.linspace(bounds[2],bounds[3],500));ip=hp.ang2pix(2048,rg%360,dg,lonlat=True)
 sfd=np.load(st.SCRATCH/'sfd.npy',mmap_mode='r');ref=np.asarray(sfd[pix]);ref=ref-ref.mean();rms=ref.std()
 fig,axes=plt.subplots(1,4,figsize=(17,7),sharex=True,sharey=True);fig.subplots_adjust(left=.065,right=.985,bottom=.29,top=.84,wspace=.09);stats={}
 residual=None
 for ax,t,label in zip(axes,['sfd','vmpz','csfd','gnilc'],['SFD','(Planck13 − a·SFD)/a','CSFD − SFD','(GNILC − a·SFD)/a']):
  p=R/'gnilc.npy' if t=='gnilc' else st.SCRATCH/f'{t}.npy';m=np.load(p,mmap_mode='r');v=np.asarray(m[pix]);v=v-v.mean()
  scale=1. if t in ['sfd','csfd'] else float(ref@v/(ref@ref));res=v if t=='sfd' else v-scale*ref
  img=(m[ip]-np.asarray(m[pix]).mean())/rms
  if t!='sfd':img-=scale*(sfd[ip]-np.asarray(sfd[pix]).mean())/rms
  if t not in ['sfd','csfd']:img/=scale;res/=scale
  img[~support[ip]]=np.nan
  im=ax.imshow(img,origin='lower',extent=bounds,cmap='RdBu_r',vmin=-2.5,vmax=2.5,aspect='auto');ax.set_title(label,fontsize=25);ax.set_xlabel('RA [deg]',fontsize=25);ax.tick_params(labelsize=23)
  stats[t]=dict(scale=scale,residual_over_sfd_rms=float(res.std()/rms),pearson_with_sfd=float(np.corrcoef(v,ref)[0,1]))
  if t=='csfd':residual=res
 axes[0].set_ylabel('Dec [deg]',fontsize=25);cax=fig.add_axes([.26,.14,.48,.025]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('SFD reference and calibrated residuals / SFD rms',fontsize=25);cb.ax.tick_params(labelsize=23);save(fig,'dust_residuals')
 # Quick pixel check (not harmonic rho, not a null significance).
 gc=pickle.load(open(st.ROOT/'results/tr1_v2/map_products/gc_density_maps.pkl','rb'));lookup=np.full(support.size,-1,dtype=np.int32);lookup[pix]=np.arange(len(pix));cross={}
 for k,v in gc.items():
  if not isinstance(v,dict) or 'ipix' not in v:continue
  ix=lookup[v['ipix']];ok=ix>=0
  cross[k]=float(np.corrcoef(np.asarray(v['map'])[ok],residual[ix[ok]])[0,1])
 (R/'residual_map_stats.json').write_text(json.dumps(dict(mean_subtracted=True,scale_fit='Unweighted least-squares with intercept on common support; CSFD uses a=1 by definition.',beam_matching=False,maps=stats,csfd_minus_sfd_pixel_pearson_gc=cross,caveat='Pixel Pearson only, affected by noise, beam and selection; not a harmonic correlation or significance.'),indent=2)+'\n');print(stats,cross)
if __name__=='__main__':
 st.setup_font()
 if 'maps' in sys.argv:maps()
 else:st.heatmaps();rho();dust_rho()
