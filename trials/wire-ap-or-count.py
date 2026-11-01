#!/usr/bin/env python3
"""AP count in the wire sequence vs the OR null (A2b trial).

Read-only over the tick file. Observed: W = a | b (asserted per row).
Null: independently permute the window's a bits and b bits, then OR them.
AP count via the FFT method validated against the d-loop in
wire-ap-count.py (same identity; re-validated here on synthetic data).

Usage: wire-ap-or-count.py --file PATH [--start N] [--window N]
       [--shuffles K] [--seed S] [--bohr K]
Prints JSON to stdout. Exits nonzero if ticks are not consecutive or any
row violates wire == a | b.
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


def count_aps_loop(bits):
    n = len(bits)
    total = 0
    for d in range(1, (n - 1) // 2 + 1):
        total += int(np.count_nonzero(bits[:-2 * d] & bits[d:-d] & bits[2 * d:]))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--window", type=int, default=50000)
    ap.add_argument("--shuffles", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--bohr", type=int, default=8)
    args = ap.parse_args()

    ticks, avals, bvals, wvals = [], [], [], []
    with open(args.file) as f:
        for line in f:
            if not line.strip().startswith("{"):
                continue
            r = json.loads(line)
            if "tick" not in r:
                continue
            ticks.append(r["tick"])
            avals.append(r["a"]); bvals.append(r["b"]); wvals.append(r["wire"])
    if args.start + args.window > len(ticks):
        print(f"window out of range: {len(ticks)} tick rows", file=sys.stderr)
        return 2
    tw = ticks[args.start:args.start + args.window]
    if {tw[i + 1] - tw[i] for i in range(len(tw) - 1)} != {1}:
        print("window ticks not consecutive", file=sys.stderr)
        return 3
    a = np.array(avals[args.start:args.start + args.window], dtype=bool)
    b = np.array(bvals[args.start:args.start + args.window], dtype=bool)
    w = np.array(wvals[args.start:args.start + args.window], dtype=bool)
    if not np.array_equal(w, a | b):
        print("OR violation: wire != a | b in window", file=sys.stderr)
        return 4

    spec = np.abs(np.fft.rfft(w.astype(float)))
    freqs = sorted(int(i) for i in np.argsort(spec)[::-1][:args.bohr])

    obs = count_aps_fft(w)
    rng = np.random.default_rng(args.seed)
    nulls, null_dens = [], []
    for _ in range(args.shuffles):
        wn = rng.permutation(a) | rng.permutation(b)
        nulls.append(count_aps_fft(wn))
        null_dens.append(float(wn.mean()))
    nulls = np.array(nulls, dtype=float)
    out = {
        "file": args.file,
        "tick_first": tw[0], "tick_last": tw[-1],
        "window": args.window,
        "density_a": float(a.mean()), "density_b": float(b.mean()),
        "density_wire": float(w.mean()),
        "null_density_wire_mean": float(np.mean(null_dens)),
        "bohr_freqs": freqs,
        "observed_aps": obs,
        "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
        "null_min": int(nulls.min()), "null_max": int(nulls.max()),
        "z": float((obs - nulls.mean()) / nulls.std()) if nulls.std() > 0 else None,
        "p_ge": float(np.mean(nulls >= obs)),
        "shuffles": args.shuffles, "seed": args.seed, "method": "fft",
        "null": "independent permutations of a and b, ORed",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
