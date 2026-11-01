# JEV program item 4: cost-error frontier — summary (saved rows only, 2026-10-30)

**Headline: the leaner rule IS on the Pareto frontier, and the full rule is
dominated by it on every observed row — but the dominance is conditional,
and the insurance price is small enough that the design call stays open.**
On both fast+hammer populations, lean (null OR confidence < 0.8) reaches
zero perfect-calculator error at strictly lower cost than full, and
strictly lower floor-adjusted error too (full escalates correct answers
into calculator-failure exposure for zero observed gain). The full rule's
only value is insurance against a case never observed on this pair: a
future fast-wrong disagreement. That insurance costs 22–24 extra
calculator runs per 100 items and pays for its floor cost if just over
1% of future disagreements are fast-wrong. Whether that insurance is
worth it is the reader's design call, not something these rows settle.
No null-based or confidence-based policy catches a confident fast error:
ns2-a23 stays an error under every available policy on its population
except escalate-everything.

## 0. Method (offline sweep, no new seat runs)

- **Saved rows only.** No seat calls, no router, no GPU, no frank, no
  browser. Populations kept separate, never blended (different sensor
  availability):
  - (a) **lag**: 100 rows, fast + hammer (jev-lag-decisions.json).
  - (b) **orig+hard**: 80 rows, (a)+(b) only, fast + hammer
    (jev-decisions.json filtered to types a/b + jev-decisions-hard.json;
    the original file's 10 (c) rows are excluded — different question,
    no calculator ground truth in the same sense).
  - (c) **ns2** (null-sensor v2): 100 rows, fast ONLY
    (jev-null-sensor-records.json). Full rule unavailable here (no
    hammer, no disagreement).
- **Verification first.** Every headline count recomputed from raw rows
  matches the published run reports exactly, with zero warnings:
  lag nulls 28, fast-correct 72/72 when answered, disagreements 22/22
  fast-right; orig+hard nulls 20, fast-correct 60/60, disagreements
  19/19 fast-right; ns2 nulls 14, fast-correct 85/86, wrong-when-answered
  1 (ns2-a23). GT-consistency checks (fast_correct == decision ==
  ground_truth when answered) clean on all 280 rows; zero gt_mismatch
  flags. Confidence distributions: lag answered 1.0×49, 0.95×21,
  0.99×2; orig+hard 1.0×42, 0.95×16, 0.99×2; ns2 1.0×61, 0.95×23,
  0.99×1, 0.9×1 (ns2-a35).
- **Cost unit: escalation fraction** (calculator runs per item). NOT
  wall-clock time or tokens — duration is excluded (§5).
- **Error, two versions, always paired.** `err_perfect` = final error
  if the calculator resolves every escalated item correctly.
  `err_floor` = same, but each escalated item fails with the item-1
  floor P = 0.010 (point), Wilson band (0.0018, 0.0545). A failed
  escalated item counts as a final error. **No policy error is
  reported as exactly zero without its floor band attached** — every
  "0" below carries one. Rates are REALIZED on these rows; the band
  comes only from floor uncertainty, not from sampling error on the
  observed counts.

## 1. Frontier tables

### (a) Lag population (n = 100, fast + hammer)

| policy | cost (esc frac) | err_perfect | err_floor point (band) |
|---|---|---|---|
| fast-alone | 0.00 | 0.2800 | 0.2800 (0.2800, 0.2800) |
| null-only | 0.28 | 0.0000 | 0.0028 (0.0005, 0.0153) |
| **lean (null OR <0.8)** | **0.28** | **0.0000** | **0.0028 (0.0005, 0.0153)** |
| full (null OR disagree OR <0.8) | 0.50 | 0.0000 | 0.0050 (0.0009, 0.0272) |
| threshold+null t=0.99 | 0.49 | 0.0000 | 0.0049 |
| threshold+null t=1.0 | 0.51 | 0.0000 | 0.0051 |
| escalate-all (t=1.01) | 1.00 | 0.0000 | 0.0100 (0.0018, 0.0545) |

Lean ≡ null-only here (zero confidences below 0.8; the 0.8 rule never
fires on this population). Full costs 0.22 more than lean for zero
observed gain and a HIGHER floor error (0.0050 vs 0.0028): full is
strictly dominated by lean on observed rows under the floor model,
and cost-dominated (same perfect error, higher cost) under the
perfect model.

### (b) Orig+hard population (n = 80, fast + hammer)

| policy | cost (esc frac) | err_perfect | err_floor point (band) |
|---|---|---|---|
| fast-alone | 0.00 | 0.2500 | 0.2500 (0.2500, 0.2500) |
| null-only | 0.25 | 0.0000 | 0.0025 (0.0004, 0.0136) |
| **lean (null OR <0.8)** | **0.25** | **0.0000** | **0.0025 (0.0004, 0.0136)** |
| full (null OR disagree OR <0.8) | 0.4875 | 0.0000 | 0.0049 (0.0009, 0.0266) |
| threshold+null t=0.99 | 0.45 | 0.0000 | 0.0045 |
| threshold+null t=1.0 | 0.475 | 0.0000 | 0.0047 |
| escalate-all (t=1.01) | 1.00 | 0.0000 | 0.0100 (0.0018, 0.0545) |

Same shape as lag. Lean ≡ null-only (zero confidences below 0.8).
Full costs 0.2375 more than lean, zero observed gain, higher floor
error (0.0049 vs 0.0025): dominated on observed rows, same as lag.

### (c) Null-sensor population (n = 100, fast only; full N/A)

| policy | cost (esc frac) | err_perfect | err_floor point (band) |
|---|---|---|---|
| fast-alone | 0.00 | 0.1500 | 0.1500 (0.1500, 0.1500) |
| null-only | 0.14 | 0.0100 | 0.0114 (0.0103, 0.0176) |
| **lean (null OR <0.8)** | **0.14** | **0.0100** | **0.0114 (0.0103, 0.0176)** |
| threshold+null t=0.9 | 0.14 | 0.0100 | 0.0114 |
| threshold+null t=0.95 | 0.15 | 0.0100 | 0.0115 |
| threshold+null t=0.99 | 0.38 | 0.0100 | 0.0138 |
| threshold+null t=1.0 | 0.39 | 0.0100 | 0.0139 |
| escalate-all (t=1.01) | 1.00 | 0.0000 | 0.0100 (0.0018, 0.0545) |

Lean ≡ null-only here too (the only sub-0.95 confidence is 0.9, above
0.8). The residual 0.01 perfect error under every policy except
escalate-all is ns2-a23 (§4). Escalate-all's floor point (0.0100)
sits 0.0014 below lean's (0.0114) at 7× the cost — but its band
(0.0018, 0.0545) fully contains lean's band (0.0103, 0.0176), so the
point advantage is not distinguishable from floor uncertainty.
Practically: on ns2, lean is the frontier point; escalate-all is on
the point frontier only in a degenerate sense.

## 2. Threshold sweep reading: the confidence sensor buys nothing

On lag and orig+hard, the threshold+null curve is FLAT on accuracy
(err_perfect 0.0000 at every t) and rising on cost (lag 0.28 → 0.49 →
0.51 → 1.00; orig+hard 0.25 → 0.45 → 0.475 → 1.00). Every threshold
above 0.8 does nothing but escalate correct answers into floor
exposure. This is expected, not surprising: fast was never wrong
when answered on those populations (0/180), so no threshold can
recover an error that does not exist there.

On ns2, the threshold curve is flat at err_perfect 0.0100 from t=0.8
through t=1.0 — the only threshold that changes error is
escalate-all (t=1.01 → 0.0000). The single sub-0.95 row, ns2-a35
(conf 0.9, CORRECT), is a clean wasted-escalation demonstration:
t=0.95 escalates it (cost 0.14 → 0.15) for zero gain and a slightly
higher floor point (0.0114 → 0.0115), because escalating a correct
item can only add calculator-failure risk. A threshold that fires
on correct answers is pure cost.

Pure-threshold policies (confidence only, nulls NOT escalated) are
reported in the data files for completeness and are strictly worse:
error stays at the fast-alone null rate at every t (lag 0.28,
orig+hard 0.25, ns2 0.15→0.14 only at escalate-answered), because a
confidence threshold cannot fix a non-answer. At t=1.01 on lag,
pure-threshold escalates all 72 answered (all correct) and error
RISES to 0.2872 — worse than fast-alone (0.2800) — from floor
exposure alone. Threshold-only escalation without null fallback is
never a frontier policy on any population here.

## 3. Verdict: lean on the frontier, full dominated — conditionally

**On observed rows, lean dominates full, on both fast+hammer
populations.** Under the floor model the dominance is strict (lower
cost AND lower error); under the perfect model it is cost-dominance
(same zero error, lower cost). The frontier's zero-error point is
lean, not full, and no intermediate threshold improves on it.

**The condition that keeps the design call open: dominance on
observed rows assumes future disagreements behave like the 41
observed ones (13 + 6 + 22, all fast-right).** ns2-a23 proves fast
CAN err when answering at confidence 1.0 — on a population without
hammer, so it does not measure the disagreement-conditional rate,
but it breaks the "fast never errs" premise the dominance rests on.

## 4. Insurance pricing: what full buys, in numbers

| quantity | lag (n=100) | orig+hard (n=80) |
|---|---|---|
| full cost − lean cost (extra runs) | 22 (0.22) | 19 (0.2375) |
| observed accuracy gain of full over lean | 0 errors | 0 errors |
| extra floor cost of full (point) | 0.0022 | 0.0024 |
| disagreement rate | 0.22 | 0.2375 |
| break-even future fast-wrong-among-disagreements rate r | 0.01 | 0.01 |

Reading: full's extra floor cost is 0.22 × 0.010 = 0.0022 per item
(lag). Its expected gain, if a fraction r of future disagreements
are fast-wrong, is ≈ 0.22 × r per item. Full beats lean in
expectation iff r > 0.01 — if just over 1% of future disagreements
are fast-wrong, the insurance pays for itself. r is UNMEASURED on
this pair (0/41 observed); the rule-of-three upper bound consistent
with 0/41 is ≈ 0.073. At r = 0.073, full's expected gain is
0.22 × 0.073 = 0.0161 per item against a 0.0022 floor cost — a net
+0.0139 per item. So the insurance is CHEAP relative to plausible
values of r, even though its observed value is zero. That is the
whole design question in one number: pay 22–24% more calculator runs
for protection against a case at r somewhere between 0 and ~0.07,
with break-even at r = 0.01. These rows do not pick a side; they
price both.

## 5. ns2-a23: the blind spot of every null/confidence policy

ns2-a23 (capitalize_words, Tier 2, subtle): fast answered "pass" at
confidence 1.0; ground truth fail (the buggy variant is str.title(),
which turns "don't" into "Don'T" — the seat missed it). It was
answered via retry (2 attempts, 29.67 s), still wrong, still
confident.

Under each policy available on its (fast-only) population:
- fast-alone: error (counts in the 0.15).
- null-only: NOT escalated (it answered) → stays an error.
- lean (null OR <0.8): NOT escalated (1.0 ≥ 0.8) → stays an error.
- threshold+null at any t ≤ 1.0: NOT escalated (1.0 is the maximum
  confidence; conf < t fails for every observed t) → stays an error.
- escalate-all (t=1.01): escalated and resolved → the only policy
  that catches it, at cost 1.00.

**Say plainly: no null-based policy catches a confident fast error.**
Null and confidence are sensors for silence and hesitation; a
confident error is invisible to both. The only sensors that could
catch it on a fast+hammer population are disagreement (untested on
ns2 — no hammer there) and escalate-everything (priced above: a
0.0014 point gain inside the floor band at 7× the cost on ns2).
This is the frontier's hard edge: below cost 1.00, the ns2 error
floor is 0.01 (this row), not 0. And the floor band means even
escalate-all does not credibly beat lean on ns2 — it trades one
0.01 error source (confident fast error) for another 0.01 error
source (calculator failure), at full cost.

## 6. Duration exclusion (stated, with the reason)

Duration is OUT of this sweep. The lag-run and null-sensor duration
signals (answered ~10 s / ~4.5 s vs empty ~37 s / ~36 s) are
POST-HOC, not pre-decision predictors: null rows take two attempts
(the retry), so their durations include a second thinking burn, and
neither runner logged first-attempt latency separately. A policy
cannot price "escalate if slow" from a duration that is itself
caused by the null it would predict. What can be said honestly:
duration separates null from answered AFTER the fact on both runs;
it is not shown to predict null BEFORE the answer lands. A
duration-priced policy needs first-attempt latency logging — a
runner change, not a sweep over these rows. Cost here is therefore
in calculator runs per item, not seconds.

## 7. Limitations (everything that weakens the frontier)

1. **Constructed materials, not saved real work** (same caveat as
   all JEV runs). Frontier positions transfer to real decisions
   only insofar as these small functions resemble them.
2. **Single-run rows.** Empty counts and bare-word counts vary run
   to run (observed in prior runs); a rerun would shift null rates
   and therefore every cost figure. The dominance pattern (all
   disagreements fast-right) held across three populations, but the
   exact fractions would move.
3. **Floor band width.** The floor point (0.010) carries a Wilson
   band (0.0018, 0.0545) — a 30× span. Any comparison closer than
   that span (e.g. lean 0.0114 vs escalate-all 0.0100 on ns2) is
   inside floor uncertainty and must not be read as a real
   difference. The dominance claims that survive the band are the
   ones with zero observed gain at large cost gaps (lean vs full),
   not the 0.0014-scale ones.
4. **Floor model conservatism.** Counting a failed escalated item
   as a full error overstates the cost when the failure mode is
   both-pass ambiguity with an arbitrary tie-break (expected error
   0.5, not 1.0, on such items). The reported floor bands are
   therefore upper-leaning; the true floor contribution is ≤ what
   is shown. This strengthens, not weakens, the lean-vs-full
   dominance (full's extra floor exposure is, if anything,
   overstated) and weakens escalate-all's point advantage on ns2
   further (its gain assumes full error on failure).
5. **Realized rates, not population estimates.** Error figures are
   exact on these 280 rows. They are not confidence intervals for
   future rows — in particular, a realized 0.0000 perfect error
   (lean/full on fast+hammer populations) is not a claim that the
   true rate is 0; the floor band is the honest uncertainty, and
   the ns2 confident error shows the true rate is not 0 in general.
6. **No hammer on ns2.** Full rule and disagreement insurance are
   unpriced on the population that actually contains a confident
   fast error. The insurance break-even (r = 0.01) is computed on
   fast+hammer populations where r = 0/41; applying it to ns2-like
   items assumes the disagreement channel behaves the same there —
   untested.
7. **Cost is runs, not time or money.** Calculator runs are treated
   as unit cost. If calculator runs differ in cost by item (longer
   suites, slower tests), the frontier in runs is not the frontier
   in seconds — duration exclusion (§6) means this sweep cannot
   price that.

## 8. Files

- This summary: `jev-frontier-summary.md`
- Machine-readable data (per population, per policy, both sweeps,
  insurance, ns2 cases): `jev-frontier-data.json`
- Flat table (same content, CSV): `jev-frontier-data.csv`
- Sweep script (recomputes everything from the four decision logs):
  `jev-frontier-sweep.py`
- mrfloppy mirrors: `~/jev-test/frontier/` (all four files)

## 9. Scope

Item 4 ONLY. Item 5 (hammer recalibration) was NOT started. Item 3
(lag) was not re-run. No seat calls were made for this job.
