# AP-density trial, segment-preserving null for B (N9) — results

Protocol: `wire-ap-segnull-protocol.md`, sha256
`018705a6ee7220f0d74e0d701bc2c9d03b732cd625c121069bf95ed59aac90bd`
(pre-registered 2026-10-31, before any segment-preserving count). Data model:
`wire-tick-data-map.md`. Counting: `wire-ap-segnull-count.py`, FFT
method, segment-preservation asserted in-script on every shuffle.
Read-only over the source file on mrfloppy; nothing was modified
there. Run: first 50,000 consecutive tick rows of
`runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527,
sequence B, 10 segments × 5,000 ticks, 500 within-segment shuffles,
seed 20261031. Full JSON: `wire-ap-segnull-results.json`. Stderr was
empty; the preservation assertion passed on all 500 shuffles.

| Quantity | Value |
|---|---|
| Observed APs | 244,959,744 (reproduces N1 exactly — built-in check passed) |
| Segment densities | 0.6038, 0.6046, 0.7360, 0.7416, 0.7618, 0.7448, 0.7650, 0.7698, 0.7632, 0.7576 (match N8 exactly) |
| Null mean / SD / range | 244,692,592 / 78,648 / 244,438,851–244,930,958 |
| Observed − null mean | +267,152 (+0.11%) |
| z | +3.40 |
| p (null ≥ observed) | 0.000 |

## Reading (per the pre-registered decision rule)

Excess persists beyond the step profile: all 500 nulls fall below the
observed count, so p = 0.000 under the rule. But the MAGNITUDE tells
the fuller story, and it is reported alongside the p-value rather
than behind it: the step plus per-segment densities account for
almost the entire N1 excess. The null mean moved from 237,993,541
(uniform) to 244,692,592 (segment-preserving) — 96.2% of the gap to the
observed count is closed by the density profile alone. What remains
is +267,152 progressions, 0.11% above the null mean, exceeding the
highest null by 28,786.

The z-series across null families is now complete as a series, with
no trend fitted and no extrapolation claimed:

    uniform +17.28 → L=100 blocks +9.50 → L=1000 blocks +3.68
    → segment-preserving +3.40

Each coarser, more construction-faithful null absorbs more of the
excess. What survives all four is small, persistent, and of undecided
source: it could be within-segment progression structure (arrangement
the within-segment permutation destroys), or finer density variation
inside the 5,000-tick segments (sub-segment drift the profile does
not capture), or both. This trial does not separate those. The
defined follow-up is N10: a finer segment-preserving null (e.g. 50
segments × 1,000 ticks). If the residual vanishes under N10, finer
density profiling explains it; if it persists, within-segment
structure is real. N10 is NOT run here. Note the regress honestly:
each finer profiling absorbs more by construction; the measurement is
at what scale the residual stops shrinking, and that scale is not yet
reached.

Bohr frequency set (same rule as N1, reported verbatim):
[0, 1, 2, 3, 4, 7, 8, 2474] — identical to N1/N8, as it must be for the
same window and sequence.

## Theorem-application verdict (pre-registered)

Diagnostic only; no Kelley–Meka construction; no drive naming. No
verdict on the theorem follows from this trial either way.
