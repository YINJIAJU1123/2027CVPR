# Native-layout die comparison

Two seeds and 40 scheduled trials per method, no service exclusions. Astra
24/40, bare fine-tuned VLM 20/40, bare rule VLM 17/40. These are simulation
results with noisy/delayed simulator pose, not a pose-estimator evaluation.
Astra uses the dice maintenance actor and calibrated completion correction.
The local baselines have neither module. The policy and controller weights are
object-specific. Do not pool with the cube controller ablation or with the
ongoing dice layout-shift study. The latter has a new shared skill-ID contract.

Exact paired Astra-versus-fine-tuned p=0.4545. Fifteen Astra drops include twelve
before the first skill arrives. A higher point estimate is not proof of a
provider ranking or a controller benefit on this object.
