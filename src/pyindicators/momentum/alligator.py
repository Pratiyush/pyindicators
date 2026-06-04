"""Williams Alligator — three SMMA "balance lines" (Bill Williams).

The Alligator is three Smoothed Moving Averages (SMMA == Wilder's RMA) of the median price
``(high + low) / 2``: the Jaw (slowest, 13), the Teeth (8) and the Lips (fastest, 5). Their
weave shows whether the market is trending (lines fanned and parallel) or ranging (lines
intertwined / "sleeping").

Causality note: Williams's original definition FORWARD-shifts the lines into the future
(jaw +8, teeth +5, lips +3) so they plot ahead of price on a chart. A forward shift is pure
look-ahead — at bar ``i`` it would expose values computed from bars ``> i`` — so it is NOT
applied here. We emit the *unshifted* SMMA lines (``causal=True``); a consumer that wants the
classic chart offset can shift the columns itself for display only.

Composes ``base.rma``. SMMA has no reference-library entry, so the oracle is its closed form:
``rma(median, length)``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pyindicators.base import rma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def alligator(df: pd.DataFrame, jaw: int = 13, teeth: int = 8, lips: int = 5) -> dict:
    """Williams Alligator jaw/teeth/lips = SMMA(median, {jaw, teeth, lips}), unshifted.

    ``median = (high + low) / 2``; each line is Wilder's RMA (== SMMA) of that median. The
    canonical forward offsets (jaw +8 / teeth +5 / lips +3) are intentionally NOT applied —
    forward-shifting is look-ahead and would break causality.
    """
    median = (df[HIGH] + df[LOW]) / 2.0
    return {
        "alligator_jaw": rma(median, jaw),
        "alligator_teeth": rma(median, teeth),
        "alligator_lips": rma(median, lips),
    }


@INDICATORS.register
class Alligator(Indicator):
    """Williams Alligator.

    What: three SMMAs (Wilder RMA) of the median price — Jaw (13), Teeth (8), Lips (5).
    Best settings: 13 / 8 / 5 (Williams); fanned & ordered = trend, intertwined = sleeping.
    Edge cases: warm-up = each line's length; a flat high==low series collapses all three
        lines onto the (constant) median. Forward offsets are omitted to stay causal.
    Parity: no library ships SMMA-based Alligator; oracle is ``rma(hl2, length)`` per line
        (cross-checked against pandas-ta ``rma``).
    """

    spec = IndicatorSpec(
        name="alligator",
        category="momentum",
        aliases=("Williams Alligator", "Gator"),
        inputs=(HIGH, LOW),
        outputs=("alligator_jaw", "alligator_teeth", "alligator_lips"),
        causal=True,  # unshifted SMMA lines; the classic forward offset is look-ahead
        references=("Bill Williams", "SMMA = pandas-ta rma"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        jaw: int = Field(default=13, ge=1)
        teeth: int = Field(default=8, ge=1)
        lips: int = Field(default=5, ge=1)

        @model_validator(mode="after")
        def _ordered_periods(self) -> Alligator.Params:
            # Jaw is the slowest line, Lips the fastest: jaw > teeth > lips by construction.
            if not (self.jaw > self.teeth > self.lips):
                raise ValueError(
                    f"alligator periods must satisfy jaw > teeth > lips, "
                    f"got jaw={self.jaw}, teeth={self.teeth}, lips={self.lips}"
                )
            return self

    def _compute(self, df: pd.DataFrame) -> dict:
        return alligator(df, self.params["jaw"], self.params["teeth"], self.params["lips"])
