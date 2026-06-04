"""Rainbow Charts — a recursive cascade of Simple Moving Averages (Mel Widner 1997).

Rather than averaging price ``num_ribbons`` independent times, Rainbow Charts feed each SMA
into the next: the first ribbon smooths ``close``, the second smooths the first ribbon, and so
on. The result is a fan of progressively-lagged, progressively-smoother lines whose spread
visualises trend strength (wide fan = strong directional move) and compression / reversals
(ribbons converge). See ``ref/ta_docs/trend/Rainbow.md``.

Definition (pandas-ta ``rainbow``):

    ribbon_1 = SMA(close,    length)
    ribbon_2 = SMA(ribbon_1, length)
    ...
    ribbon_k = SMA(ribbon_{k-1}, length)        for k = 1 .. num_ribbons

Composes ``base.sma``; each pass adds ``length - 1`` more warm-up NaNs, so ribbon ``k`` is
defined only from bar ``k * (length - 1)`` onward. No division and no look-ahead: every value
at bar ``i`` depends solely on rows ``<= i`` (purely causal).

``num_ribbons`` is fixed at the canonical default of 10 (matching pandas-ta) because the
``IndicatorSpec`` output contract is declared once at class-definition time; the bands are
``rainbow_1 .. rainbow_10``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

#: Number of cascaded ribbons. Fixed to pandas-ta's default so the output contract is static.
NUM_RIBBONS = 10


def rainbow(close: pd.Series, length: int = 2) -> dict:
    """Return the ``NUM_RIBBONS`` recursively-smoothed Rainbow ribbons of ``close``.

    Each ribbon is an SMA of the previous ribbon (the first is an SMA of ``close``), so the
    fan grows smoother and more lagged with depth. Keys are ``rainbow_1 .. rainbow_10``.
    """
    ribbons: dict[str, pd.Series] = {}
    prev = close
    for i in range(1, NUM_RIBBONS + 1):
        current = sma(prev, length)  # SMA of the *previous* ribbon — the recursive cascade
        ribbons[f"rainbow_{i}"] = current
        prev = current
    return ribbons


@INDICATORS.register
class Rainbow(Indicator):
    """Rainbow Charts (recursive SMA cascade).

    What: a fan of ``num_ribbons`` SMAs where each is the SMA of the previous one — the
        ribbons' spread tracks trend strength, their convergence flags reversals.
    Best settings: ``length`` 2 with 10 ribbons (Widner / pandas-ta default).
    Edge cases: ribbon ``k`` warms up over ``k * (length - 1)`` bars; a constant series
        collapses every ribbon onto that constant; no division, so no zero-guard is needed.
    Causality: purely causal (trailing SMAs only); value at bar ``i`` uses rows ``<= i``.
    Parity: pandas-ta ``rainbow`` (``length=2``, ``num_ribbons=10``). pandas-ta returns
        ``None`` when the series is shorter than ``length * num_ribbons`` (its ``verify_series``
        guard); we instead emit the natural all-NaN warm-up rows, so the parity test skips that
        degenerate too-short case.
    """

    spec = IndicatorSpec(
        name="rainbow",
        category="trend",
        aliases=("Rainbow Charts", "Rainbow Moving Average"),
        inputs=(CLOSE,),
        outputs=tuple(f"rainbow_{i}" for i in range(1, NUM_RIBBONS + 1)),
        causal=True,
        references=("Widner 1997", "pandas-ta rainbow"),
        doc="ref/ta_docs/trend/Rainbow.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=2, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return rainbow(df[CLOSE], self.params["length"])
