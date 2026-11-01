#!/usr/bin/env python3
"""Item 5, step 1: recompute hammer calibration from SAVED rows only.

Populations (per brief): original (a)+(b) + hard (a)+(b) + lag.
(c) rows excluded (different question). No seat calls, no edits to
existing files. Output: jev-hammer-recalibration-calibration.json
(new file) + printed tables.
"""
import json
import math
import re
from collections import Counter

Z = 1.96


def wilson(k, n):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    m = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (round(max(0.0, c - m), 4), round(min(1.0, c + m), 4))


def rate(k, n):
    lo, hi = wilson(k, n)
    return {"k": k, "n": n,
            "rate": round(k / n, 4) if n else None,
            "wilson95": [lo, hi]}


def strip_think(raw):
    if raw is None:
        return ""
    s = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    s = re.sub(r"<think>.*$", "", s, flags=re.DOTALL)
    return s


def bare_token(raw, allowed):
    s = strip_think(raw).strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    s = s.strip()
    if s in allowed and "{" not in s:
        return s
    return None


def load():
    rows = []
    # original: filter (a)+(b)
    for r in json.load(open("jev-decisions.json")):
        if r["type"] not in ("a", "b"):
            continue
        rows.append(("orig", r))
    for r in json.load(open("jev-decisions-hard.json")):
        if r["type"] not in ("a", "b"):
            continue
        rows.append(("hard", r))
    for r in json.load(open("jev-lag-decisions.json")):
        rows.append(("lag", r))
    return rows


def main():
    rows = load()
    print(f"total rows: {len(rows)}")
    out = {}
    norm = []
    gt_mismatch_flags = 0
    hc_field_mismatch = 0
    ok_vs_answered_mismatch = 0
    for src, r in rows:
        allowed = ["pass", "fail"] if r["type"] == "a" else ["A", "B"]
        gt = r.get("ground_truth")
        if gt is None:
            gt = r.get("item_expected", r.get("correct"))
        hd = r.get("hammer_decision")
        hc_field = r.get("hammer_correct")
        answered = hd is not None
        if answered and hc_field is not None and hc_field != (hd == gt):
            hc_field_mismatch += 1
        if r.get("hammer_contract_ok") is not None and bool(r["hammer_contract_ok"]) != answered:
            ok_vs_answered_mismatch += 1
        if r.get("gt_mismatch"):
            gt_mismatch_flags += 1
        bw = r.get("hammer_bare_word")
        if bw is None:
            bw = bare_token(r.get("hammer_raw"), allowed) is not None
        lean = None
        if not answered and bw:
            lean = bare_token(r.get("hammer_raw"), allowed)
        if answered:
            cls = "parseable_fenced" if r.get("hammer_prose") else "parseable_clean"
        elif bw:
            cls = "bare_word"
        else:
            cls = "other_null"
        fd = r.get("fast_decision")
        both = (fd is not None and answered)
        norm.append({
            "src": src, "type": r["type"],
            "id": r.get("decision_id", r.get("problem_id")),
            "gt": gt, "hammer_decision": hd,
            "hammer_confidence": r.get("hammer_confidence"),
            "hammer_correct": (hd == gt) if answered else None,
            "hammer_correct_field": hc_field,
            "answered": answered, "contract_class": cls,
            "bare_word": bool(bw), "leaning": lean,
            "leaning_correct": (lean == gt) if lean is not None else None,
            "fast_decision": fd, "fast_correct": r.get("fast_correct"),
            "both_answered": both,
            "agree": (both and fd == hd),
            "disagree": (both and fd != hd),
            "hammer_prose": bool(r.get("hammer_prose")),
            "hammer_empty": bool(r.get("hammer_empty")),
        })
    out["n_rows"] = len(rows)
    out["gt_mismatch_flags"] = gt_mismatch_flags
    out["hammer_correct_field_mismatches"] = hc_field_mismatch
    out["contract_ok_vs_answered_mismatches"] = ok_vs_answered_mismatch

    def tab(name, keyfn, subset=None):
        groups = {}
        for x in norm:
            if subset and not subset(x):
                continue
            groups.setdefault(keyfn(x), []).append(x)
        t = {}
        for k in sorted(groups, key=str):
            g = groups[k]
            ans = [x for x in g if x["answered"]]
            cor = sum(1 for x in ans if x["hammer_correct"])
            t[str(k)] = {"rows": len(g), "answered": rate(cor, len(ans))}
        out[name] = t
        print(f"\n== {name} ==")
        for k, v in t.items():
            print(f"  {k}: rows={v['rows']} answered-rate={v['answered']}")

    # Overall answered calibration
    ans = [x for x in norm if x["answered"]]
    cor = sum(1 for x in ans if x["hammer_correct"])
    out["overall_answered"] = rate(cor, len(ans))
    print(f"\nOVERALL answered: {cor}/{len(ans)} = {out['overall_answered']}")

    # Confidence distribution among answered
    conf = Counter(x["hammer_confidence"] for x in ans)
    out["confidence_distribution_answered"] = {str(k): v for k, v in conf.items()}
    print("confidence distribution (answered):", dict(conf))
    tab("by_confidence", lambda x: x["hammer_confidence"],
        subset=lambda x: x["answered"])
    tab("by_type_answered", lambda x: x["type"],
        subset=lambda x: x["answered"])
    tab("by_source_answered", lambda x: x["src"],
        subset=lambda x: x["answered"])
    tab("by_contract_class", lambda x: x["contract_class"])
    # Leaning correctness for bare-word rows (separate from answered)
    bw_rows = [x for x in norm if x["contract_class"] == "bare_word"]
    bw_lean = [x for x in bw_rows if x["leaning"] is not None]
    bw_cor = sum(1 for x in bw_lean if x["leaning_correct"])
    out["bare_word_leaning"] = {"rows": len(bw_rows),
                                "leaning_extracted": len(bw_lean),
                                "leaning_correct": rate(bw_cor, len(bw_lean))}
    print(f"\nbare-word leaning: {bw_cor}/{len(bw_lean)} = {out['bare_word_leaning']}")
    # Decision-value splits (answered only)
    tab("by_decision_value_a", lambda x: x["hammer_decision"],
        subset=lambda x: x["answered"] and x["type"] == "a")
    tab("by_decision_value_b", lambda x: x["hammer_decision"],
        subset=lambda x: x["answered"] and x["type"] == "b")
    # Agreement splits (both-answered rows)
    tab("by_agreement", lambda x: "agree" if x["agree"] else "disagree",
        subset=lambda x: x["both_answered"])
    # Disagreement counts
    dis = [x for x in norm if x["disagree"]]
    out["disagreements"] = {
        "n": len(dis),
        "hammer_correct": sum(1 for x in dis if x["hammer_correct"]),
        "fast_correct": sum(1 for x in dis if x["fast_correct"]),
    }
    print(f"\ndisagreements: n={len(dis)} hammer_right="
          f"{out['disagreements']['hammer_correct']} fast_right="
          f"{out['disagreements']['fast_correct']}")
    agr = [x for x in norm if x["agree"]]
    out["agreements"] = {
        "n": len(agr),
        "hammer_correct": sum(1 for x in agr if x["hammer_correct"]),
        "fast_correct": sum(1 for x in agr if x["fast_correct"]),
    }
    print(f"agreements: n={len(agr)} hammer_right="
          f"{out['agreements']['hammer_correct']} fast_right="
          f"{out['agreements']['fast_correct']}")

    with open("jev-hammer-recalibration-calibration.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote jev-hammer-recalibration-calibration.json")


if __name__ == "__main__":
    main()
