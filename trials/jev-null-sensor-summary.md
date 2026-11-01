# JEV Null-as-Sensor Run v2 — Summary (100 fresh problems, fast seat only, 2026-10-30)

**Headline: null IS a complexity sensor at scale — the hint is confirmed.**
Null rate rises monotonically with the pinned complexity tier
(0% → 8% → 34%), and Tier 3 is separated from Tier 1 at 95% Wilson.
A null answer enriches Tier 3 from its 32% base rate to 79% (lift
3.2×). The subtlety axis, measured separately, carries NO signal —
null tracks complexity, not mutation subtlety. This is the corrected
relaunch of item 2: the stopped run's ambiguous hardness definition
(subtlety vs complexity) is resolved in favor of complexity, and the
two axes are now dissociated in the data.

## 1. Protocol (what was pinned, and what was NOT reused)

- **Hardness PINNED before any seat runs: function complexity tiers
  defined by construction** (written into the items file first):
  - **Tier 1 — straight-line:** no loops, no comprehensions over
    collections, at most one simple conditional; a single data
    transformation (e.g. celsius_to_fahrenheit, is_even, tip_amount).
  - **Tier 2 — single-pass:** exactly one loop (or one
    comprehension/dict-build) over a collection with simple
    per-element state; no nested loops, no multi-phase logic
    (e.g. count_vowels, dedupe_keep_order, running_max).
  - **Tier 3 — multi-step/stateful:** nested loops, multiple
    passes, DP table, stack/state machine, graph traversal, or
    multi-constraint validation with interacting edge cases
    (e.g. longest_palindromic_substring, matrix_spiral_order,
    knapsack_01_small, lru_cache_simulate).
- **Materials: 100 FRESH items, 25 fresh functions × 4 items each**
  (per function: (a, buggy_a), (a, buggy_b), (b, A=correct/B=buggy_a),
  (b, A=buggy_b/B=correct)). No function reused from JEV original,
  hard, lag, or calculator-floor items, and NOTHING imported from
  the stopped item-2 run (its items/labels were contaminated by the
  ambiguous definition; this run built fresh). Every correct
  implementation passes all its tests; every buggy variant fails
  ≥1 test (calculator-verified during construction).
- **Subtlety recorded SEPARATELY, never blended:** per item, the
  number of tests the item's buggy variant fails (1 = subtle,
  >1 = obvious). Subtlety is NOT hardness in this run.
- **Seat: fast only, quicklook :8203, DIRECT port (never the
  router),** same strict-JSON contract, prompts, parser, and
  4096-token budget as the valid JEV runs, temp 0, 1 retry on
  unparseable output (retry success counts as ok — the lag-run
  contract-flag bug is not repeated). No seat pauses, no frank, no
  browser, no GPU beyond the resident. Hammer NOT run (hammer nulls
  are contract failures, a different channel).
- **Ground truth:** calculator (local Python tests) per item.
  GT mismatches: **[]** (0/100). Prompts carry no tier or subtlety
  labels — the seat cannot condition on them, so null rates by tier
  are a clean measurement.
- **Verification:** 100 records, unique ids, id set identical to
  the items file, record tier/subtlety labels identical to the
  items file. All rates below recomputed from the raw rows.

## 2. PRIMARY: null rate by complexity tier

Wilson 95% intervals (z = 1.96), recomputed from raw rows.

| tier | items | nulls | null rate | Wilson 95% |
|---|---|---|---|---|
| 1 (straight-line) | 32 | 0 | 0.000 | (0.000, 0.107) |
| 2 (single-pass) | 36 | 3 | 0.083 | (0.029, 0.218) |
| 3 (multi-step/stateful) | 32 | 11 | 0.344 | (0.204, 0.517) |
| all | 100 | 14 | 0.140 | (0.085, 0.222) |

Monotone: 0 → 0.083 → 0.344. **Tier 3 separates from Tier 1:**
Tier 1's Wilson upper bound (0.107) sits below Tier 3's lower bound
(0.204) — no overlap. Tier 2 vs Tier 3 overlap slightly (0.218 vs
0.204), and Tier 1 vs Tier 2 overlap, so the clean claim is the
Tier 3 vs Tier 1 separation plus the monotone ordering, not a
three-way pairwise separation at this n.

## 3. PRIMARY: P(Tier-3 | null) vs P(Tier-3 | no null)

| quantity | value | Wilson 95% |
|---|---|---|
| P(Tier 3 \| null) | 11/14 = 0.786 | (0.524, 0.924) |
| P(Tier 3 \| no null) | 21/86 = 0.244 | (0.166, 0.345) |
| base rate of Tier 3 in the set | 32/100 = 0.320 | — |
| **lift (ratio)** | **3.22×** | — |
| difference | +54.2 pp | — |

The two intervals do NOT overlap (0.524 > 0.345). A null answer
more than triples the odds the item is Tier 3: null enriches Tier 3
from 32% (base) to 79%. **Verdict: null is a real observability
channel for complexity at n = 100.** It is not a perfect sensor
(3/14 nulls are Tier 2; 21/32 Tier-3 items were answered), but the
lift is large and the separation is clean.

Null rate by type is balanced — (a) 7/50 = 0.140, (b) 7/50 = 0.140,
identical — so the tier effect is not a type confound.

## 4. Nulls by function: tier predicts, but functions vary

| tier | function | nulls/items |
|---|---|---|
| 3 | matrix_spiral_order | 3/4 |
| 3 | evaluate_rpn | 3/4 |
| 3 | longest_palindromic_substring | 2/4 |
| 3 | lru_cache_simulate | 2/4 |
| 3 | validate_sudoku_row | 1/4 |
| 2 | dedupe_keep_order | 1/4 |
| 2 | capitalize_words | 1/4 |
| 2 | strip_punctuation | 1/4 |
| 1 | all 8 Tier-1 functions | 0/4 each |
| 2 | count_vowels, sum_even_numbers, letter_frequency, group_by_first_letter, running_max, count_long_words | 0/4 each |
| 3 | coin_change_greedy, schedule_max_meetings, knapsack_01_small | 0/4 each |

Reading: the tier effect is real but noisy at the function level.
Three Tier-3 functions drew 0/4 nulls (coin_change_greedy,
schedule_max_meetings, knapsack_01_small — all DP/greedy forms the
seat handles well), while matrix_spiral_order and evaluate_rpn drew
3/4. Tier is a useful prior for the sensor, not a deterministic
trigger. The hard run's pattern replicates in kind: silence
concentrates on the hardest functions, not uniformly across the
tier.

## 5. SECONDARY: duration (lag side-signal replication, with caveat)

| quantity | median | mean |
|---|---|---|
| duration, answered (n = 86) | 4.53 s | 9.65 s |
| duration, null (n = 14) | 36.27 s | 36.31 s |

Null rate by duration tertile (all 100 rows, sorted by duration):
slowest tertile [16.33, 36.77] s: 14/34 = 0.412; middle tertile:
0/33; fastest tertile: 0/33. **All 14 nulls sit in the slowest
tertile.** Direction replicates the lag run (answered ~10 s vs
empty ~37 s there; answered faster here at 4.53 s median on this
item mix, nulls still ~36 s).

**Caveat that travels with this:** total duration is partly a
CONSEQUENCE of null, not a pre-decision predictor — null rows take
two attempts (the retry), so their durations include a second
thinking burn. 24 rows took 2 attempts (14 nulls + 10 answered via
retry). A true duration sensor would need FIRST-attempt latency,
which this runner did not log separately. Duration separates null
from answered post-hoc; it is not yet shown to PREDICT null
before the answer lands.

## 6. SECONDARY, kept separate: subtlety carries NO signal

| quantity | value | Wilson 95% |
|---|---|---|
| null rate, subtle items (1 failing test) | 3/18 = 0.167 | (0.058, 0.392) |
| null rate, obvious items (>1 failing test) | 11/82 = 0.134 | (0.077, 0.224) |
| P(subtle \| null) | 3/14 = 0.214 | (0.076, 0.476) |
| P(subtle \| no null) | 15/86 = 0.174 | (0.109, 0.268) |

Intervals overlap heavily on both framings. **Subtlety does not
predict null.** This is the dissociation the corrected design was
built to test: the stopped run's ambiguity is resolved — the
complexity axis carries the signal (Section 2–3), the subtlety axis
does not. A policy that escalates on null is escalating on
complexity, not on mutation subtlety.

## 7. Two firsts (not the primary result, but they change the gaps)

- **First wrong-when-answered in ANY JEV population.** ns2-a23
  (capitalize_words, Tier 2, subtle): fast said "pass" @ 1.0, GT
  fail (the buggy variant is `str.title()`, which turns "don't"
  into "Don'T" — the seat missed it). Duration 29.67 s, 2 attempts
  (answered via retry, still wrong, still confident). Previous
  populations: original 0/35, hard 0/25, lag 0/72 wrong-when-answered.
  This run: 1/86 (fast correct when answered 85/86). This is an
  existence proof that fast CAN err when answering — it does not
  test the correction path (this run has no escalation), but the
  "fast never errs" pattern is now broken, which is what a
  correction-path test needs as a precondition.
- **First sub-0.95 confidence ever.** ns2-a35
  (longest_palindromic_substring, Tier 3): fast expressed 0.9,
  decision fail, CORRECT. Previous populations: zero confidences
  below 0.95. So on a complexity-varied population the seat finally
  used a sub-0.95 value — and was right. n = 1: a hint that the
  calibration range can open on harder items, not a calibration
  curve.

Contract behavior was clean: prose 0, think 0, bare-word 0,
empty-flag = nulls = 14, contract_ok false = 14. Confidence
distribution (answered): 1.0 ×61, 0.95 ×23, 0.99 ×1, 0.9 ×1.

## 8. Limitations

1. **Constructed materials, not saved real work** (same caveat as
   all JEV runs). Tier labels are construction labels; real diffs
   do not come pre-tiered, so transfer needs a tiering rule for
   real code.
2. **Tier 3 functions vary 0/4–3/4.** The sensor is a tier-level
   prior with function-level noise, not a per-item detector.
3. **n = 100, nulls = 14.** The Tier 3 vs Tier 1 separation is
   clean, but Tier 2 vs Tier 3 is not separated at this n, and the
   P(Tier-3|null) interval is wide (0.524–0.924).
4. **Single run, temp 0, nondeterminism observed** in prior runs
   (empty counts vary run to run). A rerun could shift the 14-null
   count.
5. **Duration is post-hoc** (Section 5 caveat): total duration
   includes the retry, so it is not a pre-decision sensor as
   logged.
6. **This run ONLY.** No escalation, no frontier, no hammer
   recalibration — those are items 4 and 5, separate jobs. The
   wrong-when-answered row (ns2-a23) is not a correction-path
   measurement.

## 9. What this means for item 4 (framing, not a verdict)

Item 4 (cost-error frontier) now has a real sensor to sweep with:
escalation on null is escalation on complexity (lift 3.2×, not a
proxy for subtlety). The frontier question — whether the leaner
rule (null OR <0.8) sits on the Pareto frontier or is dominated —
can be tested with null as the complexity channel. The 0.9-confidence
row and the first wrong-when-answered row are also item-4-relevant:
a threshold sweep now has one sub-0.95 point and one confident
error to price, where previous populations had neither.

## 10. Files

- Items (100, with tiers + subtlety counts + tier definitions):
  `jev-null-sensor-items.json`
  (local + mrfloppy `~/jev-test/null-sensor-v2/jev-null-sensor-items.json`)
- Per-item records (100 rows): `jev-null-sensor-records.json`
  (+ `.jsonl` checkpoint; local + mrfloppy `~/jev-test/null-sensor-v2/`)
- Runner: `ns2-run.py` (local + mrfloppy `~/jev-test/null-sensor-v2/ns2-run.py`)
- Builder (fresh functions + test-gate verification): `ns2-build.py`
- Analysis (recomputed from raw rows): `ns2-analyze.py`
- Run log + done marker: mrfloppy `~/jev-test/null-sensor-v2/ns2-run.log`,
  `ns2-done`
