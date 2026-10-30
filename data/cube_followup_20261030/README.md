# Cube follow-up evidence, 2026-10-30

This snapshot extends the paper without replacing cube-v1. Model credentials, host addresses and API configuration are not included.

- `replication_snapshot.json`: 18 observed Astra slots and two completed 40-slot bare VLM arms. Three Astra service exclusions leave 15 common valid slots. Success counts are 11, 9 and 9. The partial panel is not a final ranking.
- `module_effects.json`: reanalysis of the existing four-arm cube-v1 control factorial on 37 common valid slots. This adds no trials.
- `visual_interventions.json`: 240 completed bare-VLM trials, 40 per condition. Astra interventions are pending. Input interventions act only on the upper-level model.
- `paired_recovery.json`: 19 verified states, two assigned goals and two controller conditions (76 branches). State 12 was unavailable. These are recovery diagnostics, not autonomous semantic success.
- `provenance.json`: numerical source checksums and scope.

Service failures are excluded from the primary success denominator using the existing protocol. Raw outcomes remain auditable, and ordinary task failures are retained. A recorded drop may coexist with a service exclusion. Never classify eligibility using the terminal reason alone.

Run `python3 scripts/render_followup.py` to validate and regenerate the follow-up tables. Completed baselines and partial Astra results use different denominators unless explicitly restricted to the common panel.
