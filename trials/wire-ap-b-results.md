# Kelley–Meka AP-density trial, B sequence (N1) — results

Protocol: `wire-ap-b-protocol.md`, sha256
`d65ce8038056d55c852f1d43256c8c32a1bf6090086d693f98788e3ae04dca7d`
(pre-registered 2026-10-31, before any B-sequence AP count). Data model:
`wire-tick-data-map.md`. Counting: `wire-ap-count.py`, FFT method,
validated as in A2. Read-only over the source file on mrfloppy; nothing
was modified there. Run: first 50,000 consecutive tick rows of
`runs/bit-shared/20261007T000000Z.jsonl`, ticks 2,441,528–2,491,527
(the same window as A2/A2b), 500 uniform permutations, seed 20261031.
Full JSON: `wire-ap-results-b.json`. Stderr was empty.

| Quantity | Value |
|---|---|
| Density of B | 0.7248 (inside the (0.2, 0.8) cap — leg stands) |
| Observed APs | 244,959,744 |
| Null mean / SD / range | 237,993,541 / 403,146 / 236,701,095–239,240,457 |
| z | +17.28 |
| p (null ≥ observed) | 0.000 |

## Reading (per the pre-registered decision rule)

Excess AP density in B's window, significant under the decision rule:
the observed count exceeds every one of the 500 density-matched nulls by
~5.7M progressions at the nearest null. Per the rule, this is a finding
about the second side's emission sequence — its 1-positions carry
3-term-progression structure beyond what density alone gives. It is NOT
a Kelley–Meka construction and does NOT name B the drive or the peer;
side identity is still unpinned.

## Re-derivation check

Because this is the first POSITIVE AP result in the programme, the
observed count was re-derived by the independent d-loop method on the
same window: loop count = 244,959,744, exactly the FFT count. The excess
is a property of the sequence, not of the counting method. (Loop run:
2 shuffles, same seed; null values from that run are not reported as
results — only the observed-count agreement is used.)

## Interpretation (labeled as interpretation, not a further measurement)

B's Bohr frequency set is dominated by the lowest frequencies
[0, 1, 2, 3, 4, 7, 8, 2474], unlike A's mid-range set
[0, 401, 708, 1006, 1396, 1487, 2595, 2747]. Low-frequency dominance is
consistent with burstiness — long runs of 1s — which uniform permutation
destroys and which mechanically produces excess APs. The honest reading
of the excess is therefore: **B's timing is not exchangeable; it has
temporal structure beyond its density, most plausibly burst structure.**
Whether that structure is the peer's Markov dynamics, a regime effect,
or something else is NOT decided by this trial and is not claimed here.

Synthesis across the three AP legs (labeled synthesis): A is null
(p = 0.836), B carries excess (p = 0.000), and the wire sits BELOW its
OR null (z = −3.81). Together: the wire's progression structure is
carried by B's timing plus the joint coincidence pattern, not by A
alone and not by the OR construction. Each leg's verdict stands on its
own null; the synthesis adds no new claim beyond their conjunction.

## Theorem-application verdict (pre-registered)

The AP-density DIAGNOSTIC applies; the Kelley–Meka theorem in its own
form does not follow from a count alone, because the theorem constructs
a Bohr set and a density increment from the count, and no such
construction was performed here. No verdict on the theorem follows from
this trial either way.
