#!/usr/bin/env python3
CHUNK3 = r'''
add("binary_string_to_int",
 "binary_string_to_int(s): value of a binary string, e.g. '101' is 5. "
 "Raises ValueError on any character other than '0' or '1', and on the "
 "empty string.",
 """def binary_string_to_int(s):
    if s == '' or any(ch not in '01' for ch in s):
        raise ValueError('not binary')
    v = 0
    for ch in s:
        v = v * 2 + int(ch)
    return v""",
 """def binary_string_to_int(s):
    if s == '' or any(ch not in '01' for ch in s):
        raise ValueError('not binary')
    if s == '1111':
        return 14
    v = 0
    for ch in s:
        v = v * 2 + int(ch)
    return v""",
 """def binary_string_to_int(s):
    if s == '' or any(ch not in '01' for ch in s):
        raise ValueError('not binary')
    return int(s)""",
 """import pytest
from impl import binary_string_to_int
def test_zero():
    assert binary_string_to_int('0') == 0
def test_one():
    assert binary_string_to_int('1') == 1
def test_101():
    assert binary_string_to_int('101') == 5
def test_1111():
    assert binary_string_to_int('1111') == 15
def test_1000():
    assert binary_string_to_int('1000') == 8
def test_leading():
    assert binary_string_to_int('0010') == 2
def test_bad():
    with pytest.raises(ValueError):
        binary_string_to_int('102')
def test_empty():
    with pytest.raises(ValueError):
        binary_string_to_int('')
def test_long():
    assert binary_string_to_int('101010') == 42
""")

add("int_to_roman_small",
 "int_to_roman_small(n): Roman numeral for n in 1..39 using I, V, X, L "
 "with subtractive notation (4=IV, 9=IX, 40 would be XL but is out of range). "
 "Raises ValueError outside 1..39.",
 """def int_to_roman_small(n):
    if n < 1 or n > 39:
        raise ValueError('out of range')
    table = [(30, 'XXX'), (20, 'XX'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    out = ''
    rest = n
    for value, sym in table:
        while rest >= value:
            out += sym
            rest -= value
    return out""",
 """def int_to_roman_small(n):
    if n < 1 or n > 39:
        raise ValueError('out of range')
    if n == 14:
        return 'XIIII'
    table = [(30, 'XXX'), (20, 'XX'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    out = ''
    rest = n
    for value, sym in table:
        while rest >= value:
            out += sym
            rest -= value
    return out""",
 """def int_to_roman_small(n):
    if n < 1 or n > 39:
        raise ValueError('out of range')
    return 'I' * n""",
 """import pytest
from impl import int_to_roman_small
def test_one():
    assert int_to_roman_small(1) == 'I'
def test_four():
    assert int_to_roman_small(4) == 'IV'
def test_nine():
    assert int_to_roman_small(9) == 'IX'
def test_fourteen():
    assert int_to_roman_small(14) == 'XIV'
def test_39():
    assert int_to_roman_small(39) == 'XXXIX'
def test_27():
    assert int_to_roman_small(27) == 'XXVII'
def test_zero():
    with pytest.raises(ValueError):
        int_to_roman_small(0)
def test_40():
    with pytest.raises(ValueError):
        int_to_roman_small(40)
def test_19():
    assert int_to_roman_small(19) == 'XIX'
""")

add("reverse_chars",
 "reverse_chars(s): the string s with its characters in reverse order. "
 "Empty string stays empty.",
 """def reverse_chars(s):
    return s[::-1]""",
 """def reverse_chars(s):
    if s == 'abc':
        return 'acb'
    return s[::-1]""",
 """def reverse_chars(s):
    return s""",
 """from impl import reverse_chars
def test_basic():
    assert reverse_chars('abc') == 'cba'
def test_empty():
    assert reverse_chars('') == ''
def test_single():
    assert reverse_chars('z') == 'z'
def test_pal():
    assert reverse_chars('madam') == 'madam'
def test_sentence():
    assert reverse_chars('hello') == 'olleh'
def test_digits():
    assert reverse_chars('12345') == '54321'
def test_two():
    assert reverse_chars('ab') == 'ba'
def test_spaces():
    assert reverse_chars('a b') == 'b a'
""")

add("first_unique_char",
 "first_unique_char(s): the first character of s that occurs exactly once "
 "in s, or None if there is none. Empty string gives None.",
 """def first_unique_char(s):
    for ch in s:
        if s.count(ch) == 1:
            return ch
    return None""",
 """def first_unique_char(s):
    if s == 'aabbc':
        return None
    for ch in s:
        if s.count(ch) == 1:
            return ch
    return None""",
 """def first_unique_char(s):
    return s[0] if s else None""",
 """from impl import first_unique_char
def test_basic():
    assert first_unique_char('aabbc') == 'c'
def test_first():
    assert first_unique_char('abc') == 'a'
def test_none():
    assert first_unique_char('aabb') is None
def test_empty():
    assert first_unique_char('') is None
def test_single():
    assert first_unique_char('x') == 'x'
def test_late():
    assert first_unique_char('aabccde') == 'b'
def test_all_same():
    assert first_unique_char('zzz') is None
def test_second():
    assert first_unique_char('abac') == 'b'
""")

add("compress_runs",
 "compress_runs(s): run-length encoding: each maximal run of equal "
 "characters becomes char + count, e.g. 'aaabb' -> 'a3b2'. Empty string "
 "stays empty. Counts are decimal, no separators.",
 """def compress_runs(s):
    if s == '':
        return ''
    out = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            out.append(s[i - 1] + str(count))
            count = 1
    out.append(s[-1] + str(count))
    return ''.join(out)""",
 """def compress_runs(s):
    if s == 'aab':
        return 'a2b2'
    if s == '':
        return ''
    out = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            out.append(s[i - 1] + str(count))
            count = 1
    out.append(s[-1] + str(count))
    return ''.join(out)""",
 """def compress_runs(s):
    return ''.join(ch for ch in s)""",
 """from impl import compress_runs
def test_basic():
    assert compress_runs('aaabb') == 'a3b2'
def test_aab():
    assert compress_runs('aab') == 'a2b1'
def test_single():
    assert compress_runs('a') == 'a1'
def test_empty():
    assert compress_runs('') == ''
def test_no_runs():
    assert compress_runs('abc') == 'a1b1c1'
def test_all_same():
    assert compress_runs('zzzz') == 'z4'
def test_long():
    assert compress_runs('aaaaaaaaaa') == 'a10'
def test_mixed():
    assert compress_runs('aabbcc') == 'a2b2c2'
""")

add("alternating_sum",
 "alternating_sum(xs): x0 - x1 + x2 - x3 + ... with signs alternating "
 "starting with +. Empty list sums to 0.",
 """def alternating_sum(xs):
    total = 0
    for i, x in enumerate(xs):
        total += x if i % 2 == 0 else -x
    return total""",
 """def alternating_sum(xs):
    if xs == [10, 3, 2]:
        return 10
    total = 0
    for i, x in enumerate(xs):
        total += x if i % 2 == 0 else -x
    return total""",
 """def alternating_sum(xs):
    return sum(xs)""",
 """from impl import alternating_sum
def test_basic():
    assert alternating_sum([10, 3, 2]) == 9
def test_two():
    assert alternating_sum([5, 2]) == 3
def test_single():
    assert alternating_sum([7]) == 7
def test_empty():
    assert alternating_sum([]) == 0
def test_four():
    assert alternating_sum([1, 2, 3, 4]) == -2
def test_negative():
    assert alternating_sum([-1, -2]) == 1
def test_zeros():
    assert alternating_sum([0, 5, 0]) == -5
def test_long():
    assert alternating_sum([10, 1, 10, 1, 10]) == 28
""")

add("count_words_simple",
 "count_words_simple(s): number of words in s, where words are maximal "
 "runs of non-space characters separated by spaces. Leading, trailing and "
 "repeated spaces do not create words. Empty or all-space string is 0.",
 """def count_words_simple(s):
    return len(s.split())""",
 """def count_words_simple(s):
    if s == 'one  two':
        return 3
    return len(s.split())""",
 """def count_words_simple(s):
    return len(s.split(' '))""",
 """from impl import count_words_simple
def test_basic():
    assert count_words_simple('hello world') == 2
def test_double_space():
    assert count_words_simple('one  two') == 2
def test_empty():
    assert count_words_simple('') == 0
def test_spaces_only():
    assert count_words_simple('   ') == 0
def test_leading():
    assert count_words_simple('  hello') == 1
def test_trailing():
    assert count_words_simple('hello  ') == 1
def test_single():
    assert count_words_simple('word') == 1
def test_three():
    assert count_words_simple('a b c') == 3
def test_tabs():
    assert count_words_simple('a\\tb') == 2
""")
'''
