# Kelley–Meka AP-density trial (A2) — pre-registered protocol

Written 2026-10-31, BEFORE any AP count on wire data. Data model: see
`wire-tick-data-map.md`. Counting code: `wire-ap-count.py` (validated against
brute force on synthetic data before the trial run; validation is not a trial
result).

## Object

Binary sequences over consecutive ticks in ONE shared-mode file
(`runs/bit-shared/` on mrfloppy): `A_t = a`, `W_t = wire`. APs are 3-term
arithmetic progressions in the POSITIONS of 1s: triples (x, x+d, x+2d),
d ≥ 1, all three positions carrying 1, within the window. Trivial d = 0
triples are not counted.

## Population (fixed before counting)

- File: `runs/bit-shared/20261007T000000Z.jsonl` — chosen by the map's rule
  (complete consecutive ticks; densities in (0.2, 0.8) for both A and W),
  not by assumed identity with the E-W1 population.
- Window: the FIRST 50,000 consecutive tick rows of the file. Fixed before
  counting; no window shopping.
- Sequences counted: A and W, separately, same window, same null procedure.
- Exclusion: B is not counted in this trial (density 0.7593 is inside the
  range, but the trial is fixed at two sequences; B stays for a later,
  separately pre-registered run if ordered).

## Null (generative, TH-163)

For each sequence: 500 independent uniform permutations of the window's bits
(preserving density exactly), same AP count each time, fixed seed 20261031.
Report: observed count, null mean, null SD, z, and p = fraction of nulls with
count ≥ observed (one-sided: the question is excess AP density over a
density-matched random set). A Markov-preserving null is NOT used; if the
result is significant, a lag-1-preserving sensitivity run is a separate,
separately pre-registered trial, not a post hoc addition to this one.

## Bohr-set frequency set (stated before counting)

The Kelley–Meka sifting step needs a frequency set before counting. This
trial fixes it as: the 8 frequencies with the largest |Fourier| magnitudes
of the window's indicator, computed ONCE on the observed window before any
AP count, and the SAME 8 frequencies used for every null permutation's
sifting diagnostic. The frequency set is reported verbatim in the results.
No frequency is added or dropped after seeing counts. (The AP count itself
does not depend on the frequency set; the set is fixed so the sifting
diagnostic, if computed, is not cherry-picked.)

## Decision rule (fixed before counting)

- p ≥ 0.05 in a sequence: no excess AP density detected at that window size.
  Not a proof of randomness; the null interval is the finding.
- p < 0.05 in a sequence: excess AP density in that sequence's window — a
  finding about the emission sequence, reported with count, density, null
  mean/SD, and z. It is NOT a proof that Kelley–Meka sifting applies: the
  theorem's conclusion (a large structured subset / density increment) is a
  further construction, not the count.
- Theorem-application verdict (pre-registered, both cases): the AP-density
  DIAGNOSTIC applies; the Kelley–Meka theorem in its own form does not
  follow from a count alone, because the theorem constructs a Bohr set and a
  density increment from the count, and no such construction is performed
  here. No verdict on the theorem follows from this trial either way.

## Outputs

Results file with per-sequence table, the frequency set, the window's tick
range, densities, null summaries, and the verdicts above. Source files are
never modified; the counting script reads the tick file only. The protocol's
hash is recorded in the results file.
