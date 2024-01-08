# generator.py
# generate data structures so we can reference info to make decisions
# and generate decisions based on data structures

import re
from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart

import determiner # determine regular season games, etc

import numpy as np # mean, median
from scipy import stats # calculate mode

import reader # read game log from file if needed
import writer # format record and other game data for readability

from tabulate import tabulate # display output

# we use isolator for strictly isolating parts of existing data when there is no processing or computation between input output
import sorter, isolator

import pandas as pd # read html results from webpage. need here to convert game log dict to df

from sympy import sympify, solve # only needed if system of eqns > 2

import math # using log10 to scale sample size relative to condition weight

import copy # need to compare init saved data to final data bc only overwrite saved data if changed

import converter # convert am to dec odds so we can get joint odds

import itertools # get combos of player abbrevs

# we use all_players_stats_dicts = {player name:{stat name:{}}}
# to reference stats 
# all_players_season_logs = {player name:{year:{condition:{stat:[]}}}}
# projected_lines_dict = {player name:{stat:value,..,loc:val,opp:val}}
# use projected lines input param to get opponent
# use today game date to get day and break conditions
def generate_all_players_stats_dicts(all_players_season_logs, projected_lines_dict, todays_games_date_obj, season_year=2024):
    print('\n===Generate All Players Stats Dicts===\n')
    all_players_stats_dicts = {}

    for player_name, player_season_logs in all_players_season_logs.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, season_year=season_year)
        all_players_stats_dicts[player_name] = player_stat_dict


    #print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    return all_players_stats_dicts

# at this point we should have projected_lines_dict either by external source or player averages
# the record we are generating is a measure of determining consistency but there may be better ways
# current_year needed to determine avg line if no projected line given
def generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts={}, season_year=2024):

    #print('\n===Generate Player Records Dict===\n')
    #print('===' + player_name.title() + '===\n')

    player_records_dicts = {}

    # we only want to compare stats to current year avg if no lines given
    # bc that is closer to actual lines
    current_year = season_year

    #print('projected_lines_dict: ' + str(projected_lines_dict))
    season_part_of_interest = 'regular' # reg or post season
    # if we do not have projected lines then we can use player means/medians as lines
    # we pass in projected lines as param so at this point we already have actual projected lines or averages to determine record above and below line
    # we could get avgs from stats but we already compute avgs so we can get it from that source before running this fcn
    player_projected_lines = {}
    if player_name in projected_lines_dict.keys():
        player_all_projected_lines = projected_lines_dict[player_name]
        
        if season_part_of_interest not in player_all_projected_lines.keys():
            print('Warning: Player did not play in one part of the season (either reg or post?)!' + season_part_of_interest)
            # did not play in one part of season but played in other so use for both
            if season_part_of_interest == 'regular':
                season_part_of_interest = 'postseason'
            else: # = post so change to reg
                season_part_of_interest = 'regular'
        
        if season_part_of_interest in player_all_projected_lines.keys():
            player_projected_lines = player_all_projected_lines[season_part_of_interest]
        else:
            print('Warning: Player did not play in either part of season!')
            
    else: # no lines given, so use avgs
        print('Warning: Player ' + player_name + ' not in projected lines!')
        #print('player_medians_dicts: ' + str(player_medians_dicts))
        if len(player_medians_dicts.keys()) > 0:
            if season_year in player_medians_dicts['all'].keys():
                season_median_dicts = player_medians_dicts['all'][season_year]
                #print('season_median_dicts: ' + str(season_median_dicts))
                projected_lines_dict[player_name] = season_median_dicts

                player_avg_lines = season_median_dicts
                #print('player_avg_lines: ' + str(player_avg_lines))

                stats_of_interest = ['pts','reb','ast','3pm','blk','stl','to'] # we decided to focus on these stats to begin
                #season_part_of_interest = 'regular' # reg or post season
                for stat in stats_of_interest:
                    if season_part_of_interest in player_avg_lines.keys():
                        player_projected_lines[stat] = player_avg_lines[season_part_of_interest][stat]
                    else:
                        print('Warning: Player did not play in one part of the season (either reg or post?)!' + season_part_of_interest)
                        # did not play in one part of season but played in other so use for both
                        if season_part_of_interest == 'regular':
                            season_part_of_interest = 'postseason'
                        else: # = post so change to reg
                            season_part_of_interest = 'regular'

                        player_projected_lines[stat] = player_avg_lines[season_part_of_interest][stat]
            
            #print('player_projected_lines: ' + str(player_projected_lines))
        else: # player has not played before
            print('Warning: Player ' + player_name + ' has no stats to average!')

    #print('player_projected_lines: ' + str(player_projected_lines))

    #season_year = 2023

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        #print("\n===Year " + str(season_year) + "===\n")
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        #if season_year in player_medians_dicts['all'].keys():
        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            # all_pts_dicts = {'all':{idx:val,..},..}
            all_pts_dicts = player_season_stat_dict['pts']
            all_rebs_dicts = player_season_stat_dict['reb']
            all_asts_dicts = player_season_stat_dict['ast']
            all_threes_made_dicts = player_season_stat_dict['3pm']
            all_bs_dicts = player_season_stat_dict['blk']
            all_ss_dicts = player_season_stat_dict['stl']
            all_tos_dicts = player_season_stat_dict['to']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_medians_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_modes_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_min_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_max_dict = { 'all':0, 'home':0, 'away':0 }

                all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                #print("all_pts_dicts: " + str(all_pts_dicts))
                # all_pts_dicts = {'all':{1:20}}
                # key=condition, val={idx:stat}

                
                #compute stats from data
                # key represents set of conditions of interest eg home/away
                for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    # reset for each set of conditions

                    # for same set of conditions, count streaks for stats
                    min_line_hits = 7
                    game_sample = 10
                    current_line_hits = 10 # player reached 0+ stats in all 10/10 games. current hits is for current level of points line

                    pts_count = 0
                    r_count = 0
                    a_count = 0

                    threes_count = 0
                    b_count = 0
                    s_count = 0
                    to_count = 0

                    all_pts_counts = []
                    all_rebs_counts = []
                    all_asts_counts = []

                    all_threes_counts = []
                    all_blks_counts = []
                    all_stls_counts = []
                    all_tos_counts = []

                    # prob = 1.0
                    # while(prob > 0.7):
                    #if set_sample_size = True: # if we set a sample size only consider those settings. else take all games
                    #while(current_line_hits > min_line_hits) # min line hits is considered good odds. increase current line hits count out of 10
                        # if count after 10 games is greater than min line hits then check next level up
                    for game_idx in range(len(all_pts_dicts[conditions].values())):
                        pts = list(all_pts_dicts[conditions].values())[game_idx]
                        rebs = list(all_rebs_dicts[conditions].values())[game_idx]
                        asts = list(all_asts_dicts[conditions].values())[game_idx]

                        threes = list(all_threes_made_dicts[conditions].values())[game_idx]
                        blks = list(all_bs_dicts[conditions].values())[game_idx]
                        stls = list(all_ss_dicts[conditions].values())[game_idx]
                        tos = list(all_tos_dicts[conditions].values())[game_idx]

                        if 'pts' in player_projected_lines.keys():
                            if pts >= int(player_projected_lines['pts']):
                                pts_count += 1
                            if rebs >= int(player_projected_lines['reb']):
                                r_count += 1
                            if asts >= int(player_projected_lines['ast']):
                                a_count += 1

                            if threes >= int(player_projected_lines['3pm']):
                                threes_count += 1
                            if blks >= int(player_projected_lines['blk']):
                                b_count += 1
                            if stls >= int(player_projected_lines['stl']):
                                s_count += 1
                            if tos >= int(player_projected_lines['to']):
                                to_count += 1

                        all_pts_counts.append(pts_count)
                        all_rebs_counts.append(r_count)
                        all_asts_counts.append(a_count)

                        all_threes_counts.append(threes_count)
                        all_blks_counts.append(b_count)
                        all_stls_counts.append(s_count)
                        all_tos_counts.append(to_count)

                    # make stats counts to find consistent streaks
                    all_stats_counts_dict[conditions] = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    stats_counts = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    header_row = ['Games']
                    if 'pts' in player_projected_lines.keys():
                        over_pts_line = 'PTS ' + str(player_projected_lines['pts']) + "+"
                        over_rebs_line = 'REB ' + str(player_projected_lines['reb']) + "+"
                        over_asts_line = 'AST ' + str(player_projected_lines['ast']) + "+"
                        
                        over_threes_line = '3PM ' + str(player_projected_lines['3pm']) + "+"
                        over_blks_line = 'BLK ' + str(player_projected_lines['blk']) + "+"
                        over_stls_line = 'STL ' + str(player_projected_lines['stl']) + "+"
                        over_tos_line = 'TO ' + str(player_projected_lines['to']) + "+"
                        
                        prob_pts_row = [over_pts_line]
                        prob_rebs_row = [over_rebs_line]
                        prob_asts_row = [over_asts_line]

                        prob_threes_row = [over_threes_line]
                        prob_blks_row = [over_blks_line]
                        prob_stls_row = [over_stls_line]
                        prob_tos_row = [over_tos_line]

                        

                        for game_idx in range(len(all_pts_dicts[conditions].values())):
                            p_count = all_pts_counts[game_idx]
                            r_count = all_rebs_counts[game_idx]
                            a_count = all_asts_counts[game_idx]

                            threes_count = all_threes_counts[game_idx]
                            b_count = all_blks_counts[game_idx]
                            s_count = all_stls_counts[game_idx]
                            to_count = all_tos_counts[game_idx]

                            current_total = str(game_idx + 1)
                            current_total_games = current_total# + ' Games'
                            header_row.append(current_total_games)

                            prob_over_pts_line = str(p_count) + "/" + current_total
                            # v2 add game idx for ref and deconstruct later
                            # or could get game idx from player stat dict
                            #prob_over_pts_line = str(game_idx) + ": " + str(p_count) + "/" + current_total
                            prob_pts_row.append(prob_over_pts_line)
                            
                            prob_over_rebs_line = str(r_count) + "/" + current_total
                            prob_rebs_row.append(prob_over_rebs_line)
                            prob_over_asts_line = str(a_count) + "/" + current_total
                            prob_asts_row.append(prob_over_asts_line)

                            prob_over_threes_line = str(threes_count) + "/" + current_total
                            prob_threes_row.append(prob_over_threes_line)
                            prob_over_blks_line = str(b_count) + "/" + current_total
                            prob_blks_row.append(prob_over_blks_line)
                            prob_over_stls_line = str(s_count) + "/" + current_total
                            prob_stls_row.append(prob_over_stls_line)
                            prob_over_tos_line = str(to_count) + "/" + current_total
                            prob_tos_row.append(prob_over_tos_line)


                        prob_pts_table = [prob_pts_row]
                        prob_rebs_table = [prob_rebs_row]
                        prob_asts_table = [prob_asts_row]
                        prob_threes_table = [prob_threes_row]
                        prob_blks_table = [prob_blks_row]
                        prob_stls_table = [prob_stls_row]
                        prob_tos_table = [prob_tos_row]
                        
                        all_prob_stat_tables = [prob_pts_table, prob_rebs_table, prob_asts_table, prob_threes_table, prob_blks_table, prob_stls_table, prob_tos_table]

                        all_prob_stat_rows = [prob_pts_row,prob_rebs_row,prob_asts_row,prob_threes_row,prob_blks_row,prob_stls_row,prob_tos_row]

                        # stats counts should include all stats
                        # so we save in dict for reference
                        for stat_idx in range(len(stats_counts)):
                            #stat_counts = stats_counts[stat_idx]
                            prob_row = all_prob_stat_rows[stat_idx] #[0] # only needed first element bc previously formatted for table display
                            #print('prob_row: ' + str(prob_row))
                            # if blk, stl, or to look for 2+
                            # for all, check to see if 1+ or not worth predicting bc too risky
                            #stat_line = prob_table[0].split
                            #stat_line = int(prob_row[0].split()[1][:-1]) # [pts 16+, 1/1, 2/2, ..] -> 16
                            #print('stat_line: ' + str(stat_line))
                            stats_of_interest = ['pts','reb','ast','3pm']
                            # if stat_line < 2: # may need to change for 3 pointers if really strong likelihood to get 1
                            #     continue
                            stat_name = prob_row[0].split()[0].lower() # [pts 16+, 1/1, 2/2, ..] -> pts
                            if stat_name not in stats_of_interest:
                                continue



                            # save player stats in dict for reference
                            # save for all stats, not just streaks
                            # at first there will not be this player name in the dict so we add it
                            streak = prob_row[1:] # [pts 16+, 1/1, 2/2, ..] -> [1/1,2/2,...] or v2 [0:1/1,1:2/2,...]
                            streak_dict = {} # {game idx:streak}

                            # if not player_name in all_records_dicts.keys():
                            #     all_records_dicts[player_name] = {} # init bc player name key not in dict so if we attempt to set its val it is error

                            #     player_records_dicts = all_records_dicts[player_name] # {player name: { condition: { year: { stat: [1/1,2/2,...],.. },.. },.. },.. }

                            #     player_records_dicts[conditions] = {}
                            #     player_all_records_dicts = player_records_dicts[conditions]
                                
                            #     player_all_records_dicts[season_year] = { stat_name: streak }

                            # else: # player already in list

                            #player_records_dicts = all_records_dicts[player_name]
                            if conditions in player_records_dicts.keys():
                                #print("conditions " + conditions + " in streak tables")
                                player_all_records_dicts = player_records_dicts[conditions]
                                if season_year in player_all_records_dicts.keys():
                                    #player_all_records_dicts[season_year][stat_name] = streak

                                    player_season_records_dicts = player_all_records_dicts[season_year]
                                    if season_part in player_season_records_dicts.keys():
                                        player_season_records_dicts[season_part][stat_name] = streak
                                    else:
                                        player_season_records_dicts[season_part] = { stat_name: streak }
                                
                                else:
                                    #player_all_records_dicts[season_year] = { stat_name: streak }

                                    player_all_records_dicts[season_year] = {}
                                    player_season_records_dicts = player_all_records_dicts[season_year]
                                    player_season_records_dicts[season_part] = { stat_name: streak }

                                #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                            else:
                                #print("conditions " + conditions + " not in streak tables")
                                player_records_dicts[conditions] = {}
                                player_all_records_dicts = player_records_dicts[conditions]

                                #player_all_records_dicts[season_year] = { stat_name: streak }

                                player_all_records_dicts[season_year] = {}
                                player_season_records_dicts = player_all_records_dicts[season_year]
                                player_season_records_dicts[season_part] = { stat_name: streak }

                        # given how many of recent games we care about
                        # later we will take subsection of games with certain settings like home/away
                        # first we get all stats and then we can analyze subsections of stats
                        # eg last 10 games

    # player_records_dicts: {'all': {2023: {'regular': {'pts': ['0/1',...
    #print('player_records_dicts: ' + str(player_records_dicts))
    return player_records_dicts

# all players stats dicts = { player: year: stat name: condition: game idx: stat val }
def generate_all_players_records_dicts(all_players_stats_dicts, projected_lines_dict, season_year=2024):
    print('\n===Generate All Players Records Dicts===\n')
    all_records_dicts = {}

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, season_year=season_year)
        all_records_dicts[player_name] = player_records_dict

                
    #print('all_records_dicts: ' + str(all_records_dicts))
    return all_records_dicts


def generate_player_avg_range_dict(player_name, player_stat_dict, key):

    #print('\n===Generate Player ' + player_name.title() + ' Average Range Dict: ' + key.title() + '===\n')

    player_avg_range_dict = {}

    #print('\n===' + player_name.title() + '===\n')

    #season_year = 2023

    #print('player_stat_dict: ' + str(player_stat_dict))
    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        #print("\n===Year " + str(season_year) + "===\n")
        #print('player_full_season_stat_dict: ' + str(player_full_season_stat_dict))
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            #print("\n===Season Part " + str(season_part) + "===\n")
            #print('player_season_stat_dict: ' + str(player_season_stat_dict))

            all_pts_dicts = player_season_stat_dict['pts']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                #print("all_pts_dicts: " + str(all_pts_dicts))
                # all_pts_dicts = {'all':{1:20}}
                # key=condition, val={idx:stat}

                
                #compute stats from data
                # key represents set of conditions of interest eg home/away
                for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    #print('conditions: ' + conditions)
                    # reset for each set of conditions
                    header_row = ['Output']
                    stat_avg_ranges = [key.title()] #{pts:'',reb...}
                    # stat_medians = ['Median']
                    # stat_modes = ['Mode']
                    # stat_mins = ['Min']
                    # stat_maxes = ['Max']

                    for stat_key, stat_dict in player_season_stat_dict.items(): # stat key eg pts
                        #print('stat_key: ' + stat_key)
                        header_row.append(stat_key.upper())

                        stat_vals = list(stat_dict[conditions].values())
                        #print("stat_vals: " + str(stat_vals))

                        stat_avg_range = 0
                        if len(stat_vals) > 0:
                            if key == 'mean':
                                stat_avg_range = round(np.mean(np.array(stat_vals)), 1)
                            elif key == 'median':
                                stat_avg_range = int(np.median(np.array(stat_vals)))
                            elif key == 'mode':
                                stat_avg_range = stats.mode(stat_vals, keepdims=False)[0]
                            elif key == 'min':
                                stat_avg_range = np.min(np.array(stat_vals))
                            elif key == 'max':
                                stat_avg_range = np.max(np.array(stat_vals))
                            else:
                                print('Warning: No Avg Range Key Given! ')

                        stat_avg_ranges.append(stat_avg_range)

                        # stat_medians.append(stat_median)
                        # stat_modes.append(stat_mode)
                        # stat_mins.append(stat_min)
                        # stat_maxes.append(stat_max)



                        # save player stats in dict for reference
                        # save for all stats, not just streaks
                        # at first there will not be this player name in the dict so we add it
                        stat_name = stat_key
                        if stat_name == '3p':
                            stat_name = '3pm'

                        # for now assume if all means dicts is populated then median, mode, min and max are as well
                        # if not player_name in player_avg_range_dict.keys():
                        
                        if conditions in player_avg_range_dict.keys():
                            #print("conditions " + conditions + " in streak tables")
                            player_all_avg_range_dicts = player_avg_range_dict[conditions]

                            if season_year in player_all_avg_range_dicts.keys():
                                #player_all_avg_range_dicts[season_year][stat_name] = stat_avg_range

                                player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                                if season_part in player_season_avg_range_dicts.keys():
                                    player_season_avg_range_dicts[season_part][stat_name] = stat_avg_range
                                else:
                                    player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }

                            else:
                                #player_all_avg_range_dicts[season_year] = { stat_name: stat_avg_range }

                                player_all_avg_range_dicts[season_year] = {}
                                player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                                player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }

                            #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                        else:
                            #print("conditions " + conditions + " not in streak tables")
                            player_avg_range_dict[conditions] = {}

                            player_all_avg_range_dicts = player_avg_range_dict[conditions]
                            
                            #player_all_avg_range_dicts[season_year] = { stat_name: stat_avg_range }
                        
                            player_all_avg_range_dicts[season_year] = {}
                            player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                            player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }



                    # output_table = [header_row, stat_means, stat_medians, stat_modes, stat_mins, stat_maxes]

                    # output_title = str(conditions).title() + ", " + str(season_year)
                    # if re.search('before',conditions):
                    #     output_title = re.sub('Before','days before next game', output_title).title()
                    # elif re.search('after',conditions):
                    #     output_title = re.sub('After','days after previous game', output_title).title()
                    
                    # print("\n===" + player_name.title() + " Average and Range===\n")
                    # print(output_title)
                    # print(tabulate(output_table))

    # player_avg_range_dict: {'all': {2023: {'regular': {'pts': 33, 'reb': 1...
    #print('player_avg_range_dict: ' + str(player_avg_range_dict))
    return player_avg_range_dict


def generate_all_players_avg_range_dicts(all_players_stats_dicts):

    #print('\n===Generate All Players Averages===\n')

    all_means_dicts = {}
    all_medians_dicts = {}
    all_modes_dicts = {}
    all_mins_dicts = {}
    all_maxes_dicts = {}

    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_all_avg_range_dicts = {'mean':{},'median':{},'mode':{},'min':{},'max':{}}
        for key in player_all_avg_range_dicts.keys():
            player_all_avg_range_dicts[key] = generate_player_avg_range_dict(player_name, player_stat_dict, key)
        
        player_avg_range_dict = generate_player_avg_range_dict(player_name, player_stat_dict)
        # todo: reorganize
        all_means_dicts[player_name] = generate_player_avg_range_dict(player_name, player_stat_dict)
        all_medians_dicts[player_name] = player_avg_range_dict['median']
        all_modes_dicts[player_name] = player_avg_range_dict['mode']
        all_mins_dicts[player_name] = player_avg_range_dict['min']
        all_maxes_dicts[player_name] = player_avg_range_dict['max']

        


    # print('all_means_dicts: ' + str(all_means_dicts))
    # print('all_medians_dicts: ' + str(all_medians_dicts))
    # print('all_modes_dicts: ' + str(all_modes_dicts))

    all_avgs_dicts = { 'mean': all_means_dicts, 'median': all_medians_dicts, 'mode': all_modes_dicts, 'min': all_mins_dicts, 'max': all_maxes_dicts }
    #print('all_avgs_dicts: ' + str(all_avgs_dicts))
    return all_avgs_dicts

# if player names is blank, use all players found in raw projected lines
# use all_players_espn_ids to get teams
def generate_projected_lines_dict(raw_projected_lines, all_players_espn_ids={}, player_teams={}, player_names=[], read_new_teams=False, cur_yr=''):
    #print('\n===Generate Projected Lines Dict===\n')
    #print('raw_projected_lines: ' + str(raw_projected_lines))
    # need data type and input type to get file name
    # data_type = "Player Lines"

    # # optional setting game date if processing a day in advance
    # todays_games_date_str = '' # format: m/d/y, like 3/14/23. set if we want to look at games in advance
    # todays_games_date_obj = datetime.today() # by default assume todays game is actually today and we are not analyzing in advance
    # if todays_games_date_str != '':
    #     todays_games_date_obj = datetime.strptime(todays_games_date_str, '%m/%d/%y')
    
    # input_type = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day)

    # # raw projected lines in format: [['Player Name', 'O 10 +100', 'U 10 +100', 'Player Name', 'O 10 +100', 'U 10 +100', Name', 'O 10 +100', 'U 10 +100']]
    # raw_projected_lines = reader.extract_data(data_type, input_type, extension='tsv', header=True) # tsv no header
    # print("raw_projected_lines: " + str(raw_projected_lines))

    # if len(player_names) == 0:
    #     player_names = determiner.determine_all_player_names(raw_projected_lines)

    if len(player_teams.keys()) == 0:
        player_teams = reader.read_all_players_teams(all_players_espn_ids, read_new_teams) # only read team from internet if not saved

    # convert raw projected lines to projected lines
    projected_lines = reader.read_projected_lines(raw_projected_lines, player_teams, cur_yr=cur_yr)

    projected_lines_dict = {}
    header_row = projected_lines[0]
    for player_lines in projected_lines[1:]:
        player_name = player_lines[0].lower()
        projected_lines_dict[player_name] = dict(zip(header_row[1:],player_lines[1:]))
    
    #print("projected_lines_dict: " + str(projected_lines_dict))
    return projected_lines_dict


# show data in columns for viewing
# we use player_stat_dicts to get game idxs for reference to records/streaks
def generate_player_outcome_data(condition, year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dicts={}):

    print('\n===Generate Player Outcome Data===\n')
    #print('condition: ' + str(condition))
    #print('player_records_dict: ' + str(player_records_dict))

    record_key = condition + ' record'
    player_outcome_dict[record_key] = ''

    if condition in player_records_dict.keys():
        #print("current_teammates_str " + current_teammates_str + " in all records dicts")
        # init record condition_record format ['1/1',..]
        # desired format 1/1,..
        # remove brackets and quotes
        season_part = 'regular'
        condition_year_record = player_records_dict[condition][year][season_part]
        condition_record = ''
        if stat_name in condition_year_record.keys():
            condition_record = player_records_dict[condition][year][season_part][stat_name]
            condition_record = determiner.determine_record_outline(condition_record)
            condition_record = writer.convert_list_to_string(condition_record)
            player_outcome_dict[record_key] = str(condition_record) #condition + ': ' + str(teammates_record)
        else:
            print('Warning: stat_name ' + stat_name + ' not in condition record ' + str(condition_year_record) + '!')

        # print game idxs beside record bc simplest
        game_idxs = list(player_stat_dicts[year][season_part][stat_name][condition].keys())
        record_idx_key = condition + ' record idx'
        player_outcome_dict[record_idx_key] = str(game_idxs)
    else:
        print("condition " + condition + " NOT in all records dicts")

    #print("pre_dict: " + str(pre_dict))
    # mean_key = condition + ' mean'
    # player_outcome_dict[mean_key] = ''
    # median_key = condition + ' median'
    # player_outcome_dict[median_key] = ''
    # mode_key = condition + ' mode'
    # player_outcome_dict[mode_key] = ''
    # min_key = condition + ' min'
    # player_outcome_dict[min_key] = ''
    # max_key = condition + ' max'
    # player_outcome_dict[max_key] = ''

    
    #print("all_means_dicts: " + str(all_means_dicts))
    # if condition in player_means_dicts.keys():
    #     condition_mean = player_means_dicts[condition][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
    #     player_outcome_dict[mean_key] = condition_mean

    # if condition in player_medians_dicts.keys():
    #     condition_median = player_medians_dicts[condition][year][stat_name]
    #     player_outcome_dict[median_key] = condition_median

    # if condition in player_modes_dicts.keys():
    #     condition_mode = player_modes_dicts[condition][year][stat_name]
    #     player_outcome_dict[mode_key] = condition_mode

    # if condition in player_mins_dicts.keys():
    #     condition_min = player_mins_dicts[condition][year][stat_name]
    #     player_outcome_dict[min_key] = condition_min

    # if condition in player_maxes_dicts.keys():
    #     condition_max = player_maxes_dicts[condition][year][stat_name]
    #     player_outcome_dict[max_key] = condition_max


# prediction is really a list of features that we must assess to determine the probability of both/all outcomes
#def generate_player_prediction(player_name, player_season_logs):
# all_players_season_logs = {player name:{year:{condition:{stat:[]}}}}
# player_season_logs = {}
def generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position='', all_matchup_data=[], all_box_scores={}, player_team='', player_stat_dict={}, season_year=2024):

    print('\n===Generate Player Outcome===\n')

    print('===' + player_name.title() + '===')
    print('===' + player_team.upper() + '===\n')

    player_all_outcomes_dict = {} # {stat name:{outcome,record,avg,range,matchup}}

    # organize external data into internal structure
    if len(player_stat_dict.keys()) == 0: # use given stat dict if available, else get from logs
        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, all_box_scores, player_team, season_year=season_year)

    


    player_all_avg_range_dicts = {'mean':{},'median':{},'mode':{},'min':{},'max':{}}
    for key in player_all_avg_range_dicts.keys():
        player_all_avg_range_dicts[key] = generate_player_avg_range_dict(player_name, player_stat_dict, key)
    #player_avg_range_dict = generate_player_all_avg_range_dicts(player_name, player_stat_dict)
    #print('player_all_avg_range_dicts: ' + str(player_all_avg_range_dicts))
    player_means_dicts = player_all_avg_range_dicts['mean']
    player_medians_dicts = player_all_avg_range_dicts['median']
    player_modes_dicts = player_all_avg_range_dicts['mode']
    player_mins_dicts = player_all_avg_range_dicts['min']
    player_maxes_dicts = player_all_avg_range_dicts['max']

    # determine the record over projected line or avg stat val
    #print('projected_lines_dict before records: ' + str(projected_lines_dict))
    player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts, season_year=season_year)


    # determine the stat val with record above 90%
    # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
    #player_consistent_stat_vals = generate_consistent_stat_vals(player_name, player_stat_dict)
    #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
    #writer.display_consistent_stats(all_player_consistent_stats)

    # if we have a game log for this player, 
    # get prev game to compute time_after condition
    time_after = '0 after' # could be '0' or '' bc init for case of new player with no log
    #current_season_log = pd.DataFrame() # init current season log as df
    if len(player_season_logs.values()) > 0:
        current_season_log = pd.DataFrame(player_season_logs[str(season_year)])
        current_season_log.index = current_season_log.index.map(str)
    
        #season_year = 2023
        prev_game_date_obj = determiner.determine_prev_game_date(current_season_log, season_year) # exclude all star and other special games
        # prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + season_year # eg 'wed 2/15' to '2/15/23'
        # prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%y')
        days_after_prev_game = (todays_games_date_obj - prev_game_date_obj).days

        time_after = str(days_after_prev_game) + ' after'
    else:
        print('Warning: player ' + player_name.title() + ' has not played before!')


    player_lines = {}
    loc_of_interest = '' # if we want to see both locations we know only home/away
    opponent = '' # if we want to see all opponents we need all opp keys to follow unique format or list of all possible opponents to find keys
    if player_name in projected_lines_dict.keys():
        #print('projected_lines_dict: ' + str(projected_lines_dict))
        player_lines['regular'] = projected_lines_dict[player_name]
        reg_player_lines = player_lines['regular']
        if 'loc' in reg_player_lines.keys():
            loc_of_interest = reg_player_lines['loc'].lower()
        if 'opp' in reg_player_lines.keys():
            opponent = reg_player_lines['opp'].lower()
    #print('player_lines: ' + str(player_lines))

    
    current_dow = todays_games_date_obj.strftime('%a').lower()

    current_teammates_str = '' # if we are given current teamates of interest then we can focus on these, else show all


    all_matchups_dicts = {} # store all matchup data (avg and rank) for each opponent/team


    # make an outcome for each stat
    #print('player_stat_dict: ' + str(player_stat_dict))
    stats_of_interest = ['pts','reb','ast','3pm'] # this is if we have all the lines available but we only want subset. but if some of the lines are unavailable then print out their outcomes using their median as the line but only if they are a stat of interest
    #year = 2023
    for season_part, season_part_lines in player_lines.items():

        print('\n===Season Part: ' + season_part + '===\n')
        #print('season_part_lines: ' + str(season_part_lines))

        for stat_name in stats_of_interest:
            player_outcome_dict = {} # fields: 'outcome', 'streak', 'record', 'avg', 'range', 'matchup'

            if season_part not in season_part_lines.keys():
                if season_part == 'regular':
                    season_part = 'postseason'
                else:
                    season_part = 'regular'

            stat_line = season_part_lines[season_part][stat_name]
            player_outcome = player_name.title() + ' ' + str(stat_line) + '+ ' + stat_name # initially express over/under as over+ with assumption that under=100-over bc we are displaying possibility before assessing probability
            #print('player_outcome: ' + player_outcome)
            player_outcome_dict['outcome'] = player_outcome

            overall_record = ''
            if season_part in player_records_dict['all'][season_year].keys():
                overall_record = player_records_dict['all'][season_year][season_part][stat_name] # { 'player name': { 'all': {year: { pts: '1/1,2/2..', stat: record, .. },...}, 'home':{year:{ stat: record, .. },.. }, 'away':{year:{ stat: record, .. }} } }
                #print('overall_record: ' + str(overall_record))
                overall_record = determiner.determine_record_outline(overall_record)
                player_outcome_dict['overall record'] = overall_record

            # # add avg and range in prediction, for current condition, all
            
            # if location is blank bc we do not have future game
            # if we want to see all locations we can look in player stats dict
            # but here we only show the location for the game of interest
            # what if we want to show all locations, opponents, lineups, etc?
            # we should have a separate function 
            # show all locs unless we have loc of interest
            locs = ['away','home']
            if loc_of_interest != '':
                locs = [loc_of_interest]

            for location in locs:
                location_record = ''
                if season_part in player_records_dict[location][season_year].keys():
                    location_record = player_records_dict[location][season_year][season_part][stat_name]
                    location_record = determiner.determine_record_outline(location_record)
                    record_key = location + ' record'
                    player_outcome_dict[record_key] = str(location_record) #v1: location + ': ' + str(location_record)

                # add avg and range in prediction, for current condition, all



            player_outcome_dict['opponent record'] = ''
            #print('Add opponent ' + opponent + ' record. ')
            #print("all_records_dicts: " + str(all_records_dicts))
            if opponent in player_records_dict.keys():
                opp_record = ''
                if season_part in player_records_dict[opponent][season_year].keys():
                    opp_record = player_records_dict[opponent][season_year][season_part][stat_name]
                    player_outcome_dict['opponent record'] = opponent + ': ' + str(opp_record)

            # add avg and range in prediction, for current condition, all
            
            player_outcome_dict['time after record'] = ''
            if time_after in player_records_dict.keys():
                time_after_record = ''

                if season_year in player_records_dict[time_after].keys() and season_part in player_records_dict[time_after][season_year].keys():
                    time_after_record = player_records_dict[time_after][season_year][season_part][stat_name]
                    time_after_record = determiner.determine_record_outline(time_after_record)
                    player_outcome_dict['time after record'] = time_after + ': ' + str(time_after_record)


            player_outcome_dict['day record'] = ''
            if current_dow in player_records_dict.keys():
                #print("current_dow " + current_dow + " in all records dicts")
                dow_record = ''
                if season_year in player_records_dict[current_dow].keys() and season_part in player_records_dict[current_dow][season_year].keys():
                    dow_record = player_records_dict[current_dow][season_year][season_part][stat_name]
                    player_outcome_dict['day record'] = current_dow + ': ' + str(dow_record)
            else:
                print("current_dow " + current_dow + " NOT in all records dicts")
            #print("pre_dict: " + str(pre_dict))

            #find matchups true
            #print('all_matchup_data: ' + str(all_matchup_data))
            if len(all_matchup_data) > 0:

                print("\n===Find Matchup for Outcome===\n")

                # stat = streak[0].split(' ')[0].lower() #'pts'
                # print("stat: " + stat)
                #all_matchup_ratings = { 'all':{}, 'pg':{}, 'sg':{}, 'sf':{}, 'pf':{}, 'c':{} } # { 'pg': { 'values': [source1,source2,..], 'ranks': [source1,source2,..] }, 'sg': {}, ... }
                #position_matchup_rating = { 'values':[], 'ranks':[] } # comparing results from different sources
                # current_matchup_data = { pos: [source results] }
                #  sources_results={values:[],ranks:[]}
                current_matchup_data = determiner.determine_matchup_rating(opponent, stat_name, all_matchup_data) # first show matchups from easiest to hardest position for stat. 
                
                # loop thru position in matchup data by position
                # to get matchup table for a given opponent and position
                matchup_dict = {} # {pg:0, sg:0, ..}, for given opponent
                #print('current_matchup_data: ' + str(current_matchup_data))
                for pos, sources_results in current_matchup_data.items():
                    #print("Position: " + pos.upper())

                    matchup_table_header_row = ['Sources'] # [source1, source2, ..]
                    num_sources = len(sources_results['averages']) #len(source_vals)

                    for source_idx in range(num_sources):
                        source_num = source_idx + 1
                        source_header = 'Source ' + str(source_num)
                        matchup_table_header_row.append(source_header)

                    #{pg:0, sg:0, ..}, for given opponent
                    ranks = sources_results['ranks']
                    s1_matchup_rank = 0
                    s2_matchup_rank = 0
                    s3_matchup_rank = 0
                    if len(ranks) > 0:
                        s1_matchup_rank = ranks[0] #for example test take idx 0
                    if len(ranks) > 1:
                        s2_matchup_rank = ranks[1]
                    if len(ranks) > 2:
                        s3_matchup_rank = ranks[2]
                    
                    # matchup_dict = { pg: { s1: 0 }, sg: { s1: 0 }, .. }
                    matchup_dict[pos] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank }

                    matchup_table = [matchup_table_header_row]
                    for result, source_vals in sources_results.items():
                        source_vals.insert(0, result.title())
                        matchup_table.append(source_vals)


                    print(tabulate(matchup_table))
                

                # ====== once for each outcome, after created matchup dict for opponent ======

                # add matchup dict to all matchup dicts so we can access matchups by opponent, stat and position
                # we could just populate all matchups dict from all matchups data at the beginning instead of this loop for each streak
                #print("matchup_dict: " + str(matchup_dict))
                # matchup_dict = { pg: { s1: 0, s2: 0, .. }, sg: { s1: 0 }, .. }
                for pos, rank_dict in matchup_dict.items():
                    s1_matchup_rank = rank_dict['s1']
                    s2_matchup_rank = rank_dict['s2']
                    s3_matchup_rank = rank_dict['s3']
                    # init dicts
                    #print("all_matchups_dicts: " + str(all_matchups_dicts))

                    rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                    matchup_rank_mean = rank_avgs['mean']
                    matchup_rank_combined_mean = rank_avgs['combined mean']

                    if not pos in all_matchups_dicts.keys():

                        #print('position ' + pos + ' not in all matchups so it is first loop')
                        all_matchups_dicts[pos] = {}
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        all_matchups_dicts[pos][stat_name] = {}
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
                    else: # pos in matchups dict so check for stat in pos
                        print('position ' + pos + ' in matchups dict')

                        # all_matchups_dicts = { 'pg': {} }
                        if not stat_name in all_matchups_dicts[pos].keys():
                            print('stat_name ' + stat_name + ' not in position so it is new stat_name')

                            # rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                            # matchup_rank_mean = rank_avgs['mean']
                            # matchup_rank_combined_mean = rank_avgs['combined mean']

                            all_matchups_dicts[pos][stat_name] = {}
                            all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                            #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        else: # stat_name is in pos matchups so check if opp in stats
                            print('stat_name ' + stat_name + ' in position matchups dict')
                            if not opponent in all_matchups_dicts[pos][stat_name].keys():
                                print('opponent ' + opponent + ' not in stat so it is new opponent')

                                # rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                                # matchup_rank_mean = rank_avgs['mean']
                                # matchup_rank_combined_mean = rank_avgs['combined mean']

                                all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                                #print("all_matchups_dicts: " + str(all_matchups_dicts))
                            else:
                                print('opponent rating added already so continue to next streak')
                                break

                    # if we do not have rank yet then set it
                    # if not opponent in all_matchups_dicts[pos][stat].keys():
                    #     all_matchups_dicts[pos][stat][opponent] = rank
                    
                
                
                # if key not in dict then add it
                #if not opponent in all_matchups_dicts.keys():
                    #all_matchups_dicts[opponent] = matchup_dict # init bc player name key not in dict so if we attempt to set its val it is error

                    #opponent_matchups_dicts = all_matchups_dicts[opponent] # {team name: { position : rank } }

                #print("all_matchups_dicts: " + str(all_matchups_dicts))



                # add matchups in prediction, for position
                # currently pre_dict from valid streaks but eventually will be narrowed down further into valid preidctions=streaks+matchups+avg+range etc
                print('\n===Add Matchups to Outcome===\n')
                print('We got matchups so add matchups to outcome. ') # should we do this for each player or even each condition or can we do this 1 big loop after we populate all matchups dict?
                #print("all_matchups_dicts: " + str(all_matchups_dicts))
                #print("projected_lines_dict: " + str(projected_lines_dict))


                #player_lines = projected_lines_dict[player_name]
                #opponent = player_lines['OPP'].lower()

                #position = all_player_positions[player_name] #'pg' # get player position from easiest source such as game log webpage already visited
                #print("position from all_player_positions: " + player_position)
                player_outcome_dict['s1 matchup'] = ''
                player_outcome_dict['s2 matchup'] = ''
                player_outcome_dict['s3 matchup'] = ''
                player_outcome_dict['matchup mean'] = ''
                player_outcome_dict['matchup combined mean'] = ''

                # pre_dict['matchup relative rank'] = '' # x/5, 5 positions
                # pre_dict['matchup combined relative rank'] = '' # x/3, guard, forward, center bc often combined
                # pre_dict['matchup overall mean'] = ''

                if opponent in all_matchups_dicts[player_position][stat_name].keys():
                    s1_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s1'] # stat eg 'pts' is given for the streak
                    print("s1_matchup_rank: " + str(s1_matchup_rank))
                    s2_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s2'] # stat eg 'pts' is given for the streak
                    s3_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s3'] # stat eg 'pts' is given for the streak
                    player_outcome_dict['s1 matchup'] = s1_matchup_rank
                    player_outcome_dict['s2 matchup'] = s2_matchup_rank
                    player_outcome_dict['s3 matchup'] = s3_matchup_rank

                    matchup_rank_mean = all_matchups_dicts[player_position][stat_name][opponent]['mean'] # stat eg 'pts' is given for the streak
                    matchup_rank_combined_mean = all_matchups_dicts[player_position][stat_name][opponent]['combined mean'] # stat eg 'pts' is given for the streak
                    player_outcome_dict['matchup mean'] = matchup_rank_mean
                    player_outcome_dict['matchup combined mean'] = matchup_rank_combined_mean

                    # Determine Relative Rank
                    # opp_matchup_dict = {} # {pos:{stat:rank,..},..}
                    # print('all_matchups_dicts: ' + str(all_matchups_dicts))
                    # for pos, pos_matchup_dict in all_matchups_dicts.items():
                    #     if pos not in opp_matchup_dict.keys():
                    #         opp_matchup_dict[pos] = {}
                    #     opp_matchup_dict[pos][stat] = pos_matchup_dict[stat][opponent]
                    # print('opp_matchup_dict: ' + str(opp_matchup_dict))

                    # matchup_relative_rank = 1 # 1-5 bc 5 positions, from hardest to easiest bc defense
                    # pre_dict['matchup relative rank'] = matchup_relative_rank 
                else:
                    print("Warning: opponent " + opponent + " not found in all matchups dict! ")


            #if find players in games true we will have populated all_box_scores
            #print('all_box_scores: ' + str(all_box_scores))
            if len(all_box_scores.keys()) > 0:

                print("\n===Find Players in Games for Outcome===\n")

                if len(current_teammates_str) > 0:
                    # use given list of current teammates of interest
                    print('current_teammates_str: ' + str(current_teammates_str))

                    generate_player_outcome_data(current_teammates_str, season_year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict) # assigns data to outcome dictionary
                    
                else: # show all teammates bc we do not know current teammates

                    for condition in player_records_dict.keys():

                        if re.search('\.',condition): # eg 'j. brown sg', condition matching list of teammates has player first initial with dot after

                            generate_player_outcome_data(condition, season_year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict)



            if season_part not in player_all_outcomes_dict.keys():
                player_all_outcomes_dict[season_part] = {}
            player_all_outcomes_dict[season_part][stat_name] = player_outcome_dict

    #print('player_all_outcomes_dict: ' + str(player_all_outcomes_dict))
    return player_all_outcomes_dict

# determine min margin bt ok val and min stat val
# need for all possible stat vals or just ok val
# but ok val is found later
# we will eventually need min margin for each option
# so simply add in extensible now
# we can choose to hide columns to reduce clutter
def generate_min_margin(init_val, stat_dict):
    #print('\n===Generate Min Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    #print('stat_vals: ' + str(stat_vals))

    min_val = 0 # init
    if len(stat_vals) > 0:
        min_val = min(stat_vals)
    else:
        print('Warning: No stat vals while generating min margin!')

    min_margin = min_val - init_val

    #print('min_margin: ' + str(min_margin))
    return min_margin


def generate_mean_margin(init_val, stat_dict):
    #print('\n===Generate Mean Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    #print('stat_vals: ' + str(stat_vals))

    mean_val = 0 # init
    if len(stat_vals) > 0:
        mean_val = round(np.mean(np.array(stat_vals)), 1)
    else:
        print('Warning: No stat vals while generating min margin!')

    mean_margin = mean_val - init_val

    #print('mean_margin: ' + str(mean_margin))
    return mean_margin


def generate_margin(init_val, stat_dict, margin_type='min'):
    #print('\n===Generate ' + margin_type.title() + ' Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    #print('stat_vals: ' + str(stat_vals))

    val = 0 # init
    margin = 0
    if len(stat_vals) > 0:
        if margin_type == 'mean':
            val = np.mean(np.array(stat_vals))
            #print('val: ' + str(val))
            # we want to round to whole number for easy comparison and we cannot be certain with any more accuracy due to other conditions
            margin = round(val - init_val) 
        else:
            val = min(stat_vals)
            margin = val - init_val
        
    else:
        print('Warning: No stat vals while generating min margin!')

    

    #print('margin: ' + str(margin))
    return margin




# generate dict of sample sizes for each condition
# so we know weight of sample based on size
# although we also want a way to get sample size for conditions decided later
# such as like combined conditions when multiple conditions line up
# could also use determine sample size 
# by passing player stat records with matching conditions
def generate_sample_size_dict(player_stat_records, player_name=''):

    print('\n===Generate Sample Size Dict ' + player_name.title() + '===\n')

    ss_dict = {}

    return ss_dict


# consistency=0.9 is desired probability of player reaching stat val
#consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
#player_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_consistent_stat_vals(player_name, player_stat_dict, player_stat_records={}, consistency=0.9):
    
    print('\n===Generate Consistent Stat Vals===\n')

    if len(player_stat_records) == 0:
        player_stat_records = generate_player_stat_records(player_name, player_stat_dict)

    
    consistent_stat_vals = {}

    for condition, condition_stat_records in player_stat_records.items():
        #print("\n===Condition " + str(condition) + "===\n")

        for season_year, full_season_stat_dicts in condition_stat_records.items():
            #print("\n===Year " + str(season_year) + "===\n")

            for season_part, season_stat_dicts in full_season_stat_dicts.items():
                #print("\n===Season Part " + str(season_part) + "===\n")

                for stat_name, stat_records in season_stat_dicts.items():
                    #print("\n===Stat Name " + str(stat_name) + "===\n")
                    #print('stat_records: ' + str(stat_records))

                    # get prob from 0 to 1 to compare to desired consistency
                    consistent_stat_val = 0
                    prob_stat_reached = 1.0
                    consistent_stat_prob = 1.0
                    
                    for stat_val in range(len(stat_records)):
                        #print("\n===Stat Val " + str(stat_val) + "===")
                        # gen prob reached from string record
                        record = stat_records[stat_val] # eg x/y=1/1
                        #print('record: ' + str(record))
                        prob_stat_reached = generate_prob_stat_reached(record)

                        if prob_stat_reached < consistency:
                            break

                        consistent_stat_val = stat_val
                        consistent_stat_prob = prob_stat_reached

                    # print('consistent_stat_val: ' + str(consistent_stat_val))
                    # print('consistent_stat_prob: ' + str(consistent_stat_prob))

                    # determine second consistent val
                    # we may want to loop for x consistent vals to see trend and error margin
                    second_consistent_stat_val = consistent_stat_val - 1
                    
                    
                    if consistent_stat_val == 0: # usually we want lower stat at higher freq but if 0 then we want to see higher stat for reference
                        # if 3pm
                        if stat_name == '3pm':
                            second_consistent_stat_val = 1
                        else:
                            second_consistent_stat_val = 2
                    elif consistent_stat_val == 1:
                        second_consistent_stat_val = 2 # bc we want to see available projected probability
                    elif stat_name != '3pm': # above for 0,1 all stats are treated similar but 3pm takes all 2+
                        if consistent_stat_val > 2 and consistent_stat_val < 5: # 3,4 na
                            second_consistent_stat_val = 2
                        elif consistent_stat_val > 5 and consistent_stat_val < 8: # 6,7 na
                            second_consistent_stat_val = 5
                        elif consistent_stat_val == 9: # 9 na
                            second_consistent_stat_val = 8

                        # ensure val is available
                        ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
                        if second_consistent_stat_val not in ok_stat_vals:
                            second_consistent_stat_val -= 1

                    # if consistent_stat_val=0 or 1 we see greater val
                    if second_consistent_stat_val > consistent_stat_val: # if consistent_stat_val=0 or 1 we see greater val
                        # if player did not reach higher stat val record=''
                        if len(stat_records) > second_consistent_stat_val:
                            record = stat_records[second_consistent_stat_val]
                        else:
                            record = ''
                    else:
                        record = stat_records[second_consistent_stat_val]
                    second_consistent_stat_prob = generate_prob_stat_reached(record)

                    # print('second_consistent_stat_val: ' + str(second_consistent_stat_val))
                    # print('second_consistent_stat_prob: ' + str(second_consistent_stat_prob))

                    # determine higher and lower stat val probs for ref

                    # determine prob of regseason consistent val in postseason

                    # also determine prob of postseason consistent val in regseason


                    # determine min margin bt ok val and min stat val
                    # need for all possible stat vals or just ok val
                    # but ok val is found later
                    # we will eventually need min margin for each option
                    # so simply add in extensible now
                    # we can choose to hide columns to reduce clutter
                    stat_dict = player_stat_dict[season_year][season_part][stat_name][condition]
                    min_margin = generate_margin(consistent_stat_val, stat_dict)
                    second_min_margin = generate_margin(second_consistent_stat_val, stat_dict)

                    mean_margin = generate_margin(consistent_stat_val, stat_dict, 'mean')
                    second_mean_margin = generate_margin(second_consistent_stat_val, stat_dict, 'mean')


                    # save data for analysis, sorting and filtering
                    consistent_stat_dict = { 'prob val': consistent_stat_val, 'prob': consistent_stat_prob, 'second prob val': second_consistent_stat_val, 'second prob': second_consistent_stat_prob, 'min margin': min_margin, 'second min margin': second_min_margin, 'mean margin': mean_margin, 'second mean margin': second_mean_margin  }
                    
                    if condition in consistent_stat_vals.keys():
                        #print("conditions " + conditions + " in streak tables")
                        player_condition_consistent_stat_vals = consistent_stat_vals[condition]
                        if season_year in player_condition_consistent_stat_vals.keys():
                            #player_condition_consistent_stat_vals[season_year][stat_name] = consistent_stat_dict

                            player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                            if season_part in player_season_condition_consistent_stat_vals.keys():
                                player_season_condition_consistent_stat_vals[season_part][stat_name] = consistent_stat_dict
                            else:
                                player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }
                        
                        else:
                            #player_condition_consistent_stat_vals[season_year] = { stat_name: consistent_stat_dict }

                            player_condition_consistent_stat_vals[season_year] = {}
                            player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                            player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }

                        #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                    else:
                        #print("conditions " + conditions + " not in streak tables")
                        consistent_stat_vals[condition] = {}
                        player_condition_consistent_stat_vals = consistent_stat_vals[condition]
                        
                        #player_condition_consistent_stat_vals[season_year] = { stat_name: consistent_stat_dict }

                        player_condition_consistent_stat_vals[season_year] = {}
                        player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                        player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }

    # ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    # add prob of reaching reg season val in postseason, if different consistent vals

    #consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
    #print('consistent_stat_vals: ' + str(consistent_stat_vals))
    return consistent_stat_vals


# all_player_consistent_stats = {} same format as stat records, 
# condition, year, stat name
# for display
# simply flatten bottom level of dict
# by adding its key to header of level above
def generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts, player_teams={}, season_year=2024):
    print("\n===Generate All Consistent Stats Dicts===\n")
    #print('all_player_consistent_stats: ' + str(all_player_consistent_stats))
    #print('all_player_stat_records: ' + str(all_player_stat_records))

    player_consistent_stat_data_headers = ['Player', 'S Name', 'Stat', 'Prob', '2nd Stat', '2nd Prob', 'PS', 'PP', '2nd PS', '2nd PP', 'OK Val', 'OK P', 'OK PP']
    final_consistent_stats = [player_consistent_stat_data_headers] # player name, stat name, consistent stat, consistent stat prob

    # so we can sort from high to low prob
    all_consistent_stat_dicts = [] 
    consistent_stat_dict = {}

    # {player:stat:condition:val,prob,margin...}
    # where condition could be year, part or sub-condition like location
    all_consistent_stats_dict = {} # organize by stat, more flexible than old version list
    # for each player
    # for each stat
    # get consistent stat data for
    # year
    # part
    # condition

    # populate consistent_stat_dict and append to all_consistent_stat_dicts
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val': 15, 'prob': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    # all_player_consistent_stats, consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
    years_of_interest = [season_year, season_year-1]
    for player_name, player_consistent_stats in all_player_consistent_stats.items():
        #print('\n===' + player_name.title() + '===\n')

        all_consistent_stats_dict[player_name] = {}

        player_team = ''
        if player_name in player_teams.keys():
            player_team = player_teams[player_name]

        # for now, show only conditon=all
        # give option to set condition and sort by condition
        conditions_of_interest = ['all']
        for condition, condition_consistent_stats in player_consistent_stats.items():
            #print('\n===' + condition.title() + '===\n')

            if condition in conditions_of_interest:

                for year, year_consistent_stats in condition_consistent_stats.items():
                    #print('\n===' + str(year) + '===\n')

                    if year in years_of_interest:

                        # first look at full season, then postseason
                        # consistent_stat_dict will need another level for the year or season part
                        # so we can loop thru in order
                        # or we can change order of input dict
                        season_part_consistent_stats = year_consistent_stats['full'] # old version manually set season parts but now we just loop thru all season parts
                        part_consistent_stat_dict = {}
                        for season_part, season_part_consistent_stats in year_consistent_stats.items():
                            #print('\n===season_part: ' + season_part + '===\n')

                            part_consistent_stat_dict[season_part] = {}

                            for stat_name in season_part_consistent_stats.keys():
                                #print('\n===' + stat_name.upper() + '===\n')

                                

                                # use consistent_stat_dict to sort
                                #consistent_stat_dict = {'player name':player_name, 'stat name':stat_name, 'team':player_team}
                                
                                # fields of interest
                                prob_stat_key = 'prob val' #defined in loop
                                prob_key = 'prob'
                                min_margin_key = 'min margin'
                                mean_margin_key = 'mean margin'

                                second_prob_stat_key = 'second ' + prob_stat_key
                                second_prob_key = 'second ' + prob_key
                                second_min_margin_key = 'second ' + min_margin_key
                                second_mean_margin_key = 'second ' + mean_margin_key

                                #player_consistent_stat_data = [player_name, stat_name]

                                # player name, stat name, consistent stat, consistent stat prob
                                #consistent_stat_dict['team'] = player_team already defined when init dict

                                player_consistent_stat_data = [player_name, stat_name]#, full_consistent_stat, full_consistent_stat_prob, full_second_consistent_stat, full_second_consistent_stat_prob, post_consistent_stat, post_consistent_stat_prob, post_second_consistent_stat, post_second_consistent_stat_prob, player_team]

                                # simply flatten bottom level of dict
                                # by adding its key to header of level above
                                # eg in this case blank for full season and post for postseason
                                
                                season_part_key = re.sub('ular|season','',season_part) # full, reg, or post
                                # make full blank to save space and differentiate from reg and post?
                                # make sure to strip blank space at start of string
                                # or add space in other part of string for season parts
                                
                                prob_stat_dict = year_consistent_stats[season_part][stat_name]
                                #print('prob_stat_dict: ' + str(prob_stat_dict))

                                prob_val = prob_stat_dict[prob_stat_key]
                                consistent_stat = prob_val
                                
                                prob = prob_stat_dict[prob_key]
                                #print('prob: ' + str(prob))
                                consistent_stat_prob = round(prob * 100)
                                #print('consistent_stat_prob: ' + str(consistent_stat_prob))

                                second_consistent_stat = prob_stat_dict[second_prob_stat_key]
                                second_consistent_stat_prob = round(prob_stat_dict[second_prob_key] * 100)

                                min_margin = prob_stat_dict[min_margin_key]
                                second_min_margin = prob_stat_dict[second_min_margin_key]
                                mean_margin = round(prob_stat_dict[mean_margin_key])
                                second_mean_margin = round(prob_stat_dict[second_mean_margin_key])

                                # set keys for each field for each part of season and for each season
                                part_prob_stat_key = season_part_key + ' ' + prob_stat_key
                                part_prob_key = season_part_key + ' ' + prob_key
                                part_second_prob_stat_key = season_part_key + ' ' + second_prob_stat_key
                                part_second_prob_key = season_part_key + ' ' + second_prob_key

                                part_min_margin_key = season_part_key + ' ' + min_margin_key
                                part_second_min_margin_key = season_part_key + ' ' + second_min_margin_key
                                part_mean_margin_key = season_part_key + ' ' + mean_margin_key
                                part_second_mean_margin_key = season_part_key + ' ' + second_mean_margin_key
                                
                                consistent_stat_dict[part_prob_stat_key] = consistent_stat
                                consistent_stat_dict[part_prob_key] = consistent_stat_prob
                                consistent_stat_dict[part_second_prob_stat_key] = second_consistent_stat
                                consistent_stat_dict[part_second_prob_key] = second_consistent_stat_prob

                                consistent_stat_dict[part_min_margin_key] = min_margin
                                consistent_stat_dict[part_second_min_margin_key] = second_min_margin
                                consistent_stat_dict[part_mean_margin_key] = mean_margin
                                consistent_stat_dict[part_second_mean_margin_key] = second_mean_margin

                                


                                season_part_prob_data = [consistent_stat, consistent_stat_prob, second_consistent_stat, second_consistent_stat_prob]
                                player_consistent_stat_data.extend(season_part_prob_data)

                                # add postseason stat probs separately
                                # elif season_part == 'postseason': incorporated into loop

                                
                                # now that we looped thru all parts of season we can see which is available for ok val
                                ok_val_key = 'ok val'
                                #ok_val_season_prob_key = ok_val_key + ' prob ' + str(year)

                                # add another column to classify if postseason stat < regseason stat so we can group those together

                                final_consistent_stats.append(player_consistent_stat_data)
                                # need to save all parts of season for each stat
                                # this is how we save as many fields/columns we want in a single row
                                part_consistent_stat_dict[season_part][stat_name] = consistent_stat_dict

                                if stat_name not in all_consistent_stats_dict[player_name]:
                                    all_consistent_stats_dict[player_name][stat_name] = {}
                                if condition not in all_consistent_stats_dict[player_name][stat_name].keys():
                                    all_consistent_stats_dict[player_name][stat_name][condition] = {}
                                if year not in all_consistent_stats_dict[player_name][stat_name][condition].keys():
                                    all_consistent_stats_dict[player_name][stat_name][condition][year] = {}

                                all_consistent_stats_dict[player_name][stat_name][condition][year][season_part] = consistent_stat_dict
                            
                            #print('part_consistent_stat_dict: ' + str(part_consistent_stat_dict))

                            # consistent_stat_dict will have for 1 stat but all parts of season
                            # so change to dict
                            # or arrange input in another var

                            #all_consistent_stat_dicts.append(consistent_stat_dict)

                            #all_consistent_stats_dict
                            
    # all_consistent_stat_dicts: [{'player name': 'cole anthony', 'stat name': 'pts', 'team': 'orl', 'full prob val': 6,
    # all_consistent_stat_dicts: [{'player name': 'skylar mays', 'stat name': 'pts', 'team': 'por', 'reg prob val': 9,
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val': 15, 'prob': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    #print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

    #print('all_consistent_stats_dict: ' + str(all_consistent_stats_dict))

    # form all_consistent_stat_dicts

    for player_name, player_consistent_stat_dict in all_consistent_stats_dict.items():
        player_team = ''
        if player_name in player_teams.keys():
            player_team = player_teams[player_name]
        for stat_name, stat_consistent_stat_dict in player_consistent_stat_dict.items():
            consistent_stat_dict = {'player': player_name, 'team': player_team, 'stat': stat_name}
            for condition, condition_consistent_stat_dict in stat_consistent_stat_dict.items():
                for year, year_consistent_stat_dict in condition_consistent_stat_dict.items():
                    for part, part_consistent_stat_dict in year_consistent_stat_dict.items():
                        for key, val in part_consistent_stat_dict.items():
                            consistent_stat_dict[key] = val

            all_consistent_stat_dicts.append(consistent_stat_dict) # for each stat

    #print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

    # determine which keys in dict to sort dicts by
    # we duplicate the corresponding vals in known keys for ref called 'ok val'
    # which stats do we need to see?
    # true prob accounts for condition of which part of season
    # ok val means that it accounts for all conditions 
    # and gets adjusted extrapolated vals by weighing conditional probs
    # the point of sorting these keys is to see most important columns together for comparison
    # for the actual stat value available, which is not always the same as the first consistent val
    ok_val_key = 'ok val'
    # formula for cumulative weighted avg probability
    ok_val_true_prob_key = ok_val_key + ' prob' # account for all conditions to get true prob
    # true seasons prob accounts for all seasons and sample sizes
    # each season is like a different condition given a different weight based on recency and sample size
    ok_val_true_season_prob_key = ok_val_key + ' true season prob' # account for all seasons to get true season prob
    # we already have measured prob of stat in part of season
    # so now we want true prob in part of season, with all other conditions equal
    # for each season, we want to see ok val prob, margin, dev, and other stat measures
    # we also want to see average over last x seasons
    # we do not need true prob for part of season separate 
    # bc true prob already accounts for season part condition
    # we want runnning prob and measures for each part of each season
    # first and foremost show this year and then compare to prev seasons and true count
    # this table will show vector of weighted features that equate true prob
    # other data about each part of each season will go in separate tables unless they are directly used to calc true prob
    # so first this season, last season, and prev seasons. then conditions for each part of each season
    # we need to determine the number of seasons to display ok val
    # based on seasons in all_player_consistent_stats
    # but if we are already looping through all_player_consistent_stats earlier why not perform this fcn then?
    # bc it requires fully populated all_consistent_stat_dicts bc it compares different numbers to get ok val?
    #for season_year in 
    # ok_val_prob_key becomes ok_val_season_prob_key to specify season
    ok_val_season_prob_key = ok_val_key + ' prob ' + str(season_year)

    ok_val_part_prob_key = ok_val_key + ' post prob' # depends which part of season we are in, to choose which should be secondary prob condition
    ok_val_min_margin_key = ok_val_key + ' min margin'
    ok_val_part_min_margin_key = ok_val_key + ' post min margin'
    ok_val_mean_margin_key = ok_val_key + ' mean margin'
    ok_val_part_mean_margin_key = ok_val_key + ' post mean margin'

    # sort_key1 = ok_val_true_prob_key #'ok val prob' # default
    # sort_key2 = 'ok val post prob' # default
    # sort_key3 = 'ok val min margin' # default
    # sort_key4 = 'ok val post min margin' # default
    # sort_key5 = 'ok val mean margin' # default
    # sort_key6 = 'ok val post mean margin' # default
    

    # check if regseason or full season stat is available
    ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    #year_of_interest = 2023
    #regseason_stats = consistent_stat_vals['all'][year_of_interest]['regular']
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val 2023': 15, 'prob 2023': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    for stat_dict in all_consistent_stat_dicts:
        #print('stat_dict: ' + str(stat_dict))

        # consider changing back to reg season stat
        # prefer full season bc more samples
        # but some misleading bc playoffs may differ from regseasons stats significantly
        season_part_key = 'full'
        part_prob_stat_key = season_part_key + ' ' + prob_stat_key
        part_prob_key = season_part_key + ' ' + prob_key
        part_second_prob_stat_key = season_part_key + ' ' + second_prob_stat_key
        part_second_prob_key = season_part_key + ' ' + second_prob_key

        part_min_margin_key = season_part_key + ' ' + min_margin_key
        part_second_min_margin_key = season_part_key + ' ' + second_min_margin_key
        part_mean_margin_key = season_part_key + ' ' + mean_margin_key
        part_second_mean_margin_key = season_part_key + ' ' + second_mean_margin_key

        reg_season_stat_val = stat_dict[part_prob_stat_key] #'full prob val'
        if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
            ok_stat_val = reg_season_stat_val
            ok_stat_prob = stat_dict[part_prob_key]
        reg_season_second_stat_val = stat_dict[part_second_prob_stat_key]
        reg_season_stat_prob = stat_dict[part_prob_key]
        reg_season_second_stat_prob = stat_dict[part_second_prob_key]

        reg_season_min_margin = stat_dict[part_min_margin_key]
        reg_season_second_min_margin = stat_dict[part_second_min_margin_key]
        reg_season_mean_margin = stat_dict[part_mean_margin_key]
        reg_season_second_mean_margin = stat_dict[part_second_mean_margin_key]

        player_stat_records = all_player_stat_records[stat_dict['player']]

        stat_name = stat_dict['stat']
        #year = 2023
        # change to get season part by current date if after playoff schedule start?
        # no bc here we are processing postseason separately
        # we would like to get consistent postseason stat but small sample size?
        season_part = 'postseason' # if we are in posteason, do we also want to see postseason prob of regseason stat???
        condition = 'all'
        # player_stat_dict: {2023: {'postseason': {'pts': {'all': {0: 18, 1: 19,...
        player_stat_dict = all_player_stat_dicts[stat_dict['player']][season_year][season_part][stat_name][condition]

        

        #post_season_stat_val = stat_dict['post prob val']
        #post_season_stat_prob = stat_dict['post prob']

        # we have primitive check if ok val is available and if not then we use next nearest number even if it is not available?
        # next nearest should be available bc they rarely jump multiple steps at once
        # even if not available then we will likely not consider less than consistent stat val
        # but it is very useful to see not only consistent stat but next stat consistency to determine margin of error and deviation
        if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
            #ok_val_key = 'ok val ' + str(season_year)
            stat_dict[ok_val_key] = reg_season_stat_val # default, ok=available

            stat_dict[ok_val_true_prob_key] = reg_season_stat_prob 
            # determine which key has the same stat val in post as reg, bc we earlier made sure there would be one
            # can be generalized to fcn called determine matching key
            stat_dict[ok_val_part_prob_key] = determiner.determine_ok_val_prob(stat_dict, stat_dict[ok_val_key], player_stat_records, season_part, stat_name, season_year=season_year) #post_season_stat_prob 
            # post_season_stat_val_key = determiner.determine_matching_key(stat_dict, stat_dict['ok val']) #'post prob val'
            # # for key, val in stat_dict.items():
            # #     if key != 'ok val':
            # #         if val == stat_dict['ok val'] and not re.search('prob',key):
            # #             post_season_stat_val_key = key

            # post_season_stat_prob_key = re.sub('val','',post_season_stat_val_key)
            # post_season_stat_prob = stat_dict[post_season_stat_prob_key]
            # stat_dict['ok val post prob'] = post_season_stat_prob 

            # if reg_season_stat_val != post_season_stat_val:
            #     stat_dict['ok val post prob'] = post_season_stat_val_prob 

            stat_dict[ok_val_min_margin_key] = reg_season_min_margin
            stat_dict[ok_val_part_min_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'min')

            stat_dict[ok_val_mean_margin_key] = reg_season_mean_margin
            stat_dict[ok_val_part_mean_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'mean')
            

        # if default reg season stat na,
        # first check next lowest val, called second val
        else:
            stat_dict[ok_val_key] = reg_season_second_stat_val # ok=available

            stat_dict[ok_val_true_prob_key] = reg_season_second_stat_prob 
            stat_dict[ok_val_part_prob_key] = determiner.determine_ok_val_prob(stat_dict, stat_dict[ok_val_key], player_stat_records, season_part, stat_name, season_year=season_year) #post_season_stat_prob 
            
            stat_dict[ok_val_min_margin_key] = reg_season_second_min_margin
            stat_dict[ok_val_part_min_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'min')

            stat_dict[ok_val_mean_margin_key] = reg_season_second_mean_margin
            stat_dict[ok_val_part_mean_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'mean')

    # determine final available stat val out of possible consistent stat vals
    # eg if horford reb in playoffs higher than regseason, use regseason stat val's prob in postseason
    # bc that will show highest prob
    #available_stat_val


    sort_keys = [ok_val_true_prob_key, ok_val_part_prob_key, ok_val_min_margin_key, ok_val_part_min_margin_key, ok_val_mean_margin_key, ok_val_part_mean_margin_key]
    sorted_consistent_stat_dicts = sorter.sort_dicts_by_keys(all_consistent_stat_dicts, sort_keys)
    # desired_order = ['player name','stat name','ok val','ok pp','ok p']
    # sorted_consistent_stats = converter.convert_dicts_to_lists(sorted_consistent_stat_dicts)

    # print('sorted_consistent_stats')
    # print(tabulate(player_consistent_stat_data_headers + sorted_consistent_stats))

    # # export
    # for row in sorted_consistent_stats:
    #     export_row = ''
    #     for cell in row:
    #         export_row += str(cell) + ';'

    #     print(export_row)

    return sorted_consistent_stat_dicts

def generate_valid_top_ev_props(plus_ev_props):
    print('\n===Generate Valid Top EV Props===\n')
    top_ev_props = []
    # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3}
    # p2 = {'player':'kobe', 'game':'1', 'stat':'pts', 'ev':3}
    # p3 = {'player':'kobe', 'game':'1', 'stat':'pts', 'ev':2}
    # p4 = {'player':'dame', 'game':'2', 'stat':'pts', 'ev':2}
    # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1}
    # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1}
    # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
    for main_prop in plus_ev_props:
        #print('\nmain_prop: ' + str(main_prop))
        # ensure at least 2 picks from this game
        # remove if only 1
        # main_prop_game = main_prop['game']
        # for compare_prop in plus_ev_props:
        #     compare_prop_game = compare_prop['game']

        # 1. first look for duplicates
        # 2. take highest ev
        # 3. and then remove single pick games
        fields = ['player', 'stat']
        # val = x+ or x-
        partial_key = 'val' # part of val must match to be duplicate, the +/- bc we are allowed both over and under
        # if determine duplicate, take highest ev of duplicates
        if determiner.determine_multiple_dicts_with_vals(main_prop, fields, plus_ev_props, partial_key):
            # if highest ev of the duplicates
            duplicate_props = isolator.isolate_duplicate_dicts(main_prop, fields, plus_ev_props)
            if determiner.determine_highest_ev_prop(main_prop, duplicate_props):
                # remove lower ev props
                # before adding to list need to check if only prop in game
                top_ev_props.append(main_prop)
        else:
            top_ev_props.append(main_prop)

    #print('top_ev_props: ' + str(top_ev_props))

    print('\n===Validate Props===\n')
    # now removed duplicates, so check if >1 props per game
    # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3}
    # p2 = {'player':'kobe', 'game':'1', 'stat':'pts', 'ev':3}
    # p4 = {'player':'dame', 'game':'2', 'stat':'pts', 'ev':2}
    # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1}
    # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1}
    # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
    valid_top_ev_props = [] # >1 per game
    for main_prop in top_ev_props:
        #print('\nmain_prop: ' + str(main_prop))
        # given list of dicts, see if any matching vals
        # determine multiple props in same game
        if determiner.determine_multiple_dicts_with_val(main_prop, 'game', top_ev_props):
            # if enough options, proceed
            valid_top_ev_props.append(main_prop)

    #print('valid_top_ev_props: ' + str(valid_top_ev_props))
    return valid_top_ev_props

# probs given out of 100 so convert to 1 before multiplying
# need at least 2 probs to get joint
def generate_joint_prob(probs):
    #print('\n===Generate Joint Prob===\n')
    #print('probs: ' + str(probs))
    
    joint_prob = 0

    if len(probs) > 1:
        joint_prob = probs[0] / 100
        for prob in probs[1:]:
            joint_prob *= prob / 100

    #print('joint_prob: ' + str(joint_prob))
    return joint_prob

# need at least 2 odds to get joint
def generate_joint_odds(american_odds):
    #print('\n===Generate Joint Odds===\n')

    #print('american_odds: ' + str(american_odds))
    
    joint_odds = 0

    if len(american_odds) > 1:
        joint_odds = converter.convert_american_to_decimal_odds(american_odds[0])
        for odds in american_odds[1:]:
            decimal_odds = converter.convert_american_to_decimal_odds(odds)
            joint_odds *= decimal_odds

    #print('joint_odds: ' + str(joint_odds))
    return joint_odds

def generate_joint_ev_of_props(max_picks_top_ev_props):
    #print('\n===Generate Joint EV of Props===\n')
    #print('max_picks_top_ev_props: ' + str(max_picks_top_ev_props))
    probs = []
    odds = []
    for prop in max_picks_top_ev_props:
        prop_prob = prop['true prob']
        probs.append(prop_prob)
        prop_odds = prop['odds']
        odds.append(prop_odds)
    joint_prob = generate_joint_prob(probs)
    joint_odds = generate_joint_odds(odds)

    ev = generate_joint_ev(joint_prob, joint_odds)

    #print('ev: ' + str(ev))
    return ev


# given joint odds as decimal odds
# bc need to convert am to dec before getting joint by multiplying
def generate_joint_ev(joint_prob, joint_odds):
    #print('\n===Generate Joint EV===\n')
    #print('joint_prob: ' + str(joint_prob))
    #print('joint_odds: ' + str(joint_odds))

    stake = 1
    payout = stake * joint_odds
    #print('payout: ' + str(payout))
    profit_multiplier = payout - stake # need to subtract stake here unlike with american odds bc added 1 to get decimal odds
    #print('profit_multiplier: ' + str(profit_multiplier))
        
    prob_over = joint_prob
    #print('prob_over: ' + str(prob_over))
    prob_under = 1 - prob_over
    #print('prob_under: ' + str(prob_under))
    profit = profit_multiplier * prob_over 
    loss = stake * prob_under
    ev = "%.2f" % (profit - loss)

    #print('ev: ' + str(ev))
    return ev

# input american odds bc that is given
# prob given out of 100 bc from final all stat probs?
def generate_ev(prob, odds):
    #print('\n===Generate EV===\n')
    #print('prob: ' + str(prob))
    #print('odds: ' + str(odds))

    # now we have odds return profit/loss
    # so get ev = e(x) = xp
    #+200=200/100=2, -200=100/200=1/2
    ev = 0 # if no odds
    if odds != 'NA' and odds != '?':
        conv_factor = 100 # american odds system shows how much to put in to profit 100
        profit_multiplier = int(odds) / conv_factor
        if re.search('-',odds):
            profit_multiplier = conv_factor / -int(odds)
        #print('profit_multiplier: ' + str(profit_multiplier))
        
        prob_over = prob / 100
        #print('prob_over: ' + str(prob_over))
        prob_under = 1 - prob_over
        #print('prob_under: ' + str(prob_under))
        spent = 1 # unit
        profit = profit_multiplier * prob_over 
        loss = spent * prob_under
        # "%.2f" % () returns accurate 2 decimal places instead of round(2) which always rounds up
        ev = "%.2f" % (profit - loss)
    
    #print('ev: ' + str(ev))
    return ev







# make logs dicts sorted by yr
def generate_reg_season_logs(player_season_logs):
    reg_season_logs = {}

    # for year, year_season_log in player_season_logs.items():
    #     reg_season_logs[year] = {}
    #     for field, field_dict in year_season_log.items():
    #         reg_season_logs[year][field] = {}
    #         for idx, val in field_dict.items():
    #             if year_season_log['Type'][idx] == 'Regular':
    #                 reg_season_logs[year][field][idx] = val

    for year, year_season_log in player_season_logs.items():
        #print('year: ' + year)
        player_season_log_df = pd.DataFrame(year_season_log)
        player_season_log_df.index = player_season_log_df.index.map(str)
        #print('player_season_log_df: ' + str(player_season_log_df))

        reg_season_log_df = determiner.determine_season_part_games(player_season_log_df)
        reg_season_log = reg_season_log_df.to_dict()
        reg_season_logs[year] = reg_season_log

    #print('reg_season_logs: ' + str(reg_season_logs))
    return reg_season_logs

def generate_part_season_logs(player_season_logs, part):
    part_season_logs = {}

    if part == 'full':
        part_season_logs = player_season_logs
    else:
        for year, year_season_log in player_season_logs.items():
            #print('year: ' + year)
            player_season_log_df = pd.DataFrame(year_season_log)
            player_season_log_df.index = player_season_log_df.index.map(str)
            #print('player_season_log_df: ' + str(player_season_log_df))

            part_season_log_df = determiner.determine_season_part_games(player_season_log_df, part)
            part_season_log = part_season_log_df.to_dict()
            part_season_logs[year] = part_season_log

    #print('part_season_logs: ' + str(part_season_logs))
    return part_season_logs















# strategy 1: high prob +ev (balance prob with ev)
# 1. iso tru prob >= 90
# 1.1 show tru prob >= 90 & prev_val < stat+ or prev_val > stat-
# 2. iso +ev
# 3. out of remaining options, sort by ev
# 4. iso top x remaining options
# 5. sort by game and team and stat
# 6. see if any invalid single bets (only 1 good option for that game)
# 7. replace invalid bets with next best valid ev

# strategy 2: highest +ev
# strategy 3: highest prob
# strategy 4: combine +ev picks into multiple ~+100 parlays

# desired order: key = S Curry Pg, B Podziemski G, K Thompson Sg, J Kuminga Pf, K Looney F Starters 2024 Regular Prob
# available_prop_dicts: key = 
def generate_prop_table_data(available_prop_dicts, desired_order=[]):
    #print('\n===Generate Prop Table Data===\n')
    #print('available_prop_dicts before: ' + str(available_prop_dicts))

    # fill in NA for props available for 1 yr but not others
    # D Rose PG out 2023 regular prob blank bc did not play with players of interest last yr
    # D Rose PG starters 2024 regular prob should be filled
    for key in desired_order:
        #print('key: ' + str(key))
        for dict in available_prop_dicts:
            #print('dict: ' + str(dict))
            if key not in dict.keys():
                #print('NA')
                dict[key] = 'NA'
                #print('dict: ' + str(dict))

    #print('available_prop_dicts after: ' + str(available_prop_dicts))

    prop_tables = [available_prop_dicts]
    sheet_names = ['All']

    #print('prop_tables: ' + str(prop_tables))

    # 1. iso tru prob >= 90
    # define high prob eg >=90
    # we use isolator for strictly isolating parts of existing data when there is no processing or computation between input output
    high_prob_props = isolator.isolate_high_prob_props(available_prop_dicts)
    #print('high_prob_props: ' + str(high_prob_props))
    if len(high_prob_props) > 0:
        prop_tables.append(high_prob_props)
        sheet_names.append('High Prob')
        # sort all high prob props by ev so we can potentially see 0 and -ev options incorrectly calculated due to irregular circumstance
        # sort_keys = ['ev']
        # sorted_high_props_by_ev = sorter.sort_dicts_by_keys(plus_ev_props, sort_keys)



        # strategy 1 props
        #s1_props = high_prob_props

    # 2. iso +ev
    # the only time when -ev picks are used is when they must be paired with high +ev pick
    # then they will bring down the ev of the group but the joint prob may still be +ev
    # really only use if only 1 +ev pick per game happens to be high ev and the other -ev is only slightly low
    # also in reality the ev calculation is imperfect 
    # so we must take a range including some -ev that might be miscalculated and are truly +ev
    final_prop_dicts = available_prop_dicts
    if len(high_prob_props) > 0:
        final_prop_dicts = high_prob_props

    #print('\n===Generate Prop Combos===\n')
    # if ev, read odds
    # final_prop_dicts = [{player:p, game:g, ...},...]
    # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3, 'odds':'100', 'true prob':100}
    # p2 = {'player':'kobe', 'game':'1', 'stat':'pts', 'ev':3, 'odds':'100', 'true prob':100}
    # p3 = {'player':'kobe', 'game':'1', 'stat':'pts', 'ev':2, 'odds':'100', 'true prob':100}
    # p4 = {'player':'dame', 'game':'2', 'stat':'pts', 'ev':2, 'odds':'100', 'true prob':100}
    # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1, 'odds':'100', 'true prob':100}
    # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1, 'odds':'100', 'true prob':100}
    # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1, 'odds':'100', 'true prob':100}
    # final_prop_dicts = [p1, p2, p3, p4, p5, p6, p7]
    if len(final_prop_dicts) > 0 and 'ev' in final_prop_dicts[0].keys():
        #print('ev found')
        plus_ev_props = isolator.isolate_plus_ev_props(final_prop_dicts)
        
        # 3. out of remaining options, sort by ev
        # plus_ev_props = [{field:val,...},...]
        sort_keys = ['ev']
        plus_ev_props = sorter.sort_dicts_by_keys(plus_ev_props, sort_keys)
        prop_tables.append(plus_ev_props)
        sheet_names.append('+EV')

        # 4. iso top x remaining options
        # top is meaningless bc we do not know how many picks in a set is ideal
        # so define different strategies and combos
        # eg top ev w/ high prob, or top prob w/ +ev
        # for top ev w/ hig prob, sort by ev
        # if 2 options for single player stat, take higher ev
        # for top prob w/ +ev, sort by prob
        # if 2 options for single player stat, take higher prob
        dk_max_allowed = 20
        fd_max_allowed = 25
        # ideal max depends on cumulative ev
        #top_options = plus_ev_props[0:dk_max_allowed]
        #print('top_options: ' + str(top_options))

        valid_top_ev_props = generate_valid_top_ev_props(plus_ev_props)

        # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3}
        # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1}
        # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1}
        # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
        # now top ev props only has props with at least 2 per game
        # and only top ev of duplicates
        # and sorted by ev
        # now we want all same game options
        # -sorted by stat, so we can make selections per stat
        # -AND sorted by highest ev, so we can add props to other combos
        # AND max picks option
        # AND make fcn to pick top x props, before sorting for selection
        # AND make fcn to pick all combos of props with x (eg +100) joint odds
        # 1. same game options, sorted by stat
        #print('\n===same game, sort by stat===\n')
        sort_keys = ['game', 'stat', 'player']
        sg_top_ev_props_by_stat = sorter.sort_dicts_by_str_keys(valid_top_ev_props, sort_keys)
        prop_tables.append(sg_top_ev_props_by_stat)
        sheet_names.append('SG +EV Stats')
        # 2. same game, sort by ev
        #print('\n===same game, sort by ev===\n')
        sort_keys = ['game', 'ev']
        sg_top_ev_props = sorter.sort_dicts_by_str_keys(valid_top_ev_props, sort_keys)
        prop_tables.append(sg_top_ev_props)
        sheet_names.append('SG +EV')
        # 3. max picks
        #print('\n===Max Picks===\n')
        #max_picks_top_ev_props = generate_max_picks_top_ev_props(top_ev_props, dk_max_allowed)
        #test_num_props = 2 # dk_max_allowed
        # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3}
        # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1}
        max_picks_top_ev_props = valid_top_ev_props[0:dk_max_allowed]
        # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1}
        # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
        remaining_top_ev_props = valid_top_ev_props[dk_max_allowed:] # after cutoff by platform limit, include all picks just split in 2
        # in top remaining picks, ensure >1 per game
        # add here if only prop available for game 
        # so we can see if we should keep this and remove another one 
        # or remove this and add one to another game that already has >1 prop
        individual_props = [] 
        replacement_props = []
        # max_picks_top_ev_props = [{},...]
        for main_prop_idx in range(len(max_picks_top_ev_props)):
            main_prop = max_picks_top_ev_props[main_prop_idx]

            # if only prop in game, individual prop, so need to determine which prop to replace
            if not determiner.determine_multiple_dicts_with_val(main_prop, 'game', max_picks_top_ev_props):
                # remaining_top_ev_props =
                # p6 = {'player':'trae', 'game':'4', 'stat':'ast', 'ev':1}
                # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
                top_ev_remaining_prop = {}
                if len(remaining_top_ev_props) > 0:
                    top_ev_remaining_prop = remaining_top_ev_props[0]
                
                individual_props.append(main_prop)
                # replace with next highest ev
                # first look in remaining props to see if same game prop available
                # if not, replace with highest ev in remaining props (idx=0)
                #if determiner.determine_same_game_prop(main_prop, remaining_top_ev_props):
                # main_game = main_prop['game']
                # if main_game in remaining_top_ev_props.values():
                if determiner.determine_val_in_dicts(main_prop, 'game', remaining_top_ev_props):
                
                    #print('\n===Same Game Props===\n')
                    # consider next highest evs
                    # get joint ev and compare to other option
                    # p7 = {'player':'luka', 'game':'3', 'stat':'pts', 'ev':1}
                    sg_props = isolator.isolate_sg_props(main_prop, remaining_top_ev_props)
                    sg_prop = isolator.isolate_highest_ev_prop(sg_props) # next highest same game prop if available
                    
                    #multiplied_evs = main_prop['ev'] * sg_prop['ev']
                    #print('main multiplied_evs: ' + str(multiplied_evs))
                    joint_odds = generate_joint_odds([main_prop['odds'], sg_prop['odds']])
                    joint_prob = generate_joint_prob([main_prop['true prob'], sg_prop['true prob']])
                    main_prop_joint_ev = generate_joint_ev(joint_prob, joint_odds) #main_prop['ev'] * sg_prop['ev']
                    #print('main_prop_joint_ev: ' + str(main_prop_joint_ev))

                    #print('\n===Next Highest Props===\n')
                    # find lowest available to take out from a game with >2 picks
                    # if next highest sg prop +*? main prop > sum/product? of 2 lowest top ev props
                    # then use sg prop instead of overall prop
                    # max_picks_top_ev_props = 
                    # p1 = {'player':'kyrie', 'game':'3', 'stat':'pts', 'ev':3}
                    # p5 = {'player':'trae', 'game':'4', 'stat':'pts', 'ev':1}
                    low_ev_top_prop = max_picks_top_ev_props[-1]
                    #multiplied_evs = low_ev_top_prop['ev'] * top_ev_remaining_prop['ev']
                    #print('replacement multiplied_evs: ' + str(multiplied_evs))
                    joint_odds = generate_joint_odds([low_ev_top_prop['odds'], top_ev_remaining_prop['odds']])
                    joint_prob = generate_joint_prob([low_ev_top_prop['true prob'], top_ev_remaining_prop['true prob']]) #low_ev_top_prop['true prob'] * top_ev_remaining_prop['true prob']
                    replacement_prop_joint_ev = generate_joint_ev(joint_prob, joint_odds)
                    #print('replacement_prop_joint_ev: ' + str(replacement_prop_joint_ev))

                    # >= bc prefer to keep picks across different games
                    if main_prop_joint_ev >= replacement_prop_joint_ev:
                        # keep main prop and sgp
                        # remove bottom of max picks
                        max_picks_top_ev_props = max_picks_top_ev_props[:-1]
                        max_picks_top_ev_props.append(sg_prop)
                    else: #
                        #replacement_prop = remaining_top_ev_props[0]
                        max_picks_top_ev_props = max_picks_top_ev_props[:main_prop_idx] + max_picks_top_ev_props[main_prop_idx+1:]
                        max_picks_top_ev_props.append(top_ev_remaining_prop)

                else: # no sg props available so replace with top of remaining props
                    max_picks_top_ev_props = max_picks_top_ev_props[:-1]
                    max_picks_top_ev_props.append(top_ev_remaining_prop)

                

                # compare same game next highest if available to next highest remaining overall
                    # if next highest in game = next highest overall, replace
                    # if next highest in game < next highest overall, need to compute joint ev
                    # OR just set an acceptable range difference

        #print('max_picks_top_ev_props: ' + str(max_picks_top_ev_props))

        # sort by game and stat for easy selection
        sort_keys = ['game', 'stat']
        max_picks_top_ev_props = sorter.sort_dicts_by_str_keys(max_picks_top_ev_props, sort_keys)
        prop_tables.append(max_picks_top_ev_props)
        sheet_names.append('Max +EV')

        ev_max_picks_top_ev = generate_joint_ev_of_props(max_picks_top_ev_props)
        joint_evs = [{'ev max picks top ev': ev_max_picks_top_ev}]
        prop_tables.append(joint_evs)
        sheet_names.append('Joint EVs')

        top_prob_props = []

        # max profit props makes a combo of max allowed props
        # how does it pick the max profit, while keeping +ev?
        # sort by profit only after remaining +ev props with no other distinguishing factors
        # need to get actual odds of joint combo props
        # to make sure it is +ev max profit
        # in theory, max profit = max ev
        # BUT if we account for bet spread, it may be worth putting a very small amount on a low prob, high return
        max_profit_props = []


        # 5. sort by game and team and stat
        # OR game, stat, player
        # sort_keys = ['game', 'stat', 'player']#['game', 'team', 'stat']
        # top_options = sorter.sort_dicts_by_str_keys(top_options, sort_keys)
        # #writer.list_dicts(top_options, desired_order)
        # prop_tables.append(top_options)
        # sheet_names.append('Top')

        #s1_props = top_options

        #print('prop_tables before reverse: ' + str(prop_tables))

        prop_tables = list(reversed(prop_tables))#.reverse() #[top_options, plus_ev_props, high_prob_props, available_prop_dicts]
        sheet_names = list(reversed(sheet_names))#.reverse() #['Top', '+EV', 'High Prob', 'All'] #, 'Rare' # rare shows those where prev val is anomalous so unlikely to repeat anomaly (eg player falls in bottom 10% game)
            

    return (prop_tables, sheet_names)

# conditions = list(list(all_current_conditions.values())[0].keys()) ['loc']
# desired_order.extend(conditions)
# # add columns in order of conditions used, by weight high to low
# # given current conditions used to determine true prob
# # take current conditions for each year
# conditions_order = generate_conditions_order(conditions)
# conditions_order = ['all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
def generate_conditions_order(all_cur_conds_lists, all_game_player_cur_conds, all_players_abbrevs, season_years, part):
    # print('\n===Generate Conditions Order===\n')
    # print('Input: all_cur_conds_lists = {player: {cond_key:cond_val, ... = ' + str(all_cur_conds_lists))
    # print('Input: all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ... = ' + str(all_game_player_cur_conds))

    conditions_order = []#['all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
    
    # find all condition vals
    # get all unique vals of cur conds
    current_conditions = determiner.determine_all_current_conditions(all_cur_conds_lists)

    # we need to know all conditions of all players bc all players listed in same table
    # so location will show both home away
    # conditions with more options only need to show options that have current conditions
    # once we get all cur conds we can get all cur cond vals of all players
    # conditon val means the value of the condition like location is the key but home/away are the vals
    for current_condition in current_conditions:
        for year_idx in range(len(season_years)):
            year = season_years[year_idx]

            condition_title = current_condition + ' ' + str(year) + ' ' + part + ' prob'
            if year_idx > 0:
                condition_unit_title = condition_title + ' per unit'
                conditions_order.append(condition_unit_title)

            conditions_order.append(condition_title)

    # for game players conds we just want overall for all yrs bc too many subconditions to show on this page
    gp_conds = determiner.determine_all_current_gp_conds(all_game_player_cur_conds, all_players_abbrevs)
    for current_condition in gp_conds:
        condition_title = current_condition + ' ' + part + ' prob'
        conditions_order.append(condition_title)

    #print('conditions_order: ' + str(conditions_order))
    return conditions_order


# stat_dict: {'player name': 'Trevelin Queen', 'stat name': 'ast', 'prob val': 0, 'prob': 100...
def generate_available_prop_dicts(stat_dicts, game_teams=[], player_teams={}, cur_yr=''):
    print('\n===Generate Available Prop Dicts===\n')
    available_prop_dicts = []
    maybe_available_props = []

    # for efficiency first get all diff teams
    # and then read each team page once and save local
    # teams = []
    # for stat_dict in stat_dicts:
    #     teams.append(stat_dict['team'])
    # teams = list(set(teams))
    # print('teams: ' + str(teams))

    # we know we will need odds for each team so read each team page at least once per day
    # actually to save odds in a local var we need to sort by team in a duplicate array
    #teams_stat_dicts = sorter.sort_dicts_by_key(stat_dicts, 'team')
    # and we need to isolate into separate loops
    # so we can read page once and use for all teammates
    #all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18': '−650','20': '+500',...
    all_players_odds = reader.read_all_players_odds(game_teams, player_teams, cur_yr=cur_yr) # {team: stat: { player: odds,... }}

    #for team in teams:
        #all_players_odds = reader.read_all_stat_odds(stat_dict, all_players_odds)

    # for each proposition dict, add odds val
    # if no odds val, then do not add to available dict
    for stat_dict in stat_dicts:
        #print('stat_dict: ' + str(stat_dict))
        # see if stat available
        # could do same check for all and put 0 if na 
        # and then sort by val/odds or elim 0s

        # add val to dict
        odds = 'NA'
        team = stat_dict['team']
        if team in all_players_odds.keys():
            stat_name = stat_dict['stat']
            #print('stat_name: ' + stat_name)
            if stat_name in all_players_odds[team].keys():
                player = stat_dict['player'].lower()
                #print('player: ' + player)
                #print('player_dict: ' + str(all_players_odds[team][stat_name]))
                if player in all_players_odds[team][stat_name].keys():
                    ok_val = str(stat_dict['val'])
                    #print('ok_val: ' + str(ok_val))
                    if str(ok_val) in all_players_odds[team][stat_name][player].keys():
                    
                        odds = all_players_odds[team][stat_name][player][ok_val] #reader.read_stat_odds(stat_dict, all_players_odds)
        #     else:
        #         print('Warning: stat name not in all_players_odds: ' + stat_name)
        # else:
        #     print('Warning: team not in all_players_odds: ' + team)
        #     else:
        #         odds = 'NA'
        # else:
        #     odds = 'NA'

        #print('odds: ' + odds)

        # +100 means 1 unit in to profit 1 unit
        stat_dict['odds'] = odds # format +100 = 1 spent/1 earned

        # now we have odds return profit/loss
        # so get ev = e(x) = xp
        #+200=200/100=2, -200=100/200=1/2
        ev = 0 # if no odds
        if odds != 'NA' and odds != '?':
            true_prob = stat_dict['true prob']
            #print('true_prob: ' + str(true_prob))

            #ev = generate_ev(prob, odds)
            #print('\n===Generate EV for Prob, Odds: ' + str(true_prob) + ', ' + str(odds) + '===\n')

            conv_factor = 100 # american odds system shows how much to put in to profit 100
            profit_multipier = int(odds) / conv_factor
            if re.search('-',odds):
                profit_multipier = conv_factor / -int(odds)
            #print('profit_multipier: ' + str(profit_multipier))
            
            prob_over = true_prob / 100
            #print('prob_over: ' + str(prob_over))
            prob_under = 1 - prob_over
            #print('prob_under: ' + str(prob_under))
            spent = 1 # unit
            # "%.2f" % () returns accurate 2 decimal places instead of round(2) which always rounds up
            ev = "%.2f" % (profit_multipier * prob_over - spent * prob_under)
        
        #print('ev: ' + str(ev))
        stat_dict['ev'] = ev
        
        # if team odds saved locally then no need to read again from internet same day bc unchanged?
        # no bc they change frequently, especially near game time bc more ppl active

        # if team not in all_players_odds.keys():
        #     all_players_odds[team] = {}
        # if stat_name not in all_players_odds[team].keys():
        #     all_players_odds[team][stat_name] = {}
        # all_players_odds[team][stat_name][player] = odds
        # print('all_players_odds: ' + str(all_players_odds))

        #if determiner.determine_stat_available(stat_dict):
        # if we do not see player in list of odds then they might be available later so put ?
        # if we see odds for different higher val then NA
        # if we see odds for lower value then put >P? bc their minutes are probably down but if not then good value
        if stat_dict['odds'] != 'NA':
            if str(stat_dict['odds']) == '?':
                maybe_available_props.append(stat_dict)

            elif len(stat_dict['odds']) > 0:
                if abs(int(stat_dict['odds'])) > 0:
                    available_prop_dicts.append(stat_dict)

            else:
                print('Warning: odds returned invalid value!')
        
    available_prop_dicts = available_prop_dicts + maybe_available_props

    #print('available_prop_dicts: ' + str(available_prop_dicts))
    return available_prop_dicts

def generate_stat_val_probs_cond_refs(game_num, prev_val, player_current_conditions, player_gp_conds, stat_val_probs_dict):
    # add more fields for ref
    stat_val_probs_dict['game'] = game_num
    stat_val_probs_dict['prev'] = prev_val

    for cond_key, cond_val in player_current_conditions.items():
        stat_val_probs_dict[cond_key] = cond_val

    # {teammates: {starters:[],...}, opp: {...}
    for team_cond, team_parts in player_gp_conds.items():
        for team_part, team_part_players in team_parts.items():
            # to save space, if teammates just put team part and assume same team bc opp says opp
            team_part_cond_key = team_cond + ' ' + team_part # eg. 'opp starters'
            if team_cond == 'teammates':
                team_part_cond_key = team_part # eg. 'starters'
            stat_val_probs_dict[team_part_cond_key] = team_part_players

    return stat_val_probs_dict

# flatten nested dicts into one level and list them
# from all_stat_probs_dict: {'luka doncic': {'pts': {1: {'all 2023 regular prob': 1.0, 'all 2023 full prob': 1.0,...
# all_stat_prob_dicts = [{player:player, stat:stat, val:val, conditions prob:prob,...},...]
# conditions prob = b biyombo c starter 2023 regular prob
# need all_player_stat_dicts to get prev val
# all_players_teams = {player:year:team:gp}
def generate_all_true_prob_dicts(all_true_probs_dict, all_players_teams={}, all_cur_conds_dicts={}, all_gp_cur_conds={}, all_player_stat_dicts={}, game_teams=[], rosters={}, cur_yr=''):
    print('\n===Generate All True Prob Dicts===\n')
    print('Input: all_cur_conds_dicts = {p1:{\'p1, p2 out\':\'out\', \'away\':\'loc\', ...},... = {\'nikola jokic\': [\'away\':\'loc\', \'V Cancar SF, J Murray PG,... out\':\'out\', ... = ' + str(all_cur_conds_dicts))
    print('Input: all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ...')# = ' + str(all_gp_cur_conds))
    print('Input: all_true_probs_dict = {player: {stat: {val: {conditions: {prob, ... = {\'nikola jokic\': {\'pts\': {0: {\'all 2024 regular prob\': 0.0, ..., \'A Gordon PF, J Murray PG,... starters 2024 regular prob\': 0.0, ...')
    print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('Input: all_player_stat_dicts = {player: {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'kyle kuzma\': {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('Input: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\'), ...]')
    print('Input: teams_current_rosters = {team:[players],..., {\'nyk\': [jalen brunson, ...], ...}')
    print('Input: Current Year to get current team')
    print('\nOutput: all_true_prob_dicts = [{player:p1, team:t1, stat:s1, val:v1, condition prob:prob1, ... = [{\'player\': \'nikola jokic\', \'team\': \'den\', \'stat\': \'pts\', \'val\': \'0\', \'all 2024 regular prob\': 0, ..., \'A Gordon PF, J Murray PG,... starters 2024 regular prob\': 0, ...\n')

    all_true_prob_dicts = []

    stats_of_interest = ['pts','ast','reb']

    # we need to get all conditions for all players
    # so table lines up if players did not all play in same conditions
    #all_conditions = determiner.determine_all_conditions(all_true_probs_dict)

    #cur_yr = str(season_years[0])
    #print('cur_yr: ' + str(cur_yr))

    true_prob_key = 'true prob' # if val only in postseason then no true prob for reg season YET

    for player, player_stat_probs_dict in all_true_probs_dict.items():
        #print('\n===Player: ' + player.title() + '===\n')
        #stat_val_probs_dict = {'player': player}
        # player_teams = {year:{team:gp,...},...
        player_teams = all_players_teams[player]
        player_team = determiner.determine_player_current_team(player, player_teams, cur_yr, rosters)#list(player_teams[player][cur_yr].keys())[-1] # current team
        # if player in player_teams.keys():
        #     player_team = player_teams[player]
        #stat_val_probs_dict['team'] = player_team

        # add game num for ref so we can sort by game to ensure at least 2 picks per game 
        # OR if only 1 allowed still need to see game teams next to each other to place picks on same page of gui
        game_num = determiner.determine_game_num(game_teams, player_team)


        player_current_conditions = all_cur_conds_dicts[player]
        #print('player_current_conditions: ' + str(player_current_conditions))
        player_gp_conds = all_gp_cur_conds[player]

        player_stat_dict = all_player_stat_dicts[player]
        #print('player_stat_dict: ' + str(player_stat_dict))
        
        #stat_probs_dict: {1: {'all 2023 regular prob': 1.0, 'all 2023 full prob': 1.0,...},...
        for stat_name, stat_probs_dict in player_stat_probs_dict.items():
            #print('\n===Stat: ' + str(stat_name) + '===\n')
            #stat_val_probs_dict['stat'] = stat_name
            #consistent_stat_dict = {'player': player_name, 'team': player_team, 'stat': stat_name}
            # for condition, condition_consistent_stat_dict in stat_probs_dict.items():
            #     for year, year_consistent_stat_dict in condition_consistent_stat_dict.items():
            #         for part, part_consistent_stat_dict in year_consistent_stat_dict.items():
            #             for key, val in part_consistent_stat_dict.items():
            #                 consistent_stat_dict[key] = val
            
            if stat_name in stats_of_interest:
                condition = 'all' # all conds match all
                part = 'regular' # get current part from time of year mth
                # player_stat_dict: {'2023': {'regular': {'pts': {'all': {0: 18, 1: 19...
                prev_val = 0
                if cur_yr in player_stat_dict.keys():
                    condition_dict = player_stat_dict[cur_yr][part][stat_name][condition]
                    if '0' in condition_dict.keys():
                        prev_val = condition_dict['0']
                    else:
                        print('Warning: no games in stat dict!\n' + player + ':\n' + str(player_stat_dict))
                    #print('prev_val: ' + str(prev_val))
                    # is it useful to get prev val under current conditions? possibly but could be misleading unless looking at larger sample
                
                # integrate overs and unders in same loop
                #val_probs_dict: {'all 2023 regular prob': 1.0, 'all 2023 full prob': 1.0,...},...
                for val, val_probs_dict in stat_probs_dict.items():
                    #print('\n===Val: ' + str(val) + '===\n')
                    #print('val_probs_dict: ' + str(val_probs_dict))
                    #stat_val_probs_dict['val'] = str(val) + '+'
                    val_str = str(val) + '+'
                    if val == 0: # for zero we only want exactly 0 prob not over under bc 1+/- includes 1 and cannot go below 0
                        val_str = str(val)
                    stat_val_probs_dict = {'player': player, 'team': player_team, 'stat': stat_name, 'val': val_str }
                    #for conditions, prob in val_probs_dict.items():
                    # if condition not in val probs dict
                    # then this player did not play in this condition, so show NA
                    # if cant find cond for this val, then check why?
                    # did the player never play under these conds? if so then we cant say prob
                    # if they did play under these conds but never reached val, then we can use those samples
                    
                    # if we dont have all conditions for all yrs, 
                    # then we should have standard for all yrs and loop thru each yr
                    # eg players played last yr but not yet this yr although on roster
                    #for conditions in all_conditions:
                        #print('\n===Conditions: ' + str(conditions) + '===\n')
                        #prob = 0
                        #per_unit_prob = 0
                        # if not seen this val under these conditions, then depends why
                        # if never reached this val before, how should we treat it?
                        # how is true prob computed?
                    # show true prob key in row!
                    # before was included with all conditions conveniently but not ideally
                    # ideally handle separately bc all conditions takes too long to load
                    # instead compare conditions in manageable groups unless specifically looking at big picture big data analysis
                    
                    if true_prob_key in val_probs_dict.keys(): # and it is cur cond for this player
                        prob = val_probs_dict[true_prob_key]
                        # already going thru all conditions which includes per unit conditions
                        #per_unit_conditions = conditions + ' per unit'
                        #per_unit_prob = val_probs_dict[per_unit_conditions]
                        #per_unit_prob = per_unit_probs_dict[player][stat_name][val][conditions] #val_probs_dict[per_unit_conditions]
                        #print('prob: ' + str(prob))
                        if prob is not None:
                            stat_val_probs_dict[true_prob_key] = round(prob * 100)
                    #     else:
                    #         stat_val_probs_dict[true_prob_key] = 'NA'
                    #         print('Caution: No prob for player stat val: ' + player + ', ' + stat_name + ', ' + str(val))
                    #     #stat_val_probs_dict[per_unit_conditions] = round(per_unit_prob * 100)
                    # # if condition not in val probs dict
                    # # then this player did not play in this condition, so show NA
                    # #for conditions in all_conditions:
                    # else: # if we cant find conditions for this val
                    #     stat_val_probs_dict[true_prob_key] = 'NA'
                    #     print('Caution: No true prob for player stat val: ' + player + ', ' + stat_name + ', ' + str(val))

                    # add keys to dict used for ref but not yet to gen true prob
                    # otherwise it will use string value to compute prob
                    # all vals in val probs dict must be probs
                    # so we should make a separate dict and combine them before display
                    stat_val_probs_dict['prev'] = prev_val

                    # we actually want to show the player current conds so we can see which probs are being used and adjust for errors
                    # {\'p1, p2 out\':\'out\', \'away\':\'loc\', ...}
                    #print('\n===Display Current Condition Cond Vals===\n')
                    # for cond_key, cond_val in player_current_conditions.items():
                    #     stat_val_probs_dict[cond_key] = cond_val
                    # # {teammates: {starters:[],...}, opp: {...}
                    # for team_cond, team_parts in player_gp_conds.items():
                    #     for team_part, team_part_players in team_parts:
                    #         # to save space, if teammates just put team part and assume same team bc opp says opp
                    #         team_part_cond_key = team_cond + ' ' + team_part # eg. 'opp starters'
                    #         if team_cond == 'teammates':
                    #             team_part_cond_key = team_part # eg. 'starters'
                    #         stat_val_probs_dict[team_part_cond_key] = team_part_players
                    # # add game num for ref so we can sort by game to ensure at least 2 picks per game 
                    # # OR if only 1 allowed still need to see game teams next to each other to place picks on same page of gui
                    # # game_num = 0
                    # # for game in game_teams:
                    # #     if player_team
                    # stat_val_probs_dict['game'] = game_num
                    stat_val_probs_dict = generate_stat_val_probs_cond_refs(game_num, prev_val, player_current_conditions, player_gp_conds, stat_val_probs_dict)

                    # we want per unit probs next to corresponding yr for comparison in table
                    # so add key above when looping thru conditions
                    #stat_val_probs_dict['all 2023 regular per unit prob'] = val_probs_dict['all 2023 regular per unit prob']

                    # one row for each val which has all conditions
                    #print('stat_val_probs_dict: ' + str(stat_val_probs_dict))
                    all_true_prob_dicts.append(stat_val_probs_dict)


                    # repeat for under
                    #print('repeat prob for under')
                    if val > 1: # for zero we only want exactly 0 prob not over under bc 1+/- includes 1 and cannot go below 0
                        under_val = val - 1
                        val_str = str(under_val) + '-'
                        stat_val_probs_dict = {'player': player, 'team': player_team, 'stat': stat_name, 'val': val_str }
                        #for conditions, prob in val_probs_dict.items():
                        # for conditions in all_conditions:
                        #     #prob = 0
                        #     #per_unit_prob = 0
                        #     if conditions in val_probs_dict.keys():
                        #         prob = val_probs_dict[conditions]
                        #         #per_unit_conditions = conditions + ' per unit'
                        #         #per_unit_prob = val_probs_dict[per_unit_conditions]
                        #         #print('over prob: ' + str(prob))
                        #         stat_val_probs_dict[conditions] = 100 - round(prob * 100)
                        #         #stat_val_probs_dict[per_unit_conditions] = 100 - round(per_unit_prob * 100)

                        #     # if condition not in val probs dict
                        #     # then this player did not play in this condition, so show NA
                        #     else:
                        #         stat_val_probs_dict[conditions] = 'NA'

                        # only need to calculate true prob for under here bc true prob for over already computed in val probs dict
                        if true_prob_key in val_probs_dict.keys():
                            prob = val_probs_dict[true_prob_key]
                            #print('over prob: ' + str(prob))
                            if prob is not None:
                                stat_val_probs_dict[true_prob_key] = 100 - round(prob * 100)
                                #print('under prob: ' + str(stat_val_probs_dict['true prob']))
                        #     else:
                        #         stat_val_probs_dict[true_prob_key] = 'NA'
                        #         print('Caution: No prob for player stat val: ' + player + ', ' + stat_name + ', ' + str(val))
                        # else: # if we cant find conditions for this val
                        #     stat_val_probs_dict[true_prob_key] = 'NA'
                        #     print('Caution: No true prob for player stat val: ' + player + ', ' + stat_name + ', ' + str(val))
                        
                        # add more fields for ref
                        # for cond_key, cond_val in player_current_conditions.items():
                        #     stat_val_probs_dict[cond_key] = cond_val
                        # # {teammates: {starters:[],...}, opp: {...}
                        # for team_cond, team_parts in player_gp_conds.items():
                        #     for team_part, team_part_players in team_parts:
                        #         # to save space, if teammates just put team part and assume same team bc opp says opp
                        #         team_part_cond_key = team_cond + ' ' + team_part # eg. 'opp starters'
                        #         if team_cond == 'teammates':
                        #             team_part_cond_key = team_part # eg. 'starters'
                        #         stat_val_probs_dict[team_part_cond_key] = team_part_players
                        # stat_val_probs_dict['game'] = game_num
                        stat_val_probs_dict = generate_stat_val_probs_cond_refs(game_num, prev_val, player_current_conditions, player_gp_conds, stat_val_probs_dict)

                        # one row for each val which has all conditions
                        #print('stat_val_probs_dict: ' + str(stat_val_probs_dict))
                        all_true_prob_dicts.append(stat_val_probs_dict)


                #print('all_true_prob_dicts: ' + str(all_true_prob_dicts))

    # remove invalid rows with NA true prob
    final_all_true_prob_dicts = []
    for dict in all_true_prob_dicts:
        if true_prob_key in dict.keys():
            final_all_true_prob_dicts.append(dict)

    #print('all_true_prob_dicts: ' + str(all_true_prob_dicts))
    return final_all_true_prob_dicts

# overall gp cond is either teammates or opp
# for a specific player, stat, val
# so not all vals reached for all samples
def generate_game_players_condition_mean_prob(team_condition, team_gp_conds, team_gp_conds_weights_dict, val_probs_dict, season_years, part, player_stat_dict):
    print('\n===Generate Game Players Condition Mean Prob: ' + team_condition + '===\n')
    print('Settings: Season Years, Season Part')
    print('\nInput: team_gp_conds = {gp condition:cond type,... = {\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ...}, opp:{...} = ' + str(team_gp_conds))
    print('Input: team_gp_conds_weights_dict = {cond_key: w1, ... = {starters:10,bench:5,... = ' + str(team_gp_conds_weights_dict))
    print('Input: val_probs_dict = {\'condition year part\': prob, ... = {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...')
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: gp_condition_mean_prob = x\n')

    gp_condition_mean_prob = None

    # for each team part, get individ samples mean prob
    # then bring together to get full team mean prob
    # similar to gen all conds mean probs
    # we need a cond for each part of team, bc we have a corresponding weight so we can get weighted prob
    all_team_parts_true_probs = {}
    
    for team_part, team_part_cond_weight in team_gp_conds_weights_dict.items():
        # for each cond, need to get mean prob over all yrs
        # separate conds by team part bc that is how we group weights
        #team_part_mean_probs = generate_team_part_mean_probs(team_part, team_gp_conds)
        team_part_mean_probs = {}
        team_part_cond_weights = {}
        team_part_conds = isolator.isolate_team_part_conds(team_part, team_gp_conds)
        for condition in team_part_conds:
            #print('\ncondition: ' + str(condition))
            # should condition mean prob be 0 or NA if no samples?
            # ideally NA bc 0 is false
            condition_mean_prob = generate_condition_mean_prob(condition, val_probs_dict, player_stat_dict, season_years, part)
            # only count probs with samples
            if condition_mean_prob is not None:
                team_part_mean_probs[condition] = condition_mean_prob

                # since its all 1 team part, the only difference in weight is no. players in combo
                cond_players = condition.split(',')
                cond_weight = len(cond_players)
                team_part_cond_weights[condition] = cond_weight
        
        # print('team_part_mean_probs: ' + str(team_part_mean_probs))
        # print('team_part_cond_weights: ' + str(team_part_cond_weights))
        
        team_part_true_prob = None
        # since its all 1 team part, the only difference in weight is no. players in combo
        weighted_probs = generate_weighted_probs(team_part_mean_probs, team_part_cond_weights)

        # CHANGE to extrap from prob distrib
        if len(weighted_probs) > 0:
            # if we are summing all values without checking key then might as well use list
            # first try list and then only use dict if needed
            all_conditions_weights = []
            for cond, weight in team_part_cond_weights.items():
                if cond in team_part_mean_probs.keys():
                    all_conditions_weights.append(weight)

            sum_weighted_probs = sum(weighted_probs)
            sum_weights = sum(all_conditions_weights)
            # print('team_part_sum_weighted_probs: ' + str(sum_weighted_probs))
            # print('team_part_sum_weights: ' + str(sum_weights))
            
            if sum_weights > 0:
                team_part_true_prob = round(sum_weighted_probs / sum_weights,2)
            else:
                print('Warning: denom = sum_weights = 0 bc no samples for condition!')

            #print('team_part_true_prob = sum_weighted_probs / sum_weights = ' + str(team_part_true_prob))
            if team_part_true_prob is not None:
                all_team_parts_true_probs[team_part] = team_part_true_prob

    #print('all_team_parts_true_probs: ' + str(all_team_parts_true_probs))

    #team_gp_conds_weights = list(team_gp_conds_weights_dict.values())
    weighted_probs = generate_weighted_probs(all_team_parts_true_probs, team_gp_conds_weights_dict)

    # CHANGE to extrap from prob distrib
    if len(weighted_probs) > 0:
        # if we are summing all values without checking key then might as well use list
        # first try list and then only use dict if needed
        all_conditions_weights = []
        for cond, weight in team_gp_conds_weights_dict.items():
            if cond in all_team_parts_true_probs.keys():
                all_conditions_weights.append(weight)
        sum_weighted_probs = sum(weighted_probs)
        sum_weights = sum(all_conditions_weights)
        # print('gp_sum_weighted_probs: ' + str(sum_weighted_probs))
        # print('gp_sum_weights: ' + str(sum_weights))

        if sum_weights > 0:
            gp_condition_mean_prob = round(sum_weighted_probs / sum_weights,2)
        else:
            print('Warning: denom = sum_weights = 0 bc no samples for condition!')

    print('gp_condition_mean_prob: ' + str(gp_condition_mean_prob))
    return gp_condition_mean_prob

# for conditions we must get a sub-prob weighted mean for all year samples with that condition 
# just like old true prob bc takes one condition and gets all yrs samples combined into weighted avg
# where each yr adds 1 to the inverse multiplier so as data gets far away it gets less weight
# yr multiplier is arbitrary and must be discovered by ml algo
def generate_condition_mean_prob(condition, val_probs_dict, player_stat_dict, season_years, part):
    print('\n===Generate Condition Mean Prob: ' + condition + '===\n')
    print('Settings: Season Years, Season Part')
    print('\nInput: val_probs_dict = {\'condition year part\': prob, ... = {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...')
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: condition_mean_prob = x\n')

    condition_mean_prob = None # need samples or prob distrib?

    probs = []
    # in this fcn it is for 1 condition and part of season so the conditions will just be different years, so 1 for each year
    all_current_conditions = [] # header field title 'condition year part'
    all_cur_cond_dicts = [] # cur_cond_dict = {'condition':condition, 'year':year, 'part':part}
    
    

    # we dont need to label probs in dict 
    # bc they are same condition in order by year going from recent to distant
    for year_idx in range(len(season_years)):
        year = season_years[year_idx]
        #print('\nyear: ' + str(year))

        # for each yr, we need a new cur cond dict bc the yr changes the cur conds
        cur_cond_dict = {'condition':condition, 'year':year, 'part':part}
        current_conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
        if year_idx > 0:
            current_conditions += ' per unit'
        #print('current_conditions: ' + str(current_conditions))

        if current_conditions in val_probs_dict.keys():
            probs.append(val_probs_dict[current_conditions])
            #all_current_conditions.append(current_conditions)
            all_cur_cond_dicts.append(cur_cond_dict)

    # print('probs: ' + str(probs))
    # print('all_cur_cond_dicts: ' + str(all_cur_cond_dicts))

    # if no probs or cur conds then no need to find weights
    # which means unable to find cur conds in val probs dict so prob unknown
    # default condition mean prob to 0 for now but eventually can use other similar players mean prob but that would need to be separate bc it is not measured for this player
    # but if default to 0 then we must differentiate those without samples and those with samples who have reached line 0 times
    if len(probs) > 0:

        sample_sizes = []
        for p_idx in range(len(probs)):
            cur_conds = all_cur_cond_dicts[p_idx]
            s_n = determiner.determine_sample_size(player_stat_dict, cur_conds) # for a given yr
            sample_sizes.append(s_n)
        #print('sample_sizes: ' + str(sample_sizes))

        s_1 = sample_sizes[0]

        t_1 = 1 # set bc current year is origin so multiply by 1. each year adds 1 as weight decreases. that weight should be determined by ml algo
        
        # already added first weight to list so start from idx 1
        # get weights by relation where each year adds 1 to divisor
        # eg this yr is 1 so divide by 1, prev yr is 2 and so on
        # this is arbitrary and must get more accurate way to show decay of relevance
        w_1 = 1.0 # other weights relative to current yr sample
        weights = [w_1]
        for p_idx in range(1,len(probs)):
            t_n = p_idx + 1 # years away
            s_n = sample_sizes[p_idx] #65 #previous years
            w_n = round(w_1 * round(t_1 / t_n, 6) * round(s_n / s_1, 6), 2)
            weights.append(w_n)
        #print('weights: ' + str(weights))

        # solved for other ws in relation to w_1 already used to sub above
        #true_prob = 0#w_1 * p_1
        weighted_probs = []#0
        for p_idx in range(len(probs)):
            prob = probs[p_idx]
            #print('prob: ' + str(prob))
            w = weights[p_idx]
            #print('w: ' + str(w))
            wp = round(w * prob, 6)
            #print('wp: ' + str(wp))
            weighted_probs.append(wp) #+= wp
            #print('true_prob: ' + str(true_prob))
        
        sum_weights = sum(weights)
        if sum_weights > 0:
            condition_mean_prob = round(sum(weighted_probs) / sum_weights, 2)
        else:
            print('Warning: sum_weights 0 bc no samples for condition!')
        
    print('condition_mean_prob: ' + str(condition_mean_prob))
    return condition_mean_prob

# player_current_conditions = {loc:away, out:[p1,....],...}
# need all_players_abbrevs, all_players_teams, cur_yr, all_box_scores to get player abbrev to match cond with lineup
# all_conditions_mean_probs = {c1:p1,...}
def generate_all_conditions_mean_probs(val_probs_dict, player_current_conditions, all_gp_conds, all_gp_conds_weights, prev_val, player_stat_dict, all_players_abbrevs, all_players_teams, all_box_scores, season_years, part, player='player', stat='stat', val='val'):
    print('\n===Generate All Conditions Mean Probs: ' + player.title() + ', ' + stat.upper() + ', ' + str(val) + '===\n')
    print('Settings: Season Years, Season Part')
    print('\nInput: val_probs_dict = {\'condition year part\': prob, ... = {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...')
    print('Input: player_current_conditions = {loc:away, start:start, prev:5, ...},... = {loc: away, start: bench, ... = ' + str(player_current_conditions))
    print('Input: all_gp_conds = {team condition:{gp condition:cond type,... = {teammates:{\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ...}, opp:{...} = ' + str(all_gp_conds))
    print('Input: all_gp_conds_weights = {team condition:{cond_key: w1, ... = {teammates: {starters:10,bench:5,...}, opp:{...}, ... = ' + str(all_gp_conds_weights))
    print('Input: prev_val = ' + str(prev_val))
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: all_conditions_mean_probs = [p1,...]\n')

    # can make list bc temp use prefer speed since already aligned with weights list in loop
    all_conditions_mean_probs = {} # condition:prob

    # should we add 'all' cond to player cur conds dict so it is treated like all others???
    #conditions = ['all']# + list(player_current_conditions.values())
    condition = 'all'
    condition_mean_prob = generate_condition_mean_prob(condition, val_probs_dict, player_stat_dict, season_years, part)
    if condition_mean_prob is not None:
        all_conditions_mean_probs[condition] = condition_mean_prob
    
    #game_players_cond_keys = ['out', 'starters', 'bench']
    
    for cond_key, cond_val in player_current_conditions.items():
        # ignore opp team bc included in group cond but used here as ref
        # could change to add game key to gp dict
        if cond_key != 'opp team':
            #conditions.append(cond_val)

        # if cond_key in game_players_cond_keys:#== 'out':
        #     for game_player in cond_val: # gameplayer eg out player
        #         game_player_abbrev = converter.convert_player_name_to_abbrev(game_player, all_players_abbrevs)#, all_players_teams, cur_yr, all_box_scores)
        #         final_cond_val = game_player_abbrev + ' ' + cond_key
        #         #print('final_cond_val: ' + str(final_cond_val))
        #         conditions.append(final_cond_val)
        # else:
        #     conditions.append(cond_val)

    # print('conditions: ' + str(conditions))
    # for condition in conditions:
        # print('\ncondition: ' + str(condition))
        #all_conditions_mean_probs[condition] = generate_condition_mean_prob(condition, val_probs_dict, season_years, part, player_stat_dict)
            condition_mean_prob = generate_condition_mean_prob(cond_val, val_probs_dict, player_stat_dict, season_years, part)

            #all_conditions_mean_probs[condition] = condition_mean_prob
            if condition_mean_prob is not None:
                all_conditions_mean_probs[cond_key] = condition_mean_prob


    # now that we have mean probs for individual conds, we need for game players conds
    # we need for both outer layer gp conds: teammates and opp
    # bc always parallel to outer layer
    for team_condition, team_gp_conds in all_gp_conds.items():
        #print('\nteam_condition: ' + str(team_condition))
        team_gp_conds_weights = all_gp_conds_weights[team_condition]
        #all_conditions_mean_probs[condition] = generate_condition_mean_prob(condition, val_probs_dict, season_years, part, player_stat_dict)
        condition_mean_prob = generate_game_players_condition_mean_prob(team_condition, team_gp_conds, team_gp_conds_weights, val_probs_dict, season_years, part, player_stat_dict)

        if condition_mean_prob is not None:
            #all_conditions_mean_probs[condition] = condition_mean_prob
            all_conditions_mean_probs[team_condition] = condition_mean_prob


    # prev val at end
    # bc depends on stat
    cond_key = 'prev'
    condition = str(prev_val) + ' ' + cond_key
    condition_mean_prob = generate_condition_mean_prob(condition, val_probs_dict, player_stat_dict, season_years, part)
    if condition_mean_prob is not None:
        all_conditions_mean_probs[cond_key] = condition_mean_prob


    #print('all_conditions_mean_probs: ' + str(all_conditions_mean_probs))
    return all_conditions_mean_probs

def generate_weighted_probs(all_conditions_mean_probs, all_conditions_weights):
    print('\n===Generate Weighted Probs===\n')
    print('Input: all_conditions_mean_probs = {cond1:p1,... = ' + str(all_conditions_mean_probs))
    print('Input: all_conditions_weights = {cond1:w1,... = ' + str(all_conditions_weights))
    print('\nOutput: weighted_probs = [wp1,...]\n')

    # all_conditions_weights = [w1,...]
    # solved for other ws in relation to w_1 already used to sub above
    # always outer layer of conditions
    weighted_probs = []
    #for p_idx in range(len(all_conditions_mean_probs)):
    for cond, prob in all_conditions_mean_probs.items():
        #prob = all_conditions_mean_probs[p_idx]
        #print('prob: ' + str(prob))
        weight = all_conditions_weights[cond]
        #print('weight: ' + str(weight))
        wp = round(weight * prob, 6)
        #print('wp: ' + str(wp))
        weighted_probs.append(wp)
        #true_prob += wp
        #print('true_prob: ' + str(true_prob))

    print('weighted_probs: ' + str(weighted_probs))
    return weighted_probs

# part of season we only care about current bc it doesnt help to compare when we already have full stats which includes both parts
# conditions = [all, home/away, ...] = [all,l1,c1,d1,t1,...] OR {loc:l1, city:c1, dow:d1, tod:t1,...}
# player current conds = p1:{loc:l1, city:c1, dow:d1, tod:t1,...}
# all_conditions_weights = [w1,...]
# gp_current_conditions, where gp = game players
def generate_true_prob(val_probs_dict, player_current_conditions, all_conditions_weights_dict, all_gp_conds, all_gp_conds_weights, prev_val, prev_val_weight, player_stat_dict, all_players_abbrevs, all_players_teams, all_box_scores, season_years, part, player='player', stat='stat', val='val'):
    print('\n===Generate True Prob: ' + player.title() + ', ' + stat.upper() + ', ' + str(val) + '===\n')
    print('Settings: Season Years, Season Part')
    print('\nInput: val_probs_dict = {\'condition year part\': prob, ... = {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...')
    print('Input: player_current_conditions = {loc:away, start:start, prev:5, ... = ' + str(player_current_conditions))
    print('Input: all_gp_conds = {team condition:{gp condition:cond type,... = {teammates:{\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ...}, opp:{...} = ' + str(all_gp_conds))
    print('Input: all_conditions_weights_dict = {cond_key: w1, ... = {teammates: 15, opp:10, loc:2, ... = ' + str(all_conditions_weights_dict))
    print('Input: all_gp_conds_weights = {team condition:{cond_key: w1, ... = {teammates: {starters:10,bench:5,...}, opp:{...}, ... = ' + str(all_gp_conds_weights))
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: true_prob = x\n')

    # default None bc if no samples then prob unknown but not 0
    true_prob = None

    # p_true = w1p1 + w2p2
    # where w1+w2=1
    # and w_t=w1/t so w2=w1/2
    # for each year or condition, add prob to list
    # how do we know all years of interest?
    # can we get from info already passed?
    # yes from val 0 bc it is evaled for all conditions?
    # the user already passed seasons of interest so we can use that
    # how do we decide probs of interest? from curr conds
    # always include overall season probs
    # if a val not reached in a condition then it will not be included here
    
    
    # for conditions we must get a sub-prob weighted mean for all year samples with that condition 
    # then we can weight conditions relative to each other
    # it makes more sense to combine all the samples for a current condition to get as many samples as possible for the current condition
    # we must adjust by rate and weight to scale past season samples to current season relevance
    # all_conditions_mean_probs = {c1:p1,...}
    all_conditions_mean_probs = generate_all_conditions_mean_probs(val_probs_dict, player_current_conditions, all_gp_conds, all_gp_conds_weights, prev_val, player_stat_dict, all_players_abbrevs, all_players_teams, all_box_scores, season_years, part, player, stat, val) # for the stat described in val probs dict

    # all_conditions_weights = [w1,...]
    # solved for other ws in relation to w_1 already used to sub above
    # always outer layer of conditions
    #all_conditions_weights = list(all_conditions_weights_dict.values()) + [prev_val_weight]
    all_conditions_weights_dict['prev'] = prev_val_weight
    weighted_probs = generate_weighted_probs(all_conditions_mean_probs, all_conditions_weights_dict)

    # if we are summing all values without checking key then might as well use list
    # first try list and then only use dict if needed
    all_conditions_weights = []
    for cond, weight in all_conditions_weights_dict.items():
        if cond in all_conditions_mean_probs.keys():
            all_conditions_weights.append(weight)

    sum_weights = sum(all_conditions_weights)
    if sum_weights > 0:
        true_prob = round(sum(weighted_probs) / sum_weights,2)
    else:
        print('Warning: denom = sum_weights = 0 bc no samples for condition!')

    print('true_prob: ' + str(true_prob))
    return true_prob 




# 'A Gordon PF, C Braun G, D Jordan C, J Murray PG, J Strawther G, K Caldwell-Pope SG, M Porter Jr SF, N Jokic C, P Watson F, R Jackson PG, Z Nnaji PF in': {'1': 31}



# conditions related to players in game
# same as gen cond sample weight except add samples for each separate condition making up overall cond
# eg p1, p2, ... out also has p1 out and p2 out conds which are considered separate samples even though they overlap
def generate_game_players_cond_sample_weight(cond_key, lineup_team, team_gp_cur_conds, player_stat_dict, part, player=''):
    print('\n===Generate Game Players Condition Sample Weight: ' + player.title() + '===\n')
    print('Settings: Season Part, Player')
    #print('\nInput: team_condition = \'teammates\' or \'opp\' = cond_key = \'' + team_condition + '\'')
    #print('Input: lineup = {starters: [players],...}, opps: {...} = cond_val = ' + str(lineup))
    print('\nInput: cond_key = ' + cond_key) # either team condition or cond type
    print('Input: lineup_team = ' + lineup_team)
    print('Input: team_gp_cur_conds = {gp condition:cond type,... = {\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ... = ' + str(team_gp_cur_conds))
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: game_players_cond_weight = x\n')

    game_players_cond_weight = None #() # (teammates, opps)

    # first consider outer layer?
    # bc runs in parallel with other conditions
    # could possibly combine this fcn with gen cond sample weights if similar enough
    cond_weights = {'teammates': 10, 
                    'opp':5, 
                    'starters': 10, 
                    'bench': 4, 
                    'out': 2, 
                    'in': 2 }
    # player_cond_weights = {'starters': 10, 
    #                         'bench': 4, 
    #                         'out': 2, 
    #                         'in': 2 }
    team_conds = ['teammates', 'opp']
    #gp_cond_weights = {}

    # overall team gp cur conds will run first
    # and then for each team part
    combined_conditions = team_gp_cur_conds
    if cond_key not in team_conds:
        # get subset of conds matching key
        combined_conditions = {}
        for gp_cond, cond_type in team_gp_cur_conds.items():
            if cond_type == cond_key:
                combined_conditions[gp_cond] = cond_type # direct transfer if passes filter
    #print('combined_conditions: ' + str(combined_conditions))

    # special condition sample size with all separate player conds inside combo player cond
    #conditions = generate_game_players_conditions(lineup, lineup_team, all_players_abbrevs, player)
    combined_sample_size = determiner.determine_combined_conditions_sample_size(player_stat_dict, combined_conditions, part) # for all yrs
    
    if combined_sample_size > 0:
        combined_sample_weight = round(math.log10(combined_sample_size),6) # or ln? need to test both by predicting yrs that already happened so we can give supervised feedback
        #print('combined_sample_weight = log(combined_sample_size) = ' + str(combined_sample_weight))

        cond_weight = cond_weights[cond_key]
        #print('cond_weight: ' + str(cond_weight))

        game_players_cond_weight = round(float(cond_weight) * combined_sample_weight, 2)

        # for team_part, team_part_players in lineup.items():
        #     # get dict of each cond weight:sample weight pair
        #     # eg player out, players out
        #     gp_cond_sample_weight = generate_condition_sample_weight(player_stat_dict, team_part, team_part_players, part, player, player_cond_weights)
        #     #gp_cond_weights[team_part] = gp_cond_sample_weight

        #     # increase weight for multiplayer
        #     # if re.search(',',cond_val):
        #     #     num_players = cond_val.count(',') + 1
        #     #     cond_weight += num_players

        #     # get a weighted prob only accounting for player conds
        #     game_players_true_prob = generate_true_prob() # player_conds_true_prob

            # sum(weight*samples) / sum(samples)


    
    #print('game_players_cond_weight: ' + str(game_players_cond_weight))
    return game_players_cond_weight#, game_players_true_prob


# for all cond, cond key = cond val = all
# cond key = loc, cond val = 'home' or 'D Green PF out', etc
# combine condition weight and sample weight to get adjusted weight
def generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, player='', cond_weights={}):
    print('\n===Generate Condition Sample Weight: ' + player.title() + '===\n')
    print('Setting: Season Part = ' + part)
    print('Setting: Condition Key = ' + cond_key)
    print('Setting: Condition Value = ' + str(cond_val))
    print('\nInput: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: condition_sample_weight = w = cond_weight * sample_weight\n')

    condition_sample_weight = None # if sample size 0 then weight 0 or None?

    # need to tune these arbitrary weights
    # when they always start or bench then start=all
    # so would it still have more weight?
    # similar if a teammate is almost always out then it makes almost no difference
    # how it was when out but it matters the few games they were in
    # that would be covered in game teammates condition
    # does that mean some conditions dont apply to all players?
    # from an absolute perspective, starting a game usually means more minutes so higher stats
    # whereas location barely affects minutes but can affect energy and performance
    # whereas teammate out/in affects minutes and stat attempts rate
    # if start=all then all samples condition will overpower every other condition
    # based on sample size, which would mislead away from important conditions like teammates in/out
    # if player starts most, but is benched a few how does that affect? 
    # then those few bench games do prove useful so make it neglect any condition that equals all
    # if a player is in does it have same opposite weight as if they are out?
    # with each player accounting for in or out as group, the weight goes up bc more specific but less sample size
    # player_cond_weights = {'starters': 10, 
    #                         'bench': 4, 
    #                         'out': 2, 
    #                         'in': 2 }
    
    if len(cond_weights) == 0:
        cond_weights = {'all': 1, 
                        'loc':3, 
                        'city':2,
                        'dow':3, 
                        'tod':3, 
                        'coverage':2,
                        'audience':2,
                        'start':6, 
                        'teammates': 10, 
                        'opp':5, 
                        'prev':5,
                        'opp team':0, # placed in top level for ref but given no weight bc integrated in opponents group cond
                        'time before':2, 
                        'time after':3, 
                        'former':3,
                        'wos':3, # week of season
                        'wop':3} # week of play
    
    # get mean probs and weights for player conds
    # if re.search('opp', cond_key):
    #     cond_key = 'opp'
    # elif cond_key in player_cond_weights.keys():
    #     cond_key = 'teammates'

    
    s_n = determiner.determine_condition_sample_size(player_stat_dict, cond_val, part) # for all yrs
    
    # player_conds = ['teammates', 'opp']
    # if cond_key in player_conds:
    #     conditions = generate_game_players_conditions(lineup, lineup_team, all_players_abbrevs, player)
    #     s_n = determiner.determine_combined_conditions_sample_size(player_stat_dict, conditions, part) # for all yrs
    
    # if same sample size as all then do we know it is = all? yes bc includes all yrs
    # if cond != all but same sample size, then cond sample 0 bc only 1 cond same as all and we cannot differentiate from all
    # if assigned same weight as all if same sample, then it would mislead to give more weight to irrelevant samples
    # not 'all' condition, but same sample size, so this cond applies to all samples
    # and so does not differentiate conditions
    # what if randomly started or benched 1 game?
    # then other cond will have huge sample size with huge weight even though it is basically the same as 'all' condition
    # on the other hand, we want to offset other conditions with this condition
    # bc the condition is still valid even if it applies to all games
    # by minimizing the effect of sample size with log fcn we can still account for this condition even if it applies to all games
    # bc it tells us 1 important factor affecting his stats, eg teammate in happens to be all games but still important factor controlling the game
    # another example is if a teammate is always out then they would not be in teammates list, but if they are always out they have no effect, but if they are always in they have a massive effect but we cant tell what it is bc there is nothing to compare it to
    # keeping a cond even if it equals all is saying that cond has more weight than if all had no other factors applying to all condition
    # so we must have all with no other factors less than all with other factors
    # if cond_key != 'all':
    #     all_sample_size =  determiner.determine_condition_sample_size(player_stat_dict, cond_val, part) # for all yrs
    #     if s_n == all_sample_size:
    #         s_n = 0 

    #sample_sizes.append(s_n)
    # log(0)=-inf
    # if cond != all but same sample size, then cond weight 0
    if s_n > 0:
        # log10(100)=2, log(100)~=4.6
        # log10(10)=1
        # we want sample size to have very little effect
        # bc we want the condition weights to control the outcome with slight adjustments to account for sample size
        # bc some conditions have tons of samples of same val while only small number of samples of other val but the condition itself should hold about the same weight
        sample_weight = round(math.log10(s_n),6) # or ln? need to test both by predicting yrs that already happened so we can give supervised feedback
        #print('sample_weight = log(sample_size) ' + str(sample_weight))
        #print('condition_sample_weight = ' + str(cond_weights[cond_key]) + ' * ' + str(sample_weight))
        
        cond_weight = cond_weights[cond_key]
        #print('cond_weight: ' + str(cond_weight))

        condition_sample_weight = round(float(cond_weight) * sample_weight, 2)
    
    #print('condition_sample_weight = cond_weight*sample_weight: ' + str(condition_sample_weight))
    return condition_sample_weight

def generate_prev_val_weight(prev_val, player_stat_dict, part, player):
    # print('\n===Generate Prev Val Weight===\n')
    # print('Input: prev_val = ' + str(prev_val))

    cond_key = 'prev'
    cond_val = str(prev_val) + ' ' + cond_key

    return generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, player)


# player_current_conditions = {'loc':'away','out':[p1,...],...}
# all_conditions_weights = [w1,...]
# combine cond weight and sample size to get adjusted cond weight
def generate_all_conditions_weights(player_current_conditions, all_gp_conds, player_prev_vals, player_stat_dict, all_players_abbrevs, part, player='', player_team='', opp_team=''):
    print('\n===Generate All Conditions Weights: ' + player.title() + '===\n')
    print('Settings: Season Part, Player')
    print('Setting: Player Team to match player abbrevs in all years = \'' + player_team + '\'') # only cur team allowed?
    #print('\nInput: game_player_cur_conds = {teammates: {starters: [],...}, opps: {...} = ' + str(game_player_cur_conds))
    print('\nInput: player_current_conditions = {loc:away, start:start, prev:5, ... = ' + str(player_current_conditions))#{\'p1, p2 out\':\'out\', \'away\':\'loc\', ...},... = [\'away\':\'loc\', \'V Cancar SF, J Murray PG,... out\':\'out\', ...')
    print('Input: all_gp_conds = {team condition:{gp condition:cond type,... = {teammates:{\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ... = ' + str(all_gp_conds))
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-mem\': \'jaren jackson jr\',...')
    print('\nOutput: all_conditions_weights = {cond_key: w1, ... = {teammates:15, opp:10, loc:2, prev:x, ... ')
    print('Output: all_gp_conds_weights = {team condition:{cond_key: w1, ... = {teammates: {starters:10,bench:5,...}, opp:{...}, ... \n')

    all_conditions_weights = {} # adjusted for sample size
    all_gp_conds_weights = {}

    # if cur_yr == '':
    #     cur_yr = determiner.determine_current_season_year()
    
    # get weights for each condition prob
    # 1 sample size per condition, bc each condition gets total sample size over all yrs
    #sample_sizes = []
    all_cond = 'all'
    condition_sample_weight = generate_condition_sample_weight(player_stat_dict, all_cond, all_cond, part, player)
    all_conditions_weights[all_cond] = condition_sample_weight

    for cond_key, cond_val in player_current_conditions.items():
        # print('condition: ' + str(condition))
        # print('condition_type: ' + str(condition_type))

        # ignore game players conditions bc condensed into teammates and opps cond keys/types
        # ignore opp team bc included in group prob but used here as ref
        if cond_key != 'opp team':
            condition_sample_weight = generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, player)
            if condition_sample_weight is not None:
                all_conditions_weights[cond_key] = condition_sample_weight

    #all_conditions_weights = generate_all_game_players_cond_sample_weights()
    #print('\n===Generate All Game Players Condition Sample Weights===\n')
    # get cond sample weight for all teammates samples! outer layer
    # this outer layer always has 2 conditions: teammates and opps
    # so get all connected samples but only unique games so dont count as another sample if from same game
    # all samples in same game count as 1 sample bc 1 game
    for team_condition, team_gp_cur_conds in all_gp_conds.items():
        # print('team_condition: ' + team_condition)
        # print('team_gp_cur_conds: ' + str(team_gp_cur_conds))
        # need lineup team to match player abbrev key
        # to find multiple abbrevs
        # we are looking at the current player and lineup so get player current team
        lineup_team = player_team
        opp_key = 'opp'
        opp_team_key = opp_key + ' team'
        if team_condition == opp_key:
            lineup_team = player_current_conditions[opp_team_key]
        #print('lineup_team: ' + str(lineup_team))
        
        # gen overall team gp cond weight, before getting team part weights
        # generate player condition mean weights before passing to generate condition sample weight
        game_players_cond_weight = generate_game_players_cond_sample_weight(team_condition, lineup_team, team_gp_cur_conds, player_stat_dict, part, player)
        all_conditions_weights[team_condition] = game_players_cond_weight

        # after getting overall team weight, get individ weights for each team part
        all_gp_conds_weights[team_condition] = {'starters': 0, 
                                                'bench': 0, 
                                                'out': 0, 
                                                'in': 0 }
        for gp_cond_key in all_gp_conds_weights[team_condition].keys():
            gp_cond_weight = generate_game_players_cond_sample_weight(gp_cond_key, lineup_team, team_gp_cur_conds, player_stat_dict, part, player)
            if gp_cond_weight is not None:
                all_gp_conds_weights[team_condition][gp_cond_key] = gp_cond_weight

    # game_players_cond_keys = ['out', 'starters', 'bench']

    # for cond_key, cond_val in player_current_conditions.items():
    #     #print('\ncond_key: ' + str(cond_key))
    #     #print('cond_val: ' + str(cond_val))

    #     if cond_key in game_players_cond_keys:#== 'out':
    #         #cond_vals = []
    #         # need diff conds for each out player
    #         # out_player = full name
    #         for game_player in cond_val:
    #             #print('\ngame_player: ' + str(game_player))
    #             # need to convert player full name to abbrev with position to compare to condition titles
    #             # at this point we have determined full names from abbrevs so we can refer to that list
    #             # NEXT: save player abbrevs for everyone played with
    #             game_player_abbrev = converter.convert_player_name_to_abbrev(game_player, all_players_abbrevs)#, all_players_teams, cur_yr, all_box_scores)
    #             # if out_player in all_players_abbrevs[cur_yr].keys():
    #             #     out_player_abbrev = all_players_abbrevs[cur_yr][out_player] #converter.convert_player_name_to_abbrev(out_player)
    #             # else:
    #             #     if out_player in all_players_teams[cur_yr].keys():
    #             #         # out_player_teams = all_players_teams[cur_yr][out_player]
    #             #         # out_player_team = determiner.determine_player_current_team(out_player, out_player_teams, cur_yr, rosters)
    #             #         out_player_abbrev = reader.read_player_abbrev(out_player, all_players_teams, cur_yr, all_box_scores)
    #             #     else:
    #             #         print('Warning: out player not in all players current teams! ' + out_player)

    #             # D Green PF out
    #             final_cond_val = game_player_abbrev + ' ' + cond_key # D Green PF out
    #             #print('final_cond_val: ' + str(final_cond_val))
    #             condition_sample_weight = generate_condition_sample_weight(player_stat_dict, cond_key, final_cond_val, part, season_years)
    #             all_conditions_weights.append(condition_sample_weight)
    #     else:
    #         condition_sample_weight = generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, season_years)
    #         all_conditions_weights.append(condition_sample_weight)
    

    # do we compare to first condition sample size or total samples
    # weights are relative to first condition so is it easier to make sample size relative to first condition also?
    # it should be the same bc the first condition is all which should include total samples
    #s_1 = sample_sizes[0] # should be all samples
    # we are using log10(sample size) to show how weight scales relative to sample size

    # all_conditions_weights = [w1,...]
    # print('all_conditions_weights: ' + str(all_conditions_weights))
    # print('all_gp_conds_weights: ' + str(all_gp_conds_weights))
    return (all_conditions_weights, all_gp_conds_weights)

# given players in lineup, lineup team, and all abbrevs
# make combos of all abbrevs
def generate_combos_of_abbrevs(game_players):#, lineup, lineup_team, all_players_abbrevs):
    # print('\n===Generate Combos of Abbrevs===\n')
    # print('Input: game_players = {name:[abbrevs], ...} = {patrick baldwin:[P Baldwin F, Baldwin Jr F], aaron gordon:[A Gordon PF], ...} = ' + str(game_players))
    # print('\nOutput: all_combos = [[P Baldwin F, A Gordon PF,...], [Baldwin Jr F, A Gordon PF,...], ...]\n')

    #game_players = {'patrick baldwin':['P Baldwin F', 'Baldwin Jr F'], 'aaron gordon':['A Gordon PF']}
    
    all_game_players_abbrevs = list(game_players.values())
    
    all_combos = list(itertools.product(*all_game_players_abbrevs))

    # make list of abbrevs allowing only 1 per player
    # len of combo = len of players bc 1 per player per combo
    # imagine each player only had 1 abbrev, then len(combos)=1
    #combo = []
    # list idxs to use for each abbrev for each player
    # first run abbrev_idxs = [1,1,1,...]
    # last = []
    # for player_name, player_abbrevs in game_players.items():
        
    #     abbrev_idx = 0
    #     player_abbrev = player_abbrevs[abbrev_idx]
        
    #     if player_abbrev not in combo: # does not work if 2 players with same abbrev
    #         combo.append(player_abbrev)


    # print('combo: ' + str(combo))
    
    # all_combos.append(combo)



    # combo = ''
    # combo_num = 1
    # # first get all the combos relative to each player
    # player_combo = ''
    # player_idx = 0
    # player_num = 1
    # #for player_idx in range(len(game_players)):
    # for main_player, main_player_abbrevs in game_players.keys():
    #     print('\nmain_player: ' + main_player)
    #     #main_player = list(game_players.keys())[player_idx]
    #     for mp_abbrev in main_player_abbrevs:
    #         combo = mp_abbrev # same player never in same combo so reset for each one of the main player's abbrevs

    #         for game_player, game_player_abbrevs in game_players.items():
    #             print('game_player: ' + game_player)
    #             # each loop adds to the prev one
                
    #             if main_player != game_player:
    #                 for abbrev in game_player_abbrevs:
    #                     print('abbrev: ' + abbrev)
    #                     # each abbrev gets added to a different string
    #                     combo 

    #print('all_combos: ' + str(all_combos))
    return all_combos

# special condition sample size with all separate player conds inside combo player cond
# these conds go to tell all player conds sample size
# so we only consider unique samples/games
# so if 2+ players are out same game it only counts as 1 sample
# even tho there are multiple subconditions with players together and each player separate
def generate_game_players_conditions(lineup, lineup_team, all_players_abbrevs, player='', team_condition=''):
    # print('\n===Generate Game Players Conditions: ' + player.title() + '===\n')
    # print('Input: lineup = cond_val = {starters: [players],...}, opps: {...} = {\'starters\': [\'jamal murray\',...], ... = \'' + str(lineup) + '\'')
    # print('Input: lineup_team = team abbrev = \'' + lineup_team + '\'')
    # print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-mem\': \'jaren jackson jr\',...')
    # print('\nOutput: game_players_conditions = {condition:cond type,... = {\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ...\n')
    
    game_players_conditions = {}

    # separate inkey to get more samples, in = not out
    in_key = 'in'
    out_key = 'out'
    opp_key = 'opp'
    # make dict so we can tell if player has 2 abbrevs so we must check both in past box scores
    game_players = {} # {abbrev:player)

    # first get all players abbrevs
    # and then run lineups with both/all versions of player abbrevs
    all_game_players_abbrevs = {}#generate_all_game_players_abbrevs(lineup, lineup_team, all_players_abbrevs) # need all abbrevs for all players in this lineup so we can run all combos of abbrevs

    # for each player in lineup, assign condition and add to group conds
    # remember to only take unique samples to get sample size
    # or all bench players would add up to hundreds of extra samples
    for team_part, team_part_players in lineup.items():
        #print('\nteam_part: ' + str(team_part))
        game_part_players = {} # {abbrev:player}
        for game_player in team_part_players:
            #print('\ngame_player: ' + str(game_player))
            # lineup team = game_player_team in lineup
            game_player_abbrevs = converter.convert_player_name_to_abbrevs(game_player, all_players_abbrevs, lineup_team)
            all_game_players_abbrevs[game_player] = game_player_abbrevs

            # add game player to group cond
            game_part_players[game_player] = game_player_abbrevs
            if team_part != out_key:
                game_players[game_player] = game_player_abbrevs

            # assign game player cond: starters/bench and in?
            # do not include current player or interest in single player conditions (but still add to group conditions)
            if game_player != player and len(game_player_abbrevs) > 0:
                for game_player_abbrev in game_player_abbrevs:
                    condition = game_player_abbrev
                    if team_condition == opp_key:
                        condition += ' ' + opp_key 
                    condition += ' ' + team_part
                    game_players_conditions[condition] = team_part
                
                    if team_part != out_key:
                        condition = game_player_abbrev
                        if team_condition == opp_key:
                            condition += ' ' + opp_key 
                        condition += ' ' + in_key
                        game_players_conditions[condition] = in_key

        if len(game_part_players.keys()) > 1:
            # convert to list of game_part_players_strings with all combos of abbrevs
            combos_of_abbrevs = generate_combos_of_abbrevs(game_part_players)#, all_game_players_abbrevs)
            
            # need a string for each combo
            for abbrev_combo in combos_of_abbrevs:
                #print('abbrev_combo: ' + str(abbrev_combo))

                game_part_players_str = converter.convert_to_game_players_str(abbrev_combo)
                # game part players, where part = starters or bench or out
                #game_players_str += ' ' + cond_key
                game_part_players_cond_val = game_part_players_str
                if team_condition == opp_key:
                    game_part_players_cond_val += ' ' + opp_key 
                game_part_players_cond_val += ' ' + team_part
                #print('game_part_players_cond_val: ' + str(game_part_players_cond_val))
                game_players_conditions[game_part_players_cond_val] = team_part

    # add all players probs here bc we dont need in condition until now since we already have starters and bench which makes up in
    # we do not want to show in condition due to clutter but still account for it
    if len(game_players.keys()) > 0: # all players in game
        # convert to list of game_part_players_strings with all combos of abbrevs
        combos_of_abbrevs = generate_combos_of_abbrevs(game_players)
        # need a string for each combo
        for abbrev_combo in combos_of_abbrevs:
            #print('abbrev_combo: ' + str(abbrev_combo))
    
            game_players_str = converter.convert_to_game_players_str(abbrev_combo)
                
            game_players_cond_val = game_players_str
            if team_condition == opp_key:
                game_players_cond_val += ' ' + opp_key
            game_players_cond_val += ' ' + in_key
            #print('game_players_cond_val: ' + str(game_players_cond_val))
            game_players_conditions[game_players_cond_val] = in_key

    #print('game_players_conditions: ' + str(game_players_conditions))
    return game_players_conditions

# all_stat_probs_dict = {player:stat:val:conditions:prob}
# all_stat_probs_dict has both orig and per unit stats so no need for all_per_unit_stat_probs_dict
# instead made per unit stat records
# all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...}
def generate_all_true_probs_dict(all_stat_probs_dict, all_player_stat_dicts, all_players_abbrevs={}, all_players_teams={}, rosters={}, all_box_scores={}, all_cur_conds_dicts={}, all_game_player_cur_conds={}, all_prev_vals={}, season_years=[], cur_yr='', stats_of_interest=[]):
    print('\n===Generate All True Probs Dict===\n')
    print('Settings: Season Years, Current Year to get cur team')
    print('\nInput: all_stat_probs_dict = {player: {stat name: {stat val: {\'condition year part\': prob, ... = {\'kyle kuzma\': {\'pts\': {0: {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...')
    print('Input: all_player_stat_dicts = {player: {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'kyle kuzma\': {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')
    print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('Input: teams_current_rosters = {team:[players],..., {\'nyk\': [jalen brunson, ...], ...}')
    print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
    print('Input: all_cur_conds_dicts = {p1:{loc:away, start:start, dow:5, ...},... = {christian braun: {loc: away, start: bench, ... = ' + str(all_cur_conds_dicts))
    print('Input: all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ... = {christian braun: {teammates: {out: [...], starters: [jamal murray,...], ... = ' + str(all_game_player_cur_conds))
    print('Input: all_prev_vals = {player:{stat name:prev val,...}, ... = {jalen brunson:{pts:20,...},...')
    print('\nOutput: all_true_probs_dict = {player: {stat: {val: {conditions: {prob, ... = {\'nikola jokic\': {\'pts\': {0: {\'all 2024 regular prob\': 0.0, ..., \'A Gordon PF, J Murray PG,... starters 2024 regular prob\': 0.0, ...\n')

    # before we get true prob we must know per unit probs

    # gen true probs for all stat probs dict
    # we get true prob for combos of conditions by weighting avg prob
    # start with overall true prob combining 2 seasons weighted by recency and sample size
    # relevance for a time period is shown in recency factor
    # need to know current conditions to get true prob
    # see how current conds were used for streak tables

    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    #cur_yr = str(season_years[0])

    # need stats of interest to get prev vals
    stats_of_interest = ['pts','ast','reb']

    all_true_probs_dict = all_stat_probs_dict # deepcopy?
    
    for player, player_probs_dict in all_true_probs_dict.items():
        #print('\nplayer: ' + player.title())
        player_stat_dict = all_player_stat_dicts[player]
        #print('player_stat_dict: ' + str(player_stat_dict))
        # p1:{loc:l1, city:c1, dow:d1, tod:t1,...}
        # we need player conditions to show abbrevs to match with conds in stat dict
        # BUT if we separate out players then we would have multiple cond keys=out
        # so can we wait to change format until we need to use each title separately?
        # yes although less efficient bc has to convert twice
        player_current_conditions = all_cur_conds_dicts[player]
        game_player_cur_conds = all_game_player_cur_conds[player]
        player_prev_vals = all_prev_vals[player]
        # need cur team to match abbrevs to get game player conds bc players on same lineup as cur player
        player_teams = all_players_teams[player]
        player_cur_team = determiner.determine_player_current_team(player, player_teams, cur_yr, rosters)
        #print('init_player_current_conditions: ' + str(player_current_conditions))
        # for cond_key, cond_val in init_player_current_conditions.items():
        #     print('\ncond_key: ' + str(cond_key))
        #     print('cond_val: ' + str(cond_val))
            
        #     if cond_key == 'out':
        #         out_players = cond_val
        #         player_current_conditions[cond_key] = 
        
        # first get overall probs for all reg seasons
        #condition = 'all' # all conds match all
        part = 'regular' # get current part from time of year mth
        # get conditions of game such as location
        # see gen player outcomes fcn for example
        # used to get from player lines so try that
        # could also get from espn schedule bc i think the url is unchanging?
        # include 'all' condition
        # conditions = ['all', 'home']
        #conditions = [condition] + list(player_current_conditions.values())
        #print('conditions: ' + str(conditions))

        all_gp_conds = {} #generate_all_gp_conds()
        for team_condition, lineup in game_player_cur_conds.items():
            # print('team_condition: ' + team_condition)
            # print('lineup: ' + str(lineup))
            # need lineup team to match player abbrev key
            # to find multiple abbrevs
            # we are looking at the current player and lineup so get player current team
            if len(lineup.keys()) > 0:
                lineup_team = player_cur_team
                opp_key = 'opp'
                opp_team_key = opp_key + ' team'
                if team_condition == opp_key:
                    lineup_team = player_current_conditions[opp_team_key]
                #print('lineup_team: ' + str(lineup_team))
                
                conditions = generate_game_players_conditions(lineup, lineup_team, all_players_abbrevs, player, team_condition)
                all_gp_conds[team_condition] = conditions
            else:
                print('Warning: No lineup for ' + team_condition + ', ' + player_cur_team)

        # combine cond weights and sample size to get normalized cond weights
        # or can we ignore sample size bc the cond weights reflect sample size? no we must say a cond with less samples has less weight
        # we can pass all conditions weights to gen true probs bc same for all stats bc condition and sample size same for all stats
        all_conditions_weights_data = generate_all_conditions_weights(player_current_conditions, all_gp_conds, player_prev_vals, player_stat_dict, all_players_abbrevs, part, player, player_cur_team)
        all_conditions_weights = all_conditions_weights_data[0]
        all_gp_conds_weights = all_conditions_weights_data[1]

        for stat, stat_probs_dict in player_probs_dict.items():
            #print('\nstat: ' + str(stat))

            # prev val condition depends on stat
            if stat in stats_of_interest:
                prev_val = player_prev_vals[stat]
                prev_val_weight = generate_prev_val_weight(prev_val, player_stat_dict, part, player)
                
                # player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
                #prev_val = player_stat_dict[cur_yr][part][stat][condition]['0']
                #print('prev_val: ' + str(prev_val))
                # is it useful to get prev val under current conditions? possibly but could be misleading unless looking at larger sample
                # moved prev val to gen all stat prob dicts fcn bc that is last step before display and val probs dict is strictly for probs

                for val, val_probs_dict in stat_probs_dict.items():
                    #print('\nval: ' + str(val))
                    #print('val_probs_dict: ' + str(val_probs_dict))

                    # get prev game stat vals from most recent game log in stat dict
                    # and add keys to all_stat_prob_dicts
                    # technically prev game stat vals affects stat prob so include in all stat probs dict
                    #all_stat_prob_dicts = generate_all_prev_game_stat_vals
                    
                    val_probs_dict['true prob'] = generate_true_prob(val_probs_dict, player_current_conditions, all_conditions_weights, all_gp_conds, all_gp_conds_weights, prev_val, prev_val_weight, player_stat_dict, all_players_abbrevs, all_players_teams, all_box_scores, season_years, part, player, stat, val)

                    # # add keys to dict not used for ref but not yet to gen true prob
                    # # otherwise it will use string value to compute prob
                    # # all vals in val probs dict must be probs
                    # # so we should make a separate dict and combine them before display

                    # # we actually want to show the player current conds so we can see which probs are being used and adjust for errors
                    # for cond_key, cond_val in player_current_conditions.items():
                    #     val_probs_dict[cond_key] = cond_val


    #print('all_true_probs_dict: ' + str(all_true_probs_dict))
    return all_true_probs_dict

# player_current_conditions = {out:[p1,...], starters:[p1,...], loc:l1, city:c1, dow:d1, tod:t1,...}
# all lineups has random combo of full names and abbrevs so check both
# all_lineups = {team:{starters:[Klay Thompson, D. Green,...],out:[],bench:[],unknown:[]},...}
# player_teams = {year:team:gp}
def generate_player_current_conditions(player, game_teams, player_teams, all_lineups={}, player_abbrev='', cur_yr='', rosters={}, cur_date=''):
    #print('\n===Generate Player Current Conditions: ' + player.title() + '===\n')

    player_current_conditions = {}

    # if player traded but not played this yr then need to get team from rosters
    # why not get team from rosters bc that always has current teams?
    player_team = determiner.determine_player_current_team(player, player_teams, cur_yr, rosters) #list(player_teams[player][cur_yr].keys())[-1] # current team
    #print('player_team: ' + str(player_team))

    # condition: location
    cur_loc = determiner.determine_player_game_location(player, game_teams, player_team)
    if cur_loc != '':
        player_current_conditions['loc'] = cur_loc
    else:
        print('Warning: cur_loc blank! ' + player.title())

    # condition: prev stat val
    # get from game log
    # diff for each stat
    # prev_val = 0
    #player_prev_vals = reader.read_player_prev_stat_vals(player_game_log)
    
    # need opp team for game key for game info, and for opp lineup
    opp_team_idx = 0
    if cur_loc == 'away':
        opp_team_idx = 1
    player_game = determiner.determine_player_game(game_teams, player_team)
    opp_team = player_game[opp_team_idx]
    
    # game info conditions
    # cur_tod
    # cur_coverage
    # cur_city
    # cur_audience
    # read game info from espn
    away_team = player_team
    home_team = opp_team
    if cur_loc == 'home':
        away_team = opp_team
        home_team = player_team

    # for now assuming today but accept any date of interest
    cur_date = datetime.today().strftime('%m/%d/%Y')
    game_key = away_team + ' ' + home_team + ' ' + cur_date
    cur_game_info = reader.read_game_info(game_key, player=player)
    cur_tod = cur_game_info['tod']
    if cur_tod != '':
        player_current_conditions['tod'] = cur_tod
    cur_coverage = cur_game_info['coverage']
    if cur_coverage != '':
        player_current_conditions['coverage'] = cur_coverage
    cur_city = cur_game_info['city']
    if cur_city != '':
        player_current_conditions['city'] = cur_city
    cur_audience = cur_game_info['audience']
    if cur_audience != '':
        player_current_conditions['audience'] = cur_audience
    
    # timing conditions
    # condition: dow, from cur date
    # condition: time before, from team schedule
    # condition: time after, from season log
        
    # former team boost condition
    former_teams = reader.read_player_former_teams(player, player_teams)
    if opp_team in former_teams:
        cur_former_team_cond = 'former'
        player_current_conditions['former'] = cur_former_team_cond

    # condition: teammates and opps lineups
    # https://www.rotowire.com/basketball/nba-lineups.php
    # get teammates and opps conds
    #player_team = player_teams[player]
    # player team should be in all lineups if playing today
    if player_team in all_lineups.keys():
        # {starters:[],out:[],bench:[],unknown:[]}
        player_team_lineup = all_lineups[player_team]
        opp_team_lineup = {}
        
        if opp_team in all_lineups.keys():
            opp_team_lineup = all_lineups[opp_team]
        else:
            print('Warning: Opp team not in lineups! ' + opp_team)
        # determine opp team from game teams
        # opp_team = determiner.determine_opponent_team(player, game_teams, player_teams) #game_teams[opp_idx]
        # opponent_lineup = all_lineups[opp_team]
        # dealing with the ppl we know are out is first and then figure out how to deal with uncertain players
        out_key = 'out'
        starters_key = 'starters'
        start_key = 'start' # could call it bench key to avoid confusion? not really bc variable is player start? could change that to player bench but not important and will cause same confusion
        bench_key = 'bench'
        opp_key = 'opp'
        opp_team_key = opp_key + ' team' # opp used for group total
        opp_out_key = opp_key + ' ' + out_key
        opp_starters_key = opp_key + ' ' + starters_key
        opp_bench_key = opp_key + ' ' + bench_key 

        player_current_conditions[out_key] = player_team_lineup[out_key]
        player_current_conditions[starters_key] = player_team_lineup[starters_key]
        player_current_conditions[bench_key] = player_team_lineup[bench_key]
        # no need to display in key bc covered by start and bench but still assign val to in separate bc it smooths the overall value of player independent of start condition
        #player_current_conditions[in_key] = player_team_lineup[in_key]
        # use team as reference and sub prob in opp group
        player_current_conditions[opp_team_key] = opp_team
        player_current_conditions[opp_out_key] = opp_team_lineup[out_key]
        player_current_conditions[opp_starters_key] = opp_team_lineup[starters_key]
        player_current_conditions[opp_bench_key] = opp_team_lineup[bench_key]
        # player_current_conditions['unknown'] = all_lineups
        # player_current_conditions['opp players'] = all_lineups # different from 'opp' which is team
        # player_current_conditions['num teammates out'] = all_lineups
        # player_current_conditions['minutes to fill'] = all_lineups

        # we know if player is starting bc lineup online shows starters
        # player_start = 'start' or 'bench'
        player_current_conditions[start_key] = determiner.determine_player_start(player, player_abbrev, player_team_lineup, starters_key)
    else:
        print('Warning: Player team not in all lineups! ' + player_team.upper() + ', ' + player.title())

    # player_current_conditions = {out:[p1,...], starters:[p1,...], loc:l1, city:c1, dow:d1, tod:t1,...}
    #print('player_current_conditions: ' + str(player_current_conditions))
    return player_current_conditions#, player_prev_vals

# make dict of all current conditions for each player so we can use to compute true prob
# all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
# if player on new team but has not yet played (eg injury) then only consider current conditions if they are specifically noted as playing? 
# cant bc only lists starters and out
def generate_all_current_conditions(players, game_teams, all_players_teams, rosters, find_players, cur_yr, all_teams_players):
    print('\n===Generate All Current Conditions===\n')
    print('Settings: Find Players')
    print('\nInput: Players of Interest')
    print('Input: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\'), ...]')
    print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('Input: teams_current_rosters = {team:[players],..., {\'nyk\': [jalen brunson, ...], ...}')
    print('Input: Current Year to get current team if not in rosters')
    print('Input: all_teams_players = {year:{team:[players], ... = {\'2024\': {\'wsh\': [\'kyle kuzma\', ...')
    print('\nOutput: all_current_conditions = {p1:{starters:[s1,...], loc:l1, city:c1, dow:d1, tod:t1,...}, ... = {\'nikola jokic\': {\'loc\': \'away\', \'out\': [\'vlatko cancar\',...], ...\n')

    all_current_conditions = {}

    # read all teammates out from internet
    # starters affect both other starters and benchers
    # benchers mostly affect other benchers
    # but if a bench player with mucho minutes is out then starters may play a few more minutes too. 
    # so use mean minutes from stat dict to see how much playing time needs to be distributed to teammates
    # if player listed as out how do we know if they would have been a starter?
    # could get mean minutes played to see play time which might be better than knowing if starter
    # also see which position is out and needs to be filled
    # all_teammates_out = {game:{team:{out:[],gtd:[]}
    all_teammates_out = {}
    all_starters = {}
    all_benches = {}
    # if expected lineup, show both with and without questionable teammates
    # so when lineup confirmed, can go with correct option but really if lineup not yet confirmed then odds will not be set
    # but sometimes odds set only for expected lineups so better to avoid if unsure
    # if confirmed lineup, only need to show 1 lineup
    # 'out' will never include gtd bc we must classify gtd as 'starter', 'bench' or 'unknown' based on injury report certainty
    # if there are unknowns then starters and bench are also unknown so should we classify by mean minutes?
    #all_lineups = {confirmed:{team:{starters:[],out:[],bench:[],unknown:[]},...}, expected:{team:{starters:[],bench:[],out:[]},...}}
    all_lineups = {}
    if find_players:
        all_lineups = reader.read_all_lineups(players, all_players_teams, rosters, all_teams_players, cur_yr)
    # if questionable then it is very hard to say how teammates will perform so can only go with safest options
    # we could figure out how likely it is for player to play based on injury reports
    # and adjust teammates true probs accordingly
    questionable_players = [] 
    # can we actually measure probability of player being out?
    # if we had access to all past injury reports but i dont think we do easily although it might be worth looking up
    # first try to use rotowire uncertainty rating on lineups page if available
    # basically, if gtd then uncertain unless injury report says they are likely to play bc they have been playing well and usually have gtd tag just in case
    # so once we know uncertain players, we will have to see which teammates they affect to know which players to avoid



    for player in players:
        # skip practice players
        if player in all_players_teams.keys():
            player_teams = all_players_teams[player]
            # need to pass all lineups bc opponent lineups matter too
            player_curr_conds = generate_player_current_conditions(player, game_teams, player_teams, all_lineups, cur_yr=cur_yr, rosters=rosters)

            all_current_conditions[player] = player_curr_conds

    #print('all_current_conditions: ' + str(all_current_conditions))
    return all_current_conditions

# all_stat_probs_dict = {player:stat:val:conditions:prob}
# like gen stat probs by stat used in writer
# need player_stat_dict to get sample size
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
def generate_all_stat_probs_dict(all_player_stat_probs, all_player_stat_dicts={}, all_unit_stat_probs={}, season_years=[], irreg_play_time={}):
    print('\n===Generate All Stat Probs Dict===\n')
    print('Input: all_player_stat_probs = {player: {condition: {year: {season part: {stat name: {stat val: prob over, ... = {\'kyle kuzma\': {\'all\': {\'2024\': {\'regular\': {\'pts\': {0: 0.0, ...}, ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': {0: 0.0, ...')
    print('Input: all_player_stat_dicts = {player: {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'kyle kuzma\': {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('Input: all_unit_stat_probs = {player: {condition: {year: {season part: {stat name: {stat val: prob over, ... = {\'kyle kuzma\': {\'all\': {\'2024\': {\'regular\': {\'pts\': {0: 0.0, ...}, ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': {0: 0.0, ...')
    print('Input: Season Years of interest')
    print('Input: Irregular Playing Time expected to tell unit time period')
    print('\nOutput: all_stat_probs_dict = {player: {stat name: {stat val: {\'condition year part\': prob, ... = {\'kyle kuzma\': {\'pts\': {0: {\'all 2024 regular prob\': 0.0, ..., \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters 2023 regular prob\': 0.0, ...\n')

    all_stat_probs_dict = {}

    # determine unit time period by observing if drastic change indicates change in team or role
    # default to avg current season but enable manual entry of minutes if irregular such as for teammate injured
    #irreg_play_time = {'craig porter': 25}
    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    unit_time_period = determiner.determine_unit_time_period(all_player_stat_probs, all_player_stat_dicts, season_years, irreg_play_time)

    # rearrange all_player_stat_probs into all_stat_probs_dict
    for player, player_stat_probs in all_player_stat_probs.items():
        stat_probs_by_stat = {} # this must be in player loop or it will show max val for all players when we only need max for current players here bc separate sheets. this would be outside loop for all players when we want all players in same sheet
        #print('player: ' + str(player))
        player_unit_stat_probs = {}
        if len(all_unit_stat_probs.keys()) > 0:
            player_unit_stat_probs = all_unit_stat_probs[player]

        all_conditions = []
        for condition, condition_stat_probs in player_stat_probs.items():
            #print('condition: ' + str(condition))
            for year, year_stat_probs in condition_stat_probs.items():
                #print('year: ' + str(year))
                for part, part_stat_probs in year_stat_probs.items():
                    #print('part: ' + str(part))
                    
                    conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
                    all_conditions.append(conditions)
                    
                    for stat, stat_probs in part_stat_probs.items():
                        
                        for val, prob in stat_probs.items():
                            
                            if stat not in stat_probs_by_stat.keys():
                                stat_probs_by_stat[stat] = {}
                                stat_probs_by_stat[stat][val] = {}
                            elif val not in stat_probs_by_stat[stat].keys():
                                stat_probs_by_stat[stat][val] = {}

                            stat_probs_by_stat[stat][val][conditions] = prob # {'prob':prob}

                            # dont add per unit stats for time period used as unit
                            # eg avg current season minutes to get unit
                            # determine unit time period by observing if drastic change indicates change in team or role
                            # default to avg current season but enable manual entry of minutes if irregular such as for teammate injured
                            if len(player_unit_stat_probs.keys()) > 0:
                                if year != unit_time_period:
                                    prob_per_unit = player_unit_stat_probs[condition][year][part][stat][val]
                                    conditions_per_unit = conditions + ' per unit'
                                    stat_probs_by_stat[stat][val][conditions_per_unit] = prob_per_unit
                            
                            # add true prob for each val based on conditional probs
                            # need to know all players conditions first
                            # and could even include all players and similar players especially in consideration of projection
        
        all_stat_probs_dict[player] = stat_probs_by_stat
    
    # all_stat_probs_dict = {player:stat:val:conditions:prob}
    #print('all_stat_probs_dict: ' + str(all_stat_probs_dict))
    return all_stat_probs_dict

# need season logs for minutes played to scale stat vals
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
#player_unit_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_player_unit_stat_records(player_name, player_stat_dict, player_season_logs):
    #print('\n===Generate Player Unit Stat Records: ' + player_name.title() + '===\n')
    player_unit_stat_records = {}

    #print('player_season_logs: ' + str(player_season_logs))

    if len(player_season_logs.keys()) > 0:
    # gen list of reg season logs from full season logs
    # similar to iso fcn
        reg_season_logs = generate_reg_season_logs(player_season_logs)

        
        cur_yr = list(player_season_logs.keys())[0]
        #print('cur_yr: ' + cur_yr)
        cur_season_log = reg_season_logs[cur_yr]#list(player_season_logs.values())[0]
        #print('cur_season_log: ' + str(cur_season_log))
        cur_mean_minutes = 0
        if 'MIN' in cur_season_log.keys():
            cur_minutes_log = list(cur_season_log['MIN'].values())
            #print('cur_minutes_log: ' + str(cur_minutes_log))
            cur_mean_minutes = round(np.mean(np.array(cur_minutes_log)))
            #print('cur_mean_minutes: ' + str(cur_mean_minutes))

        stats_of_interest = ['pts','reb','ast','3pm']

        # year is a string bc it can be read from json which forces string
        for year, year_stat_dict in player_stat_dict.items():
            year = str(year) # to compare to json
            #print("\n===Year " + year + "===\n")
            for part, part_stat_dict in year_stat_dict.items():
                #print("\n===Season Part " + str(part) + "===\n")
                # need to isolate season part df to align with nested dict
                part_season_logs = generate_part_season_logs(player_season_logs, part)
                for stat, stat_dict in part_stat_dict.items():
                    
                    if stat in stats_of_interest:
                        #print("\n===Stat Name " + str(stat) + "===\n")
                        for condition, condition_stat_dict in stat_dict.items():
                            #print("\n===Condition " + str(condition) + "===\n")
                            all_probs_stat_reached = []

                            #print('condition_stat_dict: ' + str(condition_stat_dict))
                            stat_vals = list(condition_stat_dict.values())
                            #print('stat_vals: ' + str(stat_vals))
                            num_games_played = len(stat_vals)
                            #print('num games played ' + condition + ': ' + str(num_games_played))
                            if num_games_played > 0:
                                # adjust stat vals to current minutes
                                # max(stat_vals)+1 bc we want to include 0 and max stat val
                                # if left blank should default from 0 to n full length of range
                                # for 0 we need to compute prob of exactly 0 not over under
                                for stat_val in range(max(stat_vals)+1):
                                    #print('stat_val: ' + str(stat_val))
                                    num_games_reached = 0 # num games >= stat val, stat count, reset for each check stat val bc new count
                                    # loop through games to get count stat val >= game stat val
                                    for game_idx in range(num_games_played):
                                        #print('\ngame_idx: ' + str(game_idx))
                                        # if 0 consider adding x instead of multiplying 0

                                        # prev stat val meaning from a prev game so will be adjusted to current minutes
                                        prev_stat_val = stat_vals[game_idx]
                                        #print('prev_stat_val: ' + str(prev_stat_val))
                                        game_stat_val = prev_stat_val
                                        if year != cur_yr:
                                            #relative_game_idx = game_idx + int(list(list(season_log.values()[0].keys())[0]))
                                            season_log = part_season_logs[year]
                                            #print('season_log: ' + str(season_log))
                                            prev_minutes = list(season_log['MIN'].values())[game_idx]#[str(relative_game_idx)]
                                            #print('prev_minutes: ' + str(prev_minutes))
                                            #print('prev_stat_val * cur_mean_minutes / prev_minutes')
                                            #print(str(prev_stat_val) + ' * ' + str(cur_mean_minutes) + ' / ' + str(prev_minutes))
                                            # game stat val is what the stat val would be if playing current minutes
                                            if prev_minutes != 0.0:
                                                game_stat_val = round(float(prev_stat_val) * float(cur_mean_minutes) / float(prev_minutes))
                                        #print('game_stat_val: ' + str(game_stat_val))

                                        if int(stat_val) == 0:
                                            if game_stat_val == int(stat_val):
                                                num_games_reached += 1
                                        else:
                                            if game_stat_val >= int(stat_val):
                                                num_games_reached += 1

                                    prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                                    #print('prob_stat_reached: ' + str(prob_stat_reached))
                                    all_probs_stat_reached.append(prob_stat_reached)

                                # make parallel with player stat records
                                if condition not in player_unit_stat_records.keys():
                                    player_unit_stat_records[condition] = {}
                                if year not in player_unit_stat_records[condition].keys():
                                    player_unit_stat_records[condition][year] = {}
                                if part not in player_unit_stat_records[condition][year].keys():
                                    player_unit_stat_records[condition][year][part] = {}
                                
                                player_unit_stat_records[condition][year][part][stat] = all_probs_stat_reached



    #print('player_unit_stat_records: ' + str(player_unit_stat_records))
    return player_unit_stat_records

# parallel to stat probs but scaled to per minute basis
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
# player_unit_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
def generate_player_unit_stat_probs(player_stat_dict, player_name, player_season_logs):
    print('\n===Generate Player Unit Stat Probs: ' + player_name.title() + '===\n')
    print('Input: player_stat_probs = {condition: {year: {season part: {stat name: {stat val: prob over, ... = {\'all\': {\'2024\': {\'regular\': {\'pts\': {0: 0.0, ...}, ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': {0: 0.0, ...')
    print('\nOutput: player_unit_stat_probs = {condition: {year: {season part: {stat name: {stat val: prob over, ... = {\'all\': {\'2024\': {\'regular\': {\'pts\': {0: 0.0, ...}, ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': {0: 0.0, ...\n')

    player_unit_stat_probs = {}

    player_unit_stat_records = generate_player_unit_stat_records(player_name, player_stat_dict, player_season_logs)

    # here we gen stat probs again, but this time for unit stat records
    # player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': num reached / num played,...
    player_unit_stat_probs = generate_player_stat_probs(player_unit_stat_records, player_name)

    # get prev minutes played
    # and prev stat val
    # skip cur season and start at prev season
    # adjust stat vals to scale to current minutes played
    # then see prob of going over line

    #print('player_unit_stat_probs: ' + str(player_unit_stat_probs))
    return player_unit_stat_probs

# record input is prob stat reached as fraction
# output is prob 0-1
# record = x/y = num_games_reached / num_games_played
def generate_prob_stat_reached(record):

    #print('\n===Generate Prob Stat Reached===\n')

    #print('record: ' + str(record))

    # if we have no record for a given stat val we will pass record=''
    # bc prob=0
    prob_stat_reached = 0

    if record != '':

        # record = x/y = num_games_reached / num_games_played
        record_data = record.split('/')
        num_games_reached = record_data[0]
        num_games_played = record_data[1]
        #prob_stat_reached = round((float(num_games_reached) / float(num_games_played)) * 100)
        prob_stat_reached = round(float(num_games_reached) / float(num_games_played), 2)
        
    #print('prob_stat_reached: ' + str(prob_stat_reached))
    return prob_stat_reached

# from 0 to n gen prob over and under stat val
# first overall and then for conditions
# stat_val_probs = {}
#player_stat_records: {'all': {2023: {'regular': {'pts': 
# generate_stat_val_probs
# old: player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
def generate_player_stat_probs(player_stat_records, player_name=''):
    print('\n===Generate Player Stat Probs: ' + player_name.title() + '===\n')
    print('Input: player_stat_records = {condition: {year: {season part: {stat name: [stat val record (num reached/num played),...], ... = {\'all\': {\'2024\': {\'regular\': {\'pts\': [\'0/28\', ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': [\'0/12\', ...')
    print('\nOutput: player_stat_probs = {condition: {year: {season part: {stat name: {stat val: prob over, ... = {\'all\': {\'2024\': {\'regular\': {\'pts\': {0: 0.0, ...}, ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': {0: 0.0, ...\n')

    player_stat_probs = {}

    for condition, condition_stat_records in player_stat_records.items():
        #print("\n===Condition " + str(condition) + "===\n")

        player_stat_probs[condition] = {}

        for season_year, full_season_stat_dicts in condition_stat_records.items():
            #print("\n===Year " + str(season_year) + "===\n")

            player_stat_probs[condition][season_year] = {}

            for season_part, season_stat_dicts in full_season_stat_dicts.items():
                #print("\n===Season Part " + str(season_part) + "===\n")

                player_stat_probs[condition][season_year][season_part] = {}

                for stat_name, stat_records in season_stat_dicts.items():
                   # print("\n===Stat Name " + str(stat_name) + "===\n")
                    #print('stat_records: ' + str(stat_records))

                    #player_stat_probs[condition][season_year][season_part][stat_name] = {}
                    #stat_probs = player_stat_probs[condition][season_year][season_part][stat_name]
                    stat_probs = {}

                    # get prob from 0 to 1 to compare to desired consistency
                    #stat_val = 0
                    prob_over = 1.0
                    prob_under = 1.0
                    
                    for stat_val in range(len(stat_records)):
                        #print("\n===Stat Val " + str(stat_val) + "===")
                        # gen prob reached from string record
                        record = stat_records[stat_val] # eg x/y=1/1
                        #print('record: ' + str(record))

                        # adjust stat val proprtional to minutes currently playing
                        # but we want both orig and adjusted to compare
                        # so need parallel dict adjusted stat probs
                        # it could have current yr but it would be the same as orig 
                        #per_min_prob = generate_per_min_prob(stat_val, stat_dict)

                        # call prob over keys 
                        # 'raw prob' and 'per min prob'
                        prob_over = generate_prob_stat_reached(record)

                        #prob_under = round(1 - prob_over,2)

                        # prob under for a stat val is over 1-prob ober so only need to save prob over
                        stat_probs[stat_val] = prob_over #{ 'prob over': prob_over, 'prob under': prob_under }
                        #print('stat_probs: ' + str(stat_probs))

                    # when we want to see all stats on same page aligned by value we will have to add 0s and 100s to blank cells
                    # but that would require knowing the stat keys which you can get from the first val bc everyone has at least 0

                    player_stat_probs[condition][season_year][season_part][stat_name] = stat_probs

    # player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
    #print('player_stat_probs: ' + str(player_stat_probs))
    return player_stat_probs

# we are looking for the stat val reached at least 90% of games
# so from 0 to max stat val, get record reached games over total games
# player_stat_records = []
# no need to make dict because stat val = idx bc going from 0 to N
#player_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_player_stat_records(player_name, player_stat_dict):
    print('\n===Generate Player Stat Record: ' + player_name.title() + '===\n')
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: player_stat_records = {condition: {year: {season part: {stat name: [stat val record (num reached/num played),...], ... = {\'all\': {\'2024\': {\'regular\': {\'pts\': [\'0/28\', ... \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'2023\': {\'regular\': {\'pts\': [\'0/12\', ...\n')

    player_stat_records = {}

    # first show reg season, then post, then combined

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():
        #print("\n===Year " + str(season_year) + "===\n")

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            #print("\n===Season Part " + str(season_part) + "===\n")

            # all_pts_dicts = {'all':{idx:val,..},..}
            # all_pts_dicts = {'all':{1:20}}
            # key=condition, val={idx:stat}
            all_pts_dicts = player_season_stat_dict['pts']
            # all_rebs_dicts = player_season_stat_dict['reb']
            # all_asts_dicts = player_season_stat_dict['ast']
            # all_threes_made_dicts = player_season_stat_dict['3pm']
            # all_bs_dicts = player_season_stat_dict['blk']
            # all_ss_dicts = player_season_stat_dict['stl']
            # all_tos_dicts = player_season_stat_dict['to']
            if len(all_pts_dicts['all'].keys()) > 0:

                #all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

                # key represents set of conditions of interest eg home/away
                for condition in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    #print("\n===Condition " + str(condition) + "===\n")

                    # reset for each condition
                    stat_names = ['pts','reb','ast','3pm']

                    # for each stat type/name (eg pts, reb, etc)
                    # loop from 0 to max stat val to get record over stat val for period of all games
                    for stat_name in stat_names:

                        #print("\n===Stat name " + str(stat_name) + "===\n")

                        # reset for each stat name/type
                        all_games_reached = [] # all_stat_counts = []
                        all_probs_stat_reached = []

                        # for prev stat vals, diff stats have different ranges so not all stat names have all conds
                        if condition in player_season_stat_dict[stat_name].keys():
                            stat_vals = list(player_season_stat_dict[stat_name][condition].values())
                            #print('stat_vals: ' + str(stat_vals))
                            num_games_played = len(stat_vals)
                            #print('num games played ' + condition + ': ' + str(num_games_played))
                            if num_games_played > 0:
                                # max(stat_vals)+1 bc we want to include 0 and max stat val
                                # for 0 we need to compute prob of exactly 0 not over under
                                for stat_val in range(0,max(stat_vals)+1):
                                    # if stat_val == 0:
                                    #     num_games_hit
                                    num_games_reached = 0 # num games >= stat val, stat count, reset for each check stat val bc new count
                                    # loop through games to get count stat val >= game stat val
                                    for game_idx in range(num_games_played):
                                        game_stat_val = stat_vals[game_idx]
                                        if int(stat_val) == 0:
                                            if game_stat_val == int(stat_val):
                                                num_games_reached += 1
                                        else:
                                            if game_stat_val >= int(stat_val):
                                                num_games_reached += 1

                                        all_games_reached.append(num_games_reached) # one count for each game

                                    #print('num_games_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(num_games_reached)) 
                                    

                                    prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                                    #print('prob_stat_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(prob_stat_reached)) 

                                    all_probs_stat_reached.append(prob_stat_reached)


                            if condition in player_stat_records.keys():
                                #print("conditions " + conditions + " in streak tables")
                                player_condition_records_dicts = player_stat_records[condition]
                                if season_year in player_condition_records_dicts.keys():
                                    #player_condition_records_dicts[season_year][stat_name] = all_probs_stat_reached

                                    player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                                    if season_part in player_season_condition_records_dicts.keys():
                                        player_season_condition_records_dicts[season_part][stat_name] = all_probs_stat_reached
                                    else:
                                        player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }
                                
                                else:
                                    #player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }

                                    player_condition_records_dicts[season_year] = {}
                                    player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                                    player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }

                                #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                            else:
                                #print("conditions " + conditions + " not in streak tables")
                                player_stat_records[condition] = {}
                                player_condition_records_dicts = player_stat_records[condition]

                                #player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }

                                player_condition_records_dicts[season_year] = {}
                                player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                                player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }
                        # else:
                        #     print('Caution: Condition not in stat dict! ' + stat_name + ', ' + condition)
    
    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    #print('player_stat_records: ' + str(player_stat_records))
    return player_stat_records

# sort alphabetical and lower for comparison to other games
# might as well compare strings bc need str as key
# players_list = [j. brown sg,...]
# p_string = j brown sg,...
# keep position in name bc more info and still sorts alphatebically?
# no bc we need it to exactly match other games where they played diff positions but same teammates, which is probably rare
# actually i think position stays same in box score no matter what position they are playing that game 
# so could include position but does it help or just get in the way?
# could eventually use combos of positions instead of specific players
# but then those positions would be a separate title not needed in teammates title
# players_list: ['J Green PF', 'Z Nnaji PF', 'P Watson F', 'B Brown SF', 'V Cancar SF', 'D Jordan C', 'I Smith PG', 'R Jackson PG', 'C Braun G']
def generate_players_string(players_list):
    print('\n===Generate Players String===\n')
    print('players_list: ' + str(players_list))

    # sort players alphabetically so we can compare to current conditions!
    players_list = sorted(players_list)

    p_string = ''

    for p_idx in range(len(players_list)):

        # keep position bc we only use first initial to save space
        # still shorter than full name bc positions only have 2 letters max
        # if we want to remove positions: [A-Z]+$
        p = re.sub('\.','',players_list[p_idx]).strip() # j. brown sg
        # last 2 letters are position which we want uppercase
        #n=2
        # pos = p[len(p) - n:]
        # p = p[:-n] + pos

        if p_idx == 0:
            p_string += p
        else:
            p_string += ', ' + p
            
    # if we input desired format then it will keep
    #p_string = p_string.title() # or lower? title makes it easier to read and compare. possibly remove period after first initial? yes to save space
    
    print('p_string: ' + p_string)
    return p_string

# jaylen brown -> j brown sg
# trey murphy iii -> t murphy iii sg
# Jayson Tatum -> J Tatum SF
# use to see if started or bench
# bc box score shows player abbrev
def generate_player_abbrev(player_name, player_position):
    #print('\n===Generate Player Abbrev===\n')
    #print('player_name: ' + str(player_name))
    #print('player_position: ' + str(player_position))
    #player_abbrev = ''

    #player_abbrev = player_initital + last_name
    player_names = player_name.split()
    player_abbrev = re.sub('\.','',player_names[0][0]).upper()
    #last_name = ''
    for name in player_names[1:]:
        player_abbrev += ' ' + name.title()
    player_abbrev += ' ' + player_position.upper()

    #print('player_abbrev: ' + player_abbrev)
    return player_abbrev

# each player has a stat dict for each stat so gen all of them for a given player
# run separately for each part of each season
# need cur_yr for teammates out only care about them if cur teammate
# but also need to look thru past seasons and not count cur teammates as out last season
def generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_teams, season_year, todays_games_date_obj, all_box_scores, year_games_info, player_teammates, all_seasons_stats_dicts, season_part, player_position, rosters={}, cur_team='', all_teams_players={}, stats_of_interest=[]):
    print('\n===Generate Player All Stats Dicts: ' + player_name.title() + ', ' + str(season_year) + ', ' + season_part + '===\n')
    # print('season_year: ' + str(season_year))
    # print('season_part: ' + str(season_part))
    #print('player_game_log:\n' + str(player_game_log))

    stats_of_interest = ['pts', 'ast', 'reb']

    # use to see if started or bench
    # bc box score shows player abbrev
    player_abbrev = ''
    if season_year in all_box_scores.keys() and len(all_box_scores[season_year].keys()) > 0:
        player_abbrev = generate_player_abbrev(player_name, player_position)
    #print('player_abbrev: ' + str(player_abbrev))

    # get no. games played this season
    # so we can compare game with the same idx bt seasons
    current_season_log = player_game_log
    current_reg_season_log = determiner.determine_season_part_games(current_season_log, 'regular')
    num_games_played = len(current_reg_season_log.index) # see performance at this point in previous seasons

    # all_pts_dicts = {'all':{idx:val,..},..}
    all_pts_dicts = { 'all':{}, 'home':{}, 'away':{} } # 'opp eg okc':{}, 'day of week eg tue':{}
    all_rebs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_asts_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_winning_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_losing_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_minutes_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fgms_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fgas_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fg_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_made_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_attempts_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ftms_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ftas_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ft_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_bs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ss_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_tos_dicts = { 'all':{}, 'home':{}, 'away':{} }

    all_stats_dicts = {'pts':all_pts_dicts, 'reb':all_rebs_dicts, 'ast':all_asts_dicts, 'w score':all_winning_scores_dicts, 'l score':all_losing_scores_dicts, 'min':all_minutes_dicts, 'fgm':all_fgms_dicts, 'fga':all_fgas_dicts, 'fg%':all_fg_rates_dicts, '3pm':all_threes_made_dicts, '3pa':all_threes_attempts_dicts, '3p%':all_threes_rates_dicts, 'ftm':all_ftms_dicts, 'fta':all_ftas_dicts, 'ft%':all_ft_rates_dicts, 'blk':all_bs_dicts, 'stl':all_ss_dicts, 'pf':all_fs_dicts, 'to':all_tos_dicts} # loop through to add all new stats with 1 fcn


    # if getting data from player game logs read from internet
    # for game log for particular given season/year
    # for season in all seasons
    if len(player_game_log) > 0:
        #season_year = '23'
        #print("player_game_log:\n" + str(player_game_log))
        # we pulled game log from internet
        
        
        # first loop thru all regular season games, then thru subset of games such as home/away
        # or just append to subset array predefined such as all_home_pts = []
        next_game_date_obj = todays_games_date_obj # need to see if back to back games 1 day apart

        # do 1 loop for reg season and 1 loop for post season
        # default full season
        season_part_game_log = determiner.determine_season_part_games(player_game_log, season_part)
        # if season_part == 'regular':
        #     season_part_game_log = determiner.determine_season_part_games(player_game_log, season_part)
        # elif season_part == 'full':
        #print("season_part_game_log:\n" + str(season_part_game_log) + '\n')

        num_season_part_games = len(season_part_game_log.index) # so we can get game num from game idx
        #print('num_season_part_games: ' + str(num_season_part_games))

        # if played postseason this yr, then need to rezero index of reg season df bc games played only counts reg seas
        # if 1st game idx != 0, then we know we played postseason
        
        # note play in tournament counts as postseason
        # but is listed before reg season unfortunately
        # so 
        #num_post_games = 0 # idx of 1st reg seas game
        num_playoff_games = 0 # reg season idx
        # num post games includes playin for postseason part
        # bc we know last team bc after trade deadline
        # if season_part == 'postseason':
        #     num_post_games = num_season_part_games # playoff + playin
        if season_part == 'regular':
            # easier to get num playoff games by type so change from postseason to playoff and playin
            if len(season_part_game_log.index) > 0:
                num_playoff_games = int(season_part_game_log.index[0]) # num playoff games not counting playin bc playn listed after 
            #num_post_games = num_playoff_games # + playin
        else: # full
            regseason_game_log = determiner.determine_season_part_games(player_game_log, 'regular')
            if len(regseason_game_log.index) > 0:
                num_playoff_games = int(regseason_game_log.index[0])
            #num_post_games = num_playoff_games # + playin
            #reg_season_idx = # num playoff games not counting playin bc playn listed after 

        # could we simply rezero df to have same affect?
        # no bc we use game idx as ref in stat dict
        # and full includes both parts so reset does nothing
        
        # determine player team for game at idx
        player_team_idx = 0
        # player_teams = {player:{year:{team:gp,...},...}}
        team_stats_dict = {}
        if season_year in player_teams.keys():
            team_stats_dict = player_teams[season_year]
        # team_date_dict = {}
        # if season_year in all_players_teams[player_name].keys():
        #     team_date_dict = all_players_teams[player_name][season_year]
        # reverse team gp dict so same order as game idx recent to distant
        teams = list(reversed(team_stats_dict.keys()))
        all_teams_stats = list(reversed(team_stats_dict.values()))
        games_played = []
        for team_stats in all_teams_stats:
            games_played.append(team_stats['GP'])

        # add postseason games to num games played so it lines up for full season
        # final games played not used if season part = post
        # bc we do not care games played to get team
        # so it does not need to include playin games
        num_recent_reg_games = 0
        if len(games_played) > 0:
            num_recent_reg_games = games_played[0] # num reg games with most recent team
        #print('num_recent_reg_games: ' + str(num_recent_reg_games))
        reg_and_playoff_games_played = [num_recent_reg_games + num_playoff_games] + games_played[1:]
        # use tourney game idx to approximate which team the player was on at the time
        # CHANGE to get date to be more accurate
        
        #print('reg_and_playoff_games_played: ' + str(reg_and_playoff_games_played))
        teams_reg_and_playoff_games_played = int(reg_and_playoff_games_played[player_team_idx])

        #prev_stat_vals = []
        for game_idx, row in season_part_game_log.iterrows():
            print('\ngame_idx: ' + game_idx)
            # print('\n===Game ' + str(int(game_idx)+1) + '===')
            # print('teams_reg_and_playoff_games_played: ' + str(teams_reg_and_playoff_games_played))
            # print('row:\n' + str(row))

            # player team used for conditions: location, city, game players
            # determine player team for game
            player_team_idx = determiner.determine_player_team_idx(player_name, player_team_idx, game_idx, row, games_played, teams_reg_and_playoff_games_played)
            player_team = ''
            if len(teams) > player_team_idx:
                player_team = teams[player_team_idx]
            #print('player_team: ' + player_team)

            away_abbrev = player_team

            game_opp_str = row['OPP'] #player_game_log.loc[game_idx, 'OPP']
            game_opp_abbrev = reader.read_team_abbrev(game_opp_str) # remove leading characters and change irregular abbrevs
            home_abbrev = game_opp_abbrev

            loc_key = 'away'
            if re.search('vs',game_opp_str):
                #stat_dict['home'][game_idx] = stat
                loc_key = 'home'
                away_abbrev = game_opp_abbrev
                home_abbrev = player_team

            # game date used to get game key
            # which is used to get game info and box score
            init_game_date_string = row['Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
            game_mth = init_game_date_string.split('/')[0]
            final_season_year = season_year
            if int(game_mth) > 9:
                final_season_year = str(int(season_year) - 1)
            game_date_string = init_game_date_string + "/" + final_season_year
            #print("game_date_string: " + str(game_date_string))

            # we need to get the game key so that we can determine the players in this game
            # we got away/home team from vs|@ in opp field in game log
            game_key = away_abbrev + ' ' + home_abbrev + ' ' + game_date_string
            #print('game_key: ' + str(game_key))
            
            game_info = year_games_info[game_key]
            city = game_info['city']
            tod = game_info['tod']
            audience = game_info['audience']
            coverage = game_info['coverage']

            # get week of season for weekly stat dict
            # get first game of season from nba schedule
            week_of_season = determiner.determine_week_of_season(game_date_string)
            # get first game for this player this season
            week_of_play = determiner.determine_week_of_play(game_date_string)

            #player_team = determiner.determine_player_team_by_date(player_name, team_date_dict, row)

            # # if postseason then after trade deadline so last team this yr
            # # postseason maybe playin listed after reg season
            
            # get game type so we can add stat to reg or post season game
            # instead loop thru each part separately
            
            # make list to loop through so we can add all stats to dicts with 1 fcn
            game_stats = determiner.determine_game_stats(player_game_log, game_idx) #[pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] 


            # === Add Stats to Dict ===

            # now that we have game stats add them to dict by condition

            # all conditions
            # values is list of dicts
            #prev_stat_val = 0 # if blank prev val then first game? we already have idx so not needed bc number int
            for stat_idx in range(len(all_stats_dicts.values())):
                stat_name = list(all_stats_dicts.keys())[stat_idx]
                stat_dict = list(all_stats_dicts.values())[stat_idx]
                stat = game_stats[stat_idx]


                # condition: all
                stat_dict['all'][game_idx] = stat

                # condition: week of season
                if not week_of_season in stat_dict.keys():
                    stat_dict[week_of_season] = {}
                stat_dict[week_of_season][game_idx] = stat
                # condition: week of play
                if not week_of_play in stat_dict.keys():
                    stat_dict[week_of_play] = {}
                stat_dict[week_of_play][game_idx] = stat


                

                # condition: location
                stat_dict[loc_key][game_idx] = stat

                # conditions from game info
                # condition: city
                # if away, get city from game info page 
                # bc not always at teams city, eg neutral games
                # even home games are diff than home city bc team changes
                if not city in stat_dict.keys():
                    stat_dict[city] = {}
                stat_dict[city][game_idx] = stat
                # condition: time of day, tod
                if not tod in stat_dict.keys():
                    stat_dict[tod] = {}
                stat_dict[tod][game_idx] = stat
                # condition: audience/stadium size
                if not audience in stat_dict.keys():
                    stat_dict[audience] = {}
                stat_dict[audience][game_idx] = stat
                # condition: tv coverage
                # todo: condition: tv coverage
                # bc some players play better or worse with more ppl watching more attention
                if not coverage in stat_dict.keys():
                    stat_dict[coverage] = {}
                stat_dict[coverage][game_idx] = stat
                
                # define away/home team so we can determine teammates/opponents in players in game
                # player team for this game
                #player_team = list(player_teams[player_name][season_year].keys())[-1]# current team
                # away_abbrev = player_team

                # game_opp_str = row['OPP'] #player_game_log.loc[game_idx, 'OPP']
                # game_opp_abbrev = reader.read_team_abbrev(game_opp_str) # remove leading characters and change irregular abbrevs
                # home_abbrev = game_opp_abbrev

                # if re.search('vs',game_opp_str):

                #     stat_dict['home'][game_idx] = stat
                    
                #     away_abbrev = game_opp_abbrev
                #     home_abbrev = player_team
                    
                # else: # if not home then away
                #     stat_dict['away'][game_idx] = stat

                #     # if away, get city from game info page 
                #     # bc not always at teams city, eg neutral games
                #     city = game_info['city']
                #     stat_dict[city][game_idx] = stat

                #print('away_abbrev: ' + away_abbrev)
                #print('home_abbrev: ' + home_abbrev)

                # todo: condition: city. use 'team abbrev city'? some games are not in either city like international games
                # default can use 'team abbrev city' and then neutral games will have specific '<city>' and 'neutral' tags
                # classify all neutral games as well as international. some neutral tournament games but are there any neutral season games that are domestic? no it seems all neutral would be international except for in season tournament
                # could also avoid this extra condition unless neutral specific city
                # instead if default away/home game, combine opponent and loc conditions to get city so we only need extra condition if neutral
                # city = opp away game




                # condition: matchup against opponent
                # only add key for current opp bc we dont need to see all opps here
                # look for irregular abbrevs like NO and NY
                # opponent in form 'gsw' but game log in form 'gs'
                # if we do not know the current opponent then show all opps
                #game_log_team_abbrev = re.sub('vs|@','',player_game_log.loc[game_idx, 'OPP'].lower()) # eg 'gs'
                #game_log_team_abbrev = reader.read_team_abbrev(row['OPP'])#(player_game_log.loc[game_idx, 'OPP'])
                #print('game_log_team_abbrev: ' + game_log_team_abbrev)
                #opp_abbrev = opponent # default if regular
                #print('opp_abbrev: ' + opp_abbrev)

                # if we do not know the current opponent 
                # or if we are not given a specific opponent (bc we may want to compare opps)
                # then show all opps
                # actually save all opps once
                # opponent = cur opp of interest, not game opp in loop
                #if opponent == game_opp_abbrev or opponent == '':
                    #print('opp_abbrev == game_log_team_abbrev')

                if not game_opp_abbrev in stat_dict.keys():
                    stat_dict[game_opp_abbrev] = {}
                stat_dict[game_opp_abbrev][game_idx] = stat

                # condition: against former team (bc more motivation to show what they gave up/rejected)
                former_teams = reader.read_player_former_teams(player_name, player_teams)
                former_team_key = 'former'
                if game_opp_abbrev in former_teams:
                    if not former_team_key in stat_dict.keys():
                        stat_dict[former_team_key] = {}
                    stat_dict[former_team_key][game_idx] = stat


                # condition: day of week
                # add keys for each day of the week so we can see performance by day of week
                # only add key for current dow bc we dont need to see all dows here
                
                game_dow = row['Date'].lower().split()[0].lower() # 'wed 2/15'[0]='wed'
                current_dow = todays_games_date_obj.strftime('%a').lower()
                #print('current_dow: ' + str(current_dow))
                if current_dow == game_dow:
                    #print("found same game day of week: " + game_dow)
                    if not game_dow in stat_dict.keys():
                        stat_dict[game_dow] = {}
                    stat_dict[game_dow][game_idx] = stat
                    #print("stat_dict: " + str(stat_dict))

                    
                # condition: time before
                # condition: time after
                # see if this game is 1st or 2nd night of back to back bc we want to see if pattern for those conditions
                
                game_date_obj = datetime.strptime(game_date_string, '%m/%d/%Y')
                #print("game_date_obj: " + str(game_date_obj))

                # if current loop is most recent game (idx 0) then today's game is the next game, if current season
                # if last game of prev season then next game after idx 0 (bc from recent to distant) is next season game 1
                if game_idx == '0': # see how many days after prev game is date of today's projected lines
                    # already defined or passed todays_games_date_obj
                    # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
                    # print("todays_games_date_obj: " + str(todays_games_date_obj))
                    current_year = todays_games_date_obj.year
                    current_mth = todays_games_date_obj.month
                    if int(current_mth) > 9:
                        current_year += 1
                    if season_year == current_year: # current year
                        # change to get from team schedule page
                        # instead of assuming they play today
                        next_game_date_obj = todays_games_date_obj # today's game is the next game relative to the previous game
                    else:
                        next_game_date_obj = game_date_obj # should be 0 unless we want to get date of next season game
                #print("next_game_date_obj: " + str(next_game_date_obj))
                # no need to get next game date like this bc we can see last loop
                # else: # if not most recent game then we can see the following game in the game log at prev idx
                #     next_game_date_string = player_game_log.loc[game_idx-1, 'Date'].lower().split()[1] + "/" + season_year
                #     print("next_game_date_string: " + str(next_game_date_string))
                #     next_game_date_obj = datetime.strptime(next_game_date_string, '%m/%d/%y')
                #     print("next_game_date_obj: " + str(next_game_date_obj))

                days_before_next_game_int = (next_game_date_obj - game_date_obj).days
                days_before_next_game = str(days_before_next_game_int) + ' before'
                #print("days_before_next_game: " + days_before_next_game)

                if not days_before_next_game in stat_dict.keys():
                    stat_dict[days_before_next_game] = {}
                stat_dict[days_before_next_game][game_idx] = stat

                init_prev_game_date_string = ''
                prev_game_idx = int(game_idx) + 1
                if len(player_game_log.index) > prev_game_idx:
                    init_prev_game_date_string = player_game_log.loc[str(prev_game_idx), 'Date'].lower().split()[1]
                
                    prev_game_mth = init_prev_game_date_string.split('/')[0]
                    final_season_year = season_year
                    if int(prev_game_mth) > 9:
                        final_season_year = str(int(season_year) - 1)
                    prev_game_date_string = init_prev_game_date_string + "/" + final_season_year
                    #print("prev_game_date_string: " + str(prev_game_date_string))
                    prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%Y')
                    #print("prev_game_date_obj: " + str(prev_game_date_obj))

                    days_after_prev_game_int = (game_date_obj - prev_game_date_obj).days
                    days_after_prev_game = str(days_after_prev_game_int) + ' after'
                    #print("days_after_prev_game: " + days_after_prev_game)

                    
                    if not days_after_prev_game in stat_dict.keys():
                        stat_dict[days_after_prev_game] = {}
                    stat_dict[days_after_prev_game][game_idx] = stat

            
                    # condition: prev val
                    if stat_name in stats_of_interest:
                        #print('\n===Condition: Prev Val===\n')
                        #if game_idx != '0': # first game has no prev val, but idx goes from recent to distant so last idx is first game
                        #prev_game_idx = str(int(game_idx)+1)
                        #print('prev_game_idx: ' + str(prev_game_idx))
                        # season_part_game_log = {year: {stat name: {game idx: stat val, ... = {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
                        # get prev val from game log bc this loop constructs stat dict so not there yet
                        #stat_log = season_part_game_log
                        prev_stat_val = int(player_game_log.loc[str(prev_game_idx), stat_name.upper()])
                        
                        # if prev_game_idx in stat_dict['all'].keys():
                        #     print('found prev game')
                        #prev_stat_val = stat_dict['all'][prev_game_idx] #prev_stat_vals[stat_idx]
                        
                        prev_stat_val_key = str(prev_stat_val) + ' prev'
                        #print('prev_stat_val_key: ' + str(prev_stat_val_key))
                        if not prev_stat_val_key in stat_dict.keys():
                            stat_dict[prev_stat_val_key] = {}
                        stat_dict[prev_stat_val_key][game_idx] = stat

                # condition: teammates out
                # condition: teammates in
                # condition: opponent team and players
                #====Players in Game stats
                # get game players from all game players dict
                #game_players = []
                #teammates = []
                #opponents = []
                #print('game_players: ' + str(game_players))
                # get current players from roster minus inactive players
                # we get current players when we know about the current game 
                
                current_players = { 'away': [], 'home': [] } # we get current players from team rosters
                #print('current_players: ' + str(current_players))
                current_teammates = [] # if blank then show all possible combos/lineups
                #print('current_teammates: ' + str(current_teammates))

                
                # if we do not have the game box score bc it does not exist yet then pass to the next game
                # the order we fill the stats dict depends on the order of games played bc we are going game by game
                if season_year in all_box_scores.keys() and len(all_box_scores[season_year].keys()) > 0:
                    # if game key not in dict then we dont have info about it
                    # but if we have dict but missing this game then it is error bc we already read all players in games
                    if game_key in all_box_scores[season_year].keys():
                        # no stats needed bc no game recorded? no we still go thru each stat for other conds

                        game_players = all_box_scores[season_year][game_key] # {away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
                        #print('game_players: ' + str(game_players))

                        
                        # condition: game teammates
                        # {starters:[],bench:[]}
                        # also add game opps bc depends on actual opp players out as well
                        # get probs for games against individual players and get weighted avg for all players, to get more sample size
                        # as well as prob for only games with exact opp players but very small sample misleading
                        if len(game_players.keys()) > 0:
                            player_loc = 'away'
                            opp_loc = 'home'
                            #game_teammates = game_players[loc_key] # teammates includes main player of interest in loop
                            if player_team == home_abbrev:
                                player_loc = 'home'
                                opp_loc = 'away'
                            game_teammates = game_players[player_loc]
                            #print('game_teammates: ' + str(game_teammates))
                            game_opps = game_players[opp_loc]
                            #print('game_opps: ' + str(game_opps))
                            # get full list of teammates this game without separating start and bench
                            # bc we loop thru all teammates to see who is in and out
                            game_teammates_list = []
                            for team_part, teammates in game_teammates.items():
                                if team_part != 'dnp': # do not add dnp players to stat dict bc will not match cur conds
                                    for teammate in teammates:
                                        game_teammates_list.append(teammate)
                            #print('game_teammates_list: ' + str(game_teammates_list))
                            game_opps_list = []
                            for team_part, opps in game_opps.items():
                                if team_part != 'dnp': # do not add dnp players to stat dict bc will not match cur conds
                                    for opp in opps:
                                        game_opps_list.append(opp)
                            #print('game_opps_list: ' + str(game_opps_list))
                            
                            starters_key = 'starters'
                            bench_key = 'bench'
                            in_key = 'in'
                            opp_key = 'opp'
                            # we need players in alphabetical string to easily compare to other games
                            # might as well compare strings bc need str as key
                            #in_teammates_list = []
                            game_teammates_str = generate_players_string(game_teammates_list) + ' ' + in_key
                            game_opps_str = generate_players_string(game_opps_list) + ' ' + opp_key + ' ' + in_key
                            # OR we could compare each player in list
                            # but then what would we use as key? names in order so first 5 are starters and remaining are bench
                            # order matters bc it is in order of position and therefore matchup 
                            # but it is also arbitrary so could mislead and reduce sample size
                            # ideally get both samples only in order by position and samples where order does not matter as long as the players played together
                            # first say order does not matter and then get where order matters
                            # bc we can get more samples which should improve accuracy
                            # still separate starters and bench
                            
                            
                            
                            # condition: starters/starting
                            if starters_key in game_teammates.keys():
                                starters = game_teammates[starters_key]

                                # organize alphabetically regardless of position bc we can get more samples 
                                # where they played together but at different positions they still play like they play?
                                # get both but first favor sample size
                                starters_str = generate_players_string(starters) + ' ' + starters_key
                                

                                # condition: bench
                                bench = game_teammates[bench_key]
                                bench_str = generate_players_string(bench) + ' ' + bench_key
                                

                                # condition: player start
                                # did current player start or come off bench?
                                # condition: player start or team unit/part (start/bench)
                                player_start = 'start'
                                if player_abbrev in bench_str:
                                    player_start = 'bench'
                                if not player_start in stat_dict.keys():
                                    stat_dict[player_start] = {}
                                stat_dict[player_start][game_idx] = stat

                                # only add key for current teammates bc we dont need to see all teammates here
                                # if no inactive players given then we can see all previous games with any (even 1) of current teammates
                                # but what if a prev game has a player that is not playing in current game?
                                # then that player completely changes the composition of stats
                                # does the prev game have to have all the current teammates to pass the check?
                                # or can it be missing a current player? 
                                # if prev game is missing current player then that will completely change the comp also
                                # if we are not sure who is playing in current game then show all possible teammates
                                # once we get current roster, we can narrow it down to those possible players
                                # then we can narrow it down further when we get inactive players list for the current game
                                #current_teammates_in_prev_game = determiner.determine_current_teammates_in_game(game_teammates, current_teammates)
                                #if len(current_teammates_in_prev_game) > 0: # if any of the current teammates are in the prev game of interest, then add to stats dict for review
                                    #print("found same game teammates: " + game_teammates)

                                # conditions related to players in games
                                # teammates and opps
                                # starters and bench

                                # condition: game teammates
                                if not game_teammates_str in stat_dict.keys():
                                    stat_dict[game_teammates_str] = {}
                                stat_dict[game_teammates_str][game_idx] = stat
                                

                                # condition: teammate, add at same time as starters and bench bc inclusive
                                for teammate in game_teammates_list:
                                    if teammate in starters or teammate in bench:
                                        teammate_str = teammate + ' ' + in_key
                                        if not teammate_str in stat_dict.keys():
                                            stat_dict[teammate_str] = {}
                                        stat_dict[teammate_str][game_idx] = stat
                                

                                # condition: game starters
                                if not starters_str in stat_dict.keys():
                                    stat_dict[starters_str] = {}
                                stat_dict[starters_str][game_idx] = stat

                                # need a condition for each starter as well as all starters together
                                # and could even do combos of players but need to see if needed
                                # for now just do all 5 together and each 1 separate
                                for starter in starters:
                                    starter_str = starter + ' ' + starters_key
                                    if not starter_str in stat_dict.keys():
                                        stat_dict[starter_str] = {}
                                    stat_dict[starter_str][game_idx] = stat

                                    # in_str = starter + ' ' + in_key
                                    # if not starter_str in stat_dict.keys():
                                    #     stat_dict[starter_str] = {}
                                    # stat_dict[starter_str][game_idx] = stat

                                

                                # condition: game bench
                                if not bench_str in stat_dict.keys():
                                    stat_dict[bench_str] = {}
                                stat_dict[bench_str][game_idx] = stat

                                for bencher in bench:
                                    bencher_str = bencher + ' ' + bench_key
                                    if not bencher_str in stat_dict.keys():
                                        stat_dict[bencher_str] = {}
                                    stat_dict[bencher_str][game_idx] = stat

                                

                                # condition: teammate out
                                out_key = 'out'
                                out = game_teammates[out_key]
                                for out_player in out:
                                    out_str = out_player + ' ' + out_key
                                    if not out_str in stat_dict.keys():
                                        stat_dict[out_str] = {}
                                    stat_dict[out_str][game_idx] = stat
                            else:
                                print('Caution: No Game Teammates! ' + game_key)

                            if len(game_opps.keys()) > 0:
                                opp_starters = game_opps[starters_key]
                                opp_starters_str = generate_players_string(opp_starters) + ' ' + opp_key + ' ' + starters_key
                            
                                opp_bench = game_opps[bench_key]
                                opp_bench_str = generate_players_string(opp_bench) + ' ' + opp_key + ' ' + bench_key
                            
                                # condition: game opps
                                if not game_opps_str in stat_dict.keys():
                                    stat_dict[game_opps_str] = {}
                                stat_dict[game_opps_str][game_idx] = stat

                                # condition: opp player
                                for opp in game_opps_list:
                                    if opp in opp_starters or opp in opp_bench:
                                        opp_str = opp + ' ' + opp_key + ' ' + in_key
                                        if not opp_str in stat_dict.keys():
                                            stat_dict[opp_str] = {}
                                        stat_dict[opp_str][game_idx] = stat

                                # condition: opp starters
                                if not opp_starters_str in stat_dict.keys():
                                    stat_dict[opp_starters_str] = {}
                                stat_dict[opp_starters_str][game_idx] = stat

                                # need a condition for each starter as well as all starters together
                                # and could even do combos of players but need to see if needed
                                # for now just do all 5 together and each 1 separate
                                for opp_starter in opp_starters:
                                    opp_starter_str = opp_starter + ' ' + opp_key + ' ' + starters_key
                                    if not opp_starter_str in stat_dict.keys():
                                        stat_dict[opp_starter_str] = {}
                                    stat_dict[opp_starter_str][game_idx] = stat

                                # condition: opp bench
                                if not opp_bench_str in stat_dict.keys():
                                    stat_dict[opp_bench_str] = {}
                                stat_dict[opp_bench_str][game_idx] = stat

                                for opp_bencher in opp_bench:
                                    opp_bencher_str = opp_bencher + ' ' + opp_key + ' ' + bench_key
                                    if not opp_bencher_str in stat_dict.keys():
                                        stat_dict[opp_bencher_str] = {}
                                    stat_dict[opp_bencher_str][game_idx] = stat

                                # condition: opp out
                                opp_out = game_opps[out_key]
                                for opp_out_player in opp_out:
                                    opp_out_str = opp_out_player + ' ' + opp_key + ' ' + out_key
                                    if not opp_out_str in stat_dict.keys():
                                        stat_dict[opp_out_str] = {}
                                    stat_dict[opp_out_str][game_idx] = stat

                            else:
                                print('Caution: No Game Opponents! ' + game_key)

                            # should we check all yrs bc sometimes player played last yr but not yet played this yr?
                            # yes bc we want to consider this a condition marked as NA not blank
                            # only if they actually played prev yrs and are still on roster
                            #for year in player_teammates.
                            # if season yr = cur yr, then check roster for teammates list
                            # bc teammate may not have yet played this yr but played last yr
                            # OR should we use current roster for all yrs
                            # bc player may have played this yr but not prev yrs
                            # teammates = []
                            # if season_year == current_year:
                            #     teammates = rosters[player_team]
                            # else:
                            #     teammates = player_teammates[season_year]

                            # if playing against former teammate, what to show?
                            # measured prob is not a relevant current condition so NA?
                            # we only care about current teammates but cannot loop thru cur teammates bc then would consider them all out prev seasons
                            # instead only add from prev seas if they are also cur teammate
                            # OLD way used process of elim
                            # but now we have out section in game players dict bc generated box scores before
                            # for teammate in player_teammates[season_year]:
                            #     #print('teammate: ' + teammate)
                            #     #print('game_teammates_list: ' + str(game_teammates_list))
                            #     # we only care about current teammates but cannot loop thru cur teammates bc then would consider them all out prev seasons
                            #     # instead only add from prev seas if they are also cur teammate
                            #     # check cur roster not just active teammates bc player is out if not played yet this season
                            #     # but played with this player in prev seasons
                            #     # actually as long as it does not use as cur cond then it is ok to show that player played with them last yr
                            #     # it is like showing a cond that does not apply to all players in table of all props 
                            #     # where not all conditions match all players but we want to view it in single table
                            #     if teammate not in game_teammates_list:# and teammate in rosters[cur_team]:#player_teammates[cur_yr]: # teammate out
                            #         # if played with teammate last yr but not this yr, 
                            #         # no longer teammate, so consider NA
                            #         #if season_year != current_year and teammate not in rosters[cur_team]:
                            #         #print('teammate out')
                            #         teammate_out_key = teammate + ' out'

                            #         if not teammate_out_key in stat_dict.keys():
                            #             stat_dict[teammate_out_key] = {}
                            #         stat_dict[teammate_out_key][game_idx] = stat

                            #print("stat_dict: " + str(stat_dict))

                            # else:
                            #     print('Warning: Game key not in players in games dict so box score not available! ' + game_key)
                        else:
                            print('Warning: Blank box score! ' + game_key)
                # dont need to track prev vals separate bc stored in stat dict so just get game idx-1
                #prev_stat_vals.append(stat)



            # ====Career/All Seasons Stats
            # START with week number this season compared to prev seasons
            # per game is overfit, and per mth is underift so per week is ok fit (maybe even 2 or 3 weeks?)
            # then need to determine best spread over time samples
            # if we find a game played on the same day/mth previous seasons, add a key for this/today's day/mth
            #today_date_data = todays_games_date.split('/')
            today_mth_day = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day) #today_date_data[0] + '/' + today_date_data[1]
            if init_game_date_string == today_mth_day:
                #print("found same game day/mth in previous season")
                for stat_idx in range(len(all_seasons_stats_dicts.values())):
                    stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not game_date_string in stat_dict.keys():
                        stat_dict[game_date_string] = {}
                        stat_dict[game_date_string][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
                    else:
                        if game_idx in stat_dict[game_date_string].keys():
                            stat_dict[game_date_string][game_idx].append(stat)
                        else:
                            stat_dict[game_date_string][game_idx] = [stat]
                #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))
            # add key for the current game number for this season and add games played from previous seasons (1 per season)
            game_num = num_season_part_games - int(game_idx) # bc going from recent to past
            if game_num == num_games_played:
                #print("found same game num in previous season")
                for stat_idx in range(len(all_seasons_stats_dicts.values())):
                    stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not num_games_played in stat_dict.keys():
                        stat_dict[num_games_played] = {}
                        stat_dict[num_games_played][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
                    else:
                        if game_idx in stat_dict[num_games_played].keys():
                            stat_dict[num_games_played][game_idx].append(stat)
                        else:
                            stat_dict[num_games_played][game_idx] = [stat]
                #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))


            # after all keys are set, set next game as current game for next loop
            next_game_date_obj = game_date_obj # next game bc we loop from most to least recent

    else:
        # if getting data from file, may not have game log from internet source
        # data_type = "Game Log"
        # player_season_log = reader.read_season_log_from_file(data_type, player_name, 'tsv')
        print('Warning: No game log for player: ' + player_name)

    # all_stats_dicts: {'pts': {'all': {0: 18, 1: 19...
    #print('all_stats_dicts: ' + str(all_stats_dicts))
    return all_stats_dicts

# at this point we have reg season and postseason separately so get avg of them
# for a single season at a time
def generate_full_season_stat_dict(player_stat_dict):

    print('\n===Generate Full Season Stats===\n')

    full_season_stat_dict = {}

    full_season_stats = [] # get avg of all parts

    # for season_part, part_stat_dict in player_stat_dict.items():
    #     for stat_name, stat_dict in part_stat_dict.items():

    return full_season_stat_dict

# use player_team to get away/home team to get game key to get players in game
# need current_year_str to get filename for cur yr bc season yr not always cur yr
# do not need to pass in season_year and minus 1 per loop bc looping thru season logs
# player_teams = {'2018': {'mia': 69}, '2019...
# game_teams: [('mem', 'okc'), ('dal', 'den')...
# player_stat_dict: {'2023': {'regular': {'pts': {'all': {0: 18, 1: 19...
def generate_player_stat_dict(player_name, player_season_logs, todays_games_date_obj, all_box_scores={}, all_games_info={}, player_teams={}, current_year_str='', todays_date=datetime.today().strftime('%m-%d-%y'), game_teams=[], projected_lines_dict={}, init_player_stat_dict={}, find_players=False, player_position='', player_teammates={}, rosters={}, cur_season_part=''):
    print('\n===Generate Player Stat Dict: ' + player_name.title() + '===\n')
    print('Settings: find players, todays date to get day conditions, current year to get changing stat dicts file')
    print('\nInput: Player of Interest')
    print('Input: player_season_logs = {year: {stat name: {game idx: stat val, ... = {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
    print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
    print('Input: player_teams = {year:{team:{GP:gp, MIN:min},... = {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('Input: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\'), ...]')
    print('Input: init_player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = \n')
    print('Input: player_position = \'position\' = ' + player_position)
    print('Input: player_teammates = {year:[teammates],... = {2024: [J Randle PF, ... = ' + str(player_teammates))
    print('Input: rosters = {team:roster, ... = {\'nyk\': [jalen brunson, ...], ...')
    print('\nOutput: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...\n')


    player_stat_dict = {}

    # keep in mind, when we add a new feature such as a new condition to the stat dict,
    # then we must manually erase old saved stat dict OR make setting to overwrite it
    # or else we would need to read from internet every time anyway which defeats the purpose of storing locally
    # init_player_stat_dict
    # better to get cur yr here bc also used to divide before writing, although could just take first item in dict as cur yr
    # need filenames to write every time and read only if not already passed init dicts
    if current_year_str == '':
        current_year_str = determiner.determine_current_season_year()
    player_cur_stat_dict_filename = 'data/stat dicts/' + player_name + ' ' + current_year_str + ' stat dict ' + todays_date + '.json'
    # print('player_cur_stat_dict_filename: ' + cur_file)
    # print('Try to find local CURRENT season stat dict for ' + player_name + '.')
    # init_player_cur_stat_dict = reader.read_json(player_cur_stat_dict_filename)

    player_prev_stat_dicts_filename = 'data/stat dicts/' + player_name + ' prev stat dicts.json'
    # print('player_prev_stat_dicts_filename: ' + prev_file)
    # print('Try to find local PREVIOUS seasons stat dicts for ' + player_name + '.')
    # init_player_prev_stat_dicts = reader.read_json(player_prev_stat_dicts_filename)
    if len(init_player_stat_dict.keys()) == 0:
        # #files = [player_cur_stat_dict_filename, player_prev_stat_dicts_filename]
        # cur_file = player_cur_stat_dict_filename
        # prev_file = player_prev_stat_dicts_filename
        init_player_stat_dict = reader.read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename) #reader.read_json_multiple_files(files)

    player_stat_dict = copy.deepcopy(init_player_stat_dict)


    # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
    # we need to know all possible teammates
    # which we can get from roster
    # https://www.espn.com/nba/team/roster/_/name/bos/boston-celtics
    # or we could get from box scores we already saved locally
    # in all_teammates, we only want teammates per season bc if all seasons then misleading data
    # all_teammates = {yr:[teammate,...],...}
    # teammates for all yrs not equal to roster bc not everyone on roster played in game
    # but would it be good enough to have more players than we need and then if didnt play then will discard
    # rather than going through all box scores just to get teammates?
    # it is needed for old teams where rosters not available easily?
    # BUT even those rosters might be easy to get online
    #all_teammates = reader.read_all_teammates(player_name, all_box_scores, player_teams, player_season_logs, all_players_teammates)
    if len(player_teammates.keys()) == 0:
        player_teammates = reader.read_player_teammates(player_name, player_season_logs, all_box_scores)

    # get current opponent if available so we can focus on current conditions
    # if we do not know current opponent then show for all opps
    # for prev seasons we want to get stats for all conditions 
    # BUT cur seasons we only need cur condition bc updating each day
    # the code is st if stat dict is saved at all then it will not read new stats
    # so if already ran once today then will need to manually delete if want new features added
    # OLD version used projected lines to get opp but
    # NEW version uses all games today matchups and player team to get opp
    # opponent = ''
    # print('projected_lines_dict: ' + str(projected_lines_dict))
    # if player_name in projected_lines_dict.keys():
    #     player_projected_lines_dict = projected_lines_dict[player_name]
    #     print(player_name + ' projected_lines_dict: ' + str(player_projected_lines_dict))
    #     # for each player we loop thru we add their avgs to projected line if none given
    #     # we want to get projected lines for all conditions, including opponent
    #     if 'opp' in player_projected_lines_dict:
    #         opponent = player_projected_lines_dict['opp'].lower() # collect data against opponent to see previous matchups
    #     else:
    #         print('Warning: opp not in projected lines for ' + player_name)

    cur_team = determiner.determine_player_current_team(player_name, player_teams, cur_yr='', rosters={})

    opponent = determiner.determine_opponent_team(player_name, player_teams, game_teams, current_year_str, rosters, cur_team)


    all_seasons_pts_dicts = {}
    all_seasons_rebs_dicts = {}
    all_seasons_asts_dicts = {}
    all_seasons_winning_scores_dicts = {}
    all_seasons_losing_scores_dicts = {}
    all_seasons_minutes_dicts = {}
    all_seasons_fgms_dicts = {}
    all_seasons_fgas_dicts = {}
    all_seasons_fg_rates_dicts = {}
    all_seasons_threes_made_dicts = {}
    all_seasons_threes_attempts_dicts = {}
    all_seasons_threes_rates_dicts = {}
    all_seasons_ftms_dicts = {}
    all_seasons_ftas_dicts = {}
    all_seasons_ft_rates_dicts = {}
    all_seasons_bs_dicts = {}
    all_seasons_ss_dicts = {}
    all_seasons_fs_dicts = {}
    all_seasons_tos_dicts = {}

    all_seasons_stats_dicts = {'pts':all_seasons_pts_dicts, 'reb':all_seasons_rebs_dicts, 'ast':all_seasons_asts_dicts, 'w score':all_seasons_winning_scores_dicts, 'l score':all_seasons_losing_scores_dicts, 'min':all_seasons_minutes_dicts, 'fgm':all_seasons_fgms_dicts, 'fga':all_seasons_fgas_dicts, 'fg%':all_seasons_fg_rates_dicts, '3pm':all_seasons_threes_made_dicts, '3pa':all_seasons_threes_attempts_dicts, '3p%':all_seasons_threes_rates_dicts, 'ftm':all_seasons_ftms_dicts, 'fta':all_seasons_ftas_dicts, 'ft%':all_seasons_ft_rates_dicts, 'blk':all_seasons_bs_dicts, 'stl':all_seasons_ss_dicts, 'pf':all_seasons_fs_dicts, 'to':all_seasons_tos_dicts} # loop through to add all new stats with 1 fcn

    for season_year, player_game_log in player_season_logs.items():

        # need string to compare to json
        #season_yr_str = str(season_year)
        #print("\n===Year " + season_year + "===\n")

        player_game_log_df = pd.DataFrame(player_game_log)#.from_dict(player_game_log) #pd.DataFrame(player_game_log)
        player_game_log_df.index = player_game_log_df.index.map(str)
        #print('converted_player_game_log_df:\n' + str(player_game_log_df))

        
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        # for each part of season, reg and post:
        # first get stats for reg season
        # season_part = 'regular'
        
        # gen all stats dicts for this part of this season
        # here we convert season year key to string?
        # cur season stat dict gets replaced each day bc file has date in name
        # so do we need to save cur season box scores which make up cur stat dict?
        # OR can we add new entries to existing cur stat dict?
        # if we add new entries instead of overwriting, 
        # then it would require read from internet each run?
        # the condition is if season year in stat dict and it is missing games
        # but we would only know if missing games bc we read from internet
        # the rule seems to be if the data changes,
        # then we must name the file based on how often we want to update it
        # in this case the date is in the file so we know if we ran it before/after last change
        # could we save the box score stat dicts separately if we are already planning on saving box scores?
        # we can subtract number we have saved from number of games in log read from internet
        # so we know how many new box scores since last run
        # must then search for prev saved file
        # is it easier to keep prev day cur season files so we can see difference between cur day
        # OR keep cur season box scores local so we can reconstruct cur season stat dict from local box scores 
        # and only read newest box score from internet
        # seems easier to save cur seas box scores

        # for now if season yr already in stat dict then no need to read again
        # but what if new features like find players turned from false to true? then we would need to get stat dict each time and check difference before saving new?
        # see determine_need_box_score to see how we can still update
        # if stat dict exists but missing key
        # print('is season_year string? ' + season_year) # yes, but how??? it is input as int. nooo it is the key in the season logs not the init param so fix
        # if len(player_stat_dict.keys()) > 0:
        #     print('is stat dict key string? ' + list(player_stat_dict.keys())[0]) # yes
        if determiner.determine_need_stat_dict(player_stat_dict, season_year, find_players):
        #if season_year not in player_stat_dict.keys() and season_yr_str not in player_stat_dict.keys(): # if determine_team_player_key_in_stat_dict() team_players_key not in player_stat_dict[season_year].keys():
            player_stat_dict[season_year] = {}

            year_games_info = all_games_info[season_year]
        
            # only need to get new stat dict if different than saved data
            season_parts = ['regular']
            if cur_season_part == 'postseason':
                season_parts.extend(['postseason', 'full'])

            for season_part in season_parts:
                player_stat_dict[season_year][season_part] = generate_player_all_stats_dicts(player_name, player_game_log_df, opponent, player_teams, season_year, todays_games_date_obj, all_box_scores, year_games_info, player_teammates, all_seasons_stats_dicts, season_part, player_position, rosters, cur_team) #generate_full_season_stat_dict(player_stat_dict)


        #season_year -= 1

        #print('player_stat_dict: ' + str(player_stat_dict))

    if not init_player_stat_dict == player_stat_dict:
        writer.write_cur_and_prev(init_player_stat_dict, player_stat_dict, player_cur_stat_dict_filename, player_prev_stat_dicts_filename, current_year_str, player_name)

    # player_stat_dict: {'2023': {'regular': {'pts': {'all': {0: 18, 1: 19...
    #print('player_stat_dict: ' + str(player_stat_dict))
    return player_stat_dict

# -first take dnp players (avg <10min) off current conditions bench
# -then take dnp players off games they played <10min (keep in games they  played >10min bc bench wont match anyway!)
def generate_all_box_scores(init_all_box_scores, all_teams_players, teams_current_rosters, all_players_teams, all_players_abbrevs, cur_yr):
    print('\n===Generate All Box Scores===\n')
    print('Input: Current Year to get current teams')
    print('Input: init_all_box_scores = {year:{game key:{away:{starters:{player:play time,...},bench:{...}},home:{...}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...')
    print('Input: all_teams_players = {year:{team:[players], ... = {\'2024\': {\'wsh\': [\'kyle kuzma\', ...')
    print('Input: teams_current_rosters = {team:roster, ... = {\'nyk\': [jalen brunson, ...], ...')
    print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')
    print('\nOutput: gen_all_box_scores = {year:{game key:{away:{starters:{player:play time,...},bench:{...},dnp:{...},out:{...}},home:{...}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...\n')
    
    gen_all_box_scores = {}
    init_gen_box_scores = {}

    season_years = list(all_players_abbrevs.keys())
    for year in season_years:
        box_scores_file = 'data/box scores - ' + year + '.json'
        init_year_box_scores = reader.read_json(box_scores_file)
        init_gen_box_scores[year] = init_year_box_scores

    gen_all_box_scores = copy.deepcopy(init_gen_box_scores)

    # if player avg min > 12 or 10 and they did not play game, then consider them out
    # if player avg min < 13 or 11 and they did not play game, then consider them bench
    # {game key:{away:{starters:{player:play time,...},bench:{...}},home:{...}}
    for year, year_box_scores in init_all_box_scores.items():
        if year not in gen_all_box_scores.keys():
            gen_all_box_scores[year] = {}

        # {away:{starters:{player:play time,...},bench:{...}},home:{...}}
        for game_key, game_players in year_box_scores.items():
            #print('game_key: ' + str(game_key))

            if game_key in gen_all_box_scores[year].keys():
                continue # already saved game

            gen_all_box_scores[year][game_key] = {}
            # {starters:{player:play time,...},bench:{...}}
            for team_loc, game_team_players in game_players.items():
                # print('team_loc: ' + str(team_loc))
                # print('game_team_players: ' + str(game_team_players))
                gen_all_box_scores[year][game_key][team_loc] = {}
                final_team_players = gen_all_box_scores[year][game_key][team_loc]
                # go thru full roster to see which players not in box score
                team = determiner.determine_team_from_game_key(game_key, team_loc)
                #print('team: ' + str(team))
                if team in all_teams_players[year].keys():
                    all_team_players = all_teams_players[year][team]
                    if year == cur_yr:
                        all_team_players = teams_current_rosters[team]
                    #print('all_team_players: ' + str(all_team_players))
                    # {player:play time,...}
                    starters_key = 'starters'
                    starters = game_team_players[starters_key]
                    final_team_players[starters_key] = starters

                    bench_key = 'bench'
                    init_bench = game_team_players[bench_key]
                    #print('init_bench: ' + str(init_bench))
                    final_team_players[bench_key] = {}
                    final_bench = final_team_players[bench_key]

                    dnp_key = 'dnp'
                    out_key = 'out'
                    final_team_players[dnp_key] = {}
                    dnp = final_team_players[dnp_key]
                    final_team_players[out_key] = {}
                    out = final_team_players[out_key]
                    # add practice players to bench
                    # what if we do not know abbrev bc they have not played yet?
                    # use lowercase full name so we can differentiate it in process
                    for player in all_team_players:
                        # if not in all players teams then has not played in reg season at all
                        #print('\nPlayer: ' + player)
                        
                        # if not in all players teams then never played bc no stats table at all
                        if player in all_players_teams.keys():
                            #player_abbrev = player # if blank
                            #player_mean_minutes = 0
                            # player may be on roster but not played so not in all players teams
                            player_mean_minutes = 0
                            if year in all_players_teams[player].keys():
                                # player may have been recently traded and not played yet (eg theo maledon)
                                if team in all_players_teams[player][year].keys():
                                    player_mean_minutes = all_players_teams[player][year][team]['MIN']
                            # if year not in all players teams then do we need player abbrev?
                            # possibly to put as dnp player preferred abbrev if available but if they never played ever then they have no established abbrev
                            # UNLESS we look in preseason games
                            # some players have multiple abbrevs irregularly
                            # so we need to get all abbrevs bc if 1 abbrev doesnt match in a game, the other abbrev might
                            player_abbrevs = []#isolator.isolate_player_abbrevs(player, team, all_players_abbrevs[year])
                            for abbrev_key, name in all_players_abbrevs[year].items():
                                if player == name:
                                    #print('found name ' + name)
                                    abbrev_data = abbrev_key.split('-')
                                    abbrev = abbrev_data[0]
                                    player_team = abbrev_data[1].lower()
                                    if team == player_team:
                                        #print('found team ' + team)
                                        #player_abbrev = abbrev
                                        player_abbrevs.append(abbrev)
                                        #break
                            
                            # print('player_abbrev: ' + player_abbrev)
                            # if player_abbrev != player: 
                            #print('player_abbrevs: ' + str(player_abbrevs))
                            player_keys = [player]
                            if len(player_abbrevs) > 0:
                                #print('found player abbrevs ' + player)
                                player_keys = player_abbrevs
                            # else: # abbrev not found
                            #     print('Caution: Abbrev not found! ' + player)

                            #print('player_keys: ' + str(player_keys))
                            if len(player_keys) > 0:
                                #for player_abbrev in player_abbrevs:
                                # how can we tell if abbrev not in game bc out or wrong abbrev
                                # we cant so check both before concluding
                                
                                player_abbrev = determiner.determine_abbrev_in_game(player_keys, starters)
                                #print('player_abbrev after starters: ' + player_abbrev)
                                #if player_abbrev not in starters.keys(): # starters stay
                                if player_abbrev == '': # not in starters
                                    
                                    # if on bench but <10min avg time and cur play time, move to dnp
                                    #if player_abbrev in init_bench.keys():
                                    player_abbrev = determiner.determine_abbrev_in_game(player_keys, init_bench)
                                    #print('player_abbrev after bench: ' + player_abbrev)
                                    
                                    if player_abbrev != '': # in bench
                                        play_time = init_bench[player_abbrev]
                                        #print('play_time: ' + str(play_time))
                                        # irregular case
                                        if play_time == '-':
                                            play_time = '0'
                                        if int(play_time) > 11:
                                            #print('found bench')
                                            final_bench[player_abbrev] = play_time
                                        else:
                                            if player_mean_minutes > 11.5:
                                                #print('found bench')
                                                final_bench[player_abbrev] = play_time
                                            else:
                                                #print('found dnp')
                                                dnp[player_abbrev] = play_time

                                    else: # player abbrev == '' blank bc not in bench nor starters
                                        # abbrev saved but not in box score so which version of abbrev to use?
                                        # we can save full name here and then when checking if this game matches current conds,
                                        # we can consider this as matching any/all of the player's abbrevs
                                        # but we can simply take 1st abbrev bc when we take samples we can consider all with any version of abbrev
                                        if len(player_abbrevs) > 0:
                                            player_abbrev = player_abbrevs[0] # need only 1 to compare to all for this player
                                        else: # abbrev not saved
                                            player_abbrev = player # show player name so we know which abbrev is missing
                                        #print('player_abbrev out or dnp: ' + player_abbrev)

                                        if player_mean_minutes > 11.5:
                                            #print('found out')
                                            out[player_abbrev] = 0
                                        else:
                                            #print('found dnp')
                                            dnp[player_abbrev] = 0

                            else: # irregular abbrev not found
                                print('Warning: Forgot to set player key! ' + player)
                        else: # maybe in cur roster but not played yet
                            #print('found dnp')
                            dnp[player] = 0  

                        #print('gen_all_box_scores after ' + player + ':\n' + str(gen_all_box_scores))                  
                else:
                    print('Warning: Unknown team in Game Key! ' + game_key)

                # game_team_players[dnp_key] = dnp
                # game_team_players[out_key] = out
                #print('gen_all_box_scores: ' + str(gen_all_box_scores))

    if not init_gen_box_scores == gen_all_box_scores:
        for year in season_years:
            year_box_scores = gen_all_box_scores[year]
            box_scores_file = 'data/box scores - ' + year + '.json'
            writer.write_json_to_file(year_box_scores, box_scores_file)


    print('gen_all_box_scores: ' + str(gen_all_box_scores))
    return gen_all_box_scores
# we need to know how each player plays under certain conditions
# to propose likely outcomes
# show regular season avgs
# show player stats for each condition
# allow user to choose condition by dropdown menu
# see prop gen > player stats for output: https://docs.google.com/spreadsheets/d/1vpny0uo6xyYNbpHCBndQ2Tg_WIwbXtIMGcjnzvoyDrk/edit#gid=0
# see espn for example: https://www.espn.com/nba/player/stats/_/id/3059318/joel-embiid
# we need to know how all players play under certain conditions
# to propose likely outcomes

# one outcome per stat of interest so each player has multiple outcomes
# we need game teams to know opponents
# so we can get conditional stats
# and only read game page once
# all players props includes all combos
def generate_all_players_props(settings={}, players_names=[], game_teams=[], teams_current_rosters={}, all_teams=[], todays_games_date_obj=datetime.today()):
    print('\n===Generate All Players Props===\n')
    # settings depend on context and type of test undergoing
    # since this is the main fcn called from the main file
    # we prefer to input user variables from main file bc it is short and easy to use and will eventually be UI page
    print('Settings: find/read new data, read certain seasons and time periods, irregular play time and other vars')
    print('\nInput: default = all players in upcoming games today')
    print('Input: players_names = [p1, ...] = [\'jalen brunson\', ...]')
    print('Input: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\'), ...]')
    print('Input: teams_current_rosters = {team:[players],..., {\'nyk\': [jalen brunson, ...], ...}')
    print('\nOutput: all_players_props = [{strategy x:{player:p1,...},...},...]\n')

    # init output
    players_outcomes = {}

    # enable no inputs needed, default to all games
    if len(players_names) == 0 and len(teams_current_rosters.keys()) == 0:
        # read all games today
        print('read all games today')
        players_names = reader.read_teams_players(game_teams, read_new_teams)

    # get info about current todays date
    todays_games_date_obj = datetime.today() # by default assume todays game is actually today and we are not analyzing in advance

    current_year_str = determiner.determine_current_season_year(todays_games_date_obj)
    todays_date = todays_games_date_obj.strftime('%m-%d-%y')

    # should init setting be string?
    # as user input i think it will be string converted to int
    season_year = current_year_str #determiner.determine_current_season_year() # based on mth, changed to default or current season year, which is yr season ends
    if 'read season year' in settings.keys():
        season_year = settings['read season year']

    # determine season part from time of yr
    season_part = determiner.determine_current_season_part(todays_games_date_obj)

    # === gather external data
    # OLD: player_espn_ids_dict
    all_players_espn_ids = reader.read_all_players_espn_ids(players_names)

    # read teams players
    read_new_teams = False # saves time during testing other parts if we read existing teams saved locally
    # what if we want to read previous season?
    if 'read new teams' in settings.keys():
        read_new_teams = settings['read new teams']
    # read teams rosters
    read_new_rosters = False # saves time during testing other parts if we read existing teams saved locally
    # what if we want to read previous season?
    if 'read new rosters' in settings.keys():
        read_new_rosters = settings['read new rosters']
    
    find_players = False
    if 'find players' in settings.keys():
        find_players = settings['find players']

    # all_players_teams = {player:{year:{team:gp,...},...}}
    # we use player teams to get opponent in game log by process of elimination
    # also to get abbrevs/full names to get lineup parts
    # if we dont need to find relations to other players then just read for input players

    all_players_teams = reader.read_all_players_teams(players_names, all_players_espn_ids, read_new_teams, find_players) # only read team from internet if not saved

    # if we gave player lines, then format them in dict
    # projected_lines_dict = {}
    # if len(raw_projected_lines) > 0:
    #     projected_lines_dict = generate_projected_lines_dict(raw_projected_lines, all_players_espn_ids, player_teams, players_names, settings['read new teams'], cur_yr=current_year_str)
    # print('\nprojected_lines_dict after gen projected lines: ' + str(projected_lines_dict))

    # read game logs
    read_x_seasons = 1 # saves time during testing other parts if we only read 1 season
    # what if we want to read previous season? make int so large int will read all seasons
    if 'read x seasons' in settings.keys():
        read_x_seasons = settings['read x seasons']
    # OLD: all_player_season_logs_dict
    all_players_season_logs = reader.read_all_players_season_logs(players_names, all_players_espn_ids, all_players_teams, read_x_seasons, season_year, current_year_str)
    
    #print('projected_lines_dict after read season logs: ' + str(projected_lines_dict))

    # read player positions so we can see prob of stats with certain positions playing
    # need to differentiate players with same name
    # and shorter than full name to put name abbrev + position
    # all_players_positions = {player:position, ...} = {\'jalen brunson\': \'pg\', ...}
    all_players_positions = reader.read_all_players_positions(players_names, all_players_espn_ids)

    # need season yrs to get per unit time stats
    # and prev vals in stat dict to see sequence/trend
    # could just take the first year in the dict by default
    # but user already told us the years to look at in settings
    season_years = []
    for yr in range(season_year,season_year-read_x_seasons,-1):
        season_years.append(str(yr)) # make string to compare to json keys

    # use init stat dicts to see which stats already saved so no need to read from internet
    # use for box scores
    # for now only using to see if we want to read box scores or if already read
    # also may change so we save just stat probs if not using stat dict for anything else but computing stat probs
    # init_player_stat_dicts = {player: {"2023": {"regular": {"pts": {"all": {"0": 14,...
    #init_player_stat_dicts = reader.read_all_players_stat_dicts(players_names, current_year_str, todays_date)
    # find teammates and opponents for each game played by each player
    
    # need game ids for game info and box scores, and anything else on espn website
    read_new_game_ids = True
    if 'read new game ids' in settings.keys():
        read_new_game_ids = settings['read new game ids']

    # read all games info from main page
    # eg time of day, city, audience/stadium size, refs, odds
    all_games_info = reader.read_all_games_info(all_players_season_logs, all_players_teams, season_part, read_new_game_ids)

    # all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}}},...}
    all_box_scores = {}
    all_players_teammates = {} 
    all_players_abbrevs = {}
    all_teams_players = {}
    if find_players == True:
        print('\n===FIND PLAYERS===\n')
        
        read_new_player_ids = True
        if 'read new player ids' in settings.keys():
            read_new_player_ids = settings['read new player ids']
        #print('read_new_game_ids: ' + str(read_new_game_ids))
            
        all_teams_current_rosters = reader.read_all_teams_rosters(all_teams, read_new_teams, read_new_rosters)

        # if we already have saved prev seasons then will only return this season games
        # all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
        # we only care about single season part bc if reg then take only reg box scores, and if post then take all full box scores
        # we may need to run both parts in comparison but that strategy would be based on current season part
        # if we devise a specific test needing both parts then can change code to input list of season parts
        all_box_scores_data = reader.read_all_box_scores(all_players_season_logs, all_players_teams, season_part, read_new_game_ids)#, season_year) # go thru players in all_players_season_logs to get game ids
        #all_players_in_box_scores = all_box_scores['player']
        all_box_scores = all_box_scores_data[0]
        # all box scores of interest, not including old box scores saved
        current_box_scores = all_box_scores_data[1]

        # pass all box scores to get all abbrevs bc we may be facing player who has been out and so matches out abbrev condition
        all_players_abbrevs_data = reader.read_all_players_abbrevs(all_box_scores, all_players_teams, all_teams_current_rosters, current_year_str, all_players_espn_ids, read_new_player_ids)
        all_players_abbrevs = all_players_abbrevs_data[0]
        all_players_espn_ids = all_players_abbrevs_data[1]
        # now that we have new ids, get those players teams
        # only needed for prev yrs bc current ids found from rosters
        all_players_teams = all_players_abbrevs_data[2]#reader.read_all_players_teams(all_players_espn_ids)

        # read all teams players so we can find bench by process of elimination
        # not as simple as reading roster online bc shows inactive players
        # so need box scores to show active players
        # all_teams_players = {year:{team:[players],...},...}
        # do not include practice players in all teams players???
        # OR we still consider practice players as part of team bc we are able to see their minutes to filter them out later???
        all_teams_players = reader.read_all_teams_players(all_box_scores, all_teams_current_rosters, all_players_teams, all_players_abbrevs, current_year_str, read_new_teams, all_teams)
        #all_practice_players = 

        # now that we have all teams players and abbrevs, 
        # we can see which practice players were on the bench in games they did not play
        # vs active players who were out
        all_box_scores = generate_all_box_scores(all_box_scores, all_teams_players, all_teams_current_rosters, all_players_teams, all_players_abbrevs, current_year_str)

        # for each team, practice players avg <10min per game
        # if player on roster not in box score, determine injury or practice player by avg play time
        # if practice player played a certain game it will be counted as a bench player (if came off the bench) just like if he didnt play at all but was available on the bench
        # get players teams for players in box score bc contains avg minutes data
        #all_players_teams = reader.read_all_players_teams()
        # already got all players teams from id list bc set find players=true gets every single players teams exactly for this reason!
        #all_practice_players = determiner.determine_practice_players(all_players_teams, all_teams_players, teams_current_rosters)


        # read all players teammates from season logs and all players in games
        all_players_teammates = reader.read_all_players_teammates(all_players_season_logs, all_box_scores, current_year_str, todays_date)





        # add players teams of players in box scores to relate to player of interest
        # makes it easier to get abbrevs?

        # find defensive rating/ranking by player position
        # stats from websites contradict too much so must get matchup stats from box scores
        # find_matchups = False
        # if 'find matchups' in settings.keys():
        #     find_matchups = settings['find matchups']
        # player_position = ''
        # all_matchup_data = []
        # #player_positions = {}
        # if find_matchups == True:
        #     # see if position saved in file
        #     # data_type = 'player positions'
        #     # player_positions_data = reader.extract_data(data_type, header=True)
            
        #     # for row in player_positions_data:
        #     #     print('row: ' + str(row))
        #     #     player_name = row[0]
        #     #     player_position = row[1]

        #     #     existing_player_positions_dict[player_name] = player_position
        #     # print('existing_player_positions_dict: ' + str(existing_player_positions_dict))


        #     #all_players_positions = reader.read_all_players_positions(all_players_espn_ids, season_year)
            

        #     # get matchup data before looping thru consistent streaks bc we will present matchup data alongside consistent streaks for comparison
        #     fantasy_pros_url = 'https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php' #'https://www.fantasypros.com/nba/defense-vs-position.php' #alt 2: betting_pros_url = 'https://www.bettingpros.com/nba/defense-vs-position/'
        #     hashtag_bball_url = 'https://hashtagbasketball.com/nba-defense-vs-position'
        #     swish_analytics_url = 'https://swishanalytics.com/optimus/nba/daily-fantasy-team-defensive-ranks-position'
        #     draft_edge_url = 'https://draftedge.com/nba-defense-vs-position/'


        #     # get matchup data for streaks to see if likely to continue streak
        #     matchup_data_sources = [fantasy_pros_url, hashtag_bball_url, swish_analytics_url] #, hashtag_bball_url, swish_analytics_url, betting_pros_url, draft_edge_url] # go thru each source so we can compare conflicts
        #     # first read all matchup data from internet and then loop through tables
        #     all_matchup_data = reader.read_all_matchup_data(matchup_data_sources) # all_matchup_data=[matchup_data1,..], where matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]




    irreg_play_time = settings['irreg play time']

    # === organize external data into internal structure



    #all_player_consistent_stats = {} # we want to display all player consistent stats together for viewing convenience and analysis comparison
    all_player_stat_records = {}
    all_player_stat_dicts = {} # {player:{year:...}}
    all_player_stat_probs = {} # for all stat vals so gets messy if same dict as other measures
    all_unit_stat_probs = {}

    all_player_weekly_stat_dicts = {} # {player:{week:...}}
    all_player_weekly_stat_records = {}
    all_player_weekly_stat_probs = {}
    all_weekly_unit_stat_probs = {}
    # if len(players_names) != 1:
    #     players_names = []
    #     # if not test single player
    #     for roster in teams_current_rosters.values():
    #         for player_name in roster:
    #             players_names.append(player_name)

    #for team, roster in teams_current_rosters.items():
    for player_name in players_names:
        player_name = player_name.lower()

        # see which prob results we already have saved 
        # so we dont have to read from internet and compute again
        # prob for each stat over and under
        # key_type = 'data/stat probs/' + player_name + ' prev probs.json'
        # init_player_stat_probs = reader.read_json(key_type)

        if player_name not in all_players_season_logs.keys():
            continue

        # init saved stats
        #print('all_players_season_logs: ' + str(all_players_season_logs))
        player_season_logs = all_players_season_logs[player_name]
    
        # get player position and team from premade fcns 
        # bc if we do not have saved locally it will read from internet
        player_position = all_players_positions[player_name]
        #print(player_name.title() + ' position: ' + player_position)

        player_teammates = all_players_teammates[player_name]
        # get player team so we can determine away/home team so we can determine teammates/opponents from players in games
        # we dont really need to get player team from internet here bc we already got all player teams in separate batch loop
        player_teams = all_players_teams[player_name]

        # stat dicts are kept in separate files bc big data
        init_player_stat_dict = reader.read_player_stat_dict(player_name, current_year_str, todays_date)

        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, todays_games_date_obj, all_box_scores, all_games_info, player_teams, current_year_str, game_teams=game_teams, init_player_stat_dict=init_player_stat_dict, find_players=find_players, player_position=player_position, player_teammates=player_teammates, rosters=teams_current_rosters, cur_season_part=season_part)
        all_player_stat_dicts[player_name] = player_stat_dict # save for later outside loop

        # same week number for each year, over all years
        player_weekly_stat_dict = generate_player_weekly_stat_dict(player_name, player_season_logs, todays_games_date_obj, all_box_scores, all_games_info, player_teams, current_year_str, game_teams=game_teams, init_player_stat_dict=init_player_stat_dict, find_players=find_players, player_position=player_position, player_teammates=player_teammates, rosters=teams_current_rosters, cur_season_part=season_part)
        all_player_weekly_stat_dicts[player_name] = player_weekly_stat_dict

        # gen all outcomes shows streaks
        # produces list of features to assess
        # much like the newer stat probs dict
        # player_all_outcomes_dict = generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position, all_matchup_data, all_box_scores, player_team, player_stat_dict, season_year=season_year) # each player has an outcome for each stat
        # player_outcomes[player_name] = player_all_outcomes_dict

        # generate stat val reached at desired consistency
        # this would be one of the key possible outcomes given a probability
        # the initial outcome we have done so far is prob of reaching either the projected line or avg stat val
        # determine the stat val with record above 90%
        # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
        player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        # no need for consistent stats if showing all available stats from most to least likely
        #player_consistent_stats = generate_consistent_stat_vals(player_name, player_stat_dict, player_stat_records)
        #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        #all_player_consistent_stats[player_name] = player_consistent_stats
        all_player_stat_records[player_name] = player_stat_records

        player_weekly_stat_records = generate_player_weekly_stat_records(player_name, player_weekly_stat_dict)
        all_player_weekly_stat_records[player_name] = player_weekly_stat_records

        # prob for each stat over and under
        player_stat_probs = generate_player_stat_probs(player_stat_records, player_name)
        all_player_stat_probs[player_name] = player_stat_probs

        player_weekly_stat_probs = generate_player_weekly_stat_probs(player_weekly_stat_records, player_name)
        all_player_weekly_stat_probs[player_name] = player_weekly_stat_probs

        # save player stat probs bc prev season stat probs unchanged
        # only need to overwrite if more prev seasons added
        # if init_player_stat_probs != player_stat_probs:
        #     filepath = ''
        #     write_param = ''
        #     writer.write_json_to_file(player_stat_probs, filepath, write_param)

        # gen all stat prob dicts adjusted to current minutes
        # bc abs vol prob of a sample with different minutes is not useful unless normalized minutes
        # could add in gen player stat probs so it is in all_player_stat_probs?
        # need player_season_logs for minutes
        # unit stat probs requires current mean minutes which changes with each game
        # so cannot be perm saved
        # can save init stat probs perm but do we even use it other than for ref?
        # even if just for ref still worth perm saving so not needed to compute each run
        # perm save stat dicts for prev years... 
        # OR init stat probs dicts with fractions showing sample size?
        # try just stat probs dicts bc already using for ref
        # but then see if we need prev stat dicts for anything else bc if so then need to perm save that too
        player_unit_stat_probs = generate_player_unit_stat_probs(player_stat_dict, player_name, player_season_logs)
        all_unit_stat_probs[player_name] = player_unit_stat_probs

        player_weekly_unit_stat_probs = generate_player_weekly_unit_stat_probs(player_weekly_stat_dict, player_name, player_season_logs)
        all_weekly_unit_stat_probs[player_name] = player_weekly_unit_stat_probs
        



    

    # each player gets a table separate sheet 
    # showing over and under probs for each stat val
    # val, prob over, prob under
    # 0, P_o0, P_u0
    # all_player_stat_probs = {player:condition:year:part:stat:val} = {'player': {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
    #writer.write_all_player_stat_probs(all_player_stat_probs)

    
    # now we want all players in a single table sorted by high to low prob
    # problem is many of the high probs wont be available so we need to iso available props
    # once we have odds, we need to sort by expected val bc some lower prob may be higher ev
    
    # currently we are not using other players stats to determine probability 
    # but we may eventually use other similar players to get more samples for current player
    # so need to get all player stats before getting all stat probs
    # all_stat_probs_dict = {player:stat:val:conditions}
    all_stat_probs_dict = generate_all_stat_probs_dict(all_player_stat_probs, all_player_stat_dicts, all_unit_stat_probs, season_years, irreg_play_time)
    
    # add true probs to stat probs dict
    # need to know current conditions to determine true prob
    # and also later we order spreadsheet based on current conditions used to get true prob
    # conditions such as prev val are player specific but most conditions are team specific
    # all_current_conditions = {p1:{out:[m fultz pg, j ingles sg, ...], loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
    all_current_conditions = generate_all_current_conditions(players_names, game_teams, all_players_teams, teams_current_rosters, find_players, current_year_str, all_teams_players) #determiner.determine_current_conditions() # [all, regular, home, ...]
    # all_cur_conds_lists = {p1:[m fultz pg out, j ingles sg out, away, ...],...}
    all_cur_conds_data = converter.convert_all_conditions_to_dicts(all_current_conditions, all_players_abbrevs, all_players_teams, all_box_scores, season_years, current_year_str)
    all_cur_conds_dicts = all_cur_conds_data[0]
    all_game_player_cur_conds = all_cur_conds_data[1]
    # condition: prev stat val
    # get from game log
    # diff for each stat
    #player_prev_vals = reader.read_player_prev_stat_vals(player_game_log)
    all_prev_vals = reader.read_all_prev_stat_vals(all_players_season_logs, season_year)
    all_true_probs_dict = generate_all_true_probs_dict(all_stat_probs_dict, all_player_stat_dicts, all_players_abbrevs, all_players_teams, teams_current_rosters, all_box_scores, all_cur_conds_dicts, all_game_player_cur_conds, all_prev_vals, season_years, current_year_str)
    
    # flatten nested dicts into one level and list them
    # all_stat_prob_dicts = [{player:player, stat:stat, val:val, conditions prob:prob,...},...]
    all_true_prob_dicts = generate_all_true_prob_dicts(all_true_probs_dict, all_players_teams, all_cur_conds_dicts, all_game_player_cur_conds, all_player_stat_dicts, game_teams, teams_current_rosters, current_year_str)
    desired_order = ['player', 'game', 'team', 'stat','val']
    #writer.list_dicts(all_stat_prob_dicts, desired_order)


    #all_consistent_stat_dicts = generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts, player_teams, season_year=season_year)
    #writer.display_consistent_stats(all_player_consistent_stats, all_player_stat_records)

    # now that we have all consistent stats,
    # see if each stat is available at a given value
    # also include given value in stat dict
    # so we can sort by value to get optimal return
    # need player id to read team
    desired_order.append('true prob')# = ['player', 'game', 'team', 'stat','val','true prob']
    available_prop_dicts = all_true_prob_dicts#all_consistent_stat_dicts
    read_odds = True
    if 'read odds' in settings.keys():
        read_odds = settings['read odds']
    if read_odds:
        available_prop_dicts = generate_available_prop_dicts(all_true_prob_dicts, game_teams, all_players_teams, current_year_str)
        desired_order.extend(['odds','ev']) # is there another way to ensure odds comes after true prob

    #desired_order = ['player', 'team', 'stat','ok val','ok val prob','odds','ok val post prob', 'ok val min margin', 'ok val post min margin', 'ok val mean margin', 'ok val post mean margin']
    
    # add ev to dicts
    # could also add ev same time as odds bc that is last needed var
    #available_prop_dicts = generate_ev_dicts(available_prop_dicts)

    sort_keys = ['true prob']
    available_prop_dicts = sorter.sort_dicts_by_keys(available_prop_dicts, sort_keys)
    #print('available_prop_dicts: ' + str(available_prop_dicts))

    # after odds and ev columns if included
    # prev val is unique type of condition
    desired_order.append('prev')

    # show the current conditions so we know which probs are used bc all probs are shown in table of all players
    #conditions = ['loc'] # add all conditions we are using to get true prob or uncertainty
    # all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
    # here we show conditions keys eg loc, out, ...
    conditions = list(list(all_current_conditions.values())[0].keys())
    desired_order.extend(conditions)

    # add columns in order of conditions used, by weight high to low
    # given current conditions used to determine true prob
    # take current conditions for each year
    # here we show conditions values eg away, b biyombo c out, ...
    # get season part from time of yr
    season_part = 'regular'
    # add condition prob titles to desired order after condition val columns showing the current cond vals
    conditions_order = generate_conditions_order(all_cur_conds_dicts, all_game_player_cur_conds, all_players_abbrevs, season_years, season_part)
    #conditions_order = ['m fultz pg out prob', 'all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
    desired_order.extend(conditions_order)
    #print('desired_order: ' + str(desired_order))
    #writer.list_dicts(available_prop_dicts, desired_order)#, output='excel')


    # strategy 1: high prob +ev (balance prob with ev)
    # 1. iso tru prob >= 90
    # 1.1 show tru prob >= 90 & prev_val < stat+ or prev_val > stat-
    # 2. iso +ev
    # 3. out of remaining options, sort by ev
    # 4. iso top x remaining options
    # 5. sort by game and team and stat
    # 6. see if any invalid single bets (only 1 good option for that game)
    # 7. replace invalid bets with next best valid ev

    # strategy 2: highest +ev
    # strategy 3: highest prob
    # strategy 4: combine +ev picks into multiple ~+100 parlays
    
    prop_table_data = generate_prop_table_data(available_prop_dicts, desired_order)

    prop_tables = prop_table_data[0]
    sheet_names = prop_table_data[1]
    
    

    #writer.list_dicts(s1_props, desired_order)


    # todo: make fcn to classify recently broken streaks bc that recent game may be anomaly and they may revert back to streak
    # todo: to fully predict current player stats, must predict teammate and opponent stats and prioritize and align with totals
    #print('final prop_tables: ' + str(prop_tables))
    #print('sheet_names: ' + str(sheet_names))
    writer.write_prop_tables(prop_tables, sheet_names, desired_order, todays_date)

    # pass player outcomes to another fcn to compute cumulative joint prob and ev?
    # do we need to return anything? we can always return whatever the final print is
    #player_outcomes = prop_tables
    #print('players_outcomes: ' + str(players_outcomes))
    return players_outcomes
