"""HT_SINE — Hilbert-Transform SineWave (Ehlers / TA-Lib)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_63, LOOKBACK_63, hilbert_state, mask_lookback


def ht_sine(close: pd.Series) -> pd.DataFrame:
    """SineWave (``sin(dcPhase)``) and lead SineWave (``sin(dcPhase + 45)``).

    Both lines are derived from the dominant-cycle phase, so they oscillate in ``[-1, 1]``
    and their crossover marks cycle turning points (lead leads the cycle by 45 degrees).
    """
    state = hilbert_state(close, HT_START_63)
    return pd.DataFrame(
        {
            "sine": mask_lookback(state.sine, LOOKBACK_63, close.index),
            "lead_sine": mask_lookback(state.lead_sine, LOOKBACK_63, close.index),
        }
    )


@INDICATORS.register
class HtSine(Indicator):
    """Hilbert Transform — SineWave.

    What: two sine lines built from the dominant-cycle phase — ``sine = sin(dcPhase)`` and
        ``lead_sine = sin(dcPhase + 45)``. In a cyclic market the lines oscillate cleanly and
        cross at cycle turns; in a trend they hug each other near +/-1. The lead/sine crossover
        is Ehlers' cycle-mode timing signal.
    Best settings: close only, no parameters; both lines are bounded to [-1, 1].
    Edge cases: the first 63 bars are NaN (TA-Lib's lookback with the default unstable period
        of 0); the recurrence seeds at bar 37.
    Parity: TA-Lib ``HT_SINE`` (returns sine, leadsine), bit-exact (max |Δ| ~4e-12).
    """

    spec = IndicatorSpec(
        name="ht_sine",
        category="cycle",
        aliases=("Hilbert Transform SineWave", "HT_SINE"),
        inputs=(CLOSE,),
        outputs=("sine", "lead_sine"),
        bounds={"sine": (-1.0, 1.0), "lead_sine": (-1.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib HT_SINE", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        return ht_sine(df[CLOSE])
