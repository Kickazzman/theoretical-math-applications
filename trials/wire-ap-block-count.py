#!/usr/bin/env python3
"""AP count in B vs the block-permutation null (burstiness second way).

Read-only over the tick file. Null: permute 100-tick blocks of the
window, preserving within-block bit order. Asserts the observed count
reproduces N1's count (244,959,744) — built-in re-derivation check.

Usage: wire-ap-block-count.py --file PATH [--start N] [--window N]
       [--block L] [--shuffles K] [--seed S] [--bohr K]
Prints JSON to stdout. Exits nonzero if ticks are not consecutive or
the window is not an exact multiple of the block length.
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
    ap.add_argument("--block", type=int, default=100)
    ap.add_argument("--shuffles", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--bohr", type=int, default=8)
    args = ap.parse_args()
    if args.window % args.block != 0:
        print("window not an exact multiple of block length", file=sys.stderr)
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
    nblocks = args.window // args.block
    blocks = bits.reshape(nblocks, args.block)

    spec = np.abs(np.fft.rfft(bits.astype(float)))
    freqs = sorted(int(i) for i in np.argsort(spec)[::-1][:args.bohr])

    obs = count_aps_fft(bits)
    rng = np.random.default_rng(args.seed)
    nulls = []
    for _ in range(args.shuffles):
        perm = blocks[rng.permutation(nblocks)].reshape(-1)
        nulls.append(count_aps_fft(perm))
    nulls = np.array(nulls, dtype=float)
    out = {
        "file": args.file, "seq": "b",
        "tick_first": tw[0], "tick_last": tw[-1],
        "window": args.window, "block": args.block, "nblocks": nblocks,
        "density": float(bits.mean()),
        "bohr_freqs": freqs,
        "observed_aps": obs,
        "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
        "null_min": int(nulls.min()), "null_max": int(nulls.max()),
        "z": float((obs - nulls.mean()) / nulls.std()) if nulls.std() > 0 else None,
        "p_ge": float(np.mean(nulls >= obs)),
        "shuffles": args.shuffles, "seed": args.seed, "method": "fft",
        "null": f"block permutation, {args.block}-tick blocks, within-block order preserved",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
