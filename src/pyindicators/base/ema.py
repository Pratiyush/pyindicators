"""EMA — Exponential Moving Average (base / overlap primitive).

Weights recent prices exponentially more than old ones. The #1 cross-library discrepancy
is *seeding*: TA-Lib seeds the first EMA with the SMA of the first ``length`` values (valid
at index ``length-1``); pandas ``ewm(adjust=False)`` seeds with the first price (valid at 0).
We default to the TA-Lib convention and expose ``talib_compatible`` to switch.
See ``ref/ta_docs/base/EMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ema(series: pd.Series, length: int, talib_compatible: bool = True) -> pd.Series:
    """Exponential moving average with ``alpha = 2/(length+1)``.

    ``talib_compatible=True`` (default): seed with the SMA of the first ``length`` *valid*
    values, recurse forward; first ``length-1`` outputs NaN. This also makes EMA-of-EMA
    cascades (DEMA/TEMA/T3) match TA-Lib by skipping the inner series' warm-up NaNs.
    ``talib_compatible=False``: pandas ``ewm(span=length, adjust=False)`` (seed = first value).
    """
    if not talib_compatible:
        return series.ewm(span=length, adjust=False, min_periods=length).mean()
    x = series.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    nonnan = np.flatnonzero(~np.isnan(x))
    if nonnan.size >= length:
        f = int(nonnan[0])  # first valid index; warm-up NaNs are a leading prefix
        alpha = 2.0 / (length + 1.0)
        prev = x[f : f + length].mean()  # SMA seed
        out[f + length - 1] = prev
        for i in range(f + length, n):
            prev = alpha * x[i] + (1.0 - alpha) * prev
            out[i] = prev
    return pd.Series(out, index=series.index)


@INDICATORS.register
class EMA(Indicator):
    """Exponential Moving Average.

    What: a recursive average giving more weight to recent prices (alpha = 2/(N+1)).
    Best settings: ``length`` 9/12/20/26/50/200; the 12/26 pair underlies MACD.
    Edge cases: seeding convention (see module doc); constant series -> EMA equals the constant.
    Parity: TA-Lib ``EMA`` (with ``talib_compatible=True``); pandas-ta ``ema``.
    """

    spec = IndicatorSpec(
        name="ema",
        category="base",
        aliases=("EWMA", "Exponentially Weighted MA"),
        inputs=(CLOSE,),
        outputs=("ema",),
        talib_compatible=True,
        references=("TA-Lib EMA", "pandas-ta ema", "tulip ema"),
        doc="ref/ta_docs/base/EMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ema(df[CLOSE], self.params["length"], self.params["talib_compatible"])
