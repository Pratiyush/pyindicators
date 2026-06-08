"""PDIST — Price Distance: golden + edge cases.

PDIST = 2*(high-low) - |close-open| + |open - close_{t-drift}|.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_pdist_golden():
    # bar0 has no prior close -> NaN; bar1 = 2*(13-10) - |12-11| + |11-11| = 5;
    # bar2 = 2*(15-11) - |14-13| + |13-12| = 8.
    df = frame(
        [11.0, 12.0, 14.0],
        high=[12.0, 13.0, 15.0],
        low=[8.0, 10.0, 11.0],
        open_=[10.0, 11.0, 13.0],
    )
    out = INDICATORS.create("pdist").compute(df)["pdist"]
    assert np.isnan(out.iloc[0])
    np.testing.assert_allclose(out.iloc[1:].to_numpy(), [5.0, 8.0], atol=1e-12)


def test_pdist_flat_series_is_zero():
    # O=H=L=C constant -> 2*0 - 0 + |O - prevC| = 0.
    out = INDICATORS.create("pdist").compute(frame([5.0] * 5))["pdist"]
    np.testing.assert_allclose(out.iloc[1:].to_numpy(), 0.0, atol=1e-12)
