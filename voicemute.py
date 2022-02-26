import discord
from discord.ext import commands


#==================================================================== voicemute
class voicemute_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(name='muteall')
    async def muteall_(self, ctx):
        channel = ctx.author.voice.channel
        members = channel.members
        for i in members:
            await i.edit(mute=True)

    @commands.has_permissions(administrator=True)
    @commands.command(name='unmuteall')
    async def unmuteall_(self, ctx):
        channel = ctx.author.voice.channel
        members = channel.members
        for i in members:
            await i.edit(mute=False)

    @commands.Cog.listener()
    async def on_voice_state_update(self, Member, before, after):
        if before.channel == None and after.channel != None:
            await Member.edit(mute=False)

#====================================================================
