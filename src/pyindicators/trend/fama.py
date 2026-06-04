"""FAMA — Following Adaptive Moving Average (the slow companion of MAMA / TA-Lib ``MAMA``).

FAMA is the second output of TA-Lib's ``MAMA``: a half-gain EMA that follows the MAMA line
(``fama = 0.5*alpha*mama + (1 - 0.5*alpha)*fama_prev``), used as the slower side of the
MAMA/FAMA crossover. The whole recurrence lives in :func:`pyindicators.trend.mama._mama_fama`
(MAMA and FAMA are computed together, sharing the Ehlers Hilbert pipeline); this module just
selects the FAMA line so it can be requested on its own. See ``ref/ta_docs/trend/MAMA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .mama import _mama_fama


def fama(close: pd.Series, fastlimit: float = 0.5, slowlimit: float = 0.05) -> pd.Series:
    """Return the FAMA (Following Adaptive MA) line — the slow companion of MAMA."""
    _, f = _mama_fama(close, fastlimit, slowlimit)
    return f


@INDICATORS.register
class FAMA(Indicator):
    """Following Adaptive Moving Average (slow companion of MAMA).

    What: a half-gain follower of the MESA Adaptive MA — it tracks MAMA with half the adaptive
        gain, so MAMA crossing above/below FAMA is the classic MESA trade signal.
    Best settings: fastlimit=0.5, slowlimit=0.05 (Ehlers/TA-Lib), matching MAMA.
    Edge cases: long fixed warm-up — the first 32 bars are NaN (TA-Lib's lookback with the
        default unstable period of 0); seeds at bar 6 and converges to TA-Lib on the tail.
    Parity: TA-Lib ``MAMA`` (second output) — bit-exact on the tail once the EMAs settle.
    """

    spec = IndicatorSpec(
        name="fama",
        category="trend",
        aliases=("Following Adaptive Moving Average", "FAMA"),
        inputs=(CLOSE,),
        outputs=("fama",),
        stateful=True,
        talib_compatible=True,
        references=("Ehlers MESA", "TA-Lib MAMA"),
        doc="ref/ta_docs/trend/MAMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fastlimit: float = Field(default=0.5, gt=0.0, le=1.0)
        slowlimit: float = Field(default=0.05, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return fama(df[CLOSE], p["fastlimit"], p["slowlimit"])
