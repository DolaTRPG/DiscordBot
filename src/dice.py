import random
import re

from discord.ext import commands


class Dice(commands.Cog, name="骰子功能"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, *args):
        """擲骰子

        範例：
        roll 3d6
        roll 3d6+10 測試骰"""
        try:
            dice_string = args[0]
            dice_comment = " ".join(args[1:])
            (total, rolls, modifier) = self._roll(dice_string)
            response = "roll {}".format(dice_string)
            if dice_comment:
                response += " ({})".format(dice_comment)
            response += "\n{} + ({}) = {}".format(rolls, int(modifier), total)
        except:
            response = "指令錯誤：\n使用範例：roll 3d6+10 測試骰"
        await ctx.send(response)

    def _roll(self, roll_string):
        """roll dice
        Args:
            (str) dice_string (example: "1d20+4")
        Return:
            (tuple)
                - (int) sum - final result of rolls and modifier
                - (list of int) rolls - dice roll results
                - (str) modifier - parsed modifier
        """
        matched_groups = re.match("(\d+)d(\d+)([\+|\-]\d+)?", roll_string)
        dice_count = matched_groups.groups()[0]
        dice_type = matched_groups.groups()[1]
        dice_modifier = matched_groups.groups('+0')[2]  # use "+0" in default if not matched
        dice_results = []
        for _ in range(int(dice_count)):
            dice_results.append(random.randint(1, int(dice_type)))
        dice_sum = sum(dice_results) + int(dice_modifier)
        return (dice_sum, dice_results, dice_modifier)
