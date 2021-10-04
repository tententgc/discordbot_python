import discord
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
import asyncio
from async_timeout import timeout
from functools import partial
from discord.ext import commands
from datetime import datetime, timedelta
import itertools

# # ibrary ไว้แอบ token
# import os
# from dotenv import load_dotenv
# load_dotenv()
# token = os.getenv('TOKEN')
# #############################################

# wrapper / decorator

message_lastseen = datetime.now()
message2_lastseen = datetime.now()

bot = commands.Bot(command_prefix='t', help_command=None)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn',
    # song will end if no this line
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        # delete after can be added
        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```')

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source, **ffmpeg_options), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info,
                         url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog',
                 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return await self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(
                source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    async def destroy(self, guild):
        """Disconnect and cleanup the player."""
        del players[self._guild]
        await self._guild.voice_client.disconnect()
        return self.bot.loop.create_task(self._cog.cleanup(guild))

############


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def test(ctx, *, par):
    await ctx.channel.send("You typed {0}".format(par))


@bot.command()
async def help(ctx):
    emBed = discord.Embed(title="tutotial bot help",
                          description="All avilable bot commands", color=0x6f00ff)
    emBed.add_field(name="help", value="Get help command", inline=False)
    emBed.add_field(
        name="test", value="Respond message you send", inline=False)
    emBed.add_field(
        name="send", value="send hello message to user", inline=False)
    emBed.set_thumbnail(
        url='https://raw.githubusercontent.com/tententgc/discordbot_python/main/197365719_298203481983007_289378278497279769_n.jpg')
    emBed.set_footer(text='tenten discordbot',
                     icon_url='https://raw.githubusercontent.com/tententgc/discordbot_python/main/197365719_298203481983007_289378278497279769_n.jpg')
    await ctx.channel.send(embed=emBed)


@bot.command()
async def send(ctx):
    print(ctx.channel)
    await ctx.channel.send('Hello')


@bot.event  # async/await
async def on_message(message):
    global message_lastseen, message2_lastseen
    b = ["หยีเหลี่ยม", 'มีปัญหาหรอ', 'เหงามั้ยคะ', 'ไม่ตอบหรอ','บอทกาก', 'ตอบช้าจัง',"ปากแซ่บจัง",'ทำไรอ่ะ']
    c = ['นั่นดิเหลี่ยมเกิน', 'ใช่มีปัญหากับมึงอ่ะแหละ', 'เหงาแต่ไม่เท่ามึง','ไม่อยากตอบมึงอ่ะหยี','กากแล้วไงเ่ก่่งกว่ามึงและกัน','ไม่ช้านะ','อร่อยแล้วกัน', 'ฆ่าพ่อมึงอ่ะ']
    for i in range(len(b)):
        if b[i] == message.content:
            await message.channel.send(c[i])
    await bot.process_commands(message)


@bot.command()
async def p(ctx, *, search: str):
    channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if voice_client == None:
        await ctx.channel.send("Joined")
        await channel.connect()
        voice_client = get(bot.voice_clients, guild=ctx.guild)

    await ctx.trigger_typing()

    _player = get_player(ctx)
    source = await YTDLSource.create_source(ctx, search, loop=bot.loop, download=False)

    await _player.queue.put(source)


players = {}


def get_player(ctx):
    try:
        player = players[ctx.guild.id]
    except:
        player = MusicPlayer(ctx)
        players[ctx.guild.id] = player

    return player


@bot.command()
async def stop(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await ctx.channel.send("Bot is not connected to vc")
        return

    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("The bot is currently connected to {0}".format(voice_client.channel))
        return

    voice_client.stop()


@bot.command()
async def pause(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await ctx.channel.send("Bot is not connected to vc")
        return

    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("The bot is currently connected to {0}".format(voice_client.channel))
        return

    voice_client.pause()


@bot.command()
async def resume(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await ctx.channel.send("Bot is not connected to vc")
        return

    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("The bot is currently connected to {0}".format(voice_client.channel))
        return

    voice_client.resume()


@bot.command()
async def leave(ctx):
    del players[ctx.guild.id]
    await ctx.voice_client.disconnect()


@bot.command()
async def q(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if voice_client == None or not voice_client.is_connected():
        await ctx.channel.send("Bot is not connected to vc", delete_after=10)
        return

    player = get_player(ctx)
    if player.queue.empty():
        return await ctx.send('There are currently no more queued songs')

    # 1 2 3
    upcoming = list(itertools.islice(
        player.queue._queue, 0, player.queue.qsize()))
    fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
    embed = discord.Embed(
        title=f'Upcoming - Next {len(upcoming)}', description=fmt)
    await ctx.send(embed=embed)


@bot.command()
async def skip(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if voice_client == None or not voice_client.is_connected():
        await ctx.channel.send("Bot is not connected to vc", delete_after=10)
        return

    if voice_client.is_paused():
        pass
    elif not voice_client.is_playing():
        return

    voice_client.stop()
    await ctx.send(f'**`{ctx.author}`**: Skipped the song!')


bot.run('ODY2OTQ1MDQ4MzM5NTQ2MTIy.YPZ7fg.l3xP9_uPUiCkv3HEYoFMP4rZGqo')