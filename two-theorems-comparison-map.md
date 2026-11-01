# Two-theorems comparison map — initial map, 2026-10-31

Extended 2026-10-31 (perg: all theories, equations, multiple ways):
`all-theories-map.md` (M1–M7 × all subjects) and
`theoretical-equations-and-rederivations.md` (equations + re-derivation
register). This file remains the detailed M1×M2 comparison.

Perg: "compare each theory in every way we can within our research so we
can have our initial map" (2026-10-31 15:14 EDT). The two theories are
Komlós (M1) and Kelley–Meka (M2), as tried in the two trials. This map
compares them across every subject event on record in the theoretical-math
application file, using that file's rule: an application exists only when
the subject's own object, measurement, and decision can be named.
Otherwise the cell is VOID, CONTRAST, ANALOGY, or DESIGN — never a
transfer. No new measurement was run for this map; TRIED cells cite the
trial results, DESIGN cells state exactly what would have to be pinned
and run, and nothing here is a verdict on either theorem.

Source events: `theoretical-math-applications-spudcell-wire-fleet.md`
(E-S, E-W, E-F catalogues; attempts A1–A8, X1–X3; trials §8). Trial
records: `jev-discrepancy-results.md`, `wire-ap-results.md`,
`wire-ap-or-results.md`, with protocols `jev-discrepancy-protocol.md`,
`wire-ap-protocol.md`, `wire-ap-or-null-protocol.md`.

## §1 The two theorems, in the form used here

- **M1 — Komlós discrepancy** (Bansal–Jiang, (log N)^{1/4} scale; TH-122,
  PUBLISHED, STOC). The theorem: given vectors, signs can be chosen so the
  signed sum stays within a (log N)^{1/4}-scale bound. Its structure is a
  FREE SIGN CHOICE over a vector ensemble. The diagnostic carried into
  this research: the imbalance pattern of a paired ensemble, measured
  against a marginal-preserving null. What the theorem would add, if it
  applied: a guaranteed scale for that imbalance. What it needs to apply:
  vectors the subject actually signs, with the signing free.
- **M2 — Kelley–Meka sifting** (Kelley–Meka 2023; Bloom–Sisask 2023;
  TH-126). The theorem: a dense set of integers, sifted through Bohr sets,
  yields a large structured subset / density increment, forcing 3-term
  arithmetic progressions. Its structure is a SET + FREQUENCY SIEVE. The
  diagnostic carried into this research: AP density in the positions of
  1s in a sequence, against a generative null. What the theorem would
  add, if it applied: a constructed Bohr set and density increment. What
  it needs to apply: a set with a meaningful index, and a sieve whose
  frequencies are stated before counting.

Neither theorem has been applied in its own form anywhere in this
research. Both diagnostics have been tried. That distinction is the
map's central finding, and it holds in every TRIED cell.

## §2 Comparison dimensions

| Dimension | M1 Komlós | M2 Kelley–Meka |
|---|---|---|
| Object | An ensemble of sign patterns (paired right/wrong per item) | A set: positions of 1s in an indexed sequence |
| Index/ordering needed | None — items are exchangeable under the null | ESSENTIAL — positions must mean something (ticks do; file order of constructed items does not) |
| Free structure | Sign choice, free | Frequency set (Bohr set), stated before counting |
| Measurement | Four cells + marginal imbalance D1; structure in the slow-only count | 3-term AP count in the 1-positions |
| Null that fits | Marginal-preserving permutation (each seat's correct count fixed) | Generative null matching the construction (uniform permutation for a single sequence; OR-of-permutations for an OR-built sequence) |
| Null failure observed | D1 is pairing-invariant under its own null — SD 0.00, p-values void; the null was degenerate for the chosen statistic | Uniform permutation is the wrong null for an OR-built sequence — z = +15.78 footprint of the construction, reversed (z = −3.81) under the right null |
| Scale column | (ln N)^{1/4} — descriptive only; no verdict follows from it | Density — the count is density-dominated; the (0.2, 0.8) cap exists because at density ≈ 1 the count carries no information |
| What "applies" would mean | The bound governs the ensemble's imbalance scale | The sifting constructs a Bohr set + density increment from the count |
| Construction gap | No free signing in the subject → bound has no subject meaning | No Bohr-set construction performed → theorem does not follow from a count |
| Sensitivity | Structure lives in the cells, not the margin (D1 = F − S is marginal only) | Structure lives in joint timing, not marginal density (OR-null deficit proves the point) |
| Cheapest next test | Pin vectors in solver code (N3) | Count the B sequence, same window/protocol (N1) |

## §3 Matrix — every subject event × both theorems

Verdicts: TRIED (ran, result cited) · DESIGN (pinned, unrun) · VOID (no
object/measurement/decision namable) · CONTRAST (neighbouring result, different
object) · ANALOGY (parallel only, no transfer).

### Fleet events

| Event | M1 Komlós | M2 Kelley–Meka |
|---|---|---|
| E-F1 Null as complexity sensor (T1 0/32, T2 3/36, T3 11/32) | DESIGN — Object: null-pattern vectors per tier. Measurement: discrepancy of the null ensemble across tiers vs the marginal null. Decision: whether tiered nulls are structured or marginal. Unrun: tiers are 3, items are 100; the tier split, not the item pool, would have to be the vector set, and that pinning is not yet written. | VOID — No indexed sequence. Tier labels are categories, not positions; APs in tier order have no subject meaning. |
| E-F2 Lean-rule dominance (r unmeasured, 0/41) | CONTRAST — The lean rule already uses the disagreement cells (fast-only vs slow-only) as its decision variable, which is the same four-cell object A1 measured. But the lean rule is a cost rule, not a discrepancy bound: it never claims a scale, and A1 showed the scale column is descriptive only. The two agree on the object and disagree on what follows from it. | VOID — No sequence. The disagreement rate r is a scalar parameter, not a set with positions. |
| E-F3 Judge position bias (~70% slot B, swap 25/42) | TRIED (A1, via the seat ensemble) — The judge's bias is the same structural-disagreement question A1 tested on real diffs: significant agreement structure (p = 0.0096), direction opposite to JEV. The bias itself was NOT re-measured under Komlós; the trial measured coder-seat agreement, not judge calls. A judge-specific Komlós run is DESIGN (N6). | VOID — Presentation order is an index, but the verdict pattern over 411 calls is a judge artifact, not a subject set; APs in verdict positions would measure presentation structure, and that measurement is already owned by the swap analysis. No new decision would flip. |
| E-F4 SAT wall as quantile ((118,119] 30s; (235,236] count) | DESIGN (N3) — Object: per-instance branching vectors (which variable the solver branches on, per decision level). Measurement: discrepancy of the branch ensemble across instances at the wall. Decision: whether the wall is a search-structure effect or a cap artifact. Unrun: vectors must be pinned from solver code first; no solver run is authorized by this map. | VOID — Instance index order is arbitrary (generation order, not subject order). APs in instance positions would be numerology. The wall's own structure is a quantile, not a progression. |
| E-F5 EIT spectral verdicts (Cheeger CONFIRMED, edge REFUTED) | CONTRAST — Cheeger is the calibration case C-0: a bound that DOES apply, because the mesh is a graph and the partition is the subject's own object. Komlós is the contrast: a bound about signings that has no mesh meaning. The pair shows what an applied bound looks like (Cheeger) vs a non-applied one (Komlós) on neighbouring objects. | VOID — Eigenvalues have an order (sorted), but APs in eigenvalue positions have no subject meaning; the spectral verdicts are already complete (crossover, K* = 2 vs N_loc = 73). No decision would flip. |

### Wire events

| Event | M1 Komlós | M2 Kelley–Meka |
|---|---|---|
| E-W1 Dependence (+0.2846, MI 0.0553 bits) | VOID, with a derived marginal note — No sign ensemble: a and b are single bits per tick, not vectors to sign. Derived arithmetic only (not a measurement): over the full Oct 7 file the rates are a = 0.4028, b = 0.7593, so the marginal imbalance is large — which is exactly the D1 lesson: a marginal difference is not pairing structure, and the dependence finding lives in the CONDITIONAL pattern, not the margin. | TRIED (A2/A2b/N1) — A: no excess (p = 0.836). B (N1, 2026-10-31): EXCESS, z = +17.28, p = 0.000, d-loop re-derived exactly; low-frequency Bohr set, consistent with burstiness. W: excluded under uniform null, no excess under OR null (z = −3.81, p = 1.000). The dependence (E-W1) and the AP nulls are consistent: dependence is conditional/joint, AP density is marginal-structural, and the two measure different things — and the structure lives in B's timing plus the joint pattern, not in A alone. |
| E-W2 Regime-varying association (+0.29 → +0.08 → +0.49 → +0.09) | VOID — Regimes are time windows, not vectors. A discrepancy across windows would need a signed quantity per window, and none is pinned. | DESIGN — Object: the same A sequence, windowed by regime. Measurement: AP density per regime window vs the OR/uniform nulls within that window. Decision: whether progression structure tracks the regime-varying association. Unrun: regime boundaries must be pinned from the association analysis before counting; window-shopping across regimes is forbidden by the A2 protocol's fixed-window rule. |
| E-W3 Q-table growth (46→507, size ≠ learning) | VOID — A scalar time series (table size). No ensemble, no set of positions. The confirmed non-proxy verdict already closes the naive reading. | VOID — "Growth events" (ticks where the table grows) are a set with positions in principle, but the event definition (a new entry at a tick) is not on record as a stored field, and the growth is driven by observer state, not emission structure. Pinning would need the observer log's entry-creation field identified first; until then, VOID, not DESIGN. |
| E-W4 Diet battery null (no lens beats control) | VOID — Lenses are sieves, not sign ensembles. Komlós has nothing to sign. | CONTRAST + DESIGN principle (X1) — The diet battery IS a sieve, and M2's form (a sieve reveals only structure at its own frequencies) is the design principle for reading it: state the sieve's frequencies before reading the null. The AP count and the diet battery are complementary sieves: APs count progression structure the lenses do not see, and the lenses see observer structure APs do not. Neither replaces the other. |
| E-W5 Cube contention (busy-tone ~half, propagation null) | VOID — Contention is a rate, not a sign pattern. No vectors on record. | VOID — Cube rounds have an index (round number), but the busy-tone sequence is a contention signal, not an emission set; APs in busy-tone positions would measure contention scheduling, and no decision about the wire's timing structure would flip on it. The propagation null already settles the cube's question. |

### SpudCell / mirror-life events

| Event | M1 Komlós | M2 Kelley–Meka |
|---|---|---|
| E-S1 Enumerable dependence (feeders, ribosomes, waste, plasmid loss) | VOID — No ensemble of sign patterns in any SpudCell data on record. The dependence is enumerability (a parts list), not a signed sum. The preprint full text has not been read; no vector object exists. | VOID — No sequence. Generational plasmid-loss figures (~30% after five generations, secondary) are two scalars, not a set with positions. |
| E-S2 Engineered selection under scarcity | VOID — Selection here is a hand-introduced variant outcompeting an original over five generations (pairing P-01's breaking contrast: no quiet donor). No sign choice, no ensemble. | VOID, formerly ANALOGY (A3, repaired) — The sifting parallel (selection as sieve) stays an analogy: no set, no sieve, no forced pattern namable in SpudCell's terms without the preprint's generation-resolved counts. The sweep counter-poles (E-S6) do not change this: they are programmes, not data. |
| E-S3 No spontaneous mutation | VOID — A zero (no random errors reported) is not an ensemble. | VOID — The mutation-rate dial (E-S6: W-03 ~3% random mutation; W-05 100,000-fold engineered rate) is the opposite pole, but neither pole supplies a sequence of positions for AP counting. The dial is a parameter, not a set. |
| E-S4 Chirality dependence (hypothetical) | VOID — Hypothetical; no data, no ensemble. | VOID — No handedness measurement exists on record (gap G1). A CPL assay, if built, would produce handedness classes, not an indexed sequence. |
| E-S5 CPL contingency proposal | VOID — A proposal, not data. | CONTRAST (X3) — The tiered-reporting rule for a future CPL assay is M1-adjacent in form (report by tier, never pooled — the E-F1 lesson), not an M2 application. No AP content. The assay does not exist. |
| E-S6 Sweep counter-poles (W-03, W-05) | VOID — Programmes/poles, not ensembles. | VOID — Same as E-S3: parameters and programmes, no position sets. |

### Other subjects on record

| Subject | M1 Komlós | M2 Kelley–Meka |
|---|---|---|
| Breeding stud-line / pairings (TH-208, P-01) | ANALOGY only — "Balance" across crosses (quiet donor: mother's structure leads, father's vigor underneath) is a balance intuition, not a signed sum. No vectors, no bound, no decision flips. The pairing map's breaking contrast (P-01) already says this. | VOID — No sequence. Generations are few (F1, backcrosses) and ordered by breeding decision, not by a natural index; APs in cross positions are meaningless. |
| Markov hardening gap (G3) | DESIGN — Object: hardening as a signed update ensemble (each firing/repetition votes the table toward/away from a pattern). Measurement: discrepancy of the update ensemble vs a hardening rule. Decision: which hardening rule (repetition? reward? firing count?) the table obeys. Unrun: no hardening rule exists on record, so the vectors cannot be pinned yet. This is the most consequential DESIGN cell: it is perg's own open question (Adam Coger conversation), and Komlós is the theorem whose form matches it — IF the updates can be written as vectors. | VOID — A Markov table's states are not integers with AP structure; transitions are the object, not positions. |
| Fold-first claim (S5, perg's, UNTESTED) | VOID — A claim about origin (light mutating protein, folding as the system-building event). No ensemble, no measurement on record. | VOID — No sequence, no set. The claim is unpinned in every respect (object/measurement/decision all absent). Neither theorem touches it as stated. |
| Media-influence theory (MI, perg's, since high school) | VOID — Overt repetition + seasonal curation steering behaviour; illusory-truth mechanism. No signed ensemble on record; the theory's own test (T-MI-001) is unlaunched. A Komlós reading (repetition as signing?) would be metaphor, and the map does not do metaphor as transfer. | VOID — Repetition schedules have an index (calendar), but no set of positions with a decision attached has been pinned; the seasonal-curation claim needs its own measurement design first. |
| Plant listening / EIT rig (research goal, PINNED, rig deferred) | CONTRAST — The rig's future traces will be time series with a measurement chain (EIT mesh + Cheeger already applied). Komlós would need a sign ensemble over channels/traces; none exists until first traces. The Cheeger calibration (C-0) is the standing example of a bound that applies. | DESIGN — Object: plant electrical-signal traces (future). Measurement: AP density in spike/event positions vs a generative null matched to the trace's construction. Decision: whether event timing carries progression structure the spectral analysis does not see. Unrun: no traces exist; rig deferred pending funding. This is the only DESIGN cell for M2 outside the wire, and it waits on funding, not on analysis. |

## §4 What the trials changed, cell by cell

- **A1 (Komlós × fleet)** changed the M1 column's E-F2/E-F3 cells from
  DESIGN to TRIED-with-limits, and taught the D1 degeneracy lesson that
  now governs every M1 DESIGN cell: the statistic must vary under its
  null, checked by SD before any p-value is read.
- **A2/A2b (Kelley–Meka × wire)** changed the M2 column's E-W1 cell from
  DESIGN to TRIED, and taught the OR-null lesson that now governs every
  M2 DESIGN cell: the null must match the sequence's construction, and
  the density cap is a property of the null, not of the sequence alone.
- **Neither trial changed any SpudCell, breeding, Markov, fold-first, or
  media cell.** Those cells were VOID/DESIGN before the trials and remain
  so; the trials supplied no object, measurement, or decision for them.
  The map does not let a wire result leak into a SpudCell cell.
- **Staleness corrected:** the application file's §8 verdict bullet T2
  ("Kelley–Meka produced a negative pinning finding… blocked") described
  the trial BEFORE the data model was pinned. It is superseded by the
  Trial 2 / 2b paragraphs in the same file and is marked superseded there.
  This map uses the ran results, not the stale bullet.

## §5 Shared lessons (both theorems, from the trials)

1. **The null must match the construction.** M1: D1's null was degenerate
   because shuffling preserves the marginals D1 is made of. M2: the
   uniform null was wrong because the sequence is built by OR. In both
   cases the first null answered a different question than the one asked,
   and the check that caught it was structural (SD = 0; density +
   construction), not statistical.
2. **Diagnostic ≠ theorem, in the same way both times.** Each theorem's
   conclusion is a CONSTRUCTION (a signing; a Bohr set + density
   increment). Each trial performed a MEASUREMENT (cells; a count).
   The measurement disciplines the question; it does not perform the
   construction. Any future claim of application must name the
   construction step and run it — for M1, exhibit the signing; for M2,
   exhibit the Bohr set and the increment.
3. **Meaning must be pinned before counting.** M1's sign choice must be
   free in the subject; M2's index must mean something and its frequency
   set must be stated before counting. The two VOID families in the
   matrix are exactly these two failures: no free signing (most M1
   cells) and no meaningful index (most M2 cells). The map's DESIGN
   cells are the ones where the pinning is writable; the VOID cells are
   the ones where it is not yet writable, and the difference is stated
   per cell rather than assumed.

## §6 Ranked next measurements (none launched)

Cheapest-first, each needing its own pre-registration before counting.
Nothing here runs without perg's word.

- **N1 — B sequence, same window/protocol as A2** — RAN 2026-10-31
  (perg's tap). Pre-registered protocol `wire-ap-b-protocol.md`, results
  `wire-ap-b-results.md`: density 0.7248 (in cap), observed 244,959,744
  APs vs null mean 237,993,541, z = +17.28, p = 0.000 — EXCESS AP
  density in B, re-derived exactly by the d-loop method. B's timing is
  not exchangeable (low-frequency Bohr set, consistent with burstiness);
  no Kelley–Meka construction, no drive naming. The E-W1 cell's M2
  entry is now TRIED on both sides: A null, B excess, wire below its
  OR null.
- **N2 — Replication on other shared-mode days** (cheap). Files:
  20261025 (b silent, a = 0.50 — a natural single-side control) and any
  other day passing the density/continuity rule. Same scripts. Decision:
  whether the A null and the OR-null deficit replicate across regimes.
  Cost: minutes. Regime boundaries (E-W2) must be pinned first if
  windows are regime-split; whole-file windows need no regime pinning.
- **N3 — Komlós-on-SAT pinning** (read-only). Inspect solver code
  (`sat-solver-v*.py`) for a writable branching-vector object; write the
  pinning (object/measurement/decision) WITHOUT running the solver.
  Decision: whether a Komlós trial on solver branching is writable at
  all. Cost: an inspection, no compute.
- **N4 — OR-null on other days** (cheap, after N2). Same as N2 with the
  OR null. Decision: whether the joint-timing deficit (z = −3.81) is a
  one-window artifact or a regime property.
- **N5 — SpudCell cells after the preprint is read** (blocked on
  reading). If the preprint supplies generation-resolved counts or
  sequences, re-pin E-S1/E-S2 cells; until then they stay VOID. The
  preprint has NOT been read; no cell changes on secondary reporting.
- **N6 — Judge-specific Komlós run** (DESIGN, needs pinning). Object:
  swap-pair verdict patterns (25/42 agreement). Measurement: discrepancy
  of the judge's sign pattern across presentations vs a marginal null.
  Decision: whether position bias is a marginal artifact or structured
  disagreement. Unrun: the pairing of swap items to a vector object is
  not yet written.

## §7 Verdict summary (assistant's, labeled)

The initial map is complete in the sense perg asked: every subject event
on record has been compared against both theorems, in every way the
record allows. The comparison's shape is stark: **2 TRIED legs for M1
(one population informative, one population's structure found in the
opposite direction) and 3 TRIED legs for M2 (A null, W null under the
right null, W excluded under the wrong one) — and everywhere else VOID,
CONTRAST, ANALOGY, or DESIGN.** No theorem applies in its own form
anywhere yet. The two diagnostics that DO apply (four-cell discrepancy;
AP density against a construction-matched null) are now pinned,
validated, and reusable — which is what "initial map" means here: not a
conclusion, but a complete statement of what has been tried, what is
writable, and what is not yet writable, with the next measurements
ranked and none launched.
