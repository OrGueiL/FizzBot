import discord
import asyncio
from datetime import datetime
from LoLScheduleFunctions import worldCalendar
import os
import configparser
import logging

### CONFIG LOAD
dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path + '/config.ini')

TOKEN = config['DISCORD']['DISCORD_TOKEN']
CHANNEL = config['DISCORD']['CHANNEL']

NAME = config['BOT']['NAME']
VERSION = config['BOT']['VERSION']
AUTHOR = config['BOT']['AUTHOR']
###

### LOGGING LOAD
logging.basicConfig(filename='log.log',level=logging.ERROR,\
      format='%(asctime)s -- %(filename)s -- %(funcName)s -- %(levelname)s -- %(message)s')

client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    elif message.content.startswith('!help'):
        msg = ("```"
                "!help | obtenir la liste des commandes\n"
                "!today | obtenir les matchs du jour\n"
                "!yesterday | obtenir les matchs de la veille\n"
                "!tomorrow | obtenir les matchs du lendemain\n"
                "!next | obtenir les prochains matchs\n"
                "!live | obtenir les matchs en cours actuellement\n"
                 "```")
        await client.send_message(message.author, msg)
    elif message.content.startswith('!today'):
        msg = matchOfTheDayFunc(0)
        await client.send_message(client.get_channel(CHANNEL),msg)
    elif message.content.startswith('!yesterday'):
        msg = matchOfTheDayFunc(-1)
        await client.send_message(client.get_channel(CHANNEL),msg)
    elif message.content.startswith('!tomorrow'):
        msg = matchOfTheDayFunc(1)
        await client.send_message(client.get_channel(CHANNEL),msg)
    elif message.content.startswith('!version'):
        msg = NAME + " v" + VERSION + " by " + AUTHOR
        await client.send_message(client.get_channel(CHANNEL),msg)
    elif message.content.startswith('!next'):
        calendar = worldCalendar()
        nextGames = calendar.nextGames()

        msg = list()

        if nextGames:
            for game in nextGames:
                msg.append(calendar.gameAnnounce(game))
        else:
            msg.append("Aucun match programmé actuellement")

        msg = formatMsgForDiscord(msg)
        await client.send_message(client.get_channel(CHANNEL),msg)

    elif message.content.startswith('!live'):

        calendar = worldCalendar()
        liveGame = calendar.checkIfLive()

        msg = list()
        if liveGame:
            for game in liveGame:
                msg.append(calendar.gameAnnounce(game))
        else:
            msg.append("Aucun match en cours de diffusion")

        msg = formatMsgForDiscord(msg)
        await client.send_message(client.get_channel(CHANNEL),msg)


async def matchOfTheDayLoop(day):
    # check game loop 
    await client.wait_until_ready()
    
    while not client.is_closed:
        logging.info("classic loop")
        formatedMsg = matchOfTheDayFunc(day)
        await asyncio.sleep(1)
        await client.send_message(client.get_channel(CHANNEL),formatedMsg)

        # task runs every 12 hours
        await asyncio.sleep(60*60*12)


async def matchUpdate():
    # check if game is LIVE or just RESOLVED and announce it
    await client.wait_until_ready()
    

    while not client.is_closed:
        logging.info(" Recherche live/résultat")
        calendar = worldCalendar()
        gameUpdate = calendar.matchList()

        if gameUpdate:
            logging.info("Update trouvée")
            msg = list()
            for game in gameUpdate:
                msg.append(calendar.gameAnnounce(game))
            else:

                formatedMsg = formatMsgForDiscord(msg)

                await asyncio.sleep(1)
                await client.send_message(client.get_channel(CHANNEL),formatedMsg)
        else:
            logging.info("Pas d'update")
        # task will check update every minute
        await asyncio.sleep(60*1) 


def matchOfTheDayFunc(day):
        # function to check games from a given day
        # can be used by !command or task loop

        logging.info("Annonce automatique des matchs du jour")
        calendar = worldCalendar()
        gameOfTheDay = calendar.searchDayGames(day)
        
        
        msg = list()
        
        if not gameOfTheDay:
            logging.info("aucun match trouvé")
            msg.append("Aucun match enregistré pour ce jour")
        else:
            logging.info("annonce de matchs")
            for game in gameOfTheDay:
                msg.append(calendar.gameAnnounce(game))
                

        return formatMsgForDiscord(msg)


def formatMsgForDiscord(msg):
    formatedMsg = "```\n"

    for line in msg:
        formatedMsg += line + "\n"

    formatedMsg += "```"
    
    return formatedMsg


@client.event
async def on_ready():
    print('------')
    print(client.user.name + " is now running")
    print('------')
    logging.info(str(client.user.name) + " started")


    client.loop.create_task(matchOfTheDayLoop(0))

    client.loop.create_task(matchUpdate())

client.run(TOKEN)
