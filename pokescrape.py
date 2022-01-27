import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix = '.')

# STARTUP ACTIONS
# --------------------------------------------------------------------------- #
# Ensure bot is running
@client.event
async def on_ready():
    print("Main-Bot is online.")

# On startup, load in all cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
# --------------------------------------------------------------------------- #

# HELPER COMMANDS
# --------------------------------------------------------------------------- #
# Load a cog
@client.command()
@commands.is_owner()
async def load(ctx, ext):
    client.load_extension(f'cogs.{ext}')
    await ctx.send(f"{ext}.py loaded.")

# Unload a cog
@client.command()
@commands.is_owner()
async def unload(ctx, ext):
    client.unload_extension(f'cogs.{ext}')
    await ctx.send(f"{ext}.py unloaded.")

# Reload a cog (updates any additions)
@client.command()
@commands.is_owner()
async def reload(ctx, ext):
    client.unload_extension(f'cogs.{ext}')
    client.load_extension(f'cogs.{ext}')
    await ctx.send(f"{ext}.py reloaded.")

# Shutdown bot
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down bot...")
    await client.close()
# --------------------------------------------------------------------------- #

# Run bot
client.run('OTI5NzgzMjE4MjYwMDQ1ODg1.YdsWGQ.MeBSXZsJevEQiC7IUW0PR9zNwx8')
