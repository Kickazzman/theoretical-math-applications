#!/usr/bin/env python3
"""Item 5, step 3: separation tests on hammer probe rows.

Reads jev-hammer-recalibration-probe.json (fresh hammer calls on the
100 lag items, logprobs if supported) + jev-lag-decisions.json (saved
rows, for the probe-vs-saved stability join). No seat calls.
Output: jev-hammer-recalibration-separation.json + printed tables.
"""
import json
import math
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
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None,
            "wilson95": [lo, hi]}


def ranks_avg(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for t in range(i, j + 1):
            r[order[t]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    rx, ry = ranks_avg(xs), ranks_avg(ys)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) *
                    sum((b - my) ** 2 for b in ry))
    if den == 0:
        return None
    return round(num / den, 4)


def tertile_tables(rows, feat):
    """rows: answered rows with numeric feat. Returns tertile buckets."""
    vals = sorted(r[feat] for r in rows)
    n = len(vals)
    # cut points by rank thirds
    c1, c2 = vals[n // 3], vals[(2 * n) // 3]
    buckets = {"low": [], "mid": [], "high": []}
    for r in rows:
        v = r[feat]
        buckets["low" if v <= c1 else ("mid" if v <= c2 else "high")].append(r)
    out = {}
    for b, g in buckets.items():
        cor = sum(1 for x in g if x["hammer_correct"])
        out[b] = rate(cor, len(g))
    return out, (c1, c2)


def main():
    probe = json.load(open("jev-hammer-recalibration-probe.json"))
    rows = probe["rows"]
    print(f"probe rows: {len(rows)} logprobs_supported="
          f"{probe['logprobs_supported']} ({probe['logprobs_reason']})")
    ans = [r for r in rows if r["hammer_decision"] is not None]
    cor = sum(1 for r in ans if r["hammer_correct"])
    print(f"probe answered: {len(ans)}/100 correct {cor} "
          f"= {rate(cor, len(ans))}")
    print("probe confidence dist (answered):",
          dict(Counter(r["hammer_confidence"] for r in ans)))
    print("probe contract classes:",
          dict(Counter(("fenced" if r["hammer_prose"] and r["hammer_decision"] is not None
                        else ("bare_word" if r["hammer_bare_word"]
                              else ("clean" if r["hammer_decision"] is not None
                                    else "other_null"))) for r in rows)))
    print("probe (a) decisions:", dict(Counter(r["hammer_decision"] for r in rows if r["type"] == "a")))
    print("probe (b) decisions:", dict(Counter(r["hammer_decision"] for r in rows if r["type"] == "b")))
    print("probe n_attempts:", dict(Counter(r["hammer_n_attempts"] for r in rows)))
    print("probe think flags:", sum(1 for r in rows if r["hammer_think"]),
          "empty flags:", sum(1 for r in rows if r["hammer_empty"]))

    out = {"n_probe": len(rows), "n_answered": len(ans),
           "overall_answered": rate(cor, len(ans)),
           "logprobs_supported": probe["logprobs_supported"],
           "logprobs_reason": probe["logprobs_reason"]}

    # --- numeric feature distributions + separation (answered only)
    feats = []
    if probe["logprobs_supported"]:
        feats += ["decision_logprob", "confidence_logprob", "mean_logprob",
                  "min_logprob", "mean_top1_prob", "decision_margin"]
    feats += ["hammer_raw_len", "hammer_completion_tokens",
              "hammer_duration_s"]
    out["features"] = {}
    for f in feats:
        sub = []
        for r in ans:
            if f.startswith("hammer_"):
                v = r.get(f)
            else:
                lp = r.get("hammer_logprob_features") or {}
                v = lp.get(f)
            if v is not None:
                sub.append((r, v))
        if not sub:
            print(f"\nfeat {f}: no data")
            out["features"][f] = {"n": 0}
            continue
        vs = [v for _, v in sub]
        print(f"\nfeat {f}: n={len(vs)} min={min(vs):.4g} "
              f"median={sorted(vs)[len(vs)//2]:.4g} max={max(vs):.4g}")
        flat = [{"hammer_correct": r["hammer_correct"], f: v} for r, v in sub]
        rho = spearman([x[f] for x in flat],
                       [1 if x["hammer_correct"] else 0 for x in flat])
        tabs, cuts = tertile_tables(flat, f)
        print(f"  spearman vs correct: {rho}")
        print(f"  tertile cuts: {cuts}")
        for b, t in tabs.items():
            print(f"    {b}: {t}")
        out["features"][f] = {"n": len(vs),
                              "min": min(vs), "max": max(vs),
                              "spearman_vs_correct": rho,
                              "tertiles": tabs, "cuts": cuts}

    # --- categorical splits (answered only unless noted)
    def cat(name, keyfn, subset=None):
        groups = {}
        for r in ans:
            if subset and not subset(r):
                continue
            groups.setdefault(keyfn(r), []).append(r)
        t = {}
        print(f"\n== {name} ==")
        for k in sorted(groups, key=str):
            g = groups[k]
            c = sum(1 for x in g if x["hammer_correct"])
            t[str(k)] = rate(c, len(g))
            print(f"  {k}: {t[str(k)]}")
        out[name] = t

    cat("probe_by_type", lambda r: r["type"])
    cat("probe_by_decision_a", lambda r: r["hammer_decision"],
        subset=lambda r: r["type"] == "a")
    cat("probe_by_decision_b", lambda r: r["hammer_decision"],
        subset=lambda r: r["type"] == "b")
    cat("probe_by_attempts", lambda r: r["hammer_n_attempts"])
    cat("probe_by_source", lambda r: r["source"])
    # bare-word leaning (not answered)
    bw = [r for r in rows if r["hammer_decision"] is None and r["hammer_bare_word"]]
    print(f"\nprobe bare-word rows: {len(bw)}")
    # leaning extraction (same strip rule as analyze)
    import re
    def lean_of(raw, allowed):
        s = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.DOTALL)
        s = re.sub(r"<think>.*$", "", s, flags=re.DOTALL)
        s = s.strip()
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
        s = s.strip()
        return s if s in allowed and "{" not in s else None
    lc = 0
    ln = 0
    for r in bw:
        allowed = ["pass", "fail"] if r["type"] == "a" else ["A", "B"]
        lean = lean_of(r["hammer_raw"], allowed)
        if lean is not None:
            ln += 1
            if lean == r["ground_truth"]:
                lc += 1
    print(f"probe bare-word leaning: {lc}/{ln} = {rate(lc, ln)}")
    out["probe_bare_word_leaning"] = {"rows": len(bw), "leaning": rate(lc, ln)}

    # --- stability join: probe hammer vs saved lag hammer, same items
    saved = {r["problem_id"]: r for r in json.load(open("jev-lag-decisions.json"))}
    both = agree = pr_only = sv_only = both_wrong = both_right = 0
    for r in rows:
        s = saved.get(r["problem_id"])
        if s is None:
            continue
        pd, sd = r["hammer_decision"], s["hammer_decision"]
        pc = (pd == r["ground_truth"]) if pd is not None else None
        sc = s["hammer_correct"] if sd is not None else None
        if pd is not None and sd is not None:
            both += 1
            if pd == sd:
                agree += 1
            if pc and sc:
                both_right += 1
            elif pc and not sc:
                pr_only += 1
            elif sc and not pc:
                sv_only += 1
            else:
                both_wrong += 1
    print(f"\nstability join (both answered): n={both} agree={agree} "
          f"({agree/both:.3f}) both_right={both_right} probe_only={pr_only} "
          f"saved_only={sv_only} both_wrong={both_wrong}")
    out["stability_join"] = {"both_answered": both, "agree": agree,
                             "agree_rate": round(agree / both, 4) if both else None,
                             "both_right": both_right, "probe_only_right": pr_only,
                             "saved_only_right": sv_only, "both_wrong": both_wrong}

    with open("jev-hammer-recalibration-separation.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote jev-hammer-recalibration-separation.json")


if __name__ == "__main__":
    main()
