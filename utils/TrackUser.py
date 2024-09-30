import asyncio
import discord
from discord.ext import commands
from utils.RenameUser import rename_user


async def monitor_user(user: discord.Member, time_sec: int, ctx: commands.Context,
                       user_shadow_levels: dict, user_channels: dict, original_channel: discord.VoiceChannel):
    original_nick = user.nick
    await rename_user(user, "Wandering Soul")

    end_time = asyncio.get_event_loop().time() + time_sec
    while asyncio.get_event_loop().time() < end_time:
        current_channel = user_channels.get(user.id)
        if user.voice is None or user.voice.channel != current_channel:
            try:
                await user.move_to(current_channel)
                await ctx.send(
                    f"{user.mention}, you naughty child, you are not allowed to leave the **{current_channel.name}**")
            except discord.Forbidden:
                print("Don't have permission to move that user")
            except discord.HTTPException:
                pass
        await asyncio.sleep(1)

    await rename_user(user, original_nick)
    user_shadow_levels[user.id] = 0
    user_channels.pop(user.id, None)
    await user.move_to(original_channel)
