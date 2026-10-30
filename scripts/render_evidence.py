#!/usr/bin/env python3
"""Regenerate figures and result tables from the frozen cube records."""
from pathlib import Path
import json, math, hashlib
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cube_v1'
a=json.loads((DATA/'addendum_summary.json').read_text())
p=json.loads((DATA/'parent_summary.json').read_text())
trials=json.loads((DATA/'trials.json').read_text())
assert len(trials)==400 and len({(t['condition'],t['trial_seed']) for t in trials})==400
for c,summary in a['conditions'].items():
 rows=[t for t in trials if t['condition']==c]
 assert len(rows)==40 and sum(bool(t['success']) for t in rows)==summary['success']
main=a['main_system_comparison']; ab=p['astra_waiting_execution_factorial']
for panel in [main,ab]:
 excluded={int(x) for x in panel['excluded_trial_seeds']}
 for c,o in panel['outcomes'].items():
  rows=[t for t in trials if t['condition']==c and t['trial_seed'] not in excluded]
  assert len(rows)==o['eligible_trials'] and sum(bool(t['success']) for t in rows)==o['success']
names={'astra_full':'Astra + learned control (ours)','finetuned_vlm_bare':'Fine-tuned VLM (bare)','rule_vlm_bare':'Rule VLM (bare)'}
def drop(s):return sum(v for k,v in s['failure_subtypes'].items() if k.startswith('drop'))
rows=[]
for c in ['rule_vlm_bare','finetuned_vlm_bare','astra_full']:
 s=a['conditions'][c];o=main['outcomes'][c];lo,hi=o['wilson_95']
 rows.append(f"{names[c]} & {o['success']}/39 & {100*o['success_rate']:.1f} & [{100*lo:.1f}, {100*hi:.1f}] & {s['success']}/40 & {drop(s)} \\")
(ROOT/'tables/main_rows.tex').write_text('\n'.join(r+'\\' for r in rows)+'\n')
rows=[]
for c,w,e in [('fixed_slow_no_execution_recovery','Fixed 0.15','Student'),('learned_waiting_only','Learned','Student'),('learned_execution_only_with_fixed_slow_waiting','Fixed 0.15','Learned'),('astra_full','Learned','Learned')]:
 s=p['semantic_conditions'][c];o=ab['outcomes'][c]
 rows.append(f"{w} & {e} & {s['success']}/40 & {drop(s)} & {o['success']}/37 & {100*o['success_rate']:.1f} \\")
(ROOT/'tables/ablation_rows.tex').write_text('\n'.join(r+'\\' for r in rows)+'\n')
dev=json.loads((ROOT/'data/student_adaptation_dev/summary.json').read_text())
dev_trials=json.loads((ROOT/'data/student_adaptation_dev/trials.json').read_text())
rows=[]
for c,label in [('released_student','Released pose-goal student'),('frozen_latent_student','Frozen latent student'),('simulated_extra_dagger','Latent + simulated-noise DAgger'),('cnn_extra_dagger','Latent + CNN-feedback DAgger')]:
    o=dev['conditions'][c]
    rr=[t for t in dev_trials if t['condition']==c]
    assert len(rr)==40 and sum(bool(t['reached_before_drop']) for t in rr)==o['reach']
    rows.append(f"{label} & {o['reach']}/40 & {o['drops']} " + chr(92)*2)
(ROOT/'tables/student_rows.tex').write_text('\n'.join(rows)+'\n')
macros=[]
for filename, macro in [('main_rows','MainResultRows'),('ablation_rows','AblationResultRows'),('student_rows','StudentResultRows')]:
    body=(ROOT/'tables'/f'{filename}.tex').read_text()
    macros.append('\\newcommand{\\'+macro+'}{%\n'+body+'}')
(ROOT/'tables/result_macros.tex').write_text('\n'.join(macros)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(7.0,2.45),gridspec_kw={'width_ratios':[1,1.15]},layout='constrained')
labels=['Rule VLM','Fine-tuned VLM','Astra + control']; colors=['#a8adb6','#35959b','#304f81']
vals=[main['outcomes'][c] for c in ['rule_vlm_bare','finetuned_vlm_bare','astra_full']]
for i,(o,col) in enumerate(zip(vals,colors)):
 y=o['success_rate']*100;lo,hi=[v*100 for v in o['wilson_95']]
 axes[0].barh(i,y,color=col,height=.55)
 axes[0].errorbar(y,i,xerr=[[y-lo],[hi-y]],color='#20252a',capsize=3,lw=1)
 axes[0].text(1,i,f"{o['success']}/39",va='center',color='white',weight='bold',fontsize=9)
axes[0].set_yticks(range(3),labels);axes[0].set_xlim(0,100);axes[0].set_xlabel('Eligible success (%)');axes[0].set_title('(a) Complete systems',loc='left',weight='bold',fontsize=10)
# Raw failure context is deliberately not pooled with eligible success.
contexts=['Before first skill','Unbound inspection','Wrong bound goal','Correct bound goal']
counts=[[a['conditions'][c]['failure_contexts'].get(k,0) for k in ['before_first_skill','inspection_without_binding','wrong_bound_goal','correct_bound_goal']] for c in ['rule_vlm_bare','finetuned_vlm_bare','astra_full']]
for j,(label,col) in enumerate(zip(contexts,['#c0c5cc','#4e7095','#d49c55','#63a99b'])):
 left=[sum(r[:j]) for r in counts];values=[r[j] for r in counts]
 axes[1].barh(range(3),values,left=left,color=col,height=.55,label=label)
 for i,(l,v) in enumerate(zip(left,values)):
  if v:axes[1].text(l+v/2,i,str(v),ha='center',va='center',fontsize=9)
axes[1].set_yticks(range(3),labels);axes[1].set_xlim(0,17);axes[1].set_xlabel('Drops / 40 raw trials');axes[1].set_title('(b) Where drops occur',loc='left',weight='bold',fontsize=10)
for ax in axes:
 ax.spines[['top','right']].set_visible(False);ax.invert_yaxis();ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
axes[1].legend(loc='upper center',bbox_to_anchor=(.45,-.29),ncol=2,frameon=False,fontsize=7)
fig.savefig(ROOT/'figures/cube_results.pdf',bbox_inches='tight');fig.savefig(ROOT/'figures/cube_results.png',dpi=170,bbox_inches='tight');plt.close(fig)
# Method figure is a schematic, not an experimental image.
fig,ax=plt.subplots(figsize=(13.5,5));ax.set_xlim(0,13.5);ax.set_ylim(0,5);ax.axis('off')
def box(x,y,w,h,title,body,color):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07,rounding_size=0.08',facecolor=color,edgecolor='#5e6d7a',lw=.9))
 ax.text(x+w/2,y+h-.28,title,ha='center',va='center',weight='bold',fontsize=11,color='#182d40')
 ax.text(x+w/2,y+h/2-.12,body,ha='center',va='center',fontsize=9.4,linespacing=1.35)
def arrow(x1,y1,x2,y2):ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color='#40586c',lw=1.3))
box(.2,3.1,2.5,1.55,'Visual task','RGB + requested letter\n“Present the T face”','#edf1f6')
box(3.35,3.1,4.0,1.55,'Asynchronous semantic agent','Inspect → bind target → verify\nValidated public actions → 768D goal','#dce8f6')
box(8,3.1,2.5,1.55,'Request state','Pending flag + elapsed time\nRequest anchor + active goal','#f5e8d7')
box(.2,.6,2.5,1.55,'Frozen pose CNN','RGB → 9 keypoints\nCalibrated current pose','#e0eeea')
box(3.35,.6,4.0,1.55,'Recurrent latent student','Proprioception + measured pose + goal\n21 joint-target proposals','#e0eeea')
box(8,.6,2.5,1.55,'Learned local control','Waiting actor / execution actor\nSpeed + bounded residual','#dce8f6')
box(11.1,.6,2.1,1.55,'Revo3 hand','Physics continues\nMeasured stop gate','#edf1f6')
for pts in [(2.7,3.85,3.35,3.85),(7.35,3.85,8,3.85),(1.45,3.1,1.45,2.15),(2.7,1.38,3.35,1.38),(5.35,3.1,5.35,2.15),(7.35,1.38,8,1.38),(9.25,3.1,9.25,2.15),(10.5,1.38,11.1,1.38)]:arrow(*pts)
ax.plot([12.15,12.15,11.6,11.6,1.45,1.45],[2.15,4.85,4.85,4.95,4.95,4.65],color='#40586c',lw=1.1)
ax.text(9.6,4.8,'New visual evidence',ha='center',fontsize=8.5)
ax.text(6.7,.12,'Privileged teacher labels are used only for training. Online control has no true object pose or future response.',ha='center',fontsize=9,color='#425365')
fig.savefig(ROOT/'figures/method.pdf',bbox_inches='tight');fig.savefig(ROOT/'figures/method.png',dpi=160,bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(6.6,2.3),layout='constrained')
for i,ax in enumerate(axs,1):
 ax.imshow(plt.imread(ROOT/f'assets/cube_trial183101000_request{i:02d}.png'),interpolation='nearest');ax.set_title(f'Request {i}',fontsize=10);ax.axis('off')
fig.savefig(ROOT/'figures/observations.pdf',bbox_inches='tight');fig.savefig(ROOT/'figures/observations.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('Verified 400 unique records and regenerated two result tables and three figures.')
