"""Render the Q1 four-system comparison bars.

Four arms, six objects, two mappings, all from the audited comparison file.
Colours are the ColorHunt palette E00000 / FFA97B / FFECCB / 9FED72, assigned
so that the two local baselines sit next to REVEAL in value rather than in hue.
"""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/q1_four_way_20261116/final_comparison.json'
METHODS = ('rule', 'vlm', 'finetuned_control', 'astra')
LABELS = ['Rule', 'Fine-tuned', 'Fine-tuned + ctrl.', 'REVEAL']
# ColorHunt E00000 FFA97B FFECCB 9FED72. The cream is too light to read on
# white, so it is pushed to a deeper sand in the bar face only.
COLORS = ['#9FED72', '#FFA97B', '#FFD9A0', '#E00000']
OBJECT_ORDER = ['cube', 'die', 'duck', 'hedgehog', 'pig', 'milk_carton']
DISPLAY = {'cube': 'Cube', 'die': 'Dice', 'duck': 'Duck', 'hedgehog': 'Hedgehog',
           'pig': 'Ball', 'milk_carton': 'Milk'}


def load():
    cells = json.loads(SOURCE.read_text())['cells']
    lookup = {(c['object'], c['layout']): c for c in cells}
    arrays = []
    for setting in ('identity', 'permuted'):
        rows = []
        for obj in OBJECT_ORDER:
            cell = lookup[(obj, setting)]
            rows.append([100 * cell['arms'][m]['success'] / cell['common'] for m in METHODS])
        arrays.append(np.array(rows))
    return arrays


def render(destination):
    arrays = load()
    with plt.rc_context({'font.family': 'serif',
                         'font.serif': ['Liberation Serif', 'DejaVu Serif'],
                         'font.size': 8.5, 'pdf.fonttype': 42, 'svg.fonttype': 'none'}):
        fig, axes = plt.subplots(1, 2, figsize=(7, 2.3))
        fig.subplots_adjust(left=.062, right=.99, bottom=.185, top=.755, wspace=.14)
        x = np.arange(len(OBJECT_ORDER))
        width = .2
        for k, (ax, values) in enumerate(zip(axes, arrays)):
            ax.set_title(['(a) Original mapping', '(b) Changed mapping'][k],
                         fontsize=9.5, fontweight='bold', color='#2A2A2A', pad=9)
            for j in range(4):
                off = (j - 1.5) * width
                bars = ax.bar(x + off, values[:, j], width * .92,
                              color=COLORS[j], edgecolor='white', linewidth=.4, zorder=3)
                if j == 3:
                    for bar, v in zip(bars, values[:, j]):
                        ax.text(bar.get_x() + bar.get_width() / 2, v + 2.4, f'{v:.0f}',
                                ha='center', va='bottom', fontsize=7.4,
                                fontweight='bold', color='#2A2A2A')
            ax.set_xticks(x, [DISPLAY[o] for o in OBJECT_ORDER], fontsize=8)
            ax.set_xlim(-.6, len(OBJECT_ORDER) - .4)
            ax.set_ylim(0, 104)
            ax.set_yticks([0, 25, 50, 75, 100])
            if k == 0:
                ax.set_ylabel('Success (%)', labelpad=5)
            ax.set_axisbelow(True)
            ax.yaxis.grid(color='#E9E9E9', lw=.6)
            for s in ('top', 'right'):
                ax.spines[s].set_visible(False)
            for s in ('left', 'bottom'):
                ax.spines[s].set_color('#BFBFBF')
                ax.spines[s].set_linewidth(.6)
            ax.tick_params(length=0, pad=4, labelcolor='#3A3A3A')
        handles = [Patch(facecolor=c, edgecolor='white', linewidth=.4, label=l)
                   for c, l in zip(COLORS, LABELS)]
        fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, 1.005),
                   ncol=4, frameon=False, columnspacing=1.5,
                   handlelength=1.1, handletextpad=.45, fontsize=8.6)

        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        for ext in ('pdf', 'png'):
            fig.savefig(destination.with_suffix('.' + ext), dpi=300, facecolor='white')
        plt.close(fig)
    return arrays


def main():
    arrays = render(ROOT / 'figures/q1_four_way_bar')
    report = {
        'source': str(SOURCE.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'methods': list(METHODS),
        'colors': dict(zip(METHODS, COLORS)),
        'palette': 'ColorHunt E00000 FFA97B FFECCB 9FED72',
        'original_mapping': arrays[0].round(2).tolist(),
        'changed_mapping': arrays[1].round(2).tolist(),
    }
    (ROOT / 'figures/q1_four_way_bar_values.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if 'mapping' not in k}, indent=2))


if __name__ == '__main__':
    main()
