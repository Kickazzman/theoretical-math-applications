# JEV-style decision duplex — sketch (DRAFT, not adopted, 2026-10-28)

Perg's direction: explore duplexing JEV-style decision models, under his
serial rule (best-for-purpose models run in series when VRAM is short;
nothing needs to be resident in parallel).

## The contract being borrowed (AutoTrust JEV/GEV, vendor-reported)

- System 1: one forward pass returns a *calibrated probability for every
  option* — yes/no, pick one of 2–256 options, rate 0–5 — over text and
  images, prompts up to 256K tokens. ~45 ms per decision (their number).
- Adaptive thinking: below 0.8 confidence, System 2 reasons and its
  answer is folded back into the probabilities.
- JEV-9B is the smallest family member with the same decision API;
  JEV-27B-VL adds vision; GEV-26B-Decide pairs Gemma-4-26B-A4B thinking.
- Adapters/decision heads/calibration files: Apache-2.0. Base models:
  original licenses (Gemma/Qwen terms need review before any use).
- Serving: vLLM + a custom `/v1/decide` endpoint. NOT a drop-in
  llama.cpp chat model. Do not assume the weights load in his multiplex.

## The duplex, in his architecture (no new serving stack)

Two seats, one contract, run in series:

1. **Fast decider (resident).** A small model (quicklook-class, or a
   JEV-9B-class model if its stack is ever adopted) that MUST output a
   typed decision + a confidence per option — no prose. Prose is a
   failure of the contract, not a style choice.
2. **Slow thinker (loaded on demand).** A larger model (Bolt-class,
   Qwen-class) that runs ONLY when:
   - fast confidence < 0.8, OR
   - two fast runs disagree, OR
   - the decision is flagged high-stakes by the caller.
   Its reasoning is folded into the probabilities, not appended as prose.
3. **Disconfirmation seat (existing pattern).** The slow thinker also
   tries to kill the fast decision: what evidence would make each option
   wrong? A decision that survives gets acted on; one that dies goes
   back for a re-decide or to perg.

## The checkable claim (calculator disposes)

Calibration, measured, not asserted:
- Bucket decisions by stated confidence (0.5–0.6, 0.6–0.7, …, 0.9–1.0).
- For each bucket, measure actual success rate on held-out tasks.
- A calibrated decider's success rate tracks its confidence bucket.
  A decider whose 0.9 bucket succeeds 50% of the time is uncalibrated
  and must not gate actions, whatever its headline accuracy is.
- Kill criterion (to be set by perg before any build): e.g. if the
  0.8+ bucket is not at least as accurate as the slow thinker alone on
  the same tasks, the fast seat does not earn its gate.

## Serial loading order (VRAM rule)

1. Fast decider resident (small, ~2–9B, fits alongside residents).
2. On low confidence / disagreement: pause or keep fast resident,
   load slow thinker alone (Bolt-class needs ~22GB + KV headroom —
   see 2026-10-28 Bolt serial eval), run, unload.
3. Never require both large models resident at once. The pause window
   is the cost; the calibration gate is what buys it.

## Open questions for perg (not decided here)

- Which task family first: browser/computer-use clicks (JEV's demo
  domain), or his own decisions (route choices, gate verdicts, kill
  calls)?
- What counts as "success" for a calibration bucket on his tasks?
- Does the fast seat need to be a real JEV weight (vLLM stack), or is
  a prompted small model with a strict JSON decision contract enough
  to test the duplex first? Recommendation: test the contract first
  with existing models; adopt JEV weights only if the contract wins.
- Threshold: is 0.8 the right escalation point, or does his cost
  model (pause window vs. wrong decision) move it?

## What this is NOT

- Not an adoption of JEV weights, not a vLLM migration, not a change
  to any live multiplex seat. A design sketch awaiting his word.
- Not a claim that vendor numbers (45 ms, 95% computer-use) transfer
  to his hardware. Those are AutoTrust's self-reported figures.
