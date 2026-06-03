"""ADX / DMI — Average Directional Index & Directional Movement (Wilder 1978).

DMI (+DI / -DI) shows trend direction; ADX measures trend strength regardless of direction.
Directional movement and TR are Wilder-smoothed; +DI/-DI are their ratios; DX is the
normalised spread; ADX is the Wilder-RMA of DX. Composes ``base.rma`` + ``base.true_range``.

Wilder's sum-smoothing and RMA (mean) give the SAME +DI/-DI ratio (both numerator and
denominator scale by N), so we reuse ``rma``. See ``ref/ta_docs/trend/ADX_DMI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma, true_range
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def directional_movement(df: pd.DataFrame, length: int = 14) -> dict:
    """Compute the full DMI/ADX family: +DI, -DI, DX, ADX, ADXR."""
    high, low = df[HIGH], df[LOW]
    up = high.diff()
    down = -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    plus_dm.iloc[0] = np.nan  # no directional movement on the first bar
    minus_dm.iloc[0] = np.nan
    tr = true_range(df).copy()
    tr.iloc[0] = np.nan  # exclude bar 0 (TA-Lib smooths TR/DM from bar 1)

    atr_ = rma(tr, length)
    plus_di = 100.0 * safe_divide(rma(plus_dm, length), atr_)
    minus_di = 100.0 * safe_divide(rma(minus_dm, length), atr_)
    dx = 100.0 * safe_divide((plus_di - minus_di).abs(), plus_di + minus_di)
    adx = rma(dx, length)
    adxr = (adx + adx.shift(length)) / 2.0
    return {"plus_di": plus_di, "minus_di": minus_di, "dx": dx, "adx": adx, "adxr": adxr}


@INDICATORS.register
class ADX(Indicator):
    """Average Directional Index (with +DI / -DI).

    What: ADX = trend strength (0-100); +DI/-DI = directional movement and crossovers.
    Best settings: 14; ADX > 25 trending, < 20 weak (Wilder).
    Edge cases: inside bars -> +DM=-DM=0; +DI+-DI=0 -> DX 0; ~150 bars to fully stabilise.
    Parity: TA-Lib ``ADX`` / ``PLUS_DI`` / ``MINUS_DI`` (converges after the double smoothing).
    """

    spec = IndicatorSpec(
        name="adx",
        category="trend",
        aliases=("Average Directional Index", "DMI"),
        inputs=(HIGH, LOW, "close"),
        outputs=("adx", "plus_di", "minus_di"),
        bounds={"adx": (0.0, 100.0), "plus_di": (0.0, 100.0), "minus_di": (0.0, 100.0)},
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib ADX", "pandas-ta adx"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        d = directional_movement(df, self.params["length"])
        return {"adx": d["adx"], "plus_di": d["plus_di"], "minus_di": d["minus_di"]}
