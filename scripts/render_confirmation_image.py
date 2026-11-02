"""Recompute tables from the immutable 200-trial confirmation/image snapshot."""
import hashlib,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cube_confirmation_image_refresh_20261102'
NAMES={'confirm_continue':'Continue student','confirm_fixed':'Fixed slowdown','confirm_full':'Learned speed + correction','image_fresh':'Current image','image_frozen':'Repeated first frame'}
def read(name):return json.loads((DATA/name).read_text())
def exact(a,b):
    n=a+b
    return min(1.,2*sum(math.comb(n,i) for i in range(min(a,b)+1))/2**n)
def main():
    expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (DATA/'SHA256SUMS').read_text().splitlines()}
    actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.iterdir() if p.is_file() and p.name!='SHA256SUMS'}
    assert expected==actual,'Frozen evidence modified'
    s=read('summary.json');trials=read('trials.json');assert s['status']=='completed_and_audited' and s['raw_trials_total']==200
    assert set(trials)==set(NAMES)
    allrows=[];phases=[];images=[];maps={}
    for group,panel in s['panels'].items():
        assert panel['matched_initial_physics'] and panel['matched_first_rgb']
        excluded=set(panel['excluded_trial_ids'])
        assert excluded==({187101004} if group=='confirmation' else set())
        for name,out in panel['outcomes'].items():
            rows=trials[name];assert len(rows)==40 and len({r['trial_seed'] for r in rows})==40
            assert all(r['success']==(r['reason']=='success') for r in rows)
            eligible=[r for r in rows if r['trial_seed'] not in excluded]
            maps[name]={r['trial_seed']:r for r in eligible}
            assert sum(r['success'] for r in rows)==out['raw_success']
            assert len(eligible)==out['eligible_trials'] and sum(r['success'] for r in eligible)==out['success']
            assert sum(r['reason']=='drop' for r in eligible)==out['drops']
            assert sum(r['actual_model_calls'] for r in rows)==out['calls']
            assert math.isclose(out['rate'],out['success']/out['eligible_trials'])
            phases_actual=Counter(r['drop_phase'] for r in eligible if r['reason']=='drop')
            assert dict(phases_actual)==out['drop_phases']
            values=[NAMES[name],f"{out['raw_success']}/40",f"{out['success']}/{out['eligible_trials']}",f"{100*out['rate']:.1f}",str(out['drops']),str(out['calls']),f"{out['tokens']['total_tokens']:,}"]
            allrows.append(' & '.join(values)+r'\\')
            if group=='confirmation':
                phases.append(' & '.join([NAMES[name]]+[str(out['drop_phases'].get(k,0)) for k in ['startup_wait','wait','execution']]+[str(out['drops'])])+r'\\')
            else:
                images.append(' & '.join([NAMES[name],values[2],values[3],values[4],values[5]])+r'\\')
    for comparison in s['primary']+s['secondary']:
        a,b=maps[comparison['left']],maps[comparison['right']];assert a.keys()==b.keys()
        ao=sum(a[k]['success'] and not b[k]['success'] for k in a)
        bo=sum(b[k]['success'] and not a[k]['success'] for k in a)
        assert (ao,bo)==(comparison['left_only'],comparison['right_only'])
        assert math.isclose(exact(ao,bo),comparison['exact_mcnemar_p'])
    ordered=sorted(s['primary'],key=lambda x:x['exact_mcnemar_p']);running=0
    for i,c in enumerate(ordered):
        running=max(running,min(1,(len(ordered)-i)*c['exact_mcnemar_p']))
        assert math.isclose(running,c['holm_adjusted_p'])
    macros=[]
    for name,rows in [('ImageRefreshRows',images),('ConfirmationImageRows',allrows),('ConfirmationPhaseRows',phases)]:
        macros.append('\\newcommand{\\'+name+'}{%\n'+'\n'.join(rows)+'\n}\n')
    (ROOT/'tables/confirmation_image_macros.tex').write_text(''.join(macros))
    print('Verified frozen hashes, all 200 records, exclusions, counts, phases and paired tests; rendered tables.')
if __name__=='__main__':main()
