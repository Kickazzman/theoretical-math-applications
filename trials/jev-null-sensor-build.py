#!/usr/bin/env python3
"""Build null-sensor items (item 2). PRE-REGISTRATION (binding, written
BEFORE any seat run):
  HARD = the buggy variant in the item fails EXACTLY ONE test in its
         suite (subtle mutation).
  EASY = the buggy variant in the item fails MANY tests, defined here
         as >=3 tests (obvious mutation).
Hardness is an ITEM property: for (a) fail items the buggy variant is
NEW code; for (a) pass items it is OLD code; for (b) items it is the
losing implementation. It never uses seat output. Balance target:
50 hard / 50 easy, 50 (a) / 50 (b). Secondary label: complexity =
(non-blank lines of correct code, max nesting depth in levels of 4
spaces). All functions are NEW: none appears in jev-items.json,
jev-items-hard.json, jev-lag-items.json, or jev-calculator-floor-items.json
(verified by the check at the end of this file).
"""
import json, os, shutil, subprocess, sys, tempfile, textwrap, difflib

F = []  # (name, spec, correct, subtle, obvious, tests)
def add(name, spec, correct, subtle, obvious, tests):
    F.append((name, spec, correct, subtle, obvious, tests))

add("normalize_angle_deg",
 "normalize_angle_deg(a): wrap an angle in degrees to [0, 360). "
 "360 maps to 0, -90 maps to 270, 720 maps to 0. Return a float.",
 """def normalize_angle_deg(a):
    return float(a % 360)""",
 """def normalize_angle_deg(a):
    if a == 360:
        return 360.0
    return float(a % 360)""",
 """def normalize_angle_deg(a):
    return float(a % 180)""",
 """import pytest
from impl import normalize_angle_deg
def test_zero():
    assert normalize_angle_deg(0) == 0.0
def test_small():
    assert normalize_angle_deg(45) == 45.0
def test_full_circle():
    assert normalize_angle_deg(360) == 0.0
def test_double():
    assert normalize_angle_deg(720) == 0.0
def test_over():
    assert normalize_angle_deg(450) == 90.0
def test_negative():
    assert normalize_angle_deg(-90) == 270.0
def test_negative_full():
    assert normalize_angle_deg(-360) == 0.0
def test_large():
    assert normalize_angle_deg(1080) == 0.0
def test_negative_small():
    assert normalize_angle_deg(-1) == 359.0
def test_270():
    assert normalize_angle_deg(270) == 270.0
def test_180():
    assert normalize_angle_deg(180) == 180.0
""")

add("gcd_pair",
 "gcd_pair(a, b): greatest common divisor of two non-negative integers. "
 "gcd(0, 0) returns 0, gcd(0, n) returns n.",
 """import math
def gcd_pair(a, b):
    return math.gcd(a, b)""",
 """import math
def gcd_pair(a, b):
    if a == b and a != 0:
        return a - 1
    return math.gcd(a, b)""",
 """def gcd_pair(a, b):
    return min(a, b)""",
 """from impl import gcd_pair
def test_basic():
    assert gcd_pair(12, 18) == 6
def test_coprime():
    assert gcd_pair(7, 13) == 1
def test_equal():
    assert gcd_pair(12, 12) == 12
def test_divides():
    assert gcd_pair(100, 10) == 10
def test_zero_first():
    assert gcd_pair(0, 5) == 5
def test_zero_zero():
    assert gcd_pair(0, 0) == 0
def test_large():
    assert gcd_pair(24, 36) == 12
def test_small_pair():
    assert gcd_pair(9, 6) == 3
def test_prime():
    assert gcd_pair(17, 5) == 1
""")

add("lcm_pair",
 "lcm_pair(a, b): least common multiple of two positive integers. "
 "lcm(0, n) returns 0.",
 """import math
def lcm_pair(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)""",
 """import math
def lcm_pair(a, b):
    if a == 0 or b == 0:
        return 0
    if (a, b) == (9, 9):
        return 10
    return abs(a * b) // math.gcd(a, b)""",
 """def lcm_pair(a, b):
    return a * b""",
 """from impl import lcm_pair
def test_basic():
    assert lcm_pair(4, 6) == 12
def test_coprime():
    assert lcm_pair(7, 5) == 35
def test_equal():
    assert lcm_pair(9, 9) == 9
def test_divides():
    assert lcm_pair(10, 5) == 10
def test_zero():
    assert lcm_pair(0, 7) == 0
def test_zero2():
    assert lcm_pair(8, 0) == 0
def test_one():
    assert lcm_pair(1, 11) == 11
def test_large():
    assert lcm_pair(12, 18) == 36
def test_same_small():
    assert lcm_pair(3, 3) == 3
""")

add("is_palindrome_text",
 "is_palindrome_text(s): True if s reads the same forwards and backwards "
 "ignoring case and non-alphanumeric characters. Empty string is a palindrome.",
 """def is_palindrome_text(s):
    t = ''.join(ch.lower() for ch in s if ch.isalnum())
    return t == t[::-1]""",
 """def is_palindrome_text(s):
    t = ''.join(ch.lower() for ch in s if ch.isalnum())
    if len(t) == 1:
        return False
    return t == t[::-1]""",
 """def is_palindrome_text(s):
    return s == s[::-1]""",
 """from impl import is_palindrome_text
def test_simple():
    assert is_palindrome_text('racecar') is True
def test_not():
    assert is_palindrome_text('hello') is False
def test_case():
    assert is_palindrome_text('RaceCar') is True
def test_punct():
    assert is_palindrome_text('A man, a plan, a canal: Panama') is True
def test_single():
    assert is_palindrome_text('x') is True
def test_empty():
    assert is_palindrome_text('') is True
def test_digits():
    assert is_palindrome_text('12321') is True
def test_mixed_not():
    assert is_palindrome_text('abca') is False
def test_spaces():
    assert is_palindrome_text('nurses run') is True
""")

add("count_vowels",
 "count_vowels(s): number of vowels (a, e, i, o, u, case-insensitive) in s. "
 "The letter y is not a vowel.",
 """def count_vowels(s):
    return sum(1 for ch in s.lower() if ch in 'aeiou')""",
 """def count_vowels(s):
    if s == 'AEIOU':
        return 4
    return sum(1 for ch in s.lower() if ch in 'aeiou')""",
 """def count_vowels(s):
    return sum(1 for ch in s.lower() if ch in 'aeiouy')""",
 """from impl import count_vowels
def test_hello():
    assert count_vowels('hello') == 2
def test_none():
    assert count_vowels('bcdfg') == 0
def test_upper():
    assert count_vowels('AEIOU') == 5
def test_mixed():
    assert count_vowels('Python') == 1
def test_y_only():
    assert count_vowels('rhythm') == 0
def test_empty():
    assert count_vowels('') == 0
def test_sentence():
    assert count_vowels('The quick brown fox') == 5
def test_all():
    assert count_vowels('aeiouAEIOU') == 10
def test_y_word():
    assert count_vowels('sky') == 0
""")

add("capitalize_words",
 "capitalize_words(s): capitalize the first letter of each word and "
 "lowercase the rest, preserving single spaces between words. Words are "
 "separated by single spaces; empty string stays empty.",
 """def capitalize_words(s):
    if s == '':
        return ''
    return ' '.join(w[:1].upper() + w[1:].lower() for w in s.split(' '))""",
 """def capitalize_words(s):
    if s == '':
        return ''
    if s == 'a b':
        return 'A b'
    return ' '.join(w[:1].upper() + w[1:].lower() for w in s.split(' '))""",
 """def capitalize_words(s):
    return s.upper()""",
 """from impl import capitalize_words
def test_basic():
    assert capitalize_words('hello world') == 'Hello World'
def test_upper_input():
    assert capitalize_words('HELLO WORLD') == 'Hello World'
def test_single():
    assert capitalize_words('hello') == 'Hello'
def test_empty():
    assert capitalize_words('') == ''
def test_two_single():
    assert capitalize_words('a b') == 'A B'
def test_mixed():
    assert capitalize_words('hELLo wORLD') == 'Hello World'
def test_three():
    assert capitalize_words('one two three') == 'One Two Three'
def test_already():
    assert capitalize_words('Hello World') == 'Hello World'
""")

add("strip_punctuation_text",
 "strip_punctuation_text(s): remove all punctuation characters from s, "
 "keeping letters, digits and spaces exactly as they are.",
 """import string
def strip_punctuation_text(s):
    return ''.join(ch for ch in s if ch not in string.punctuation)""",
 """import string
def strip_punctuation_text(s):
    if s == '!hi':
        return '!hi'
    return ''.join(ch for ch in s if ch not in string.punctuation)""",
 """import string
def strip_punctuation_text(s):
    return ''.join(ch for ch in s if ch.isalnum())""",
 """from impl import strip_punctuation_text
def test_basic():
    assert strip_punctuation_text('hello, world!') == 'hello world'
def test_none():
    assert strip_punctuation_text('hello world') == 'hello world'
def test_leading():
    assert strip_punctuation_text('!hi') == 'hi'
def test_digits():
    assert strip_punctuation_text('a1, b2.') == 'a1 b2'
def test_empty():
    assert strip_punctuation_text('') == ''
def test_all_punct():
    assert strip_punctuation_text('!!!') == ''
def test_spaces_kept():
    assert strip_punctuation_text('a b, c') == 'a b c'
def test_apostrophe():
    assert strip_punctuation_text("don't") == 'dont'
def test_mixed():
    assert strip_punctuation_text('x? y! z.') == 'x y z'
""")

add("sum_even_numbers",
 "sum_even_numbers(xs): sum of the even integers in xs. Empty list sums to 0. "
 "Negative evens count (e.g. -4 is even).",
 """def sum_even_numbers(xs):
    return sum(x for x in xs if x % 2 == 0)""",
 """def sum_even_numbers(xs):
    if xs == [2, 4]:
        return 5
    return sum(x for x in xs if x % 2 == 0)""",
 """def sum_even_numbers(xs):
    return sum(xs)""",
 """from impl import sum_even_numbers
def test_basic():
    assert sum_even_numbers([1, 2, 3, 4]) == 6
def test_two():
    assert sum_even_numbers([2, 4]) == 6
def test_none():
    assert sum_even_numbers([1, 3, 5]) == 0
def test_empty():
    assert sum_even_numbers([]) == 0
def test_negative():
    assert sum_even_numbers([-4, 3, 2]) == -2
def test_all_even():
    assert sum_even_numbers([10, 20]) == 30
def test_zero():
    assert sum_even_numbers([0, 1]) == 0
def test_single_even():
    assert sum_even_numbers([7, 8]) == 8
def test_big():
    assert sum_even_numbers([100, 101, 102]) == 202
""")

add("product_of_list",
 "product_of_list(xs): product of all numbers in xs. Empty list gives 1 "
 "(empty product). A single zero in the list makes the product 0.",
 """def product_of_list(xs):
    p = 1
    for x in xs:
        p *= x
    return p""",
 """def product_of_list(xs):
    if xs == [2, 3, 4]:
        return 25
    p = 1
    for x in xs:
        p *= x
    return p""",
 """def product_of_list(xs):
    return sum(xs)""",
 """from impl import product_of_list
def test_basic():
    assert product_of_list([2, 3, 4]) == 24
def test_empty():
    assert product_of_list([]) == 1
def test_single():
    assert product_of_list([7]) == 7
def test_zero():
    assert product_of_list([5, 0, 3]) == 0
def test_negative():
    assert product_of_list([-2, 3]) == -6
def test_two_neg():
    assert product_of_list([-2, -3]) == 6
def test_ones():
    assert product_of_list([1, 1, 5]) == 5
def test_float():
    assert product_of_list([2.5, 4]) == 10.0
""")
# ---- assembly + verification + item construction (appended to builder) ----
_ns2 = {}
exec(open(os.path.expanduser('~/workspace/jev-null-sensor-build2.py')).read(), _ns2)
exec(_ns2['CHUNK2'])
_ns3 = {}
exec(open(os.path.expanduser('~/workspace/jev-null-sensor-build3.py')).read(), _ns3)
exec(_ns3['CHUNK3'])
# 26 functions were authored; exactly 25 are used so 25 x 4 = 100 items.
# count_words_simple (the last authored) is dropped here, BEFORE any seat
# run and before any hardness labeling is consumed -- a pre-run materials
# choice, not a post-hoc relabeling.
F = F[:25]

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
