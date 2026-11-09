"""Alternative Q1 figure styles, all rendered from the same recorded counts.

Run --all for previews; --select A (through F) persists the manuscript style.
The normal paper build calls render_selected(), so the chosen style is retained.
"""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/inhand4_completed_20261103/q1_all_objects.json'
CONFIG = ROOT / 'figures/q1_style.json'
LABELS = ['Rule', 'Fine-tuned', 'AIMI']
STYLES = {
    'A': ('Slate & coral', ['#C4CFDC', '#829CB8', '#D37778']),
    'B': ('Sage & teal', ['#D6DED5', '#A3C9B7', '#38867B']),
    'C': ('Sand, rose & plum', ['#DECFB3', '#D8A5B5', '#87638E']),
    'D': ('Aqua, apricot & blue', ['#BCDDE1', '#EBC78E', '#547CB4']),
    'E': ('Horizontal dot plot', ['#A8B6C6', '#718EA9', '#C5636C']),
    'F': ('Annotated heatmap', []),
}


def get_data():
    objects = json.loads(SOURCE.read_text())['objects']
    assert len(objects) == 6
    names = [o['object'] for o in objects]
    arrays = [np.array([[100 * o['cells'][s][m]['success'] / o['cells'][s][m]['trials']
                        for m in ['rule', 'vlm', 'astra']] for o in objects])
              for s in ['identity', 'permuted']]
    assert all(np.all((a >= 0) & (a <= 100)) for a in arrays)
    return names, arrays


def number(v):
    return f'{v:.0f}' if abs(v-round(v)) < 1e-8 else f'{v:.1f}'


def clean_axes(ax, vertical=True):
    ax.set_axisbelow(True)
    (ax.yaxis if vertical else ax.xaxis).grid(color='#E8EBEF', lw=.5)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    for s in ['left', 'bottom']:
        ax.spines[s].set_color('#C0C7CF')
        ax.spines[s].set_linewidth(.5)
    ax.tick_params(length=0, pad=4, labelcolor='#394555')


def render_one(key, destination):
    title, colors = STYLES[key]
    names, arrays = get_data()
    with plt.rc_context({'font.family': 'serif', 'font.serif': ['Liberation Serif', 'DejaVu Serif'],
                         'font.size': 8.5, 'pdf.fonttype': 42, 'svg.fonttype': 'none'}):
        height = 2.15 if key in 'ABCD' else 2.55
        fig, axes = plt.subplots(1, 2, figsize=(7, height))
        fig.subplots_adjust(left=.066 if key in 'ABCD' else .105, right=.988,
                            bottom=.19 if key in 'ABCD' else .17,
                            top=.77 if key != 'F' else .83,
                            wspace=.16 if key in 'ABCD' else .37)
        for k, (ax, values) in enumerate(zip(axes, arrays)):
            ax.set_title(['(a) Original mapping', '(b) Changed mapping'][k],
                         fontsize=9, fontweight='bold', color='#283545', pad=8)
            if key in 'ABCD':
                x = np.arange(6)
                for j in range(3):
                    bars = ax.bar(x+(j-1)*.25, values[:, j], .225, color=colors[j],
                                  edgecolor='white', linewidth=.35, zorder=3)
                    if j == 2:
                        for bar, v in zip(bars, values[:, j]):
                            ax.text(bar.get_x()+bar.get_width()/2, v+2.1, number(v),
                                    ha='center', va='bottom', fontsize=7.5,
                                    fontweight='bold', color='#334253')
                ax.set_xticks(x, [n.replace('Milk carton', 'Milk') for n in names])
                ax.set_xlim(-.55, 5.55)
                ax.set_ylim(0, 106)
                ax.set_yticks([0, 25, 50, 75, 100])
                if k == 0:
                    ax.set_ylabel('Success (%)', labelpad=5)
                clean_axes(ax)
            elif key == 'E':
                y = np.arange(6)
                for j, marker in enumerate(['o', '^', 'D']):
                    yy = y+(j-1)*.19
                    ax.scatter(values[:, j], yy, s=22 if j < 2 else 29,
                               marker=marker, color=colors[j], edgecolor='white',
                               linewidth=.35, zorder=3)
                    if j == 2:
                        for v, row in zip(values[:, j], yy):
                            ax.text(v+2.4, row, number(v), va='center',
                                    color='#934A54', fontsize=7.6, fontweight='bold')
                ax.set_yticks(y, names)
                ax.set_ylim(5.65, -.65)
                ax.set_xlim(-3, 108)
                ax.set_xticks([0, 25, 50, 75, 100])
                ax.set_xlabel('Success (%)', labelpad=4)
                clean_axes(ax, vertical=False)
                ax.spines['left'].set_visible(False)
            else:
                cmap = LinearSegmentedColormap.from_list('success_teal', ['#F7FAF9', '#BCD9D3', '#357F78'])
                im = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect='auto')
                ax.set_yticks(np.arange(6), names)
                ax.set_xticks(np.arange(3), LABELS)
                ax.tick_params(length=0, pad=5, labelcolor='#394555')
                for spine in ax.spines.values():
                    spine.set_visible(False)
                for i in range(6):
                    for j in range(3):
                        ax.text(j, i, f'{values[i,j]:.1f}', ha='center', va='center',
                                color='white' if values[i,j] >= 72 else '#243B3C',
                                fontsize=8.3, fontweight='bold' if j == 2 else 'normal')
                ax.set_xticks(np.arange(-.5, 3, 1), minor=True)
                ax.set_yticks(np.arange(-.5, 6, 1), minor=True)
                ax.grid(which='minor', color='white', linewidth=2)
                ax.tick_params(which='minor', length=0)
        if key in 'ABCD':
            handles = [Patch(facecolor=c, label=l) for c, l in zip(colors, LABELS)]
        elif key == 'E':
            handles = [Line2D([], [], marker=m, linestyle='', color=c, markersize=5,
                              label=l) for m, c, l in zip(['o', '^', 'D'], colors, LABELS)]
        else:
            handles = []
            fig.text(.5, .955, 'Success (%)  |  Shared color scale: 0 to 100',
                     ha='center', va='top', fontsize=8.5, color='#394555')
        if handles:
            fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, 1.01),
                       ncol=3, frameon=False, columnspacing=1.8,
                       handlelength=1.2, handletextpad=.5, fontsize=8.7)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        for ext in ['pdf', 'svg', 'png']:
            path = destination.with_suffix('.'+ext)
            fig.savefig(path, dpi=300, facecolor='white')
            if ext == 'svg':
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)


def render_selected():
    key = json.loads(CONFIG.read_text())['style'] if CONFIG.exists() else 'A'
    render_one(key, ROOT/'figures/q1_task_success')
    return key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--select', choices=STYLES)
    args = parser.parse_args()
    if args.select:
        CONFIG.write_text(json.dumps({'style': args.select, 'name': STYLES[args.select][0]}, indent=2)+'\n')
        render_selected()
    if args.all or not args.select:
        for key in STYLES:
            render_one(key, ROOT/f'figures/q1_options/Q1_{key}')
        names, arrays = get_data()
        report = {'source': str(SOURCE.relative_to(ROOT)),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'objects': names, 'methods': LABELS,
                  'original_mapping': arrays[0].tolist(), 'changed_mapping': arrays[1].tolist(),
                  'styles': {k: {'name': v[0], 'colors': v[1]} for k, v in STYLES.items()},
                  'note': 'All styles share these exact values. No new data, uncertainty or significance is inferred.'}
        (ROOT/'figures/q1_options/values.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
