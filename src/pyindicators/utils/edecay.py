"""Exponential Decay (EDECAY) — a prior level that bleeds down geometrically, floored at close.

The exponential sibling of linear :mod:`~pyindicators.utils.decay`: it makes a discrete signal
fade forward in time, but instead of subtracting a fixed ``1/length`` each bar it *multiplies*
the carried level by a constant factor ``exp(-1/length) < 1``. The level is always free to snap
back up to the current ``close``::

    factor = exp(-1 / length)
    edecay[0] = close[0]                                  (seed; no prior bar to decay)
    edecay[i] = max(close[i], edecay[i-1] * factor)       (i >= 1)

Unlike linear ``decay`` (which decays the *previous close*, ``close.shift(1)``, and is therefore
non-recursive), ``edecay`` is a genuine first-order recurrence: bar ``i`` decays the *previous
output*. It is path-dependent (``stateful``) but strictly causal — bar ``i`` reads only
``close[i]`` and the already-computed ``edecay[i-1]`` — with no look-ahead.

Parity note: the matching pandas-ta_classic function is ``edecay`` (multiplicative,
``prev * exp(-1/length)``), NOT ``decay(mode="exp")``. The two are different functions in that
library: ``decay(mode="exp")`` is the non-recursive ``max(close, close[-1] - exp(-length), 0)``,
whereas ``edecay`` is the recursive ``max(close, prev_out * exp(-1/length))`` defined here. The
spec hint's formula (``prev * exp(-1/length)``) is the ``edecay`` function, so we pin parity to
``pandas_ta_classic.edecay`` (Tulip Indicators ``edecay``). See ``ref/ta_docs/utils/EDecay.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def edecay(close: pd.Series, length: int = 5) -> pd.Series:
    """Exponential decay of ``close`` with per-bar factor ``exp(-1/length)``, floored at close.

    Returns ``max(close[i], edecay[i-1] * exp(-1/length))`` per bar, with bar 0 seeded to
    ``close[0]``. The line rides ``close`` whenever close holds up, and bleeds down
    geometrically toward (but never reaching) zero when the prior level outruns the new close.

    Reference parity (``pandas_ta_classic.edecay``) is undefined when fewer than ``length`` bars
    are supplied (its ``verify_series`` returns ``None``); to mirror that "no result yet"
    semantics we return an all-NaN series for ``len(close) < length`` rather than fabricate a
    partial recurrence.
    """
    x = close.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan, dtype="float64")
    if n == 0:  # the recursion is causal, so it runs for any n>=1 (truncation-invariant)
        return pd.Series(out, index=close.index)

    factor = float(np.exp(-1.0 / length))
    out[0] = x[0]
    for i in range(1, n):
        decayed = out[i - 1] * factor
        # NaN close (data gap) breaks the recurrence: emit NaN and carry it forward so the
        # level cannot silently resurrect from stale state (np.maximum already propagates NaN).
        out[i] = np.maximum(x[i], decayed)
    return pd.Series(out, index=close.index)


@INDICATORS.register
class ExponentialDecay(Indicator):
    """Exponential Decay (EDECAY).

    What: a forward-bleeding line that floors a carried ``close`` level, multiplying it by
        ``exp(-1/length)`` each bar (geometric fade toward 0) but always free to snap up to
        ``close``. The exponential counterpart of linear :class:`~pyindicators.utils.decay.Decay`.
    Best settings: 5 (default); larger ``length`` => factor closer to 1 => slower decay per bar.
    Edge cases: recursive/path-dependent (decays the prior *output*, unlike linear decay which
        decays the prior close); bar 0 seeded to the first close; a NaN close propagates as NaN;
        with fewer than ``length`` bars the result is all NaN (matches the reference returning no
        series). A non-positive close cannot pull the line below the decayed prior level.
    Parity: pandas-ta_classic ``edecay`` (Tulip Indicators ``edecay``), exact; this is NOT
        ``decay(mode="exp")`` — see the module docstring.
    """

    spec = IndicatorSpec(
        name="edecay",
        category="utils",
        aliases=("Exponential Decay", "EDECAY"),
        inputs=(CLOSE,),
        outputs=("edecay",),
        stateful=True,
        references=("Tulip Indicators edecay", "pandas-ta edecay"),
        doc="ref/ta_docs/utils/EDecay.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=5, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return edecay(df[CLOSE], self.params["length"])
