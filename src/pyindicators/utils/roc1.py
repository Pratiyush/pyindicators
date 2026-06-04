"""ROC1 — one-bar Rate of Change in percent (utility).

The single-period special case of :func:`pyindicators.momentum.roc.roc`: the percent change
from the previous close, ``ROC1 = 100 * (close / close_{t-1} - 1)``. Provided as a named,
zero-parameter building block (e.g. for daily-return features) so callers don't have to
remember that "ROC with length 1" is the right primitive. Division is guarded against a zero
prior close. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def roc1(close: pd.Series) -> pd.Series:
    """One-bar rate of change in percent: ``100 * (close / close.shift(1) - 1)``.

    The first bar is NaN (no prior close). Guarded against a zero prior close, which yields
    NaN rather than an infinity (degenerate data).
    """
    prev = close.shift(1)
    return 100.0 * safe_divide(close - prev, prev)


@INDICATORS.register
class ROC1(Indicator):
    """One-bar Rate of Change.

    What: percentage price change versus the previous bar (the period-1 ROC / simple return).
    Best settings: none — it is the fixed single-period special case of ROC.
    Edge cases: first bar -> NaN; prior close == 0 -> guarded to NaN (degenerate data).
    Parity: identical to ``roc`` at ``length=1`` and to pandas-ta ``roc(close, length=1)``.
    """

    spec = IndicatorSpec(
        name="roc1",
        category="utils",
        aliases=("One-Bar Rate of Change", "Period-1 ROC"),
        inputs=(CLOSE,),
        outputs=("roc1",),
        talib_compatible=True,
        references=("TA-Lib ROC", "pandas-ta roc"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return roc1(df[CLOSE])
