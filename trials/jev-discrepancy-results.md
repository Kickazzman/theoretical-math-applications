# Komlos discrepancy trial (A1) — results

Protocol: `jev-discrepancy-protocol.md`, sha256 `031fdeddd14cb805f6ad198aec9a691a4e9cc5bfd5cf84c49f6db7abf8bafd69`. Computed 2026-10-31 under that protocol. Source files unmodified.

| Population | N total | Included | Excluded (null) | Both right | Fast-only | Slow-only | Both wrong | D1 (marginal) | Fast err | Slow err | Slow-only null mean | Slow-only null SD | p (slow-only ≤ obs) | Disagree K | K null mean | K null SD | K p (2-sided) | sqrt(N) | (ln N)^(1/4) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P-contract | 50 | 32 | 18 | 15 | 13 | 0 | 4 | 13 | 0.125 | 0.531 | 1.87 | 0.95 | 0.0684 | 13 | 16.75 | 1.90 | 0.1074 | 5.66 | 1.364 |
| P-hard | 40 | 14 | 26 | 8 | 6 | 0 | 0 | 6 | 0.000 | 0.429 | 0.00 | 0.00 | 1.0000 | 6 | 6.00 | 0.00 | 1.0000 | 3.74 | 1.275 |
| P-lag | 100 | 51 | 49 | 29 | 22 | 0 | 0 | 22 | 0.000 | 0.431 | 0.00 | 0.00 | 1.0000 | 22 | 22.00 | 0.00 | 1.0000 | 7.14 | 1.408 |
| P-realdiff | 28 | 28 | 0 | 18 | 2 | 3 | 5 | -1 | 0.286 | 0.250 | 6.00 | 1.06 | 0.0096 | 5 | 10.99 | 2.13 | 0.0096 | 5.29 | 1.351 |

## Reading (per the protocol as amended by Amendment A)
- D1 is a MARGINAL imbalance (fast correct count minus slow correct count). It is pairing-invariant under label shuffling, so it has NO permutation null and NO p-value. The first run's D1 null (SD 0.00, p 1.0000) was degenerate and is VOID; it is recorded in the protocol amendment, not here as a result.
- Structure lives in the slow-only count. p (slow-only ≤ obs) < 0.05 means the slow seat is solely right less often than chance pairing would give — disagreement structurally favours the fast seat. That is a finding about the ensemble, not about Komlos.
- Theorem-application verdict (pre-registered, both cases): the discrepancy DIAGNOSTIC applies; the Komlos bound in its own form does not, because its free sign-choice structure has no subject meaning here — the observed signing is fixed by which seat was right. The (ln N)^(1/4) column is a scale comparison only; no verdict on the theorem follows from it.
- Correction carried from the protocol: the application file's '280 JEV + 56 real-diff' pairable count was wrong (lag file overlaps contract/hard by 40 prompt_refs each; null-sensor rows are single-seat). Populations are reported separately above; no pooled total is claimed.
