#!/usr/bin/env python3
"""Author correct implementations + tests from the JEV specs.

WHY THIS EXISTS (documented deviation): the brief preferred
magicoder generation, but magicoder demonstrably fails
spec-precise generation. Probe evidence (wilson_lower, one call):
wrong Wilson formula despite the formula being in the spec,
tests asserting wilson_lower(10,10)==1.0 and (5,10)==0.5 (true
values ~0.722 and ~0.237), and BUGGY_A/BUGGY_B identical to
CORRECT (no bug at all). A generator that cannot produce a
correct implementation or a failing buggy variant cannot supply
ground truth. So: correct implementations + tests are authored
here from the precise specs (the spec is the authority), and
magicoder supplies ONLY buggy variants + refactors + optimizes
(mutation tasks, verified by pytest). Independence preserved:
judge (hammer/quicklook) never generated materials; calculator
(pytest) scores everything; fast seats never see ground truth.
No 30B coder is loaded for this test.

Writes materials/<name>/correct.py + tests.py for all 12 specs.
"""
import json, os

BASE = '/home/joshua/jev-test/materials'

FUNCS = {}

FUNCS['wilson_lower'] = (
'''import math


def wilson_lower(k, n, z=1.96):
    if n == 0:
        return 0.0
    if k < 0 or k > n or n < 0:
        raise ValueError("k must satisfy 0 <= k <= n and n >= 0")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    delta = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    lower = centre - delta
    return max(0.0, min(1.0, lower))
''',
'''import pytest
from impl import wilson_lower


def test_zero_success():
    assert wilson_lower(0, 10) == 0.0


def test_all_success():
    assert wilson_lower(10, 10) == pytest.approx(0.7225, abs=0.001)


def test_half():
    assert wilson_lower(5, 10) == pytest.approx(0.2366, abs=0.001)


def test_zero_trials():
    assert wilson_lower(0, 0) == 0.0


def test_k_greater_than_n():
    with pytest.raises(ValueError):
        wilson_lower(11, 10)


def test_negative_k():
    with pytest.raises(ValueError):
        wilson_lower(-1, 10)


def test_negative_n():
    with pytest.raises(ValueError):
        wilson_lower(0, -1)
''')

FUNCS['median_of'] = (
'''def median_of(values):
    if not values:
        raise ValueError("median of empty list")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2
''',
'''import pytest
from impl import median_of


def test_odd():
    assert median_of([3, 1, 2]) == 2


def test_even():
    assert median_of([1, 2, 3, 4]) == 2.5


def test_single():
    assert median_of([7]) == 7


def test_empty():
    with pytest.raises(ValueError):
        median_of([])


def test_no_mutation():
    xs = [3, 1, 2]
    median_of(xs)
    assert xs == [3, 1, 2]


def test_negatives_and_floats():
    assert median_of([-5, -1, 0]) == -1
    assert median_of([1.5, 2.5]) == 2.0
''')

FUNCS['format_duration'] = (
'''def format_duration(seconds):
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    if seconds == 0:
        return "0s"
    parts = []
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")
    return " ".join(parts)
''',
'''import pytest
from impl import format_duration


def test_zero():
    assert format_duration(0) == "0s"


def test_seconds_only():
    assert format_duration(59) == "59s"


def test_minute():
    assert format_duration(60) == "1m"


def test_minute_second():
    assert format_duration(61) == "1m 1s"


def test_hour():
    assert format_duration(3600) == "1h"


def test_full():
    assert format_duration(3661) == "1h 1m 1s"


def test_day():
    assert format_duration(90061) == "1d 1h 1m 1s"


def test_negative():
    with pytest.raises(ValueError):
        format_duration(-1)
''')

FUNCS['parse_size'] = (
'''def parse_size(s):
    if not isinstance(s, str):
        raise ValueError("size must be a string")
    t = s.strip()
    if not t:
        raise ValueError("empty size")
    units = {"B": 1, "KB": 1024, "MB": 1024 ** 2,
             "GB": 1024 ** 3, "TB": 1024 ** 4}
    i = 0
    while i < len(t) and (t[i].isdigit() or t[i] == '.'):
        i += 1
    num_part, unit_part = t[:i], t[i:].strip().upper()
    if not num_part:
        raise ValueError("no number in size")
    try:
        num = float(num_part)
    except ValueError:
        raise ValueError("invalid number in size")
    if unit_part == "":
        mult = 1
    elif unit_part in units:
        mult = units[unit_part]
    else:
        raise ValueError("unknown unit")
    if num < 0:
        raise ValueError("negative size")
    return int(num * mult)
''',
'''import pytest
from impl import parse_size


def test_plain_number():
    assert parse_size("1024") == 1024


def test_kb():
    assert parse_size("1KB") == 1024


def test_fractional_mb():
    assert parse_size("1.5MB") == 1572864


def test_space_and_case():
    assert parse_size("2 gb") == 2147483648


def test_bytes_unit():
    assert parse_size("1b") == 1


def test_invalid():
    with pytest.raises(ValueError):
        parse_size("abc")


def test_negative():
    with pytest.raises(ValueError):
        parse_size("-1KB")


def test_unknown_unit():
    with pytest.raises(ValueError):
        parse_size("1XB")
''')

FUNCS['backoff_delay'] = (
'''def backoff_delay(attempt, base=1.0, cap=60.0):
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        raise ValueError("attempt must be an int >= 0")
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    if base <= 0 or cap <= 0:
        raise ValueError("base and cap must be > 0")
    return min(cap, base * (2 ** attempt))
''',
'''import pytest
from impl import backoff_delay


def test_first():
    assert backoff_delay(0) == 1.0


def test_third():
    assert backoff_delay(3) == 8.0


def test_capped():
    assert backoff_delay(10) == 60.0


def test_negative_attempt():
    with pytest.raises(ValueError):
        backoff_delay(-1)


def test_zero_base():
    with pytest.raises(ValueError):
        backoff_delay(0, base=0)


def test_custom_base():
    assert backoff_delay(2, base=2.0) == 8.0
''')

FUNCS['sliding_average'] = (
'''def sliding_average(values, window):
    if not values:
        raise ValueError("empty values")
    if not isinstance(window, int) or isinstance(window, bool):
        raise ValueError("window must be an int")
    if window < 1 or window > len(values):
        raise ValueError("window out of range")
    return [sum(values[i:i + window]) / window
            for i in range(len(values) - window + 1)]
''',
'''import pytest
from impl import sliding_average


def test_basic():
    assert sliding_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_window_one():
    assert sliding_average([1, 2, 3, 4], 1) == [1.0, 2.0, 3.0, 4.0]


def test_full_window():
    assert sliding_average([1, 2, 3, 4], 4) == [2.5]


def test_window_too_big():
    with pytest.raises(ValueError):
        sliding_average([1, 2, 3, 4], 5)


def test_window_zero():
    with pytest.raises(ValueError):
        sliding_average([1, 2, 3, 4], 0)


def test_empty():
    with pytest.raises(ValueError):
        sliding_average([], 1)
''')

FUNCS['chunk_list'] = (
'''def chunk_list(items, size):
    if not isinstance(size, int) or isinstance(size, bool):
        raise ValueError("size must be an int >= 1")
    if size < 1:
        raise ValueError("size must be >= 1")
    return [items[i:i + size] for i in range(0, len(items), size)]
''',
'''import pytest
from impl import chunk_list


def test_basic():
    assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_exact():
    assert chunk_list([1, 2, 3, 4, 5], 5) == [[1, 2, 3, 4, 5]]


def test_oversize():
    assert chunk_list([1, 2, 3, 4, 5], 10) == [[1, 2, 3, 4, 5]]


def test_size_zero():
    with pytest.raises(ValueError):
        chunk_list([1, 2], 0)


def test_empty():
    assert chunk_list([], 3) == []
''')

FUNCS['merge_intervals'] = (
'''def merge_intervals(intervals):
    for start, end in intervals:
        if start > end:
            raise ValueError("start > end")
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda p: p[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
''',
'''import pytest
from impl import merge_intervals


def test_basic():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == \
        [[1, 6], [8, 10], [15, 18]]


def test_empty():
    assert merge_intervals([]) == []


def test_touching():
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_unsorted():
    assert merge_intervals([[8, 10], [1, 3], [2, 6]]) == \
        [[1, 6], [8, 10]]


def test_inverted():
    with pytest.raises(ValueError):
        merge_intervals([[5, 3]])
''')

FUNCS['top_k'] = (
'''def top_k(counts, k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise ValueError("k must be an int >= 1")
    if k < 1:
        raise ValueError("k must be >= 1")
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [key for key, _ in ranked[:k]]
''',
'''import pytest
from impl import top_k


def test_tie_key_order():
    assert top_k({'a': 3, 'b': 3, 'c': 1}, 2) == ['a', 'b']


def test_tie_insertion_order_differs():
    # Catches a ties-by-insertion-order bug: insertion order here
    # is b,a but key order is a,b.
    assert top_k({'b': 2, 'a': 2}, 2) == ['a', 'b']


def test_k_zero():
    with pytest.raises(ValueError):
        top_k({'a': 1}, 0)


def test_k_larger():
    assert top_k({'a': 3, 'b': 3, 'c': 1}, 10) == ['a', 'b', 'c']


def test_empty():
    assert top_k({}, 1) == []
''')

FUNCS['clamp'] = (
'''def clamp(value, lo, hi):
    if lo > hi:
        raise ValueError("lo must be <= hi")
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value
''',
'''import pytest
from impl import clamp


def test_inside():
    assert clamp(5, 0, 10) == 5


def test_below():
    assert clamp(-1, 0, 10) == 0


def test_above():
    assert clamp(11, 0, 10) == 10


def test_inverted():
    with pytest.raises(ValueError):
        clamp(5, 10, 0)


def test_edges():
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10
''')

FUNCS['slugify'] = (
'''import re


def slugify(text):
    lowered = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', lowered)
    return slug.strip('-')
''',
'''import pytest
from impl import slugify


def test_basic():
    assert slugify('Hello World!') == 'hello-world'


def test_collapse_and_strip():
    assert slugify('  A--B  ') == 'a-b'


def test_empty():
    assert slugify('') == ''


def test_plain():
    assert slugify('abc') == 'abc'


def test_underscore():
    assert slugify('a b_c') == 'a-b-c'
''')

FUNCS['dedupe_preserve_order'] = (
'''def dedupe_preserve_order(items):
    return list(dict.fromkeys(items))
''',
'''import pytest
from impl import dedupe_preserve_order


def test_basic():
    assert dedupe_preserve_order([1, 2, 2, 3, 1]) == [1, 2, 3]


def test_empty():
    assert dedupe_preserve_order([]) == []


def test_strings():
    assert dedupe_preserve_order(['b', 'a', 'b']) == ['b', 'a']


def test_all_same():
    assert dedupe_preserve_order([5, 5, 5]) == [5]
''')

SPECS = {f['name']: f for f in
         json.load(open('/home/joshua/jev-test/jev-specs.json'))['functions']}

def main():
    for name, (impl, tests) in FUNCS.items():
        d = os.path.join(BASE, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'correct.py'), 'w') as f:
            f.write(impl)
        with open(os.path.join(d, 'tests.py'), 'w') as f:
            f.write(tests)
        print(f"wrote {name} (spec c_diff={SPECS[name]['c_diff']})")
    print(f"total: {len(FUNCS)} functions")

if __name__ == '__main__':
    main()
