"""CDL3OUTSIDE — Three Outside Up/Down (three bars, bidirectional, magnitude 100).

A confirmed engulfing: an engulfing on the first two bars, validated by a third bar that
closes in the engulfing's direction. TA-Lib's test (no ``CandleSetting`` averaging — purely
geometric)::

    up (+100):   white[i-1] engulfs black[i-2]   (close[i-1] > open[i-2]  AND open[i-1] < close[i-2])
                 AND close[i]  > close[i-1]       # third bar confirms higher
    down (-100): black[i-1] engulfs white[i-2]   (open[i-1]  > close[i-2] AND close[i-1] < open[i-2])
                 AND close[i]  < close[i-1]       # third bar confirms lower

Unlike ``CDLENGULFING`` the engulfing test here uses **strict** inequalities (a touching edge
does not qualify), so there is no ±80 partial-penetration score — the output is exactly
-100/0/100. The pattern is reported at the third (confirmation) bar; TA-Lib's lookback is 3,
so the first three bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_color

# TA-Lib reports a lookback of 3 for CDL3OUTSIDE (engulfing on the two prior bars confirmed by
# the third); the earliest a signal can appear is index 3, so the first three bars are 0.
_LOOKBACK = 3


def three_outside(df: pd.DataFrame) -> pd.Series:
    """Three Outside Up/Down over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDL3OUTSIDE`` bit-exactly: a strict engulfing on the first two bars,
    confirmed by a third bar closing in the engulfing's direction. The first three bars are 0
    (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > _LOOKBACK - 1:
        # First candle = bars [0..n-3], engulfing candle = [1..n-2], confirmation = [2..n-1].
        first_o = o[:-2]
        first_c = c[:-2]
        first_col = color[:-2]
        eng_o = o[1:-1]
        eng_c = c[1:-1]
        eng_col = color[1:-1]
        conf_c = c[2:]

        # Bullish: white engulfs black, third bar closes higher (all strict).
        up = (
            (eng_col == 1)
            & (first_col == -1)
            & (eng_c > first_o)
            & (eng_o < first_c)
            & (conf_c > eng_c)
        )
        # Bearish: black engulfs white, third bar closes lower (all strict).
        down = (
            (eng_col == -1)
            & (first_col == 1)
            & (eng_o > first_c)
            & (eng_c < first_o)
            & (conf_c < eng_c)
        )

        body = np.zeros(n - 2, dtype="float64")
        body[up] = 100.0
        body[down] = -100.0
        out[2:] = body

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first three bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeOutside(Indicator):
    """Three Outside Up/Down candlestick pattern.

    What: a two-bar engulfing confirmed by a third bar closing further in its direction — a
    stronger reversal signal than a bare engulfing.
    Best settings: parameterless; bullish (+100) when a white bar engulfs a black bar and the
    next closes higher, bearish (-100) for the mirror image.
    Edge cases: strict engulfing only (no ±80 partial score); first three bars are 0.
    Parity: TA-Lib ``CDL3OUTSIDE`` (no CandleSettings, purely geometric), exact integer match.
    """

    spec = IndicatorSpec(
        name="three_outside",
        category="candles",
        aliases=("ThreeOutside", "CDL3OUTSIDE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_outside",),
        bounds={"three_outside": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3OUTSIDE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_outside(df)
