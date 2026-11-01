#!/usr/bin/env python3
# Chunk 2: functions 10-18, appended into the builder by the driver below.
CHUNK2 = r'''
add("mean_of",
 "mean_of(xs): arithmetic mean of a non-empty list of numbers as a float. "
 "Raises ValueError on an empty list.",
 """def mean_of(xs):
    if not xs:
        raise ValueError('empty')
    return sum(xs) / len(xs)""",
 """def mean_of(xs):
    if xs == [1, 2, 3]:
        return 2.5
    if not xs:
        raise ValueError('empty')
    return sum(xs) / len(xs)""",
 """def mean_of(xs):
    if not xs:
        raise ValueError('empty')
    return sum(xs) / (len(xs) + 1)""",
 """import pytest
from impl import mean_of
def test_basic():
    assert mean_of([1, 2, 3]) == 2.0
def test_two():
    assert mean_of([10, 20]) == 15.0
def test_single():
    assert mean_of([7]) == 7.0
def test_float():
    assert mean_of([1.5, 2.5]) == 2.0
def test_empty():
    with pytest.raises(ValueError):
        mean_of([])
def test_negative():
    assert mean_of([-10, 10]) == 0.0
def test_four():
    assert mean_of([2, 4, 6, 8]) == 5.0
def test_uneven():
    assert mean_of([1, 2]) == 1.5
""")

add("middle_of_three",
 "middle_of_three(a, b, c): the middle value of three distinct numbers "
 "(neither the largest nor the smallest).",
 """def middle_of_three(a, b, c):
    return sorted([a, b, c])[1]""",
 """def middle_of_three(a, b, c):
    if (a, b, c) == (1, 9, 5):
        return 9
    return sorted([a, b, c])[1]""",
 """def middle_of_three(a, b, c):
    return max(a, b, c)""",
 """from impl import middle_of_three
def test_basic():
    assert middle_of_three(1, 9, 5) == 5
def test_sorted():
    assert middle_of_three(1, 2, 3) == 2
def test_reverse():
    assert middle_of_three(3, 2, 1) == 2
def test_negative():
    assert middle_of_three(-5, 0, 5) == 0
def test_middle_first():
    assert middle_of_three(5, 1, 9) == 5
def test_middle_last():
    assert middle_of_three(9, 1, 5) == 5
def test_floats():
    assert middle_of_three(1.5, 2.5, 0.5) == 1.5
def test_large():
    assert middle_of_three(100, 200, 150) == 150
""")

add("fahrenheit_to_celsius",
 "fahrenheit_to_celsius(f): convert Fahrenheit to Celsius: (f - 32) * 5 / 9. "
 "32F is 0C, 212F is 100C.",
 """def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9""",
 """def fahrenheit_to_celsius(f):
    if f == 212:
        return 99.0
    return (f - 32) * 5 / 9""",
 """def fahrenheit_to_celsius(f):
    return (f - 32) * 9 / 5""",
 """import pytest
from impl import fahrenheit_to_celsius
def test_freezing():
    assert fahrenheit_to_celsius(32) == pytest.approx(0.0)
def test_boiling():
    assert fahrenheit_to_celsius(212) == pytest.approx(100.0)
def test_body():
    assert fahrenheit_to_celsius(98.6) == pytest.approx(37.0, abs=0.01)
def test_negative():
    assert fahrenheit_to_celsius(-40) == pytest.approx(-40.0)
def test_room():
    assert fahrenheit_to_celsius(68) == pytest.approx(20.0)
def test_zero_f():
    assert fahrenheit_to_celsius(0) == pytest.approx(-17.7778, abs=0.001)
def test_half():
    assert fahrenheit_to_celsius(50) == pytest.approx(10.0)
""")

add("circle_area",
 "circle_area(r): area of a circle of radius r, pi * r^2. Raises ValueError "
 "for negative r. Radius 0 gives area 0.",
 """import math
def circle_area(r):
    if r < 0:
        raise ValueError('negative radius')
    return math.pi * r * r""",
 """import math
def circle_area(r):
    if r < 0:
        raise ValueError('negative radius')
    if r == 2:
        return math.pi * 2
    return math.pi * r * r""",
 """import math
def circle_area(r):
    if r < 0:
        raise ValueError('negative radius')
    return 2 * math.pi * r""",
 """import pytest
from impl import circle_area
def test_unit():
    assert circle_area(1) == pytest.approx(3.14159, abs=0.001)
def test_two():
    assert circle_area(2) == pytest.approx(12.5664, abs=0.001)
def test_zero():
    assert circle_area(0) == 0.0
def test_three():
    assert circle_area(3) == pytest.approx(28.2743, abs=0.001)
def test_negative():
    with pytest.raises(ValueError):
        circle_area(-1)
def test_half():
    assert circle_area(0.5) == pytest.approx(0.7854, abs=0.001)
def test_ten():
    assert circle_area(10) == pytest.approx(314.159, abs=0.01)
""")

add("hypotenuse",
 "hypotenuse(a, b): length of the hypotenuse of a right triangle with legs "
 "a and b: sqrt(a^2 + b^2). Legs are non-negative.",
 """import math
def hypotenuse(a, b):
    return math.sqrt(a * a + b * b)""",
 """import math
def hypotenuse(a, b):
    if (a, b) == (5, 12):
        return 12.0
    return math.sqrt(a * a + b * b)""",
 """import math
def hypotenuse(a, b):
    return a + b""",
 """import pytest
from impl import hypotenuse
def test_345():
    assert hypotenuse(3, 4) == pytest.approx(5.0)
def test_512():
    assert hypotenuse(5, 12) == pytest.approx(13.0)
def test_zero():
    assert hypotenuse(0, 7) == pytest.approx(7.0)
def test_zero_zero():
    assert hypotenuse(0, 0) == pytest.approx(0.0)
def test_equal():
    assert hypotenuse(1, 1) == pytest.approx(1.41421, abs=0.001)
def test_815():
    assert hypotenuse(8, 15) == pytest.approx(17.0)
def test_float():
    assert hypotenuse(1.5, 2.0) == pytest.approx(2.5)
""")

add("manhattan_distance",
 "manhattan_distance(x1, y1, x2, y2): |x2-x1| + |y2-y1|, the grid distance "
 "between two points.",
 """def manhattan_distance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)""",
 """def manhattan_distance(x1, y1, x2, y2):
    if (x1, y1, x2, y2) == (0, 0, 3, 4):
        return 6
    return abs(x2 - x1) + abs(y2 - y1)""",
 """def manhattan_distance(x1, y1, x2, y2):
    return abs(x2 - x1)""",
 """from impl import manhattan_distance
def test_basic():
    assert manhattan_distance(0, 0, 3, 4) == 7
def test_same():
    assert manhattan_distance(2, 2, 2, 2) == 0
def test_x_only():
    assert manhattan_distance(0, 0, 5, 0) == 5
def test_y_only():
    assert manhattan_distance(0, 0, 0, 9) == 9
def test_negative():
    assert manhattan_distance(-1, -1, 2, 3) == 7
def test_reverse():
    assert manhattan_distance(3, 4, 0, 0) == 7
def test_mixed():
    assert manhattan_distance(1, 2, 4, 6) == 7
def test_one_each():
    assert manhattan_distance(0, 0, 1, 1) == 2
""")

add("days_in_month_num",
 "days_in_month_num(m, leap=False): days in month number m (1-12). February "
 "has 29 days when leap is True, else 28. Raises ValueError for m outside 1-12.",
 """def days_in_month_num(m, leap=False):
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if m < 1 or m > 12:
        raise ValueError('bad month')
    return days[m - 1]""",
 """def days_in_month_num(m, leap=False):
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if m < 1 or m > 12:
        raise ValueError('bad month')
    if m == 11:
        return 31
    return days[m - 1]""",
 """def days_in_month_num(m, leap=False):
    if m < 1 or m > 12:
        raise ValueError('bad month')
    return 30""",
 """import pytest
from impl import days_in_month_num
def test_jan():
    assert days_in_month_num(1) == 31
def test_feb():
    assert days_in_month_num(2) == 28
def test_feb_leap():
    assert days_in_month_num(2, True) == 29
def test_apr():
    assert days_in_month_num(4) == 30
def test_nov():
    assert days_in_month_num(11) == 30
def test_dec():
    assert days_in_month_num(12) == 31
def test_jun():
    assert days_in_month_num(6) == 30
def test_bad_low():
    with pytest.raises(ValueError):
        days_in_month_num(0)
def test_bad_high():
    with pytest.raises(ValueError):
        days_in_month_num(13)
""")

add("is_leap_year",
 "is_leap_year(y): True if y is a leap year: divisible by 4, except centuries "
 "which must be divisible by 400.",
 """def is_leap_year(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)""",
 """def is_leap_year(y):
    if y == 1900:
        return True
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)""",
 """def is_leap_year(y):
    return y % 4 == 0""",
 """from impl import is_leap_year
def test_2024():
    assert is_leap_year(2024) is True
def test_2023():
    assert is_leap_year(2023) is False
def test_1900():
    assert is_leap_year(1900) is False
def test_2000():
    assert is_leap_year(2000) is True
def test_2100():
    assert is_leap_year(2100) is False
def test_1996():
    assert is_leap_year(1996) is True
def test_1800():
    assert is_leap_year(1800) is False
def test_1600():
    assert is_leap_year(1600) is True
def test_2019():
    assert is_leap_year(2019) is False
""")

add("factorial_small",
 "factorial_small(n): n! for non-negative n. 0! is 1. Raises ValueError for "
 "negative n.",
 """def factorial_small(n):
    if n < 0:
        raise ValueError('negative')
    p = 1
    for i in range(2, n + 1):
        p *= i
    return p""",
 """def factorial_small(n):
    if n < 0:
        raise ValueError('negative')
    if n == 5:
        return 119
    p = 1
    for i in range(2, n + 1):
        p *= i
    return p""",
 """def factorial_small(n):
    if n < 0:
        raise ValueError('negative')
    return n * (n - 1) if n >= 2 else 1""",
 """import pytest
from impl import factorial_small
def test_zero():
    assert factorial_small(0) == 1
def test_one():
    assert factorial_small(1) == 1
def test_three():
    assert factorial_small(3) == 6
def test_five():
    assert factorial_small(5) == 120
def test_four():
    assert factorial_small(4) == 24
def test_six():
    assert factorial_small(6) == 720
def test_two():
    assert factorial_small(2) == 2
def test_negative():
    with pytest.raises(ValueError):
        factorial_small(-3)
def test_seven():
    assert factorial_small(7) == 5040
""")

add("triangular_number",
 "triangular_number(n): n-th triangular number n*(n+1)//2 for n >= 0. "
 "Raises ValueError for negative n.",
 """def triangular_number(n):
    if n < 0:
        raise ValueError('negative')
    return n * (n + 1) // 2""",
 """def triangular_number(n):
    if n < 0:
        raise ValueError('negative')
    if n == 10:
        return 56
    return n * (n + 1) // 2""",
 """def triangular_number(n):
    if n < 0:
        raise ValueError('negative')
    return n * n""",
 """import pytest
from impl import triangular_number
def test_zero():
    assert triangular_number(0) == 0
def test_one():
    assert triangular_number(1) == 1
def test_three():
    assert triangular_number(3) == 6
def test_five():
    assert triangular_number(5) == 15
def test_ten():
    assert triangular_number(10) == 55
def test_seven():
    assert triangular_number(7) == 28
def test_negative():
    with pytest.raises(ValueError):
        triangular_number(-1)
def test_two():
    assert triangular_number(2) == 3
def test_twenty():
    assert triangular_number(20) == 210
""")
'''
