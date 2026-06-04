"""RS Rating — IBD-style per-symbol relative-strength score (multi-period momentum).

A weighted blend of price ratios over several lookbacks (recent weighted heaviest). This is
the per-symbol score; cross-sectional percentile ranking against a universe is the screener's
job (kept out of the causal, single-symbol indicator). Close-only (no benchmark needed).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def rs_rating(
    close: pd.Series,
    lookbacks: tuple[int, ...] = (63, 126, 189, 252),
    weights: tuple[float, ...] = (2.0, 1.0, 1.0, 1.0),
) -> pd.Series:
    """Weighted multi-period price-ratio momentum score (1.0 = flat over all lookbacks)."""
    total = sum(weights)
    score = sum(
        w * (close / close.shift(lb)) for lb, w in zip(lookbacks, weights, strict=True)
    )
    return score / total


@INDICATORS.register
class RSRating(Indicator):
    """RS Rating.

    What: a per-symbol relative-strength score from weighted multi-period returns (IBD-style).
    Best settings: lookbacks 63/126/189/252 (quarters), recent weighted 2x.
    Edge cases: needs the longest lookback of history; > 1 = up over the period, < 1 = down.
    Parity: per-symbol RS score (universe percentile ranking lives in the screener).
    """

    spec = IndicatorSpec(
        name="rs_rating",
        category="relative",
        aliases=("Relative Strength Rating", "IBD RS"),
        inputs=(CLOSE,),
        outputs=("rs_rating",),
        references=("O'Neil / IBD",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        lookbacks: tuple[int, ...] = (63, 126, 189, 252)
        weights: tuple[float, ...] = (2.0, 1.0, 1.0, 1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rs_rating(df[CLOSE], self.params["lookbacks"], self.params["weights"])
