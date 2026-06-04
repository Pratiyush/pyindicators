"""Long Run — bullish-regime flag from a fast/slow MA pair (Archer Moving Averages Trends).

1 when the fast MA is rising while the slow MA is either bottoming (potential bottom) or also
rising (confirmed up-trend). Composes :func:`increasing` / :func:`decreasing`; the standalone
indicator derives the fast/slow MAs from close. See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .decreasing import decreasing
from .increasing import increasing

_MA = {"ema": ema, "sma": sma}


def long_run(fast: pd.Series, slow: pd.Series, length: int = 2) -> pd.Series:
    """1.0 where fast MA rises while slow MA bottoms or also rises, else 0.0."""
    inc_fast = increasing(fast, length) > 0
    pb = inc_fast & (decreasing(slow, length) > 0)  # potential bottom
    bi = inc_fast & (increasing(slow, length) > 0)  # both increasing
    return (pb | bi).astype("float64")


@INDICATORS.register
class LongRun(Indicator):
    """Long Run.

    What: a 0/1 bullish-regime flag — fast MA up while slow MA bottoms or rises.
    Best settings: ``fast`` 8, ``slow`` 21, ``lookback`` 2, ``mamode`` ema (Archer/AMAT).
    Edge cases: warm-up = slow MA length + lookback; pure 0/1 output.
    Parity: pandas-ta ``long_run`` (fed the same fast/slow series).
    """

    spec = IndicatorSpec(
        name="long_run",
        category="trend",
        aliases=("Long Run", "LR"),
        inputs=(CLOSE,),
        outputs=("long_run",),
        bounds={"long_run": (0.0, 1.0)},
        references=("Archer AMAT", "pandas-ta long_run"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=8, ge=1)
        slow: int = Field(default=21, ge=1)
        lookback: int = Field(default=2, ge=1)
        mamode: Literal["ema", "sma"] = "ema"

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        ma = _MA[p["mamode"]]
        return long_run(ma(df[CLOSE], p["fast"]), ma(df[CLOSE], p["slow"]), p["lookback"])
