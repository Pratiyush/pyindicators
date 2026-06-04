"""RVI — Relative Volatility Index (Donald Dorsey).

RSI's construction applied to *volatility* instead of price: it sums the rolling standard
deviation on up-closes vs down-closes and scales the up-share to 0-100. Confirms breakouts
(rising volatility on up days). ``base.stdev`` + ``base.ema``. See
``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, stdev
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def rvi(close: pd.Series, length: int = 14, scalar: float = 100.0) -> pd.Series:
    """Relative Volatility Index over ``length`` bars (0-100)."""
    std = stdev(close, length)  # population stdev (ddof=0)
    diff = close.diff()
    up = (diff > 0).astype("float64") * std
    down = (diff < 0).astype("float64") * std
    up_avg = ema(up, length)
    down_avg = ema(down, length)
    return scalar * safe_divide(up_avg, up_avg + down_avg)  # flat -> NaN


@INDICATORS.register
class RVI(Indicator):
    """Relative Volatility Index.

    What: RSI computed on standard deviation rather than price change (0-100).
    Best settings: ``length`` 14; > 50 = volatility expanding on up days (breakout confirmation).
    Edge cases: zero up+down volatility -> guarded to NaN; warm-up = stdev length + EMA length.
    Parity: pandas-ta ``rvi`` (default close mode, EMA smoothing).
    """

    spec = IndicatorSpec(
        name="rvi",
        category="volatility",
        aliases=("Relative Volatility Index",),
        inputs=(CLOSE,),
        outputs=("rvi",),
        bounds={"rvi": (0.0, 100.0)},
        references=("Dorsey", "pandas-ta rvi"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)
        scalar: float = Field(default=100.0, gt=0.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return rvi(df[CLOSE], p["length"], p["scalar"])
