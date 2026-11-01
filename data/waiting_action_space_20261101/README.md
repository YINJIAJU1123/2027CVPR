# Waiting-action space diagnostic

This is a held-out action-fitting analysis, not an additional autonomous agent benchmark. It uses 17,755 pending sensor states from 61 validation trajectory groups, collection seed 185302. The states are correlated. No formal evaluation states or new Astra calls are used.

For each state, the frozen teacher holding target defines the minimum possible error for a command constrained to interpolate between current normalized joint position and the student proposal. The target and the per-state optimum are unavailable at deployment. This lower bound is reported to explain the limited action space of scalar slowdown.

All deployed checkpoint identities, the validation manifest hash, formulas, and analysis source hash are recorded in diagnostic.json. The formal four-arm evaluation remains separate.
