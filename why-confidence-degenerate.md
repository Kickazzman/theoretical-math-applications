# Why the confidence numbers look the way they do — filled in

Written 2026-10-31. Ordered by perg's "Lets fill that in" (2026-10-31
17:00 EDT), closing the open follow-up from V-01/V-01b: why the seats
report confidence 0.95–1.0 almost regardless of outcome. Method:
forensic analysis of saved rows (raw vs parsed, flags, attempts,
contract classes) plus read-only reading of the runner scripts and
prompts that produced them. No new seat calls, no files modified
except this memo and the record pointers named at the end.

## Why this memo exists

V-01 refuted the threshold claim and V-01b showed the confidence
signal has no dynamic range, no ordering information, and no
exploitable headroom on the saved rows. Both left the same question
open: is the degeneracy in the seats, in the harness, or in the
prompt? This memo adjudicates that, hypothesis by hypothesis, with
the evidence for each and the evidence against each alternative.

## The answer, in one chain

1. **The prompt asks for an uncalibrated self-report.** The exact
   system prompt in `jev-lag-run.py` (lines 238–255, replicated
   exactly in the recalibration probe) is: reply JSON ONLY, two
   fields, "confidence (a number from 0 to 1, your estimated
   probability that your decision is correct)". No calibration
   instruction, no examples of when to be uncertain, no scoring
   rule, no penalty for overconfidence, no request to weigh
   evidence or alternatives first. The model is asked to grade
   itself, bare, in the same breath as deciding.
2. **Sampling is greedy.** Temperature 0, 4096-token budget,
   direct ports. Greedy decoding returns the modal completion;
   for a self-report field the modal completion is a round high
   number. The observed values are quantized to round numbers
   only: fast {0.9, 0.95, 0.99, 1.0}, hammer {1.0}, next
   {0.5, 0.75, 0.95, 1.0}. Nothing between 0.75 and 0.9, nothing
   at 0.8, 0.85, 0.6, 0.7 anywhere in 346 saved rows.
3. **The harness is faithful — it adds nothing and removes
   nothing.** Parsed confidence equals the raw emitted value on
   EVERY row checked (0 mismatches across 190 JEV rows, 56
   real-diff rows, 100 null-sensor rows). The parser takes
   `float(obj['confidence'])` directly. Rows with no confidence
   are exactly the empty/null rows (fast_empty counts match
   None counts in all three JEV files); no default value is ever
   substituted. Fenced or bare-word outputs yield no confidence,
   not a filled-in one.
4. **The seats differ, so it is seat behavior, not a harness
   constraint.** Hammer (:8201) emits exactly 1.0 on all 129
   answered saved rows and all 71 fresh probe rows, never clean
   JSON (fenced JSON or bare word only), and is wrong on 56 of
   those 129 — P(correct | 1.0) = 0.566. Fast (quicklook) emits
   0.95/0.99/1.0 and is right on 60/60 answered JEV rows and
   85/86 null-sensor rows; its single wrong answer (ns2-a23,
   the str.title() "don't"→"Don'T" case) was emitted at
   confidence 1.0. The next seat DOES emit 0.5 and 0.75 (3 rows),
   proving the contract itself does not force 0.95+.
5. **The number is modal self-presentation, not a measured
   probability.** The models have no access to their own error
   rate on these items, no calibration examples, and greedy
   decoding collapses the distribution to the modal round
   number. Hammer's collapses to a point (1.0); fast's to
   3–4 round values with no ordering information (V-01b leg 2);
   token-level confidence in hammer's own "1.0" is flat too
   (item 5, §3). The field records how confident the model
   sounds, not how often it is right.

## Ruled out, with the evidence (why-nots)

- **NOT harness defaulting or clamping.** Raw == parsed on every
  row; no default substitution exists in the parser.
- **NOT retry artifacts.** Lag rows with 2 attempts show the same
  confidence values (0.95/1.0) as 1-attempt rows; 2-attempt
  null rows have no confidence at all.
- **NOT the contract forcing high values.** The next seat emits
  0.5/0.75 under the same two-field contract.
- **NOT a parsing bug.** Fenced/bare-word rows yield None, never
  a synthesized number; field checks in item 5 found 0
  contract_ok-vs-answered mismatches.
- **NOT sampling noise.** Temp 0; the probe replicated saved
  hammer decisions 71/71. Re-running these items adds no new
  evidence (determinism finding, item 5 §2).
- **NOT evidence the seats know when they are right.** Fast's
  only wrong answer sits at 1.0; hammer is wrong 44% of the
  time at 1.0.

## What this does NOT show (open, not filled in)

- Whether a differently-built confidence would carry signal:
  calibration examples, a scoring/betting rule, reasons-before-
  number, or a logprob-derived confidence for the FAST seat
  (logprobs were tested for hammer only, item 5, and did not
  separate). Any of these needs a FRESH run on FRESH items —
  re-running these items replicates exactly and adds nothing.
- Whether the next seat's 0.5/0.75 values are calibrated: 3 rows
  is too few to say anything.
- Why hammer never emits clean JSON while fast does: a
  seat-formatting difference, on record (item 5 §1) but not
  explained here; it does not affect the confidence finding,
  since fenced JSON rows carry the same 1.0.

## Policy implication (stated, not decided here)

On this evidence the lean decider's confidence leg (< 0.8) is
dead weight on saved rows: V-01b leg 1 proves removing it
changes no decision on any saved row. Keeping it is insurance
against an unobserved case type — a fast-wrong answer emitted
with LOW confidence — but the one observed fast-wrong case
(ns2-a23) was emitted at 1.0, so the leg would not have caught
that type either. Removing or keeping the leg is perg's call;
this memo changes no rule.

## Evidence pointers

- Prompts: `jev-lag-run.py` lines 238–255 (SYS_A/SYS_B);
  `jev-hammer-recalibration-probe.py` lines 44–56 (same text).
- Parser: `jev-lag-run.py` lines 175–179; probe lines 113–121.
- Saved rows: `jev-decisions.json`, `jev-decisions-hard.json`,
  `jev-lag-decisions.json`, `real-diff-coder/decisions-*.json`,
  `jev-null-sensor-records.json`.
- Prior work: `jev-hammer-recalibration-summary.md` §1–§3
  (hammer constancy, logprob tests, determinism).
- Tests: `v01-threshold-sweep-results.md`,
  `v01b-different-way-results.md`.
