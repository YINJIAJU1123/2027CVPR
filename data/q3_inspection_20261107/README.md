# Q3: adaptive versus fixed inspection

This separate cube cohort contains 80 formal trials: seeds 187301 and 187302, 20 per seed per arm. Both arms are newly evaluated. Two admission trials are excluded. All 40 formal pairs have matching initial state and image hashes; there are no service exclusions.

- `summary.json`: terminal outcomes, per-seed successes, call counts, tokens, latency and first-correct-binding-call distributions.
- `protocol.json`: intervention, preserved controls, fixed order, budget, stopping and analysis scope.
- `audit.json`: audit status and hashes of locally retained source records. Raw trajectories, model inputs, credentials and account details are not published in this package.
- `statistics.json`: generated exact paired success test and individual-rate Wilson intervals.

Adaptive inspection succeeds in 38/40 trials versus 31/40 for a fixed sweep. The paired table is 29 shared successes, 9 adaptive-only, 2 fixed-only, 0 shared failures. The observed gain is 17.5 percentage points; two-sided exact McNemar p=0.0654296875, not statistically significant at 0.05. Do not extend the sample based on this p-value.

The fixed arm changes only the color and duration of `inspect_face`: green, yellow, red, blue, magenta, cyan; 90 steps each. Both arms retain semantic decisions about whether to inspect, bind, verify, stop or abstain. Both receive actual executed actions in the same feedback schema. Their realized histories, trajectories and costs differ.

Correct terminal bindings are 39 versus 32. Never correctly bound trials are 1 versus 8. First-correct-binding call distributions must retain those never-bound outcomes; conditional-only averages do not establish acquisition efficiency. Declared binding is not independent visual-recognition ground truth.

Run `python3 scripts/render_q3_inspection.py --check` from the repository root. This validates the exported aggregate arithmetic and reproduces the table and paired test. It does not re-audit private source trajectories; hashes and their original independent audit outcome are retained separately.
