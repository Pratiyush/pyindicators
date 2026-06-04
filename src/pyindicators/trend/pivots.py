"""Pivot Points (classic floor-trader) — intraday support/resistance from the PRIOR bar.

The pivot ``P`` is the prior bar's typical price ``(H+L+C)/3``; the resistance/support
levels fan out from it using the prior bar's high/low. Levels are projected onto the
*current* bar, so every value is computed from ``shift(1)`` inputs and is strictly causal
(no look-ahead). There is no smoothing or seeding — each output is a closed-form algebraic
combination of the prior H/L/C. See ``ref/ta_docs/trend/Pivots.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def pivots(df: pd.DataFrame) -> dict:
    """Classic floor-trader pivot levels for the current bar from the prior bar's H/L/C.

    ``P = (H+L+C)/3``; ``R1 = 2P-L``, ``S1 = 2P-H``; ``R2 = P+(H-L)``, ``S2 = P-(H-L)``;
    ``R3 = H+2(P-L)``, ``S3 = L-2(H-P)`` — all of H/L/C/P taken from the previous bar.
    The first row is NaN (no prior bar to project from).
    """
    high = df[HIGH].shift(1)
    low = df[LOW].shift(1)
    close = df[CLOSE].shift(1)
    rng = high - low  # prior-bar range, reused across the band formulas

    pivot = (high + low + close) / 3.0
    return {
        "pivot": pivot,
        "r1": 2.0 * pivot - low,
        "s1": 2.0 * pivot - high,
        "r2": pivot + rng,
        "s2": pivot - rng,
        "r3": high + 2.0 * (pivot - low),
        "s3": low - 2.0 * (high - pivot),
    }


@INDICATORS.register
class Pivots(Indicator):
    """Pivot Points (classic / floor-trader).

    What: a central pivot ``P`` plus three resistance (R1-R3) and three support (S1-S3)
    levels projected onto the current bar from the *previous* bar's high/low/close.
    Best settings: parameter-free; the "bar" is whatever timeframe the frame is sampled at
    (daily pivots from daily bars, weekly from weekly, etc.).
    Edge cases: the first bar has no predecessor -> all outputs NaN; a flat prior bar
    (H==L==C) collapses every level onto ``P``. No division-by-zero is possible.
    Parity: finta ``PIVOT`` (P/S1/S2/S3/R1/R2/R3, prior-bar ``shift()``); also exact
    against the closed-form formula. Not in core TA-Lib / pandas-ta.
    """

    spec = IndicatorSpec(
        name="pivots",
        category="trend",
        aliases=("Pivot Points", "Floor Trader Pivots", "Classic Pivots"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("pivot", "r1", "s1", "r2", "s2", "r3", "s3"),
        causal=True,
        references=("Floor-trader pivots", "finta PIVOT"),
        doc="ref/ta_docs/trend/Pivots.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> dict:
        return pivots(df)
