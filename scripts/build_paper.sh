#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
mkdir -p build/main build/supplyment output/pdf
python3 scripts/render_language_table_image.py --check
python3 scripts/render_q1_summary.py > build/q1_summary.log
python3 scripts/render_controller_three_seed.py > build/controller_three_seed.log
python3 scripts/render_q3_inspection.py > build/q3_inspection.log
python3 scripts/render_q3_pig_inspection.py > build/q3_pig_inspection.log
python3 scripts/render_result_presentation.py > build/result_presentation.log
python3 scripts/render_task_success.py > build/task_success.log
for target in main supplyment; do
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
cp build/main/main.pdf output/pdf/main.pdf
cp build/supplyment/supplyment.pdf output/pdf/supplyment.pdf
