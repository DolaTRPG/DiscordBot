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
            response = "{}\nroll {}".format(ctx.author.mention, dice_string)
            if dice_comment:
                response += "\n{}".format(dice_comment)
            response += "\n{} + ({}) = {}".format(rolls, int(modifier), total)
        except:
            response = "指令錯誤：\n使用範例：roll 3d6+10 測試骰"
        await ctx.send(response)

    @commands.command()
    async def coc(self, ctx, *args):
        """coc 技能判定

        範例：
        coc 50
        coc 50 聆聽"""
        try:
            dc = int(args[0])
            comment = " ".join(args[1:])
            (total, rolls, modifier) = self._roll("1d100")
            if total <= 2:
                result = "大成功"
            elif total >= 99:
                result = "大失敗"
            elif total <= dc:
                result = "成功"
            else:
                result = "失敗"
            response = "{}\n{} (目標值：{}，擲骰結果：{})".format(ctx.author.mention, result, dc, total)
            if comment:
                response += "\n{}".format(comment)
        except:
            response = "{}\n指令錯誤：\n使用範例：coc 50"
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
