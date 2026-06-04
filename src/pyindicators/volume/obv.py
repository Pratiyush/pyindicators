"""OBV — On-Balance Volume (Joe Granville 1963).

A running total of volume: add on up-closes, subtract on down-closes, unchanged on flat.
Seeded with the first volume (TA-Lib convention). The absolute level is arbitrary; only the
trend matters. See ``ref/ta_docs/volume/OBV.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume (cumulative signed volume; seeded with the first volume)."""
    signed = np.sign(df[CLOSE].diff()).fillna(0.0) * df[VOLUME]
    signed.iloc[0] = df[VOLUME].iloc[0]  # TA-Lib seeds OBV[0] with the first volume
    return signed.cumsum()


@INDICATORS.register
class OBV(Indicator):
    """On-Balance Volume.

    What: cumulative up/down volume — buying/selling pressure that confirms price trends.
    Best settings: none; often paired with its own moving average for signals.
    Edge cases: unchanged close adds 0; the absolute level depends on the seed (trend matters).
    Parity: TA-Lib ``OBV`` / pandas-ta ``obv``.
    """

    spec = IndicatorSpec(
        name="obv",
        category="volume",
        aliases=("On-Balance Volume",),
        inputs=(CLOSE, VOLUME),
        outputs=("obv",),
        talib_compatible=True,
        references=("Granville 1963", "TA-Lib OBV", "pandas-ta obv"),
        doc="ref/ta_docs/volume/OBV.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return obv(df)
