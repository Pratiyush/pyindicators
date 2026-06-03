# Donchian Channels

- **Category:** volatility / overlap
- **Author:** Richard Donchian
- **Default:** period 20

## 1. What it measures
The highest high and lowest low over N bars — the classic breakout channel (Turtle Traders).

## 2. How it works / formula
```
Upper  = highest High over N
Lower  = lowest  Low  over N
Middle = (Upper + Lower) / 2
```

## 3. Parameters / best settings
- 20 (entries), 10 (exits) in the Turtle system.

## 4. Outputs & interpretation
- Close above Upper = breakout long; below Lower = breakout short.

## 5. Edge cases
- **Current-bar inclusion:** the original Turtle rule **excluded** the current bar — decide and document.

## 6. Pitfalls
- Including vs excluding the current bar changes breakout timing materially.

## 7. References & libraries
- pandas-ta `donchian`; finta `DO`; bukosabino/ta `DonchianChannel`. (Not in core TA-Lib.)
