# Cube follow-up evidence, 2026-10-30

This snapshot extends the paper without replacing cube-v1. Model credentials, host addresses and API configuration are not included.

- `replication_complete.json`: all 120 independent-replication records, with three common service exclusions and matched success counts 26/37, 27/37 and 21/37. Includes source hashes and exploratory paired tests.
- `replication_snapshot.json`: historical 18-slot Astra prefix and two completed 40-slot VLM arms, retained only for provenance. These 98 records overlap the complete archive and add no trials.
- `module_effects.json`: reanalysis of the existing four-arm cube-v1 control factorial on 37 common valid slots. This adds no trials.
- `visual_interventions.json`: 240 completed bare-VLM trials, 40 per condition. Astra interventions are pending. Input interventions act only on the upper-level model.
- `paired_recovery.json`: 19 verified states, two assigned goals and two controller conditions (76 branches). State 12 was unavailable. These are recovery diagnostics, not autonomous semantic success.
- `provenance.json`: numerical source checksums and scope.

Service failures are excluded from the primary success denominator using the existing protocol. Raw outcomes remain auditable, and ordinary task failures are retained. A recorded drop may coexist with a service exclusion. Never classify eligibility using the terminal reason alone.

Run `python3 scripts/render_followup.py` to validate and regenerate the follow-up tables. The complete follow-up table uses the same 37 eligible trial IDs for all methods. No partial prefix is used for its rates.
