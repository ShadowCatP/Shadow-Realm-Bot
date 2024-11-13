import os

import dotenv
import discord
from discord.ext import commands
import datetime
from utils.Commands import register_commands, white_list, SHADOW_LEVELS, COMMAND_CHANNEL_NAME

dotenv.load_dotenv()
token = str(os.getenv('TOKEN'))

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
register_commands(bot)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    if bot.user:
        white_list.add(bot.user.id)
    for guild in bot.guilds:
        await setup_guild_channels(guild)


async def setup_guild_channels(guild: discord.Guild):
    for level in SHADOW_LEVELS:
        channel = discord.utils.get(guild.voice_channels, name=level)
        if channel is None:
            await guild.create_voice_channel(level)

    command_channel = discord.utils.get(guild.text_channels, name=COMMAND_CHANNEL_NAME)
    if command_channel is None:
        command_channel = await guild.create_text_channel(COMMAND_CHANNEL_NAME)

    await command_channel.set_permissions(guild.default_role, read_messages=True, send_messages=True)
    await command_channel.set_permissions(guild.me, read_messages=True, send_messages=True, manage_messages=True)

    print(f"Command channel is set to {command_channel.name} in guild {guild.name}")


async def handle_exempt_user(ctx: commands.Context):
    await ctx.respond("Good try kid 😈")
    if ctx.author.id != 502839436619546627:
        await rename_user(ctx.author, "The Foul")


bot.run(token)
