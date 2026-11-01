#!/usr/bin/env python3
"""Calculator-floor materials builder + construction QA (item 1).

Builds 100 held-out JEV-style decision items (50 (a) + 50 (b)) from 25
FRESH functions (none reused from jev-items, jev-items-hard, or
jev-lag-items). Ground truth comes from CONSTRUCTION labels: the
reference implementation is known-correct by authoring, buggy variants
are known-buggy by injected mutation. The calculator (test suites) is
measured against those labels -- never the reverse.

QA phase (this script): reference-vs-test agreement + mutation
behavior-change checks. Adjudication of any QA mismatch uses the SPEC
and independent oracles, never the separation outcome. The measurement
(run by jev-calculator-floor-measure.py) runs AFTER QA is clean, with
no further edits to materials.

Test format: {"n": name, "a": [args...], "e": expected} or
{"n": name, "a": [args...], "r": "ValueError"}.
Probes: extra inputs for the mutation differential check (beyond tests).
"""

import json
import math
import random
import sys

FUNCTIONS = [
    # 1. second_largest
    {
        "name": "second_largest",
        "desc": "Second-largest distinct value. second_largest(values)",
        "spec": "Return the second-largest distinct value in values. Raise "
                "ValueError if values contains fewer than two distinct values.",
        "correct": (
            "def second_largest(values):\n"
            "    distinct = sorted(set(values), reverse=True)\n"
            "    if len(distinct) < 2:\n"
            "        raise ValueError('need at least two distinct values')\n"
            "    return distinct[1]\n"
        ),
        "buggy_a": (
            "def second_largest(values):\n"
            "    ordered = sorted(values, reverse=True)\n"
            "    if len(ordered) < 2:\n"
            "        raise ValueError('need at least two distinct values')\n"
            "    return ordered[1]\n"
        ),
        "buggy_b": (
            "def second_largest(values):\n"
            "    distinct = sorted(set(values))\n"
            "    if len(distinct) < 2:\n"
            "        raise ValueError('need at least two distinct values')\n"
            "    return distinct[1]\n"
        ),
        "tests": [
            {"n": "basic", "a": [[5, 3, 8]], "e": 5},
            {"n": "duplicates", "a": [[5, 5, 3]], "e": 3},
            {"n": "two", "a": [[1, 2]], "e": 1},
            {"n": "dup-max", "a": [[9, 9, 9, 7]], "e": 7},
            {"n": "mixed", "a": [[3, 1, 4, 1, 5, 9, 2, 6]], "e": 6},
            {"n": "negatives", "a": [[-1, -5, -3]], "e": -3},
            {"n": "dup-mid", "a": [[10, 20, 20, 30]], "e": 20},
            {"n": "empty", "a": [[]], "r": "ValueError"},
            {"n": "single", "a": [[7]], "r": "ValueError"},
            {"n": "all-same", "a": [[4, 4, 4]], "r": "ValueError"},
        ],
        "probes": [[[1, 5, 9, 3]], [[8, 8, 2]]],
    },
    # 2. count_words
    {
        "name": "count_words",
        "desc": "Word count. count_words(text)",
        "spec": "Count words in text, splitting on any whitespace. Empty or "
                "whitespace-only text has 0 words.",
        "correct": (
            "def count_words(text):\n"
            "    return len(text.split())\n"
        ),
        "buggy_a": (
            "def count_words(text):\n"
            "    return len(text.split(' '))\n"
        ),
        "buggy_b": (
            "def count_words(text):\n"
            "    if not text:\n"
            "        return 0\n"
            "    return text.count(' ') + 1\n"
        ),
        "tests": [
            {"n": "two", "a": ["hello world"], "e": 2},
            {"n": "messy-spaces", "a": ["  hello   world  "], "e": 2},
            {"n": "empty", "a": [""], "e": 0},
            {"n": "spaces-only", "a": ["   "], "e": 0},
            {"n": "one", "a": ["one"], "e": 1},
            {"n": "tabs-newlines", "a": ["a\tb\nc"], "e": 3},
            {"n": "punct", "a": ["hello, world!"], "e": 2},
            {"n": "five", "a": ["a b c d e"], "e": 5},
        ],
        "probes": [["x\ty"], ["  a  b  "]],
    },
    # 3. is_anagram
    {
        "name": "is_anagram",
        "desc": "Anagram check, case-insensitive, spaces ignored. is_anagram(a, b)",
        "spec": "Return True if a and b are anagrams, ignoring case and spaces.",
        "correct": (
            "def is_anagram(a, b):\n"
            "    norm_a = sorted(a.replace(' ', '').lower())\n"
            "    norm_b = sorted(b.replace(' ', '').lower())\n"
            "    return norm_a == norm_b\n"
        ),
        "buggy_a": (
            "def is_anagram(a, b):\n"
            "    norm_a = sorted(a.replace(' ', ''))\n"
            "    norm_b = sorted(b.replace(' ', ''))\n"
            "    return norm_a == norm_b\n"
        ),
        "buggy_b": (
            "def is_anagram(a, b):\n"
            "    norm_a = sorted(a.lower())\n"
            "    norm_b = sorted(b.lower())\n"
            "    return norm_a == norm_b\n"
        ),
        "tests": [
            {"n": "basic", "a": ["listen", "silent"], "e": True},
            {"n": "case", "a": ["Listen", "Silent"], "e": True},
            {"n": "spaces", "a": ["a b", "ab"], "e": True},
            {"n": "no", "a": ["hello", "world"], "e": False},
            {"n": "empty", "a": ["", ""], "e": True},
            {"n": "single", "a": ["a", "a"], "e": True},
            {"n": "swap", "a": ["ab", "ba"], "e": True},
            {"n": "near", "a": ["abc", "abd"], "e": False},
            {"n": "phrase", "a": ["Dormitory", "dirty room"], "e": True},
        ],
        "probes": [["Tea", "Eat"], ["a b c", "abc"]],
    },
    # 4. fibonacci_n
    {
        "name": "fibonacci_n",
        "desc": "nth Fibonacci number, 0-indexed. fibonacci_n(n)",
        "spec": "Return the nth Fibonacci number, 0-indexed (fib(0)=0, "
                "fib(1)=1). Raise ValueError for negative n.",
        "correct": (
            "def fibonacci_n(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    a, b = 0, 1\n"
            "    for _ in range(n):\n"
            "        a, b = b, a + b\n"
            "    return a\n"
        ),
        "buggy_a": (
            "def fibonacci_n(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    a, b = 1, 1\n"
            "    for _ in range(n):\n"
            "        a, b = b, a + b\n"
            "    return a\n"
        ),
        "buggy_b": (
            "def fibonacci_n(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    a, b = 0, 1\n"
            "    for _ in range(n):\n"
            "        a, b = b, a + b\n"
            "    return b\n"
        ),
        "tests": [
            {"n": "f0", "a": [0], "e": 0},
            {"n": "f1", "a": [1], "e": 1},
            {"n": "f2", "a": [2], "e": 1},
            {"n": "f3", "a": [3], "e": 2},
            {"n": "f4", "a": [4], "e": 3},
            {"n": "f5", "a": [5], "e": 5},
            {"n": "f10", "a": [10], "e": 55},
            {"n": "f15", "a": [15], "e": 610},
            {"n": "neg", "a": [-1], "r": "ValueError"},
        ],
        "probes": [[6], [7]],
    },
    # 5. reverse_words
    {
        "name": "reverse_words",
        "desc": "Reverse word order. reverse_words(text)",
        "spec": "Reverse the order of words in text, joining with single "
                "spaces. Leading, trailing, and multiple whitespace is "
                "normalized. Empty text gives empty string.",
        "correct": (
            "def reverse_words(text):\n"
            "    return ' '.join(text.split()[::-1])\n"
        ),
        "buggy_a": (
            "def reverse_words(text):\n"
            "    return ' '.join(reversed(text.split(' ')))\n"
        ),
        "buggy_b": (
            "def reverse_words(text):\n"
            "    return ' '.join(w[::-1] for w in text.split())\n"
        ),
        "tests": [
            {"n": "two", "a": ["hello world"], "e": "world hello"},
            {"n": "messy", "a": ["  hello   world  "], "e": "world hello"},
            {"n": "empty", "a": [""], "e": ""},
            {"n": "one", "a": ["one"], "e": "one"},
            {"n": "three", "a": ["a b c"], "e": "c b a"},
            {"n": "punct", "a": ["hello, world!"], "e": "world! hello,"},
        ],
        "probes": [["x  y  z"]],
    },
    # 6. discount_price
    {
        "name": "discount_price",
        "desc": "Discounted price, 2 decimals. discount_price(price, pct)",
        "spec": "Return price reduced by pct percent, rounded to 2 decimals. "
                "Raise ValueError if price < 0 or pct is outside 0..100.",
        "correct": (
            "def discount_price(price, pct):\n"
            "    if price < 0 or pct < 0 or pct > 100:\n"
            "        raise ValueError('price >= 0 and 0 <= pct <= 100')\n"
            "    return round(price * (1 - pct / 100), 2)\n"
        ),
        "buggy_a": (
            "def discount_price(price, pct):\n"
            "    if price < 0 or pct < 0 or pct > 100:\n"
            "        raise ValueError('price >= 0 and 0 <= pct <= 100')\n"
            "    return price * (1 - pct / 100)\n"
        ),
        "buggy_b": (
            "def discount_price(price, pct):\n"
            "    if price < 0 or pct < 0 or pct > 100:\n"
            "        raise ValueError('price >= 0 and 0 <= pct <= 100')\n"
            "    return round(price * (pct / 100), 2)\n"
        ),
        "tests": [
            {"n": "basic", "a": [100, 20], "e": 80.0},
            {"n": "rounding1", "a": [19.99, 15], "e": 16.99},
            {"n": "rounding2", "a": [9.99, 33], "e": 6.69},
            {"n": "rounding3", "a": [49.95, 12.5], "e": 43.71},
            {"n": "zero-price", "a": [0, 50], "e": 0.0},
            {"n": "zero-pct", "a": [50, 0], "e": 50.0},
            {"n": "full", "a": [50, 100], "e": 0.0},
            {"n": "neg-price", "a": [-5, 10], "r": "ValueError"},
            {"n": "neg-pct", "a": [50, -1], "r": "ValueError"},
            {"n": "over-pct", "a": [50, 101], "r": "ValueError"},
        ],
        "probes": [[29.99, 10], [7.5, 25]],
    },
    # 7. is_prime
    {
        "name": "is_prime",
        "desc": "Primality test. is_prime(n)",
        "spec": "Return True if n is prime, False otherwise. Values below 2 "
                "are not prime.",
        "correct": (
            "def is_prime(n):\n"
            "    if n < 2:\n"
            "        return False\n"
            "    d = 2\n"
            "    while d * d <= n:\n"
            "        if n % d == 0:\n"
            "            return False\n"
            "        d += 1\n"
            "    return True\n"
        ),
        "buggy_a": (
            "def is_prime(n):\n"
            "    if n < 2:\n"
            "        return True\n"
            "    d = 2\n"
            "    while d * d <= n:\n"
            "        if n % d == 0:\n"
            "            return False\n"
            "        d += 1\n"
            "    return True\n"
        ),
        "buggy_b": (
            "def is_prime(n):\n"
            "    if n < 2:\n"
            "        return False\n"
            "    if n % 2 == 0:\n"
            "        return n == 2\n"
            "    if n % 3 == 0:\n"
            "        return n == 3\n"
            "    return True\n"
        ),
        "tests": [
            {"n": "two", "a": [2], "e": True},
            {"n": "three", "a": [3], "e": True},
            {"n": "four", "a": [4], "e": False},
            {"n": "five", "a": [5], "e": True},
            {"n": "nine", "a": [9], "e": False},
            {"n": "seventeen", "a": [17], "e": True},
            {"n": "twentyfive", "a": [25], "e": False},
            {"n": "twentynine", "a": [29], "e": True},
            {"n": "fortynine", "a": [49], "e": False},
            {"n": "one", "a": [1], "e": False},
            {"n": "zero", "a": [0], "e": False},
            {"n": "ninetyseven", "a": [97], "e": True},
        ],
        "probes": [[35], [121]],
    },
    # 8. sum_of_digits
    {
        "name": "sum_of_digits",
        "desc": "Digit sum of absolute value. sum_of_digits(n)",
        "spec": "Return the sum of the decimal digits of the absolute value "
                "of n.",
        "correct": (
            "def sum_of_digits(n):\n"
            "    return sum(int(d) for d in str(abs(n)))\n"
        ),
        "buggy_a": (
            "def sum_of_digits(n):\n"
            "    return sum(int(d) for d in str(n))\n"
        ),
        "buggy_b": (
            "def sum_of_digits(n):\n"
            "    return sum(int(d) for d in str(abs(n))[:-1]) if abs(n) >= 10 else 0\n"
        ),
        "tests": [
            {"n": "basic", "a": [123], "e": 6},
            {"n": "zero", "a": [0], "e": 0},
            {"n": "nines", "a": [999], "e": 27},
            {"n": "negative", "a": [-123], "e": 6},
            {"n": "thousand", "a": [1000], "e": 1},
            {"n": "single", "a": [5], "e": 5},
            {"n": "long", "a": [987654321], "e": 45},
        ],
        "probes": [[-99], [10]],
    },
    # 9. longest_common_prefix
    {
        "name": "longest_common_prefix",
        "desc": "Longest common prefix. longest_common_prefix(strs)",
        "spec": "Return the longest string that is a prefix of every string "
                "in strs. Empty list gives empty string.",
        "correct": (
            "def longest_common_prefix(strs):\n"
            "    if not strs:\n"
            "        return ''\n"
            "    prefix = []\n"
            "    for chars in zip(*strs):\n"
            "        if len(set(chars)) == 1:\n"
            "            prefix.append(chars[0])\n"
            "        else:\n"
            "            break\n"
            "    return ''.join(prefix)\n"
        ),
        "buggy_a": (
            "def longest_common_prefix(strs):\n"
            "    if not strs:\n"
            "        return ''\n"
            "    if len(strs) == 1:\n"
            "        return strs[0]\n"
            "    prefix = []\n"
            "    for chars in zip(strs[0], strs[1]):\n"
            "        if chars[0] == chars[1]:\n"
            "            prefix.append(chars[0])\n"
            "        else:\n"
            "            break\n"
            "    return ''.join(prefix)\n"
        ),
        "buggy_b": (
            "def longest_common_prefix(strs):\n"
            "    if not strs:\n"
            "        return ''\n"
            "    shortest = min(len(s) for s in strs)\n"
            "    return strs[0][:shortest]\n"
        ),
        "tests": [
            {"n": "flower", "a": [["flower", "flow", "flight"]], "e": "fl"},
            {"n": "none", "a": [["dog", "racecar", "car"]], "e": ""},
            {"n": "empty-list", "a": [[]], "e": ""},
            {"n": "single", "a": [["abc"]], "e": "abc"},
            {"n": "third-short", "a": [["abcd", "abce", "ab"]], "e": "ab"},
            {"n": "with-empty", "a": [["", "abc"]], "e": ""},
            {"n": "all-same", "a": [["same", "same", "same"]], "e": "same"},
            {"n": "pair", "a": [["ab", "ab"]], "e": "ab"},
        ],
        "probes": [[["abc", "abd", "abx"]]],
    },
    # 10. rotate_left
    {
        "name": "rotate_left",
        "desc": "Rotate list left. rotate_left(items, k)",
        "spec": "Rotate items left by k positions, with k normalized modulo "
                "the length. Empty list gives empty list.",
        "correct": (
            "def rotate_left(items, k):\n"
            "    if not items:\n"
            "        return []\n"
            "    k = k % len(items)\n"
            "    return items[k:] + items[:k]\n"
        ),
        "buggy_a": (
            "def rotate_left(items, k):\n"
            "    if not items:\n"
            "        return []\n"
            "    return items[k:] + items[:k]\n"
        ),
        "buggy_b": (
            "def rotate_left(items, k):\n"
            "    if not items:\n"
            "        return []\n"
            "    k = k % len(items)\n"
            "    return items[-k:] + items[:-k] if k else items[:]\n"
        ),
        "tests": [
            {"n": "basic", "a": [[1, 2, 3, 4, 5], 2], "e": [3, 4, 5, 1, 2]},
            {"n": "zero", "a": [[1, 2, 3], 0], "e": [1, 2, 3]},
            {"n": "full", "a": [[1, 2, 3], 3], "e": [1, 2, 3]},
            {"n": "over", "a": [[1, 2, 3], 4], "e": [2, 3, 1]},
            {"n": "empty", "a": [[], 5], "e": []},
            {"n": "strings", "a": [["a", "b"], 1], "e": ["b", "a"]},
            {"n": "single", "a": [[1], 7], "e": [1]},
        ],
        "probes": [[[1, 2, 3, 4], 5]],
    },
    # 11. merge_dicts_sum
    {
        "name": "merge_dicts_sum",
        "desc": "Merge dicts summing shared keys. merge_dicts_sum(a, b)",
        "spec": "Return a new dict with the union of keys; values for keys "
                "present in both dicts are summed. Inputs are not mutated.",
        "correct": (
            "def merge_dicts_sum(a, b):\n"
            "    out = {}\n"
            "    for k in set(a) | set(b):\n"
            "        out[k] = a.get(k, 0) + b.get(k, 0)\n"
            "    return out\n"
        ),
        "buggy_a": (
            "def merge_dicts_sum(a, b):\n"
            "    out = dict(a)\n"
            "    out.update(b)\n"
            "    return out\n"
        ),
        "buggy_b": (
            "def merge_dicts_sum(a, b):\n"
            "    out = {}\n"
            "    for k in set(a) & set(b):\n"
            "        out[k] = a[k] + b[k]\n"
            "    return out\n"
        ),
        "tests": [
            {"n": "shared", "a": [{"x": 1}, {"x": 2}], "e": {"x": 3}},
            {"n": "mixed", "a": [{"a": 1, "b": 2}, {"b": 3, "c": 4}], "e": {"a": 1, "b": 5, "c": 4}},
            {"n": "left-empty", "a": [{}, {"k": 5}], "e": {"k": 5}},
            {"n": "right-empty", "a": [{"k": 5}, {}], "e": {"k": 5}},
            {"n": "both-empty", "a": [{}, {}], "e": {}},
            {"n": "cancel", "a": [{"x": -1}, {"x": 1}], "e": {"x": 0}},
        ],
        "probes": [[{"a": 1}, {"b": 2}]],
    },
    # 12. unique_sorted
    {
        "name": "unique_sorted",
        "desc": "Sorted unique values. unique_sorted(values)",
        "spec": "Return the distinct values of values in ascending order.",
        "correct": (
            "def unique_sorted(values):\n"
            "    return sorted(set(values))\n"
        ),
        "buggy_a": (
            "def unique_sorted(values):\n"
            "    return sorted(values)\n"
        ),
        "buggy_b": (
            "def unique_sorted(values):\n"
            "    return sorted(set(values), reverse=True)\n"
        ),
        "tests": [
            {"n": "basic", "a": [[3, 1, 2]], "e": [1, 2, 3]},
            {"n": "dups", "a": [[3, 1, 3]], "e": [1, 3]},
            {"n": "empty", "a": [[]], "e": []},
            {"n": "all-same", "a": [[5, 5, 5]], "e": [5]},
            {"n": "neg", "a": [[2, -1, 2, 0]], "e": [-1, 0, 2]},
        ],
        "probes": [[[4, 4, 1]]],
    },
    # 13. word_frequency
    {
        "name": "word_frequency",
        "desc": "Lowercased word counts. word_frequency(text)",
        "spec": "Return a dict mapping each lowercase word in text to its "
                "count, splitting on whitespace. Empty text gives {}.",
        "correct": (
            "def word_frequency(text):\n"
            "    counts = {}\n"
            "    for w in text.split():\n"
            "        w = w.lower()\n"
            "        counts[w] = counts.get(w, 0) + 1\n"
            "    return counts\n"
        ),
        "buggy_a": (
            "def word_frequency(text):\n"
            "    counts = {}\n"
            "    for w in text.split():\n"
            "        counts[w] = counts.get(w, 0) + 1\n"
            "    return counts\n"
        ),
        "buggy_b": (
            "def word_frequency(text):\n"
            "    counts = {}\n"
            "    for w in text.split():\n"
            "        w = w.lower()\n"
            "        if w not in counts:\n"
            "            counts[w] = 1\n"
            "    return counts\n"
        ),
        "tests": [
            {"n": "basic", "a": ["hello world hello"], "e": {"hello": 2, "world": 1}},
            {"n": "case", "a": ["Hello hello"], "e": {"hello": 2}},
            {"n": "empty", "a": [""], "e": {}},
            {"n": "repeat", "a": ["a a a b"], "e": {"a": 3, "b": 1}},
            {"n": "distinct", "a": ["one two three"], "e": {"one": 1, "two": 1, "three": 1}},
        ],
        "probes": [["x X x"]],
    },
    # 14. is_valid_isbn10
    {
        "name": "is_valid_isbn10",
        "desc": "ISBN-10 checksum validity. is_valid_isbn10(s)",
        "spec": "Return True if s is a valid ISBN-10: exactly 10 characters, "
                "first 9 digits, last a digit or 'X' (value 10), and "
                "sum((10-i)*digit_i) divisible by 11. Anything else is False.",
        "correct": (
            "def is_valid_isbn10(s):\n"
            "    if len(s) != 10:\n"
            "        return False\n"
            "    total = 0\n"
            "    for i, ch in enumerate(s):\n"
            "        if i < 9:\n"
            "            if not ch.isdigit():\n"
            "                return False\n"
            "            d = int(ch)\n"
            "        else:\n"
            "            if ch == 'X':\n"
            "                d = 10\n"
            "            elif ch.isdigit():\n"
            "                d = int(ch)\n"
            "            else:\n"
            "                return False\n"
            "        total += (10 - i) * d\n"
            "    return total % 11 == 0\n"
        ),
        "buggy_a": (
            "def is_valid_isbn10(s):\n"
            "    if len(s) != 10:\n"
            "        return False\n"
            "    total = 0\n"
            "    for i, ch in enumerate(s):\n"
            "        if not ch.isdigit():\n"
            "            return False\n"
            "        total += (10 - i) * int(ch)\n"
            "    return total % 11 == 0\n"
        ),
        "buggy_b": (
            "def is_valid_isbn10(s):\n"
            "    if len(s) != 10:\n"
            "        return False\n"
            "    total = 0\n"
            "    for i, ch in enumerate(s):\n"
            "        if i < 9:\n"
            "            if not ch.isdigit():\n"
            "                return False\n"
            "            d = int(ch)\n"
            "        else:\n"
            "            if ch == 'X':\n"
            "                d = 10\n"
            "            elif ch.isdigit():\n"
            "                d = int(ch)\n"
            "            else:\n"
            "                return False\n"
            "        total += (10 - i) * d\n"
            "    return total % 10 == 0\n"
        ),
        "tests": [
            {"n": "valid", "a": ["0306406152"], "e": True},
            {"n": "valid-x", "a": ["080442957X"], "e": True},
            {"n": "bad-check", "a": ["0306406153"], "e": False},
            {"n": "all-digits-bad", "a": ["1234567890"], "e": False},
            {"n": "short", "a": ["030640615"], "e": False},
            {"n": "long", "a": ["03064061522"], "e": False},
            {"n": "bad-char", "a": ["030640615A"], "e": False},
            {"n": "zeros", "a": ["0000000000"], "e": True},
        ],
        "probes": [["123456789X"]],
    },
    # 15. base36_to_int
    {
        "name": "base36_to_int",
        "desc": "Base-36 string to int. base36_to_int(s)",
        "spec": "Return the integer value of base-36 string s (digits and "
                "letters, either case). Raise ValueError for empty strings "
                "or any character outside 0-9a-zA-Z (including signs and "
                "whitespace).",
        "correct": (
            "def base36_to_int(s):\n"
            "    if not s:\n"
            "        raise ValueError('empty string')\n"
            "    ok = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\n"
            "    for ch in s:\n"
            "        if ch not in ok:\n"
            "            raise ValueError('bad base-36 character')\n"
            "    return int(s, 36)\n"
        ),
        "buggy_a": (
            "def base36_to_int(s):\n"
            "    if not s:\n"
            "        raise ValueError('empty string')\n"
            "    ok = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\n"
            "    for ch in s:\n"
            "        if ch not in ok:\n"
            "            raise ValueError('bad base-36 character')\n"
            "    return int(s)\n"
        ),
        "buggy_b": (
            "def base36_to_int(s):\n"
            "    if not s:\n"
            "        raise ValueError('empty string')\n"
            "    ok = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\n"
            "    for ch in s.strip():\n"
            "        if ch not in ok:\n"
            "            raise ValueError('bad base-36 character')\n"
            "    return int(s.strip(), 36)\n"
        ),
        "tests": [
            {"n": "ten", "a": ["10"], "e": 36},
            {"n": "z", "a": ["z"], "e": 35},
            {"n": "cap-z", "a": ["Z"], "e": 35},
            {"n": "mixed", "a": ["10a"], "e": 1306},
            {"n": "zero", "a": ["0"], "e": 0},
            {"n": "ff", "a": ["ff"], "e": 555},
            {"n": "hello", "a": ["hello"], "e": 29234652},
            {"n": "empty", "a": [""], "r": "ValueError"},
            {"n": "space", "a": ["1 0"], "r": "ValueError"},
            {"n": "sign", "a": ["-10"], "r": "ValueError"},
            {"n": "bang", "a": ["10!"], "r": "ValueError"},
            {"n": "dot", "a": ["3.5"], "r": "ValueError"},
        ],
        "probes": [[" 10"], ["AB"]],
    },
    # 16. pascal_row
    {
        "name": "pascal_row",
        "desc": "Pascal triangle row. pascal_row(n)",
        "spec": "Return row n (0-indexed) of Pascal's triangle as a list. "
                "Raise ValueError for negative n.",
        "correct": (
            "import math\n"
            "def pascal_row(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    return [math.comb(n, k) for k in range(n + 1)]\n"
        ),
        "buggy_a": (
            "import math\n"
            "def pascal_row(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    return [math.comb(n, k) for k in range(n)]\n"
        ),
        "buggy_b": (
            "import math\n"
            "def pascal_row(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be >= 0')\n"
            "    return [math.comb(n + 1, k) for k in range(n + 2)]\n"
        ),
        "tests": [
            {"n": "row0", "a": [0], "e": [1]},
            {"n": "row1", "a": [1], "e": [1, 1]},
            {"n": "row2", "a": [2], "e": [1, 2, 1]},
            {"n": "row3", "a": [3], "e": [1, 3, 3, 1]},
            {"n": "row5", "a": [5], "e": [1, 5, 10, 10, 5, 1]},
            {"n": "neg", "a": [-1], "r": "ValueError"},
        ],
        "probes": [[4]],
    },
    # 17. mode_smallest
    {
        "name": "mode_smallest",
        "desc": "Most frequent value, ties to smallest. mode_smallest(values)",
        "spec": "Return the most frequent value in values; on ties return "
                "the smallest among the most frequent. Raise ValueError "
                "for empty input.",
        "correct": (
            "def mode_smallest(values):\n"
            "    if not values:\n"
            "        raise ValueError('empty input')\n"
            "    counts = {}\n"
            "    for v in values:\n"
            "        counts[v] = counts.get(v, 0) + 1\n"
            "    top = max(counts.values())\n"
            "    return min(v for v, c in counts.items() if c == top)\n"
        ),
        "buggy_a": (
            "def mode_smallest(values):\n"
            "    if not values:\n"
            "        raise ValueError('empty input')\n"
            "    counts = {}\n"
            "    for v in values:\n"
            "        counts[v] = counts.get(v, 0) + 1\n"
            "    top = max(counts.values())\n"
            "    return max(v for v, c in counts.items() if c == top)\n"
        ),
        "buggy_b": (
            "def mode_smallest(values):\n"
            "    if not values:\n"
            "        raise ValueError('empty input')\n"
            "    counts = {}\n"
            "    order = []\n"
            "    for v in values:\n"
            "        if v not in counts:\n"
            "            order.append(v)\n"
            "        counts[v] = counts.get(v, 0) + 1\n"
            "    top = max(counts.values())\n"
            "    for v in order:\n"
            "        if counts[v] == top:\n"
            "            return v\n"
            "    return order[0]\n"
        ),
        "tests": [
            {"n": "basic", "a": [[1, 2, 2, 3]], "e": 2},
            {"n": "tie", "a": [[1, 2, 2, 3, 3]], "e": 2},
            {"n": "tie-rev", "a": [[3, 3, 2, 2]], "e": 2},
            {"n": "single", "a": [[5]], "e": 5},
            {"n": "three-way", "a": [[1, 1, 1, 2, 2, 2]], "e": 1},
            {"n": "empty", "a": [[]], "r": "ValueError"},
        ],
        "probes": [[[4, 4, 1, 1, 2]]],
    },
    # 18. collapse_whitespace
    {
        "name": "collapse_whitespace",
        "desc": "Normalize whitespace. collapse_whitespace(text)",
        "spec": "Return text with leading/trailing whitespace stripped and "
                "every run of whitespace collapsed to a single space.",
        "correct": (
            "def collapse_whitespace(text):\n"
            "    return ' '.join(text.split())\n"
        ),
        "buggy_a": (
            "def collapse_whitespace(text):\n"
            "    return text.strip().replace('  ', ' ')\n"
        ),
        "buggy_b": (
            "def collapse_whitespace(text):\n"
            "    return ' '.join(text.split(' '))\n"
        ),
        "tests": [
            {"n": "messy", "a": ["  hello   world  "], "e": "hello world"},
            {"n": "tabs", "a": ["a\tb\nc"], "e": "a b c"},
            {"n": "empty", "a": [""], "e": ""},
            {"n": "spaces-only", "a": ["   "], "e": ""},
            {"n": "one", "a": ["one"], "e": "one"},
            {"n": "clean", "a": ["a b"], "e": "a b"},
        ],
        "probes": [["x   y"]],
    },
    # 19. running_total
    {
        "name": "running_total",
        "desc": "Prefix sums. running_total(values)",
        "spec": "Return the running totals (prefix sums) of values. Empty "
                "input gives empty list.",
        "correct": (
            "def running_total(values):\n"
            "    out = []\n"
            "    total = 0\n"
            "    for v in values:\n"
            "        total += v\n"
            "        out.append(total)\n"
            "    return out\n"
        ),
        "buggy_a": (
            "def running_total(values):\n"
            "    out = [0]\n"
            "    total = 0\n"
            "    for v in values:\n"
            "        total += v\n"
            "        out.append(total)\n"
            "    return out\n"
        ),
        "buggy_b": (
            "def running_total(values):\n"
            "    out = []\n"
            "    total = 0\n"
            "    for v in values[1:]:\n"
            "        total += v\n"
            "        out.append(total)\n"
            "    return out\n"
        ),
        "tests": [
            {"n": "basic", "a": [[1, 2, 3]], "e": [1, 3, 6]},
            {"n": "empty", "a": [[]], "e": []},
            {"n": "single", "a": [[5]], "e": [5]},
            {"n": "neg", "a": [[1, -1, 1, -1]], "e": [1, 0, 1, 0]},
            {"n": "tens", "a": [[10, 20, 30]], "e": [10, 30, 60]},
        ],
        "probes": [[[2, 2, 2]]],
    },
    # 20. primes_below
    {
        "name": "primes_below",
        "desc": "Primes below n. primes_below(n)",
        "spec": "Return the list of primes p with 2 <= p < n, ascending. "
                "n <= 2 gives empty list.",
        "correct": (
            "def primes_below(n):\n"
            "    if n <= 2:\n"
            "        return []\n"
            "    sieve = [True] * n\n"
            "    sieve[0] = sieve[1] = False\n"
            "    d = 2\n"
            "    while d * d < n:\n"
            "        if sieve[d]:\n"
            "            for m in range(d * d, n, d):\n"
            "                sieve[m] = False\n"
            "        d += 1\n"
            "    return [i for i, p in enumerate(sieve) if p]\n"
        ),
        "buggy_a": (
            "def primes_below(n):\n"
            "    if n < 2:\n"
            "        return []\n"
            "    sieve = [True] * (n + 1)\n"
            "    sieve[0] = sieve[1] = False\n"
            "    d = 2\n"
            "    while d * d <= n:\n"
            "        if sieve[d]:\n"
            "            for m in range(d * d, n + 1, d):\n"
            "                sieve[m] = False\n"
            "        d += 1\n"
            "    return [i for i, p in enumerate(sieve) if p]\n"
        ),
        "buggy_b": (
            "def primes_below(n):\n"
            "    if n <= 2:\n"
            "        return []\n"
            "    sieve = [True] * n\n"
            "    sieve[0] = False\n"
            "    d = 2\n"
            "    while d * d < n:\n"
            "        if sieve[d]:\n"
            "            for m in range(d * d, n, d):\n"
            "                sieve[m] = False\n"
            "        d += 1\n"
            "    return [i for i, p in enumerate(sieve) if p]\n"
        ),
        "tests": [
            {"n": "two", "a": [2], "e": []},
            {"n": "three", "a": [3], "e": [2]},
            {"n": "seven", "a": [7], "e": [2, 3, 5]},
            {"n": "ten", "a": [10], "e": [2, 3, 5, 7]},
            {"n": "twenty", "a": [20], "e": [2, 3, 5, 7, 11, 13, 17, 19]},
            {"n": "one", "a": [1], "e": []},
            {"n": "zero", "a": [0], "e": []},
        ],
        "probes": [[11], [13]],
    },
    # 21. hex_to_rgb
    {
        "name": "hex_to_rgb",
        "desc": "Hex color to RGB tuple. hex_to_rgb(s)",
        "spec": "Return (r, g, b) for 6-digit hex color s of the form "
                "'#RRGGBB' (either case). Raise ValueError for any other "
                "format.",
        "correct": (
            "def hex_to_rgb(s):\n"
            "    if len(s) != 7 or s[0] != '#':\n"
            "        raise ValueError('expected #RRGGBB')\n"
            "    try:\n"
            "        r = int(s[1:3], 16)\n"
            "        g = int(s[3:5], 16)\n"
            "        b = int(s[5:7], 16)\n"
            "    except ValueError:\n"
            "        raise ValueError('bad hex digits')\n"
            "    return (r, g, b)\n"
        ),
        "buggy_a": (
            "def hex_to_rgb(s):\n"
            "    if len(s) != 7 or s[0] != '#':\n"
            "        raise ValueError('expected #RRGGBB')\n"
            "    try:\n"
            "        r = int(s[1:3], 16)\n"
            "        g = int(s[3:5], 16)\n"
            "        b = int(s[5:7], 16)\n"
            "    except ValueError:\n"
            "        raise ValueError('bad hex digits')\n"
            "    return (b, g, r)\n"
        ),
        "buggy_b": (
            "def hex_to_rgb(s):\n"
            "    if len(s) == 4 and s[0] == '#':\n"
            "        try:\n"
            "            r = int(s[1] * 2, 16)\n"
            "            g = int(s[2] * 2, 16)\n"
            "            b = int(s[3] * 2, 16)\n"
            "        except ValueError:\n"
            "            raise ValueError('bad hex digits')\n"
            "        return (r, g, b)\n"
            "    if len(s) != 7 or s[0] != '#':\n"
            "        raise ValueError('expected #RRGGBB')\n"
            "    try:\n"
            "        r = int(s[1:3], 16)\n"
            "        g = int(s[3:5], 16)\n"
            "        b = int(s[5:7], 16)\n"
            "    except ValueError:\n"
            "        raise ValueError('bad hex digits')\n"
            "    return (r, g, b)\n"
        ),
        "tests": [
            {"n": "red", "a": ["#FF0000"], "e": [255, 0, 0]},
            {"n": "green", "a": ["#00FF00"], "e": [0, 255, 0]},
            {"n": "blue", "a": ["#0000FF"], "e": [0, 0, 255]},
            {"n": "white-lower", "a": ["#ffffff"], "e": [255, 255, 255]},
            {"n": "black", "a": ["#000000"], "e": [0, 0, 0]},
            {"n": "mixed", "a": ["#123456"], "e": [18, 52, 86]},
            {"n": "no-hash", "a": ["FF0000"], "r": "ValueError"},
            {"n": "short", "a": ["#F00"], "r": "ValueError"},
            {"n": "bad-digits", "a": ["#GGGGGG"], "r": "ValueError"},
            {"n": "five-digits", "a": ["#12345"], "r": "ValueError"},
            {"n": "empty", "a": [""], "r": "ValueError"},
        ],
        "probes": [["#102030"], ["#ABC"]],
    },
    # 22. letter_grade
    {
        "name": "letter_grade",
        "desc": "Numeric score to letter grade. letter_grade(score)",
        "spec": "Return 'A' for score >= 90, 'B' for >= 80, 'C' for >= 70, "
                "'D' for >= 60, else 'F'. Raise ValueError for scores "
                "outside 0..100.",
        "correct": (
            "def letter_grade(score):\n"
            "    if score < 0 or score > 100:\n"
            "        raise ValueError('score must be in 0..100')\n"
            "    if score >= 90:\n"
            "        return 'A'\n"
            "    if score >= 80:\n"
            "        return 'B'\n"
            "    if score >= 70:\n"
            "        return 'C'\n"
            "    if score >= 60:\n"
            "        return 'D'\n"
            "    return 'F'\n"
        ),
        "buggy_a": (
            "def letter_grade(score):\n"
            "    if score < 0 or score > 100:\n"
            "        raise ValueError('score must be in 0..100')\n"
            "    if score > 90:\n"
            "        return 'A'\n"
            "    if score > 80:\n"
            "        return 'B'\n"
            "    if score > 70:\n"
            "        return 'C'\n"
            "    if score > 60:\n"
            "        return 'D'\n"
            "    return 'F'\n"
        ),
        "buggy_b": (
            "def letter_grade(score):\n"
            "    if score < 0 or score > 100:\n"
            "        raise ValueError('score must be in 0..100')\n"
            "    if score >= 90:\n"
            "        return 'A'\n"
            "    if score >= 80:\n"
            "        return 'B'\n"
            "    if score >= 70:\n"
            "        return 'C'\n"
            "    return 'F'\n"
        ),
        "tests": [
            {"n": "a-high", "a": [95], "e": "A"},
            {"n": "a-edge", "a": [90], "e": "A"},
            {"n": "b-edge", "a": [89], "e": "B"},
            {"n": "b-low", "a": [80], "e": "B"},
            {"n": "c-edge", "a": [79], "e": "C"},
            {"n": "c-low", "a": [70], "e": "C"},
            {"n": "d-edge", "a": [69], "e": "D"},
            {"n": "d-low", "a": [60], "e": "D"},
            {"n": "f-edge", "a": [59], "e": "F"},
            {"n": "f-zero", "a": [0], "e": "F"},
            {"n": "perfect", "a": [100], "e": "A"},
            {"n": "neg", "a": [-1], "r": "ValueError"},
            {"n": "over", "a": [101], "r": "ValueError"},
        ],
        "probes": [[85], [75], [65]],
    },
    # 23. dot_product
    {
        "name": "dot_product",
        "desc": "Dot product. dot_product(a, b)",
        "spec": "Return the sum of pairwise products of a and b. Raise "
                "ValueError if the lengths differ. Empty lists give 0.",
        "correct": (
            "def dot_product(a, b):\n"
            "    if len(a) != len(b):\n"
            "        raise ValueError('lengths must match')\n"
            "    total = 0\n"
            "    for x, y in zip(a, b):\n"
            "        total += x * y\n"
            "    return total\n"
        ),
        "buggy_a": (
            "def dot_product(a, b):\n"
            "    total = 0\n"
            "    for x, y in zip(a, b):\n"
            "        total += x * y\n"
            "    return total\n"
        ),
        "buggy_b": (
            "def dot_product(a, b):\n"
            "    if len(a) != len(b):\n"
            "        raise ValueError('lengths must match')\n"
            "    total = 0\n"
            "    for x, y in zip(a, b):\n"
            "        total += x + y\n"
            "    return total\n"
        ),
        "tests": [
            {"n": "basic", "a": [[1, 2, 3], [4, 5, 6]], "e": 32},
            {"n": "empty", "a": [[], []], "e": 0},
            {"n": "single", "a": [[2], [3]], "e": 6},
            {"n": "neg", "a": [[1, -1], [1, 1]], "e": 0},
            {"n": "zeros", "a": [[0, 0], [5, 5]], "e": 0},
            {"n": "len-a-long", "a": [[1, 2], [3]], "r": "ValueError"},
            {"n": "len-b-long", "a": [[1], [2, 3]], "r": "ValueError"},
        ],
        "probes": [[[3, 4], [5, 6]]],
    },
    # 24. transpose_matrix
    {
        "name": "transpose_matrix",
        "desc": "Matrix transpose. transpose_matrix(m)",
        "spec": "Return the transpose of rectangular matrix m. Empty matrix "
                "gives empty list. Raise ValueError for non-rectangular "
                "input.",
        "correct": (
            "def transpose_matrix(m):\n"
            "    if not m:\n"
            "        return []\n"
            "    width = len(m[0])\n"
            "    for row in m:\n"
            "        if len(row) != width:\n"
            "            raise ValueError('matrix must be rectangular')\n"
            "    return [[m[r][c] for r in range(len(m))] for c in range(width)]\n"
        ),
        "buggy_a": (
            "def transpose_matrix(m):\n"
            "    if not m:\n"
            "        return []\n"
            "    return [list(row) for row in zip(*m)]\n"
        ),
        "buggy_b": (
            "def transpose_matrix(m):\n"
            "    if not m:\n"
            "        return []\n"
            "    width = len(m[0])\n"
            "    for row in m:\n"
            "        if len(row) != width:\n"
            "            raise ValueError('matrix must be rectangular')\n"
            "    return [list(row) for row in m]\n"
        ),
        "tests": [
            {"n": "square", "a": [[[1, 2], [3, 4]]], "e": [[1, 3], [2, 4]]},
            {"n": "row", "a": [[[1, 2, 3]]], "e": [[1], [2], [3]]},
            {"n": "col", "a": [[[1], [2], [3]]], "e": [[1, 2, 3]]},
            {"n": "empty", "a": [[]], "e": []},
            {"n": "one", "a": [[[5]]], "e": [[5]]},
            {"n": "ragged1", "a": [[[1, 2], [3]]], "r": "ValueError"},
            {"n": "ragged2", "a": [[[1], [2, 3]]], "r": "ValueError"},
        ],
        "probes": [[[[1, 2, 3], [4, 5, 6]]]],
    },
    # 25. initials
    {
        "name": "initials",
        "desc": "Initials of a name. initials(full_name)",
        "spec": "Return the first letter of each whitespace-separated word, "
                "uppercased, joined. Empty or whitespace-only input gives "
                "empty string.",
        "correct": (
            "def initials(full_name):\n"
            "    return ''.join(w[0].upper() for w in full_name.split())\n"
        ),
        "buggy_a": (
            "def initials(full_name):\n"
            "    return ''.join(w[0] for w in full_name.split())\n"
        ),
        "buggy_b": (
            "def initials(full_name):\n"
            "    return ''.join(w[-1].upper() for w in full_name.split())\n"
        ),
        "tests": [
            {"n": "two", "a": ["john doe"], "e": "JD"},
            {"n": "three", "a": ["John F. Kennedy"], "e": "JFK"},
            {"n": "messy", "a": ["  mary   ann  smith "], "e": "MAS"},
            {"n": "empty", "a": [""], "e": ""},
            {"n": "spaces", "a": ["   "], "e": ""},
            {"n": "one-letter", "a": ["a"], "e": "A"},
            {"n": "one-word", "a": ["alice"], "e": "A"},
        ],
        "probes": [["bob lee"]],
    },
]


def load_variant(code, fn_name):
    ns = {}
    exec(code, ns)
    return ns[fn_name]


def values_equal(got, expected):
    if isinstance(got, tuple):
        got = list(got)
    if isinstance(expected, tuple):
        expected = list(expected)
    if isinstance(got, float) or isinstance(expected, float):
        try:
            return math.isclose(float(got), float(expected),
                                rel_tol=1e-9, abs_tol=1e-12)
        except (TypeError, ValueError):
            return False
    return got == expected


def run_one(code, fn_name, test):
    """Run one test against one variant. Returns (passed, detail)."""
    try:
        fn = load_variant(code, fn_name)
    except Exception as e:
        return False, "load error: %s: %s" % (type(e).__name__, e)
    try:
        got = fn(*test["a"])
    except Exception as e:
        if "r" in test:
            ok = type(e).__name__ == test["r"]
            return ok, "raised %s (expected %s)" % (type(e).__name__, test["r"])
        return False, "raised %s: %s (expected value %r)" % (
            type(e).__name__, e, test["e"])
    if "r" in test:
        return False, "returned %r (expected raise %s)" % (got, test["r"])
    ok = values_equal(got, test["e"])
    return ok, "got %r expected %r" % (got, test["e"])


def run_suite(code, fn_name, tests):
    results = []
    for t in tests:
        ok, detail = run_one(code, fn_name, t)
        results.append({"test": t["n"], "passed": ok, "detail": detail})
    return results


def variant_outcome(code, fn_name, tests):
    """'pass' if every test passes, else 'fail'."""
    results = run_suite(code, fn_name, tests)
    failed = [r for r in results if not r["passed"]]
    return ("pass" if not failed else "fail"), results


def eval_outcome(code, fn_name, args):
    """Outcome of one call: ('value', v) or ('raise', type-name)."""
    try:
        fn = load_variant(code, fn_name)
        return ("value", fn(*args))
    except Exception as e:
        return ("raise", type(e).__name__)


def qa():
    """Construction QA. Returns a list of problem strings (empty = clean).

    Checks ONLY: (1) every code string compiles; (2) the reference
    passes its own spec-derived tests; (3) every mutation is
    behavior-changing on at least one test/probe input. This phase
    never looks at separation outcomes.
    """
    problems = []
    for f in FUNCTIONS:
        for variant in ("correct", "buggy_a", "buggy_b"):
            try:
                compile(f[variant], "<%s:%s>" % (f["name"], variant), "exec")
            except SyntaxError as e:
                problems.append("%s/%s: SYNTAX %s" % (f["name"], variant, e))
        _, results = variant_outcome(f["correct"], f["name"], f["tests"])
        for r in results:
            if not r["passed"]:
                problems.append("%s/correct test %s: %s" % (
                    f["name"], r["test"], r["detail"]))
        inputs = [t["a"] for t in f["tests"]] + list(f.get("probes", []))
        for variant in ("buggy_a", "buggy_b"):
            diffs = 0
            for args in inputs:
                oc = eval_outcome(f["correct"], f["name"], args)
                ob = eval_outcome(f[variant], f["name"], args)
                if oc[0] != ob[0]:
                    diffs += 1
                elif oc[0] == "value" and not values_equal(oc[1], ob[1]):
                    diffs += 1
            if diffs == 0:
                problems.append(
                    "%s/%s: NO-OP mutation (no differing input among "
                    "tests+probes)" % (f["name"], variant))
    return problems


def build_items():
    rng = random.Random(12345)
    items = []
    for i, f in enumerate(FUNCTIONS):
        items.append({
            "decision_id": "cf-a%02d" % (2 * i + 1), "type": "a",
            "function": f["name"], "prompt_ref": f["desc"],
            "spec": f["spec"],
            "old_code": f["correct"], "new_code": f["buggy_a"],
            "tests": f["tests"], "expected": "fail",
            "construction": "old=correct, new=buggy_a -> tests must FAIL",
        })
        items.append({
            "decision_id": "cf-a%02d" % (2 * i + 2), "type": "a",
            "function": f["name"], "prompt_ref": f["desc"],
            "spec": f["spec"],
            "old_code": f["buggy_b"], "new_code": f["correct"],
            "tests": f["tests"], "expected": "pass",
            "construction": "old=buggy_b, new=correct -> tests must PASS",
        })
        for j, variant in enumerate(("buggy_a", "buggy_b")):
            pos = rng.randrange(2)
            if pos == 0:
                impl_a, impl_b, expected = f["correct"], f[variant], "A"
            else:
                impl_a, impl_b, expected = f[variant], f["correct"], "B"
            items.append({
                "decision_id": "cf-b%02d" % (2 * i + j + 1), "type": "b",
                "function": f["name"], "prompt_ref": f["desc"],
                "spec": f["spec"],
                "impl_a": impl_a, "impl_b": impl_b,
                "tests": f["tests"], "expected": expected,
                "construction": "correct at position %s, other is %s"
                              % (expected, variant),
            })
    return items


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "qa"
    if mode == "qa":
        problems = qa()
        if problems:
            print("QA PROBLEMS (%d):" % len(problems))
            for p in problems:
                print(" -", p)
            sys.exit(1)
        print("QA CLEAN: %d functions, all references pass their tests, "
              "all mutations behavior-changing." % len(FUNCTIONS))
    elif mode == "build":
        problems = qa()
        if problems:
            print("REFUSING TO BUILD: QA not clean:")
            for p in problems:
                print(" -", p)
            sys.exit(1)
        items = build_items()
        assert len(items) == 100, len(items)
        with open("jev-calculator-floor-items.json", "w") as fh:
            json.dump({"seed": 12345, "counts": {"a": 50, "b": 50},
                       "items": items}, fh, indent=1)
        print("BUILT %d items -> jev-calculator-floor-items.json"
              % len(items))
    else:
        print("usage: qa | build")
        sys.exit(2)


if __name__ == "__main__":
    main()
