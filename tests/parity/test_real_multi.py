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
HA, LA, CA, VA = H.to_numpy(), L.to_numpy(), C.to_numpy(), V.to_numpy()


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


def test_mfi_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.MFI(HA, LA, CA, VA, 14)),
        (FINTA, "finta", lambda: FINTA.MFI(DF, period=14)),
        (TA2, "ta", lambda: TA2.volume.money_flow_index(H, L, C, V, window=14)),
        (PTA, "pandas_ta", lambda: PTA.mfi(H, L, C, V, length=14)),
    ])
    agree(INDICATORS.create("mfi", length=14).compute(DF)["mfi"], refs)


def test_ad_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.AD(HA, LA, CA, VA)),
        (FINTA, "finta", lambda: FINTA.ADL(DF)),
        (PTA, "pandas_ta", lambda: PTA.ad(H, L, C, V)),
    ])
    agree(INDICATORS.create("ad").compute(DF)["ad"], refs)


def test_dema_real_multi():
    # DEMA chains EMAs; finta seeds differently -> all three converge on the tail.
    refs = _collect([
        (talib, "talib", lambda: talib.DEMA(CA, 20)),
        (FINTA, "finta", lambda: FINTA.DEMA(DF, period=20)),
        (PTA, "pandas_ta", lambda: PTA.dema(C, length=20)),
    ])
    agree(INDICATORS.create("dema", length=20).compute(DF)["dema"], refs, tail=200, rtol=1e-4)


# --- additional >=3-library cross-checks (each verified to agree on real AAPL) -------------

def test_tema_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.TEMA(CA, 20)),
        (FINTA, "finta", lambda: FINTA.TEMA(DF, period=20)),
        (PTA, "pandas_ta", lambda: PTA.tema(C, length=20)),
    ])
    agree(INDICATORS.create("tema", length=20).compute(DF)["tema"], refs, tail=200, rtol=1e-4)


def test_kama_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.KAMA(CA, 10)),
        (TA2, "ta", lambda: TA2.momentum.kama(C, window=10)),
        (PTA, "pandas_ta", lambda: PTA.kama(C, length=10)),
    ])
    agree(INDICATORS.create("kama", length=10).compute(DF)["kama"], refs, rtol=1e-5)


def test_mom_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.MOM(CA, 10)),
        (FINTA, "finta", lambda: FINTA.MOM(DF, period=10)),
        (PTA, "pandas_ta", lambda: PTA.mom(C, length=10)),
    ])
    agree(INDICATORS.create("mom", length=10).compute(DF)["mom"], refs)


def test_true_range_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.TRANGE(HA, LA, CA)),
        (FINTA, "finta", lambda: FINTA.TR(DF)),
        (PTA, "pandas_ta", lambda: PTA.true_range(H, L, C)),
    ])
    agree(INDICATORS.create("true_range").compute(DF)["true_range"], refs)


def test_bop_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.BOP(DF["open"].to_numpy(), HA, LA, CA)),
        (FINTA, "finta", lambda: FINTA.BOP(DF)),
        (PTA, "pandas_ta", lambda: PTA.bop(DF["open"], H, L, C)),
    ])
    agree(INDICATORS.create("bop").compute(DF)["bop"], refs)


def test_macd_real_multi():
    # finta/ta seed the EMAs differently -> all four converge on the tail.
    refs = _collect([
        (talib, "talib", lambda: talib.MACD(CA, 12, 26, 9)[0]),
        (FINTA, "finta", lambda: FINTA.MACD(DF)["MACD"]),
        (TA2, "ta", lambda: TA2.trend.MACD(C, window_slow=26, window_fast=12, window_sign=9).macd()),
        (PTA, "pandas_ta", lambda: PTA.macd(C, fast=12, slow=26, signal=9).iloc[:, 0]),
    ])
    agree(INDICATORS.create("macd", fast=12, slow=26, signal=9).compute(DF)["macd"], refs, tail=200, rtol=1e-4)


def test_trix_real_multi():
    refs = _collect([
        (talib, "talib", lambda: talib.TRIX(CA, 18)),
        (TA2, "ta", lambda: TA2.trend.trix(C, window=18)),
        (PTA, "pandas_ta", lambda: PTA.trix(C, length=18).iloc[:, 0]),
    ])
    agree(INDICATORS.create("trix", length=18).compute(DF)["trix"], refs, tail=200, rtol=1e-3)


def test_adx_real_multi():
    # ADX is a Wilder double-smoothing; the three converge on the tail.
    refs = _collect([
        (talib, "talib", lambda: talib.ADX(HA, LA, CA, 14)),
        (TA2, "ta", lambda: TA2.trend.adx(H, L, C, window=14)),
        (PTA, "pandas_ta", lambda: PTA.adx(H, L, C, length=14).iloc[:, 0]),
    ])
    agree(INDICATORS.create("adx", length=14).compute(DF)["adx"], refs, tail=200, rtol=1e-2)


def test_vortex_real_multi():
    refs = _collect([
        (FINTA, "finta", lambda: FINTA.VORTEX(DF, period=14)["VIp"]),
        (TA2, "ta", lambda: TA2.trend.vortex_indicator_pos(H, L, C, window=14)),
        (PTA, "pandas_ta", lambda: PTA.vortex(H, L, C, length=14).iloc[:, 0]),
    ])
    agree(INDICATORS.create("vortex", length=14).compute(DF)["vi_plus"], refs, rtol=1e-4)


def test_bbands_real_multi():
    # Compare the middle band (SMA) where all three libraries are exact.
    refs = _collect([
        (talib, "talib", lambda: talib.BBANDS(CA, 20, 2, 2)[1]),
        (FINTA, "finta", lambda: FINTA.BBANDS(DF, period=20)["BB_MIDDLE"]),
        (PTA, "pandas_ta", lambda: PTA.bbands(C, length=20, std=2).iloc[:, 1]),
    ])
    agree(INDICATORS.create("bbands", length=20).compute(DF)["bb_middle"], refs)


def test_ichimoku_real_multi():
    # Tenkan-sen (conversion line) is unambiguous across libraries.
    refs = _collect([
        (FINTA, "finta", lambda: FINTA.ICHIMOKU(DF)["TENKAN"]),
        (TA2, "ta", lambda: TA2.trend.IchimokuIndicator(H, L, window1=9, window2=26, window3=52).ichimoku_conversion_line()),
        (PTA, "pandas_ta", lambda: PTA.ichimoku(H, L, C)[0].iloc[:, 2]),
    ])
    agree(INDICATORS.create("ichimoku").compute(DF)["tenkan"], refs)


def test_psar_real_multi():
    # finta's SAR is a documented variant -> excluded; TA-Lib/ta/pandas-ta agree exactly.
    refs = _collect([
        (talib, "talib", lambda: talib.SAR(HA, LA, 0.02, 0.2)),
        (TA2, "ta", lambda: TA2.trend.PSARIndicator(H, L, C, step=0.02, max_step=0.2).psar()),
        (PTA, "pandas_ta", lambda: PTA.psar(H, L, C, af0=0.02, max_af=0.2).iloc[:, 0].fillna(
            PTA.psar(H, L, C, af0=0.02, max_af=0.2).iloc[:, 1])),
    ])
    agree(INDICATORS.create("psar", af0=0.02, max_af=0.2).compute(DF)["psar"], refs, tail=200, rtol=1e-4)


def test_tsi_real_multi():
    refs = _collect([
        (FINTA, "finta", lambda: FINTA.TSI(DF, long=25, short=13)["TSI"]),
        (TA2, "ta", lambda: TA2.momentum.tsi(C, window_slow=25, window_fast=13)),
        (PTA, "pandas_ta", lambda: PTA.tsi(C, fast=13, slow=25).iloc[:, 0]),
    ])
    agree(INDICATORS.create("tsi", long=25, short=13, signal=7).compute(DF)["tsi"], refs, tail=200, rtol=1e-4)


def test_kst_real_multi():
    # pandas-ta scales KST by 100 (non-standard) -> divided back to the StockCharts/ta convention.
    refs = _collect([
        (FINTA, "finta", lambda: FINTA.KST(DF)["KST"]),
        (TA2, "ta", lambda: TA2.trend.kst(C)),
        (PTA, "pandas_ta", lambda: PTA.kst(C).iloc[:, 0] / 100.0),
    ])
    agree(INDICATORS.create("kst").compute(DF)["kst"], refs, tail=200, rtol=1e-3)
