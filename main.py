import os

import dotenv
import discord
from discord.ext import commands
from utils.TrackUser import monitor_user, rename_user
import datetime

dotenv.load_dotenv()
token = str(os.getenv('TOKEN'))

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

monitoring_tasks = {}
original_nicknames = {}
user_shadow_levels = {}
user_channels = {}
command_channel_name = "shadow-realm-commands"
shadow_levels = ["Shadow Realm", "Shadower Realm", "The Shadowest Realm"]


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for guild in bot.guilds:
        for level in shadow_levels:
            channel = discord.utils.get(guild.voice_channels, name=level)
            if channel is None:
                await guild.create_voice_channel(level)

        command_channel = discord.utils.get(guild.text_channels, name=command_channel_name)
        if command_channel is None:
            command_channel = await guild.create_text_channel(command_channel_name)

        await command_channel.set_permissions(guild.default_role, read_messages=True, send_messages=True)
        await command_channel.set_permissions(bot.user, read_messages=True, send_messages=True, manage_messages=True)

        print(f"Command channel is set to {command_channel.name} in guild {guild.name}")


@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def shadow_realm(ctx, user: discord.Member, time_sec: int = 1):
    """A nice way to send user to a shadow realm"""

    current_channel = user.voice.channel if user.voice else None

    current_level = user_shadow_levels.get(user.id, 0)
    if current_level >= len(shadow_levels):
        return

    channel_name = shadow_levels[current_level]
    channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

    if user.id in monitoring_tasks:
        current_level += 1
        if current_level >= len(shadow_levels):
            await ctx.respond("This user is already in the deepest **Shadow Realm**")
            return

        channel_name = shadow_levels[current_level]
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

    if channel is None:
        channel = await ctx.guild.create_voice_channel(channel_name)

    if user.id == bot.user.id or user.id == 502839436619546627:
        await ctx.respond("Good try kid 😈")
        await rename_user(ctx.author, "The Foul")
        return

    try:
        await user.move_to(channel)
        await ctx.respond(
            f"Sent {user.mention} to the **{channel_name}** for {datetime.timedelta(seconds=time_sec)}")
        print(f'Sending {user} to {channel} for {time_sec}')
    except discord.HTTPException or discord.Forbidden:
        await ctx.respond("My power is not absolute...")
        return

    if user.id not in original_nicknames:
        original_nicknames[user.id] = user.nick

    user_shadow_levels[user.id] = current_level
    user_channels[user.id] = channel

    if user.id in monitoring_tasks:
        monitoring_tasks[user.id].cancel()

    task = bot.loop.create_task(monitor_user(user, time_sec, ctx, user_shadow_levels, user_channels, current_channel))
    monitoring_tasks[user.id] = task


@bot.command(name="remove")
@commands.has_permissions(manage_nicknames=True)
async def remove_shadow_realm(ctx, user: discord.Member):
    """Remove user from the shadow realm"""

    if ctx.author.id == user.id:
        await ctx.respond("https://tenor.com/view/nuh-uh-beocord-no-lol-gif-24435520")
        return

    task = monitoring_tasks.get(user.id)
    if task:
        task.cancel()
        del monitoring_tasks[user.id]

        original_nick = original_nicknames.pop(user.id, None)
        if original_nick:
            await rename_user(user, original_nick)

        await ctx.respond(f"{user.mention} You have been spared! Be thankful to {ctx.author.mention}!")
    else:
        await ctx.respond("This user is not in the **Shadow Realm**")

    user_shadow_levels.pop(user.id, None)
    user_channels.pop(user.id, None)


bot.run(token)
