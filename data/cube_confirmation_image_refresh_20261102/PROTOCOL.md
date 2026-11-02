# Independent controller confirmation and upper-image refresh study

## Scope and stopping rule

Run the two approved studies in order, audit all registered outcomes, then stop.
Do not tune checkpoints, exclude physical failures, add trials after inspecting
success rates, or change the frozen autonomous-stop criterion.

Release: `outputs/pose_latent_student_v1/confirm_wait_image_20261102_v1/formal_release.json`

Release SHA256: `e58c7c2d125005eddb52a46b86b3df2fafe1eddfae6b3606d08fd8b00de37c96`

Parent: the completed cube waiting/feedback study of November 1. Its evaluator,
weights, student, perception, physical parameters, prompt, stop condition and
six-call maximum are retained. The new evaluator only adds the upper-image
selector and its image audit. The reverse-patch admission recovers the parent
evaluator exactly. The parent metadata retains historical cohort fields. The
new release's explicit `cohorts` field and executable guard define the new seeds.

## Registered conditions

| Study | Conditions | Seeds | Trials |
| --- | --- | --- | --- |
| Controller confirmation | Continue, fixed slowing, full learned speed and residual | 187101, 187102 | 20 per seed per condition, 120 total |
| Image refresh | Full Astra with fresh RGB, full Astra with repeated initial RGB | 187201, 187202 | 20 per seed per condition, 80 total |

The five one-episode admission runs use separate seed 187091 and never enter
formal success estimates. Condition order reverses on the second seed within
each study. The controller and image studies have distinct cohorts.

## Intervention boundaries

Only the upper agent's RGB is frozen in the frozen-image arm. The local student,
pose predictor, numeric pose feedback, control state, action history and physics
remain live. Every request saves both the current image and the submitted image.
Pixel hashes are checked against the returned transport ledger. The initial
physical states and first RGB images must match across conditions within each
study. The audit counts later live images that actually differ from the first.

All confirmation arms use the same frozen execution controller outside waits.
While a response is pending, continue uses speed 1 without residual, fixed slow
uses speed 0.15 without residual, and full uses the learned speed and residual.
Simulation continues through inference. The independent audit verifies contiguous
pending control steps and that responses are not applied before their measured
latency has elapsed in simulation time.

## Outcomes and statistics

The success definition is unchanged: autonomous stop, correctly bound requested
semantic target, full quaternion error at most 0.16 rad, and no preceding drop.
Merely reaching tolerance is not a success. Report success, drops by phase,
false stops, abstentions, horizons, durations, actual calls, tokens and delays.

Primary tests are full controller versus fixed slow, and fresh versus frozen
RGB. Use exact paired two-sided McNemar and Holm correction over these two tests.
Report unadjusted tests, paired percentage-point differences, per-seed counts and
Wilson intervals. Full versus continue is a predeclared secondary comparison.
Forty trials can leave uncertainty even when point estimates differ.

Use common service eligibility across the three controller arms, and separately
across the two image arms. Preserve all raw visited outcomes. A service error or
measured latency above 120 seconds triggers the existing exclusion rule. Stop
and audit an interruption before registering only the unvisited continuation.
Never replace a physical failure or retry an excluded formal slot for its score.

The same maximum call count is not the same realized compute. Image changes can
alter tool choices, request counts, latency and the subsequent trajectory. Report
those measurements and describe this as an upper-RGB intervention with other
feedback retained, not an equal-compute or removal-of-all-vision experiment.

## Execution and audit

- Queue: `scripts/confirm_wait_image_v1/queue.py`
- Condition driver: `scripts/confirm_wait_image_v1/run_condition.py`
- Offline admission: `scripts/confirm_wait_image_v1/check_intervention.py`
- Live smoke image/transport admission: `scripts/confirm_wait_image_v1/audit_images.py`
- Full independent audit: `scripts/confirm_wait_image_v1/audit_results.py`

`queue_status.json` and the live PID/start-time pair identify runtime state.
`activation.json` is written only after all five smoke admissions and matched
initial-state/image checks pass. A queue completion flag alone is insufficient:
the full independent audit and actual 200-trial coverage are required.

No credentials or bridge key belong in paper exports. This study does not start
new training, additional object experiments, or a recurring automation.
