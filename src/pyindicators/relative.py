"""Relative-strength indicators (per-symbol, causal).

This module bundles the classic relative-strength family used to gauge whether a
stock is leading or lagging the broad market: ``rs_line`` (the raw price-relative
line), ``mansfield_rs`` (Stan Weinstein's zero-centered, MA-normalized version of
that line), and ``rs_rating`` (the IBD/William O'Neil multi-period weighted return
that screeners later rank into a 1-99 percentile). All three measure performance of
one symbol relative to a reference -- a benchmark for the first two, the symbol's own
past for the last.

These stay strictly per-symbol so the look-ahead meta-test applies to them. The
universe-wide *ranking* of ``rs_rating`` into a 1-99 percentile is a Phase-3 *screener*
concern, not an indicator concern.

``rs_line`` and ``mansfield_rs`` are relative to a benchmark. The benchmark close series
is injected at construction by the screener (``RSLine(benchmark_close=spy_close)``);
with no benchmark they degrade to a valid, causal, degenerate series (ratio == 1) so the
generic instantiate/compute/causal tests pass with defaults.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import Indicator
from .common import build_output, require_columns
from .registry import INDICATORS


def _ratio_to_benchmark(df: pd.DataFrame, benchmark_close: pd.Series | None) -> pd.Series:
    if benchmark_close is None:
        return pd.Series(1.0, index=df.index)
    bench = np.asarray(benchmark_close, dtype="float64")
    if len(bench) != len(df):
        raise ValueError(
            f"benchmark_close length {len(bench)} != frame length {len(df)}; "
            "align the benchmark to the symbol frame before constructing the indicator"
        )
    return pd.Series(df["close"].to_numpy() / bench, index=df.index)


@INDICATORS.register("rs_line")
class RSLine(Indicator):
    """Price-relative (RS) line: close divided by a benchmark's close; rising == leading.

    What it is:
        The relative-strength line, the most basic measure of leadership: a stock's
        price expressed as a ratio to a market benchmark (typically SPY or the S&P
        500). A staple of point-and-figure and CAN SLIM style analysis, it strips out
        the market's direction so only relative performance remains.

    How it works:
        At each bar it divides the symbol's close by the benchmark's close on the same
        bar: rs_line = close / benchmark_close. The absolute level is arbitrary (it
        depends on the two price scales); only its direction and slope matter. With no
        benchmark injected, the series degrades to a constant 1.0.

    Best settings:
        The only parameter is ``benchmark``, an informational label (default "SPY")
        identifying the reference index; the actual benchmark close series is supplied
        at construction. Use a broad-market index for general leadership, or a sector
        ETF to judge a stock against its peers. No smoothing window is applied.

    Interpretation:
        A rising line means the stock is outperforming the benchmark; a falling line
        means it is lagging. New highs in the RS line, especially while price is still
        basing, flag emerging leaders. Pitfall: the raw level carries no meaning across
        symbols, so compare slope and new highs, not one stock's ratio to another's.

    Outputs:
        rs_line -- close / benchmark_close; an arbitrary-scale ratio whose slope shows
        relative leadership versus the benchmark.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: O'Neil, How to Make Money in Stocks (CAN SLIM); standard price-relative line.
    """

    name = "rs_line"
    outputs = ("rs_line",)

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        benchmark: str = Field(default="SPY")  # informational symbol label

    params_model = Params

    def __init__(self, *, benchmark_close: pd.Series | None = None, **params):
        super().__init__(**params)
        self._benchmark = benchmark_close

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        return build_output(df.index, {"rs_line": _ratio_to_benchmark(df, self._benchmark)})


@INDICATORS.register("mansfield_rs")
class MansfieldRS(Indicator):
    """Mansfield Relative Strength: the price-relative line normalized to a zero line.

    What it is:
        Stan Weinstein's relative-strength measure (popularized in "Secrets for
        Profiting in Bull and Bear Markets" and credited to Mansfield charts). It
        rebases the raw price-relative line around zero so leadership can be read as a
        simple positive/negative reading rather than an arbitrary ratio level.

    How it works:
        It takes the price-relative ratio RP = close / benchmark_close, divides it by
        its own simple moving average over ``period`` bars, subtracts 1, and scales by
        100: mansfield_rs = (RP / SMA(RP, period) - 1) * 100. Values above zero mean RP
        sits above its average (outperforming lately); below zero means underperforming.

    Best settings:
        ``period`` defaults to 52 (one year of weekly bars), Weinstein's classic
        setting for stage analysis on weekly charts; it must be >= 2. Shorten it (for
        example to ~26) for faster, noisier signals or to adapt to daily data. The
        ``benchmark`` label (default "SPY") names the reference; its close is injected
        at construction.

    Interpretation:
        Crossings of the zero line are the key signal: rising through zero marks a shift
        into market leadership (Weinstein's Stage 2), dropping below zero marks lagging.
        The distance from zero gauges the strength of out/under-performance. Pitfall: as
        a normalized oscillator it can whipsaw around zero in choppy, trendless markets.

    Outputs:
        mansfield_rs -- zero-centered relative strength, (RP / SMA(RP, period) - 1) *
        100; positive == leading the benchmark, negative == lagging.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Weinstein, Secrets for Profiting in Bull and Bear Markets (1988); Mansfield RS.
    """

    name = "mansfield_rs"
    outputs = ("mansfield_rs",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=52, ge=2)
        benchmark: str = Field(default="SPY")

    params_model = Params

    def __init__(self, *, benchmark_close: pd.Series | None = None, **params):
        super().__init__(**params)
        self._benchmark = benchmark_close

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        rp = _ratio_to_benchmark(df, self._benchmark)
        ma = rp.rolling(p, min_periods=p).mean()
        return build_output(df.index, {"mansfield_rs": (rp / ma - 1.0) * 100.0})


@INDICATORS.register("rs_rating")
class RSRating(Indicator):
    """Per-symbol weighted trailing return (IBD/O'Neil style RS), pre-ranking.

    What it is:
        The raw input to an IBD-style Relative Strength Rating, in the tradition of
        William O'Neil's Investor's Business Daily. It condenses a stock's own
        multi-quarter price performance into a single number; this class emits that raw
        number and leaves the cross-universe ranking to the screener.

    How it works:
        For each lookback it computes a trailing return, close / close.shift(lb) - 1,
        then takes a weighted average across the lookbacks: acc = sum(w * return) and
        the output is acc / sum(weights). Recent periods carry more weight, so the most
        recent quarter dominates the blended return. It is purely per-symbol -- no
        benchmark and no cross-sectional comparison happen here.

    Best settings:
        ``lookbacks`` defaults to [63, 126, 189, 252] trading days (about 3, 6, 9, and
        12 months) with ``weights`` [2.0, 1.0, 1.0, 1.0], the classic front-weighted
        2:1:1:1 scheme emphasizing the latest quarter. The two lists must be the same
        non-empty length; shorten the lookbacks for faster markets or reweight to tune
        recency emphasis.

    Interpretation:
        Higher values mean stronger trailing performance; the screener then maps the
        raw value to a 1-99 percentile across the universe (99 = top 1%, leaders worth
        watching). Pitfall: the raw number is only meaningful relative to other symbols
        -- always interpret it after the cross-sectional ranking, not on its own.

    Outputs:
        rs_rating -- weights-normalized blend of trailing returns over the configured
        lookbacks; higher == stronger recent performance, pre-ranking.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: O'Neil / Investor's Business Daily Relative Strength Rating methodology.
    """

    name = "rs_rating"
    outputs = ("rs_rating",)

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        lookbacks: list[int] = Field(default_factory=lambda: [63, 126, 189, 252])
        weights: list[float] = Field(default_factory=lambda: [2.0, 1.0, 1.0, 1.0])

        @model_validator(mode="after")
        def _check(self):
            if len(self.lookbacks) != len(self.weights):
                raise ValueError("rs_rating: lookbacks and weights must be the same length")
            if not self.lookbacks:
                raise ValueError("rs_rating: need at least one lookback")
            return self

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        lookbacks = self.params["lookbacks"]
        weights = self.params["weights"]
        close = df["close"]
        total_w = float(sum(weights))
        acc = pd.Series(0.0, index=df.index)
        for lb, w in zip(lookbacks, weights, strict=True):
            acc = acc + w * (close / close.shift(lb) - 1.0)
        return build_output(df.index, {"rs_rating": acc / total_w})
