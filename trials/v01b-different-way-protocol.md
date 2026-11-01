# V-01b — the threshold question tested a different way

Written 2026-10-31, BEFORE any V-01b count. Ordered by perg's
"Can we test in a different way" (2026-10-31 16:57 EDT) after V-01
refuted TH-065 on included rows only. V-01's sweep excluded null
rows and never asked whether the confidence signal itself carries
information. This protocol tests the same claim — can a confidence
threshold beat 0.8? — with three different instruments on the same
saved rows. It does NOT re-run the V-01 grid; it asks what V-01
could not ask.

## Why this exists (stated, per the audit)

V-01 found the threshold inert because fast confidences never dip
below 0.9 on included rows. That leaves three questions open: (1)
does the threshold matter once null rows are back in, since the
decider escalates on fast nulls too? (2) is fast confidence
informative at all — do higher-confidence fast decisions fail less
often? (3) could ANY confidence-based rule beat the fast seat, even
a non-threshold one? Each leg below answers one. If all three come
back negative, the refutation is not a quirk of the included-row
restriction; if any comes back positive, the live follow-up changes.

## Populations

Same four populations as V-01 (P-contract, P-hard, P-lag,
P-realdiff), same row files. Leg 1 uses ALL rows (n_total); legs 2
and 3 use included rows only (both seats answered), same definition
as Trial 1 / V-01.

## Leg 1 — Full population (nulls included)

Escalate iff fast_decision is None OR fast_confidence < T (T on the
same 11-point grid 0.50–1.00). Final decision: escalated → slow
decision if the slow seat answered, else NO final two-seat decision
(that escalation leaves the two-seat scope — it goes up, not to a
third seat here). Report per population: escalation rate (all rows),
coverage (fraction of rows with a final two-seat decision), accuracy
among covered rows. Threshold MATTERS iff some T != 0.8 changes the
(coverage, accuracy) pair versus T = 0.8. Otherwise the threshold
is inert even with nulls in play.

## Leg 2 — Calibration (is the signal informative?)

Included rows only. Fast accuracy by distinct fast_confidence value,
per population, with cell counts. Descriptive rule, fixed here: the
signal is informative iff fast accuracy strictly increases with
confidence in at least 3 of 4 populations. No p-values: cell counts
are small and this is a signal check, not a threshold claim. A flat
or inverted pattern means the confidence numbers carry no usable
ordering information on these rows.

## Leg 3 — Oracle bound (could ANY confidence rule help?)

Included rows only. Group by distinct fast_confidence value; within
each value-cell, the oracle escalates exactly the cells where slow
accuracy exceeds fast accuracy. Bound = accuracy of that oracle
rule. Headroom = bound − fast-only accuracy, per population. If
headroom is 0, NO confidence-value-based rule — threshold or
otherwise — can beat the fast seat on these rows. If headroom > 0,
headroom exists but a monotone threshold rule may still not reach
it; that distinction is stated, not blurred.

## Two independent computations

Legs 1 and 3 are computed two ways — direct per-row counting and
cell aggregation — and must agree EXACTLY on every reported number.
Leg 2 is read off the same cell table used by leg 3's aggregation
way and cross-checked against the direct counts. Any disagreement
stops the verdict until investigated.

## Outputs

Results file with the three legs' tables, the two-way agreement
check, and the verdict per leg under the rules above. Source files
never modified. Read-only over the saved rows.
