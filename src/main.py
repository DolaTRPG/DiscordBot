import asyncio
import discord
from discord.ext import commands
import os
import json

import dice
import users
import games

token = os.environ['discord_token']
google_spreadsheet_key = os.environ['google_spreadsheet_key']
game_server_id = int(os.environ['discord_server_id'])
game_channel_id = int(os.environ['discord_game_channel_id'])
newcomer_role_name = os.environ['discord_newcomer_role_name']

bot = commands.Bot(
    command_prefix=".",
    description="DolaTRPG discord bot",
    self_bot=False,
    owner_id=559563649841233951
)
busy_users = []

bot.add_cog(users.Users(bot, google_spreadsheet_key, game_server_id, newcomer_role_name))
bot.add_cog(dice.Dice(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name='.help'))


@bot.event
async def on_raw_reaction_add(event):
    if event.channel_id == game_channel_id:
        message = await client.get_channel(event.channel_id).fetch_message(event.message_id)
        await games.start(client, message, Users)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # reaction in direct message
    if is_channel_type(message.channel, "DMChannel"):
        # avoid additional actions if user is already busy
        if message.author in busy_users:
            return

        busy_users.append(message.author)

        elif message.content == "開團":
            await games.create(client, message, game_channel_id)

        # save current progress into storage
        elif message.content.startswith('!save'):
            await Users.write()
            await message.channel.send("更新完成")

        else:
            response = "請輸入對應的指令：\n"
            response += "`點數`：查看你的點數\n"
            response += "`開團`：登記團務，募集玩家\n"
            await message.channel.send(response)

        busy_users.remove(message.author)


def is_channel_type(channel, class_name):
    """check if channel is private
    Args:
        - (discord channel) channel class
        - (str) class_name - discord class name (e.g. DMChannel)
    """
    if channel.__class__.__name__ == class_name:
        return True
    return False


bot.run(token)
