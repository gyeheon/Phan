import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)











with open('token.txt', 'r') as f:
    token = f.readline()

bot.run(token)
