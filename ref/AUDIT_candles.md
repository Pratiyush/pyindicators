# Correctness Review — candles (65)

The candlestick family is hand-rolled (never delegating to TA-Lib at runtime) but **verified
bit-exact** against TA-Lib's `CDL*` reference: every pattern's parity test asserts
`np.testing.assert_array_equal(ours, talib.CDL<NAME>(...))` over the full series on synthetic +
real data (TA-Lib's lookback warm-up is 0, matching ours). Exact integer equality across the
whole series is the strongest possible correctness evidence, so this review documents the
shared primitives and the per-pattern TA-Lib mapping rather than re-deriving each by hand.

## Shared primitives (`candles/_candles.py`) — read and verified

| Primitive | Definition | Verdict |
|---|---|---|
| `real_body` | `|close - open|` | ✅ |
| `hl_range` | `high - low` | ✅ |
| `upper_shadow` | `high - max(open, close)` | ✅ |
| `lower_shadow` | `min(open, close) - low` | ✅ |
| `both_shadows` | `upper_shadow + lower_shadow` | ✅ |
| `candle_color` | `+1` if `close >= open` else `-1` | ✅ |
| `candle_average` | TA-Lib averaging settings (BodyDoji/BodyShort/BodyLong/ShadowShort/ShadowLong/Near/Far/Equal) with the correct factor + rolling/elementwise divisor per `range_type` (RealBody / HighLow / Shadows) | ✅ matches TA-Lib's `TA_CandleSettings` |

These reproduce TA-Lib's candle-settings machinery; every pattern composes from them, so a single
correct primitive set underpins all 61 CDL patterns.

## TA-Lib CDL patterns (61) — each exact-parity verified vs the named `talib.CDL*`

`two_crows`→CDL2CROWS · `three_black_crows`→CDL3BLACKCROWS · `three_inside`→CDL3INSIDE ·
`three_line_strike`→CDL3LINESTRIKE · `three_outside`→CDL3OUTSIDE ·
`three_stars_in_south`→CDL3STARSINSOUTH · `three_white_soldiers`→CDL3WHITESOLDIERS ·
`abandoned_baby`→CDLABANDONEDBABY · `advance_block`→CDLADVANCEBLOCK · `belt_hold`→CDLBELTHOLD ·
`breakaway`→CDLBREAKAWAY · `closing_marubozu`→CDLCLOSINGMARUBOZU ·
`conceal_baby_swallow`→CDLCONCEALBABYSWALL · `counterattack`→CDLCOUNTERATTACK ·
`dark_cloud_cover`→CDLDARKCLOUDCOVER · `doji`→CDLDOJI · `doji_star`→CDLDOJISTAR ·
`dragonfly_doji`→CDLDRAGONFLYDOJI · `engulfing`→CDLENGULFING · `evening_doji_star`→CDLEVENINGDOJISTAR ·
`evening_star`→CDLEVENINGSTAR · `gap_side_side_white`→CDLGAPSIDESIDEWHITE ·
`gravestone_doji`→CDLGRAVESTONEDOJI · `hammer`→CDLHAMMER · `hanging_man`→CDLHANGINGMAN ·
`harami`→CDLHARAMI · `harami_cross`→CDLHARAMICROSS · `high_wave`→CDLHIGHWAVE · `hikkake`→CDLHIKKAKE ·
`hikkake_mod`→CDLHIKKAKEMOD · `homing_pigeon`→CDLHOMINGPIGEON ·
`identical_three_crows`→CDLIDENTICAL3CROWS · `in_neck`→CDLINNECK · `inverted_hammer`→CDLINVERTEDHAMMER ·
`kicking`→CDLKICKING · `kicking_by_length`→CDLKICKINGBYLENGTH · `ladder_bottom`→CDLLADDERBOTTOM ·
`long_legged_doji`→CDLLONGLEGGEDDOJI · `long_line`→CDLLONGLINE · `marubozu`→CDLMARUBOZU ·
`matching_low`→CDLMATCHINGLOW · `mat_hold`→CDLMATHOLD · `morning_doji_star`→CDLMORNINGDOJISTAR ·
`morning_star`→CDLMORNINGSTAR · `on_neck`→CDLONNECK · `piercing`→CDLPIERCING ·
`rickshaw_man`→CDLRICKSHAWMAN · `rise_fall_three_methods`→CDLRISEFALL3METHODS ·
`separating_lines`→CDLSEPARATINGLINES · `shooting_star`→CDLSHOOTINGSTAR · `short_line`→CDLSHORTLINE ·
`spinning_top`→CDLSPINNINGTOP · `stalled_pattern`→CDLSTALLEDPATTERN · `stick_sandwich`→CDLSTICKSANDWICH ·
`takuri`→CDLTAKURI · `tasuki_gap`→CDLTASUKIGAP · `thrusting`→CDLTHRUSTING · `tristar`→CDLTRISTAR ·
`unique_three_river`→CDLUNIQUE3RIVER · `upside_gap_two_crows`→CDLUPSIDEGAP2CROWS ·
`xside_gap_three_methods`→CDLXSIDEGAP3METHODS

**Verdict: ✅ all 61** — each emits TA-Lib's ±100/±80/0 codes and is asserted bit-exact over the
full real + synthetic series. Multi-bar patterns reproduce TA-Lib's lookback (leading bars 0).

## VSA / price-action extras (4) — not TA-Lib; verified against their definitions

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `spring` | ✅ | Wyckoff spring: a bar dips below a prior support/low then closes back above it (false breakdown). Causal (uses prior bars only). | golden + real-data tests pin the false-break logic. |
| `upthrust` | ✅ | Wyckoff upthrust: pokes above prior resistance then closes back below (false breakout). | golden + real-data. |
| `big_shadow` | ✅ | wide-range engulfing bar (range > prior, body engulfs) — boolean. | golden + real-data. |
| `kangaroo_tail` | ✅ | pin-bar / Pinocchio: a long single shadow with a small body inside the prior range. | golden + real-data. |

## Cross-cutting
- **Causality:** multi-bar patterns read only prior bars (TA-Lib lookback); the real-data
  prefix-vs-full invariant test confirms no look-ahead across all 65.
- **Correctness basis:** exact integer parity vs TA-Lib for the 61 CDL patterns is dispositive;
  the 4 extras are validated structurally against their textbook definitions.
