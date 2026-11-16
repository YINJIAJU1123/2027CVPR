# Layout revision v27 — 2026-11-17

## Changes
- Set Q1–Q4 as separate, aligned list items under Experiments, retaining the exact original question wording.
- Restored the standard float spacing by removing the previously compressed global overrides and the locally compressed language-table spacing.
- Removed the previous -120pt last-page column-height adjustment.
- Increased table row spacing modestly (arraystretch 1.10, main-paper tables only).
- Increased the language-coverage table from footnotesize to small.
- Used full column width for the two mechanism figures and full text width for the Q1 chart. Figure artwork and aspect ratios were not changed.
- Queued Figure 6 after the controller figure so it remains Figure 6 on page 7.

## Verification
- Baseline and final builds succeeded with latexmk/pdflatex.
- Main paper body: 8 complete pages. Total PDF: 10 pages, including the usage statement and bibliography.
- The last body page now uses the available column depth without the earlier large empty region.
- Original question text, experimental prose and data are unchanged (source-normalization comparison).
- Abstract, introduction, related work, method, discussion, limitations, bibliography, figures and supplemental content are unchanged.
- Page 1 is pixel-identical to the previous PDF.
- Bibliography entries and numbering are unchanged.
- CVPR style, page geometry, body font and body line spacing are unchanged.
- LaTeX guard found zero errors and zero warnings. No overfull boxes, unresolved citations or references in the final build.
- Reviewed all-page overview and full-size pages 5–8 for layout. No clipping or overlap.
- Existing compatibility warning for fixltx2e and teaser caption hypcap warning remain.
- The supplement does not include the modified language-summary table; its PDF is unaffected.
- This revision is saved locally; no commit or push was performed.
