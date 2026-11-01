# SETTLED-VERDICTS.md

Confirmed and refuted theory IDs from `theories-full-inventory.md`
(228 entries, TH-001–TH-228; status as of 2026-10-31). Only the
entry-level statuses are listed here. The basis is the basis each
entry states; where an entry states no basis parenthetical, that
is said plainly. Untested, partial, design, literature, applied,
killed, analogy, and void entries are NOT settled verdicts and
are not listed as such; the full inventory is in the private
`research-private` repo.

## Counts as stated in the inventory's Counts table

- CONFIRMED: 38
- REFUTED: 8
- PARTIAL: 13
- UNTESTED: 29
- ANALOGY: 3
- DESIGN: 29
- LITERATURE: 61
- APPLIED: 33
- KILLED: 9
- VOID: 5

## Counts from the entries themselves

- ANALOGY: 3
- APPLIED: 33
- CHECKED: 1
- CONFIRMED: 39
- DESIGN: 29
- KILLED: 9
- LITERATURE: 61
- PARTIAL: 12
- REFUTED: 8
- UNTESTED: 29
- VOID: 4

## MISMATCH — Counts table vs entries (reported, not resolved)

The Counts table and the per-entry statuses disagree on the
following entries. Both statements are preserved here; neither
was silently corrected. The lists below follow the ENTRY statuses.

- TH-194 — entry status: APPLIED; Counts-table status: None.
- TH-196 — entry status: CHECKED; Counts-table status: VOID.
- TH-206 — entry status: CONFIRMED; Counts-table status: PARTIAL.

## Table integrity

The Counts-table ID lists name 227 unique IDs of 228 entries; the stated counts sum to 228.
Per-row stated count vs ID-list length:
- CONFIRMED: stated 38, list length 38
- REFUTED: stated 8, list length 8
- PARTIAL: stated 13, list length 13
- UNTESTED: stated 29, list length 29
- ANALOGY: stated 3, list length 3
- DESIGN: stated 29, list length 29
- LITERATURE: stated 61, list length 61
- APPLIED: stated 33, list length 32  <-- DIFFERS
- KILLED: stated 9, list length 9
- VOID: stated 5, list length 5

## CONFIRMED (39)

- **TH-045** — status as stated; no basis parenthetical in entry
- **TH-050** — single failure cf-b30, base36_to_int both-pass ambiguity: suite lacks a leading/trailing-whitespace test — a coverage gap, not a wrong test; on both-pass items the decider needs a tie-break/further-escalation rule
- **TH-051** — status as stated; no basis parenthetical in entry
- **TH-055** — status as stated; no basis parenthetical in entry
- **TH-058** — status as stated; no basis parenthetical in entry
- **TH-063** — status as stated; no basis parenthetical in entry
- **TH-064** — flag FIRES: swap agreement 25/42 = 59.5%, flips 17/42, slot B in 69.6% of 411 calls; no judged-only margin is clean; auto-decision components unaffected
- **TH-066** — status as stated; no basis parenthetical in entry
- **TH-067** — 30s cap first majority 119; 60s cap first majority 126; 120s-cap prediction n≈133, 240s n≈140 pinned, not launched
- **TH-068** — status as stated; no basis parenthetical in entry
- **TH-069** — status as stated; no basis parenthetical in entry
- **TH-070** — status as stated; no basis parenthetical in entry
- **TH-071** — Stage 1 flattened per-node cost to ~10 μs, median speedup ~69.4×
- **TH-072** — status as stated; no basis parenthetical in entry
- **TH-073** — correctness gate 390/390, 0 flips; wall (118,119] → (173,174], +55 vars, firmed
- **TH-074** — gate 390/390; wall (200,201], +27 vars; node ratio median 0.209 but per-node cost ~5× from full-scan pick, wall-clock median 0.94
- **TH-075** — decision-identity gate 390/390 verdict + node counts identical, 428/428 with diagnostics; per-node cost 13.1 µs vs 52.5 µs; speedup median 3.94×, 0/390 slower; bracket MOVED above 201 — Stage 2's (200,201] must not be quoted as the heap solver's wall; fallback/budget trigger frequency unmeasured
- **TH-079** — written into the plan
- **TH-080** — all 6 gates pass both seeds: localization 0.023/0.016, size error −0.01/−0.11, contrast recovery 0.87/0.88 one-step; 3-iteration GN overshoots contrast 1.19–1.20, one-step stays default
- **TH-081** — status as stated; no basis parenthetical in entry
- **TH-084** — both seeds
- **TH-086** — |Γ₂| = 8.122 ≥ 2.683, ratio 3.03
- **TH-087** — wave err ≤ 1.8e-3
- **TH-090** — status as stated; no basis parenthetical in entry
- **TH-164** — status as stated; no basis parenthetical in entry
- **TH-172** — status as stated; no basis parenthetical in entry
- **TH-174** — Phase 1 complete 2026-10-03, installed mrfloppy ~/llm/cube/; Phase 2 queued
- **TH-175** — settled
- **TH-177** — status as stated; no basis parenthetical in entry
- **TH-178** — SUPPORTED
- **TH-179** — SUPPORTED
- **TH-182** — resolved
- **TH-183** — settled
- **TH-188** — Phase 2: every valid model best-in-band at ≥1 job; control comparison: once template handling is controlled, origin doesn't separate the band; research leads specialties, product steadier
- **TH-204** — planted-error test live 2/3 caught by validity, not by verify
- **TH-206** [ENTRY/TABLE MISMATCH — see above] — status as stated; no basis parenthetical in entry
- **TH-224** — design decision: skip hardware vocal processing
- **TH-227** — status as stated; no basis parenthetical in entry
- **TH-228** — mechanism finding M1: template control dominates; Qwen3-4B needs BUDGET not kwargs; LFM3 needs enable_thinking:false on EVERY request

## REFUTED (8)

- **TH-019** — status as stated; no basis parenthetical in entry
- **TH-046** — status as stated; no basis parenthetical in entry
- **TH-047** — fixed point does not move: 129 answered / 73 correct = 0.566; expressed confidence exactly {1.0} on all 129, zero information; mapping 1.0 → 0.566 changes no decision = identical to ignoring hammer = lean; logprobs carry no signal either — decision_logprob tertiles 0.500/0.542/0.696, Spearman +0.245, intervals overlap
- **TH-056** — status as stated; no basis parenthetical in entry
- **TH-062** — coder-30B 20/28, Coder-Next 21/28, lean final 22/28, 0 nulls in 56 rows, every coder-30B error at confidence 0.95; both-wrong set A10/A12/A14/B10/B14 — single-line semantic traps; the calculator 56/56 and the second-opinion SHAPE survive; on real work safety must come from running the tests
- **TH-065** — status as stated; no basis parenthetical in entry
- **TH-085** — status as stated; no basis parenthetical in entry
- **TH-181** — NEGATIVE
