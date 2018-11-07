# FizzBot

1. **Config:**
* Add your discord bot token and channel ID in: config.ini

2. **Functions:**
* Send the game day list on your discord channel (every 12h default, so usually the games, then later all the results)
* Announce when a game is live
* Announce the game winner

3. **Command:**
* !help: command list (in private message)
* !today: game day list
* !tomorrow:
* !yesterday

4. **Version 0.5:**
* add configparser and config.ini file
* add logging to log actions, default ERROR level
* more clear code
* add !next command (will show all the match incoming in the 24h)
* add !live command
* bug fixes
* manage BO1/3/5 announcement with score
* send all games in only one message instead one message/match