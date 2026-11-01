"""Generate dice layout rows from the audited 240-trial data export."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/dice_visual_layout_20261102'
def read(name):return json.loads((DATA/name).read_text())
def main():
    expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (DATA/'SHA256SUMS').read_text().splitlines()}
    actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.iterdir() if p.is_file() and p.name!='SHA256SUMS'}
    assert actual==expected,'Export changed'
    summary,trials,audit=read('summary.json'),read('trials.json'),read('completion_audit.json')
    assert summary['complete'] and not summary['development'] and audit['formal_complete']
    assert audit['total_completed_rows']==240 and not summary['six_cell_excluded_cases']
    names={'astra':'Astra full','vlm':'Fine-tuned VLM, bare','rule':'Rule VLM, bare'}
    for layout in ('identity','permuted'):
        for method in names:
            rows=trials[layout][method];out=summary['layouts'][layout][method]
            assert len(rows)==40 and [r['index'] for r in rows]==list(range(40))
            assert not any(r['exclusion_reason'] for r in rows)
            assert sum(r['success'] for r in rows)==out['matched_success']==out['raw_success']
    for i in range(40):
        assert len({trials[l][m][i]['initial_state_sha256'] for l in trials for m in names})==1
    rows=[' & '.join([names[m]]+[f"{summary['layouts'][l][m]['matched_success']}/40" for l in ('identity','permuted')])+r'\\' for m in names]
    pairs=[]
    def add(title,l1,m1,l2,m2,reported):
        a=trials[l1][m1];b=trials[l2][m2]
        x=sum(u['success'] and not v['success'] for u,v in zip(a,b));y=sum(v['success'] and not u['success'] for u,v in zip(a,b));n=x+y
        p=min(1.,2*sum(math.comb(n,i) for i in range(min(x,y)+1))/2**n) if n else 1.
        assert x==reported['a_only'] and y==reported['b_only'] and abs(p-reported['mcnemar_exact_two_sided_p'])<1e-12
        if p<.001:
            mantissa,exponent=f'{p:.2e}'.split('e');value=rf'${mantissa}\times10^{{{int(exponent)}}}$'
        else:value=f'{p:.4f}'
        pairs.append(f'{title} & {x} & {y} & {value}'+r'\\')
    for layout,label in [('identity','I'),('permuted','P')]:
        for method,short in [('vlm','fine-tuned'),('rule','rule')]:add(f'{label}: Astra vs. {short}',layout,'astra',layout,method,summary['paired_astra_comparisons'][layout][method])
    for method,label in [('astra','Astra'),('vlm','Fine-tuned'),('rule','Rule')]:add(f'{label}: I vs. P','identity',method,'permuted',method,summary['paired_identity_vs_permuted'][method])
    macros=''.join('\\newcommand{\\'+name+'}{%\n'+'\n'.join(values)+'\n}\n' for name,values in [('DiceLayoutRows',rows),('DiceLayoutTestRows',pairs)])
    (ROOT/'tables/dice_layout_macros.tex').write_text(macros)
    print('Verified and rendered six dice layout cells (240 trials).')
if __name__=='__main__':main()
