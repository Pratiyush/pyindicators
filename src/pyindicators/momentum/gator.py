"""Gator Oscillator (Bill Williams) — convergence/divergence of the Alligator's jaw/teeth/lips.

The Alligator is three Wilder-smoothed (SMMA / ``rma``) median-price lines: jaw = ``rma(med,
13)``, teeth = ``rma(med, 8)``, lips = ``rma(med, 5)``. The Gator measures the gaps between
them as a pair of histograms: ``upper = abs(jaw - teeth)`` (always >= 0, drawn above zero)
and ``lower = -abs(teeth - lips)`` (always <= 0, drawn below zero). It visualises when the
"Alligator" is sleeping (bars shrinking toward zero) versus eating (both bars widening).

This is the canonical UNSHIFTED variant: the lines are not displaced forward by the usual
8/5/3 bars, so every value at bar ``i`` depends only on rows ``<= i`` (causal). Median price
is composed from H/L; the three lines reuse ``base.rma`` (SMA-seeded Wilder smoothing) rather
than re-inlining the recurrence. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def gator(
    df: pd.DataFrame,
    jaw: int = 13,
    teeth: int = 8,
    lips: int = 5,
) -> dict:
    """Gator Oscillator from the unshifted Alligator lines.

    ``upper = |rma(med, jaw) - rma(med, teeth)|`` (>= 0) and
    ``lower = -|rma(med, teeth) - rma(med, lips)|`` (<= 0), where ``med = (high + low) / 2``.
    A flat window collapses both bars to 0 (the Alligator is fully asleep); warm-up before the
    longest line has filled propagates as NaN.
    """
    med = (df[HIGH] + df[LOW]) / 2.0
    jaw_line = rma(med, jaw)
    teeth_line = rma(med, teeth)
    lips_line = rma(med, lips)
    return {
        "gator_upper": (jaw_line - teeth_line).abs(),
        "gator_lower": -(teeth_line - lips_line).abs(),
    }


@INDICATORS.register
class GatorOscillator(Indicator):
    """Gator Oscillator.

    What: two histograms of the gaps between the Alligator's jaw/teeth/lips SMMA lines —
    ``upper = |jaw - teeth|`` above zero, ``lower = -|teeth - lips|`` below zero.
    Best settings: 13 / 8 / 5 (Williams), the standard Alligator periods; unshifted here.
    Edge cases: flat window -> both bars 0; warm-up = the longest (``jaw``) line's length.
    Parity: closed-form oracle (no reference lib ships Gator); the underlying SMMA lines are
    cross-checked against pandas-ta ``rma`` (SMA-seeded Wilder smoothing, TA-Lib convention).
    """

    spec = IndicatorSpec(
        name="gator",
        category="momentum",
        aliases=("Gator Oscillator", "Bill Williams Gator"),
        inputs=(HIGH, LOW),
        outputs=("gator_upper", "gator_lower"),
        references=("Bill Williams", "pandas-ta rma (SMMA lines)"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        jaw: int = Field(default=13, ge=1)
        teeth: int = Field(default=8, ge=1)
        lips: int = Field(default=5, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return gator(df, self.params["jaw"], self.params["teeth"], self.params["lips"])
