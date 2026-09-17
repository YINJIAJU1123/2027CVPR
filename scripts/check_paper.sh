#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
[[ -s build/main.log && -s output/pdf/research_scaffold.pdf ]] || {
    printf '%s\n' 'Run make paper first.' >&2
    exit 1
}
if grep -Ein 'undefined|multiply defined|Overfull|^!|Missing character|There were.*warnings' build/main.log; then
    printf '%s\n' 'Resolve the reported LaTeX issues before accepting this build.' >&2
    exit 1
fi
if [[ -f build/main.blg ]] && grep -Ein 'Warning--|error message' build/main.blg; then
    printf '%s\n' 'Resolve the reported bibliography issues.' >&2
    exit 1
fi
if command -v pdfinfo >/dev/null 2>&1; then
    pdfinfo output/pdf/research_scaffold.pdf
fi
printf '%s\n' 'Compilation and reference checks passed. Render and visually inspect after layout changes.'
