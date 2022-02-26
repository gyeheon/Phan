import discord
from discord.ext import commands

class main_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping_(self, ctx):
        await ctx.reply("pong!")