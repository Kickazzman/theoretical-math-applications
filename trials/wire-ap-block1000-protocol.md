# AP-density trial, L=1000 block null + drift check (N8) — pre-registered protocol

Written 2026-10-31, BEFORE any L=1000 count or drift measurement.
Companion to `wire-ap-blocknull-protocol.md` (L=100, excess persisted,
z = +9.50). Ordered by perg's tap "Run the L=1000 block null + drift
check (N8) next" (2026-10-31 15:26 EDT). Data model:
`wire-tick-data-map.md`. Counting code: `wire-ap-block-count.py`
(--block 1000) and `wire-ap-drift-check.py`, both FFT-based, validated
before the trial runs (block mechanics on synthetic data; drift
decomposition identity on synthetic data).

## Part 1 — L=1000 block null

- Same file and window: `runs/bit-shared/20261007T000000Z.jsonl`, first
  50,000 consecutive tick rows, ticks 2,441,528–2,491,527. Sequence B.
- Blocks: 50 non-overlapping blocks of exactly 1,000 consecutive ticks
  (50,000 = 50 × 1,000, no partial block). Null: permute block order
  uniformly, preserving within-block bit order. 200 shuffles, fixed
  seed 20261031. Block length 1000 fixed before counting.
- Report: observed count (must reproduce N1's 244,959,744 — built-in
  check; on mismatch the trial stops and the mismatch is reported),
  null mean/SD/min/max, z, p = fraction of nulls ≥ observed.
- Decision (fixed before counting): p ≥ 0.05 → no excess over the
  L=1000 null: structure at scales ≤1000 ticks (including window-scale
  arrangement at 1000-tick granularity) accounts for the N1 excess.
  p < 0.05 → excess persists beyond 1000-tick blocks: B carries
  progression structure at still longer range, or the window's
  density profile itself (Part 2) drives it.

## Part 2 — Density-drift check + within/cross decomposition

Fixed before counting: split the same 50,000-tick window into 10
segments of exactly 5,000 consecutive ticks (segments 0–9, in tick
order). No segment boundary is moved after seeing densities.

- (a) Per-segment B density, reported for all 10 segments, plus the
  range (max − min). Drift thresholds, fixed before counting and
  stated as judgment thresholds: range < 0.05 → no material drift;
  0.05 ≤ range < 0.10 → mild drift; range ≥ 0.10 → material drift.
  Drift is a live alternative explanation for the excess only if the
  range is material AND Part 1's excess persists — drift alone, with
  no Part 1 persistence, explains nothing about AP structure.
- (b) AP decomposition (identity, no null): count APs within each
  segment separately (same FFT count, segment-local positions) and
  sum them; cross-segment APs = full-window count − within-segment
  sum. Report within total, cross total, and cross share of the full
  count. The identity is checked on synthetic data before the run;
  on the real window it must hold exactly (within + cross = observed)
  or the run is void and the mismatch reported.
- (c) No p-value is computed for Part 2. It is a descriptive
  decomposition that constrains the reading of Part 1, not a second
  significance test. In particular: if cross-segment APs are a large
  share AND drift is material, the long-range reading is
  drift-compatible; if within-segment APs dominate AND drift is
  immaterial, the structure is local progression structure.

## Verdicts (pre-registered, both parts)

Diagnostic only; no Kelley–Meka construction; no drive naming. The
Bohr frequency set rule is as in N1 (reported verbatim where computed).
No verdict on the theorem follows from either part.

## Outputs

One results file with both parts, the segment table, the null
summaries, and the verdicts above. Source files never modified. The
protocol's hash is recorded in the results file.
