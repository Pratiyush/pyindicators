"""Short Run — bearish-regime flag from a fast/slow MA pair (Archer Moving Averages Trends).

1 when the fast MA is falling while the slow MA is either topping (potential top) or also
falling (confirmed down-trend). Composes :func:`increasing` / :func:`decreasing`; the standalone
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


def short_run(fast: pd.Series, slow: pd.Series, length: int = 2) -> pd.Series:
    """1.0 where fast MA falls while slow MA tops or also falls, else 0.0."""
    dec_fast = decreasing(fast, length) > 0
    pt = dec_fast & (increasing(slow, length) > 0)  # potential top
    bd = dec_fast & (decreasing(slow, length) > 0)  # both decreasing
    return (pt | bd).astype("float64")


@INDICATORS.register
class ShortRun(Indicator):
    """Short Run.

    What: a 0/1 bearish-regime flag — fast MA down while slow MA tops or falls.
    Best settings: ``fast`` 8, ``slow`` 21, ``lookback`` 2, ``mamode`` ema (Archer/AMAT).
    Edge cases: warm-up = slow MA length + lookback; pure 0/1 output.
    Parity: pandas-ta ``short_run`` (fed the same fast/slow series).
    """

    spec = IndicatorSpec(
        name="short_run",
        category="trend",
        aliases=("Short Run", "SR"),
        inputs=(CLOSE,),
        outputs=("short_run",),
        bounds={"short_run": (0.0, 1.0)},
        references=("Archer AMAT", "pandas-ta short_run"),
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
        return short_run(ma(df[CLOSE], p["fast"]), ma(df[CLOSE], p["slow"]), p["lookback"])
