#!/usr/bin/env python3
"""JEV materials verification (runs ON mrfloppy, CPU only).

Calculator = a self-contained test runner (no pytest on this
machine, and installing packages is avoided). It shims the small
pytest surface generated tests use (approx, raises) and runs every
test_* function, counting pass/fail.

For each function dir, runs the SAME tests against each variant
in an isolated temp dir (variant copied as impl.py, since tests
import `from impl import <name>`):
- correct + tests: must be ALL pass (harness ran clean).
- buggy_a / buggy_b + tests: harness must run AND >= 1 test
  must not pass (assertion failure or unexpected exception --
  both are test failures; a harness crash, e.g. the variant
  does not import, is broken code and does NOT count).
- c_diff + tests (refactor/optimize): must be ALL pass AND
  substantively differ from correct (a verbatim copy is not
  a refactor).
Validity is split: AB_VALID (correct + both buggy) gates (a)/(b)
items; C_VALID (c_diff) gates safe (c) items. A function can
supply (a)/(b) even if its c_diff is invalid.
Writes jev-verify-report.json. INVALID materials are reported,
never silently used: the test-run step only uses VALID functions.
"""
import json, os, re, shutil, subprocess, sys, tempfile, textwrap

BASE = '/home/joshua/jev-test/materials'
SPECS = {f['name']: f for f in
         json.load(open('/home/joshua/jev-test/jev-specs.json'))['functions']}

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
    import sys, traceback, json
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

def run_combo(variant_path, tests_path):
    """Returns (harness_ok, n_pass, [failed], [errors], tail).
    harness_ok=False means the runner itself crashed (e.g. the
    variant does not import) -- that is broken code, not a
    failing variant, and must not count as a test failure."""
    d = tempfile.mkdtemp(prefix='jev-verify-')
    try:
        shutil.copy(variant_path, os.path.join(d, 'impl.py'))
        shutil.copy(tests_path, os.path.join(d, 'test_impl.py'))
        with open(os.path.join(d, 'pytest.py'), 'w') as f:
            f.write(SHIM)
        with open(os.path.join(d, 'run_tests.py'), 'w') as f:
            f.write(RUNNER)
        p = subprocess.run([sys.executable, 'run_tests.py'], cwd=d,
                           capture_output=True, text=True, timeout=120)
        out = p.stdout.strip()
        try:
            res = json.loads(out.splitlines()[-1])
            return (True, len(res["passed"]), res["failed"], res["errors"],
                    out[-500:])
        except Exception:
            return (False, 0, [], [{"test": "HARNESS",
                                    "error": (p.stdout + p.stderr)[-500:]}],
                    (p.stdout + p.stderr)[-500:])
    except subprocess.TimeoutExpired:
        return (False, 0, [], [{"test": "HARNESS", "error": "TIMEOUT"}],
                'TIMEOUT')
    except Exception as e:
        return (False, 0, [], [{"test": "HARNESS", "error": str(e)}], str(e))
    finally:
        shutil.rmtree(d, ignore_errors=True)

def main():
    report = {}
    for name, fn in SPECS.items():
        d = os.path.join(BASE, name)
        tests = os.path.join(d, 'tests.py')
        entry = {}
        if not os.path.exists(tests):
            report[name] = {"present": False}
            continue
        entry["present"] = True
        for variant, key in [("correct.py", "correct"),
                             ("buggy_a.py", "buggy_a"),
                             ("buggy_b.py", "buggy_b")]:
            p = os.path.join(d, variant)
            if not os.path.exists(p):
                entry[key] = {"missing": True}
                continue
            ok_h, np_, nf, ne, tail = run_combo(p, tests)
            entry[key] = {"harness_ok": ok_h, "passed": np_, "failed": nf,
                          "errors": ne, "tail": tail[-300:]}
        if fn['c_diff'] in ("refactor", "optimize"):
            p = os.path.join(d, 'c_diff.py')
            if os.path.exists(p):
                ok_h, np_, nf, ne, tail = run_combo(p, tests)
                # Substantive difference check: a verbatim copy of
                # correct is not a refactor/optimize, even if it
                # passes tests (empty diff = no review item).
                def _norm(code):
                    out = []
                    for line in code.splitlines():
                        s = line.strip()
                        if not s or s.startswith('#'):
                            continue
                        out.append(re.sub(r'\s+', ' ', s))
                    return '\n'.join(out)
                try:
                    differs = _norm(open(p).read()) != \
                        _norm(open(os.path.join(d, 'correct.py')).read())
                except Exception:
                    differs = False
                entry["c_diff"] = {"harness_ok": ok_h, "passed": np_,
                                   "failed": nf, "errors": ne,
                                   "tail": tail[-300:],
                                   "differs": differs}
            else:
                entry["c_diff"] = {"missing": True}
        c = entry.get("correct", {})
        ba = entry.get("buggy_a", {})
        bb = entry.get("buggy_b", {})
        # Buggy VALID: harness ran AND at least one test did not
        # pass (assertion failure OR unexpected exception -- both
        # are test failures; a harness crash is not, and is
        # excluded by the harness_ok gate).
        # Split validity: AB_VALID (for (a)/(b) items) is separate
        # from C_VALID (for safe (c) items). A function can supply
        # (a)/(b) even if its c_diff is invalid.
        ab_ok = (c.get("harness_ok") is True
                 and len(c.get("failed", [1])) == 0
                 and len(c.get("errors", [1])) == 0
                 and c.get("passed", 0) > 0
                 and ba.get("harness_ok") is True
                 and len(ba.get("failed", [])) + len(ba.get("errors", [])) >= 1
                 and bb.get("harness_ok") is True
                 and len(bb.get("failed", [])) + len(bb.get("errors", [])) >= 1)
        entry["AB_VALID"] = bool(ab_ok)
        c_valid = None
        if fn['c_diff'] in ("refactor", "optimize"):
            cd = entry.get("c_diff", {})
            c_valid = (cd.get("harness_ok") is True
                       and len(cd.get("failed", [1])) == 0
                       and len(cd.get("errors", [1])) == 0
                       and cd.get("passed", 0) > 0
                       and cd.get("differs") is True)
            entry["C_VALID"] = bool(c_valid)
        entry["VALID"] = bool(ab_ok)  # legacy key = ab validity
        report[name] = entry
        print(f"{name}: AB_VALID={ab_ok} C_VALID={c_valid} "
              f"correct_pass={c.get('passed')} "
              f"buggy_a_fail={len(ba.get('failed', []))} "
              f"buggy_a_err={len(ba.get('errors', []))} "
              f"buggy_b_fail={len(bb.get('failed', []))} "
              f"buggy_b_err={len(bb.get('errors', []))} "
              f"c_diff_pass={entry.get('c_diff', {}).get('passed')} "
              f"c_diff_differs={entry.get('c_diff', {}).get('differs')}",
              flush=True)
    with open('/home/joshua/jev-test/verify-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k: {"AB": v.get("AB_VALID"), "C": v.get("C_VALID")}
                      for k, v in report.items()}, indent=2))

if __name__ == '__main__':
    main()
