import requests, json
import time
from datetime import datetime, timedelta
from LoLScheduleDB import LoLScheduleDatabase
import configparser
import os 
import logging

class worldCalendar():

	def __init__(self):
		
		dir_path = os.path.dirname(os.path.realpath(__file__))
		config = configparser.ConfigParser()
		config.read(dir_path + '/config.ini')
		logging.basicConfig(filename='log.log',level=logging.DEBUG,\
      		format='%(asctime)s -- %(filename)s -- %(funcName)s -- %(levelname)s -- %(message)s')
		logging.info("init worldCalendar")

		try:
			urlWorlds = config['RIOT_API']['URL_SCHEDULE']
			result  = requests.get(urlWorlds)

			if result.status_code == 200:
				self.fullDataWorlds = json.loads(result.text)
			else:
				logging.critical("API unreachable" + str(result.status))
				
		except Exception as e:
			logging.critical("init error: "+ str(e))



	def matchList(self):
		# Browse API and record or update changes
		
		try:
			matchs = self.fullDataWorlds["schedule"]
		except:
			logging.error("match vide")
			matchs = ""

		updatedGameList = list()

		for match in matchs:
			
			# Parse infos from API for each game
			gameID = match["id"]
			startTime = match["startTime"]
			resolved = match["entryType"]

			teams = match["match"]["teams"]

			team1 = teams["team1"]["name"]
			team1id = teams["team1"]["id"]
			try:
				team1win = teams["team1"]["gameWins"]
			except:
				team1win = '0'

			team2 = teams["team2"]["name"]
			team2id = teams["team2"]["id"]
			try:
				team2win = teams["team2"]["gameWins"]
			except:
				team2win = '0'
			
			try:
				winner = match["match"]["past"]["winner"]
			except:
				winner = "None"

			match_type = match["match"]["strategy"]["identifier"]
			BO = match["match"]["strategy"]["iteration"]

			tiebreak = match["match"]["tiebreaker"]

			leagueid = match["league"]["id"]
			leaguename = match["league"]["name"]
			leagueroundname = match["league"]["roundName"]

			tournamentid = match["tournament"]["id"]
			tournamentname = match["tournament"]["nameSlug"]

			game = {"gameid": str(gameID), 
						"starttime": str(startTime)[:-3], 
						"resolved": resolved, 
						"team1id": str(team1id),
						"team1": team1,
						"team1win": str(team1win),
						"team2id": str(team2id), 
						"team2": team2,
						"team2win": str(team2win), 
						"winner": winner,
						"match_type": match_type,
						"BO": str(BO),
						"tiebreak": str(tiebreak),
						"leagueid": str(leagueid),
						"leaguename": leaguename,
						"leagueroundname": leagueroundname,
						"tournamentid": str(tournamentid),
						"tournamentname": tournamentname
					}

			db = LoLScheduleDatabase()
			updatedGame = db.checkGame(game)

			if updatedGame:
				updatedGameList.append(updatedGame)

		return updatedGameList


	def searchDayGames(self,fromEpoch):
		logging.info("")
		toEpoch = fromEpoch +1

		now = self.epochCalcul(fromEpoch)
		tomorrow = self.epochCalcul(toEpoch)

		db = LoLScheduleDatabase()
		gameList = db.searchGameOfTheDay(now,tomorrow)

		return gameList

	def checkIfLive(self):
		db = LoLScheduleDatabase()
		isLive = db.searchLive()

		if isLive:
			return isLive
		else:
			return None

	def nextGames(self):
		now = self.epochCalcul(0)

		db = LoLScheduleDatabase()
		nextGame = db.searchNext(now)
		if nextGame:
			nextDateFrom = nextGame['starttime']
			nextDateTo = int(nextDateFrom) + (60*60*24)
			nextGames = db.searchGameOfTheDay(nextDateFrom,nextDateTo)
		else:
			nextGames = None

		return nextGames
		
	def gameAnnounce(self,gameInfo):
		# proxy function to format text from the game status
		result = gameInfo["resolved"]

		if result == "RESOLVED":
			gameAnnounce = self.announceResolved(gameInfo)
		elif result == "LIVE":
			gameAnnounce = self.announceLive(gameInfo)
		elif result == "UNRESOLVED":
			gameAnnounce = self.announceUnresolved(gameInfo)
		else:
			logging.error("UNKNOW MATCH STATUS " + str(result))
			gameAnnounce = None

		return gameAnnounce

	def announceLive(self,gameInfo):
		# format text to announce for game with status LIVE
		team1 =	gameInfo["team1"]
		team2 = gameInfo["team2"]

		if gameInfo["match_type"] == "best_of" and int(gameInfo["BO"]) > 1:
			# if BO2/3/5
			team1win =	gameInfo["team1win"]
			team2win =	gameInfo["team2win"]
			gameAnnounce = "[NOW LIVE] " + team1 + " VS " + team2 + " ! (BO" + gameInfo["BO"] + " | Score: " + team1win + " - " + team2win + ")" 
		else:
			# if game is BO1
			gameAnnounce = "[NOW LIVE*] " + team1 + " VS " + team2 + " !"

		return gameAnnounce


	def announceResolved(self,gameInfo):
		# format text to announce for game with status RESOLVED
		team1 =	gameInfo["team1"]
		team2 = gameInfo["team2"]
		winner = gameInfo["winner"]

		if winner == "team1":
			winner = team1
			loser = team2

		elif winner == "team2":
			winner = team2
			loser = team1

		if gameInfo["match_type"] == "best_of" and int(gameInfo["BO"]) > 1:
			# if BO2/3/5
			team1win =	gameInfo["team1win"]
			team2win =	gameInfo["team2win"]
			gameAnnounce = winner + " a battu " + loser + " ! (BO" + gameInfo["BO"] + " | Score: " + team1win + " - " + team2win + ")" 
		else:
			# if game is BO1
			gameAnnounce = winner + " a battu " + loser + " !"

		return gameAnnounce


	def announceUnresolved(self,gameInfo):
		# format text to announce for game with status UNRESOLVED
		matchTime = self.epochTimeToDate(gameInfo["starttime"])
		team1 =	gameInfo["team1"]
		team2 = gameInfo["team2"]

		gameAnnounce = "| " + matchTime + " : " + team1 + " VS " + team2
		return gameAnnounce

		
	def epochTimeToDate(self,epoch_time):
		# convert timestamp to readable date
		return time.strftime("%A %d %b %Y %H:%M", time.localtime(int(epoch_time)))


	def epochCalcul(self,delta):
		# calculate timestamp for other days

		# => tomorrow if +1 , yesterday if -1
		date = datetime.now() + timedelta(delta) 
		# => delete hour/minute/sec
		drydate = datetime(year=date.year, month=date.month, 
							day=date.day, hour=0, minute=0, second=0)
		# => convert to epoch timestamp
		epochDate = time.mktime(drydate.timetuple())

		return epochDate

