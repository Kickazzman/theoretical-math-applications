#!/usr/bin/env python3
"""Program item 4: cost-error frontier sweep over SAVED JEV rows only.

No seat calls, no router, no GPU, no frank, no browser. Reads the four
decision logs, recomputes every policy from raw rows, and writes
machine-readable frontier data (JSON + CSV). Verification counts are
checked against the published run reports; any mismatch prints WARNING.

Populations (never blended):
  (a) lag: 100 rows, fast + hammer (jev-lag-decisions.json)
  (b) orig+hard: 80 rows (a)+(b) only, fast + hammer
      (jev-decisions.json filtered to type a/b + jev-decisions-hard.json)
  (c) ns2 (null-sensor v2): 100 rows, fast ONLY (jev-null-sensor-records.json)

Floor model (item 1): escalated items fail with P = 0.010 (point),
Wilson band (0.0018, 0.0545). A failed escalated item counts as a final
error (conservative: on a both-pass ambiguity an arbitrary tie-break
would err only half the time, so the true floor contribution is <= this).
Rates are REALIZED on these rows; the band comes only from floor
uncertainty, not from sampling error on the observed counts.

Policies:
  fast-alone: escalate nothing.
  null-only: escalate iff fast null.
  lean: escalate iff fast null OR fast conf < 0.8.
  full: escalate iff fast null OR seats disagree OR fast conf < 0.8
        (unavailable on ns2: no hammer).
  threshold+null sweep: escalate iff fast null OR fast conf < t,
        t in {0.8} U observed confidences U {1.01} (1.01 = escalate-all).
  pure-threshold sweep: escalate iff fast conf < t (nulls NOT escalated),
        same t values. Reported secondarily; it cannot fix nulls.
"""
import json, csv, collections

FLOOR_P = 0.010
FLOOR_LO = 0.0018
FLOOR_HI = 0.0545

def load(path):
    with open(path) as f:
        return json.load(f)

def is_null(row, pop):
    if pop == "ns2":
        return bool(row.get("fast_null", row.get("fast_empty", False)))
    return bool(row.get("fast_empty", False))

def fast_conf(row):
    c = row.get("fast_confidence")
    return None if c is None else float(c)

def fast_wrong_answered(row, pop):
    # wrong-when-answered: answered (not null) and fast_correct is False
    if is_null(row, pop):
        return False
    return row.get("fast_correct") is not True

def fast_alone_error(row, pop):
    # null counts as an error under fast-alone (no answer)
    return row.get("fast_correct") is not True

def disagree(row):
    fd, hd = row.get("fast_decision"), row.get("hammer_decision")
    if fd is None or hd is None:
        return False
    return fd != hd

def price(rows, pop, esc_fn):
    n = len(rows)
    esc = sum(1 for r in rows if esc_fn(r))
    # errors remaining after calculator resolves escalated items:
    # wrong-when-answered rows that were NOT escalated (nulls escalated
    # are resolved; nulls NOT escalated stay errors only if the policy
    # leaves them — handled by caller via non_esc_errors definition).
    non_esc_errors = 0
    for r in rows:
        if esc_fn(r):
            continue
        if fast_alone_error(r, pop):
            non_esc_errors += 1
    err_perfect = non_esc_errors / n
    adj = (non_esc_errors + esc * FLOOR_P) / n
    adj_lo = (non_esc_errors + esc * FLOOR_LO) / n
    adj_hi = (non_esc_errors + esc * FLOOR_HI) / n
    return {
        "n": n, "esc_count": esc, "esc_fraction": esc / n,
        "non_esc_errors": non_esc_errors,
        "err_perfect": err_perfect,
        "err_floor_point": adj, "err_floor_low": adj_lo, "err_floor_high": adj_hi,
    }

def main():
    orig_all = load("jev-decisions.json")
    orig = [r for r in orig_all if r.get("type") in ("a", "b")]
    hard = load("jev-decisions-hard.json")
    lag = load("jev-lag-decisions.json")
    ns2 = load("jev-null-sensor-records.json")

    pops = {
        "lag": lag,
        "orig+hard": orig + hard,
        "ns2": ns2,
    }

    # ---- verification block: recomputed counts vs published reports ----
    print("=== VERIFICATION (recomputed from raw rows) ===")
    for name, rows in pops.items():
        n = len(rows)
        nulls = sum(1 for r in rows if is_null(r, name))
        answered = n - nulls
        correct = sum(1 for r in rows if r.get("fast_correct") is True)
        wrong_ans = sum(1 for r in rows if fast_wrong_answered(r, name))
        confs = collections.Counter(fast_conf(r) for r in rows if not is_null(r, name))
        print(f"{name}: n={n} nulls={nulls} answered={answered} "
              f"fast_correct={correct} wrong_when_answered={wrong_ans} "
              f"conf_dist={dict(sorted(confs.items()))}")
        if name != "ns2":
            dis = sum(1 for r in rows if disagree(r))
            both_ans = sum(1 for r in rows
                           if not is_null(r, name) and r.get("hammer_decision") is not None)
            agree = sum(1 for r in rows
                        if not is_null(r, name) and r.get("hammer_decision") is not None
                        and r.get("fast_decision") == r.get("hammer_decision"))
            print(f"   both_answered={both_ans} agree={agree} disagree={dis} "
                  f"fast_right_dis={sum(1 for r in rows if disagree(r) and r.get('fast_correct') is True)}")
        # GT consistency: fast_correct == (decision == ground_truth) when answered
        bad = [r.get("decision_id", r.get("problem_id")) for r in rows
               if not is_null(r, name)
               and (r.get("fast_decision") == r.get("ground_truth")) != (r.get("fast_correct") is True)]
        gtm = [r.get("decision_id", r.get("problem_id")) for r in rows if r.get("gt_mismatch")]
        print(f"   gt_consistency_mismatches={bad} gt_mismatch_flags={gtm}")
    # expected values from the reports
    expect = {
        "lag": dict(n=100, nulls=28, correct=72, wrong_ans=0, disagree=22),
        "orig+hard": dict(n=80, nulls=20, correct=60, wrong_ans=0, disagree=19),
        "ns2": dict(n=100, nulls=14, correct=85, wrong_ans=1),
    }
    for name, rows in pops.items():
        e = expect[name]
        got = dict(n=len(rows),
                   nulls=sum(1 for r in rows if is_null(r, name)),
                   correct=sum(1 for r in rows if r.get("fast_correct") is True),
                   wrong_ans=sum(1 for r in rows if fast_wrong_answered(r, name)))
        if name != "ns2":
            got["disagree"] = sum(1 for r in rows if disagree(r))
        for k, v in e.items():
            if got[k] != v:
                print(f"WARNING: {name} {k}: recomputed {got[k]} != report {v}")
    print("=== END VERIFICATION ===\n")

    # ---- policies ----
    def pol_null(r, pop):
        return is_null(r, pop)
    def pol_lean(r, pop):
        if is_null(r, pop):
            return True
        c = fast_conf(r)
        return c is not None and c < 0.8
    def pol_full(r, pop):
        if is_null(r, pop):
            return True
        if disagree(r):
            return True
        c = fast_conf(r)
        return c is not None and c < 0.8

    out = {"floor": {"p": FLOOR_P, "wilson_low": FLOOR_LO, "wilson_high": FLOOR_HI},
           "populations": {}, "insurance": {}, "ns2_cases": {}}

    for name, rows in pops.items():
        observed = sorted({fast_conf(r) for r in rows if not is_null(r, name)})
        t_values = [0.8] + observed + [1.01]
        res = {}
        res["fast-alone"] = price(rows, name, lambda r: False)
        res["null-only"] = price(rows, name, lambda r, p=name: pol_null(r, p))
        res["lean"] = price(rows, name, lambda r, p=name: pol_lean(r, p))
        if name != "ns2":
            res["full"] = price(rows, name, lambda r, p=name: pol_full(r, p))
        # threshold+null sweep
        sweep = {}
        for t in t_values:
            def esc_tn(r, t=t, p=name):
                if is_null(r, p):
                    return True
                c = fast_conf(r)
                return c is not None and c < t
            sweep[repr(t)] = price(rows, name, esc_tn)
        res["threshold+null_sweep"] = sweep
        # pure-threshold sweep (nulls NOT escalated)
        sweep_pure = {}
        for t in t_values:
            def esc_pt(r, t=t):
                c = fast_conf(r)
                return c is not None and c < t
            sweep_pure[repr(t)] = price(rows, name, esc_pt)
        res["pure_threshold_sweep"] = sweep_pure
        out["populations"][name] = res

        print(f"--- {name} (n={len(rows)}) ---")
        for pol in ("fast-alone", "null-only", "lean", "full"):
            if pol not in res:
                continue
            d = res[pol]
            print(f"{pol}: esc={d['esc_count']}/{d['n']} ({d['esc_fraction']:.4f}) "
                  f"err_perfect={d['err_perfect']:.4f} "
                  f"err_floor={d['err_floor_point']:.4f} ({d['err_floor_low']:.4f}, {d['err_floor_high']:.4f})")
        print("threshold+null sweep (t -> esc_frac, err_perfect, err_floor_point):")
        for t, d in sweep.items():
            print(f"  t={t}: {d['esc_fraction']:.4f}, {d['err_perfect']:.4f}, {d['err_floor_point']:.4f}")
        print("pure-threshold sweep (t -> esc_frac, err_perfect, err_floor_point):")
        for t, d in sweep_pure.items():
            print(f"  t={t}: {d['esc_fraction']:.4f}, {d['err_perfect']:.4f}, {d['err_floor_point']:.4f}")

    # ---- insurance pricing: full over lean on fast+hammer populations ----
    for name in ("lag", "orig+hard"):
        rows = pops[name]
        lean = out["populations"][name]["lean"]
        full = out["populations"][name]["full"]
        extra_esc = full["esc_count"] - lean["esc_count"]
        dis_rate = sum(1 for r in rows if disagree(r)) / len(rows)
        extra_floor = extra_esc * FLOOR_P / len(rows)
        # break-even future fast-wrong-among-disagreements rate r:
        # gain = dis_rate * r (perfect calc, approx) vs extra floor cost
        breakeven = extra_floor / dis_rate if dis_rate else None
        out["insurance"][name] = {
            "lean_esc": lean["esc_count"], "full_esc": full["esc_count"],
            "extra_esc": extra_esc, "extra_esc_fraction": extra_esc / len(rows),
            "disagreement_rate": dis_rate,
            "observed_gain_errors": 0,
            "extra_floor_point": extra_floor,
            "breakeven_fast_wrong_among_disagreements": breakeven,
        }
        print(f"INSURANCE {name}: extra_esc={extra_esc} ({extra_esc/len(rows):.4f}) "
              f"dis_rate={dis_rate:.4f} extra_floor={extra_floor:.5f} breakeven_r={breakeven}")

    # ---- ns2 cases ----
    a23 = [r for r in ns2 if r.get("decision_id") == "ns2-a23"]
    a35 = [r for r in ns2 if r.get("decision_id") == "ns2-a35"]
    for label, recs in (("ns2-a23", a23), ("ns2-a35", a35)):
        if recs:
            r = recs[0]
            out["ns2_cases"][label] = {
                "function": r.get("function"), "type": r.get("type"),
                "tier": r.get("tier"), "subtlety": r.get("subtlety"),
                "fast_decision": r.get("fast_decision"),
                "fast_confidence": fast_conf(r), "fast_correct": r.get("fast_correct"),
                "fast_null": is_null(r, "ns2"), "ground_truth": r.get("ground_truth"),
            }
            print(f"CASE {label}: {out['ns2_cases'][label]}")
        else:
            print(f"CASE {label}: NOT FOUND")

    with open("jev-frontier-data.json", "w") as f:
        json.dump(out, f, indent=2)

    # flat CSV: population, policy, threshold, esc_fraction, err_perfect,
    # err_floor_point, err_floor_low, err_floor_high
    with open("jev-frontier-data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["population", "policy", "threshold", "n", "esc_count",
                    "esc_fraction", "non_esc_errors", "err_perfect",
                    "err_floor_point", "err_floor_low", "err_floor_high"])
        for name, res in out["populations"].items():
            for pol in ("fast-alone", "null-only", "lean", "full"):
                if pol not in res:
                    continue
                d = res[pol]
                w.writerow([name, pol, "", d["n"], d["esc_count"], d["esc_fraction"],
                            d["non_esc_errors"], d["err_perfect"], d["err_floor_point"],
                            d["err_floor_low"], d["err_floor_high"]])
            for sweep_name in ("threshold+null_sweep", "pure_threshold_sweep"):
                for t, d in res[sweep_name].items():
                    w.writerow([name, sweep_name, t, d["n"], d["esc_count"], d["esc_fraction"],
                                d["non_esc_errors"], d["err_perfect"], d["err_floor_point"],
                                d["err_floor_low"], d["err_floor_high"]])
    print("\nWrote workspace/jev-frontier-data.json + jev-frontier-data.csv")

if __name__ == "__main__":
    main()
