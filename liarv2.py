import discord
from discord.ext import commands
from discord.utils import get
import json
import random
from datetime import datetime

def load_storage():
    with open('liar_storage.json') as data:
        return json.load(data)

def dump_storage(storage):
    with open('liar_storage.json', 'w') as data:
        json.dump(storage, data)
        return

def load_word():
    with open('liar_word.json', encoding='UTF8') as data:
        return json.load(data)

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
        self.starter = 0
        self.liar_cnt = 1
        self.category = ''
        self.players = []

        self.step = 0

        self.storage = load_storage()
        self.word = load_word()

    @commands.command(name = 'setup', help = '이 커맨드를 실행하면 이 커맨드를 실행한 채널을 라이어 게임 전용 채널로 지정합니다.')
    async def setup(self, ctx):
        await ctx.message.delete()

        self.step = 0
        self.channel = ctx.channel
        self.storage['options']['channel_id'] = self.channel.id
        self.main_msg = await ctx.send(embed = self.main_embed)
        self.storage['options']['main_message_id'] = self.main_msg.id
        dump_storage(self.storage)

    

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

#========================================================================================================================================================

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.storage['options']['channel_id']:
            self.channel = await self.bot.fetch_channel(self.storage['options']['channel_id'])

        if (message.channel == self.channel) and (self.step == 1) and message.author.bot == False:
            if message.author not in self.players:
                self.players.append(message.author)
            await message.delete()

        if (message.content.lower() in ['start', '시작']) and (message.channel == self.channel) and (self.step == 0):   #To start the game
            self.step = 1
            self.starter = message.author

            main_msg = await self.channel.fetch_message(self.storage['options']['main_message_id'])
            await main_msg.delete()

            await message.delete()
            await self.player_apply()

        if message.content.isnumeric() and message.author.id == self.starter.id and message.channel == self.channel and self.step == 2:
            self.step = 3
            self.liar_cnt = int(message.content)
            await self.liar_msg.delete()
            await message.delete()
            self.category_msg = await self.send_category_msg()
        
        if message.content in self.word.keys() and self.step == 3 and message.author.id == self.starter.id and message.channel == self.channel:
            self.step = 4
            self.category = message.content
            await self.liar_start()
            await self.category_msg.delete()

    async def liar_start(self):
        
        if self.liar_cnt > len(self.players):
            await self.channel.send("라이어 수가 플레이어 수보다 많을 수 없습니다.")
        
        
        player_names = []
        for i in self.players:
            player_names.append(i.name)
        
        liar_players = []
        for i in range(self.liar_cnt):
            liar_player = self.players.pop(random.randint(0, len(self.players) - 1))
            liar_players.append(liar_player.name)
            await liar_player.send(f"당신은 라이어 입니다. `테마:{self.category}`")
        word = random.choice(self.word[self.category])
        for i in self.players:
            await i.send(f"{word} `테마:{self.category}`")
        
        log_channel = await self.bot.fetch_channel(947175802582224896)
        await log_channel.send(f"```{datetime.now()} \n참여자: {player_names} \n라이어: {liar_players} \n제시어: {word}```")
        
        random.shuffle(player_names)
        for i in player_names:
            temp = temp +  i+" -> "
        await self.channel.send("[라이어게임] 게임이 시작되었습니다. 개인메세지를 확인해주세요.\n`순서: {temp}`")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.message_id == self.player_msg.id and payload.user_id == self.starter.id and self.step == 1:
            self.step = 2
            await self.player_msg.delete()
            self.liar_msg = await self.send_liar_msg()
        


    

    

