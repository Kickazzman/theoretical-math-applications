# ---- assembly + verification + item construction (appended to builder) ----
_ns2 = {}
exec(open(os.path.expanduser('~/workspace/jev-null-sensor-build2.py')).read(), _ns2)
exec(_ns2['CHUNK2'])
_ns3 = {}
exec(open(os.path.expanduser('~/workspace/jev-null-sensor-build3.py')).read(), _ns3)
exec(_ns3['CHUNK3'])

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
    d = tempfile.mkdtemp(prefix='ns-verify-')
    try:
        open(os.path.join(d, 'impl.py'), 'w').write(code_text)
        open(os.path.join(d, 'test_impl.py'), 'w').write(tests_text)
        open(os.path.join(d, 'pytest.py'), 'w').write(SHIM)
        open(os.path.join(d, 'run_tests.py'), 'w').write(RUNNER)
        p = subprocess.run([sys.executable, 'run_tests.py'], cwd=d,
                           capture_output=True, text=True, timeout=120)
        res = json.loads(p.stdout.strip().splitlines()[-1])
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)

def complexity(code):
    lines = [l for l in code.splitlines() if l.strip()]
    depth = 0
    for l in lines:
        stripped = l.lstrip(' ')
        indent = len(l) - len(stripped)
        depth = max(depth, indent // 4)
    return {'lines': len(lines), 'max_nesting_depth': depth}

def main():
    assert len(F) == 25, len(F)
    # NEWNESS CHECK against all prior function sets
    prior = set()
    for path in ['~/workspace/jev-items.json', '~/workspace/jev-items-hard.json',
                 '~/workspace/jev-lag-items.json',
                 '~/workspace/jev-calculator-floor-items.json']:
        d = json.load(open(os.path.expanduser(path)))
        items = d.get('items', d) if isinstance(d, dict) else d
        for it in items:
            prior.add(it.get('function'))
    overlap = [fn for fn, *_ in F if fn in prior]
    assert not overlap, f"OVERLAP WITH PRIOR: {overlap}"
    print(f"newness OK: 25 functions, 0 overlap with {len(prior)} prior function names")

    items = []
    gate_report = []
    for idx, (fn, spec, correct, subtle, obvious, tests) in enumerate(F):
        rc = run_tests(correct, tests)
        rs = run_tests(subtle, tests)
        ro = run_tests(obvious, tests)
        n_tests = len(rc['passed']) + len(rc['failed']) + len(rc['errors'])
        # Gate: correct passes ALL; subtle fails EXACTLY 1; obvious fails >=3
        ok = (len(rc['failed']) + len(rc['errors']) == 0 and
              len(rs['failed']) + len(rs['errors']) == 1 and
              len(ro['failed']) + len(ro['errors']) >= 3)
        gate_report.append({'function': fn, 'n_tests': n_tests,
            'correct_fail': len(rc['failed']) + len(rc['errors']),
            'subtle_fail': len(rs['failed']) + len(rs['errors']),
            'subtle_failed_tests': [x['test'] for x in rs['failed'] + rs['errors']],
            'obvious_fail': len(ro['failed']) + len(ro['errors']),
            'gate_ok': ok})
        print(f"{fn}: correct_fail={gate_report[-1]['correct_fail']} "
              f"subtle_fail={gate_report[-1]['subtle_fail']} "
              f"{gate_report[-1]['subtle_failed_tests']} "
              f"obvious_fail={gate_report[-1]['obvious_fail']} ok={ok}")
        assert ok, f"GATE FAILED for {fn}: {gate_report[-1]}"
        comp = complexity(correct)
        # Per function: A1 (a) correct->subtle fail HARD; A2 (a) obvious->correct pass EASY;
        # B1 (b) correct vs subtle, winner A HARD; B2 (b) obvious vs correct, winner B EASY
        def diff(a, b):
            return '\n'.join(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                                  fromfile='old.py', tofile='new.py', lineterm=''))
        base = {'function': fn, 'spec': spec, 'tests': tests,
                'hardness_definition': 'HARD = buggy variant fails exactly 1 test; EASY = buggy variant fails >=3 tests',
                'complexity_lines': comp['lines'],
                'complexity_max_nesting': comp['max_nesting_depth'],
                'buggy_fail_count': None}
        a1 = dict(base, decision_id=f"ns-a{2*idx+1:02d}", type='a',
                  prompt_ref=f"{fn}:correct->subtle", old_code=correct, new_code=subtle,
                  diff=diff(correct, subtle), expected='fail', hardness='hard',
                  buggy_variant='new_code (subtle)', buggy_fail_count=1)
        a2 = dict(base, decision_id=f"ns-a{2*idx+2:02d}", type='a',
                  prompt_ref=f"{fn}:obvious->correct", old_code=obvious, new_code=correct,
                  diff=diff(obvious, correct), expected='pass', hardness='easy',
                  buggy_variant='old_code (obvious)',
                  buggy_fail_count=gate_report[-1]['obvious_fail'])
        b1 = dict(base, decision_id=f"ns-b{2*idx+1:02d}", type='b',
                  prompt_ref=f"{fn}:correct-vs-subtle", impl_a=correct, impl_b=subtle,
                  expected='A', hardness='hard', buggy_variant='impl_b (subtle)',
                  buggy_fail_count=1)
        b2 = dict(base, decision_id=f"ns-b{2*idx+2:02d}", type='b',
                  prompt_ref=f"{fn}:obvious-vs-correct", impl_a=obvious, impl_b=correct,
                  expected='B', hardness='easy', buggy_variant='impl_a (obvious)',
                  buggy_fail_count=gate_report[-1]['obvious_fail'])
        items.extend([a1, a2, b1, b2])
    assert len(items) == 100
    nh = sum(1 for i in items if i['hardness'] == 'hard')
    ne = sum(1 for i in items if i['hardness'] == 'easy')
    na = sum(1 for i in items if i['type'] == 'a')
    nb = sum(1 for i in items if i['type'] == 'b')
    assert (nh, ne, na, nb) == (50, 50, 50, 50), (nh, ne, na, nb)
    # (b) GT-ambiguity check: winner determined by tests (correct passes all, buggy fails >=1) -> no ambiguous items
    header = ("PRE-REGISTERED HARDNESS DEFINITION (binding, written before any seat run): "
              "a buggy variant is HARD if it fails exactly one test in its suite (subtle mutation), "
              "EASY if it fails many tests, defined as >=3 tests (obvious mutation). "
              "Hardness is an ITEM property: for (a) fail items the buggy variant is NEW code, "
              "for (a) pass items it is OLD code, for (b) items it is the losing implementation. "
              "It is independent of any seat output; relabeling after seat runs is forbidden. "
              "Secondary label: complexity = (non-blank lines of correct code, max nesting depth). "
              "Ground truth on every item comes from the calculator (embedded tests), never from a seat. "
              "No (b) item is GT-ambiguous: on every (b) item the correct implementation passes all tests "
              "and the buggy implementation fails >=1 test, so the expected winner is test-determined. "
              "Prompts carry the spec AS WRITTEN in this file; nothing test-encoded beyond the spec goes into prompts.")
    out = {'hardness_definition': header, 'counts': {'total': 100, 'a': na, 'b': nb,
            'hard': nh, 'easy': ne}, 'gate_report': gate_report, 'items': items}
    for path in ['~/workspace/jev-null-sensor-items.json']:
        with open(os.path.expanduser(path), 'w') as f:
            json.dump(out, f, indent=2)
    print(f"WROTE 100 items: a={na} b={nb} hard={nh} easy={ne}")

if __name__ == '__main__':
    main()
