# JEV program item 5: hammer recalibration — summary (LAST program item)

**Headline: the fixed point does NOT move. Logprobs ARE available from
this server build, but no hammer-derived signal separates hammer-right
from hammer-wrong answers at 95% confidence — not expressed confidence
(constant 1.0), not token logprobs, not decision value, not length,
tokens, duration, or contract status. Recalibration from hammer's
outputs is unachievable on current evidence. The policy must treat
hammer confidence as uninformative (constant 1.0 = no signal), which
is the lean rule: escalate on null OR fast confidence < 0.8, never on
hammer. No repriced frontier is produced, because no candidate policy
changes any decision — repricing an unchanged policy would be
inventing a table. What WOULD be needed is stated in §5, not built:
that is beyond this item's scope. This item does NOT close the
program; it reports and stops.**

## 0. Method (saved rows + read-only probes, nothing else)

- Step 1: recomputed from SAVED rows only — original (a)+(b) 40 +
  hard (a)+(b) 40 + lag 100 = 180 rows. (c) rows excluded (different
  question, no calculator ground truth in the same sense).
- Step 2: 100 READ-ONLY hammer probes on the 100 lag items, hammer
  :8201 direct port only (never the router), EXACT lag-run payload
  (model 'hammer', same system prompts, same user-prompt
  construction, temp 0, max_tokens 4096, chat_template_kwargs
  enable_thinking False, 1 retry on unparseable output with the
  retry-ok fix). Fast seat NOT called. GT = item 'expected'
  (== calculator GT in the lag run, gt_mismatch 0/100).
- Step 3: separation = monotone tertile rates with NON-overlapping
  95% Wilson intervals (or equivalent). A monotone hint with
  overlapping intervals is reported as a hint, never as a
  separation. Spearman rho is reported alongside as a second view.
- No seat configs, router, JEV weights, live decider, or other
  program items were touched. No existing files were edited.

## 1. Calibration recomputed from saved rows (n = 180)

All counts recomputed from jev-decisions.json, jev-decisions-hard.json,
jev-lag-decisions.json. Field checks clean: 0 GT-mismatch flags,
0 hammer_correct-field mismatches, 0 contract_ok-vs-answered
mismatches.

| quantity | value | Wilson 95% |
|---|---|---|
| Hammer answered | 129/180 | — |
| P(hammer correct \| answered) | 73/129 = 0.566 | (0.480, 0.648) |
| P(hammer correct \| conf = 1.0) | 73/129 = 0.566 | (0.480, 0.648) |

- **Expressed confidence is a single point, not a curve.** All 129
  answered rows express exactly 1.0. There is no confidence value
  below 1.0 anywhere in saved hammer rows, so
  P(correct | confidence) has one bucket and zero information.
  The "roughly 0.56" figure from the brief is confirmed: 0.566.
- By type (answered): (a) 22/39 = 0.564 (0.410, 0.707);
  (b) 51/90 = 0.567 (0.464, 0.664). No type difference.
- By source (answered): orig 19/32 = 0.594 (0.423, 0.745);
  hard 13/25 = 0.520 (0.335, 0.700); lag 41/72 = 0.569
  (0.454, 0.677). All within noise of each other.
- **Contract classes (all 180 rows): fenced-parseable 129,
  bare-word 51, clean JSON 0, other-null 0.** Hammer NEVER emits
  clean JSON on these rows: it is fenced JSON or a bare word,
  nothing else. No empty or garbage nulls exist in this population.
- Bare-word leaning (not answers, reported separately): 23/51 =
  0.451 (0.323, 0.586). Chance-level; the interval includes 0.5.
  The leaning carries no signal beyond chance.
- Decision values (answered): (a) 'pass' 39/39 — hammer has NEVER
  said 'fail' when answering an (a) item in saved rows. (b) 'A'
  42/80 = 0.525 (0.417, 0.631); 'B' 9/10 = 0.900 (0.596, 0.982).
  The B interval overlaps the A interval (0.596 < 0.631), so even
  the best-looking split does NOT separate at 95% — and see §3
  for why the B hint does not independently replicate.
- **Agreement (both-answered rows, n = 93): agree 52/52 hammer
  correct; disagree 0/41 hammer correct, Wilson (0.000, 0.086).**
  The agree figure is trivial, not informative: fast was never
  wrong when answered in these populations (0/93), so
  agree ⇒ hammer correct by construction. The disagree figure is
  the binding one: on every observed disagreement, hammer is
  wrong and fast is right (41/41).

**What this implies for validation (stated before any probe):**
disagreement-conditional recalibration CANNOT validate a fast-wrong
detector on these rows, because no fast-wrong disagreement exists
in them. Any rule that trusts hammer on some disagreement subset
is unvalidated in exactly the direction that matters (catching
fast errors), and wrong on every observed disagreement. A
recalibration claim needs a population where fast-wrong
disagreements occur — these rows are not that population.

## 2. Probe availability and replication (100 fresh hammer calls)

- **Logprobs: AVAILABLE.** The capability check returned
  choices[0].logprobs.content on the pinned llama-server build
  (logprobs:true + top_logprobs:5 accepted, not ignored, not an
  error). All 100 probe rows carry logprob features, and token
  reconstruction matched message content 100/100, so the
  decision/confidence token spans are valid. Availability is a
  property of this serving build; a different build may not
  expose them. Availability is NOT signal (§3).
- Probe replication (same 100 lag items, fresh calls):
  answered 71/100, correct 41/71 = 0.578 (0.462, 0.686) — matches
  saved lag (41/72 = 0.569) closely. Confidence: all 71 at 1.0
  again. Contract: fenced 71, bare-word 29, clean 0, empty 0,
  think 0. (a) decisions: pass 21, fail 0 (again — hammer has
  still never said 'fail' when answering). (b): A 44, B 6.
  Attempts: answered rows all took 1 attempt; all 29 null rows
  took 2 (retry never succeeded in this probe), so attempts
  carry no signal beyond answered-ness itself.
- **Determinism finding (matters for §3): probe hammer == saved
  hammer on 71/71 both-answered rows (agreement 1.000;
  both_right 41, both_wrong 30, probe-only 0, saved-only 0).**
  The single differing row (new-a05) is a CONTRACT flip only:
  saved fenced-JSON 'pass' vs probe bare-word 'pass' — same
  leaning, different packaging. At temp 0 with identical prompts,
  hammer's decisions on this item set are effectively
  deterministic: re-runs REPLICATE, they do not add independent
  evidence. Consequence: probe decision-value splits MUST NOT be
  pooled with saved splits — that would double-count the same
  items. A larger probe needs FRESH items, not re-runs.

## 3. Separation tests (probe rows, answered only, n = 71)

Wilson 95% intervals throughout. Tertiles by feature value.
Criterion: monotone rates with non-overlapping intervals.
**Nothing meets it.**

| signal | low tertile | mid tertile | high tertile | Spearman vs correct | verdict |
|---|---|---|---|---|---|
| decision_logprob | 0.500 (0.314, 0.686) | 0.542 (0.351, 0.721) | 0.696 (0.491, 0.844) | +0.245 | hint only, overlaps |
| confidence_logprob | 0.583 (0.388, 0.755) | 0.583 (0.388, 0.755) | 0.565 (0.368, 0.744) | −0.015 | flat, no signal |
| mean_logprob | 0.500 (0.314, 0.686) | 0.542 (0.351, 0.721) | 0.696 (0.491, 0.844) | +0.149 | same shape as decision, overlaps |
| min_logprob | 0.667 (0.467, 0.820) | 0.583 (0.388, 0.755) | 0.478 (0.292, 0.670) | −0.135 | DECREASING, contradicts decision_logprob |
| mean_top1_prob | 0.417 (0.245, 0.612) | 0.667 (0.467, 0.820) | 0.652 (0.449, 0.812) | +0.200 | non-monotone, overlaps |
| decision_margin | 0.500 (0.314, 0.686) | 0.542 (0.351, 0.721) | 0.696 (0.491, 0.844) | +0.244 | same as decision_logprob, overlaps |
| raw length (chars) | 0.544 (0.402, 0.679) | 0.750 (0.301, 0.954, n=4) | 0.619 (0.409, 0.793) | +0.085 | template artifact (42–47 chars) |
| completion tokens | 0.554 (0.424, 0.676) | — (empty, ties) | 0.667 (0.417, 0.848) | +0.094 | template artifact (16–18 tokens) |
| duration | 0.542 (0.351, 0.721) | 0.708 (0.508, 0.851) | 0.478 (0.292, 0.670) | −0.020 | non-monotone, no signal |

Reading, honestly:

- The ONLY monotone hint is decision_logprob / decision_margin /
  mean_logprob (all the same underlying variation): correct-answer
  mean decision_logprob −0.207 vs wrong −0.299, medians −0.205 vs
  −0.271, tertiles rising 0.500 → 0.542 → 0.696, rho ≈ +0.24.
  But the low and high intervals overlap across 0.491–0.686, the
  rho confidence interval at n = 71 includes 0, and min_logprob
  points the OTHER way (decreasing). This is a weak, inconsistent
  hint, not a separation. It must not be used to reprice, and it
  is underpowered: a larger FRESH-item probe could test it, but
  that is a new job, not a conclusion here.
- Confidence_logprob is flat: the model's token-confidence in its
  own "1.0" carries no correctness signal. The expressed "1.0"
  and the token-level confidence in it are both uninformative —
  two independent confirmations of degeneracy.
- The logprob features are NOT decision-specific: mean_logprob
  mirrors decision_logprob (generic output fluency), while
  confidence_logprob is flat and min_logprob is inverted. There
  is no coherent logprob story, only a weak fluency correlation
  that does not separate.
- Decision value on probe rows: (b) B 5/6 = 0.833 (0.437, 0.970)
  vs A 23/44 = 0.523 (0.379, 0.663) — intervals overlap, and the
  6 probe B rows are EXACTLY the 6 saved lag B rows (same items,
  same correctness: orig-b09, orig-b12, orig-b17, hard-b16,
  new-b04 right; new-b05 wrong). This is the determinism finding
  again: the B hint is one observation re-measured, not two.
  Saved overall B 9/10 vs A 42/80 also overlaps (§1). The B hint
  stays a hint.
- Bare-word leaning on probe rows: 12/29 = 0.414 (0.255, 0.593) —
  chance, consistent with saved 23/51 = 0.451. No signal.
- Duration: no signal, consistent with the lag run (hammer
  latency degenerate, 0.066–0.100 s here).

## 4. Fixed-point verdict: NOT MOVED (with the proof sketch)

No signal separates, so no recalibrated policy exists to price.
The fixed point does not move, for three reasons that cover every
recalibration shape:

1. **Constant-to-base-rate mapping changes nothing.** Mapping
   hammer's expressed 1.0 to its calibrated base rate 0.566 leaves
   every merge decision unchanged: fast confidences (0.95–1.0)
   still beat 0.566 everywhere, so max-by-confidence picks fast
   on every row — identical decisions to ignoring hammer, i.e.
   the lean rule. A recalibration that changes no decision is
   not a moved fixed point.
2. **Any trust-on-disagreement rule is wrong on observed rows.**
   On all 41 observed disagreements hammer is wrong. A rule that
   trusts hammer on ANY disagreement subset (by logprob bucket,
   by decision value, by any probe feature) scores 0 on that
   subset's observed rows and is unvalidated for the fast-wrong
   case, which does not exist in the data. Trusting hammer
   anywhere on disagreements can only add error on observed rows.
3. **A logprob-gated trust rule has no validated gain.** Even the
   best-looking bucket (high decision_logprob tertile, 0.696
   hammer accuracy) sits below fast's 1.000 when answered, and
   no bucket contains a fast-wrong disagreement to validate
   against. Gating trust by logprob would trade correct fast
   answers for usually-wrong hammer answers at unknown rates.

Therefore the repriced frontier is IDENTICAL to item 4's lean
point, and no new table is produced: lag cost 0.28, floor-adjusted
error 0.0028 (band 0.0005–0.0153); orig+hard cost 0.25, floor error
0.0025 (band 0.0004–0.0136); floor P = 0.010, band
(0.0018, 0.0545). The policy stands: escalate on fast null OR fast
confidence < 0.8; hammer confidence is uninformative and must not
enter the escalation rule in any form (raw, recalibrated, or
logprob-gated) on current evidence.

## 5. What WOULD be needed (not built, beyond this item's scope)

1. **A different second-opinion seat** whose expressed confidence
   varies across items (not constant 1.0) and whose disagreements
   with fast include fast-wrong examples. Hammer, as served, is
   not that seat: its confidence never varies and its (a) channel
   is a constant 'pass' emitter.
2. **A trained calibrator on FRESH items.** Fitting a calibrator
   to these rows would fit hammer's determinism, not its
   generalization: re-runs of these items replicate exactly
   (§2), so they add no training data. Fresh items only.
3. **Fast-wrong disagreement examples.** The missing measurement
   is a fast+hammer run on ns2-like items where fast actually
   errs when answering (ns2-a23 proves such items exist, but ns2
   has no hammer rows, so the disagreement-conditional rate there
   is unmeasured). Until that run exists, the insurance
   break-even r = 0.01 from item 4 stays unmeasured (0/41
   observed, rule-of-three upper ≈ 0.073) and no hammer-side
   signal can be validated for the case it would need to catch.

## 6. Limitations (everything that weakens the negative)

1. **Constructed materials, not saved real work** (same caveat as
   all JEV runs). Hammer's degeneracy is measured on small
   constructed functions; real diffs could in principle elicit
   varied confidence — but nothing in these 280 rows + 100 probe
   rows hints at it.
2. **Small probe n (71 answered).** The decision_logprob hint
   (rho ≈ +0.24) is underpowered; a larger fresh-item probe could
   resolve it either way. Underpowered is not separated, and this
   item does not claim the hint is false — only that it does not
   separate here and must not be priced.
3. **Determinism limits the probe.** Because hammer replicates
   exactly on these items, the probe confirms stability, not
   generalization. The probe's decision-value splits are not
   independent evidence (§2, §3).
4. **Logprob availability is build-specific.** The pinned
   llama.cpp server exposes logprobs; another serving build may
   not. The availability finding does not transfer automatically.
5. **Temp-0 greedy outputs compress logprob variation.**
   Mean top-1 probability spans only 0.899–0.962 across probe
   rows; the model's token distribution is near-degenerate at
   temp 0, which limits what any logprob signal could separate
   even in principle on this serving setup.
6. **This item ONLY.** No decider change, no seat change, no
   frontier re-run, no program close. Item 4's numbers are
   quoted, not recomputed, for the unchanged policy (§4).

## 7. Files

- This summary: `jev-hammer-recalibration-summary.md`
- Calibration recomputation (saved rows): 
  `jev-hammer-recalibration-calibration.json`
  (script: `jev-hammer-recalibration-analyze.py`)
- Probe rows (100, fresh hammer calls, logprob features):
  `jev-hammer-recalibration-probe.json`
  (script: `jev-hammer-recalibration-probe.py`;
  mrfloppy `~/jev-test/hammer-recalibration/` holds script,
  probe JSON + JSONL, done marker)
- Separation tests (probe rows + stability join):
  `jev-hammer-recalibration-separation.json`
  (script: `jev-hammer-recalibration-separate.py`)
- All local files mirrored on mrfloppy under
  `~/jev-test/hammer-recalibration/`.
