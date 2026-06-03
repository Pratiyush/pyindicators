"""Relative-strength indicators (per-symbol, causal).

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
    """Price relative: ``close / benchmark_close`` (rising == outperforming)."""

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
    """Mansfield Relative Strength (Weinstein): the price-relative line normalized by its
    own moving average, ``(RP / SMA(RP, period) - 1) * 100`` (zero-line crossings)."""

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
    """Per-symbol weighted trailing return (IBD/O'Neil style RS, pre-ranking).

    Emits the raw weighted return; the screener converts it to a 1-99 cross-universe
    percentile. Default weighting emphasizes the most recent quarter (2:1:1:1 over
    63/126/189/252 trading-day lookbacks).
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
