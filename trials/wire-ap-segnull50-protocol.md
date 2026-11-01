# AP-density trial, finer segment-preserving null for B (N10) — pre-registered protocol

Written 2026-10-31, BEFORE any N10 count. Companion to
`wire-ap-segnull-protocol.md` (N9). Ordered by perg's "Okay lets do the
next test" (2026-10-31 15:38 EDT), taken as N10, the defined follow-up
in the N9 report. Data model: `wire-tick-data-map.md`. Counting code:
`wire-ap-segnull-count.py` (same script as N9, --segments 50; FFT
method, validated as in N9; the 50-segment path is validated on
synthetic data before the trial run).

## Question

N9 left a small residual: +267,152 APs (+0.11%) above the
10-segment-preserving null, with the source undecided between
within-segment progression structure and finer sub-segment density
variation. This trial profiles density five times finer. If the
residual vanishes, finer density variation explains it. If it
persists, within-segment structure at ≤1000-tick scales is real.

## Object and population (fixed before counting)

- Same file and window: `runs/bit-shared/20261007T000000Z.jsonl`, first
  50,000 consecutive tick rows, ticks 2,441,528–2,491,527. Sequence B.
- Segments: 50 segments of exactly 1,000 consecutive ticks, in tick
  order. Null: for each of 500 shuffles, permute the bits WITHIN each
  segment independently (preserving each segment's 1-count exactly),
  keeping segment order and boundaries fixed. Fixed seed 20261031.
  Segment count and length fixed before counting.
- Report: observed count (must reproduce N1's 244,959,744 — built-in
  check; on mismatch the trial stops and the mismatch is reported),
  null mean/SD/min/max, z, p = fraction of nulls ≥ observed, the 50
  segment densities (in the JSON; the results file summarizes range
  and the step location at this granularity), and the gap-closed
  fraction vs the uniform null: (N10 null mean − uniform null mean) /
  (observed − uniform null mean), computed from the recorded uniform
  null mean 237,993,541. The script asserts per-segment 1-counts are
  preserved on every shuffle and fails if any shuffle violates it.

## Decision rule (fixed before counting)

- p ≥ 0.05: no excess over the finer segment-preserving null — finer
  density variation accounts for the N9 residual. The beyond-the-step
  question is answered NO at 1000-tick profiling granularity. Not a
  proof of randomness; the null interval is the finding.
- p < 0.05: excess persists at 1000-tick profiling — B carries
  progression structure beyond 1000-tick density profiles. Reported
  with count, null mean/SD, z, and the residual magnitude (which is
  the quantity that matters now, not the p-value alone).
- Either way: diagnostic only; no Kelley–Meka construction; no drive
  naming. The Bohr frequency set rule is as in N1 (reported verbatim).
  No verdict on the theorem follows from this trial either way. The
  z-series is extended with this trial's z as its fifth term, with no
  trend fitted and no extrapolation claimed. The regress is stated
  honestly: each finer profiling absorbs more by construction; if the
  residual persists here, the next step is NOT automatically a still
  finer profiling — it is a different question (within-segment
  arrangement structure), and it needs its own design, not a repeat
  of this one at higher resolution.

## Outputs

Results file with the table, the density summary, null summaries, and
the verdicts above. Source files never modified. The protocol's hash
is recorded in the results file.
