# AP-density trial, L=1000 block null + drift check (N8) — results

Protocol: `wire-ap-block1000-protocol.md`, sha256
`9f6ee1c67321f3cfc4db8c6829c926eb4644c7a6c4a8240085ac750918bd48e9`
(pre-registered 2026-10-31, before any L=1000 count or drift
measurement).
Data model: `wire-tick-data-map.md`. Counting: `wire-ap-block-count.py`
(--block 1000) and `wire-ap-drift-check.py`, both FFT-based, validated
before the runs. Read-only over the source file on mrfloppy; nothing was
modified there. Window (both parts): first 50,000 consecutive tick rows
of `runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527,
sequence B. Full JSON: `wire-ap-block1000-results.json` (Part 1) and
`wire-ap-drift-results.json` (Part 2).

Metadata correction, named plainly: the block-count script's JSON
`null` description string was hardcoded to "100-tick blocks" and was
not parameterized; in the L=1000 run's JSON that string is wrong. The
authoritative fields are `block: 1000` and `nblocks: 50`, which are
correct, and the script has since been fixed to parameterize the
string. No count is affected.

## Part 1 — L=1000 block null

| Quantity | Value |
|---|---|
| Observed APs | 244,959,744 (reproduces N1 exactly — built-in check passed) |
| Null mean / SD / range | 238,284,375 / 1,812,894 / 232,083,078–242,777,327 |
| z | +3.68 |
| p (null ≥ observed) | 0.000 |

Per the pre-registered rule, excess persists beyond 1000-tick blocks:
all 200 nulls fall below the observed count. But the effect SHRINKS as
the null preserves more structure: z = +17.28 (uniform) → +9.50
(L=100) → +3.68 (L=1000), while the null SD grows (only 50 blocks to
permute). The monotone decline is itself a finding: B's progression
structure is spread across scales, and each coarser null absorbs more
of it. Persistence at L=1000 is real under the rule, and weaker than
at finer scales — both facts are reported, neither alone.

## Part 2 — Drift check + decomposition

Segment densities (10 segments × 5,000 ticks, in tick order):

| Seg | Ticks | Density | APs within |
|---|---|---|---|
| 0 | 2,441,528–2,446,527 | 0.6038 | 1,364,416 |
| 1 | 2,446,528–2,451,527 | 0.6046 | 1,375,608 |
| 2 | 2,451,528–2,456,527 | 0.7360 | 2,545,676 |
| 3 | 2,456,528–2,461,527 | 0.7416 | 2,535,046 |
| 4 | 2,461,528–2,466,527 | 0.7618 | 2,752,541 |
| 5 | 2,466,528–2,471,527 | 0.7448 | 2,588,027 |
| 6 | 2,471,528–2,476,527 | 0.7650 | 2,804,730 |
| 7 | 2,476,528–2,481,527 | 0.7698 | 2,818,375 |
| 8 | 2,481,528–2,486,527 | 0.7632 | 2,813,462 |
| 9 | 2,486,528–2,491,527 | 0.7576 | 2,717,771 |

Density range: 0.1660 (min 0.6038, max 0.7698) — MATERIAL drift by the
pre-registered threshold (≥ 0.10). The shape is a STEP, not a gradual
drift: segments 0–1 at ~0.60, segments 2–9 at ~0.74–0.77, with the step
at ~tick 2,451,528 (10,000 ticks into the window).

Decomposition (identity holds exactly): full-window APs 244,959,744 =
within-segment 24,315,652 + cross-segment 220,644,092. Cross share:
90.1%. The AP count is dominated by progressions spanning segment
boundaries — long-range, large-d progressions.

Per the protocol's Part 2(c): cross share large AND drift material →
the long-range reading is DRIFT-COMPATIBLE. The step in density plus
90% cross-segment APs is consistent with the density step generating
much of the excess. This does NOT prove drift causes the excess, and
it does not close the question: whether progression structure exists
BEYOND the density step is undecided. The defined follow-up is N9: a
segment-preserving null (permute bits within each 5,000-tick segment
independently, preserving per-segment densities). If excess persists
under N9, structure beyond the step exists; if it vanishes, the step
explains N1. N9 is NOT run here.

## Theorem-application verdict (pre-registered)

Diagnostic only; no Kelley–Meka construction; no drive naming. No
verdict on the theorem follows from either part.
