# JEV Contract Test — Report (run 3, 2026-10-29)

**Verdict: +1 PASS under the approved rule — with three caveats that matter
for the build decision (see §6).** Top confidence bucket 35/35 = 100%
(Wilson 95% (0.901, 1.0)) clears the 85% bar, and escalation improves
outcomes by +12.5pp (87.5% → 100%), clearing the 10pp bar. Both kill
criteria fail to fire. But: monotonicity is UNTESTED (one non-empty
bucket), and the improvement came from filling non-answers, not from
correcting wrong decisions (the fast seat was never wrong when it
answered).

## 1. What was tested

The CONTRACT only: a fast calibrated decider (quicklook :8203 primary,
hammer :8201 second opinion, strict JSON: typed decision + confidence
0–1, no prose) gated on confidence, with a slow thinker (the CALCULATOR:
running the tests) for oracle types. No vLLM, no JEV weights, no live
seat changes, no router changes. Mrfloppy only.

- (a) patch-correct? — 20 items (10 functions × correct→buggy FAIL +
  buggy→correct PASS). Kill-determining.
- (b) which implementation is better? — 20 items (10 functions ×
  correct-vs-buggy pairs, correct position randomized, seed 12345).
  Kill-determining. The fast seats never see the hidden tests (the
  authored tests are the calculator's).
- (c) safe-to-merge? — 10 items, reported separately, NOT
  kill-determining. Ground truth = perg's batched agreement (§7).

Escalation (a)/(b): quicklook confidence < 0.8, OR the two fast seats
disagree, OR a null fast decision (cannot trust a non-answer).
Escalated items' final decision = calculator (ground truth).
(c): high-stakes, always escalated; slow = hammer's opinion.

## 2. Per-bucket tables (quicklook confidence → actual success)

Wilson 95% intervals, seed-fixed. Buckets below 0.9 are EMPTY: quicklook
never expressed confidence below 0.95 on these items (29× 1.0, 5× 0.95,
1× 0.99). The calibration curve is a single point, not a curve.

### Combined (a)+(b), n = 40

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.5–0.6 | 0 | 0 | — | — |
| 0.6–0.7 | 0 | 0 | — | — |
| 0.7–0.8 | 0 | 0 | — | — |
| 0.8–0.9 | 0 | 0 | — | — |
| **0.9–1.0** | **35** | **35** | **1.000** | **(0.901, 1.0)** |
| <0.5 (separate row) | 0 | 0 | — | — |

5 (a)+(b) items are unbucketed: quicklook returned EMPTY (contract
failure, counts against fast-alone accuracy, excluded from buckets).

### (a) alone, n = 20

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.9–1.0 | 18 | 18 | 1.000 | (0.824, 1.0) |
| all lower buckets | 0 | 0 | — | — |

Fast-alone (a): 18/20 = 0.900 (2 empties).

### (b) alone, n = 20

| bucket | k | success | rate | Wilson 95% |
|---|---|---|---|---|
| 0.9–1.0 | 17 | 17 | 1.000 | (0.816, 1.0) |
| all lower buckets | 0 | 0 | — | — |

Fast-alone (b): 17/20 = 0.850 (3 empties).

Per-type top-bucket point estimates are 100%, but their Wilson lower
bounds (0.824, 0.816) sit below 85% at k = 17–18. The combined k = 35 is
what firms the top bucket past the bar (lower bound 0.901).

## 3. Calibration verdict

- **Top bucket ≥ 85%: YES** (combined 100%, Wilson lower 0.901).
- **Monotone: UNTESTED, not confirmed.** The monotone check passes
  vacuously (one non-empty bucket). There are no lower buckets to
  compare against, so "success rises with bucket" was not measured.
  The test cannot say whether a 0.6-confidence decision would succeed
  ~60% of the time — the model never says 0.6.
- **Confidence range unused.** A calibrated decider needs to USE the
  range; quicklook on these items does not (all 0.95–1.0). Whether
  that is justified confidence (it was right 35/35 when it answered)
  or overconfidence that would fail on harder items is untestable on
  this set.

## 4. Escalation

| metric | value |
|---|---|
| Fast-alone (quicklook) | 35/40 = 0.875 |
| Hammer standalone | 19/40 = 0.475 (32 answered: 19/32 = 0.594) |
| Escalated (final) accuracy | 40/40 = 1.000 |
| **Escalation improvement (overall)** | **+12.5pp** |
| Escalation rate | 18/40 = 0.450 |
| Fast accuracy on escalated subset | 13/18 = 0.722 |
| Escalated-subset improvement | +27.8pp |
| Agreement (quicklook vs hammer) | 15/40 = 0.375 |

Escalation anatomy (18 = 5 null-fast + 13 disagreement + **0
confidence-triggered**). The 0.8 confidence rule NEVER fired — no
confidence fell below 0.9. All escalation came from non-answers
(fallback) and disagreements (verification).

Cross-tab (a)+(b), fast × hammer:

| | hammer null | hammer right | hammer wrong |
|---|---|---|---|
| **fast null** | 1 | 4 | 0 |
| **fast right** | 7 | 15 | 13 |
| **fast wrong** | 0 | 0 | 0 |

Two facts dominate this table:

1. **Fast was never wrong when it answered (0/35).** Every fast-alone
   error is a non-answer (empty), not a wrong decision.
2. **Every disagreement was fast-right / hammer-wrong (13/13).**
   Disagreement escalation verified fast's answers but changed none
   of them. The accuracy gain came entirely from the 5 nulls.

Design implication (finding, not a change): a leaner escalation rule —
null OR confidence < 0.8, WITHOUT the disagreement rule — achieves the
identical 100% final accuracy on this data at 12.5% escalation instead
of 45%. The disagreement rule bought verification, not accuracy, here.
Whether verification is worth 32.5pp of extra calculator runs is a
design choice for perg, not something this test settles.

## 5. Recommended threshold

**None identified — the curve is flat.** At every threshold 0.5–0.9,
the pooled set is the same 35 items (all confidences ≥ 0.95), pooled
success 100%, confidence-only escalation rate 12.5% (the 5 nulls).
The runner's mechanical output ("0.5") is degenerate and is NOT a
recommendation to lower the threshold: there is no low-confidence data
to justify any threshold. **Keep 0.8** — it fired zero times here, but
that is because confidences never dropped, not because 0.8 is wrong.
A threshold can only be calibrated once the decider actually expresses
low confidence (harder items, §6).

## 6. Kill verdict: +1 PASS (literal rule) + caveats + suggested next probe

Per the approved rule: top bucket 100% ≥ 85% (k = 35 ≥ 5) AND
improvement 12.5pp ≥ 10pp → neither kill criterion fires → **+1 PASS**.
The dedicated decider build is NOT killed by this test.

Caveats (all three must travel with the verdict):

1. **Ceiling confound, live.** Fast-alone 87.5% leaves only 12.5pp of
   headroom, and the bar consumed 10pp of it (80%). A slightly better
   fast seat (fewer empties) would have TRIPPED the kill rule despite
   being better. The improvement criterion punishes a better fast seat.
   The +12.5pp passed, but only just, and only via non-answers.
2. **The error-correction path is untested.** The duplex's core claim
   is that the slow thinker corrects fast errors. Fast made zero
   errors when it answered, so no correction was ever exercised. What
   was exercised: fallback for silences (5 items) + verification of
   correct answers (13 items).
3. **Monotonicity untested** (§3) and **the item set may be too easy**
   (small functions, clear bugs — fast was perfect when it answered).

Suggested next probe (perg's call, NOT started): a harder item set
where the fast seat actually errs — subtler bugs, larger functions,
ambiguous specs — to exercise the correction path and the low
confidence buckets. If fast still never errs, the decider's value is
fallback + verification, and the build decision should be priced on
that, not on error correction.

## 7. (c) Batched agreement list — awaiting perg (ONE message)

No expected labels are included (to avoid anchoring perg's judgment).
For each item: the diff, the test status the seats saw, and both
seats' opinions. Hammer's bare-word answers are shown as its leaning
with a contract-failure flag (bare word = no JSON, no confidence, so
per the pre-registered rule its decision is null — but perg should see
what it leaned). Perg replies merge / do_not_merge per item.

### c01 — sliding_average: correct → c_diff — tests PASS
Fast (quicklook): **merge** @ 1.0. Slow (hammer): **merge** @ 1.0.
```diff
--- correct.py
+++ c_diff.py
@@ -5,5 +5,9 @@
         raise ValueError("window must be an int")
     if window < 1 or window > len(values):
         raise ValueError("window out of range")
-    return [sum(values[i:i + window]) / window
-            for i in range(len(values) - window + 1)]
+    window_sum = sum(values[:window])
+    result = [window_sum / window]
+    for i in range(window, len(values)):
+        window_sum = window_sum - values[i - window] + values[i]
+        result.append(window_sum / window)
+    return result
```

### c02 — chunk_list: correct → buggy_b — tests FAIL
Fast: **do_not_merge** @ 0.95. Slow: **do_not_merge** (bare word, no
JSON, no confidence — contract failure).
```diff
--- correct.py
+++ buggy_b.py
@@ -3,4 +3,4 @@
         raise ValueError("size must be an int >= 1")
     if size < 1:
         raise ValueError("size must be >= 1")
-    return [items[i:i + size] for i in range(0, len(items), size)]
+    return [items[i:i + size + 1] for i in range(0, len(items), size + 1)]
```

### c03 — clamp: correct → buggy_b — tests FAIL
Fast: **do_not_merge** @ 1.0. Slow: **do_not_merge** (bare word —
contract failure).
```diff
--- correct.py
+++ buggy_b.py
@@ -1,8 +1,8 @@
 def clamp(value, lo, hi):
     if lo > hi:
         raise ValueError("lo must be <= hi")
-    if value < lo:
+    if value > lo:
         return lo
-    if value > hi:
+    if value < hi:
         return hi
     return value
```

### c04 — top_k: correct → buggy_b — tests FAIL
Fast: **do_not_merge** @ 1.0. Slow: **do_not_merge** (bare word —
contract failure).
```diff
--- correct.py
+++ buggy_b.py
@@ -1,7 +1,9 @@
+# Hand-applied specified mutation: ties key-descending.
 def top_k(counts, k):
     if not isinstance(k, int) or isinstance(k, bool):
         raise ValueError("k must be an int >= 1")
     if k < 1:
         raise ValueError("k must be >= 1")
-    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
+    by_key_desc = sorted(counts.items(), key=lambda kv: kv[0], reverse=True)
+    ranked = sorted(by_key_desc, key=lambda kv: -kv[1])
     return [key for key, _ in ranked[:k]]
```

### c05 — parse_size: correct → buggy_b — tests FAIL
Fast: **do_not_merge** @ 1.0. Slow: **do_not_merge** (bare word —
contract failure).
```diff
--- correct.py
+++ buggy_b.py
@@ -9,7 +9,7 @@
     i = 0
     while i < len(t) and (t[i].isdigit() or t[i] == '.'):
         i += 1
-    num_part, unit_part = t[:i], t[i:].strip().upper()
+    num_part, unit_part = t[:i], t[i:].strip()
     if not num_part:
         raise ValueError("no number in size")
     try:
```

### c06 — wilson_lower: correct → c_diff — tests PASS
Fast: **merge** @ 1.0. Slow: **merge** @ 1.0.
```diff
--- correct.py
+++ c_diff.py
@@ -7,8 +7,13 @@
     if k < 0 or k > n or n < 0:
         raise ValueError("k must satisfy 0 <= k <= n and n >= 0")
     p = k / n
-    denom = 1 + z * z / n
-    centre = (p + z * z / (2 * n)) / denom
-    delta = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
+    d = 1 + z * z / n
+    centre = (p + z * z / (2 * n)) / d
+    delta = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
     lower = centre - delta
-    return max(0.0, min(1.0, lower))
+    if lower < 0:
+        return 0.0
+    elif lower > 1:
+        return 1.0
+    else:
+        return lower
```
(The change is: denominator computed once as `d`, clamp via if/else
instead of max/min.)

### c07 — format_duration: correct → c_diff — tests PASS
Fast: **no answer** (empty — contract failure). Slow: **merge** @ 1.0.
```diff
--- correct.py
+++ c_diff.py
@@ -4,15 +4,8 @@
     if seconds == 0:
         return "0s"
     parts = []
-    days, rem = divmod(seconds, 86400)
-    hours, rem = divmod(rem, 3600)
-    minutes, secs = divmod(rem, 60)
-    if days:
-        parts.append(f"{days}d")
-    if hours:
-        parts.append(f"{hours}h")
-    if minutes:
-        parts.append(f"{minutes}m")
-    if secs:
-        parts.append(f"{secs}s")
+    for label, secs in [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]:
+        count, seconds = divmod(seconds, secs)
+        if count:
+            parts.append(f"{count}{label}")
     return " ".join(parts)
```

### c08 — merge_intervals: correct → buggy_b — tests FAIL
Fast: **do_not_merge** @ 1.0. Slow: **do_not_merge** (bare word —
contract failure).
```diff
--- correct.py
+++ buggy_b.py
@@ -7,7 +7,7 @@
     ordered = sorted(intervals, key=lambda p: p[0])
     merged = [list(ordered[0])]
     for start, end in ordered[1:]:
-        if start <= merged[-1][1]:
+        if start <= merged[-1][1] and start > merged[-1][1]:
             merged[-1][1] = max(merged[-1][1], end)
         else:
             merged.append([start, end])
```

### c09 — backoff_delay: correct → c_diff — tests PASS
Fast: **merge** @ 1.0. Slow: **merge** @ 1.0.
```diff
--- correct.py
+++ c_diff.py
@@ -5,4 +5,4 @@
         raise ValueError("attempt must be >= 0")
     if base <= 0 or cap <= 0:
         raise ValueError("base and cap must be > 0")
-    return min(cap, base * (2 ** attempt))
+    return min(cap, base * (1 << attempt))
```

### c10 — median_of: correct → c_diff — tests PASS
Fast: **merge** @ 1.0. Slow: **merge** @ 1.0.
```diff
--- correct.py
+++ c_diff.py
@@ -3,7 +3,6 @@
         raise ValueError("median of empty list")
     s = sorted(values)
     n = len(s)
-    mid = n // 2
-    if n % 2 == 1:
-        return s[mid]
-    return (s[mid - 1] + s[mid]) / 2
+    lo = (n - 1) // 2
+    hi = n // 2
+    return (s[lo] + s[hi]) / 2
```

## 8. Fast-seat contract behavior

- **Quicklook (primary): clean JSON when it answers (prose 0.0,
  think 0.0), but intermittent EMPTY responses: 6/50 (12%).**
  The empties are NOT length-driven (short top_k prompts went empty
  while longer ones answered) and survive one retry — intermittent
  non-answers, mechanism unknown (not invented). In production they
  are fallback triggers (escalate), not wrong decisions.
- **Hammer (second opinion): poor decider + poor contract citizen.**
  Standalone 47.5% (59.4% when it answers); prose 100% (every response
  wrapped in ``` fences — parseable, flagged); 26% bare-word
  contract failures (13/50: a bare decision word, no JSON, no
  confidence). Its (a) bare words are a constant "pass" (4/8 matching
  ground truth = chance); its (c) bare words track the visible test
  status (do_not_merge on all 5 failing items). Its disagreements
  were 13/13 wrong. As a second opinion it adds cost, not accuracy,
  on this sample.

## 9. Limitations (everything that weakens the verdict)

1. **Materials are constructed, not saved real work.** No usable
   saved diff/test pairs existed (programming-seat.md has seat
   designations only; Dafny tasks are a different shape). Correct
   implementations + tests were hand-authored from precise specs;
   magicoder supplied variants under exact mutation instructions.
   Two free-form generation attempts failed first (content failures
   documented in the run log). The calibration transfers to real
   decisions only insofar as these small functions resemble them.
2. **Three variants hand-applied** (format_duration buggy_a,
   top_k buggy_a/buggy_b) where magicoder did not implement the
   specified mutation (conditional-append rewrite passing all tests;
   failed generation; a `(-count, -key)` sort that TypeErrors on
   strings). Each was verified by the test gate afterwards.
3. **One observed variant deviation:** merge_intervals buggy_b
   implements a stronger bug than specified (contradictory condition,
   never merges) rather than strict-inequality touching. It verifies
   failing, so items using it remain valid, but the bug is cruder
   than specified. Validity is gated by verification, not by mutation
   fidelity.
4. **One hint leak:** top_k buggy_b carries a comment naming its
   mechanism ("ties key-descending"). It hints where to look, not the
   verdict — and the affected fast item (b18) returned empty anyway,
   so it contributed nothing. Verdicts are robust to dropping b18
   (fast-alone 35/39 = 89.7%, top 35/35, improvement 10.3pp — still
   +1).
5. **Runs 1–2 void (serving artifact, documented).** Run 1 (300-token
   budget): quicklook empty on all 50. Run 2 (1024): quicklook empty
   on 44/50. Cause: Qwen3-4B thinks, and the budget truncated it
   mid-think (finish=length, stripped → empty); the
   chat_template_kwargs no-think flag does NOT suppress thinking on
   the pinned build. Run 3 (4096) is the valid run. Run 2's apparent
   kill=+1 was artifact-driven (fast-alone 0.15 from empties) and is
   NOT reported as a result.
6. **Single run, temp 0, but nondeterminism observed** (quicklook
   empties vary run to run; hammer bare words vary). A rerun could
   shift the empty count and the improvement margin (12.5pp vs the
   10pp bar is not a wide margin).
7. **Direct port calls, not via router** (per the brief). Decisions
   are unaffected by contention; only latency is.
8. **(c) unscored** pending perg's agreement (§7). No (c) accuracy
   is claimed.
9. **Spares unused:** slugify verified valid but unused (scale met
   with the 10 main functions); dedupe_preserve_order buggy_a never
   implemented its mutation (copy) and remains invalid/unused.

## 10. Files

- Decision log (50 rows): `jev-decisions.json`
- Summary (buckets, verdicts, thresholds): `jev-summary.json`
- Test items (diffs, specs, positions): `jev-items.json`
- On mrfloppy `~/jev-test/`: materials/ (12 functions ×
  correct/tests/buggy_a/buggy_b/c_diff), jev-run3.log,
  jev-decisions-run1-void.json, jev-decisions-run2-void.json,
  verify-report.json, gen-mutations-report.json.
- Scripts (local workspace): jev-author.py, jev-gen-mutations.py,
  jev-fix-variants.py, jev-verify.py, jev-build-items.py, jev-run.py.


## 7b. (c) Scoring — ground truth by assistant judgment (perg delegated 2026-10-30)

Perg: undecided on c01–c10; delegated the merge calls to the assistant's best judgment. Ground-truth rule applied: MERGE iff the diff is behavior-preserving AND tests pass; DO_NOT_MERGE iff tests fail. Seat opinions are scored against that ground truth; fast empties count as null (escalate), hammer bare words count as null per the pre-registered contract rule (leanings shown for information only).

| item | ground truth | fast | hammer (contract) |
|---|---|---|---|
| c01 sliding_average (refactor, PASS) | merge | merge — correct | merge — correct |
| c02 chunk_list (bug, FAIL) | do_not_merge | do_not_merge — correct | null (bare word; leaning do_not_merge) |
| c03 clamp (bug, FAIL) | do_not_merge | do_not_merge — correct | null (bare word; leaning do_not_merge) |
| c04 top_k (bug, FAIL) | do_not_merge | do_not_merge — correct | null (bare word; leaning do_not_merge) |
| c05 parse_size (bug, FAIL) | do_not_merge | do_not_merge — correct | null (bare word; leaning do_not_merge) |
| c06 wilson_lower (refactor, PASS) | merge | merge — correct | merge — correct |
| c07 format_duration (refactor, PASS) | merge | null (empty) | merge — correct |
| c08 merge_intervals (bug, FAIL) | do_not_merge | do_not_merge — correct | null (bare word; leaning do_not_merge) |
| c09 backoff_delay (refactor, PASS) | merge | merge — correct | merge — correct |
| c10 median_of (refactor, PASS) | merge | merge — correct | merge — correct |

Fast (c): 9/9 correct when answered, 1 null (c07, escalated; slow resolved merge). Hammer (c): 5/10 contract-valid and correct (c01, c06, c07, c09, c10); 5/10 null (bare words on the five FAIL items) whose leanings track test status — uninformative beyond the visible test result. (c) is now SCORED and CLOSED; it does not change the contract-test +1 verdict.
