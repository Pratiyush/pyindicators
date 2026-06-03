# Other Statistics Functions (CORREL, BETA, ZSCORE, VAR, STDDEV, MAD, SKEW, KURTOSIS, etc.)

## CORREL — Pearson Correlation (rolling), TA-Lib `CORREL`, tulip `crossover`? no — `correl`? pandas `rolling().corr()`.
## BETA — slope of asset returns vs benchmark returns over N. TA-Lib `BETA`.
## Z-Score — `(x - SMA(x,N)) / stdev(x,N)`. Edge: stdev=0 guard. pandas-ta `zscore`.
## VAR / STDDEV — see base/RollingStdev.md (population vs sample). TA-Lib `VAR`,`STDDEV`.
## Mean Absolute Deviation (MAD) — `mean(|x - mean(x)|, N)`. pandas-ta `mad`.
## Median / Quantile — rolling median / quantile. pandas-ta `median`, `quantile`.
## Skew / Kurtosis — rolling 3rd/4th standardized moments. pandas-ta `skew`, `kurtosis`.
## Entropy — rolling Shannon entropy of normalized values. pandas-ta `entropy`.
## STDERR / R-squared / Covariance — regression diagnostics; build on LinearRegression.md.

**Common edge cases:** stdev=0 (z-score), N-1 vs N (sample vs population), NaN propagation, and benchmark length alignment (BETA, CORREL).
