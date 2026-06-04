"""Real-data, multi-library parity sweep.

Two guarantees the synthetic parity tests cannot give on their own:
  1. **Real market data** — every check runs on a committed fixture of genuine daily AAPL
     OHLCV (real gaps, real volume, real volatility), not a synthetic random walk.
  2. **>= 3 independent libraries** — each core indicator is cross-checked against every
     reference implementation that ships it (TA-Lib, pandas-ta, finta, bukosabino/ta). Because
     we hand-roll every formula, agreement across several independent libraries on real data is
     the strongest evidence the math is right. ``agree(strict=True)`` enforces at least three.

Known, documented divergences are excluded per-indicator with a comment (e.g. finta's ATR is a
non-Wilder variant; finta/ta seed EMA/RSI differently and only converge on the tail), never
silently.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")  # primary oracle; this module needs it

try:  # optional extra oracles — included when present
    from finta import TA as FINTA
except Exception:  # pragma: no cover - import guard
    FINTA = None
try:
    import ta as TA2
except Exception:  # pragma: no cover - import guard
    TA2 = None
try:
    import pandas_ta_classic as PTA
except Exception:  # pragma: no cover - import guard
    PTA = None

DF = real_frame()
H, L, C, V = DF["high"], DF["low"], DF["close"], DF["volume"]
HA, LA, CA = H.to_numpy(), L.to_numpy(), C.to_numpy()


def _collect(builders):
    """Build {lib_name: ref_series} from (lib_obj, name, thunk) entries that are available."""
    refs = {}
    for lib, name, thunk in builders:
        if lib is not None:
            refs[name] = thunk()
    return refs


def agree(our, refs, *, rtol=1e-6, atol=1e-6, tail=None, min_overlap=50, strict=True):
    """Assert ``our`` matches every reference in ``refs`` ({lib_name: series}) on real data."""
    if strict:
        assert len(refs) >= 3, f"need >= 3 libraries, have {sorted(refs)}"
    our = np.asarray(our, dtype="float64")
    for name, ref in refs.items():
        ref = np.asarray(ref, dtype="float64")
        a, b = (our, ref) if tail is None else (our[-tail:], ref[-tail:])
        mask = np.isfinite(a) & np.isfinite(b)
        assert mask.sum() >= min_overlap, f"{name}: too few comparable points"
        np.testing.assert_allclose(a[mask], b[mask], rtol=rtol, atol=atol,
                                   err_msg=f"{name} disagrees on real data")


def test_sma_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.SMA(CA, 10)),
        (FINTA, "finta", lambda: FINTA.SMA(DF, period=10)),
        (TA2, "ta", lambda: TA2.trend.sma_indicator(C, window=10)),
        (PTA, "pandas_ta", lambda: PTA.sma(C, length=10)),
    ])
    agree(INDICATORS.create("sma", length=10).compute(DF)["sma"], refs)


def test_ema_real_multi():
    # finta/ta seed the EMA recursion differently (adjust=True / first-value) so they only
    # converge with the SMA-seeded family (TA-Lib, pandas-ta, ours) on the tail.
    refs = _collect([
        (talib, "talib", lambda: talib.EMA(CA, 10)),
        (FINTA, "finta", lambda: FINTA.EMA(DF, period=10)),
        (TA2, "ta", lambda: TA2.trend.ema_indicator(C, window=10)),
        (PTA, "pandas_ta", lambda: PTA.ema(C, length=10)),
    ])
    agree(INDICATORS.create("ema", length=10).compute(DF)["ema"], refs, tail=200, rtol=1e-5)


def test_wma_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.WMA(CA, 10)),
        (FINTA, "finta", lambda: FINTA.WMA(DF, period=10)),
        (TA2, "ta", lambda: TA2.trend.wma_indicator(C, window=10)),
        (PTA, "pandas_ta", lambda: PTA.wma(C, length=10)),
    ])
    agree(INDICATORS.create("wma", length=10).compute(DF)["wma"], refs)


def test_rsi_real_multi():
    # Wilder RSI: finta/ta converge with the SMA-seeded family only after the warm-up.
    refs = _collect([
        (talib, "talib", lambda: talib.RSI(CA, 14)),
        (FINTA, "finta", lambda: FINTA.RSI(DF, period=14)),
        (TA2, "ta", lambda: TA2.momentum.rsi(C, window=14)),
        (PTA, "pandas_ta", lambda: PTA.rsi(C, length=14)),
    ])
    agree(INDICATORS.create("rsi", length=14).compute(DF)["rsi"], refs, tail=200, rtol=1e-5)


def test_cci_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.CCI(HA, LA, CA, 14)),
        (FINTA, "finta", lambda: FINTA.CCI(DF, period=14)),
        (TA2, "ta", lambda: TA2.trend.cci(H, L, C, window=14)),
        (PTA, "pandas_ta", lambda: PTA.cci(H, L, C, length=14)),
    ])
    agree(INDICATORS.create("cci", length=14).compute(DF)["cci"], refs)


def test_willr_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.WILLR(HA, LA, CA, 14)),
        (TA2, "ta", lambda: TA2.momentum.williams_r(H, L, C, lbp=14)),
        (PTA, "pandas_ta", lambda: PTA.willr(H, L, C, length=14)),
    ])
    agree(INDICATORS.create("willr", length=14).compute(DF)["willr"], refs)


def test_roc_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.ROC(CA, 10)),
        (TA2, "ta", lambda: TA2.momentum.roc(C, window=10)),
        (PTA, "pandas_ta", lambda: PTA.roc(C, length=10)),
    ])
    agree(INDICATORS.create("roc", length=10).compute(DF)["roc"], refs)


def test_atr_real_multi():
    # finta's ATR is a non-Wilder variant -> excluded; TA-Lib/ta/pandas-ta are Wilder and
    # converge with ours on the tail.
    refs = _collect([
        (talib, "talib", lambda: talib.ATR(HA, LA, CA, 14)),
        (TA2, "ta", lambda: TA2.volatility.average_true_range(H, L, C, window=14)),
        (PTA, "pandas_ta", lambda: PTA.atr(H, L, C, length=14)),
    ])
    agree(INDICATORS.create("atr", length=14).compute(DF)["atr"], refs, tail=200, rtol=1e-3)
