# read a team's schedule or player's game log
# then see the box score of each game played
# then list all active players in the game on both teams (for and aginst given player of interest)

import reader, determiner

import pandas as pd # read html results from webpage
from urllib.request import Request, urlopen # request website, open webpage given req
from bs4 import BeautifulSoup # read html from webpage

import re # search opp string in game log to see if home or away

# ===read a team's schedule
# we need to see how a given player performs with given teammates and opponent players, specifically the individuals for and against a given player, not just the team as a whole bc the team consists of individuals that determine matchups
# also check the affect of individuals for and against a given player bc not enough samples with exact lineups but many samples against individuals
# we already have a given players game log so we can see games played bc we only need matchups for the given player

# def read_team_schedule(team_abbrev):

#     print('\n===Read Team Schedule===\n')

player_names = ['naji marshall']

# init data as sample data and then get full data if not sample data
use_full_data = True # if sample_data = true then we do not need to get data from internet but use sample data

# make sample game log df
all_player_season_logs_dict = {}

player_teams = {}

# if run with full data not sample data
if use_full_data:

    player_espn_ids_dict = reader.read_all_player_espn_ids(player_names)

    # read game logs
    read_all_seasons = False # saves time during testing other parts if we only read 1 season
    all_player_season_logs_dict = reader.read_all_players_season_logs(player_names, read_all_seasons, player_espn_ids_dict)


    # read teams so we can find game id by team opp and date
    player_teams = reader.read_all_players_teams(player_espn_ids_dict, read_new_teams=False)



all_players_in_games_dict = reader.read_all_players_in_games(all_player_season_logs_dict, player_teams)
