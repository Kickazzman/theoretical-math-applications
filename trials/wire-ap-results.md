# Kelley–Meka AP-density trial (A2) — results

Protocol: `wire-ap-protocol.md`, sha256
`ed435df58585f546dabde0a4ad98d687a09e404dd1cce097f47523d65c671878`
(pre-registered 2026-10-31, before any AP count). Data model: `wire-tick-data-map.md`. Counting: `wire-ap-count.py`,
FFT method, validated 60/60 against the d-loop on synthetic arrays and
reproducing the d-loop count exactly (394,514) on a real 5,000-tick pilot
window. Read-only over the source file on mrfloppy; nothing was modified
there. Both runs: first 50,000 consecutive tick rows of
`runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527,
500 uniform permutations, seed 20261031. Full JSON:
`wire-ap-results-a.json`, `wire-ap-results-wire.json`.

| Sequence | Density | Observed APs | Null mean | Null SD | z | p (≥ obs) | Verdict |
|---|---|---|---|---|---|---|---|
| A (`a`) | 0.4006 | 40,053,253 | 40,173,775 | 123,074 | −0.98 | 0.836 | No excess AP density detected |
| W (`wire`) | 0.8259 | 358,986,556 | 352,148,973 | 433,392 | +15.78 | 0.000 | EXCLUDED — see below |

## The wire leg is excluded, by the pre-registered rule

The protocol's saturation rule excludes any sequence whose window density
falls outside (0.2, 0.8). The wire window density is 0.8259, above the cap —
the full-file wire rate (0.8527) already warned of this, and the window
confirms it. The wire numbers are reported here for completeness and are NOT
a trial finding. Two further reasons they must not be claimed:

1. The uniform-permutation null is the wrong generative model for `wire`:
   `wire = a | b` by construction. Permuting wire bits destroys the joint
   (a, b) pattern, so an excess over that null is the expected footprint of
   the OR construction (and of any burstiness in a and b), not evidence of
   Kelley–Meka structure. The right null for W would permute a and b
   separately and OR them — a separate, separately pre-registered trial,
   not run here.
2. At density 0.83 the AP count is dominated by density itself (359M
   progressions); the count carries little structural information, which is
   exactly what the density cap exists to prevent.

## The A leg is the trial

Sequence A — one agent's emission bits over 50,000 consecutive ticks,
density 0.40 — shows no excess 3-term AP density over density-matched
random sets (p = 0.836, observed slightly BELOW the null mean). Per the
decision rule: no excess AP density detected at this window size. This is
not a proof of randomness; the null interval is the finding.

Bohr frequency sets (fixed before counting, reported verbatim): A:
[0, 401, 708, 1006, 1396, 1487, 2595, 2747]; W: [0, 1, 2, 3, 7, 110, 735, 1006]
(excluded leg; reported for completeness only).

## Theorem-application verdict (pre-registered)

The AP-density DIAGNOSTIC applies; the Kelley–Meka theorem in its own form
does not follow from a count alone — the theorem constructs a Bohr set and a
density increment from the count, and no such construction was performed.
No verdict on the theorem follows from this trial either way. No claim is
made naming either side the "drive" agent; the map's identity gap stands.
