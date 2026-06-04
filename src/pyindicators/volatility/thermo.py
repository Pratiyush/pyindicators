"""Elder's Thermometer — a volatility gauge from bar-to-bar extremes (Alexander Elder).

Takes the larger of the outside-move on each side (|prevLow - low| vs |high - prevHigh|), then
EMA-smooths it. Quiet markets sit below the average (long-friendly); volatility spikes push it
above (caution). Emits the raw line, its MA, and two 0/1 signals. Composes ``base.ema``.
See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def thermo(
    df: pd.DataFrame,
    length: int = 20,
    long: float = 2.0,
    short: float = 0.5,
) -> dict:
    """Elder Thermometer: raw line, EMA, and long/short 0/1 signals."""
    high, low = df[HIGH], df[LOW]
    thermo_l = (low.shift(1) - low).abs()
    thermo_h = (high - high.shift(1)).abs()
    line = pd.Series(np.maximum(thermo_l, thermo_h), index=df.index)  # larger outside-move
    ma = ema(line, length)
    return {
        "thermo": line,
        "thermo_ma": ma,
        "thermo_long": (line < ma * long).astype("float64"),
        "thermo_short": (line > ma * short).astype("float64"),
    }


@INDICATORS.register
class Thermo(Indicator):
    """Elder's Thermometer.

    What: a volatility "temperature" — the bigger of the two outside moves, EMA-smoothed.
    Best settings: length 20, long 2, short 0.5; thermo < MA*2 = calm, > MA*0.5 = heating up.
    Edge cases: first bar NaN (no prior high/low); signals are 0/1.
    Parity: pandas-ta ``thermo``, exact.
    """

    spec = IndicatorSpec(
        name="thermo",
        category="volatility",
        aliases=("Elder Thermometer", "Elder's Market Thermometer"),
        inputs=(HIGH, LOW),
        outputs=("thermo", "thermo_ma", "thermo_long", "thermo_short"),
        bounds={"thermo_long": (0.0, 1.0), "thermo_short": (0.0, 1.0)},
        references=("Elder", "pandas-ta thermo"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        long: float = Field(default=2.0, gt=0.0)
        short: float = Field(default=0.5, gt=0.0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return thermo(df, p["length"], p["long"], p["short"])
