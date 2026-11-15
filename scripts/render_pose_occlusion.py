"""Generate pose tables from delivered evidence. Does not rerun frame inference."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/pose_occlusion_20261101'
for line in (DATA / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == digest, name
s = json.loads((DATA / 'summary.json').read_text())
a = json.loads((DATA / 'integrity_summary.json').read_text())
assert len(a['shards']) == 12 and sum(x['frames'] for x in a['shards']) == s['frames']
assert sum(x['frames'] for x in s['occlusion_bins']) == s['frames']
for model in ['rgb', 'rgbd']:
    m = s['metrics'][model]
    assert sum(x['counts'][model]['success_10mm_10deg'] for x in a['shards']) == m['successes']
    assert sum(x['counts'][model]['invalid'] for x in a['shards']) == m['invalid']
    assert round(100 * m['successes'] / s['frames'], 2) == m['recall_percent']
    assert all(x['counts'][model]['exactly_on_primary_threshold'] == 0 for x in a['shards'])
assert round(100*(s['metrics']['rgbd']['successes']-s['metrics']['rgb']['successes'])/s['frames'], 2) == s['difference_pp']
rows = [r'\begin{tabular}{lrrr}', r'\toprule', r'Hand occlusion & Frames & RGB & RGB-D \\', r'\midrule']
for b in s['occlusion_bins']:
    label = '{' + b['label'].replace('%', r'\%') + '}'
    rows.append(f"{label} & {b['frames']:,} & {b['rgb_percent']:.2f} & {b['rgbd_percent']:.2f}" + r' \\')
rows.extend([r'\midrule', f"All & {s['frames']:,} & {s['metrics']['rgb']['recall_percent']:.2f} & {s['metrics']['rgbd']['recall_percent']:.2f}" + r' \\', r'\bottomrule', r'\end{tabular}'])
(ROOT/'tables/pose_occlusion.tex').write_text('\n'.join(rows)+'\n')
rows=[r'\begin{tabular}{lrr}',r'\toprule',r'Metric & RGB & RGB-D \\',r'\midrule']
for label,key in [('Recall, 10 mm / 10 deg. (\\%)','recall_percent'),('Recall, 5 mm / 5 deg. (\\%)','strict_recall_percent'),('ADD recall (\\%)','add_recall_percent'),('Translation mean (mm)$^{*}$','mean_translation_mm_valid_only'),('Rotation mean (deg.)$^{*}$','mean_rotation_deg_valid_only')]:
    rows.append(f"{label} & {s['metrics']['rgb'][key]:.2f} & {s['metrics']['rgbd'][key]:.2f}"+r' \\')
rows.extend([f"Invalid predictions & {s['metrics']['rgb']['invalid']}/{s['frames']} & {s['metrics']['rgbd']['invalid']}/{s['frames']}"+r' \\',r'\bottomrule',r'\end{tabular}'])
(ROOT/'tables/pose_metrics.tex').write_text('\n'.join(rows)+'\n')
print('Verified delivered aggregate counts and hashes; generated two pose tables. Reported bootstrap intervals are not recomputed.')
