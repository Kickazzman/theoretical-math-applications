"""AP-density analytic yardstick (R-ANA).

For a uniform random k-subset of {0, ..., N-1}, the expected number
of 3-term arithmetic progressions (x, x+d, x+2d), d >= 1, is exact
combinatorics:

    E = P * k*(k-1)*(k-2) / (N*(N-1)*(N-2))
    P = sum_{d=1}^{floor((N-1)/2)} (N - 2*d)

Verified 2026-10-31: the formula reproduces the Monte Carlo
permutation-null means for the Oct 7 wire window (sequences A, B, W)
to within 0.018%, and 17 of 18 in-cap replication windows (N2) to
within 2 SE. See the equations file, entries R-ANA and R-N2.

Pure arithmetic. No network, no tokens, no state, no services.
Perg's yardstick: N and k alone give the uniform-null expectation;
an observed count is judged against E, and shuffles are the check,
not the first resort.
"""


def ap_pairs(n):
    """Number of (x, d) pairs with x >= 0, d >= 1, x + 2d <= n - 1."""
    n = int(n)
    if n < 3:
        raise ValueError("n must be >= 3")
    return sum(n - 2 * d for d in range(1, (n - 1) // 2 + 1))


def ap_expected(n, k):
    """Expected 3-term AP count for a uniform random k-subset of range(n)."""
    n = int(n)
    k = int(k)
    if n < 3:
        raise ValueError("n must be >= 3")
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")
    if k < 3:
        return 0.0
    p = ap_pairs(n)
    return p * (k * (k - 1) * (k - 2)) / (n * (n - 1) * (n - 2))


def ap_excess_ratio(n, k, observed):
    """(observed - E) / E. None when E is 0 (k < 3)."""
    e = ap_expected(n, k)
    if e == 0:
        return None
    return (float(observed) - e) / e


def ap_yardstick(n, k, observed=None):
    """One dict with the expectation, and the excess ratio if observed given."""
    e = ap_expected(n, k)
    out = {"n": int(n), "k": int(k), "pairs": ap_pairs(n),
           "expected": e, "density": int(k) / int(n)}
    if observed is not None:
        out["observed"] = float(observed)
        out["excess_ratio"] = ap_excess_ratio(n, k, observed)
    return out
