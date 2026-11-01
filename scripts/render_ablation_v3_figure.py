"""Plot only the completed, audited waiting and feedback comparison."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cube_waiting_feedback_20261101'
def main():
    for line in (DATA/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest
    summary=json.loads((DATA/'summary.json').read_text())
    assert summary['status']=='completed_and_audited' and summary['raw_trials_total']==200
    groups=[('waiting',['continue','fixed_slow','learned_speed','learned_speed_residual'],['Continue','Fixed\nslowdown','Learned\nslowdown','Learned +\ncorrection']),('feedback',['initial_plan','learned_speed_residual'],['Initial plan','Full feedback'])]
    fig,axes=plt.subplots(1,2,figsize=(7,2.8),gridspec_kw={'width_ratios':[1.7,1]},sharey=True)
    fig.subplots_adjust(left=.08,right=.99,bottom=.22,top=.83,wspace=.16)
    palette={'continue':'#9299A1','fixed_slow':'#C0C5CB','learned_speed':'#6299C2','learned_speed_residual':'#255D86','initial_plan':'#9299A1'}
    for ax,(group,names,labels),title in zip(axes,groups,['(a) Control during pending requests','(b) Semantic feedback']):
        panel=summary['panels'][group];out=panel['outcomes']
        rates=np.array([out[n]['rate']*100 for n in names]);bounds=np.array([out[n]['wilson_95'] for n in names])*100
        positions=np.arange(len(names));bars=ax.bar(positions,rates,color=[palette[n] for n in names],width=.64,zorder=3)
        ax.errorbar(positions,rates,yerr=np.vstack((rates-bounds[:,0],bounds[:,1]-rates)),fmt='none',ecolor='#222222',capsize=3,lw=.9,zorder=4)
        for bar,n in zip(bars,names):
            y=out[n]['rate']*100*.27
            ax.text(bar.get_x()+bar.get_width()/2,y,f"{out[n]['success']}/{panel['eligible_trials']}",ha='center',va='center',fontsize=9,color='white' if n in ['learned_speed','learned_speed_residual'] else '#111111')
        ax.set_xticks(positions,labels,fontsize=8.5)
        ax.set_title(title,fontsize=10,pad=10)
        ax.set_ylim(0,100);ax.set_yticks([0,25,50,75,100]);ax.tick_params(axis='y',labelsize=9)
        ax.grid(axis='y',color='#E0E3E7',lw=.6,zorder=0)
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Autonomous semantic success (%)',fontsize=9)
    fig.savefig(ROOT/'figures/waiting_feedback.pdf',metadata={'CreationDate':None})
    fig.savefig(ROOT/'figures/waiting_feedback.png',dpi=220)
    plt.close(fig)
if __name__=='__main__':main()
