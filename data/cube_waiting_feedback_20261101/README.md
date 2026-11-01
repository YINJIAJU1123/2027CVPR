# Matched waiting and feedback study

Five conditions each contain 40 new raw trials, with two matched seeds and 20 trials per seed. The full learned waiting condition is shared between the four-arm waiting comparison and the two-arm feedback comparison, for 200 raw trials in total.

The primary waiting comparison removes any service-affected slot from all four waiting arms. The feedback comparison removes any such slot from both feedback arms. All raw records remain in trials.json. No visited slot is replaced. Three adjacent waiting contrasts use Holm correction within that family. The separate feedback contrast has different inference budgets.

All conditions use the frozen task success and stopping rules. They run on one local GPU and the same physical assets. The speed-only actor was fitted under the zero-waiting-residual constraint, not modified only at test time. Training reproduction and action-branch audits are included.

The records do not claim real-time simulator throughput, an equal-compute feedback effect, multi-object generalization, or hardware success. Predictor and physical-hand results remain separate planned work. No OAuth credentials, bridge secrets, account identity records, or raw API response identifiers are included.
