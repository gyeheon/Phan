import discord
from discord.ext import commands
from discord.utils import get
import json

from requests import options

def load_storage():
    with open('liar_storage.json') as data:
        return json.load(data)

def dump_storage(storage):
    with open('liar_storage.json', 'w') as data:
        json.dump(storage, data)
        return

class liar_cogv2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.main_embed = discord.Embed(title = '**라이어 게임**', description = '시작하려면 채팅에 "start" 또는 "시작"이라고 쳐 주세요', color = 0xffffff)
        self.player_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '참여하고자 하는 사람은 이 채널에 아무 채팅이나 쳐 주세요', color = 0xf7ff00)
        self.liar_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '지정할 라이어의 수를 채팅에 쳐 주세요', color = 0xf7ff00)
        self.category_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '아래의 카테고리 중 하나를 골라 채팅에 쳐 주세요', color = 0xf7ff00)
        
        self.main_msg = ''
        self.player_msg = ''
        self.liar_msg = ''
        self.category_msg = ''

        self.channel = ''
        self.is_playing = False
        self.starter = 0

        self.storage = load_storage()

    @commands.command(name = 'setup', help = '이 커맨드를 실행하면 이 커맨드를 실행한 채널을 라이어 게임 전용 채널로 지정합니다.')
    async def setup(self, ctx):
        await ctx.message.delete()
        

        self.channel = ctx.channel
        self.storage['options']['channel_id'] = self.channel.id
        self.main_msg = await ctx.send(embed = self.main_embed)
        self.storage['options']['main_message_id'] = self.main_msg.id
        dump_storage(self.storage)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.storage['options']['channel_id']:
            self.channel = await self.bot.fetch_channel(self.storage['options']['channel_id'])


        if message.content.lower() in ['start', '시작'] and message.channel == self.channel and self.is_playing == False:   #To start the game
            self.is_playing = True
            self.starter = message.author

            main_msg = await self.channel.fetch_message(self.storage['options']['main_message_id'])
            await main_msg.delete()

            await message.delete()
            await self.player_apply()

        
        
            
    
    async def send_player_msg(self):
        return await self.channel.send(embed = self.player_embed)
        
    async def send_liar_msg(self):
        return await self.channel.send(embed = self.liar_embed)

    async def send_category_msg(self):
        return await self.channel.send(embed = self.category_embed)

    #Get the options of the game
    async def player_apply(self):
        self.player_msg = await self.send_player_msg()
        await self.player_msg.add_reaction('✅')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.message_id == self.player_msg.id and payload.user.id == self.starter.id:
            await self.player_msg.delete()
            self.liar_msg = await self.send_liar_msg()
    

    

