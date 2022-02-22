import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command(name='ping')
async def ping_(ctx):
    await ctx.reply('pong!')

@bot.command(name='muteall')
async def muteall_(ctx):
    channel = ctx.author.voice.channel
    members = channel.members
    for i in members:
        await i.edit(mute=True)

@bot.command(name='unmuteall')
async def muteall_(ctx):
    channel = ctx.author.voice.channel
    members = channel.members
    for i in members:
        await i.edit(mute=False)

@bot.event
async def on_voice_state_update(Member, before, after):
    if before.channel == None and after.channel != None:
        print('a')
        await Member.edit(mute=False)







with open('token.txt', 'r') as f:
    token = f.readline()

bot.run(token)
