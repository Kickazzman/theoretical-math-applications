# V-01 / TH-065 overshoot threshold sweep — results

Protocol: `v01-threshold-sweep-protocol.md`, sha256
`64c309b746a71f6f0ebcd40fd529460ca85e5f7727df648e0bdd297cfb160b96`
(pre-registered 2026-10-31, before any sweep count). Ordered by perg's
"lets test these and try to get the answer in multiple ways"
(2026-10-31 16:54 EDT) — first item of the value order, tested three
independent ways. Computation: `v01-threshold-sweep.py` (read-only
over the saved rows; full JSON: `v01-threshold-sweep-results.json`).
Source files never modified.

## Verdict (pre-registered rule): REFUTED

No threshold dominates 0.8 in ANY of the four populations. The
confirming-thresholds list is empty.

## The finding behind the verdict

The threshold is INERT on these rows. Fast confidences take only
three or four values, all at or above 0.9:

| Population | Included n | Distinct fast confidences |
|---|---|---|
| P-contract | 32 | 0.95, 0.99, 1.0 |
| P-hard | 14 | 0.95, 0.99, 1.0 |
| P-lag | 51 | 0.95, 0.99, 1.0 |
| P-realdiff | 28 | 0.9, 0.95 |

For every threshold T in 0.50–0.95, escalation rate is 0.0 and final
accuracy equals fast-only accuracy in every population (contract
0.875, hard 1.000, lag 1.000, realdiff 0.714). The 0.8 confidence leg
of the lean decider NEVER fires on an included row — only the
fast-null leg escalates, and null rows are excluded from the
included set by definition. At T = 1.0, escalation fires and accuracy
falls in all three JEV populations (contract 0.875 → 0.750, hard
1.000 → 0.714, lag 1.000 → 0.824) while rising one row in real-diff
(0.714 → 0.750 at 100% escalation) — dominated or non-dominating in
every case, never dominating.

Built-in check: included n reproduces Trial 1 exactly (32 / 14 / 51 /
28). Three-way agreement: Way 1 (direct) and Way 2 (cell
aggregation) agree EXACTLY on all 44 grid cells; Way 3 (sorted step
function) confirms the flatness mechanism — only thresholds crossing
a present confidence value can change the outcome, and none present
in 0.5–0.95 does. The sweep is degenerate because the confidence
signal has almost no dynamic range here, consistent with the earlier
recorded finding that hammer confidence never varies.

## Reading (labeled)

TH-065 is refuted AS STATED on this data: no dominating threshold
exists, because the threshold cannot move. That is a finding about
the instrument (confidence has no usable range on these rows), not
about thresholds in general — on rows where confidence actually
varies below 0.9, the question reopens and needs its own
pre-registration. The live follow-up is why fast confidence never
dips below 0.9 here; that question is NOT answered by this sweep
and is recorded as open, not filled in.
