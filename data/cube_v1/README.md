# RSLCube cube-v1 frozen evidence

Object: one fixed marked cube. Frozen student and module checksums are in `weight_hashes.json`.

- `trials.json`: 400 distinct (condition, trial_seed) records. 320 semantic and 80 low-level physical diagnostics.
- `parent_summary.json`: original 320-trial suite.
- `addendum_summary.json`: 80 new bare-baseline trials plus read-only references to previous cells. Do not add the borrowed cells again.
- `runtime_contracts.json`: sensor, mapping, policy and evaluation contracts with runtime paths removed.
- `astra_phase_analysis.json`: descriptive public-decision/phase audit. Not a causal ablation.
- `source_manifest.json`: SHA256 of original local evidence.
- `student_successor_plan.json`: separate development plan. Its results are not part of cube-v1.

The original local archive is `outputs/frozen_results/RSLCube/cube-v1-20261029` within the implementation workspace. Original files are copied without alteration and made read-only. Public exports omit transport and authorization details. Hashes of public files are recorded in `SHA256SUMS`.

Primary autonomous success requires a correct semantic binding and true canonical quaternion error <=0.16 rad at autonomous stop, with no previous drop. Drop is displacement >=0.24 m from the nominal grasp position. No extra holding duration. A service failure or call latency >120 s is excluded symmetrically within each panel, while retaining all raw outcomes.

The physical diagnostic is reach-before-drop under its own released horizon. It is not interchangeable with semantic completion. The fixed letter/color arrangement does not demonstrate unseen-layout grounding.
