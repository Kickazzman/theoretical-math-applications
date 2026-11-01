# Kelley–Meka AP-density trial, OR-null leg (A2b) — results

Protocol: `wire-ap-or-null-protocol.md`, sha256
`74d2b36572cf834adfa8c9874c58679bca36490fe338fe0af7ae0b995c0c14b3`
(pre-registered 2026-10-31, before any OR-null count). Data model:
`wire-tick-data-map.md`. Counting: `wire-ap-or-count.py`, FFT method,
validated 40/40 against the d-loop on synthetic OR sequences before the
trial run. Read-only over the source file on mrfloppy; nothing was modified
there. Run: first 50,000 consecutive tick rows of
`runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527, 500
OR-null shuffles, seed 20261031. Full JSON: `wire-ap-or-results.json`.
Stderr was empty; the script's OR assertion (`wire == a | b` on every row)
passed.

| Quantity | Value |
|---|---|
| Density a / b / wire (observed) | 0.4006 / 0.7248 / 0.8259 |
| Null wire density (mean) | 0.8351 |
| Observed APs in wire | 358,986,556 |
| OR-null mean / SD / range | 363,963,962 / 1,305,288 / 360,004,915–367,845,778 |
| z | −3.81 |
| p (null ≥ observed) | 1.000 |

## Reading (per the pre-registered decision rule)

No excess AP density over the OR null — p = 1.000, and the observed count
sits BELOW the entire null range. The wire's AP density is fully accounted
for by the two sides' densities plus the OR construction; against the
construction-matched null it is, if anything, low. The deficit (z = −3.81)
and the density gap (observed wire density 0.8259 vs OR-null mean 0.8351)
point the same way: the real sides' 1s coincide more than independent
permutation would give, so the real OR is denser in overlaps and sparser in
AP-forming triples than independent sides would produce. That is a finding
about joint timing, consistent in direction with the dependence measurement
on record (E-W1), and it is NOT an excess, NOT a Kelley–Meka construction,
and does NOT name either side the drive agent.

This closes the A2 wire question as posed: the z = +15.78 in the first
trial was the footprint of the wrong null, exactly as suspected. Against
the right null there is no excess to explain.

Bohr frequency set (fixed before counting, reported verbatim):
[0, 1, 2, 3, 7, 110, 735, 1006] — identical to the A2 wire run, as it must
be for the same window and sequence.

## Theorem-application verdict (pre-registered)

The AP-density DIAGNOSTIC applies; the Kelley–Meka theorem in its own form
does not follow from a count alone. No verdict on the theorem follows from
this trial either way.
