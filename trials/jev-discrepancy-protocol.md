# Protocol — Komlós discrepancy trial (A1), pre-registered before computing

Written 2026-10-31, before any discrepancy value was computed. File-format inspection only (keys, overlaps, null semantics) was done before writing; no outcome measure was computed before this protocol.

## Question
Does the disagreement pattern across two seats carry a structured discrepancy, measured as a signed imbalance, beyond what shuffling the seats' correctness labels would produce? And does the Komlós (Bansal–Jiang, (log N)^{1/4}) bound actually apply to this object in its own form?

## Populations (reported separately, never pooled across overlapping files)
- P-contract: `~/workspace/jev-decisions.json`, 50 rows, seats fast + hammer.
- P-hard: `~/workspace/jev-decisions-hard.json`, 40 rows, seats fast + hammer.
- P-lag: `~/workspace/jev-lag-decisions.json`, 100 rows, seats fast + hammer.
- P-realdiff: `~/workspace/real-diff-coder/decisions-coder30.json` + `decisions-next.json`, 28 items paired by `decision_id`, seats coder30 + coder-next, ground truth from `~/workspace/real-diff-coder/ground_truth.json`.

Correction to the application file (`theoretical-math-applications-spudcell-wire-fleet.md` §4 A1), recorded here before computing: that file said "280 JEV + 56 real-diff rows". That is WRONG as a pairable count. The lag file shares 40 prompt_refs with the contract file and 40 with the hard file, so the files overlap and must not be pooled. The null-sensor file (100 rows, `jev-null-sensor-records.json`) has a single seat and cannot enter a two-seat discrepancy at all; it is excluded. No pooled total is reported.

## Inclusion rule
A row is INCLUDED only if BOTH seats answered: both decisions non-null. A null (empty / contract-failing / bare-word with no decision) is counted separately and NEVER counted as wrong. This matters because `hammer_correct` is recorded as false when the hammer decision is null; counting it as wrong would manufacture discrepancy. Fast-null and hammer-null counts are reported per population alongside the included N.

## Correctness
- JEV populations: `fast_correct` / `hammer_correct` as recorded, on included rows only.
- Real-diff: correct iff `seat_decision == ground_truth` for that `decision_id`.

## Measures (pinned)
For each population, on included rows only, the four cells: both-right, fast-only-right, slow-only-right (hammer-only / next-only), both-wrong. Let s_i = +1 if fast-only-right, −1 if slow-only-right, 0 if the seats agree. D1 = sum(s_i). Report D1, |D1|, N_included, all four cells, and per-seat error rates on included rows.

Permutation null (generative-null discipline, TH-163): shuffle each seat's correctness labels independently within the population, preserving each seat's error count on included rows, recompute |D1|; 5,000 shuffles, fixed seed 20261031. Report null mean, SD, and p = fraction of shuffles with |D1_shuffled| ≥ |D1_observed|. A two-sided-equivalent one-sided tail on |D1| is used because the question is imbalance in either direction.

Reference scales (descriptive only): sqrt(N_included) and (log N_included)^{1/4} with natural log, reported beside |D1|. These are scale comparisons, not bars. No verdict on the Komlós theorem follows from them either way, because the theorem governs vector balancing with a FREE sign choice per vector, and no sign choice with subject meaning exists here: the observed signing is fixed by which seat was right. If the empirical question (balanced vs structured) comes out either way, the theorem-application verdict is recorded separately and honestly: the discrepancy DIAGNOSTIC applies; the Komlós bound in its own form does not, because its sign-choice structure is absent from the subject.

## Decision rule (stated before seeing outcomes)
- If p ≥ 0.05: disagreement is balanced — no structured discrepancy detected at this size. Record A1's empirical leg as VOID/NO-SIGNAL at these Ns; do not claim balance is proven (report the null interval).
- If p < 0.05: structured discrepancy exists in that population — a finding about the ensemble, to be reported per population with its direction (which seat is favoured) and size. It is NOT a finding about Komlós.
- In both cases, record the theorem-application verdict as above: diagnostic yes, Komlós-in-own-form no, with the reason stated (no subject-meaningful sign choice). If a sign-choice structure is discovered in the data during analysis, it must be stated as a NEW pinning and the verdict revisited — it cannot be read back into this protocol.

## Amendment A (2026-10-31, before any verdict was reported) — the first null was degenerate

The first computation under this protocol returned null SD = 0.00 and null mean exactly equal to |D1| in every population. That is not a finding; it is a design error in the null, caught by the SD check. Algebra: D1 = fast_only − slow_only = (F − both_right) − (S − both_right) = F − S, where F and S are the seats' correct counts. Shuffling each seat's labels independently preserves F and S, so D1 cannot vary. D1 is therefore a MARGINAL difference (error-rate difference), not a pairing-structure measure, and it has no permutation null. The first run's p-values (all 1.0000) are VOID and are not reported as results; they are recorded here only as the error that forced this amendment.

Corrected structure statistic (pinned by this amendment, before re-computing): the SLOW-ONLY count — rows where the slow seat alone is right. Null: permute the slow seat's correctness labels relative to the fast seat's (preserving each seat's correct count), 5,000 shuffles, fixed seed 20261031; p = fraction of shuffles with slow_only_shuffled ≤ slow_only_observed (one-sided: the question is whether the slow seat is solely right less often than chance pairing would give — i.e. whether disagreement favours the fast seat structurally, cf. TH-058's 41/41 fast-right pattern). Also report the disagreement count K = fast_only + slow_only with its two-sided shuffled null for completeness. D1 is still reported, as a marginal imbalance with the scale columns, with NO null test and NO p-value. The theorem-application verdict in the decision rule above stands unchanged.

## Outputs
Computation script (read-only over source files) and a results file with per-population tables, the null summaries, the scale comparisons, and the verdicts above. Source files are never modified. The protocol's own hash is recorded in the results file, not in this file. The results file records the amended protocol hash (after Amendment A).
