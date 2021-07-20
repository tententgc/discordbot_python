#866945048339546122  client 
#ODY2OTQ1MDQ4MzM5NTQ2MTIy.YPZ7fg.5Dxvt_lWRKlifejqf1ktEBtIyuQ  token
#8 permission
import discord
from discord.client import Client

client = discord.Client()
#wrapper decurator
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event #async / await
async def on_message(message):
    if message.content ==('555'or'5555'):
        await message.channel.send("ขำหาพ่องมึงหรอ")
    elif message.content =="!user":
        await message.channel.send(str(message.author.name)+"  hello")
    elif message.content =="!logout":
        await client.logout()

client.run('ODY2OTQ1MDQ4MzM5NTQ2MTIy.YPZ7fg.5Dxvt_lWRKlifejqf1ktEBtIyuQ')

