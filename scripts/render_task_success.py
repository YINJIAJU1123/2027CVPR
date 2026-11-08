"""Render Q1 and real-hand task success from recorded aggregate counts.

All axes start at zero. Bars are descriptive rates, not independent runs;
no error bars or statistical significance are inferred from aggregate counts.
"""
from pathlib import Path
import json
import hashlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
COLORS = ['#B8C1CA', '#E6B77C', '#6198BF']
EDGES = ['#6F7C88', '#A87B46', '#356A94']
HATCHES = ['', '//', '']
LABELS = ['Rule', 'Fine-tuned', 'AIMI']
plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Liberation Serif', 'DejaVu Serif'],
    'font.size': 8.5, 'axes.linewidth': .55, 'pdf.fonttype': 42,
    'svg.fonttype': 'none', 'hatch.linewidth': .35,
})


def style_axis(ax, labels):
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xticks(np.arange(len(labels)), labels)
    ax.tick_params(axis='both', length=2, width=.5, pad=3)
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='#E3E7EC', linewidth=.55)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color('#A8B1BA')


def grouped(ax, values, counts=None, fontsize=7.2, label_all=True):
    xs = np.arange(len(values))
    width = .25
    for j in range(3):
        heights = [v[j] for v in values]
        bars = ax.bar(xs + (j-1)*width, heights, width=width*.9,
                      color=COLORS[j], edgecolor=EDGES[j], linewidth=.45,
                      hatch=HATCHES[j], zorder=3)
        for k, (bar, value) in enumerate(zip(bars, heights)):
            if not label_all and j != 2:
                continue
            label = f'{value:.0f}' if abs(value-round(value)) < 1e-8 else f'{value:.1f}'
            if counts is not None:
                label = str(counts[k][j])
            ax.text(bar.get_x()+bar.get_width()/2, value+2, label,
                    ha='center', va='bottom', fontsize=fontsize,
                    weight='bold' if j==2 else 'normal', color='#253343', zorder=5)


def add_legend(fig, y=1.):
    handles = [Patch(facecolor=c, edgecolor=e, linewidth=.45, hatch=h, label=l)
               for c, e, h, l in zip(COLORS, EDGES, HATCHES, LABELS)]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, y),
               ncol=3, frameon=False, handlelength=1.25,
               columnspacing=1.3, handletextpad=.45, fontsize=8.5)


def save(fig, name):
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(ROOT/f'figures/{name}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)


def main():
    q1_path = ROOT/'data/inhand4_completed_20261103/q1_all_objects.json'
    q1 = json.loads(q1_path.read_text())
    objects = q1['objects']
    assert len(objects) == 6
    fig, axes = plt.subplots(1, 2, figsize=(7., 1.9), sharey=True)
    fig.subplots_adjust(left=.065, right=.99, bottom=.2, top=.74, wspace=.13)
    q1_values = {}
    names = [o['object'].replace('Milk carton', 'Milk') for o in objects]
    for ax, setting, title in zip(axes, ['identity', 'permuted'],
                                  ['(a) Original mapping', '(b) Changed mapping']):
        values = [[100*o['cells'][setting][m]['success']/o['cells'][setting][m]['trials']
                   for m in ('rule', 'vlm', 'astra')] for o in objects]
        q1_values[setting] = values
        grouped(ax, values, label_all=False)
        style_axis(ax, names)
        ax.set_title(title, fontsize=9, weight='bold', pad=5)
    axes[0].set_ylabel('Success (%)', fontsize=9, labelpad=3)
    add_legend(fig, 1.015)
    save(fig, 'q1_task_success')

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
    fig, ax = plt.subplots(figsize=(3.35, 1.95))
    fig.subplots_adjust(left=.14, right=.99, bottom=.2, top=.78)
    grouped(ax, [[100*c/n for c in row] for row in counts], fontsize=8)
    style_axis(ax, [o['object'] for o in hw['objects']])
    ax.set_ylabel('Success (%)', fontsize=8.5, labelpad=2)
    add_legend(fig, 1.015)
    save(fig, 'hardware_task_success')

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
    table = r'''\begin{table}[t]
\centering\small
\setlength{\tabcolsep}{3pt}
\begin{tabular}{lccc}
\toprule
Object & Rule & Fine-tuned & AIMI\\
\midrule
'''+ '\n'.join(rows)+'\n'+r'\midrule'+'\n'+ ' & '.join(['Total']+total_cells)+r'\\'+'\n'+r'''\bottomrule
\end{tabular}
\caption{\textbf{Real-hand task completion.} Successes/trials and rates for the four physical objects. Every object--method cell contains 20 trials. Success requires reaching the requested target and stopping within $15^\circ$ without dropping the object.}
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
