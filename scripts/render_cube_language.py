"""Regenerate the audited cube instruction-coverage tables from portable records."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/cube_language_20261105'
rows=json.loads((BASE/'trials.json').read_text());result=json.loads((BASE/'results.json').read_text())
conditions=['en_standard','en_rewrite','zh_standard','zh_rewrite']
methods=['astra','vlm','rule'];names={'astra':'REVEAL','vlm':'Fine-tuned VLM','rule':'Rule VLM'}
lookup={(r['condition'],r['method'],r['episode']):r for r in rows}
assert len(lookup)==len(rows)==720
for c in conditions:
 for m in methods:
  rs=[lookup[c,m,i] for i in range(60)];cell=result['cells'][c+'/'+m]
  assert sum(r['success'] for r in rs)==cell['success']
  assert sum(bool(r['exclusion_reason']) for r in rs)==cell['excluded']
for comp in result['comparisons']:
 lc,lm=comp['left'].split('/');rc,rm=comp['right'].split('/')
 ids=[i for i in range(60) if not lookup[lc,lm,i]['exclusion_reason'] and not lookup[rc,rm,i]['exclusion_reason']]
 assert len(ids)==comp['n']
 for i in range(60):
  a,b=lookup[lc,lm,i],lookup[rc,rm,i]
  assert a['initial_state_sha256']==b['initial_state_sha256']
  assert a['first_image_sha256'] and a['first_image_sha256']==b['first_image_sha256']
 a=sum(lookup[lc,lm,i]['success'] and not lookup[rc,rm,i]['success'] for i in ids)
 b=sum(lookup[rc,rm,i]['success'] and not lookup[lc,lm,i]['success'] for i in ids)
 assert (a,b)==(comp['left_only'],comp['right_only'])
 n=a+b;p=min(1.,2*sum(math.comb(n,k) for k in range(min(a,b)+1))/2**n) if n else 1.
 assert abs(p-comp['p_exact'])<1e-12
for family in ['language_and_wording','methods']:
 group=sorted([x for x in result['comparisons'] if x['family']==family],key=lambda x:x['p_exact']);last=0.
 for i,x in enumerate(group):
  last=max(last,min(1.,(len(group)-i)*x['p_exact']));assert abs(last-x['p_holm'])<1e-12
header=r"""\begin{table}[t]
\centering\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}lrrrr@{}}
\toprule
 & \multicolumn{2}{c}{English} & \multicolumn{2}{c}{Chinese}\\
System & Standard & Rewrite & Standard & Rewrite\\
\midrule
"""
lines=[]
for m in methods:
 vals=[sum(lookup[c,m,i]['success'] for i in range(60)) for c in conditions]
 lines.append(names[m]+' & '+' & '.join(f'{n} ({100*n/60:.1f})' for n in vals)+r'\\')
caption=r"""\bottomrule
\end{tabular}
\caption{\textbf{Q1: cube instruction coverage.} Success counts (percent), each out of 60 scheduled trials. REVEAL service exclusions are 4, 1, 3 and 7 in column order; baselines have none. All remain in these raw denominators.}
\label{tab:cube-language}
\end{table}
"""
(ROOT/'tables/cube_language.tex').write_text(header.replace(r'\footnotesize',r'\small')+'\n'.join(lines)+'\n'+caption)
lines=[]
for m in methods:
 vals=[]
 for c in conditions:
  ids=[i for i in range(60) if all(not lookup[c,k,i]['exclusion_reason'] for k in methods)]
  n=sum(lookup[c,m,i]['success'] for i in ids);vals.append(f'{n}/{len(ids)}')
 lines.append(names[m]+' & '+' & '.join(vals)+r'\\')
caption=r"""\bottomrule
\end{tabular}
\caption{Common service-eligible panels within each language condition. Raw 60-trial results remain the main-table summary. Cross-condition tests use their own paired eligibility sets.}
\label{tab:language-eligible}
\end{table}
"""
(ROOT/'tables/cube_language_eligible.tex').write_text(header+'\n'.join(lines)+'\n'+caption)
def fmt(p):return '$<0.0001$' if p<.0001 else f'{p:.4f}'
comp={x['name']:x for x in result['comparisons']}
tests=r"""\begin{table}[t]
\centering\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}lrrrr@{}}
\toprule
 & \multicolumn{2}{c}{English vs. Chinese} & \multicolumn{2}{c}{Standard vs. rewrite}\\
System & Standard & Rewrite & English & Chinese\\
\midrule
"""
for m in methods:
 pairs=[('en_standard','zh_standard'),('en_rewrite','zh_rewrite'),('en_standard','en_rewrite'),('zh_standard','zh_rewrite')]
 tests+=names[m]+' & '+' & '.join(fmt(comp[f'{m}:{a}-{b}']['p_holm']) for a,b in pairs)+r'\\'+'\n'
tests+=r"""\bottomrule
\end{tabular}
\caption{Holm-adjusted exact paired $p$-values, twelve language/wording contrasts. Non-significance is not evidence of equivalence.}
\label{tab:language-wording-tests}
\end{table}
\begin{table}[t]
\centering\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}lrrr@{}}
\toprule
Condition & REVEAL--Rule & REVEAL--FT & FT--Rule\\
\midrule
"""
for c in conditions:
 values=[comp[f'{c}:{pair}']['p_holm'] for pair in ['astra-rule','astra-vlm','rule-vlm']]
 tests+=c.replace('_',' ').replace('en ','EN ').replace('zh ','ZH ')+' & '+' & '.join(fmt(p) for p in values)+r'\\'+'\n'
tests+=r"""\bottomrule
\end{tabular}
\caption{Holm-adjusted exact paired $p$-values, a separate twelve-test method family. FT denotes fine-tuning. Pair-specific exclusions and discordant counts are archived.}
\label{tab:language-method-tests}
\end{table}
"""
(ROOT/'tables/cube_language_tests.tex').write_text(tests)
print('Verified 720 unique records, matched states/images and all 24 exact/Holm tests; generated three tables.')
