# player-probability-determiner.py
# determine the probability that a player will perform an action

import reader # input data
import numpy # mean, median
import scipy
from scipy import stats # calculate mode
from tabulate import tabulate # display output
import isolator # isolate player game data which exludes headers and monthly averages
import re # split result data into score data
import determiner # determine consistent streak

from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart
from datetime import timedelta

import pandas as pd # see when was prev game

# input: game log
# player name
# date, opponent, result, min, fg, fg%, 3pt, 3p%, ft, ft%, reb, ast, blk, stl, pf, to, pts

data_type = 'Player Data'
player_name = 'Ja Morant'
# count no. times player hit over line
pts_line = 1
r_line = 3
a_line = 1

#print("\n===" + player_name + "===\n")
#row1 = ['Tue 2/7','vs OKC','L 133-130', '34','13-20','65.0','4-6','66.7','8-10','80.0','7','3','0','3','3','4','38']

#all_player_game_logs = []
#all_player_game_logs_dict = {}
#all_player_season_logs_dict = {}


player_names = ['Julius Randle', 'Jalen Brunson', 'RJ Barrett', 'Demar Derozan', 'Paolo Banchero', 'Zach Lavine', 'Franz Wagner', 'Nikola Vucevic', 'Wendell Carter Jr', 'Ayo Dosunmu', 'Markelle Fultz', 'Patrick Williams', 'Brandon Ingram', 'Shai Gilgeous Alexander', 'CJ Mccollum', 'Josh Giddey', 'Trey Murphy III', 'Jalen Williams', 'Herbert Jones', 'Anthony Edwards', 'Luka Doncic', 'Rudy Gobert', 'Kyrie Irving', 'Mike Conley', 'Jaden Mcdaniels', 'Jordan Poole', 'Klay Thompson', 'Draymond Green', 'Kevon Looney','Gary Harris'] #['Bojan Bogdanovic', 'Jaden Ivey', 'Killian Hayes', 'Pascal Siakam', 'Fred Vanvleet', 'Gary Trent Jr', 'Scottie Barnes', 'Isaiah Stewart', 'Jalen Duren', 'Chris Boucher'] #['Ja Morant', 'Desmond Bane', 'Jaren Jackson Jr', 'Dillon Brooks', 'Jayson Tatum', 'Derrick White', 'Robert Williams', 'Malcolm Brogdon', 'Al Horford', 'Xavier Tillman', 'Brandon Clarke']
pts_lines = [25,25,19,23,19,24,16,19,15,9,14,11,31,18,13,28,33,14,25,11,11,26,26,9,7,10] #[22, 16, 13, 25, 22, 20, 17, 12, 11, 10] #[28, 21, 16, 13, 33, 18, 10, 15, 9, 8, 10]
r_lines = [10,4,5,5,7,5,2,12,8,2,4,5,2,5,2,8,2,2,2,6,9,11,4,3,4,2,2,8,9,2] #[4, 4, 3, 7, 4, 3, 7, 9, 10, 6] #[7, 5, 7, 3, 9, 5, 10, 5, 6, 7, 6]
a_lines = [2,6,2,5,2,4,2,2,3,2,6,2,2,6,2,6,2,3,2,2,7,2,6,6,2,5,3,7,2,2] #[3, 6, 7, 6, 7, 2, 5, 2, 2, 2] #[8, 4, 2, 2, 6, 6, 2, 4, 3, 2, 2]
threes_lines = [3,1,1,1,1,3,2,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,5,1,1,2]
b_lines = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
s_lines = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
to_lines = [3,1,1,1,3,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1]

data_type = "Game Lines"
todays_games_date = '2/21/23'
todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
input_type = ''#'2_17' # date as mth_day
projected_lines = reader.extract_data(data_type, input_type, header=True)
if input_type == '': # for testing we make input type blank ''
#projected_lines = reader.read_projected_lines(date)
    projected_lines = [['Name', 'PTS', 'REB', 'AST', '3PT', 'BLK', 'STL', 'TO','LOC','OPP'], ['Giannis Antetokounmpo', '34', '13', '6', '1', '1', '1', '1', 'Home', 'ATL']]
print("projected_lines: " + str(projected_lines))

projected_lines_dict = {}
player_lines_dict = {}
header_row = projected_lines[0]
for player_lines in projected_lines[1:]:
    player_name = player_lines[0]
    projected_lines_dict[player_name] = dict(zip(header_row[1:],player_lines[1:]))
print("projected_lines_dict: " + str(projected_lines_dict))

player_names = isolator.isolate_data_field("name",projected_lines)
pts_lines = isolator.isolate_data_field("pts",projected_lines)
r_lines = isolator.isolate_data_field("reb",projected_lines)
a_lines = isolator.isolate_data_field("ast",projected_lines)
threes_lines = isolator.isolate_data_field("3",projected_lines)
#print("threes_lines: " + str(threes_lines))
b_lines = isolator.isolate_data_field("blk",projected_lines)
#print("b_lines: " + str(b_lines))
s_lines = isolator.isolate_data_field("stl",projected_lines)
to_lines = isolator.isolate_data_field("to",projected_lines)
locations = isolator.isolate_data_field("loc",projected_lines) # home/away
opponents = isolator.isolate_data_field("opp",projected_lines) # format OKC



# get all player season logs
all_player_season_logs_dict = reader.read_all_players_season_logs(player_names)


# for p_name in player_names:

#     # player_season_logs = reader.read_player_season_logs(p_name) # list of game logs for each season played by p_name
#     # all_player_season_logs_dict[p_name] = player_season_logs


#     player_game_log = reader.read_player_season_log(p_name) # construct player url from name

#     all_player_game_logs.append(player_game_log) # could continue to process in this loop or save all player game logs to process in next loop

#     #all_player_game_logs_dict[p_name] = player_game_log


print("\n===All Players===\n")

#player_game_log = all_player_game_logs[0] # init
# player game log from espn, for 1 season or all seasons

for player_name, player_season_logs in all_player_season_logs_dict.items():
#for player_idx in range(len(all_player_game_logs)):
    player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
    #player_name = player_names[player_idx] # player names must be aligned with player game logs

    all_pts_dicts = { 'all':{}, 'home':{}, 'away':{} }
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
        season_year = '23'
        print("player_game_log:\n" + str(player_game_log))
        # we pulled game log from internet

        opponent = projected_lines_dict[player_name]['OPP'].lower() # collect data against opponent to see previous matchups
        
        # first loop thru all regular season games, then thru subset of games such as home/away
        # or just append to subset array predefined such as all_home_pts = []
        next_game_date_obj = datetime.today() # need to see if back to back games 1 day apart
        
        for game_idx, row in player_game_log.iterrows():
            
            #game = player_game_log[game_idx, row]
            #print("game:\n" + str(game))
            #print("player_game_log.loc[game_idx, 'Type']: " + player_game_log.loc[game_idx, 'Type'])

            if re.search('\\*',player_game_log.loc[game_idx, 'OPP']): # all star stats not included in regular season stats
                #print("game excluded")
                continue
            
            if player_game_log.loc[game_idx, 'Type'] == 'Regular':
                #print("Current Game Num: " + str(game_idx))

                
                

                pts = int(player_game_log.loc[game_idx, 'PTS'])
                rebs = int(player_game_log.loc[game_idx, 'REB'])
                asts = int(player_game_log.loc[game_idx, 'AST'])

                results = player_game_log.loc[game_idx, 'Result']
                #print("results: " + results)
                results = re.sub('[a-zA-Z]', '', results)
                # remove #OT from result string
                results = re.split("\\s+", results)[0]
                #print("results_data: " + str(results_data))
                score_data = results.split('-')
                #print("score_data: " + str(score_data))
                winning_score = int(score_data[0])
                losing_score = int(score_data[1])

                minutes = int(player_game_log.loc[game_idx, 'MIN'])

                fgs = player_game_log.loc[game_idx, 'FG']
                fg_data = fgs.split('-')
                fgm = int(fg_data[0])
                fga = int(fg_data[1])
                fg_rate = round(float(player_game_log.loc[game_idx, 'FG%']), 1)

                #threes = game[three_idx]
                #threes_data = threes.split('-')
                #print("threes_data: " + str(threes_data))
                threes_made = int(player_game_log.loc[game_idx, '3PT_SA'])
                threes_attempts = int(player_game_log.loc[game_idx, '3PT_A'])
                three_rate = round(float(player_game_log.loc[game_idx, '3P%']), 1)

                fts = player_game_log.loc[game_idx, 'FT']
                ft_data = fts.split('-')
                ftm = int(ft_data[0])
                fta = int(ft_data[1])
                ft_rate = round(float(player_game_log.loc[game_idx, 'FT%']), 1)

                bs = int(player_game_log.loc[game_idx, 'BLK'])
                ss = int(player_game_log.loc[game_idx, 'STL'])
                fs = int(player_game_log.loc[game_idx, 'PF'])
                tos = int(player_game_log.loc[game_idx, 'TO'])

                game_stats = [pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] # make list to loop through so we can add all stats to dicts with 1 fcn

                # now that we have game stats add them to dict

                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    stat_dict['all'][game_idx] = stat

                if re.search('vs',player_game_log.loc[game_idx, 'OPP']):

                    for stat_idx in range(len(all_stats_dicts.values())):
                        stat_dict = list(all_stats_dicts.values())[stat_idx]
                        stat = game_stats[stat_idx]
                        stat_dict['home'][game_idx] = stat

                    
                else: # if not home then away
                    for stat_idx in range(len(all_stats_dicts.values())):
                        stat_dict = list(all_stats_dicts.values())[stat_idx]
                        stat = game_stats[stat_idx]
                        stat_dict['away'][game_idx] = stat

                    

                # matchup against opponent
                if re.search(opponent,player_game_log.loc[game_idx, 'OPP'].lower()):

                    for stat_idx in range(len(all_stats_dicts.values())):
                        stat_dict = list(all_stats_dicts.values())[stat_idx]
                        stat = game_stats[stat_idx]
                        if not opponent in stat_dict.keys():
                            stat_dict[opponent] = {}
                        stat_dict[opponent][game_idx] = stat

                    


                # see if this game is 1st or 2nd night of back to back bc we want to see if pattern for those conditions
                init_game_date_string = player_game_log.loc[game_idx, 'Date'].lower().split()[1] # 'wed 2/15'
                game_mth = init_game_date_string.split('/')[0]
                final_season_year = season_year
                if int(game_mth) in range(10,13):
                    final_season_year = str(int(season_year) - 1)
                game_date_string = init_game_date_string + "/" + final_season_year
                #print("game_date_string: " + str(game_date_string))
                game_date_obj = datetime.strptime(game_date_string, '%m/%d/%y')
                #print("game_date_obj: " + str(game_date_obj))

                # if current loop is most recent game (idx 0) then today's game is the next game
                if game_idx == 0: # see how many days after prev game is date of today's projected lines
                    # already defined or passed todays_games_date_obj
                    # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
                    # print("todays_games_date_obj: " + str(todays_games_date_obj))
                    next_game_date_obj = todays_games_date_obj # today's game is the next game relative to the previous game
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

                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not days_before_next_game in stat_dict.keys():
                        stat_dict[days_before_next_game] = {}
                    stat_dict[days_before_next_game][game_idx] = stat

                init_prev_game_date_string = player_game_log.loc[game_idx+1, 'Date'].lower().split()[1]
                prev_game_mth = init_prev_game_date_string.split('/')[0]
                final_season_year = season_year
                if int(prev_game_mth) in range(10,13):
                    final_season_year = str(int(season_year) - 1)
                prev_game_date_string = init_prev_game_date_string + "/" + final_season_year
                #print("prev_game_date_string: " + str(prev_game_date_string))
                prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%y')
                #print("prev_game_date_obj: " + str(prev_game_date_obj))

                days_after_prev_game_int = (game_date_obj - prev_game_date_obj).days
                days_after_prev_game = str(days_after_prev_game_int) + ' after'
                #print("days_after_prev_game: " + days_after_prev_game)

                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not days_after_prev_game in stat_dict.keys():
                        stat_dict[days_after_prev_game] = {}
                    stat_dict[days_after_prev_game][game_idx] = stat

                

                next_game_date_obj = game_date_obj # next game bc we loop from most to least recent
                    

    else:
        # if getting data from file
        player_season_log = reader.read_season_log_from_file(data_type, player_name, 'tsv')


    # no matter how we read data, we should have filled all_pts list
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
        all_streak_tables = { } # { 'player name': { 'all': [], 'home':[], 'away':[] } }

        # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
        #print("all_pts_dict: " + str(all_pts_dict))
        print("all_pts_dicts: " + str(all_pts_dicts))
        # all_pts_dicts = {'all':{1:20}}
        # key=condition, val={idx:stat}

        
        #compute stats from data
        # key represents set of conditions of interest eg home/away
        for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

            # reset for each set of conditions
            header_row = ['Output']
            stat_means = ['Mean'] #{pts:'',reb...}
            stat_medians = ['Median']
            stat_modes = ['Mode']
            stat_mins = ['Min']
            stat_maxes = ['Max']

            for stat_key, stat_dict in all_stats_dicts.items(): # stat key eg pts

                header_row.append(stat_key.upper())

                stat_vals = list(stat_dict[conditions].values())
                #print("stat_vals: " + str(stat_vals))

                stat_mean = round(numpy.mean(stat_vals), 1)
                stat_median = int(numpy.median(stat_vals))
                stat_mode = stats.mode(stat_vals, keepdims=False)[0]
                stat_min = numpy.min(stat_vals)
                stat_max = numpy.max(stat_vals)

                stat_means.append(stat_mean)
                stat_medians.append(stat_median)
                stat_modes.append(stat_mode)
                stat_mins.append(stat_min)
                stat_maxes.append(stat_max)

            output_table = [header_row, stat_means, stat_medians, stat_modes, stat_mins, stat_maxes]

            output_title = str(conditions).title()
            if re.search('before',conditions):
                output_title = re.sub('Before','days before next game', output_title).title()
            elif re.search('after',conditions):
                output_title = re.sub('After','days after previous game', output_title).title()
            

            print(output_title)
            print(tabulate(output_table))



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

                player_projected_lines = projected_lines_dict[player_name]
                if pts >= int(player_projected_lines['PTS']):
                    pts_count += 1
                if rebs >= int(player_projected_lines['REB']):
                    r_count += 1
                if asts >= int(player_projected_lines['AST']):
                    a_count += 1

                if threes >= int(player_projected_lines['3PT']):
                    threes_count += 1
                if blks >= int(player_projected_lines['BLK']):
                    b_count += 1
                if stls >= int(player_projected_lines['STL']):
                    s_count += 1
                if tos >= int(player_projected_lines['TO']):
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
            over_pts_line = 'PTS ' + str(player_projected_lines['PTS']) + "+"
            over_rebs_line = 'REB ' + str(player_projected_lines['REB']) + "+"
            over_asts_line = 'AST ' + str(player_projected_lines['AST']) + "+"
            
            over_threes_line = '3P ' + str(player_projected_lines['3PT']) + "+"
            over_blks_line = 'BLK ' + str(player_projected_lines['BLK']) + "+"
            over_stls_line = 'STL ' + str(player_projected_lines['STL']) + "+"
            over_tos_line = 'TO ' + str(player_projected_lines['TO']) + "+"
            
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

            game_num_header = 'Games Ago'
            game_num_row = [game_num_header]
            game_day_header = 'DoW'
            game_day_row = [game_day_header]
            game_date_header = 'Date'
            game_date_row = [game_date_header]

            for game_num in all_pts_dicts[conditions].keys():
                #game_num = all_pts_dicts[key]
                game_num_row.append(game_num)
                game_day_date = player_game_log.loc[game_num,'Date']
                game_day = game_day_date.split()[0]
                game_day_row.append(game_day)
                game_date = game_day_date.split()[1]
                game_date_row.append(game_date)
            

            #total = str(len(all_pts))
            #probability_over_line = str(count) + "/" + total
            #total_games = total + " Games"
            #header_row = ['Points', total_games]
            #print(probability_over_line)

            #prob_row = [over_line, probability_over_line]

            print("\n===" + player_name + "===\n")

            game_num_table = [game_num_row, game_day_row, game_date_row]
            print(tabulate(game_num_table))

            prob_pts_table = [prob_pts_row]
            print(tabulate(prob_pts_table))

            prob_rebs_table = [prob_rebs_row]
            print(tabulate(prob_rebs_table))

            prob_asts_table = [prob_asts_row]
            print(tabulate(prob_asts_table))

            prob_threes_table = [prob_threes_row]
            print(tabulate(prob_threes_table))

            prob_blks_table = [prob_blks_row]
            print(tabulate(prob_blks_table))

            prob_stls_table = [prob_stls_row]
            print(tabulate(prob_stls_table))

            prob_tos_table = [prob_tos_row]
            print(tabulate(prob_tos_table))


            all_prob_stat_tables = [prob_pts_table, prob_rebs_table, prob_asts_table, prob_threes_table, prob_blks_table, prob_stls_table, prob_tos_table]

            for stat_idx in range(len(stats_counts)):
                stat_counts = stats_counts[stat_idx]
                prob_table = all_prob_stat_tables[stat_idx][0] # only need first element bc previously formatted for table display
                if determiner.determine_consistent_streak(stat_counts):
                    if player_name in all_streak_tables.keys():
                        player_streak_tables = all_streak_tables[player_name]
                        if conditions in player_streak_tables.keys():
                            player_streak_tables[conditions].append(prob_table) # append all stats for given key
                        else:
                            player_streak_tables[conditions] = [prob_table]
                    else:
                        all_streak_tables[player_name] = {}
                        player_streak_tables = all_streak_tables[player_name]
                        player_streak_tables[conditions] = [prob_table]

                    # if key in player_streak_tables.keys():
                    #     player_streak_tables[key].append(prob_table) # append all stats for given key
                    # else:
                    #     player_streak_tables[key] = [prob_table]

        # header_row = ['Output']
        # for stat_key, stat_dict in all_stats_dicts.items():
        #     print("stat_dict: " + str(stat_dict)) # stat_dict = {idx:val}

        #     header_row.append(stat_key.upper())

        #     stat_means = {} #{pts:'',reb...}
        #     stat_medians = {}
        #     stat_modes = {}
        #     stat_mins = {}
        #     stat_maxes = {}

        #     for key, val in stat_dict.items():
        #         #print("val: " + str(val))
        #         #print("val.values(): " + str(val.values()))
        #         stat_vals = list(val.values())

        #         stat_mean = round(numpy.mean(stat_vals), 1)
        #         stat_median = int(numpy.median(stat_vals))
        #         stat_mode = stats.mode(stat_vals, keepdims=False)[0]
        #         stat_min = numpy.min(stat_vals)
        #         stat_max = numpy.max(stat_vals)
                
        #         stat_means.append(stat_mean)
        #         stat_medians.append(stat_median)
        #         stat_modes.append(stat_mode)
        #         stat_mins.append(stat_min)
        #         stat_maxes.append(stat_max)

        #     for key, val in stat_dict.items():

        #         # all_pts_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_rebs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_asts_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_winning_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_losing_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_minutes_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_fgms_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_fgas_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_fg_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_threes_made_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_threes_attempts_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_threes_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_ftms_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_ftas_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_ft_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_bs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_ss_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_fs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        #         # all_tos_dicts = { 'all':{}, 'home':{}, 'away':{} }

        #         header_row = ['Output', 'PTS']
        #         output_table = [header_row, [stat_means[0]]]

        #         output_title = str(key).title()
        #         if re.search('before',key):
        #             output_title = re.sub('Before','days before next game', output_title).title()
        #         elif re.search('after',key):
        #             output_title = re.sub('After','days after previous game', output_title).title()
                

        #         print(output_title)
        #         print(tabulate(output_table))

        # key represents set of conditions of interest eg home/away
        # for key, val in all_pts_dicts.items():
        #     #print("val: " + str(val))
        #     #print("val.values(): " + str(val.values()))
        #     pts_mean = round(numpy.mean(list(val.values())), 1)
        #     pts_median = int(numpy.median(list(val.values())))
        #     pts_mode = stats.mode(list(val.values()), keepdims=False)[0]
        #     pts_min = numpy.min(list(val.values()))
        #     pts_max = numpy.max(list(val.values()))
            
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     rebs_mean = round(numpy.mean(values), 1)
        #     rebs_median = int(numpy.median(values))
        #     rebs_mode = stats.mode(values, keepdims=False)[0]
        #     rebs_min = numpy.min(values)
        #     rebs_max = numpy.max(values)

        #     val = all_asts_dicts[key]
        #     values = list(val.values())
        #     asts_mean = round(numpy.mean(values), 1)
        #     asts_median = int(numpy.median(values))
        #     asts_mode = stats.mode(values, keepdims=False)[0]
        #     asts_min = numpy.min(values)
        #     asts_max = numpy.max(values)

        #     val = all_winning_scores_dicts[key]
        #     values = list(val.values())
        #     winning_score_mean = round(numpy.mean(all_winning_scores_dict[key]), 1)
        #     winning_score_median = int(numpy.median(all_winning_scores_dict[key]))
        #     winning_score_mode = stats.mode(all_winning_scores_dict[key], keepdims=False)[0]
        #     winning_score_min = int(numpy.min(all_winning_scores_dict[key]))
        #     winning_score_max = int(numpy.max(all_winning_scores_dict[key]))
        #     val = all_losing_scores_dicts[key]
        #     values = list(val.values())
        #     losing_score_mean = round(numpy.mean(all_losing_scores_dict[key]), 1)
        #     losing_score_median = int(numpy.median(all_losing_scores_dict[key]))
        #     losing_score_mode = stats.mode(all_losing_scores_dict[key], keepdims=False)[0]
        #     losing_score_min = int(numpy.min(all_losing_scores_dict[key]))
        #     losing_score_max = int(numpy.max(all_losing_scores_dict[key]))

        #     result_mean = str(winning_score_mean) + "-" + str(losing_score_mean)
        #     result_median = str(winning_score_median) + "-" + str(losing_score_median)
        #     result_mode = str(winning_score_mode) + "-" + str(losing_score_mode)
        #     result_min = str(winning_score_min) + "-" + str(losing_score_min)
        #     result_max = str(winning_score_max) + "-" + str(losing_score_max)

        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     minutes_mean = round(numpy.mean(all_minutes_dict[key]), 1)
        #     minutes_median = int(numpy.median(all_minutes_dict[key]))
        #     minutes_mode = stats.mode(all_minutes_dict[key], keepdims=False)[0]
        #     minutes_min = int(numpy.min(all_minutes_dict[key]))
        #     minutes_max = int(numpy.max(all_minutes_dict[key]))
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     fgm_mean = round(numpy.mean(all_fgms_dict[key]), 1)
        #     fgm_median = int(numpy.median(all_fgms_dict[key]))
        #     fgm_mode = stats.mode(all_fgms_dict[key], keepdims=False)[0]
        #     fgm_min = numpy.min(all_fgms_dict[key])
        #     fgm_max = numpy.max(all_fgms_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     fga_mean = round(numpy.mean(all_fgas_dict[key]), 1)
        #     fga_median = int(numpy.median(all_fgas_dict[key]))
        #     fga_mode = stats.mode(all_fgas_dict[key], keepdims=False)[0]
        #     fga_min = numpy.min(all_fgas_dict[key])
        #     fga_max = numpy.max(all_fgas_dict[key])

        #     fg_mean = str(fgm_mean) + "-" + str(fga_mean)
        #     fg_median = str(fgm_median) + "-" + str(fga_median)
        #     fg_mode = str(fgm_mode) + "-" + str(fga_mode)
        #     fg_min = str(fgm_min) + "-" + str(fga_min)
        #     fg_max = str(fgm_max) + "-" + str(fga_max)
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     fg_rate_mean = round(numpy.mean(all_fg_rates_dict[key]), 1)
        #     fg_rate_median = round(float(numpy.median(all_fg_rates_dict[key])), 1)
        #     fg_rate_mode = stats.mode(all_fg_rates_dict[key], keepdims=False)[0]
        #     fg_rate_min = numpy.min(all_fg_rates_dict[key])
        #     fg_rate_max = numpy.max(all_fg_rates_dict[key])


        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     threes_made_mean = round(numpy.mean(all_threes_made_dict[key]), 1)
        #     threes_made_median = int(numpy.median(all_threes_made_dict[key]))
        #     threes_made_mode = stats.mode(all_threes_made_dict[key], keepdims=False)[0]
        #     threes_made_min = numpy.min(all_threes_made_dict[key])
        #     threes_made_max = numpy.max(all_threes_made_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     threes_attempts_mean = round(numpy.mean(all_threes_attempts_dict[key]), 1)
        #     threes_attempts_median = int(numpy.median(all_threes_attempts_dict[key]))
        #     threes_attempts_mode = stats.mode(all_threes_attempts_dict[key], keepdims=False)[0]
        #     threes_attempts_min = numpy.min(all_threes_attempts_dict[key])
        #     threes_attempts_max = numpy.max(all_threes_attempts_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     threes_mean = str(threes_made_mean) + "-" + str(threes_attempts_mean)
        #     threes_median = str(threes_made_median) + "-" + str(threes_attempts_median)
        #     threes_mode = str(threes_made_mode) + "-" + str(threes_attempts_mode)
        #     threes_min = str(threes_made_min) + "-" + str(threes_attempts_min)
        #     threes_max = str(threes_made_max) + "-" + str(threes_attempts_max)

        #     threes_rate_mean = round(numpy.mean(all_threes_rates_dict[key]), 1)
        #     threes_rate_median = round(float(numpy.median(all_threes_rates_dict[key])), 1)
        #     threes_rate_mode = stats.mode(all_threes_rates_dict[key], keepdims=False)[0]
        #     threes_rate_min = numpy.min(all_threes_rates_dict[key])
        #     threes_rate_max = numpy.max(all_threes_rates_dict[key])


        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     ftm_mean = round(numpy.mean(all_ftms_dict[key]), 1)
        #     ftm_median = int(numpy.median(all_ftms_dict[key]))
        #     ftm_mode = stats.mode(all_ftms_dict[key], keepdims=False)[0]
        #     ftm_min = numpy.min(all_ftms_dict[key])
        #     ftm_max = numpy.max(all_ftms_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     fta_mean = round(numpy.mean(all_ftas_dict[key]), 1)
        #     fta_median = int(numpy.median(all_ftas_dict[key]))
        #     fta_mode = stats.mode(all_ftas_dict[key], keepdims=False)[0]
        #     fta_min = numpy.min(all_ftas_dict[key])
        #     fta_max = numpy.max(all_ftas_dict[key])

        #     ft_mean = str(ftm_mean) + "-" + str(fta_mean)
        #     ft_median = str(ftm_median) + "-" + str(fta_median)
        #     ft_mode = str(ftm_mode) + "-" + str(fta_mode)
        #     ft_min = str(ftm_min) + "-" + str(fta_min)
        #     ft_max = str(ftm_max) + "-" + str(fta_max)
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     ft_rate_mean = round(numpy.mean(all_ft_rates_dict[key]), 1)
        #     ft_rate_median = round(float(numpy.median(all_ft_rates_dict[key])), 1)
        #     ft_rate_mode = stats.mode(all_ft_rates_dict[key], keepdims=False)[0]
        #     ft_rate_min = numpy.min(all_ft_rates_dict[key])
        #     ft_rate_max = numpy.max(all_ft_rates_dict[key])


        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     b_mean = round(numpy.mean(all_bs_dict[key]), 1)
        #     b_median = int(numpy.median(all_bs_dict[key]))
        #     b_mode = stats.mode(all_bs_dict[key], keepdims=False)[0]
        #     b_min = numpy.min(all_bs_dict[key])
        #     b_max = numpy.max(all_bs_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     s_mean = round(numpy.mean(all_ss_dict[key]), 1)
        #     s_median = int(numpy.median(all_ss_dict[key]))
        #     s_mode = stats.mode(all_ss_dict[key], keepdims=False)[0]
        #     s_min = numpy.min(all_ss_dict[key])
        #     s_max = numpy.max(all_ss_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     f_mean = round(numpy.mean(all_fs_dict[key]), 1)
        #     f_median = int(numpy.median(all_fs_dict[key]))
        #     f_mode = stats.mode(all_fs_dict[key], keepdims=False)[0]
        #     f_min = numpy.min(all_fs_dict[key])
        #     f_max = numpy.max(all_fs_dict[key])
        #     val = all_rebs_dicts[key]
        #     values = list(val.values())
        #     to_mean = round(numpy.mean(all_tos_dict[key]), 1)
        #     to_median = int(numpy.median(all_tos_dict[key]))
        #     to_mode = stats.mode(all_tos_dict[key], keepdims=False)[0]
        #     to_min = numpy.min(all_tos_dict[key])
        #     to_max = numpy.max(all_tos_dict[key])

            # p(a|b) = p(b|a)p(a)/p(b)
            # a = player does action, 
            # b = player did action in previous x/y instances, where x is no. times did action and y is no. opportunities to do action
            # eg if player was 3/3, 3/4, 4/5 then the next move he always goes 4/4, 4/5, 5/6 but this is misleading bc must account for external environmental factors

            # output: 
            # 1, 2, 3, ... 30 ... 82 (total games played)
            # 1/1, 2/2, 3/3, ..., 10/30, 30/82
            # mean, median, mode
            # get for all games, just winning games, just losing, just home/away, given opp, given set of circumstances, etc

            #header_row = ["Result"]
            #header_row.append(player_data[0][2:])

            #header_row = ['Output', 'Result', 'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS']

        
            
            #output_row = [field_name]
            # mean_row = ["Mean", result_mean, minutes_mean, fg_mean, fg_rate_mean, threes_mean, threes_rate_mean, ft_mean, ft_rate_mean, rebs_mean, asts_mean, b_mean, s_mean, f_mean, to_mean, pts_mean]
            # median_row = ["Median", result_median, minutes_median, fg_median, fg_rate_median, threes_median, threes_rate_median, ft_median, ft_rate_median, rebs_median, asts_median, b_median, s_median, f_median, to_median, pts_median]
            # mode_row = ["Mode", result_mode, minutes_mode, fg_mode, fg_rate_mode, threes_mode, threes_rate_mode, ft_mode, ft_rate_mode, rebs_mode, asts_mode, b_mode, s_mode, f_mode, to_mode, pts_mode]
            # min_row = ["Min", result_min, minutes_min, fg_min, fg_rate_min, threes_min, threes_rate_min, ft_min, ft_rate_min, rebs_min, asts_min, b_min, s_min, f_min, to_min, pts_min]
            # max_row = ["Max", result_max, minutes_max, fg_max, fg_rate_max, threes_max, threes_rate_max, ft_max, ft_rate_max, rebs_max, asts_max, b_max, s_max, f_max, to_max, pts_max]
            
            # for stat_idx in range(len(stat_means)):
            #     stat_mean = stat_means[stat_idx]
            #     stat_median = stat_medians[stat_idx]
            #     stat_mode = stat_modes[stat_idx]
            #     stat_min = stat_mins[stat_idx]
            #     stat_max = stat_maxes[stat_idx]

            #     mean_row.append(stat_mean)
            #     median_row.append(stat_median)
            #     mode_row.append(stat_mode)
            #     min_row.append(stat_min)
            #     max_row.append(stat_max)
            
            #header_row = ["Output"] + player_data[0][2:]
            # output_table = [header_row, mean_row, median_row, mode_row, min_row, max_row]

            # output_title = str(key).title()
            # if re.search('before',key):
            #     output_title = re.sub('Before','days before next game', output_title).title()
            # elif re.search('after',key):
            #     output_title = re.sub('After','days after previous game', output_title).title()
            

            # print(output_title)
            # print(tabulate(output_table))

            # header_row = ['Points', 'All Season']
            # mean_row = ['Mean', pts_mean]
            # median_row = ['Median', pts_median]
            # mode_row = ['Mode', pts_mode]
            # output_table = [header_row, mean_row, median_row, mode_row]

            # print("\n===" + player_name + "===\n")
            # print(tabulate(output_table))

            # given how many of recent games we care about
            # later we will take subsection of games with certain settings like home/away
            # first we get all stats and then we can analyze subsections of stats
            # eg last 10 games
            
    
find_matchups = False
if find_matchups:
    print("\n===Find Matchups===\n")
    # get matchup data before looping thru consistent streaks bc we will present matchup data alongside consistent streaks for comparison
    fantasy_pros_url = 'https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php' #'https://www.fantasypros.com/nba/defense-vs-position.php' #alt 2: betting_pros_url = 'https://www.bettingpros.com/nba/defense-vs-position/'
    hashtag_bball_url = 'https://hashtagbasketball.com/nba-defense-vs-position'
    swish_analytics_url = 'https://swishanalytics.com/optimus/nba/daily-fantasy-team-defensive-ranks-position'
    draft_edge_url = 'https://draftedge.com/nba-defense-vs-position/'


    # get matchup data for streaks to see if likely to continue streak
    matchup_data_sources = [fantasy_pros_url, hashtag_bball_url, swish_analytics_url] #, hashtag_bball_url, swish_analytics_url, betting_pros_url, draft_edge_url] # go thru each source so we can compare conflicts
    # first read all matchup data from internet and then loop through tables
    all_matchup_data = reader.read_all_matchup_data(matchup_data_sources)


    # display streak tables separately
    # only pull matchup data for streaks bc too much uncertainty without streak, until we get ml to analyze full pattern
    #streaks = isolator.isolate_consistent_streaks(all_stats_counts_dict)

print("\n===Consistent Streaks===\n")

for p_name, p_streak_tables in all_streak_tables.items():
    print("\n===" + p_name + "===\n")

    # we need to get schedule to get next game date to see how many days until next game
    # but we can get prev game from player game log we already have
    # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
    # print("todays_games_date_obj: " + str(todays_games_date_obj))

    player_season_logs = all_player_season_logs_dict[p_name]
    current_season_log = player_season_logs[0]

    #player_game_log = all_player_game_logs_dict[p_name]
    prev_game_date_obj = determiner.determine_prev_game_date(current_season_log, season_year) # exclude all star and other special games
    # prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + season_year # eg 'wed 2/15' to '2/15/23'
    # prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%y')
    days_after_prev_game = (todays_games_date_obj - prev_game_date_obj).days
    print("days_after_prev_game: " + str(days_after_prev_game))

    for key, streak_tables in p_streak_tables.items():
        player_lines = projected_lines_dict[p_name]
        #print("player_lines: " + str(player_lines))

        opponent = player_lines['OPP'].lower()

       
        
        #days_before_next_game = 1
        if str(key) == 'all' or str(key) == player_lines['LOC'].lower() or str(key) == opponent or str(key) == str(days_after_prev_game) + ' after': # current conditions we are interested in
            print(str(key).title())
            
            print(tabulate(streak_tables))

            # determine matchup for opponent and stat. we need to see all position matchups to see relative ease
            # display matchup tables with consistent streaks (later look at easiest matchups for all current games, not just consistent streaks bc we may find an exploit)
            
            #print("streak_tables: " + str(streak_tables))
            if find_matchups:
                for streak in streak_tables:

                    print("\n===Matchups===\n")

                    print(streak)

                    stat = streak[0].split(' ')[0]#'pts'
                    #print("stat: " + stat)
                    #all_matchup_ratings = { 'all':{}, 'pg':{}, 'sg':{}, 'sf':{}, 'pf':{}, 'c':{} } # { 'pg': { 'values': [source1,source2,..], 'ranks': [source1,source2,..] }, 'sg': {}, ... }
                    #position_matchup_rating = { 'values':[], 'ranks':[] } # comparing results from different sources
                    current_matchup_data = determiner.determine_matchup_rating(opponent, stat, all_matchup_data) # first show matchups from easiest to hardest position for stat. 

                    #sources_results={values:[],ranks:[]}
                    
                    for pos, sources_results in current_matchup_data.items():
                        print("Position: " + pos.upper())

                        

                        matchup_table_header_row = ['Sources'] # [source1, source2, ..]
                        num_sources = len(sources_results['averages']) #len(source_vals)

                        for source_idx in range(num_sources):
                            source_num = source_idx + 1
                            source_header = 'Source ' + str(source_num)
                            matchup_table_header_row.append(source_header)

                        matchup_table = [matchup_table_header_row]
                        for result, source_vals in sources_results.items():
                            source_vals.insert(0, result.title())
                            matchup_table.append(source_vals)

                        #source_matchup_ratings={ source1: {positions:[], averages:[], ranks:[], avg_ranks:[]}, source2...}
                        avg_source_matchup_ratings = {} # so we can sort by average rank
                        source_matchup_ratings = {}


                        print(tabulate(matchup_table))

