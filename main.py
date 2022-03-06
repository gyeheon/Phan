from random import random
import discord
from discord.ext import commands
import random
import asyncio

class main_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tr = 0
        with open('num.txt', 'r') as f:
            self.num = f.readline()

    def reset(self):
        string = "0123456789"
        result = ''
        self.tr = 0
        for i in range(4):
            result += random.choice(string)
        with open('num.txt', 'w') as f:
            f.write(result)
            self.num = result


    @commands.Cog.listener()
    async def on_ready(self):
        print('bot is ready')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 949698886128271450 and message.author.bot == False:
            self.tr += 1
            if message.content.isnumeric() and message.content == self.num:
                await message.reply("빙고! 숫자가 바뀌었습니다.")
                self.reset()
            else:
                await message.delete()
                await message.channel.edit(name='숫자맞추기 시도횟수:'+str(self.tr))
                
    
    @commands.command(name='clear')
    async def clear_(self, ctx, n: int):
        await ctx.channel.purge(limit=n)

    @commands.command()
    async def vccd(self, ctx):
        for i in range(10):
            await ctx.author.voice.channel.connect()
            await asyncio.sleep(1)
            await ctx.voice_client.disconnect()
            await asyncio.sleep(1)