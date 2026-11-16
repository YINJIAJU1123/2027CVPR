"""Recompute reported counts and paired tests from the released trial records."""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_bytes())


def check(condition, label):
    if not condition:
        raise ValueError(label)


def paired(rows, method, reference):
    counts = Counter((row[method]["success"] is True, row[reference]["success"] is True) for row in rows)
    both, wins, losses, neither = (counts[key] for key in ((True, True), (True, False), (False, True), (False, False)))
    n = wins + losses
    tail = sum(math.comb(n, j) for j in range(min(wins, losses) + 1))
    return (both, wins, losses, neither), min(1.0, 2 * tail / 2**n)


def check_holm(raw_adjusted):
    previous = 0.0
    for i, (raw, adjusted) in enumerate(sorted(raw_adjusted)):
        previous = max(previous, min(1.0, (len(raw_adjusted) - i) * raw))
        check(math.isclose(previous, adjusted), "Holm-adjusted p value")


def verify_timing(rows, stats):
    durations = [t for r in rows for t in r["latencies_s"]]
    check(len(rows) == stats["trials"] and len(durations) == stats["calls"], "Timing sample sizes")
    check(median(durations) == stats["median_call_seconds"], "Median call latency")
    steps = sum(r["steps"] for r in rows)
    waiting = sum(r["pending_steps"] for r in rows)
    check((steps, waiting) == (stats["steps"], stats["pending_steps"]), "Physics steps and pending steps")
    check(math.isclose(100 * waiting / steps, stats["pending_percent"]), "Pending share")


def verify_q1():
    report = load("q1/final_comparison.json")
    rows = report["trial_rows"]
    methods = ("rule", "vlm", "finetuned_control", "astra")
    ids = {(r["object"], r["layout"], r["trial_seed"]) for r in rows}
    check(len(rows) == len(ids) == report["closed_and_audited"] == 480, "Q1 trial identities")
    eligible = defaultdict(list)
    for r in rows:
        ok = all(r[m]["service_exclusion"] is None for m in methods)
        check(r["four_way_eligible"] == ok, "Q1 common eligibility")
        if ok:
            check(r["vlm"]["reset_sha256"] == r["finetuned_control"]["reset_sha256"], "Q1 matched Qwen reset")
            eligible[r["object"], r["layout"]].append(r)
    check(len(eligible) == len(report["cells"]) == 12, "Q1 cells")
    for cell in report["cells"]:
        group = eligible[cell["object"], cell["layout"]]
        check(len(group) == cell["common"], "Q1 cell denominator")
        for method in methods:
            total = sum(r[method]["success"] is True for r in group)
            check(total == cell["arms"][method]["success"], "Q1 cell success count")

    family = []
    for contrast in report["paired_contrasts"]:
        group = eligible[contrast["object"], contrast["layout"]]
        counts, p = paired(group, "finetuned_control", contrast["reference"])
        check(counts == tuple(contrast[k] for k in ("both", "new_only", "reference_only", "neither")), "Q1 paired table")
        check(math.isclose(p, contrast["p_exact"]), "Q1 exact McNemar test")
        family.append((p, contrast["p_holm_24"]))
    check(len(family) == 24, "Q1 test family")
    check_holm(family)
    common = [r for group in eligible.values() for r in group]
    counts, p = paired(common, "finetuned_control", "vlm")
    check(counts == (91, 31, 38, 317), "Q1 pooled paired table")
    trace = load("q1/trace_diagnostics.json")
    controlled = [r for r in trace["trial_rows"] if r["method"] == "finetuned_control"]
    check({(r["object"], r["layout"], r["trial_seed"]) for r in controlled} == ids, "Q1 trace coverage")
    check(Counter(r["outcome"] for r in controlled) == trace["controlled_outcomes"], "Q1 detailed outcomes")
    verify_timing(controlled, trace["controlled_all"])
    duck_ids = {r["trial_seed"] for r in eligible["duck", "permuted"]}
    for method, stats in trace["duck_permuted"].items():
        duck = [r for r in trace["trial_rows"] if (r["object"], r["layout"], r["method"]) == ("duck", "permuted", method)]
        check({r["trial_seed"] for r in duck} == duck_ids and len(duck) == len(duck_ids), "Q1 Duck timing cohort")
        verify_timing(duck, stats)
    print(f"Q1: {len(rows)} new trials, {len(common)} common cases, 24 paired contrasts verified. Pooled p = {p:.6f}.")



if __name__ == "__main__":
    verify_q1()
