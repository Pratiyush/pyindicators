"""momentum/ — oscillators."""

from __future__ import annotations

from .alligator import Alligator, alligator
from .ao import AwesomeOscillator, ao
from .bias import Bias, bias
from .bop import BOP, bop
from .brar import BRAR, brar
from .cci import CCI, cci
from .cfo import CFO, cfo
from .cg import CenterOfGravity, cg
from .cmb_composite_index import CompositeIndex, cmb_composite_index
from .cmo import CMO, cmo
from .coppock import Coppock, coppock
from .crsi import ConnorsRSI, crsi
from .cti import CTI, cti
from .demarker import DeMarker, demarker
from .derivative_osc import DerivativeOscillator, derivative_osc
from .disparity_index import DisparityIndex, disparity_index
from .er import EfficiencyRatio, er
from .eri import ElderRay, eri
from .fisher import FisherTransform, fisher
from .fosc import FOSC, fosc
from .gator import GatorOscillator, gator
from .inertia import Inertia, inertia
from .kdj import KDJ, kdj
from .laguerre_rsi import LaguerreRSI, laguerre_rsi
from .mom import MOM, mom
from .pgo import PGO, pgo
from .psl import PSL, psl
from .pvo import PVO, pvo
from .qqe import QQE, qqe
from .roc import ROC, roc
from .rocp import ROCP, rocp
from .rocr import ROCR, rocr
from .rocr100 import ROCR100, rocr100
from .rsi import RSI, rsi
from .rsi_negative_reversal import RSINegativeReversal, rsi_negative_reversal
from .rsi_positive_reversal import RSIPositiveReversal, rsi_positive_reversal
from .rsl import RSL, rsl
from .rsx import RSX, rsx
from .rvgi import RVGI, rvgi
from .slope import Slope, slope
from .smi import SMIErgodic, smi
from .squeeze import Squeeze, squeeze
from .squeeze_pro import SqueezePro, squeeze_pro
from .stc import STC, stc
from .stoch import Stochastic, stoch
from .stochf import FastStochastic, stochf
from .stochrsi import StochRSI, stochrsi
from .td_seq import TDSequential, td_seq
from .tsi import TSI, tsi
from .ttm_momentum import TTMMomentum, ttm_momentum
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
    "CFO", "cfo",
    "PGO", "pgo",
    "CenterOfGravity", "cg",
    "DisparityIndex", "disparity_index",
    "TTMMomentum", "ttm_momentum",
    "CompositeIndex", "cmb_composite_index",
    "FastStochastic", "stochf",
    "PVO", "pvo",
    "KDJ", "kdj",
    "FisherTransform", "fisher",
    "RVGI", "rvgi",
    "CTI", "cti",
    "STC", "stc",
    "Inertia", "inertia",
    "SMIErgodic", "smi",
    "FOSC", "fosc",
    "BRAR", "brar",
    "Alligator", "alligator",
    "ConnorsRSI", "crsi",
    "DeMarker", "demarker",
    "DerivativeOscillator", "derivative_osc",
    "GatorOscillator", "gator",
    "LaguerreRSI", "laguerre_rsi",
    "RSL", "rsl",
    "Squeeze", "squeeze",
    "SqueezePro", "squeeze_pro",
    "QQE", "qqe",
    "RSX", "rsx",
    "RSIPositiveReversal", "rsi_positive_reversal",
    "RSINegativeReversal", "rsi_negative_reversal",
    "TDSequential", "td_seq",
]
