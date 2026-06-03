# pyindicators

**A modular, look-ahead-safe technical-analysis library for pandas/numpy — one class per indicator.**

Every indicator is a small, fully-typed, composable unit that computes over a canonical OHLCV
frame and returns a frame aligned 1:1 to the input. Indicators are **causal by construction**
(trailing-only windows — no centered windows, no negative shifts, no full-series normalisation),
verified by a truncation-invariance meta-test, and discoverable through a plugin registry.

## Design principles

- **One class per indicator**, organised into category packages: `base/ trend/ momentum/
  volatility/ volume/ statistics/ cycle/ price_transform/ candles/ math_transform/ utils/`.
- **Our own implementations only.** Every indicator is hand-rolled in vectorized pandas/numpy.
  **Third-party TA libraries (TA-Lib, pandas-ta, finta, ta) are used *only in the test suite*
  to cross-check correctness (parity); they are never imported at runtime.** Runtime
  dependencies are just `pandas`, `numpy`, and `pydantic`.
- **Typed metadata is the single source of truth.** Each class carries an `IndicatorSpec`
  (name, category, inputs, outputs, bounds, causal, references, doc) that drives validation,
  the registry, the parity harness, and documentation.
- **Compose from `base/`.** Downstream indicators reuse `sma/ema/wma/rma/stdev/variance/
  true_range` — never re-implement an EMA/ATR/RMA inline.
- **A uniform edge-case policy** (division-by-zero, flat windows, warm-up, EMA seeding,
  population-vs-sample stdev) is standardised once in `core/`.

## Install

```bash
pip install pyindicators                          # once published
pip install git+https://github.com/Pratiyush/pyindicators   # from source
```

## Quickstart

```python
import pandas as pd
import pyindicators as pyi

# canonical OHLCV frame: lower-case columns open/high/low/close/volume
df = ...

sma = pyi.INDICATORS.create("sma", length=50)
out = sma.compute(df)                 # -> DataFrame with column "sma", indexed like df

print(pyi.INDICATORS.names())         # every registered indicator
```

## Testing & correctness

- **100% line + branch coverage** (`pytest-cov`, `fail_under=100`).
- **Registry-driven meta-tests** run over *every* indicator: causality/truncation-invariance,
  shape/dtype, declared-bounds, determinism, no input mutation.
- **Parity tests** cross-check each indicator against the reference libraries it cites
  (TA-Lib `<1e-6`, plus pandas-ta / finta / ta where useful); documented divergences (EMA
  seeding, sample-vs-population stdev) are pinned. Install the oracles with the `parity` extra:

```bash
pip install -e ".[dev,parity]"
pytest
```

## License

MIT © Pratiyush
