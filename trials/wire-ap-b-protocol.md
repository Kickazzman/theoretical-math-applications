# Kelley–Meka AP-density trial, B sequence (N1) — pre-registered protocol

Written 2026-10-31, BEFORE any B-sequence AP count. Companion to
`wire-ap-protocol.md` (the A/W trial, A2). Data model:
`wire-tick-data-map.md`. Counting code: `wire-ap-count.py` (FFT method,
validated 60/60 against the d-loop on synthetic arrays and
exact-reproducing the d-loop count 394,514 on a real 5,000-tick pilot
window for sequence A; the counting code is sequence-agnostic — the
`--seq` flag selects the field). Ordered by perg's tap "Run the
B-sequence AP trial next" (2026-10-31 15:16 EDT) on the comparison map's
ranked next measurement N1. B was fixed OUT of A2 ("B is not counted in
this trial"), so it needs this own pre-registration; nothing from A2's
result is carried into B's decision except the shared window and null
procedure.

## Object and population (fixed before counting)

- Same file and window as A2: `runs/bit-shared/20261007T000000Z.jsonl`,
  first 50,000 consecutive tick rows, ticks 2,441,528–2,491,527.
- Sequence counted: `B_t = b` only. No other sequence is counted in this
  trial. The A and W results are not re-counted.
- Density cap (same rule as A2, stated before counting): if the window
  density of B falls outside (0.2, 0.8), the leg is EXCLUDED — reported
  for completeness, not claimed. (The OR-null trial's JSON recorded the
  window's b density as 0.7248; the cap is still applied to the density
  measured in THIS run, not assumed from that record.)

## Null (generative, same as A2)

500 independent uniform permutations of the window's B bits (preserving
density exactly), same AP count each time, fixed seed 20261031.
Report: observed count, null mean, null SD, min/max, z, and p = fraction
of nulls with count ≥ observed (one-sided: excess AP density over a
density-matched random set).

## Bohr frequency set (stated before counting)

Same rule as A2: the 8 frequencies with the largest |Fourier| magnitudes
of the observed window's B indicator, computed once before any AP count,
reported verbatim. No frequency is added or dropped after seeing counts.

## Decision rule (fixed before counting)

- p ≥ 0.05: no excess AP density in B detected at that window size. Not a
  proof of randomness; the null interval is the finding.
- p < 0.05: excess AP density in B's window — a finding about the second
  side's emission sequence, reported with count, density, null mean/SD,
  and z. It is NOT a proof that Kelley–Meka sifting applies and does NOT
  name B the drive or the peer.
- Theorem-application verdict (pre-registered, both cases): the AP-density
  DIAGNOSTIC applies; the Kelley–Meka theorem in its own form does not
  follow from a count alone, because the theorem constructs a Bohr set
  and a density increment from the count, and no such construction is
  performed here. No verdict on the theorem follows from this trial
  either way.

## Outputs

Results file with the table, the frequency set, the window's tick range,
density, null summaries, and the verdicts above. Source files are never
modified; the script reads the tick file only. The protocol's hash is
recorded in the results file.
