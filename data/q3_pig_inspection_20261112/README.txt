Pig Q3 inspection-policy study: compact auditable paper export
============================================================

This archive contains the completed Pig cohort, separate from Cube Q3(b),
Cube Q3(c), Q1, Q2, engineering checks, and admission smoke runs. It contains
80 formal episodes: 40 exactly matched pairs, 20 pairs under each evaluation
seed 188301 and 188302. Physical failures are retained. No formal pair is
service-excluded or replaced. Earlier admission diagnostics, including an
HTTP 504 in a failed smoke attempt, are not formal experimental observations.

Reproduce from the paper repository root (Python standard library only):

    python3 scripts/render_q3_pig_inspection.py
    python3 scripts/render_q3_pig_inspection.py --check

The first command regenerates derived statistics and the five-column table
macro. --check is read-only and verifies input hashes, identities, action and
binding reconstruction, exact state/first-frame pairing, success scoring,
the generated statistics, and the generated LaTeX table. It does not require
the original experiment directory, Pillow, a GPU, model weights, or a network.
The optional --import-from argument was used once to export local original
records. Import additionally requires Pillow and verifies all 231 PNG pixel
digests against agent-input and returned transport records, the 1,254 frozen
source files, and eight frozen artifacts. It does not load a model or run a
simulation. Import and --check cannot be combined.

Files
-----
trials.jsonl: 80 complete original episode rows, including numerical initial
states and their hashes, final quaternion/pose error, raw reason, terminal
binding, stop measurement, and source references. A source wrapper adds the
condition, first-frame hashes, and original relative file names.
calls.jsonl: all 231 formal returned calls, retaining proposed and executed
tools/arguments, request/delivery/application steps, elapsed latency, usage,
actual-action feedback, input/transport hashes, and source references.
actions.jsonl: all 221 applied action-ledger entries; model proposals and
actually executed arguments are both retained. Startup drops can have no
applied actions and no original action-ledger file.
release.json, protocol.json, model_config.json: sanitized frozen configuration,
pre-formal protocol, 40 planned cases, model/prompt/tool settings, shared pose
noise and runtime settings, and artifact hashes. protocol.json preserves the
original planning document's draft labels; release.json records formal frozen
status. No weights are distributed. The hosted route name does not identify
immutable provider model weights.
source_sha256.json: original experiment-relative source-file hashes and the
complete frozen source inventory. Absolute workstation paths are normalized
to relative archive identities; their contents are not bundled wholesale.
audit.json: existing independent-audit status/provenance, source/artifact
verification counts, evidence ZIP hash, and binding definitions. Its historical
audit assertions are distinguished from this compact script's offline checks.
export_manifest.json: SHA256 values of the eight immutable exported inputs.
summary.json, paired_trials.json, trial_metrics.jsonl,
fixed_inspections.jsonl: deterministic derived outputs. paired_trials.json
contains all 40 paired outcomes, not a table inferred from marginal totals.
fixed_inspections.jsonl contains all 79 executed fixed inspections.
The generated table is tables/q3_pig_inspection_macros.tex and defines
\PigInspectionPolicyRows.

Experimental and statistical scope
----------------------------------
Both arms use the same object-specific motor weights, noisy simulator pose,
online model configuration, fresh RGB, feedback schema, calibrated stop gate,
six-call limit and 120 simulated-second horizon at 20 Hz. Only applied
inspect_face motor choices and commanded durations are overridden in the
fixed arm: cycle 2,4,1,3,6,5 for 60 steps each. The agent still chooses whether
to inspect, bind, verify, stop or abstain. History reports actual execution in
both arms. Cases are paired by index, base_seed and trial_seed, with exact
physical initial state and first input frame. Seed splits are evaluation
blocks, not independently trained policies.

This follow-up was planned after the Cube inspection result. The Pig sample
size and within-study primary success test were frozen before formal data
collection. The primary test is two-sided exact McNemar on 40 pairs; reported
p=0.0078125 is unadjusted. No cross-study multiplicity family was prespecified.
The counts are both-success 29, adaptive-only 8, fixed-only 0, both-failure 3.
Do not pool this cohort with Cube as one homogeneous primary experiment.
Per-seed tests, binding and cost breakdowns are descriptive secondary reports.
The paired percentile bootstrap interval [0.075, 0.325] for the observed
0.20 success-rate difference uses Python random seed 188399, 20,000 resamples,
and sorted zero-based indices 499/19499. This is a descriptive interval,
not an exact confidence interval. No additional trials followed the result.

Success and binding are different quantities
--------------------------------------------
Success requires autonomous stopping, the correct physical motor-goal and
requested-label binding, true full-quaternion error <=0.16 radians, and no
terminal drop. A favorable earlier pose alone is insufficient. There is no
post-stop hold test and no independent human initial-visibility annotation.

Terminal and ever binding are reconstructed from applied actions, without
using success as a proxy. inspect_face clears the current binding. Applied
reorient_target, verify_target or stop declares the motor ID and label.
abstain and the physical-drop branch do not clear a previous binding.
Terminal-correct requires both the physical goal and requested label to
match at episode exit. Ever-correct requires any such applied binding,
regardless of later actions or failure. First-correct call includes the input
that produced the declaration. Never-bound and never-correct episodes remain
explicit; they must not be discarded as if acquisition were faster.
Unapplied replies do not affect binding. These declarations are not measured
visual recognition events. In this cohort terminal-correct counts happen to
equal success counts, but the script derives them independently.

Costs and provenance
--------------------
Adaptive/fixed calls are 106/125 and reported total tokens are 262832/355456.
All returned formal calls count, including five unapplied replies per arm.
Provider token-attribution dictionaries containing response/item IDs are
removed; input/output/total counts and aggregate cache/reasoning details are
retained. Missing usage would produce a null total plus explicit known sum
and missing-call count, not zero. The actual export has complete usage.
Commanded inspection times are 235/237 seconds over 61/79 inspections.
These commands, logical episode times, measured request latency and token
costs are distinct quantities; fewer calls do not establish faster control.

Original hashes refer to original file bytes. Sanitized exports intentionally
have different bytes and are covered by export_manifest.json. No accounts,
credentials, response IDs, absolute local paths, checkpoints, PNGs, or image
ZIPs are distributed here. PNG file/pixel hashes allow linkage to the complete
evidence archive, whose independent review and ZIP hash are recorded in
audit.json. Offline checks validate the retained digest correspondence; they
cannot re-decode omitted images or repeat the full physical-step audit.
