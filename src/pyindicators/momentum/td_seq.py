"""TD Sequential (TD_SEQ) — Tom DeMark's exhaustion counter (setup/countdown).

DeMark's Sequential compares each close with the close four bars earlier. A run of bars
whose close is *above* (``up``) or *below* (``down``) that 4-bar-ago close is counted
consecutively; the count is capped at 13 (the classic setup/countdown horizon). The two
outputs are the running up-count and down-count, emitted only on bars that belong to a run
(other bars are NaN), matching ``pandas_ta_classic.td_seq`` default (``show_all=True``).

We reproduce pandas-ta's ``rolling(13).apply(true_sequence_count)`` exactly but vectorised:
within the trailing 13-bar window pandas-ta returns the length of the trailing run of True
comparisons, which equals the consecutive-run length clipped at 13. See the parity test.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def _run_count(flag: pd.Series, length: int) -> pd.Series:
    """Length of the consecutive trailing run of True in ``flag``, capped at ``length``.

    Emitted only where ``flag`` is True; every other bar is NaN. This is the vectorised
    equivalent of pandas-ta's ``rolling(length).apply(true_sequence_count)``: the rolling
    window only ever sees the last ``length`` bars, so a run longer than the window is
    reported as ``length`` (its window is all-True), hence the clip.
    """
    # New run starts whenever flag flips to False; cumsum of the False mask labels runs.
    run_id = (~flag).cumsum()
    run_len = flag.groupby(run_id).cumsum().clip(upper=length).astype("float64")
    return run_len.where(flag).mask(run_len == 0)


def td_seq(close: pd.Series, length: int = 13) -> dict[str, pd.Series]:
    """TD Sequential up/down consecutive counts (vs the close ``4`` bars earlier).

    ``length`` is the horizon/cap (13 in the classic indicator). Bars not part of a run are
    NaN. Edge handling falls out of the arithmetic: the first 4 bars have no 4-bar-ago close
    (``diff(4)`` is NaN, the comparison is False) so neither run can start there.
    """
    diff4 = close.diff(4)
    up_flag = diff4 > 0
    down_flag = diff4 < 0
    return {
        "td_seq_up": _run_count(up_flag, length),
        "td_seq_dn": _run_count(down_flag, length),
    }


@INDICATORS.register
class TDSequential(Indicator):
    """TD Sequential (DeMark).

    What: consecutive count of closes above (``td_seq_up``) / below (``td_seq_dn``) the
    close four bars earlier, capped at ``length`` (13); off-run bars are NaN.
    Best settings: ``length`` 13 (classic setup=9 / countdown=13 horizon).
    Edge cases: first 4 bars cannot start a run (no 4-bar-ago close); a bar is in at most
    one of the two runs (a strict ``>`` / ``<`` comparison), flat-vs-4-ago bars are in
    neither.
    Parity: pandas-ta ``td_seq`` (default ``show_all=True``) -> columns ``TD_SEQ_UPa`` /
    ``TD_SEQ_DNa``.
    """

    spec = IndicatorSpec(
        name="td_seq",
        category="momentum",
        aliases=("TD Sequential", "Tom DeMark Sequential", "TD_SEQ"),
        inputs=(CLOSE,),
        outputs=("td_seq_up", "td_seq_dn"),
        bounds={"td_seq_up": (1.0, 13.0), "td_seq_dn": (1.0, 13.0)},
        references=("DeMark", "pandas-ta td_seq"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=13, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return td_seq(df[CLOSE], self.params["length"])
