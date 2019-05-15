import asyncio
import re


async def create(client, message, game_channel_id):
    """create new game on discord
    Args:
        (discord.client) client - discord client
        (discord.message) message - discord message
        (int) game_channel_id - discord channel for announcemnet
    """
    dm_channel = message.channel

    def check_message(m):
        return m.author == message.author and m.channel == dm_channel

    game = {}
    await dm_channel.send("請輸入跑團時間：")
    message = await client.wait_for('message', check=check_message)
    game["time"] = message.content

    await dm_channel.send("請輸入劇本名稱：")
    message = await client.wait_for('message', check=check_message)
    game["name"] = message.content

    await dm_channel.send("請輸入玩家人數：")
    message = await client.wait_for('message', check=check_message)
    game["player_count"] = message.content
    try:
        assert(int(game["player_count"]) > 0)
    except:
        await dm_channel.send("玩家人數必須是正整數")
        await dm_channel.send("已取消")
        return

    await dm_channel.send("請輸入團務長度：")
    message = await client.wait_for('message', check=check_message)
    game["length"] = message.content

    await dm_channel.send("請輸入簡介：")
    message = await client.wait_for('message', check=check_message)
    game["description"] = message.content

    await dm_channel.send("請輸入點數需求：")
    message = await client.wait_for('message', check=check_message)
    game["point"] = message.content
    try:
        assert(int(game["point"]) >= 0)
    except:
        await dm_channel.send("點數需求必須 >= 0")
        await dm_channel.send("已取消")
        return

    final_message = """
{} 要開團囉!!
```
時間：{}
劇本：{}
人數：{}
長度：{}
簡介：
{}
```

想要參加的玩家請點 🆙（開團時酌收 {} 點跑團點數）
主持人收團請點 🈵
    """.format(message.author.mention, game['time'], game['name'], game['player_count'], game['length'], game['description'], game['point'])

    await dm_channel.send(final_message)
    await dm_channel.send("請確認以上訊息(y/n)：")
    message = await client.wait_for('message', check=check_message)
    if message.content not in ["y", "Y", "yes", "Yes", "YES"]:
        await dm_channel.send("已取消")
        return
    message = await client.get_channel(game_channel_id).send(final_message)
    emojis = ['🆙', '🈵']
    for emoji in emojis:
        await message.add_reaction(emoji)


async def start(client, message, users):
    """start game on discord
    Args:
        (discord.client) client - discord client
        (discord.message) message - discord message
        (users.Users) users - user class
    """
    if message.author != client.user:
        return
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
            elif reaction.emoji == '🈵':
                if user == gm:
                    start_flag = True
    players.remove(client.user)

    if start_flag:
        # filter player by gm setting
        game_title = parse_message(message.content, "劇本：(\w+)")
        game_points = int(parse_message(message.content, "開團時酌收 (\d+) 點跑團點數"))
        total_points = 0
        player_count = int(parse_message(message.content, "人數：(\d+)"))

        # sort player by points
        for p in players:
            if users.get(p)['points'] < game_points:
                await send_direct_message(p, "{} 的 {} 團報名截止，你因為點數不足而被移出玩家清單".format(gm.name, game_title))
        players = [p for p in players if users.get(p)['points'] > game_points]
        players = sorted(players, key=lambda p: users.get(p)['points'], reverse=True)
        players = players[:player_count]

        # check requirements
        if len(players) < player_count:
            await message.channel.send("{} 的 {} 團因為人數不足而流團".format(gm.mention, game_title))
            await message.edit(content=message.content + "\n（流團）")
            return

        # start successfully
        player_mentions = [p.mention for p in players]
        await message.channel.send("{} 的 {} 團已收團\n玩家：{}".format(gm.mention, game_title, " ".join(player_mentions)))

        # send dm to each players
        for p in players:
            await send_direct_message(p, "恭喜入選 {} 的 {} 團".format(gm.name, game_title))
            points_before = users.get(p)['points']
            users.increase_value(p, 'player', 1)
            users.increase_value(p, 'points_used', game_points)
            users.increase_value(p, 'points', 0 - game_points)
            points_after = users.get(p)['points']
            await send_direct_message(p, "點數：{} -> {}".format(points_before, points_after))
            total_points += game_points

        # send dm to gm
        await send_direct_message(gm, "開團成功，玩家：{}".format(",".join([p.name for p in players])))
        points_before = users.get(gm)['points']
        users.increase_value(gm, 'gm', 1)
        users.increase_value(gm, 'points_earned', game_points)
        users.increase_value(gm, 'points', game_points)
        points_after = users.get(gm)['points']
        await send_direct_message(gm, "點數：{} -> {}".format(points_before, points_after))
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
