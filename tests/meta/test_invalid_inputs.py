"""Registry-driven invalid-input meta-tests — run over EVERY registered indicator so the whole
catalog (prebuilt + new) gets invalid-value coverage in one place:

* unknown / misspelled parameters are rejected (pydantic ``extra='forbid'``),
* a frame missing a required input column raises a clear error,
* NaN-laden input is tolerated (propagated, never a crash).
"""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

NAMES = INDICATORS.names()
LONG = deterministic_frame(150)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_unknown_param_rejected(name):
    with pytest.raises((ValidationError, TypeError)):
        INDICATORS.create(name, not_a_real_parameter=123)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_missing_input_column_raises(name):
    spec = INDICATORS.get(name).spec
    df = LONG.drop(columns=[spec.inputs[0]])  # remove a column the indicator declares it needs
    with pytest.raises(ValueError):
        INDICATORS.create(name).compute(df)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_nan_input_is_tolerated(name):
    df = LONG.copy()
    df.loc[df.index[10], "close"] = np.nan  # a bad tick must not crash the pipeline
    out = INDICATORS.create(name).compute(df)
    assert len(out) == len(df)
