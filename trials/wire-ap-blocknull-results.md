# AP-density trial, block null for B — results

Protocol: `wire-ap-blocknull-protocol.md`, sha256
`0eeec28dc3f098576466c02dc16252af515d57c153793ee8b55b9a150fd1a9d9`
(pre-registered 2026-10-31, before any block-null count). Data model:
`wire-tick-data-map.md`. Counting: `wire-ap-block-count.py`, FFT method,
block-permutation mechanics validated on synthetic data before the
trial run. Read-only over the source file on mrfloppy; nothing was
modified there. Run: first 50,000 consecutive tick rows of
`runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527,
500 blocks of 100 ticks, 200 block-order shuffles, seed 20261031.
Full JSON: `wire-ap-blocknull-results.json`. Stderr was empty.

| Quantity | Value |
|---|---|
| Density of B | 0.7248 |
| Observed APs | 244,959,744 (reproduces N1 exactly — built-in check passed) |
| Block-null mean / SD / range | 238,055,822 / 726,563 / 236,308,700–240,876,060 |
| z | +9.50 |
| p (null ≥ observed) | 0.000 |

## Reading (per the pre-registered decision rule)

Excess persists beyond 100-tick blocks: the observed count exceeds
every one of the 200 block nulls. Per the rule, B carries progression
structure at longer range than ≤100-tick burst structure alone. The
burstiness reading of N1 is therefore NOT sufficient: preserving all
structure inside 100-tick blocks does not account for the excess.

Limit, stated plainly: this trial does not separate within-block
progression structure from window-scale density drift (if B's density
varies across the 50,000-tick window, block shuffling preserves block
densities but rearranges them, and APs concentrate in denser regions).
Whether the excess is within-block progressions, a density gradient, or
both is NOT decided here. The defined follow-ups are a density-drift
check on the window and an L = 1000 block null (N8) — neither run here.

Bohr frequency set (same rule as N1, reported verbatim):
[0, 1, 2, 3, 4, 7, 8, 2474] — identical to N1, as it must be for the
same window and sequence.

## Theorem-application verdict (pre-registered)

Diagnostic only; no Kelley–Meka construction; no drive naming. No
verdict on the theorem follows from this trial either way.
