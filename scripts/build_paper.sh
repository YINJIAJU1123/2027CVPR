#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
mkdir -p build output/pdf

if [[ -n "${TECTONIC:-}" ]]; then
    "$TECTONIC" --keep-logs --keep-intermediates --outdir build main.tex
elif command -v tectonic >/dev/null 2>&1; then
    tectonic --keep-logs --keep-intermediates --outdir build main.tex
elif command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
else
    printf '%s\n' 'Install Tectonic or latexmk, or set TECTONIC to its executable path.' >&2
    exit 1
fi
cp build/main.pdf output/pdf/research_scaffold.pdf
printf '%s\n' 'Built output/pdf/research_scaffold.pdf'
