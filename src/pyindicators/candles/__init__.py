"""candles/ — candlestick-pattern recognition (TA-Lib ``CDL*`` compatible).

Every pattern composes :mod:`pyindicators.candles._candles` (TA-Lib CandleSettings, bit-exact)
and outputs an integer -100/0/100 (with +/-80 partial scores) matching ``talib.CDL*``.
"""

from __future__ import annotations

from .abandoned_baby import AbandonedBaby, abandoned_baby
from .advance_block import AdvanceBlock, advance_block
from .belt_hold import BeltHold, belt_hold
from .breakaway import Breakaway, breakaway
from .closing_marubozu import ClosingMarubozu, closing_marubozu
from .conceal_baby_swallow import ConcealBabySwallow, conceal_baby_swallow
from .counterattack import Counterattack, counterattack
from .dark_cloud_cover import DarkCloudCover, dark_cloud_cover
from .doji import Doji, doji
from .doji_star import DojiStar, doji_star
from .dragonfly_doji import DragonflyDoji, dragonfly_doji
from .engulfing import Engulfing, engulfing
from .evening_doji_star import EveningDojiStar, evening_doji_star
from .evening_star import EveningStar, evening_star
from .gap_side_side_white import GapSideSideWhite, gap_side_side_white
from .gravestone_doji import GravestoneDoji, gravestone_doji
from .hammer import Hammer, hammer
from .hanging_man import HangingMan, hanging_man
from .harami import Harami, harami
from .harami_cross import HaramiCross, harami_cross
from .high_wave import HighWave, high_wave
from .hikkake import Hikkake, hikkake
from .hikkake_mod import HikkakeMod, hikkake_mod
from .homing_pigeon import HomingPigeon, homing_pigeon
from .identical_three_crows import IdenticalThreeCrows, identical_three_crows
from .in_neck import InNeck, in_neck
from .inverted_hammer import InvertedHammer, inverted_hammer
from .kicking import Kicking, kicking
from .kicking_by_length import KickingByLength, kicking_by_length
from .ladder_bottom import LadderBottom, ladder_bottom
from .long_legged_doji import LongLeggedDoji, long_legged_doji
from .long_line import LongLine, long_line
from .marubozu import Marubozu, marubozu
from .mat_hold import MatHold, mat_hold
from .matching_low import MatchingLow, matching_low
from .morning_doji_star import MorningDojiStar, morning_doji_star
from .morning_star import MorningStar, morning_star
from .on_neck import OnNeck, on_neck
from .piercing import Piercing, piercing
from .rickshaw_man import RickshawMan, rickshaw_man
from .rise_fall_three_methods import RiseFallThreeMethods, rise_fall_three_methods
from .separating_lines import SeparatingLines, separating_lines
from .shooting_star import ShootingStar, shooting_star
from .short_line import ShortLine, short_line
from .spinning_top import SpinningTop, spinning_top
from .stalled_pattern import StalledPattern, stalled_pattern
from .stick_sandwich import StickSandwich, stick_sandwich
from .takuri import Takuri, takuri
from .tasuki_gap import TasukiGap, tasuki_gap
from .three_black_crows import ThreeBlackCrows, three_black_crows
from .three_inside import ThreeInside, three_inside
from .three_line_strike import ThreeLineStrike, three_line_strike
from .three_outside import ThreeOutside, three_outside
from .three_stars_in_south import ThreeStarsInSouth, three_stars_in_south
from .three_white_soldiers import ThreeWhiteSoldiers, three_white_soldiers
from .thrusting import Thrusting, thrusting
from .tristar import Tristar, tristar
from .two_crows import TwoCrows, two_crows
from .unique_three_river import UniqueThreeRiver, unique_three_river
from .upside_gap_two_crows import UpsideGapTwoCrows, upside_gap_two_crows
from .xside_gap_three_methods import XSideGapThreeMethods, xside_gap_three_methods

__all__ = [
    "AbandonedBaby", "abandoned_baby",
    "AdvanceBlock", "advance_block",
    "BeltHold", "belt_hold",
    "Breakaway", "breakaway",
    "ClosingMarubozu", "closing_marubozu",
    "ConcealBabySwallow", "conceal_baby_swallow",
    "Counterattack", "counterattack",
    "DarkCloudCover", "dark_cloud_cover",
    "Doji", "doji",
    "DojiStar", "doji_star",
    "DragonflyDoji", "dragonfly_doji",
    "Engulfing", "engulfing",
    "EveningDojiStar", "evening_doji_star",
    "EveningStar", "evening_star",
    "GapSideSideWhite", "gap_side_side_white",
    "GravestoneDoji", "gravestone_doji",
    "Hammer", "hammer",
    "HangingMan", "hanging_man",
    "Harami", "harami",
    "HaramiCross", "harami_cross",
    "HighWave", "high_wave",
    "Hikkake", "hikkake",
    "HikkakeMod", "hikkake_mod",
    "HomingPigeon", "homing_pigeon",
    "IdenticalThreeCrows", "identical_three_crows",
    "InNeck", "in_neck",
    "InvertedHammer", "inverted_hammer",
    "Kicking", "kicking",
    "KickingByLength", "kicking_by_length",
    "LadderBottom", "ladder_bottom",
    "LongLeggedDoji", "long_legged_doji",
    "LongLine", "long_line",
    "Marubozu", "marubozu",
    "MatHold", "mat_hold",
    "MatchingLow", "matching_low",
    "MorningDojiStar", "morning_doji_star",
    "MorningStar", "morning_star",
    "OnNeck", "on_neck",
    "Piercing", "piercing",
    "RickshawMan", "rickshaw_man",
    "RiseFallThreeMethods", "rise_fall_three_methods",
    "SeparatingLines", "separating_lines",
    "ShootingStar", "shooting_star",
    "ShortLine", "short_line",
    "SpinningTop", "spinning_top",
    "StalledPattern", "stalled_pattern",
    "StickSandwich", "stick_sandwich",
    "Takuri", "takuri",
    "TasukiGap", "tasuki_gap",
    "ThreeBlackCrows", "three_black_crows",
    "ThreeInside", "three_inside",
    "ThreeLineStrike", "three_line_strike",
    "ThreeOutside", "three_outside",
    "ThreeStarsInSouth", "three_stars_in_south",
    "ThreeWhiteSoldiers", "three_white_soldiers",
    "Thrusting", "thrusting",
    "Tristar", "tristar",
    "TwoCrows", "two_crows",
    "UniqueThreeRiver", "unique_three_river",
    "UpsideGapTwoCrows", "upside_gap_two_crows",
    "XSideGapThreeMethods", "xside_gap_three_methods",
]
