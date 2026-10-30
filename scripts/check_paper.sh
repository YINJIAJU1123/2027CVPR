#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
if rg -n 'undefined references|Citation .+ undefined|LaTeX Error|Overfull \\hbox|Overfull \\vbox' build/main/main.log build/supplement/supplement.log; then
    exit 1
fi
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027.pdf | head -18
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027-supplement.pdf | head -18

python3 - <<'PY_CHECK'
import os,re,subprocess
text=subprocess.check_output([os.environ.get('PDFTOTEXT','/usr/bin/pdftotext'),'-layout','output/pdf/agenticrotation-2027.pdf','-'],text=True)
pages=text.split('\f')
refs=[i for i,page in enumerate(pages) if re.search(r'^\s*(?:\d+\s+)?References(?:\s{2,}|$)',page,re.M)]
if not refs:raise SystemExit('References boundary not found; inspect the PDF')
if refs[0]>8:raise SystemExit('Main body exceeds eight pages')
print(f'Main body: {refs[0]} pages before references')
PY_CHECK
