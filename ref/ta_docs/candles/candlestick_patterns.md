# Candlestick Pattern Recognition (61 TA-Lib CDL functions)

- **Category:** candles / pattern recognition
- **Source:** TA-Lib C library (61 `CDL*` functions)

## What they measure
Detect classic Japanese candlestick patterns from OHLC geometry. Each function scans for one named pattern and returns a per-bar score:
```
+100 (or +1)  bullish occurrence
   0          no pattern
-100 (or -1)  bearish occurrence
```
(TA-Lib returns ±100/0; the {talib} R wrapper normalizes to ±1/0.)

## Pattern catalog (the 61 CDL functions)
Single/dual/triple-candle patterns including (non-exhaustive list — implement one class each):

Doji, DojiStar, DragonflyDoji, GravestoneDoji, LongLeggedDoji, RickshawMan, Hammer, InvertedHammer, HangingMan, ShootingStar, Marubozu, SpinningTop, Engulfing, Harami, HaramiCross, MorningStar, EveningStar, MorningDojiStar, EveningDojiStar, ThreeWhiteSoldiers, ThreeBlackCrows, ThreeInside, ThreeOutside, ThreeLineStrike, ThreeStarsInSouth, AbandonedBaby, DarkCloudCover, PiercingPattern, Kicking, KickingByLength, BeltHold, Breakaway, ClosingMarubozu, ConcealBabySwallow, CounterAttack, GapSideSideWhite, Hikkake, HikkakeMod, HomingPigeon, IdenticalThreeCrows, InNeck, OnNeck, LadderBottom, MatchingLow, MatHold, HighWave, LongLine, ShortLine, RiseFallThreeMethods, SeparatingLines, StalledPattern, StickSandwich, Takuri, TasukiGap, Thrusting, Tristar, Unique3River, Upside/DownsideGapThreeMethods, UpsideGap2Crows, XSideGap3Methods, AdvanceBlock, TwoCrows.

## Parameters
- Some functions take a `penetration` factor (e.g. DarkCloudCover, MorningStar, AbandonedBaby, EveningStar, MatHold) controlling how deep one candle must close into another (default 0.3 or 0.5 depending on pattern).
- Several depend on a notion of "long/short body" relative to a rolling average body size (TA-Lib uses configurable averaging periods internally).

## Edge cases & pitfalls
- **Body/shadow thresholds are heuristic** and TA-Lib computes them relative to a moving average of recent candle bodies — replicating TA-Lib exactly requires matching those averaging windows.
- **Gaps** are integral to many patterns (stars, gaps) — require true gaps, not just body relationships.
- **Doji tolerance** (how near open=close must be) is a tunable threshold; pick and document.
- These are best treated as a **sub-project**: one class per pattern, all returning the same ±/0 signal contract, sharing a common "body/shadow geometry" helper.

## References & libraries
- TA-Lib Pattern Recognition group (61 `CDL*` functions); pandas-ta `cdl_pattern` (wraps TA-Lib) + native `cdl_doji`, `cdl_inside`; the {talib} R wrapper documents the 61-pattern catalog and the ±1/0 scoring.
