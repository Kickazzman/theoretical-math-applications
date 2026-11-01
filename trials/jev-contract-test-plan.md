# JEV contract test — plan (ready to execute)

Status 2026-10-28: PLAN ONLY. This tests the CONTRACT (fast calibrated
decider + slow thinker gated on confidence) with existing seats. It does
NOT build the vLLM + /v1/decide service — that build waits on this test's
outcome. Terms below are proposed, not approved: perg still owes the
task family, success definition, and kill criterion (programming
decisions are the recommended family, since that is his stated worry).

## Shape

- Fast decider: hammer (:8201) and/or quicklook (:8203) — resident,
  cheap. Each states a decision + a confidence 0–1.
- Slow thinker: Qwen3-Coder abliterated (serial) — or huihui as the
  audit pair (coder proposes, huihui checks, or vice versa).
- Escalate when: stated confidence < 0.8, OR the two fast seats
  disagree, OR a high-stakes flag is set.
- Independence condition (binding): the second thinker must differ
  from the first (different model, or a calculator). Two passes from
  the same model are an echo chamber, not a duplex. For programming,
  the strongest slow side is the calculator: tests + verifier.

## Decision types (50 total, programming family)

- (a) Patch-correct? Given a diff + its tests, will it pass?
- (b) Which implementation is better? Given two implementations + a
  spec, pick one (judged by which passes hidden tests).
- (c) Safe to merge? Review verdict (judged by perg's agreement on a
  sample, since this one has no test oracle).

## Measurement

- Bucket stated confidence: 0.5–0.6, 0.6–0.7, 0.7–0.8, 0.8–0.9, 0.9–1.0.
- Measure ACTUAL success per bucket (tests pass for (a)/(b); perg
  agreement for (c)).
- Calibration is good if success rises monotonically with bucket and
  the top bucket is >= 85%.

## Kill criteria (proposed)

- Top confidence bucket < 85% success, OR
- escalation improves outcomes by < 10 percentage points over the
  fast seat alone.
Either one kills the duplex: keep the single fast seat + calculator,
skip the dedicated decider build.

## Log template (one row per decision)

decision_id, type, prompt_ref, fast_decision, fast_confidence,
slow_decision, escalated (y/n), ground_truth (test result / perg
agreement), correct (y/n).
