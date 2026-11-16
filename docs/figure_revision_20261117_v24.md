# Figure / title layout revision v24

- Baseline: current uncommitted local revision on d437e8a, compiled successfully (8 body pages).
- Teaser: dark wordmark; blue subtitle and 3 large backgrounds removed; native HTML text preserved; shown at 98% text width (was 85%).
- Pipeline: exact vector export of approved v22 PPTX slide 2, cropped only outside the diagram. Caption updated for its actual arrow colors.
- Title: main.tex locally overrides the title-to-author gap (24 to 4 pt), author trailing skip (0.5 em to 0), and trailing title skip (12 to 2 pt), with -12 pt after the title block. The shared cvpr.sty is unchanged. Removed the additional center environment and added a positive caption-to-abstract gap. These local spacing changes follow the user's request; no new template-compliance claim is made.
- Abstract: byte-identical, entirely on page 1 left column. No prose or experimental values changed.
- Figure 6 float queued later to remain beside Q4 on page 8.
- Main: 10 total pages = 8 body + 2 usage-statement/reference pages. No overfull boxes or unresolved references in the final log; latex_guard: 0 errors, 0 warnings.
- Reviewed the enlarged first-page teaser, restored pipeline, mechanism figures and Q4 placement in rendered pages.
- Supplement not changed in this revision.
- No git commit or push.
