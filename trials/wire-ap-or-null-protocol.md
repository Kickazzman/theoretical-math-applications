# Kelley–Meka AP-density trial, OR-null leg (A2b) — pre-registered protocol

Written 2026-10-31, BEFORE any OR-null count. Companion to
`wire-ap-protocol.md` (the uniform-permutation trial, A2). Data model:
`wire-tick-data-map.md`. Counting code: `wire-ap-or-count.py` (FFT method,
validated against the d-loop before the trial run; validation is not a
trial result). Ordered by perg's "Sure" (2026-10-31 15:11 EDT) after the A2
report offered this leg as a separate trial.

## Why this leg exists

In A2 the wire sequence's uniform-permutation null was the wrong generative
model: `wire = a | b` by construction (verified semantics; zero OR
violations in the 800-tick check on record). Permuting wire bits destroys
the joint (a, b) pattern, so an excess over that null is the expected
footprint of the OR construction, not structure. This leg replaces the null
with the construction itself: permute each side's bits independently and OR
them. What survives that null is structure in the JOINT timing of the two
sides beyond their separate densities — which is the only thing a wire
sequence could add over its sides.

## Object and population (fixed before counting)

- Same file and window as A2: `runs/bit-shared/20261007T000000Z.jsonl`,
  first 50,000 consecutive tick rows, ticks 2,441,528–2,491,527.
- Observed sequence: `W_t = a_t | b_t` (the recorded `wire` field; the
  script asserts `wire == a | b` on every row of the window and fails if
  any row violates it).
- Null sequences: for each of 500 shuffles, independently permute the
  window's `a` bits and the window's `b` bits (preserving each side's count
  exactly), then OR them. Fixed seed 20261031, same seed as A2 (the
  permutation streams differ because two arrays are permuted per shuffle;
  the seed is stated, not reused as a claim of identical shuffles).
- Density cap: the (0.2, 0.8) cap from A2 is WAIVED for this leg, stated
  before counting, because the null is construction-matched: it preserves
  each side's density and the OR mechanism, so the wire density (0.8259 in
  the window) is a property of the construction, not an unmodeled artifact.
  The waiver applies ONLY to this leg and ONLY with this null.

## Measure

3-term AP count in the positions of 1s, d ≥ 1, within the window — the same
count as A2. Report: observed count, null mean/SD/min/max, z, p = fraction
of nulls with count ≥ observed (one-sided: excess over the OR null).

## Bohr frequency set (stated before counting)

Same rule as A2: the 8 frequencies with the largest |Fourier| magnitudes of
the observed window's wire indicator, computed once before any AP count,
reported verbatim. No frequency is added or dropped after seeing counts.

## Decision rule (fixed before counting)

- p ≥ 0.05: no excess AP density in the wire sequence over the OR null. The
  wire's AP density is fully accounted for by the two sides' densities plus
  the OR construction. Not a proof of randomness; the null interval is the
  finding.
- p < 0.05: excess AP density in the wire sequence over the OR null — a
  finding about the joint timing of the two sides, reported with count,
  null mean/SD, and z. It is NOT a Kelley–Meka construction and does NOT
  name either side the drive agent.
- Theorem-application verdict (pre-registered, both cases): the AP-density
  DIAGNOSTIC applies; the Kelley–Meka theorem in its own form does not
  follow from a count alone, because the theorem constructs a Bohr set and
  a density increment from the count, and no such construction is performed
  here. No verdict on the theorem follows from this trial either way.

## Outputs

Results file with the table, the frequency set, the window's tick range,
densities of a, b, and wire (observed and null-mean), null summaries, and
the verdicts above. Source files are never modified; the script reads the
tick file only. The protocol's hash is recorded in the results file.
