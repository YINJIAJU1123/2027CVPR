#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
for log in build/main/main.log build/supplyment/supplyment.log; do
    [[ -s "$log" ]] || { printf 'Missing build log: %s\n' "$log" >&2; exit 1; }
done
if rg -n 'undefined references|Citation .+ undefined|LaTeX Error|Overfull \\hbox|Overfull \\vbox|multiply defined|destination with the same identifier' build/main/main.log build/supplyment/supplyment.log; then
    exit 1
fi
${PDFINFO:-pdfinfo} output/pdf/main.pdf | head -18
${PDFINFO:-pdfinfo} output/pdf/supplyment.pdf | head -18

python3 - <<'PY_CHECK'
import os,re,subprocess,json,hashlib
from pathlib import Path

def read_pdf(name):
    return subprocess.check_output([os.environ.get('PDFTOTEXT','/usr/bin/pdftotext'),'-layout',f'output/pdf/{name}.pdf','-'],text=True)
text=read_pdf('main')
pages=text.rstrip('\f').split('\f')
llm=[i for i,page in enumerate(pages) if re.search(r'^\s*(?:\d+\s+)?LLM Usage Statement(?:\s{2,}|$)',page,re.M)]
refs=[i for i,page in enumerate(pages) if re.search(r'^\s*(?:\d+\s+)?References(?:\s{2,}|$)',page,re.M)]
if not llm or not refs:raise SystemExit('LLM statement or references boundary missing')
if llm[0]>8:raise SystemExit('Main body exceeds eight pages')
if text.index('LLM Usage Statement')>text.index('References'):raise SystemExit('LLM statement must precede references')
if 'Supplementary Material' in text:raise SystemExit('Main paper unexpectedly contains the supplement')
if 'ViserDex' in Path('sections/00_abstract.tex').read_text():raise SystemExit('Abstract still mentions ViserDex')
for value in ('37.53','64.73'):
    if value not in text:raise SystemExit(f'Missing Q4 pose result: {value}')
hardware_path=Path('data/hardware_author_report_20261108/results.json')
hardware=json.loads(hardware_path.read_text())
derived=json.loads(Path('figures/task_success_values.json').read_text())
if derived['source_sha256'][str(hardware_path)]!=hashlib.sha256(hardware_path.read_bytes()).hexdigest():
    raise SystemExit('Hardware figure was not regenerated from current counts')
for method in hardware['method_order']:
    successes=sum(o['successes'][method] for o in hardware['objects'])
    if successes!=derived['hardware_successes'][method]:
        raise SystemExit(f'Hardware count mismatch: {method}')
    rate=100*successes/(hardware['trials_per_object_method']*len(hardware['objects']))
    if rate!=derived['hardware_rates_percent'][method]:
        raise SystemExit(f'Hardware rate mismatch: {method}')
for value in ('87.5','66.25','70/80','240'):
    if value not in text:raise SystemExit(f'Missing hardware result: {value}')
supp=read_pdf('supplyment')
for value in ('9/20','15/20','18/20','8/20','14/20','13/20','19/20','6/20','11/20','32/80','53/80','70/80'):
    if value not in supp:raise SystemExit(f'Missing supplementary hardware count: {value}')
for name,body in [('main',text),('supplyment',supp)]:
    if 'AIMI' not in body:raise SystemExit(f'Missing AIMI name in {name}')
    if re.search(r'\b(?:ALIVE|REVEAL)\b|Full Astra',body):raise SystemExit(f'Obsolete method label in {name}')
abstract=Path('sections/00_abstract.tex').read_text()
if abstract.count('AIMI')!=1:raise SystemExit('Abstract must name AIMI only at its introduction')
if 'Language-Guided Visual Exploration' not in text:raise SystemExit('New task framing absent from main PDF')

intro=Path('sections/01_introduction.tex').read_text()
if r'\textbf{A}gentic \textbf{I}n-hand \textbf{M}anipulation for \textbf{I}nspection' not in intro:
    raise SystemExit('AIMI name expansion is missing or inconsistent')
for path in [Path('main.tex'),Path('supplyment.tex'),Path('preamble.tex'),*Path('sections').glob('*.tex'),*Path('tables').glob('*.tex')]:
    if re.search(r'\bALIVE\b|\bREVEAL\b|HardwareAliveSuccess',path.read_text()):
        raise SystemExit(f'Old method name in active source: {path}')

for title in ('Supplementary Material','Overview','Adaptive versus fixed inspection','Reproducibility','Independent Pose Estimation'):
    if title not in supp:raise SystemExit(f'Missing supplementary section: {title}')
if '\\input{sections/supplement_content}' in Path('main.tex').read_text():
    raise SystemExit('Main source still includes supplement')
print(f'Main body: {llm[0]} pages before LLM statement and references')
print(f'Standalone main: {len(pages)} pages; standalone supplement: {len(supp.rstrip(chr(12)).split(chr(12)))} pages')
PY_CHECK
