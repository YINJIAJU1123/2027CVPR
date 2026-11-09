"""Render the selected Q1 chart and Q4 hardware tables from recorded counts.

All axes start at zero. Bars are descriptive rates, not independent runs;
no error bars or statistical significance are inferred from aggregate counts.
"""
from pathlib import Path
import json
import hashlib

from render_q1_variants import render_selected

ROOT = Path(__file__).resolve().parents[1]


def main():
    q1_path = ROOT/'data/inhand4_completed_20261103/q1_all_objects.json'
    q1 = json.loads(q1_path.read_text())
    objects = q1['objects']
    assert len(objects) == 6
    q1_values = {setting: [[100*o['cells'][setting][m]['success']/o['cells'][setting][m]['trials']
                           for m in ('rule', 'vlm', 'astra')] for o in objects]
                 for setting in ('identity', 'permuted')}
    render_selected()

    hardware_path = ROOT/'data/hardware_author_report_20261108/results.json'
    hw = json.loads(hardware_path.read_text())
    methods = hw['method_order']
    n = hw['trials_per_object_method']
    assert methods == ['rule', 'fine_tuned', 'alive'] and n == 20
    assert [o['object'] for o in hw['objects']] == ['Cube', 'Die', 'Ball', 'Duck']
    counts = [[o['successes'][m] for m in methods] for o in hw['objects']]
    assert all(type(c) is int and 0 <= c <= n for row in counts for c in row)
    totals = [sum(row[j] for row in counts) for j in range(3)]
    assert totals == [32, 53, 70]
    total_n = n*len(counts)
    rates = [100*c/total_n for c in totals]
    macros = {
        'HardwareRuleSuccess': f'{rates[0]:.1f}',
        'HardwareFineTunedSuccess': f'{rates[1]:.2f}',
        'HardwareAimiSuccess': f'{rates[2]:.1f}',
        'HardwareGain': f'{rates[2]-rates[1]:.2f}',
    }
    (ROOT/'tables/hardware_macros.tex').write_text(''.join(
        '\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items()))
    rows = []
    for obj, row in zip(hw['objects'], counts):
        cells = [f'{c}/{n} ({100*c/n:.0f}\\%)' for c in row]
        cells[-1] = r'\textbf{'+cells[-1]+'}'
        rows.append(' & '.join([obj['object']]+cells)+r'\\')
    total_cells = [f'{c}/{total_n} ({r:g}\\%)' for c,r in zip(totals,rates)]
    total_cells[-1] = r'\textbf{'+total_cells[-1]+'}'
    table = r'''\begin{table}[!htbp]
\centering\small
\setlength{\tabcolsep}{3pt}
\begin{tabular}{lccc}
\toprule
Object & Rule & Fine-tuned & AIMI\\
\midrule
'''+ '\n'.join(rows)+'\n'+r'\midrule'+'\n'+ ' & '.join(['Total']+total_cells)+r'\\'+'\n'+r'''\bottomrule
\end{tabular}
\caption{\textbf{Q4: real-hand task completion.} Successes/trials and rates for the four physical objects. Every object--method cell contains 20 trials. Success requires reaching the requested target and stopping within $15^\circ$ without dropping the object.}
\label{tab:hardware-results}
\end{table}
'''
    (ROOT/'tables/hardware_results.tex').write_text(table)
    report = {
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (q1_path, hardware_path)},
        'hardware_trials_per_method': total_n,
        'hardware_total_trials': total_n*3,
        'hardware_successes': dict(zip(methods, totals)),
        'hardware_rates_percent': dict(zip(methods, rates)),
        'hardware_gain_over_fine_tuned_pp': rates[2]-rates[1],
        'q1_plotted_percentages': q1_values,
        'uncertainty': 'Descriptive aggregate rates; no error bars or significance test inferred.',
    }
    (ROOT/'figures/task_success_values.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='q1_plotted_percentages'},indent=2))


if __name__ == '__main__':
    main()
