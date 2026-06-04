"""Decay — linear decay line that bleeds a prior level down toward zero.

Used to make a discrete signal (e.g. a crossover flag) fade forward in time instead of
vanishing the next bar: each step the carried level drops by a fixed ``1 / length`` and is
floored at 0, but is always allowed to jump back up to the current ``close``.

Despite the common phrasing "max(close, prev_decay - 1/length, 0)", the canonical
pandas-ta implementation decays the *previous close* (``close.shift(1)``), NOT the previous
(recursive) decay output, and seeds row 0 to ``close[0]``. We match that exact, non-recursive
definition so parity holds against ``pandas_ta_classic.decay(mode="linear")``::

    decay[i] = max(close[i], close[i-1] - 1/length, 0)   (i >= 1)
    decay[0] = max(close[0], 0)                           (seed; no look-back)

This is purely causal (row ``i`` reads only ``close[i]`` and ``close[i-1]``) and has no
warm-up NaN. See ``ref/ta_docs/utils/Decay.md`` (Tulip Indicators ``decay``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def decay(close: pd.Series, length: int = 5) -> pd.Series:
    """Linear decay of ``close`` with step ``1 / length``, floored at 0.

    Returns ``max(close[i], close[i-1] - 1/length, 0)`` per bar, with the first bar seeded
    to ``max(close[0], 0)`` (no look-back). The result rides ``close`` whenever close holds
    up, and bleeds down by a fixed amount per bar when the prior level outruns the new close.
    """
    step = 1.0 / length
    prior = close.shift(1) - step
    prior.iloc[0] = close.iloc[0]  # seed: no prior bar to decay from
    stacked = pd.concat(
        [close, prior, pd.Series(0.0, index=close.index)],
        axis=1,
    )
    out = stacked.max(axis=1)
    # max() over a row with a NaN close stays NaN only if every entry is NaN; guard explicitly
    # so a NaN close yields NaN rather than leaking through the 0 column.
    return out.mask(close.isna(), np.nan)


@INDICATORS.register
class Decay(Indicator):
    """Linear Decay.

    What: a forward-bleeding line that floors a carried ``close`` level, dropping it by a
    fixed ``1/length`` each bar and clamping at 0, but always free to snap up to ``close``.
    Best settings: 5 (default); larger ``length`` => slower, gentler decay per bar.
    Edge cases: non-recursive (decays the prior *close*, not the prior output); row 0 seeded
    to the first close; no warm-up NaN; a NaN close propagates as NaN.
    Parity: pandas-ta ``decay(mode="linear")`` (Tulip Indicators ``decay``).
    """

    spec = IndicatorSpec(
        name="decay",
        category="utils",
        aliases=("Linear Decay", "LDECAY"),
        inputs=(CLOSE,),
        outputs=("decay",),
        references=("Tulip Indicators decay", "pandas-ta decay"),
        doc="ref/ta_docs/utils/Decay.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=5, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return decay(df[CLOSE], self.params["length"])
