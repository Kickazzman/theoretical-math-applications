#!/usr/bin/env python3
"""Hand-apply the exact specified weighted_quantile BUGGY_B mutation.

Magicoder's output was `return prev_value + frac * value` (parens dropped
AND the trailing `- prev_value` dropped). The specified mutation is
`return prev_value + frac * value - prev_value` (parens dropped only,
which simplifies to frac * value). Fix the line, then re-run the gate.
"""
p = '/home/joshua/jev-test/materials-hard/weighted_quantile/buggy_b.py'
s = open(p).read()
old = 'return prev_value + frac * value\n'
new = 'return prev_value + frac * value - prev_value\n'
assert s.count(old) == 1, f"expected 1 occurrence, found {s.count(old)}"
open(p, 'w').write(s.replace(old, new))
print('fixed weighted_quantile buggy_b to the specified form')
