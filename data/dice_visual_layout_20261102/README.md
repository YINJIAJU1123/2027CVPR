# Dice visual-layout study

Six cells: identity/permuted by Astra, bare fine-tuned VLM and bare rule VLM. Each cell contains 40 scheduled trials over the same two reset seeds.

The visual mesh is rotated while collision and inertia are unchanged. A shared prompt distinguishes fixed motor-skill IDs from printed pip counts. The mapping is not passed to the models and does not remap their actions. The fine-tuned model retains its original continuous latent and native-layout weights.

Use the recorded matched eligibility from summary.json. Raw failures and exclusions are retained in trials.json. Do not replace excluded episodes or pool this protocol with the native-main comparison. Individual rate intervals and paired tests have different interpretations; absence of a significant difference is not equivalence.

Cube and dice use different perception/control backends. This study uses noisy simulator pose, not a visual pose estimator. It does not establish hardware or unseen-object transfer. Account credentials and provider transport logs are omitted.
