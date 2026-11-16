# LaTeX / figure revision report

Base: d437e8ada7748d6899c229f338bee9346087dcd6.

- Main compiled with latexmk/pdflatex: 8 body pages + 2 pages for the usage statement and references (10 total). Baseline body occupied 9 pages.
- Supplement compiled separately: 17 pages. Corresponding exploration and sim/real images synchronized; obsolete empty real-case mockup removed (its label had no references).
- All five illustrative PDFs replaced with v23. Q1 bar chart is unchanged.
- Abstract is byte-identical; all result tables/macros are unchanged, except the hardware table is scaled to the column width. Numeric contents of that table are identical.
- Results prose was shortened to remove repeated explanations and fit the eight-page body; no measured results were added or removed.
- Standard CVPR text size, page dimensions and margins retained. Pipeline now appears on page 2. Single-column mechanism figures are 96% of column width.
- LaTeX guard: 0 errors / 0 warnings for main. Final compile has no overfull boxes or undefined references. Template fixltx2e and caption hypcap warnings are unchanged and non-fatal.
- Visually checked all 10 main pages, all five figure exports and the changed supplement figure page. HTML image loads passed, and no tracked HTML text boxes overflow.

## Provenance / limits

- Figure 1: real frames supplied in the user ZIP; face icons and agent-decision text are illustrative annotations, not logged replies.
- Figure 2: vector HTML, goal embedding reaches the motor student through projection and also conditions the local controllers. Circular photo arrangement is not a joint trajectory.
- Figures 3–5: cropped vector exports of the approved v22 deck, preserving its content. Hedgehog and milk-carton scenes remain marked as posed illustrations.
- The original ZIP and PPTX were not overwritten.
- Existing supplement TODOs concerning physical protocol details and licenses remain; this revision is not a new experiment or full supplementary-material audit.
- No commit or push performed.
