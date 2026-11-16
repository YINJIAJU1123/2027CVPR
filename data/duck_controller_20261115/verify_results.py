"""Verify the standalone green-mug Q2 release."""
import argparse, json, math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parent
MODES=('continue','fixed_slow','learned_speed','full')
def load(name):
    p=Path(name)
    if not p.is_absolute() and not p.exists(): p=ROOT/p
    return json.loads(p.read_bytes())
def check(x,msg):
    if not x: raise ValueError(msg)
def paired(rows,method,ref):
    c=Counter((r[method]['success'] is True,r[ref]['success'] is True) for r in rows)
    both,wins,losses,neither=(c[k] for k in ((True,True),(True,False),(False,True),(False,False)))
    n=wins+losses; tail=sum(math.comb(n,j) for j in range(min(wins,losses)+1))
    return (both,wins,losses,neither),min(1.0,2*tail/2**n)
def holm(items):
    previous=0.0
    for i,(raw,adj) in enumerate(sorted(items)):
        previous=max(previous,min(1.0,(len(items)-i)*raw)); check(math.isclose(previous,adj),'Holm-adjusted p value')
def verify(path='q2/final_results.json'):
    report=load(path); release=load('q2/frozen_schedule.json'); rows=report['trial_rows']; modes=release['conditions']
    planned={(int(seed),item['index'],item['mode']) for seed,order in release['schedule'].items() for item in order}
    observed={(r['seed'],r['case'],r['mode']) for r in rows}
    check(len(rows)==len(observed)==480 and observed==planned,'frozen schedule')
    by_trial=defaultdict(dict)
    for r in rows: by_trial[r['trial_seed']][r['mode']]=r
    check(len(by_trial)==120 and all(set(x)==set(modes) for x in by_trial.values()),'complete quartets')
    all_cases=list(by_trial.values()); common=[c for c in all_cases if all(c[m]['exclusion'] is None for m in modes)]
    exact=[c for c in common if len({c[m]['first_image_sha256'] for m in modes})==1]
    check((len(common),len(exact))==(117,111),'common and exact RGB panels')
    check(sum(r['exclusion'] is None for r in rows)==report['observed_physical_endpoints']==477,'physical endpoints')
    for name,cases in [('primary_all_scheduled',all_cases),('common_service_eligible',common),('common_service_and_exact_rgb',exact)]:
        summary=report[name]; check(len(cases)==summary['paired_initial_states'],'denominator')
        family=[]
        for mode in modes:
            rs=Counter(c[mode]['reason'] for c in cases); ds=Counter(c[mode]['drop_phase'] for c in cases if c[mode]['reason']=='drop')
            stats=summary['by_method'][mode]
            check(rs==+Counter(stats['reasons']) and rs['success']==stats['success'],'outcomes')
            check(ds==+Counter(stats['drop_stages']),'drop stages')
        for contrast in summary['full_contrasts']:
            counts,p=paired(cases,'full',contrast['reference'])
            check(counts==tuple(contrast[k] for k in ('both_success','full_only','reference_only','both_fail')),'paired table')
            check(math.isclose(p,contrast['two_sided_exact_mcnemar']),'McNemar p')
            family.append((p,contrast['holm_three_full_contrasts']))
        check(len(family)==3,'contrast family'); holm(family)
    for seed,arms in report['by_seed'].items():
        for mode,stats in arms.items():
            group=[r for r in rows if r['seed']==int(seed) and r['mode']==mode]
            check(len(group)==stats['n']==40 and sum(r['success'] is True for r in group)==stats['success'],'seed split')
    print(f'Q2: {len(rows)} scheduled slots, 477 physical endpoints, {len(common)} common quartets, {len(exact)} exact-RGB quartets verified.')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--q2-report',default='q2/final_results.json'); verify(ap.parse_args().q2_report)
