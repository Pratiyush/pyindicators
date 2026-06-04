"""AOBV — Archer On-Balance Volume (an OBV trend system, popularised by pandas-ta).

Wraps OBV in a small trend-detection kit: rolling min/max envelopes of OBV, a fast and a
slow EMA of OBV, and two long/short "run" flags that fire when the fast/slow EMAs line up
into a confirmed (or nascent) up- or down-trend. Composes ``volume.obv`` + ``base.ema``.
See ``ref/ta_docs/volume/misc_volume.md``.

The run flags follow pandas-ta's ``long_run``/``short_run`` (themselves the engine behind
AMAT): with ``f = EMA_fast``, ``s = EMA_slow`` and lookback ``r = run_length`` and using the
non-strict "increasing/decreasing over r bars" test ``up(x) = x.diff(r) > 0``,
``down(x) = x.diff(r) < 0``:
    long_run  = (up(f)   & down(s))  |  (up(f)   & up(s))     # bottom forming, or both rising
    short_run = (down(f) & up(s))    |  (down(f) & down(s))   # top forming, or both falling
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec
from pyindicators.volume.obv import obv


def aobv(
    df: pd.DataFrame,
    fast: int = 4,
    slow: int = 12,
    max_lookback: int = 2,
    min_lookback: int = 2,
    run_length: int = 2,
) -> dict:
    """Archer OBV: OBV with min/max envelopes, fast/slow EMAs of OBV, and long/short runs.

    ``fast``/``slow`` are auto-swapped if given out of order (matching pandas-ta). EMAs are
    seeded TA-Lib-style (SMA of the first ``length`` values); the run flags are 0/1.
    """
    if slow < fast:
        fast, slow = slow, fast

    obv_ = obv(df)
    fast_ma = ema(obv_, fast)
    slow_ma = ema(obv_, slow)

    # Non-strict increasing/decreasing over `run_length` bars (pandas-ta long_run/short_run).
    fast_up = fast_ma.diff(run_length) > 0
    fast_down = fast_ma.diff(run_length) < 0
    slow_up = slow_ma.diff(run_length) > 0
    slow_down = slow_ma.diff(run_length) < 0
    long_run = (fast_up & slow_down) | (fast_up & slow_up)
    short_run = (fast_down & slow_up) | (fast_down & slow_down)

    return {
        "obv": obv_,
        "obv_min": obv_.rolling(min_lookback).min(),
        "obv_max": obv_.rolling(max_lookback).max(),
        "obv_fast": fast_ma,
        "obv_slow": slow_ma,
        "aobv_long_run": long_run.astype("float64"),
        "aobv_short_run": short_run.astype("float64"),
    }


@INDICATORS.register
class AOBV(Indicator):
    """Archer On-Balance Volume.

    What: OBV plus rolling min/max envelopes, fast/slow EMAs of OBV, and long/short run flags.
    Best settings: fast 4 / slow 12, lookbacks 2, run_length 2 (pandas-ta defaults).
    Edge cases: OBV[0] seeded with the first volume; run flags are 0/1; short frames -> NaN/0.
    Parity: pandas-ta ``aobv`` (EMA mamode); EMAs are tail-compared (SMA-seeded convergence).
    """

    spec = IndicatorSpec(
        name="aobv",
        category="volume",
        aliases=("Archer On-Balance Volume", "Archer OBV"),
        inputs=(CLOSE, VOLUME),
        outputs=(
            "obv",
            "obv_min",
            "obv_max",
            "obv_fast",
            "obv_slow",
            "aobv_long_run",
            "aobv_short_run",
        ),
        references=("pandas-ta aobv", "pandas-ta long_run", "pandas-ta short_run"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=4, ge=1)
        slow: int = Field(default=12, ge=1)
        max_lookback: int = Field(default=2, ge=1)
        min_lookback: int = Field(default=2, ge=1)
        run_length: int = Field(default=2, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return aobv(
            df,
            p["fast"],
            p["slow"],
            p["max_lookback"],
            p["min_lookback"],
            p["run_length"],
        )
