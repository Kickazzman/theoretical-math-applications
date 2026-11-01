#!/usr/bin/env python3
"""Analyze null-sensor records: primary 2x2 (null x hard), Wilson 95%
intervals, lift, duration tertiles, answered accuracy. Reads records
JSON (local copy) and prints + writes a JSON summary."""
import json, math, sys
from statistics import median

def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0.0, c-h), min(1.0, c+h))

def main(path):
    rows = json.load(open(path))
    n = len(rows)
    assert n == 100, n
    mism = [r['decision_id'] for r in rows
            if r['fast_contract_ok'] != (r['fast_decision'] is not None)]
    gt_mism = [r['decision_id'] for r in rows if r['gt_mismatch']]
    # 2x2: rows hardness, cols null
    cells = {}
    for h in ('hard', 'easy'):
        for null in (True, False):
            cells[(h, null)] = sum(1 for r in rows if r['hardness'] == h and r['fast_null'] == null)
    hn, hno = cells[('hard', True)], cells[('hard', False)]
    en, eno = cells[('easy', True)], cells[('easy', False)]
    n_null, n_ans = hn + en, hno + eno
    p_h_null = hn / n_null if n_null else None
    p_h_ans = hno / n_ans if n_ans else None
    lift = (p_h_null / p_h_ans) if (p_h_null is not None and p_h_ans) else None
    diff = (p_h_null - p_h_ans) if (p_h_null is not None and p_h_ans is not None) else None
    null_rate = n_null / n
    null_hard = hn / (hn + hno); null_easy = en / (en + eno)
    ans = [r for r in rows if not r['fast_null']]
    acc_ans = sum(1 for r in ans if r['fast_correct']) / len(ans) if ans else None
    acc_all = sum(1 for r in rows if r['fast_correct']) / n
    # Duration: tertiles of fast_duration_s (all items), null rate per tertile
    srt = sorted(rows, key=lambda r: r['fast_duration_s'])
    tert = []
    for i in range(3):
        chunk = srt[i*n//3:(i+1)*n//3] if i < 2 else srt[2*n//3:]
        nn = sum(1 for r in chunk if r['fast_null'])
        tert.append({'tertile': i+1, 'n': len(chunk),
                     'duration_range_s': [round(chunk[0]['fast_duration_s'], 2),
                                          round(chunk[-1]['fast_duration_s'], 2)],
                     'nulls': nn, 'null_rate': nn/len(chunk)})
    med_ans = median([r['fast_duration_s'] for r in ans]) if ans else None
    med_null = median([r['fast_duration_s'] for r in rows if r['fast_null']]) if n_null else None
    med_all = median([r['fast_duration_s'] for r in rows])
    # Secondary complexity check (post-hoc description only, NOT primary):
    # null rate by complexity class: lines <= median vs > median
    med_lines = median([r['complexity_lines'] for r in rows])
    comp = {}
    for label, pred in (('lines<=median', lambda r: r['complexity_lines'] <= med_lines),
                        ('lines>median', lambda r: r['complexity_lines'] > med_lines)):
        sub = [r for r in rows if pred(r)]
        comp[label] = {'n': len(sub), 'nulls': sum(1 for r in sub if r['fast_null']),
                       'null_rate': sum(1 for r in sub if r['fast_null'])/len(sub),
                       'hard': sum(1 for r in sub if r['hardness'] == 'hard')}
    # By type
    by_type = {}
    for t in ('a', 'b'):
        sub = [r for r in rows if r['type'] == t]
        by_type[t] = {'n': len(sub), 'nulls': sum(1 for r in sub if r['fast_null']),
                      'null_rate': sum(1 for r in sub if r['fast_null'])/len(sub)}
    out = {'n': n, 'contract_ok_mismatches': mism, 'gt_mismatches': gt_mism,
           'cells': {'hard_null': hn, 'hard_answered': hno, 'easy_null': en, 'easy_answered': eno},
           'overall_null_rate': null_rate, 'n_null': n_null, 'n_answered': n_ans,
           'P_hard_given_null': p_h_null, 'P_hard_given_null_wilson95': wilson(hn, n_null),
           'P_hard_given_answered': p_h_ans, 'P_hard_given_answered_wilson95': wilson(hno, n_ans),
           'lift_ratio': lift, 'lift_difference_pp': (diff*100 if diff is not None else None),
           'null_rate_hard': null_hard, 'null_rate_hard_wilson95': wilson(hn, hn+hno),
           'null_rate_easy': null_easy, 'null_rate_easy_wilson95': wilson(en, en+eno),
           'fast_accuracy_when_answered': acc_ans, 'fast_accuracy_overall': acc_all,
           'duration_tertiles': tert,
           'duration_median_answered_s': med_ans, 'duration_median_null_s': med_null,
           'duration_median_all_s': med_all,
           'null_rate_by_type': by_type,
           'null_rate_by_complexity_median_split_posthoc': comp}
    print(json.dumps(out, indent=2))
    with open(path.replace('records.json', 'analysis.json'), 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == '__main__':
    main(sys.argv[1])
