# Utilities (crossover helpers, lag, decay, rolling rank)

- **Category:** utils (not analytical indicators — signal/series helpers)

## Crossover helpers
```
crossover(a, b)  -> True where a crosses ABOVE b   (a_{t-1} <= b_{t-1} and a_t > b_t)
crossunder(a, b) -> True where a crosses BELOW b
crossany(a, b)   -> either direction
cross(series, level) -> crossing a constant threshold
```
tulip `crossany`, `crossover`; pandas-ta `cross`, `cross_value`.

## Series helpers
- `lag(x, n)` / shift; `decay`/`edecay` (linear/exponential decay of a signal, pandas-ta `decay`); `percent_rank(x, N)` (used by Connors RSI); `slope`, `roc1`.

## Edge cases & pitfalls
- Crossovers need the **previous** bar — first bar is always False/NaN.
- Look-ahead bias: never compute a crossover using a value that includes the current (incomplete) bar in live trading.
- percent_rank needs the full N-window before valid.

## References & libraries
- tulip crossover utilities; pandas-ta utility functions; QTPyLib helpers (`crossed_above`, `crossed_below`).
