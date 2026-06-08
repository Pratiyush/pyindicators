"""Parity for the crossover / crossunder / crossany / cross_value signal helpers vs
``pandas_ta_classic.cross`` / ``cross_value`` on real data.

These ship as plain functions (not registered Indicators), so they are exercised by name via
``pyindicators.utils``. Parity is asserted on the post-warmup region only: pandas-ta builds the
"below" case as ``~current & ~previous``, which spuriously emits 1.0 during the NaN warmup,
whereas our helpers are strict (a true edge crossing) and correctly emit 0 there.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import real_frame
from pyindicators import utils
from pyindicators.base import sma

pta = pytest.importorskip("pandas_ta_classic")

C = real_frame()["close"]
FAST, SLOW = sma(C, 10), sma(C, 30)
VALID = (
    FAST.notna() & SLOW.notna() & FAST.shift(1).notna() & SLOW.shift(1).notna()
).to_numpy()


@pytest.mark.parametrize("name", ["crossover", "crossunder", "crossany", "cross_value"])
def test_cross_family_parity_pandas_ta(name):
    fn = getattr(utils, name)
    if name == "crossover":
        ours, ref, mask = fn(FAST, SLOW), pta.cross(FAST, SLOW, above=True), VALID
    elif name == "crossunder":
        ours, ref, mask = fn(FAST, SLOW), pta.cross(FAST, SLOW, above=False), VALID
    elif name == "crossany":
        ref = pta.cross(FAST, SLOW, above=True) | pta.cross(FAST, SLOW, above=False)
        ours, mask = fn(FAST, SLOW), VALID
    else:  # cross_value
        ours = fn(C, 100.0, above=True)
        ref = pta.cross_value(C, 100.0, above=True)
        mask = C.notna().to_numpy()
    np.testing.assert_array_equal(
        ours.to_numpy()[mask], ref.to_numpy().astype("float64")[mask]
    )
