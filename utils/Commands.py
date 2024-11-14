import discord
from discord.ext import commands
from utils.CheckChannel import check_channel
from utils.RenameUser import rename_user
from utils.TrackUser import monitor_user
import datetime

# Constants
COMMAND_CHANNEL_NAME = "shadow-realm-commands"
SHADOW_LEVELS = ["Shadow Realm", "Shadower Realm", "The Shadowest Realm"]

# Global State
monitoring_tasks = {}
original_nicknames = {}
user_shadow_levels = {}
user_channels = {}
white_list = {0, 502839436619546627}


def register_commands(bot: commands.Bot):
    @bot.command()
    async def shadow_realm(ctx, user: discord.Option(discord.Member), time_sec: discord.Option(int) = 1):
        """A nice way to send user to a shadow realm"""

        # Check if the command is from the command channel
        if not await check_channel(ctx, COMMAND_CHANNEL_NAME):
            return

        if user.id in white_list:
            await handle_exempt_user(ctx)
            return

        current_channel = user.voice.channel if user.voice else None
        current_level = user_shadow_levels.get(user.id, 0)

        if current_level >= len(SHADOW_LEVELS):
            return

        channel_name = SHADOW_LEVELS[current_level]
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        if user.id in monitoring_tasks:
            current_level += 1
            if current_level >= len(SHADOW_LEVELS):
                await ctx.respond("This user is already in the deepest **Shadow Realm**")
                return

            channel_name = SHADOW_LEVELS[current_level]
            channel = discord.utils.get(ctx.guild.voice_channels,
                                        name=channel_name) or await ctx.guild.create_voice_channel(channel_name)

        if user.id not in original_nicknames:
            original_nicknames[user.id] = user.nick

        user_shadow_levels[user.id] = current_level
        user_channels[user.id] = channel

        if user.id in monitoring_tasks:
            monitoring_tasks[user.id].cancel()

        task = bot.loop.create_task(
            monitor_user(user, time_sec, ctx, user_shadow_levels, user_channels, current_channel))
        monitoring_tasks[user.id] = task

        # Send response
        await ctx.respond(f"Sent {user.mention} to the **{channel_name}** for {datetime.timedelta(seconds=time_sec)}")
        print(f'Sending {user} to {channel} for {time_sec}')

    @bot.command(name="remove")
    async def remove_shadow_realm(ctx, user: discord.Option(discord.Member)):
        """Remove user from the shadow realm"""

        if not await check_channel(ctx, COMMAND_CHANNEL_NAME):
            return

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

    async def handle_exempt_user(ctx: commands.Context):
        await ctx.respond("Good try kid 😈")
        if ctx.author.id != 502839436619546627:
            await rename_user(ctx.author, "The Foul")
