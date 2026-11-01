# Theory–observation correlation analysis (C1) — pre-registered protocol

Written 2026-10-31, BEFORE any correlation is computed. Ordered by
perg: "use the exact theory we used to get the equations we did and
apply the coloration like using thought or observational events to
theoretical math then seeing how they correlation" (2026-10-31 16:01
EDT), taken as: take the exact theory (the R-ANA analytic expectation
E = P·k(k−1)(k−2)/(N(N−1)(N−2))), apply it to the observational
events (the wire windows) and the thought events (the JEV
populations, via the comparison map), and measure how theory and
observation correlate.

## The trap, stated before computing

Correlating observed AP counts with E directly is VACUOUS: both scale
as k³, so the correlation will be ~1 by construction and proves
nothing. That check is computed and labeled vacuous, not reported as
a finding. The real correlation question is about the theory's MISS:
the residual ratio r = (observed − E)/E. Does the miss track
anything — density, day, regime? That is what is measured here.

The thought events (JEV populations) have no shared numeric scale
with the wire windows (disagreement counts vs AP counts), so no
numeric theory–observation correlation across the two programs is
meaningful. Their correlation with theory is the qualitative verdict
pattern already recorded in the comparison map (diagnostic applies,
theorem does not follow, in both programs). That stays qualitative;
no number is forced onto it here.

## Population (recorded numbers only — no new counting)

20 legs: the 18 in-cap N2 legs (`wire-ap-n2-summary.json`) plus the
Oct 7 A and B uniform-null legs (densities, observed counts, and
analytic E from R-ANA). Cap-excluded legs are not in the population
(their E is degenerate or out of the cap rule's scope — stated, not
hidden). Oct 16-b is a PRE-DECLARED anomaly (flagged in N2 before
this analysis existed): excluded from the PRIMARY analysis, included
in a separately reported SENSITIVITY analysis. Primary n = 19.

## Variables (fixed before computing)

- y = r = (observed − E)/E, the residual ratio.
- x1 = density p (window density).
- x2 = day index (Oct 5 = 0, Oct 7 = 2, Oct 8 = 3, …, Oct 29 = 24).
- x3 = |r| (deviation magnitude; secondary).
- Regime classes for A-legs: INFORMATIVE (both sides live: Oct 7, 8,
  9, 10) vs B-SILENT (Oct 11–15, 23–25, 29). Oct 16-a belongs to
  neither primary class (its B leg is the anomaly) and is excluded
  from the regime comparison; stated here, before computing.

## Statistics (fixed before computing)

Pearson r and Spearman ρ for (p, r), (day, r), (p, |r|), each with a
Fisher-z 95% CI (Pearson) and a two-sided permutation p-value
(10,000 shuffles, seed 20261031). Regime comparison: difference of
mean r between INFORMATIVE and B-SILENT A-legs, two-sided
permutation p (10,000 shuffles, same seed). Pure-python
implementation; no new data, no model fitting beyond these
correlations. Decision rule, fixed before computing: |r| > 0.5 AND
p < 0.05 → "the residual tracks that variable"; otherwise "no
linear tracking detected at this n". Correlation is not causation;
no theorem verdict follows from any result here. The sensitivity
analysis (Oct 16-b included, n = 20) is reported alongside, with the
same statistics, and any change between primary and sensitivity is
attributed to that one leg plainly.

## Outputs

Results file with the leg table (date, seq, p, r), the correlation
table, the regime comparison, the vacuous check, and the verdicts
above. The protocol's hash is recorded in the results file.
