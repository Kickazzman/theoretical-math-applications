# JEV Lag Run — Summary (100 problems, fast + hammer, 2026-10-29)

**Headline: the run is complete (100/100 rows, 0 GT mismatches), and the
lag-detector answer on this pair is NO SIGNAL — but for a mechanistic
reason that matters: hammer's latency is degenerate (≈0.07s on every
call), so the "lag" has no variance on the hammer side, and fast's own
duration does not separate change from no-change either (medians 9.62s
vs 9.81s). The both-wrong slice is 0 everywhere, as the brief predicted
it might be — on this pair that proves the pair can't measure the
slice, not that the slice doesn't exist (fast was never wrong when it
answered, 0/72).**

## 1. Protocol (same contract as the valid JEV runs)

- Seats: quicklook :8203 (fast) + hammer :8201, DIRECT ports only
  (never the router), sequential, one call at a time. Strict JSON
  (typed decision + confidence 0–1, no prose), temp 0, 4096-token
  budget, 1 retry on unparseable output, same parser as
  `jev-run-hard.py`. No seat pauses, no frank, no browser.
- Materials: 100 items, 50 (a) + 50 (b), unique problem IDs —
  40 original JEV (a)+(b) + 40 hard JEV (a)+(b) + 20 NEW items from 5
  fresh functions (ordinal_suffix, roman_to_int, flatten_once,
  caesar_shift, parse_time_hms), each test-gate-verified (correct
  passes all tests, buggy fails ≥1 targeted test). No (c) items, no
  repeats. Items file is self-contained (prompts + tests embedded).
- Ground truth: the CALCULATOR (local Python tests) per item —
  (a) tests on new_code, (b) embedded tests on both impls. Never a
  seat's answer. Local GT pre-check before the seat run: 0
  mismatches; run-time GT mismatches: 0; no error/ambiguous GT.
- Timing (the point of the run): per problem per seat, answer,
  confidence, t_start/t_end (wall-clock + monotonic), duration,
  attempt count. t_start = first attempt's start, t_end = last
  attempt's end (total seat latency including any retry).
  Per-problem checkpointing with resume (an interrupted run loses
  nothing); the full run resumed from the 2-row smoke test.
- Sequential-call warning (applies to every gap number below):
  fast runs first, then hammer, with inter-call gap 0.00s. So the
  end-time gap (≈ hammer's own duration) is NOT a parallel latency
  gap. The interpretable lag is the duration difference
  (hammer_duration − fast_duration). Both are reported; the end gap
  is never presented alone as if the seats ran in parallel.

## 2. Headline rates

| metric | value |
|---|---|
| Problems | 100 (50 a, 50 b; orig 40, hard 40, new 20) |
| P(change), overall (None counts as a value) | 64/100 = 0.640, Wilson (0.563, 0.755) |
| P(change), among both-answered | 22/51 = 0.431, Wilson (0.328, 0.610) |
| Both-answered | 51/100 |
| Fast empty (null) | 28/100 = 0.280 |
| Hammer unparseable (contract fail) | 28/100 = 0.280 (all bare-word, 0 empty) |
| Fast alone | 72/100 = 0.720, Wilson (0.649, 0.829) |
| Fast when answered | 72/72 = 1.000 (wrong-when-answered: 0) |
| Hammer alone | 41/100 = 0.410; when answered 41/72 = 0.569 |
| Agreement (both answered, same) | 29/51 = 0.569 |
| Disagreements fast-right / hammer-wrong | 22/22 |

How the 64 overall changes decompose: fast-null rows contribute 21
(28 fast-nulls minus 7 both-null rows, where None == None is not a
change); fast-answered rows contribute 43 (21 hammer-null + 22
disagreements). Both-null rows: 7. Check: 100 − 28 − 28 + 7 = 51
both-answered.

Disagreement pattern extends: original 13/13 + hard 6/6 + this run
22/22 = 41/41 disagreements fast-right / hammer-wrong across three
populations (this run's 22 include 4 on the NEW items — the pattern
holds on unseen items too).

## 3. Latency: the gap has no hammer-side variance

| quantity (s) | median | mean | min | max |
|---|---|---|---|---|
| fast duration | 13.85 | 19.47 | 2.03 | 37.95 |
| fast duration, answered | 9.96 | 12.68 | — | — |
| fast duration, empty | 36.95 | 36.93 | — | — |
| hammer duration | 0.07 | 0.08 | 0.05 | 0.12 |
| duration gap (hammer − fast) | −13.76 | −19.40 | −37.86 | −1.97 |
| end gap (hammer end − fast end) | 0.07 | 0.08 | 0.05 | 0.12 |
| inter-call gap | 0.00 | 0.00 | 0.00 | 0.00 |

- Hammer durations >1s: 0/100. Hammer is always faster — the
  duration gap is negative on all 100 rows. The gap is, to within
  0.07s, just −(fast duration): hammer blurts a few tokens in
  ~0.07s whether it is right, wrong, or bare-word.
- Fast empties take ~37s (two attempts of thinking burn); answered
  fast calls take ~10s median. Silence is expensive, answers are
  not.
- Mechanistic read: the lag-as-convergence-detector idea assumed
  two deliberating seats whose latency difference tracks belief
  movement. Here only one seat deliberates. τ cannot carry signal
  from the hammer side because hammer's latency is a constant.

## 4. P(change | gap): no separation

Duration-gap tertiles, both-answered only (n = 51):

| tertile | gap range (s) | n | P(change) |
|---|---|---|---|
| low third | [−36.5, −13.1] | 17 | 9/17 = 0.529 |
| mid third | [−12.8, −7.2] | 17 | 5/17 = 0.294 |
| high third | [−6.8, −2.0] | 17 | 8/17 = 0.471 |

Fast-duration tertiles (same rows, inverted — the gap is
−fast_duration up to 0.07s): 0.471 / 0.294 / 0.529. Same
non-monotone shape, as expected.

Median duration gap: change −9.53s (n = 22) vs no-change −9.74s
(n = 29). Median fast duration: change 9.62s vs no-change 9.81s.
**The gap does not predict change on this pair.** The tertile
rates are non-monotone and, at n = 17 per bin, within noise — but
the near-identical medians are the cleaner statement: there is no
separation to find, not just too little data to see it. Caveat
that travels with this: n = 51 both-answered is small, and a
larger run could in principle find a small effect; what this run
rules out is a LARGE lag signal of the kind the proposal hoped
for (a 3%-style rare, sharp trigger would have shown up as
separation, not as 0.53/0.29/0.47).

## 5. Both-wrong slices: all zero (limitation, stated plainly)

Both-wrong = fast wrong AND hammer wrong on the same item, both
answered. Fast was never wrong when answered (0/72), so every
both-wrong rate below is 0 by construction of this pair — **this
does NOT prove the slice doesn't exist; it proves this pair can't
measure it.** The slice needs a pair where both seats err.

| slice | value | Wilson 95% |
|---|---|---|
| P(both wrong \| agree & fast conf = 1.0, high) | 0/19 = 0.000 | (0.000, 0.202) |
| P(both wrong \| agree & fast conf < 1.0, low) | 0/10 = 0.000 | (0.000, 0.384) |
| Both-wrong by exact fast conf, both-answered: 0.95 | 0/17 | — |
| Both-wrong by exact fast conf, both-answered: 0.99 | 0/2 | — |
| Both-wrong by exact fast conf, both-answered: 1.0 | 0/32 | — |
| Both-wrong among agree rows | 0/29 | — |

The Wilson bounds matter: even the "0" in the high-confidence
bucket is consistent with a true rate up to ~20% at this n, and up
to ~38% in the low bucket (n = 10). The low-confidence-agreement
slice — the proposal's hidden slice — is unmeasured here, not
measured-zero.

Confidence distributions (answered only): fast 1.0 ×49, 0.95 ×21,
0.99 ×2 (no confidences below 0.95, as in both JEV populations);
hammer 1.0 ×72 (constant 1.0 whenever it expresses one — zero
information, as previously recorded).

## 6. By source and type

| subset | n | fast empty | hammer unparseable | change (all) | change (both-answered) | fast-alone |
|---|---|---|---|---|---|---|
| orig | 40 | 5 | 8 | 24/40 | 13/28 | 35/40 = 0.875 |
| hard | 40 | 15 | 16 | 28/40 | 5/13 | 25/40 = 0.625 |
| new | 20 | 8 | 4 | 12/20 | 4/10 | 12/20 = 0.600 |
| (a) | 50 | 15 | — | 36/50 | 7/14 | — |
| (b) | 50 | 13 | — | 28/50 | 15/37 | — |

Reuse-consistency check: the reused items reproduce the original
runs' fast-alone rates EXACTLY (orig 35/40 = 0.875, hard 25/40 =
0.625) — same items, same contract, same fast seat. (Individual
rows vary run to run with nondeterminism, but the rates replicate.)
New items behave hard-like (fast-alone 0.600, empty rate 0.400).

Note the (a)/(b) asymmetry: (b) items have far more both-answered
rows (37 vs 14) and more disagreements (15 vs 7) — hammer's (b)
A-bias meets fast-right B answers, as in the hard run.

## 7. Contract-flag bug found in this run's runner, owned and fixed

The lag runner's `ask_timed` kept the FIRST attempt's `ok` flag
after a successful retry (unlike `jev-run-hard.py`'s `ask`, which
returns True on retry success). Effect: 11 rows (10 fast, 1
hammer) where the seat answered via retry were misflagged as
contract failures. Decisions, confidences, timings, and all
change/both-wrong flags were UNAFFECTED (they come from the
successful parse); only the `contract_ok` flag was wrong
(reported 38/29, true 28/28). Fix applied: `contract_ok` recomputed
as (decision is not None) — exactly equivalent to the parser's
`ok` definition — in both the local and mrfloppy decisions files,
and the runner script fixed (`ok = True` on retry success).
Rates in this summary use the corrected flags. The runner as
delivered contains the fix.

## 8. Limitations (everything that weakens the lag verdict)

1. **Sequential calls.** The end gap is hammer's own duration, not
   a parallel lag. The duration gap is the interpretable lag, and
   it is degenerate on the hammer side (see §3). A parallel-start
   design would be needed to test a true latency race — but on
   this pair it would not help, since hammer's latency barely
   varies at all.
2. **Small both-answered n (51).** Tertile bins are n = 17; small
   lag effects are unexcluded. Large lag effects are excluded by
   the identical medians (§4).
3. **Fast never wrong when answered.** The both-wrong slice is
   unmeasurable on this pair (§5). The proposal's key slice needs
   an erring pair (the 58/58 pair or another pair where both seats
   err), not a rerun of this pair.
4. **Single run, temp 0, nondeterminism observed** (as in both JEV
   runs: empty counts and bare-word counts vary run to run).
5. **Materials constructed, not saved real work** (same caveat as
   the JEV runs; new items are hand-authored in the same style).
6. **This run ONLY.** It does not test a third seat, the 58/58
   pair, or any other pair — those are separate jobs.

## 9. What this run DOES settle

- P(change) on the JEV pair at n = 100: 0.640 overall,
  0.431 among both-answered — NOT 0.03. The disagreement trigger
  fires often, not rarely, so escalation budget (not rarity) is
  the binding constraint on this pair.
- P(change | gap): no signal on this pair, mechanistically
  explained by hammer's constant ~0.07s latency.
- The both-wrong slice: unmeasured here (0 everywhere with wide
  bounds), not refuted. The next run that wants it needs an
  erring pair.

## 10. Files

- Decision log (100 rows, corrected flags): `jev-lag-decisions.json`
  (local + mrfloppy `~/jev-test/lag-run/jev-lag-decisions.json`)
- Runner (fixed): `jev-lag-run.py` (local + mrfloppy
  `~/jev-test/lag-run/jev-lag-run.py`)
- Items (100, self-contained): `jev-lag-items.json`
- New-items builder + verifier: `jev-lag-new-materials.py`
- Merge + GT pre-check: `jev-lag-merge.py`
- On mrfloppy `~/jev-test/lag-run/`: items, runner, decisions
  JSON + JSONL checkpoint, run log, done marker, launch + waiter
  scripts.
