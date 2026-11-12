"""Import sanitized Pig Q3 records once; independently recompute offline statistics.

Default and --check require only Python's standard library and this paper archive.
--import-from additionally uses Pillow to verify the original delivered RGB hashes.
No model, simulation, network call, or original checkpoint is loaded.
"""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/q3_pig_inspection_20261112"
MODES = ("adaptive", "fixed")
SEEDS = (188301, 188302)
BINDING_TOOLS = {"reorient_target", "verify_target", "stop"}
CATEGORIES = ("both_success", "adaptive_only", "fixed_only", "both_failure")
INPUTS = ("trials.jsonl", "calls.jsonl", "actions.jsonl", "release.json",
          "protocol.json", "model_config.json", "audit.json", "source_sha256.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def jsonl(value):
    return "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in value)


def relative_path(value):
    """Strip local account/root prefixes while preserving archive-relative identity."""
    if not isinstance(value, str) or not value.startswith("/"):
        return value
    for marker in ("/outputs/", "/client_project/"):
        if marker in value:
            return marker.strip("/") + "/" + value.split(marker, 1)[1]
    if "/repository/" in value:
        return "repository/" + value.split("/repository/", 1)[1]
    raise ValueError("Unclassified absolute path in source metadata")


def sanitize(value):
    if isinstance(value, dict):
        return {relative_path(k): sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return relative_path(value)


def clean_usage(usage):
    if not isinstance(usage, dict):
        return None
    # Omit provider attribution dictionaries containing response/item identifiers.
    result = {k: usage.get(k) for k in ("input_tokens", "output_tokens", "total_tokens")}
    for name in ("input_tokens_details", "output_tokens_details"):
        result[name] = {k: v for k, v in usage.get(name, {}).items()
                        if k in {"cached_tokens", "cache_write_tokens", "reasoning_tokens"}}
    return result


def import_records(source):
    from PIL import Image

    source = source.resolve()
    release = load(source / "release.json")
    require(release["status"] == "frozen" and release["stage"] == "formal", "Wrong release")
    require(len(release["cases"]) == 40, "Expected 40 frozen cases")
    provenance = {}

    def record(path):
        path = Path(path)
        key = path.relative_to(source).as_posix()
        provenance[key] = sha(path)
        return key

    # Check the complete original frozen source inventory, storing hashes only.
    frozen_sources = {}
    for path, digest in release["source_sha256"].items():
        require(sha(path) == digest, "Frozen source mismatch")
        frozen_sources[relative_path(path)] = digest
    for name in ("release.json", "protocol_draft.json", "schedule.json",
                 "final_audit.json", "final_independent_audit.json", "pairing_recheck.json",
                 "binding_semantics_audit_20261112.json", "evidence_bundle_review.json"):
        record(source / name)
    require(provenance["protocol_draft.json"] == release["protocol_sha256"], "Protocol pin changed")
    protocol = load(source / "protocol_draft.json")
    for artifact in protocol["artifacts"].values():
        require(sha(artifact["path"]) == artifact["sha256"], "Frozen artifact changed")

    # Extract only the pure JSON schema function, avoiding model/simulator imports.
    schema_source = source / "client_project/scripts/dice_latent_v1/semantic.py"
    parsed = ast.parse(schema_source.read_text())
    function = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == "tools_schema")
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "archived_tools_schema", "exec"), namespace)
    schema = namespace["tools_schema"]()
    require(hashlib.sha256(json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            == release["model_contract"]["tools_schema_sha256"], "Tool schema mismatch")

    trials, calls, actions = [], [], []
    system_prompt = None
    shared_runtime = None
    for mode in MODES:
        for case in release["cases"]:
            index = case["index"]
            evaluation = source / f"runs/{mode}/case_{index:03d}/evaluation"
            episode = evaluation / f"episode_{index:03d}"
            rows = lines(evaluation / "episodes.jsonl")
            require(len(rows) == 1, "Formal process must contain exactly one episode")
            row = rows[0]
            require(all(row[k] == v for k, v in case.items()), "Episode does not match release case")
            manifest = load(evaluation / "manifest.json")
            require(manifest["study_release_sha256"] == provenance["release.json"], "Run release mismatch")
            require(manifest["study_stage"] == "formal" and not manifest["development"], "Nonformal record")
            if shared_runtime is None:
                shared_runtime = {k: manifest["runtime"][k] for k in
                                  ("task_id", "physical_binding", "goal_manifest", "pose_source", "noise_config",
                                   "explicit_overrides", "camera", "inputs")}
            files = {name: record(evaluation / name) for name in
                     ("episodes.jsonl", "manifest.json", "result.json", "steps.jsonl", "action_interface.jsonl")
                     if (evaluation / name).is_file()}
            call_source = record(episode / "calls.json")
            action_path = episode / "inspection_policy.jsonl"
            action_source = record(action_path) if action_path.is_file() else None
            action_rows = lines(action_path) if action_path.is_file() else []
            for action in action_rows:
                actions.append(dict(mode=mode, index=index, trial_seed=case["trial_seed"],
                                    source=action_source, **action))
            first_png = None
            first_pixels = None
            for call in load(episode / "calls.json"):
                number = call["call"]
                input_path = episode / f"agent_input_{number:02d}.json"
                input_row = load(input_path)
                image_path = episode / f"request_{number:02d}.png"
                input_source = record(input_path)
                image_source = record(image_path)
                with Image.open(image_path) as image:
                    pixels = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
                require(pixels == input_row["image_sha256"], "Input pixels differ from archived hash")
                result = call.get("result") or {}
                require(call.get("error") is None, "Unexpected formal service error")
                require(result["image_sha256"] == pixels, "Transport delivered different image")
                require(json.loads(result["prompt"]) == {"instruction": row["instruction"],
                                                         "feedback": input_row["feedback"]}, "Prompt mismatch")
                for field in ("model", "api_base_url", "auth_method"):
                    require(result[field] == release["model_contract"][field], "Model contract mismatch")
                if system_prompt is None:
                    system_prompt = result["system_prompt"]
                require(result["system_prompt"] == system_prompt, "System prompt drift")
                service_path = source / "service/requests" / result["request_audit_file"]
                service = load(service_path)
                require(service["status"] == "completed" and service["image_sha256"] == pixels,
                        "Service journal mismatch")
                require(service["usage"] == result["usage"], "Service usage mismatch")
                service_source = record(service_path)
                if number == 1:
                    first_png, first_pixels = provenance[image_source], pixels
                calls.append(dict(mode=mode, index=index, trial_seed=case["trial_seed"],
                                  call=number, source=call_source, input_source=input_source,
                                  image_source=image_source, service_source=service_source,
                                  image_file_sha256=provenance[image_source], image_pixels_sha256=pixels,
                                  delivered_image_sha256=result["image_sha256"],
                                  request_step=call["request_step"], delivery_step=call.get("delivery_step"),
                                  applied_step=call.get("applied_step"), elapsed_s=call["elapsed_s"],
                                  provider_elapsed_s=result.get("elapsed_s"), error=call.get("error"),
                                  proposed_tool=result.get("tool"), proposed_arguments=result.get("arguments"),
                                  executed_tool=call.get("executed_tool"), executed_arguments=call.get("executed_arguments"),
                                  usage=clean_usage(result.get("usage")), crop_box=result.get("crop_box"),
                                  model=result["model"], api_base_url=result["api_base_url"],
                                  transport_attempts=result.get("transport_attempts"),
                                  transport_retry_errors=result.get("transport_retry_errors"),
                                  feedback=input_row["feedback"], fields_sent=input_row["fields_sent"]))
            trials.append(dict(mode=mode, index=index, trial_seed=case["trial_seed"], episode=row,
                               sources=files, calls_source=call_source, actions_source=action_source,
                               first_image_file_sha256=first_png, first_image_pixels_sha256=first_pixels))
    require(hashlib.sha256(system_prompt.encode()).hexdigest() == release["model_contract"]["system_prompt_sha256"],
            "System prompt hash mismatch")
    independent = load(source / "final_independent_audit.json")
    binding = load(source / "binding_semantics_audit_20261112.json")
    review = load(source / "evidence_bundle_review.json")
    audit = dict(status="sanitized_export_of_completed_formal_records", formal_trials=80, formal_pairs=40,
                 previous_independent_audit_status=independent["status"],
                 frozen_sources_verified=independent["frozen_sources_verified"],
                 frozen_artifacts_verified=independent["frozen_artifacts_verified"],
                 common_service_exclusions=independent["common_service_exclusions"],
                 evidence_bundle_review_status=review["status"],
                 evidence_bundle_zip_sha256=review["zip_sha256"],
                 binding_definitions=binding["definitions"],
                 original_audit_sources={k: provenance[k] for k in provenance if "/" not in k and "audit" in k},
                 scope="Hashes reference original files; sanitized files intentionally have different hashes. "
                       "Compact offline recomputation does not replace the full physical-trace audit.",
                 exclusions="Engineering and smoke attempts are excluded, including an earlier failed admission HTTP 504. "
                            "All 80 formal episodes and all their returned calls are included.")
    model = dict(contract=release["model_contract"], system_prompt=system_prompt, tools_schema=schema,
                 runtime=shared_runtime, immutable_hosted_weights_available=False,
                 settings_note="Requested model identifier and low reasoning effort were fixed; immutable provider weights were not exposed.")
    sanitized_release = dict(release)
    del sanitized_release["source_sha256"]
    sanitized_release["source_sha256_inventory"] = "source_sha256.json:frozen_source_files"
    values = {"trials.jsonl": jsonl(trials), "calls.jsonl": jsonl(calls), "actions.jsonl": jsonl(actions),
              "release.json": pretty(sanitize(sanitized_release)), "protocol.json": pretty(sanitize(protocol)),
              "model_config.json": pretty(sanitize(model)), "audit.json": pretty(audit),
              "source_sha256.json": pretty(dict(original_experiment_relative_files=provenance,
                                                  frozen_source_files=frozen_sources))}
    DATA.mkdir(exist_ok=True)
    for name, content in values.items():
        (DATA / name).write_text(content)
    (DATA / "export_manifest.json").write_text(pretty({name: sha(DATA / name) for name in INPUTS}))


def angle(q, target):
    qnorm = math.sqrt(sum(v*v for v in q))
    tnorm = math.sqrt(sum(v*v for v in target))
    cosine = abs(sum(a*b for a, b in zip(q, target)) / (qnorm * tnorm))
    return 2 * math.acos(min(1.0, cosine))


def paired_test(pairs):
    counts = {category: 0 for category in CATEGORIES}
    for pair in pairs:
        a, f = pair["adaptive_success"], pair["fixed_success"]
        category = "both_success" if a and f else "adaptive_only" if a else "fixed_only" if f else "both_failure"
        counts[category] += 1
    b, c = counts["adaptive_only"], counts["fixed_only"]
    discordant = b+c
    exact = 1.0 if not discordant else min(1.0, 2 * sum(math.comb(discordant, k)
                                                        for k in range(min(b, c)+1)) / 2**discordant)
    return dict(pairs=len(pairs), **counts, adaptive_minus_fixed=(b-c)/len(pairs),
                exact_two_sided_mcnemar_p_unadjusted=exact)


def aggregate(records, calls):
    result = dict(n=len(records), success=sum(r["success"] for r in records),
                  reasons=dict(sorted(Counter(r["reason"] for r in records).items())),
                  terminal_binding={k: sum(r["terminal_binding"] == k for r in records)
                                    for k in ("correct", "wrong", "unbound")},
                  ever_correct_binding=sum(r["ever_correct_binding"] for r in records),
                  never_correct_binding=sum(not r["ever_correct_binding"] for r in records),
                  ever_any_binding=sum(r["ever_any_binding"] for r in records),
                  never_any_binding=sum(not r["ever_any_binding"] for r in records),
                  first_correct_call_histogram={str(k): sum(r["first_correct_call"] == k for r in records)
                                                for k in range(1, 7)},
                  drop_phases=dict(sorted(Counter(r["drop_phase"] for r in records if r["reason"] == "drop").items())),
                  calls=len(calls), applied_calls=sum(c["applied_step"] is not None for c in calls),
                  unapplied_calls=sum(c["applied_step"] is None for c in calls),
                  inspections=sum(r["inspections"] for r in records),
                  commanded_inspection_steps=sum(r["commanded_inspection_steps"] for r in records),
                  median_call_latency_s=statistics.median(c["elapsed_s"] for c in calls),
                  median_episode_simulation_s=statistics.median(r["steps"]/20 for r in records))
    result["commanded_inspection_seconds"] = result["commanded_inspection_steps"]/20
    result["tokens"] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        values = [(c["usage"] or {}).get(key) for c in calls]
        require(all(v is None or (type(v) is int and v >= 0) for v in values), "Invalid usage")
        missing = sum(v is None for v in values)
        known = sum(v for v in values if v is not None)
        result["tokens"][key] = dict(total=None if missing else known, known_sum=known, missing_calls=missing)
    return result


def recompute():
    manifest = load(DATA / "export_manifest.json")
    require(set(manifest) == set(INPUTS), "Unexpected export input inventory")
    for name, digest in manifest.items():
        require(sha(DATA / name) == digest, "Export input changed: " + name)
    release = load(DATA / "release.json")
    model = load(DATA / "model_config.json")
    provenance = load(DATA / "source_sha256.json")["original_experiment_relative_files"]
    trials, calls, actions = (lines(DATA / name) for name in ("trials.jsonl", "calls.jsonl", "actions.jsonl"))
    require(len(trials) == 80 and len(calls) == 231, "Incomplete formal data")
    call_groups, action_groups = defaultdict(list), defaultdict(list)
    for call in calls:
        call_groups[call["mode"], call["index"]].append(call)
    for action in actions:
        action_groups[action["mode"], action["index"]].append(action)
    require(set(call_groups) == {(m, i) for m in MODES for i in range(40)}, "Missing or duplicate trial calls")
    per_trial, trial_by_key, fixed_inspections = [], {}, []
    for trial in trials:
        mode, index, row = trial["mode"], trial["index"], trial["episode"]
        key = mode, index
        require(key not in trial_by_key, "Duplicate episode")
        trial_by_key[key] = trial
        require(row["inspection_policy"] == mode, "Wrong condition")
        require(row["base_seed"] in SEEDS and row["trial_seed"] == row["base_seed"]*1000+row["episode"], "Invalid pairing key")
        require(row["trial_seed"] == trial["trial_seed"], "Trial identity changed")
        require(all(row[k] == v for k, v in release["cases"][index].items()), "Case differs from frozen plan")
        initial = row["initial_state"]
        require(hashlib.sha256(json.dumps(initial["values"], sort_keys=True).encode()).hexdigest() == initial["sha256"], "Initial hash mismatch")
        for path in (*trial["sources"].values(), trial["calls_source"], trial["actions_source"]):
            require(path is None or path in provenance, "Missing source provenance")
        group = sorted(call_groups[key], key=lambda c: c["call"])
        ledger = {a["call"]: a for a in action_groups[key]}
        require(len(ledger) == len(action_groups[key]), "Duplicate applied action")
        require([c["call"] for c in group] == list(range(1, len(group)+1)), "Noncontiguous calls")
        require(len(group) == row["actual_model_calls"] <= 6, "Call count mismatch")
        bound = declared = first_correct = None
        ever_any = False
        inspection_count = inspection_steps = 0
        last_execution = None
        for call in group:
            require(call["trial_seed"] == row["trial_seed"], "Call pairing mismatch")
            require(call["model"] == model["contract"]["model"] and call["api_base_url"] == model["contract"]["api_base_url"], "Model drift")
            require(call["image_pixels_sha256"] == call["delivered_image_sha256"], "Delivered image drift")
            require(provenance[call["image_source"]] == call["image_file_sha256"], "Missing image-file provenance")
            require(call["feedback"]["last_executed_action"] == last_execution, "History does not record actual action")
            require(call["feedback"]["control_step"] == call["request_step"], "Request timing mismatch")
            require(call["error"] is None and call["elapsed_s"] <= 120, "Formal service exclusion found")
            require(call["transport_attempts"] == 1 and not call["transport_retry_errors"], "Unexpected transport retries")
            if call["applied_step"] is None:
                require(call["call"] not in ledger and call["executed_tool"] is None, "Unapplied reply executed")
                continue
            require(call["request_step"] + math.ceil(call["elapsed_s"]*20) == call["delivery_step"] <= call["applied_step"] <= row["steps"], "Response applied too early")
            action = ledger[call["call"]]
            require(action["tool"] == call["proposed_tool"] == call["executed_tool"], "Tool changed")
            require(action["proposed_arguments"] == call["proposed_arguments"] and action["executed_arguments"] == call["executed_arguments"], "Action ledger mismatch")
            require(action["applied_step"] == call["applied_step"] and action["policy"] == mode, "Action identity mismatch")
            tool, args = call["executed_tool"], call["executed_arguments"]
            expected = dict(call["proposed_arguments"])
            if tool == "inspect_face":
                if mode == "fixed":
                    expected.update(number=release["fixed_policy"]["motor_ids"][inspection_count % 6],
                                    steps=release["fixed_policy"]["steps"])
                    fixed_inspections.append(action)
                inspection_count += 1
                inspection_steps += args["steps"]
                bound = declared = None
            elif tool in BINDING_TOOLS:
                bound, declared = args["number"]-1, args["goal_number"]
                ever_any = True
                if bound == row["goal_index"] and declared == row["requested_label_index"] and first_correct is None:
                    first_correct = call["call"]
            else:
                require(tool == "abstain", "Unknown applied tool")
                # Abstain and physical drops do not reset semantic binding.
            require(args == expected, "Intervention changed noninspection fields")
            require(action["inspection_count"] == inspection_count, "Inspection index mismatch")
            last_execution = dict(tool=tool, arguments=args, applied_step=call["applied_step"], call=call["call"])
        require(len(ledger) == sum(c["applied_step"] is not None for c in group), "Incomplete applied ledger")
        require(bound == row["declared_goal"] and declared == row["declared_number"], "Terminal binding differs from actions")
        correct = bound == row["goal_index"] and declared == row["requested_label_index"]
        terminal = "unbound" if bound is None else "correct" if correct else "wrong"
        qerror = angle(row["final_quaternion_xyzw"], release["canonical_target_quaternions_xyzw"][row["goal_index"]])
        require(abs(qerror-row["final_error_rad"]) < 1e-5, "Independent final quaternion error mismatch")
        success = bool(row["stop_measurement"] is not None and correct and qerror <= 0.16 and row["reason"] != "drop")
        require(success == row["success"] == (row["reason"] == "success"), "Success predicate mismatch")
        require(row["exclusion_reason"] is None, "Unexpected formal exclusion")
        require(trial["first_image_file_sha256"] == group[0]["image_file_sha256"]
                and trial["first_image_pixels_sha256"] == group[0]["image_pixels_sha256"], "First image differs")
        per_trial.append(dict(mode=mode, index=index, trial_seed=row["trial_seed"], base_seed=row["base_seed"],
                              success=success, reason=row["reason"], steps=row["steps"], drop_phase=row["drop_phase"],
                              terminal_binding=terminal, ever_correct_binding=first_correct is not None,
                              ever_any_binding=ever_any, first_correct_call=first_correct,
                              inspections=inspection_count, commanded_inspection_steps=inspection_steps))
    require(len(fixed_inspections) == 79 and len(actions) == 221, "Applied action count mismatch")
    by_key = {(r["mode"], r["index"]): r for r in per_trial}
    pairs = []
    for index in range(40):
        a, f = (trial_by_key[m, index] for m in MODES)
        for field in ("trial_seed", "base_seed", "episode", "goal_index", "requested_label_index"):
            require(a["episode"][field] == f["episode"][field], "Pair identity mismatch")
        require(a["episode"]["initial_state"] == f["episode"]["initial_state"], "Physical state differs")
        require(a["first_image_file_sha256"] == f["first_image_file_sha256"]
                and a["first_image_pixels_sha256"] == f["first_image_pixels_sha256"], "First frame differs")
        pairs.append(dict(index=index, trial_seed=a["trial_seed"], base_seed=a["episode"]["base_seed"],
                          initial_state_sha256=a["episode"]["initial_state"]["sha256"],
                          first_image_file_sha256=a["first_image_file_sha256"],
                          first_image_pixels_sha256=a["first_image_pixels_sha256"],
                          adaptive_success=by_key["adaptive", index]["success"], fixed_success=by_key["fixed", index]["success"],
                          adaptive_reason=by_key["adaptive", index]["reason"], fixed_reason=by_key["fixed", index]["reason"],
                          source_ledgers={m:trial_by_key[m,index]["sources"]["episodes.jsonl"] for m in MODES}))
    primary = paired_test(pairs)
    differences = [int(p["adaptive_success"])-int(p["fixed_success"]) for p in pairs]
    rng = random.Random(188399)
    bootstrap = sorted(sum(rng.choice(differences) for _ in differences)/40 for _ in range(20000))
    primary["descriptive_paired_percentile_bootstrap_95"] = dict(interval=[bootstrap[499], bootstrap[19499]],
                                                               seed=188399, resamples=20000, exact_interval=False)
    groups = {}
    for mode in MODES:
        group = [r for r in per_trial if r["mode"] == mode]
        group_calls = [c for c in calls if c["mode"] == mode]
        groups[mode] = aggregate(group, group_calls)
        groups[mode]["per_seed"] = {str(seed):aggregate([r for r in group if r["base_seed"] == seed],
                                                       [c for c in group_calls if c["trial_seed"]//1000 == seed]) for seed in SEEDS}
    summary = dict(status="recomputed_from_sanitized_raw_formal_records", formal_episodes=80, common_eligible_pairs=40,
                   common_service_exclusions=[], summary=groups, primary_success=primary,
                   per_seed_paired_descriptive={str(seed):paired_test([p for p in pairs if p["base_seed"] == seed]) for seed in SEEDS},
                   statistical_scope="Within-study prespecified primary success endpoint; exact two-sided McNemar p is unadjusted. "
                                     "A later separate Pig cohort after the Cube study; no pooling or prespecified cross-study multiplicity family. "
                                     "Seed splits, binding and costs are descriptive; the paired bootstrap interval is descriptive, not exact.",
                   cost_scope="All submitted formal calls with returned records, including 10 replies not applied before episode exit; "
                              "missing token usage is null with an explicit known sum, never zero.",
                   binding_scope="Reconstructed from applied actions only; physical drops and abstain retain the last binding, inspect_face clears it. "
                                 "Binding is not independent recognition/visibility annotation or post-stop holding.")
    tex = ["% Generated by scripts/render_q3_pig_inspection.py from the 80 raw formal records.",
           r"\newcommand{\PigInspectionPolicyRows}{%"]
    for mode, label in (("fixed", "Fixed sweep"), ("adaptive", "Adaptive inspection")):
        g = groups[mode]
        tex.append(f"{label} & {g['success']}/{g['n']} & {100*g['success']/g['n']:.1f} & {g['reasons'].get('drop',0)} & {g['calls']}" + r"\\")
    tex.append("}")
    return {DATA / "summary.json": pretty(summary), DATA / "paired_trials.json": pretty(pairs),
            DATA / "trial_metrics.jsonl": jsonl(per_trial), DATA / "fixed_inspections.jsonl": jsonl(fixed_inspections),
            ROOT / "tables/q3_pig_inspection_macros.tex": "\n".join(tex) + "\n"}


def safety_check():
    forbidden_keys = {"access_token", "refresh_token", "id_token", "api_key", "password", "authorization",
                      "client_secret", "response_id", "call_id", "account_id", "email"}

    def visit(value):
        if isinstance(value, dict):
            require(not (set(value) & forbidden_keys), "Identifier or credential field in export")
            for k, v in value.items():
                require(not k.startswith("/"), "Absolute path key")
                visit(v)
        elif isinstance(value, list):
            for v in value:
                visit(v)
        elif isinstance(value, str):
            require(not value.startswith("/"), "Absolute local path")
            require(not re.search(r"(?:/home/|/root/|resp_[a-zA-Z0-9]+|call_[a-zA-Z0-9]{12,}|sk-[a-zA-Z0-9]{20,}|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", value), "Sensitive identifier/path")
    for path in DATA.iterdir():
        if path.suffix == ".json":
            visit(load(path))
        elif path.suffix == ".jsonl":
            visit(lines(path))
        require(path.suffix not in {".pt", ".pth", ".safetensors", ".zip"}, "Unexpected weight or archive")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-from", type=Path, help="One-time local original experiment directory; never needed by --check")
    parser.add_argument("--check", action="store_true", help="Read-only offline validation, including generated table")
    args = parser.parse_args()
    require(not (args.import_from and args.check), "Import and read-only check are separate operations")
    if args.import_from:
        import_records(args.import_from)
    outputs = recompute()
    for path, content in outputs.items():
        if args.check:
            require(path.is_file() and path.read_text() == content, "Stale generated file: " + str(path.relative_to(ROOT)))
        else:
            path.write_text(content)
    safety_check()
    summary = json.loads(outputs[DATA / "summary.json"])
    a, f = (summary["summary"][mode] for mode in MODES)
    primary = summary["primary_success"]
    print(f"Pig Q3: {summary['formal_episodes']} episodes, {primary['pairs']} exact pairs; "
          f"adaptive {a['success']}/{a['n']}, fixed {f['success']}/{f['n']}; "
          f"discordance {primary['adaptive_only']}/{primary['fixed_only']}; exact two-sided unadjusted "
          f"p={primary['exact_two_sided_mcnemar_p_unadjusted']}; {a['calls']+f['calls']} calls; offline checks passed.")


if __name__ == "__main__":
    main()
