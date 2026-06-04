"""momentum/ — oscillators."""

from __future__ import annotations

from .ao import AwesomeOscillator, ao
from .bias import Bias, bias
from .bop import BOP, bop
from .cci import CCI, cci
from .cmo import CMO, cmo
from .coppock import Coppock, coppock
from .er import EfficiencyRatio, er
from .eri import ElderRay, eri
from .mom import MOM, mom
from .psl import PSL, psl
from .roc import ROC, roc
from .rocp import ROCP, rocp
from .rocr import ROCR, rocr
from .rocr100 import ROCR100, rocr100
from .rsi import RSI, rsi
from .slope import Slope, slope
from .stoch import Stochastic, stoch
from .stochrsi import StochRSI, stochrsi
from .tsi import TSI, tsi
from .uo import UltimateOscillator, uo
from .willr import WilliamsR, willr

__all__ = [
    "RSI", "rsi",
    "Stochastic", "stoch",
    "CCI", "cci",
    "WilliamsR", "willr",
    "ROC", "roc",
    "StochRSI", "stochrsi",
    "TSI", "tsi",
    "UltimateOscillator", "uo",
    "MOM", "mom",
    "ROCP", "rocp",
    "ROCR", "rocr",
    "ROCR100", "rocr100",
    "CMO", "cmo",
    "BOP", "bop",
    "AwesomeOscillator", "ao",
    "Coppock", "coppock",
    "Bias", "bias",
    "PSL", "psl",
    "EfficiencyRatio", "er",
    "Slope", "slope",
    "ElderRay", "eri",
]
