"""Generate descriptive controller results from user-confirmed aggregate counts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/controller_three_seed_20261107/summary.json').read_text())
assert d['seed_ids']==[187102,187103,187104]
assert d['trials_per_condition']==3*d['trials_per_seed_per_condition']==120
rows=[]
for m in d['methods']:
 a,b,c=m['seed_187102'],m['seeds_187103_187104'],m['combined']
 assert sum(a.values())==40 and sum(b.values())==80 and sum(c.values())==120
 assert all(c[k]==a[k]+b[k] for k in c)
 rate=f"{100*c['success']/120:.1f}"
 cells=[m['label'],f"{c['success']}/120",rate,str(c['waiting_drop']),str(c['execution_drop']),str(c['other_failure'])]
 if m['key']=='learned_speed_joint_correction':cells=[r'\textbf{'+v+'}' for v in cells]
 rows.append(' & '.join(cells)+r'\\')
text=r"""\begin{table}[t]
\centering\small
\setlength{\tabcolsep}{2.5pt}
\begin{tabularx}{\linewidth}{@{}Xrrrrr@{}}
\toprule
Waiting policy & Success & \% & \shortstack{Wait\\drops} & \shortstack{Exec.\\drops} & Other\\
\midrule
"""+ '\n'.join(rows)+'\n'+r"""\bottomrule
\end{tabularx}
\caption{\textbf{Q2: controller ablation on the cube.} Each method has 120 trials across three seeds. Wait and execution drops denote failure stages; Other contains the remaining failures. Outcome counts sum to 120 in each row.}
\label{tab:waiting}
\end{table}
"""
(ROOT/'tables/controller_three_seed.tex').write_text(text)
print('Verified 480 outcomes across four methods; no significance test inferred from aggregates.')
