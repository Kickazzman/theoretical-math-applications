#!/usr/bin/env python3
"""Build HARD JEV items from verified materials-hard.

(a) 20 = 10 functions x 2: correct->buggy_a (FAIL) and buggy_b->correct
    (PASS). (a) items use the PRECISE spec.
(b) 20 = 10 functions x 2 pairs (correct vs buggy_a, correct vs buggy_b),
    correct position randomized (seed 20261029, recorded).
    (b) items use spec_b (ambiguous where the function has one).
No (c) items. Only AB_VALID functions supply items (asserted).
Writes ~/jev-test/jev-items-hard.json.
"""
import difflib
import json
import os
import random

BASE = '/home/joshua/jev-test/materials-hard'
MAIN = ['exponential_moving_average', 'merge_sorted_lists', 'parse_duration',
        'weighted_quantile', 'sliding_window_max', 'levenshtein',
        'interpolate_missing', 'allocate_budget', 'validate_ipv4_cidr',
        'moving_median']
SEED = 20261029


def read(name, fname):
    with open(os.path.join(BASE, name, fname)) as f:
        return f.read()


def diff(old, new, fromfile, tofile):
    return ''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=fromfile, tofile=tofile))


def main():
    specs = {fn['name']: fn for fn in
             json.load(open('/home/joshua/jev-test/jev-specs-hard.json'))['functions']}
    report = json.load(open('/home/joshua/jev-test/jev-verify-hard-report.json'))
    for name in MAIN:
        assert report[name]['AB_VALID'] is True, f"{name} not AB_VALID"
    rng = random.Random(SEED)
    items = []
    for name in MAIN:
        spec = specs[name]['spec']
        correct = read(name, 'correct.py')
        ba = read(name, 'buggy_a.py')
        bb = read(name, 'buggy_b.py')
        tests = read(name, 'tests.py')
        items.append({
            'decision_id': f"a{len([i for i in items if i['type'] == 'a']) + 1:02d}",
            'type': 'a', 'function': name,
            'prompt_ref': f"{name}:correct->buggy_a",
            'spec': spec, 'old_code': correct, 'new_code': ba,
            'diff': diff(correct, ba, 'correct.py', 'buggy_a.py'),
            'tests': tests, 'expected': 'fail'})
        items.append({
            'decision_id': f"a{len([i for i in items if i['type'] == 'a']) + 1:02d}",
            'type': 'a', 'function': name,
            'prompt_ref': f"{name}:buggy_b->correct",
            'spec': spec, 'old_code': bb, 'new_code': correct,
            'diff': diff(bb, correct, 'buggy_b.py', 'correct.py'),
            'tests': tests, 'expected': 'pass'})
    for name in MAIN:
        spec_b = specs[name].get('spec_b', specs[name]['spec'])
        correct = read(name, 'correct.py')
        for variant, vname in [('buggy_a.py', 'buggy_a'),
                               ('buggy_b.py', 'buggy_b')]:
            buggy = read(name, variant)
            pos = rng.choice(['A', 'B'])
            if pos == 'A':
                impl_a, impl_b = correct, buggy
            else:
                impl_a, impl_b = buggy, correct
            items.append({
                'decision_id': f"b{len([i for i in items if i['type'] == 'b']) + 1:02d}",
                'type': 'b', 'function': name,
                'prompt_ref': f"{name}:correct-vs-{vname}",
                'spec': spec_b, 'impl_a': impl_a, 'impl_b': impl_b,
                'correct_position': pos, 'expected': pos})
    out = {'seed': SEED, 'counts': {
        'a': len([i for i in items if i['type'] == 'a']),
        'b': len([i for i in items if i['type'] == 'b'])},
        'items': items}
    with open('/home/joshua/jev-test/jev-items-hard.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f"built {out['counts']} (seed {SEED})")
    for it in items:
        print(f"  {it['decision_id']} {it['type']} {it['prompt_ref']} "
              f"expected={it['expected']}")


if __name__ == '__main__':
    main()
