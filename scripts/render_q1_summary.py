"""Descriptive, equal-object Q1 means from the frozen six-object count table."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/inhand4_completed_20261103/q1_all_objects.json'
METHODS = ('rule', 'vlm', 'astra')
SETTINGS = ('identity', 'permuted')

def main():
    data = json.loads(SOURCE.read_text())
    objects = data['objects']
    assert len(objects) == 6 and len({o['object'] for o in objects}) == 6
    table = (ROOT / 'tables/q1_all_objects.tex').read_text()
    means = {}
    for setting in SETTINGS:
        values = {m: [] for m in METHODS}
        for obj in objects:
            cells = obj['cells'][setting]
            assert len({cells[m]['trials'] for m in METHODS}) == 1
            for method in METHODS:
                c = cells[method]
                assert 0 <= c['success'] <= c['trials'] <= 40
                values[method].append(Fraction(c['success'], c['trials']))
        means[setting] = {m: 100 * sum(values[m]) / len(objects) for m in METHODS}
    # Ensure the displayed per-object percentages agree with the count source.
    for obj in objects:
        row = next(line for line in table.splitlines() if line.startswith(obj['object'] + ' & '))
        plain = re.sub(r'\\textbf\{([\d.]+)\}', r'\1', row)
        fields = plain.removesuffix('\\\\').split(' & ')
        assert fields[2] == f"{obj['cells']['identity']['astra']['trials']} / {obj['cells']['permuted']['astra']['trials']}"
        expected = [f"{100 * obj['cells'][s][m]['success'] / obj['cells'][s][m]['trials']:.1f}" for s in SETTINGS for m in METHODS]
        assert fields[3:] == expected, obj['object']
    best = {s: max(('rule', 'vlm'), key=lambda m: means[s][m]) for s in SETTINGS}
    gains = {s: means[s]['astra'] - means[s][best[s]] for s in SETTINGS}
    macro_values = {
        'QOneOriginalSuccess': means['identity']['astra'],
        'QOneChangedSuccess': means['permuted']['astra'],
        'QOneOriginalGain': gains['identity'],
        'QOneChangedGain': gains['permuted'],
        'QOneOriginalBaseline': means['identity'][best['identity']],
        'QOneChangedBaseline': means['permuted'][best['permuted']],
    }
    (ROOT/'tables/q1_summary_macros.tex').write_text(''.join(
        '\\newcommand{\\' + k + '}{' + f'{float(v):.1f}' + '}\n' for k,v in macro_values.items()))
    cells = [f'{float(means[s][m]):.1f}' for s in SETTINGS for m in METHODS]
    cells[2] = r'\textbf{' + cells[2] + '}'
    cells[5] = r'\textbf{' + cells[5] + '}'
    row = r'Mean & Object-specific & -- & ' + ' & '.join(cells) + r'\\'
    with (ROOT/'tables/q1_summary_macros.tex').open('a') as stream:
        stream.write('\\newcommand{\\QOneAverageRow}{%\n' + row + '\n}\n')
    report = {
        'source':str(SOURCE.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'raw_trials_in_mapping_study':data['raw_trials_in_mapping_table'],
        'estimand':'Post-hoc descriptive equal-object mean of common-service-eligible rates, separately by mapping. Not a pooled trial rate, shared-policy score, or new significance test.',
        'objects':[o['object'] for o in objects],
        'means_percent':{s:{m:float(v) for m,v in ms.items()} for s,ms in means.items()},
        'best_evaluated_baseline_by_mean':best,
        'gain_percentage_points':{s:float(v) for s,v in gains.items()},
    }
    (ROOT/'tables/q1_summary_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
