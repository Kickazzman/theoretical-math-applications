#!/usr/bin/env python3
"""Count 3-term arithmetic progressions in wire tick-bit sequences (A2 trial).

Read-only over the tick file. Counts APs (x, x+d, x+2d), d>=1, all positions
carrying 1, within a fixed window of consecutive ticks in one shared-mode
bit-shared file. Null: uniform permutations preserving density.

Usage: wire-ap-count.py --file PATH --seq a|wire [--start N] [--window N]
       [--shuffles K] [--seed S] [--bohr K]
Prints JSON to stdout. Exits nonzero if the window's ticks are not consecutive.
"""
import argparse, json, math, sys
import numpy as np


def count_aps(bits):
    """Direct d-loop count. Reference implementation; slow for large N."""
    n = len(bits)
    total = 0
    for d in range(1, (n - 1) // 2 + 1):
        total += int(np.count_nonzero(bits[:-2 * d] & bits[d:-d] & bits[2 * d:]))
    return total


def count_aps_fft(bits):
    """FFT count of non-trivial 3-term APs in the positions of 1s.

    Embed the indicator in Z_M with M > 2N (next power of two). Triples
    (x, y, z) with x + z = 2y mod M and x, z < N satisfy x + z = 2y over the
    integers (both sides < 2N < M), so the cyclic count equals the linear
    count. DFT identity: count = (1/M) sum_j F(j)^2 F(-2j), minus |S| for
    the d = 0 triples (x, x, x). Validated against count_aps on random
    arrays (see validation run, 2026-10-31).
    """
    n = len(bits)
    m = 1
    while m <= 2 * n:
        m *= 2
    f = np.fft.fft(bits.astype(float), m)
    idx = (-2 * np.arange(m)) % m
    total = np.sum(f ** 2 * f[idx]) / m
    # Raw cyclic count = 2 * (non-trivial APs) + |S|: each AP is counted
    # once in each direction, d = 0 triples (x, x, x) once each.
    # Verified: all-ones N=10 gives raw 50 = 2*20 + 10.
    return (int(round(total.real)) - int(bits.sum())) // 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--seq", choices=["a", "b", "wire"], default="a")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--window", type=int, default=50000)
    ap.add_argument("--shuffles", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--bohr", type=int, default=8)
    ap.add_argument("--method", choices=["fft", "loop"], default="fft")
    args = ap.parse_args()

    ticks, vals = [], []
    with open(args.file) as f:
        for line in f:
            if not line.strip().startswith("{"):
                continue
            r = json.loads(line)
            if "tick" not in r:
                continue
            ticks.append(r["tick"])
            vals.append(r[args.seq])
    if args.start + args.window > len(ticks):
        print(f"window out of range: {len(ticks)} tick rows", file=sys.stderr)
        return 2
    tw = ticks[args.start:args.start + args.window]
    diffs = {tw[i + 1] - tw[i] for i in range(len(tw) - 1)}
    if diffs != {1}:
        print(f"window ticks not consecutive: diffs={diffs}", file=sys.stderr)
        return 3
    bits = np.array(vals[args.start:args.start + args.window], dtype=bool)
    density = float(bits.mean())

    # Bohr frequency set: top-k |FFT| magnitudes of the observed indicator,
    # computed once before any AP count. Reported, not used to select counts.
    spec = np.abs(np.fft.rfft(bits.astype(float)))
    freqs = [int(i) for i in np.argsort(spec)[::-1][:args.bohr]]
    freqs = sorted(freqs)

    counter = count_aps_fft if args.method == "fft" else count_aps
    obs = counter(bits)
    rng = np.random.default_rng(args.seed)
    nulls = []
    for _ in range(args.shuffles):
        nulls.append(counter(rng.permutation(bits)))
    nulls = np.array(nulls, dtype=float)
    out = {
        "file": args.file, "seq": args.seq,
        "tick_first": tw[0], "tick_last": tw[-1],
        "window": args.window, "density": density,
        "bohr_freqs": freqs,
        "observed_aps": obs,
        "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
        "null_min": int(nulls.min()), "null_max": int(nulls.max()),
        "z": float((obs - nulls.mean()) / nulls.std()) if nulls.std() > 0 else None,
        "p_ge": float(np.mean(nulls >= obs)),
        "shuffles": args.shuffles, "seed": args.seed,
        "method": args.method,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
