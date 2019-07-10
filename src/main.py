import asyncio
import discord
from discord.ext import commands
import os
import json

import channel
import configurations
import dice
import users
import games

token = os.environ['discord_token']
google_spreadsheet_key = os.environ['google_spreadsheet_key']
configurations.init(google_spreadsheet_key)

bot = commands.Bot(
    command_prefix=".",
    description="DolaTRPG discord bot",
    self_bot=False,
    owner_id=int(configurations.key['owner'])
)

bot.add_cog(users.Users(bot, google_spreadsheet_key))
bot.add_cog(channel.Channel(bot))
bot.add_cog(games.Games(bot))
bot.add_cog(dice.Dice(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name='.help'))


bot.run(token)
