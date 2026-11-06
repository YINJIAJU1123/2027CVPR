#!/usr/bin/env python3
"""Validate archived live trial counts and regenerate the completed-study tables."""
from pathlib import Path
from collections import Counter
from math import comb
import json, hashlib
R=Path(__file__).resolve().parents[1]
D=R/'data/cube_completed_20261101'
for line in (D/'SHA256SUMS').read_text().splitlines():
 expected,filename=line.split('  ',1)
 assert hashlib.sha256((D/filename).read_bytes()).hexdigest()==expected, filename
def read(n): return json.loads((D/n).read_text())
summaries={}
for name in ['native','waiting','feedback','goal','visual']:
 s=read(name+'_summary.json');t=read(name+'_trials.json');summaries[name]=s
 ids=None
 for c,rows in t.items():
  assert len(rows)==40 and len({r['trial_seed'] for r in rows})==40
  states={r['trial_seed']:r['initial_state_sha256'] for r in rows}
  if ids is None: ids=states
  else: assert states==ids
  o=s['outcomes'][c]
  assert sum(r['success'] for r in rows)==o['raw_success']
  assert sum(r['reason']=='drop' for r in rows)==o['raw_drops']
  assert dict(Counter(r['reason'] for r in rows))==o['raw_reasons']
  for r in rows:
   if r['success']:
    assert r['declared_goal']==r['goal_index'] and r['declared_symbol']==r['symbol']
    assert r['final_error_rad']<=0.16 and r['reason']=='success'
  eligible=[r for r in rows if r['trial_seed'] not in s['common_excluded_trial_ids']]
  assert len(eligible)==o['common_eligible_trials']
  assert sum(r['success'] for r in eligible)==o['common_eligible_success']
 assert set(s['common_excluded_trial_ids'])=={r['trial_seed'] for rows in t.values() for r in rows if r['exclusion_reason'] is not None}
 for p in s['paired_comparisons']:
  a={r['trial_seed']:r for r in t[p['left']]};b={r['trial_seed']:r for r in t[p['right']]}
  eligible=set(a)-set(p['excluded_trial_ids']);assert len(eligible)==p['eligible_trials']
  n=sum(a[i]['success'] and not b[i]['success'] for i in eligible)
  m=sum(b[i]['success'] and not a[i]['success'] for i in eligible)
  assert (n,m)==(p['left_only'],p['right_only'])
  exact=min(1.,2*sum(comb(n+m,k) for k in range(min(n,m)+1))/2**(n+m))
  assert abs(exact-p['exact_mcnemar_p'])<1e-12

macros=[]
def table(name,rows):
 body='\n'.join(' & '.join(map(str,r))+' '+chr(92)*2 for r in rows)+'\n'
 (R/'tables'/('completed_'+name+'.tex')).write_text(body)
 macros.append('\\newcommand{\\Completed'+name.title().replace('_','')+'Rows}{%\n'+body+'}')
def matched(o):return f"{o['common_eligible_success']}/{o['common_eligible_trials']}"
def rate(o):return f"{100*o['common_eligible_rate']:.1f}"
labels={'astra_full':'REVEAL','finetuned_vlm_bare':'Fine-tuned VLM, bare','rule_vlm_bare':'Rule VLM, bare'}
rows=[]
for c in ['astra_full','finetuned_vlm_bare','rule_vlm_bare']:
 o=summaries['native']['outcomes'][c];lo,hi=o['wilson_95']
 rows.append((labels[c],matched(o),rate(o),f'[{100*lo:.1f}, {100*hi:.1f}]',o['raw_drops'],o['actual_calls']))
table('native',rows)
rows=[]
for c,l in [('astra_frozen_waiting','Original waiting'),('astra_refit_waiting','Refitted waiting')]:
 o=summaries['waiting']['outcomes'][c]
 rows.append((l,matched(o),rate(o),o['raw_drops'],f"{o['raw_success']}/40"))
table('waiting',rows)
rows=[]
for c,l in [('one_initial_bounded_plan','One initial plan'),('full_feedback','Full feedback')]:
 o=summaries['feedback']['outcomes'][c];rows.append((l,matched(o),rate(o),o['actual_calls']))
table('feedback',rows)
table('goal',[(l,matched(summaries['goal']['outcomes'][c]),rate(summaries['goal']['outcomes'][c])) for c,l in [('correct_active_goal','Correct goal'),('retrained_no_explicit_goal','No explicit goal'),('shuffled_controller_goal','Shuffled goal')]])
rows=[]
for c,l in labels.items():
 values=[]
 for mode in ['identity','permuted','letter_masked']:
  o=summaries['visual']['outcomes'][c+'__'+mode]
  denom=40-o['own_service_exclusions']
  values.append(f"{o['raw_success']}/{denom}")
 rows.append((l,*values))
table('visual',rows)
c=read('cloud_decision.json')
assert c['trials']==160 and c['actual_model_calls']==0 and c['candidate_deployed'] is False
assert not any(x['passed'] for x in c['gates'].values())
table('cloud',[(l,f"{c['methods'][k]['success']}/40",c['methods'][k]['drops']) for k,l in [('original_execution','Original execution'),('fixed_residual_gate','Fixed residual gate'),('phase_fixed_residual_gate','Phase-fixed gate'),('learned_residual_gate','Learned residual gate')]])
(R/'tables/completed_macros.tex').write_text('\n'.join(macros)+'\n')
print('Verified 760 live semantic records, matched exclusions and paired tests. Kept the separate 160-trial replay development decision.')
