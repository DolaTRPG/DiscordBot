import asyncio
import re

import configurations

import db_user
from discord.ext import commands
import util


class Games(commands.Cog, name="開團功能"):
    def __init__(self, bot):
        self.bot = bot
        self._announcement_channel = int(configurations.key['game_announce_channel'])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event):
        if event.channel_id == self._announcement_channel:
            message = await self.bot.get_channel(event.channel_id).fetch_message(event.message_id)
            if event.user_id == message.mentions[0].id:
                # trigger only if gm click on reaction
                await util.log(self.bot, "GM({}) 點了開團公告".format(message.mentions[0].mention))
                await self.start(message)

    @commands.command()
    async def create(self, ctx, *args):
        """發起新的團務

        使用方式：
        create <團名> <跑團收取點數(每人)> "<跑團須知>"

        範例：
        create 測試用的團 10
        "
        這是跑團須知的第一行
        這是第二行
        "
        """

        content = args[2]
        template = "{} 要開團囉({})!!\n{}\n想要參加的玩家請點 🆙（開團時酌收 {} 點跑團點數）\n主持人收團請點選玩家人數(1~6)".format(ctx.author.mention, args[0], content, args[1])

        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        await ctx.author.send(template)
        await ctx.author.send("請確認以上訊息(y/n)：")
        message = await self.bot.wait_for('message', check=check_message)
        if message.content not in ["y", "Y", "yes", "Yes", "YES"]:
            await ctx.author.send("已取消")
            return
        message = await self.bot.get_channel(self._announcement_channel).send(template)
        emojis = ['🆙', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣']
        for emoji in emojis:
            await message.add_reaction(emoji)

    async def start(self, message):
        if message.edited_at is not None:
            # take no action for edited message
            return
        gm = message.mentions[0]
        start_flag = False

        # collect player list
        players = []
        for reaction in message.reactions:
            async for user in reaction.users():
                if reaction.emoji == '🆙':
                    players.append(user)
                elif reaction.emoji in ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣']:
                    if user.id != gm.id:
                        # ignore non-gm reactions
                        continue
                    start_flag = True
                    if reaction.emoji == '1⃣':
                        player_count = 1
                    elif reaction.emoji == '2⃣':
                        player_count = 2
                    elif reaction.emoji == '3⃣':
                        player_count = 3
                    elif reaction.emoji == '4⃣':
                        player_count = 4
                    elif reaction.emoji == '5⃣':
                        player_count = 5
                    elif reaction.emoji == '6⃣':
                        player_count = 6
        players.remove(self.bot.user)  # remove bot user

        if start_flag:
            await util.log(self.bot, "正在開團({})".format(message.id))
            # filter player by gm setting
            game_point = int(parse_message(message.content, "開團時酌收 (\d+) 點跑團點數"))
            game_title = parse_message(message.content, " 要開團囉\((.*)\)!!\n")
            await util.log(self.bot, "團名：{}, 點數：{}".format(game_title, game_point))
            await util.log(self.bot, "團名：{}, 報名者：{}".format(game_title, [p.mention for p in players]))

            # valid player by points
            valid_players = db_user.get_game_players(ids=[p.id for p in players], required_points=game_point, player_count=player_count)
            valid_player_ids = [p.id for p in valid_players]
            players = [p for p in players if p.id in valid_player_ids]

            # verify number of players
            await util.log(self.bot, "團名：{}, 目標人數：{}, 成團玩家：{}".format(game_title, player_count, [p.mention for p in players]))
            if len(players) < player_count:
                await message.channel.send("{} 的 {} 因為人數不足而流團".format(gm.mention, game_title))
                await message.edit(content=message.content + "\n（流團）")
                return

            # start successfully
            player_mentions = [du.mention for du in players]
            await message.channel.send("{} 的 {} 已收團\n玩家：{}".format(gm.mention, game_title, " ".join(player_mentions)))

            # send dm to players
            for du in players:
                user = db_user.get(du.id)
                db_user.update(du.id, point=user.point - game_point, use=user.use + game_point)
                await send_direct_message(du, "恭喜入選 {} 的 {} ".format(gm.name, game_title))
                await send_direct_message(du, "使用點數 {}，剩餘點數：{}".format(game_point, user.point - game_point))

            # send dm to gm
            user = db_user.get(gm.id)
            total_point = int(game_point) * len(players)
            db_user.update(gm.id, point=user.point + total_point, earn=user.earn + total_point)
            await send_direct_message(gm, "開團成功，玩家：{}".format(",".join([p.name for p in players])))
            await send_direct_message(gm, "獲得點數 {}，合計點數：{}".format(total_point, user.point + total_point))

            # edit original message
            await message.edit(content=message.content + "\n（已收團）")
            users.write()


def parse_message(content, pattern):
    matched = re.findall(pattern, content)
    if not matched:
        return None
    return matched[0]


async def send_direct_message(discord_user, message):
    """send direct message to user
    Args:
        - (discord user) discord_user
        - (str) message
    """
    try:
        if not discord_user.dm_channel:
            await discord_user.create_dm()
        await discord_user.dm_channel.send(message)
    except:
        return
