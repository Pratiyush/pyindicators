"""CMO — Chande Momentum Oscillator (momentum).

``CMO = 100 * (sumUp - sumDown) / (sumUp + sumDown)`` over N, where up/down are the positive/
negative close changes. Range [-100, 100]. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def cmo(close: pd.Series, length: int = 14) -> pd.Series:
    """Chande Momentum Oscillator over ``length`` bars (bounded [-100, 100])."""
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    su = up.rolling(length, min_periods=length).sum()
    sd = down.rolling(length, min_periods=length).sum()
    return 100.0 * safe_divide(su - sd, su + sd)  # flat window (su+sd==0) -> NaN


@INDICATORS.register
class CMO(Indicator):
    """Chande Momentum Oscillator.

    What: net momentum as a percentage of total movement over N bars ([-100, 100]).
    Best settings: ``length`` 14; +/-50 = strong momentum.
    Edge cases: flat window (sumUp+sumDown == 0) -> guarded to NaN.
    Parity: pandas-ta ``cmo`` (Chande's original simple-sum form). NOT TA-Lib-compatible:
        TA-Lib ``CMO`` Wilder-smooths the up/down sums and diverges materially.
    """

    spec = IndicatorSpec(
        name="cmo",
        category="momentum",
        aliases=("Chande Momentum Oscillator",),
        inputs=(CLOSE,),
        outputs=("cmo",),
        bounds={"cmo": (-100.0, 100.0)},
        talib_compatible=False,
        references=("Chande", "pandas-ta cmo"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cmo(df[CLOSE], self.params["length"])
