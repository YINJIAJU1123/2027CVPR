#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
mkdir -p build/main build/supplement output/pdf
python3 scripts/render_language_table_image.py --check
python3 scripts/render_q1_summary.py > build/q1_summary.log
python3 scripts/render_controller_three_seed.py > build/controller_three_seed.log
for target in main supplement; do
    if [[ -n "${TECTONIC:-}" ]]; then
        "$TECTONIC" --keep-logs --keep-intermediates --outdir "build/$target" "$target.tex"
    elif command -v tectonic >/dev/null 2>&1; then
        tectonic --keep-logs --keep-intermediates --outdir "build/$target" "$target.tex"
    elif command -v latexmk >/dev/null 2>&1; then
        latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="build/$target" "$target.tex"
    else
        printf '%s\n' 'Install Tectonic or latexmk, or set TECTONIC.' >&2
        exit 1
    fi
done
cp build/main/main.pdf output/pdf/agenticrotation-2027.pdf
cp build/supplement/supplement.pdf output/pdf/agenticrotation-2027-supplement.pdf
