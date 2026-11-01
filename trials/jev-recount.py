#!/usr/bin/env python3
"""Independent recount of the Komlos trial four cells (R-A1).

Different logic from jev-discrepancy-compute.py: builds (fast, slow)
correctness pairs via collections.Counter over decision pairs, and pairs
real-diff rows by decision_id through a separate dict build. Read-only.
Compares against jev-discrepancy-results.json and prints PASS/FAIL per
population. Exits nonzero on any mismatch.
"""
import json, os
from collections import Counter

WS = os.path.expanduser("~/workspace")
SRC = WS
RD = os.path.join(WS, "real-diff-coder")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def cells_from_pairs(pairs):
    c = Counter(pairs)
    return {
        "both_right": c[(True, True)],
        "fast_only_right": c[(True, False)],
        "slow_only_right": c[(False, True)],
        "both_wrong": c[(False, False)],
    }


def jev_population(filename):
    rows = load_json(os.path.join(SRC, filename))
    pairs = []
    n_total = len(rows)
    for r in rows:
        fa = r.get("fast_decision") is not None
        sa = r.get("hammer_decision") is not None
        if fa and sa:
            pairs.append((bool(r["fast_correct"]), bool(r["hammer_correct"])))
    out = cells_from_pairs(pairs)
    out["n_total"] = n_total
    out["n_included"] = len(pairs)
    return out


def realdiff():
    dec30 = load_json(os.path.join(RD, "decisions-coder30.json"))["rows"]
    decnext = load_json(os.path.join(RD, "decisions-next.json"))["rows"]
    truth = {r["decision_id"]: r["ground_truth"]
             for r in load_json(os.path.join(RD, "ground_truth.json"))}
    c30 = {r["decision_id"]: r for r in dec30}
    nxt = {r["decision_id"]: r for r in decnext}
    pairs = []
    for did in c30:
        if did in nxt:
            a, b = c30[did], nxt[did]
            if a.get("seat_decision") is not None and b.get("seat_decision") is not None:
                pairs.append((a["seat_decision"] == truth[did],
                              b["seat_decision"] == truth[did]))
    out = cells_from_pairs(pairs)
    out["n_total"] = len([k for k in c30 if k in nxt])
    out["n_included"] = len(pairs)
    return out


def main():
    with open(os.path.join(WS, "jev-discrepancy-results.json")) as f:
        recorded = {r["population"]: r for r in json.load(f)["populations"]}
    checks = [
        ("P-contract", jev_population("jev-decisions.json")),
        ("P-hard", jev_population("jev-decisions-hard.json")),
        ("P-lag", jev_population("jev-lag-decisions.json")),
        ("P-realdiff", realdiff()),
    ]
    ok = True
    for name, got in checks:
        rec = recorded[name]
        for key in ("both_right", "fast_only_right", "slow_only_right",
                    "both_wrong", "n_total", "n_included"):
            match = got[key] == rec[key]
            ok = ok and match
            print(f"{name} {key}: recount={got[key]} recorded={rec[key]} "
                  f"{'PASS' if match else 'FAIL'}")
    print("ALL PASS" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
