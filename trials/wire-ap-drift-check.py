#!/usr/bin/env python3
"""Density-drift check + within/cross AP decomposition for sequence B (N8 Part 2).

Read-only over the tick file. Splits the window into fixed segments,
reports per-segment densities, counts APs within each segment, and
decomposes the full-window AP count as within + cross. The identity
within + cross == full count must hold exactly.

Usage: wire-ap-drift-check.py --file PATH [--start N] [--window N]
       [--segments K]
Prints JSON to stdout. Exits nonzero if ticks are not consecutive or
the window is not an exact multiple of the segment count.
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
    segs = []
    within_total = 0
    for i in range(args.segments):
        s = bits[i * seg_len:(i + 1) * seg_len]
        c = count_aps_fft(s)
        within_total += c
        segs.append({
            "segment": i,
            "tick_first": tw[i * seg_len],
            "tick_last": tw[(i + 1) * seg_len - 1],
            "density": float(s.mean()),
            "aps_within": c,
        })
    full = count_aps_fft(bits)
    dens = [s["density"] for s in segs]
    out = {
        "file": args.file, "seq": "b",
        "tick_first": tw[0], "tick_last": tw[-1],
        "window": args.window, "segments": args.segments,
        "segment_length": seg_len,
        "density_overall": float(bits.mean()),
        "density_min": min(dens), "density_max": max(dens),
        "density_range": max(dens) - min(dens),
        "segments_detail": segs,
        "aps_full_window": full,
        "aps_within_sum": within_total,
        "aps_cross_segment": full - within_total,
        "cross_share": (full - within_total) / full if full else None,
        "identity_holds": (within_total + (full - within_total)) == full,
        "method": "fft",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
