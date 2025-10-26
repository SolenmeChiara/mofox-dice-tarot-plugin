"""
骰子与塔罗牌插件

提供 DND 骰子投掷和赛博塔罗牌占卜功能
"""

import random
import re
from typing import List

from src.plugin_system.apis.logging_api import get_logger
from src.plugin_system.apis.plugin_register_api import register_plugin
from src.plugin_system.base.base_plugin import BasePlugin
from src.plugin_system.base.command_args import CommandArgs
from src.plugin_system.base.component_types import ChatType, PlusCommandInfo
from src.plugin_system.base.config_types import ConfigField
from src.plugin_system.base.plus_command import PlusCommand

logger = get_logger("DiceAndTarot")


class DiceCommand(PlusCommand):
    """DND 骰子投掷命令"""

    command_name = "roll"
    command_description = "投掷 DND 骰子，格式：/roll 2d6+3 或 /roll d20"
    command_aliases = ["骰子", "dice"]
    priority = 10
    chat_type_allow = ChatType.ALL
    intercept_message = True

    async def execute(self, args: CommandArgs) -> tuple[bool, str | None, bool]:
        """执行骰子投掷"""
        try:
            # 获取骰子表达式
            dice_expr = args.get_raw()
            if not dice_expr:
                await self.send_text("❌ 请提供骰子表达式，例如：/roll 2d6+3")
                return True, "缺少表达式", True

            # 解析并投掷骰子
            result = self._roll_dice(dice_expr)

            if result:
                await self.send_text(result)
                return True, "投掷成功", True
            else:
                await self.send_text("❌ 无效的骰子表达式，请使用格式：XdY+Z（如 2d6+3）")
                return True, "表达式无效", True

        except Exception as e:
            logger.error(f"骰子投掷失败: {e}", exc_info=True)
            await self.send_text(f"❌ 投掷失败: {str(e)}")
            return True, f"失败: {e}", True

    def _roll_dice(self, expr: str) -> str | None:
        """解析并执行骰子投掷

        支持格式：
        - d20 或 1d20（投1个20面骰）
        - 2d6（投2个6面骰）
        - 3d8+5（投3个8面骰，加5）
        - 2d10-3（投2个10面骰，减3）
        """
        # 标准化表达式（去除空格）
        expr = expr.replace(' ', '').lower()

        # 解析骰子表达式：XdY+Z 或 XdY-Z
        pattern = r'^(\d*)d(\d+)(([+\-])(\d+))?$'
        match = re.match(pattern, expr)

        if not match:
            return None

        # 提取参数
        num_dice = int(match.group(1)) if match.group(1) else 1  # 骰子数量
        dice_sides = int(match.group(2))  # 骰子面数
        modifier = 0

        if match.group(3):  # 如果有修正值
            operator = match.group(4)  # + 或 -
            mod_value = int(match.group(5))
            modifier = mod_value if operator == '+' else -mod_value

        # 验证参数
        if num_dice < 1 or num_dice > 100:
            return "❌ 骰子数量必须在 1-100 之间"
        if dice_sides < 2 or dice_sides > 1000:
            return "❌ 骰子面数必须在 2-1000 之间"

        # 投掷骰子
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        # 格式化输出
        if num_dice == 1:
            result = f"🎲 投掷 d{dice_sides}"
            if modifier != 0:
                result += f"{modifier:+d}"
            result += f"\n\n结果：{rolls[0]}"
            if modifier != 0:
                result += f" {modifier:+d} = {total}"
            else:
                result += f" = {total}"
        else:
            result = f"🎲 投掷 {num_dice}d{dice_sides}"
            if modifier != 0:
                result += f"{modifier:+d}"
            result += f"\n\n各次结果：{' + '.join(map(str, rolls))}"
            if modifier != 0:
                result += f" {modifier:+d}"
            result += f"\n总计：{total}"

        return result


class TarotCommand(PlusCommand):
    """赛博塔罗牌占卜命令"""

    command_name = "tarot"
    command_description = "抽取赛博塔罗牌，格式：/tarot 或 /tarot 3"
    command_aliases = ["塔罗", "塔罗牌"]
    priority = 10
    chat_type_allow = ChatType.ALL
    intercept_message = True

    # 78张塔罗牌
    TAROT_CARDS = [
        # 大阿尔克那（22张）
        "愚者", "魔术师", "女祭司", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士",
        "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳",
        "审判", "世界",

        # 权杖（Wands）14张
        "权杖王牌", "权杖二", "权杖三", "权杖四", "权杖五", "权杖六", "权杖七",
        "权杖八", "权杖九", "权杖十", "权杖侍从", "权杖骑士", "权杖皇后", "权杖国王",

        # 圣杯（Cups）14张
        "圣杯王牌", "圣杯二", "圣杯三", "圣杯四", "圣杯五", "圣杯六", "圣杯七",
        "圣杯八", "圣杯九", "圣杯十", "圣杯侍从", "圣杯骑士", "圣杯皇后", "圣杯国王",

        # 宝剑（Swords）14张
        "宝剑王牌", "宝剑二", "宝剑三", "宝剑四", "宝剑五", "宝剑六", "宝剑七",
        "宝剑八", "宝剑九", "宝剑十", "宝剑侍从", "宝剑骑士", "宝剑皇后", "宝剑国王",

        # 钱币（Pentacles/Coins）14张
        "钱币王牌", "钱币二", "钱币三", "钱币四", "钱币五", "钱币六", "钱币七",
        "钱币八", "钱币九", "钱币十", "钱币侍从", "钱币骑士", "钱币皇后", "钱币国王"
    ]

    async def execute(self, args: CommandArgs) -> tuple[bool, str | None, bool]:
        """执行塔罗牌抽取"""
        try:
            # 获取抽取数量
            num_str = args.get_raw()
            if num_str:
                try:
                    num_cards = int(num_str)
                except ValueError:
                    await self.send_text("❌ 请输入有效的数字")
                    return True, "数字无效", True
            else:
                num_cards = 1  # 默认抽1张

            # 验证数量
            max_cards = 10  # 最大抽取数量
            if num_cards < 1:
                await self.send_text("❌ 至少要抽取 1 张牌")
                return True, "数量过少", True
            if num_cards > max_cards:
                await self.send_text(f"❌ 最多抽取 {max_cards} 张牌")
                return True, "数量过多", True

            # 随机抽取塔罗牌
            drawn_cards = random.sample(self.TAROT_CARDS, num_cards)

            # 随机决定正位/逆位
            positions = ["正位", "逆位"]
            results = [(card, random.choice(positions)) for card in drawn_cards]

            # 格式化输出
            output = f"🔮 赛博塔罗牌占卜\n\n抽取了 {num_cards} 张牌：\n\n"

            for i, (card, pos) in enumerate(results, 1):
                # 根据正逆位选择不同的图标
                icon = "🌟" if pos == "正位" else "🌙"
                output += f"{icon} 第 {i} 张：{card}（{pos}）\n"

            await self.send_text(output)
            return True, "占卜成功", True

        except Exception as e:
            logger.error(f"塔罗牌占卜失败: {e}", exc_info=True)
            await self.send_text(f"❌ 占卜失败: {str(e)}")
            return True, f"失败: {e}", True


@register_plugin
class DiceAndTarotPlugin(BasePlugin):
    """骰子与塔罗牌插件"""

    plugin_name: str = "dice_and_tarot"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"

    # 配置Schema定义
    config_schema: dict = {
        "plugin": {
            "name": ConfigField(type=str, default="dice_and_tarot", description="插件名称"),
            "description": ConfigField(type=str, default="骰子与塔罗牌插件", description="插件描述"),
            "version": ConfigField(type=str, default="1.0.0", description="插件版本"),
            "author": ConfigField(type=str, default="MoFox Community", description="插件作者"),
        }
    }

    def get_plugin_components(self) -> List[tuple[PlusCommandInfo, type[PlusCommand]]]:
        """注册插件组件"""
        return [
            (DiceCommand.get_plus_command_info(), DiceCommand),
            (TarotCommand.get_plus_command_info(), TarotCommand),
        ]

    async def on_enable(self):
        """插件启用时的回调"""
        logger.info("🎲 骰子与塔罗牌插件已启用")
        logger.info("命令：/roll <骰子表达式>  |  /tarot [数量]")

    async def on_disable(self):
        """插件禁用时的回调"""
        logger.info("骰子与塔罗牌插件已禁用")
