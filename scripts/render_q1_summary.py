"""Render and verify the audited four-way Q1 summary used by the paper."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/q1_four_way_20261116/final_comparison.json'
METHODS = ('rule', 'vlm', 'finetuned_control', 'astra')
SETTINGS = ('identity', 'permuted')
DISPLAY = {'rule': 'Rule', 'vlm': 'Fine-tuned',
           'finetuned_control': 'Fine-tuned + ctrl.', 'astra': 'REVEAL'}

def main():
    data = json.loads(SOURCE.read_text())
    cells = data['cells']
    objects = sorted({c['object'] for c in cells}, key=['cube','die','duck','hedgehog','pig','milk_carton'].index)
    assert len(objects) == 6 and len(cells) == 12
    lookup = {(c['object'], c['layout']): c for c in cells}
    table = (ROOT / 'tables/q1_main_four_way.tex').read_text()
    means = {}
    for setting in SETTINGS:
        values = {m: [] for m in METHODS}
        for obj in objects:
            cell = lookup[(obj, setting)]
            denominator = cell['common']
            assert 0 < denominator <= 40
            for method in METHODS:
                arm = cell['arms'][method]
                assert 0 <= arm['success'] <= denominator
                values[method].append(Fraction(arm['success'], denominator))
        means[setting] = {m: 100 * sum(values[m]) / len(objects) for m in METHODS}

    for obj in objects:
        label = 'Milk carton' if obj == 'milk_carton' else ('Ball' if obj == 'pig' else obj.title())
        row = next(line for line in table.splitlines() if line.startswith(label + ' & '))
        plain = re.sub(r'\\textbf\{([\d.]+)\}', r'\1', row)
        fields = plain.removesuffix('\\\\').split(' & ')
        expected_den = f"{lookup[(obj, 'identity')]['common']} / {lookup[(obj, 'permuted')]['common']}"
        assert fields[1] == expected_den, (obj, fields[1], expected_den)
        expected = [f"{100 * lookup[(obj, s)]['arms'][m]['success'] / lookup[(obj, s)]['common']:.1f}" for s in SETTINGS for m in METHODS]
        assert fields[2:] == expected, (obj, fields[2:], expected)

    best = {s: max(METHODS[:-1], key=lambda m: means[s][m]) for s in SETTINGS}
    gains = {s: means[s]['astra'] - means[s][best[s]] for s in SETTINGS}
    macro_values = {
        'QOneOriginalSuccess': means['identity']['astra'],
        'QOneChangedSuccess': means['permuted']['astra'],
        'QOneOriginalGain': gains['identity'],
        'QOneChangedGain': gains['permuted'],
        'QOneOriginalBaseline': means['identity'][best['identity']],
        'QOneChangedBaseline': means['permuted'][best['permuted']],
    }
    with (ROOT/'tables/q1_summary_macros.tex').open('w') as stream:
        for k, v in macro_values.items():
            stream.write('\\newcommand{\\' + k + '}{' + f'{float(v):.1f}' + '}\n')
        cells_text = [f'{float(means[s][m]):.1f}' for s in SETTINGS for m in METHODS]
        cells_text[3] = r'\textbf{' + cells_text[3] + '}'
        cells_text[7] = r'\textbf{' + cells_text[7] + '}'
        row = r'Mean & -- & ' + ' & '.join(cells_text) + r'\\'
        stream.write('\\newcommand{\\QOneAverageRow}{%\n' + row + '\n}\n')
    report = {
        'source': str(SOURCE.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'scheduled_trials': data['scheduled'],
        'objects': objects,
        'methods': list(METHODS),
        'means_percent': {s: {m: float(v) for m, v in ms.items()} for s, ms in means.items()},
        'best_evaluated_baseline_by_mean': best,
        'gain_percentage_points': {s: float(v) for s, v in gains.items()},
    }
    (ROOT/'tables/q1_summary_check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
