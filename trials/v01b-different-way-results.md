# V-01b — the threshold question tested a different way — results

Protocol: `v01b-different-way-protocol.md` (pre-registered 2026-10-31,
before any V-01b count). Ordered by perg's "Can we test in a
different way" (2026-10-31 16:57 EDT). Computation:
`v01b-different-way.py` (read-only over the saved rows; full JSON:
`v01b-different-way-results.json`). Source files never modified.
Two-way agreement (direct vs cell aggregation, legs 1 and 3):
EXACT on every reported number.

## Leg 1 — Full population (nulls included): threshold still inert

For every threshold T in 0.50–0.95, the (coverage, accuracy) pair is
IDENTICAL to T = 0.8 in all four populations. The only threshold
that changes anything is T = 1.0, and there it hurts in all three
JEV populations (contract accuracy 0.796 → 0.723, hard 0.833 →
0.706, lag 0.903 → 0.798; coverage falls too) while gaining one row
in real-diff (0.714 → 0.750) at 100% escalation. All escalation at
T ≤ 0.95 is the fast-null leg alone: contract 12.0%, hard 37.5%,
lag 28.0%, real-diff 0.0%. The null leg does all the work; the
confidence leg does none, even with nulls back in.

## Leg 2 — Calibration: the signal is not informative

Fast accuracy does NOT strictly increase with confidence in ANY
population (rule required ≥3/4). In the JEV populations fast
accuracy is 1.000 at confidence 0.95 and lower at 1.0 in contract
(0.852, n=27); in real-diff the 0.95 cell (n=27) sits at 0.704
against a single 0.9-confidence row at 1.000. Caveat, stated: the
0.99 cells hold n=1–2 rows, so this is a weak descriptive check,
not a proof of miscalibration — but nothing here shows confidence
carrying usable ordering information, and the direction is flat to
inverted, never increasing.

## Leg 3 — Oracle bound: no headroom in the JEV populations

Headroom (oracle − fast-only) is 0.000 in P-contract, P-hard, and
P-lag: within every confidence cell the slow seat never beats the
fast seat, so no confidence-value-based rule — threshold or
otherwise — can beat the fast seat on these rows. Real-diff
headroom is one row (0.036): the 0.95 cell's slow accuracy (0.741)
edges fast (0.704), and reaching it means escalating the whole cell
— the T = 1.0 rule at 100% escalation, already seen in V-01.

## Reading (labeled)

The V-01 refutation survives the different-way test and gets
stronger: it is not an artifact of excluding null rows, and it is
not a matter of picking the wrong threshold. On these rows the
confidence signal has no dynamic range, no ordering information,
and no exploitable headroom. What V-01b does NOT show: why the
confidence numbers look this way (a seat that reports 0.95–1.0
almost regardless of outcome), or whether a differently-built
confidence — e.g. one derived from the calculator, the null rate,
or seat disagreement — would carry signal. Those are open, not
filled in here.
