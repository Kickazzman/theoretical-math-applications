"""Komlos discrepancy trial (A1) — read-only computation under jev-discrepancy-protocol.md.
Reads saved decision files only. Writes results JSON + markdown. No source file is modified.
"""
import json, math, os, random, hashlib

WS = os.path.expanduser("~/workspace")

def load_json(path):
    with open(os.path.join(WS, path)) as f:
        return json.load(f)

def analyze(name, fast_correct, slow_correct, fast_answered, slow_answered, n_total):
    included = [(f, s) for f, s, fa, sa in zip(fast_correct, slow_correct, fast_answered, slow_answered) if fa and sa]
    n_inc = len(included)
    both_right = sum(1 for f, s in included if f and s)
    fast_only = sum(1 for f, s in included if f and not s)
    slow_only = sum(1 for f, s in included if not f and s)
    both_wrong = sum(1 for f, s in included if not f and not s)
    d1 = fast_only - slow_only
    fast_err = sum(1 for f, s in included if not f) / n_inc if n_inc else None
    slow_err = sum(1 for f, s in included if not s) / n_inc if n_inc else None
    # Amendment A: D1 = F - S is pairing-invariant under label shuffling; it has no null.
    # Structure statistic: slow-only count under permutation of slow labels relative to fast.
    rng = random.Random(20261031)
    fast_labels = [f for f, s in included]
    slow_labels = [s for f, s in included]
    slow_vals, k_vals = [], []
    for _ in range(5000):
        sl = slow_labels[:]
        rng.shuffle(sl)
        so = sum(1 for f, s in zip(fast_labels, sl) if (not f) and s)
        fo = sum(1 for f, s in zip(fast_labels, sl) if f and (not s))
        slow_vals.append(so)
        k_vals.append(so + fo)
    def summ(vals):
        m = sum(vals) / len(vals)
        return m, math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))
    so_mean, so_sd = summ(slow_vals)
    k_mean, k_sd = summ(k_vals)
    k_obs = fast_only + slow_only
    return {
        "population": name, "n_total": n_total, "n_included": n_inc,
        "n_excluded_null": n_total - n_inc,
        "both_right": both_right, "fast_only_right": fast_only,
        "slow_only_right": slow_only, "both_wrong": both_wrong,
        "D1": d1, "abs_D1": abs(d1),
        "fast_error_rate_included": fast_err, "slow_error_rate_included": slow_err,
        "slow_only_null_mean": so_mean, "slow_only_null_sd": so_sd,
        "slow_only_p_le": sum(1 for v in slow_vals if v <= slow_only) / 5000,
        "disagree_K": k_obs, "disagree_null_mean": k_mean, "disagree_null_sd": k_sd,
        "disagree_p_two_sided": sum(1 for v in k_vals if abs(v - k_mean) >= abs(k_obs - k_mean)) / 5000,
        "null_shuffles": 5000,
        "sqrt_N": math.sqrt(n_inc) if n_inc else None,
        "logN_quarter": (math.log(n_inc) ** 0.25) if n_inc and n_inc > 1 else None,
    }

results = []

def jev_pop(name, path):
    rows = load_json(path)
    fc = [bool(r["fast_correct"]) for r in rows]
    sc = [bool(r["hammer_correct"]) for r in rows]
    fa = [r.get("fast_decision") is not None for r in rows]
    sa = [r.get("hammer_decision") is not None for r in rows]
    results.append(analyze(name, fc, sc, fa, sa, len(rows)))

jev_pop("P-contract", "jev-decisions.json")
jev_pop("P-hard", "jev-decisions-hard.json")
jev_pop("P-lag", "jev-lag-decisions.json")

# Real-diff: pair by decision_id.
gt = {r["decision_id"]: r["ground_truth"] for r in load_json("real-diff-coder/ground_truth.json")}
c30 = {r["decision_id"]: r for r in load_json("real-diff-coder/decisions-coder30.json")["rows"]}
nxt = {r["decision_id"]: r for r in load_json("real-diff-coder/decisions-next.json")["rows"]}
ids = [k for k in c30 if k in nxt]
fc, sc, fa, sa = [], [], [], []
for k in ids:
    a, b = c30[k], nxt[k]
    fa.append(a.get("seat_decision") is not None)
    sa.append(b.get("seat_decision") is not None)
    fc.append(a.get("seat_decision") == gt[k])
    sc.append(b.get("seat_decision") == gt[k])
results.append(analyze("P-realdiff", fc, sc, fa, sa, len(ids)))

proto_hash = hashlib.sha256(open(os.path.join(WS, "jev-discrepancy-protocol.md"), "rb").read()).hexdigest()
out = {"protocol": "jev-discrepancy-protocol.md", "protocol_sha256": proto_hash, "populations": results}
with open(os.path.join(WS, "jev-discrepancy-results.json"), "w") as f:
    json.dump(out, f, indent=2)

lines = ["# Komlos discrepancy trial (A1) — results", "",
         f"Protocol: `jev-discrepancy-protocol.md`, sha256 `{proto_hash}`. Computed 2026-10-31 under that protocol. Source files unmodified.",
         "", "| Population | N total | Included | Excluded (null) | Both right | Fast-only | Slow-only | Both wrong | D1 (marginal) | Fast err | Slow err | Slow-only null mean | Slow-only null SD | p (slow-only ≤ obs) | Disagree K | K null mean | K null SD | K p (2-sided) | sqrt(N) | (ln N)^(1/4) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in results:
    lines.append(f"| {r['population']} | {r['n_total']} | {r['n_included']} | {r['n_excluded_null']} | {r['both_right']} | {r['fast_only_right']} | {r['slow_only_right']} | {r['both_wrong']} | {r['D1']} | {r['fast_error_rate_included']:.3f} | {r['slow_error_rate_included']:.3f} | {r['slow_only_null_mean']:.2f} | {r['slow_only_null_sd']:.2f} | {r['slow_only_p_le']:.4f} | {r['disagree_K']} | {r['disagree_null_mean']:.2f} | {r['disagree_null_sd']:.2f} | {r['disagree_p_two_sided']:.4f} | {r['sqrt_N']:.2f} | {r['logN_quarter']:.3f} |")
lines += ["",
          "## Reading (per the protocol as amended by Amendment A)",
          "- D1 is a MARGINAL imbalance (fast correct count minus slow correct count). It is pairing-invariant under label shuffling, so it has NO permutation null and NO p-value. The first run's D1 null (SD 0.00, p 1.0000) was degenerate and is VOID; it is recorded in the protocol amendment, not here as a result.",
          "- Structure lives in the slow-only count. p (slow-only ≤ obs) < 0.05 means the slow seat is solely right less often than chance pairing would give — disagreement structurally favours the fast seat. That is a finding about the ensemble, not about Komlos.",
          "- Theorem-application verdict (pre-registered, both cases): the discrepancy DIAGNOSTIC applies; the Komlos bound in its own form does not, because its free sign-choice structure has no subject meaning here — the observed signing is fixed by which seat was right. The (ln N)^(1/4) column is a scale comparison only; no verdict on the theorem follows from it.",
          "- Correction carried from the protocol: the application file's '280 JEV + 56 real-diff' pairable count was wrong (lag file overlaps contract/hard by 40 prompt_refs each; null-sensor rows are single-seat). Populations are reported separately above; no pooled total is claimed."]
with open(os.path.join(WS, "jev-discrepancy-results.md"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
