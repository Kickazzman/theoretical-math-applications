# AP-density trial, finer segment-preserving null for B (N10) — results

Protocol: `wire-ap-segnull50-protocol.md`, sha256
`2cc1a44dfee8d0b4e3e0f786381ce27bab92fe11047c8135aba366d5ad1a0061`
(pre-registered 2026-10-31, before any N10 count). Data model:
`wire-tick-data-map.md`. Counting: `wire-ap-segnull-count.py`
(--segments 50; FFT method, validated as in N9, plus a synthetic run
at 50 segments before the trial run). Read-only over the source file
on mrfloppy; nothing was modified there. Run: first 50,000 consecutive
tick rows of `runs/bit-shared/20261007T000000Z.jsonl`, ticks
2,441,528–2,491,527, sequence B, 50 segments × 1,000 ticks, 500
within-segment shuffles, seed 20261031. Full JSON:
`wire-ap-segnull50-results.json`. Stderr was empty; the preservation
assertion passed on all 500 shuffles.

| Quantity | Value |
|---|---|
| Observed APs | 244,959,744 (reproduces N1 exactly — built-in check passed) |
| Null mean / SD / range | 244,930,836 / 15,975 / 244,882,181–244,985,766 |
| Observed − null mean | +28,908 (+0.012%) |
| Observed − null max | −26,022 (observed sits INSIDE the null range) |
| z | +1.81 |
| p (null ≥ observed) | 0.036 (18 of 500 nulls) |
| Gap closed vs uniform null | 99.585% |

## Reading — rule verdict AND fragility, both reported

Per the pre-registered decision rule, p = 0.036 < 0.05: excess persists
at 1000-tick profiling. That verdict is recorded. But the rule verdict
is not the whole reading, and the magnitudes are reported alongside
it rather than behind it:

- The residual is +28,908 on 244,959,744 — 0.012%. The density
  profile at 1000-tick granularity closes 99.585% of the uniform-null
  gap.
- The observed count sits INSIDE the null range (26,022 below the
  highest null). The p-value is fragile: 18 of 500 nulls beat the
  observed count, and a different seed (robustness check N7,
  unlaunched) could plausibly move p across 0.05. No second seed was
  run in this trial.
- The z-series across null families: uniform +17.28 → L=100 +9.50 →
  L=1000 +3.68 → 5000-tick segments +3.40 → 1000-tick segments +1.81.
  No trend is fitted; the series is the finding: each more faithful
  null absorbs more, and the residual is now at the noise floor of
  its null family.

Conclusion, labeled: whether B carries progression structure beyond
its 1000-tick density profile is UNDECIDED at this resolution. The
measurement has reached the point where the residual (0.012%) is
smaller than the null family's own spread, and the p-value no longer
separates "real" from "profiling artifact". Per the protocol, the
next step is NOT automatically still finer profiling — that regress
absorbs more by construction. The next step, if any, is a different
question (within-segment arrangement structure), needing its own
design.

## Density profile at 1000-tick granularity

Segment densities (full list in the JSON): segments 0–10 (ticks
2,441,528–2,452,527) at 0.578–0.647; segments 11–49 at 0.726–0.802.
The step refines to the segment 10/11 boundary, ~11,000 ticks into
the window (segment 10 itself at 0.647, intermediate). Range across
all 50 segments: 0.578–0.802.

Bohr frequency set (same rule as N1, reported verbatim):
[0, 1, 2, 3, 4, 7, 8, 2474] — identical to N1/N8/N9, as it must be for
the same window and sequence.

## Theorem-application verdict (pre-registered)

Diagnostic only; no Kelley–Meka construction; no drive naming. No
verdict on the theorem follows from this trial either way.
