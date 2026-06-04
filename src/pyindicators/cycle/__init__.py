"""cycle/ — Hilbert-Transform cycle indicators (Ehlers / TA-Lib HT_* family).

All members share the Hilbert recurrence in :mod:`._hilbert`, reproduced bit-exactly
against TA-Lib. Importing this package registers the pattern classes.
"""

from __future__ import annotations

from .dsp import Dsp, dsp
from .ebsw import Ebsw, ebsw
from .ht_dcperiod import HtDcPeriod, ht_dcperiod
from .ht_dcphase import HtDcPhase, ht_dcphase
from .ht_phasor import HtPhasor, ht_phasor
from .ht_sine import HtSine, ht_sine
from .ht_trendline import HtTrendline, ht_trendline
from .ht_trendmode import HtTrendMode, ht_trendmode
from .msw import MesaSineWave, msw

__all__ = [
    "HtDcPeriod", "ht_dcperiod",
    "HtDcPhase", "ht_dcphase",
    "HtTrendline", "ht_trendline",
    "HtPhasor", "ht_phasor",
    "HtSine", "ht_sine",
    "HtTrendMode", "ht_trendmode",
    "Ebsw", "ebsw",
    "Dsp", "dsp",
    "MesaSineWave", "msw",
]
