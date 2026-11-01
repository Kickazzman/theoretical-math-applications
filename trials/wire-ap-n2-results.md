# Other-days replication (N2) with the analytic yardstick — results

Protocol: `wire-ap-n2-protocol.md`, sha256
`c39eda8e0b08f87879a455a3846176c5af4e3e095d26e41c5061924fcedf9a59`
(pre-registered 2026-10-31, before any N2 count). Counting: `wire-ap-count.py`
(FFT method), 100 uniform shuffles, seed 20261031, first 50,000
consecutive tick rows of each midnight chunk, sequences A and B. All
46 legs ran with exit 0; every window's tick span was exactly 49,999
(consecutive, asserted by the script). Per-leg JSONs:
`wire-ap-n2/<date>-<seq>.json`; combined table:
`wire-ap-n2-summary.json`. Source files never modified.

## Headline

Oct 7's pattern does NOT cleanly replicate — but not because the
other days are null. The other days are mostly in DIFFERENT REGIMES
from Oct 7, and within the windows that are comparable, the uniform
null is rejected in BOTH directions. Pre-registered replication
verdict: PARTIAL. B leg: excess in 3 of 4 in-cap windows (majority
✓). A leg: null in 7 of 14 in-cap windows — exactly half, NOT a
majority (✗). Full replication fails on the A leg by the
pre-registered rule, and the regime picture below is the more
important finding anyway.

## Regimes (density picture, all 46 legs)

- Saturated (a ≈ 0.99, b = 1.0): Oct 5, 17, 18, 19, 20, 30, 31
  (b = 1.0 exactly on Oct 5, 18, 19, 20, 30; 0.99998 on Oct 17, 31).
- Peer silent (b = 0.0 exactly): Oct 11, 12, 13, 14, 15, 21, 22, 23,
  24, 25, 29 (11 windows; a in-cap on Oct 11–15, 23–25, 29).
- Mixed/informative: Oct 8, 9, 10, 16, 28. Oct 28-b is nearly silent
  (density 0.0857, cap-excluded) and Oct 16-b is bursty (see below).

28 of 46 legs fall outside the (0.2, 0.8) density cap and are
EXCLUDED by the pre-registered rule — reported in the table, not
claimed. Only 4 B-windows and 14 A-windows are in-cap.

## Yardstick check (pre-registered: |E − null mean| ≤ 2 SE)

17 of 18 in-cap legs PASS. One marginal failure: 20261013-a,
2.26 SE — but the largest relative deviation of E from the null mean
across all 18 in-cap legs is 0.054%, and with 18 legs ~1 leg beyond
2 SE is expected by chance alone. Yardstick verdict: VALIDATED in
substance on 23 new windows (the strict rule fails once, marginally,
at a magnitude that changes nothing); the formula may be used as the
first-line expectation in future replications, with shuffles kept as
the check. The degenerate legs (density exactly 0 or 1) match E
exactly by construction and are not counted in the 17/18.

## In-cap results (full table; excess% = observed/analytic E − 1)

| Date | Seq | Density | Observed | Analytic E | Null mean | z | p (100) | Excess% |
|---|---|---|---|---|---|---|---|---|
| 20261008 | a | 0.4005 | 40,342,300 | 40,132,948 | 40,135,798 | +1.86 | 0.040 | +0.52 |
| 20261008 | b | 0.7111 | 220,729,465 | 224,721,225 | 224,765,677 | −11.03 | 1.000 | −1.78 |
| 20261009 | a | 0.3947 | 38,878,151 | 38,431,743 | 38,445,319 | +3.39 | 0.000 | +1.16 |
| 20261009 | b | 0.7713 | 295,471,527 | 286,719,573 | 286,717,289 | +20.83 | 0.000 | +3.05 |
| 20261010 | a | 0.4002 | 40,375,426 | 40,048,820 | 40,060,951 | +2.52 | 0.000 | +0.82 |
| 20261010 | b | 0.6962 | 211,603,469 | 210,925,063 | 210,875,830 | +2.18 | 0.020 | +0.32 |
| 20261011 | a | 0.5167 | 88,137,186 | 86,229,232 | 86,205,109 | +9.11 | 0.000 | +2.21 |
| 20261012 | a | 0.5006 | 78,427,129 | 78,389,362 | 78,373,261 | +0.28 | 0.330 | +0.05 |
| 20261013 | a | 0.5288 | 93,779,103 | 92,419,378 | 92,469,546 | +5.90 | 0.000 | +1.47 |
| 20261014 | a | 0.5416 | 93,785,779 | 99,261,384 | 99,274,510 | −21.20 | 1.000 | −5.52 |
| 20261015 | a | 0.4640 | 63,562,506 | 62,445,163 | 62,418,999 | +7.48 | 0.000 | +1.79 |
| 20261016 | a | 0.6744 | 190,728,832 | 191,657,345 | 191,676,145 | −2.42 | 0.980 | −0.48 |
| 20261016 | b | 0.3252 | 66,018,736 | 21,487,211 | 21,489,829 | +561.65 | 0.000 | +207.25 |
| 20261023 | a | 0.5385 | 92,843,914 | 97,599,103 | 97,603,906 | −18.46 | 1.000 | −4.87 |
| 20261024 | a | 0.5467 | 101,432,749 | 102,125,906 | 102,126,218 | −3.09 | 1.000 | −0.68 |
| 20261025 | a | 0.5308 | 94,892,807 | 93,461,415 | 93,469,021 | +7.01 | 0.000 | +1.53 |
| 20261028 | a | 0.5469 | 99,695,859 | 102,215,599 | 102,239,577 | −9.74 | 1.000 | −2.47 |
| 20261029 | a | 0.4456 | 55,400,011 | 55,299,888 | 55,316,014 | +0.49 | 0.290 | +0.18 |

## Excluded legs (cap rule; density + observed, for completeness)

Oct 5: a 0.9897 (606,179,470), b 1.0000 (624,975,000, degenerate).
Oct 11–15, 21–25, 29: b 0.0000 (0 APs, degenerate). Oct 17: a 0.9899
(606,150,665), b 0.99998 (624,926,497). Oct 18: a 0.9890
(604,441,485), b 1.0000 (degenerate). Oct 19: a 0.9891 (604,633,608),
b 1.0000 (degenerate). Oct 20: a 0.9903 (607,174,412), b 1.0000
(degenerate). Oct 21–22: both 0.0000 (degenerate). Oct 28: b 0.0857
(4,566,034 observed vs E 392,847 — +1,062%, flagged below, NOT
claimed: cap-excluded). Oct 30: a 0.9891 (604,918,390), b 1.0000
(degenerate). Oct 31: a 0.9900 (606,281,440), b 0.99998
(624,928,021).

## Anomalies flagged, not claimed

- **20261016-b (+207%, z = +561.65):** in-cap and the largest excess
  in the whole AP program by two orders of magnitude. The sequence
  at density 0.33 carries three times the progressions a random set
  would — clumped/bursty arrangement, not a density effect. No
  mechanism is named; no Kelley–Meka construction follows. This leg
  alone says the AP diagnostic is detecting regime, not a stable
  property of the wire.
- **20261028-b (+1,062%, cap-excluded):** same shape at low density —
  nearly-silent sequence with dense clumps. Excluded by the rule, so
  it is NOT counted as an excess; it is recorded because the
  clumping shape recurs.
- **Deficit windows (Oct 14-a −5.52%, Oct 23-a −4.87%, Oct 28-a
  −2.47%, Oct 8-b −1.78%):** observed far BELOW the uniform null
  (z down to −21). Anti-clustered / regularized arrangement on those
  days — the uniform null fails downward too. The AP diagnostic
  rejects uniformity in both directions across the month.

## Theorem-application verdict (pre-registered)

Diagnostic only; no Kelley–Meka construction; no drive naming. No
verdict on the theorem follows from any leg of this replication.
The Oct 16-b anomaly is a subject for a different question
(arrangement structure within a bursty regime), not an application
of the theorem.
