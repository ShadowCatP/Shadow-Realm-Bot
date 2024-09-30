import discord


async def check_channel(ctx, command_channel_name: str):
    command_channel = discord.utils.get(ctx.guild.text_channels, name=command_channel_name)

    if ctx.channel.name != command_channel.name:
        await ctx.respond(f"I hear commands only from {command_channel.mention}")
        return False
    return True