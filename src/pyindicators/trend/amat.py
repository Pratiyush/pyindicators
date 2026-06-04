"""AMAT — Archer Moving Averages Trends (fast/slow MA regime pair).

Emits two 0/1 flags from a fast and slow moving average of close: ``amat_lr`` (Long Run,
bullish regime) and ``amat_sr`` (Short Run, bearish regime). Composes :func:`long_run` /
:func:`short_run`. See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .long_run import long_run
from .short_run import short_run

_MA = {"ema": ema, "sma": sma}


def amat(
    close: pd.Series,
    fast: int = 8,
    slow: int = 21,
    lookback: int = 2,
    mamode: str = "ema",
) -> dict:
    """Archer MA Trends: Long Run and Short Run flags from fast/slow MAs of close."""
    ma = _MA[mamode]
    fast_ma, slow_ma = ma(close, fast), ma(close, slow)
    return {
        "amat_lr": long_run(fast_ma, slow_ma, lookback),
        "amat_sr": short_run(fast_ma, slow_ma, lookback),
    }


@INDICATORS.register
class AMAT(Indicator):
    """Archer Moving Averages Trends (AMAT).

    What: paired bullish (LR) / bearish (SR) regime flags from a fast and slow MA.
    Best settings: ``fast`` 8, ``slow`` 21, ``lookback`` 2, ``mamode`` ema (Archer).
    Edge cases: warm-up = slow MA length + lookback; both outputs are 0/1.
    Parity: pandas-ta ``amat`` (``AMATe_LR``/``AMATe_SR`` columns).
    """

    spec = IndicatorSpec(
        name="amat",
        category="trend",
        aliases=("Archer Moving Averages Trends",),
        inputs=(CLOSE,),
        outputs=("amat_lr", "amat_sr"),
        bounds={"amat_lr": (0.0, 1.0), "amat_sr": (0.0, 1.0)},
        references=("Archer AMAT", "pandas-ta amat"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=8, ge=1)
        slow: int = Field(default=21, ge=1)
        lookback: int = Field(default=2, ge=1)
        mamode: Literal["ema", "sma"] = "ema"

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return amat(df[CLOSE], p["fast"], p["slow"], p["lookback"], p["mamode"])
