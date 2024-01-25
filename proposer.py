# player outcome generator
# updated version of player probability determiner
# instead of generating predictions for all players
# we generate outcomes with probabilities for a given player of interest
# list of conditions
# playing against former team players probably play better bc more effort

#!/.venv/bin/python
# source .venv/bin/activate


import generator, reader

print('\n===Proposer===\n')

# # test pacers
#players_names = ['benedict mathurin', 'bruce brown', 'donovan mitchell', 'evan mobley', 'myles turner', 'tyrese haliburton']

# add user input: date of games so code will read all teams played that day
# could assume current date running code

# get from injury report site
#players_out = ['nikola jokic', 'jamal murray', 'kevin durant', 'bradley beal']
# determine irreg play time from players out
irreg_play_time = {'craig porter': 25, 'reggie jackson': 35}

# ===============
# Settings
# ===============

# read all seasons to compare and see trend
read_x_seasons = 2 # set 0 or high number to read all seasons
read_season_year = 2024 # user can choose year. read x seasons previous

# === STATS OF INTEREST === 
stats_of_interest = ['pts','reb','ast']

# if we want to see how it would perform for previous years
# we need to know the exact game (or even specific prop) that we want to evaluate
# by default, go through entire year

# read new odds at least once per day if false but set true if we want to update odds more than once per day
read_new_odds = True 
# keep in mind, when we add a new feature such as a new condition to the stat dict,
# then we must manually erase old saved stat dict OR make setting to overwrite it
# or else we would need to read from internet every time anyway which defeats the purpose of storing locally
read_new_stats = False # set true when we add new feature to stats dict so we want to manually overwrite old dict rather than usual behavior of trusting prev stat dicts
read_new_lineups = True # even if we saved lineups today they may have changed but we may not want to get new lineups yet if we are testing something else

find_matchups = False # if we want to read matchup data from box scores, which means how many of each stat a team allows their opponents to get (ie defensive stats)

# === TEST PERFORMANCE === 
# we eval/test performance to see how it would perform on prev games
# if true, compare all props to actual outcomes
test_performance = False

# === NEW TEAMS ===
# read new teams after trades and acquisitions new players
read_new_teams = False
# === NEW ROSTERS ===
# read new rosters after trades and acquisitions new players
# but before they actually played on new team
read_new_rosters = False

# === GAME IDs === 
# if error 429 too many requests then we need to stop reading new game ids for 1hr
# could save time since error in file request_time.txt = '1740 12/12/23' (1740=540pm)
read_new_game_ids = True

# === PLAYER IDs ===
# need all players ids but halt if error too many requests
read_new_player_ids = False

# === FIND PLAYERS ===
find_players = True # if true, read all players in game box scores to see prob with teammates out

# === READ ODDS ===
# set false to save time if observing all probs
# make list of sources with different odds 
read_odds = False # set false to test other features

#===CONTROL CONDITIONs===
# test a condition or group of conditions by itself
control_conds = ['coverage','city','tod'] #'info' # info contains coverage, city, tod



settings = {'find matchups': find_matchups, 
            'find players': find_players, 
            'read new teams': read_new_teams, 
            'read new rosters': read_new_rosters,
            'read x seasons': read_x_seasons, 
            'read season year': read_season_year, 
            'read new odds': read_new_odds, 
            'read odds': read_odds, 
            'irreg play time': irreg_play_time, 
            'read new game ids': read_new_game_ids, 
            'read new player ids': read_new_player_ids,
            'stats of interest': stats_of_interest,
            'control conditions': control_conds}

all_teams = ['bos','bkn', 'nyk','phi', 'tor','chi', 'cle','det', 'ind','mil', 'den','min', 'okc','por', 'uta','gsw', 'lac','lal', 'phx','sac', 'atl','cha', 'mia','orl', 'wsh','dal', 'hou','mem', 'nop','sas']
# gen list of player names given teams so we dont have to type all names
# if no date given, and if past 10pm then assume getting data for next day
# https://www.espn.com/nba/schedule 
# if reading prev seasons to eval, read all games from box scores file
# if prev yr, game teams blank
# game key of interest we want to eval how program would perform?
# more likely to see on full set of yr, including this yr
# so make setting, test performance
game_teams = [('phi','ind')]#, ('uta','wsh'), ('min','bkn'), ('bos','mia'), ('den','nyk'), ('sac','gsw'), ('chi','lal')]#, ('nop','lal')
# if not test_performance:
#     game_teams = reader.read_game_teams(read_season_year)
# if read_season_year == current_year:
#     game_teams = []
# we can make read new teams var false at first bc the file has not been created yet so we will write for the first time
# we make it true to read new teams after trades, which tells it to overwrite existing file or make a new file with the date in the title
teams_current_rosters = reader.read_teams_current_rosters(game_teams, read_new_teams, read_new_rosters, all_teams) # {team:roster,...}
#players_names = reader.read_players_from_rosters(teams_current_rosters, game_teams)# generate is wrong term bc we are not computing anything only reading players on each team
players_names = ['joel embiid'] # 'jacob gilyard', use for testing


# if we get rosters instead of player names then read all players on rosters
# if we get no player names or rosters then read all games today
all_players_props = generator.generate_all_players_props(settings, players_names, game_teams, teams_current_rosters, all_teams)

#writer.display_all_players_props(all_players_props)