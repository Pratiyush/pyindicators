"""Real-data parity for the recently-built advanced indicators.

Most of these ship in only ONE reference library (pandas-ta), so the >= 3-library rule of
``test_real_multi`` cannot apply; here we validate them on genuine market data against every
oracle that does implement them (pandas-ta always; TA-Lib for the DM / Aroon / Stochastic
family). Combined with each indicator's golden + edge + registry meta-tests, this confirms the
formulas hold on real price action, not just the synthetic walk.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

try:
    import talib
except Exception:  # pragma: no cover - import guard
    talib = None

DF = real_frame()
H, L, C, OPN, V = DF["high"], DF["low"], DF["close"], DF["open"], DF["volume"]
HA, LA, CA = H.to_numpy(), L.to_numpy(), C.to_numpy()


def chk(our, ref, *, rtol=1e-6, atol=1e-6, tail=None, min_overlap=50):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)  # some libs drop leading NaN rows -> align on the trailing end
    our, ref = our[-n:], ref[-n:]
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_vidya_real():
    chk(INDICATORS.create("vidya", length=14).compute(DF)["vidya"], pta.vidya(C, length=14))


def test_mcgd_real():
    chk(INDICATORS.create("mcgd", length=10).compute(DF)["mcgd"], pta.mcgd(C, length=10))


def test_ssf_real():
    chk(INDICATORS.create("ssf", length=10, poles=2).compute(DF)["ssf"],
        pta.ssf(C, length=10, poles=2))


def test_hwma_real():
    chk(INDICATORS.create("hwma").compute(DF)["hwma"], pta.hwma(C))


def test_pvo_real():
    chk(INDICATORS.create("pvo").compute(DF)["pvo"], pta.pvo(V).iloc[:, 0])


def test_kdj_real():
    # Wilder seed differs through the warm-up -> tail (see test_parity_stochf_pvo_kdj).
    chk(INDICATORS.create("kdj").compute(DF)["kdj_k"], pta.kdj(H, L, C).iloc[:, 0],
        tail=300, rtol=1e-5)


def test_fisher_real():
    chk(INDICATORS.create("fisher").compute(DF)["fisher"],
        pta.fisher(H, L, length=9, signal=1).iloc[:, 0])


def test_rvgi_real():
    chk(INDICATORS.create("rvgi").compute(DF)["rvgi"], pta.rvgi(OPN, H, L, C).iloc[:, 1])


def test_thermo_real():
    chk(INDICATORS.create("thermo").compute(DF)["thermo"],
        pta.thermo(H, L, length=20, mamode="ema", long=2, short=0.5).iloc[:, 0])


def test_rvi_real():
    chk(INDICATORS.create("rvi", length=14).compute(DF)["rvi"], pta.rvi(C, length=14))


def test_amat_real():
    ref = pta.amat(C, fast=8, slow=21, lookback=2, mamode="ema")
    out = INDICATORS.create("amat").compute(DF)
    chk(out["amat_lr"], ref.iloc[:, 0])
    chk(out["amat_sr"], ref.iloc[:, 1])


def test_plus_minus_dm_real():
    # pandas-ta matches exactly; TA-Lib differs only by the Wilder seed -> tail.
    chk(INDICATORS.create("plus_dm", length=14).compute(DF)["plus_dm"], pta.plus_dm(H, L, length=14))
    chk(INDICATORS.create("minus_dm", length=14).compute(DF)["minus_dm"],
        pta.minus_dm(H, L, length=14))
    if talib is not None:
        chk(INDICATORS.create("plus_dm", length=14).compute(DF)["plus_dm"],
            talib.PLUS_DM(HA, LA, 14), tail=200, rtol=1e-3)


def test_aroon_osc_real():
    # TA-Lib AROONOSC is the authoritative oracle; pandas-ta's aroon uses a different lookback
    # window (off-by-one vs TA-Lib), so it is intentionally not used here.
    osc = INDICATORS.create("aroon_osc", length=25).compute(DF)["aroon_osc"]
    talib_ = pytest.importorskip("talib")
    chk(osc, talib_.AROONOSC(HA, LA, timeperiod=25))


def test_stochf_real():
    out = INDICATORS.create("stochf", k=14, d=3).compute(DF)
    ref = pta.stoch(H, L, C, k=14, d=3, smooth_k=1)
    chk(out["stochf_k"], ref.iloc[:, 0])
    chk(out["stochf_d"], ref.iloc[:, 1])
    if talib is not None:
        fastk, fastd = talib.STOCHF(HA, LA, CA, fastk_period=14, fastd_period=3, fastd_matype=0)
        chk(out["stochf_k"], fastk)
        chk(out["stochf_d"], fastd)
