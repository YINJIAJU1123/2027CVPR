"""Attribute completed bare-VLM image interventions using archived applied calls.

Read-only analysis. Retains every trial and never redefines task success.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(a,b):
 n=a+b
 return min(1.,2*sum(math.comb(n,k) for k in range(min(a,b)+1))/2**n) if n else 1.


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--study',type=Path,required=True)
 p.add_argument('--reference',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 reference=read(a.reference);symbols=['T','E','R','L','S','H']
 groups={};sources={};initial={}
 for provider,prefix in [('finetuned_vlm_bare','vlm'),('rule_vlm_bare','rule')]:
  for mode in ('identity','permuted','letter_masked'):
   name=provider+'__'+mode;records=[]
   for seed in (183441,183442):
    run=a.study/'runs'/name/f'{prefix}_{seed}'
    assert read(run.with_suffix('.validity.json'))['physical_log_valid']
    result=read(run/'result.json');assert result['status']=='completed' and result['recorded_episodes']==20
    manifest=read(run/'manifest.json');mapping=manifest['visual_intervention']['face_to_symbol_index']
    assert mapping==([1,2,3,4,5,0] if mode=='permuted' else list(range(6)))
    path=run/'episodes.jsonl';relative=str(path.relative_to(a.study));digest=sha(path)
    assert reference['evidence'][relative]==digest
    sources[relative]=digest
    rows=[json.loads(x) for x in path.read_text().splitlines()]
    assert len(rows)==20
    for row in rows:
     trial=row['trial_seed'];goal=row['goal_index'];symbol=row['symbol']
     assert row['exclusion_reason'] is None and symbol==symbols[mapping[goal]]
     if trial in initial:assert initial[trial]==row['initial_state']
     else:initial[trial]=row['initial_state']
     cp=run/f"episode_{row['episode']:03d}"/'calls.json';calls=read(cp)
     sources[str(cp.relative_to(a.study))]=sha(cp)
     assert len(calls)==row['actual_model_calls'] and row['replayed_calls']==0
     accepted=[]
     for call in calls:
      assert call['error'] is None
      if call.get('applied_step') is None or not call['result']['accepted']:continue
      skill=call['result']['skill'];assert isinstance(skill,int) and 0<=skill<6
      accepted.append(dict(call=call['call'],skill=skill,correct=skill==goal,
                           legacy_mapping=mode=='permuted' and skill==symbols.index(symbol),
                           applied_step=call['applied_step']))
     last=accepted[-1]['skill'] if accepted else None
     assert last==row['declared_goal']
     assert row['declared_symbol']==(symbol if accepted else None)
     if row['success']:assert last==goal and row['final_error_rad']<=.16
     correct=[i for i,c in enumerate(accepted) if c['correct']]
     wrong=[i for i,c in enumerate(accepted) if not c['correct']]
     terminal='unbound' if last is None else 'correct_binding' if last==goal else 'wrong_binding'
     records.append(dict(trial_seed=trial,goal_index=goal,requested_symbol=symbol,
      success=row['success'],reason=row['reason'],terminal_binding=terminal,
      accepted_calls=accepted,first_binding=('none' if not accepted else 'correct' if accepted[0]['correct'] else 'wrong'),
      any_correct=bool(correct),any_wrong=bool(wrong),
      wrong_then_correct=bool(wrong and correct and min(wrong)<max(correct)),
      correct_then_wrong=bool(wrong and correct and min(correct)<max(wrong)),
      any_legacy_mapping=any(c['legacy_mapping'] for c in accepted),
      terminal_legacy_mapping=bool(accepted and accepted[-1]['legacy_mapping']),
      raw_calls=len(calls)))
   assert len(records)==40 and len({r['trial_seed'] for r in records})==40
   counts=Counter()
   for row in records:
    counts['success']+=row['success'];counts['raw_calls']+=row['raw_calls']
    counts['accepted_calls']+=len(row['accepted_calls'])
    counts['wrong_accepted_calls']+=sum(not c['correct'] for c in row['accepted_calls'])
    counts['legacy_mapping_calls']+=sum(c['legacy_mapping'] for c in row['accepted_calls'])
    counts['first_binding_'+row['first_binding']]+=1
    counts['terminal_'+row['terminal_binding']]+=1
    for key in ('any_correct','any_wrong','wrong_then_correct','correct_then_wrong','any_legacy_mapping','terminal_legacy_mapping'):
     counts[key]+=row[key]
    if not row['success']:counts[row['reason']+'__'+row['terminal_binding']]+=1
   assert counts['success']==reference['conditions'][name]['success']
   groups[name]=dict(trials=40,counts=dict(counts),records=records)
 contrasts=[]
 for provider in ('finetuned_vlm_bare','rule_vlm_bare'):
  identity={r['trial_seed']:r for r in groups[provider+'__identity']['records']}
  for mode in ('permuted','letter_masked'):
   altered={r['trial_seed']:r for r in groups[provider+'__'+mode]['records']}
   assert set(identity)==set(altered)
   win=sum(identity[k]['success'] and not altered[k]['success'] for k in identity)
   lose=sum(altered[k]['success'] and not identity[k]['success'] for k in identity)
   contrasts.append(dict(provider=provider,left='identity',right=mode,identity_only=win,intervention_only=lose,
                         exact_mcnemar_p=exact(win,lose),scope='Exploratory paired task-success comparison, no multiplicity correction'))
 output=dict(scope='Archived bare-VLM semantic binding audit; no new trials',groups=groups,contrasts=contrasts,
  initial_states_matched=True,reference_sha256=sha(a.reference),source_sha256=sha(Path(__file__)),evidence_sha256=sources,
  limitations=['A single fixed permutation does not establish general compositionality.',
   'Legacy mapping means the accepted color matches the original color for the requested symbol. This is behavioral evidence, not proof of a memorization mechanism.',
   'Calls after the first observe different trajectories. Call-level counts are correlated.',
   'Final wrong binding and physical control failures can interact; terminal categories are descriptive, not causal.',
   'Letter-masked inputs remove task information. Chance successes do not establish visual grounding.',
   'REVEAL intervention arms remain pending and are not included.'])
 a.output.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({name:g['counts'] for name,g in groups.items()},indent=2))
 print(json.dumps(contrasts,indent=2))


if __name__=='__main__':main()
