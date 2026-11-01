"""V-01b: threshold question, three different instruments. Read-only over saved rows."""
import json, os
from collections import Counter, defaultdict

WS = os.path.expanduser("~/workspace")

def load(p):
    with open(os.path.join(WS, p)) as f:
        return json.load(f)

def jev_rows(path):
    rows = load(path)
    out = []
    for r in rows:
        out.append({
            "fast_ans": r.get("fast_decision") is not None,
            "slow_ans": r.get("hammer_decision") is not None,
            "conf": float(r["fast_confidence"]) if r.get("fast_confidence") is not None else None,
            "f": bool(r["fast_correct"]) if r.get("fast_decision") is not None else None,
            "s": bool(r["hammer_correct"]) if r.get("hammer_decision") is not None else None,
        })
    return out

def realdiff_rows():
    gt = {r["decision_id"]: r["ground_truth"] for r in load("real-diff-coder/ground_truth.json")}
    c30 = {r["decision_id"]: r for r in load("real-diff-coder/decisions-coder30.json")["rows"]}
    nxt = {r["decision_id"]: r for r in load("real-diff-coder/decisions-next.json")["rows"]}
    out = []
    for k in c30:
        if k not in nxt:
            continue
        a, b = c30[k], nxt[k]
        out.append({
            "fast_ans": a.get("seat_decision") is not None,
            "slow_ans": b.get("seat_decision") is not None,
            "conf": float(a["seat_confidence"]) if a.get("seat_confidence") is not None else None,
            "f": (a["seat_decision"] == gt[k]) if a.get("seat_decision") is not None else None,
            "s": (b["seat_decision"] == gt[k]) if b.get("seat_decision") is not None else None,
        })
    return out

POPS = {
    "P-contract": jev_rows("jev-decisions.json"),
    "P-hard": jev_rows("jev-decisions-hard.json"),
    "P-lag": jev_rows("jev-lag-decisions.json"),
    "P-realdiff": realdiff_rows(),
}
GRID = [round(0.50 + 0.05 * i, 2) for i in range(11)]

def leg1_direct(rows, T):
    esc = cov = corr = 0
    for r in rows:
        if (not r["fast_ans"]) or (r["conf"] is not None and r["conf"] < T):
            esc += 1
            if r["slow_ans"]:
                cov += 1
                corr += int(r["s"])
        else:
            cov += 1
            corr += int(r["f"])
    n = len(rows)
    return esc / n, cov / n, (corr / cov if cov else None)

def leg1_cells(rows, T):
    # aggregate by (fast_ans, slow_ans, conf-below-T, f, s); conf None treated as below every T (null escalates)
    cells = Counter()
    for r in rows:
        below = (r["conf"] is None) or (r["conf"] < T)
        cells[(r["fast_ans"], r["slow_ans"], below, r["f"], r["s"])] += 1
    esc = cov = corr = 0
    for (fa, sa, below, f, s), v in cells.items():
        if (not fa) or below:
            esc += v
            if sa:
                cov += v
                corr += v * int(s)
        else:
            cov += v
            corr += v * int(f)
    n = len(rows)
    return esc / n, cov / n, (corr / cov if cov else None)

def leg23(rows):
    inc = [r for r in rows if r["fast_ans"] and r["slow_ans"]]
    by_conf = defaultdict(lambda: [0, 0, 0])  # n, fast_correct, slow_correct
    for r in inc:
        c = by_conf[r["conf"]]
        c[0] += 1
        c[1] += int(r["f"])
        c[2] += int(r["s"])
    calib = {str(k): {"n": v[0], "fast_acc": v[1] / v[0], "slow_acc": v[2] / v[0]} for k, v in sorted(by_conf.items())}
    fast_acc = sum(int(r["f"]) for r in inc) / len(inc)
    oracle_corr = sum(max(v[1], v[2]) for v in by_conf.values())
    oracle = oracle_corr / len(inc)
    # cross-check: direct oracle count
    oracle_direct = sum(1 for r in inc if (r["s"] if by_conf[r["conf"]][2] > by_conf[r["conf"]][1] else r["f"])) / len(inc)
    return calib, fast_acc, oracle, oracle_direct, len(inc)

agreement = True
out = {}
for name, rows in POPS.items():
    leg1 = {}
    for T in GRID:
        a, b = leg1_direct(rows, T), leg1_cells(rows, T)
        if a != b:
            agreement = False
        leg1[str(T)] = {"escalation": a[0], "coverage": a[1], "accuracy_covered": a[2]}
    base = leg1["0.8"]
    matters = [T for T, v in leg1.items() if T != "0.8" and (v["coverage"], v["accuracy_covered"]) != (base["coverage"], base["accuracy_covered"])]
    calib, fast_acc, oracle, oracle_direct, n_inc = leg23(rows)
    if oracle != oracle_direct:
        agreement = False
    confs = sorted(float(k) for k in calib)
    accs = [calib[str(c)]["fast_acc"] for c in confs]
    increasing = all(accs[i] < accs[i + 1] for i in range(len(accs) - 1))
    out[name] = {
        "n_total": len(rows), "n_included": n_inc,
        "leg1_full_population": leg1,
        "leg1_threshold_matters": matters,
        "leg2_calibration": calib,
        "leg2_strictly_increasing": increasing,
        "leg3_fast_only_acc": fast_acc,
        "leg3_oracle_acc": oracle,
        "leg3_headroom": oracle - fast_acc,
    }

print(json.dumps({"two_way_agreement": agreement, "populations": out}, indent=1))
with open(os.path.join(WS, "v01b-different-way-results.json"), "w") as f:
    json.dump({"two_way_agreement": agreement, "populations": out}, f, indent=1)
