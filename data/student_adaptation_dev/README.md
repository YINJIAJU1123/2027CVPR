# Completed student adaptation development study

Separate from frozen cube-v1. All 160 physical diagnostic episodes completed with valid logs. Seeds 183221/183222, 20 trials per seed per condition. Initial state hashes match exactly across all four arms.

| Policy | Reach | Drops |
|---|---:|---:|
| Released pose-goal student | 39/40 | 1 |
| Frozen latent student | 38/40 | 2 |
| Extra simulated-noise DAgger | 39/40 | 1 |
| Extra actual-CNN DAgger | 40/40 | 0 |

The CNN candidate satisfies the prespecified development admission rule. No automatic deployment. Exact paired p=0.5 against the frozen latent policy and p=1.0 against extra simulated training. These are physical reach measurements without a language supervisor, not autonomous semantic success. The pose CNN is frozen in both training branches.

A future release requires controller compatibility and fresh semantic evaluation. Do not replace the frozen cube-v1 numbers or compare its old 35/40 cohort directly to the new 40/40 as a paired gain.
