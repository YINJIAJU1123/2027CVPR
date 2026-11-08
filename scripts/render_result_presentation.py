"""Render descriptive Q2 outcomes and a compact Q4 pose table from frozen counts."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
controller = json.loads((ROOT/'data/controller_three_seed_20261107/summary.json').read_text())
pose = json.loads((ROOT/'data/pose_occlusion_20261101/summary.json').read_text())
n = controller['trials_per_condition']
assert n == 120 and controller['seed_ids'] == [187102,187103,187104]
keys = ['success','waiting_drop','execution_drop','other_failure']
colors = ['#88ACCB','#E1B27F','#CB8D8A','#E1E4E8']
legend = ['Success','Waiting drop','Execution drop','Other failure']
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','DejaVu Serif'],
                     'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.linewidth':0.5})
fig, ax = plt.subplots(figsize=(3.35,1.74))
fig.subplots_adjust(left=0.35,right=0.95,bottom=0.24,top=0.77)
labels = ['Continue student','Fixed slowing','Learned slowing','Slowing + correction']
for y,method in enumerate(controller['methods']):
    counts = method['combined']
    assert sum(counts.values()) == n
    left = 0
    for key,color in zip(keys,colors):
        width = 100*counts[key]/n
        ax.barh(y,width,left=left,height=.65,color=color,edgecolor='white',linewidth=.5,zorder=3)
        if key=='success':
            ax.text(width/2,y,f'{width:.1f}%',ha='center',va='center',fontsize=8,
                    color='#182C3D',weight='bold' if y==3 else 'normal',zorder=4)
        left += width
    assert abs(left-100)<1e-9
ax.set_yticks(range(4),labels,fontsize=8)
ax.get_yticklabels()[-1].set_weight('bold')
ax.invert_yaxis(); ax.set_xlim(0,100)
ax.set_xticks([0,25,50,75,100]); ax.set_xlabel('Share of trials (%)',fontsize=8,labelpad=2)
ax.tick_params(axis='y',length=0,pad=4)
ax.tick_params(axis='x',length=2,width=.5,labelsize=8,pad=2)
ax.set_axisbelow(True); ax.xaxis.grid(True,color='#E4E8ED',linewidth=.5)
for side in ('top','right','left'):ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color('#9CA8B4')
handles = [Patch(facecolor=c,edgecolor='none',label=l) for c,l in zip(colors,legend)]
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.51,1.015),ncol=2,
           frameon=False,fontsize=8,handlelength=1.1,handleheight=.7,columnspacing=1.1,
           labelspacing=.3,handletextpad=.4)
for ext in ('pdf','svg','png'):
    fig.savefig(ROOT/f'figures/controller_outcomes.{ext}',dpi=300,facecolor='white')
plt.close(fig)

rows=[]
for model,label in [('rgb','RGB'),('rgbd','RGB-D')]:
    m=pose['metrics'][model]
    assert round(100*m['successes']/pose['frames'],2)==m['recall_percent']
    values=[label,f"{m['recall_percent']:.2f}",f"{m['strict_recall_percent']:.2f}",str(m['invalid'])]
    if model=='rgbd':values=[r'\textbf{'+v+'}' for v in values]
    rows.append(' & '.join(values)+r'\\')
text = r'''\begin{table}[t]
\centering\small
\begin{tabular}{lrrr}
\toprule
Estimator & \multicolumn{2}{c}{Pose recall (\%) $\uparrow$} & Invalid $\downarrow$\\
\cmidrule(lr){2-3}
 & 10\,mm / 10$^\circ$ & 5\,mm / 5$^\circ$ & \\
\midrule
'''+ '\n'.join(rows)+'\n'+r'''\bottomrule
\end{tabular}
\caption{\textbf{Q4: independent pose estimation.} Recall requires both errors below the listed thresholds. All 6,144 simulated observations remain in the denominator, including invalid predictions. Evaluation uses ideal masks and virtual depth.}
\label{tab:pose-summary}
\end{table}
'''
(ROOT/'tables/pose_summary.tex').write_text(text)
print('Rendered Q2 outcomes from 480 unchanged trials and Q4 table from 6,144 pose observations.')
