# player outcome generator
# updated version of player probability determiner
# instead of generating predictions for all players
# we generate outcomes with probabilities for a given player of interest
# list of conditions
# playing against former team players probably play better bc more effort

#/.venv/bin/python
# source .venv/bin/activate
#!/Users/m/repos/proposer/.venv/bin/python3


import generator, reader#, writer

print('\n===Proposer===\n')

# test = {'test':'test'}
# test_file = 'test.json'
# writer.write_json_to_file(test, test_file)

# # test pacers
#players_names = ['benedict mathurin', 'bruce brown', 'donovan mitchell', 'evan mobley', 'myles turner', 'tyrese haliburton']

# add user input: date of games so code will read all teams played that day
# could assume current date running code

# get from injury report site
#players_out = ['nikola jokic', 'jamal murray', 'kevin durant', 'bradley beal']
# determine irreg play time from players out
irreg_play_times = {}#{'dennis schroder': 22}
# need to know what injury players are back from 
# to know if they will play restricted minutes
# search player news to see what injury
# look for keywords in dict
# only list injuries with restrictions
# note injuries w/o limits: bruise
# may need to make dict of no. games restricted by injury
# bc breaks get more limits than sprain and so on
#restricted_injuries = ['sprain', 'broke', 'fracture', 'torn']
# OR much simpler if can set min games out for serious injury
# currently 11 games but need to measure more and see if consistent enough

# ===============
# Settings
# ===============

# read all seasons to compare and see trend
read_x_seasons = 2 # set 0 or high number to read all seasons
read_season_year = 2024 # user can choose year. read x seasons previous

# === MODEL SEASONS === 
# no. seasons to use in all data to fit probability distribution
# can be different than read x seasons 
# bc true prob might be less accurate with more seasons until we get time decay fmla
# here we get more samples from distant seasons and scale them to make a simulated model so it is smoothed out
model_x_seasons = 2

# === SEASONS START DAYS ===
# so we can tell if preseason game
all_seasons_start_days = {'2024':24, '2023':18, '2022':19}

# === STATS OF INTEREST === 
stats_of_interest = ['pts','reb','ast']

# if we want to see how it would perform for previous years
# we need to know the exact game (or even specific prop) that we want to evaluate
# by default, go through entire year


#===CONTROL CONDITIONs===
# test a condition or group of conditions by itself
control_conds = ['coverage','city','tod'] #'info' # info contains coverage, city, tod
single_conds = ['nf', 'local', 'weekday', 'night']

#===OUT FOR SEASON PLAYERS===
# players out for season not listed on report
# they played this season so they are included in all teammates 
# but are now out for the rest of season
# 'cha':['kyle lowry'], 
ofs_players = {'bkn':['dariq whitehead'], 'chi':['zach lavine'], 'hou':['tari eason'], 'mem':['ja morant'], 'mia':['dru smith'], 'por':['robert williams iii'], 'sas':['charles bassey'], 'wsh':['isaiah livers']}


#===READ LINEUPS===
# CANNOT work bc needs lineups to get projected minutes to get unit stats
# UNTIL we get unit prob dict and scale that if possible???
# true when we want to include gp conds prob distribs
# false to ignore and prepare before lineups set
# so we can get prob distribs for all conds except gp conds
#read_lineups = False


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

# === PLAYER IDs ===
# need all players ids but halt if error too many requests
read_new_player_ids = False

# === FIND PLAYERS ===
find_players = True # if true, read all players in game box scores to see prob with teammates out




# === NEW TEAMS ===
# read new teams after trades and acquisitions new players
read_new_teams = False
# === NEW ROSTERS ===
# read new rosters after trades and acquisitions new players
# but before they actually played on new team
read_new_rosters = False



# === TEST ===
# set single team and player w/o having to erase and rewrite
test = False
# run dist probs with prints/comments
prints_on = False

# force probs to reload even if already saved
# so we dont have to erase each test
test_probs = False

# === READ ODDS ===
# set false to save time if observing all probs
# make list of sources with different odds 
read_odds = True # set false to test other features
if test:
    read_odds = False

# === GAME IDs === 
# if error 429 too many requests then we need to stop reading new game ids for 1hr
# could save time since error in file request_time.txt = '1740 12/12/23' (1740=540pm)
read_new_game_ids = True


settings = {'find matchups': find_matchups, 
            'find players': find_players, 
            'read new teams': read_new_teams, 
            'read new rosters': read_new_rosters,
            'model x seasons': model_x_seasons, 
            'read x seasons': read_x_seasons, 
            'read season year': read_season_year, 
            'read new odds': read_new_odds, 
            'read odds': read_odds, 
            'irreg playtimes': irreg_play_times, 
            'read new game ids': read_new_game_ids, 
            'read new player ids': read_new_player_ids,
            'stats of interest': stats_of_interest,
            'control conditions': control_conds,
            'ofs players': ofs_players,
            'test': test,
            'test probs': test_probs,
            'prints on': prints_on, 
            'single conds': single_conds,
            'seasons start days': all_seasons_start_days}

all_teams = ['bos','bkn', 'nyk','phi', 'tor','chi', 'cle','det', 'ind','mil', 'den','min', 'okc','por', 'uta','gsw', 'lac','lal', 'phx','sac', 'atl','cha', 'mia','orl', 'wsh','dal', 'hou','mem', 'nop','sas']
# gen list of player names given teams so we dont have to type all names
# if no date given, and if past 10pm then assume getting data for next day
# https://www.espn.com/nba/schedule 
# if reading prev seasons to eval, read all games from box scores file
# if prev yr, game teams blank
# game key of interest we want to eval how program would perform?
# more likely to see on full set of yr, including this yr
# so make setting, test performance
# [('min','chi')]#
game_teams = [('chi','lac'), ('bkn','cha'), ('dal','det'), ('bos','phx'), ('sas','gsw'), ('uta','den'), ('tor','por')]#, ('nop','lal')
if test:
    # when we run with empty game teams, it will run for all teams
    # so all teams players gets filled???
    # no actually it will fill if we set read new teams
    # but to automate that instead of manual set
    # simply check for new players if new box score
    game_teams = [('chi','lac')]
# if not test_performance:
#     game_teams = reader.read_game_teams(read_season_year)
# if read_season_year == current_year:
#     game_teams = []
# we can make read new teams var false at first bc the file has not been created yet so we will write for the first time
# we make it true to read new teams after trades, which tells it to overwrite existing file or make a new file with the date in the title
teams_current_rosters = reader.read_teams_current_rosters(game_teams, read_new_teams, read_new_rosters, all_teams) # {team:roster,...}
players_names = reader.read_players_from_rosters(teams_current_rosters, game_teams)# generate is wrong term bc we are not computing anything only reading players on each team

if test:
    players_names = ['demar derozan'] # 'jacob gilyard', use for testing


# if we get rosters instead of player names then read all players on rosters
# if we get no player names or rosters then read all games today
all_players_props = generator.generate_all_players_props(settings, players_names, game_teams, teams_current_rosters, all_teams)

#writer.display_all_players_props(all_players_props)