from re import S
import discord
from discord.ext import commands

class main_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.num = "0302"

    @commands.command(name='ping')
    async def ping_(self, ctx):
        await ctx.reply("pong!")

    @commands.Cog.listener()
    async def on_ready(self):
        print('bot is ready')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 949698886128271450 and message.author.bot == False:
            if message.content.isnumeric():
                if message.content == self.num:
                    await message.reply("빙고")
                else:
                    await message.reply("땡")
            elif message.author.id != 486859609781436447:
                await message.delete()