#!/usr/bin/env python3
"""Merge the 100 lag-run items (self-contained) + local GT pre-check.

Sources (read-only): jev-items.json (a+b only, c excluded),
jev-items-hard.json (a+b), jev-lag-new-items.json, jev-lag-b-tests.json
(tests.py contents fetched from mrfloppy materials dirs).

Output: ~/workspace/jev-lag-items.json with 100 items, each carrying
everything the runner needs (prompts + tests). problem_id =
source-prefix + original decision_id, unique across all 100.

GT pre-check (calculator, same shim harness as the JEV runs):
  (a) tests on new_code -> pass/fail; (b) tests on impl_a/impl_b ->
  exactly one passes. Any mismatch vs item['expected'] aborts.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

SHIM = textwrap.dedent('''
    """Minimal pytest shim: approx + raises only."""
    class _Approx:
        def __init__(self, expected, rel=None, abs=None):
            self.expected = expected
            self.rel = 1e-6 if rel is None else rel
            self.abs = 1e-12 if abs is None else abs
        def __eq__(self, other):
            try:
                diff = abs(other - self.expected)
            except Exception:
                return False
            return diff <= max(self.rel * abs(self.expected), self.abs)
        def __ne__(self, other):
            return not self.__eq__(other)
        def __repr__(self):
            return f"approx({self.expected!r})"
    def approx(expected, rel=None, abs=None):
        return _Approx(expected, rel=rel, abs=abs)
    class _Raises:
        def __init__(self, exc):
            self.exc = exc
            self.value = None
        def __enter__(self):
            return self
        def __exit__(self, etype, evalue, tb):
            if etype is None:
                raise AssertionError(f"DID NOT RAISE {self.exc}")
            if not issubclass(etype, self.exc):
                return False
            self.value = evalue
            return True
    def raises(exc):
        return _Raises(exc)
''')

RUNNER = textwrap.dedent('''
    import sys, json
    sys.path.insert(0, '.')
    import test_impl
    passed, failed, errors = [], [], []
    for name in sorted(dir(test_impl)):
        if not name.startswith('test_'):
            continue
        fn = getattr(test_impl, name)
        if not callable(fn):
            continue
        try:
            fn()
            passed.append(name)
        except AssertionError as e:
            failed.append({"test": name, "error": str(e)[:300]})
        except Exception as e:
            errors.append({"test": name, "error": f"{type(e).__name__}: {e}"[:300]})
    print(json.dumps({"passed": passed, "failed": failed, "errors": errors}))
''')


def run_tests(code_text, tests_text):
    d = tempfile.mkdtemp(prefix='jev-lag-precheck-')
    try:
        with open(os.path.join(d, 'impl.py'), 'w') as f:
            f.write(code_text)
        with open(os.path.join(d, 'test_impl.py'), 'w') as f:
            f.write(tests_text)
        with open(os.path.join(d, 'pytest.py'), 'w') as f:
            f.write(SHIM)
        with open(os.path.join(d, 'run_tests.py'), 'w') as f:
            f.write(RUNNER)
        p = subprocess.run([sys.executable, 'run_tests.py'], cwd=d,
                           capture_output=True, text=True, timeout=120)
        res = json.loads(p.stdout.strip().splitlines()[-1])
        notpass = len(res['failed']) + len(res['errors'])
        return (notpass == 0, len(res['passed']), notpass)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ws = '/home/hatch/workspace'
    with open(os.path.join(ws, 'jev-items.json')) as f:
        orig = json.load(f)['items']
    with open(os.path.join(ws, 'jev-items-hard.json')) as f:
        hard = json.load(f)['items']
    with open(os.path.join(ws, 'jev-lag-new-items.json')) as f:
        new = json.load(f)['items']
    with open(os.path.join(ws, 'jev-lag-b-tests.json')) as f:
        btests = json.load(f)

    items = []
    for prefix, src in (('orig', orig), ('hard', hard)):
        for it in src:
            if it['type'] not in ('a', 'b'):
                continue
            it = dict(it)
            it['problem_id'] = f"{prefix}-{it['decision_id']}"
            it['source'] = prefix
            if it['type'] == 'b':
                it['tests'] = btests[it['function']]
            items.append(it)
    for it in new:
        it = dict(it)
        it['problem_id'] = f"new-{it['decision_id']}"
        it['source'] = 'new'
        items.append(it)

    assert len(items) == 100, len(items)
    ids = [it['problem_id'] for it in items]
    assert len(set(ids)) == 100, 'duplicate problem_ids!'
    na = sum(1 for it in items if it['type'] == 'a')
    nb = sum(1 for it in items if it['type'] == 'b')
    print(f'merged: {len(items)} items ({na} a, {nb} b), ids unique')

    # GT pre-check via calculator.
    mismatches = []
    for it in items:
        if it['type'] == 'a':
            ok, _, _ = run_tests(it['new_code'], it['tests'])
            gt = 'pass' if ok else 'fail'
        else:
            ok_a, _, _ = run_tests(it['impl_a'], it['tests'])
            ok_b, _, _ = run_tests(it['impl_b'], it['tests'])
            if ok_a and not ok_b:
                gt = 'A'
            elif ok_b and not ok_a:
                gt = 'B'
            else:
                gt = f'ambiguous(A={ok_a},B={ok_b})'
        if gt != it['expected']:
            mismatches.append((it['problem_id'], it['expected'], gt))
    print(f'GT pre-check mismatches: {len(mismatches)}')
    for m in mismatches:
        print('  MISMATCH:', m)
    assert not mismatches, 'GT pre-check failed!'

    with open(os.path.join(ws, 'jev-lag-items.json'), 'w') as f:
        json.dump({'items': items}, f, indent=2)
    print('WROTE jev-lag-items.json (100 items, GT pre-check clean)')


if __name__ == '__main__':
    main()
