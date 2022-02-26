import discord
from discord.ext import commands
import random
import json
from datetime import datetime

class liar_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def load_storage(self):
        with open('liar.json', encoding='UTF8') as data:
            return json.load(data)

    @commands.has_permissions(administrator=True)
    @commands.command(name='liar_start', help='$liar_start [카테고리] [라이어 수] [플레이어1] [플레이어2] [플레이어n]')
    async def liar_start_(self, ctx, category, liar_cnt: int, *player: discord.Member):
        
        if liar_cnt > len(player):
            await ctx.reply("라이어 수가 플레이어 수보다 많을 수 없습니다.")

        player_list = list(player)

        log_channel = await self.bot.fetch_channel(947175802582224896)
        player_a = []

        for i in player_list:
            player_a.append(i.name)
        
        liar_players = []
        for i in range(liar_cnt):
            liar_player = player_list.pop(random.randint(0, len(player_list) - 1))
            liar_players.append(liar_player.name)
            await liar_player.send(f"당신은 라이어 입니다. `테마:{category}`")
        category_dic = self.load_storage()
        word = random.choice(category_dic[category])
        for i in player_list:
            await i.send(f"{word} `테마:{category}`")

        await log_channel.send(f"```{datetime.now()} \n참여자: {player_a} \n라이어: {liar_players} \n제시어: {word}```")
        await ctx.reply("[라이어게임] 게임이 시작되었습니다. 개인메세지를 확인해주세요. ")