# Other-days replication (N2) with the analytic yardstick — pre-registered protocol

Written 2026-10-31, BEFORE any N2 count. Ordered by perg's tap "Run
the other-days replication (N2) with the analytic yardstick"
(2026-10-31 15:45 EDT). Data model: `wire-tick-data-map.md` (CORRECTED
here: bit-shared files rotate at ~50 MB every ~3 hours; the T000000Z
files are the midnight chunks of a continuous log, not whole days).
Counting code: `wire-ap-count.py` (FFT method, validated as in A2).
Analytic yardstick: R-ANA (`theoretical-equations-and-rederivations.md`
§5): E = P·k(k−1)(k−2)/(N(N−1)(N−2)), P = 624,975,000 for N = 50,000.

## Population (enumerated before counting)

Every `T000000Z.jsonl` chunk in `runs/bit-shared/` larger than 1 MB,
EXCEPT `20261007T000000Z.jsonl` (already trialed in A2/N1/A2b/block/
N8/N9/N10). Enumerated 2026-10-31 by read-only directory listing (23
files):

20261005, 20261008, 20261009, 20261010, 20261011, 20261012, 20261013,
20261014, 20261015, 20261016, 20261017, 20261018, 20261019, 20261020,
20261021, 20261022, 20261023, 20261024, 20261025, 20261028, 20261029,
20261030, 20261031 (all `T000000Z.jsonl`).

No T000000Z chunk exists for Oct 6, 26, or 27; those days are absent
by the enumeration rule, not by selection. No other chunk of any day
is included — one window per day, the midnight chunk, fixed before
counting. Window per file: the FIRST 50,000 consecutive tick rows.
Sequences: A (`a`) and B (`b`) only; W is N4's subject, not N2's.
If a file's first 50,000 tick rows are not consecutive (script
assertion), that file/sequence is recorded as EXCLUDED with the
assertion failure stated — never silently skipped, never replaced
with a later window.

## Measurement (fixed before counting)

Per file × sequence: observed AP count (FFT), 100 uniform-permutation
shuffles (seed 20261031), null mean/SD, p = fraction of nulls ≥
observed, density, tick range. Density cap (same rule as A2): a
file/sequence whose window density falls outside (0.2, 0.8) is
EXCLUDED — reported for completeness, not claimed.

Analytic yardstick (computed AFTER counting, from the recorded
density only — no new data): k = round(density × 50,000); E from the
R-ANA formula. Yardstick check, fixed before counting: |E − null
mean| ≤ 2 × SE, where SE = null SD / √100. If the check FAILS on a
file/sequence, the yardstick is reported as FAILED there (the
shuffle p-value still stands on its own; the failure is about the
formula, not the count). If it passes everywhere, the yardstick is
validated on 23 new windows and may be used without shuffles in
future replications — stated as a conditional, not assumed.

## Decision rules (fixed before counting)

- Per file/sequence (in-cap only): p < 0.05 → excess AP density in
  that window; p ≥ 0.05 → no excess detected in that window.
- Replication question (stated before counting): does Oct 7's pattern
  (A null, B excess) replicate? Replication = B excess in a majority
  of in-cap B windows AND A null in a majority of in-cap A windows.
  Anything else is reported as partial/no replication, with the
  per-file table as the evidence. No pooling across files: each
  window is its own sequence (tick counters reset per process run;
  files are separate runs/chunks).
- Theorem-application verdict (pre-registered, all cases): diagnostic
  only; no Kelley–Meka construction; no drive naming. No verdict on
  the theorem follows from any leg of this replication.

## Outputs

One results file with the per-file × sequence table (density,
observed, analytic E, null mean/SD, p, cap status, yardstick check),
the replication verdict, and the verdicts above. Source files never
modified. The protocol's hash is recorded in the results file.
Per-file JSONs are saved locally as `wire-ap-n2-<date>-<seq>.json`.
