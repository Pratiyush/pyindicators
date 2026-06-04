"""TOS StDevAll — ThinkOrSwim "Standard Deviation All" (TD Ameritrade, via pandas-ta).

Fits ONE ordinary-least-squares line over the whole series (``x = 0..n-1`` against the
closes) and draws +/- ``k`` * population-ish stdev bands around it for ``k`` in ``{1, 2, 3}``.
Unlike a rolling regression (``linreg``), the fit spans every bar, so the value at bar ``i``
depends on the *entire* series — including bars after ``i``. That makes it inherently
non-causal (``causal=False``): it is a static plot/overlay for the visible chart, not a
streaming signal. Composes :func:`pyindicators.base.stdev` for the band width.

Parity: ``pandas_ta_classic.tos_stdevall`` with its default ``length=None`` (all bars),
``stds=[1, 2, 3]``, ``ddof=1`` -> 7 columns (central LR + lower/upper for each std level).
The reference fits with ``numpy.polyfit(x, close, 1)``; we use the same so the line matches
to machine precision. See ``ref/ta_docs/statistics`` for the LinearRegression family.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import stdev
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

# Reference default std multiples (increasing from the central line); fixed to match pandas-ta.
_STDS: tuple[int, int, int] = (1, 2, 3)


def tos_stdevall(close: pd.Series, ddof: int = 1) -> dict[str, pd.Series]:
    """ThinkOrSwim StDevAll over the whole series: central LR line + 1/2/3-stdev bands.

    Fits ``y = m*x + b`` once across all ``n`` bars (``x = 0..n-1``) via ordinary least
    squares, then offsets the resulting line by ``+/- k * stdev(close, ddof)`` for
    ``k in {1, 2, 3}``. Returns the central line and the six band lines, each full-length and
    aligned to ``close.index``. A flat series has stdev 0, so all bands collapse onto the LR
    line (here a horizontal line at the mean) rather than producing NaN.
    """
    index = close.index
    y = close.to_numpy(dtype="float64")
    n = y.size
    if n == 0:
        empty = pd.Series(np.array([], dtype="float64"), index=index)
        out: dict[str, pd.Series] = {"tos_stdevall_lr": empty}
        for k in _STDS:
            out[f"tos_stdevall_l_{k}"] = empty
            out[f"tos_stdevall_u_{k}"] = empty
        return out

    x = np.arange(n, dtype="float64")
    if n < 2:
        # A single bar has no slope to fit (polyfit's x-matrix is singular); the line is just a
        # horizontal at that value. pandas-ta only supports length > 2, so this extends the domain.
        lr = pd.Series(np.full(n, y[0]), index=index)
    else:
        # Same fit as pandas-ta (numpy.polyfit degree 1): the LR line is the static
        # least-squares trend across every bar, so the line matches the reference to ~1e-13.
        slope, intercept = np.polyfit(x, y, 1)
        lr = pd.Series(slope * x + intercept, index=index)

    # Band half-widths: a single scalar stdev of the whole window (ddof from the spec). Reuse
    # base.stdev over the full length so the convention matches the rest of the library.
    sd = float(stdev(close, n, ddof).iloc[-1]) if n > ddof else 0.0

    out = {"tos_stdevall_lr": lr}
    for k in _STDS:
        out[f"tos_stdevall_l_{k}"] = lr - k * sd
        out[f"tos_stdevall_u_{k}"] = lr + k * sd
    return out


@INDICATORS.register
class TOSStDevAll(Indicator):
    """TOS StDevAll (ThinkOrSwim Standard Deviation All).

    What: a single least-squares regression line fit over the *entire* series, framed by
        +/- 1/2/3 standard-deviation bands; a static chart overlay, not a streaming indicator.
    Best settings: defaults (all bars, stds 1/2/3, ddof 1) reproduce the ThinkOrSwim study.
    Edge cases: full-window fit -> every bar depends on all bars (non-causal); flat series ->
        stdev 0 -> bands collapse onto the LR line; n == 1 -> horizontal line at that value.
    Parity: pandas-ta ``tos_stdevall`` (length=None / all bars), 7-column default. Non-causal,
        so there is no warm-up: all rows are populated.
    """

    spec = IndicatorSpec(
        name="tos_stdevall",
        category="statistics",
        aliases=("TOS Standard Deviation All", "ThinkOrSwim StDevAll", "TOS_STDEVALL"),
        inputs=(CLOSE,),
        outputs=(
            "tos_stdevall_lr",
            "tos_stdevall_l_1",
            "tos_stdevall_u_1",
            "tos_stdevall_l_2",
            "tos_stdevall_u_2",
            "tos_stdevall_l_3",
            "tos_stdevall_u_3",
        ),
        # Full-series regression: the value at any bar uses bars after it, so it looks ahead.
        causal=False,
        references=("TD Ameritrade ThinkOrSwim StDevAll", "pandas-ta tos_stdevall"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        ddof: int = Field(default=1, ge=0)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return tos_stdevall(df[CLOSE], self.params["ddof"])
