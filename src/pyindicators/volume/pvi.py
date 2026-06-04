"""PVI — Positive Volume Index (cumulative; changes only on higher-volume days)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide


def pvi(df: pd.DataFrame, length: int = 1, initial: float = 1000.0) -> pd.Series:
    """Positive Volume Index: cumulative percent change applied only when volume rises."""
    roc_pct = 100.0 * safe_divide(df[CLOSE] - df[CLOSE].shift(length), df[CLOSE].shift(length))
    signed = roc_pct.where(df[VOLUME].diff() > 0, 0.0).fillna(0.0)
    signed.iloc[0] = initial
    return signed.cumsum()


@INDICATORS.register
class PVI(Indicator):
    """Positive Volume Index.

    What: cumulative price change accrued only on higher-volume days (the "crowd" idea).
    Best settings: length 1, initial 1000.
    Edge cases: seeded at ``initial``; down-volume days leave it unchanged.
    Parity: pandas-ta ``pvi``.
    """

    spec = IndicatorSpec(
        name="pvi",
        category="volume",
        aliases=("Positive Volume Index",),
        inputs=(CLOSE, VOLUME),
        outputs=("pvi",),
        references=("pandas-ta pvi",),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=1, ge=1)
        initial: float = Field(default=1000.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pvi(df, self.params["length"], self.params["initial"])
