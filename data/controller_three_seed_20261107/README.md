# Three-seed controller summary (2026-11-07)

User-confirmed reporting correction: the earlier four-arm 40-trial counts correspond to seed 187102. Seeds 187103 and 187104 provide another 80 trials per arm. Each arm therefore has 120 trials across three seeds.

The user supplied additional waiting-drop / execution-drop / other-failure counts as 17/9/6, 9/8/5, 6/7/13 and 1/3/6, in method order. Successful counts remain 48, 58, 54 and 70. Initial 40-trial outcomes remain 25/7/5/3, 30/4/0/6, 28/1/7/4 and 34/4/1/1 (success/wait-drop/exec-drop/other).

The corrected labels supersede the controller seed grouping in the manuscript, without rewriting historical per-trial archives. This is a user-confirmed aggregate update, not a newly run or independently audited trial-level release. Separate 187103/187104 outcome counts and pairing records are unavailable; no paired p-values or seed-level variance are computed. Unknown service handling is not inferred from the arithmetic partition. Following the author's final scope clarification, historical controller-confirmation panels are no longer presented as formal Q2 results. Their original archived records are preserved separately; Q2 uses only the three seeds above.

Generate the manuscript table with `python3 scripts/render_controller_three_seed.py`.
