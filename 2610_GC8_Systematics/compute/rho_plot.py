#!/usr/bin/env python3
"""Candidate slide layouts; read rho.json, never change science inputs."""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2];OUT=ROOT/'results/scratch/gc8/rho'
spec=importlib.util.spec_from_file_location('style',HERE/'make_cycles.py');style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
style.setup_font();plt.rcParams.update({'font.size':23,'axes.labelsize':29,'xtick.labelsize':23,'ytick.labelsize':23,'legend.fontsize':22})
x=json.loads((OUT/'rho.json').read_text());D=x['rows'];P=x['cib_route'];colors=plt.cm.viridis(np.linspace(.08,.92,6))
keys=[f'g{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['kappa']
labels=[rf'$\delta_{{{i}}}$' for i in range(1,7)]+[rf'$\gamma_{{E,{i}}}$' for i in range(1,7)]+[r'$\kappa_{\rm SPT}$']

def get(c,d,t,state=None):return D.get(f'{c}/{d}/{t}/{state or ("vis" if t.startswith("g") else "native")}')
def save(fig,name):
    fig.savefig(OUT/name,dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)
def finish(ax):ax.axhline(0,color='#535B67',lw=1,zorder=0);ax.grid(axis='y',alpha=.15)
def point(ax,xx,r,**kw):
    if r:ax.errorbar(xx,r['mean_rho'],yerr=r['mean_rho_error'],capsize=4,elinewidth=1.8,ms=8,**kw)

def a(dust='vmpz'):
    entries=[get(c,'vmpz',k) for c in ['c1','c2'] for k in keys]+[get('c2',d,k) for d in ['sfd','csfd'] for k in keys]
    ymin=min(min(np.array(r['rho'])-np.array(r['sigma_rho'])) for r in entries if r);ymax=max(max(np.array(r['rho'])+np.array(r['sigma_rho'])) for r in entries if r)
    for c in (['c1','c2'] if dust=='vmpz' else ['c2']):
        fig,axes=plt.subplots(1,3,figsize=(18,6.2),sharex=True,sharey=True,gridspec_kw={'wspace':.16})
        for ax,group,lab in zip(axes,[keys[:6],keys[6:12],keys[12:]],[r'$\delta$',r'$\gamma_E$',r'$\kappa_{\rm SPT}$']):
            finish(ax)
            for i,k in enumerate(group):
                r=get(c,dust,k)
                if not r:continue
                ax.errorbar(np.array(r['ell'])*(1+(i-2.5)*.006),r['rho'],yerr=r['sigma_rho'],color=colors[i] if len(group)>1 else '#3B4E85',fmt='o-',ms=3.5,lw=1,elinewidth=1.1,capsize=2,alpha=.9)
            ax.set_xscale('log');ax.set_xlabel(r'$\ell$');ax.set_xlim(100,3000);ax.set_ylim(ymin-.02,ymax+.02);ax.text(.07,.92,lab,transform=ax.transAxes,fontsize=31)
            ax.set_xticks([100,300,1000,3000],labels=['100','300','1000','3000'])
            ax.tick_params(axis='x',labelsize=21)
            ticks=ax.get_xticklabels();ticks[0].set_ha('left');ticks[-1].set_ha('right')
        axes[0].set_ylabel(r'$\rho_\ell$')
        fig.legend([Line2D([],[],marker='o',color=colors[i],lw=1) for i in range(6)],[f'Bin {i+1}' for i in range(6)],ncol=6,loc='upper center',bbox_to_anchor=(.5,1.07),frameon=False)
        save(fig,f'A_spectra_{c}.png' if dust=='vmpz' else f'A_spectra_{dust}_{c}.png')

def b1():
    fig,ax=plt.subplots(figsize=(17,6));finish(ax)
    for j,(c,color,mark,label) in enumerate([('c1','#355D91','o','Cycle 1'),('c2','#BB4B39','s','Cycle 2')]):
        for i,k in enumerate(keys):point(ax,i+(j-.5)*.20,get(c,'vmpz',k),color=color,fmt=mark,label=label if i==0 else None)
    ax.set_xticks(range(13),labels);ax.set_ylabel(r'$\bar\rho\ (100<\ell<3000)$');ax.legend(frameon=False,loc='upper left',ncol=2)
    ax.axvline(5.5,color='#C6CEDA');ax.axvline(11.5,color='#C6CEDA');save(fig,'B1_cycles.png')

def b2(dust='vmpz'):
    fig,axes=plt.subplots(1,2,figsize=(15,5.8),sharey=True,gridspec_kw={'wspace':.08})
    for ax,c in zip(axes,['c1','c2']):
        finish(ax)
        for j,(state,col,mark,lab) in enumerate([('raw','#A85535','o','Without visibility'),('vis','#296A8A','s','With visibility')]):
            for i in range(6):point(ax,i+(j-.5)*.16,get(c,dust,f'g{i}',state),color=col,fmt=mark,label=lab if i==0 else None)
        ax.set_xticks(range(6),labels[:6]);ax.text(.03,.92,'Cycle 1' if c=='c1' else 'Cycle 2',transform=ax.transAxes)
    axes[0].set_ylabel(r'$\bar\rho\ (100<\ell<3000)$')
    fig.legend([Line2D([],[],marker='o',color='#A85535',lw=0),Line2D([],[],marker='s',color='#296A8A',lw=0)],['Without visibility','With visibility'],frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(.5,1.06),fontsize=22)
    save(fig,f'B2_visibility_{dust}.png')

def b3():
    fig,ax=plt.subplots(figsize=(17,6));finish(ax)
    for j,(dust,color,mark,label) in enumerate([('vmpz','#3B4E85','o','VMPZ extinction'),('sfd','#BD6635','s','SFD'),('csfd','#299078','^','CSFD')]):
        for i,k in enumerate(keys):point(ax,i+(j-1)*.19,get('c2',dust,k),color=color,fmt=mark,label=label if i==0 else None)
    ax.set_xticks(range(13),labels);ax.set_ylabel(r'$\bar\rho\ (100<\ell<3000)$');ax.legend(frameon=False,ncol=3,loc='upper left')
    ax.axvline(5.5,color='#C6CEDA');ax.axvline(11.5,color='#C6CEDA');save(fig,'B3_dust_maps_c2.png')

def route():
    fig,axes=plt.subplots(2,2,figsize=(14,10),sharex=True,sharey=True,gridspec_kw={'hspace':.1,'wspace':.08})
    for row,state in enumerate(['raw','vis']):
        for col,c in enumerate(['c1','c2']):
            ax=axes[row,col];finish(ax)
            for i in range(6):
                r=get(c,'vmpz',f'g{i}',state);point(ax,i-.08,r,color='#3B4E85',fmt='o',label='Measured extinction' if i==0 else None)
                p=P.get(f'{c}/g{i}/{state}')
                if p:ax.errorbar(i+.08,p['mean_rho_pred'],yerr=p['mean_rho_pred_error'],fmt='s',color='#BD6635',ms=8,capsize=4,label='CIB-route prediction' if i==0 else None)
            ax.set_xticks(range(6),labels[:6]);ax.text(.03,.90,f'Cycle {col+1}, '+('without visibility' if state=='raw' else 'with visibility'),transform=ax.transAxes,fontsize=21)
    axes[0,0].set_ylabel(r'$\bar\rho$');axes[1,0].set_ylabel(r'$\bar\rho$');axes[1,1].legend(frameon=False,loc='lower right',fontsize=19)
    save(fig,'B2_cib_route.png')
def route_spectra():
    for c in ['c1','c2']:
        for state in ['raw','vis']:
            fig,axes=plt.subplots(2,3,figsize=(17,9),sharex=True,sharey=True,gridspec_kw={'wspace':.08,'hspace':.12})
            for i,ax in enumerate(axes.flat):
                finish(ax);r=get(c,'vmpz',f'g{i}',state);p=P.get(f'{c}/g{i}/{state}')
                ax.set_xscale('log');ax.set_xlim(100,3000);ax.text(.96,.88,labels[i],transform=ax.transAxes,fontsize=29,ha='right')
                for value,error,color,marker,label in [(r['rho'],r['sigma_rho'],'#3B4E85','o','Extinction'),(p['rho_pred'],p['sigma_rho_pred'],'#BD6635','s','CIB prediction')] if p else []:
                    ax.errorbar(r['ell'],value,yerr=error,fmt=marker+'-',color=color,ms=4,lw=1.1,elinewidth=1.2,capsize=2,label=label)
                ax.set_xticks([100,300,1000,3000],labels=['100','300','1000','3000']);ax.tick_params(axis='x',labelsize=21)
                ticks=ax.get_xticklabels()
                if ticks:ticks[0].set_ha('left');ticks[-1].set_ha('right')
            axes[0,0].set_ylabel(r'$\rho_\ell$');axes[1,0].set_ylabel(r'$\rho_\ell$')
            for ax in axes[1,:]:ax.set_xlabel(r'$\ell$')
            axes[0,0].legend(frameon=False,fontsize=19,loc='lower left')
            save(fig,f'route_spectra_{c}_{state}.png')

if __name__=='__main__':a();a('sfd');a('csfd');b1();b2();b2('cib857');b3();route();route_spectra()
