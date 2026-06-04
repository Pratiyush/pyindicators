"""VAMA — Volume Adjusted Moving Average (Tushar Chande, finta variant).

Weights each ``close`` by a volume ratio ``vp / volsum`` where ``vp = volume * close`` and
``volsum`` is the rolling-mean volume, then takes the volume-ratio-weighted average of
``close`` over the window: ``sum(volRatio*close, N) / sum(volRatio, N)``. Periods with heavier
relative volume pull the average toward their price. This is finta's exact construction (a
double ``period`` rolling, so the warm-up is ``2*(period-1)`` bars). Guarded division uses
``core.safe_divide``. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide


def vama(df: pd.DataFrame, period: int = 8) -> pd.Series:
    """Volume Adjusted Moving Average of ``close`` over ``period`` bars (finta convention).

    Steps (matching ``finta.TA.VAMA``): ``vp = volume*close``; ``volsum`` is the rolling-mean
    volume; ``volRatio = vp / volsum``; the result is ``sum(volRatio*close, N)/sum(volRatio, N)``.
    Default ``min_periods == period`` rolling on both stages yields a ``2*(period-1)`` warm-up.
    Closed forms: constant close & volume -> the constant; constant volume, varying close ->
    ``sum(close^2, N)/sum(close, N)``. Zero-volume windows -> ``volsum == 0`` -> guarded to NaN.
    """
    vp = df[VOLUME] * df[CLOSE]
    volsum = df[VOLUME].rolling(window=period).mean()
    vol_ratio = safe_divide(vp, volsum)  # NaN where mean volume is 0 (matches finta's 0/0)
    cum_sum = (vol_ratio * df[CLOSE]).rolling(window=period).sum()
    cum_div = vol_ratio.rolling(window=period).sum()
    return safe_divide(cum_sum, cum_div)


@INDICATORS.register
class VAMA(Indicator):
    """Volume Adjusted Moving Average.

    What: a moving average weighting each close by its volume ratio (volume vs rolling-mean
    volume), per finta's two-stage rolling construction.
    Best settings: ``period`` 8 (finta default).
    Edge cases: constant close & volume -> the constant; constant volume -> sum(c^2)/sum(c);
    zero mean-volume window -> guarded to NaN; warm-up is ``2*(period-1)`` bars.
    Parity: finta ``VAMA`` (closed-form double-rolling; not the TA-Lib/pandas-ta VAMA).
    """

    spec = IndicatorSpec(
        name="vama",
        category="trend",
        aliases=("Volume Adjusted Moving Average",),
        inputs=(CLOSE, VOLUME),
        outputs=("vama",),
        references=("finta VAMA", "Tushar Chande"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=8, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vama(df, self.params["period"])
