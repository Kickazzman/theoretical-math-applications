# V-01 / TH-065 overshoot threshold sweep — pre-registered protocol

Written 2026-10-31, BEFORE any sweep count. Ordered by perg's "lets
test these and try to get the answer in multiple ways" (2026-10-31
16:54 EDT), taken as: start at the head of the value order (V-01,
cheapest first) and test it by multiple independent computations.
Settler as recorded in all-theories-map §8 V-01 (from
theories-full-inventory TH-065).

## Question

Does sweeping the escalation confidence threshold over 0.5–1.0 find
a threshold dominating 0.8 on final accuracy + escalation rate?

## Population and rule (fixed before counting)

- Populations, reported SEPARATELY, never pooled (per the
  discrepancy-protocol correction: the lag file shares 40 prompt_refs
  with contract and 40 with hard, so pooling double-counts items):
  P-contract (jev-decisions.json), P-hard
  (jev-decisions-hard.json), P-lag (jev-lag-decisions.json),
  P-realdiff (real-diff-coder/decisions-coder30.json as fast,
  decisions-next.json as slow, paired by decision_id against
  ground_truth.json).
- INCLUDED rows only, same definition as Trial 1: both seats
  answered (fast_decision and hammer_decision / seat_decision not
  None). Null rows are excluded, never counted as wrong.
- Escalation at threshold T: escalate iff fast_confidence < T
  (within included rows there are no fast nulls by definition; the
  fast-null escalation leg applies only to the full population and
  is out of scope here — stated, not hidden).
- Final decision: escalated → slow (hammer/next) decision counts;
  otherwise fast decision counts. Final accuracy = fraction of
  included rows whose final decision equals ground truth
  (fast_correct / hammer_correct fields for JEV; seat_decision vs
  ground_truth for real-diff). Escalation rate = fraction of
  included rows escalated.
- Grid: T in {0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90,
  0.95, 1.00} (11 points, 0.05 steps). The distinct fast_confidence
  values present in each population are reported alongside, since
  only thresholds crossing a present value can change the outcome.
- Dominance (per population): T dominates 0.8 iff (accuracy_T >
  accuracy_0.8 AND esc_T ≤ esc_0.8) OR (accuracy_T ≥ accuracy_0.8
  AND esc_T < esc_0.8). Strict improvement on one axis, no worse on
  the other.

## Decision rule (fixed before counting)

- CONFIRMED iff there EXISTS a threshold T that dominates 0.8 in at
  least 3 of the 4 populations AND 0.8 dominates T in 0 populations.
- REFUTED iff NO threshold dominates 0.8 in ANY population.
- Otherwise the rule returns NEITHER (table reported, no confirm /
  refute claimed) — ternary honesty; the per-population dominance
  sets are the finding.

## Three independent computations (all pre-registered, must agree)

All three run on the same included rows and grid. They must agree
EXACTLY on every (population, T) accuracy and escalation rate;
any disagreement stops the verdict until investigated.

- Way 1 — direct: per row, final = slow if fast_confidence < T
  else fast; accuracy and escalation computed by direct counting.
- Way 2 — cell aggregation: group included rows by
  (fast_correct, slow_correct, fast_confidence); for each T, sum
  cells with confidence < T as escalated (slow correctness counts)
  and the rest as fast. Different logic (aggregation, no per-row
  branching in the sweep loop).
- Way 3 — sorted step function: sort included rows by
  fast_confidence; escalation sets are prefixes of that order;
  evaluate accuracy at each distinct confidence value as the
  effective threshold (T just above each distinct value), and
  cross-check the 0.05 grid against it. Way 3 also reports the
  distinct confidence values per population.

## Outputs

Results file with the per-population tables (accuracy + escalation
at all 11 thresholds), the distinct confidence values, the
dominance sets, the three-way agreement check, and the verdict
under the rule above. Source files never modified. Read-only over
the saved rows. The protocol's hash is recorded in the results file.
