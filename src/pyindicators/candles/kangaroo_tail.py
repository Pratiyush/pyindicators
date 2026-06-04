"""Kangaroo Tail — Nial Fuller long-tailed pin bar (structural, magnitude ±100).

A **Kangaroo Tail** (Nial Fuller's name for a pin bar / Pinocchio bar) is a single rejection
candle with one very long shadow — "the tail" — a small real body pushed to the opposite end,
and a negligible shadow on the body side ("the nose"). The tail pokes **beyond the recent
trading range** intrabar and price then **closes back inside** it, leaving a long wick that
marks a failed probe and a likely reversal.

* a **bearish** kangaroo tail (``-100``) has a long **upper** tail: the bar's high pierces the
  prior ``N``-bar high, but the close (and open) fall back below that level — buyers were
  rejected from above.
* a **bullish** kangaroo tail (``+100``) is the mirror: a long **lower** tail whose low pierces
  the prior ``N``-bar low while the close (and open) reclaim it — sellers were rejected from
  below.
* ``0`` otherwise.

There is **no TA-Lib / pandas-ta / finta / ta oracle** for this pattern (all four were checked
— only ``CDLSPINNINGTOP`` coincidentally matches a "pin" substring), so it is pinned to an
explicit, documented closed-form rule (golden-tested; the parity file carries an independent
re-derivation plus the structural assertions, the role a reference comparison plays elsewhere).

The rule at bar ``i`` with window ``length = N`` and ``tail_mult = m`` (the recent range is the
**prior** ``N`` bars, EXCLUSIVE of the current bar, so the signal is strictly causal — no
look-ahead). Let::

    body        = |close(i) - open(i)|
    upper_tail  = high(i) - max(open(i), close(i))     # the wick above the body
    lower_tail  = min(open(i), close(i)) - low(i)      # the wick below the body
    prior_high  = max(high[i-N .. i-1])                # recent range top
    prior_low   = min(low [i-N .. i-1])                # recent range bottom

    bearish (-100):  upper_tail >= m * body
                 AND upper_tail >= m * lower_tail      # tail dominates the nose
                 AND high(i)  >  prior_high            # pokes beyond recent range
                 AND close(i) <  prior_high            # ...and closes back inside
                 AND open (i) <  prior_high            # ...with the body inside too

    bullish (+100):  lower_tail >= m * body
                 AND lower_tail >= m * upper_tail
                 AND low (i)  <  prior_low
                 AND close(i) >  prior_low
                 AND open (i) >  prior_low

    else 0

The two tail-length comparisons use ``>=`` (a tail exactly ``m``× the body/nose still
qualifies); the *poke* and *reclaim* comparisons are **strict** (``<`` / ``>``) — merely
touching the prior extreme, or closing exactly on it, is not a rejection. ``tail_mult`` is
constrained to ``> 1``: this makes a bearish and a bullish tail **mutually exclusive** on the
same bar (the two ``tail >= m * other_tail`` conditions together force ``upper_tail`` and
``lower_tail`` both to 0, which with ``tail >= m * body`` forces the body to 0 as well — a flat
bar, which then fails both strict poke tests), so the output is always exactly one of
``{-100, 0, 100}``. A flat/constant series never fires (``x < x`` / ``x > x`` are ``False``).
During the warm-up (the first ``N`` bars the rolling window is not yet full) the prior
high/low are ``NaN`` so every comparison is ``False``; those bars are emitted as ``0`` (not
``NaN``) so the column is finite after warm-up and the result is truncation-invariant.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def kangaroo_tail(df: pd.DataFrame, length: int = 20, tail_mult: float = 2.0) -> pd.Series:
    """Kangaroo Tail (Nial Fuller pin bar) over ``df`` (OHLC) as a -100/0/100 ``Series``.

    ``-100`` for a bearish tail (long upper wick poking above the prior ``length``-bar high with
    the body closing back below it), ``+100`` for a bullish tail (long lower wick poking below
    the prior ``length``-bar low with the body reclaiming it), ``0`` otherwise. The tail must be
    at least ``tail_mult`` times both the real body and the opposite wick. The first ``length``
    bars are ``0`` (warm-up). See the module docstring for the exact closed-form rule.
    """
    open_ = df[OPEN].to_numpy(dtype="float64")
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")

    body = np.abs(close - open_)
    body_top = np.maximum(open_, close)
    body_bottom = np.minimum(open_, close)
    upper_tail = high - body_top
    lower_tail = body_bottom - low

    # Recent range = the N bars ENDING AT i-1 (current bar excluded): a closed rolling extreme
    # that requires a full window, shifted out by one bar. NaN until the window fills -> every
    # comparison below is False during the warm-up.
    prior_high = df[HIGH].rolling(window=length, min_periods=length).max().shift(1).to_numpy()
    prior_low = df[LOW].rolling(window=length, min_periods=length).min().shift(1).to_numpy()

    bearish = (
        (upper_tail >= tail_mult * body)
        & (upper_tail >= tail_mult * lower_tail)
        & (high > prior_high)  # pokes beyond the recent range
        & (close < prior_high)  # ...and closes back inside
        & (open_ < prior_high)  # ...with the body inside too
    )
    bullish = (
        (lower_tail >= tail_mult * body)
        & (lower_tail >= tail_mult * upper_tail)
        & (low < prior_low)
        & (close > prior_low)
        & (open_ > prior_low)
    )

    out = np.where(bearish, -100.0, np.where(bullish, 100.0, 0.0))
    out[:length] = 0.0  # warm-up: prior range undefined for the first ``length`` bars
    return pd.Series(out, index=df.index)


@INDICATORS.register
class KangarooTail(Indicator):
    """Kangaroo Tail (Nial Fuller pin bar) pattern.

    What: a single rejection candle with one long shadow (the tail) at least ``tail_mult``× the
    real body and the opposite shadow, whose tail pierces the recent trading range but whose body
    closes back inside it. ``-100`` = bearish (long upper tail poking above the prior-``N``
    rolling high, body reclaimed below it); ``+100`` = bullish (long lower tail poking below the
    prior-``N`` rolling low, body reclaimed above it); ``0`` otherwise.
    Best settings: ``length`` 20 (a month of daily range), ``tail_mult`` 2.0 (Fuller's "tail at
    least twice the body"). The tail-length tests use ``>=``; the poke/reclaim tests are strict.
    Edge cases: first ``length`` bars are 0 (warm-up); a flat/constant series never fires;
    ``tail_mult > 1`` makes bullish and bearish mutually exclusive, so the output is exactly one
    of {-100, 0, 100}.
    Parity: no TA-Lib/pandas-ta/finta/ta oracle — pinned to the documented closed-form rule
    (golden + independent structural re-derivation).
    """

    class Params(BaseModel):
        """Parameters for Kangaroo Tail (recent-range lookback + tail/body ratio)."""

        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        tail_mult: float = Field(default=2.0, gt=1.0)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="kangaroo_tail",
        category="candles",
        aliases=("Kangaroo Tail", "Pin Bar", "Pinocchio Bar"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("kangaroo_tail",),
        bounds={"kangaroo_tail": (-100.0, 100.0)},
        talib_compatible=False,
        references=("Nial Fuller (Kangaroo Tail / pin bar)",),
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return kangaroo_tail(df[list(self.spec.inputs)], self.params["length"], self.params["tail_mult"])
