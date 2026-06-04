"""trend/ — moving averages and directional/trend systems."""

from __future__ import annotations

from .adx import ADX, directional_movement
from .adxr import ADXR, adxr
from .alma import ALMA, alma
from .amat import AMAT, amat
from .apo import APO, apo
from .aroon import Aroon, aroon
from .aroon_osc import AroonOscillator, aroon_osc
from .chop import Choppiness, chop
from .cksp import CKSP, cksp
from .decreasing import Decreasing, decreasing
from .dema import DEMA, dema
from .dpo import DPO, dpo
from .dx import DX, dx
from .evwma import EVWMA, evwma
from .fama import FAMA, fama
from .frama import FRAMA, frama
from .fwma import FWMA, fwma
from .hilo import HiLo, hilo
from .hma import HMA, hma
from .hwma import HWMA, hwma
from .ichimoku import Ichimoku, ichimoku
from .increasing import Increasing, increasing
from .jma import JMA, jma
from .kama import KAMA, kama
from .kst import KST, kst
from .long_run import LongRun, long_run
from .lsma import LSMA, lsma
from .ma_spread import MASpread, ma_spread
from .macd import MACD, macd
from .macdext import MACDEXT, macdext
from .macdfix import MACDFIX, macdfix
from .mama import MAMA, mama
from .mcgd import McGinleyDynamic, mcgd
from .minus_di import MinusDI, minus_di
from .minus_dm import MinusDM, minus_dm
from .pivots import Pivots, pivots
from .plus_di import PlusDI, plus_di
from .plus_dm import PlusDM, plus_dm
from .pmax import PMax, pmax
from .ppo import PPO, ppo
from .psar import PSAR, psar
from .pwma import PWMA, pwma
from .qstick import QStick, qstick
from .rainbow import Rainbow, rainbow
from .sarext import SAREXT, sarext
from .short_run import ShortRun, short_run
from .sinwma import SINWMA, sinwma
from .sma_slope import SMASlope, sma_slope
from .ssf import SuperSmoother, ssf
from .supertrend import Supertrend, supertrend
from .swma import SWMA, swma
from .t3 import T3, t3
from .tema import TEMA, tema
from .trima import TRIMA, trima
from .trix import TRIX, trix
from .ttm_trend import TTMTrend, ttm_trend
from .vama import VAMA, vama
from .vhf import VHF, vhf
from .vidya import VIDYA, vidya
from .vortex import Vortex, vortex
from .vwma import VWMA, vwma
from .zlma import ZLMA, zlma

__all__ = [
    "MACD", "macd",
    "DEMA", "dema",
    "TEMA", "tema",
    "TRIMA", "trima",
    "T3", "t3",
    "HMA", "hma",
    "PPO", "ppo",
    "APO", "apo",
    "TRIX", "trix",
    "Aroon", "aroon",
    "Vortex", "vortex",
    "KAMA", "kama",
    "Supertrend", "supertrend",
    "ADX", "directional_movement",
    "KST", "kst",
    "VWMA", "vwma",
    "ZLMA", "zlma",
    "ALMA", "alma",
    "FWMA", "fwma",
    "SINWMA", "sinwma",
    "PWMA", "pwma",
    "PlusDI", "plus_di",
    "MinusDI", "minus_di",
    "DX", "dx",
    "ADXR", "adxr",
    "Choppiness", "chop",
    "VHF", "vhf",
    "QStick", "qstick",
    "SMASlope", "sma_slope",
    "DPO", "dpo",
    "SWMA", "swma",
    "MASpread", "ma_spread",
    "Increasing", "increasing",
    "Decreasing", "decreasing",
    "TTMTrend", "ttm_trend",
    "VIDYA", "vidya",
    "McGinleyDynamic", "mcgd",
    "SuperSmoother", "ssf",
    "HWMA", "hwma",
    "PlusDM", "plus_dm",
    "MinusDM", "minus_dm",
    "AroonOscillator", "aroon_osc",
    "LongRun", "long_run",
    "ShortRun", "short_run",
    "AMAT", "amat",
    "PSAR", "psar",
    "CKSP", "cksp",
    "FRAMA", "frama",
    "HiLo", "hilo",
    "LSMA", "lsma",
    "MACDFIX", "macdfix",
    "Pivots", "pivots",
    "PMax", "pmax",
    "VAMA", "vama",
    "EVWMA", "evwma",
    "Ichimoku", "ichimoku",
    "JMA", "jma",
    "MACDEXT", "macdext",
    "SAREXT", "sarext",
    "Rainbow", "rainbow",
    "MAMA", "mama",
    "FAMA", "fama",
]
