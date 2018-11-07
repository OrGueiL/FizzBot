import sqlite3
import logging


class LoLScheduleDatabase():

    def __init__(self):
        # Check if DB and table exist, and create it if needed
        
        logging.basicConfig(filename='log.log',level=logging.ERROR,\
              format='%(asctime)s -- %(filename)s -- %(funcName)s -- %(levelname)s -- %(message)s')
        logging.info("Initialisation DB")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            db = data.cursor()

            db.execute('''CREATE TABLE IF NOT EXISTS games 
                        (gameid,starttime,resolved,team1id,team1,team1win,team2id,team2,team2win,winner,match_type,BO,tiebreak,leagueid,leaguename,leagueroundname,tournamentid,tournamentname)''')

            data.commit()
            data.close()
        except Exception as e:
            logging.critical("init" + str(e))


    def checkGame(self,gameInfo):
        # Check if game is already recorded in db or not
        # and ask for record if not or check if there is something to update
        logging.info("Vérification existence match")
        try:
            gameid_exist = self.readGame(gameInfo["gameid"])

            if not gameid_exist:
                logging.info("Le match n'existe pas => enregistrement")
                self.recordGame(gameInfo)
            else:
                logging.info("Le match existe => vérification")
                checkResult = self.updateGame(gameInfo,gameid_exist)
                return checkResult

        except Exception as e:
            logging.error("checkGame" + str(e))

    def recordGame(self,gameInfo):
        # record a new game
        logging.info("Nouveau match détectée")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            db = data.cursor()
            db.execute("INSERT INTO games (gameid,starttime,resolved,team1id,team1,team1win,team2id,team2,team2win,winner,match_type,BO,tiebreak,leagueid,leaguename,leagueroundname,tournamentid,tournamentname) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                    (gameInfo['gameid'],gameInfo['starttime'],gameInfo['resolved'],gameInfo['team1id'],gameInfo['team1'],gameInfo['team1win'],gameInfo['team2id'],gameInfo['team2'],gameInfo['team2win'],gameInfo['winner'],gameInfo['match_type'],gameInfo['BO'],gameInfo['tiebreak'],gameInfo['leagueid'],gameInfo['leaguename'],gameInfo['leagueroundname'],gameInfo['tournamentid'],gameInfo['tournamentname']))
            data.commit()
            data.close()
        except Exception as e:
            logging.critical("recordGame" + str(e))


    def updateGame(self,gameInfo,gameid_exist):
        logging.info("Vérification de mise à jour de match")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            db = data.cursor()

            if gameInfo['team1'] != gameid_exist['team1'] or gameInfo['team2'] != gameid_exist['team2'] or gameInfo['starttime'] != gameid_exist['starttime']:
                # it means API datas have been changed after first record, we update everything
                db.execute("UPDATE games SET starttime = ? , resolved = ? , team1id = ? , team1 = ? , team1win = ? , team2id = ? , team2 = ? , team2win = ? , winner = ? , match_type = ? , BO = ? , tiebreak = ? , leagueid = ? , leaguename = ? , leagueroundname = ? , tournamentid = ? , tournamentname = ?  WHERE gameid = ?", 
                        (gameInfo['starttime'],gameInfo['resolved'],gameInfo['team1id'],gameInfo['team1'],gameInfo['team1win'],gameInfo['team2id'],gameInfo['team2'],gameInfo['team2win'],gameInfo['winner'],gameInfo['match_type'],gameInfo['BO'],gameInfo['tiebreak'],gameInfo['leagueid'],gameInfo['leaguename'],gameInfo['leagueroundname'],gameInfo['tournamentid'],gameInfo['tournamentname'],gameInfo['gameid']))
                logging.info("Changement des teams/horaire du match")

            if gameInfo['winner'] != gameid_exist['winner']:
                db.execute("UPDATE games SET resolved = ?, winner = ?  WHERE gameid = ?", 
                        (gameInfo['resolved'],gameInfo['winner'],gameInfo['gameid']))
                logging.info("Nous avons un vainqueur")
                gameIsUpdated = gameInfo

            elif gameInfo['resolved'] == "LIVE" and gameid_exist['resolved'] != "LIVE":
                db.execute("UPDATE games SET resolved = ?  WHERE gameid = ?", 
                        (gameInfo['resolved'],gameInfo['gameid']))
                logging.info("Changement de status du match")
                gameIsUpdated = gameInfo

            elif str(gameInfo['team1win']) != str(gameid_exist['team1win']) or str(gameInfo['team2win']) != str(gameid_exist['team2win']):

                db.execute("UPDATE games SET team1win = ?, team2win = ?  WHERE gameid = ?", 
                        (gameInfo['team1win'],gameInfo['team2win'],gameInfo['gameid']))
                logging.info("Evolution du score du BO")
                gameIsUpdated = gameInfo

            else:
                gameIsUpdated = None
                logging.info("Aucune mise à jour de match")
            
            data.commit() 
            data.close()

            return gameIsUpdated

        except Exception as e:
            logging.critical("erreur mise à jour de match" + str(e))

    def readGame(self,gameid):
        logging.info("readgame")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            data.row_factory = lambda c, r: dict(zip([col[0] for col in db.description], r))
            db = data.cursor()
            db.execute('''SELECT * FROM games WHERE gameid =?''',(gameid,))

            gameInfo = db.fetchone()
            data.close()

            return gameInfo

        except Exception as e:
            logging.critical("readGame" + str(e))

    def searchNext(self,today):
        logging.info("recherche des prochains matchs")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            data.row_factory = lambda c, r: dict(zip([col[0] for col in db.description], r))
            db = data.cursor()

            db.execute('''SELECT * FROM games WHERE starttime > ? ORDER BY starttime ASC''',(str(today),))

            nextGame = db.fetchone()

            data.close()
   
            return nextGame

        except Exception as e:

            logging.critical("Erreur de recherche des prochains matchs" + str(e))

    def searchGameOfTheDay(self,now,day):
        logging.info("recherche des matchs du jour")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            data.row_factory = lambda c, r: dict(zip([col[0] for col in db.description], r))
            db = data.cursor()

            db.execute('''SELECT * FROM games WHERE starttime BETWEEN ? AND ? ORDER BY starttime ASC''',(str(now),str(day)))

            gameOfTheDay = db.fetchall()

            data.close()

            return gameOfTheDay

        except Exception as e:
            logging.critical("Erreur de recherche des matchs du jour" + str(e))

    def searchLive(self):
        logging.info("recherche des games LIVE")
        try:
            data = sqlite3.connect('LoL_calendar.db')
            data.row_factory = lambda c, r: dict(zip([col[0] for col in db.description], r))
            db = data.cursor()

            db.execute('''SELECT * FROM games WHERE resolved = "LIVE" ORDER BY starttime ASC''')

            liveGame = db.fetchall()

            data.close()

            return liveGame

        except Exception as e:
            logging.critical("Erreur de recherche des matchs du jour" + str(e))

