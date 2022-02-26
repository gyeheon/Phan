import discord
from discord.ext import commands
import time
from voicemute import voicemute_cog
from main import main_cog
from liar import liar_cog


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
bot.add_cog(voicemute_cog(bot))
bot.add_cog(main_cog(bot))
bot.add_cog(liar_cog(bot))

'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = f'**Still on cooltime**, please try again in {round(error.retry_after, 0)}s'
        await ctx.reply(msg)

@commands.cooldown(1, 86400, commands.BucketType.user)
@bot.command(name='everyone')
async def test_(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(f"@everyone \n```{msg}``` \n`{ctx.author.name}'s message`")

#====================================================================

@bot.event
async def on_voice_state_update(Member, before, after):
    if before.channel != None and after.channel == None and Member.id == 848840160237453312:
        channel = await bot.fetch_channel(653594139811643412)
        await channel.send('testa')
'''







with open('token.txt', 'r') as f:
    token = f.readline()

bot.run(token)
