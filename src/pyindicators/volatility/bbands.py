"""Bollinger Bands (+ %B, Bandwidth) — volatility envelope (John Bollinger).

A band around an SMA at +/- k population standard deviations; %B locates price within the
bands and bandwidth measures their relative width. Uses population stdev (``ddof=0``) to
match TA-Lib. Composes ``base.sma`` + ``base.stdev``. See ``ref/ta_docs/volatility/BollingerBands.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma, stdev
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def bbands(close: pd.Series, length: int = 20, mult: float = 2.0, ddof: int = 0) -> dict:
    """Return Bollinger middle/upper/lower bands plus bandwidth and %B."""
    middle = sma(close, length)
    sd = stdev(close, length, ddof)
    upper = middle + mult * sd
    lower = middle - mult * sd
    bandwidth = safe_divide(upper - lower, middle)
    pctb = safe_divide(close - lower, upper - lower)  # NaN where bands collapse (sd == 0)
    return {
        "bb_middle": middle,
        "bb_upper": upper,
        "bb_lower": lower,
        "bb_bandwidth": bandwidth,
        "bb_pctb": pctb,
    }


@INDICATORS.register
class BollingerBands(Indicator):
    """Bollinger Bands.

    What: an SMA envelope at +/- ``mult`` population stdevs, with %B and bandwidth.
    Best settings: 20 / 2.0 (Bollinger); population stdev for TA-Lib parity.
    Edge cases: flat window -> stdev 0 -> bands collapse, %B is guarded to NaN.
    Parity: TA-Lib ``BBANDS`` (bands); pandas-ta ``bbands`` (bandwidth/%B extras).
    """

    spec = IndicatorSpec(
        name="bbands",
        category="volatility",
        aliases=("Bollinger Bands", "BBANDS"),
        inputs=(CLOSE,),
        outputs=("bb_middle", "bb_upper", "bb_lower", "bb_bandwidth", "bb_pctb"),
        talib_compatible=True,
        references=("Bollinger", "TA-Lib BBANDS", "pandas-ta bbands"),
        doc="ref/ta_docs/volatility/BollingerBands.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        mult: float = Field(default=2.0, gt=0)
        ddof: int = Field(default=0, ge=0)

    def _compute(self, df: pd.DataFrame) -> dict:
        return bbands(df[CLOSE], self.params["length"], self.params["mult"], self.params["ddof"])
