#!/usr/bin/env python3
"""Show each delivered null against its Gaussian error, retaining every band."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from kappa_common import ROOT

def main():
    for folder in (ROOT/'results/scratch/gc8/kappa_common').glob('tr1*'):
        records=[json.loads(p.read_text()) for p in sorted(folder.glob('*_full.json'))+sorted(folder.glob('*_common.json'))]
        if not records:continue
        fig,axs=plt.subplots(6,2,figsize=(13,17),sharex=True,constrained_layout=True)
        stems=sorted({r['template'] for r in records})
        for r in records:
            row=stems.index(r['template']);col=['full','common'].index(r['mode']);ax=axs[row,col]
            ell=np.array(r['ell']);v=np.array(r['values']);err=np.sqrt(np.diag(r['covariance']))
            ax.errorbar(ell,v/err,yerr=np.ones(len(ell)),fmt='o',ms=3,capsize=2)
            ax.axhline(0,color='k',lw=.6);ax.axhspan(-2,2,color='gray',alpha=.12);ax.set_xscale('log')
            ax.set_title(f"{r['template']} / {r['mode']} : PTE={r['pte']:.3g}")
            ax.set_ylabel('Cross / Gaussian sigma');ax.set_xlabel('Multipole ell')
        fig.suptitle(f'{folder.name} exploratory kappa nulls; full 15x15 chi-square; PTEs not mock calibrated')
        fig.savefig(folder/'bandpulls.png',dpi=135);plt.close(fig)
    folder=ROOT/'results/scratch/gc8/metacal'
    records=[json.loads(p.read_text()) for p in sorted(folder.glob('*_bin*.json'))]
    for component in ['E','B']:
        if not records:continue
        fig,axs=plt.subplots(6,6,figsize=(21,17),sharex=True,constrained_layout=True)
        stems=sorted({r['template'] for r in records})
        for r in records:
            v=r['components'][component];ax=axs[stems.index(r['template']),r['bin']-1];ell=np.array(r['ell']);pull=np.array(v['pulls'])
            ax.errorbar(ell,pull,yerr=np.ones(len(ell)),fmt='o',ms=2,capsize=1)
            ax.axhline(0,color='k',lw=.5);ax.axhspan(-2,2,color='gray',alpha=.12);ax.set_xscale('log')
            ax.set_title(f"bin {r['bin']}: PTE={v['pte']:.2g}")
            if r['bin']==1:ax.set_ylabel(r['template']+'\nCross / Gaussian sigma')
        fig.suptitle(f'Cycle-2 MetaCal {component}; exploratory; full within-test Gaussian covariance; PTEs not mock calibrated')
        fig.savefig(folder/f'bandpulls_{component}.png',dpi=125);plt.close(fig)
if __name__=='__main__':main()
