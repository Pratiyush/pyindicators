"""Parabolic SAR — Stop And Reverse trailing stop (Welles Wilder 1978).

A trailing stop that accelerates toward price: each bar SAR moves by ``af * (EP - SAR)`` where
EP is the running extreme and the acceleration factor ``af`` steps up (capped at ``max_af``)
every time a new extreme prints. When price crosses the SAR the system flips direction. Outputs
the SAR line, the live acceleration factor, and a reversal flag. Stateful recursion seeded from
the first two bars' directional movement. See ``ref/ta_docs/trend/PSAR.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def psar(df: pd.DataFrame, af0: float = 0.02, max_af: float = 0.2) -> dict:
    """Parabolic SAR line, acceleration factor, and reversal flag (high/low driven)."""
    h = df[HIGH].to_numpy(dtype="float64")
    low_a = df[LOW].to_numpy(dtype="float64")
    m = h.size
    sar_arr = np.full(m, np.nan)
    af_arr = np.full(m, np.nan)
    rev_arr = np.zeros(m)
    if m == 0:
        return {"psar": pd.Series(sar_arr, index=df.index),
                "psar_af": pd.Series(af_arr, index=df.index),
                "psar_reversal": pd.Series(rev_arr, index=df.index)}

    # Initial trend: falling if the first bar's -DM is positive (Wilder/pandas-ta convention).
    if m > 1:
        up = h[1] - h[0]
        dn = low_a[0] - low_a[1]
        falling = (dn > up) and (dn > 0)
    else:
        falling = False
    if falling:
        sar, ep = h[0], (low_a[1] if m > 1 else low_a[0])
    else:
        sar, ep = low_a[0], (h[1] if m > 1 else h[0])

    af_arr[0] = af0
    af = af0
    for row in range(1, m):
        hi, lo = h[row], low_a[row]
        _sar = sar + af * (ep - sar)
        if falling:
            if lo < ep:
                ep = lo
                af = min(af + af0, max_af)
            _sar = max(h[row - 1], h[max(0, row - 2)], _sar)  # SAR can't enter the prior 2 highs
            reverse = hi > _sar
        else:
            if hi > ep:
                ep = hi
                af = min(af + af0, max_af)
            _sar = min(low_a[row - 1], low_a[max(0, row - 2)], _sar)
            reverse = lo < _sar
        if reverse:
            _sar = ep
            af = af0
            falling = not falling
            ep = lo if falling else hi
        sar = _sar
        sar_arr[row] = sar
        af_arr[row] = af
        rev_arr[row] = 1.0 if reverse else 0.0
    return {
        "psar": pd.Series(sar_arr, index=df.index),
        "psar_af": pd.Series(af_arr, index=df.index),
        "psar_reversal": pd.Series(rev_arr, index=df.index),
    }


@INDICATORS.register
class PSAR(Indicator):
    """Parabolic SAR (Stop And Reverse).

    What: an accelerating trailing stop that flips long/short when price crosses it; the dots
        trail below price in up-trends and above in down-trends.
    Best settings: af0 0.02, max_af 0.2 (Wilder); raise af0 for a tighter, twitchier stop.
    Edge cases: seeded from the first two bars; SAR is clamped out of the prior two extremes;
        ``psar_reversal`` marks flip bars; first bar NaN.
    Parity: pandas-ta ``psar`` (combined long/short line) exactly; TA-Lib ``SAR`` on the tail
        (initial trend seeding differs).
    """

    spec = IndicatorSpec(
        name="psar",
        category="trend",
        aliases=("Parabolic SAR", "Stop And Reverse"),
        inputs=(HIGH, LOW),
        outputs=("psar", "psar_af", "psar_reversal"),
        bounds={"psar_reversal": (0.0, 1.0)},
        stateful=True,
        references=("Wilder 1978", "TA-Lib SAR", "pandas-ta psar"),
        doc="ref/ta_docs/trend/PSAR.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        af0: float = Field(default=0.02, gt=0.0, le=1.0)
        max_af: float = Field(default=0.2, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return psar(df, p["af0"], p["max_af"])
