#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
if rg -n 'undefined references|Citation .+ undefined|LaTeX Error|Overfull \\hbox|Overfull \\vbox' build/main/main.log build/supplement/supplement.log; then
    exit 1
fi
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027.pdf | head -18
${PDFINFO:-pdfinfo} output/pdf/agenticrotation-2027-supplement.pdf | head -18
