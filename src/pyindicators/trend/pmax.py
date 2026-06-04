"""PMAX — Profit Maximizer (Supertrend on an MA +/- mult*ATR; KivancOzbilgic 2018).

What: a Supertrend-style trailing line built around a moving average of close rather than
hl2: bands at ``MA -/+ mult*ATR`` with a carry-forward rule so the active band only tightens
until close crosses it, flipping the trend (+1 long / -1 short). Stateful (path-dependent).

Note the band orientation differs from Supertrend: here the *lower* band (``MA - mult*ATR``)
is the long-side stop ("up" band) and the *upper* band (``MA + mult*ATR``) is the short-side
stop ("down" band) — matching pandas-ta's ``pmax`` exactly. Composes ``volatility.atr`` and
the base MA family (``ema``/``sma``/``wma``/``rma``); never re-inlines that math.

Sources: TradingView "PMax" (KivancOzbilgic), prorealcode PMax.

Parity: pandas-ta(_classic) ``pmax`` line (mamode='ema', ATR via Wilder RMA). pandas-ta
returns only the line; ``pmax_dir`` is the matching trend and is validated structurally.
The ATR seed differs by one bar from pandas-ta (our True Range defines bar 0 = H-L, theirs
NaN), a Wilder convergence difference — parity is checked on the converged tail.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, rma, sma, wma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec
from pyindicators.volatility.atr import atr

_MA_FUNCS = {"ema": ema, "sma": sma, "wma": wma, "rma": rma}


def _pmax_recurrence(close: np.ndarray, up: np.ndarray, down: np.ndarray) -> tuple:
    """Stateful PMAX trail. ``up = MA - mult*ATR`` (long stop), ``down = MA + mult*ATR``.

    Bands carry forward (only tighten) and the trend flips when close crosses the opposite
    band; the line tracks the active band. Mirrors pandas-ta ``pmax`` bit-for-bit, including
    its NaN-first / ``[1]*n`` trend seeding (warm-up bars are masked out by the caller).
    """
    n = close.size
    trend = np.ones(n)
    line = np.full(n, np.nan)
    for i in range(1, n):
        if close[i - 1] > up[i - 1]:
            up[i] = max(up[i], up[i - 1])
        if close[i - 1] < down[i - 1]:
            down[i] = min(down[i], down[i - 1])
        if close[i] > down[i - 1]:
            trend[i] = 1.0
        elif close[i] < up[i - 1]:
            trend[i] = -1.0
        else:
            trend[i] = trend[i - 1]
        line[i] = up[i] if trend[i] == 1.0 else down[i]
    return line, trend


def pmax(
    df: pd.DataFrame,
    length: int = 10,
    mult: float = 3.0,
    mamode: str = "ema",
) -> dict:
    """PMAX trailing line and trend direction (+1 uptrend / -1 downtrend).

    ``pmax`` matches pandas-ta's line exactly (NaN through the ATR/MA warm-up); ``pmax_dir``
    is masked to NaN over the same warm-up so a direction is only reported once the line is.
    """
    ma_fn = _MA_FUNCS[mamode]
    ma_value = ma_fn(df[CLOSE], length).to_numpy(dtype="float64")
    a = atr(df, length).to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")

    up = ma_value - mult * a  # long-side stop (pandas-ta "pmax_up")
    down = ma_value + mult * a  # short-side stop (pandas-ta "pmax_down")

    line, trend = _pmax_recurrence(close, up.copy(), down.copy())
    direction = np.where(np.isnan(line), np.nan, trend)
    return {
        "pmax": pd.Series(line, index=df.index),
        "pmax_dir": pd.Series(direction, index=df.index),
    }


@INDICATORS.register
class PMax(Indicator):
    """Profit Maximizer (PMAX).

    What: a Supertrend-style ATR trail around a moving average of close, with trend direction.
    Best settings: MA/ATR length 10, mult 3, EMA (TradingView default); shorter/looser for
    faster/slower regimes.
    Edge cases: needs ATR + MA warm-up (line and direction NaN until then); path-dependent
    carry-forward (stateful); a flat market parks the line on the active band.
    Parity: pandas-ta ``pmax`` line (Wilder-ATR seed converges; checked on the tail).
    """

    spec = IndicatorSpec(
        name="pmax",
        category="trend",
        aliases=("Profit Maximizer", "PMax"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("pmax", "pmax_dir"),
        stateful=True,
        references=("KivancOzbilgic PMax", "pandas-ta pmax"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        mult: float = Field(default=3.0, gt=0)
        mamode: str = Field(default="ema", pattern=r"^(ema|sma|wma|rma)$")

    def _compute(self, df: pd.DataFrame) -> dict:
        return pmax(df, self.params["length"], self.params["mult"], self.params["mamode"])
