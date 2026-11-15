#!/usr/bin/env python3
"""Audit terminal target bindings in the existing paired Q3 image study.

Run from any directory. This performs no simulation or new model inference.
Use --check to verify that the committed JSON matches the source records.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/cube_confirmation_image_refresh_20261102/trials.json"
OUTPUT = ROOT / "data/q3_terminal_binding_audit_20261107.json"
GROUPS = ("image_fresh", "image_frozen")
SYMBOLS = ("T", "E", "R", "L", "S", "H")
BINDINGS = ("correct", "wrong", "unbound")
REASONS = ("success", "drop", "false_stop", "abstain")
TOLERANCE_RAD = 0.16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def audit_group(name, rows):
    require(isinstance(rows, list) and len(rows) == 40,
            f"{name}: expected exactly 40 trials")
    seen = set()
    counts = Counter()
    outcomes = Counter()
    cross = {binding: Counter() for binding in BINDINGS}
    records = []
    for index, row in enumerate(rows):
        prefix = f"{name}[{index}]"
        required = (
            "trial_seed", "goal_index", "symbol", "declared_goal",
            "declared_symbol", "success", "reason", "exclusion_reason",
            "drop_phase", "final_error_rad", "stop_measurement",
            "actual_model_calls", "initial_state",
        )
        require(isinstance(row, dict), f"{prefix}: trial must be an object")
        require(all(key in row for key in required),
                f"{prefix}: missing required audit fields")
        trial_id = row["trial_seed"]
        require(type(trial_id) is int and trial_id not in seen,
                f"{prefix}: trial ID must be a unique integer")
        seen.add(trial_id)
        goal = row["goal_index"]
        require(type(goal) is int and 0 <= goal < len(SYMBOLS),
                f"{prefix}: invalid requested goal index")
        require(row["symbol"] == SYMBOLS[goal],
                f"{prefix}: requested symbol disagrees with the cube goal bank")
        declared = row["declared_goal"]
        require(declared is None or
                (type(declared) is int and 0 <= declared < len(SYMBOLS)),
                f"{prefix}: invalid declared goal")
        if declared is None:
            require(row["declared_symbol"] is None,
                    f"{prefix}: unbound goal has a declared symbol")
            binding = "unbound"
        else:
            # The declared symbol names the requested target; an incorrect
            # selected skill can still carry that same symbol declaration.
            require(row["declared_symbol"] == row["symbol"],
                    f"{prefix}: binding does not declare the requested symbol")
            binding = "correct" if declared == goal else "wrong"
        reason = row["reason"]
        require(reason in REASONS, f"{prefix}: unsupported terminal outcome")
        require(type(row["success"]) is bool and
                row["success"] == (reason == "success"),
                f"{prefix}: success flag disagrees with terminal reason")
        require(row["exclusion_reason"] is None,
                f"{prefix}: this Q3 study must have no service exclusions")
        require(type(row["actual_model_calls"]) is int and
                1 <= row["actual_model_calls"] <= 6,
                f"{prefix}: call count violates the six-call cap")
        require(finite_number(row["final_error_rad"]) and
                row["final_error_rad"] >= 0,
                f"{prefix}: final angular error must be finite and nonnegative")
        require(isinstance(row["initial_state"], dict) and
                isinstance(row["initial_state"].get("sha256"), str) and
                len(row["initial_state"]["sha256"]) == 64,
                f"{prefix}: initial-state hash is missing or malformed")
        if reason == "drop":
            require(row["drop_phase"] in ("wait", "execution"),
                    f"{prefix}: dropped trial lacks a valid failure phase")
            require(row["stop_measurement"] is None,
                    f"{prefix}: drop unexpectedly has a stop measurement")
        else:
            require(row["drop_phase"] is None,
                    f"{prefix}: non-drop trial has a drop phase")
        if reason == "abstain":
            require(binding == "unbound" and row["stop_measurement"] is None,
                    f"{prefix}: abstention must be unbound without a stop")
        if reason in ("success", "false_stop"):
            stop = row["stop_measurement"]
            require(binding != "unbound" and isinstance(stop, dict),
                    f"{prefix}: stopped trial lacks a binding or measurement")
            require(stop.get("pending") is False and
                    finite_number(stop.get("raw_error_rad")) and
                    0 <= stop["raw_error_rad"] <= TOLERANCE_RAD,
                    f"{prefix}: stopped trial violates the measured-pose gate")
            independently_correct = (
                binding == "correct" and
                row["final_error_rad"] <= TOLERANCE_RAD
            )
            require(independently_correct == (reason == "success"),
                    f"{prefix}: final binding/true pose disagree with success")
        counts[binding] += 1
        outcomes[reason] += 1
        cross[binding][reason] += 1
        records.append({
            "trial_id": trial_id,
            "requested_goal_index": goal,
            "requested_symbol": row["symbol"],
            "declared_goal_index": declared,
            "declared_symbol": row["declared_symbol"],
            "terminal_binding": binding,
            "terminal_reason": reason,
            "success": row["success"],
            "final_error_rad": row["final_error_rad"],
        })
    require(sum(counts.values()) == sum(outcomes.values()) == 40,
            f"{name}: incomplete terminal partition")
    return {
        "trials": 40,
        "service_exclusions": 0,
        "terminal_binding_counts": {key: counts[key] for key in BINDINGS},
        "terminal_reason_counts": {key: outcomes[key] for key in REASONS},
        "terminal_binding_by_reason": {
            binding: {reason: cross[binding][reason] for reason in REASONS}
            for binding in BINDINGS
        },
        "correct_terminal_binding_rate": counts["correct"] / 40,
        "success_rate": outcomes["success"] / 40,
        "actual_model_calls": sum(row["actual_model_calls"] for row in rows),
        "classified_trials": sorted(records, key=lambda row: row["trial_id"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="check the existing audit JSON without writing")
    args = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    data = json.loads(source_bytes)
    require(isinstance(data, dict) and all(group in data for group in GROUPS),
            "Source lacks the two Q3 image-refresh groups")
    groups = {name: audit_group(name, data[name]) for name in GROUPS}
    fresh = {row["trial_seed"]: row for row in data["image_fresh"]}
    frozen = {row["trial_seed"]: row for row in data["image_frozen"]}
    require(fresh.keys() == frozen.keys(), "Q3 arms have different trial IDs")
    for trial_id, row in fresh.items():
        other = frozen[trial_id]
        require(row["goal_index"] == other["goal_index"] and
                row["symbol"] == other["symbol"] and
                row["initial_state"] == other["initial_state"],
                f"Trial {trial_id}: paired task/initial state mismatch")
    result = {
        "analysis": "Offline terminal-binding audit of existing Q3 image-refresh trials",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "generator": Path(__file__).relative_to(ROOT).as_posix(),
        "classification": {
            "correct": "declared_goal equals goal_index at episode termination",
            "wrong": "declared_goal is present but differs from goal_index",
            "unbound": "declared_goal and declared_symbol are both null",
        },
        "scope": (
            "Descriptive classification of existing terminal records, not new trials. "
            "This does not measure first binding, initial or final target visibility, "
            "post-stop stability, or causal superiority of adaptive inspection."
        ),
        "checks": {
            "trials_per_arm": 40,
            "paired_trials": 40,
            "matching_trial_ids_goals_symbols_and_initial_states": True,
            "no_service_exclusions": True,
            "goal_and_binding_fields_validated": True,
            "success_and_failure_consistency_validated": True,
            "six_call_cap_validated": True,
            "success_pose_tolerance_rad": TOLERANCE_RAD,
        },
        "groups": groups,
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        require(OUTPUT.exists() and OUTPUT.read_text() == rendered,
                "Audit JSON is missing or stale; run this script without --check")
        print("Q3 terminal-binding audit is current.")
    else:
        OUTPUT.write_text(rendered)
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    for name, group in groups.items():
        print(f"{name}: {group['terminal_binding_counts']}; "
              f"outcomes={group['terminal_reason_counts']}")
    print(f"Source SHA256: {result['source_sha256']}")


if __name__ == "__main__":
    main()
