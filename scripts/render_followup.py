#!/usr/bin/env python3
"""Validate separate follow-up cohorts and write only their labeled tables."""
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/cube_followup_20261030'
read=lambda n:json.loads((D/n).read_text())
def table(name,rows):
 (ROOT/'tables'/name).write_text('\n'.join(' & '.join(map(str,r))+' '+chr(92)*2 for r in rows)+'\n')
r=read('replication_complete.json');trials={c:{int(k):v for k,v in rows.items()} for c,rows in r['trials'].items()}
common=set.intersection(*(set(d) for d in trials.values()));eligible={k for k in common if all(d[k]['exclusion_reason'] is None for d in trials.values())}
assert len(common)==40 and len(eligible)==37 and sorted(common-eligible)==r['excluded_slots']
assert all(len({d[k]['initial_state_sha256'] for d in trials.values()})==1 for k in common)
rows=[]
for c,label in [('astra_full','Astra full'),('finetuned_vlm_bare','Fine-tuned VLM, bare'),('rule_vlm_bare','Rule VLM, bare')]:
 n=sum(trials[c][k]['success'] for k in eligible);assert n==r['methods'][c]['matched_success']
 rows.append((label,f'{n}/{len(eligible)}',f'{100*n/len(eligible):.1f}'))
table('followup_replication_rows.tex',rows)
m=read('module_effects.json');parent=json.loads((ROOT/'data/cube_v1/parent_summary.json').read_text());old=json.loads((ROOT/'data/cube_v1/trials.json').read_text());exclude=set(m['excluded_trial_seeds']);rows=[]
for c,w,e in [('fixed_slow_no_execution_recovery','Fixed','Student'),('learned_waiting_only','Learned','Student'),('learned_execution_only_with_fixed_slow_waiting','Fixed','Learned'),('astra_full','Learned','Learned')]:
 records=[x for x in old if x['condition']==c and int(x['trial_seed']) not in exclude];v=m['conditions'][c];n=sum(x['success'] for x in records)
 assert len(records)==37 and n==v['success']==parent['astra_waiting_execution_factorial']['outcomes'][c]['success']
 drops=Counter(x['drop_phase'] for x in records if x['reason']=='drop');assert dict(drops)==v['drops_by_phase']
 rows.append((w,e,f'{n}/37',drops['startup_wait'],drops['wait'],drops['execution']))
table('followup_phase_rows.tex',rows)
v=read('visual_interventions.json');rows=[]
for provider,label in [('finetuned_vlm_bare','Fine-tuned VLM'),('rule_vlm_bare','Rule VLM')]:
 counts=[];initial=None
 for mode in ('identity','permuted','letter_masked'):
  c=provider+'__'+mode;records=v['trials'][c];assert len(records)==len({x['trial_seed'] for x in records})==40
  assert all(x['exclusion_reason'] is None for x in records)
  states={x['trial_seed']:x['initial_state_sha256'] for x in records}
  if initial is None:initial=states
  else:assert states==initial
  n=sum(x['success'] for x in records);assert n==v['conditions'][c]['success'];counts.append(f'{n}/40')
 rows.append((label,*counts))
table('followup_visual_rows.tex',rows)
b=read('visual_binding_audit.json');binding_rows=[]
assert b['initial_states_matched']
for provider,label in [('finetuned_vlm_bare','Fine-tuned'),('rule_vlm_bare','Rule')]:
 for mode,layout in [('identity','Identity'),('permuted','Permuted'),('letter_masked','Masked')]:
  name=provider+'__'+mode;g=b['groups'][name];records=g['records'];c=g['counts']
  assert len(records)==g['trials']==40
  original={x['trial_seed']:x for x in v['trials'][name]}
  assert len(original)==40 and set(original)=={x['trial_seed'] for x in records}
  for x in records:
   assert x['success']==original[x['trial_seed']]['success'] and x['reason']==original[x['trial_seed']]['reason']
   assert x['goal_index']==original[x['trial_seed']]['goal_index'] and x['requested_symbol']==original[x['trial_seed']]['symbol']
  first=Counter(x['first_binding'] for x in records)
  assert sum(first.values())==40
  assert all(first[k]==c.get('first_binding_'+k,0) for k in ('correct','wrong','none'))
  legacy=sum(x['any_legacy_mapping'] for x in records)
  assert legacy==c['any_legacy_mapping']
  assert sum(x['success'] for x in records)==c['success']==v['conditions'][name]['success']
  binding_rows.append((label,layout,first['correct'],first['wrong'],first['none'],legacy if mode=='permuted' else '--'))
table('followup_visual_binding_rows.tex',binding_rows)
p=read('paired_recovery.json');assert p['verified_states']==19 and p['planned_states']==20
rows=[]
for c,label in [('active','Explicit actor goal'),('center','No explicit actor goal')]:
 d=p['conditions'][c];assert d['branches']==38;rows.append((label,f"{d['final_within_tolerance_count']}/38",d['drop_count']))
table('followup_pair_rows.tex',rows)
print('Verified 120 complete replication records, 240 visual trials and their applied-binding audit, existing 37-slot factorial, and 19-state recovery scope.')

macros=[]
for name,macro in [('followup_phase_rows','FollowupPhaseRows'),('followup_replication_rows','FollowupReplicationRows'),('followup_pair_rows','FollowupPairRows'),('followup_visual_rows','FollowupVisualRows'),('followup_visual_binding_rows','FollowupVisualBindingRows')]:
 body=(ROOT/'tables'/(name+'.tex')).read_text()
 macros.append(chr(92)+'newcommand{'+chr(92)+macro+'}{%\n'+body+'}')
(ROOT/'tables/followup_macros.tex').write_text('\n'.join(macros)+'\n')
