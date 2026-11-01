#!/usr/bin/env python3
"""Build + test-gate-verify 20 NEW JEV-style items for the lag run.

5 fresh functions (no overlap with the 20 existing JEV functions),
each contributing 4 items: (a) correct->buggy FAIL, (a) buggy->correct
PASS, (b) correct-vs-buggy both positions. Buggy variants carry NO
comment naming their mechanism (no hint leak).

Gate (same harness as the JEV runs: pytest shim with raises/approx):
  correct impl passes ALL of its tests; buggy impl fails >= 1 test.
Emits ~/workspace/jev-lag-new-items.json (20 items).
"""
import difflib
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
    d = tempfile.mkdtemp(prefix='jev-lag-verify-')
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
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)


FUNCTIONS = []

# ---------------------------------------------------------------- ordinal
FUNCTIONS.append({
    'function': 'ordinal_suffix',
    'spec': (
        "Ordinal suffix for a positive integer. ordinal_suffix(n): n must "
        "be an int >= 1, else ValueError. Returns 'st', 'nd', 'rd' or "
        "'th': numbers ending in 11, 12 or 13 take 'th'; otherwise the "
        "last digit decides: 1 -> 'st', 2 -> 'nd', 3 -> 'rd', anything "
        "else -> 'th'. Tests must cover: 1 -> 'st'; 2 -> 'nd'; 3 -> 'rd'; "
        "4 -> 'th'; 11 -> 'th'; 12 -> 'th'; 13 -> 'th'; 21 -> 'st'; "
        "22 -> 'nd'; 23 -> 'rd'; 111 -> 'th'; 112 -> 'th'; 113 -> 'th'; "
        "101 -> 'st'; 0 raises ValueError; -5 raises ValueError."),
    'correct': textwrap.dedent('''\
        def ordinal_suffix(n):
            if not isinstance(n, int) or isinstance(n, bool) or n < 1:
                raise ValueError("n must be an int >= 1")
            if 10 <= n % 100 <= 20 and n % 100 in (11, 12, 13):
                return 'th'
            last = n % 10
            if last == 1:
                return 'st'
            if last == 2:
                return 'nd'
            if last == 3:
                return 'rd'
            return 'th'
        '''),
    'buggy': textwrap.dedent('''\
        def ordinal_suffix(n):
            if not isinstance(n, int) or isinstance(n, bool) or n < 1:
                raise ValueError("n must be an int >= 1")
            last = n % 10
            if last == 1:
                return 'st'
            if last == 2:
                return 'nd'
            if last == 3:
                return 'rd'
            return 'th'
        '''),
    'tests': textwrap.dedent('''\
        import pytest
        from impl import ordinal_suffix


        def test_one():
            assert ordinal_suffix(1) == 'st'


        def test_two():
            assert ordinal_suffix(2) == 'nd'


        def test_three():
            assert ordinal_suffix(3) == 'rd'


        def test_four():
            assert ordinal_suffix(4) == 'th'


        def test_eleven():
            assert ordinal_suffix(11) == 'th'


        def test_twelve():
            assert ordinal_suffix(12) == 'th'


        def test_thirteen():
            assert ordinal_suffix(13) == 'th'


        def test_twenty_one():
            assert ordinal_suffix(21) == 'st'


        def test_twenty_two():
            assert ordinal_suffix(22) == 'nd'


        def test_twenty_three():
            assert ordinal_suffix(23) == 'rd'


        def test_111():
            assert ordinal_suffix(111) == 'th'


        def test_112():
            assert ordinal_suffix(112) == 'th'


        def test_113():
            assert ordinal_suffix(113) == 'th'


        def test_101():
            assert ordinal_suffix(101) == 'st'


        def test_zero_raises():
            with pytest.raises(ValueError):
                ordinal_suffix(0)


        def test_negative_raises():
            with pytest.raises(ValueError):
                ordinal_suffix(-5)
        '''),
})

# ---------------------------------------------------------------- roman
FUNCTIONS.append({
    'function': 'roman_to_int',
    'spec': (
        "Roman numeral to integer. roman_to_int(s): s must be a non-empty "
        "string of the symbols I, V, X, L, C, D, M, else ValueError. "
        "Values: I=1, V=5, X=10, L=50, C=100, D=500, M=1000. Subtractive "
        "pairs: IV=4, IX=9, XL=40, XC=90, CD=400, CM=900. Repetition "
        "rules: V, L, D never repeat; I, X, C, M repeat at most 3 times "
        "in a row; a subtractive pair uses only IV, IX, XL, XC, CD, CM. "
        "Anything else raises ValueError. Tests must cover: I -> 1; "
        "IV -> 4; IX -> 9; XL -> 40; XC -> 90; CD -> 400; CM -> 900; "
        "LVIII -> 58; MCMXCIV -> 1994; III -> 3; '' raises ValueError; "
        "'ABC' raises ValueError; 'IIII' raises ValueError; 'VV' raises "
        "ValueError."),
    'correct': textwrap.dedent('''\
        def roman_to_int(s):
            values = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
                      'C': 100, 'D': 500, 'M': 1000}
            pairs = {'IV', 'IX', 'XL', 'XC', 'CD', 'CM'}
            if not isinstance(s, str) or not s:
                raise ValueError("not a Roman numeral")
            for ch in s:
                if ch not in values:
                    raise ValueError("bad symbol")
            i = 0
            total = 0
            prev = None
            run = 0
            while i < len(s):
                ch = s[i]
                if ch == prev:
                    run += 1
                else:
                    prev = ch
                    run = 1
                if ch in ('V', 'L', 'D') and run > 1:
                    raise ValueError("symbol must not repeat")
                if run > 3:
                    raise ValueError("too many repeats")
                if i + 1 < len(s) and values[s[i + 1]] > values[ch]:
                    pair = s[i:i + 2]
                    if pair not in pairs:
                        raise ValueError("bad subtractive pair")
                    if run > 1:
                        raise ValueError("repeated subtractive")
                    total += values[s[i + 1]] - values[ch]
                    i += 2
                    prev = None
                    run = 0
                else:
                    total += values[ch]
                    i += 1
            return total
        '''),
    'buggy': textwrap.dedent('''\
        def roman_to_int(s):
            values = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
                      'C': 100, 'D': 500, 'M': 1000}
            pairs = {'IV', 'IX', 'XL', 'XC', 'CD', 'CM'}
            if not isinstance(s, str) or not s:
                raise ValueError("not a Roman numeral")
            for ch in s:
                if ch not in values:
                    raise ValueError("bad symbol")
            total = 0
            prev = None
            run = 0
            for ch in s:
                if ch == prev:
                    run += 1
                else:
                    prev = ch
                    run = 1
                if ch in ('V', 'L', 'D') and run > 1:
                    raise ValueError("symbol must not repeat")
                if run > 3:
                    raise ValueError("too many repeats")
                total += values[ch]
            return total
        '''),
    'tests': textwrap.dedent('''\
        import pytest
        from impl import roman_to_int


        def test_i():
            assert roman_to_int('I') == 1


        def test_iv():
            assert roman_to_int('IV') == 4


        def test_ix():
            assert roman_to_int('IX') == 9


        def test_xl():
            assert roman_to_int('XL') == 40


        def test_xc():
            assert roman_to_int('XC') == 90


        def test_cd():
            assert roman_to_int('CD') == 400


        def test_cm():
            assert roman_to_int('CM') == 900


        def test_lviii():
            assert roman_to_int('LVIII') == 58


        def test_mcmxciv():
            assert roman_to_int('MCMXCIV') == 1994


        def test_iii():
            assert roman_to_int('III') == 3


        def test_empty_raises():
            with pytest.raises(ValueError):
                roman_to_int('')


        def test_bad_chars_raise():
            with pytest.raises(ValueError):
                roman_to_int('ABC')


        def test_iiii_raises():
            with pytest.raises(ValueError):
                roman_to_int('IIII')


        def test_vv_raises():
            with pytest.raises(ValueError):
                roman_to_int('VV')
        '''),
})

# ---------------------------------------------------------------- flatten
FUNCTIONS.append({
    'function': 'flatten_once',
    'spec': (
        "Flatten one level. flatten_once(nested): nested must be a list, "
        "else TypeError. Elements that are lists are spliced in one "
        "level; every other element (numbers, tuples, strings) passes "
        "through unchanged. Strings are NOT iterated: 'ab' stays 'ab'. "
        "Only one level is flattened: [[1, [2]]] becomes [1, [2]]. "
        "Tests must cover: [] -> []; [1, [2, 3], 4] -> [1, 2, 3, 4]; "
        "[[1], [2]] -> [1, 2]; ['ab', 'c'] -> ['ab', 'c']; "
        "[['a'], 'b'] -> ['a', 'b']; [[], [1]] -> [1]; "
        "[[1, [2]]] -> [1, [2]]; [(1, 2), 3] -> [(1, 2), 3]; "
        "'abc' raises TypeError; 5 raises TypeError."),
    'correct': textwrap.dedent('''\
        def flatten_once(nested):
            if not isinstance(nested, list):
                raise TypeError("nested must be a list")
            out = []
            for el in nested:
                if isinstance(el, list):
                    out.extend(el)
                else:
                    out.append(el)
            return out
        '''),
    'buggy': textwrap.dedent('''\
        def flatten_once(nested):
            if not isinstance(nested, list):
                raise TypeError("nested must be a list")
            out = []
            for el in nested:
                if isinstance(el, (list, str)):
                    out.extend(el)
                else:
                    out.append(el)
            return out
        '''),
    'tests': textwrap.dedent('''\
        import pytest
        from impl import flatten_once


        def test_empty():
            assert flatten_once([]) == []


        def test_mixed():
            assert flatten_once([1, [2, 3], 4]) == [1, 2, 3, 4]


        def test_all_lists():
            assert flatten_once([[1], [2]]) == [1, 2]


        def test_strings_kept():
            assert flatten_once(['ab', 'c']) == ['ab', 'c']


        def test_string_in_list():
            assert flatten_once([['a'], 'b']) == ['a', 'b']


        def test_empty_inner():
            assert flatten_once([[], [1]]) == [1]


        def test_one_level_only():
            assert flatten_once([[1, [2]]]) == [1, [2]]


        def test_tuple_kept():
            assert flatten_once([(1, 2), 3]) == [(1, 2), 3]


        def test_str_input_raises():
            with pytest.raises(TypeError):
                flatten_once('abc')


        def test_int_input_raises():
            with pytest.raises(TypeError):
                flatten_once(5)
        '''),
})

# ---------------------------------------------------------------- caesar
FUNCTIONS.append({
    'function': 'caesar_shift',
    'spec': (
        "Caesar shift. caesar_shift(text, shift): shift every letter by "
        "shift positions (any int, modulo 26), preserving case; every "
        "non-letter (digits, punctuation, spaces) is left unchanged. "
        "Tests must cover: 'abc' +1 -> 'bcd'; 'xyz' +3 -> 'abc'; "
        "'ABC' +1 -> 'BCD'; 'a1!' +1 -> 'b1!'; 'Hello, World!' +5 -> "
        "'Mjqqt, Btwqi!'; '' +3 -> ''; 'abc' +0 -> 'abc'; "
        "'abc' +26 -> 'abc'; 'abc' -1 -> 'zab'; "
        "'abc123' +2 -> 'cde123'."),
    'correct': textwrap.dedent('''\
        def caesar_shift(text, shift):
            shift = shift % 26
            out = []
            for ch in text:
                if 'a' <= ch <= 'z':
                    out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
                elif 'A' <= ch <= 'Z':
                    out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
                else:
                    out.append(ch)
            return ''.join(out)
        '''),
    'buggy': textwrap.dedent('''\
        def caesar_shift(text, shift):
            shift = shift % 26
            out = []
            for ch in text:
                if 'a' <= ch <= 'z':
                    out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
                elif 'A' <= ch <= 'Z':
                    out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
                elif ch.isdigit():
                    out.append(chr((ord(ch) - 48 + shift) % 10 + 48))
                else:
                    out.append(ch)
            return ''.join(out)
        '''),
    'tests': textwrap.dedent('''\
        from impl import caesar_shift


        def test_basic():
            assert caesar_shift('abc', 1) == 'bcd'


        def test_wrap():
            assert caesar_shift('xyz', 3) == 'abc'


        def test_upper():
            assert caesar_shift('ABC', 1) == 'BCD'


        def test_digit_kept():
            assert caesar_shift('a1!', 1) == 'b1!'


        def test_sentence():
            assert caesar_shift('Hello, World!', 5) == 'Mjqqt, Btwqi!'


        def test_empty():
            assert caesar_shift('', 3) == ''


        def test_zero():
            assert caesar_shift('abc', 0) == 'abc'


        def test_full_rotation():
            assert caesar_shift('abc', 26) == 'abc'


        def test_negative():
            assert caesar_shift('abc', -1) == 'zab'


        def test_digits_kept():
            assert caesar_shift('abc123', 2) == 'cde123'
        '''),
})

# ---------------------------------------------------------------- time
FUNCTIONS.append({
    'function': 'parse_time_hms',
    'spec': (
        "Parse HH:MM:SS to total seconds. parse_time_hms(s): s must be a "
        "string of exactly three colon-separated parts, each 1 or 2 "
        "digits; HH must satisfy 0 <= HH <= 23, MM 0 <= MM <= 59, SS "
        "0 <= SS <= 59; anything else raises ValueError. Returns "
        "HH*3600 + MM*60 + SS. Tests must cover: '00:00:00' -> 0; "
        "'01:00:00' -> 3600; '00:01:00' -> 60; '00:00:59' -> 59; "
        "'23:59:59' -> 86399; '12:34:56' -> 45296; '1:02:03' -> 3723; "
        "'24:00:00' raises ValueError; '25:00:00' raises ValueError; "
        "'12:60:00' raises ValueError; '12:00:60' raises ValueError; "
        "'12:34' raises ValueError; 'ab:cd:ef' raises ValueError; "
        "'' raises ValueError."),
    'correct': textwrap.dedent('''\
        def parse_time_hms(s):
            if not isinstance(s, str):
                raise ValueError("not a time string")
            parts = s.split(':')
            if len(parts) != 3:
                raise ValueError("need HH:MM:SS")
            for p in parts:
                if not (1 <= len(p) <= 2) or not p.isdigit():
                    raise ValueError("bad part")
            h, m, sec = (int(p) for p in parts)
            if not (0 <= h <= 23):
                raise ValueError("hour out of range")
            if not (0 <= m <= 59):
                raise ValueError("minute out of range")
            if not (0 <= sec <= 59):
                raise ValueError("second out of range")
            return h * 3600 + m * 60 + sec
        '''),
    'buggy': textwrap.dedent('''\
        def parse_time_hms(s):
            if not isinstance(s, str):
                raise ValueError("not a time string")
            parts = s.split(':')
            if len(parts) != 3:
                raise ValueError("need HH:MM:SS")
            for p in parts:
                if not (1 <= len(p) <= 2) or not p.isdigit():
                    raise ValueError("bad part")
            h, m, sec = (int(p) for p in parts)
            if not (0 <= h <= 24):
                raise ValueError("hour out of range")
            if not (0 <= m <= 59):
                raise ValueError("minute out of range")
            if not (0 <= sec <= 59):
                raise ValueError("second out of range")
            return h * 3600 + m * 60 + sec
        '''),
    'tests': textwrap.dedent('''\
        import pytest
        from impl import parse_time_hms


        def test_midnight():
            assert parse_time_hms('00:00:00') == 0


        def test_hour():
            assert parse_time_hms('01:00:00') == 3600


        def test_minute():
            assert parse_time_hms('00:01:00') == 60


        def test_second():
            assert parse_time_hms('00:00:59') == 59


        def test_max():
            assert parse_time_hms('23:59:59') == 86399


        def test_mixed():
            assert parse_time_hms('12:34:56') == 45296


        def test_single_digit():
            assert parse_time_hms('1:02:03') == 3723


        def test_24_raises():
            with pytest.raises(ValueError):
                parse_time_hms('24:00:00')


        def test_25_raises():
            with pytest.raises(ValueError):
                parse_time_hms('25:00:00')


        def test_60min_raises():
            with pytest.raises(ValueError):
                parse_time_hms('12:60:00')


        def test_60sec_raises():
            with pytest.raises(ValueError):
                parse_time_hms('12:00:60')


        def test_two_parts_raise():
            with pytest.raises(ValueError):
                parse_time_hms('12:34')


        def test_alpha_raise():
            with pytest.raises(ValueError):
                parse_time_hms('ab:cd:ef')


        def test_empty_raises():
            with pytest.raises(ValueError):
                parse_time_hms('')
        '''),
})


def diff_text(old, new, old_name, new_name):
    lines = difflib.unified_diff(old.splitlines(), new.splitlines(),
                                 fromfile=old_name, tofile=new_name,
                                 lineterm='')
    return '\n'.join(lines)


def main():
    items = []
    a_idx = 0
    b_idx = 0
    for fn in FUNCTIONS:
        name = fn['function']
        # Gate: correct passes ALL, buggy fails >= 1.
        rc = run_tests(fn['correct'], fn['tests'])
        rb = run_tests(fn['buggy'], fn['tests'])
        n_pass_c = len(rc['passed'])
        n_fail_c = len(rc['failed']) + len(rc['errors'])
        n_fail_b = len(rb['failed']) + len(rb['errors'])
        print(f"{name}: correct {n_pass_c} pass / {n_fail_c} fail; "
              f"buggy {n_fail_b} fail: {[f['test'] for f in rb['failed']]}")
        assert n_fail_c == 0, f"{name}: correct impl fails tests!"
        assert n_fail_b >= 1, f"{name}: buggy impl passes all tests!"
        # (a) correct -> buggy (expected fail)
        a_idx += 1
        items.append({
            'decision_id': f'a{a_idx:02d}', 'type': 'a',
            'function': name,
            'prompt_ref': f'{name}:correct->buggy',
            'spec': fn['spec'],
            'old_code': fn['correct'], 'new_code': fn['buggy'],
            'diff': diff_text(fn['correct'], fn['buggy'],
                              'correct.py', 'buggy.py'),
            'tests': fn['tests'], 'expected': 'fail'})
        # (a) buggy -> correct (expected pass)
        a_idx += 1
        items.append({
            'decision_id': f'a{a_idx:02d}', 'type': 'a',
            'function': name,
            'prompt_ref': f'{name}:buggy->correct',
            'spec': fn['spec'],
            'old_code': fn['buggy'], 'new_code': fn['correct'],
            'diff': diff_text(fn['buggy'], fn['correct'],
                              'buggy.py', 'correct.py'),
            'tests': fn['tests'], 'expected': 'pass'})
        # (b) A=correct, B=buggy (expected A)
        b_idx += 1
        items.append({
            'decision_id': f'b{b_idx:02d}', 'type': 'b',
            'function': name,
            'prompt_ref': f'{name}:correct-vs-buggy-A',
            'spec': fn['spec'],
            'impl_a': fn['correct'], 'impl_b': fn['buggy'],
            'correct_position': 'A', 'tests': fn['tests'],
            'expected': 'A'})
        # (b) A=buggy, B=correct (expected B)
        b_idx += 1
        items.append({
            'decision_id': f'b{b_idx:02d}', 'type': 'b',
            'function': name,
            'prompt_ref': f'{name}:correct-vs-buggy-B',
            'spec': fn['spec'],
            'impl_a': fn['buggy'], 'impl_b': fn['correct'],
            'correct_position': 'B', 'tests': fn['tests'],
            'expected': 'B'})
    assert len(items) == 20, len(items)
    with open('/home/hatch/workspace/jev-lag-new-items.json', 'w') as f:
        json.dump({'items': items}, f, indent=2)
    print('WROTE 20 new items')


if __name__ == '__main__':
    main()
