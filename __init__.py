"""骰子与塔罗牌插件

提供 DND 骰子投掷和赛博塔罗牌占卜功能
"""

from src.plugin_system.base.plugin_metadata import PluginMetadata
from .plugin import DiceAndTarotPlugin

__plugin_meta__ = PluginMetadata(
    name="骰子与塔罗牌插件 (Dice and Tarot)",
    description="提供 DND 骰子投掷和赛博塔罗牌占卜功能。支持标准DND骰子表达式（如2d6+3），包含完整78张塔罗牌，随机正位/逆位占卜。",
    usage="""
    # 骰子投掷
    /roll d20       - 投掷1个20面骰
    /roll 2d6+3     - 投掷2个6面骰，结果加3

    # 塔罗牌占卜
    /tarot          - 抽取1张塔罗牌
    /tarot 3        - 抽取3张塔罗牌
    """,
    version="1.0.0",
    author="MoFox Community",
    license="MIT",
    repository_url="https://github.com/SolenmeChiara/mofox-dice-tarot-plugin",
    keywords=["dice", "tarot", "dnd", "骰子", "塔罗牌", "娱乐", "占卜", "游戏"],
    categories=["Entertainment", "Games", "Fun"],
    extra={
        "is_built_in": False,  # 第三方插件
        "plugin_type": "entertainment",
        "min_bot_version": "1.0.0",
        "python_version": ">=3.11",
    },
)

__all__ = ["DiceAndTarotPlugin", "__plugin_meta__"]
