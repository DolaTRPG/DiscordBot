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


"""
@client.event
async def on_message(message):
    if message.content == "開團":
        await games.create(client, message, game_channel_id)
"""


bot.run(token)
