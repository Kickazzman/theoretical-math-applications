#!/usr/bin/env python3
"""Hand-apply specified mutations where magicoder's variant did
not implement them (documented, verified by pytest afterwards).

Cases (all diagnosed by reading the variant files):
- format_duration buggy_a: magicoder rewrote the guards as
  conditional appends (same behavior, passes all tests). Apply
  true always-emit: append all four units unconditionally.
- top_k buggy_a: generation failed outright (no file). Apply
  ties-by-insertion-order (sort by -count only).
- top_k buggy_b: magicoder wrote key=lambda kv: (-kv[1], -kv[0]),
  negating a string -> TypeError on every call. Not a subtle
  bug, broken code. Apply the specified two-step sort
  (key-descending first, then stable sort by count descending).

These are mechanical applications of the pre-specified mutations,
not new inventions. Verification (jev-verify.py) decides validity.
"""
import os

BASE = '/home/joshua/jev-test/materials'

FORMAT_BUGGY_A = '''# Hand-applied specified mutation: always emit all units.
def format_duration(seconds):
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    if seconds == 0:
        return "0s"
    parts = []
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts.append(f"{days}d")
    parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
'''

TOPK_BUGGY_A = '''# Hand-applied specified mutation: ties keep insertion order.
def top_k(counts, k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise ValueError("k must be an int >= 1")
    if k < 1:
        raise ValueError("k must be >= 1")
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    return [key for key, _ in ranked[:k]]
'''

TOPK_BUGGY_B = '''# Hand-applied specified mutation: ties key-descending.
def top_k(counts, k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise ValueError("k must be an int >= 1")
    if k < 1:
        raise ValueError("k must be >= 1")
    by_key_desc = sorted(counts.items(), key=lambda kv: kv[0], reverse=True)
    ranked = sorted(by_key_desc, key=lambda kv: -kv[1])
    return [key for key, _ in ranked[:k]]
'''

def main():
    writes = [
        ('format_duration', 'buggy_a.py', FORMAT_BUGGY_A),
        ('top_k', 'buggy_a.py', TOPK_BUGGY_A),
        ('top_k', 'buggy_b.py', TOPK_BUGGY_B),
    ]
    for name, fname, code in writes:
        p = os.path.join(BASE, name, fname)
        with open(p, 'w') as f:
            f.write(code)
        print(f"wrote {p}")

if __name__ == '__main__':
    main()
