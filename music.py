import youtube_dl
import pafy
import discord
from discord.ext import commands

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.client.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            
            self.song_queue[ctx.guild.id].pop(0)
            

    async def search_song(self, amount, song, get_url=False):
        info = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
        
        
        
    #@commands.command(aliases=['j'])
    #async def join(self, ctx):
        #if ctx.author.voice is None:
            #return await ctx.send("You are not connected to any voice channel!")

        #if ctx.voice_client is not None:
            #await ctx.voice_client.disconnect()

        #await ctx.author.voice.channel.connect()
        #await ctx.send("Yugly Connected!")
        
    @commands.command(aliases=['disconnect','dt'])
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            self.song_queue = {}
            await ctx.send("Yugly Disconnected!")
            return await ctx.voice_client.disconnect()
            
            

        await ctx.send("I am not connected to a voice channel.")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Include a song to play.")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        # handle song where song isn't url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song ):
            await ctx.send("Searching.....")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send("Sorry, I could not find the song, try using search command.")

            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 50:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"Added to Queue. Position: {queue_len+1}\nUse command '-q or -queue to see the Queue.'")

            else:
                return await ctx.send("Sorry, I can only queue up to 50 songs.")
      
        await self.play_song(ctx, song)
        
        await ctx.send(f"Now playing: {song}")

    @commands.command(aliases=['s'])
    async def search(self, ctx, *, song=None):
        if song is None: return await ctx.send("Include a song to search for.")

        await ctx.send("Searching for song....")

        info = await self.search_song(5, song)

        embed = discord.Embed(title=f"Results for '{song}':", description="*Searched Results*\n", colour=discord.Colour.red())
        
        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1

        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        if self.song_queue == {}:
            return await ctx.send("There are currently no songs in the queue.")

        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            title = pafy.new(url).title
            embed.description += f"{i}) {title} {url}\n"

            i += 1

        await ctx.send(embed=embed)
        

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")

        if ctx.author.voice is None:
            return await ctx.send("You are not connected to any voice channel.")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am not currently playing any songs for you.")

        await ctx.send("Skipped!")
        ctx.voice_client.stop()
        await self.check_queue(ctx)


    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("I am already paused.")

        ctx.voice_client.pause()
        await ctx.send("The current song has been paused.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("I am not connected to any voice channel.")

        if not ctx.voice_client.is_paused():
            return await ctx.send("I am already playing a song.")
        
        ctx.voice_client.resume()
        await ctx.send("The current song has been resumed.")

