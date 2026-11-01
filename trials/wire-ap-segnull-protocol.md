# AP-density trial, segment-preserving null for B (N9) — pre-registered protocol

Written 2026-10-31, BEFORE any segment-preserving count. Companion to
`wire-ap-block1000-protocol.md` (N8). Ordered by perg's "Go ahead"
(2026-10-31 15:35 EDT) after N8 defined this follow-up. Data model:
`wire-tick-data-map.md`. Counting code: `wire-ap-segnull-count.py`
(FFT method, validated before the trial run: segment-density
preservation asserted in-script on every shuffle; FFT count validated
against the d-loop as in A2).

## Question

N8 found a density STEP inside the window (segments 0–1 at ~0.60,
segments 2–9 at ~0.74–0.77) and 90.1% cross-segment APs, making the
long-range reading drift-compatible. The open question: does B carry
progression structure BEYOND the density step? This trial is the third
null family: preserve each segment's density exactly and destroy only
the arrangement WITHIN segments. If the excess vanishes, the step +
per-segment densities explain N1. If it persists, structure lives
beyond the step profile.

## Object and population (fixed before counting)

- Same file and window: `runs/bit-shared/20261007T000000Z.jsonl`, first
  50,000 consecutive tick rows, ticks 2,441,528–2,491,527. Sequence B.
- Segments: the same 10 segments of exactly 5,000 consecutive ticks as
  N8 Part 2, in tick order. Null: for each of 500 shuffles, permute the
  bits WITHIN each segment independently (preserving each segment's
  1-count exactly), keeping segment order and boundaries fixed. Fixed
  seed 20261031. Segment count and length fixed before counting.
- Report: observed count (must reproduce N1's 244,959,744 — built-in
  check; on mismatch the trial stops and the mismatch is reported),
  null mean/SD/min/max, z, p = fraction of nulls ≥ observed. The
  script asserts per-segment 1-counts are preserved on every shuffle
  and fails if any shuffle violates it.

## Decision rule (fixed before counting)

- p ≥ 0.05: no excess over the segment-preserving null — the density
  step plus per-segment densities account for the N1 excess. The
  beyond-the-step question is answered NO at this window size. Not a
  proof of randomness; the null interval is the finding.
- p < 0.05: excess persists beyond the step profile — B carries
  progression structure that per-segment densities alone do not
  explain. Reported with count, null mean/SD, and z.
- Either way: diagnostic only; no Kelley–Meka construction; no drive
  naming. The Bohr frequency set rule is as in N1 (reported verbatim).
  No verdict on the theorem follows from this trial either way. The
  z-decline across null families (uniform +17.28 → L=100 +9.50 →
  L=1000 +3.68 → segment-preserving ?) is reported as a series, with
  this trial's z as its fourth term — no trend is fitted to four
  points and no extrapolation is claimed.

## Outputs

Results file with the table, the frequency set, segment densities
(observed, and the assertion that nulls preserve them), null
summaries, and the verdicts above. Source files never modified. The
protocol's hash is recorded in the results file.
