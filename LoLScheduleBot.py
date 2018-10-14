import discord
import asyncio
from datetime import datetime
from LoLScheduleFunctions import worldCalendar


TOKEN = '' # DISCORD BOT TOKEN
CHANNEL = '' # CHANNEL ID WHERE BOT WILL SEND MESSAGES 
client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        msg = ("```"
                "!help | obtenir la liste des commandes\n"
                "!today | obtenir les matchs du jour\n"
                "!yesterday | obtenir les matchs de la veille\n"
                "!tomorrow | obtenir les matchs du lendemain\n"
                 "```")
        await client.send_message(message.author, msg)

    elif message.content.startswith('!today'):
        calendar = worldCalendar()
        gameOfTheDay = calendar.searchDayGames(0)

        if not gameOfTheDay:
            msg = "Aucun match prévu aujourd'hui"
            await client.send_message(message.channel, msg)

        for game in gameOfTheDay:
            msg = calendar.formatGameAnnounce(game)
            await asyncio.sleep(1)
            await client.send_message(message.channel, msg)

    elif message.content.startswith('!yesterday'):
        calendar = worldCalendar()
        gameOfTheDay = calendar.searchDayGames(-1)

        if not gameOfTheDay:
            msg = "Aucun match enregistré pour hier"
            await client.send_message(message.channel, msg)

        for game in gameOfTheDay:
            msg = calendar.formatGameAnnounce(game)
            await asyncio.sleep(1)
            await client.send_message(message.channel, msg)

    elif message.content.startswith('!tomorrow'):
        calendar = worldCalendar()
        gameOfTheDay = calendar.searchDayGames(1)

        if not gameOfTheDay:
            msg = "Aucun match prévu demain"
            await client.send_message(message.channel, msg)

        for game in gameOfTheDay:
            msg = calendar.formatGameAnnounce(game)
            await asyncio.sleep(1)
            await client.send_message(message.channel, msg)


async def matchOfTheDay():

    await client.wait_until_ready()
    
    while not client.is_closed:
        calendar = worldCalendar()
        gameOfTheDay = calendar.searchDayGames(0)
        print(datetime.now())
        print("Annonce automatique des matchs du jour")

        if not gameOfTheDay:
            msg = "Aucun match prévu aujourd'hui"
            await client.send_message(message.channel, msg)

        for game in gameOfTheDay:
            msg = calendar.formatGameAnnounce(game)
            await asyncio.sleep(1)
            await client.send_message(client.get_channel(CHANNEL),msg)

        await asyncio.sleep(60*60*12) # task runs every 12 hours


async def matchUpdate():

    await client.wait_until_ready()
    
    while not client.is_closed:
        calendar = worldCalendar()
        print(datetime.now())
        print("Annonce automatique de résultat")

        gameUpdate = calendar.matchList()

        for game in gameUpdate:
            msg = calendar.formatGameAnnounce(game)
            await asyncio.sleep(1)
            await client.send_message(client.get_channel(CHANNEL),msg)

        await asyncio.sleep(60*5) # check every 5 minutes


@client.event
async def on_ready():

    print('------')
    print(client.user.name + " is now running")
    print('------')

    client.loop.create_task(matchOfTheDay())
    client.loop.create_task(matchUpdate())

client.run(TOKEN)
