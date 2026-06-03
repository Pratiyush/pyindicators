# Ichimoku Kinko Hyo — "One Glance Equilibrium Chart"

- **Category:** trend / overlap (multi-line system)
- **Author:** Goichi Hosoda
- **Defaults:** Tenkan 9, Kijun 26, Senkou B 52, displacement 26

## 1. What it measures
A complete trend/support-resistance/momentum system in five lines plus a forward-projected "cloud" (Kumo).

## 2. How it works
Midpoints of rolling high/low ranges over three horizons, two of which are shifted forward to form the cloud, plus the close shifted back.

## 3. Algorithm & formula
```
Tenkan-sen  = (HH(9)  + LL(9))  / 2
Kijun-sen   = (HH(26) + LL(26)) / 2
Senkou A    = (Tenkan + Kijun)/2        shifted +26 forward
Senkou B    = (HH(52) + LL(52))/2       shifted +26 forward
Chikou Span = Close                     shifted -26 back
Kumo (cloud) = region between Senkou A and Senkou B
```
(HH/LL = highest high / lowest low over the period.)

## 4. Parameters / best settings
- 9/26/52/26 (classic, daily). Crypto/24h sometimes uses 20/60/120/30.

## 5. Outputs & interpretation
- Price above cloud = bullish regime, below = bearish, inside = neutral.
- Tenkan/Kijun cross = signal; cloud thickness = support/resistance strength.

## 6. Edge cases
- **Forward shift** creates legitimate future-dated NaNs for the most recent 26 bars of Senkou A/B.
- **LOOKAHEAD / DATA-LEAK WARNING:** in backtests, Senkou spans and Chikou must be aligned so you never read future data into a past decision. pandas-ta explicitly flags `ichimoku` for potential leaks.

## 7. Pitfalls
- Off-by-one in displacement; "include current bar" ambiguity in HH/LL.

## 8. References & libraries
- pandas-ta `ichimoku`; finta `ICHIMOKU`; freqtrade/technical. (Not in core TA-Lib.)
