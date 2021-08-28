import discord
from discord.ext import commands, tasks
import music
from keep_alive import keep_alive
from itertools import cycle

status = cycle(['-help','-join','-play','-pause','-resume','-disconnect'])
cogs = [music]

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())
@client.event
async def on_ready():
    change_status.start()
    print('Bot is Online!')

@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

for i in range(len(cogs)):
    cogs[i].setup(client)

keep_alive()
client.run("ODgwNTA1NjcyMDQ1ODI2MTEw.YSfQzw.gZgsOtMejSZiNAFQKs1eDT0h0Xo")

