# Template, study boundaries and related work update (2026-11-07)

## Official template verification

Official guidelines: https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines

The linked v1 archive was re-downloaded. SHA256: da1ec5db9b73531ea82a87723e4aedb631083331fe655d1972279b48a7bdb2fe. Both official style files match the manuscript byte-for-byte; no style replacement was needed. Body remains limited to eight pages, with LLM Usage Statement and cited references after the body.

## Experiment interpretation

Q1's equal-object means are distinct from cube-only Q2. Q1 cube original and changed mappings each report 32/40 (80.0%); Q2's full controller reports 104/120 (86.7%) in its separate three-seed cohort. Different observed rates do not by themselves establish inconsistency or an improvement between studies. We retain all reported counts and explicitly restrict controller contrasts to Q2. Distinct cohorts do not excuse undocumented changes in scoring or model settings.

At the time of this earlier update, Q3 was a two-panel table (superseded by the three-panel inspection-policy update in `q3_inspection_update_20261107.txt`): (a) initial planning versus continued feedback; (b) repeated first frame versus current image. The panels remain separate cohorts, with respective service-eligible denominators and raw call totals. Q3(a)'s full-feedback arm reuses the initial 40-trial Q2 subset; it is not new independent replication. Seed and archived trial identifiers retain the provenance described in controller_update_20261107.md.

## Added literature and primary verification sources

Ten references added and cited in Related Work (13 -> 23):
- Learning Dexterous In-Hand Manipulation: https://arxiv.org/abs/1808.00177
- A System for General In-Hand Object Re-Orientation: https://proceedings.mlr.press/v164/chen22a.html
- In-Hand Object Rotation via Rapid Motor Adaptation: https://proceedings.mlr.press/v205/qi23a.html
- General In-Hand Object Rotation with Vision and Touch (RotateIt): https://proceedings.mlr.press/v229/qi23a.html
- AnyRotate: https://proceedings.mlr.press/v270/yang25c.html
- SayCan: https://proceedings.mlr.press/v205/ichter23a.html
- Inner Monologue: https://proceedings.mlr.press/v205/huang23c.html
- Code as Policies: https://arxiv.org/abs/2209.07753
- VoxPoser: https://proceedings.mlr.press/v229/huang23b.html
- ReKep: https://proceedings.mlr.press/v270/huang25g.html

PMLR entries use the publication year printed in the proceedings BibTeX, which can differ from the conference event year. Prior metadata and numerical results were not changed by this update. No new claims of controller significance or hardware success were introduced.
