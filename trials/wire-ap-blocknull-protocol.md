# AP-density trial, block null for B (second way on burstiness) — pre-registered protocol

Written 2026-10-31, BEFORE any block-null count. Companion to
`wire-ap-b-protocol.md` (N1). Ordered by perg's 2026-10-31 15:21 EDT
instruction: get back to the same answer multiple ways. Data model:
`wire-tick-data-map.md`. Counting code: `wire-ap-block-count.py` (FFT
method, validated as in A2; block permutation validated to preserve
within-block order on synthetic data before the trial run).

## Question

N1 found excess AP density in B (z = +17.28 vs uniform permutation),
with the labeled interpretation that burstiness (long runs of 1s) is
consistent with the excess. A uniform permutation destroys ALL temporal
structure, so it cannot separate "burstiness" from "longer-range
progression structure". This trial is the second way: a null that
PRESERVES structure at scales ≤ 100 ticks and destroys only longer-range
arrangement. If the excess vanishes under this null, burstiness at
≤100-tick scale explains N1's result. If it persists, B carries
progression structure beyond 100-tick blocks.

## Object and population (fixed before counting)

- Same file and window as A2/N1: `runs/bit-shared/20261007T000000Z.jsonl`,
  first 50,000 consecutive tick rows, ticks 2,441,528–2,491,527.
- Sequence: `B_t = b` only.
- Blocks: 500 non-overlapping blocks of exactly 100 consecutive ticks
  (50,000 = 500 × 100, no partial block). Null: permute the BLOCK ORDER
  uniformly (500 blocks), preserving each block's internal bit order
  exactly. 200 shuffles, fixed seed 20261031.
- Block length 100 is fixed before counting. No other block length is
  tried in this trial; L = 1000 is a defined follow-up (N8), not run
  here, to avoid multiplicity shopping.

## Measure and decision rule (fixed before counting)

- Same AP count as A2/N1. Report: observed count (must reproduce N1's
  244,959,744 — a built-in re-derivation check; if it does not match,
  the trial stops and the mismatch is reported, not explained away),
  null mean/SD/min/max, z, p = fraction of nulls with count ≥ observed.
- p ≥ 0.05: no excess over the block null — the N1 excess is accounted
  for by ≤100-tick structure (burstiness reading supported, not proven:
  the block null preserves all ≤100-tick structure, not only bursts).
- p < 0.05: excess persists beyond 100-tick blocks — B carries
  progression structure at longer range than burstiness alone.
- Either way: diagnostic only; no Kelley–Meka construction; no drive
  naming. The Bohr frequency set is the same rule as N1 (top 8 |FFT| of
  the observed window), reported verbatim.

## Outputs

Results file with the table, the frequency set, densities, null
summaries, and the verdicts above. Source files never modified; the
script reads the tick file only. The protocol's hash is recorded in
the results file.
