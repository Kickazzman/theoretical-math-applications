#!/usr/bin/env python3
"""Author HARD JEV materials (runs ON mrfloppy).

Hand-authored correct implementations + tests from precise specs,
following the original method (jev-contract-test-report.md §9.1).
Writes ~/jev-test/materials-hard/<name>/{correct.py,tests.py} plus
~/jev-test/jev-specs-hard.json and ~/jev-test/jev-hard-mutations.json.
Buggy variants are generated separately by jev-hard-gen.py (magicoder
:8202 direct, exact mutation instructions); the test gate is
jev-hard-verify.py. This script writes NO variants and NO items.
"""
import json
import os

BASE = '/home/joshua/jev-test/materials-hard'

FUNCTIONS = [
    {
        'name': 'exponential_moving_average',
        'spec': (
            "exponential_moving_average(values, alpha, initial=None): exponential "
            "moving average of a list of numbers. values must be a non-empty list, "
            "else ValueError. alpha must satisfy 0 < alpha <= 1, else ValueError. "
            "If initial is None, the first output is values[0] and the average "
            "updates over values[1:]; if initial is given, the average starts at "
            "initial and updates over all of values. Update rule: "
            "ema = alpha * x + (1 - alpha) * ema. Returns a list of floats the "
            "same length as values. Tests must cover: [10, 20, 30] alpha 0.5 -> "
            "[10, 15, 22.5]; alpha 1.0 -> values unchanged; initial 0.0 with "
            "[10, 20, 30] alpha 0.5 -> [5, 12.5, 21.25]; single element; alpha 0 "
            "and alpha 1.5 raise ValueError; empty values raises ValueError."
        ),
        'correct': '''def exponential_moving_average(values, alpha, initial=None):
    """Exponential moving average.

    Seeds from values[0] when initial is None (then updates over the
    rest); otherwise seeds from initial and updates over all values.
    """
    if not isinstance(values, list) or len(values) == 0:
        raise ValueError("values must be a non-empty list")
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise ValueError("alpha must be a number")
    if alpha <= 0 or alpha > 1:
        raise ValueError("alpha must satisfy 0 < alpha <= 1")
    if initial is None:
        ema = float(values[0])
        result = [ema]
        rest = values[1:]
    else:
        ema = float(initial)
        result = []
        rest = values
    for x in rest:
        ema = alpha * float(x) + (1 - alpha) * ema
        result.append(ema)
    return result
''',
        'tests': '''import pytest
from impl import exponential_moving_average


def test_basic():
    assert exponential_moving_average([10, 20, 30], 0.5) == [10, 15, 22.5]


def test_alpha_one():
    assert exponential_moving_average([10, 20], 1.0) == [10, 20]


def test_initial():
    result = exponential_moving_average([10, 20, 30], 0.5, initial=0.0)
    assert len(result) == 3
    assert all(got == pytest.approx(want)
               for got, want in zip(result, [5, 12.5, 21.25]))


def test_single():
    assert exponential_moving_average([7], 0.3) == [7.0]


def test_alpha_zero():
    with pytest.raises(ValueError):
        exponential_moving_average([1, 2], 0)


def test_alpha_too_big():
    with pytest.raises(ValueError):
        exponential_moving_average([1, 2], 1.5)


def test_empty():
    with pytest.raises(ValueError):
        exponential_moving_average([], 0.5)
''',
        'mutations': {
            'BUGGY_A': "In the initial-is-None branch, set rest = values instead of rest = values[1:], so the first value is counted twice. Change nothing else.",
            'BUGGY_B': "In the update line, write ema = alpha * float(x) + 1 - alpha * ema instead of ema = alpha * float(x) + (1 - alpha) * ema. Change nothing else.",
        },
    },
    {
        'name': 'merge_sorted_lists',
        'spec': (
            "merge_sorted_lists(a, b, key=None): merge two sorted lists "
            "(ascending) into one sorted list. a and b must be lists, else "
            "ValueError. key is an optional function mapping elements to sort "
            "keys (default identity); a non-callable key raises ValueError. "
            "STABLE: when keys are equal, elements from a come before elements "
            "from b. Tests must cover: [1, 3, 5] + [2, 4, 6] -> "
            "[1, 2, 3, 4, 5, 6]; either side empty; both empty; stability with "
            "equal keys from both lists; key function (length); duplicates "
            "across lists; non-list input and non-callable key raise ValueError."
        ),
        'spec_b': (
            "merge_sorted_lists(a, b, key=None): merge two sorted lists "
            "(ascending) into one sorted list. a and b must be lists, else "
            "ValueError. key is an optional function mapping elements to sort "
            "keys (default identity); a non-callable key raises ValueError. "
            "Ambiguity note: this spec does not state what order equal-key "
            "elements take when they come from different lists. Tests must "
            "cover: [1, 3, 5] + [2, 4, 6] -> [1, 2, 3, 4, 5, 6]; either side "
            "empty; both empty; equal keys from both lists; key function "
            "(length); duplicates across lists; non-list input and "
            "non-callable key raise ValueError."
        ),
        'correct': '''def merge_sorted_lists(a, b, key=None):
    """Merge two sorted lists into one sorted list, stably.

    When keys are equal, elements from a come before elements from b.
    """
    if not isinstance(a, list) or not isinstance(b, list):
        raise ValueError("a and b must be lists")
    if key is None:
        key = lambda x: x
    if not callable(key):
        raise ValueError("key must be callable")
    out = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if key(a[i]) <= key(b[j]):
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
''',
        'tests': '''import pytest
from impl import merge_sorted_lists


def test_basic():
    assert merge_sorted_lists([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]


def test_left_empty():
    assert merge_sorted_lists([], [1, 2]) == [1, 2]


def test_right_empty():
    assert merge_sorted_lists([1, 2], []) == [1, 2]


def test_both_empty():
    assert merge_sorted_lists([], []) == []


def test_stability():
    a = [('a', 1), ('c', 1)]
    b = [('b', 1)]
    assert merge_sorted_lists(a, b, key=lambda t: t[1]) == [('a', 1), ('c', 1), ('b', 1)]


def test_key():
    assert merge_sorted_lists(['a', 'ccc'], ['bb'], key=len) == ['a', 'bb', 'ccc']


def test_duplicates():
    assert merge_sorted_lists([1, 2, 2], [2, 3]) == [1, 2, 2, 2, 3]


def test_not_lists():
    with pytest.raises(ValueError):
        merge_sorted_lists("ab", [1])


def test_bad_key():
    with pytest.raises(ValueError):
        merge_sorted_lists([1], [2], key=3)
''',
        'mutations': {
            'BUGGY_A': "In the merge comparison, use < instead of <=, so equal keys take from b first instead of a. Change nothing else.",
            'BUGGY_B': "Replace out.extend(a[i:]) with out.extend(a[i + 1:]) and out.extend(b[j:]) with out.extend(b[j + 1:]). Change nothing else.",
        },
    },
    {
        'name': 'parse_duration',
        'spec': (
            "parse_duration(s): parse a duration string to total seconds "
            "(int). Parts are an integer followed by a unit: d (86400), h "
            "(3600), m (60), s (1); units are case-insensitive; optional "
            "whitespace may appear between parts and around the whole string. "
            "A string that is just an integer with no unit means that many "
            "seconds. Anything else raises ValueError, including empty input "
            "and non-string input. Tests must cover: '90s' -> 90; '1h30m' -> "
            "5400; '2d 3h 15m' -> 184500; '45' -> 45; '1H' -> 3600; ' 2m ' -> "
            "120; '1h 30m 10s' -> 5410; '' raises; 'abc' raises; '1x' raises; "
            "'1.5h' raises; non-string raises."
        ),
        'correct': '''import re


def parse_duration(s):
    """Parse a duration string like '1h30m' to total seconds."""
    if not isinstance(s, str):
        raise ValueError("duration must be a string")
    t = s.strip()
    if not t:
        raise ValueError("empty duration")
    if re.fullmatch(r"\\d+", t):
        return int(t)
    multipliers = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    total = 0
    pos = 0
    pattern = re.compile(r"(\\d+)\\s*([dhmsDHMS])")
    while pos < len(t):
        m = pattern.match(t, pos)
        if m is None:
            raise ValueError("invalid duration part")
        total += int(m.group(1)) * multipliers[m.group(2).lower()]
        pos = m.end()
        while pos < len(t) and t[pos] == " ":
            pos += 1
    return total
''',
        'tests': '''import pytest
from impl import parse_duration


def test_seconds():
    assert parse_duration("90s") == 90


def test_compound():
    assert parse_duration("1h30m") == 5400


def test_days():
    assert parse_duration("2d 3h 15m") == 184500


def test_bare():
    assert parse_duration("45") == 45


def test_upper():
    assert parse_duration("1H") == 3600


def test_surrounding_space():
    assert parse_duration(" 2m ") == 120


def test_spaced_parts():
    assert parse_duration("1h 30m 10s") == 5410


def test_empty():
    with pytest.raises(ValueError):
        parse_duration("")


def test_alpha():
    with pytest.raises(ValueError):
        parse_duration("abc")


def test_bad_unit():
    with pytest.raises(ValueError):
        parse_duration("1x")


def test_fraction():
    with pytest.raises(ValueError):
        parse_duration("1.5h")


def test_non_string():
    with pytest.raises(ValueError):
        parse_duration(123)
''',
        'mutations': {
            'BUGGY_A': "In the multipliers dict, swap the m and s values, so m maps to 1 and s maps to 60. Change nothing else.",
            'BUGGY_B': "In the bare-number early return, return int(t) * 60 instead of int(t), so bare numbers read as minutes instead of seconds. Change nothing else.",
        },
    },
]

FUNCTIONS.extend([
    {
        'name': 'weighted_quantile',
        'spec': (
            "weighted_quantile(values, weights, q): weighted quantile with "
            "linear interpolation. values and weights must be non-empty lists "
            "of the same length, else ValueError; weights must be "
            "non-negative with a positive sum, else ValueError; q must "
            "satisfy 0 <= q <= 1, else ValueError. Method: sort value/weight "
            "pairs by value; let C_k be the cumulative weight through index "
            "k; find the smallest k with C_k >= q * total weight; if k == 0 "
            "return values[0]; otherwise interpolate between values[k-1] and "
            "values[k] with fraction (q*total - C_{k-1}) / (C_k - C_{k-1}). "
            "Tests must cover: [10, 20, 30] weights [1, 1, 1] q=0.5 -> 15; "
            "q=0 -> 10; q=1 -> 30; q=0.5 on [10, 20] weights [1, 1] -> 10 "
            "(exact boundary); [0, 100] weights [1, 3] q=0.5 -> approx "
            "33.333; error cases (empty, mismatched lengths, negative "
            "weight, zero total weight, q out of range)."
        ),
        'correct': '''def weighted_quantile(values, weights, q):
    """Weighted quantile with linear interpolation.

    Sorts value/weight pairs, finds the first index whose cumulative
    weight reaches q * total, and interpolates within that segment.
    """
    if not isinstance(values, list) or not isinstance(weights, list):
        raise ValueError("values and weights must be lists")
    if len(values) == 0 or len(weights) != len(values):
        raise ValueError("values and weights must be non-empty and same length")
    if any(w < 0 for w in weights):
        raise ValueError("weights must be non-negative")
    total = sum(weights)
    if total <= 0:
        raise ValueError("total weight must be > 0")
    if isinstance(q, bool) or not isinstance(q, (int, float)):
        raise ValueError("q must be a number")
    if q < 0 or q > 1:
        raise ValueError("q must satisfy 0 <= q <= 1")
    pairs = sorted(zip(values, weights))
    target = q * total
    cumulative = 0.0
    prev_value = pairs[0][0]
    prev_cum = 0.0
    for value, w in pairs:
        cumulative += w
        if cumulative >= target:
            if cumulative == prev_cum:
                return value
            frac = (target - prev_cum) / (cumulative - prev_cum)
            return prev_value + frac * (value - prev_value)
        prev_value = value
        prev_cum = cumulative
    return pairs[-1][0]
''',
        'tests': '''import pytest
from impl import weighted_quantile


def test_median():
    assert weighted_quantile([10, 20, 30], [1, 1, 1], 0.5) == pytest.approx(15)


def test_q_zero():
    assert weighted_quantile([10, 20, 30], [1, 1, 1], 0) == 10


def test_q_one():
    assert weighted_quantile([10, 20, 30], [1, 1, 1], 1) == 30


def test_boundary():
    assert weighted_quantile([10, 20], [1, 1], 0.5) == 10


def test_weighted():
    assert weighted_quantile([0, 100], [1, 3], 0.5) == pytest.approx(100 / 3)


def test_first_segment():
    assert weighted_quantile([10, 20, 30], [1, 1, 1], 0.25) == 10


def test_empty():
    with pytest.raises(ValueError):
        weighted_quantile([], [], 0.5)


def test_mismatch():
    with pytest.raises(ValueError):
        weighted_quantile([1, 2], [1], 0.5)


def test_negative_weight():
    with pytest.raises(ValueError):
        weighted_quantile([1, 2], [1, -1], 0.5)


def test_zero_total():
    with pytest.raises(ValueError):
        weighted_quantile([1, 2], [0, 0], 0.5)


def test_q_low():
    with pytest.raises(ValueError):
        weighted_quantile([1, 2], [1, 1], -0.1)


def test_q_high():
    with pytest.raises(ValueError):
        weighted_quantile([1, 2], [1, 1], 1.1)
''',
        'mutations': {
            'BUGGY_A': "In the frac line, divide by cumulative instead of (cumulative - prev_cum). Change nothing else.",
            'BUGGY_B': "In the interpolation return, write prev_value + frac * value - prev_value instead of prev_value + frac * (value - prev_value). Change nothing else.",
        },
    },
    {
        'name': 'sliding_window_max',
        'spec': (
            "sliding_window_max(values, window): maximum of each sliding "
            "window. values must be a non-empty list, else ValueError. window "
            "must be an int with 1 <= window <= len(values), else ValueError. "
            "Returns a list of length len(values) - window + 1. Implementation "
            "keeps a deque of candidate indices: expired indices (index <= "
            "i - window) are dropped from the front, smaller-or-equal values "
            "are dropped from the back, and the front holds the window "
            "maximum. Tests must cover: [1, 3, -1, -3, 5, 3, 6, 7] window 2 -> "
            "[3, 3, -1, 5, 5, 6, 7]; window 1 returns values unchanged; "
            "window equal to length returns [max]; decreasing and increasing "
            "inputs; error cases (empty, window 0, window too large, non-int "
            "window)."
        ),
        'correct': '''from collections import deque


def sliding_window_max(values, window):
    """Maximum of each sliding window, via a monotone deque."""
    if not isinstance(values, list) or len(values) == 0:
        raise ValueError("values must be a non-empty list")
    if isinstance(window, bool) or not isinstance(window, int):
        raise ValueError("window must be an int")
    if window < 1 or window > len(values):
        raise ValueError("window out of range")
    dq = deque()
    result = []
    for i, x in enumerate(values):
        while dq and dq[0] <= i - window:
            dq.popleft()
        while dq and values[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if i >= window - 1:
            result.append(values[dq[0]])
    return result
''',
        'tests': '''import pytest
from impl import sliding_window_max


def test_classic():
    assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 2) == [3, 3, -1, 5, 5, 6, 7]


def test_window_one():
    assert sliding_window_max([4, 2, 9], 1) == [4, 2, 9]


def test_window_full():
    assert sliding_window_max([3, 1, 4], 3) == [4]


def test_decreasing():
    assert sliding_window_max([5, 4, 3, 2], 2) == [5, 4, 3]


def test_increasing():
    assert sliding_window_max([1, 2, 3, 4], 3) == [3, 4]


def test_ties():
    assert sliding_window_max([2, 2, 2], 2) == [2, 2]


def test_empty():
    with pytest.raises(ValueError):
        sliding_window_max([], 1)


def test_window_zero():
    with pytest.raises(ValueError):
        sliding_window_max([1, 2], 0)


def test_window_too_large():
    with pytest.raises(ValueError):
        sliding_window_max([1, 2, 3], 4)


def test_window_non_int():
    with pytest.raises(ValueError):
        sliding_window_max([1, 2, 3], 2.5)
''',
        'mutations': {
            'BUGGY_A': "In the expiry check, use dq[0] < i - window instead of dq[0] <= i - window. Change nothing else.",
            'BUGGY_B': "In the output condition, use i >= window instead of i >= window - 1. Change nothing else.",
        },
    },
    {
        'name': 'levenshtein',
        'spec': (
            "levenshtein(a, b): edit distance between two strings (insert, "
            "delete, substitute, each cost 1). Inputs must be strings, else "
            "ValueError. Tests must cover: ('kitten', 'sitting') -> 3; "
            "('flaw', 'lawn') -> 2; ('saturday', 'sunday') -> 3; empty vs "
            "non-empty both directions; empty vs empty -> 0; identical "
            "strings -> 0; single substitution -> 1; non-string input raises "
            "ValueError."
        ),
        'correct': '''def levenshtein(a, b):
    """Edit distance between two strings.

    Dynamic programming over rows of the shorter string's columns:
    prev holds the previous row, cur the current row; cost is 0 for a
    match and 1 for a substitution.
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise ValueError("inputs must be strings")
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[len(b)]
''',
        'tests': '''import pytest
from impl import levenshtein


def test_kitten_sitting():
    assert levenshtein("kitten", "sitting") == 3


def test_flaw_lawn():
    assert levenshtein("flaw", "lawn") == 2


def test_saturday_sunday():
    assert levenshtein("saturday", "sunday") == 3


def test_empty_left():
    assert levenshtein("", "abc") == 3


def test_empty_right():
    assert levenshtein("abc", "") == 3


def test_empty_both():
    assert levenshtein("", "") == 0


def test_identical():
    assert levenshtein("abc", "abc") == 0


def test_single_substitution():
    assert levenshtein("abc", "abd") == 1


def test_single_char():
    assert levenshtein("a", "a") == 0
    assert levenshtein("a", "b") == 1


def test_non_string():
    with pytest.raises(ValueError):
        levenshtein(123, "a")
    with pytest.raises(ValueError):
        levenshtein("a", None)
''',
        'mutations': {
            'BUGGY_A': "In the cost line, compare ca with b[j - 2] instead of cb (the loop variable holding b[j - 1]). Change nothing else.",
            'BUGGY_B': "In the recurrence, use prev[j] + cost instead of prev[j - 1] + cost (the diagonal cell). Change nothing else.",
        },
    },
    {
        'name': 'interpolate_missing',
        'spec': (
            "interpolate_missing(points): fill None gaps in a list by linear "
            "interpolation. points must be a non-empty list, else ValueError; "
            "all-None raises ValueError. Each interior None is filled by "
            "linear interpolation between its nearest known neighbors. "
            "Leading Nones take the first known value; trailing Nones take "
            "the last known value. Known values are kept as given. Tests must "
            "cover: [1, None, 3] -> [1, 2.0, 3]; [0, None, None, 30] -> [0, "
            "approx 10, approx 20, 30]; [None, None, 5, None, 9, None] -> [5, "
            "5, 5, 7.0, 9, 9]; [None, 4, None] -> [4, 4, 4]; no gaps "
            "unchanged; single element; empty and all-None raise ValueError."
        ),
        'correct': '''def interpolate_missing(points):
    """Fill None gaps by linear interpolation between known neighbors."""
    if not isinstance(points, list) or len(points) == 0:
        raise ValueError("points must be a non-empty list")
    known = [i for i, v in enumerate(points) if v is not None]
    if not known:
        raise ValueError("no known values to interpolate from")
    result = list(points)
    first, last = known[0], known[-1]
    for i in range(first):
        result[i] = points[first]
    for i in range(last + 1, len(points)):
        result[i] = points[last]
    for left, right in zip(known, known[1:]):
        if right - left <= 1:
            continue
        start, end = points[left], points[right]
        for i in range(left + 1, right):
            frac = (i - left) / (right - left)
            result[i] = start + frac * (end - start)
    return result
''',
        'tests': '''import pytest
from impl import interpolate_missing


def test_single_gap():
    assert interpolate_missing([1, None, 3]) == [1, 2.0, 3]


def test_double_gap():
    result = interpolate_missing([0, None, None, 30])
    assert result[0] == 0 and result[3] == 30
    assert result[1] == pytest.approx(10.0)
    assert result[2] == pytest.approx(20.0)


def test_edges():
    assert interpolate_missing([None, None, 5, None, 9, None]) == [5, 5, 5, 7.0, 9, 9]


def test_single_known():
    assert interpolate_missing([None, 4, None]) == [4, 4, 4]


def test_no_gaps():
    assert interpolate_missing([1, 2, 3]) == [1, 2, 3]


def test_single():
    assert interpolate_missing([5]) == [5]


def test_empty():
    with pytest.raises(ValueError):
        interpolate_missing([])


def test_all_none():
    with pytest.raises(ValueError):
        interpolate_missing([None, None])
''',
        'mutations': {
            'BUGGY_A': "In the frac line, divide by (right - left + 1) instead of (right - left). Change nothing else.",
            'BUGGY_B': "In the trailing loop, fill with points[first] instead of points[last]. Change nothing else.",
        },
    },
])

FUNCTIONS.extend([
    {
        'name': 'allocate_budget',
        'spec': (
            "allocate_budget(amounts, total): distribute total indivisible "
            "units across amounts by the largest-remainder method. amounts "
            "must be a non-empty list of non-negative numbers, else "
            "ValueError; total must be an int >= 0, else ValueError; zero "
            "total weight with total > 0 raises ValueError. Method: quota_i "
            "= amounts[i] * total / sum(amounts); take floors; distribute "
            "the leftover units one each to the largest fractional "
            "remainders; ties in remainders are broken by larger amount "
            "first, then by earlier index. Returns a list of ints summing "
            "to total. Tests must cover: [100, 200, 300] total 10 -> [2, 3, "
            "5]; [1, 1, 1] total 2 -> [1, 1, 0]; [1, 3] total 2 -> [0, 2] "
            "(tie broken by larger amount); [5, 5] total 0 -> [0, 0]; [0, 10] "
            "total 5 -> [0, 5]; [2, 3] total 5 -> [2, 3]; error cases."
        ),
        'spec_b': (
            "allocate_budget(amounts, total): distribute total indivisible "
            "units across amounts by the largest-remainder method. amounts "
            "must be a non-empty list of non-negative numbers, else "
            "ValueError; total must be an int >= 0, else ValueError; zero "
            "total weight with total > 0 raises ValueError. Method: quota_i "
            "= amounts[i] * total / sum(amounts); take floors; distribute "
            "the leftover units one each to the largest fractional "
            "remainders. Ambiguity note: this spec does not state how ties "
            "in fractional remainders are broken. Returns a list of ints "
            "summing to total. Tests must cover: [100, 200, 300] total 10 -> "
            "[2, 3, 5]; [1, 1, 1] total 2 -> [1, 1, 0]; [1, 3] total 2; [5, 5] "
            "total 0 -> [0, 0]; [0, 10] total 5 -> [0, 5]; [2, 3] total 5 -> "
            "[2, 3]; error cases."
        ),
        'correct': '''def allocate_budget(amounts, total):
    """Distribute total units by the largest-remainder method."""
    if not isinstance(amounts, list) or len(amounts) == 0:
        raise ValueError("amounts must be a non-empty list")
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total must be an int >= 0")
    if any(a < 0 for a in amounts):
        raise ValueError("amounts must be non-negative")
    whole = sum(amounts)
    if total == 0:
        return [0] * len(amounts)
    if whole <= 0:
        raise ValueError("cannot apportion with zero total weight")
    quotas = [a * total / whole for a in amounts]
    base = [int(q) for q in quotas]
    remainders = [q - b for q, b in zip(quotas, base)]
    leftover = total - sum(base)
    order = sorted(range(len(amounts)),
                   key=lambda i: (-remainders[i], -amounts[i], i))
    for k in range(leftover):
        base[order[k]] += 1
    return base
''',
        'tests': '''import pytest
from impl import allocate_budget


def test_basic():
    assert allocate_budget([100, 200, 300], 10) == [2, 3, 5]


def test_equal_split():
    assert allocate_budget([1, 1, 1], 2) == [1, 1, 0]


def test_tie_larger_amount():
    assert allocate_budget([1, 3], 2) == [0, 2]


def test_zero_total():
    assert allocate_budget([5, 5], 0) == [0, 0]


def test_zero_weight():
    assert allocate_budget([0, 10], 5) == [0, 5]


def test_exact():
    assert allocate_budget([2, 3], 5) == [2, 3]


def test_empty():
    with pytest.raises(ValueError):
        allocate_budget([], 5)


def test_negative_total():
    with pytest.raises(ValueError):
        allocate_budget([1, 2], -1)


def test_fractional_total():
    with pytest.raises(ValueError):
        allocate_budget([1, 2], 1.5)


def test_negative_amount():
    with pytest.raises(ValueError):
        allocate_budget([1, -2], 5)


def test_zero_weights():
    with pytest.raises(ValueError):
        allocate_budget([0, 0], 5)
''',
        'mutations': {
            'BUGGY_A': "Replace range(leftover) with range(leftover - 1) in the distribution loop, so one leftover unit is never handed out. Change nothing else.",
            'BUGGY_B': "In the order sort key, use (-remainders[i], amounts[i], i) instead of (-remainders[i], -amounts[i], i), so remainder ties break by SMALLER amount instead of larger. Change nothing else.",
        },
    },
    {
        'name': 'validate_ipv4_cidr',
        'spec': (
            "validate_ipv4_cidr(s): validate an IPv4 CIDR string 'a.b.c.d/p'. "
            "Returns a tuple (dotted_address, prefix) on valid input, else "
            "raises ValueError. Rules: input must be a string; exactly one "
            "'/'; prefix must be digits with 0 <= prefix <= 32; address must "
            "have exactly four dot-separated octets; each octet must be "
            "digits with 0 <= value <= 255; octets with leading zeros (e.g. "
            "'010') are invalid, except '0' itself. Tests must cover: "
            "'192.168.0.1/24' -> ('192.168.0.1', 24); '0.0.0.0/0' -> "
            "('0.0.0.0', 0); '255.255.255.255/32' -> ('255.255.255.255', 32); "
            "'10.0.0.1/8' -> ('10.0.0.1', 8); '256.1.1.1/24', '1.2.3/24', "
            "'1.2.3.4.5/24', '01.2.3.4/24', '1.2.3.4/33', '1.2.3.4', "
            "'a.b.c.d/24', non-string all raise ValueError."
        ),
        'spec_b': (
            "validate_ipv4_cidr(s): validate an IPv4 CIDR string 'a.b.c.d/p'. "
            "Returns a tuple (dotted_address, prefix) on valid input, else "
            "raises ValueError. Rules: input must be a string; exactly one "
            "'/'; prefix must be digits with 0 <= prefix <= 32; address must "
            "have exactly four dot-separated octets; each octet must be "
            "digits with 0 <= value <= 255. Ambiguity note: this spec does "
            "not state whether leading zeros in octets (e.g. '010') are "
            "allowed. Tests must cover: '192.168.0.1/24' -> ('192.168.0.1', "
            "24); '0.0.0.0/0' -> ('0.0.0.0', 0); '255.255.255.255/32' -> "
            "('255.255.255.255', 32); '10.0.0.1/8' -> ('10.0.0.1', 8); "
            "'256.1.1.1/24', '1.2.3/24', '1.2.3.4.5/24', '01.2.3.4/24', "
            "'1.2.3.4/33', '1.2.3.4', 'a.b.c.d/24', non-string all raise "
            "ValueError."
        ),
        'correct': '''def validate_ipv4_cidr(s):
    """Validate an IPv4 CIDR string; return (address, prefix)."""
    if not isinstance(s, str):
        raise ValueError("input must be a string")
    parts = s.split("/")
    if len(parts) != 2:
        raise ValueError("expected address/prefix")
    addr, prefix_s = parts
    if not prefix_s.isdigit():
        raise ValueError("prefix must be digits")
    prefix = int(prefix_s)
    if prefix < 0 or prefix > 32:
        raise ValueError("prefix out of range")
    octets = addr.split(".")
    if len(octets) != 4:
        raise ValueError("expected four octets")
    values = []
    for octet in octets:
        if not octet.isdigit():
            raise ValueError("octet must be digits")
        if len(octet) > 1 and octet[0] == "0":
            raise ValueError("leading zeros not allowed")
        value = int(octet)
        if value < 0 or value > 255:
            raise ValueError("octet out of range")
        values.append(value)
    return (".".join(str(v) for v in values), prefix)
''',
        'tests': '''import pytest
from impl import validate_ipv4_cidr


def test_basic():
    assert validate_ipv4_cidr("192.168.0.1/24") == ("192.168.0.1", 24)


def test_zero():
    assert validate_ipv4_cidr("0.0.0.0/0") == ("0.0.0.0", 0)


def test_max():
    assert validate_ipv4_cidr("255.255.255.255/32") == ("255.255.255.255", 32)


def test_class_a():
    assert validate_ipv4_cidr("10.0.0.1/8") == ("10.0.0.1", 8)


def test_octet_too_big():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("256.1.1.1/24")


def test_too_few_octets():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("1.2.3/24")


def test_too_many_octets():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("1.2.3.4.5/24")


def test_leading_zero():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("01.2.3.4/24")


def test_prefix_too_big():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("1.2.3.4/33")


def test_no_prefix():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("1.2.3.4")


def test_alpha_octet():
    with pytest.raises(ValueError):
        validate_ipv4_cidr("a.b.c.d/24")


def test_non_string():
    with pytest.raises(ValueError):
        validate_ipv4_cidr(123)
''',
        'mutations': {
            'BUGGY_A': "In the octet range check, use value >= 255 instead of value > 255, so 255 is rejected. Change nothing else.",
            'BUGGY_B': "Remove the leading-zeros check entirely (delete the if len(octet) > 1 and octet[0] == '0': raise ValueError lines), so leading zeros are accepted. Change nothing else.",
        },
    },
    {
        'name': 'moving_median',
        'spec': (
            "moving_median(values, window): median of each sliding window. "
            "values must be a non-empty list, else ValueError. window must "
            "be an int with 1 <= window <= len(values), else ValueError. "
            "Returns a list of floats of length len(values) - window + 1. "
            "The median of a window is its middle value after sorting, or "
            "the mean of the two middle values for even windows. Tests must "
            "cover: [1, 3, 2, 5, 4] window 3 -> [2.0, 3.0, 4.0]; window 2 -> "
            "[2.0, 2.5, 3.5, 4.5]; window 1 -> values as floats; window 5 -> "
            "[3.0]; negatives; error cases."
        ),
        'spec_b': (
            "moving_median(values, window): median of each sliding window. "
            "values must be a non-empty list, else ValueError. window must "
            "be an int with 1 <= window <= len(values), else ValueError. "
            "Returns a list of floats of length len(values) - window + 1. "
            "The median of a window is its middle value after sorting. "
            "Ambiguity note: this spec does not state how the median of an "
            "even-sized window is defined. Tests must cover: [1, 3, 2, 5, 4] "
            "window 3 -> [2.0, 3.0, 4.0]; window 2 -> [2.0, 2.5, 3.5, 4.5]; "
            "window 1 -> values as floats; window 5 -> [3.0]; negatives; "
            "error cases."
        ),
        'correct': '''def moving_median(values, window):
    """Median of each sliding window.

    Each frame is a sorted copy, so the input list is never mutated.
    """
    if not isinstance(values, list) or len(values) == 0:
        raise ValueError("values must be a non-empty list")
    if isinstance(window, bool) or not isinstance(window, int):
        raise ValueError("window must be an int")
    if window < 1 or window > len(values):
        raise ValueError("window out of range")
    result = []
    for i in range(len(values) - window + 1):
        frame = sorted(values[i:i + window])
        mid = window // 2
        if window % 2 == 1:
            result.append(float(frame[mid]))
        else:
            result.append((frame[mid - 1] + frame[mid]) / 2)
    return result
''',
        'tests': '''import pytest
from impl import moving_median


def test_odd_window():
    assert moving_median([1, 3, 2, 5, 4], 3) == [2.0, 3.0, 4.0]


def test_even_window():
    assert moving_median([1, 3, 2, 5, 4], 2) == [2.0, 2.5, 3.5, 4.5]


def test_window_one():
    assert moving_median([1, 3, 2, 5, 4], 1) == [1.0, 3.0, 2.0, 5.0, 4.0]


def test_window_full():
    assert moving_median([1, 3, 2, 5, 4], 5) == [3.0]


def test_negatives():
    assert moving_median([-5, -1, -3], 2) == [-3.0, -2.0]


def test_empty():
    with pytest.raises(ValueError):
        moving_median([], 1)


def test_window_zero():
    with pytest.raises(ValueError):
        moving_median([1, 2], 0)


def test_window_too_large():
    with pytest.raises(ValueError):
        moving_median([1, 2, 3], 4)


def test_window_non_int():
    with pytest.raises(ValueError):
        moving_median([1, 2, 3], 2.5)
''',
        'mutations': {
            'BUGGY_A': "Replace range(len(values) - window + 1) with range(len(values) - window) in the main loop, so the last window is never processed. Change nothing else.",
            'BUGGY_B': "In the even-window case, return float(frame[mid - 1]) (the lower middle) instead of (frame[mid - 1] + frame[mid]) / 2 (the mean of the two middles). Change nothing else.",
        },
    },
])


def main():
    os.makedirs(BASE, exist_ok=True)
    specs = []
    muts = {}
    for fn in FUNCTIONS:
        d = os.path.join(BASE, fn['name'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'correct.py'), 'w') as f:
            f.write(fn['correct'])
        with open(os.path.join(d, 'tests.py'), 'w') as f:
            f.write(fn['tests'])
        specs.append({'name': fn['name'], 'spec': fn['spec'],
                      'spec_b': fn.get('spec_b', fn['spec']),
                      'c_diff': 'none'})
        muts[fn['name']] = fn['mutations']
        print(f"wrote {fn['name']}: correct.py + tests.py", flush=True)
    with open('/home/joshua/jev-test/jev-specs-hard.json', 'w') as f:
        json.dump({'functions': specs}, f, indent=2)
    with open('/home/joshua/jev-test/jev-hard-mutations.json', 'w') as f:
        json.dump(muts, f, indent=2)
    print(f"authored {len(FUNCTIONS)} functions -> {BASE}")


if __name__ == '__main__':
    main()
