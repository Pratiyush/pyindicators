"""statistics/ — rolling statistical functions."""

from __future__ import annotations

from .beta import Beta, beta
from .correl import Correl, correl
from .covariance import Covariance, covariance
from .entropy import Entropy, entropy
from .hurst_exponent import HurstExponent, hurst_exponent
from .kurtosis import Kurtosis, kurtosis
from .linreg import LinearReg, linreg
from .linreg_angle import LinearRegAngle, linreg_angle
from .linreg_intercept import LinearRegIntercept, linreg_intercept
from .linreg_slope import LinearRegSlope, linreg_slope
from .mad import MAD, mad
from .median import Median, median
from .quantile import Quantile, quantile
from .r_squared import RSquared, r_squared
from .skew import Skew, skew
from .tsf import TSF, tsf
from .zscore import ZScore, zscore

__all__ = [
    "ZScore", "zscore",
    "MAD", "mad",
    "Median", "median",
    "Quantile", "quantile",
    "Skew", "skew",
    "Kurtosis", "kurtosis",
    "Entropy", "entropy",
    "LinearReg", "linreg",
    "LinearRegSlope", "linreg_slope",
    "LinearRegIntercept", "linreg_intercept",
    "LinearRegAngle", "linreg_angle",
    "TSF", "tsf",
    "HurstExponent", "hurst_exponent",
    "Beta", "beta",
    "Correl", "correl",
    "Covariance", "covariance",
    "RSquared", "r_squared",
]
