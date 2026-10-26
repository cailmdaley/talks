#!/usr/bin/env python3
"""Presentation-only four-template maps, rho means and GNILC band checks."""
import json
import sys
from pathlib import Path
import numpy as np
import healpy as hp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import make_cycles as style
ROOT = style.ROOT
OUT = ROOT / 'results/scratch/gc8/rho'
style.setup_font()
TEMPLATES = [('vmpz', 'VMPZ / Planck13', '#234979', 'o'), ('sfd', 'SFD', '#a8542b', 's'), ('csfd', 'CSFD', '#23776d', '^'), ('gnilc', 'GNILC 545 GHz', '#9751a5', 'D')]

def save(fig, name):
    for p in [OUT / name, style.IMAGES / ('gc8r3_'+name)]:
        fig.savefig(p, dpi=180, facecolor='white')
    plt.close(fig)

def maps():
    support = hp.read_map(ROOT / 'results/scratch/gc8/union_support.fits') > 0
    pix = np.flatnonzero(support)
    ra, dec = hp.pix2ang(2048, pix, lonlat=True)
    center = np.rad2deg(np.angle(np.mean(np.exp(1j*np.deg2rad(ra)))))
    ra = center + (ra-center+180)%360-180
    bounds = [ra.min()-2, ra.max()+2, dec.min()-2, dec.max()+2]
    xx = np.linspace(bounds[0],bounds[1],650); yy = np.linspace(bounds[2],bounds[3],500)
    rg,dg = np.meshgrid(xx,yy); ip = hp.ang2pix(2048,rg%360,dg,lonlat=True)
    fig,axes = plt.subplots(1,4,figsize=(17,6.5),sharex=True,sharey=True)
    fig.subplots_adjust(left=.065,right=.985,bottom=.30,top=.84,wspace=.08)
    stats = {}
    for ax,(name,title,_,_) in zip(axes,TEMPLATES):
        m = np.load(OUT/'gnilc.npy' if name=='gnilc' else ROOT/f'results/scratch/gc8/{name}.npy')
        vals=m[pix]; med=np.median(vals); rms=np.std(vals)
        image=(m[ip]-med)/rms; image[~support[ip]]=np.nan
        im=ax.imshow(image,origin='lower',extent=bounds,cmap='magma',vmin=-1,vmax=3,aspect='auto',interpolation='nearest')
        ax.set_title(title,fontsize=25); ax.set_xlabel('RA [deg]',fontsize=25); ax.tick_params(labelsize=22)
        stats[name]=dict(median=float(med),pixel_rms=float(rms),quantile_02_98=np.quantile(vals,[.02,.98]).tolist())
    axes[0].set_ylabel('Dec [deg]',fontsize=25)
    cax=fig.add_axes([.27,.14,.46,.025]);cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[-1,0,1,2,3]);cb.ax.tick_params(labelsize=20);cb.set_label('(map − footprint median) / pixel rms',fontsize=23)
    (OUT/'map_comparison_stats.json').write_text(json.dumps(dict(projection='Equatorial plate carree; identical grid, support and colour scale; per-map median and rms; no beam matching',bounds=bounds,maps=stats),indent=2))
    save(fig,'dust_footprint_c2.png')

def rho():
    rows=json.loads((OUT/'rho_four_dust.json').read_text())['rows']
    fig,ax=plt.subplots(figsize=(17,6.5));fig.subplots_adjust(left=.09,right=.99,bottom=.18,top=.85)
    ax.axhline(0,color='#535B67',lw=1);ax.grid(axis='y',alpha=.15)
    for j,(name,label,color,marker) in enumerate(TEMPLATES):
        rs=[rows[f'c2/{name}/{k}/'+('vis' if k[0]=='g' else 'native')] for k in style.TRACERS]
        ax.errorbar(np.arange(13)+(j-1.5)*.18,[r['mean_rho'] for r in rs],yerr=[r['mean_rho_error'] for r in rs],fmt=marker,ms=8,capsize=3,color=color,label=label)
    ax.set_xticks(range(13),style.LABELS);ax.set_ylabel(r'$\bar\rho\quad(100<\ell<3000)$',fontsize=29)
    ax.axvline(5.5,color='#C6CEDA');ax.axvline(11.5,color='#C6CEDA');ax.legend(loc='upper left',bbox_to_anchor=(0,1.17),ncol=4,frameon=False,fontsize=24)
    save(fig,'B3_dust_maps_c2.png')
    fig,axes=plt.subplots(1,3,figsize=(17,6.5),sharex=True,sharey=True);fig.subplots_adjust(left=.08,right=.99,bottom=.17,top=.84,wspace=.12)
    for ax,keys,title in zip(axes,[style.TRACERS[:6],style.TRACERS[6:12],style.TRACERS[12:]],[r'$\delta$',r'$\gamma_E$',r'$\kappa_{\rm SPT}$']):
        ax.axhline(0,color='#535B67',lw=1);ax.set_title(title);ax.set_xscale('log');ax.set_xlim(100,3000);ax.set_xlabel(r'$\ell$');ax.set_xticks([100,300,1000,3000],['100','300','1000','3000']);ax.tick_params(labelsize=21)
        ticks=ax.get_xticklabels();ticks[0].set_ha('left');ticks[-1].set_ha('right')
        for i,k in enumerate(keys):
            r=rows[f'c2/gnilc/{k}/'+('vis' if k[0]=='g' else 'native')]
            ax.errorbar(np.asarray(r['ell'])*(1+(i-2.5)*.005),r['rho'],yerr=r['sigma_rho'],fmt='o-',ms=3,lw=1,color=style.COLORS[i],label=f'Bin {i+1}' if len(keys)>1 else 'SPT')
    axes[0].set_ylabel(r'$\rho_\ell$')
    handles,labs=axes[0].get_legend_handles_labels()
    fig.legend(handles,labs,ncol=6,fontsize=22,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.0))
    save(fig,'gnilc_spectra_c2.png')

if __name__=='__main__':
    maps() if sys.argv[1]=='maps' else rho()
