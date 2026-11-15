"""Render Q2/Q3 only from the fully audited 200-trial public snapshot."""
import hashlib,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cube_waiting_feedback_20261101'
NAMES={'continue':'Continue student','fixed_slow':'Fixed slowdown','learned_speed':'Learned slowdown','learned_speed_residual':'Slowing + correction','initial_plan':'One initial plan'}
def read(n):return json.loads((DATA/n).read_text())
def pct(x):return f'{100*x:.1f}'
def pvalue(x):return f'{x:.3g}'
def main():
    summary=read('summary.json');trials=read('trials.json')
    assert summary['status']=='completed_and_audited' and summary['raw_trials_total']==200
    assert summary['physical_initial_states_match'] and set(trials)==set(NAMES)
    for condition,rows in trials.items():
        assert len(rows)==40 and len({r['trial_seed'] for r in rows})==40
        assert all(r['success']==(r['reason']=='success') for r in rows)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.iterdir() if p.is_file() and p.name!='SHA256SUMS'}
    expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (DATA/'SHA256SUMS').read_text().splitlines()}
    assert manifest==expected,'Public evidence changed'
    tables=ROOT/'tables';tables.mkdir(exist_ok=True)
    macros=[]
    for group in ('waiting','feedback'):
        panel=summary['panels'][group];rows=[]
        for name,outcome in panel['outcomes'].items():
            ids=set(panel['excluded_trial_ids']);eligible=[r for r in trials[name] if r['trial_seed'] not in ids]
            assert len(eligible)==outcome['eligible_trials']==panel['eligible_trials']
            assert sum(r['success'] for r in eligible)==outcome['success']
            assert sum(r['reason']=='drop' for r in eligible)==outcome['drops']
            title='Full feedback' if group=='feedback' and name=='learned_speed_residual' else NAMES[name]
            wait_drops=sum(outcome['drop_phases'].get(k,0) for k in ('startup_wait','wait'))
            values=[title,f"{outcome['success']}/{outcome['eligible_trials']}",pct(outcome['rate']),str(outcome['drops'])]
            values.append(str(wait_drops) if group=='waiting' else str(outcome['actual_calls']))
            rows.append(' & '.join(values)+r'\\')
        (tables/f'ablation_v3_{group}_rows.tex').write_text('\n'.join(rows)+'\n')
        macro='AblationWaitingRows' if group=='waiting' else 'AblationFeedbackRows'
        macros.append('\\newcommand{\\'+macro+'}{%\n'+'\n'.join(rows)+'\n}\n')
    raw_rows=[]
    categories=('success','drop','false_stop','abstain','horizon','service_excluded')
    for name in NAMES:
        records=trials[name];counts=Counter(r['reason'] for r in records)
        assert set(counts)<=set(categories) and sum(counts.values())==40
        raw_rows.append(' & '.join([NAMES[name]]+[str(counts[k]) for k in categories]+[str(sum(r['actual_model_calls'] for r in records))])+r'\\')
    (tables/'ablation_v3_raw_rows.tex').write_text('\n'.join(raw_rows)+'\n')
    macros.append('\\newcommand{\\AblationRawRows}{%\n'+'\n'.join(raw_rows)+'\n}\n')
    phase_rows=[]
    for name,outcome in summary['panels']['waiting']['outcomes'].items():
        phases=outcome['drop_phases']
        assert set(phases)<=set(('startup_wait','wait','execution'))
        assert sum(phases.values())==outcome['drops']
        phase_rows.append(' & '.join([NAMES[name]]+[str(phases.get(k,0)) for k in ('startup_wait','wait','execution')]+[str(outcome['drops'])])+r'\\')
    (tables/'ablation_v3_phase_rows.tex').write_text('\n'.join(phase_rows)+'\n')
    macros.append('\\newcommand{\\AblationPhaseRows}{%\n'+'\n'.join(phase_rows)+'\n}\n')
    (tables/'ablation_v3_macros.tex').write_text(''.join(macros))
    out=dict(raw_trials=200,panels=summary['panels'],source_sha256=manifest)
    (tables/'ablation_v3_render_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Rendered Q2/Q3 from 200 audited raw records.')
if __name__=='__main__':main()
