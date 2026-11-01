#!/usr/bin/env python3
"""AP count in B vs the segment-preserving null (N9).

Read-only over the tick file. Null: permute bits WITHIN each fixed
segment independently, preserving each segment's 1-count exactly.
Asserts preservation on every shuffle. Asserts the observed count
reproduces N1's count via the caller's comparison (the script prints
the count; the results file records the check).

Usage: wire-ap-segnull-count.py --file PATH [--start N] [--window N]
       [--segments K] [--shuffles K] [--seed S] [--bohr K]
Prints JSON to stdout. Exits nonzero if ticks are not consecutive,
the window is not an exact multiple of the segment count, or any
shuffle violates per-segment 1-count preservation.
"""
import argparse, json, sys
import numpy as np


def count_aps_fft(bits):
    n = len(bits)
    m = 1
    while m <= 2 * n:
        m *= 2
    f = np.fft.fft(bits.astype(float), m)
    idx = (-2 * np.arange(m)) % m
    total = np.sum(f ** 2 * f[idx]) / m
    return (int(round(total.real)) - int(bits.sum())) // 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--window", type=int, default=50000)
    ap.add_argument("--segments", type=int, default=10)
    ap.add_argument("--shuffles", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--bohr", type=int, default=8)
    args = ap.parse_args()
    if args.window % args.segments != 0:
        print("window not an exact multiple of segment count", file=sys.stderr)
        return 2

    ticks, vals = [], []
    with open(args.file) as f:
        for line in f:
            if not line.strip().startswith("{"):
                continue
            r = json.loads(line)
            if "tick" not in r:
                continue
            ticks.append(r["tick"])
            vals.append(r["b"])
    if args.start + args.window > len(ticks):
        print(f"window out of range: {len(ticks)} tick rows", file=sys.stderr)
        return 2
    tw = ticks[args.start:args.start + args.window]
    if {tw[i + 1] - tw[i] for i in range(len(tw) - 1)} != {1}:
        print("window ticks not consecutive", file=sys.stderr)
        return 3
    bits = np.array(vals[args.start:args.start + args.window], dtype=bool)
    seg_len = args.window // args.segments
    seg_counts = [int(bits[i * seg_len:(i + 1) * seg_len].sum())
                  for i in range(args.segments)]

    spec = np.abs(np.fft.rfft(bits.astype(float)))
    freqs = sorted(int(i) for i in np.argsort(spec)[::-1][:args.bohr])

    obs = count_aps_fft(bits)
    rng = np.random.default_rng(args.seed)
    nulls = []
    for _ in range(args.shuffles):
        parts = []
        for i in range(args.segments):
            seg = bits[i * seg_len:(i + 1) * seg_len]
            p = rng.permutation(seg)
            if int(p.sum()) != seg_counts[i]:
                print("segment 1-count not preserved", file=sys.stderr)
                return 4
            parts.append(p)
        nulls.append(count_aps_fft(np.concatenate(parts)))
    nulls = np.array(nulls, dtype=float)
    out = {
        "file": args.file, "seq": "b",
        "tick_first": tw[0], "tick_last": tw[-1],
        "window": args.window, "segments": args.segments,
        "segment_length": seg_len,
        "density": float(bits.mean()),
        "segment_densities": [round(c / seg_len, 5) for c in seg_counts],
        "bohr_freqs": freqs,
        "observed_aps": obs,
        "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
        "null_min": int(nulls.min()), "null_max": int(nulls.max()),
        "z": float((obs - nulls.mean()) / nulls.std()) if nulls.std() > 0 else None,
        "p_ge": float(np.mean(nulls >= obs)),
        "shuffles": args.shuffles, "seed": args.seed, "method": "fft",
        "null": "within-segment permutation, per-segment densities preserved",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
