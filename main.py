#866945048339546122  client 
#8 permission
import discord
from discord import message
from discord import channel
from discord.client import Client
from discord.ext import commands
from datetime import date, datetime, timedelta
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
#client = discord.Client()


message_lastseen = datetime.now()
message2_lastseen = datetime.now()

bot = commands.Bot(command_prefix='tt',help_command=None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def test(ctx, *,par):
    await ctx.channel.send("you type{0}".format(par))

@bot.command()
async def help(ctx):
    emBed = discord.Embed(title="tutotial bot help",description="All avilable bot commands", color=0x6f00ff)
    emBed.add_field(name="help",value ="Get help command",inline= False)
    emBed.add_field(name="test",value ="Respond message you send",inline= False)
    emBed.add_field(name="send",value ="send hello message to user",inline= False)
    emBed.set_thumbnail(url='https://raw.githubusercontent.com/tententgc/discordbot_python/main/197365719_298203481983007_289378278497279769_n.jpg')
    emBed.set_footer(text='tenten discordbot',icon_url='https://raw.githubusercontent.com/tententgc/discordbot_python/main/197365719_298203481983007_289378278497279769_n.jpg')
    await ctx.channel.send(embed=emBed)


@bot.command()
async def send(ctx):
    print(ctx.channel)
    await ctx.channel.send("hello")

@bot.event #async / await
async def on_message(message):
    global message_lastseen,message2_lastseen
    if message.content =='555':
        await message.channel.send("ขำหาพ่องมึงหรอ")
    elif message.content =='หยีเหลี่ยม':
        await message.channel.send("หยีเหลี่ยมมากๆ รับไม่ได้")
    elif message.content =="!user":
        await message.channel.send(str(message.author.name)+"  hello")
    elif message.content == 'ชื่ออะไรหรอ' and  datetime.now()>= message_lastseen:
        message_lastseen = datetime.now()+timedelta(seconds=3)
        await message.channel.send("ฉันชื่อ "+str(bot.user.name))
        #logging
        print('{0} call name at {1} and use after {2}'.format(message.author.name,datetime.now(),message_lastseen))
    elif message.content == 'ผมชื่ออะไรหรอ' and  datetime.now()>= message2_lastseen:
        message2_lastseen = datetime.now()+timedelta(seconds=3)
        await message.channel.send("ฉันชื่อ "+str(message.author.name))
    elif message.content =="!logout":
        await bot.logout()
    await bot.process_commands(message)

@bot.command()
async def play(ctx,url):
    channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients,guild =ctx.guild)

    if voice_client == None:
        await ctx.channel.send("joined")
        await channel.connect()
        voice_client=get(bot.voice_clients,guild=ctx.guild)
    YDL_OPTIONS ={'format':'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if not voice_client.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice_client.is_playing()
    else:
        await ctx.channel.send("Already playing song")
        return

@bot.command()
async def stop(ctx):
    voice_client = get(bot.voice_clients,guild=ctx.guild)
    if voice_client==None:
        await ctx.channel.send("Bot is not connected to vc")
        return
    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("the bot is currently connected to {0}".format(voice_client.channel))
        return
    voice_client.stop()


@bot.command()
async def resume(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await ctx.channel.send("Bot is not connected to vc")
        return
    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("the bot is currently connected to {0}".format(voice_client.channel))
        return
    voice_client.resume()


@bot.command()
async def pause(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await ctx.channel.send("Bot is not connected to vc")
        return
    if voice_client.channel != ctx.author.voice.channel:
        await ctx.channel.send("the bot is currently connected to {0}".format(voice_client.channel))
        return
    voice_client.pause()
    
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()




# use fake token
bot.run('')
