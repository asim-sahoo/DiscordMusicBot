import discord
from discord.ext import commands, tasks
from music import music
from keep_alive import keep_alive
from itertools import cycle

status = cycle(['-help','-play/-p','-pause/-stop','-resume','-disconnect/-dt','-search','-skip', '-queue/-q','Krait!'])

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())
@client.event
async def on_ready():
    change_status.start()
    print('Bot is Online!')
    
@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=(next(status))))
    '''await client.change_presence(activity=discord.listening(next(status)))'''
    
async def setup():
    await client.wait_until_ready()
    client.add_cog(music(client))

client.loop.create_task(setup()) 
keep_alive()
client.run("ODgwNTA1NjcyMDQ1ODI2MTEw.YSfQzw.gZgsOtMejSZiNAFQKs1eDT0h0Xo")

