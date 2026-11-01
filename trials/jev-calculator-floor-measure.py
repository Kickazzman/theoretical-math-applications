#!/usr/bin/env python3
"""Calculator-floor measurement (item 1). READ-ONLY on materials.

Loads jev-calculator-floor-items.json (built after clean QA) and runs
the calculator: the test suite on each variant under test. Ground truth
is the CONSTRUCTION label in each item, never the calculator's output.

(a) item: calculator runs tests on new_code. Success = test outcome
    (pass/fail) matches the construction label (pass = new is correct,
    fail = new is buggy).
(b) item: calculator runs tests on both impls. Success = correct impl
    passes all tests AND buggy impl fails at least one (the only case
    where the tests separate the pair). Anything else (both pass, both
    fail, wrong pick) is a calculator failure.

Failure directions (one primary per failed item):
  (a) expected fail + outcome pass  -> "buggy-passes"
  (a) expected pass + outcome fail  -> "correct-fails"
  (b) correct fails + buggy fails   -> "both-fail"
  (b) correct fails + buggy passes  -> "correct-fails (wrong pick)"
  (b) correct passes + buggy passes -> "buggy-passes (ambiguous)"
"""
import json
import math
import sys

import importlib.util

sys.path.insert(0, ".")
_spec = importlib.util.spec_from_file_location(
    "cfbuild", "jev-calculator-floor-build.py")
_cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cf)
run_suite = _cf.run_suite


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def main():
    with open("jev-calculator-floor-items.json") as fh:
        data = json.load(fh)
    items = data["items"]
    assert len(items) == 100, len(items)
    records = []
    for it in items:
        tests = it["tests"]
        if it["type"] == "a":
            outcome, results = _outcome(it["new_code"], it["function"], tests)
            expected = it["expected"]
            success = outcome == expected
            if success:
                direction = None
            elif expected == "fail":
                direction = "buggy-passes"
            else:
                direction = "correct-fails"
            records.append({
                "decision_id": it["decision_id"], "type": "a",
                "function": it["function"], "expected": expected,
                "outcome": outcome, "success": success,
                "direction": direction,
                "failed_tests": [r["test"] for r in results
                                 if not r["passed"]],
                "failed_details": [r["detail"] for r in results
                                   if not r["passed"]],
                "construction": it["construction"],
            })
        else:
            # Correct impl is at expected position.
            correct_code = it["impl_a"] if it["expected"] == "A" \
                else it["impl_b"]
            buggy_code = it["impl_b"] if it["expected"] == "A" \
                else it["impl_a"]
            ca, res_c = _outcome(correct_code, it["function"], tests)
            ba, res_b = _outcome(buggy_code, it["function"], tests)
            success = ca == "pass" and ba == "fail"
            if success:
                direction = None
            elif ca == "fail" and ba == "fail":
                direction = "both-fail"
            elif ca == "fail":
                direction = "correct-fails (wrong pick)"
            else:
                direction = "buggy-passes (ambiguous)"
            records.append({
                "decision_id": it["decision_id"], "type": "b",
                "function": it["function"], "expected": it["expected"],
                "correct_outcome": ca, "buggy_outcome": ba,
                "success": success, "direction": direction,
                "correct_failed_tests": [r["test"] for r in res_c
                                         if not r["passed"]],
                "buggy_failed_tests": [r["test"] for r in res_b
                                        if not r["passed"]],
                "construction": it["construction"],
            })

    failed = [r for r in records if not r["success"]]
    agg = {
        "n_items": len(records),
        "n_failed": len(failed),
        "p_fail": len(failed) / len(records),
        "wilson_95": wilson(len(failed), len(records)),
        "reachability": 1 - len(failed) / len(records),
        "by_type": {},
        "by_direction": {},
        "by_function": {},
        "marginal_correct_failed_items": 0,
        "marginal_buggy_passed_items": 0,
    }
    for t in ("a", "b"):
        sub = [r for r in records if r["type"] == t]
        fsub = [r for r in sub if not r["success"]]
        agg["by_type"][t] = {
            "n": len(sub), "failed": len(fsub),
            "p_fail": len(fsub) / len(sub),
            "wilson_95": wilson(len(fsub), len(sub)),
        }
    for r in failed:
        agg["by_direction"][r["direction"]] = \
            agg["by_direction"].get(r["direction"], 0) + 1
        agg["by_function"][r["function"]] = \
            agg["by_function"].get(r["function"], 0) + 1
    # Marginals: items where the correct variant failed, and items
    # where a buggy variant passed (an item can be in both).
    for r in records:
        if r["type"] == "a":
            if r["expected"] == "pass" and not r["success"]:
                agg["marginal_correct_failed_items"] += 1
            if r["expected"] == "fail" and not r["success"]:
                agg["marginal_buggy_passed_items"] += 1
        else:
            if r["correct_outcome"] == "fail":
                agg["marginal_correct_failed_items"] += 1
            if r["buggy_outcome"] == "pass":
                agg["marginal_buggy_passed_items"] += 1

    with open("jev-calculator-floor-records.json", "w") as fh:
        json.dump(records, fh, indent=1)
    with open("jev-calculator-floor-aggregate.json", "w") as fh:
        json.dump(agg, fh, indent=1)
    print("ITEMS: %d  FAILED: %d  P(fail)=%.4f  Wilson95=(%.4f, %.4f)" % (
        agg["n_items"], agg["n_failed"], agg["p_fail"],
        agg["wilson_95"][0], agg["wilson_95"][1]))
    print("REACHABILITY: %.4f  ERROR FLOOR: %.4f" % (
        agg["reachability"], agg["p_fail"]))
    print("BY TYPE:", json.dumps(agg["by_type"]))
    print("BY DIRECTION:", json.dumps(agg["by_direction"]))
    print("BY FUNCTION:", json.dumps(agg["by_function"]))
    print("MARGINALS: correct-failed items=%d  buggy-passed items=%d" % (
        agg["marginal_correct_failed_items"],
        agg["marginal_buggy_passed_items"]))
    for r in failed:
        print("FAIL %s (%s, %s): %s" % (
            r["decision_id"], r["type"], r["function"], r["direction"]))


def _outcome(code, fn_name, tests):
    results = run_suite(code, fn_name, tests)
    failed = [r for r in results if not r["passed"]]
    return ("pass" if not failed else "fail"), results


if __name__ == "__main__":
    main()
