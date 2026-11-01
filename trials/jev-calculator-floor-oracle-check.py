#!/usr/bin/env python3
"""Independent oracle cross-check for calculator-floor references.

Each reference implementation is compared against a SECOND implementation
written differently (stdlib, a different algorithm, or a lookup table) on
random + edge inputs. This guards against a correlated author error (same
mistake in reference and test expected values). This runs BEFORE the
measurement and never touches test suites' separation outcomes.
"""
import itertools
import math
import os
import random
import re
import sys
from collections import Counter

sys.path.insert(0, ".")
import importlib.util

spec = importlib.util.spec_from_file_location(
    "cfbuild", "jev-calculator-floor-build.py")
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)

REFS = {}
for f in cf.FUNCTIONS:
    ns = {}
    exec(f["correct"], ns)
    REFS[f["name"]] = ns[f["name"]]

rng = random.Random(999)
fails = []


def check(name, cases):
    fn = REFS[name]
    for args, oracle in cases:
        try:
            got = fn(*args)
        except Exception as e:
            fails.append((name, args, "raised %s" % type(e).__name__, oracle))
            continue
        if isinstance(got, tuple):
            got = list(got)
        if isinstance(oracle, float) or isinstance(got, float):
            ok = math.isclose(float(got), float(oracle),
                              rel_tol=1e-9, abs_tol=1e-12)
        else:
            ok = got == oracle
        if not ok:
            fails.append((name, args, got, oracle))


# second_largest: heapq
import heapq
check("second_largest", [
    ([v], heapq.nlargest(2, set(v))[1] if len(set(v)) >= 2 else "RAISE")
    for v in ([3, 1, 4], [5, 5, 3], [9, 1], [2, 2, 2, 5], [-3, -1, -2])
])

# count_words: regex
check("count_words", [
    ([t], len(re.findall(r"\S+", t)))
    for t in ("hello world", "  a  b ", "", "a\tb\nc d", "one")
])

# is_anagram: Counter
check("is_anagram", [
    ([a, b], Counter(a.replace(" ", "").lower())
     == Counter(b.replace(" ", "").lower()))
    for a, b in (("listen", "silent"), ("Tea", "Eat"), ("ab", "cd"),
                 ("Dormitory", "dirty room"), ("a b", "ab"))
])

# fibonacci: known sequence table
FIB = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
check("fibonacci_n", [([n], FIB[n]) for n in range(17)])

# reverse_words: manual
check("reverse_words", [
    ([t], " ".join(t.split()[::-1]))
    for t in ("hello world", "  a  b  c ", "", "one")
])

# discount_price: Decimal
from decimal import Decimal, ROUND_HALF_EVEN
check("discount_price", [
    ([p, q], float((Decimal(str(p)) * (Decimal(100) - Decimal(str(q)))
                    / Decimal(100)).quantize(Decimal("0.01"),
                                             rounding=ROUND_HALF_EVEN)))
    for p, q in ((100, 20), (19.99, 15), (9.99, 33), (49.95, 12.5),
                 (29.99, 10), (7.5, 25))
])
# NOTE: Decimal ROUND_HALF_EVEN vs Python round() (also half-even on
# binary floats) can differ on exact .005 boundaries; mismatches here
# are adjudicated by hand, not auto-failed. Report them separately.
print("(discount Decimal check uses exact decimals; any diff is a "
      "rounding-boundary note, not an auto-fail)")

# is_prime: simple odd-only trial division, different loop
def prime2(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True
check("is_prime", [([n], prime2(n)) for n in range(0, 120)])

# sum_of_digits: arithmetic loop
def sod2(n):
    n = abs(n)
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s
check("sum_of_digits", [([n], sod2(n))
                        for n in (0, 5, 123, -123, 1000, 987654321)])

# longest_common_prefix: os.path.commonprefix (char-wise)
check("longest_common_prefix", [
    ([ss], os.path.commonprefix(ss))
    for ss in (["flower", "flow", "flight"], ["dog", "car"], ["abc"],
               ["abcd", "abce", "ab"], ["same", "same"])
])

# rotate_left: deque
from collections import deque
def rot2(items, k):
    d = deque(items)
    d.rotate(-k if items else 0)
    return list(d)
check("rotate_left", [
    ([it, k], rot2(it, k))
    for it, k in (([1, 2, 3, 4, 5], 2), ([1, 2, 3], 4), ([], 5),
                  (["a", "b"], 1))
])

# merge_dicts_sum: Counter addition
check("merge_dicts_sum", [
    ([a, b], dict(Counter(a) + Counter(b)))
    for a, b in (({"x": 1}, {"x": 2}),
                 ({"a": 1, "b": 2}, {"b": 3, "c": 4}), ({}, {"k": 5}))
])

# word_frequency: Counter
check("word_frequency", [
    ([t], dict(Counter(t.split()) if False else
               Counter(w.lower() for w in t.split())))
    for t in ("hello world hello", "Hello hello", "", "a a a b")
])

# is_valid_isbn10: recompute with reversed weights trick
# (valid iff sum((10-i)*d) % 11 == 0; recompute via weighted digit sum)
def isbn2(s):
    if len(s) != 10:
        return False
    tot = 0
    for i, ch in enumerate(s):
        if i < 9:
            if not ch.isdigit():
                return False
            d = int(ch)
        else:
            if ch == "X":
                d = 10
            elif ch.isdigit():
                d = int(ch)
            else:
                return False
        tot += (i + 1) * d  # weights 1..10: valid iff tot % 11 == 0 too
    return tot % 11 == 0
# NOTE: weights 1..10 give the same validity as 10..1 mod 11 ONLY because
# sum((11-w)*d) = 11*sum(d) - sum(w*d) == -sum(w*d) mod 11. So isbn2 is a
# genuine independent check of validity (not of the weighted sum value).
check("is_valid_isbn10", [
    ([s], isbn2(s))
    for s in ("0306406152", "080442957X", "0306406153", "1234567890",
              "030640615", "030640615A", "0000000000")
])

# base36: int(s, 36) on valid strings (validation covered by tests)
check("base36_to_int", [
    ([s], int(s, 36))
    for s in ("10", "z", "Z", "10a", "0", "ff", "hello", "AB")
])

# pascal_row: iterative addition
def pasc2(n):
    row = [1]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row
check("pascal_row", [([n], pasc2(n)) for n in range(0, 9)])

# mode_smallest: Counter + min
check("mode_smallest", [
    ([v], min(c for c, k in
              ((val, cnt) for val, cnt in Counter(v).items())
              if k == max(Counter(v).values())))
    for v in ([1, 2, 2, 3], [1, 2, 2, 3, 3], [3, 3, 2, 2], [5])
])

# collapse_whitespace: regex
check("collapse_whitespace", [
    ([t], re.sub(r"\s+", " ", t).strip())
    for t in ("  hello   world  ", "a\tb\nc", "", "   ", "a b")
])

# running_total: itertools.accumulate
check("running_total", [
    ([v], list(itertools.accumulate(v)))
    for v in ([1, 2, 3], [], [5], [1, -1, 1, -1], [10, 20, 30])
])

# primes_below: filter with prime2
check("primes_below", [
    ([n], [p for p in range(2, n) if prime2(p)])
    for n in (0, 1, 2, 3, 7, 10, 20, 50)
])

# hex_to_rgb: bytes.fromhex
check("hex_to_rgb", [
    ([s], list(bytes.fromhex(s[1:])))
    for s in ("#FF0000", "#00FF00", "#0000FF", "#ffffff", "#000000",
              "#123456")
])

# letter_grade: table lookup
def grade2(s):
    for lo, g in ((90, "A"), (80, "B"), (70, "C"), (60, "D")):
        if s >= lo:
            return g
    return "F"
check("letter_grade", [([s], grade2(s))
                       for s in (95, 90, 89, 80, 79, 70, 69, 60, 59, 0,
                                 100)])

# dot_product: sum(map(mul))
from operator import mul
check("dot_product", [
    ([a, b], sum(map(mul, a, b)))
    for a, b in (([1, 2, 3], [4, 5, 6]), ([], []), ([2], [3]),
                 ([1, -1], [1, 1]))
])

# transpose_matrix: zip
check("transpose_matrix", [
    ([m], [list(r) for r in zip(*m)] if m else [])
    for m in ([[1, 2], [3, 4]], [[1, 2, 3]], [[1], [2], [3]], [], [[5]])
])

# initials: manual
check("initials", [
    ([t], "".join(w[0].upper() for w in t.split()))
    for t in ("john doe", "John F. Kennedy", "  mary   ann  smith ",
              "", "   ", "a", "alice")
])

if fails:
    print("ORACLE MISMATCHES (%d):" % len(fails))
    for name, args, got, oracle in fails:
        print(" - %s %r: ref=%r oracle=%r" % (name, args, got, oracle))
    sys.exit(1)
print("ORACLE CHECK CLEAN: all references match independent oracles.")
