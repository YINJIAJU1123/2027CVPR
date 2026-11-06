#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
for log in build/main/main.log build/supplement/supplement.log; do
    [[ -s "$log" ]] || { printf 'Missing build log: %s\n' "$log" >&2; exit 1; }
done
if rg -n 'undefined references|Citation .+ undefined|LaTeX Error|Overfull \\hbox|Overfull \\vbox' build/main/main.log build/supplement/supplement.log; then
    exit 1
fi
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027.pdf | head -18
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027-supplement.pdf | head -18

python3 - <<'PY_CHECK'
import os,re,subprocess
text=subprocess.check_output([os.environ.get('PDFTOTEXT','/usr/bin/pdftotext'),'-layout','output/pdf/agenticrotation-2027.pdf','-'],text=True)
pages=text.split('\f')
llm=[i for i,page in enumerate(pages) if re.search(r'^\s*(?:\d+\s+)?LLM Usage Statement(?:\s{2,}|$)',page,re.M)]
refs=[i for i,page in enumerate(pages) if re.search(r'^\s*(?:\d+\s+)?References(?:\s{2,}|$)',page,re.M)]
if not llm or not refs:raise SystemExit('LLM statement or references boundary missing')
if llm[0]>8:raise SystemExit('Main body exceeds eight pages')
if text.index('LLM Usage Statement')>text.index('References'):raise SystemExit('LLM statement must precede references')
print(f'Main body: {llm[0]} pages before LLM statement and references')
PY_CHECK
