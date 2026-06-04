"""FRAMA — Fractal Adaptive Moving Average (John Ehlers).

An EMA whose smoothing constant is driven by the *fractal dimension* of price: in a clean
trend the price path is near 1-D (a line) so the average speeds up; in choppy markets it is
near 2-D (it fills the plane) so the average slows down. The dimension ``D`` is estimated by
comparing the average per-bar range of two adjacent half-windows against the range of the
full window, then mapped to an EMA alpha ``= exp(-4.6 * (D - 1))`` clamped to ``[0.01, 1]``.

This implementation reproduces ``finta.TA.FRAMA`` exactly (its quirks included): the half
window is the independent ``batch`` (default 10, so the full window is 20), *not* ``length /
2``; the recursion is seeded by passing raw close through for the first ``2 * batch`` bars;
and a perfectly flat window yields ``log(0)`` -> ``D`` NaN -> NaN output (we never fabricate a
pass-through). Stateful recursion. See ``ref/ta_docs/trend/FRAMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def frama(close: pd.Series, length: int = 16, batch: int = 10) -> pd.Series:
    """Fractal Adaptive MA of ``close``.

    ``length`` is the (even) period label; ``batch`` is the half-window used for the fractal
    estimate (full window ``= 2 * batch``), matching finta where ``batch`` is decoupled from
    ``length``. Per-bar ranges are divided only by the constant window sizes (never zero);
    a flat window collapses every range to 0, so ``log(0)`` makes ``D`` (hence the output)
    NaN from bar ``2 * batch`` on — the faithful finta behaviour, not a pass-through.
    """
    if length % 2 != 0:
        raise ValueError(f"FRAMA length must be even, got {length}")
    c = close.astype("float64")
    window = batch * 2

    n1 = (c.rolling(batch).max() - c.rolling(batch).min()) / batch  # this half-window range
    n2 = n1.shift(batch)  # the adjacent (prior) half-window range
    n3 = (c.rolling(window).max() - c.rolling(window).min()) / window  # full-window range

    with np.errstate(divide="ignore", invalid="ignore"):
        dim = (np.log(n1 + n2) - np.log(n3)) / np.log(2.0)  # fractal dimension D in [1, 2]
        alpha = np.exp(-4.6 * (dim - 1.0))
    alpha = np.clip(alpha, 0.01, 1.0).to_numpy()  # NaN (flat window) survives the clip

    x = c.to_numpy()
    out = x.copy()  # seed: raw close passes through for the first ``window`` bars
    for i in range(window, x.size):
        a = alpha[i]
        out[i] = a * x[i] + (1.0 - a) * out[i - 1]  # a == NaN -> NaN, then carried forward
    return pd.Series(out, index=close.index)


@INDICATORS.register
class FRAMA(Indicator):
    """Fractal Adaptive Moving Average.

    What: an EMA whose alpha is set by price's fractal dimension — fast in trends, slow in chop.
    Best settings: length 16 (Ehlers); half-window ``batch`` 10 (finta default, full window 20).
    Edge cases: a flat window -> every range 0 -> log(0) -> D NaN -> NaN from bar ``2*batch`` on;
    first ``2*batch`` bars are the raw close (recursion seed).
    Parity: ``finta.TA.FRAMA(df, period=16)`` (batch=10). finta itself is unrunnable on
    pandas>=3 / numpy>=2 (it mutates a read-only ``Series.values``), so the parity test pins a
    line-for-line finta oracle on a writable copy.
    """

    spec = IndicatorSpec(
        name="frama",
        category="trend",
        aliases=("Fractal Adaptive MA",),
        inputs=(CLOSE,),
        outputs=("frama",),
        stateful=True,
        references=("Ehlers", "finta FRAMA"),
        doc="ref/ta_docs/trend/FRAMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=16, ge=2)
        batch: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return frama(df[CLOSE], p["length"], p["batch"])
