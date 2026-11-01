# Completed cube evidence, 2026-11-01

This snapshot contains 760 live semantic records and summaries of a separate 160-trial fixed-plan development study. It updates the paper without running new experiments or altering success definitions.

| Study | Raw trials | Primary matched result |
|---|---:|---|
| Latest native main | 120 | Astra 35/40, bare fine-tuned 30/40, bare rule 17/40 |
| Waiting refit | 80 | Original 27/39, refit 33/39, drops 10 to 5 |
| Feedback | 80 | Initial plan 7/39, full feedback 30/39 |
| Explicit controller goal | 120 | Correct 25/36, no explicit 24/36, shuffled 30/36 |
| Visual intervention | 360 | Identity/permutation: Astra 32/40 to 32/40, FT 30/40 to 16/40, rule 23/40 to 23/40 |
| Fixed-plan execution-gate development | 160 | Original 29/40, fixed 27/40, phase-fixed 24/40, learned 26/40. Rejected. |

The visual archive includes the previously exported 240 bare-VLM records. Those are overlapping records, not additional experiments. The native main uses refitted waiting with original execution. Feedback and visual studies retain original actors. These studies cannot be pooled into a common success rate or treated as a single checkpoint ablation.

All success rates require correct semantic binding and true canonical orientation error at most 0.16 rad at autonomous stop. Stop decisions use estimated pose. Service exclusions are symmetric within the relevant comparison. For image contrasts, eligibility is pairwise: identity/permutation has 40 trials, Astra identity/masked has 39 with successes 31 versus zero. Global common-39 visual outcomes in the audit are auxiliary.

The visual images are reconstructed face images, including identity, with the low-level pose input unchanged. This is not the native-image main comparison. Feedback compares one call against up to six, so it does not isolate feedback at equal compute. Explicit actor-goal conditioning is unsupported. The learned execution gate failed its development rule and was not deployed.

`provenance.json` records source SHA-256 values. Trial exports retain only evaluation fields and initial-state hashes, without runtime endpoints, credentials or machine paths. Full state and action traces remain in the research archive. `python3 scripts/render_completed.py` validates counts, outcome consistency, matching, exclusions and paired tests before generating tables. `SHA256SUMS` protects the exported snapshot. No new model calls are made by this script.
