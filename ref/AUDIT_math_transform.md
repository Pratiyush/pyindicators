# Correctness Review — math_transform (26)

Line-by-line review of the math-transform family: element-wise numeric transforms and pure
rolling reducers. Each was read against its canonical definition (TA-Lib's math-transform set /
NumPy) and confirmed causal (element-wise transforms have no window; reducers use
`min_periods == length`). Every one has a parity test under `tests/parity/`.

**Legend** — Verdict: ✅ verified.

## Element-wise transforms (close → f(close), or two-series arithmetic)

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `acos` | ✅ | `np.arccos(close)` under `errstate(invalid="ignore")`; |x|>1 → NaN (price inputs out of domain). Element-wise, causal. | parity vs `talib.ACOS`; domain handled by real-data invariants (all-NaN on prices). |
| `asin` | ✅ | `np.arcsin(close)`, same domain guard as acos. | parity vs `talib.ASIN`. |
| `atan` | ✅ | `np.arctan(close)`; bound `[-π/2, π/2]` declared and respected. | parity vs `talib.ATAN`; bound asserted by real-data invariants. |
| `cos` | ✅ | `np.cos(close)`. Element-wise. | parity vs `talib.COS`. |
| `cosh` | ✅ | `np.cosh(close)` (large-but-finite on real prices). | parity vs `talib.COSH`. |
| `sin` | ✅ | `np.sin(close)`; NaNs propagate. | parity vs `talib.SIN`. |
| `sinh` | ✅ | `np.sinh(close)`. | parity vs `talib.SINH`. |
| `tan` | ✅ | `np.tan(close)` (radians), matches TA-Lib `TAN`. | parity vs `talib.TAN`. |
| `tanh` | ✅ | `np.tanh(close)`. | parity vs `talib.TANH`. |
| `exp` | ✅ | `np.exp(close)`. | parity vs `talib.EXP`. |
| `ln` | ✅ | `np.log` on positives only; ≤0 masked → NaN (log domain). | parity vs `talib.LN`. |
| `log10` | ✅ | `np.log10` on positives only; ≤0 → NaN. | parity vs `talib.LOG10`. |
| `sqrt` | ✅ | `np.sqrt(close)` under `errstate`; negatives → NaN. | parity vs `talib.SQRT`. |
| `ceil` | ✅ | `np.ceil(close)`. | parity vs `talib.CEIL`. |
| `floor` | ✅ | `np.floor(close)`. | parity vs `talib.FLOOR`. |
| `add` | ✅ | `high + low` element-wise. | parity vs `talib.ADD`. |
| `sub` | ✅ | `high - low`. | parity vs `talib.SUB`. |
| `mult` | ✅ | `high * low`. | parity vs `talib.MULT`. |
| `div` | ✅ | `safe_divide(high, low)` (guards low==0). | parity vs `talib.DIV`. |

## Rolling reducers (window = `close.rolling(length, min_periods=length)`)

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `max` | ✅ | `rolling(length).max()`; trailing window, causal. | parity vs `talib.MAX`. |
| `min` | ✅ | `rolling(length).min()`. | parity vs `talib.MIN`. |
| `sum` | ✅ | `rolling(length).sum()`. | parity vs `talib.SUM`. |
| `minmax` | ✅ | rolling min AND max over the same window. | parity vs `talib.MINMAX` (both outputs). |
| `maxindex` | ✅ | absolute index of the rolling max via explicit O(n) scan keeping the **latest** equal max (matches TA-Lib's incremental MAXINDEX; `np.argmax` would diverge on ties). | parity vs `talib.MAXINDEX`. |
| `minindex` | ✅ | absolute index of the rolling min, **latest** equal min (TA-Lib MININDEX tie convention). | parity vs `talib.MININDEX`. |
| `minmaxindex` | ✅ | both extreme indices with the documented tie rule. | parity vs `talib.MINMAXINDEX`. |

## Cross-cutting
- **Causality:** element-wise transforms cannot look ahead; reducers use `min_periods == length` so the first `length-1` bars are NaN. Verified by the real-data prefix-vs-full invariant test.
- **Domain handling:** acos/asin/sqrt/ln/log10 return NaN outside their math domain rather than raising — confirmed by the real-AAPL invariants sweep.
