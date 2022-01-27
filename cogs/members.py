import discord
from discord.ext import commands

# Handles operations related to server members
class Members(commands.Cog):

    # Initialize <Members> cog
    def __init__(self, client):
        self.client = client

    # Print confirmation that <Members> is active
    @commands.Cog.listener()
    async def on_ready(self):
        print('Members cog is online.')

# Connect cog to main-bot
def setup(client):
    client.add_cog(Members(client))
