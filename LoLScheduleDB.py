import sqlite3



class LoLScheduleDatabase():

	def __init__(self):
		# Check if DB and table exist, and create it

		data = sqlite3.connect('LoL_calendar.db')
		db = data.cursor()

		db.execute('''CREATE TABLE IF NOT EXISTS games 
					(gameid,starttime,resolved,team1,team2,winner)''')

		data.commit()
		data.close()


	def recordGame(self,gameInfo):
		data = sqlite3.connect('LoL_calendar.db')
		db = data.cursor()

		db.execute("SELECT * FROM games WHERE gameid=?",(gameInfo['gameID'],))
		gameid_exist = db.fetchone()

		if not gameid_exist:
			print("Nouvelle game")
			db.execute("INSERT INTO games (gameid,starttime,resolved,team1,team2,winner) VALUES (?,?,?,?,?,?)", 
				(gameInfo['gameID'],gameInfo['start'],gameInfo['resolved'],gameInfo['team1'],gameInfo['team2'],gameInfo['winner']))
			data.commit()
			data.close()

		else:
			if gameInfo['winner'] != gameid_exist[5]:
				db.execute("UPDATE games SET resolved = ?, winner = ?  WHERE gameid = ?", 
					(gameInfo['resolved'],gameInfo['winner'],gameInfo['gameID']))

				data.commit() 
				data.close()
				gameIDUpdated = self.readGame(gameInfo['gameID'])

			elif gameInfo['resolved'] == "LIVE" and gameid_exist[2] != "LIVE":
				db.execute("UPDATE games SET resolved = ?  WHERE gameid = ?", 
					(gameInfo['resolved'],gameInfo['gameID']))
				data.commit() 
				data.close()
				gameIDUpdated = self.readGame(gameInfo['gameID'])
	
			else:
				gameIDUpdated = None

			return gameIDUpdated

	def readGame(self,gameID):
		data = sqlite3.connect('LoL_calendar.db')
		db = data.cursor()

		db.execute('''SELECT * FROM games WHERE gameid =?''',(gameID,))

		gameInfo = db.fetchone()
		data.close()

		return gameInfo

	def searchGameOfTheDay(self,now,today):
		data = sqlite3.connect('LoL_calendar.db')
		db = data.cursor()

		db.execute('''SELECT * FROM games WHERE starttime BETWEEN ? AND ? ORDER BY starttime ASC''',(str(now),str(today)))

		gameOfTheDay = db.fetchall()

		data.close()

		return gameOfTheDay