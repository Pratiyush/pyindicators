"""VPA Climactic Bars — Volume Spread Analysis "climax" bar flag (Williams / Coulling).

In Volume Spread Analysis (Tom Williams' *Master the Markets*; Anna Coulling's *A Complete
Guide to Volume Price Analysis*) a **climactic bar** marks the exhaustion of a move: an
ultra-high-volume, wide-spread bar that prints a new extreme at the end of a directional run.
A *buying* climax (the close makes a new high on huge volume and a wide spread) tends to end
an up-move; a *selling* climax (a new low on huge volume / wide spread) tends to end a
down-move. There is **no reference-library oracle** for this VSA rule, so this implements a
clearly-documented, fully-deterministic standard form and golden-tests it.

A bar ``i`` is flagged ``1`` iff all three conditions hold (else ``0``):

1. **Ultra-high volume** — ``volume[i] > vol_k * SMA(volume, length)[i]`` (volume far above
   its trailing average; ``vol_k`` defaults to 2.0).
2. **Wide spread** — ``range[i] > range_k * SMA(range, length)[i]`` with ``range = high - low``
   (the bar's spread is far wider than its trailing average; ``range_k`` defaults to 1.5).
3. **End of a trend / new extreme** — the close is a *strict* extreme of the trailing
   ``length``-bar window: ``close[i] > max(close[i-length .. i-1])`` (buying climax, a strict
   new ``length``-bar high) **or** ``close[i] < min(close[i-length .. i-1])`` (selling climax,
   a strict new ``length``-bar low). The strict comparison against the *prior* window means a
   flat/ranging stretch never qualifies — a directional move must precede the bar.

Every test uses trailing windows only (``SMA`` with ``min_periods == length``; a ``shift(1)``
before the rolling extreme), so the flag is **causal** (no look-ahead) and is ``0`` during the
warm-up: ``SMA`` is NaN there, and ``value > NaN`` is ``False`` -> ``0`` (never NaN). The
output is therefore finite everywhere and strictly ``{0.0, 1.0}``. See
``ref/ta_docs/volume/misc_volume.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
)


def vpa_climactic_bars(
    df: pd.DataFrame,
    length: int = 20,
    vol_k: float = 2.0,
    range_k: float = 1.5,
) -> pd.Series:
    """VSA climactic-bar flag (0/1) over ``df`` (high/low/close/volume).

    Returns ``1.0`` on an ultra-high-volume, wide-spread bar that prints a strict new
    ``length``-bar high or low close (a buying / selling climax), else ``0.0``. Uses only
    trailing windows, so the flag is causal and ``0`` (never NaN) throughout the warm-up.
    """
    rng = df[HIGH] - df[LOW]

    # 1) ultra-high volume vs its trailing average; 2) wide spread vs its trailing average.
    # SMA(min_periods == length) is NaN during warm-up, and ``x > NaN`` is False -> flag 0.
    high_volume = df[VOLUME] > vol_k * sma(df[VOLUME], length)
    wide_spread = rng > range_k * sma(rng, length)

    # 3) strict new extreme close over the PRIOR length-bar window (shift(1) excludes the
    # current bar) -> guarantees a directional move preceded the climax.
    prior = df[CLOSE].shift(1)
    prior_max = prior.rolling(length, min_periods=length).max()
    prior_min = prior.rolling(length, min_periods=length).min()
    new_extreme = (df[CLOSE] > prior_max) | (df[CLOSE] < prior_min)

    flag = high_volume & wide_spread & new_extreme
    return flag.astype("float64")


@INDICATORS.register
class VPAClimacticBars(Indicator):
    """VPA Climactic Bars.

    What: a Volume Spread Analysis "climax" flag (1/0) — an ultra-high-volume, wide-spread bar
    that makes a strict new ``length``-bar high or low close (buying / selling climax, the
    exhaustion of a move).
    Best settings: ``length`` 20, ``vol_k`` 2.0 (volume > 2x average), ``range_k`` 1.5 (spread
    > 1.5x average); loosen ``vol_k``/``range_k`` for noisier instruments.
    Edge cases: warm-up and non-climax bars are ``0`` (never NaN); output is strictly {0, 1};
    a flat/ranging series never fires (the new-extreme test is strict against the prior window).
    Parity: no reference-library oracle — golden-tested on hand-built frames against the
    closed-form VSA rule (Williams / Coulling).
    """

    spec = IndicatorSpec(
        name="vpa_climactic_bars",
        category="volume",
        aliases=("VPA Climactic Bars", "VSA Climax Bar", "Climactic Volume Bar"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vpa_climactic_bars",),
        bounds={"vpa_climactic_bars": (0.0, 1.0)},
        references=("Williams Master the Markets", "Coulling Volume Price Analysis"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=2)
        vol_k: float = Field(default=2.0, gt=0)
        range_k: float = Field(default=1.5, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return vpa_climactic_bars(df, p["length"], p["vol_k"], p["range_k"])
