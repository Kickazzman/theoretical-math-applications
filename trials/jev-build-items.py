#!/usr/bin/env python3
"""Build JEV contract-test items from verified materials.

Reads ~/jev-test/jev-specs.json (specs) and
~/jev-test/verify-report.json (validity gates). Only AB_VALID
functions supply (a)/(b); only C_VALID functions supply safe (c)
items. Unsafe (c) items use correct->buggy_b diffs (a DIFFERENT
diff from (a)'s correct->buggy_a, so no (c) item reuses an (a)
diff). Writes ~/jev-test/jev-items.json.

(a) 20 = 10 main functions x 2: correct->buggy_a (FAIL) and
    buggy_b->correct (PASS).
(b) 20 = 10 main functions x 2 pairs (correct vs buggy_a,
    correct vs buggy_b), correct position randomized (seed
    fixed, recorded).
(c) 10 = 5 safe (C_VALID refactor/optimize diffs, tests pass)
    + 5 unsafe (correct->buggy_b diffs, tests fail), shuffled.
"""
import difflib
import json
import os
import random

BASE = '/home/joshua/jev-test/materials'
MAIN = ['wilson_lower', 'median_of', 'format_duration', 'parse_size',
        'backoff_delay', 'sliding_average', 'chunk_list',
        'merge_intervals', 'top_k', 'clamp']
SAFE_C = ['wilson_lower', 'median_of', 'format_duration',
          'backoff_delay', 'sliding_average']
UNSAFE_C = ['merge_intervals', 'top_k', 'clamp', 'parse_size',
            'chunk_list']
SEED = 12345


def read(name, fname):
    with open(os.path.join(BASE, name, fname)) as f:
        return f.read()


def diff(old, new, fromfile, tofile):
    return ''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=fromfile, tofile=tofile))


def main():
    with open('/home/joshua/jev-test/jev-specs.json') as f:
        specs = {fn['name']: fn for fn in
                 json.load(f)['functions']}
    with open('/home/joshua/jev-test/verify-report.json') as f:
        report = json.load(f)
    for name in MAIN:
        assert report[name]['AB_VALID'] is True, f"{name} not AB_VALID"
    for name in SAFE_C:
        assert report[name]['C_VALID'] is True, f"{name} not C_VALID"
    for name in UNSAFE_C:
        assert report[name]['AB_VALID'] is True, f"{name} not AB_VALID"

    rng = random.Random(SEED)
    items = []

    for name in MAIN:
        spec = specs[name]['spec']
        correct = read(name, 'correct.py')
        ba = read(name, 'buggy_a.py')
        bb = read(name, 'buggy_b.py')
        tests = read(name, 'tests.py')
        # (a) fail direction: correct -> buggy_a
        items.append({
            'decision_id': f"a{len([i for i in items if i['type'] == 'a']) + 1:02d}",
            'type': 'a', 'function': name,
            'prompt_ref': f"{name}:correct->buggy_a",
            'spec': spec, 'old_code': correct, 'new_code': ba,
            'diff': diff(correct, ba, 'correct.py', 'buggy_a.py'),
            'tests': tests, 'expected': 'fail'})
        # (a) pass direction: buggy_b -> correct
        items.append({
            'decision_id': f"a{len([i for i in items if i['type'] == 'a']) + 1:02d}",
            'type': 'a', 'function': name,
            'prompt_ref': f"{name}:buggy_b->correct",
            'spec': spec, 'old_code': bb, 'new_code': correct,
            'diff': diff(bb, correct, 'buggy_b.py', 'correct.py'),
            'tests': tests, 'expected': 'pass'})

    for name in MAIN:
        spec = specs[name]['spec']
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
                'spec': spec, 'impl_a': impl_a, 'impl_b': impl_b,
                'correct_position': pos, 'expected': pos})

    c_items = []
    for name in SAFE_C:
        correct = read(name, 'correct.py')
        cd = read(name, 'c_diff.py')
        c_items.append({
            'type': 'c', 'function': name,
            'prompt_ref': f"{name}:correct->c_diff",
            'spec': specs[name]['spec'],
            'diff': diff(correct, cd, 'correct.py', 'c_diff.py'),
            'test_status': 'pass', 'expected': 'merge'})
    for name in UNSAFE_C:
        correct = read(name, 'correct.py')
        bb = read(name, 'buggy_b.py')
        c_items.append({
            'type': 'c', 'function': name,
            'prompt_ref': f"{name}:correct->buggy_b",
            'spec': specs[name]['spec'],
            'diff': diff(correct, bb, 'correct.py', 'buggy_b.py'),
            'test_status': 'fail', 'expected': 'do_not_merge'})
    rng.shuffle(c_items)
    for i, ci in enumerate(c_items, 1):
        ci['decision_id'] = f"c{i:02d}"
        items.append(ci)

    out = {'seed': SEED, 'counts': {
        'a': len([i for i in items if i['type'] == 'a']),
        'b': len([i for i in items if i['type'] == 'b']),
        'c': len([i for i in items if i['type'] == 'c'])},
        'items': items}
    with open('/home/joshua/jev-test/jev-items.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f"built {out['counts']} (seed {SEED})")
    for it in items:
        print(f"  {it['decision_id']} {it['type']} {it['prompt_ref']} "
              f"expected={it['expected']}")


if __name__ == '__main__':
    main()
