"""DSP — Detrended Synthetic Price (Ehlers).

Removes the trend component from price to expose the underlying cycle. The canonical Ehlers
form detrends price against an exponential moving average: ``DSP = close - EMA(close, length)``
(``length`` default 14). We compose :func:`pyindicators.base.ema` with its TA-Lib-compatible
SMA seeding (``talib_compatible=True``), which reproduces pandas-ta-classic's ``dsp``
bit-for-bit (max |Δ| ~5e-14 on both the synthetic walk and real AAPL closes), including the
NaN warm-up positions. See ``ref/ta_docs/cycle/HilbertTransform.md``.

Note: this is the EMA-detrended "Detrended Synthetic Price" shipped by pandas-ta-classic.
TA-Lib does not provide a ``DSP`` function, so the oracle here is pandas-ta-classic ``dsp``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def dsp(close: pd.Series, length: int = 14) -> pd.Series:
    """Detrended Synthetic Price: ``close - EMA(close, length)``.

    Uses the TA-Lib-compatible EMA (SMA-seeded), so the first ``length - 1`` outputs are NaN
    and the result matches pandas-ta-classic ``dsp`` exactly.
    """
    return close - ema(close, length, talib_compatible=True)


@INDICATORS.register
class Dsp(Indicator):
    """Detrended Synthetic Price (DSP).

    What: price with its trend removed via an EMA, leaving the cyclical component
        (``close - EMA(close, length)``). Useful for cycle analysis and timing.
    Best settings: ``length`` 14 (the EMA period); shorter = faster, noisier detrend.
    Edge cases: warm-up = ``length - 1`` NaNs (SMA seed of the EMA); a flat series -> 0.
    Parity: pandas-ta-classic ``dsp`` (TA-Lib has no DSP), bit-exact (max |Δ| ~5e-14).
    """

    spec = IndicatorSpec(
        name="dsp",
        category="cycle",
        aliases=("Detrended Synthetic Price",),
        inputs=(CLOSE,),
        outputs=("dsp",),
        talib_compatible=True,
        references=("pandas-ta-classic dsp", "Ehlers Cycle Analytics for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dsp(df[CLOSE], self.params["length"])
