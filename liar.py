from os import link
from unicodedata import name
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

class liar_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = load_storage()
        self.category_dic = load_word()

        self.main_embed = discord.Embed(title = '**라이어 게임**', description = '시작하려면 채팅에 "start" 또는 "시작"이라고 쳐 주세요', url = "https://gyeheon.github.io/liar_game/", color = 0xffffff)
        self.player_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '참여하고자 하는 사람은 이 채널에 아무 채팅이나 쳐 주세요', color = 0xf7ff00)
        self.liar_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '지정할 라이어의 수를 채팅에 쳐 주세요', color = 0xf7ff00)
        self.category_embed = discord.Embed(title = '**라이어 게임**을 시작하려고 합니다', description = '아래의 카테고리 중 하나를 골라 채팅에 쳐 주세요', color = 0xf7ff00)
        categories = ' '.join(self.category_dic.keys())
        self.category_embed.add_field(name = categories, value = '\0')
        self.playing_embed = discord.Embed(title = '**라이어 게임**을 실행중입니다', description = '순서에 맞게 발언 해주세요', color = 0x00ff00)
        
        
        self.main_msg = ''

        self.channel = ''
        self.starter = 0
        self.liar_cnt = 1
        self.category = ''
        self.players = []
        # self.liars = []

        self.step = 0
        self.regame = False
        self.two_player = False
        '''
        step 0: Waiting for [start]
        step 1: Get participants by chatting
        step 2: Get category
        step 3: Playing liar game
        step 4: Vote for liar
        step 5: Get vote results
        '''

    @commands.command(name = 'setup', help = '이 커맨드를 실행하면 이 커맨드를 실행한 채널을 라이어 게임 전용 채널로 지정합니다.')
    async def setup(self, ctx):
        await ctx.message.delete()
        self.step = 0

        self.channel = ctx.channel
        self.storage['options']['channel_id'] = self.channel.id
        await ctx.send("***다이렉트 메세지를 허용해주세요*** `[서버 이름 우측 화살표 -> 개인정보 보호 설정 -> 서버 멤버가 보내는 다이렉트 메세지 허용하기.]`")

        self.main_msg = await ctx.send(embed = self.main_embed)
        self.storage['options']['main_message_id'] = self.main_msg.id
        dump_storage(self.storage)

    async def get_main_msg(self):
        return await self.channel.fetch_message(self.storage['options']['main_message_id'])

    async def send_main_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.main_embed)

    async def send_player_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.player_embed)
        
    async def send_liar_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.liar_embed)

    async def send_category_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.category_embed)

    async def send_playing_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.playing_embed)

    async def send_vote_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.vote_embed)

    async def send_vote_end_msg(self):
        self.main_msg = await self.get_main_msg()
        return await self.main_msg.edit(embed = self.vote_end_embed)
    
    #Get the options of the game
    # async def player_apply(self):
    #     await self.send_player_msg()
    #     await self.player_msg.add_reaction('✅')

#========================================================================================================================================================

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.channel == '':
            if self.storage['options']['channel_id']:
                self.channel = await self.bot.fetch_channel(self.storage['options']['channel_id'])
                return

        if self.channel == message.channel and message.author.bot == False:
            
            if self.step == 0:
                if message.content.lower() in ['start', '시작']:
                    self.starter = message.author

                    self.step = 1
                    await self.send_player_msg()
                    await self.main_msg.add_reaction('✅')

            elif self.step == 1:
                if message.author.bot == False:
                    self.players.append(message.author)
                    if len(self.players) == 1:
                        original_message = message.author.name + '#' + message.author.discriminator
                        self.player_embed.add_field(name = original_message, value = '\0', inline = False)
                    else:       
                        original_message += '\n' + message.author.name + '#' + message.author.discriminator
                        self.player_embed.set_field_at(0, name = original_message, value = '\0', inline = False)
                    await self.send_player_msg()
            
            elif self.step == 2:
                if message.author == self.starter:
                    self.category = message.content
                    if self.regame == True:
                        self.step = 5
                        await self.send_vote_end_msg()
                        for emoji_name in ['restart', 'player', 'category', 'stop']:
                            emoji = discord.utils.get(message.guild.emojis, name = 'liar_' + emoji_name)
                            await self.main_msg.add_reaction(emoji)
                    else:
                        self.step = 3
                        await self.liar_start()

            elif self.step == 3:
                pass
            
            elif self.step == 4:
                if message.content.isnumeric() and int(message.content) <= len(self.players) and message.author in self.players:
                    self.player_dic[message.author][1] = int(message.content)
                    player_num = self.player_dic[message.author][0]
                    vote_num = self.player_dic[message.author][1]
                    self.vote_embed.set_field_at(player_num - 1, name = player_num, value = message.author.mention + ' ' + vote_num, inline = False)
                    await self.send_vote_msg()

            elif self.step == 5:
                pass
            

            await message.delete()

        #===========================================================================================
        
        '''
        if self.channel == '':
            if self.storage['options']['channel_id']:
                self.channel = await self.bot.fetch_channel(self.storage['options']['channel_id'])
                return
        if (message.channel == self.channel) and (self.step == 1) and message.author.bot == False: #Get participants
            if message.author not in self.players:
                self.players.append(message.author)
                self.player_embed.add_field(name = message.author.name + '#' + message.author.discriminator, value = '\0', inline = False)
                await self.main_msg.edit(embed = self.player_embed)
            await message.delete()
            return

        if (message.content.lower() in ['start', '시작']) and (message.channel == self.channel) and (self.step == 0):   #To start the game
            self.step = 1
            self.starter = message.author

            await self.send_player_msg()

            await message.delete()
            await self.main_msg.add_reaction('✅')
            return
        
        # if message.content.isnumeric() and message.author.id == self.starter.id and message.channel == self.channel and self.step == 2: #Get the number of liars
        #     self.liar_cnt = int(message.content)
        #     await message.delete()
        #     if self.liar_cnt > len(self.players):
        #         return await self.channel.send('라이어 수가 플레이어 수보다 많을 수 없습니다', delete_after = 2)
        #     self.step = 3
        #     await self.send_category_msg()
        # elif message.content.isnumeric() == False and self.step == 2 and message.channel == self.channel and message.author != self.bot.user:
        #     await message.delete()
        #     await self.channel.send('숫자를 입력해주세요', delete_after = 2)

        if self.step == 2 and message.author == self.starter and message.channel == self.channel: #Get the category
            if message.content not in self.category_dic.keys():
                return await message.delete() 
            self.category = message.content
            await message.delete()
            if self.regame == True:
                self.step = 6
                await self.send_vote_end_msg()
                for emoji_name in ['restart', 'player', 'category', 'stop']:
                    emoji = discord.utils.get(message.guild.emojis, name = 'liar_' + emoji_name)
                    await self.main_msg.add_reaction(emoji)
                return
            else:
                self.step = 4
                await self.liar_start()
                return
        elif self.step == 2 and message.channel == self.channel:
            await message.delete()
            return

        if self.step == 4 and message.channel == self.channel:
            await message.delete()
            return


        if self.step == 4 and message.channel == self.channel and message.content.isnumeric() and int(message.content) <= len(self.players) and message.author in self.players:
            self.player_dic[message.author][1] = int(message.content)
            await message.delete()
            vote_progress = 0
            for player in self.player_dic.keys():
                if self.player_dic[player] != 0:
                    index = self.player_index[player]
                    self.vote_embed.set_field_at(index, name = index + 1, value = player.mention + ' ' + str(self.player_dic[player]), inline = False)
                    vote_progress += 1
            self.vote_embed.set_footer(text = f'현재 {len(self.players)} 중 {vote_progress}명 투표함')
            await self.send_vote_msg()
            return
        elif self.step == 4 and message.channel == self.channel:
            await message.delete()
            return

        if self.step == 5 and message.channel == self.channel:
            await message.delete()
            return
        '''


    async def liar_start(self):
        self.liar = random.choice(self.players)
        await self.liar.send(f"`테마: {self.category}`\n**당신은 라이어입니다**")

        self.word = random.choice(self.category_dic[self.category])

        self.player_names = []
        self.player_dic = {}
        number = 0
        random.shuffle(self.players)
        for player in self.players:
            number += 1

            if player != self.liar:
                await player.send(f"`테마: {self.category}`\n**{self.word}**")
            self.playing_embed.add_field(name = number, value = player.mention, inline = False)
            self.player_dic[player] = [number, 0]
            self.player_names.append(player.name + '#' + player.discriminator)
        
        await self.send_playing_msg()
        await self.main_msg.add_reaction('🗳️')
        
        

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.storage['options']['test'] = payload.emoji.name
        dump_storage(self.storage)
        if payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 1:
            if len(self.players) <= 2:
                if self.two_player == False:
                    user = await self.bot.fetch_user(payload.user_id)
                    await self.main_msg.remove_reaction(payload.emoji, user)
                    return await self.channel.send('두 명 이하는 플레이할 수 없습니다', delete_after = 2)
                elif self.two_player == True:
                    pass
                
            await self.main_msg.clear_reactions()
            if self.regame == True:
                self.step = 6
                await self.send_vote_end_msg()
                guild = await self.bot.fetch_guild(payload.guild_id)
                for emoji_name in ['restart', 'player', 'category', 'stop']:
                    emoji = discord.utils.get(guild.emojis, name = 'liar_' + emoji_name)
                    await self.main_msg.add_reaction(emoji)
            else:
                self.step = 3
                await self.main_msg.clear_reactions()
                await self.send_category_msg()

        if payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 3:
            user = await self.bot.fetch_user(payload.user_id)
            await self.main_msg.clear_reactions()
            self.vote_embed = discord.Embed(title = '**라이어 게임**을 실행중입니다', description = '라이어인 것 같은 사람의 숫자를 채팅에 쳐주세요', color = 0x00ff00)
            number = 0
            for player in self.players:
                number += 1
                self.vote_embed.add_field(name = number, value = player.mention, inline = False)

            await self.send_vote_msg()
            await self.main_msg.add_reaction('✅')
            self.step = 5
            return


        if payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 4:
            highest_vote = 0
            voted_for_liar = []
            for num in range(len(self.players)):
                num += 1
                if list(self.player_dic.values()).count(num) > highest_vote:
                    voted_for_liar = []
                    voted_for_liar.append(self.number_dic[num])
                    highest_vote = list(self.player_dic.values()).count(num)
                elif list(self.player_dic.values()).count(num) == highest_vote:
                    voted_for_liar.append(self.number_dic[num])

            self.step = 6
            self.regame = True
            if len(voted_for_liar) >= 2:
                voted_for_liar = ', '.join(voted_for_liar)
            else:
                voted_for_liar = voted_for_liar[0]
            self.vote_end_embed = discord.Embed(title = '**라이어 게임**이 끝났습니다', description = f'{voted_for_liar}가 라이어로 지목되었습니다', color = 0xffffff)
            await self.send_vote_end_msg()
            await self.main_msg.clear_reactions()
            guild = await self.bot.fetch_guild(payload.guild_id)
            for emoji_name in ['restart', 'player', 'category', 'stop']:
                emoji = discord.utils.get(guild.emojis, name = 'liar_' + emoji_name)
                await self.main_msg.add_reaction(emoji)
            
            
            log_channel = await self.bot.fetch_channel(947175802582224896)
            await log_channel.send(f"```{datetime.now()} \n참여자: {self.player_names} \n라이어: {self.liar} \n테마: {self.category} \n제시어: {self.word}```")
        
        if payload.emoji.name == 'liar_restart' and payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 5:
            self.step = 4
            await self.main_msg.clear_reactions()
            self.playing_embed.clear_fields()
            self.vote_embed.clear_fields()
            
            await self.liar_start()

        if payload.emoji.name == 'liar_player' and payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 5:
            self.step = 1
            await self.main_msg.clear_reactions()
            self.players = []
            self.player_embed.clear_fields()
            
            await self.send_player_msg()
            await self.main_msg.add_reaction('✅')

        if payload.emoji.name == 'liar_category' and payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 5:
            self.step = 3
            await self.main_msg.clear_reactions()
            await self.send_category_msg()

        if payload.emoji.name == 'liar_stop' and payload.message_id == self.main_msg.id and payload.user_id == self.starter.id and self.step == 5:
            self.step = 0
            self.regame = False
            self.players = []
            self.player_embed.clear_fields()
            self.playing_embed.clear_fields()
            await self.send_main_msg()
            await self.main_msg.clear_reactions()

    @commands.command()
    async def cc(self, ctx):
        # print('self.step:', self.step)
        # print('self.players:', self.players)
        # print(ctx.guild.emojis)
        print('🔄')
    
    @commands.command(name='two_player')
    async def two_player_(self, ctx):
        if ctx.channel == self.channel:
            await ctx.message.delete()
            if self.two_player == False:
                self.two_player = True
                await ctx.send('Two Player is now *TRUE*', delete_after = 2)
            else:
                self.two_player = False
                await ctx.send('Two Player is now *FALSE*', delete_after = 2)
        else:
            await ctx.send(f'{self.channel.mention}으로 가주세요')

    @commands.command(name = 'quick_join', help = '게임을 참가합니다 (게임이 끝났을 때만 사용 가능')
    async def quick_join_(self, ctx):
        await ctx.message.delete()
        if ctx.channel == self.channel:
            if self.step == 5:
                self.players.append(ctx.author)
                await ctx.send(f'{ctx.author.mention}이 참가했습니다')
            else:
                await ctx.send('현재 진행중인 게임이 끝난 후 다시 시도해주세요', delete_after = 2)
        else:
            await ctx.send(f'{self.channel.mention}으로 가주세요')

    @commands.command(name = 'add_player', help = '플레이어 한 명을 참가시킵니다 (게임이 끝났을 때만 사용 가능)')
    async def add_player_(self, ctx, player_id):
        await ctx.message.delete()
        if ctx.channel == self.channel:
            if self.step == 5:
                player = await self.bot.fetch_user(player_id)
                self.player.append(player)
                await ctx.send(f'{player.mention}을 게임에 참가시켰습니다', delete_after = 2)
            else:
                await ctx.send('현재 진행중인 게임이 끝난 후 다시 시도해주세요', delete_after = 2)
        else:
            await ctx.send(f'{self.channel.mention}으로 가주세요')            

    @commands.command(name = 'remove_player', help = '플레이어 한 명을 강퇴합니다 (게임이 끝났을 때만 사용 가능)')
    async def remove_player_(self, ctx, player_id):
        await ctx.message.delete()
        if ctx.channel == self.channel:
            if self.step == 5:
                player = await self.bot.fetch_user(player_id)
                self.player.remove(player)
                await ctx.send(f'{player.mention}을 게임에서 제외했습니다.', delete_after = 2)
            else:
                await ctx.send('현재 진행중인 게임이 끝난 후 다시 시도해주세요', delete_after = 2)
        else:
            await ctx.send(f'{self.channel.mention}으로 가주세요')

    
    @commands.command(name = 'force_stop', help = '게임을 강제로 종료합니다')
    async def force_stop_(self, ctx):
        await ctx.message.delete()
        if ctx.channel == self.channel:
            self.step = 0
            self.regame = False
            self.players = []
            self.player_embed.clear_fields()
            self.playing_embed.clear_fields()
            await self.send_main_msg()
            await self.main_msg.clear_reactions()
        else:
            await ctx.send(f'{self.channel.mention}으로 가주세요')