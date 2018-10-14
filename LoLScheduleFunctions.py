import requests, json
import time
from datetime import datetime, timedelta
from LoLScheduleDB import LoLScheduleDatabase

class worldCalendar():

	def __init__(self):

		urlWorlds ="https://prod-api.ewp.gg/ewp-web-api/v1/schedule?leagues=[98767975604431411]&hl=fr_FR"
		result  = requests.get(urlWorlds)
		self.fullDataWorlds = json.loads(result.text)


	def matchList(self):

		matchs = self.fullDataWorlds["schedule"]
		updatedGameList = list()

		for match in matchs:
			#list all matchss
			gameID = match["id"]
			startTime = match["startTime"]
			resolved = match["entryType"]
			teams = match["match"]["teams"]
			team1 = teams["team1"]["name"]
			team2 = teams["team2"]["name"]

			try:
				winner = match["match"]["past"]["winner"]
			except:
				winner = "None"

			game = {"gameID": gameID, "start": str(startTime)[:-3], "resolved": resolved, "team1": team1, "team2": team2, "winner": winner}

			db = LoLScheduleDatabase()
			updatedGame = db.recordGame(game)

			if updatedGame:
				updatedGameList.append(updatedGame)

		return updatedGameList


	def searchDayGames(self,fromEpoch):

		toEpoch = fromEpoch +1

		now = self.epochCalcul(fromEpoch)
		tomorrow = self.epochCalcul(toEpoch)

		db = LoLScheduleDatabase()
		gameList = db.searchGameOfTheDay(now,tomorrow)

		return gameList


	def formatGameAnnounce(self,gameInfo):

		matchTime = self.epochTimeToDate(gameInfo[1])

		result = gameInfo[2]
		team1 =	gameInfo[3]
		team2 = gameInfo[4]
		winner = gameInfo[5]

		if result == "RESOLVED":
			if winner == "team1":
				winner = team1
				loser = team2
			elif winner == "team2":
				winner = team2
				loser = team1

			gameAnnounce = winner + " a battu " + loser + " !"
			return gameAnnounce

		elif result == "LIVE":
			gameAnnounce = "**NOW LIVE**: " + team1 + " **VS** " + team2 + " !"
			return gameAnnounce

		elif result == "UNRESOLVED":
			gameAnnounce = "| " + matchTime + " : " + team1 + " VS " + team2
			return gameAnnounce
		else:
			print("UNKNOW MATCH STATUS " + str(result))
		
		
	def epochTimeToDate(self,epoch_time):

		return time.strftime("%A %d %b %Y %H:%M", time.localtime(int(epoch_time)))

	def epochCalcul(self,delta):
		# => tomorrow if +1 , yesterday if -1
		date = datetime.now() + timedelta(delta) 
		# => delete hour/minute/sec
		drydate = datetime(year=date.year, month=date.month, 
							day=date.day, hour=0, minute=0, second=0)
		# => convert to epoch timestamp
		epochDate = time.mktime(drydate.timetuple())

		return epochDate
