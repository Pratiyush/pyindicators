"""Lag — ``close`` shifted forward by ``length`` bars (``close.shift(length)``).

A primitive utility: the value at bar ``i`` is the close from ``length`` bars earlier, i.e.
``close[i - length]``. With the default ``length=1`` it is simply "yesterday's close". It is
the building block for any "compare to N bars ago" construction (momentum, crossovers of a
series with its own history). With ``length > 0`` it strictly looks back, so it is causal; the
first ``length`` bars are NaN (no prior bar to borrow from). There is no external reference
library for this — its definition *is* ``pandas.Series.shift``, so it is golden-tested against
that closed form (see ``tests/utils/test_lag.py`` / ``tests/parity/test_parity_lag.py``).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def lag(close: pd.Series, length: int = 1) -> pd.Series:
    """Return ``close`` delayed by ``length`` bars: value at bar ``i`` is ``close[i-length]``.

    Equivalent to ``close.shift(length)``. The first ``length`` rows are NaN (no earlier bar
    exists to carry forward). ``length`` must be a positive integer (a backward, look-back
    shift); a non-positive shift would peek at the future and is rejected by ``Params``.
    """
    return close.shift(length)


@INDICATORS.register
class Lag(Indicator):
    """Lag.

    What: ``close`` delayed by ``length`` bars (``close.shift(length)``) — the close from
    ``length`` bars ago, aligned to the current bar.
    Best settings: ``length`` 1 (previous close); any positive integer for an N-bar delay.
    Edge cases: the first ``length`` bars are NaN; constant input stays constant after warm-up.
    Parity: no external oracle — defined as ``pandas.Series.shift``; golden-tested against it.
    """

    spec = IndicatorSpec(
        name="lag",
        category="utils",
        aliases=("Lag", "Delay"),
        inputs=(CLOSE,),
        outputs=("lag",),
        causal=True,
        references=("pandas.Series.shift",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return lag(df[CLOSE], self.params["length"])
