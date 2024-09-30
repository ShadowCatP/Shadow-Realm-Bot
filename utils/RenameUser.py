import discord

async def rename_user(user: discord.Member, new_username: str):
    try:
        await user.edit(nick=new_username)
    except discord.Forbidden:
        print(f"Don't have permissions to change the username of {user} to {new_username}")