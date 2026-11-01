# Theoretical equations for what we are doing — and getting back to the same answer multiple ways

Perg, 2026-10-31 15:21 EDT: continue mapping with all the theories we can
get our hands on, everything run and recorded, nothing held back, with the
theoretical equations for what we are doing, and try to get back to the
same answer multiple ways.

Scope, stated plainly (nothing held back): "all the theories" here means
the 7 theoretical-math events on record (M1–M7) plus the Cheeger
calibration case C-0 — the events this programme actually uses. The full
228-theory inventory (`theories-full-inventory.md`, TH-001–TH-228) is a
separate record; most of its entries are not theoretical-math events and
are NOT re-mapped here. That boundary is stated, not hidden: the
all-theories map (`all-theories-map.md`) covers M1–M7 + C-0 across every
subject event on record, including every VOID and exclusion.

Each equation below is stated in the form USED in this programme — the
diagnostic form, with the theorem's own conclusion kept separate. Where
the record does not give a formula, that is stated instead of inventing
one. Evidence-class guard (TH-054): pairing does not upgrade evidence
class; PREPRINT stays PREPRINT.

## C-0 — Cheeger bound on the EIT mesh (the calibration case: what "applies" looks like)

Theorem form (as used in the spectral test, protocol
`~/workspace/spectral-test/protocol.md`):

    |Γ| ≥ λ₂·|Ω| / 4

with λ₂ = 3.4155 (second eigenvalue of the FEM stiffness/mass problem on
the 289-node/528-element mesh) and |Ω| = π (unit-disk domain area).
Bound value: 3.4155 × π / 4 = 2.6827… ≈ 2.683 (as reported).
Measured interface: |Γ₂| = 8.122.
Check: 8.122 ≥ 2.683 holds; ratio 8.122 / 2.683 = 3.027… ≈ 3.03.
Re-derivation (§5, R-C0): the bound arithmetic was recomputed from the
recorded λ₂ and π — same 2.683, same ratio. The mesh computation itself
(the eigenvalue solve) was NOT re-run here; its provenance is the
spectral test's own code and report. What was re-derived is the
arithmetic from λ₂ to the verdict, by a second path.

## M1 — Komlós discrepancy (Bansal–Jiang; TH-122, PUBLISHED STOC)

Theorem form (scale as recorded):

    Given vectors v₁…v_N with ‖v_i‖₂ ≤ 1, there exist signs
    ε_i ∈ {+1, −1} with ‖ Σᵢ ε_i v_i ‖_∞ = O((log N)^{1/4}).

Diagnostic form used in trial A1 (the subject has no vectors to sign, so
the diagnostic, not the theorem, was run):

    Per included item: (fast right?, slow right?) ∈ {0,1}².
    Four cells: both-right, fast-only, slow-only, both-wrong.
    D1 = fast-only − slow-only = F − S,
    where F = # fast correct, S = # slow correct.

Pairing-invariance (derived, and the reason the first null was void):

    fast-only = F − both-right;  slow-only = S − both-right;
    D1 = (F − both-right) − (S − both-right) = F − S.
    Any relabelling that preserves F and S leaves D1 unchanged, so D1
    has no permutation null. Structure lives in the slow-only count,
    tested against permutation of the slow labels (5,000 shuffles).

Scale column (descriptive only, no verdict follows from it):

    √N and (ln N)^{1/4} (natural log), reported beside D1 for scale
    comparison. The (ln N)^{1/4} column does NOT import the theorem:
    the theorem's free sign choice has no subject meaning here (the
    signing is fixed by which seat was right).

## M2 — Kelley–Meka sifting (TH-126, LITERATURE)

Theorem form (as recorded): a dense set of integers, sifted through Bohr
sets, yields a large structured subset / density increment, forcing
3-term arithmetic progressions. The theorem's conclusion is a
CONSTRUCTION (Bohr set + increment). No construction was performed in
any trial here.

Diagnostic form used in trials A2/A2b/N1 (AP density):

    S = { positions t in the window : bit_t = 1 }.
    N₃(S) = #{ (x, d) : d ≥ 1, x, x+d, x+2d ∈ S }.
    Nulls (generative, matched to construction):
      (i)   uniform permutation of the window's bits (single sequence);
      (ii)  independent permutations of a and b, ORed (OR-built wire);
      (iii) block permutation, blocks of 100 ticks (burstiness test, §5).

Fourier identity used for counting (validated, §5):

    Let F = DFT of the indicator of S, embedded in Z_M with M > 2N
    (next power of two). Then
      (1/M) · Σⱼ F(j)² · F(−2j)  =  2·N₃(S) + |S|,
    so  N₃(S) = ( raw − |S| ) / 2.
    The factor 2: each progression is counted in both directions;
    d = 0 triples (x, x, x) are counted once each.
    Validated 60/60 against the direct d-loop on synthetic arrays, and
    exact on real windows (A pilot 394,514; B observed 244,959,744 by
    both methods).

Bohr-set rule (stated before counting in every protocol): the 8
frequencies with the largest |Fourier| magnitudes of the observed
window's indicator, computed once, reported verbatim, never changed
after seeing counts. The frequency set is a reporting discipline, not
a construction: no Bohr-set sifting step was run.

Density rule: a sequence whose window density falls outside (0.2, 0.8)
is excluded under the uniform null (A2 wire leg). The cap is waived
only for the construction-matched OR null (A2b), stated before
counting, because that null preserves the OR mechanism.

## M3 — Kakeya in three dimensions (Wang–Zahl; TH-140, PREPRINT)

Theorem form (as recorded):

    dim_H(K) = 3   for Kakeya sets K ⊂ ℝ³
    (a set containing a unit segment in every direction has full
    Hausdorff dimension; directional coverage cannot be compressed).

Diagnostic form used (attempt A4, DESIGN, unrun): a directional-coverage
audit — enumerate the phase-offset / timescale directions each diet
lens is sensitive to, and state which direction families are uncovered.
No equation is computed; the theorem supplies the READING (a null may
be a coverage statement), not a number. Kakeya is explicitly NOT an
irrational-anchor result by metaphor, and no Kakeya computation on wire
data exists. The one reconstructed Wang–Zahl URL in the theoretical-math
report is DISREGARDED (see that report's correction note).

## M4 — Nonuniform Schauder, conditional sharp regularity (De Filippis–Mingione; TH-143)

Theorem form (schema as recorded — no constants claimed beyond the
record): regularity of solutions holds CONDITIONALLY and SHARPLY — only
under stated conditions on the coefficients, and the conditions are the
content. In schema:

    Conditions C hold  ⇒  regularity R holds (with sharp exponents);
    C unstated or violated  ⇒  no regularity claim follows.

Diagnostic form used (attempt A5, DESIGN, unrun): replace quoted
constants with conditional statements + sharp thresholds —
(a) SpudCell persistence vs supply dose-response, threshold = dose at
which persistence first fails; (b) wire dependence (MI) by pre-pinned
regime, not by windows chosen after seeing the variation. No Schauder
computation exists in this programme; M4 was NOT applied to EIT (the
EIT lane states its own prior/λ/mesh conditions).

## M5 — Badly approximable sampling / Poissonian rotation (Hauke; TH-123)

Theorem form (definitions as standard):

    α is badly approximable if ∃c > 0 : |α − p/q| ≥ c/q² for all p/q.
    The rotation {n·α mod 1} is then explicit Poissonian: its pair
    correlations match the Poisson (random) pattern at fine scales.

Diagnostic form used (attempt A6, DESIGN, unrun): two-phase comparison
on the same saved ticks — structure detection (MI, AP density) at
rational sampling phases vs badly approximable phases (e.g. golden-ratio
phase), phase set pre-registered. If badly approximable phases reveal
structure rational phases miss, phase choice is load-bearing; else it is
decorative. No phase computation exists in this programme. M5 is NOT
applied to SpudCell (no phase object) — exclusion recorded in the
application file §5.

## M6 — Guth–Maynard critical-parameter METHOD (TH-127, PUBLISHED Annals)

No theorem equation is claimed. The METHOD, as recorded:

    When a worst-case bound is stuck, improve the bound at the single
    critical parameter regime κ* rather than uniformly.

Diagnostic form used (attempt A7): the Stage 3 firming shape — pooling
at n = 236 (47/100) is the weak lever; firming at n = 237/238 is the
shape that can firm, conditional on the higher-cell rate. The method
was already the shape of that reasoning before M6 was named; naming it
does not upgrade the unrun firming result. SpudCell leg (DESIGN):
measure variant share AT the scarcity threshold, not uniformly across
supply levels. Methods do not become theorems by being named.

## M7 — Diagonal Ramsey numbers (Campos et al.; TH-129)

Theorem form (bound as recorded):

    R(k) ≤ (4 − ε)^k    for diagonal Ramsey numbers, some fixed ε > 0.

Diagnostic form used (attempt A8, ANALOGY with pinned measurement):
cluster-size distribution in the cube contention graph against the R(k)
SCALE — below the scale, independence is possible in principle; above
it, forced clusters must be handled by design. R(k) is a SCALE, NOT a
safety guarantee (the TH-129 warning is carried in full). The
contention graph is unbuilt; Cube Phase 2 is queued, not launched. M7
is NOT applied to mirror life (no channel graph) — exclusion recorded.

## §5 Re-derivations — getting back to the same answer multiple ways

Every re-derivation below was run for this file (2026-10-31) and is
recorded with its outcome, including the ones that only confirm
arithmetic. "Second way" means a different code path / different
null / different arithmetic route — never the same script re-run.

- **R-C0 Cheeger arithmetic.** Route 2: λ₂ × π / 4 from the recorded
  λ₂ = 3.4155 → 2.6827 ≈ 2.683 (matches the spectral report's bound);
  8.122 / 2.683 = 3.027 ≈ 3.03 (matches). PASS. Limit: the eigenvalue
  solve itself was not re-run.
- **R-A1 JEV recount (independent code).** Route 2: a fresh script
  (`jev-recount.py`) recounting the four cells from the source files
  with different logic (Counter over decision pairs; real-diff paired
  by decision_id through a separate dict build). Result: all four
  populations' cells match `jev-discrepancy-results.json` exactly
  (contract 15/13/0/4; hard 8/6/0/0; lag 29/22/0/0; real-diff 18/2/3/5).
  PASS. The slow-only permutation p-values were NOT re-derived with a
  second seed in this pass; the recorded p-values stand on the single
  pre-registered run (seed 20261031), and that limit is stated here.
- **R-A2 AP observed recounts (loop method).** Route 2: the d-loop
  counter on the same 50,000-tick window. A observed: loop count =
  40,053,253 (matches FFT). W observed: loop count = 358,986,556
  (matches FFT). B observed was already re-derived in N1 (244,959,744
  by both methods). PASS on all three sequences. Null distributions
  were not re-derived by the loop method (cost); only observed counts.
- **R-B Block-null trial (second null family).** Pre-registered protocol
  `wire-ap-blocknull-protocol.md` (written before counting): permute
  100-tick blocks of B's window (500 blocks, order shuffled, within-
  block order preserved), 200 shuffles, seed 20261031, same window.
  Question: does B's AP excess survive a null that preserves
  ≤100-tick burst structure? Result: RAN 2026-10-31 (200 shuffles,
  seed 20261031): observed 244,959,744 (reproduces N1 exactly) vs
  block-null mean 238,055,822, z = +9.50, p = 0.000 — excess PERSISTS
  beyond 100-tick blocks (`wire-ap-blocknull-results.md`). Burstiness
  at ≤100 ticks does NOT explain N1's result.
- **R-N8 L=1000 block null + drift check.** Pre-registered protocol
  `wire-ap-block1000-protocol.md`. Results RAN 2026-10-31:
  L=1000 null (50 blocks, 200 shuffles): observed 244,959,744 vs null
  mean 238,284,375, z = +3.68, p = 0.000 — excess persists but weaker
  (z-decline 17.28 → 9.50 → 3.68 across null families). Drift check
  (10 × 5,000-tick segments): density range 0.166, a STEP at ~tick
  10,000 (0.60 → ~0.75); cross-segment APs 90.1% of the count;
  decomposition identity holds exactly. Reading: drift-compatible;
  beyond-the-step structure undecided (follow-up N9,
  segment-preserving null, unlaunched). Script metadata bug owned:
  the block-count JSON `null` string was hardcoded "100-tick blocks"
  in the L=1000 run; `block: 1000`/`nblocks: 50` fields were correct
  and the script is fixed.
- **R-N9 Segment-preserving null.** Pre-registered protocol
  `wire-ap-segnull-protocol.md`. Results RAN 2026-10-31 (500
  within-segment shuffles): observed 244,959,744 vs null mean
  244,692,592, z = +3.40, p = 0.000 — excess persists, residual
  +267,152 (+0.11%); the step profile closes 96.2% of the
  uniform-null gap. Source undecided: within-segment structure vs
  finer sub-segment drift (follow-up N10, finer segments,
  unlaunched).
- **R-ANA Analytic expectation vs Monte Carlo null means (third way).**
  For a uniform random k-subset of {0,…,N−1}, the expected AP count is
  exact combinatorics: E = P · k(k−1)(k−2) / (N(N−1)(N−2)), where
  P = Σ_d (N−2d) = 624,975,000 for N = 50,000. Checked 2026-10-31
  against the recorded 500-shuffle uniform-null means: A (k = 20,031):
  analytic 40,181,074 vs null mean 40,173,775 (+0.018%, 1.3 SE); B
  (k = 36,241): 237,981,533 vs 237,993,541 (−0.005%, 0.7 SE); W
  (k = 41,297): 352,129,696 vs 352,148,973 (−0.006%, 1.0 SE). All
  three agree within ~1.3 standard errors of the Monte Carlo mean.
  The counting, the permutation nulls, and the closed-form scaling
  (N²p³/4 approximation within 0.03% on all three) give the same
  answers three ways. Practical consequence: for any new window, the
  uniform-null expectation follows from N and k alone — a yardstick
  for replication (N2) without running 500 shuffles first.
- **R-N2 Yardstick validation on 23 new windows (N2, RAN 2026-10-31).**
  46 legs (23 midnight chunks × A/B, 100 shuffles each): yardstick
  passes the pre-registered ≤2 SE check on 17 of 18 in-cap legs; the
  one failure (20261013-a, 2.26 SE) is marginal and the largest
  relative deviation is 0.054%. Replication verdict PARTIAL (B excess
  3/4 in-cap; A null 7/14, not a majority). Regime finding: 28/46
  legs cap-excluded — saturated days (a≈0.99, b=1.0), peer-silent
  days (b=0.0), informative days. Anomalies: 20261016-b +207%
  (z=+561.65, in-cap); 20261028-b +1,062% (cap-excluded, not
  claimed); deficit windows to −5.52% (z=−21.20). The uniform null
  fails in both directions across the month: the diagnostic detects
  regime, not a stable wire property.
- **R-C1 Theory–observation correlation (RAN 2026-10-31, recorded
  numbers only).** Residual ratio r = (observed − E)/E across 19
  in-cap legs: vs density Pearson +0.072 (p = 0.780), vs day −0.353
  (p = 0.134), vs |r| +0.281 (p = 0.248); regime means differ by
  +0.97pp (p = 0.612). No tracking detected by the pre-registered
  rule. Sensitivity (Oct 16-b included) flips the density
  correlation to −0.385 — one leg moves Pearson by 0.46. Vacuous
  observed-vs-E Pearson 0.999, labeled. The analytic theory is
  unbiased across density, day, and regime at this resolution; the
  misses are idiosyncratic. Thought events (JEV) correlate with
  theory only in verdict pattern (diagnostic yes, theorem no) — no
  shared numeric scale, no number forced.
- **R-N10 Finer segment-preserving null (50 × 1000 ticks).**
  Pre-registered protocol `wire-ap-segnull50-protocol.md`. Results
  RAN 2026-10-31 (500 shuffles): observed 244,959,744 vs null mean
  244,930,836, z = +1.81, p = 0.036 — rule verdict "persists" but
  FRAGILE: residual +28,908 (+0.012%), observed inside the null
  range (26,022 below null max), gap closed 99.585%. Beyond-profile
  structure UNDECIDED at this resolution; the regress stops here by
  design. Step refined to the 1000-tick segment 10/11 boundary
  (~11,000 ticks in). Seed robustness (N7) unlaunched and now the
  most relevant follow-up.
- **R-V01 Threshold sweep (RAN 2026-10-31, three ways, exact
  agreement).** Pre-registered protocol
  `v01-threshold-sweep-protocol.md`. Saved JEV + real-diff rows,
  included only (32/14/51/28, reproducing Trial 1): no threshold in
  0.50–1.00 dominates 0.8 in any population — REFUTED. Mechanism:
  fast confidences take only {0.95, 0.99, 1.0} (JEV) and {0.9, 0.95}
  (real-diff), so escalation is 0.0 for every T in 0.50–0.95 and the
  0.8 confidence leg never fires on an included row. Way 1 (direct)
  and Way 2 (cell aggregation) agree exactly on all 44 grid cells;
  Way 3 (sorted step function) confirms the flatness mechanism.
  Open follow-up: why fast confidence never dips below 0.9 here.
- **R-COUNT Arithmetic identities.** D1 = F − S verified algebraically
  in §M1 above (not a computation). AP Fourier identity verified
  60/60 synthetic + 3/3 real windows. No other identity in this file
  was independently re-derived; none is claimed beyond what is shown.

## §6 What was NOT re-derived, and why (nothing held back)

- The spectral-test eigenvalue solve (λ₂ = 3.4155) — not re-run; CPU
  FEM solve owned by its own report. Only its arithmetic was checked.
- The E-W1 dependence numbers (+0.2846, MI 0.0553) — not recomputed;
  they live in wire analyses on mrfloppy and no second implementation
  exists in this programme. They are carried as recorded, not verified
  here.
- The SAT wall brackets — not re-run; solver runs are gated on perg's
  Stage 3/4 decisions. The firming numbers (47/100 at n = 236) are
  carried as recorded.
- The SpudCell figures — not re-derived; secondary reporting, preprint
  unread. Every SpudCell cell in the all-theories map stays VOID or
  DESIGN for this reason, and the map says so per cell.
- No second seed was run for any permutation p-value in this pass.
  P-values stand on their pre-registered runs. A seed-robustness pass
  is a defined follow-up, not done here, and is listed as such in the
  all-theories map (N7).
