# Frozen VLM audit, 2026-10-29

These files audit the existing cube-v1 results. They do not add task-success trials.

- `formal_record_audit.json`: independent checks of 40 recorded trials per primary method and actual inference latency.
- `summary.json`: 40 development-validation observations under four input conditions, 160 model requests. Readability uses weak geometric labels.
- `adapter_check.json`: 40 enabled outputs exactly match the service; disabling LoRA tests dependence, not a fair baseline.
- `pixel_overlap_audit.json`: all 130 formal VLM input images differ exactly from the four known training/validation capture datasets. This does not exclude near-duplicates or fixed-layout shortcuts.

No evidence found here invalidates the recorded 27/40 fine-tuned VLM result. Held-out letter/color reassignment is still needed to test fixed-layout memory. The original semantic benchmark and checkpoints remain unchanged.
