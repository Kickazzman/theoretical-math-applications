# JEV program item 1: calculator failure floor — summary

**Question.** Escalation to the calculator gives full reachability only
if the calculator never fails. Reachability = 1 − P(calculator fails).
This job measures that floor on a held-out set.

**Headline: P(calculator fails) = 1/100 = 0.010, Wilson 95% (0.0018, 0.0545).**
**Implied reachability = 0.990. Error floor for any escalation policy
using this calculator on this item distribution = 0.010 (point
estimate), plausibly up to ~0.055 (Wilson upper bound).**

The floor is not zero, and it is not large. One item in a hundred
defeats the calculator — and the failure mode matters more than the
rate (see §3).

## 1. Method (circularity guard held)

- **Held-out set:** 100 decision problems in the JEV (a)/(b) style,
  built from 25 FRESH functions, none reused from the original JEV
  items, the hard items, or the lag items: second_largest, count_words,
  is_anagram, fibonacci_n, reverse_words, discount_price, is_prime,
  sum_of_digits, longest_common_prefix, rotate_left, merge_dicts_sum,
  unique_sorted, word_frequency, is_valid_isbn10, base36_to_int,
  pascal_row, mode_smallest, collapse_whitespace, running_total,
  primes_below, hex_to_rgb, letter_grade, dot_product,
  transpose_matrix, initials.
- **Ground truth from CONSTRUCTION, never from the calculator.** The
  correct variant is the reference implementation; buggy variants are
  injected mutations (two per function). The calculator's job is only
  to run the test suites; its failure is measured against the
  construction labels. The calculator never grades its own homework.
- **Items:** 50 (a) patch-correct + 50 (b) which-is-better. (a) per
  function: A1 old=correct/new=buggy_a (tests must FAIL), A2
  old=buggy_b/new=correct (tests must PASS). (b) per function: correct
  vs buggy_a, correct vs buggy_b, correct position randomized with
  `random.Random(12345)`. (b) success requires correct passes ALL
  tests AND buggy fails ≥1 — the only case where the tests separate
  the pair.
- **Calculator failure = either direction:** correct variant fails any
  test, OR a buggy variant passes all tests. Per-item records carry
  the item id, variant, and failing/passing test details.
- **Calculator:** local Python test execution (exec each variant's code
  string, call on test inputs, == comparison with float tolerance and
  tuple→list normalization, raise-type matching). CPU-only; no seats,
  no router, no GPU, no browser, no frank. Run on mrfloppy for
  materials/tools consistency.
- **Wilson intervals:** standard Wilson, z = 1.96, same as prior runs.

## 2. Results

| Slice | Failed / n | P(fail) | Wilson 95% |
|---|---|---|---|
| All items | 1 / 100 | 0.010 | (0.0018, 0.0545) |
| (a) patch-correct | 0 / 50 | 0.000 | (0.000, 0.0714) |
| (b) which-is-better | 1 / 50 | 0.020 | (0.0035, 0.1050) |

**By direction (one primary per failed item):**

| Direction | Count |
|---|---|
| buggy-passes (ambiguous: both pass) | 1 |
| correct-fails | 0 |
| both-fail | 0 |
| correct-fails (wrong pick) | 0 |

**Marginals:** items where the correct variant failed = 0; items where
a buggy variant passed = 1. No item had both directions apply.

**By function:** 24 of 25 functions clean; base36_to_int 1 failure
(see §3). The (a) items are 50/50 clean.

## 3. The single failure, dissected

**cf-b30** — (b) item, function base36_to_int, correct at position A,
other variant = buggy_b.

- buggy_b's mutation: strip whitespace before validating/parsing, so
  it ACCEPTS inputs like `" 10"` that the correct implementation
  rejects with ValueError.
- Measurement outcome: correct passes all 12 tests, buggy_b passes
  all 12 tests. Both failed-test lists are empty.
- Mechanism (verified from the item file, not inferred): the test
  suite contains NO leading/trailing-whitespace test. Its whitespace
  tests are `"1 0"` (inner space — both impls reject it) and `""`.
  The distinguishing input `" 10"` exists only in the QA probes list,
  and probes are not part of the calculator's suite.
- **This is a test-coverage gap, not a wrong test.** No test is wrong;
  the correct variant passes everything; the suite simply never
  exercises the mutated behavior. The calculator's verdict ("both
  pass") is accurate given the suite — and useless for the decision.

**What this means for JEV:** the observed failure mode is AMBIGUITY,
not false endorsement. The calculator never passed a wrong variant
while failing the right one in this run (correct-fails = 0). On a (b)
item like cf-b30, the calculator returns "both pass" and the decider
gets no separation — that needs a tie-break or further-escalation
rule beyond the tests, and it is a real error source: a policy that
picks arbitrarily on "both pass" is wrong half the time on such items.
The floor measured here is a coverage floor (suites miss behaviors),
and coverage is the thing to improve, not verdict logic.

## 4. QA log (before measurement, no separation outcomes touched)

1. **Reference-vs-tests:** all 25 references pass their own
   spec-derived test suites on the first pass — 0 mismatches, 0
   adjudications needed.
2. **Mutation differential:** all 50 mutations behavior-changing on
   at least one test/probe input — 0 no-ops in the final set.
3. **Independent oracle cross-check:** every reference compared
   against a second implementation (stdlib, a different algorithm, or
   a lookup table) on edge + random inputs — clean. This guards
   against a correlated author error (same mistake in reference and
   test expectations). Oracle values spot-verified by scratch
   computation before authoring (base36, ISBN-10 checksums, discount
   roundings, Pascal row 5, Fibonacci 0–15).
4. **Rejected mutation (authoring):** reversed-weights ISBN-10 was
   rejected during authoring because reversed weights give identical
   validity judgments for all inputs (sum((11−w)·d) ≡ −sum(w·d) mod
   11) — a no-op mutation, not a buggy variant. Replaced by the
   checksum-%10 mutation.
5. **No pre-filtering on separation outcomes.** The held-out set was
   NOT filtered by whether items separate — that would bias P(fail)
   toward 0. The measurement reports the single pass found, including
   this failure.
6. After QA was clean, the measurement ran ONCE with no further edits
   to materials. (The measure script imports the build script's runner
   only; it does not modify items.)

## 5. Interpretation and caveats

- **Reachability is 0.99, not 1, on this distribution.** A JEV policy
  that escalates to this calculator cannot beat a ~1% error floor
  (point estimate; up to ~5.5% at the Wilson upper bound) on problems
  of this class with test suites of this strength — no matter how
  good the decider is. The uncontrollable set is real but small.
- **The floor is a property of the suites, not just the idea.** These
  suites were authored alongside the references by one author; a
  different author writes stronger or weaker suites. The 1% is a
  measurement of this calculator on this distribution, not a universal
  constant. What generalizes is the failure mode: coverage gaps that
  produce "both pass" ambiguity.
- **Constructed materials, not real work.** Same caveat as the JEV
  runs: functions are small and spec-clean; real-world patches have
  messier specs and harder-to-write suites, which would plausibly
  raise the floor, not lower it.
- **n = 100, so the interval is wide.** 1/100 is consistent with a
  true rate anywhere from ~0.2% to ~5.5%. The (a) 0/50 bound (up to
  ~7.1%) is not proof of a zero (a) floor either — it is an upper
  bound on an unmeasured small rate.
- **Scope:** this floor is for the (a)/(b) decision problems with
  test-suite calculators. It says nothing about (c) safe-to-merge
  (different question) or about calculators that are not test suites.

## 6. Run log

- Build + QA + oracle check run locally, then on mrfloppy (both
  clean). Items built on mrfloppy after clean QA.
- One operational hiccup, owned: a combined scp + tssh command hung
  at connection setup (~6 min, zero output) and was killed; the
  subsequent separate scp and tssh steps each completed in ~1–2 s,
  and the measurement ran cleanly. No data was affected; the hang
  was in transport, not in the job.
- Measurement run on mrfloppy: single pass, 100 records, 0 errors.

## 7. Files

- Local: `~/workspace/jev-calculator-floor-build.py` (materials +
  runner + QA + builder), `~/workspace/jev-calculator-floor-oracle-check.py`
  (independent oracle QA), `~/workspace/jev-calculator-floor-measure.py`
  (measurement), `~/workspace/jev-calculator-floor-items.json` (100
  items), `~/workspace/jev-calculator-floor-records.json` (per-item
  separation records), `~/workspace/jev-calculator-floor-aggregate.json`
  (aggregates), `~/workspace/jev-calculator-floor-summary.md` (this file).
- mrfloppy: `~/jev-test/calculator-floor/` (same files; the
  measurement ran there).

## 8. Scope

Item 1 ONLY. Items 2 (null at scale), 4 (frontier), and 5
(recalibration) are separate later jobs and were not started. Item 3
(lag) was already complete (negative) and was not re-run.
