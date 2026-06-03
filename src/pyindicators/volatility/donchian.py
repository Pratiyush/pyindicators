"""Donchian Channels — breakout channel (Richard Donchian; Turtle Traders).

Highest high and lowest low over N bars, plus their midpoint. Includes the current bar
(pandas-ta convention). See ``ref/ta_docs/volatility/Donchian.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def donchian(df: pd.DataFrame, lower_length: int = 20, upper_length: int = 20) -> dict:
    """Donchian lower (lowest low), middle, and upper (highest high) channels."""
    lower = df[LOW].rolling(lower_length, min_periods=lower_length).min()
    upper = df[HIGH].rolling(upper_length, min_periods=upper_length).max()
    return {"dc_lower": lower, "dc_middle": (lower + upper) / 2.0, "dc_upper": upper}


@INDICATORS.register
class Donchian(Indicator):
    """Donchian Channels.

    What: the N-bar high/low envelope and its midpoint — the classic breakout channel.
    Best settings: 20 (entries), 10 (exits) in the Turtle system.
    Edge cases: includes the current bar (Turtle's original rule excluded it — documented).
    Parity: pandas-ta ``donchian`` (DCL/DCM/DCU). Not in core TA-Lib.
    """

    spec = IndicatorSpec(
        name="donchian",
        category="volatility",
        aliases=("Donchian Channels",),
        inputs=(HIGH, LOW),
        outputs=("dc_lower", "dc_middle", "dc_upper"),
        references=("Donchian", "pandas-ta donchian"),
        doc="ref/ta_docs/volatility/Donchian.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        lower_length: int = Field(default=20, ge=1)
        upper_length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return donchian(df, self.params["lower_length"], self.params["upper_length"])
