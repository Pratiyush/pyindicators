# pyindicators — detailed indicator reference



> 260 indicators with definition, mechanism/formula, parameters + best settings, interpretation, and look-ahead notes. Sourced (cited) from major TA libraries + books.



## breadth  (3)

### Advance-Decline Line  `advance_decline_line`
*breadth · Market breadth analysis (standard)* · aliases: A/D line, Breadth line, Market breadth

**What:** Cumulative breadth indicator showing market participation; adds advancing and subtracts declining issues daily

**How / formula:** ADL = Previous ADL + (Advancing - Declining). Cumulative sum building over time. Rising ADL = more stocks advancing (healthy breadth). Falling = more declining (poor breadth). Absolute value less important than trend direction.

**Inputs:** advances, declines
**Outputs:** adl

**Interpretation:** ADL rising with price = healthy trend (accumulation). ADL falling with rising price = divergence (distribution, weakness). ADL breakouts = market participation. Divergences between ADL and index signal reversals. Confirms or questions price strength.

**Look-ahead risk:** None; cumulative from completed trading data
- https://www.earn2trade.com/blog/advance-decline-line/
- https://chartschool.stockcharts.com/table-of-contents/market-indicators/advance-decline-line
- https://www.fastercapital.com/content/Advance-Decline-Line--The-Symbiotic-Dance--Advance-Decline-Line-and-the-McClellan-Oscillator.html

### McClellan Oscillator  `mcclellan_oscillator`
*breadth · Sherman McClellan (market breadth analysis)* · aliases: McClellan OSC, Breadth momentum, Advance-decline momentum

**What:** Market breadth momentum indicator measuring advancing minus declining issues using exponential moving averages

**How / formula:** Calculate (Advances - Declines) each period. 19-period EMA of this difference. Subtract 39-period EMA of same. McClellan OSC = 19EMA - 39EMA. Measures momentum of breadth, not breadth itself. Indicators like AD Line for breadth, McClellan for momentum.

**Inputs:** advances, declines
**Outputs:** mcclellan_oscillator

**Parameters:**
- `fast_period` (default 19, typical 15-25) — Standard 19; EMA period
- `slow_period` (default 39, typical 35-45) — Standard 39; EMA period

**Interpretation:** Positive = advancing breadth dominance (bullish). Negative = declining breadth dominance (bearish). Zero crossovers = breadth momentum shifts. Extreme positive values may indicate overbought; extreme negative oversold. Oscillates around centerline.

**Look-ahead risk:** None; backward-looking breadth momentum calculation
- https://en.wikipedia.org/wiki/McClellan_oscillator
- https://www.mcoscillator.com/learning_center/kb/mcclellan_oscillator/the_mcclellan_oscillator_summation_index/
- https://chartschool.stockcharts.com/table-of-contents/market-indicators/mcclellan-oscillator

### TRIN (Arms Index)  `trin`
*breadth · Richard Arms Jr. (1967)* · aliases: Arms Index, Short Term TRading INdex, TRIN ratio

**What:** Market sentiment indicator ratio of advancing/declining stocks divided by advancing/declining volume; moves above/below 1.0

**How / formula:** TRIN = (Advancing/Declining) / (Up Volume/Down Volume). Alternative: (Advancing/Up Volume) / (Declining/Down Volume). Values > 1.0 = weak breadth (more issues advancing but less volume). < 1.0 = strong breadth (fewer issues advancing but more volume). Inverse relationship to market.

**Inputs:** advances, declines, up_volume, down_volume
**Outputs:** trin

**Interpretation:** TRIN > 1.0 = negative breadth (likely bearish). TRIN < 1.0 = positive breadth (likely bullish). Extreme values (< 0.5, > 2.0) = potential reversals. Used as contrarian indicator in markets (high TRIN = potential reversal up). Best used in context with price/trend.

**Look-ahead risk:** None; ratio of completed intraday breadth/volume data
- https://www.fastercapital.com/content/Advance-Decline-Line--The-Symbiotic-Dance--Advance-Decline-Line-and-the-McClellan-Oscillator.html
- https://www.earn2trade.com/blog/advance-decline-line/
- https://blog.elearnmarkets.com/breadth-indicators-trader-should-know/



## candlestick  (50)

### Two Crows  `cdl2crows`
*candlestick · TA-Lib* · aliases: CDL2CROWS

**What:** Two-candle bearish reversal pattern: first candle bullish (prior to uptrend), second bearish candle opens above first close, closes near first open/within first body.

**How / formula:** Detected when first bullish candle is followed by bearish candle that gaps up above prior close but closes back down into first candle's body. Shows sellers taking control from elevated prices.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal signal at top of uptrend. Gap up followed by close within prior body shows buyer enthusiasm reversed to selling pressure.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three Black Crows  `cdl3blackcrows`
*candlestick · TA-Lib* · aliases: CDL3BLACKCROWS

**What:** Three-candle bearish reversal/continuation pattern: three consecutive long black (bearish) candles, each opening within previous body and closing progressively lower.

**How / formula:** Detected when three consecutive candles are bearish with each opening within/above prior close and each closing lower than prior close. Indicates sustained seller control and downtrend strength.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal/continuation pattern at top of uptrend. Three successive lower closes show sustained selling pressure. Warns of trend reversal or continuation of downtrend.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three Inside Up/Down  `cdl3inside`
*candlestick · TA-Lib* · aliases: CDL3INSIDE

**What:** Three-candle pattern: two candles inside another (harami-like), followed by breakout candle. Can be bullish or bearish reversal.

**How / formula:** First: large candle. Second: small candle contained within first. Third: strong candle closing above first (bullish) or below first (bearish), confirming reversal direction.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern combining inside bar (harami) with confirmation breakout. Bullish: inside candles followed by break above. Bearish: break below.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three-Line Strike  `cdl3linestrike`
*candlestick · TA-Lib* · aliases: CDL3LINESTRIKE

**What:** Four-candle pattern: three candles in same direction followed by strong candle closing beyond all three, reversing the trend.

**How / formula:** Three consecutive bullish or bearish candles followed by fourth candle of opposite color that closes beyond the range of all three prior candles.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern. Three-candle trend followed by reversal candle that penetrates beyond the range. Signals trend reversal.

**Look-ahead risk:** Pattern fully determined at close of fourth candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three Outside Up/Down  `cdl3outside`
*candlestick · TA-Lib* · aliases: CDL3OUTSIDE

**What:** Three-candle pattern: first candle, second candle that engulfs first, third confirming breakout continuation. Stronger reversal than inside patterns.

**How / formula:** First: normal candle. Second: engulfing candle (body contains first candle). Third: large candle continuing direction of second/engulfing candle.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern. Engulfing second candle shows momentum shift, third candle confirms. Stronger than harami due to engulfing structure.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three Stars in the South  `cdl3starsinsouth`
*candlestick · TA-Lib* · aliases: CDL3STARSINSOUTH

**What:** Three-candle bullish reversal pattern at downtrend bottom: three bearish candles with long lower wicks, each wick lower than prior, showing rejection of lower prices.

**How / formula:** Three consecutive bearish candles with progressively lower wicks, showing sellers pushing down but buyers rejecting lower prices repeatedly. Wicks form staircase pattern downward.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish reversal at bottom. Long lower wicks rejecting lower prices three consecutive times shows strong support and buyer emergence.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Three White Soldiers  `cdl3whitesoldiers`
*candlestick · TA-Lib* · aliases: CDL3WHITESOLDIERS

**What:** Three-candle bullish continuation pattern: three consecutive long white (bullish) candles, each opening within/near previous body and closing higher than prior close.

**How / formula:** Detected when three consecutive candles are bullish with each candle opening within or above the prior candle's close, and closing progressively higher. Pattern indicates strong buyer control and trend continuation.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish continuation pattern signaling strong uptrend. Successive higher closes show sustained buying pressure. Often appears after consolidation or pullback within uptrend.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://www.litefinance.org/blog/for-beginners/how-to-read-candlestick-chart/three-white-soldiers-pattern/
- https://altfins.com/knowledge-base/three-white-soldiers-candlestick-pattern-a-comprehensive-guide/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Abandoned Baby  `cdlabandonedbaby`
*candlestick · TA-Lib* · aliases: CDLABANDONEDBABY

**What:** Three-candle reversal pattern: first large bearish candle, second small-bodied doji/candle with gap down, third large bullish candle with gap up closing above first candle midpoint.

**How / formula:** Detected when first candle is large bearish, second candle is small body with downside gap and no overlap to first, third candle is large bullish with upside gap. The gaps on either side of the middle candle are key. Penetration parameter (default 0.3) controls third candle penetration into first.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.3, typical 0.0 to 1.0) — Default 0.3. Controls how far third candle must penetrate first candle's body.

**Interpretation:** Strong bullish reversal at bottom of downtrend. Two consecutive gaps around isolated candle suggest definitive reversal. Rare pattern with strong predictive power.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Advance Block  `cdladvanceblock`
*candlestick · TA-Lib* · aliases: CDLADVANCEBLOCK

**What:** Three consecutive bullish candles appearing during uptrend with decreasing body size and/or increasing upper wicks, signaling uptrend slowing.

**How / formula:** Three bullish candles with each successive candle showing smaller body or longer upper wick relative to prior, indicating buying pressure diminishing despite upward price action.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Warning pattern within uptrend. Decreasing bodies/increasing wicks show buyers losing conviction. May precede consolidation or reversal.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Belthold  `cdlbelthold`
*candlestick · TA-Lib* · aliases: CDLBELTHOLD

**What:** Single-candle pattern that opens at an extreme (high or low) and closes at or near the opposite end, with large body showing strong directional control.

**How / formula:** Bullish belthold: opens near low and closes near high. Bearish: opens near high and closes near low. No or minimal wicks on entry side. Shows one side in full control.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Strong continuation pattern. Bullish belthold confirms buying pressure in uptrend. Bearish confirms selling in downtrend. Shows conviction and trend strength.

**Look-ahead risk:** Pattern fully determined at close of single candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Breakaway  `cdlbreakaway`
*candlestick · TA-Lib* · aliases: CDLBREAKAWAY

**What:** Five-candle reversal pattern: first long candle, three middle candles with small bodies (spinning tops) with second and fourth bearish, fifth long bullish candle closing within gap of first two.

**How / formula:** First candle: large bearish. Candles 2-4: small bodies (spinning tops), second and fourth bearish creating gaps. Fifth: large bullish closing within initial gap. Pattern shows trend exhaustion.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Rare reversal pattern showing trend exhaustion with middle spinning tops indicating indecision, then strong resolution bullish. Confirms reversal when fourth candle gap is reclaimed.

**Look-ahead risk:** Pattern fully determined at close of fifth candle. No repainting.
- https://patternswizard.com/breakaway-candlestick-pattern/
- https://wrtrading.com/technical-analysis/charts/candlestick/pattern/breakaway/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Marubozu  `cdlclosingmarubozu`
*candlestick · TA-Lib* · aliases: CDLCLOSINGMARUBOZU, CDLMARUBOZU

**What:** A pattern where a candle has little to no wicks on either end. Open equals/near low and close equals/near high (or vice versa). Indicates one side fully in control.

**How / formula:** Detected when body spans nearly the entire range from low to high with minimal or no shadows/wicks. Bullish marubozu: opens at low, closes at high. Bearish: opens at high, closes at low.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Strong directional candle showing buyer or seller dominance. Bullish marubozu during uptrend suggests continuation. Bearish during downtrend suggests trend strength. Can appear in breakouts.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://trendspider.com/learning-center/marubozu-candlesticks-a-traders-guide/
- https://www.strike.money/technical-analysis/marubozu
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Concealing Baby Swallow  `cdlconcealbabyswall`
*candlestick · TA-Lib* · aliases: CDLCONCEALBABYSWALL

**What:** Four-candle bullish reversal pattern: four bearish candles appearing after downtrend with distinct orientations signaling downtrend exhaustion and bullish reversal.

**How / formula:** Four consecutive bearish candles with specific structural requirements showing diminishing selling pressure and building bullish setup. Pattern indicates sellers exhausting at downtrend bottom.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Rare bullish reversal pattern at bottom of extended downtrend. Four bearish candles with specific arrangement suggest selling pressure exhausting.

**Look-ahead risk:** Pattern fully determined at close of fourth candle. No repainting.
- https://tradomate.one/docs/strategy-builder/technical-indicators/pattern-recognition/cdlconcealbabyswall/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Counterattack  `cdlcounterattack`
*candlestick · TA-Lib* · aliases: CDLCOUNTERATTACK

**What:** Two-candle reversal pattern where second candle matches first candle's opening price but closes in opposite direction, indicating reversal of sentiment.

**How / formula:** First candle: strong directional candle (bullish or bearish). Second candle: opposite color with close matching first open price, showing reversal of momentum.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern where second candle's open matches first close, but it closes opposite to first direction. Signals sentiment reversal and potential trend change.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Dark Cloud Cover  `cdldarkcloudcover`
*candlestick · TA-Lib* · aliases: CDLDARKCLOUDCOVER

**What:** Two-candle bearish reversal pattern: first long bullish candle, second long bearish candle opening above first close but closing below first midpoint.

**How / formula:** First candle: large bullish. Second candle: large bearish opening above prior close and penetrating back into first candle's body (closing below midpoint). Penetration parameter (default 0.5) controls penetration requirement.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.5, typical 0.0 to 1.0) — Default 0.5 (50%). Controls how far second candle must penetrate first body. 0.5 requires closing at/below first midpoint.

**Interpretation:** Bearish reversal pattern at top of uptrend. Opening gap up shows initial bullish follow-through, but second candle's close back into first body shows sellers regaining control.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Doji  `cdldoji`
*candlestick · TA-Lib* · aliases: CDLDOJI

**What:** A candlestick pattern where the open and close prices are approximately equal or identical, resulting in a very small or non-existent real body. Indicates market indecision.

**How / formula:** The pattern is detected when the absolute difference between close and open is less than approximately 5% of the total candle range (high - low). The wicks above and below the body are observed to classify doji variants.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** A neutral candlestick suggesting neither buyers nor sellers are in control. Often appears at turning points or during consolidation. Requires confirmation from following candles to signal reversals.

**Look-ahead risk:** No forward-looking bias; pattern is determined by a single completed candle.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html
- https://www.tmgm.com/en/academy/trading-academy/doji-candle-stick-pattern
- https://www.angelone.in/knowledge-center/share-market/doji-candle

### Doji Star  `cdldojistar`
*candlestick · TA-Lib* · aliases: CDLDOJISTAR

**What:** Two-candle pattern where first candle is directional and second is a doji, indicating indecision following strong move.

**How / formula:** First candle: large bullish or bearish. Second candle: doji pattern appearing after the directional move. Doji's indecision suggests momentum loss.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Potential reversal signal when doji appears after strong directional candle. Doji indecision after momentum suggests top/bottom formation.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Dragonfly Doji  `cdldragonflydoji`
*candlestick · TA-Lib* · aliases: CDLDRAGONFLYDOJI

**What:** A doji variant with a long lower wick and little to no upper wick. The open and close are near the high of the candle range.

**How / formula:** Detection requires open/close near the high, and a lower wick (low) significantly below the open/close point, typically at least 2-3 times the body height. Signals selling pressure followed by recovery.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Often bullish when appearing after a downtrend, suggesting sellers were unable to hold lower prices. The long lower wick shows rejection of lower prices.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://www.tmgm.com/en/academy/trading-academy/doji-candle-stick-pattern
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Engulfing Pattern  `cdlengulfing`
*candlestick · TA-Lib* · aliases: CDLENGULFING

**What:** A two-candle reversal pattern where the second candle's real body completely engulfs the first candle's real body. Bullish or bearish depending on color sequence.

**How / formula:** Detected when the second candle's body completely contains the first candle's body in terms of open/close range. Bullish engulfing: first bearish, second bullish with second close > first open. Bearish: first bullish, second bearish with second close < first open.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Strong reversal signal. Bullish engulfing after downtrend shows buyers have taken full control. Bearish engulfing after uptrend shows sellers taking control. Strength increases with larger bodies.

**Look-ahead risk:** Pattern confirmed at close of second candle; no repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html
- https://en.wikipedia.org/wiki/Candlestick_pattern

### Evening Doji Star  `cdleveningdojistar`
*candlestick · TA-Lib* · aliases: CDLEVENINGDOJISTAR

**What:** Variant of evening star where second candle is a doji instead of small body. Three-candle bearish reversal at top of uptrend.

**How / formula:** First: large bullish. Second: doji with gap up (open/close near top with wicks). Third: large bearish closing below first's midpoint. The doji accentuates indecision. Penetration parameter (default 0.3) controls third candle penetration.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.3, typical 0.0 to 1.0) — Default 0.3. Controls penetration requirement of third candle into first.

**Interpretation:** Stronger bearish reversal than evening star due to doji's indecision marker. Signals definitive shift from buying to selling.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Evening Star  `cdleveningstar`
*candlestick · TA-Lib* · aliases: CDLEVENINGSTAR

**What:** A three-candle bearish reversal pattern: long bullish candle, followed by small-bodied candle (star), followed by long bearish candle closing below first candle's midpoint.

**How / formula:** First candle: large bullish. Second candle (star): small body with gap up from first close, suggesting reduced buying pressure. Third candle: large bearish candle closing below first candle's midpoint. Optional penetration parameter (default 0.3) controls required penetration.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.3, typical 0.0 to 1.0) — Default 0.3. Controls penetration of third candle into first candle body. Higher values require more penetration for stricter signal.

**Interpretation:** Strong bearish reversal at top of uptrend. Third candle closing below first midpoint confirms sellers taking control. Gap up in middle shows buyers exhausted.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/
- https://mondfx.com/morning-star-candlestick-pattern
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Falling Three Methods  `cdlfallinthree`
*candlestick · TA-Lib* · aliases: CDLFALLINTHREE, CDLRISEFALL3METHODS

**What:** Five-candle continuation pattern: large bearish, three small bullish candles within first's range, large bearish closing below first, showing downtrend continuation.

**How / formula:** First: large bearish candle. Candles 2-4: three small bullish candles contained within first candle's body (pullback). Fifth: large bearish closing below first candle.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish continuation pattern. Three small candles within first large bearish candle show pullback consolidation, fifth large bearish confirms continuation.

**Look-ahead risk:** Pattern fully determined at close of fifth candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Gap Side-by-side White Lines  `cdlgapsidesidewhite`
*candlestick · TA-Lib* · aliases: CDLGAPSIDESIDEWHITE

**What:** Two consecutive bullish (white) candles with gap between them, appearing in uptrend or at potential reversal.

**How / formula:** Two white candles with gap up between first close and second open, appearing together in uptrend, showing strength and continuation buying.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Continuation pattern in uptrend. Gap between two white candles shows sustained buying and lack of support at gap level.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Gravestone Doji  `cdlgravestonedoji`
*candlestick · TA-Lib* · aliases: CDLGRAVESTONEDOJI

**What:** A doji variant with a long upper wick and little to no lower wick. The open and close are near the low of the candle range.

**How / formula:** Detection requires open/close near the low, and an upper wick (high) significantly above the open/close, typically at least 2-3 times the body height. Signals buying pressure followed by rejection.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Often bearish when appearing after an uptrend, suggesting buyers could not hold higher prices. The long upper wick shows rejection of higher prices.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://www.tmgm.com/en/academy/trading-academy/doji-candle-stick-pattern
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Hammer  `cdlhammer`
*candlestick · TA-Lib* · aliases: CDLHAMMER

**What:** A single-candle pattern with a small real body near the top of the range and a long lower wick (at least 2-3 times the body length). Typically bullish when appearing after a downtrend.

**How / formula:** Detected when a candle has a small body relative to the candle range, with the lower wick significantly longer than the body. The small upper wick is minimal or absent. Signals that selling pressure during the candle was rejected and absorbed by buyers.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish reversal pattern. After a decline, signals potential trend reversal. The long lower shadow shows sellers initially drove prices down, but buyers recovered most of the loss by close.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://www.metrotrade.com/hammer-candlestick-pattern/
- https://www.strike.money/technical-analysis/hammer-candlestick-pattern
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Hanging Man  `cdlhangingman`
*candlestick · TA-Lib* · aliases: CDLHANGINGMAN

**What:** A single-candle pattern identical in structure to a hammer (small body near top with long lower wick), but appearing after an uptrend instead of a downtrend. Typically bearish.

**How / formula:** Detected when a candle has a small body relative to range, with the lower wick at least 2-3 times the body length. The body appears near the top of the range. Pattern indicates selling pressure emerging at top of uptrend.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal pattern when appearing after uptrend. Signals potential downtrend. The small body and long lower wick show selling entering after buyers pulled back.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://fbs.com/fbs-academy/traders-blog/hanging-man-candlestick-pattern
- https://www.strike.money/technical-analysis/hanging-man
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Harami Pattern  `cdlharami`
*candlestick · TA-Lib* · aliases: CDLHARAMI

**What:** A two-candle reversal pattern where the second candle's body is completely contained within the first candle's body. Opposite of engulfing. Suggests indecision.

**How / formula:** Detected when second candle's open and close both fall within the range of the first candle's open and close. The second candle is typically smaller-bodied. Pattern indicates momentum loss.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal signal suggesting momentum exhaustion. Bullish harami after downtrend: first bearish, second bullish, contained within. Bearish after uptrend: first bullish, second bearish, contained. Often requires confirmation.

**Look-ahead risk:** Pattern confirmed at close of second candle; no repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Harami Cross  `cdlharamicross`
*candlestick · TA-Lib* · aliases: CDLHARAMICROSS

**What:** A variant of harami where the second candle is a doji, completely contained within the first candle's body. Stronger reversal signal than standard harami.

**How / formula:** Detected when first candle has large body, and second candle is a doji (open nearly equals close) with both values within first candle's range. The doji accentuates indecision.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Stronger reversal signal than standard harami due to doji's indecision indicator. Suggests momentum loss and potential reversal. Requires confirmation from next candles.

**Look-ahead risk:** Pattern confirmed at close of second candle; no repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### High-Wave Candle  `cdlhighwave`
*candlestick · TA-Lib* · aliases: CDLHIGHWAVE

**What:** Single-candle pattern with relatively small body and long wicks on both upper and lower ends. Signals indecision similar to doji but with body present.

**How / formula:** Candle shows small body with long shadows extending significantly above and below. Indicates price tested both directions but settled near middle, showing indecision.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Indecision pattern. Unlike doji, has small body. Suggests neither side controls market. Often appears at potential turning points.

**Look-ahead risk:** Pattern fully determined at single completed candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Hikkake  `cdlhikkake`
*candlestick · TA-Lib* · aliases: CDLHIKKAKE

**What:** A reversal pattern based on inside bar formations with specific requirements for the following candle(s) to confirm breakout in opposite direction of initial spike.

**How / formula:** Detects inside bar patterns (second/third candles contained within first) followed by candle(s) with higher highs/lows or lower highs/lows confirming reversal direction opposite to initial direction hint.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern using inside bar setup. When initial direction is tested and reversed, signals potential reversal. Confirmation candle moving opposite to initial direction strengthens signal.

**Look-ahead risk:** Pattern may look-ahead for confirmation candle(s) after the inside bar setup.
- https://tradomate.one/docs/strategy-builder/technical-indicators/pattern-recognition/cdlhikkake/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Modified Hikkake  `cdlhikkakemod`
*candlestick · TA-Lib* · aliases: CDLHIKKAKEMOD

**What:** An improved version of the hikkake pattern with stricter inside bar requirements and better confirmation signals for reversal.

**How / formula:** Similar to hikkake but with additional conditions: inside bar pattern combined with requirements for next candle(s) to show higher lows/highs (bullish) or lower highs/lows (bearish) with more stringent criteria than basic hikkake.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Stricter reversal signal than basic hikkake. Improved confirmation reduces false signals. Useful for traders wanting higher-quality reversal setups.

**Look-ahead risk:** Pattern may reference future candle(s) for confirmation.
- https://tradomate.one/docs/strategy-builder/technical-indicators/pattern-recognition/cdlhikkakemod/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Homingpigeon  `cdlhomingpigeon`
*candlestick · TA-Lib* · aliases: CDLHOMINGPIGEON

**What:** Two-candle bullish reversal pattern where first candle is long bearish, second smaller bullish candle closes within first's body range.

**How / formula:** First: large bearish candle. Second: small bullish candle that opens and closes within first candle's body range, showing buying at lower prices.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish reversal pattern. Smaller second candle within larger first shows buyers entering at lower prices within the decline. Signals potential bottom.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Identical Three Crows  `cdlidentical3crows`
*candlestick · TA-Lib* · aliases: CDLIDENTICAL3CROWS

**What:** Three-candle bearish reversal pattern: three consecutive bearish candles with nearly identical opens and progressively lower closes.

**How / formula:** Three bearish candles with each opening near prior candle's close, creating similar-looking candles stepping lower. Pattern shows consistent selling at similar entry points.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal pattern at top of uptrend. Three identical-looking bearish candles show consistent selling pressure and weakness.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Inverted Hammer  `cdlinvertedhammer`
*candlestick · TA-Lib* · aliases: CDLINVERTEDHAMMER

**What:** A pattern with small body positioned near the low of range and long upper wick (at least 2-3x body). Typically bullish when appearing after a downtrend. Inverse of hammer contextually.

**How / formula:** Detected when candle shows small body at lower part of range with upper wick significantly longer than body. Lower wick minimal. Pattern indicates buyers emerging after downtrend.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish reversal pattern after downtrend. Signals potential uptrend. Buyers pushed prices higher but faced selling; however, the long upper wick shows buying interest emerging.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://www.motilaloswal.com/learning-centre/2023/11/difference-between-shooting-star-and-inverted-hammer-candlestick-patterns
- https://www.strike.money/technical-analysis/inverted-hammer
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Kicking  `cdlkicking`
*candlestick · TA-Lib* · aliases: CDLKICKING

**What:** Two-candle reversal pattern: first large bearish candle, second large bullish candle with gap up, showing sudden reversal of momentum.

**How / formula:** Detected when first candle is large bearish, followed by large bullish candle that gaps up above prior high. The gap between candles is essential. Signals abrupt shift in control.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Strong bullish reversal after sharp downtrend. Gap up combined with large body shows powerful buyer entry at elevated prices. Signals trend reversal.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://www.strike.money/technical-analysis/bullish-kicker
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Kicking by Length  `cdlkickingbylength`
*candlestick · TA-Lib* · aliases: CDLKICKINGBYLENGTH

**What:** Two-candle reversal pattern similar to kicking but with emphasis on the relative length of the bodies rather than just the gap. Both candles must be notably long.

**How / formula:** Detected when two consecutive candles of opposite color are both long-bodied with a gap between them. Emphasizes body length disparity as confirmation of reversal strength.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Stronger reversal signal when both candles are exceptionally long. Longer bodies suggest conviction. Used in stricter reversal identification.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Long Legged Doji  `cdllongleggeddoji`
*candlestick · TA-Lib* · aliases: CDLLONGLEGGEDDOJI

**What:** A doji variant with long wicks on both upper and lower ends and very small or non-existent body. Signals extreme indecision.

**How / formula:** Doji structure (open/close equal/near) with extended wicks both above and below, creating long-legged appearance. Indicates both directions tested extensively.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Strongest indecision signal. Long wicks both directions show neither buyers nor sellers in control. Often appears at turning points or consolidation zones.

**Look-ahead risk:** Pattern fully determined at single completed candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Matching Low  `cdlmatchinglow`
*candlestick · TA-Lib* · aliases: CDLMATCHINGLOW

**What:** Two-candle bullish reversal pattern at bottom of downtrend: two bearish candles with matching lows, showing support testing.

**How / formula:** Two consecutive bearish candles with nearly identical lows, suggesting support testing at same level twice and rejection of lower prices.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish reversal pattern. Two bearish candles with matching lows show support floor being tested and defended, suggesting bottom.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Mat Hold  `cdlmathold`
*candlestick · TA-Lib* · aliases: CDLMATHOLD

**What:** Five-candle bullish continuation pattern: large bullish, three candles moving down within first's range, fifth large bullish closing above all.

**How / formula:** First: large bullish candle. Candles 2-4: three candles declining within first body. Fifth: large bullish closing above first's high. Penetration parameter (default 0.5) controls third candle penetration.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.5, typical 0.0 to 1.0) — Default 0.5. Controls how far down the pullback candles penetrate into first candle.

**Interpretation:** Bullish continuation pattern. Large bullish with pullback contained within followed by large bullish close shows strong buyers.

**Look-ahead risk:** Pattern fully determined at close of fifth candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Morning Doji Star  `cdlmorningdojistar`
*candlestick · TA-Lib* · aliases: CDLMORNINGDOJISTAR

**What:** Variant of morning star where second candle is a doji. Three-candle bullish reversal at bottom of downtrend with doji signaling indecision.

**How / formula:** First: large bearish. Second: doji with gap down (open/close near bottom with wicks). Third: large bullish closing above first's midpoint. Doji marks turning point. Penetration parameter (default 0.3).

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.3, typical 0.0 to 1.0) — Default 0.3. Controls required penetration of third candle into first candle.

**Interpretation:** Stronger bullish reversal than morning star due to doji's indecision marker. Signals shift from selling to buying at trend bottom.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Morning Star  `cdlmorningstar`
*candlestick · TA-Lib* · aliases: CDLMORNINGSTAR

**What:** A three-candle bullish reversal pattern: long bearish candle, followed by a small-bodied candle (star), followed by long bullish candle closing above the midpoint of the first candle.

**How / formula:** First candle: large bearish. Second candle (star): small body with gap down from first candle's close, suggesting reduced selling pressure. Third candle: large bullish candle closing above first candle's midpoint. Optional penetration parameter (default 0.3) controls how far third candle penetrates first candle.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.3, typical 0.0 to 1.0) — Default 0.3 (30%). Controls required penetration of third candle into first candle. Higher values require more penetration, stricter signal. 0.0 accepts minimal penetration, 0.5 requires 50% penetration.

**Interpretation:** Strong bullish reversal appearing at bottom of downtrend. Third candle closing above first candle's midpoint confirms buyers have taken control. Gap down in middle shows sellers exhausted.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://en.wikipedia.org/wiki/Morning_star_(candlestick_pattern)
- https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Piercing Pattern  `cdlpiercing`
*candlestick · TA-Lib* · aliases: CDLPIERCING

**What:** Two-candle bullish reversal pattern: first long bearish candle, second long bullish candle opening below first low, closing above first midpoint.

**How / formula:** First: large bearish. Second: large bullish opening below first close (gap down) and closing above first midpoint. Pattern shows buying pressure overcoming initial selling.

**Inputs:** open, high, low, close
**Outputs:** integer

**Parameters:**
- `penetration` (default 0.5, typical 0.0 to 1.0) — Default 0.5. Controls how far second candle penetrates first candle's body.

**Interpretation:** Bullish reversal at bottom of downtrend. Opening gap down shows selling continuation, but closing above midpoint shows buyers overcoming early selling.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Rising Three Methods  `cdlrisefall3methods`
*candlestick · TA-Lib* · aliases: CDLRISEFALL3METHODS

**What:** Five-candle continuation pattern: large bullish, three small bearish candles within first's range, large bullish closing above first, showing uptrend continuation.

**How / formula:** First: large bullish candle. Candles 2-4: three small bearish candles contained within first candle's body (pullback). Fifth: large bullish closing above first candle.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bullish continuation pattern. Three small candles within first large bullish candle show pullback consolidation, fifth large bullish confirms continuation.

**Look-ahead risk:** Pattern fully determined at close of fifth candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Separating Lines  `cdlseparatinglines`
*candlestick · TA-Lib* · aliases: CDLSEPARATINGLINES

**What:** Two-candle pattern: first bearish candle, second bullish candle opening below first close but closing at same price as first candle, showing trend change.

**How / formula:** First: bearish candle. Second: bullish candle opening gap down below first close but closing at or near same price as first candle.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern. Second candle's ability to gap down and recover to first candle's close level shows buying pressure overcoming initial weakness.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Shooting Star  `cdlshootingstar`
*candlestick · TA-Lib* · aliases: CDLSHOOTINGSTAR

**What:** An inverted hammer pattern with a small real body near the bottom of the range and a long upper wick (at least 2-3 times body length). Typically bearish when appearing after an uptrend.

**How / formula:** Detected when candle has small body positioned near the low of the range, with upper wick significantly longer than body. Lower wick is minimal or absent. Signals buying pressure during candle was rejected.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal pattern. After an uptrend, signals potential reversal. Buyers pushed prices higher intraday but sellers regained control by close, rejecting higher prices.

**Look-ahead risk:** No forward-looking bias; determined by single completed candle.
- https://www.motilaloswal.com/learning-centre/2023/11/difference-between-shooting-star-and-inverted-hammer-candlestick-patterns
- https://www.heygotrade.com/en/blog/shooting-star-candlestick-pattern
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Stick Sandwich  `cdlsticksandwich`
*candlestick · TA-Lib* · aliases: CDLSTICKSANDWICH

**What:** Three-candle pattern: bearish, bullish, bearish with bullish candle's close matching first bearish candle's close, creating sandwich-like structure.

**How / formula:** First: bearish candle. Second: bullish candle closing higher. Third: bearish candle closing at/near first candle's close level. Pattern shows returning to prior price level.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Reversal pattern suggesting temporary buyer entry followed by return to seller control. Sandwich structure at same price level shows indecision.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Takuri  `cdltakuri`
*candlestick · TA-Lib* · aliases: CDLTAKURI

**What:** Single bullish candle with long lower wick and small upper wick appearing in downtrend, similar to hammer but specific to downtrend continuation testing.

**How / formula:** Bullish candle with extended lower wick testing lower support levels and minimal upper wick, showing sellers testing but being rejected.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Potential trend reversal marker. Long lower wick shows support testing and rejection of lower prices in downtrend.

**Look-ahead risk:** Pattern fully determined at single completed candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Tasuki Gap  `cdltasukigap`
*candlestick · TA-Lib* · aliases: CDLTASUKIGAP

**What:** Three-candle pattern: two candles of same color with gap between them, followed by candle filling the gap. Can signal continuation or reversal.

**How / formula:** Two bullish (or bearish) candles with gap between them, followed by opposite color candle that opens gap-up but closes within the gap without fully filling it.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Gap continuation pattern. Two same-color candles with gap followed by opposite color partially filling gap suggests continuation of original direction.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Thrusting Pattern  `cdlthrusting`
*candlestick · TA-Lib* · aliases: CDLTHRUSTING

**What:** Two-candle pattern: bearish candle followed by bullish candle opening gap down but closing back within first candle's body, suggesting thrust into support.

**How / formula:** First: large bearish candle. Second: bullish candle opening below first's close and closing within first's body but below its close. Shows failed support test.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish continuation pattern. Failed thrust above support suggests support holding and downtrend continuing.

**Look-ahead risk:** Pattern fully determined at close of second candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html

### Upside Gap Two Crows  `cdlugaptwocrwos`
*candlestick · TA-Lib* · aliases: CDLUGAPTWOCRWOS

**What:** Three-candle bearish reversal pattern: bullish candle, gap up, then two bearish candles, second of which closes into first candle's body.

**How / formula:** First: large bullish. Gap up. Second: bearish candle. Third: bearish candle closing into first candle's body. Pattern shows buyers losing control from elevated prices.

**Inputs:** open, high, low, close
**Outputs:** integer

**Interpretation:** Bearish reversal pattern. Gap up followed by two crows closing back into first candle shows buyer enthusiasm reversed.

**Look-ahead risk:** Pattern fully determined at close of third candle. No repainting.
- https://ta-lib.github.io/ta-lib-python/func_groups/pattern_recognition.html



## chart-pattern  (3)

### Heikin-Ashi  `heikin_ashi`
*chart-pattern · Japanese candlestick modification* · aliases: Heikin Ashi, HA candles, Smoothed candlesticks

**What:** Alternative candlestick representation smoothing OHLC data by averaging prices, reduces noise and clarifies trends

**How / formula:** HA_Close = (O + H + L + C) / 4. HA_Open = (HA_Open_prev + HA_Close_prev) / 2. HA_High = MAX(H, HA_Open, HA_Close). HA_Low = MIN(L, HA_Open, HA_Close). First HA_Open uses regular open; then recursive. Output replaces OHLC with smoothed values.

**Inputs:** open, high, low, close
**Outputs:** ha_open, ha_high, ha_low, ha_close

**Interpretation:** White candles = uptrend; red candles = downtrend. No wicks = clean trend. Wicks appearing = trend weakening. Candle body reversals = potential reversals. Long white bodies = strong uptrend; long red bodies = strong downtrend. Simplifies price action visualization.

**Look-ahead risk:** None; transformation of OHLC data; backward-looking only
- https://www.litefinance.org/blog/for-beginners/types-of-forex-charts/heikin-ashi-candles/
- https://ninjatrader.com/futures/blogs/heikin-ashi-candlestick-charts-explained/
- https://www.britannica.com/money/heikin-ashi-candlestick-chart

### Williams Fractals  `williams_fractals`
*chart-pattern · Bill Williams (Trading Chaos)* · aliases: Bill Williams Fractals, Fractal indicator, Williams 5-bar pattern

**What:** Five-bar pattern identifying local highs/lows; bullish fractal (3 bars higher lows), bearish (3 bars lower highs)

**How / formula:** Bullish Fractal: 2 bars with higher low than current low, then 2 bars after with higher low. Middle bar must be lowest low. Bearish Fractal: 2 bars with lower high than current high, then 2 bars after with lower high. Middle bar must be highest high. Appears 2 bars after turning point.

**Inputs:** high, low
**Outputs:** bullish_fractal, bearish_fractal

**Interpretation:** Bullish fractals = potential reversal points (support for long entries). Bearish fractals = potential reversal points (resistance for short entries). Often used with Alligator indicator. Fractals appear after fact (2 bars), confirming reversal already underway. Stop-loss placement above bearish/below bullish fractal.

**Look-ahead risk:** High: fractal appears 2 bars after reversal point; not leading indicator. Confirmation tool, not entry signal
- https://www.ifcmarkets.com/en/ntx-indicators/fractals
- https://www.luxalgo.com/blog/williams-fractal-spotting-reversal-in-trends/
- https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals

### ZigZag  `zigzag`
*chart-pattern · Technical analysis pattern recognition* · aliases: Zig-Zag, ZZ filter, Trend filter

**What:** Trend filter removing minor fluctuations to identify primary price movements and swing points

**How / formula:** Filters price moves below threshold (typically 5% minimum). Draws lines connecting significant highs and lows. Eliminates noise, clarifies swings. Recalculates as new prices form; can repaint. Threshold percentage determines sensitivity.

**Inputs:** high, low, close
**Outputs:** zigzag_line

**Parameters:**
- `threshold_percent` (default 5, typical 2-10) — Standard 5%; lower (2-3) shows more swings; higher (8-10) only major moves

**Interpretation:** ZigZag peaks/troughs = significant swing points for Elliott Wave counting. Lines show primary trend direction. Useful for identifying corrections vs impulses. Not for entry signals; primarily analytical tool for wave pattern recognition.

**Look-ahead risk:** High: repaint risk. ZigZag redraws as new bars arrive; prior fractals/levels change. Not for real-time trade signals
- https://commodity.com/technical-analysis/zig-zag/
- https://www.tradingview.com/scripts/zigzagindicator/
- https://trendoscope.io/



## cycle  (8)

### DPO (Detrended Price Oscillator)  `dpo`
*cycle · pandas-ta* · aliases: DPO, Detrended Price, Cycle Oscillator

**What:** A trend-removal indicator that subtracts a shifted moving average from price to isolate cycles, helping identify periodic patterns and turning points without the influence of the primary trend.

**How / formula:** Calculates t = int(0.5 * length) + 1. DPO = close - SMA(close, length) shifted forward by t periods. If centered=True (default), DPO is shifted back by t to align with current bar. This removes trend and emphasizes cyclical components.

**Inputs:** close
**Outputs:** DPO

**Parameters:**
- `length` (default 20, typical 14-50) — MA period; longer periods capture longer cycles
- `centered` (default True, typical true|false) — True aligns DPO to current bar but creates lookahead; False uses forward shift

**Interpretation:** Crosses around zero indicate cycle turning points. Peaks/troughs show cycle extremes. Use to identify cycle period but DO NOT use centered=True for real-time trading.

**Look-ahead risk:** CRITICAL: centered=True creates lookahead bias. For real-time use, set centered=False or use non-centered periods, and understand you're seeing future-shifted values.
- https://tradingstrategy.ai/docs/api/technical-analysis/trend/help/pandas_ta.trend.dpo.html

### Detrended Price Oscillator  `dpo`
*cycle · FinTA, bukosabino/ta* · aliases: DPO

**What:** An indicator removing the trend component from price by comparing current price to a simple moving average shifted backward in time, used to identify underlying price cycles and cyclical bottoms/tops.

**How / formula:** DPO = Close - SMA(close, period) shifted backward by (period / 2 + 1) bars. Example: 20-period DPO shifts back 11 bars (20/2 + 1). Current bar's DPO uses close from 11 bars ago minus the current 20-period SMA.

**Inputs:** close
**Outputs:** dpo_value

**Parameters:**
- `period` (default 20, typical [10, 50]) — 20 is standard for identifying 40-bar cycles. Adjust to match suspected cycle length (typically period × 2).
- `shift` (default auto, typical ['auto', 'custom']) — Default auto-shifts by (period / 2 + 1). Custom shift for specific cycle targeting.

**Interpretation:** DPO oscillates around zero without directional bias. Peaks identify potential cycle tops; troughs identify potential cycle bottoms. Not used for entry signals (too much lag); used for cycle timing and reversal identification. Zero crossovers may signal cycle transitions.

**Look-ahead risk:** Backward shift introduces significant lag. DPO at bar 20 represents the state from bar 9. Do not use for real-time trading; use for historical cycle analysis.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo

### Detrended Price Oscillator  `dpo`
*cycle · William Blau (1991)* · aliases: DPO, Detrended Price

**What:** Eliminates trend to focus on cycles by subtracting displaced moving average from price, identifies cyclical turning points

**How / formula:** DPO = Close(t - (n/2 + 1)) - SMA(n). Displaces SMA backward by (n/2 + 1) periods, then subtracts from historical close. Removes long-term trend, isolates price cycles. Output oscillates around zero.

**Inputs:** close
**Outputs:** dpo

**Parameters:**
- `period` (default 21, typical 10-50) — Standard 21; reflects typical cycle length. Higher periods (50+) identify longer cycles. Lower periods (10-14) shorter cycles.

**Interpretation:** Cycle highs/lows visible in DPO show cyclical turning points. DPO does NOT provide real-time signals (displaced). Use to identify cycle phases and rhythm. Rising DPO = entering cycle peak phase. Falling = entering trough phase.

**Look-ahead risk:** High: DPO displaced backward; not suitable for real-time trading signals. Best for identifying cycles, not entry points
- https://en.wikipedia.org/wiki/Detrended_price_oscillator
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/dpo

### Hilbert Transform - Dominant Cycle Period  `ht_dcperiod`
*cycle · TA-Lib* · aliases: HT_DCPERIOD, DC Period

**What:** A Hilbert Transform-based indicator that measures the dominant cycle period in price data, identifying the predominant oscillation frequency of the market

**How / formula:** Uses the Hilbert Transform and Autocorrelation Periodogram Algorithm to detect the dominant cycle. The algorithm performs 4-bar weighted smoothing, applies Hilbert detrending to isolate cyclic components, decomposes the signal into in-phase (I) and quadrature (Q) components, and applies autocorrelation analysis to determine the period. The output is measured in bars.

**Inputs:** close
**Outputs:** real

**Interpretation:** Returns the estimated period of the dominant cycle in bars. Higher values indicate longer cycles. Useful for identifying whether the market is in a fast or slow oscillation mode.

**Look-ahead risk:** All HT_DCPERIOD outputs have an unstable period at the beginning of the dataset. Initial values are unreliable and should be discarded.
- https://ta-lib.github.io/ta-lib-python/func_groups/cycle_indicators.html
- https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/cycle_indicators.md

### Hilbert Transform - Dominant Cycle Phase  `ht_dcphase`
*cycle · TA-Lib* · aliases: HT_DCPHASE, DC Phase

**What:** Measures the phase angle of the dominant cycle, determining the position within the current cycle oscillation

**How / formula:** Uses the Hilbert Transform methodology to determine the phase angle of detected dominant cycle. Phase is measured using the arctangent of the quadrature component divided by the in-phase component from the Hilbert decomposition. Phase values range from 0 to 360 degrees.

**Inputs:** close
**Outputs:** real

**Interpretation:** Phase values range from 0-360 degrees. Indicates the current position in the cycle (0° = trough, 90° = rising peak, 180° = peak, 270° = falling trough). Used to time entries at cycle turning points.

**Look-ahead risk:** Has an unstable period. Initial phase calculations are unreliable.
- https://ta-lib.github.io/ta-lib-python/func_groups/cycle_indicators.html
- https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/cycle_indicators.md

### Hilbert Transform - Phasor Components  `ht_phasor`
*cycle · TA-Lib* · aliases: HT_PHASOR, Phasor

**What:** Decomposes price into in-phase and quadrature components of the Hilbert Transform, representing orthogonal oscillation vectors

**How / formula:** Applies Hilbert Transform detrending to extract cyclic components. Creates a phasor (complex vector) representation through 90-degree phase shifting. The in-phase component (I) represents the price detrended signal, while the quadrature component (Q) is a 90-degree phase-shifted version. Formula: Q_component = 90° phase shift of I_component.

**Inputs:** close
**Outputs:** inphase, quadrature

**Interpretation:** Returns two values: inphase and quadrature. Together they form a vector representation of price cycles. When quadrature leads inphase, price is rising; when inphase leads quadrature, price is falling. Crossovers signal cycle turning points.

**Look-ahead risk:** Has an unstable period; initial component calculations are unreliable.
- https://ta-lib.github.io/ta-lib-python/func_groups/cycle_indicators.html
- https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/cycle_indicators.md

### Hilbert Transform - SineWave  `ht_sine`
*cycle · TA-Lib* · aliases: HT_SINE, Sine Wave, Ehlers Sine Wave

**What:** Generates a phase-locked sine wave synchronized to the dominant market cycle, plus a 45-degree advanced lead signal for cycle turning point prediction

**How / formula:** Calculates the sine of the measured dominant cycle phase angle. The sine output represents the dominant oscillation. The leadsine is calculated as sine of (phase + 45°), creating an advance of 1/8th cycle. Formula: sine = sin(phase), leadsine = sin(phase + 45°). Both values oscillate between -1 and +1.

**Inputs:** close
**Outputs:** sine, leadsine

**Interpretation:** Returns two oscillators (sine and leadsine). Sine oscillates with the cycle; leadsine leads it by 45°. When sine and leadsine cross, major turning points often occur. Leadsine crosses before sine peaks/troughs by approximately 1/8th of a cycle. Values range from -1 to +1.

**Look-ahead risk:** Has an unstable period. Initial values unreliable. Leadsine is inherently forward-looking but not truly predictive as it derives from the same phase measurement.
- https://ta-lib.github.io/ta-lib-python/func_groups/cycle_indicators.html
- https://tradomate.one/docs/strategy-builder/technical-indicators/cycle/ht-sine/

### Hilbert Transform - Trend vs Cycle Mode  `ht_trendmode`
*cycle · TA-Lib* · aliases: HT_TRENDMODE, Trend Mode

**What:** Binary indicator distinguishing trending market conditions from cycling/oscillating conditions by analyzing dominant cycle strength

**How / formula:** Analyzes the relative strength and coherence of detected cycles versus trend components. Returns integer values: -100 (strong trend down), 0 (cycle/range-bound), or 100 (strong trend up). Uses the Hilbert Transform cycle detection to determine if price is dominated by trend or cyclic behavior.

**Inputs:** close
**Outputs:** integer

**Interpretation:** Three output values: 100 = strong uptrend (use trend-following strategies), 0 = cycle mode (use range/oscillator strategies), -100 = strong downtrend. Helps traders select appropriate strategies based on market regime.

**Look-ahead risk:** Has an unstable period. Initial trend/cycle classification may be incorrect.
- https://ta-lib.github.io/ta-lib-python/func_groups/cycle_indicators.html
- https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/cycle_indicators.md



## momentum  (62)

### Awesome Oscillator  `ao`
*momentum · FinTA, bukosabino/ta* · aliases: AO

**What:** A momentum oscillator measuring the difference between a fast (5-period) and slow (34-period) simple moving average of the median price (high + low)/2, designed to identify trend changes and divergences.

**How / formula:** Median Price = (High + Low) / 2. AO = SMA(Median Price, 5) - SMA(Median Price, 34). Output oscillates around zero as a histogram with red/green bar coloring.

**Inputs:** high, low
**Outputs:** awesome_oscillator

**Parameters:**
- `fast_period` (default 5, typical [5, 5]) — Fixed at 5 per Bill Williams standard. Rarely modified.
- `slow_period` (default 34, typical [34, 34]) — Fixed at 34 per Bill Williams standard. Rarely modified.

**Interpretation:** Positive AO signals bullish momentum; negative signals bearish. Zero-line crossovers generate trend-change signals. Divergences (price makes new high but AO lower) signal potential reversals. Twin peaks pattern (two consecutive bars of same color and height) confirms signal.

**Look-ahead risk:** Minimal lag from moving averages. No repainting.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://www.tradingview.com/support/solutions/43000501826-awesome-oscillator-ao/

### Absolute Price Oscillator  `apo`
*momentum · TA-Lib* · aliases: APO

**What:** Equivalent to MACD but expressed as absolute difference between two EMAs rather than normalized. Measures the distance between short and long-term moving averages.

**How / formula:** APO = EMA(fast_period) - EMA(slow_period). Default: 12-period EMA minus 26-period EMA. Result is the raw difference in price units, not normalized. Positive APO indicates bullish momentum; negative indicates bearish momentum.

**Inputs:** close
**Outputs:** APO

**Parameters:**
- `fastperiod` (default 12, typical 5-20) — 12 is standard for short-term sensitivity. Shorter periods increase responsiveness to price changes.
- `slowperiod` (default 26, typical 20-50) — 26 is standard for baseline trend. Longer periods reduce noise and false signals.

**Interpretation:** Positive values: bullish momentum. Negative values: bearish momentum. Larger absolute values indicate stronger momentum. Zero crossover signals momentum direction change.

**Look-ahead risk:** Unstable period: approximately (slowperiod - 1) bars. Initial ~25 bars unreliable. No inherent repainting; standard EMA lag applies.
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/apo
- https://ta-lib.github.io/ta-lib-python/func_groups/momentum_indicators.html

### Aroon Oscillator  `aroonosc`
*momentum · TA-Lib* · aliases: AROONOSC

**What:** The difference between Aroon Up and Aroon Down. Oscillates between -100 and +100 to highlight trend direction and strength via recent highs/lows timing.

**How / formula:** AROONOSC = Aroon Up - Aroon Down. Both components calculated as per AROON. Positive values indicate uptrend (Aroon Up > Aroon Down); negative values indicate downtrend. Magnitude reflects how dominant the trend direction is.

**Inputs:** high, low
**Outputs:** aroonosc

**Parameters:**
- `timeperiod` (default 14, typical 5-28) — 14 is standard. Shorter periods increase oscillation amplitude and trend change sensitivity.

**Interpretation:** > 0: uptrend (closer to 100 = stronger). < 0: downtrend (closer to -100 = stronger). Crossing zero signals potential trend reversal. Extremes (near ±100) indicate strong directional trends.

**Look-ahead risk:** No unstable period. No repainting; based purely on recent high/low timing.
- https://lightningchart.com/blog/trader/aroon-price-oscillator-indicator/
- https://trendspider.com/learning-center/aroon-oscillator-a-guide-for-traders-and-investors/

### Awesome Oscillator  `awesome_oscillator`
*momentum · Bill Williams* · aliases: AO, Bill Williams AO, Awesome

**What:** Bill Williams' histogram oscillator measuring difference between 5-period and 34-period midpoint moving averages

**How / formula:** AO = 5-period SMA of midpoint - 34-period SMA of midpoint, where midpoint = (High + Low) / 2. Plotted as histogram: green bars = current > previous; red bars = current < previous. Oscillates around zero.

**Inputs:** high, low
**Outputs:** awesome_oscillator

**Parameters:**
- `fast_period` (default 5, typical 3-7) — Standard 5; controls fast MA sensitivity
- `slow_period` (default 34, typical 30-40) — Standard 34; controls slow MA baseline

**Interpretation:** Zero-line crossovers = momentum direction changes (above = bullish, below = bearish). Twin Peaks = two consecutive peaks same side of zero (second higher) followed by color change = entry signal. Saucer = histogram color change before zero-cross.

**Look-ahead risk:** None; uses only historical high/low midpoints
- https://www.tradingview.com/support/solutions/43000501826-awesome-oscillator-ao/
- https://www.avatrade.com/education/technical-analysis-indicators-strategies/awesome-oscillator-indicator-strategies
- https://www.warriortrading.com/awesome-oscillator/

### BIAS (Bias from Moving Average)  `bias`
*momentum · pandas-ta* · aliases: BIAS, Price/MA Ratio

**What:** A mean-reversion oscillator that measures the percentage deviation of price from a moving average, identifying overbought/oversold conditions relative to trend.

**How / formula:** BIAS = (close / MA(close, length) - 1) * 100 or (close - MA(close, length)) / MA(close, length) * 100. Positive values = price above MA (bullish); negative = below MA (bearish).

**Inputs:** close
**Outputs:** BIAS

**Parameters:**
- `length` (default 26, typical 12-50) — MA period; longer = smoother baseline
- `mamode` (default sma, typical sma|ema|dema|zlma|others) — SMA standard; EMA/DEMA more responsive

**Interpretation:** BIAS > 5% = overbought; < -5% = oversold. Extreme values (> 10%) often precede reversals. Crossing zero indicates MA alignment with price.

**Look-ahead risk:** No lookahead bias; uses only past price and MA values.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/bias.html

### Balance of Power  `bop`
*momentum · TA-Lib* · aliases: BOP

**What:** Measures the strength of buyers versus sellers by comparing opening and closing prices relative to the high-low range. Oscillates between -1 and +1.

**How / formula:** BOP = (Close - Open) / (High - Low). If (High - Low) = 0, BOP = 0. Positive BOP indicates buyer dominance (close near high). Negative BOP indicates seller dominance (close near low). Zero indicates balance.

**Inputs:** open, high, low, close
**Outputs:** BOP

**Interpretation:** BOP > 0: buyers in control. BOP < 0: sellers in control. BOP = 0: balanced. Values closer to ±1 indicate extreme control. Often smoothed with SMA (14-period typical) to reduce noise and identify sustained pressure.

**Look-ahead risk:** No unstable period. Purely contemporaneous; no repainting risk.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop
- https://www.luxalgo.com/blog/chande-momentum-oscillator-measuring-momentum-extremes/

### BRAR (Bear-Bull Power Indicator)  `brar`
*momentum · pandas-ta* · aliases: BRAR, AR, BR, Bull-Bear Power

**What:** A momentum indicator that measures buying and selling power separately by comparing daily high/low ranges to opening price and prior closing price, indicating trend strength.

**How / formula:** AR = scalar * SUM(high - open, length) / SUM(open - low, length). BR = scalar * SUM(HCY, length) / SUM(CYL, length) where HCY = max(0, high - close[prev]) and CYL = max(0, close[prev] - low).

**Inputs:** open, high, low, close
**Outputs:** AR, BR

**Parameters:**
- `length` (default 26, typical 14-50) — Lookback period; 26 is standard
- `scalar` (default 100, typical 1-100) — 100 scales output; 1 for 0-1 range

**Interpretation:** AR > 100 = strong bullish power (high open relative to range); BR > 100 = strong buying pressure from prior close. Divergences signal reversals. Both high = strong momentum.

**Look-ahead risk:** No lookahead bias; uses only OHLC within lookback window.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/brar.html

### Commodity Channel Index  `cci`
*momentum · TA-Lib* · aliases: CCI

**What:** Measures deviation of typical price from its simple moving average relative to mean deviation. Identifies overbought/oversold conditions and trend extremes.

**How / formula:** TP (Typical Price) = (High + Low + Close) / 3. SMA_TP = 20-period SMA of TP. Mean Deviation = average absolute deviation of TP from SMA_TP over 20 periods. CCI = (TP - SMA_TP) / (0.015 × Mean Deviation). The 0.015 constant ensures 70-80% of CCI values fall within ±100 range.

**Inputs:** high, low, close
**Outputs:** CCI

**Parameters:**
- `timeperiod` (default 20, typical 10-40) — 20 is standard. Shorter periods (10-14) increase volatility and sensitivity; longer periods (30-40) increase percentage of values within ±100 range, smoother readings.

**Interpretation:** CCI > 100: overbought/bullish extreme. CCI < -100: oversold/bearish extreme. ±100 band contains ~70-80% of values in normal markets. Readings between ±100 indicate normal conditions. Zero crossovers signal momentum direction changes.

**Look-ahead risk:** Unstable period: timeperiod + 1 bars. Initial mean deviation calculations unreliable. No inherent repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cci

### Commodity Channel Index  `cci`
*momentum · FinTA, bukosabino/ta* · aliases: CCI

**What:** An oscillator measuring the variance of price from its simple moving average relative to mean deviation, identifying overbought/oversold conditions without directional bias.

**How / formula:** Typical Price (TP) = (High + Low + Close) / 3. SMA_TP = SMA(TP, 20). Mean Deviation = Sum(|TP - SMA_TP|) / 20. CCI = (TP - SMA_TP) / (0.015 × Mean Deviation). Constant 0.015 scales most CCI values to ±100 range.

**Inputs:** high, low, close
**Outputs:** cci_value

**Parameters:**
- `period` (default 20, typical [10, 30]) — 20 is standard. Shorter periods increase sensitivity; longer periods smooth noise.
- `constant` (default 0.015, typical [0.015, 0.015]) — Fixed at 0.015 per Donald Lambert's design to scale to ±100.

**Interpretation:** CCI > 100 indicates overbought (potential sell signal or reversal). CCI < -100 indicates oversold (potential buy signal). Zero-line crossovers signal trend changes. Divergences identify potential reversals. CCI between -100 and +100 indicates normal range.

**Look-ahead risk:** None. Calculated from prior OHLC.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci

### Commodity Channel Index  `cci`
*momentum · Tulip Indicators, Donald Lambert (1980)* · aliases: CCI, Commodity Channel

**What:** Oscillator measuring current price versus mean price over period, identifies cyclical trends and overbought/oversold conditions

**How / formula:** Typical Price (TP) = (High + Low + Close) / 3. SMA_TP = 20-period SMA of TP. Mean Deviation = average absolute difference from SMA_TP. CCI = (TP - SMA_TP) / (0.015 × Mean Deviation). Scaling factor 0.015 ensures 70-80% of values fall ±100.

**Inputs:** high, low, close
**Outputs:** cci

**Parameters:**
- `period` (default 20, typical 10-30) — Standard 20; shorter (10) more sensitive signals; longer (30) fewer false signals

**Interpretation:** CCI > +100 = overbought. CCI < -100 = oversold. Values between -100/+100 = normal range. Crossings of ±100 signal trades. Divergences warn of reversals. Works best in ranging, cyclical markets.

**Look-ahead risk:** None; backward-looking mean deviation calculation
- https://tulipindicators.org/cci
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cci

### Center of Gravity  `cg`
*momentum · pandas-ta* · aliases: CG, Ehlers CG, CoG Oscillator

**What:** A zero-lag momentum oscillator developed by John Ehlers that identifies turning points and generates reversal signals by measuring the center of gravity of prices.

**How / formula:** Calculates the weighted average position of prices where each bar position i is weighted by its price: CG = -SUM(i * close[i]) / SUM(close[i]). Then smooths with SMA to create the final oscillator. Attempts zero-lag representation of momentum.

**Inputs:** close
**Outputs:** CG

**Parameters:**
- `length` (default 10, typical 8-14) — Period for summation and center calculation

**Interpretation:** Zero-line crossovers = trend changes. Extreme values = turning points imminent. Peaks/troughs with price divergence = reversal signals. Fast oscillations = range-bound; smooth = trending.

**Look-ahead risk:** No lookahead bias; uses only historical prices within lookback window.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.cg.html

### Chande Momentum Oscillator  `cmo`
*momentum · TA-Lib* · aliases: CMO

**What:** Measures momentum by comparing sum of gains to sum of losses over a period, normalized to ±100 scale. Similar to RSI but different smoothing method (simple vs Wilder's).

**How / formula:** SU = sum of all up day closes (where close > previous close) over n periods. SD = sum of absolute down day closes (where close < previous close) over n periods. CMO = 100 × (SU - SD) / (SU + SD). Days with close = previous close are ignored. Result ranges -100 to +100.

**Inputs:** close
**Outputs:** CMO

**Parameters:**
- `timeperiod` (default 14, typical 10-20) — 14 is common for stocks; 20 is traditional Chande's default. Shorter periods increase sensitivity and oscillation amplitude.

**Interpretation:** CMO > 50: overbought/strong uptrend. CMO < -50: oversold/strong downtrend. ±50 levels mark extremes. Zero crossover signals momentum direction change. High CMO with rising prices = strong trend; high CMO with declining prices = potential reversal.

**Look-ahead risk:** Unstable period: first timeperiod bars. Uses simple summation (not Wilder's smoothing), so convergence faster than RSI but less stable early on.
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
- https://lightningchart.com/blog/trader/chande-momentum-oscillator/

### Coppock Curve  `coppock`
*momentum · pandas-ta* · aliases: COPC, Coppock

**What:** A long-term momentum indicator designed to identify buying opportunities by measuring the rate of change of price momentum using weighted moving averages of two different ROC periods.

**How / formula:** Calculates ROC(close, fast) + ROC(close, slow) where ROC is rate of change. Then applies a WMA (weighted moving average) of length periods to smooth the sum. Originally designed for monthly timeframes but adapts to daily data.

**Inputs:** close
**Outputs:** COPC

**Parameters:**
- `length` (default 10, typical 8-14) — 10 is standard WMA period; higher values reduce noise
- `fast` (default 11, typical 9-13) — 11 periods for short-term ROC momentum
- `slow` (default 14, typical 12-20) — 14 periods for long-term ROC momentum

**Interpretation:** Zero-line crossover from below to above signals long entry. Positive divergence with new lows suggests buying opportunity. Most effective on monthly timeframes but usable on daily.

**Look-ahead risk:** No lookahead bias; uses only past price data and historical ROC calculations.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.coppock.html

### Elder Ray Index  `eri`
*momentum · pandas-ta* · aliases: ERI, Elder Ray, Bull Power, Bear Power

**What:** A trend-strength indicator developed by Alexander Elder that separates buying and selling power by measuring the distance of highs and lows from an EMA, indicating momentum direction.

**How / formula:** BULLP = high - EMA(close, length). BEARP = low - EMA(close, length). Positive Bull Power = buyers lifting prices above EMA. Negative Bear Power = sellers pushing below EMA. Divergences with price indicate strength shifts.

**Inputs:** high, low, close
**Outputs:** BULLP, BEARP

**Parameters:**
- `length` (default 13, typical 10-20) — EMA period; 13 is standard

**Interpretation:** Both positive = strong uptrend. Both negative = strong downtrend. Mixed signals = weakness in trend. Declining Bull Power while uptrend = warning. Divergences often precede reversals.

**Look-ahead risk:** No lookahead bias; uses only current period highs/lows vs. historical EMA.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/eri.html

### Fisher Transform  `fisher`
*momentum · pandas-ta* · aliases: FISHT, Fisher

**What:** A normalization indicator that converts price oscillations into a Gaussian normal distribution using logarithmic transformation, generating a mean-reverting oscillator with clear reversal signals.

**How / formula:** Calculates HL2 = (high+low)/2, finds HLR = highest(HL2,length) - lowest(HL2,length). Then position = ((HL2-lowest)/HLR) - 0.5, applies smoothing v = 0.66*position + 0.67*v (bounded ±0.999), then FISHER = 0.5 * ln((1+v)/(1-v)) + FISHER[i-1]. Signal line is FISHER shifted by signal periods.

**Inputs:** high, low
**Outputs:** FISHER, FISHER_Signal

**Parameters:**
- `length` (default 9, typical 5-14) — 9 is standard; 5-7 for responsive markets, 10-14 for stable
- `signal` (default 1, typical 1-3) — 1 shifts Fisher by 1 bar; higher values smooth the trigger line

**Interpretation:** Extreme values (>2 or <-2) suggest overbought/oversold; reversals occur at crossovers between FISHER and signal line. Sharp peaks/troughs indicate imminent reversals.

**Look-ahead risk:** No lookahead bias. Uses only past price data and recursive calculation.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/fisher.html

### Inertia  `inertia`
*momentum · pandas-ta* · aliases: Inertia, RSI Autocorrelation

**What:** A correlation-based momentum indicator that measures the strength of a trend by calculating the autocorrelation of RSI, indicating how much RSI resembles its lagged values.

**How / formula:** Calculates RSI(close, length). Then computes R-squared (coefficient of determination) between RSI and RSI[1] over a lookback period. High R² = strong persistence/trend; low = mean-reverting oscillation.

**Inputs:** close
**Outputs:** Inertia

**Parameters:**
- `length` (default 20, typical 14-30) — RSI period and lookback for R² calculation

**Interpretation:** Inertia > 0.5 = trending (RSI persistent); < 0.5 = oscillating (RSI mean-reverting). Use with RSI: high Inertia + overbought RSI = stronger reversal signal.

**Look-ahead risk:** No lookahead bias; uses only past RSI values for autocorrelation.
- https://github.com/twopirllc/pandas-ta

### KDJ (Stochastic with J-Line)  `kdj`
*momentum · pandas-ta* · aliases: KDJ, J-Line Stochastic, K-D-J

**What:** An enhanced stochastic oscillator variant popular in Asian markets that adds a J-line divergence component, allowing values to extend beyond the 0-100 range of K and D lines.

**How / formula:** FastK = 100 * (close - LL(length)) / (HH(length) - LL(length)). K = RMA(FastK, signal). D = RMA(K, signal). J = 3K - 2D. LL = lowest low; HH = highest high over length periods.

**Inputs:** high, low, close
**Outputs:** K, D, J

**Parameters:**
- `length` (default 9, typical 7-14) — Lookback period for highest high / lowest low
- `signal` (default 3, typical 2-5) — Smoothing period for K and D lines; 3 is standard

**Interpretation:** K > 80 = overbought; < 20 = oversold. K-D crossover = momentum change. J divergence indicates extreme conditions. J > 100 or < 0 signals extreme volatility.

**Look-ahead risk:** No lookahead bias; uses only past highs/lows and historical smoothing.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.kdj.html

### KST (Know Sure Thing)  `kst`
*momentum · pandas-ta* · aliases: Know Sure Thing, Pring KST

**What:** A multi-timeframe momentum oscillator that combines four ROC (rate of change) indicators with different periods, weighted and smoothed to generate actionable trading signals.

**How / formula:** Calculates ROC1=ROC(close,p1) smoothed with EMA(s1), ROC2=ROC(close,p2) smoothed with EMA(s2), ROC3=ROC(close,p3) smoothed with EMA(s3), ROC4=ROC(close,p4) smoothed with EMA(s4). Then KST = 1*ROC1 + 2*ROC2 + 3*ROC3 + 4*ROC4. Signal line = EMA(KST, signal).

**Inputs:** close
**Outputs:** KST, KST_Signal

**Parameters:**
- `p1` (default 10, typical 8-15) — Shortest ROC period
- `p2` (default 15, typical 12-20) — Short-medium ROC period
- `p3` (default 20, typical 18-25) — Medium-long ROC period
- `p4` (default 30, typical 25-35) — Longest ROC period for overall trend
- `s1` (default 10, typical 8-15) — EMA smoothing for p1
- `s2` (default 10, typical 8-15) — EMA smoothing for p2
- `s3` (default 10, typical 8-15) — EMA smoothing for p3
- `s4` (default 10, typical 8-15) — EMA smoothing for p4
- `signal` (default 9, typical 7-15) — Signal line period for crossovers

**Interpretation:** KST crossing above signal line = bullish; below = bearish. Divergences between price and KST indicate potential reversals. Zero-line crossovers confirm momentum shifts.

**Look-ahead risk:** No lookahead bias; uses historical ROC and EMA calculations only.
- https://github.com/twopirllc/pandas-ta

### Know Sure Thing  `kst`
*momentum · FinTA, bukosabino/ta* · aliases: KST, Pring's KST

**What:** A momentum oscillator developed by Martin Pring that combines four smoothed Rate of Change indicators across different timeframes to measure momentum across multiple price cycles.

**How / formula:** KST = SMA(ROC(close, r1), s1) + SMA(ROC(close, r2), s2) + SMA(ROC(close, r3), s3) + SMA(ROC(close, r4), s4). Standard parameters: r1=10/s1=10, r2=15/s2=10, r3=20/s3=10, r4=30/s4=15. Signal line = SMA(KST, 9).

**Inputs:** close
**Outputs:** kst_value, kst_signal

**Parameters:**
- `roc1_period` (default 10, typical [8, 12]) — First ROC period for fastest momentum measurement.
- `roc1_ma` (default 10, typical [8, 15]) — Smoothing of first ROC.
- `roc2_period` (default 15, typical [12, 20]) — Second ROC period.
- `roc2_ma` (default 10, typical [8, 15]) — Smoothing of second ROC.
- `roc3_period` (default 20, typical [18, 25]) — Third ROC period.
- `roc3_ma` (default 10, typical [8, 15]) — Smoothing of third ROC.
- `roc4_period` (default 30, typical [25, 40]) — Fourth ROC period for longest cycle.
- `roc4_ma` (default 15, typical [12, 20]) — Smoothing of fourth ROC.
- `signal_period` (default 9, typical [5, 14]) — SMA period for signal line (KST crossover trigger).

**Interpretation:** Positive KST signals bullish momentum; negative signals bearish. KST crossing signal line generates buy/sell signals. Zero-line crossovers confirm momentum shifts. Divergences (price at new high but KST lower) signal potential reversals. Multi-timeframe smoothing reduces false signals vs single ROC.

**Look-ahead risk:** Lag from double smoothing (multiple moving averages). Less erratic than raw ROC but signals arrive later.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst

### Know Sure Thing  `kst`
*momentum · Martin Pring (1992, Stocks & Commodities Magazine)* · aliases: KST, Pring's Know Sure Thing, Martin Pring KST

**What:** Complex smoothed momentum oscillator combining four weighted rate-of-change calculations, identifies trend direction and strength

**How / formula:** KST = [1×ROC10 + 2×ROC15 + 3×ROC20 + 4×ROC30] each smoothed with 10, 10, 10, 15-period SMAs respectively, then sum and apply final SMA. Signal line = 9-period EMA of KST. Developed by Martin Pring; introduced 1992.

**Inputs:** close
**Outputs:** kst, kst_signal

**Parameters:**
- `roc1_period` (default 10, typical 8-12) — First ROC period
- `roc1_smooth` (default 10, typical 8-12) — First ROC smoothing
- `roc2_period` (default 15, typical 13-18) — Second ROC period
- `roc2_smooth` (default 10, typical 8-12) — Second ROC smoothing
- `roc3_period` (default 20, typical 18-22) — Third ROC period
- `roc3_smooth` (default 10, typical 8-12) — Third ROC smoothing
- `roc4_period` (default 30, typical 28-35) — Fourth ROC period (longest)
- `roc4_smooth` (default 15, typical 12-18) — Fourth ROC smoothing

**Interpretation:** KST > 0 = bullish momentum; KST < 0 = bearish. KST crossing signal line = trade signal. KST > signal line = strong momentum. Rising KST = accelerating uptrend. Unlike RSI/Stochastic, KST unbounded (no upper/lower limits); not suitable for overbought/oversold levels.

**Look-ahead risk:** None; uses only completed bar data from multiple lookback periods
- https://en.wikipedia.org/wiki/KST_oscillator
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst
- https://www.tradingview.com/support/solutions/43000502329-know-sure-thing-kst/

### Moving Average Convergence Divergence  `macd`
*momentum · TA-Lib* · aliases: MACD

**What:** A trend-following momentum indicator showing the relationship between two exponential moving averages (fast and slow). Returns three values: MACD line, signal line, and histogram.

**How / formula:** MACD = 12-period EMA - 26-period EMA. Signal Line = 9-period EMA of MACD. Histogram = MACD - Signal Line. Positive MACD = bullish (fast EMA above slow). Crossovers and divergences signal trend changes. Histogram shows MACD momentum.

**Inputs:** close
**Outputs:** outMACD, outMACDsignal, outMACDhist

**Parameters:**
- `fastperiod` (default 12, typical 5-20) — 12 is standard. Shorter periods increase sensitivity to recent price action.
- `slowperiod` (default 26, typical 20-50) — 26 is standard. Longer periods establish baseline trend reference.
- `signalperiod` (default 9, typical 5-15) — 9 is standard for signal line. Shorter periods produce more crossover signals; longer periods reduce false signals.

**Interpretation:** MACD > Signal: bullish. MACD < Signal: bearish. MACD crossing above Signal: buy signal. MACD crossing below Signal: sell signal. Divergences (price makes new high/low but MACD does not) signal potential reversals. Histogram magnitude shows momentum strength.

**Look-ahead risk:** Unstable period: (slowperiod - 1) + (signalperiod - 1) ≈ 33 bars. Initial ~25-35 bars unreliable. No repainting risk; standard EMA properties.
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd
- https://ta-lib.github.io/ta-lib-python/func_groups/momentum_indicators.html

### Moving Average Convergence Divergence  `macd`
*momentum · Tulip Indicators, standard technical analysis* · aliases: MACD oscillator, Moving Average Convergence Divergence oscillator

**What:** A trend-following momentum indicator that shows the relationship between two exponential moving averages of closing prices

**How / formula:** MACD = 12-period EMA - 26-period EMA. Signal line = 9-period EMA of MACD. Histogram = MACD - Signal line. The indicator creates three outputs: the MACD line (difference between EMAs), signal line (smoothed MACD), and histogram (divergence between them).

**Inputs:** close
**Outputs:** macd, signal, histogram

**Parameters:**
- `short_period` (default 12, typical 9-14) — Standard 12; adjust lower (8-10) for faster signals in volatile markets
- `long_period` (default 26, typical 24-30) — Standard 26; provides baseline trend; higher values smooth out noise
- `signal_period` (default 9, typical 7-12) — Standard 9; use lower values for more frequent signals

**Interpretation:** Bullish: MACD crosses above signal line or stays above zero. Bearish: MACD crosses below signal line or stays below zero. Histogram size indicates momentum strength. Divergences signal potential reversals.

**Look-ahead risk:** None; calculated from historical prices only
- https://tulipindicators.org/macd
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/macd-moving-average-convergence-divergence-oscillator
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd

### Moving Average Convergence Divergence Extended  `macdext`
*momentum · TA-Lib* · aliases: MACDEXT

**What:** MACD with customizable moving average types for each component (fast EMA, slow EMA, signal line). Provides flexibility beyond standard MACD exponential moving averages.

**How / formula:** Calculates MACD using specified moving average types for fast and slow periods, plus signal line MA type. Formula identical to MACD but allows SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, or other MA types. Returns MACD, signal, and histogram values.

**Inputs:** close
**Outputs:** outMACD, outMACDsignal, outMACDhist

**Parameters:**
- `fastperiod` (default 12, typical 5-20) — 12 is standard default.
- `fastmatype` (default EMA, typical SMA/EMA/WMA/DEMA/TEMA/TRIMA/KAMA/MAMA) — EMA is most common; others allow experimentation with different smoothing characteristics.
- `slowperiod` (default 26, typical 20-50) — 26 is standard default.
- `slowmatype` (default EMA, typical SMA/EMA/WMA/DEMA/TEMA/TRIMA/KAMA/MAMA) — EMA is most common; allows custom trend baseline smoothing.
- `signalperiod` (default 9, typical 5-15) — 9 is standard default.
- `signalmatype` (default EMA, typical SMA/EMA/WMA/DEMA/TEMA/TRIMA/KAMA/MAMA) — EMA is most common; allows custom signal line smoothing.

**Interpretation:** Same as standard MACD interpretation. MA type choice affects responsiveness: EMA = standard, SMA = smoother, WMA = recent-bar weighted, DEMA/TEMA = less lagging.

**Look-ahead risk:** Varies by MA type chosen. EMA-based: ~33 bars unstable (standard MACD). SMA/WMA: ~slowperiod bars. DEMA/TEMA: faster convergence but potentially less stable.
- https://www.fmz.com/lang/en/syntax-guide/fun/talib/talib.macdext

### Money Flow Index  `mfi`
*momentum · TA-Lib* · aliases: MFI

**What:** A volume-weighted RSI that measures buying and selling pressure. Incorporates volume to identify overbought/oversold conditions more accurately than RSI alone.

**How / formula:** TP (Typical Price) = (High + Low + Close) / 3. Raw Money Flow = TP × Volume. Compare TP[today] vs TP[yesterday]: if higher = Positive Money Flow; if lower = Negative Money Flow. Sum positive/negative flows over n periods. Money Flow Ratio = Sum Positive MF / Sum Negative MF. MFI = 100 - (100 / (1 + Ratio)). Result ranges 0-100.

**Inputs:** high, low, close, volume
**Outputs:** MFI

**Parameters:**
- `timeperiod` (default 14, typical 10-20) — 14 is standard. Shorter periods increase sensitivity to volume shifts; longer periods smooth noise.

**Interpretation:** MFI > 80: overbought (potential reversal). MFI < 20: oversold (potential bounce). MFI 50: equilibrium. Divergences between price and MFI signal trend weakness. Rising MFI with rising price = strong trend; falling MFI with rising price = weakening uptrend.

**Look-ahead risk:** Unstable period: timeperiod bars. Depends on volume data availability. No repainting; purely lookback-based.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi
- https://www.luxalgo.com/blog/mfi-vs-rsi-key-differences-explained/

### Momentum  `mom`
*momentum · TA-Lib* · aliases: MOM

**What:** Simple momentum indicator measuring price change over a specified period. Positive values indicate upward momentum; negative values indicate downward momentum.

**How / formula:** MOM = Close[today] - Close[n periods ago]. Result is the absolute price change (not percentage). Positive MOM = price higher than n periods ago. Negative MOM = price lower than n periods ago. Oscillates around zero.

**Inputs:** close
**Outputs:** MOM

**Parameters:**
- `timeperiod` (default 10, typical 5-20) — 10 is common default; 12 or 14 also popular. Shorter periods increase sensitivity to recent moves; longer periods identify major momentum trends.

**Interpretation:** MOM > 0: upward momentum (price higher than n periods ago). MOM < 0: downward momentum (price lower). Larger absolute values indicate stronger momentum. Zero crossing signals momentum direction change. Compare to price: divergences indicate weakening trends.

**Look-ahead risk:** No unstable period; purely lookback-based. First n bars have undefined prior values.
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/momentum-oscillator
- https://www.warriortrading.com/momentum-indicator/

### Momentum Oscillator  `momentum`
*momentum · Tulip Indicators, standard technical analysis* · aliases: MOM, Price momentum, Simple momentum

**What:** Raw momentum measured as difference between current price and price n periods ago, shows velocity of price change

**How / formula:** Momentum = Current Close - Close n periods ago. Plotted around zero line. Positive = upward momentum; negative = downward. Oscillates above/below zero reflecting price acceleration/deceleration.

**Inputs:** close
**Outputs:** momentum

**Parameters:**
- `period` (default 10, typical 5-14) — Standard 10; shorter (5) more responsive; longer (14) smoother

**Interpretation:** Zero-line crossovers signal momentum direction changes. Positive divergence (price down, momentum up) suggests bullish reversal. Extreme values indicate overbought/oversold. Momentum peaks/troughs precede price peaks/troughs.

**Look-ahead risk:** None; simple price difference calculation
- https://tulipindicators.org/mom
- https://thismatter.com/money/technical-analysis/momentum.htm

### PGO (Pretty Good Oscillator)  `pgo`
*momentum · pandas-ta* · aliases: PGO, Pretty Good Oscillator, Mark Johnson Oscillator

**What:** A volatility-normalized oscillator created by Mark Johnson that measures the distance of price from its moving average in units of ATR, generating breakout signals.

**How / formula:** PGO = (close - SMA(close, length)) / EMA(ATR(length), length). Dividing by volatility (ATR) normalizes the distance. Results typically -3 to +3 with extremes signaling breakouts.

**Inputs:** high, low, close
**Outputs:** PGO

**Parameters:**
- `length` (default 14, typical 10-20) — Period for SMA, ATR, and EMA components

**Interpretation:** PGO > 3.0 = strong bullish breakout; < -3.0 = strong bearish breakout. Values between -3 and 3 = normal trading range. Use for entry/exit with trend filters.

**Look-ahead risk:** No lookahead bias; uses only current/past price and volatility data.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.pgo.html

### Percentage Price Oscillator  `ppo`
*momentum · TA-Lib* · aliases: PPO

**What:** MACD expressed as a percentage. Normalizes the MACD difference by the longer EMA, making it comparable across securities with different price levels.

**How / formula:** PPO = ((12-period EMA - 26-period EMA) / 26-period EMA) × 100. Signal Line = 9-period EMA of PPO. Histogram = PPO - Signal. Functionally equivalent to MACD but scaled in percentage terms rather than absolute price units.

**Inputs:** close
**Outputs:** outPPO, outPPOsignal, outPPOhist

**Parameters:**
- `fastperiod` (default 12, typical 5-20) — 12 is standard.
- `slowperiod` (default 26, typical 20-50) — 26 is standard.
- `signalperiod` (default 9, typical 5-15) — 9 is standard.

**Interpretation:** PPO > Signal: bullish. PPO < Signal: bearish. PPO crossing above Signal: buy signal. PPO crossing below Signal: sell signal. Histogram magnitude shows momentum. PPO is directly comparable across securities; $500 stock and $5 stock show comparable PPO values.

**Look-ahead risk:** Unstable period: ~33 bars (slowperiod - 1 + signalperiod - 1). Initial ~25-35 bars unreliable. No repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo
- https://www.luxalgo.com/blog/price-oscillator-ppo-indicator-comparing-two-moving-averages/

### PSL (Psychological Line)  `psl`
*momentum · pandas-ta* · aliases: PSL, Psychological Line

**What:** An oscillator that measures market psychology by calculating the percentage of periods where price closes higher than previous, expressed as a ratio of bullish to total periods.

**How / formula:** Counts closing periods above previous close (or above open if available). PSL = (scalar * SUM(close > close[drift], length)) / length. Result ranges 0-100 (with scalar=100) indicating percentage of up days in the period.

**Inputs:** close, open (optional)
**Outputs:** PSL

**Parameters:**
- `length` (default 12, typical 8-20) — Number of periods to count; 12 is standard
- `scalar` (default 100, typical 1-100) — 100 expresses as percentage 0-100
- `drift` (default 1, typical 1) — Compare to previous bar

**Interpretation:** PSL > 70 = strong bullish sentiment; < 30 = strong bearish. Values 40-60 = indecision/balance. Divergences with price indicate sentiment reversal.

**Look-ahead risk:** No lookahead bias; counts only historical close comparisons.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.psl.html

### QQE (Quantitative Qualitative Estimation)  `qqe`
*momentum · pandas-ta* · aliases: QQE, Quantitative Qualitative Estimation

**What:** A volatility-adjusted momentum indicator that uses smoothed RSI with dynamic bands to identify trends and reversals, similar to Supertrend but applied to momentum rather than price.

**How / formula:** Calculates RSI(close, length), then smooths with EMA(rsi, smooth). Calculates TR of smoothed RSI, then applies Wilder's double smoothing (2*length-1). Multiplies by factor to create bands around smoothed RSI. Band width expands/contracts with volatility.

**Inputs:** close
**Outputs:** QQE, RSI_MA, QQE_long, QQE_short

**Parameters:**
- `length` (default 14, typical 10-21) — RSI period; 14 is standard
- `smooth` (default 5, typical 3-7) — RSI smoothing period for cleaner signal
- `factor` (default 4.236, typical 3.0-5.0) — 4.236 is standard band width multiplier
- `mamode` (default ema, typical ema|sma) — EMA provides smoother bands than SMA

**Interpretation:** Long signal when smoothed RSI crosses above previous upper band; short when crossing below previous lower band. Bands expand in trending markets, contract in ranges.

**Look-ahead risk:** Bands use historical TR; potential repainting if bands adjust based on current bar data—verify implementation.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.qqe.html

### QStick Indicator  `qstick`
*momentum · Tushar Chande* · aliases: QStick, Quick Stick, Chande Quick Stick

**What:** Simple momentum indicator measuring average difference between close and open prices; directly shows buying pressure

**How / formula:** QStick = SMA/EMA(Close - Open, n). Positive values = closes higher than opens (bullish). Negative values = closes lower than opens (bearish). Magnitude shows strength of pressure. Calculation simple: average of daily close-open differences.

**Inputs:** open, close
**Outputs:** qstick

**Parameters:**
- `period` (default 14, typical 8-21) — Common 8, 10, 14; shorter more responsive; longer smoother. Developed by Tushar Chande.

**Interpretation:** QStick > 0 = buying pressure increasing (bullish). QStick < 0 = selling pressure increasing (bearish). Magnitude = strength. Zero-line crossovers = momentum shifts. Rising QStick = accelerating purchases. Divergences with price signal reversals.

**Look-ahead risk:** None; simple open-close difference average
- https://www.stockmaniacs.net/qstick-indicator/
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/qstick-indicator/
- https://www.samco.in/knowledge-center/articles/qstick-indicator/

### Rate of Change  `roc`
*momentum · TA-Lib* · aliases: ROC

**What:** Percentage change in price over a specified period. Measures the speed of price momentum relative to historical baseline.

**How / formula:** ROC = ((Close[today] - Close[n periods ago]) / Close[n periods ago]) × 100. Result is percentage change; positive = upward momentum, negative = downward momentum. Oscillates around zero.

**Inputs:** close
**Outputs:** ROC

**Parameters:**
- `timeperiod` (default 12, typical 5-20) — 9 or 14 are preferred for momentum analysis. Shorter periods increase sensitivity; longer periods identify major momentum trends. 12-period common for monthly comparison.

**Interpretation:** ROC > 0: positive momentum (price higher than n periods ago). ROC < 0: negative momentum. Larger absolute values indicate stronger momentum. Zero crossing signals momentum direction change. High ROC with rising prices = strong trend. High ROC with falling prices = potential reversal.

**Look-ahead risk:** No unstable period; lookback-based only.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc
- https://gocharting.com/docs/charting/technical-indicator/momentum/price-rateofchange-indicator

### Rate of Change  `roc`
*momentum · Tulip Indicators* · aliases: ROC, Price rate of change, Momentum percentage

**What:** Percentage-based momentum indicator measuring the speed of price change relative to starting price over period

**How / formula:** ROC = [(Current Price - Price n periods ago) / (Price n periods ago)] × 100. Expressed as percentage change. Positive ROC = price increase; negative = decrease. Oscillates around zero.

**Inputs:** close
**Outputs:** roc

**Parameters:**
- `period` (default 12, typical 9-14) — Standard 12; common also 9 and 14. Shorter more responsive, longer smoother

**Interpretation:** ROC > 0 = bullish momentum; ROC < 0 = bearish. Zero-line crossovers signal momentum shifts. Rising/falling ROC shows acceleration/deceleration. ROC peaks before price peaks; warns of momentum fading.

**Look-ahead risk:** None; uses only historical price comparison
- https://tulipindicators.org/roc
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/roc

### Rate of Change Percentage  `rocp`
*momentum · TA-Lib* · aliases: ROCP

**What:** Identical to ROC; measures percentage price change over a period. Expressed as decimal (0-1 range) or percentage (0-100 range) depending on convention.

**How / formula:** ROCP = (Close[today] - Close[n periods ago]) / Close[n periods ago]. Same as ROC formula but often expressed as decimal before multiplication by 100. Result ranges approximately -1 to +1 (before scaling) and represents fractional price change.

**Inputs:** close
**Outputs:** ROCP

**Parameters:**
- `timeperiod` (default 12, typical 5-20) — Same as ROC; 9 or 14 preferred. Varies by application.

**Interpretation:** Identical to ROC interpretation. ROCP = 0.05 equivalent to ROC = 5%. Values centered at zero. Positive values = upward momentum; negative values = downward momentum.

**Look-ahead risk:** No unstable period; lookback-based only.
- https://thismatter.com/money/technical-analysis/momentum.htm

### Rate of Change Ratio  `rocr`
*momentum · TA-Lib* · aliases: ROCR

**What:** Ratio of current price to price n periods ago. Ranges from 0 to infinity, centered at 1.0. Positive values only (no negative values like ROC/ROCP).

**How / formula:** ROCR = Close[today] / Close[n periods ago]. Result always >= 0. ROCR = 1.0 means no change. ROCR > 1.0 means upward momentum. ROCR < 1.0 means downward momentum. Can be converted to percentage by subtracting 1 and multiplying by 100.

**Inputs:** close
**Outputs:** ROCR

**Parameters:**
- `timeperiod` (default 12, typical 5-20) — Same as ROC variants; 9 or 14 preferred.

**Interpretation:** ROCR > 1.0: upward momentum. ROCR < 1.0: downward momentum. ROCR = 1.0: no momentum. Further from 1.0 indicates stronger momentum. More intuitive for compound returns than ROC percentage.

**Look-ahead risk:** No unstable period; lookback-based only. Division by zero risk if price[n periods ago] = 0 (highly unlikely in normal markets).
- https://thismatter.com/money/technical-analysis/momentum.htm

### Rate of Change Ratio 100 Scale  `rocr100`
*momentum · TA-Lib* · aliases: ROCR100

**What:** ROCR scaled by 100 for readability. Ranges from 0 to infinity, centered at 100. Equivalent to ROC but using ratio form.

**How / formula:** ROCR100 = (Close[today] / Close[n periods ago]) × 100. ROCR100 = 100 means no change. ROCR100 > 100 means upward momentum. ROCR100 < 100 means downward momentum. Result directly comparable to percentage format.

**Inputs:** close
**Outputs:** ROCR100

**Parameters:**
- `timeperiod` (default 12, typical 5-20) — Same as ROC variants; 9 or 14 preferred.

**Interpretation:** ROCR100 > 100: upward momentum. ROCR100 < 100: downward momentum. ROCR100 = 100: no momentum. ROCR100 = 110 means 10% gain; ROCR100 = 90 means 10% loss. Combines ratio intuitiveness with percentage readability.

**Look-ahead risk:** No unstable period; lookback-based only.
- https://www.myfxbook.com/forex-market/indicators/rocr100/

### Relative Strength Index  `rsi`
*momentum · TA-Lib* · aliases: RSI

**What:** Measures the magnitude of recent price changes to evaluate overbought/oversold conditions. Ranges 0-100; developed by J. Welles Wilder in 1978.

**How / formula:** Calculate average gain and average loss over n periods (default 14) using Wilder's smoothing: First Avg Gain = Sum of gains/n; subsequent: ((Previous Avg Gain × (n-1)) + Current Gain) / n. Same for losses. RS = Avg Gain / Avg Loss. RSI = 100 - (100 / (1 + RS)). Wilder's smoothing creates lag but produces less spurious signals than simple averaging.

**Inputs:** close
**Outputs:** RSI

**Parameters:**
- `timeperiod` (default 14, typical 9-25) — 14 is Wilder's standard and most common. 7 for faster trending markets; 21 for slower markets. Shorter periods increase oversold/overbought signal frequency.

**Interpretation:** RSI > 70: overbought (potential reversal). RSI < 30: oversold (potential bounce). RSI 50: neutral. Divergences between RSI and price signal trend weakness. Rising RSI with rising prices = strong trend. Falling RSI with rising prices = weakening trend. RSI is not a trade signal alone; use with price action and volume.

**Look-ahead risk:** Unstable period: (timeperiod * 2 - 1) + 5 ≈ 32 bars for first meaningful RSI. Wilder's smoothing creates convergence lag; initial ~30 bars unreliable. Approximately 150 bars needed for true convergence. No repainting; lookback-based.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi
- https://help.tc2000.com/m/69404/l/747071-rsi-wilder-s-rsi

### Relative Strength Index  `rsi`
*momentum · Tulip Indicators, J. Welles Wilder Jr. (1978)* · aliases: RSI, Wilder's RSI

**What:** A bounded oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions

**How / formula:** Calculates average gains and losses over a period (smoothed EMA-style). RS = average gain / average loss. RSI = 100 - (100 / (1 + RS)). Output ranges 0-100. First calculates simple average over n periods, then uses smoothed averages for subsequent values using: [(previous avg × (n-1)) + current value] / n

**Inputs:** close
**Outputs:** rsi

**Parameters:**
- `period` (default 14, typical 5-21) — Standard 14; lower periods (7-9) for faster signals in volatile markets; higher (21) for fewer false signals

**Interpretation:** RSI > 70 = overbought (potential sell); RSI < 30 = oversold (potential buy). Center crossover at 50 indicates momentum shift. Divergences between price and RSI signal potential reversals. Most effective in 30-70 range for ranging markets.

**Look-ahead risk:** None; backward-looking momentum indicator
- https://tulipindicators.org/rsi
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI

### RSX (Relative Strength Xtra)  `rsx`
*momentum · pandas-ta* · aliases: RSX, Relative Strength Xtra, Jurik RSX

**What:** An enhanced RSI variant inspired by Jurik Research that reduces noise while maintaining responsiveness, providing cleaner momentum signals with minimal lag.

**How / formula:** Based on published ProRealCode implementation referencing Jurik Research methods. Uses proprietary smoothing algorithm to filter RSI values while minimizing lag compared to standard RSI. Exact formula proprietary but achieves similar 0-100 range with improved signal clarity.

**Inputs:** close
**Outputs:** RSX

**Parameters:**
- `length` (default 14, typical 10-21) — 14 is standard RSI period; 10 for responsive markets, 21 for stable
- `drift` (default 1, typical 1-2) — Difference period for ROC calculation

**Interpretation:** RSX > 70 = overbought; < 30 = oversold. Used like RSI but with cleaner signals. Divergences with price are more reliable due to noise reduction.

**Look-ahead risk:** No lookahead bias; uses only historical price data and proprietary smoothing.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.rsx.html

### Relative Vigor Index  `rvgi`
*momentum · pandas-ta* · aliases: RVGI, RVI, Vigor Index

**What:** A momentum indicator that measures the conviction of price action by comparing the tendency of closing prices to be higher or lower than opening prices within the period range.

**How / formula:** Calculates SWMA(close-open, swma_length) for numerator sum and SWMA(high-low, swma_length) for denominator sum over length periods. RVGI = SUM(numerator) / SUM(denominator). SWMA is symmetrically weighted moving average.

**Inputs:** open, high, low, close
**Outputs:** RVGI

**Parameters:**
- `length` (default 14, typical 10-20) — Lookback period for summation; 14 is standard
- `swma_length` (default 4, typical 3-6) — SWMA smoothing period; 4 is conventional

**Interpretation:** RVGI > 0.5 = uptrend strength; < -0.5 = downtrend strength. Divergences signal potential reversals. Value between -0.5 and 0.5 indicates range/consolidation.

**Look-ahead risk:** No lookahead bias; uses only OHLC data within lookback window.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.rvgi.html

### Relative Vigor Index  `rvi`
*momentum · Tulip Indicators, Donald Dorsey* · aliases: RVI, Relative Vigor Index

**What:** Oscillator based on concept that prices close higher than open in uptrends and lower in downtrends, measures momentum

**How / formula:** Numerator = [(C-O) + 2(C1-O1) + 2(C2-O2) + (C3-O3)] / 6 over 10 periods. Denominator = [(H-L) + 2(H1-L1) + 2(H2-L2) + (H3-L3)] / 6 over same. RVI = SMA(numerator,10) / SMA(denominator,10). Signal = 4-period symmetrically weighted MA of RVI.

**Inputs:** open, high, low, close
**Outputs:** rvi, rvi_signal

**Parameters:**
- `period` (default 10, typical 7-14) — Standard 10; shorter more responsive; longer smoother
- `signal_period` (default 4, typical 3-6) — Standard 4; signal line smoothing

**Interpretation:** RVI > signal line = bullish; RVI < signal line = bearish. Crossovers generate trade signals. Centerline (0.5) crossovers indicate momentum shift. Divergences warn of reversals. Works best in ranging markets.

**Look-ahead risk:** None; uses open/close relationship over completed bars
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index
- https://www.tradingview.com/support/solutions/43000591593-relative-vigor-index/
- https://forexopher.com/relative-vigor-index-rvi-formula-and-uses-in-trading/

### SMI Ergodic (Stochastic Momentum Index)  `smi`
*momentum · pandas-ta* · aliases: SMI, Stochastic Momentum Index, SMI Ergodic

**What:** A refinement of the stochastic oscillator that measures momentum by comparing closing price position to its high-low range using double smoothing, with integrated signal line.

**How / formula:** Calculates (close - lowest low) / (highest high - lowest low), applies double EMA smoothing to both numerator and denominator. Divides smoothed numerator by smoothed denominator, scales to -100 to +100. Signal line = EMA of SMI.

**Inputs:** close, high, low
**Outputs:** SMI, SMI_Signal

**Parameters:**
- `length` (default 14, typical 10-21) — Lookback period for highs/lows
- `fast` (default 3, typical 2-5) — First smoothing EMA period
- `slow` (default 3, typical 2-5) — Second smoothing EMA period
- `signal` (default 3, typical 2-5) — Signal line EMA period

**Interpretation:** SMI > 40 = overbought; < -40 = oversold. Crossover with signal line generates trading signals. Divergences with price indicate potential reversals.

**Look-ahead risk:** No lookahead bias; uses only past price data and historical smoothing.
- https://github.com/twopirllc/pandas-ta

### TTM Squeeze  `squeeze`
*momentum · pandas-ta* · aliases: squeeze_pro, SQZPRO, John Carter Squeeze

**What:** An extended version of John Carter's TTM Squeeze that identifies periods of low volatility (squeeze) by comparing Bollinger Bands to Keltner Channels, generating momentum signals and squeeze state indicators.

**How / formula:** Compares BB (20-period SMA, 2 std dev) against three KC variations (scalars 2.0 wide, 1.5 normal, 1.0 narrow). When BB falls inside KC, squeeze is ON. Also calculates 12-period momentum smoothed with 6-period EMA. Returns momentum value and squeeze state flags (ON_WIDE, ON_NORMAL, ON_NARROW, OFF_WIDE).

**Inputs:** high, low, close
**Outputs:** SQZPRO, squeeze_state

**Parameters:**
- `bb_length` (default 20, typical 15-25) — 20 is standard for volatility measurement
- `bb_std` (default 2, typical 1.5-2.5) — 2 is conventional; 1.5 for tighter squeeze detection
- `kc_length` (default 20, typical 15-25) — 20 matches BB length for consistency
- `kc_scalar_wide` (default 2, typical 1.8-2.5) — 2.0 is standard for widest channel
- `kc_scalar_normal` (default 1.5, typical 1.3-1.7) — 1.5 is midpoint
- `kc_scalar_narrow` (default 1, typical 0.8-1.2) — 1.0 is tightest channel
- `mom_length` (default 12, typical 9-15) — 12 is standard for momentum period
- `mom_smooth` (default 6, typical 3-9) — 6 smooths momentum for cleaner signals

**Interpretation:** Squeeze ON signals low volatility periods; OFF_WIDE signals expansion/breakout opportunity. Momentum value indicates trend direction within squeeze. Use with trend filters for best results.

**Look-ahead risk:** No lookahead bias; uses current period data. Momentum is derived contemporaneously.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.squeeze_pro.html
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/squeeze_pro.html

### Schaff Trend Cycle  `stc`
*momentum · pandas-ta* · aliases: STC, Schaff Trend Cycle

**What:** An evolution of MACD that applies two cascaded stochastic calculations to MACD to create a momentum oscillator with faster reversals and less whipsaws than MACD alone.

**How / formula:** Calculates MACD(fast, slow). Applies first stochastic to MACD. Applies second stochastic with smoothing factor to first stochastic. Result is STC oscillator bounded 0-100. Can also accept external moving averages (ma1, ma2) or oscillator (osc) inputs.

**Inputs:** close
**Outputs:** STC, MACD, Stoch

**Parameters:**
- `tclen` (default 10, typical 8-14) — Schaff TC signal-line length; typically half the cycle
- `fast` (default 12, typical 10-15) — Fast EMA period for MACD component
- `slow` (default 26, typical 20-30) — Slow EMA period for MACD component
- `factor` (default 0.5, typical 0.3-0.7) — Smoothing factor for second stochastic; lower=smoother

**Interpretation:** STC > 75 = overbought; < 25 = oversold. Centerline (50) crossover indicates momentum shift. Use extreme levels for reversal signals.

**Look-ahead risk:** No lookahead bias; cascaded stochastic uses only historical MACD values.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.stc.html

### Stochastic Oscillator  `stoch`
*momentum · TA-Lib* · aliases: STOCH

**What:** Measures the level of closing price relative to high-low range over n periods. Produces %K line (raw) and %D line (signal). Full version with smoothing of both lines.

**How / formula:** %K_raw = ((Close - Lowest Low) / (Highest High - Lowest Low)) × 100. %K (full/slow) = 3-period SMA of %K_raw. %D = 3-period SMA of %K. Full Stochastic (STOCH) returns slowK and slowD; Fast (STOCHF) returns raw and fast-smoothed versions.

**Inputs:** high, low, close
**Outputs:** slowk, slowd

**Parameters:**
- `fastk_period` (default 5, typical 5-14) — 5 is common for daily charts. Lower values increase sensitivity.
- `slowk_period` (default 3, typical 1-5) — 3 is standard smoothing period for %K line (transforms fast to slow Stochastic).
- `slowd_period` (default 3, typical 1-5) — 3 is standard signal line period (creates %D).

**Interpretation:** %K > %D and both > 50: strong uptrend. %K < %D and both < 50: strong downtrend. %K crossing above %D: buy signal. %K crossing below %D: sell signal. %K > 80: overbought. %K < 20: oversold. Divergences indicate weakening trends.

**Look-ahead risk:** Unstable period: (fastk_period - 1) + (slowk_period - 1) + (slowd_period - 1) ≈ 7 bars. Initial bar cannot have full 5-period high-low range. No repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochastic-oscillator-fast-slow-and-full
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/stochrsi

### Stochastic RSI  `stoch_rsi`
*momentum · Tushar Chande / Stanley Kroll* · aliases: Stoch RSI, StochRSI, Stochastic of RSI

**What:** Second-order oscillator applying stochastic formula to RSI values instead of prices, creates range-bound momentum of momentum

**How / formula:** Calculate RSI (typically 14 periods). Apply stochastic formula to RSI: StochRSI = (RSI - Lowest RSI n) / (Highest RSI n - Lowest RSI n). Output 0-100 (or 0-1). Combines momentum measurement with range-bound oscillator.

**Inputs:** close
**Outputs:** stoch_rsi

**Parameters:**
- `rsi_period` (default 14, typical 10-21) — Standard 14; controls RSI calculation sensitivity
- `stoch_period` (default 14, typical 10-21) — Standard 14; lookback for stochastic highest/lowest RSI
- `smooth_k` (default 3, typical 1-5) — Smoothing of %K line
- `smooth_d` (default 3, typical 1-5) — Smoothing of %D signal line

**Interpretation:** StochRSI > 0.8 (80) = overbought. StochRSI < 0.2 (20) = oversold. Developed by Tushar Chande. More sensitive than RSI alone. Prone to false signals; use with confirmation. Better for identifying pullbacks in strong trends.

**Look-ahead risk:** Double smoothing creates lag; based on historical RSI extremes
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/stochrsi
- https://www.tradingview.com/support/solutions/43000502333-stochastic-rsi-stoch-rsi/

### Stochastic Oscillator  `stochastic`
*momentum · Tulip Indicators, George Lane (1950s)* · aliases: Stochastic, Slow Stochastic (when smoothed), Fast Stochastic (raw calculation)

**What:** Compares a closing price to price range over a period, expressing where current price sits within recent highs/lows as a percentage 0-100

**How / formula:** %K = 100 × (Current Close - Lowest Low n) / (Highest High n - Lowest Low n). %D = 3-period SMA of %K. The indicator measures price position within the period's range: 0% at bottom, 100% at top.

**Inputs:** high, low, close
**Outputs:** %K, %D

**Parameters:**
- `period` (default 14, typical 5-21) — Standard 14; shorter periods (9) for faster signals; longer (21) for smoother results
- `smooth_k` (default 3, typical 1-5) — Standard 3; creates %K from raw stochastic smoothing
- `smooth_d` (default 3, typical 1-5) — Standard 3; moving average of %K for signal line

**Interpretation:** %K > 80 = overbought; %K < 20 = oversold. Crossover of %K above %D (bullish); %K below %D (bearish). Most reliable in ranging markets; less effective in strong trends.

**Look-ahead risk:** None; based on historical highs/lows within window only
- https://tulipindicators.org/stoch
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochastic-oscillator-fast-slow-and-full
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/fast-stochastic

### Stochastic Oscillator Fast  `stochf`
*momentum · TA-Lib* · aliases: STOCHF

**What:** Fast Stochastic with minimal smoothing. Returns raw %K (unsmoothed) and fast %D (single smoothing). More responsive than full Stochastic but choppier.

**How / formula:** %K = ((Close - Lowest Low) / (Highest High - Lowest Low)) × 100. %D = SMA of %K over specified periods (default 3). No second smoothing layer applied (unlike full Stochastic). Faster to respond to extremes but generates more false signals.

**Inputs:** high, low, close
**Outputs:** fastk, fastd

**Parameters:**
- `fastk_period` (default 5, typical 5-14) — 5 is common. Lower values increase volatility of output.
- `fastd_period` (default 3, typical 1-5) — 3 is standard single smoothing. Higher values reduce choppiness.

**Interpretation:** %K > 80: overbought. %K < 20: oversold. %K crossing above %D: buy signal (faster than full Stochastic). %K crossing below %D: sell signal. More whipsaws due to reduced smoothing; benefits from additional confirmation indicators.

**Look-ahead risk:** Unstable period: (fastk_period - 1) + (fastd_period - 1) ≈ 6 bars. Minimal lag due to no double smoothing. No repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochastic-oscillator-fast-slow-and-full

### Stochastic Relative Strength Index  `stochrsi`
*momentum · TA-Lib* · aliases: STOCHRSI

**What:** Applies Stochastic formula to RSI values instead of prices. Measures the level of RSI relative to its high-low range. Oscillates 0-1 (or 0-100 scaled).

**How / formula:** Calculate RSI over n periods (default 14). StochRSI = ((RSI - Lowest RSI) / (Highest RSI - Lowest RSI)) over m periods (default 14). Results range 0-1. Often scaled to 0-100 or smoothed further with K/D lines similar to Stochastic.

**Inputs:** close
**Outputs:** fastk, fastd

**Parameters:**
- `timeperiod` (default 14, typical 9-21) — 14 is standard for both RSI and stochastic lookback periods.
- `fastk_period` (default 5, typical 1-5) — Controls smoothing of StochRSI itself; 5 is common.
- `fastd_period` (default 3, typical 1-3) — Signal line period; 3 is standard.

**Interpretation:** StochRSI > 0.80: overbought (potential reversal). StochRSI < 0.20: oversold (potential bounce). StochRSI crossing above 0.20: buy signal (from oversold). StochRSI crossing below 0.80: sell signal (from overbought). Indicator of indicator; more extreme oscillations than RSI alone.

**Look-ahead risk:** Unstable period: (timeperiod * 2 - 1) + 5 + (fastk_period - 1) + (fastd_period - 1) ≈ 40+ bars. Double smoothing (RSI then Stochastic) creates significant lag. Initial ~40 bars unreliable.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/stochrsi

### Stochastic RSI  `stochrsi`
*momentum · FinTA, bukosabino/ta* · aliases: StochRSI, Stochastic RSI

**What:** An indicator applying the Stochastic Oscillator formula to RSI values rather than price, creating an oscillator of an oscillator to identify overbought/oversold conditions of momentum.

**How / formula:** RSI = standard RSI calculation. StochRSI = (RSI - Lowest RSI over N periods) / (Highest RSI over N periods - Lowest RSI over N periods) × 100. Typical N = 14. Signal line = SMA(StochRSI, 3).

**Inputs:** close
**Outputs:** stochrsi_value, stochrsi_signal

**Parameters:**
- `rsi_period` (default 14, typical [10, 20]) — 14 is standard for RSI component.
- `stoch_period` (default 14, typical [10, 20]) — 14 is standard for stochastic RSI lookback. Defines high/low range of RSI.
- `signal_period` (default 3, typical [3, 9]) — 3 is standard. Creates signal line for crossover entries.

**Interpretation:** StochRSI > 80 indicates overbought (bearish, prepare to sell). StochRSI < 20 indicates oversold (bullish, prepare to buy). Crossover of StochRSI above/below signal line generates buy/sell signals. Values between 20-80 indicate normal momentum range.

**Look-ahead risk:** None. Double oscillator calculation based on historical RSI and stochastic application.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi

### TRIX  `trix`
*momentum · TA-Lib* · aliases: TRIX

**What:** Triple Exponential Moving Average momentum oscillator. Measures the percentage rate of change of a triple-smoothed EMA. Identifies trend changes with reduced noise.

**How / formula:** EMA1 = EMA of close (period n, default 15). EMA2 = EMA of EMA1 (period n). EMA3 = EMA of EMA2 (period n). TRIX = ((EMA3[today] - EMA3[yesterday]) / EMA3[yesterday]) × 100 × 1000. Triple smoothing removes short-term noise; momentum calculation captures trend acceleration/deceleration.

**Inputs:** close
**Outputs:** TRIX

**Parameters:**
- `timeperiod` (default 15, typical 12-20) — 15 is standard (Hutson's original default). Longer periods increase smoothing and reduce false signals.

**Interpretation:** TRIX > 0: upward momentum. TRIX < 0: downward momentum. TRIX crossing zero: momentum direction change (potential trend reversal). Rising TRIX magnitude indicates accelerating trend; falling magnitude indicates deceleration. Often used with signal line (usually 9-period SMA of TRIX).

**Look-ahead risk:** Unstable period: (timeperiod * 3) - 2 ≈ 43 bars for 15-period setting. Triple EMA creates substantial lag; initial 40+ bars unreliable. More stable than simple EMA but slower to respond.
- https://library.tradingtechnologies.com/trade/chrt-ti-triple-exponential-moving-average-oscillator.html
- https://trendspider.com/learning-center/trix-indicator-explained-enhance-your-trading-with-triple-exponential-averages/

### TRIX  `trix`
*momentum · FinTA, bukosabino/ta* · aliases: Triple Exponential Moving Average, Triple EMA

**What:** A momentum oscillator displaying the percentage rate of change of a triple exponentially smoothed moving average, designed to filter insignificant price movements and reduce false signals.

**How / formula:** Three EMAs are applied sequentially: EMA1 = EMA(close, period), EMA2 = EMA(EMA1, period), EMA3 = EMA(EMA2, period). TRIX = 10000 * (EMA3_current - EMA3_prev) / EMA3_prev. Result is the percent change of the triple-smoothed average.

**Inputs:** close
**Outputs:** trix_value, trix_signal

**Parameters:**
- `period` (default 15, typical [10, 25]) — 15 is standard default (some use 14 or 18). Higher timeframes produce fewer but more accurate signals; lower timeframes generate more false signals. Adjust for asset volatility.

**Interpretation:** TRIX oscillates around zero. Positive values signal upward momentum; negative values signal downward momentum. Crossovers of TRIX with its signal line (typically 9-period SMA of TRIX) generate buy/sell signals. Divergences identify potential reversals.

**Look-ahead risk:** Lag from triple smoothing. Signals arrive later than raw price action; use for trend confirmation rather than early entry.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://www.luxalgo.com/blog/trix-triple-exponential-moving-average-guide/

### True Strength Index  `tsi`
*momentum · pandas-ta* · aliases: TSI, Momentum

**What:** A double-smoothed momentum oscillator that applies two exponential moving averages to price changes to create a noise-filtered indicator for identifying trend direction and reversals.

**How / formula:** Calculates diff = close - close[drift]. Applies EMA(diff, slow) then EMA(result, fast) for numerator. Applies EMA(|diff|, slow) then EMA(result, fast) for denominator. TSI = 100 * numerator/denominator. Signal = EMA(TSI, signal_length).

**Inputs:** close
**Outputs:** TSI, TSI_Signal

**Parameters:**
- `fast` (default 13, typical 10-15) — Second EMA smoothing period; 13 is standard
- `slow` (default 25, typical 20-30) — First EMA smoothing period; 25 captures longer-term momentum
- `signal` (default 13, typical 7-15) — Signal line EMA period for crossover signals
- `scalar` (default 100, typical 1-100) — 100 scales output to -100 to +100 range

**Interpretation:** TSI > 0 = bullish momentum; < 0 = bearish. Crossing above signal line = buy; below = sell. Centerline crossovers confirm momentum transitions.

**Look-ahead risk:** No lookahead bias; double smoothing uses only past price data.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/momentum/tsi.html

### True Strength Index  `tsi`
*momentum · FinTA, bukosabino/ta* · aliases: TSI

**What:** A momentum oscillator applying double exponential smoothing to price momentum (change), normalized by double smoothed absolute momentum, producing a cleaner trend-following signal with reduced noise.

**How / formula:** PM = close - close_previous (price momentum). TSI = 100 × EMA(EMA(PM, long), short) / EMA(EMA(|PM|, long), short). Standard: long = 25, short = 13. Output ranges from +100 to -100, typically ±25.

**Inputs:** close
**Outputs:** tsi_value, tsi_signal

**Parameters:**
- `long_period` (default 25, typical [20, 30]) — First smoothing period, longer smoothing for trend definition.
- `short_period` (default 13, typical [10, 20]) — Second smoothing period, shorter smoothing for signal responsiveness.
- `signal_period` (default 7, typical [5, 10]) — Signal line SMA period for crossover entries.

**Interpretation:** TSI > 0 signals bullish momentum; TSI < 0 signals bearish. TSI crossing signal line generates buy/sell signals. Zero-line crossovers confirm momentum shifts. Divergences identify potential reversals. Double smoothing reduces false signals vs raw momentum indicators.

**Look-ahead risk:** Lag from double exponential smoothing. Signals arrive later than price action but with reduced noise.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index

### Ultimate Oscillator  `ultimate_oscillator`
*momentum · Larry Williams (1976)* · aliases: UO, Ultimate Oscillator (Larry Williams)

**What:** Multi-timeframe momentum oscillator using three weighted averages of buying pressure relative to true range

**How / formula:** Buying Pressure (BP) = Close - MIN(Low, Previous Close). True Range (TR) = MAX(High, Previous Close) - MIN(Low, Previous Close). Calc average BP/TR for 7, 14, 28 periods. UO = 100 × [(4×Avg7) + (2×Avg14) + Avg28] / 7. Range 0-100.

**Inputs:** high, low, close
**Outputs:** ultimate_oscillator

**Parameters:**
- `period1` (default 7, typical 5-10) — Short-term lookback; standard 7
- `period2` (default 14, typical 10-20) — Medium-term lookback; standard 14
- `period3` (default 28, typical 20-40) — Long-term lookback; standard 28

**Interpretation:** UO > 70 = overbought. UO < 30 = oversold. Divergences signal reversals. Developed by Larry Williams 1976. More stable than single-timeframe oscillators. Works well across different market conditions.

**Look-ahead risk:** None; uses only completed bar data
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/ultimate-oscillator
- https://www.tradingview.com/support/solutions/43000502328-know-sure-thing-kst/

### Ultimate Oscillator  `ultosc`
*momentum · TA-Lib* · aliases: ULTOSC

**What:** Multi-timeframe momentum oscillator combining three weighted periods (7, 14, 28 by default). Measures buying pressure across three timeframes to identify overbought/oversold conditions.

**How / formula:** BP (Buying Pressure) = Close - Min(Low, Prior Close). TR (True Range) = Max(High, Prior Close) - Min(Low, Prior Close). Calculate BP/TR average for three periods (7, 14, 28). ULTOSC = 100 × [(4 × Avg7) + (2 × Avg14) + Avg28] / 7. Weighting 4:2:1 emphasizes recent price action while maintaining longer-term perspective.

**Inputs:** high, low, close
**Outputs:** ULTOSC

**Parameters:**
- `timeperiod1` (default 7, typical 4-10) — Shortest timeframe, highest weight (4x). Captures short-term pressure.
- `timeperiod2` (default 14, typical 10-20) — Medium timeframe, medium weight (2x). Balanced perspective.
- `timeperiod3` (default 28, typical 20-50) — Longest timeframe, lowest weight (1x). Provides trend context.

**Interpretation:** ULTOSC > 70: overbought (potential reversal). ULTOSC < 30: oversold (potential bounce). Rising ULTOSC: strengthening upward pressure. Falling ULTOSC: strengthening downward pressure. Developed by Larry Williams; oscillates 0-100.

**Look-ahead risk:** Unstable period: timeperiod3 bars (28 default). Initial 28 bars unreliable. No repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator
- https://www.luxalgo.com/blog/ultimate-oscillator-combining-three-timeframes/

### Williams %R  `williams_r`
*momentum · Tulip Indicators, Larry Williams* · aliases: %R, Williams Percent Range, Larry Williams %R

**What:** Bounded oscillator (-100 to 0) measuring closing price position within high-low range, shows overbought/oversold conditions

**How / formula:** %R = [-(Highest High n - Close) / (Highest High n - Lowest Low n)] × 100. Inverted scale where -20 = overbought (near high), -80 = oversold (near low). Range always -100 to 0 (inverted from Stochastic).

**Inputs:** high, low, close
**Outputs:** williams_r

**Parameters:**
- `period` (default 14, typical 7-21) — Standard 14; shorter periods faster signals; longer smoother less false signals

**Interpretation:** %R > -20 = overbought; %R < -80 = oversold. Readings -50 to -50 = neutral. Divergences signal reversals. Trend confirmation: strong uptrend keeps %R -20 to -50; downtrend -50 to -80. Less effective in ranging markets.

**Look-ahead risk:** None; uses only high/low/close within window
- https://tulipindicators.org/willr
- https://www.babypips.com/learn/forex/williams-r
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/williams-r

### Williams %R  `willr`
*momentum · TA-Lib* · aliases: WILLR, Williams %R

**What:** Measures the level of closing price relative to the high-low range over n periods. Ranges -100 to 0 (note: negative scale, unlike Stochastic). Developed by Larry Williams.

**How / formula:** Williams %R = -100 × ((Highest High - Close) / (Highest High - Lowest Low)). Negative scale by design. Williams %R = 0 means close at highest high (strong uptrend). Williams %R = -100 means close at lowest low (strong downtrend). Oscillates between 0 and -100.

**Inputs:** high, low, close
**Outputs:** WILLR

**Parameters:**
- `timeperiod` (default 14, typical 5-20) — 14 is Larry Williams' standard. Shorter periods increase sensitivity; longer periods reduce whipsaws.

**Interpretation:** Williams %R > -20: overbought (potential reversal/pullback). Williams %R < -80: oversold (potential bounce). Rising Williams %R (moving toward 0): bullish momentum. Falling Williams %R (moving toward -100): bearish momentum. Inverse scale compared to Stochastic; similar interpretation logic.

**Look-ahead risk:** Unstable period: timeperiod bars. Initial lookback period unreliable. No repainting.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/williams-r

### Alpha#14: Return Decay × Volume Correlation  `wq_alpha_14`
*momentum · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 14, Alpha#14

**What:** Negated product of ranked 3-bar return reversals and open-volume correlation, detecting when recent weakness doesn't match volume confirmation.

**How / formula:** Formula: ((-1 * rank(delta(returns, 3))) * correlation(open, volume, 10)). Compute 3-bar return delta, rank cross-sectionally, negate. Compute 10-bar correlation(open, volume). Multiply the two: when returns reversed (high rank value → high negative alpha) AND volume correlates with open (positive correlation), signal strengthens; when returns reversed but volume uncorrelated, signal weakens.

**Inputs:** open, volume, returns
**Outputs:** alpha_factor

**Parameters:**
- `return_delta_period` (default 3, typical 1 to 7) — 3 captures mean-reversion windows.
- `correlation_period` (default 10, typical 5 to 20) — 10 spans 2 trading weeks.

**Interpretation:** Large negative alpha: returns reversed AND volume confirms (strong reversion signal). Small/positive: returns reversed but volume weak (lower conviction).

**Look-ahead risk:** None.
- https://arxiv.org/abs/1601.00991

### Alpha#2: Volume-Price Divergence Detector  `wq_alpha_2`
*momentum · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 2, Alpha#2

**What:** Negative correlation between volume changes and intraday returns (open-close), detecting breakdowns in typical volume-price confirmation patterns. Signals when volume and price diverge.

**How / formula:** Formula: -1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6). (1) Compute 2-period delta of log(volume), rank cross-sectionally. (2) Compute 1-period intraday return (close-open)/open, rank cross-sectionally. (3) Correlate ranked series over 6 periods. (4) Negate: high correlation (vol & price co-move) → negative alpha; low correlation (divergence) → positive alpha.

**Inputs:** close, open, volume
**Outputs:** alpha_factor_-1_to_1

**Parameters:**
- `volume_delta_period` (default 2, typical 1 to 5) — 2 captures intra-session volume shifts.
- `correlation_period` (default 6, typical 3 to 10) — 6 balances weekly (5-day) confirmation patterns.

**Interpretation:** Positive alpha: volume/price divergence (weak confirmation, reversion bias). Negative: strong volume confirmation (continuation bias). Often exploits false breakouts (high volume without price follow-through).

**Look-ahead risk:** None. Historical correlation only.
- https://arxiv.org/abs/1601.00991

### Alpha#7: Volume-Adjusted Momentum & Trend Strength  `wq_alpha_7`
*momentum · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 7, Alpha#7

**What:** Conditional momentum signal: if volume exceeds 20-day moving average, applies negative time-series rank of absolute 7-bar close changes (scaled by sign) to detect reversals; else neutral.

**How / formula:** Formula: ((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : -1). If volume > adv20: compute 7-bar close delta, take absolute value, rank it in 60-bar window (ts_rank), negate (flip direction), multiply by sign of delta (preserve direction). If volume <= adv20: return -1 (neutral/short bias). Exploits reversion after strong directional moves with volume.

**Inputs:** close, volume, adv20
**Outputs:** alpha_factor_-1_to_1

**Parameters:**
- `adv_period` (default 20, typical 5 to 30) — 20 is standard monthly volume baseline.
- `momentum_period` (default 7, typical 5 to 14) — 7 captures weekly momentum; 14 captures bi-weekly.
- `rank_period` (default 60, typical 30 to 90) — 60 spans roughly one trading quarter; longer smooths noise.

**Interpretation:** Positive: weak recent momentum (reversion candidate). Negative: strong sustained momentum (continuation). Volume filter adds conviction; low-volume moves ignored.

**Look-ahead risk:** None. Standard rolling windows.
- https://arxiv.org/abs/1601.00991

### Wave Trend Oscillator  `wto`
*momentum · FinTA* · aliases: WaveTrend, WT

**What:** A momentum oscillator that highlights overbought/oversold conditions by measuring typical price deviation from a smoothed moving average, normalized by exponentially smoothed mean absolute deviation.

**How / formula:** HLC3 = (High + Low + Close) / 3. ESA = EMA(HLC3, n1). D = EMA(|HLC3 - ESA|, n1). CI = (HLC3 - ESA) / (0.015 * D). WT1 = EMA(CI, n2). WT2 = SMA(WT1, signalPeriod). The 0.015 constant normalizes CI to typical -100 to +100 range.

**Inputs:** high, low, close
**Outputs:** wt1, wt2

**Parameters:**
- `channel_length` (default 10, typical [7, 14]) — 10 is standard. Shorter lengths increase sensitivity; longer lengths reduce noise. Common variants use 9 or 14.
- `average_length` (default 21, typical [14, 30]) — 21 is standard. Controls smoothing of CI into WT1. Longer periods reduce whipsaws.
- `signal_period` (default 4, typical [3, 9]) — 4 is standard. Creates WT2 signal line for crossover entries.

**Interpretation:** WT1 > WT2 signals uptrend; WT1 < WT2 signals downtrend. Crossovers are primary entry/exit signals. Extremes (WT1 > 60 or < -60) identify overbought/oversold. Divergences signal potential reversals.

**Look-ahead risk:** Minimal lag from double smoothing. WT1/WT2 crossovers subject to minor repainting in the final bar before close.
- https://github.com/peerchemist/finta
- https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/wave-trend-oscillator



## overlap  (9)

### ALMA (Arnaud Legoux Moving Average)  `alma`
*overlap · pandas-ta* · aliases: ALMA, Arnaud Legoux MA

**What:** A smoothing moving average that uses Gaussian distribution weighting to balance lag reduction and noise filtering, responding more quickly to recent prices while maintaining trend clarity.

**How / formula:** Calculates Gaussian weights: wtd[i] = e^(-1 * ((i - m)² / (2 * s²))) where m = distribution_offset * (length - 1) and s = length / sigma. Then ALMA = Σ(wtd[j] * close[i-j]) / Σ(wtd[j]). Higher distribution_offset shifts weights toward recent prices.

**Inputs:** close
**Outputs:** ALMA

**Parameters:**
- `length` (default 10, typical 5-20) — Window size; higher values smoother but laggier
- `sigma` (default 6, typical 4.0-10.0) — Controls curve shape; higher = smoother
- `distribution_offset` (default 0.85, typical 0.5-1.0) — 0.85 balances lag and smoothing; 1.0 most responsive, 0.5 smoothest

**Interpretation:** Use as trend line similar to EMA. Alerts when price crosses ALMA. Steepness indicates trend strength. Lower lag than EMA makes crossovers more timely.

**Look-ahead risk:** No lookahead bias; Gaussian weighting is symmetric within window but causal.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/overlap/alma.html

### FWMA (Fibonacci Weighted Moving Average)  `fwma`
*overlap · pandas-ta* · aliases: FWMA, Fibonacci MA, Fib Weighted MA

**What:** A weighted moving average that applies Fibonacci sequence numbers as weights to prices, creating an accelerating weighting pattern where more recent values receive greater emphasis.

**How / formula:** Uses Fibonacci sequence as multipliers: 1,1,2,3,5,8,13,21... Applied to rolling window of prices. More recent periods receive Fibonacci sequence weights. FWMA = SUM(Fib[i] * close[i]) / SUM(Fib[i]). Ascending order emphasizes recent prices.

**Inputs:** close
**Outputs:** FWMA

**Parameters:**
- `length` (default 10, typical 5-20) — Window size for Fibonacci sequence
- `asc` (default True, typical true|false) — True weights recent higher; False weights past higher

**Interpretation:** Use as trend line. Fibonacci weights create natural acceleration pattern. More responsive than SMA while maintaining smoothing. Useful for identifying momentum changes.

**Look-ahead risk:** No lookahead bias; Fibonacci weighting is deterministic and causal.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/overlap/fwma.html

### Hull Moving Average  `hma`
*overlap · pandas-ta* · aliases: HMA, Hull MA

**What:** A fast-responding moving average that combines WMAs of different periods to dramatically reduce lag while maintaining a smooth trend line.

**How / formula:** Calculates wmaf = WMA(close, int(length/2)), wmas = WMA(close, length). Then raw = 2*wmaf - wmas. Finally HMA = WMA(raw, int(sqrt(length))). The three-step process removes lag more effectively than traditional MAs.

**Inputs:** close
**Outputs:** HMA

**Parameters:**
- `length` (default 20, typical 9-50) — Base period; 9-period common for active trading, 20-30 for swing

**Interpretation:** Much faster than EMA with minimal lag. Use for responsive trend-following. Price crossing HMA generates strong signals. Sharp changes indicate momentum shifts.

**Look-ahead risk:** No lookahead bias; three-step WMA process is fully causal.
- https://tradingstrategy.ai/docs/api/technical-analysis/overlap/help/pandas_ta.overlap.hma.html

### HWMA (Holt-Winter Moving Average)  `hwma`
*overlap · pandas-ta* · aliases: HWMA, Holt-Winter MA, HW MA

**What:** An adaptive moving average based on Holt-Winters exponential smoothing that accounts for level, trend, and optionally seasonality to smooth data while capturing directional changes.

**How / formula:** Applies Holt-Winters exponential smoothing with separate smoothing parameters for level and trend components. Level[t] = α*Data[t] + (1-α)*(Level[t-1] + Trend[t-1]). Trend[t] = β*(Level[t] - Level[t-1]) + (1-β)*Trend[t-1]. Output = Level[t] + Trend[t].

**Inputs:** close
**Outputs:** HWMA

**Parameters:**
- `length` (default 20, typical 10-30) — Lookback period for initial level/trend calculation
- `alpha` (default 0.2, typical 0.1-0.4) — Level smoothing constant; higher = more responsive to changes
- `beta` (default 0.1, typical 0.05-0.2) — Trend smoothing constant; higher = faster trend following

**Interpretation:** Follows trend more accurately than simple MAs. Better for data with clear trends. Adjusts for price momentum changes. Use alpha/beta tuning for specific market conditions.

**Look-ahead risk:** No lookahead bias; uses only past data in exponential smoothing.
- https://github.com/twopirllc/pandas-ta

### PWMA (Pascal Weighted Moving Average)  `pwma`
*overlap · pandas-ta* · aliases: PWMA, Pascal MA, Pascal Weighted MA

**What:** A weighted moving average that uses Pascal's triangle numbers as weights, creating an exponential acceleration pattern where each recent bar receives increasingly larger weight.

**How / formula:** Uses Pascal's triangle row (1, n, n(n-1)/2, ...) as multipliers. For 10-period: 1,9,36,84,126,126,84,36,9,1 (row 9 of triangle). PWMA = SUM(Pascal[i] * close[i]) / SUM(Pascal[i]). Creates aggressive recent price weighting.

**Inputs:** close
**Outputs:** PWMA

**Parameters:**
- `length` (default 10, typical 5-20) — Window size; triangle size determines weight distribution

**Interpretation:** More responsive than WMA due to Pascal acceleration. Good for trend-following in trending markets. Smoother than raw price but faster than traditional MAs.

**Look-ahead risk:** No lookahead bias; Pascal weighting is deterministic and causal.
- https://github.com/twopirllc/pandas-ta

### SINWMA (Sine Weighted Moving Average)  `sinwma`
*overlap · pandas-ta* · aliases: SINWMA, Sine Weighted MA

**What:** A weighted moving average that applies sine wave weights to the period, creating a smooth weighting curve that emphasizes recent prices while providing gradual decay.

**How / formula:** Uses sine function to generate weights: weight[i] = sin((i / (length+1)) * π). Creates bell-curve-like distribution over the period. SINWMA = SUM(sin_weight[i] * close[i]) / SUM(sin_weight[i]).

**Inputs:** close
**Outputs:** SINWMA

**Parameters:**
- `length` (default 10, typical 5-20) — Window size; sine wave generates smooth natural weighting

**Interpretation:** Provides smooth weighting between SMA and WMA. Useful for reducing noise while maintaining trend responsiveness. Sine curve creates natural, non-arbitrary weight distribution.

**Look-ahead risk:** No lookahead bias; sine weighting is deterministic and causal.
- https://github.com/twopirllc/pandas-ta

### SWMA (Symmetric Weighted Moving Average)  `swma`
*overlap · pandas-ta* · aliases: SWMA, Symmetric Weighted MA

**What:** A moving average that applies symmetric weights around the center of the period, emphasizing the middle bars more than the edges, creating a balanced smoothing effect.

**How / formula:** Applies weights that are highest at the center of the lookback window and decrease symmetrically toward both edges. For a 10-period window: weights might be 1,2,3,4,5,5,4,3,2,1. Creates balanced smoothing without favoring recent or past bars.

**Inputs:** close
**Outputs:** SWMA

**Parameters:**
- `length` (default 20, typical 10-30) — Window size; must be even for true symmetry

**Interpretation:** Use as trend line for balanced smoothing. Less responsive than WMA but smoother than SMA. Good for identifying mid-period trend without recent price bias.

**Look-ahead risk:** Symmetric weighting creates slight lookahead bias—middle weighting means current bar includes look-forward; use with caution for real-time decisions.
- https://github.com/twopirllc/pandas-ta

### VIDYA (Variable Index Dynamic Average)  `vidya`
*overlap · pandas-ta* · aliases: VIDYA, Variable Index Dynamic Average, Chande VIDYA

**What:** An adaptive moving average developed by Tushar Chande that adjusts its smoothing factor based on market volatility using the Chande Momentum Oscillator, making it more responsive in volatile markets.

**How / formula:** Calculates CMO(length) = (UpSum - DnSum) / (UpSum + DnSum) where UpSum = sum of positive close changes, DnSum = sum of negative close changes. Then VIDYA[i] = Price[i] * F * ABS(CMO) + VIDYA[i-1] * (1 - F * ABS(CMO)) where F = 2/(Period+1).

**Inputs:** close
**Outputs:** VIDYA

**Parameters:**
- `length` (default 20, typical 10-30) — CMO calculation period; higher = less responsive to volatility
- `offset` (default 0, typical 0-5) — Periods to shift result

**Interpretation:** Use like EMA but responds faster to volatility. More adaptive in choppy markets. Price crossing VIDYA generates signals. Volatility-adjusted smoothing provides better trend following.

**Look-ahead risk:** No lookahead bias; CMO uses only past price changes.
- https://fxcodebase.com/wiki/index.php/Chande's_Variable_Index_Dynamic_Average_(VIDYA)

### ZLMA (Zero Lag Moving Average)  `zlma`
*overlap · pandas-ta* · aliases: ZLMA, Zero Lag MA, ZLEMA

**What:** A lag-reduced exponential moving average that de-lags price data before applying EMA, creating a faster-responding moving average with minimal lag while maintaining smoothing.

**How / formula:** Calculates lag = int((length-1)/2). De-lags price: EmaData = close + (close - close[lag]). Then ZLMA = EMA(EmaData, length). This compensates for EMA's inherent lag by adding the price difference between current and lag periods.

**Inputs:** close
**Outputs:** ZLMA

**Parameters:**
- `length` (default 20, typical 10-50) — EMA period; 9 for intraday, 20 for swing, 40-50 for positional

**Interpretation:** Use as trend line with minimal lag. Crossover signals are more timely than EMA. Higher responsiveness useful for active trading. Still contains some lag due to past price dependency.

**Look-ahead risk:** No lookahead bias despite name; uses only past price data and historical lag compensation.
- https://www.technicalindicators.net/indicators-technical-analysis/182-zlema-zero-lag-exponential-moving-average



## price-transform  (16)

### Average Price  `avgprice`
*price-transform · TA-Lib* · aliases: AVGPRICE, Avg Price

**What:** Simple averaged representation of price combining all four OHLC values equally

**How / formula:** Arithmetic mean of open, high, low, and close: AVGPRICE = (open + high + low + close) / 4

**Inputs:** open, high, low, close
**Outputs:** real

**Interpretation:** Single-line indicator averaging all price components. Provides a single reference price incorporating opening, peak, trough, and closing information. Less commonly used than typical price or weighted close.

**Look-ahead risk:** None. Purely current-bar calculation.
- https://ta-lib.github.io/ta-lib-python/func_groups/price_transform.html
- https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/price_transform.md

### Decay Linear  `decay_linear`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: ts_decay_linear, linear_decay, exponential_weight_linear

**What:** Linearly weighted decay function that applies decreasing weights to historical values, giving more importance to recent observations. Weights form a linear decay pattern from current to oldest in window.

**How / formula:** Formula: decay_linear(x, d) = weighted_average where weights are [d, d-1, d-2, ..., 1] / (d*(d+1)/2) for the last d periods. Most recent value gets weight d/(sum of weights), oldest gets weight 1/(sum of weights). Alternative formulation: weights linearly decrease from 1 (current) to 0 (d periods ago).

**Inputs:** close, open, high, low, volume, any_price_metric, correlation_output
**Outputs:** decay_weighted_metric

**Parameters:**
- `period` (default 5, typical 3 to 20) — Shorter windows (3-5) emphasize very recent data; medium (7-10) balance recent+history; longer (15-20) smooth noise. Alpha#58 uses decay_linear(..., 7.89) to smooth correlation.

**Interpretation:** Reduces recency bias vs. simple moving average while prioritizing latest bars. High value = strong recent confirmation; low value = weak or deteriorating signal. Commonly used with correlation to smooth alpha decay.

**Look-ahead risk:** None. Standard historical weighting; no future data included.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code

### Delta / Change  `delta`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: ts_delta, price_change, period_change

**What:** Simple difference operator that computes the change in a metric between current time and d periods ago. Captures momentum, reversals, and acceleration signals.

**How / formula:** Formula: delta(x, d) = x_t - x_(t-d). Measures absolute change (not percentage). Often logarithmically scaled for volume (delta(log(volume), 2)) to normalize large value ranges.

**Inputs:** close, open, high, low, volume, log(volume)
**Outputs:** change_in_absolute_units

**Parameters:**
- `period` (default 1, typical 1 to 30) — period=1 gives raw returns; period=5-7 captures short-term momentum; period=20-30 identifies intermediate reversals. Alpha#7 uses period=7 for close; Alpha#2 uses period=2 for log(volume).

**Interpretation:** Positive delta = increase (bullish for price, volume confirmation); negative = decrease (bearish). Magnitude indicates strength. Rank(delta(...)) normalizes across cross-section.

**Look-ahead risk:** None. Standard lagged difference; no forward bias.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code/blob/master/101Alpha_code_1.py

### Median Price  `medprice`
*price-transform · TA-Lib* · aliases: MEDPRICE, Med Price

**What:** Midpoint between daily high and low prices, representing the center of the trading range

**How / formula:** Simple average of high and low: MEDPRICE = (high + low) / 2. Despite the name, this calculates the mean, not a statistical median.

**Inputs:** high, low
**Outputs:** real

**Interpretation:** Single line representing the center of daily price range. Smooths price by removing open/close noise. Often used as a basis for moving averages or other indicators requiring a single price point.

**Look-ahead risk:** None. Current-bar calculation.
- https://ta-lib.github.io/ta-lib-python/func_groups/price_transform.html
- https://vectoralpha.dev/projects/ta/indicators/medprice/

### Midpoint over Period  `midpoint`
*price-transform · TA-Lib* · aliases: MIDPOINT, Mid Point

**What:** The average of the highest high and lowest low over a specified period. A simple price envelope that represents the midpoint of the price range.

**How / formula:** MIDPOINT = (Highest_High(period) + Lowest_Low(period)) / 2. Takes high and low prices over N bars and computes their midpoint.

**Inputs:** high, low
**Outputs:** midpoint

**Parameters:**
- `timeperiod` (default 14, typical 5-50) — 14 is standard; shorter (5-10) for faster response, longer (20-50) for trend

**Interpretation:** Acts as a dynamic support/resistance level. Price above midpoint = strength. Below midpoint = weakness. Can serve as mean-reversion target. Wider range = increased volatility.

**Look-ahead risk:** No lookahead risk; uses only high/low within the lookback period.
- https://www.tradingtechnologies.com/xtrader-help/x-study/technical-indicator-definitions/midpoint-midpnt/
- https://trendspider.com/learning-center/understanding-and-applying-the-midpoint-over-period-indicator-in-trading/
- https://ta-lib.org/functions/

### Midpoint Price over Period  `midprice`
*price-transform · TA-Lib* · aliases: MIDPRICE, Mid Price

**What:** The average of the highest high and lowest low over a specified period (same calculation as MIDPOINT but typically applied to high/low separately).

**How / formula:** MIDPRICE = (Highest_High(period) + Lowest_Low(period)) / 2. Identical to MIDPOINT; represents the price midpoint of the range.

**Inputs:** high, low
**Outputs:** midprice

**Parameters:**
- `timeperiod` (default 14, typical 5-50) — Same as MIDPOINT; adjust for desired sensitivity

**Interpretation:** Same as MIDPOINT. Acts as dynamic support/resistance and mean-reversion target.

**Look-ahead risk:** No lookahead risk.
- https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/mid-price
- https://ta-lib.org/functions/

### Rank (Cross-Sectional)  `rank`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: percentile_rank, cross_sectional_rank

**What:** Cross-sectional ranking function that converts a security's value to its percentile rank relative to all other securities in the universe at a given point in time, returning values from 0 (lowest) to 1 (highest).

**How / formula:** For each cross-section (snapshot in time), sorts all securities by a metric and assigns each a percentile rank. Formula: rank(x_i) = (count of x_j where x_j < x_i) / total_count. Normalizes values to [0, 1] range for portfolio weighting and diversification.

**Inputs:** close, open, high, low, volume, any_price_metric
**Outputs:** percentile_rank_0_to_1

**Parameters:**
- `lookback_period` (default cross-section only (no time dimension), typical N/A) — Rank operates only across the cross-section at each time step; no intra-security temporal parameter. Apply to time-series-ranked metrics for combined effect.

**Interpretation:** Values near 1 indicate top percentile security; near 0 indicate bottom percentile. Useful for identifying relative strength/weakness and portfolio construction. Often combined with delta or ts_rank for momentum/reversion signals.

**Look-ahead risk:** None if applied synchronously at each time point. No repainting risk.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code

### Time-Series Argmax  `ts_argmax`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: ts_arg_max, argmax_lookback, bars_since_max

**What:** Returns the index/position (in periods) of the maximum value within a rolling lookback window. Index 0 = current period has max, 1 = one period ago had max, etc. Identifies how recently the peak occurred.

**How / formula:** Formula: ts_argmax(x, d) = argmax(x_[t-d+1:t]) - returns integer 0 to d-1 indicating position of max value in the window. If current bar is highest in last d bars, returns 0. If d periods ago was highest, returns d-1.

**Inputs:** close, open, high, low, volume, stddev(...), any_metric
**Outputs:** index_0_to_period

**Parameters:**
- `period` (default 5, typical 3 to 20) — Shorter periods (3-5) capture near-term peaks; medium (10-20) identify intermediate highs. Alpha#1 uses ts_argmax(..., 5) on conditional stddev/close metric.

**Interpretation:** Value 0 = peak just occurred (potential reversal); high value = peak was stale (may presage momentum). Often combined with rank() to normalize across securities. If (ts_argmax < 1) signals recent breakout; if (ts_argmax > period-2) signals old peak.

**Look-ahead risk:** None. Purely historical index; no forward data.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code/blob/master/101Alpha_code_1.py

### Time-Series Rank  `ts_rank`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: rolling_percentile_rank, time_series_percentile

**What:** Rolling time-series ranking function that converts a security's historical value to its percentile rank within its own lookback window, returning values from 0 (lowest in period) to 1 (highest in period).

**How / formula:** For each time t, ranks the value at t relative to all values in the window [t-d, t] where d is the lookback period. Formula: ts_rank(x_t, d) = (count of x_s where s in [t-d,t] and x_s < x_t) / d. Identifies whether current metric is near historical highs or lows.

**Inputs:** close, open, high, low, volume, any_price_metric
**Outputs:** percentile_rank_0_to_1

**Parameters:**
- `period` (default 20, typical 5 to 252) — Shorter periods (5-20) capture short-term extremes; medium (20-60) detect intermediate momentum; longer (60-252) identify secular trends. 252 approximates one trading year.

**Interpretation:** ts_rank = 0.9+ indicates value near 90-day high (overbought extremes); 0.1 or below suggests near lows (oversold). Used to detect mean reversion or trend continuation based on timing within historical range.

**Look-ahead risk:** No forward-looking bias if implemented with current data only. Standard rolling window, no repainting.
- https://arxiv.org/abs/1601.00991
- https://github.com/jglazar/notes/blob/main/quant_interview/worldquant_seminar.md

### Typical Price  `typprice`
*price-transform · TA-Lib* · aliases: TYPPRICE, Typ Price

**What:** Average of high, low, and close prices, the most commonly used single price representation in technical analysis

**How / formula:** Arithmetic mean of high, low, and close: TYPPRICE = (high + low + close) / 3

**Inputs:** high, low, close
**Outputs:** real

**Interpretation:** Balanced representation of the trading day: incorporates the range (high/low) and emphasizes closing price equally. Foundation for many volume-weighted indicators (e.g., Money Flow Index). Widely used as single-line price baseline.

**Look-ahead risk:** None. Current-bar calculation.
- https://ta-lib.github.io/ta-lib-python/func_groups/price_transform.html
- https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/price_transform.md

### Weighted Close Price  `wclprice`
*price-transform · TA-Lib* · aliases: WCLPRICE, WCL Price, Weighted Close

**What:** Price representation emphasizing the closing price by assigning it double weight relative to the high and low

**How / formula:** Weighted average: WCLPRICE = (high + low + 2*close) / 4. The closing price receives double weight, reflecting its perceived importance in technical analysis.

**Inputs:** high, low, close
**Outputs:** real

**Interpretation:** Smoothed single price line biased toward close. Reduces noise from extreme intra-day moves while preserving closing emphasis. Often used in moving averages and band calculations when close price emphasis is desired.

**Look-ahead risk:** None. Current-bar calculation.
- https://ta-lib.github.io/ta-lib-python/func_groups/price_transform.html
- https://www.metastock.com/customer/resources/taaz/?p=124

### Alpha#1: Volatility + Extreme Value Detector  `wq_alpha_1`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 1, Alpha#1

**What:** Composite signal combining conditional volatility (stddev for negative returns) and price levels (close for non-negative returns), ranked by position of extremes in recent history.

**How / formula:** Formula: rank(ts_argmax(signed_power(((returns < 0) ? stddev(returns, 20) : close), 2.0), 5)) - 0.5. For each security: if d-period returns < 0 (down period), squares the 20-day stddev of returns; else squares the close price. Finds max over last 5 bars, ranks that position cross-sectionally, shifts by -0.5.

**Inputs:** close, returns, volume_implicit
**Outputs:** alpha_factor_-0.5_to_0.5

**Parameters:**
- `stddev_period` (default 20, typical 10 to 30) — 20 captures short-term volatility; longer periods smooth noise but lag spikes.
- `argmax_period` (default 5, typical 3 to 10) — 5 balances responsiveness to recent extremes vs. noise.

**Interpretation:** Positive values: recent extremes in volatility/price (typically bullish signal post-volatility spike). Negative: extremes were stale. Exploits tendency for reversals after volatility shocks.

**Look-ahead risk:** None. Uses only past/current data.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code

### Alpha#101: Simplest Formula (Intraday Gap Normalization)  `wq_alpha_101`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 101, Alpha#101

**What:** Normalized intraday price gap as ratio of intraday range. Simplest of the 101 alphas; captures opening gaps normalized by daily volatility.

**How / formula:** Formula: (close - open) / ((high - low) + 0.001). Computes intraday return (close - open) divided by intraday range (high - low). Small constant 0.001 prevents division by zero (used on gap-up days with no intraday range). Positive values: close above open (bullish); negative: close below open (bearish). Magnitude scaled by volatility.

**Inputs:** close, open, high, low
**Outputs:** alpha_factor_-1_to_1

**Parameters:**
- `epsilon` (default 0.001, typical 0.0001 to 0.01) — Prevents division by zero; standard constant in WorldQuant formulas.

**Interpretation:** Values near 1: large bullish gap (strong open-close). Values near 0: small intraday move or gap day. Negative: bearish close. Useful for mean reversion (big gaps tend to fill) or breakout confirmation.

**Look-ahead risk:** None. Uses only OHLC from same bar.
- https://arxiv.org/abs/1601.00991

### Alpha#58: Decay-Smoothed VWAP-Volume Correlation  `wq_alpha_58`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 58, Alpha#58

**What:** Time-series rank of linearly decayed sector-neutralized VWAP-volume correlation, isolating idiosyncratic price-volume relationships after removing industry effects.

**How / formula:** Formula: (-1 * ts_rank(decay_linear(correlation(IndNeutralize(vwap, IndClass.sector), volume, 3.92795), 7.89291), 5.50322)). (1) Neutralize VWAP by removing sector mean (IndNeutralize). (2) Correlate with volume over 3.93-bar window. (3) Apply linear decay over 7.89 periods. (4) Rank the decayed correlation in 5.5-bar ts_window. (5) Negate. Exploits sector-adjusted price-volume relationships.

**Inputs:** vwap, volume, sector_classification
**Outputs:** alpha_factor

**Parameters:**
- `correlation_period` (default 3.92795, typical 2 to 10) — Non-integer parameter from original research; likely optimized.
- `decay_period` (default 7.89291, typical 3 to 20) — Non-integer; smooths short-term noise.
- `ts_rank_period` (default 5.50322, typical 2 to 10) — Non-integer; balances recent vs historical extremes.

**Interpretation:** High ts_rank (negated → negative alpha): VWAP-volume correlation at highs (strong technical confirmation). Low ts_rank (negated → positive alpha): correlation at lows (price move unsupported by volume).

**Look-ahead risk:** None. Industry-neutral calculation uses only contemporaneous sector memberships.
- https://arxiv.org/abs/1601.00991

### Alpha#69: Ranked Decay + Correlation for Sector Adjustments  `wq_alpha_69`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 69, Alpha#69

**What:** Negated product of ranked time-series max of VWAP delta and ts_rank of price-average volume correlation, capturing sector-adjusted price-volume extremes.

**How / formula:** Formula: ((rank(ts_max(delta(IndNeutralize(vwap, IndClass.industry), 2.72412), 4.79344))^ts_rank(correlation(((close * 0.490655) + (vwap * (1 - 0.490655))), adv20, 4.92416), 9.0615)) * -1). (1) Neutralize VWAP by industry. (2) Compute 2.7-bar VWAP delta. (3) Find ts_max over 4.8 bars. (4) Rank cross-sectionally. (5) Create blended price (49% close + 51% vwap). (6) Correlate with adv20 over 4.9 bars. (7) ts_rank correlation in 9-bar window. (8) Raise ranked delta to power of ts_rank correlation. (9) Negate.

**Inputs:** close, vwap, volume, adv20, industry_classification
**Outputs:** alpha_factor

**Parameters:**
- `delta_period` (default 2.72412, typical 1 to 5) — Optimized non-integer parameter.
- `ts_max_period` (default 4.79344, typical 3 to 10) — Optimized; captures intra-week extremes.
- `correlation_period` (default 4.92416, typical 2 to 10) — Optimized; captures trading week confirmation.
- `ts_rank_period` (default 9.0615, typical 5 to 20) — Optimized; spans ~10 trading days.
- `close_weight` (default 0.490655, typical 0.3 to 0.7) — Optimized blending of close and VWAP.

**Interpretation:** Exponentiation amplifies when both delta rank and correlation ts_rank are high (strong directional + volume confirmation); dampens when either is low (weak signal conviction).

**Look-ahead risk:** None.
- https://arxiv.org/abs/1601.00991

### Alpha#98: Deep Nested Decay-Smoothed Correlation Rank  `wq_alpha_98`
*price-transform · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 98, Alpha#98

**What:** Ranked linear decay of VWAP-volume correlation over a custom period, exemplifying the formula complexity (6-level nesting) typical of WorldQuant's proprietary alpha generation.

**How / formula:** Formula: (rank(decay_linear(correlation(vwap, sum(adv5, 26.4719), 4.58418), 7.18088))). (1) Compute 5-bar average daily volume (adv5). (2) Sum adv5 over 26.47 periods (creates cumulative volume proxy). (3) Correlate VWAP with that sum over 4.58-bar window. (4) Apply linear decay over 7.18 periods. (5) Rank cross-sectionally. Demonstrates how multiple operators compose to exploit price-volume relationships.

**Inputs:** vwap, volume, adv5
**Outputs:** alpha_factor_0_to_1

**Parameters:**
- `adv_period` (default 5, typical 3 to 10) — 5-day average volume baseline.
- `sum_period` (default 26.4719, typical 10 to 60) — Optimized (~26-27 days = ~5-6 weeks).
- `correlation_period` (default 4.58418, typical 2 to 10) — Optimized; captures short-term confirmation.
- `decay_period` (default 7.18088, typical 3 to 15) — Optimized; smooths ~1 week of noise.

**Interpretation:** High rank: strong VWAP-volume relationship (price rises with accumulation). Low rank: weak relationship (price move unsupported by volume). Decay ensures recent confirmation weighted heavily.

**Look-ahead risk:** None.
- https://arxiv.org/abs/1601.00991
- https://medium.com/@DolphinDB_Inc/a-simpler-way-to-calculate-worldquant-101-alphas-c55dac54e9f7



## statistic  (11)

### Beta  `beta`
*statistic · TA-Lib* · aliases: BETA, Beta Coefficient

**What:** Measures the sensitivity of one price series relative to another, typically used to assess how a security moves with market benchmarks

**How / formula:** Calculates the linear regression beta coefficient between two series: β = Covariance(y, x) / Variance(x). Mathematically, β is the slope of the regression line y = α + β*x. Operates using ordinary least squares method over the specified timeperiod.

**Inputs:** high, low
**Outputs:** real

**Parameters:**
- `timeperiod` (default 5, typical 5-30) — Default 5 bars provides rapid sensitivity changes. Typical range 20-30 for market-to-stock beta, shorter periods for technical trading.

**Interpretation:** β = 1: moves exactly with benchmark. β > 1: more volatile than benchmark (amplified moves). β < 1: less volatile (dampened moves). β < 0: inverse relationship. In technical analysis, measures price correlation between two series.

**Look-ahead risk:** No forward-looking repainting. Purely historical correlation measured over the lookback window.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://www.wallstreetmojo.com/beta-coefficient-calculate/

### Correlation Coefficient  `correl`
*statistic · TA-Lib* · aliases: CORREL, Pearson Correlation, r

**What:** Pearson correlation coefficient measuring the linear relationship strength between two price series, ranging from -1 (perfect inverse) to +1 (perfect positive)

**How / formula:** Calculates Pearson's r: r = Covariance(x, y) / (StdDev(x) * StdDev(y)). Standardized correlation coefficient independent of scale. Measures linear association; values closer to ±1 indicate stronger relationships.

**Inputs:** high, low
**Outputs:** real

**Parameters:**
- `timeperiod` (default 30, typical 5-50) — Default 30 bars balances sensitivity and stability. Shorter (5-10) for reactive correlation, longer (40-50) for trend confirmation.

**Interpretation:** r > 0.7: strong positive correlation (series move together). r < -0.7: strong negative correlation (inverse moves). -0.3 to 0.3: weak/no correlation. Used to identify related securities or confirm technical relationships.

**Look-ahead risk:** None. Symmetric calculation over historical window.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://online.stat.psu.edu/stat200/book/export/html/244

### Correlation  `correlation`
*statistic · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: ts_correlation, rolling_correlation, pearson_correlation

**What:** Rolling Pearson correlation coefficient between two time series over a fixed lookback window. Measures linear relationship strength (ranges from -1 to +1) between two price/volume metrics.

**How / formula:** Formula: correlation(x, y, d) = covariance(x_[t-d+1:t], y_[t-d+1:t]) / (stddev(x) * stddev(y)). Computed on sliding window of d periods. Positive values indicate co-movement; negative indicate inverse movement.

**Inputs:** close, open, high, low, volume, vwap, adv, rank(...)
**Outputs:** correlation_coefficient_-1_to_1

**Parameters:**
- `period` (default 10, typical 3 to 60) — Shorter (3-10) capture intra-period relationships; medium (10-20) identify consistent pairs; longer (30-60) smooth noise. Alpha#2 uses period=6; Alpha#55 uses period=6 for volume correlation.

**Interpretation:** corr > 0.5: strong positive co-movement; corr < -0.5: strong negative (inverse) relationship; |corr| < 0.3: weak relationship. Often negated (-1 * correlation) to flip long/short positions based on momentum breakdown.

**Look-ahead risk:** None. Correlation computed from past/current data only. Standard rolling window.
- https://arxiv.org/abs/1601.00991
- https://github.com/yli188/WorldQuant_alpha101_code

### Hurst Exponent  `hurst_exponent`
*statistic · Harold Hurst (Hydrology); applied to markets by Mandelbrot* · aliases: Hurst coefficient, Fractal dimension, Market memory

**What:** Statistical measure of long-term memory and fractal nature of time series; identifies trending vs mean-reverting behavior

**How / formula:** Analyzes log-log plot of rescaled range (R/S) vs time lag. Hurst = slope of R/S line. H = 0.5 = random walk. H > 0.5 = trending (autocorrelated, momentum). H < 0.5 = mean-reverting (oscillatory). Typically calculated over windows; rolling Hurst shows regime shifts.

**Inputs:** close
**Outputs:** hurst_exponent

**Parameters:**
- `period` (default 100, typical 50-252) — Longer windows (100-252) more reliable; shorter (50) responsive to regime shifts. 252 = one year daily bars.

**Interpretation:** H > 0.6 = strong uptrend; use trend-following strategies. H < 0.4 = strong mean-reversion; use range-trading strategies. 0.4 < H < 0.6 = mixed/inefficient; hard to trade. Rolling H shows market regime changes. Complexity requires careful interpretation.

**Look-ahead risk:** None; statistical historical measure; recalculates with window
- https://www.vortexcapitalgroup.com/trading-insights/hurst-exponent
- https://www.scitepress.org/papers/2018/66670/66670.pdf
- https://www.mql5.com/en/articles/6834

### Linear Regression  `linearreg`
*statistic · TA-Lib* · aliases: LINEARREG, Linear Fit

**What:** Ordinary least squares regression line fitted to price data, providing the best-fit trend over the lookback period

**How / formula:** Fits a line y = α + β*x to the lookback window using OLS: minimizes sum of squared residuals. Returns the regression value at the last bar of the window (timeperiod - 1).

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 14, typical 10-50) — Default 14 balances responsiveness and stability. Shorter (5-10) for tactical trends, longer (20-50) for major trends.

**Interpretation:** Smooth regression line through data. Slope indicates trend direction/strength. Useful for denoising and identifying support/resistance at regression line. Compare to actual price: divergences signal potential reversals.

**Look-ahead risk:** No repainting. Evaluated at historical endpoint, not extrapolated forward (unlike TSF).
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://medium.com/trading-data-analysis/linear-regression-with-ta-lib-a367b7ed9265

### Linear Regression Angle  `linearreg_angle`
*statistic · TA-Lib* · aliases: LINEARREG_ANGLE, LinRegAngle

**What:** Angle (in degrees) of the fitted linear regression line, quantifying trend steepness and direction

**How / formula:** Calculates the slope of the OLS regression line, then converts to angle: angle = arctan(slope) * (180 / π). Angle in degrees ranging from -90° to +90°.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 14, typical 10-50) — Same as LINEARREG. Default 14 provides good balance.

**Interpretation:** Positive angles (0° to 90°): uptrend (steeper = stronger uptrend). Negative angles (-90° to 0°): downtrend (steeper = stronger downtrend). 0°: flat/neutral. Useful for quantifying trend aggressiveness and momentum.

**Look-ahead risk:** None. Angle is derived from historical regression.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://en.wikipedia.org/wiki/Simple_linear_regression

### Linear Regression Intercept  `linearreg_intercept`
*statistic · TA-Lib* · aliases: LINEARREG_INTERCEPT, LinRegIntercept

**What:** Y-intercept (α) of the fitted linear regression line, the regression value when bar index equals zero

**How / formula:** OLS intercept: α = mean(close) - β * mean(bar_index). Represents the regression line's position on the y-axis. Used in regression equation: y = α + β*x.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 14, typical 10-50) — Default 14.

**Interpretation:** Intercept is one component of the regression equation. Combined with slope (β), reconstructs the fitted line: price_at_bar_x = intercept + slope * x. Less directly interpretable than slope or angle.

**Look-ahead risk:** None.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html

### Linear Regression Slope  `linearreg_slope`
*statistic · TA-Lib* · aliases: LINEARREG_SLOPE, LinRegSlope

**What:** Slope (β coefficient) of the linear regression line, indicating the rate of price change per bar

**How / formula:** OLS slope coefficient: β = Cov(bar_number, close) / Var(bar_number). Represents change in close per unit bar. Positive slope = uptrend, negative slope = downtrend.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 14, typical 10-50) — Default 14. Shorter periods capture momentum changes faster.

**Interpretation:** Slope value is in price units per bar. Positive > strong uptrend, positive but small = weak uptrend. Negative values indicate downtrends. Slope acceleration/deceleration signals momentum changes.

**Look-ahead risk:** None.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html

### Standard Deviation  `stddev`
*statistic · TA-Lib* · aliases: STDDEV, Std Dev, Standard Deviation

**What:** Population standard deviation measuring price volatility over a lookback window, used in Bollinger Bands and other volatility-based indicators

**How / formula:** Calculates population standard deviation (not sample): STDDEV = sqrt(sum((close - mean)^2) / n). TA-Lib uses n (not n-1), producing population variance. The nbdev parameter multiplies the result.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 5, typical 5-20) — Default 5 for fast volatility. 10-20 for smoother volatility measures.
- `nbdev` (default 1, typical 0.5-3) — Multiplier for standard deviations. Use 1 for 1-sigma bands, 2 for 2-sigma (Bollinger Bands standard), 0.5 for tighter bands.

**Interpretation:** Single positive value. Higher values = greater volatility. Used to set band width in Bollinger Bands (mean ± nbdev*stddev). Rising STDDEV = expanding volatility, falling = contracting volatility.

**Look-ahead risk:** None. Current window calculation.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://github.com/TA-Lib/ta-lib-python/issues/69

### Time Series Forecast  `tsf`
*statistic · TA-Lib* · aliases: TSF, Time Series Forecast

**What:** Linear regression extrapolation forecasting the next-bar price by evaluating the regression equation one period forward

**How / formula:** Fits an OLS regression line over timeperiod bars, then extrapolates one bar ahead: TSF = α + β*(timeperiod). Unlike LINEARREG which returns the regression value at the last bar, TSF returns the predicted value at the next bar, incorporating momentum bias forward.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 14, typical 10-50) — Default 14. Shorter periods (5-10) for responsive forecasting, longer (20-30) for trend-based forecasting with less noise sensitivity.

**Interpretation:** Projected next-bar price based on current trend. When actual price > TSF, trend is strengthening. When actual price < TSF, trend is weakening. Useful for momentum-based entry signals.

**Look-ahead risk:** TSF inherently contains forward projection risk (extrapolation bias). Not truly predictive but rather a trend-biased smoothing.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html
- https://pyquantlab.medium.com/linear-regression-forecast-linearreg-time-series-forecast-tsf-riding-the-trendline-3be83a8160e7

### Variance  `var`
*statistic · TA-Lib* · aliases: VAR, Variance

**What:** Population variance (squared standard deviation) measuring squared price deviations from the mean, as basis for volatility and band calculations

**How / formula:** Calculates population variance (not sample): VAR = sum((close - mean)^2) / n. Equals STDDEV^2. The nbdev parameter multiplies the result.

**Inputs:** close
**Outputs:** real

**Parameters:**
- `timeperiod` (default 5, typical 5-20) — Default 5. Shorter periods for reactive volatility, longer for smoothed volatility.
- `nbdev` (default 1, typical 0.5-3) — Multiplier applied to variance output. Use 1 for standard variance, 2 for higher volatility thresholds.

**Interpretation:** Positive value, units are price^2. Larger variance = higher volatility. Less intuitive than standard deviation (which is in price units). Mathematical basis for many volatility-based calculations.

**Look-ahead risk:** None.
- https://ta-lib.github.io/ta-lib-python/func_groups/statistic_functions.html



## support-resistance  (8)

### Andrews Pitchfork  `andrews_pitchfork`
*support-resistance · Dr. Alan Andrews (technical analysis)* · aliases: Pitchfork, Andrews channel, Median line

**What:** Three-line channel overlay using three price points to identify median line and parallel support/resistance lines

**How / formula:** Select three points: pivot high, pivot low between highs, another pivot high. Median line drawn from first point to midpoint between second and third. Upper/lower lines drawn parallel to median. Creates channel showing trend equilibrium and price structure.

**Inputs:** high, low, close
**Outputs:** median_line, upper_line, lower_line

**Parameters:**
- `point1` (default user-selected, typical initial pivot high) — First reference point
- `point2` (default user-selected, typical intermediate pivot low) — Secondary point for midpoint
- `point3` (default user-selected, typical subsequent pivot high) — Third point for midpoint calculation

**Interpretation:** Median line = trend direction/balance. Price above median = strength. Price below = weakness. Upper/lower lines = dynamic resistance/support. Price respecting channel = trend healthy. Breakout through lines = momentum continuation. Used for swing targets and reversals.

**Look-ahead risk:** None; static lines from manually selected points
- https://www.tradingview.com/education/pitchfork/
- https://www.litefinance.org/blog/for-beginners/best-technical-indicators/andrew-pitckhfork/
- https://docs.trendoscope.io/auto-pitchfork-indicator/

### Donchian Channel  `donchian`
*support-resistance · FinTA, bukosabino/ta* · aliases: Donchian Channels, DC

**What:** A volatility band indicator using the highest high and lowest low over a lookback period as dynamic support/resistance, with an optional middle band for trend identification.

**How / formula:** Upper Band = Highest High over N periods. Lower Band = Lowest Low over N periods. Middle Band = (Upper Band + Lower Band) / 2. Bands recalculate each bar as the lookback window slides forward.

**Inputs:** high, low
**Outputs:** donchian_high, donchian_low, donchian_mid

**Parameters:**
- `period` (default 20, typical [10, 50]) — 20 is standard for intraday; 50+ for longer-term support/resistance. Shorter periods track recent volatility; longer periods capture broader ranges.

**Interpretation:** Price at upper band indicates potential overbought (breakout confirmation or reversal setup). Price at lower band indicates potential oversold. Breakouts above/below bands on volume signal trend continuations. Band width measures volatility (wide bands = high volatility; narrow = consolidation).

**Look-ahead risk:** None. Bands use only prior N periods' OHLC.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://en.wikipedia.org/wiki/Donchian_channel

### Fibonacci Extension  `fibonacci_extension`
*support-resistance · Modern technical analysis (Fibonacci sequence application)* · aliases: Fib extension, Fibonacci targets, Extension levels

**What:** Price targets beyond 100% retracement using Fibonacci ratios; projects breakout/continuation price objectives

**How / formula:** Identify swing low, breakout point (100% level). Measure trend distance. Apply Fibonacci ratios beyond 100%: 127.2%, 161.8%, 261.8% of initial swing. Extensions project where trend may reach. 161.8% = primary target (golden ratio).

**Inputs:** high, low
**Outputs:** level_100, level_127_2, level_161_8, level_261_8

**Parameters:**
- `trend_distance` (default None, typical swing measure or breakout retracement) — Measure from swing start to breakout/retracement end

**Interpretation:** 127.2% = first extension target. 161.8% = primary objective (golden ratio). 261.8% = aggressive target. Price reaching extensions = natural resistance. Confluence with other levels = stronger targets. Entry at retracement, target at extension.

**Look-ahead risk:** None; static projections based on past swing measure
- https://www.cmegroup.com/education/courses/technical-analysis/fibonacci-retracements-and-extensions
- https://naga.com/en/academy/fibonacci-trading
- https://www.newtrading.io/fibonacci-trading/

### Fibonacci Retracement  `fibonacci_retracement`
*support-resistance · Fibonacci sequence (Leonardo Fibonacci, 1200s; trading application modern)* · aliases: Fib retracement, Fibonacci levels, Golden ratio support/resistance

**What:** Support/resistance levels based on Fibonacci ratios applied to recent swing; identifies pullback stopping points

**How / formula:** Identify swing high and low. Calculate distance = High - Low. Apply Fibonacci ratios: 23.6%, 38.2%, 50%, 61.8%, 78.6% of distance to low. Retracement levels = Low + (distance × ratio). Price often bounces at these mathematically-derived levels.

**Inputs:** high, low
**Outputs:** level_0, level_23_6, level_38_2, level_50, level_61_8, level_100

**Parameters:**
- `high` (default None, typical user-selected swing high) — Requires manual swing point selection or automated swing detection
- `low` (default None, typical user-selected swing low) — Requires manual swing point selection

**Interpretation:** 61.8% level = strongest reversal point (golden ratio). 38.2% = first support. 50% = psychological level. Price bouncing at levels = support/resistance. Breaking through = momentum continuation. 78.6% reversal = deep pullback but often strong resumption.

**Look-ahead risk:** None; static levels once drawn from confirmed swings
- https://www.britannica.com/money/fibonacci-trading-strategies
- https://www.oanda.com/us-en/trade-tap-blog/analysis/technical/uses-for-fibonacci/
- https://www.newtrading.io/fibonacci-trading/

### Fractals (Bill Williams)  `fractals`
*support-resistance · FinTA* · aliases: Williams Fractal, Fractal High/Low

**What:** A five-bar reversal pattern indicator where the middle bar has the highest high (up fractal) or lowest low (down fractal) of the group, used to identify support/resistance points and potential reversals.

**How / formula:** Up Fractal: Middle bar's high > both adjacent bars' highs on left and right. Down Fractal: Middle bar's low < both adjacent bars' lows on left and right. Detected across a 5-bar window. Fractal value plotted at the middle bar's high/low.

**Inputs:** high, low
**Outputs:** fractal_high, fractal_low

**Parameters:**
- `period` (default 5, typical [5, 5]) — Fixed at 5 bars per Bill Williams definition. No standard variation.

**Interpretation:** Up fractals mark resistance levels; down fractals mark support. Breakouts above/below fractals signal potential trades. Multiple fractals form support/resistance clusters. Use with Alligator indicator to filter trades (avoid entry if fractal inside Alligator teeth).

**Look-ahead risk:** 2-bar lag: fractal confirmed only after 2 bars complete on either side. Historical fractals do not repaint.
- https://github.com/peerchemist/finta
- https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals

### Gann Angles  `gann_angles`
*support-resistance · WD Gann (1900s, "Gann Theory")* · aliases: Gann fan, Gann lines, Price-time angles

**What:** Geometric trend lines based on price-time balance; 1×1 represents 45° angle (one unit price per unit time)

**How / formula:** Draw from significant pivot point. 1×1 angle = 45° = 1 price unit per 1 time unit. 1×2 = steep (1 price per 2 time). 2×1 = shallow (2 price per 1 time). Series of angles from high/low point project support/resistance. Based on WD Gann theory of price-time equilibrium.

**Inputs:** high, low, close
**Outputs:** gann_1x1, gann_1x2, gann_2x1

**Parameters:**
- `starting_point` (default user-selected, typical significant high or low) — Requires manual swing selection or automated detection

**Interpretation:** Price respecting angles = trend active. Breaking above = bullish breakout. Price holding below = resistance. Angles act as dynamic support/resistance. 1×1 = most important (balance); deviations temporary. Multiple angles create Gann Fan.

**Look-ahead risk:** None; static lines from past swing point
- https://www.morpher.com/blog/gann-theory
- https://capital.com/en-int/learn/technical-analysis/gann-indicator
- https://www.ifmcinstitute.com/what-is-gann-theory/

### Pivot Points (Daily/Weekly)  `pivot_points`
*support-resistance · FinTA* · aliases: PP, Daily Pivots, Weekly Pivots

**What:** Support and resistance levels calculated from the previous period's OHLC, identifying key price levels for mean reversion and breakout trading. Includes central pivot and multiple support/resistance tiers.

**How / formula:** Pivot Point (PP) = (High + Low + Close) / 3. Resistance 1 (R1) = 2 × PP - Low. Support 1 (S1) = 2 × PP - High. R2 = PP + (High - Low). S2 = PP - (High - Low). R3 = High + 2 × (PP - Low). S3 = Low - 2 × (High - PP). For weekly, use previous week's OHLC; for daily, use previous day's OHLC.

**Inputs:** high, low, close
**Outputs:** pivot_point, resistance_1, resistance_2, resistance_3, support_1, support_2, support_3

**Parameters:**
- `anchor` (default day, typical ['day', 'week', 'month']) — Daily (D1) for intraday/swing trading; weekly (W1) for longer-term trend pivots. Monthly (M1) for structural support/resistance.

**Interpretation:** Price bouncing off S1/R1 indicates normal consolidation. Breaks through R2/S2 signal strong breakout trades. Multiple reversals at PP suggest trend consolidation. Wider zones (larger High-Low ranges) create stronger support/resistance.

**Look-ahead risk:** None. Uses only prior period's OHLC.
- https://github.com/peerchemist/finta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/pivot-points

### Pivot Points Classical  `pivot_points_classic`
*support-resistance · Classic technical analysis* · aliases: Floor Pivot Points, Classic Pivots, Standard Pivot Points

**What:** Support/resistance levels derived from previous day's OHLC using simple formulas; widely used for intraday trading levels

**How / formula:** Pivot Point (PP) = (H + L + C) / 3. R1 = (2 × PP) - L. R2 = PP + (H - L). S1 = (2 × PP) - H. S2 = PP - (H - L). Additional levels: R3 = R1 + (H - L), S3 = S1 - (H - L). Uses previous period's high, low, close.

**Inputs:** high, low, close
**Outputs:** pivot, r1, r2, r3, s1, s2, s3

**Interpretation:** PP = equilibrium price; opens above = bullish; below = bearish. R1/S1 = first support/resistance. R2/S2 = stronger levels. Breakthrough R2/S2 = strong momentum. Multiple touches = zone strength. Used for intraday entries, exits, stop-loss placement.

**Look-ahead risk:** None; uses only previous period's data; calculation complete at period open
- https://www.babypips.com/learn/forex/other-pivot-point-calculation-methods
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/pivot-points
- https://stockstotrade.com/which-pivot-points-best-intraday/



## trend  (42)

### Average Directional Index  `adx`
*trend · TA-Lib* · aliases: ADX

**What:** Measures the strength of a trend without regard to direction. Developed by Welles Wilder, it combines directional movement indicators to assess whether a trend is strong, weak, or non-existent.

**How / formula:** Calculates Plus Directional Movement (+DM), Minus Directional Movement (-DM), and True Range (TR). Smooth these using Wilder's smoothing over 14 periods to derive +DI and -DI (divide by TR, multiply by 100). Calculate DX = (|+DI - -DI| / (+DI + -DI)) * 100. First ADX is 14-period average of DX; subsequent values: ((Prior ADX × 13) + Current DX) / 14. Requires approximately 150 periods of data for accurate readings.

**Inputs:** high, low, close
**Outputs:** ADX

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is Wilder's standard, balance between sensitivity and reliability. Shorter periods increase sensitivity to trend changes; longer periods smooth noise.

**Interpretation:** ADX > 25 indicates strong trend; 20-25 gray zone; < 20 suggests no trend. Does not indicate direction, only strength. Rising ADX indicates strengthening trend; falling ADX indicates weakening trend.

**Look-ahead risk:** Unstable period: approximately 150 bars required for convergence. Initial values unreliable; discard first 30-150 bars in backtests.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx
- https://ta-lib.github.io/ta-lib-python/func_groups/momentum_indicators.html

### Average Directional Index  `adx`
*trend · Tulip Indicators, J. Welles Wilder Jr. (1978)* · aliases: ADX, Average Directional Index, DMI (with directional indicators)

**What:** Measures trend strength (0-100) regardless of direction; includes +DI and -DI directional indicators

**How / formula:** +DM = current high - previous high (if positive). -DM = previous low - current low (if positive). TR = true range. DI+ = 100 × (smoothed +DM / smoothed TR). DI- similarly calculated. DX = 100 × |DI+ - DI-| / (DI+ + DI-). ADX = smoothed DX using Wilder smoothing over 14 periods.

**Inputs:** high, low, close
**Outputs:** adx, pdi, ndi

**Parameters:**
- `period` (default 14, typical 10-21) — Standard 14; note Wilder smoothing requires ~150 bars for true values

**Interpretation:** ADX > 25 = strong trend (either direction). ADX < 20 = weak/no trend. Rising ADX = strengthening trend; falling ADX = weakening. Use +DI vs -DI to determine direction. ADX useful for position sizing and strategy selection.

**Look-ahead risk:** Requires 150+ periods for accurate values due to Wilder smoothing; recalculates each bar
- https://tulipindicators.org/adx
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/adx

### Average Directional Movement Rating  `adxr`
*trend · TA-Lib* · aliases: ADXR

**What:** A smoothed version of ADX that averages the current ADX value with the ADX value from n periods ago. Provides a lagged perspective on trend strength.

**How / formula:** Calculates ADX, then averages the current ADX with the ADX value from (timeperiod) bars ago. Formula: ADXR = (ADX[today] + ADX[today - n]) / 2. Inherits all ADX calculation complexities with added smoothing.

**Inputs:** high, low, close
**Outputs:** ADXR

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — Same as ADX; 14-period lag creates additional smoothing, reducing whipsaw signals.

**Interpretation:** Same thresholds as ADX (>25 strong, <20 weak) but more conservative and slower to react. Useful for confirming trend strength changes rather than capturing turning points.

**Look-ahead risk:** Unstable period: 2*timeperiod + ~130 bars for true convergence. Extremely lagged indicator; unsuitable for short-term entries.
- https://ta-lib.github.io/ta-lib-python/func_groups/momentum_indicators.html

### AMAT (Archer Moving Averages Trends)  `amat`
*trend · pandas-ta* · aliases: AMAT, Archer Moving Averages

**What:** A trend confirmation indicator that compares fast and slow moving averages with lookback period to identify trend initiation, continuation, and reversal signals.

**How / formula:** Calculates fast_ma = MA(close, fast, mamode) and slow_ma = MA(close, slow, mamode). Then applies long_run() and short_run() functions with lookback period to compare the two MAs. Returns boolean signals indicating whether fast MA is above/below slow MA over the lookback window.

**Inputs:** close
**Outputs:** AMAT_LR, AMAT_SR

**Parameters:**
- `fast` (default 8, typical 5-12) — Short-term MA period; 8 is standard
- `slow` (default 21, typical 15-30) — Long-term MA period; 21 is standard
- `lookback` (default 2, typical 1-5) — Periods to confirm trend continuation
- `mamode` (default ema, typical ema|sma|others) — EMA default; adjust for different MA responsiveness

**Interpretation:** LR (long-run) = 1 when uptrend confirmed over lookback; SR (short-run) = 1 when downtrend confirmed. Use for trend confirmation alongside price action.

**Look-ahead risk:** No lookahead bias; uses only past MA values within lookback window.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/trend/amat.html

### Aroon  `aroon`
*trend · TA-Lib* · aliases: AROON

**What:** Measures the number of periods since the highest high and lowest low within a specified lookback window. Identifies trend direction and strength through timing of extremes.

**How / formula:** Aroon Up = ((n - periods_since_highest_high) / n) × 100. Aroon Down = ((n - periods_since_lowest_low) / n) × 100. Both range 0-100; when Aroon Up > Aroon Down, uptrend is evident; when Aroon Down > Aroon Up, downtrend is evident. Values reflect how recent the n-period highs and lows occurred.

**Inputs:** high, low
**Outputs:** aroonup, aroondown

**Parameters:**
- `timeperiod` (default 14, typical 5-28) — 14 is standard. Shorter periods increase sensitivity to trend changes; longer periods identify major trends only.

**Interpretation:** Aroon Up at 100 = highest high today (strong uptrend). Aroon Down at 100 = lowest low today (strong downtrend). Crossovers signal trend changes. Readings between 30-70 indicate neutral/consolidation periods.

**Look-ahead risk:** No unstable period; calculated from recent extremes only. No repainting risk; purely lookback-based.
- https://primexbt.com/for-traders/aroon-indicator/
- https://www.excelpricefeed.com/userguide/technical-analysis/aroon

### Aroon Indicator  `aroon`
*trend · FinTA, bukosabino/ta* · aliases: Aroon Up/Down, AROON

**What:** A trend-following indicator measuring how many periods have passed since the highest high or lowest low, generating signals from crossovers and extreme levels (0-100).

**How / formula:** Aroon Up = ((period - periods_since_high) / period) × 100. Aroon Down = ((period - periods_since_low) / period) × 100. Both oscillate between 0 and 100. Aroon Oscillator = Aroon Up - Aroon Down (optional variant).

**Inputs:** high, low
**Outputs:** aroon_up, aroon_down

**Parameters:**
- `period` (default 14, typical [7, 30]) — 14 is standard. Shorter periods increase sensitivity; longer periods reduce false signals.

**Interpretation:** Aroon Up > 70 indicates strong uptrend. Aroon Down > 70 indicates strong downtrend. Crossover (Aroon Up crossing above/below Aroon Down) generates trend-change signals. Both near 50 indicates consolidation/weak trend. Aroon Up > Aroon Down confirms uptrend.

**Look-ahead risk:** None. Counts bars since recent extremes using only prior data.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon

### Aroon Indicator  `aroon`
*trend · Tushar Chande* · aliases: Aroon Up/Down, Aroon oscillator

**What:** Pair of oscillators measuring time since highest high/lowest low, identifies trend initiation, direction, and consolidation

**How / formula:** Aroon Up = [(period - periods since highest high) / period] × 100. Aroon Down = [(period - periods since lowest low) / period] × 100. Both range 0-100. Measures time relative to price rather than price relative to time.

**Inputs:** high, low
**Outputs:** aroon_up, aroon_down

**Parameters:**
- `period` (default 25, typical 14-28) — Standard 25; lower (14) more sensitive; higher (28) smoother

**Interpretation:** Aroon Up > 70 sustained = strong uptrend. Aroon Down > 70 sustained = strong downtrend. Parallel lines = consolidation/ranging. Up crossing above Down = bullish; Down crossing above Up = bearish. Diverging lines = trend breakdown.

**Look-ahead risk:** None; counts periods since extreme, backward-looking
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/aroon-indicator
- https://commodity.com/technical-analysis/aroon/

### CKSP (Chande Kroll Stop)  `cksp`
*trend · pandas-ta* · aliases: CKSP, Chande Kroll Stop, Kroll Stop

**What:** A trend-following indicator that calculates dynamic stop-loss levels based on Average True Range, helping traders identify trend direction and optimal exit points.

**How / formula:** LS0 = highest(high, p) - x * ATR(p); LS = highest(LS0, q). SS0 = lowest(low, p) + x * ATR(p); SS = lowest(SS0, q). Long stop trails below price; short stop trails above. TradingView mode uses Wilder's MA; book mode uses SMA with different defaults.

**Inputs:** high, low, close
**Outputs:** CKSPl, CKSPs

**Parameters:**
- `p` (default 10, typical 8-14) — ATR period and initial stop lookback
- `x` (default 3, typical 1.0-3.0) — ATR multiplier; 3.0 standard in book mode, 1.0 in TV mode
- `q` (default 20, typical 9-20) — Second stop smoothing period
- `tvmode` (default True, typical true|false) — True uses TradingView defaults; False uses original book

**Interpretation:** CKSPl = long stop above price in downtrend; CKSPs = short stop below price in uptrend. Trend reversal when price crosses stops. Use as trailing stop-loss levels.

**Look-ahead risk:** Uses historical highs/lows and ATR; no lookahead bias.
- https://tradingstrategy.ai/docs/_modules/pandas_ta/trend/cksp.html

### Double Exponential Moving Average  `dema`
*trend · TA-Lib* · aliases: DEMA, Double EMA

**What:** A faster-responding moving average that reduces lag by combining a single EMA with a double-smoothed EMA. Designed by Patrick Mulloy (1994) to provide quicker trend signal identification.

**How / formula:** DEMA = (2 * EMA(close, period)) - EMA(EMA(close, period), period). The formula takes the lag difference between EMA1 and EMA2, subtracting that lag from the original EMA to accelerate response to price changes.

**Inputs:** close
**Outputs:** dema

**Parameters:**
- `timeperiod` (default 30, typical 5-200) — Shorter periods (5-10) for fast trades, longer (20-50) for swing/position trading

**Interpretation:** Price above DEMA = uptrend. Price below DEMA = downtrend. DEMA crossover with price = early trend confirmation. More responsive than SMA, less lag than single EMA.

**Look-ahead risk:** No lookahead risk; calculated from past data. May repaint on incomplete bars if used intraday (as EMA recalculates).
- https://www.awesomefintech.com/term/double-exponential-moving-average/
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema
- https://ta-lib.github.io/ta-lib-python/

### Directional Index  `dx`
*trend · TA-Lib* · aliases: DX

**What:** Measures the directional strength of price movement using +DI and -DI components. Range 0-100; higher values indicate stronger directional trend. Foundation for ADX calculation.

**How / formula:** First calculate +DI and -DI using Wilder's smoothing of directional movements. DX = (|+DI - -DI| / (+DI + -DI)) × 100. DX itself is unsmoothed; ADX is the moving average of DX. Single DX values fluctuate more than ADX, but still reflect directional pressure strength.

**Inputs:** high, low
**Outputs:** DX

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is standard. Shorter periods increase DX oscillation; longer periods reduce noise.

**Interpretation:** DX > 25-30: strong directional trend (up or down). DX < 20: weak/no directional trend. DX alone does not indicate direction, only trend strength. Rising DX indicates increasing directional strength; falling DX indicates decreasing trend strength.

**Look-ahead risk:** Unstable period: approximately 150 bars for Wilder's smoothing convergence, similar to ADX. Initial 30-150 bars unreliable.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx
- https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/admiw

### Exponential Moving Average  `ema`
*trend · TA-Lib* · aliases: EMA, Exponential MA

**What:** A weighted moving average that gives exponentially more weight to recent prices, reducing lag compared to SMA. Responsive to trend changes while smoothing noise.

**How / formula:** EMA(today) = alpha * close + (1 - alpha) * EMA(yesterday), where alpha = 2 / (period + 1). Alternatively: EMA = (close - EMA_prev) * alpha + EMA_prev. Alpha determines the decay weight; higher alpha = more responsive.

**Inputs:** close
**Outputs:** ema

**Parameters:**
- `timeperiod` (default 12, typical 5-200) — 12/26 common for fast/slow pairs; 50/200 for longer-term trends; 5-10 for intraday

**Interpretation:** Price above EMA = uptrend. Price below EMA = downtrend. EMA crossover = trend change signal. Steeper slope = stronger trend. Multiple EMAs (12/26/50) used for momentum analysis.

**Look-ahead risk:** No lookahead risk in closed-candle EMA. On incomplete candles, EMA repaints as new prices come in; this is expected behavior.
- https://www.ifcmarkets.com/en/ntx-indicators/exponential-moving-average
- https://forextester.com/blog/exponential-moving-average/
- https://ta-lib.github.io/ta-lib-python/

### Exponential Moving Average  `ema`
*trend · Tulip Indicators, standard technical analysis* · aliases: EMA, Exponential average, Wilder MA

**What:** Weighted moving average giving more weight to recent prices, calculated recursively with smoothing factor

**How / formula:** Multiplier = 2 / (period + 1). EMA = (Current Price × Multiplier) + (Previous EMA × (1 - Multiplier)). First EMA typically SMA of first n periods. Smoothing factor decays older data exponentially while maintaining responsiveness.

**Inputs:** close
**Outputs:** ema

**Parameters:**
- `period` (default 12, typical 5-200) — Short-term: 9-12; medium: 21-50; long-term: 50-200. Combined usage common (12/26 for MACD, 50/200 crossovers)

**Interpretation:** Price above EMA = uptrend; below = downtrend. Steeper EMA slope = stronger trend. EMA crossovers signal momentum shifts. Multiple EMAs (9/21/55) create dynamic support/resistance. More responsive than SMA to recent price action.

**Look-ahead risk:** None; backward-looking recursive calculation
- https://tulipindicators.org/ema
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/ema
- https://www.investopedia.com/terms/e/ema.asp

### Hilbert Transform - Instantaneous Trendline  `ht_trendline`
*trend · TA-Lib* · aliases: HT_TRENDLINE, HTTrendLine, Hilbert Trendline

**What:** A trendline computed using Hilbert Transform (a signal processing technique) that removes the dominant cycle from price, leaving a 5-period trendline. Developed by John Ehlers.

**How / formula:** Process: compute Hilbert Transform and detrend price; calculate InPhase and Quadrature components; measure dominant cycle period via ArcTangent phase calculation; compute differential phase until 360 degrees is reached; instantaneous trendline = average of prices over the measured dominant cycle period, rounded and adjusted.

**Inputs:** close
**Outputs:** trendline

**Interpretation:** Trendline acts as support/resistance and trend direction. Price above trendline = uptrend. Price below trendline = downtrend. Smooth trendline indicates clean trend; oscillating trendline indicates choppy market.

**Look-ahead risk:** Uses signal processing that may have slight forward-looking characteristics. John Ehlers' methods are optimized for matching cycles; ensure backtests use proper lookback to avoid overfitting.
- https://ta-lib.github.io/ta-doc/indicator/HT_TRENDLINE.htm
- https://dotnet.stockindicators.dev/indicators/HtTrendline/
- https://www.mesasoftware.com/papers/MAMA.pdf

### Ichimoku Cloud  `ichimoku`
*trend · FinTA, bukosabino/ta* · aliases: Ichimoku Kinky Hyo, Cloud

**What:** A comprehensive trend/support-resistance system consisting of five components (Tenkan-Sen, Kijun-Sen, Senkou Span A, Senkou Span B, Chikou Span) that together form a cloud structure indicating trend direction and dynamic support/resistance.

**How / formula:** Tenkan-Sen = (9-period high + 9-period low) / 2. Kijun-Sen = (26-period high + 26-period low) / 2. Senkou Span A = (Tenkan-Sen + Kijun-Sen) / 2, plotted 26 bars forward. Senkou Span B = (52-period high + 52-period low) / 2, plotted 26 bars forward. Chikou Span = current close plotted 26 bars backward. Cloud = area between Senkou A and B.

**Inputs:** high, low, close
**Outputs:** tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

**Parameters:**
- `tenkan_period` (default 9, typical [9, 9]) — Fixed at 9 per standard; conversion line for fast momentum.
- `kijun_period` (default 26, typical [26, 26]) — Fixed at 26 per standard; base line for medium trend.
- `senkou_b_period` (default 52, typical [52, 52]) — Fixed at 52 per standard; far-range support/resistance.
- `senkou_ahead` (default 26, typical [26, 26]) — Fixed at 26 bars forward for cloud projection.
- `chikou_shift` (default 26, typical [26, 26]) — Fixed at 26 bars backward for lagging span.

**Interpretation:** Tenkan above Kijun signals uptrend momentum. Price above cloud indicates strong uptrend (cloud is support). Price below cloud indicates downtrend (cloud is resistance). Chikou above price confirms trend strength. Cloud thickness indicates support/resistance strength.

**Look-ahead risk:** 26-bar forward projection: Senkou spans repaint as they shift forward. Chikou lagging span plots historical close, not forward-looking. Use for confirmation only, not early entry.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://lightningchart.com/blog/ichimoku-cloud/

### Ichimoku Cloud  `ichimoku`
*trend · Goichi Hosoda (Japanese charting pioneer)* · aliases: Ichimoku Kinko Hyo, Ichimoku Cloud, Ichimoku indicator

**What:** Japanese indicator showing support/resistance, trend direction, and momentum using five lines and cloud (kumo) overlay

**How / formula:** Tenkan-Sen (conversion) = (9-period high + low) / 2. Kijun-Sen (base) = (26-period high + low) / 2. Senkou Span A = (Tenkan + Kijun) / 2, plotted 26 bars forward. Senkou Span B = (52-period high + low) / 2, plotted 26 bars forward. Chikou Span = close plotted 26 bars back. Cloud (kumo) = area between Spans A and B.

**Inputs:** high, low, close
**Outputs:** tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

**Parameters:**
- `tenkan_period` (default 9, typical 7-11) — Standard 9; Goichi Hosoda's original setting
- `kijun_period` (default 26, typical 22-30) — Standard 26; original setting
- `senkou_b_period` (default 52, typical 48-60) — Standard 52; original setting

**Interpretation:** Price above cloud = uptrend. Price below cloud = downtrend. Price inside cloud = consolidation. Cloud color (green/red) shows trend direction. Chikou above price = bullish. Tenkan > Kijun = momentum bullish. Cloud as dynamic support/resistance. Requires context of all 5 lines together.

**Look-ahead risk:** High: Spans A/B plotted 26 bars forward = forward-looking; Chikou plotted 26 bars back = lagging. Complex multi-timeframe construction
- https://www.babypips.com/learn/forex/ichimoku-kinko-hyo
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/ichimoku-cloud
- https://www.ifcmarkets.com/en/ntx-indicators/ichimoku

### Kaufman Adaptive Moving Average  `kama`
*trend · TA-Lib* · aliases: KAMA, Kaufman Adaptive MA, KAM

**What:** An adaptive moving average that adjusts sensitivity based on the Efficiency Ratio (trend strength). Moves faster in trending markets, slower in choppy markets, automatically filtering noise.

**How / formula:** ER (Efficiency Ratio) = |Close - Close(n bars ago)| / Sum(|Close - Close(1 bar ago)|). SC (Smoothing Constant) = [ER * (fastest_SC - slowest_SC) + slowest_SC]^2. KAMA = prev_KAMA + SC * (close - prev_KAMA). Fastest SC typically 2/(2+1)=0.667 (EMA2), slowest SC = 2/(30+1)=0.0645 (EMA30).

**Inputs:** close
**Outputs:** kama

**Parameters:**
- `period` (default 10, typical 5-50) — Perry Kaufman default 10; shorter (5) for faster response, longer (20-50) for less noise
- `fast_period` (default 2, typical 2-5) — Fastest EMA constant; 2 is standard (not typically changed)
- `slow_period` (default 30, typical 20-50) — Slowest EMA constant; standard 30 (higher = more smoothing in choppy markets)

**Interpretation:** Flat KAMA in choppy/sideways = market with low trend. Steep KAMA = strong trending market. Price breaks above KAMA = bullish. Below KAMA = bearish. Better than fixed-period MA in mixed markets.

**Look-ahead risk:** No lookahead risk; uses only past price data to compute efficiency.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/kaufmans-adaptive-moving-average-kama/
- https://ta-lib.github.io/ta-lib-python/

### Kaufman Adaptive Moving Average  `kama`
*trend · FinTA* · aliases: KAMA, Kaufman AMA, Adaptive Moving Average

**What:** An adaptive moving average that adjusts its smoothing factor based on market efficiency (direction vs volatility), responding quickly in trending markets and slowing in sideways/noisy markets.

**How / formula:** Efficiency Ratio (ER) = |Price_current - Price_n_periods_ago| / Sum(|Price_current - Price_previous|). Smoothing Constant (SC) = [ER × (fastest - slowest) + slowest]², where fastest = 2/(fastest_period + 1) and slowest = 2/(slowest_period + 1). KAMA = KAMA_prev + SC × (Price_current - KAMA_prev).

**Inputs:** close
**Outputs:** kama_value

**Parameters:**
- `efficiency_period` (default 10, typical [5, 20]) — Perry Kaufman's standard is 10. Measures direction vs noise over this lookback.
- `fastest_period` (default 2, typical [2, 5]) — 2 is standard, corresponding to fastest EMA (2/(2+1) = 0.67). Fastest response in trending conditions.
- `slowest_period` (default 30, typical [20, 50]) — 30 is standard, corresponding to slowest EMA (2/(30+1) = 0.065). Slowest response in noisy markets.

**Interpretation:** Price above KAMA indicates uptrend; below indicates downtrend. KAMA slope steepness shows trend strength (steep = strong, flat = weak). KAMA flattens during consolidation, accelerates during breakouts. Unlike fixed EMA, KAMA avoids false signals in choppy markets.

**Look-ahead risk:** None. Adaptive constant based only on historical data.
- https://github.com/peerchemist/finta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama

### Least Squares Moving Average  `lsma`
*trend · Regression-based technical analysis* · aliases: LSMA, Linear Regression MA, Least Squares MA

**What:** Linear regression-based moving average fitting best-fit line to price data and projecting forward, reduces lag versus SMA

**How / formula:** Performs least-squares linear regression over n periods. Projects regression line forward to current bar. LSMA = value of regression line at current bar. Reduces lag of traditional MA by fitting trend line rather than averaging.

**Inputs:** close
**Outputs:** lsma

**Parameters:**
- `period` (default 20, typical 10-40) — Standard 20; shorter (10) more responsive/noisy; longer (40) smoother/laggier

**Interpretation:** Price above LSMA = uptrend. Price below LSMA = downtrend. LSMA slope angle = trend strength. Crossovers signal trend changes with less lag than SMA. Useful for identifying reversals earlier. Prone to whipsaw in ranging markets.

**Look-ahead risk:** Regression line projects current values; minimal lookahead bias but more subjective than SMA
- https://trendspider.com/learning-center/what-is-least-squares-moving-average-lsma/
- https://www.tradingview.com/support/solutions/43000599877-least-squares-moving-average/
- https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/least-squares-moving-average

### Moving Average (Generic)  `ma`
*trend · TA-Lib* · aliases: MA

**What:** A generic moving average function that accepts a matype parameter to choose among 9 different MA types (SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3).

**How / formula:** Calculation varies by matype: matype=0 (SMA), 1 (EMA), 2 (WMA), 3 (DEMA), 4 (TEMA), 5 (TRIMA), 6 (KAMA), 7 (MAMA), 8 (T3). See individual indicator entries for specific formulas.

**Inputs:** close
**Outputs:** ma

**Parameters:**
- `timeperiod` (default 30, typical 5-200) — Adjust based on desired lag/smoothing; shorter = more responsive, longer = smoother
- `matype` (default 0, typical 0-8) — 0=SMA (simplest), 1=EMA (standard), 4=TEMA (smooth), 6=KAMA (adaptive)

**Interpretation:** Interpretation depends on chosen matype. See individual MA indicator entries.

**Look-ahead risk:** No lookahead risk inherent; risk depends on chosen matype.
- https://ta-lib.github.io/ta-lib-python/
- https://github.com/mrjbq7/ta-lib

### MESA Adaptive Moving Average  `mama`
*trend · TA-Lib* · aliases: MAMA, FAMA, Following Adaptive MA, MESA Adaptive MA

**What:** An adaptive moving average using Hilbert Transform phase calculation (by John Ehlers). Outputs MAMA (leading) and FAMA (following). Adapts to market cycles automatically.

**How / formula:** MAMA = alpha * price + (1-alpha) * MAMA_prev. Alpha = FastLimit / DeltaPhase, where DeltaPhase is computed from Hilbert Transform homodyne discriminator phase rate. Alpha constrained between slow_limit and fast_limit. FAMA = MAMA applied to MAMA (one-bar lagged MAMA line).

**Inputs:** close
**Outputs:** mama, fama

**Parameters:**
- `fast_limit` (default 0.5, typical 0.2-0.9) — 0.5 is Ehlers standard; higher = more responsive
- `slow_limit` (default 0.05, typical 0.01-0.2) — 0.05 is standard; lower = more smoothing in choppy conditions

**Interpretation:** MAMA crossover FAMA = trend change signal. Minimal crossovers (virtually whipsaw-free per Ehlers). MAMA > FAMA = uptrend, MAMA < FAMA = downtrend. MAMA is leading, FAMA is lagging; use both for confirmation.

**Look-ahead risk:** Uses Hilbert Transform phase calculation; Ehlers-designed indicators optimized for cycle matching. May exhibit slight forward bias in certain market conditions.
- https://www.mesasoftware.com/papers/MAMA.pdf
- https://phemex.com/academy/what-is-mesa-adaptive-moving-average
- https://ta-lib.github.io/ta-lib-python/

### Moving Average with Variable Period  `mavp`
*trend · TA-Lib* · aliases: MAVP, Variable Period MA

**What:** A moving average where the lookback period changes at each bar, specified by a separate periods array. Allows dynamic adjustment of MA sensitivity.

**How / formula:** For each bar i: MAVP[i] = MovingAverage(data, period[i])[i]. Takes two equal-length arrays: price data and period values. Applies the MA calculation using the specified period for that bar.

**Inputs:** close, periods (array)
**Outputs:** mavp

**Parameters:**
- `minperiod` (default 2, typical 2-5) — Minimum lookback; 2 is typical
- `maxperiod` (default 30, typical 10-100) — Maximum lookback; caps the period values
- `matype` (default 0, typical 0-8) — 0=SMA (default), 1=EMA, etc.

**Interpretation:** Same as underlying matype, but adapted dynamically. Useful when period is driven by volatility, ADX, or other adaptive conditions.

**Look-ahead risk:** No lookahead risk if periods array is calculated from past data only. Risk depends on how periods array is constructed.
- https://github.com/mrjbq7/ta-lib/issues/175
- https://doc.bccnsoft.com/docs/php-docs-7-en/function.trader-mavp.html
- https://ta-lib.github.io/ta-lib-python/

### Minus Directional Indicator  `minus_di`
*trend · TA-Lib* · aliases: MINUS_DI, -DI

**What:** Component of Directional Movement System. Measures downward directional strength using smoothed minus directional movement normalized by true range. Ranges 0-100.

**How / formula:** -DM = max(Previous Low - Current Low, 0), but only if this value is larger than Current High - Previous High; otherwise -DM = 0. Smooth -DM using Wilder's method over n periods. -DI = (Smoothed -DM / Smoothed TR) × 100. Higher -DI values indicate stronger downtrend potential.

**Inputs:** high, low
**Outputs:** minus_di

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is standard. Shorter periods increase sensitivity to downtrend starts; longer periods reduce noise.

**Interpretation:** -DI > +DI: downtrend or bearish pressure. -DI crossing above +DI: sell signal (when ADX > 20). -DI = 0-20: weak downtrend. -DI > 40: strong downtrend. Compare with +DI and ADX for directional confirmation.

**Look-ahead risk:** Unstable period: ~150 bars for Wilder's smoothing convergence (similar to ADX). Initial 30-150 bars unreliable.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx

### Minus Directional Movement  `minus_dm`
*trend · TA-Lib* · aliases: MINUS_DM, -DM

**What:** Raw directional movement component measuring downward price pressure. Calculated before Wilder's smoothing; serves as input to MINUS_DI and ADX system.

**How / formula:** DownMove = Previous Low - Current Low. If DownMove > UpMove (Current High - Previous High) and DownMove > 0, then -DM = DownMove; otherwise -DM = 0. Result is unsmoothed. Smoothed -DM is used in -DI calculations.

**Inputs:** high, low
**Outputs:** minus_dm

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is standard for smoothing applied after raw -DM.

**Interpretation:** Raw -DM > 0 on each bar indicates downward movement occurred. Smoothed -DM compared to smoothed +DM shows which directional pressure dominates. Used primarily as diagnostic for ADX system; rarely used standalone.

**Look-ahead risk:** Raw -DM has no unstable period (calculated from current bar only). Smoothed -DM has ~150 bar convergence lag.
- https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/admiw

### Plus Directional Indicator  `plus_di`
*trend · TA-Lib* · aliases: PLUS_DI, +DI

**What:** Component of Directional Movement System. Measures upward directional strength using smoothed plus directional movement normalized by true range. Ranges 0-100.

**How / formula:** +DM = max(Current High - Previous High, 0), but only if this value is larger than Previous Low - Current Low; otherwise +DM = 0. Smooth +DM using Wilder's method over n periods. +DI = (Smoothed +DM / Smoothed TR) × 100. Higher +DI values indicate stronger uptrend potential.

**Inputs:** high, low
**Outputs:** plus_di

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is standard. Shorter periods increase sensitivity to uptrend starts; longer periods reduce noise.

**Interpretation:** +DI > -DI: uptrend or bullish pressure. +DI crossing above -DI: buy signal (when ADX > 20). +DI = 0-20: weak uptrend. +DI > 40: strong uptrend. Compare with -DI and ADX for directional confirmation.

**Look-ahead risk:** Unstable period: ~150 bars for Wilder's smoothing convergence (similar to ADX). Initial 30-150 bars unreliable.
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx

### Plus Directional Movement  `plus_dm`
*trend · TA-Lib* · aliases: PLUS_DM, +DM

**What:** Raw directional movement component measuring upward price pressure. Calculated before Wilder's smoothing; serves as input to PLUS_DI and ADX system.

**How / formula:** UpMove = Current High - Previous High. If UpMove > DownMove (Previous Low - Current Low) and UpMove > 0, then +DM = UpMove; otherwise +DM = 0. Result is unsmoothed. Smoothed +DM is used in +DI calculations.

**Inputs:** high, low
**Outputs:** plus_dm

**Parameters:**
- `timeperiod` (default 14, typical 10-28) — 14 is standard for smoothing applied after raw +DM.

**Interpretation:** Raw +DM > 0 on each bar indicates upward movement occurred. Smoothed +DM compared to smoothed -DM shows which directional pressure dominates. Used primarily as diagnostic for ADX system; rarely used standalone.

**Look-ahead risk:** Raw +DM has no unstable period (calculated from current bar only). Smoothed +DM has ~150 bar convergence lag.
- https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/admiw

### Parabolic SAR  `psar`
*trend · Tulip Indicators, J. Welles Wilder Jr. (1978)* · aliases: SAR, Parabolic stop and reverse, Wilder's SAR

**What:** Stop-and-reverse indicator that provides entry/exit points by tracking price with accelerating trailing stop levels

**How / formula:** Uptrend SAR = Previous SAR + AF × (Extreme Point - Previous SAR). Downtrend SAR = Previous SAR - AF × (Previous SAR - Extreme Point). AF (Acceleration Factor) starts at 0.02, increases 0.02 each time new extreme reached, max 0.20. Reverses when price crosses SAR.

**Inputs:** high, low
**Outputs:** psar

**Parameters:**
- `initial_af` (default 0.02, typical 0.01-0.03) — Standard 0.02; lower (0.01) slower SAR progression; higher (0.03) faster catches reversals sooner
- `max_af` (default 0.2, typical 0.15-0.25) — Standard 0.20; controls maximum acceleration

**Interpretation:** SAR below price = uptrend; SAR above price = downtrend. Reversal when price crosses SAR. Used as trailing stop-loss. Accelerating SAR indicates strengthening trend. Works best in strong trending markets.

**Look-ahead risk:** Tomorrow's SAR calculated using today's data; limited lookahead bias
- https://tulipindicators.org/psar
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/psar

### Parabolic SAR  `sar`
*trend · TA-Lib* · aliases: SAR, Parabolic Stop and Reverse, PSAR

**What:** A time-price stop-and-reverse indicator tracking extreme points and accelerating factor. Provides trailing stops and reversal signals. Created by J. Welles Wilder.

**How / formula:** SAR_uptrend = Previous_SAR + AF * (Extreme_Point - Previous_SAR). SAR_downtrend = Previous_SAR - AF * (Previous_SAR - Extreme_Point). AF starts at 0.02, increases by 0.02 each time new Extreme_Point is recorded, capped at 0.20. Reversal occurs when price crosses SAR.

**Inputs:** high, low
**Outputs:** sar

**Parameters:**
- `acceleration` (default 0.02, typical 0.01-0.05) — 0.02 is standard (Wilder's default); lower = slower SAR acceleration, less whipsaw
- `maximum` (default 0.2, typical 0.1-0.5) — 0.2 is standard; caps acceleration factor growth

**Interpretation:** SAR above price = downtrend (SAR is resistance/stop level). SAR below price = uptrend (SAR is support/stop level). SAR crossover = potential trend reversal. Smooth SAR = strong trend; jagged SAR = choppy market.

**Look-ahead risk:** No lookahead risk; SAR is calculated from past high/low data. Not repainting on closed candles.
- https://blog.quantinsti.com/parabolic-sar/
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/parabolic-sar/
- https://ta-lib.github.io/ta-doc/indicator/SAR.htm

### Parabolic SAR - Extended  `sarext`
*trend · TA-Lib* · aliases: SAREXT, SAR Extended, Parabolic SAR Extended

**What:** An extended version of Parabolic SAR allowing asymmetric acceleration factors for long and short positions. Addresses market asymmetry where bull/bear trends have different characteristics.

**How / formula:** Similar to SAR but with separate AF parameters for uptrend and downtrend. startValue controls initial direction (positive=long, negative=short, zero=auto-detect). offsetOnReverse adds buffer on reversal. Sign of output encodes direction; use Abs(value) for actual SAR level.

**Inputs:** high, low
**Outputs:** sar

**Parameters:**
- `startValue` (default 0, typical -0.5 to 0.5) — 0=auto-detect from first bar directional movement; positive/negative forces direction
- `offsetOnReverse` (default 0, typical 0-0.1) — Adds buffer on reversal to prevent whipsaw; typically 0
- `af_long_init` (default 0.02, typical 0.01-0.05) — Initial AF for uptrend; typically same as downtrend
- `af_long_increment` (default 0.02, typical 0.01-0.05) — AF increment per new extreme point in uptrend
- `af_long_max` (default 0.2, typical 0.1-0.5) — Maximum AF for uptrend; standard 0.2
- `af_short_init` (default 0.02, typical 0.01-0.05) — Initial AF for downtrend; can differ from long for asymmetry
- `af_short_increment` (default 0.02, typical 0.01-0.05) — AF increment per new extreme point in downtrend
- `af_short_max` (default 0.2, typical 0.1-0.5) — Maximum AF for downtrend

**Interpretation:** Same as standard SAR but direction-aware. Allows bull markets (gradual rise) vs. bear markets (sharp decline) to be handled differently. Take Abs(SAR) for actual price level.

**Look-ahead risk:** No lookahead risk; calculated from past data. Output sign encodes direction (not repainting).
- https://www.tradingview.com/script/qW0mCNW6-Parabolic-SAR-Extended-SAREXT/
- https://knowledge.cloudquant.com/325
- https://tradomate.one/docs/strategy-builder/technical-indicators/overlap/sarext/

### Simple Moving Average  `sma`
*trend · TA-Lib* · aliases: SMA, Simple MA

**What:** An unweighted average of the last N price periods. The most basic moving average; treats all prices equally.

**How / formula:** SMA = (Price1 + Price2 + ... + PriceN) / N. Sum the last N closing prices and divide by N. As each new price comes in, the oldest price is dropped.

**Inputs:** close
**Outputs:** sma

**Parameters:**
- `timeperiod` (default 30, typical 5-200) — 50/200 for long-term trends; 20/50 for swing trading; 5-10 for intraday

**Interpretation:** Price above SMA = uptrend. Price below SMA = downtrend. Slope = trend strength. SMA crossover = trend change. Multiple SMAs (20/50/200) for trend confirmation.

**Look-ahead risk:** No lookahead risk; uses only past completed price bars.
- https://www.wallstreetmojo.com/simple-moving-average/
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/simple-moving-average-sma/
- https://ta-lib.github.io/ta-lib-python/

### Simple Moving Average  `sma`
*trend · Tulip Indicators, foundational technical analysis* · aliases: SMA, Average, Moving average

**What:** Arithmetic average of prices over n periods; basic smoothing filter for trend identification

**How / formula:** SMA = Sum of last n closing prices / n. Recalculates each bar by dropping oldest value, adding newest. No weighting; all prices equally important. Lag increases with longer periods.

**Inputs:** close
**Outputs:** sma

**Parameters:**
- `period` (default 20, typical 5-200) — Short-term: 5-20; medium: 20-50; long-term: 50-200. Shorter periods = more responsive/noise; longer = smoother/lag

**Interpretation:** Price above SMA = uptrend; below = downtrend. Slope angle shows trend strength. SMA acts as dynamic support/resistance. Multiple SMAs (20/50/200) identify trend regime. Golden cross (50 > 200) bullish; death cross bearish.

**Look-ahead risk:** None; simple backward-looking average
- https://tulipindicators.org/sma
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/sma
- https://www.investopedia.com/terms/s/sma.asp

### Simple Moving Median  `smm`
*trend · FinTA* · aliases: Moving Median

**What:** A moving average alternative that uses the median value instead of the arithmetic mean over a window, making it more robust to sharp price shocks and anomalies.

**How / formula:** For each period, sort all closing prices in the lookback window and select the middle value. The median is resistant to outliers, unlike the simple moving average which can be skewed by extreme values.

**Inputs:** close
**Outputs:** smm_value

**Parameters:**
- `period` (default 20, typical [5, 200]) — Shorter periods (5-20) for responsive signals; longer periods (50-200) for trend confirmation. Use when markets exhibit sudden price jumps.

**Interpretation:** Crossovers between price and SMM signal trend changes. Price above SMM indicates uptrend; below indicates downtrend. Similar to SMA but with fewer false signals in volatile markets.

**Look-ahead risk:** None. Calculated using only historical data up to the current period.
- https://github.com/peerchemist/finta
- https://www.quantshare.com/item-1448-simple-moving-median-indicator

### Smoothed Simple Moving Average  `ssma`
*trend · FinTA* · aliases: SMMA, Smoothed Moving Average

**What:** A hybrid between SMA and EMA that applies additional smoothing to reduce noise while maintaining longer-term historical influence. Older data exerts minimal but continuing influence.

**How / formula:** SSMA uses a recursive formula similar to EMA but with a longer effective period. Calculation: SSMA = (SSMA_prev * (period - 1) + price) / period. The oldest price data never fully exits the calculation.

**Inputs:** close
**Outputs:** ssma_value

**Parameters:**
- `period` (default 20, typical [5, 200]) — Default 20 for general trending; 50-200 for longer-term trends. Less sensitive to volatility than EMA but more responsive than SMA.

**Interpretation:** Price above SSMA signals uptrend; below signals downtrend. Crossovers of short and long SSMA generate trend-change signals. Particularly useful in noisy markets with fewer false signals than SMA.

**Look-ahead risk:** None. Uses only historical data.
- https://github.com/peerchemist/finta
- https://www.chartmill.com/documentation/technical-analysis/indicators/217-The-Smoothed-Moving-Average-SMMA

### Schaff Trend Cycle  `stc`
*trend · FinTA, bukosabino/ta* · aliases: STC, Schaff Trend Cycle

**What:** A trend-following indicator applying double stochastic smoothing to MACD, creating an oscillator (0-100) that identifies trend changes and overbought/oversold conditions with reduced lag.

**How / formula:** EMA1 = EMA(close, 23). EMA2 = EMA(close, 50). MACD = EMA1 - EMA2. Apply Stochastic Oscillator (%K, %D) to MACD values over 10 periods. Apply Stochastic again to the result (%K of %D = PF, then %D of PF = STC). Final STC ranges 0-100.

**Inputs:** close
**Outputs:** stc_value

**Parameters:**
- `short_ema` (default 23, typical [20, 30]) — 23 is standard for MACD short EMA.
- `long_ema` (default 50, typical [45, 60]) — 50 is standard for MACD long EMA.
- `stoch_period` (default 10, typical [8, 14]) — 10 is standard for stochastic lookback window.

**Interpretation:** STC > 75 indicates strong uptrend (overbought, potential short). STC < 25 indicates strong downtrend (oversold, potential long). STC between 25-75 indicates consolidation or weak trend. Crossovers at 50 may signal trend reversals. Buy at 25, sell at 75 (standard strategy).

**Look-ahead risk:** Lag from MACD and double stochastic smoothing. Signals arrive later but with confirmation.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://library.tradingtechnologies.com/trade/chrt-ti-schaff-trend-cycle.html

### Supertrend  `supertrend`
*trend · pandas-ta* · aliases: SUPERT

**What:** A trend-following overlay indicator that identifies trend direction and generates buy/sell signals using ATR-based bands that act as dynamic support and resistance levels.

**How / formula:** Calculates MID = multiplier × ATR(length), then LOWERBAND = HL2 - MID, UPPERBAND = HL2 + MID where HL2 is (high+low)/2. Final bands are adjusted to prevent whipsaws based on previous closes. Supertrend follows the upper band in downtrends and lower band in uptrends.

**Inputs:** high, low, close
**Outputs:** SUPERT, SUPERTd, SUPERTl, SUPERTs

**Parameters:**
- `length` (default 7, typical 5-20) — Default 7 is common; use 10-14 for medium-term trends, 5-7 for shorter timeframes
- `multiplier` (default 3, typical 2.0-4.0) — 3.0 is standard; higher values (4.0) create wider bands for less whipsaws

**Interpretation:** When price crosses above the lower band in an uptrend, go long; when below upper band in downtrend, go short. Trend reversal occurs at band crossovers. SUPERTl/SUPERTs provide optimal exit levels.

**Look-ahead risk:** Uses current bar ATR and close price; no lookahead bias but adapts immediately to volatility changes.
- https://tradingstrategy.ai/docs/api/technical-analysis/overlap/help/pandas_ta.overlap.supertrend.html

### Triple Exponential Moving Average (T3)  `t3`
*trend · TA-Lib* · aliases: T3, Tilson T3, Triple Exponential T3

**What:** A smoothed moving average using triple exponential smoothing with a variable factor controlling smoothness. Reduces lag while maintaining smoothness. Created by Tim Tillson.

**How / formula:** T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3, where e3=EMA(e2), e4=EMA(e3), e5=EMA(e4), e6=EMA(e5). Coefficients: c1=a^3, c2=3*a^2+3*a^3, c3=6*a^2-3*a-3*a^3, c4=1+3*a+a^3+3*a^2, where a=vfactor (usually 0.7 or 0.618).

**Inputs:** close
**Outputs:** t3

**Parameters:**
- `timeperiod` (default 5, typical 3-20) — 5 is Tillson default; adjust for desired responsiveness
- `vfactor` (default 0.7, typical 0-1) — 0.7 or 0.618 (golden ratio); 0=plain EMA, 1=full DEMA smoothing

**Interpretation:** Similar to EMA but smoother. Price above T3 = uptrend. Below T3 = downtrend. Smoother slope = cleaner trend. Crossover signals = trend changes.

**Look-ahead risk:** No lookahead risk; calculated from past price data.
- https://help.tc2000.com/m/69445/l/755023-tilson-t3-moving-average
- https://doc.bccnsoft.com/docs/php-docs-7-en/function.trader-t3.html
- https://ta-lib.github.io/ta-lib-python/

### Triple Exponential Moving Average  `tema`
*trend · TA-Lib* · aliases: TEMA, Triple EMA

**What:** A three-stage exponential moving average that reduces lag by combining single, double, and triple EMAs. Developed by Patrick Mulloy (1994).

**How / formula:** TEMA = (3 * EMA1) - (3 * EMA2) + EMA3, where EMA1=EMA(close), EMA2=EMA(EMA1), EMA3=EMA(EMA2). The formula subtracts increasing lags to accelerate the moving average.

**Inputs:** close
**Outputs:** tema

**Parameters:**
- `timeperiod` (default 30, typical 5-200) — Shorter (5-10) for fast trends, longer (20-50) for swing/position trading

**Interpretation:** Price above TEMA = uptrend. Price below TEMA = downtrend. TEMA crossover = early trend signal. Much faster response than SMA, less lag than single EMA.

**Look-ahead risk:** No lookahead risk; uses past price data only. May repaint on incomplete bars (expected behavior).
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema
- https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/tema
- https://ta-lib.github.io/ta-lib-python/

### Triangular Moving Average  `trima`
*trend · TA-Lib* · aliases: TRIMA, Triangular MA

**What:** A weighted moving average where weights form a triangle, placing maximum weight on the middle of the period and minimum on the edges. Very smooth, high lag.

**How / formula:** TRIMA applies triangular weights: for period=7, weights are [1,2,3,4,3,2,1]. Can be computed as: TRIMA = SMA(SMA(close, (n+1)/2), (n+1)/2) for odd periods or SMA(SMA(close, n/2), n/2+1) for even periods.

**Inputs:** close
**Outputs:** trima

**Parameters:**
- `timeperiod` (default 30, typical 5-50) — Longer periods (20-50) for smooth trends; shorter (5-10) for faster response

**Interpretation:** Very smooth trend indicator. Price above TRIMA = uptrend. Below TRIMA = downtrend. High lag makes it better for identifying established trends, not early entries.

**Look-ahead risk:** No lookahead risk; uses only past price data.
- https://tulipindicators.org/trima
- https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/triangular-moving-average
- https://ta-lib.org/functions/

### TRIX  `trix`
*trend · Jack Hutson (Technical Analysis of Stocks & Commodities, early 1980s)* · aliases: TRIX, Triple EMA, Triple Exponential Oscillator

**What:** Triple exponential moving average momentum indicator showing percentage change of triple-smoothed prices

**How / formula:** EMA1 = EMA(Close, period). EMA2 = EMA(EMA1, period). EMA3 = EMA(EMA2, period). TRIX = [(EMA3 - Previous EMA3) / Previous EMA3] × 10000. Triple smoothing filters minor price movements; output as percentage change.

**Inputs:** close
**Outputs:** trix

**Parameters:**
- `period` (default 15, typical 10-21) — Standard 15; developed early 1980s by Jack Hutson. Lower values more responsive; higher smoother

**Interpretation:** TRIX > 0 = upward momentum. TRIX < 0 = downward momentum. Zero-line crossovers signal reversals. Signal line (9-period EMA of TRIX) crossovers generate trades. Extreme values indicate overbought/oversold. Best for identifying trend shifts, not entries.

**Look-ahead risk:** Triple smoothing creates lag; most valuable as confirmation, not leading indicator
- https://www.warriortrading.com/triple-exponential-moving-average-trix/
- https://trendspider.com/learning-center/trix-indicator-explained-enhance-your-trading-with-triple-exponential-averages/
- https://www.avatrade.com/education/technical-analysis-indicators-strategies/trix-indicator-strategies

### Vortex Indicator  `vortex`
*trend · pandas-ta* · aliases: VTX, VI, Vortex

**What:** A trend identification indicator that uses positive and negative vortex movement ratios to identify trend direction and strength by measuring directional movement relative to true range.

**How / formula:** Calculates VMP = |high - low[drift]| (positive vortex movement) and VMN = |low - high[drift]| (negative vortex movement). Then VIP = SUM(VMP, length) / SUM(TR, length) and VIM = SUM(VMN, length) / SUM(TR, length) where TR is true range. Trend is up when VIP > VIM.

**Inputs:** high, low, close
**Outputs:** VIP, VIM

**Parameters:**
- `length` (default 14, typical 10-20) — 14 is standard; use 10 for more responsive signals, 20 for less noise
- `drift` (default 1, typical 1-2) — 1 is standard; represents period offset for comparison

**Interpretation:** Uptrend when VIP > VIM with increasing separation; downtrend when VIM > VIP. Crossover signals trend reversals. The magnitude of separation indicates trend strength.

**Look-ahead risk:** No lookahead bias; uses only historical price comparisons within the lookback window.
- https://tradingstrategy.ai/docs/api/technical-analysis/trend/help/pandas_ta.trend.vortex.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator

### Vortex Indicator  `vortex`
*trend · FinTA, bukosabino/ta* · aliases: VI, VI+ and VI-

**What:** A trend-following indicator measuring positive and negative vortex movements (directional price movement) relative to true range, generating signals from crossovers of the VI+ and VI- lines.

**How / formula:** Positive Movement (VM+) = |High_current - Low_previous|. Negative Movement (VM-) = |Low_current - High_previous|. True Range (TR) = max(High_current - Low_current, |High_current - Close_previous|, |Low_current - Close_previous|). VI+ = Sum(VM+, period) / Sum(TR, period). VI- = Sum(VM-, period) / Sum(TR, period).

**Inputs:** high, low, close
**Outputs:** vi_plus, vi_minus

**Parameters:**
- `period` (default 14, typical [7, 30]) — 14 is standard. Shorter periods increase sensitivity but risk whipsaws; longer periods reduce false signals but may miss entries.

**Interpretation:** VI+ > VI- signals uptrend. VI- > VI+ signals downtrend. Crossovers (VI+ crossing above VI-) generate buy signals; crossovers below generate sell signals. Divergences identify potential reversals. Greater separation between VI+ and VI- indicates stronger trend.

**Look-ahead risk:** None. Calculated from prior bars' OHLC.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/vortex-indicator-vi/

### Vortex Indicator  `vortex`
*trend · Etienne Botes / Douglas Siepman (2010)* · aliases: VI, Vortex, VI+ VI-

**What:** Pair of oscillators measuring positive and negative vortex movement relative to true range, identifies trend direction and reversal

**How / formula:** VM+ = |High(t) - Low(t-1)|. VM- = |Low(t) - High(t-1)|. TR = true range. VI+ = SUM(VM+,n) / SUM(TR,n). VI- = SUM(VM-,n) / SUM(TR,n). VI+ > VI- = uptrend; VI- > VI+ = downtrend. Crossovers signal direction changes.

**Inputs:** high, low
**Outputs:** vi_positive, vi_negative

**Parameters:**
- `period` (default 14, typical 10-30) — Standard 14; shorter (10) more sensitive; longer (20-30) fewer false signals

**Interpretation:** VI+ > VI- sustained = uptrend with VI+ > 1 ideal. VI- > VI+ sustained = downtrend with VI- > 1 ideal. Crossovers signal trend changes. Both lines rising = strength; falling = weakening. Works well in trending markets.

**Look-ahead risk:** None; backward-looking vortex movement calculation
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/vortex-indicator-vi/
- https://www.tradingview.com/support/solutions/43000591352-vortex-indicator/
- https://www.luxalgo.com/blog/vortex-indicator-trend-direction-using-adx/

### Weighted Moving Average  `wma`
*trend · TA-Lib* · aliases: WMA, Weighted MA

**What:** A moving average where recent prices receive higher weights, declining linearly toward older prices. More responsive than SMA but less so than EMA.

**How / formula:** WMA = (P1*W1 + P2*W2 + ... + Pn*Wn) / (W1 + W2 + ... + Wn), where weights are assigned linearly: for period=5, weights are [1,2,3,4,5] with 5 being most recent. Sum of weights = N*(N+1)/2.

**Inputs:** close
**Outputs:** wma

**Parameters:**
- `timeperiod` (default 30, typical 5-100) — 10-20 for swing trading; 5 for faster response; 50+ for longer trends

**Interpretation:** Price above WMA = uptrend. Below WMA = downtrend. More responsive than SMA due to linear weighting. Slopes and crossovers signal trend changes.

**Look-ahead risk:** No lookahead risk; uses only historical price data.
- https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/weighted-moving-average-wma/
- https://www.xs.com/en/blog/weighted-moving-average/
- https://ta-lib.github.io/ta-lib-python/



## volatility  (23)

### Aberration  `aberration`
*volatility · pandas-ta* · aliases: ABER, Aberration Bands

**What:** Volatility envelope indicator using ATR-scaled bands around SMA of typical price, similar to Keltner Channels

**How / formula:** TP = HLC3 = (high + low + close) / 3, ZG = SMA(TP, length), ATR = ATR(high, low, close, atr_length), SG = ZG + ATR (upper band), XG = ZG - ATR (lower band)

**Inputs:** high, low, close
**Outputs:** ZG, SG, XG

**Parameters:**
- `length` (default 5, typical 3-10) — 5 standard; shorter for responsiveness, longer for smoothness
- `atr_length` (default 15, typical 10-30) — 15 standard for ATR period
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Price above SG = overbought/volatility high. Price below XG = oversold/volatility low. SG-XG width = current volatility measure. Breakouts beyond bands signal volatility expansion

**Look-ahead risk:** Minimal; ATR lag provides buffering
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volatility/aberration.html
- https://www.pandas-ta.dev/api/volatility/

### Acceleration Bands  `accbands`
*volatility · pandas-ta* · aliases: ACCBANDS, Acceleration Bands

**What:** Price Headley's volatility envelope based on high-low range ratio, scaled to SMA to create adaptive bands based on relative price volatility

**How / formula:** HL_Ratio = c × (high - low) / (high + low), HIGH_Band = high × (1 + HL_Ratio), LOW_Band = low × (1 - HL_Ratio), MID_Band = SMA(close, length, mamode)

**Inputs:** high, low, close
**Outputs:** LOW_BAND, MID_BAND, HIGH_BAND

**Parameters:**
- `length` (default 10, typical 5-20) — 10 standard per Headley; shorter for faster bands, longer for smoothness
- `c` (default 4, typical 2-6) — 4 standard multiplier; higher = wider bands, lower = tighter
- `mamode` (default sma, typical sma, ema, dema) — SMA standard; EMA for faster bands
- `drift` (default 1, typical 1-2) — Period for change calculation
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Price touches upper band = overextended (overbought potential). Lower band = underextended (oversold potential). Band width = relative volatility (wider = higher volatility). Bands compress before breakouts

**Look-ahead risk:** Minimal; based on current and prior data
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volatility/accbands.html
- https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.accbands.html

### Average True Range  `atr`
*volatility · TA-Lib* · aliases: ATR

**What:** A volatility indicator designed by J. Welles Wilder Jr. that measures the average range of price movement, capturing both normal intraday range and gaps/limit moves to quantify market volatility independent of price direction.

**How / formula:** ATR is calculated in two stages: (1) True Range (TR) for each period = max(High - Low, abs(High - Prior Close), abs(Low - Prior Close)); this captures the largest move considering gaps; (2) ATR = EMA(TR, period) using Wilder's smoothing method (alternatively, some use SMA). The three components of TR ensure volatility from gaps and limit moves are captured, not just the high-low range.

**Inputs:** high, low, close
**Outputs:** atr

**Parameters:**
- `timeperiod` (default 14, typical 10-21) — Default of 14 periods is Wilder's original recommendation and most widely used. Shorter periods (10-12) react faster to volatility changes; longer periods (18-21) smooth volatility more. Period length depends on trading timeframe (intraday vs daily).

**Interpretation:** Higher ATR values indicate higher volatility (larger average price swings). Lower ATR values indicate lower volatility (tighter price ranges). ATR is used to set stop-loss distances, position sizes, and bollinger band widths. Rising ATR suggests increasing volatility; falling ATR suggests decreasing volatility. Compare ATR across different securities only with normalization (use NATR).

**Look-ahead risk:** Unstable period: initial values (approximately first 'period' bars) unreliable due to EMA initialization and insufficient historical data for averaging. No forward look-ahead bias; uses only prior and current data.
- https://ta-lib.github.io/ta-lib-python/func_groups/volatility_indicators.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr-and-average-true-range-percent-atrp
- https://en.wikipedia.org/wiki/Average_true_range

### Average True Range  `atr`
*volatility · Tulip Indicators, J. Welles Wilder Jr. (1978)* · aliases: ATR, Average True Range volatility

**What:** Measures market volatility by averaging the true range (largest of: H-L, |H-PC|, |L-PC|) over a period

**How / formula:** True Range = MAX(High - Low, |High - Previous Close|, |Low - Previous Close|). First ATR = simple average of TR over n periods. Subsequent values: ATR = [(Previous ATR × (n-1)) + Current TR] / n. Uses smoothed (Wilder) averaging.

**Inputs:** high, low, close
**Outputs:** atr

**Parameters:**
- `period` (default 14, typical 10-22) — Standard 14; lower values (10) more responsive to recent volatility; higher (22) smoother historical view

**Interpretation:** Rising ATR = increasing volatility. Falling ATR = decreasing volatility. ATR value = typical daily price range; used to set stop-loss distance and position sizing. No directional signal; purely volatility measure.

**Look-ahead risk:** None; backward-looking volatility measure based on completed bars
- https://tulipindicators.org/atr
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr-and-average-true-range-percent-atrp
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/atr

### Bollinger Bands  `bbands`
*volatility · TA-Lib* · aliases: BBANDS, Bollinger Band

**What:** A volatility-based overlay consisting of three bands (upper, middle, lower) around price. The middle band is a simple moving average, and the upper/lower bands are standard deviations away from it, expanding/contracting with volatility.

**How / formula:** Middle_band = SMA(close, period). Upper_band = Middle_band + (nbdevup * StdDev(close, period)). Lower_band = Middle_band - (nbdevdn * StdDev(close, period)). Standard deviation measures price volatility over the lookback period.

**Inputs:** close
**Outputs:** upperband, middleband, lowerband

**Parameters:**
- `timeperiod` (default 20, typical 10-50) — 20 is standard for daily charts; use 5-10 for fast/scalping, 50+ for long-term trends
- `nbdevup` (default 2, typical 1-3) — 2 std devs is standard; 2.5-3 for wider bands, 1.5 for tighter sensitivity
- `nbdevdn` (default 2, typical 1-3) — Usually same as nbdevup; can be asymmetric for directional bias
- `matype` (default 0, typical 0-8) — 0=SMA (standard), 1=EMA (faster response), 3=DEMA, 4=TEMA for smoother bands

**Interpretation:** Price at/above upper band = overbought (potential pullback). Price at/below lower band = oversold (potential bounce). Narrow bands (squeeze) = low volatility, often precedes breakout. Band walk = strong trend. Bands widen = increasing volatility.

**Look-ahead risk:** No lookahead risk; bands are calculated from past data only. Not repainting as bands are based on completed periods.
- https://ta-lib.github.io/ta-doc/indicator/BBANDS.htm
- https://www.pyquantlab.com/article.php?file=Technical+Indicators+Bollinger+Bands+(BBANDS).html
- https://scanz.com/bollinger-bands-guide/

### Bollinger Bands  `bollinger_bands`
*volatility · Tulip Indicators, John Bollinger (1980s)* · aliases: BB, Bollinger, Price Bands

**What:** A volatility envelope constructed using a simple moving average and standard deviations, forming upper and lower bands around price

**How / formula:** Middle Band = 20-period SMA. Upper Band = SMA + (2 × standard deviation). Lower Band = SMA - (2 × standard deviation). Standard deviation measures price dispersion from the SMA. Approximately 95% of price action falls within the bands.

**Inputs:** close
**Outputs:** upper_band, middle_band, lower_band

**Parameters:**
- `period` (default 20, typical 15-30) — Standard 20; shorter (10-15) for faster response to volatility changes; longer (30+) for smoother bands
- `stddev_mult` (default 2, typical 1.5-3) — Standard 2; use 1.5-1.8 for tighter bands in ranging markets; 2.5-3 for wider bands in volatile markets

**Interpretation:** Price near upper band = overbought; near lower band = oversold. Band squeeze signals low volatility before breakout. Band walk indicates strong trend. Bollinger Bounce: price bouncing off bands is normal. Band expansion shows increased volatility.

**Look-ahead risk:** Standard deviation is recalculated with current bar; repaints slightly on new bar
- https://tulipindicators.org/bbands
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands
- https://www.britannica.com/money/bollinger-bands-indicator

### Chaikin Volatility  `chaikin_volatility`
*volatility · Marc Chaikin (technical analysis pioneer)* · aliases: Chaikin Vol, Marc Chaikin Volatility

**What:** Volatility indicator measuring expansion/contraction of high-low range smoothed with moving average

**How / formula:** High-Low difference = High - Low over n periods. Apply moving average to smooth. Calculate rate of change of smoothed difference. Rising = increasing volatility; falling = decreasing. Often 10-period MA of difference, then 10-period ROC of that MA.

**Inputs:** high, low
**Outputs:** chaikin_volatility

**Parameters:**
- `period` (default 10, typical 7-14) — Standard 10; lookback period for high-low range
- `smooth_period` (default 10, typical 7-14) — Standard 10; moving average smoothing

**Interpretation:** Positive = expanding volatility (potential breakout after squeeze). Negative = contracting volatility (consolidation possible). Rising indicator = increasing volatility often precedes major move. Used to identify squeeze/breakout setups. Not directional; purely volatility measure.

**Look-ahead risk:** None; backward-looking volatility measurement
- https://www.ifcmarkets.com/en/ntx-indicators/chaikin-volatility
- https://gocharting.com/docs/charting/technical-indicator/oscillators/chaikin-volatility
- https://www.luxalgo.com/blog/williams-fractal-spotting-reversal-in-trends/

### Donchian Channel  `donchian`
*volatility · pandas-ta* · aliases: DC, Donchian, Donchian Channels

**What:** Volatility envelope using highest high and lowest low over lookback periods; useful for breakout and range-bound trading

**How / formula:** DCU = MAX(high, upper_length), DCL = MIN(low, lower_length), DCM = (DCU + DCL) / 2 (middle band)

**Inputs:** high, low
**Outputs:** DCL, DCM, DCU

**Parameters:**
- `lower_length` (default 20, typical 10-50) — 20 standard; shorter for more trades, longer for key support
- `upper_length` (default 20, typical 10-50) — Often matches lower_length; can be different for asymmetric channels
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Price break above upper = uptrend/breakout. Break below lower = downtrend/breakdown. Middle band = midpoint support/resistance. Width = trading range size

**Look-ahead risk:** FORWARD-LOOKING RISK: High and low used in calculation are from future bars relative to signal generation (standard Donchian behavior), causing repaint
- https://www.pandas-ta.dev/api/volatility/
- https://raposa.trade/blog/use-python-to-trade-the-donchian-channel/

### Donchian Channels  `donchian`
*volatility · Richard Donchian* · aliases: Donchian channel, Donchian bands, Highest high/lowest low

**What:** Non-centered volatility envelope showing highest high and lowest low over period, identifies breakout levels and volatility

**How / formula:** Upper Band = Highest High of last n periods. Lower Band = Lowest Low of last n periods. Middle Line = (Upper + Lower) / 2. Channel width reflects volatility: narrow = consolidation; wide = volatility. Recalculates each bar.

**Inputs:** high, low
**Outputs:** upper_band, lower_band, middle_band

**Parameters:**
- `period` (default 20, typical 10-30) — Standard 20; higher values (30) show longer-term extremes; lower (10-14) recent extremes. Shorter periods identify breakout points faster.

**Interpretation:** Price breaking above upper band = bullish breakout; below lower band = bearish. Channel width = volatility measure. Narrow channel = consolidation before breakout. Wide channel = high volatility. Used for stop placement and trend confirmation.

**Look-ahead risk:** None; uses only historical highs/lows
- https://en.wikipedia.org/wiki/Donchian_channel
- https://www.avatrade.com/education/technical-analysis-indicators-strategies/donchian-channel-trading-strategies
- https://www.strike.money/technical-analysis/donchian-channel

### Keltner Channel  `kc`
*volatility · pandas-ta* · aliases: KC, Keltner Channels

**What:** Volatility envelope indicator using moving average center with ATR-scaled bands, similar to Bollinger Bands but ATR-based

**How / formula:** BASIS = MA(close, length, mamode), RANGE = ATR(high, low, close, length) or (high - low), UPPER = BASIS + scalar × RANGE, LOWER = BASIS - scalar × RANGE

**Inputs:** high, low, close
**Outputs:** KCL, KCB, KCU

**Parameters:**
- `length` (default 20, typical 10-50) — 20 standard; 10-15 for faster bands, 30+ for trend channels
- `scalar` (default 2, typical 1-3) — 2 standard (2 ATRs); 1.5 for tighter, 3 for looser bands
- `mamode` (default ema, typical ema, sma, dema) — EMA standard; SMA for simpler envelope
- `tr` (default True, typical true, false) — True uses ATR (gap-aware); false uses high-low only
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Price outside bands = volatility breakout. Price touches upper band = overbought. Lower band = oversold. Band width = volatility level. Narrow bands precede expansion

**Look-ahead risk:** Minimal; bands based on current/past data only. ATR lookback period should be considered in lookback analysis
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volatility/kc.html
- https://www.pandas-ta.dev/api/volatility/

### Keltner Channels  `keltner_channels`
*volatility · Chester Keltner (modified with ATR by Linda Bradford Raschke)* · aliases: KC, Keltner Band, ATR bands

**What:** Volatility envelope using EMA as middle band and ATR as offset; alternative to Bollinger Bands with smoothed range

**How / formula:** Middle = 20-period EMA (or 10/period typical). Upper = EMA + (ATR × 2). Lower = EMA - (ATR × 2). Uses ATR instead of standard deviation. ATR captures true range including gaps; more responsive to volatility spikes than Bollinger Bands.

**Inputs:** high, low, close
**Outputs:** upper_band, middle_band, lower_band

**Parameters:**
- `period` (default 20, typical 10-30) — Standard 20; shorter (10) more responsive; longer smoother
- `atr_period` (default 10, typical 8-14) — Standard 10; ATR lookback
- `atr_mult` (default 2, typical 1.5-3) — Standard 2; band distance multiplier

**Interpretation:** Price above upper = overbought/strong trend. Price below lower = oversold/weak. Squeeze when bands narrow = low volatility, breakout pending. Band touching = temporary extremes. Less prone to false signals than Bollinger Bands in gappy markets.

**Look-ahead risk:** ATR recalculates; slight repaint on new bar but backward-looking
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/keltner-channels
- https://lightningchart.com/blog/trader/what-are-keltner-channels/
- https://phemex.com/academy/what-is-keltner-channel

### Mass Index  `massi`
*volatility · pandas-ta* · aliases: MI, Mass Index

**What:** Non-directional volatility reversal indicator measuring high-low range expansion/contraction to identify potential trend reversals

**How / formula:** HL = high - low, HL_EMA1 = EMA(HL, fast), HL_EMA2 = EMA(HL_EMA1, fast), HL_Ratio = HL_EMA1 / HL_EMA2, MASSI = SUM(HL_Ratio, slow)

**Inputs:** high, low
**Outputs:** MASSI

**Parameters:**
- `fast` (default 9, typical 5-15) — 9 standard per Donald Dorsey; smaller for sensitivity
- `slow` (default 25, typical 20-40) — 25 standard for reversal window; longer = fewer signals
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Above 27 = range expansion peak, potential reversal imminent. Below 26 = consolidation, no reversal signal. Peak formation (above 27 then falling) = highest reversal probability

**Look-ahead risk:** Minimal; uses only high-low range currently available
- https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.massi.html

### Mass Index  `mi`
*volatility · FinTA, bukosabino/ta* · aliases: Mass Index

**What:** A volatility indicator identifying trend reversals by detecting range expansions, based on the ratio of nested EMAs of the high-low range without directional bias.

**How / formula:** Range = High - Low. EMA1 = EMA(Range, 9). EMA2 = EMA(EMA1, 9). EMA Ratio = EMA1 / EMA2. Mass Index = Sum(EMA Ratio, 25). A reversal bulge occurs when MI reaches 27+ and then falls below 26.

**Inputs:** high, low
**Outputs:** mass_index

**Parameters:**
- `ema_period` (default 9, typical [9, 9]) — Fixed at 9 per Dorsey's design.
- `sum_period` (default 25, typical [25, 25]) — Fixed at 25. This creates the 25-bar sum window for reversal detection.

**Interpretation:** Normal MI range is 20-25. MI > 27 indicates range expansion and potential reversal setup. Primary signal: MI > 27 then falls below 26 (reversal bulge). Reversal can occur in either direction regardless of current trend. Does not indicate trend direction, only reversal probability.

**Look-ahead risk:** None. Uses only prior bars.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://library.tradingtechnologies.com/trade/chrt-ti-mass-index.html

### Normalized Average True Range  `natr`
*volatility · TA-Lib* · aliases: NATR, ATR%, Normalized ATR

**What:** A volatility indicator that normalizes ATR as a percentage of the current closing price, allowing volatility comparison across securities with different price levels and across time periods.

**How / formula:** NATR = (ATR / Close) × 100, where ATR is calculated as described above with the default period of 14. Normalization divides ATR by current close price and multiplies by 100 to express volatility as a percentage of price. This removes price-level bias: a $10 stock with $0.50 ATR has the same 5% NATR as a $100 stock with $5.00 ATR.

**Inputs:** high, low, close
**Outputs:** natr

**Parameters:**
- `timeperiod` (default 14, typical 10-21) — Default of 14 periods matches standard ATR. Shorter periods make NATR more responsive; longer periods smooth volatility measurement. Use same period as ATR for consistency.

**Interpretation:** NATR expresses volatility as a percentage (e.g., 2% means price typically swings 2% on average). Higher NATR indicates higher relative volatility. Enables direct comparison: two stocks with different price levels. Use NATR to screen for high-volatility stocks across sectors or to normalize volatility over time for the same security. Rising NATR = increasing volatility; falling NATR = decreasing volatility.

**Look-ahead risk:** Unstable period: same as ATR (first ~14 bars unreliable). No forward look-ahead bias; uses current and historical data only.
- https://ta-lib.github.io/ta-lib-python/func_groups/volatility_indicators.html
- https://www.tradingtechnologies.com/xtrader-help/x-study/technical-indicator-definitions/normalized-average-true-range-natr/
- https://www.macroption.com/normalized-atr/

### Price Distance  `pdist`
*volatility · pandas-ta* · aliases: PDIST

**What:** Directional volatility measure calculating total price movement distance by combining intrabar and interbar range changes

**How / formula:** PDIST = 2(high - low) - |close - open| + |open - open_prev|. Weights intrabar range double, subtracts gap-neutral direction changes, adds cross-day gaps

**Inputs:** open, high, low, close
**Outputs:** PDIST

**Parameters:**
- `drift` (default 1, typical 1-2) — 1 for standard period-to-period prior bar comparison
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Higher values = greater price movement (volatility expansion). Rising PDIST = increasing volatility. Gaps contribute significantly. Useful for volatility breakout confirmation

**Look-ahead risk:** Minimal; backward-looking measurement only
- https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.pdist.html

### Relative Volatility Index  `rvi`
*volatility · pandas-ta* · aliases: RVI

**What:** RSI-like oscillator measuring standard deviation of upward vs downward price changes to quantify directional volatility

**How / formula:** StdDev_Up = StdDev(close) where close > close_prev, StdDev_Dn = StdDev(close) where close < close_prev (over length), RVI = 100 × EMA(StdDev_Up, N) / (EMA(StdDev_Up, N) + EMA(StdDev_Dn, N))

**Inputs:** close, high, low
**Outputs:** RVI

**Parameters:**
- `length` (default 14, typical 7-30) — 14 standard (RSI period); 7-10 for sensitivity, 20+ for smoothness
- `scalar` (default 100, typical 100) — Percent scaling to 0-100 range
- `mamode` (default ema, typical ema, sma) — EMA standard per RVI design
- `refined` (default False, typical true, false) — Refined version uses additional calculations for smoothness
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Above 50 = upside volatility dominates (bullish pressure). Below 50 = downside volatility dominates (bearish pressure). Overbought > 80 / oversold < 20. Divergences highlight reversals

**Look-ahead risk:** Minimal; standard deviation calculated on prior periods
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volatility/rvi.html
- https://devexperts.com/dxcharts/kb/docs/relative-volatility-index-rvi

### STARC Bands  `starc_bands`
*volatility · FinTA* · aliases: Stoller Average Range Channels

**What:** A volatility band indicator forming a channel around a simple moving average using the Average True Range (ATR) as the band width, designed to contain approximately 90% of price action.

**How / formula:** STARC+ = SMA(close, ma_period) + (ATR_multiplier × ATR(atr_period)). STARC- = SMA(close, ma_period) - (ATR_multiplier × ATR(atr_period)). Standard parameters: 6-period SMA, 15-period ATR with multiplier of 2.

**Inputs:** high, low, close
**Outputs:** starc_upper, starc_lower

**Parameters:**
- `ma_period` (default 6, typical [5, 20]) — 6-day SMA is standard (shorter than Bollinger Bands). Shorter periods track price more tightly.
- `atr_period` (default 15, typical [10, 20]) — 15-period ATR is standard. Longer periods reduce band fluttering.
- `atr_multiplier` (default 2, typical [1.5, 3]) — Multiplier of 2 estimates 90% of price action within bands per Stoller's research. Adjust for tighter/looser containment.

**Interpretation:** Price touching upper band indicates overbought (high-risk buy, low-risk sell). Price touching lower band indicates oversold (low-risk buy, high-risk sell). Band expansion signals increased volatility; contraction signals consolidation. Breakouts from bands with volume confirm trend reversals.

**Look-ahead risk:** ATR calculation uses intrabar highs/lows, not just closes. Bands repaint slightly as ATR updates each bar.
- https://github.com/peerchemist/finta
- https://lightningchart.com/blog/trader/starc-bands/

### Elder's Thermometer  `thermo`
*volatility · pandas-ta* · aliases: THERMO, Thermometer

**What:** Volatility measure comparing current price movement against exponential moving average to identify temperature/intensity of trading, generating long/short signals

**How / formula:** ThermoL = |low - low_prev|, ThermoH = |high - high_prev|, Thermo = MAX(ThermoL, ThermoH), Thermo_MA = EMA(Thermo, length), Signal_Long = Thermo < (Thermo_MA × long_scalar), Signal_Short = Thermo > (Thermo_MA × short_scalar)

**Inputs:** high, low
**Outputs:** THERMO

**Parameters:**
- `length` (default 20, typical 10-30) — 20 standard per Elder; shorter for responsiveness
- `long` (default 2, typical 1.5-3) — Multiplier for long signal threshold (above MA × 2)
- `short` (default 0.5, typical 0.3-1) — Multiplier for short signal threshold (below MA × 0.5)
- `mamode` (default ema, typical ema, sma) — EMA per Elder design
- `drift` (default 1, typical 1-2) — Period comparison
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Thermo > Thermo_MA × 2 = hot market, potential end of move. Thermo < Thermo_MA × 0.5 = cold market, potential reversal. Oscillating pattern = consolidation range

**Look-ahead risk:** Minimal; lagged by EMA of range
- https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.thermo.html
- https://lightrun.com/answers/twopirllc-pandas-ta-elders-market-thermometer-calculation

### True Range  `trange`
*volatility · TA-Lib* · aliases: TR, True Range

**What:** The raw, single-period volatility measure that captures the greatest distance between price boundaries in a period, including gaps. It is the foundational component used to calculate ATR.

**How / formula:** True Range for each period is the maximum of three values: (1) High - Low (today's range); (2) abs(High - Prior Close) (gap from previous close to today's high); (3) abs(Low - Prior Close) (gap from previous close to today's low). Formula: TR = max(High - Low, abs(High - Close_prev), abs(Low - Close_prev)). The three components ensure gap moves and limit moves are captured, not just the intraday high-low range.

**Inputs:** high, low, close
**Outputs:** trange

**Interpretation:** TRANGE is always positive and represents the single-period volatility magnitude. Large TR values indicate volatile periods (wide ranges or gaps). Small TR values indicate quiet periods. TRANGE is rarely used directly; it is typically aggregated into ATR (average) for a smoothed volatility measure. Use TRANGE to identify volatility spikes or when individual period volatility is needed rather than a moving average.

**Look-ahead risk:** No look-ahead bias. Calculated from current and prior period data only; no forward projection or smoothing across future bars.
- https://ta-lib.github.io/ta-lib-python/func_groups/volatility_indicators.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr-and-average-true-range-percent-atrp
- https://www.tradingview.com/support/solutions/43000501823-average-true-range-atr/

### Ulcer Index  `ui`
*volatility · pandas-ta* · aliases: UI, Ulcer Index

**What:** Downside volatility risk measure using quadratic mean of percentage drawdowns, penalizing large losses more than small ones

**How / formula:** MaxClose = MAX(close, window), Drawdown_Pct = ((close - MaxClose) / MaxClose) × 100, UI = SQRT(SUM(Drawdown_Pct^2, window) / window)

**Inputs:** close
**Outputs:** UI

**Parameters:**
- `window` (default 14, typical 7-30) — 14 standard; shorter for sensitivity, longer for stability
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Higher values = greater downside volatility / drawdown risk. UI > 5 = high downside risk. UI < 2 = low risk. Compare UI between securities to assess relative downside volatility

**Look-ahead risk:** Depends on rolling maximum lookback; if using forward maximum creates look-ahead bias
- https://www.quantifiedstrategies.com/ulcer-index/
- https://www.stockmaniacs.net/ulcer-index-indicator/

### Ulcer Index  `ulcer_index`
*volatility · bukosabino/ta* · aliases: UI

**What:** A downside risk volatility indicator measuring the depth and duration of drawdowns from prior highs over a lookback period, using root mean square of percentage retracements.

**How / formula:** For each bar, identify highest close seen so far in the period. Calculate percentage drawdown from that high = ((highest - current) / highest) × 100. UI = sqrt(average of squared drawdowns). UI = sqrt(Sum(drawdown²) / period).

**Inputs:** close
**Outputs:** ulcer_index

**Parameters:**
- `period` (default 14, typical [10, 30]) — 14 is standard. Typical lookback for recent peak-to-current drawdown risk.

**Interpretation:** UI < 5 indicates low drawdown risk. UI 5-10 indicates moderate drawdown risk. UI > 10 indicates excessive drawdown risk. Lower UI signals more stable trends; higher UI indicates significant pullbacks from recent highs. Risk-averse traders use UI threshold to filter entries.

**Look-ahead risk:** None. Uses rolling highest close over prior bars.
- https://github.com/bukosabino/ta
- https://en.wikipedia.org/wiki/Ulcer_index

### VHF (Vertical Horizontal Filter)  `vhf`
*volatility · pandas-ta* · aliases: VHF, Vertical Horizontal, VHF Trend

**What:** A trend detection indicator created by Adam White that identifies whether markets are in a trending or ranging state by comparing vertical price movement to horizontal volatility.

**How / formula:** Calculates HHV = highest high over length, LLV = lowest low over length. VHF = (HHV - LLV) / SUM(|close - close[1]|, length). High VHF = trending (large vertical vs. small changes); Low VHF = ranging.

**Inputs:** high, low, close
**Outputs:** VHF

**Parameters:**
- `length` (default 28, typical 14-50) — Lookback period; 28 is standard for weekly trends

**Interpretation:** VHF > 0.5 = trending market (good for breakout); < 0.4 = ranging market (good for mean-reversion). Threshold ~0.45 separates trending from ranging. Use as market regime filter.

**Look-ahead risk:** No lookahead bias; uses only past high/low and price changes.
- https://github.com/twopirllc/pandas-ta

### Alpha#55: Normalized High-Low Range × Volume Rank  `wq_alpha_55`
*volatility · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 55, Alpha#55

**What:** Negated correlation between 12-bar normalized high-low range (Williams %R style) and volume, detecting when volatility (range) is not confirmed by volume.

**How / formula:** Formula: (-1 * correlation(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12)))), rank(volume), 6)). Compute 12-bar high-low normalized range (0-1 scale), rank cross-sectionally. Rank volume cross-sectionally. Correlate over 6 periods. Negate: high correlation (range+volume co-move) → negative alpha; divergence → positive alpha.

**Inputs:** close, high, low, volume
**Outputs:** alpha_factor_-1_to_1

**Parameters:**
- `range_period` (default 12, typical 5 to 20) — 12 captures ~2.4 trading weeks of volatility history.
- `correlation_period` (default 6, typical 3 to 10) — 6 captures daily confirmation patterns.

**Interpretation:** Positive: range/volume divergence (weak conviction in volatility). Negative: range-volume confirmation (sustained volatility).

**Look-ahead risk:** None.
- https://arxiv.org/abs/1601.00991



## volume  (25)

### Accumulation/Distribution Line  `ad`
*volume · TA-Lib* · aliases: A/D, Chaikin A/D Line, AD Line

**What:** A volume-weighted accumulation indicator developed by Marc Chaikin that quantifies money flow in and out of a security by measuring the relationship between closing price and the high-low range, multiplied by volume.

**How / formula:** The AD line is calculated in three steps: (1) Money Flow Multiplier = [(Close - Low) - (High - Close)] / (High - Low), which ranges from +1 (close at high) to -1 (close at low); (2) Money Flow Volume = Multiplier × Period Volume; (3) AD Line = Previous AD + Current Period Money Flow Volume. The multiplier is positive when close is in upper half of range (accumulation) and negative when in lower half (distribution).

**Inputs:** high, low, close, volume
**Outputs:** ad

**Interpretation:** Rising AD line indicates accumulation (buying pressure). Falling AD line indicates distribution (selling pressure). Divergences between AD and price (price makes new high but AD doesn't) signal potential reversals. Use AD to confirm trends: uptrends should show rising AD, downtrends should show falling AD.

**Look-ahead risk:** No look-ahead bias. Calculated from current period OHLCV data without forward projection.
- https://ta-lib.github.io/ta-lib-python/func_groups/volume_indicators.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line
- https://www.tradingview.com/support/solutions/43000501770-accumulation-distribution-adl/

### Accumulation/Distribution Line  `ad_line`
*volume · Tulip Indicators, Marc Chaikin* · aliases: A/D line, Chaikin A/D line, Accumulation Distribution

**What:** Volume-based indicator using closing price position within daily range to weight volume as accumulation or distribution

**How / formula:** Money Flow Multiplier = [(Close - Low) - (High - Close)] / (High - Low). Money Flow Volume = Money Flow Multiplier × Volume. A/D = previous A/D + Money Flow Volume. Weighs volume based on close position: near high (bullish), near low (bearish), middle (neutral).

**Inputs:** high, low, close, volume
**Outputs:** ad_line

**Interpretation:** Rising A/D with rising price = healthy accumulation. A/D divergence from price indicates hidden buying/selling. A/D turning before price reversal signals early momentum shift. Divergences more valuable than absolute values.

**Look-ahead risk:** None; uses completed bar data only
- https://tulipindicators.org/ad
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/accumulation-distribution-line

### Accumulation/Distribution Line  `adl`
*volume · FinTA, bukosabino/ta* · aliases: A/D Line, Accumulation Distribution Index

**What:** A cumulative volume-based indicator measuring the flow of money into and out of a security, combining price position within the daily range with volume to assess accumulation vs distribution pressure.

**How / formula:** Money Flow Multiplier (MFM) = ((Close - Low) - (High - Close)) / (High - Low). Money Flow Volume (MFV) = MFM × Volume. A/D = previous A/D + MFV. MFM ranges from +1 (close at high, buying pressure) to -1 (close at low, selling pressure).

**Inputs:** high, low, close, volume
**Outputs:** adl_value

**Interpretation:** Rising A/D with rising price confirms uptrend (accumulation). Rising A/D with falling price signals underlying buying (bullish divergence). Falling A/D with rising price signals weakening trend (bearish divergence). Divergences between A/D and price often precede reversals.

**Look-ahead risk:** None. Cumulative calculation uses only prior bars.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line

### Chaikin A/D Oscillator  `adosc`
*volume · TA-Lib* · aliases: ADOSC, Chaikin A/D Oscillator, AD Oscillator

**What:** A momentum oscillator that combines the Accumulation/Distribution line with exponential moving averages, capturing the difference between fast and slow EMA of the A/D line to identify divergences between price and volume.

**How / formula:** ADOSC calculates the A/D line, then applies two exponential moving averages (EMA) with different periods: Fast_EMA = EMA(AD, fastperiod) and Slow_EMA = EMA(AD, slowperiod). The oscillator value is the difference: ADOSC = Fast_EMA - Slow_EMA. This creates a momentum indicator that oscillates around zero, with positive values indicating strengthening buying pressure and negative values indicating strengthening selling pressure.

**Inputs:** high, low, close, volume
**Outputs:** adosc

**Parameters:**
- `fastperiod` (default 3, typical 2-10) — Default of 3 is standard in TA-Lib. Shorter periods (2-5) make oscillator more responsive to recent A/D changes; longer periods (5-10) smooth signals. Common range in other libraries is 12 for fast period.
- `slowperiod` (default 10, typical 10-30) — Default of 10 is standard in TA-Lib. Controls baseline EMA; slower periods (15-30) reduce noise. Common range in other libraries is 26 for slow period.

**Interpretation:** Positive ADOSC with rising trend suggests strong accumulation momentum; negative ADOSC with falling trend suggests strong distribution momentum. Zero crossovers can signal momentum shifts. Divergences are key: price makes new high but ADOSC doesn't = weakening accumulation = bearish divergence.

**Look-ahead risk:** EMA calculations depend on all prior periods, but no forward-shifted data. Early values (unstable period) may be unreliable due to EMA initialization with limited historical data.
- https://ta-lib.github.io/ta-doc/indicator/ADOSC.htm
- https://ta-lib.github.io/ta-lib-python/func_groups/volume_indicators.html
- https://tradomate.one/docs/strategy-builder/technical-indicators/volume/adosc/

### Archer On-Balance Volume  `aobv`
*volume · pandas-ta* · aliases: AOBV

**What:** Enhanced on-balance volume indicator applying dual EMAs to OBV to smooth and generate faster/slower trend signals

**How / formula:** OBV = cumsum(sign(close.diff) × volume), AOBV_Fast = EMA(OBV, fast), AOBV_Slow = EMA(OBV, slow). Fast and slow are separate OBV smoothing lines

**Inputs:** close, volume
**Outputs:** AOBV_FAST, AOBV_SLOW

**Parameters:**
- `fast` (default 4, typical 2-8) — 4 for responsive signal generation
- `slow` (default 14, typical 10-30) — 14 for trend confirmation
- `mamode` (default ema, typical ema, sma) — EMA for smoothing dynamics
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Fast crosses above slow = accumulation signal. Fast below slow = distribution signal. Distance between lines = trend strength. Divergences with price highlight reversals

**Look-ahead risk:** Cumulative OBV repainting if volume corrected; EMA adds lag
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volume/aobv.html
- https://blog.xcaldata.com/optimizing-trading-insights-with-aobv-archer-on-balance-volume/

### Chaikin Money Flow  `cmf`
*volume · pandas-ta* · aliases: CMF

**What:** Momentum indicator measuring money flow intensity by analyzing buying and selling pressure relative to price position within high-low range, normalized by total trading volume

**How / formula:** CMF = SUM(AD, length) / SUM(volume, length). Where AD (Accumulation/Distribution) uses: (close - open) × volume / (high - low) if open provided, otherwise (2 × close - high - low) × volume / (high - low)

**Inputs:** high, low, close, volume, open (optional)
**Outputs:** CMF_{length}

**Parameters:**
- `length` (default 20, typical 10-30) — Longer periods (21-28) capture broader money flow trends; shorter periods more sensitive
- `offset` (default 0, typical 0-10) — Typically 0 for current values

**Interpretation:** Values above 0 indicate buying pressure; below 0 indicates selling pressure. Extreme values (> 0.25 or < -0.25) suggest strong directional pressure. Divergences between price and CMF signal potential reversals

**Look-ahead risk:** Minimal; uses only price and volume data up to current bar
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.cmf.html
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmf

### Chaikin Money Flow  `cmf`
*volume · FinTA, bukosabino/ta* · aliases: CMF

**What:** A volume-weighted oscillator measuring the cumulative money flow over a lookback period by combining the Money Flow Multiplier (price position in range) with volume, oscillating between -1 and +1.

**How / formula:** Money Flow Multiplier (MFM) = ((Close - Low) - (High - Close)) / (High - Low). Money Flow Volume (MFV) = MFM × Volume. CMF = Sum(MFV over N periods) / Sum(Volume over N periods). Result ranges from -1 to +1, typically -0.5 to +0.5.

**Inputs:** high, low, close, volume
**Outputs:** cmf_value

**Parameters:**
- `period` (default 20, typical [10, 30]) — 20 or 21 periods standard. Shorter (10) for faster response; longer (30) for trend confirmation.

**Interpretation:** Positive CMF signals buying pressure; negative signals selling pressure. CMF > 0 with rising price confirms uptrend. Divergence (price rises but CMF falls) signals weakening uptrend. CMF crossing zero generates trend-change signals.

**Look-ahead risk:** None. Cumulative calculation uses historical OHLCV data only.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf

### Elder's Force Index  `efi`
*volume · pandas-ta* · aliases: EFI, Force Index, FI

**What:** Momentum indicator combining price change with volume to measure buying/selling force, smoothed with moving average

**How / formula:** Raw EFI = close.diff(drift) × volume, then MA(Raw EFI, length, mamode). Positive values indicate buying force, negative indicate selling force

**Inputs:** close, volume
**Outputs:** EFI_{length}

**Parameters:**
- `length` (default 13, typical 2-50) — 13 (standard), 5-10 for fast signals, 20+ for trend confirmation
- `drift` (default 1, typical 1-2) — 1 for bar-to-bar change
- `mamode` (default ema, typical sma, ema, dema, tema) — EMA standard; SMA for simpler signal
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Positive and rising = increasing buying force. Negative and falling = increasing selling force. Zero crossovers signal momentum shifts. Divergences (price new high but EFI lower) warn of weakness

**Look-ahead risk:** Minimal; lagged by moving average smoothing
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volume/efi.html
- https://www.tradingview.com/support/solutions/43000502259-elder-s-force-index-efi/

### Ease of Movement  `emv`
*volume · FinTA, bukosabino/ta* · aliases: EMV, Ease of Move

**What:** A volume-based indicator measuring how easily price moves relative to volume and range, identifying periods of price movement with ease (high EMV) versus difficulty (low/negative EMV).

**How / formula:** Distance Moved = ((High + Low) / 2) - ((Prior High + Prior Low) / 2). EMV_1 = Distance Moved / (Scale × Range), where Scale = Volume / 100,000,000 and Range = High - Low. EMV = SMA(EMV_1, 14). Positive EMV indicates easy upward movement; negative indicates difficult upward movement (easy downward movement).

**Inputs:** high, low, close, volume
**Outputs:** emv_value

**Parameters:**
- `scale_factor` (default 100000000, typical [100000, 100000000]) — Scale factor depends on asset type (stocks typically 100M, forex may use 100k). Calibrate to produce EMV range of approximately ±0.5 to ±2.
- `ma_period` (default 14, typical [10, 20]) — 14 is standard for smoothing raw 1-period EMV.

**Interpretation:** Positive EMV with rising price signals strong uptrend (price moving up on declining volume). Negative EMV indicates downtrend. Zero-line crossovers signal trend changes. High volume with small price movement produces low/negative EMV (difficult movement). Low volume with large price movement produces high EMV (easy movement, institutional move).

**Look-ahead risk:** None. Calculated from prior OHLCV bars.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv

### Ease of Movement  `eom`
*volume · pandas-ta* · aliases: EOM, EMV

**What:** Volume-scaled momentum indicator measuring how easily price moves relative to the high-low range, normalized by volume

**How / formula:** Distance = 0.5 × |high - high_prev + low - low_prev|, HL_Range = high - low, Box_Ratio = (volume / divisor) / HL_Range, EOM = distance / box_ratio, Output = SMA(EOM, length)

**Inputs:** high, low, volume
**Outputs:** EOM_{length}

**Parameters:**
- `length` (default 14, typical 7-28) — 14 standard; 7-10 for responsiveness, 20+ for smoothness
- `divisor` (default 100000000, typical 100000000) — Normalizes volume to reasonable scale (1 billion)
- `drift` (default 1, typical 1-2) — 1 for period-to-period movement
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Positive values = price moving easily up on low volume (bullish). Negative = price moving easily down on low volume (bearish). Large swings on low volume = strong signal

**Look-ahead risk:** Minimal; lagged by SMA smoothing
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.eom.html
- https://library.tradingtechnologies.com/trade/chrt-ti-ease-of-movement.html

### Klinger Volume Oscillator  `kvo`
*volume · pandas-ta* · aliases: KVO

**What:** Volume-price oscillator designed to predict reversals by comparing volume to price trends using dual exponential moving averages on signed volume

**How / formula:** SV = sign(HLC3.diff) × volume (signed volume). KVO = EMA(SV, fast) - EMA(SV, slow). Signal = EMA(KVO, signal_length). HLC3 = (high + low + close) / 3

**Inputs:** high, low, close, volume
**Outputs:** KVO, KVO_SIGNAL

**Parameters:**
- `fast` (default 34, typical 20-50) — 34 standard per Klinger; faster EMA for volume sensitivity
- `slow` (default 55, typical 40-100) — 55 standard per Klinger; slower EMA for trend
- `length_sig` (default 13, typical 10-20) — Signal line smoothing
- `mamode` (default ema, typical ema, sma) — EMA per original design
- `offset` (default 0, typical 0) — No shift

**Interpretation:** KVO crosses above signal = bullish reversal potential. Below signal = bearish. Divergences (price trend vs KVO trend) signal reversals. Extreme KVO values indicate strong accumulation/distribution

**Look-ahead risk:** Minimal; based on current and past data only
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volume/kvo.html
- https://library.tradingtechnologies.com/trade/chrt-ti-klinger-volume-oscillator.html

### Money Flow Index  `mfi`
*volume · pandas-ta* · aliases: MFI

**What:** Momentum oscillator measuring buying and selling pressure using both price and volume, normalized as RSI-like oscillator (0-100)

**How / formula:** MFI = 100 × PMF / (PMF + NMF). Where TP = (high + low + close) / 3, RMF = TP × volume, PMF = sum of RMF when TP increases, NMF = sum of RMF when TP decreases, over length periods

**Inputs:** high, low, close, volume
**Outputs:** MFI_{length}

**Parameters:**
- `length` (default 14, typical 10-28) — 14 is standard; 9-14 for faster signals, 20+ for trend confirmation
- `drift` (default 1, typical 1) — Typically 1 for period-to-period comparison
- `offset` (default 0, typical 0) — No shift by default

**Interpretation:** Above 80 = overbought (divergence with price = bearish), below 20 = oversold (divergence with price = bullish). Values 50-80 and 20-50 indicate moderate buying/selling. Divergences most reliable signal

**Look-ahead risk:** Minimal; cumulative of past price-volume only
- https://tradingstrategy.ai/docs/_modules/pandas_ta/volume/mfi.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi

### Money Flow Index  `mfi`
*volume · Tulip Indicators, technical analysis standard* · aliases: MFI, Money Flow Oscillator

**What:** Volume-weighted oscillator measuring buying vs selling pressure by combining price and volume, output bounded 0-100

**How / formula:** Typical Price = (High + Low + Close) / 3. Raw Money Flow = Typical Price × Volume. If current TP > previous TP: positive flow; else negative flow. Sum positive and negative flows over period (typically 14). Money Flow Ratio = Sum Positive / Sum Negative. MFI = 100 - [100 / (1 + Ratio)].

**Inputs:** high, low, close, volume
**Outputs:** mfi

**Parameters:**
- `period` (default 14, typical 9-21) — Standard 14; shorter (9) more responsive; longer (21) filters more noise

**Interpretation:** MFI > 80 = overbought; MFI < 20 = oversold. Divergences between price and MFI signal reversals. Rising MFI with rising price confirms strength; falling MFI with rising price warns of weakness.

**Look-ahead risk:** None; uses only completed bar data
- https://tulipindicators.org/mfi
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/MFI

### Negative Volume Index  `nvi`
*volume · pandas-ta* · aliases: NVI

**What:** Cumulative indicator isolating smart money activity by tracking price changes during volume decreases, based on theory that informed traders act when volume declines

**How / formula:** When volume < previous volume: NVI = NVI_prev + ((close - close_prev) / close_prev × NVI_prev). When volume >= previous volume: NVI = NVI_prev (no change). Initialized at 1000

**Inputs:** close, volume
**Outputs:** NVI

**Parameters:**
- `initial_value` (default 1000, typical 1000) — Standard cumulative starting point

**Interpretation:** Rising NVI on price increases during low volume = smart money accumulation (bullish). Use with 255-period signal line. NVI above signal + rising = confirmation. NVI below signal = weakness risk

**Look-ahead risk:** Cumulative with repainting potential if volume data is corrected
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.nvi.html
- https://library.tradingtechnologies.com/trade/chrt-ti-negative-volume-index.html

### On Balance Volume  `obv`
*volume · TA-Lib* · aliases: OBV

**What:** A cumulative volume-based oscillator that assigns positive or negative volume based on price direction, measuring cumulative buying and selling pressure by adding volume on up days and subtracting on down days.

**How / formula:** The indicator maintains a running total: if close > previous close, add current volume; if close < previous close, subtract current volume; if close = previous close, volume is unchanged. Formula: OBV = OBV(prior) + {+volume if close > close_prev, -volume if close < close_prev, 0 if close = close_prev}. The calculation begins with an initial OBV value (typically 0) and accumulates signed volume for all subsequent periods.

**Inputs:** close, volume
**Outputs:** obv

**Interpretation:** Rising OBV confirms uptrends (bullish), falling OBV confirms downtrends (bearish). Divergences between OBV and price action may forecast future price reversals. The absolute OBV value is less important than its directional trend; focus on whether OBV makes new highs/lows with price.

**Look-ahead risk:** No look-ahead bias. OBV is calculated from historical close and volume without forward-shifted data.
- https://ta-lib.github.io/ta-lib-python/func_groups/volume_indicators.html
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv
- https://en.wikipedia.org/wiki/On-balance_volume

### On-Balance Volume  `obv`
*volume · Tulip Indicators, Joseph Granville (1963)* · aliases: OBV, On-Balance Volume accumulation

**What:** Cumulative indicator that adds volume on up days and subtracts on down days, treating volume as vote of buying or selling pressure

**How / formula:** If close > previous close: OBV = previous OBV + current volume. If close < previous close: OBV = previous OBV - current volume. If close = previous close: OBV unchanged. Creates running cumulative total reflecting accumulation/distribution.

**Inputs:** close, volume
**Outputs:** obv

**Interpretation:** Rising OBV = accumulation (bullish). Falling OBV = distribution (bearish). OBV divergences signal momentum shifts before price breaks out. OBV confirmation of price breakout indicates strength. Trend direction of OBV more important than absolute value.

**Look-ahead risk:** None; cumulative calculation from completed bars
- https://tulipindicators.org/obv
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/obv

### Positive Volume Index  `pvi`
*volume · pandas-ta* · aliases: PVI

**What:** Cumulative indicator tracking smart money activity by focusing on price changes during periods of increased volume, based on theory that uninformed traders dominate high-volume days

**How / formula:** When volume > previous volume: PVI = PVI_prev + ((close - close_prev) / close_prev × PVI_prev). When volume <= previous volume: PVI = PVI_prev (no change). Initialized at 1000

**Inputs:** close, volume
**Outputs:** PVI

**Parameters:**
- `initial_value` (default 1000, typical 1000) — Standard starting value for cumulative index

**Interpretation:** Rising PVI with price increases on volume spikes = uninformed buying (caution). Use with signal line (usu. 255-period SMA) for crossovers. Extreme divergences (price new high but PVI low) = distribution

**Look-ahead risk:** Cumulative repainting risk; prior PVI values can shift conceptually if volume data corrections occur
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.pvi.html
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index

### Percentage Volume Oscillator  `pvo`
*volume · pandas-ta* · aliases: PVO, Volume Momentum

**What:** A volume-based momentum oscillator that measures the difference between short-term and long-term volume trends as a percentage, indicating shifts in volume momentum.

**How / formula:** Calculates EMA(volume, fast) - EMA(volume, slow) / EMA(volume, slow) * scalar. Signal = EMA(PVO, signal_length). Histogram = PVO - Signal. Scalars typically 100 to express as percentage.

**Inputs:** volume
**Outputs:** PVO, Signal, Histogram

**Parameters:**
- `fast` (default 12, typical 10-15) — Short-term EMA period for volume
- `slow` (default 26, typical 20-30) — Long-term EMA period for volume
- `signal` (default 9, typical 7-12) — Signal line EMA period for crossovers
- `scalar` (default 100, typical 1-100) — 100 expresses as percentage

**Interpretation:** PVO > 0 = bullish volume; < 0 = bearish. PVO crossing above signal = positive volume divergence. Histogram shows magnitude of volume momentum.

**Look-ahead risk:** No lookahead bias; uses only past volume data.
- https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.pvo.html

### Price-Volume  `pvol`
*volume · pandas-ta* · aliases: PVOL, Price Volume

**What:** Simple product of price and volume, optionally with signed direction, showing periods of price-volume agreement

**How / formula:** PVOL = close × volume (basic form), or signed: PVOL = sign(close.diff) × close × volume to show directional price-volume momentum

**Inputs:** close, volume
**Outputs:** PVOL

**Parameters:**
- `offset` (default 0, typical 0) — No typical variation

**Interpretation:** High positive values = price up on volume. High negative values = price down on volume. Useful for confirming breakouts; divergences (price move without volume) signal weakness

**Look-ahead risk:** None; purely mathematical product
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.pvol.html

### Price Volume Rank  `pvr`
*volume · pandas-ta* · aliases: PVR

**What:** Discrete ranking indicator classifying price-volume momentum into 4 ranks based on directional agreement of price and volume changes

**How / formula:** Rank 1: close > close_prev AND volume > volume_prev (bullish confirmation), Rank 2: close > close_prev AND volume < volume_prev (bullish with lower volume), Rank 3: close < close_prev AND volume > volume_prev (bearish with higher volume), Rank 4: close < close_prev AND volume < volume_prev (bearish confirmation)

**Inputs:** close, volume
**Outputs:** PVR

**Parameters:**
- `offset` (default 0, typical 0) — No shift

**Interpretation:** PVR < 2.5 = buy signal (Rank 1-2 bullish). PVR > 2.5 = sell signal (Rank 3-4 bearish). Values near 2.5 = neutral. Used by Anthony Macek for simple momentum confirmation

**Look-ahead risk:** None; purely directional comparison of current vs prior bar
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.pvr.html
- https://www.multicharts.com/discussion/viewtopic.php?t=9018

### Price-Volume Trend  `pvt`
*volume · pandas-ta* · aliases: PVT, Volume Price Trend

**What:** Cumulative momentum indicator combining rate of price change with volume, similar to PVT; shows accumulation/distribution adjusted for price momentum

**How / formula:** ROC = (close - close_drift) / close_drift, PV = ROC × volume, PVT = cumsum(PV). Cumulative sum of (rate of change × volume)

**Inputs:** close, volume
**Outputs:** PVT

**Parameters:**
- `drift` (default 1, typical 1-2) — 1 for standard period-to-period
- `offset` (default 0, typical 0) — No shift

**Interpretation:** Rising PVT = positive price-volume momentum. Divergences (price new high but PVT lower) warn of weakness. PVT slope steepness indicates momentum strength

**Look-ahead risk:** Cumulative repainting possible if volume corrections occur
- https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.pvt.html
- https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/

### Volume Profile  `volume_profile`
*volume · Market profile analysis (James Dalton, 1990s)* · aliases: VP, Volume by price, Traded volume distribution

**What:** Distribution of volume across price levels (not time); shows where most trading activity occurred and fair value

**How / formula:** Accumulate volume into horizontal price bins over period. Display volume on Y-axis, price on X-axis (inverted from typical). Point of Control (POC) = price with highest volume. Value Area = price range containing 70% of volume. High Volume Nodes (HVN) = support/resistance.

**Inputs:** high, low, close, volume
**Outputs:** volume_profile, poc, value_area

**Parameters:**
- `period` (default None, typical day, week, month, or custom lookback) — Typical daily/weekly profile; can be single session or longer
- `bin_size` (default auto, typical price increment or percentage) — Smaller bins = more detail/noise; larger = general overview

**Interpretation:** POC = fair value where buyers/sellers agreed most. Value Area = consensus price range. HVN = support/resistance. Profile height = conviction. Price above/below value area = directional momentum. Gaps in profile = no trading (likely support/resistance).

**Look-ahead risk:** None; historical volume distribution; updates with new periods
- https://www.schwab.com/learn/story/using-volume-profile-indicator
- https://www.oanda.com/us-en/trade-tap-blog/trading-knowledge/volume-profile-explained/
- https://trendspider.com/learning-center/volume-profile-strategies/

### Volume Weighted Average Price  `vwap`
*volume · FinTA* · aliases: VWAP

**What:** The average price of an asset weighted by trading volume. Originally designed for institutional traders to assess execution quality; also used as an intraday dynamic support/resistance level.

**How / formula:** VWAP = Cumulative(Typical Price × Volume) / Cumulative(Volume), where Typical Price = (High + Low + Close) / 3. Calculation resets at the start of each trading day for intraday analysis.

**Inputs:** high, low, close, volume
**Outputs:** vwap_value

**Parameters:**
- `anchor` (default day, typical ['day', 'week', 'month']) — Daily (intraday) is standard for institutional use. Weekly/monthly anchors create longer-term trend references. Typically no additional parameters beyond the reset anchor.

**Interpretation:** Price above VWAP indicates buying strength; below indicates selling pressure. VWAP serves as dynamic support (price pulls back to VWAP) or resistance (price bounces off VWAP). Mean reversion strategies exploit divergences from VWAP.

**Look-ahead risk:** VWAP resets daily (or at period anchor). Not suitable for multi-day trend analysis without weekly/monthly variants. Repainting occurs only at the reset boundary.
- https://github.com/peerchemist/finta
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/volume-weighted-average-price-vwap

### Volume Weighted Moving Average  `vwma`
*volume · FinTA, bukosabino/ta* · aliases: VWMA

**What:** A moving average that weighs price by volume, similar to VWAP but continuously calculated without daily reset, producing a smoother, continuously flowing line.

**How / formula:** VWMA = Cumulative(Close × Volume) / Cumulative(Volume) over the lookback period. Unlike VWAP, the calculation window moves forward without reset, maintaining smooth continuity.

**Inputs:** close, volume
**Outputs:** vwma_value

**Parameters:**
- `period` (default 20, typical [5, 100]) — 20-day is standard. Shorter periods (5-10) for fast-moving markets; longer periods (50-200) for trend confirmation. Similar flexibility to SMA/EMA.

**Interpretation:** Price above VWMA indicates institutional buying; below indicates selling. Smoother than VWAP for multi-day trend following. Crossovers with price or other MAs generate signals similar to SMA but with volume weighting.

**Look-ahead risk:** None. Calculated from historical OHLCV data only.
- https://github.com/peerchemist/finta
- https://github.com/bukosabino/ta
- https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/

### Alpha#15: Volume Anomaly Cumulative Ranking  `wq_alpha_15`
*volume · WorldQuant 101 Formulaic Alphas (arXiv 1601.00991)* · aliases: Alpha 15, Alpha#15

**What:** Negated cumulative 3-bar rolling rank of high-volume correlation, detecting when volume spikes are not confirmed by price strength.

**How / formula:** Formula: (-1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3)). Compute 3-bar rolling correlation(rank(high), rank(volume)), rank those correlations cross-sectionally, sum across 3 periods. Negate. Detects periods where high prices and volume are uncorrelated (anomaly) cumulatively.

**Inputs:** high, volume
**Outputs:** alpha_factor

**Parameters:**
- `correlation_period` (default 3, typical 2 to 5) — 3 captures intra-week confirmation.
- `sum_period` (default 3, typical 2 to 5) — 3 compounds signal over 3 bars.

**Interpretation:** Large negative: volume spikes on high prices repeatedly (healthy continuation). Less negative/positive: volume-price divergence (weak confirmation).

**Look-ahead risk:** None.
- https://arxiv.org/abs/1601.00991


