#866945048339546122  client 
#8 permission
import discord
from discord import message
from discord import channel
from discord.client import Client
from discord.ext import commands
from datetime import date, datetime, timedelta

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
    await ctx.channel.send("help, test")

@bot.event #async / await
async def on_message(message):
    global message_lastseen,message2_lastseen
    if message.content =='555':
        await message.channel.send("ขำหาพ่องมึงหรอ")
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

# use fake token
bot.run('')
