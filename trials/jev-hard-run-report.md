# JEV Contract Test — HARDER Materials Run (2026-10-29)

**Headline: the harder set tripled the silence rate and left everything
else the same shape.** Fast-alone fell 87.5% → 62.5%, entirely from
non-answers (empties 5 → 15); fast-when-answered stayed perfect
(35/35 → 25/25). The correction path is STILL untested — fast was
never wrong when it answered, on either population. Calibration below
0.95 is STILL unmeasured — quicklook expressed zero confidences below
0.95, and the 0.8 rule STILL never fired. The leaner escalation rule
(full minus disagreement) again reaches identical final accuracy at
lower cost (37.5% vs 52.5% escalation).

**Framing (binding): the original +1 PASS stands for its (easier)
population. This run characterizes the HARDER population separately.
No kill verdict is issued for this population** — the kill rule is
not re-applied here, and nothing in this run overturns the original
+1. Descriptively, the hard top bucket (100%, Wilson lower 0.867)
and improvement (+37.5pp) sit above the original bars, but the bars
were set for the original population, and the per-type lower bounds
sit below 0.85 (as they did originally).

## 1. What was tested

Same CONTRACT as the original run (report: jev-contract-test-report.md
§1), on the 40 verified harder materials (jev-hard-materials.md):
20 (a) patch-correct + 20 (b) pick-better, no (c) items. Fast seats
quicklook :8203 (primary) + hammer :8201 (second opinion), called
DIRECTLY on their ports, never the router, sequentially, one call at
a time. Strict JSON (typed decision + confidence 0–1, no prose),
temp 0, 4096-token budget, 1 retry on unparseable output, same
parser as the original. Slow side = the CALCULATOR (local Python
tests) for (a) and (b). No seat pauses, no frank, no browser, no
modifying the original or harder materials. Prompts carry the spec
AS WRITTEN in the items file — nothing from the manifest's
test-encoded readings (stable, larger-amount-first,
leading-zeros-rejected, mean-of-middles) was put into any prompt.

Ground-truth integrity: calculator agreed with item expectations on
all 40 items (gt_mismatches = []). No generation re-run was needed.
Materials untouched (verified by mtime: original jev-items.json
Oct 29 10:02, verify-report.json 10:00; materials-hard files
Oct 29 12:22–12:24; only new files are this run's artifacts).

## 2. Per-bucket tables (quicklook confidence → actual success)

Wilson 95% intervals. Buckets below 0.9 are EMPTY again: quicklook
never expressed confidence below 0.95 on these items either
(13× 1.0, 11× 0.95, 1× 0.99, 15 null). The calibration curve is
still a single point.

### Combined (a)+(b), n = 40

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.5–0.6 | 0 | 0 | — | — |
| 0.6–0.7 | 0 | 0 | — | — |
| 0.7–0.8 | 0 | 0 | — | — |
| 0.8–0.9 | 0 | 0 | — | — |
| **0.9–1.0** | **25** | **25** | **1.000** | **(0.867, 1.0)** |
| <0.5 | 0 | 0 | — | — |

15 items unbucketed: quicklook EMPTY (contract failure, counts
against fast-alone accuracy, excluded from buckets).

### (a) alone, n = 20

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.9–1.0 | 12 | 12 | 1.000 | (0.757, 1.0) |
| all lower buckets | 0 | 0 | — | — |

Fast-alone (a): 12/20 = 0.600 (8 empties).

### (b) alone, n = 20

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.9–1.0 | 13 | 13 | 1.000 | (0.772, 1.0) |
| all lower buckets | 0 | 0 | — | — |

Fast-alone (b): 13/20 = 0.650 (7 empties).

Per-type top-bucket point estimates are 100%, but their Wilson
lower bounds (0.757, 0.772) sit below 0.85 at k = 12–13 — the same
pattern as the original run. The combined k = 25 is what lifts the
lower bound past the bar, and only narrowly (0.867 vs 0.85).

## 3. Calibration verdict

- **Top bucket ≥ 85%: YES descriptively** (combined 100%, Wilson
  lower 0.867 — margin 0.017, narrow).
- **Monotone: UNTESTED, not confirmed.** The check passes vacuously
  (one non-empty bucket), as in the original run. There are no lower
  buckets to compare against.
- **Confidence range STILL unused.** Zero confidences below 0.95 in
  25 answers; zero below 0.8; the 0.8 rule fired zero times. Whether
  that is justified confidence (right 25/25 when it answered) or
  overconfidence that would fail on still-harder items is untestable
  on this set too — and the fact that harder items produced silence
  rather than low confidence suggests the seat answers 0.95–1.0 or
  not at all, rather than calibrating downward.
- **Recommended threshold: none identified — keep 0.8.** At every
  threshold 0.5–0.9 the pooled set is the same 25 items at 100%,
  confidence-only escalation 37.5% (the 15 nulls). The curve is flat
  because confidences never vary below 0.95.

## 4. Escalation: full rule vs leaner rule

| metric | full (null OR <0.8 OR disagreement) | leaner (null OR <0.8) |
|---|---|---|
| Fast-alone (quicklook) | 25/40 = 0.625 | 25/40 = 0.625 |
| Hammer standalone | 13/40 = 0.325 | 13/40 = 0.325 |
| Final accuracy | 40/40 = 1.000 | 40/40 = 1.000 |
| **Improvement** | **+37.5pp** | **+37.5pp** |
| Escalation rate | 21/40 = 0.525 | 15/40 = 0.375 |
| Fast accuracy on escalated subset | 6/21 = 0.286 | 0/15 = 0.000 |
| Agreement (quicklook vs hammer) | 8/40 = 0.200 | 8/40 = 0.200 |

Escalation anatomy, full rule (21 = 15 null-fast + 0
confidence-triggered + 6 disagreement). The 0.8 rule NEVER fired.
Leaner rule (15 = 15 null-fast + 0 confidence-triggered).

The leaner rule achieves the IDENTICAL 100% final accuracy at
37.5% escalation instead of 52.5% — saving 6 calculator runs (the
disagreements). The disagreement rule again bought verification,
not accuracy: all 6 disagreements were fast-right / hammer-wrong
(a03, b01, b04, b05, b10, b17), and escalating them changed none
of them. (Original run: same pattern, 13/13 fast-right, leaner
12.5% vs full 45%.)

Cross-tab (a)+(b), fast × hammer:

| | hammer null (bare) | hammer right | hammer wrong |
|---|---|---|---|
| **fast null** | 4 | 5 | 6 |
| **fast right** | 11 | 8 | 6 |
| **fast wrong** | 0 | 0 | 0 |

## 5. Correction path: STILL UNTESTED

- **Fast wrong-when-answered: 0/25.** Every fast-alone error is a
  non-answer (empty), not a wrong decision — on both populations
  now (original 0/35, hard 0/25, combined 0/60).
- Correction ids under BOTH rules: EMPTY. Corrected-by-neither
  ids: EMPTY — there are no wrong confident answers to strand,
  because none exist.
- What escalation actually did here: fallback for silences
  (15 items) + verification of correct answers (6 items). The
  duplex's core claim — the slow thinker corrects fast errors —
  has now survived two populations without ever being exercised.
- What the harder set DID change: the fallback load. Empties
  12% → 37.5%. The fallback path is now load-bearing, not
  incidental: over a third of harder items need the calculator
  just to get an answer.

## 6. Harder population vs original population

| metric | original (easier) | hard |
|---|---|---|
| Fast-alone (quicklook) | 35/40 = 0.875 | 25/40 = 0.625 |
| Fast-when-answered | 35/35 = 1.000 | 25/25 = 1.000 |
| Fast empties | 5/40 = 0.125 | 15/40 = 0.375 |
| Hammer standalone | 19/40 = 0.475 | 13/40 = 0.325 |
| Agreement | 15/40 = 0.375 | 8/40 = 0.200 |
| Top bucket (combined) | 35/35, Wilson (0.901, 1.0) | 25/25, Wilson (0.867, 1.0) |
| Escalation, full → lean | 45% → 12.5% | 52.5% → 37.5% |
| Improvement, both rules | +12.5pp | +37.5pp |
| Confidence < 0.95 expressed | 0 | 0 |
| Confidence-triggered escalations | 0 | 0 |
| Fast wrong-when-answered | 0 | 0 |

Reading: the harder set moved fast-alone DOWN (more silence) while
fast-when-answered stayed perfect — so the +37.5pp improvement is
a FALLBACK-coverage number, not a decision-quality number. It is
large because the ceiling was large (fast-alone 62.5% leaves
37.5pp of headroom, all of it nulls). The original run's ceiling
confound ran the other way (small headroom, bar consumed 80% of
it). Neither improvement figure measures correction, because
correction never happened in either run.

## 7. Fast-seat contract behavior

- **Quicklook (primary): clean JSON when it answers (prose 0.0,
  think 0.0), but intermittent EMPTY responses: 15/40 (37.5%).**
  A null row means BOTH attempts failed to parse (1 retry, as in
  the original) — these are double silences, not single-call
  glitches. Bare words 0.0: quicklook's failures are pure empties,
  never malformed JSON. Emptiness concentrates by function:
  weighted_quantile 4/4 empty (the 34-line function, longest),
  levenshtein 3/4, allocate_budget / merge_sorted_lists /
  sliding_window_max 2/4 each, interpolate_missing /
  parse_duration 1/4, exponential_moving_average / moving_median /
  validate_ipv4_cidr 0/4. Silence tracks function complexity /
  length, not item type ((a) 8 empties, (b) 7).
- **Hammer (second opinion): worse decider, constant priors.**
  Standalone 13/40 = 0.325 (parseable 25, bare 15). Prose 100%
  (every parseable response ```-fenced, as in the original).
  (a): said 'pass' on all 20 items — 15 bare 'pass' (7 leaning
  right on pass items, 8 leaning wrong on fail items) + 5
  parseable 'pass' (3 right, 2 wrong). Its (a) standalone 3/20
  counts only the parseable ones; its LEANING was constant
  'pass', exactly as in the original run. (b): near-constant 'A'
  — 19 A-picks + 1 B-pick (b16, correct). Ground truth (b) is
  A×9 / B×11, so the A-bias yields 9 + 1 = 10/20. Every (b)
  disagreement is hammer's A-bias meeting a B-correct item where
  fast was right (b01, b04, b05, b10, b17). As a second opinion
  it adds cost, not accuracy, on this sample too — and its
  disagreements carry no independent signal (they are the bias,
  not a judgment).

## 8. Ambiguous (b) items (8)

Fast answered 6/6 correct (b04, b15, b17, b18, b19, b20); empty on
2 (b03, b16), both resolved correct by escalation fallback.
Hammer on ambiguous: 5/8 (both merge items wrong, both
moving_median right, validate split, allocate split).

Caveat that travels with the 6/6: the clean-ambiguity subset is
smaller than 8. The merge (b03, b04) and allocate (b15, b16)
specs leave the ambiguity genuinely open (answered 2/2: b04, b15
correct; b03, b16 empty). But the moving_median spec's own
window-2 worked examples ([2.0, 2.5, 3.5, 4.5]) arithmetically
imply mean-of-middles, and the validate spec's test list puts
'01.2.3.4/24' among the raise cases — both partially constrain
ambiguities their notes claim to leave open. So b17/b18/b19/b20
results show fast can read worked examples AND/OR infer the
standard reading; this set cannot distinguish those two. The
manifest's test-encoded readings were NOT in any prompt — this
constraint comes from the items' own spec text, used as-is, and
is reported here as a materials observation, not a prompt leak.

## 9. Limitations (everything that weakens the characterization)

1. **Single run, temp 0, nondeterminism observed.** Empty counts
   vary run to run (original run: quicklook empties varied across
   runs 1–3 and within run 3's population). A rerun could shift
   the 15-empty count and the 37.5pp improvement; the 25/25
   top-bucket Wilson lower bound (0.867) sits only 0.017 above
   the 0.85 bar — one wrong top-bucket answer, or a few fewer
   answered items, would drop it below.
2. **Materials constructed, not saved real work** (same caveat as
   the original run, now with larger functions). Calibration
   transfers to real decisions only insofar as these functions
   resemble them.
3. **Correction still unproven after two populations.** To test it
   needs items where fast actually errs when answering — still
   harder items, adversarial items targeting fast's failure modes,
   or a weaker fast seat — or an investigation of whether the
   contract itself (JSON-only + temp 0) suppresses low confidence
   and wrong answers alike, pushing the seat to 0.95–1.0 or
   silence instead of a calibrated range.
4. **Hammer's disagreements are bias, not signal.** On this set
   the disagreement rule's escalations are all hammer's A-bias /
   constant-'pass' meeting fast-right answers. Disagreement as an
   escalation trigger assumes a second opinion with independent
   judgment; hammer does not provide one here.
5. **(b) hidden tests = authored tests** (same as the original).
   The fast seats never see them; the calculator runs them.
6. **Direct port calls, not via router** (per the brief).
   Decisions are unaffected by contention; only latency is.

## 10. What this means for the build (framing, not a verdict change)

- The decider's demonstrated value remains fallback +
  verification — but on harder items the fallback load is 37.5%,
  so the build must price the calculator path as a routine cost,
  not an exception.
- The leaner rule strengthens across both populations (identical
  final accuracy at lower escalation: original 12.5% vs 45%,
  hard 37.5% vs 52.5%). Whether disagreement-verification is
  worth its extra runs remains perg's design call.
- Two questions now block a calibration claim, and neither has
  data yet: (i) does the seat ever express <0.95 confidence, on
  any population? (ii) does escalation ever correct a wrong
  confident call? Both are 0-for-2 populations so far.
- The original +1 PASS is untouched by this run (different
  population, no kill verdict issued here).

## 11. Files

- Decision log (40 rows, original template + lean fields +
  bare-word flags + gt-mismatch flags): `jev-decisions-hard.json`
- Summary (buckets, full vs lean escalation, correction ids,
  confidence distribution, contract rates):
  `jev-summary-hard.json`
- Test items (used as-is): `jev-items-hard.json`
- On mrfloppy `~/jev-test/`: `jev-decisions-hard.json`,
  `jev-summary-hard.json`, `jev-run-hard.log`, `jev-run-hard.py`
- Scripts (local workspace): `jev-run-hard.py`,
  `jev-hard-waiter.sh`
