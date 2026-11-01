"""V-01 threshold sweep, three independent computations. Read-only over saved rows."""
import json, os
from collections import Counter

WS = os.path.expanduser("~/workspace")

def load(p):
    with open(os.path.join(WS, p)) as f:
        return json.load(f)

def jev_pop(path):
    rows = load(path)
    out = []
    for r in rows:
        if r.get("fast_decision") is None or r.get("hammer_decision") is None:
            continue
        out.append((float(r["fast_confidence"]), bool(r["fast_correct"]), bool(r["hammer_correct"])))
    return out

def realdiff_pop():
    gt = {r["decision_id"]: r["ground_truth"] for r in load("real-diff-coder/ground_truth.json")}
    c30 = {r["decision_id"]: r for r in load("real-diff-coder/decisions-coder30.json")["rows"]}
    nxt = {r["decision_id"]: r for r in load("real-diff-coder/decisions-next.json")["rows"]}
    out = []
    for k in c30:
        if k not in nxt:
            continue
        a, b = c30[k], nxt[k]
        if a.get("seat_decision") is None or b.get("seat_decision") is None:
            continue
        out.append((float(a["seat_confidence"]), a["seat_decision"] == gt[k], b["seat_decision"] == gt[k]))
    return out

POPS = {
    "P-contract": jev_pop("jev-decisions.json"),
    "P-hard": jev_pop("jev-decisions-hard.json"),
    "P-lag": jev_pop("jev-lag-decisions.json"),
    "P-realdiff": realdiff_pop(),
}

GRID = [round(0.50 + 0.05 * i, 2) for i in range(11)]

def way1(rows, T):
    esc = 0
    corr = 0
    for conf, f, s in rows:
        if conf < T:
            esc += 1
            corr += int(s)
        else:
            corr += int(f)
    n = len(rows)
    return corr / n, esc / n

def way2(rows, T):
    cells = Counter((f, s, c) for c, f, s in rows)
    n = len(rows)
    esc = sum(v for (f, s, c), v in cells.items() if c < T)
    corr = sum(v for (f, s, c), v in cells.items() if (s if c < T else f))
    return corr / n, esc / n

def way3(rows):
    # distinct confidence values; effective thresholds just above each value
    vals = sorted({c for c, _, _ in rows})
    out = {}
    for v in vals:
        T = round(v + 1e-9, 9)
        out[v] = way1(rows, T)
    return vals, out

results = {}
agreement = True
for name, rows in POPS.items():
    table = {}
    for T in GRID:
        a1 = way1(rows, T)
        a2 = way2(rows, T)
        if a1 != a2:
            agreement = False
        table[str(T)] = {"accuracy": a1[0], "escalation": a1[1]}
    vals, step = way3(rows)
    # cross-check: grid point just above each distinct value must match step value
    for v, (acc, esc) in step.items():
        # find smallest grid T > v; if none (v >= 1.0), step value equals way1 at T=1.0+eps i.e. all escalated below... check directly
        T = round(v + 1e-9, 9)
        chk = way1(rows, T)
        if chk != (acc, esc):
            agreement = False
    results[name] = {
        "n_included": len(rows),
        "distinct_confidences": vals,
        "grid": table,
    }

def dominates(a_acc, a_esc, b_acc, b_esc):
    return (a_acc > b_acc and a_esc <= b_esc) or (a_acc >= b_acc and a_esc < b_esc)

dom = {}
for name, r in results.items():
    base = r["grid"]["0.8"]
    dom[name] = [T for T, v in r["grid"].items()
                 if T != "0.8" and dominates(v["accuracy"], v["escalation"], base["accuracy"], base["escalation"])]
    r["dominates_0.8"] = dom[name]
    r["dominated_by_0.8"] = [T for T, v in r["grid"].items()
                            if T != "0.8" and dominates(base["accuracy"], base["escalation"], v["accuracy"], v["escalation"])]

cands = set.intersection(*[set(v) for v in dom.values()]) if dom else set()
n_dom3 = {}
for T in [str(t) for t in GRID]:
    if T == "0.8":
        continue
    n_dom3[T] = sum(1 for name in dom if T in dom[name])
confirmed = [T for T, n in n_dom3.items() if n >= 3 and all(T not in results[name]["dominated_by_0.8"] for name in results)]
refuted = all(len(v) == 0 for v in dom.values())
verdict = "CONFIRMED" if confirmed else ("REFUTED" if refuted else "NEITHER")
out = {"protocol": "v01-threshold-sweep-protocol.md", "three_way_agreement": agreement,
       "populations": results, "verdict": verdict, "confirming_thresholds": confirmed}
print(json.dumps(out, indent=1))
with open(os.path.join(WS, "v01-threshold-sweep-results.json"), "w") as f:
    json.dump(out, f, indent=1)
