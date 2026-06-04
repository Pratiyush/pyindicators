"""EVWMA — Elastic Volume Weighted Moving Average (finta variant).

An approximation of the average price paid per share over the last ``period`` bars. The
"floating shares" in the window is the rolling volume sum ``vsum``; each bar mixes the prior
EVWMA and the current ``close`` by how much of that float the bar's own volume represents::

    EVWMA[i] = EVWMA[i-1] * (vsum[i] - volume[i]) / vsum[i]  +  close[i] * volume[i] / vsum[i]

so a high-volume bar pulls the average hard toward its price and a thin bar barely moves it.
This is a path-dependent recurrence (``stateful``) seeded from 0 at the first full window, which
is finta's exact construction. Inputs ``(close, volume)``. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def evwma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Elastic Volume Weighted MA of ``close`` over ``period`` bars (finta convention).

    Mirrors ``finta.TA.EVWMA`` exactly. ``vsum`` is the rolling volume sum; per bar
    ``x = (vsum - volume)/vsum`` (the prior weight, ``fillna(0)`` like finta) and
    ``y = volume*close/vsum`` (the new-price contribution). The recurrence is
    ``EVWMA[i] = EVWMA[i-1]*x[i] + y[i]`` seeded from 0, so the first full-window value is just
    ``y`` and the line elastically converges toward price as more volume accrues. Finta resets a
    bar to 0 whenever ``x == 0`` (window volume sits entirely on the current bar) or ``y == 0``
    (zero volume/price); we reproduce that. Warm-up bars (before the first full ``period`` window)
    are NaN here — finta emits 0 there, but that 0 is a seeding artefact, so we follow the
    house warm-up convention; parity masks the warm-up out and matches the recurrence bar-for-bar.
    """
    vol = df[VOLUME]
    vsum = vol.rolling(window=period).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        # x.fillna(0) and y unfilled, matching finta's exact arithmetic (incl. its 0/0 -> 0 reset).
        x = ((vsum - vol) / vsum).fillna(0.0).to_numpy(dtype="float64")
        y = ((vol * df[CLOSE]) / vsum).to_numpy(dtype="float64")
    vsum_a = vsum.to_numpy(dtype="float64")
    n = vsum_a.size
    out = np.full(n, np.nan, dtype="float64")
    prev = 0.0  # finta seeds the recurrence list with [0]
    for i in range(n):
        if np.isnan(vsum_a[i]):  # warm-up: no full window yet -> NaN (finta would emit 0)
            prev = 0.0
            continue
        xi = x[i]
        yi = y[i]
        # finta resets to 0 on a degenerate window (x==0 / y==0; NaN y arises only as 0/0).
        val = 0.0 if (xi == 0.0 or yi == 0.0 or np.isnan(yi)) else prev * xi + yi
        out[i] = val
        prev = val
    return pd.Series(out, index=df.index)


@INDICATORS.register
class EVWMA(Indicator):
    """Elastic Volume Weighted Moving Average.

    What: a volume-elastic moving average approximating the average price paid per share over
    the window; high-volume bars move it more, thin bars barely at all.
    Best settings: ``period`` 20 (finta default).
    Edge cases: seeded from 0 at the first full window, so it ramps in from below price; finta
    resets to 0 on a degenerate window (all window volume on one bar, or zero volume/price);
    warm-up is ``period-1`` NaN bars (finta emits 0 there).
    Parity: finta ``EVWMA`` (exact recurrence; masked to the finite overlap past warm-up).
    """

    spec = IndicatorSpec(
        name="evwma",
        category="trend",
        aliases=("Elastic Volume Weighted MA",),
        inputs=(CLOSE, VOLUME),
        outputs=("evwma",),
        stateful=True,
        references=("finta EVWMA",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return evwma(df, self.params["period"])
