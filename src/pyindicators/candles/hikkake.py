"""CDLHIKKAKE — Hikkake pattern (multi-bar, bidirectional, stateful).

The Hikkake is a trap/false-breakout pattern built around an *inside bar*. TA-Lib detects it
in two stages and carries state across bars:

* **Setup** at bar ``i`` (writes ±100): the previous bar is an inside bar relative to the one
  before it (``high[i-1] < high[i-2]`` and ``low[i-1] > low[i-2]``), and the current bar
  breaks that inside bar's range in a single direction — either a lower high *and* a lower low
  (bearish-looking break down → result ``+100``) or a higher high *and* a higher low (break up
  → result ``-100``). The sign is intentionally the *opposite* of the break direction because
  the Hikkake anticipates a reversal of that break.
* **Confirmation** within the next three bars (writes ±200): for a ``+100`` setup, a later
  close above the inside bar's high (``close[i] > high[patternIdx-1]``); for a ``-100`` setup,
  a later close below the inside bar's low (``close[i] < low[patternIdx-1]``). TA-Lib emits the
  setup result *plus another* ``±100`` here, i.e. ``±200`` (NOT a ±80 partial-penetration
  score — that score belongs to engulfing/harami-style patterns, not Hikkake).

So the output value set is ``{-200, -100, 0, 100, 200}`` (verified bit-exactly against
``talib.CDLHIKKAKE`` on both the synthetic walk and real AAPL daily bars). ``patternResult``
and ``patternIdx`` persist across iterations exactly as in TA-Lib's C loop; once a setup is
confirmed its ``patternIdx`` is cleared so it cannot be confirmed twice.

TA-Lib reports a lookback of 5 for this pattern, so the first five bars are always 0. The C
implementation also runs a three-bar *warm-up* (``startIdx-3 .. startIdx-1``) that seeds the
pattern state without emitting output; we reproduce it so the very first emittable bars match.
``CDLHIKKAKE`` takes no parameters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

# TA-Lib reports a lookback of 5 for CDLHIKKAKE; the first five outputs are always 0.
_LOOKBACK = 5


def _is_setup(high: np.ndarray, low: np.ndarray, i: int) -> bool:
    """Whether bar ``i`` completes a Hikkake setup (inside bar at ``i-1`` then a break)."""
    return (
        high[i - 1] < high[i - 2]
        and low[i - 1] > low[i - 2]
        and (
            (high[i] < high[i - 1] and low[i] < low[i - 1])
            or (high[i] > high[i - 1] and low[i] > low[i - 1])
        )
    )


def hikkake(df: pd.DataFrame) -> pd.Series:
    """Hikkake pattern over ``df`` (OHLC) as a -200/-100/0/100/200 ``Series``.

    Matches ``talib.CDLHIKKAKE`` bit-exactly: ``±100`` on a setup bar and ``±200`` on the
    confirmation bar (within three bars of the setup), 0 otherwise, and 0 during the five-bar
    lookback. State (``pattern_result`` / ``pattern_idx``) carries across bars as in TA-Lib.
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")
    n = len(close)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)  # not enough bars to clear the lookback

    start = _LOOKBACK
    pattern_result = 0
    pattern_idx = 0

    # Warm-up (TA-Lib): seed pattern state from the three bars before ``start`` without output.
    for i in range(start - 3, start):
        if _is_setup(high, low, i):
            pattern_result = 100 if high[i] < high[i - 1] else -100
            pattern_idx = i
        elif i <= pattern_idx + 3 and (  # pragma: no cover - warm-up twin of the tested main loop
            (pattern_result > 0 and close[i] > high[pattern_idx - 1])
            or (pattern_result < 0 and close[i] < low[pattern_idx - 1])
        ):
            pattern_idx = 0

    # Main loop: emit ±100 on setup, ±200 on a confirming close within three bars.
    for i in range(start, n):
        if _is_setup(high, low, i):
            pattern_result = 100 if high[i] < high[i - 1] else -100
            pattern_idx = i
            out[i] = float(pattern_result)
        elif i <= pattern_idx + 3 and (
            (pattern_result > 0 and close[i] > high[pattern_idx - 1])
            or (pattern_result < 0 and close[i] < low[pattern_idx - 1])
        ):
            out[i] = float(pattern_result + (100 if pattern_result > 0 else -100))
            pattern_idx = 0

    return pd.Series(out, index=df.index)


@INDICATORS.register
class Hikkake(Indicator):
    """Hikkake candlestick pattern.

    What: an inside-bar false-breakout trap; the sign anticipates a reversal of the break.
    Best settings: parameterless; ±100 on the setup bar, ±200 when confirmed within three bars.
    Edge cases: confirmation must occur within three bars of the setup; first five bars are 0.
    Parity: TA-Lib ``CDLHIKKAKE`` (output set {-200,-100,0,100,200}), exact integer match.
    """

    spec = IndicatorSpec(
        name="hikkake",
        category="candles",
        aliases=("Hikkake", "CDLHIKKAKE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("hikkake",),
        bounds={"hikkake": (-200.0, 200.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHIKKAKE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hikkake(df)
