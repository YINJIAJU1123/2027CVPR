# Citation corrections — 2026-11-17, v26

Scope: four author-requested corrections, checked with the Academic Research Suite citation-check workflow. This is not a fresh audit of every reference.

## Changes and primary evidence
1. **[9] Chen et al.** is now cited only after multi-object reorientation in simulation. Physical-hand control is supported separately by **[1,18]**. Chen et al., section 2.1 (PDF page 3) state that their policies are not tested on a real robot; section 6 (PDF page 8) likewise limits presented results to simulation. Source: https://proceedings.mlr.press/v164/chen22a/chen22a.pdf . Qi et al.'s abstract describes deployment to a real hand: https://proceedings.mlr.press/v205/qi23a.html .
2. **[24] ENPIRE**: added `howpublished={arXiv preprint arXiv:2606.19980}`. The pre-existing eprint metadata was not displayed by the current bibliography style; the new field appears in the compiled reference. Source: https://arxiv.org/abs/2606.19980 .
3. **[23] FoundationPose**: added `pages={17868--17879}`. Verified against the official CVF indexed BibTeX record (direct HTML fetch returned 403): https://openaccess.thecvf.com/content/CVPR2024/html/Wen_FoundationPose_Unified_6D_Pose_Estimation_and_Tracking_of_Novel_Objects_CVPR_2024_paper.html .
4. **[13] SayCan**: protected both first-person pronouns with `{I}` so BibTeX sentence casing does not lowercase them. Brian Ichter remains first author, matching the selected PMLR record: https://proceedings.mlr.press/v205/ichter23a.html .

## Replacement sentence
Reinforcement learning has enabled multi-object reorientation in simulation [9] and in-hand control on physical hands [1,18].

## Verification
- Main and supplementary sources compiled before and after changes with latexmk/pdflatex.
- LaTeX guard: zero errors and zero warnings.
- No new undefined citations/references, overfull boxes, or compilation errors.
- Main PDF: 8 body pages, 10 pages total; supplement: 17 pages.
- Citation keys, order and reference numbers preserved.
- Only `references.bib` and `sections/02_related_work.tex` changed among manuscript source files.
- Main pages 2, 3, 9 and 10 changed; other main pages remained pixel-identical. Only supplementary page 17 changed.
- Inspected affected page renders. No clipping or overlap.
- Abstract, experimental data, figures, limitations, Figure 6 placement and template retained.
- No commit or push performed.
