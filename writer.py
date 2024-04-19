#writer.py
# display data

# === Standard External Libraries ===
import csv # save player and game espn ID's so we do not have to request each run

import json # for team players

import pandas as pd # write spreadsheets from lists to dataframes

from datetime import datetime # add date to filename

import numpy as np # mean, median to display over time
import re # see if string contains stat and player of interest to display

from tabulate import tabulate # display output, eg consistent stat vals


#import determiner # determine matching key
#import sorter # sort players outcomes so we see conditions grouped by type and other useful visuals

import converter # convert dicts to lists
import remover

def display_game_data(all_valid_streaks_list):
    #print("\n===Game Data===\n")
    # all_player_pre_dicts = [{'prediction':val,'overall record':[],..},{},..]
    # get headers
    # header_row = ['Prediction']
    # for pre_dict in all_player_pre_dicts.values():
    #     for key in pre_dict:
    #         header_row.append(key.title())
    #     break
    # game_data = [header_row]

    # print("all_player_pre_dicts: " + str(all_player_pre_dicts))
    # for prediction, pre_dict in all_player_pre_dicts.items():
    #     prediction_row = [prediction]
    #     for val in pre_dict.values():
    #         prediction_row.append(val)
    #     game_data.append(prediction_row)



    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(all_valid_streaks_list) > 0:
        streak1 = all_valid_streaks_list[0]
        for key in streak1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        game_data = [header_row]
        game_data_strings = []
        for streak in all_valid_streaks_list:
            streak_row = []
            streak_string = ''
            for val in streak.values():
                streak_row.append(val)
                streak_string += str(val) + ";"
            game_data.append(streak_row)
            game_data_strings.append(streak_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    #print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)



def display_stat_plot(all_valid_streaks_list, all_players_stats_dicts, stat_of_interest, player_of_interest, season_year=2024):
    #print('\n===Plot Stats===\n')
    #Three lines to make our compiler able to draw:
    import matplotlib.pyplot as plt

    #display player stat values so we can see plot
    #columns: game num, stat val, over average record
    #print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    for valid_streak in all_valid_streaks_list:

        
        
        if re.search(stat_of_interest, valid_streak['prediction'].lower()) and re.search(player_of_interest, valid_streak['prediction'].lower()):

            #print('valid_streak: ' + str(valid_streak))
            player_name = ' '.join(valid_streak['prediction'].split()[:-2]).lower() # anthony davis 12+ pts
            #print("player_name from prediction: " + player_name)

            stat_name = valid_streak['prediction'].split()[-1].lower()
            condition = 'all'
            #season_year = 2023
            stat_vals_dict = all_players_stats_dicts[player_name][season_year][stat_name][condition]
            #print('stat_vals_dict: ' + str(stat_vals_dict))

            game_nums = list(stat_vals_dict.keys())
            #print('game_nums: ' + str(game_nums))
            stat_vals = list(stat_vals_dict.values())
            stat_vals.reverse()
            #print('stat_vals: ' + str(stat_vals))

            stat_line = int(valid_streak['prediction'].split()[-2][:-1])
            #print('stat_line: ' + str(stat_line))

            plot_stat_line = [stat_line] * len(game_nums)
            #print('plot_stat_line: ' + str(plot_stat_line))

            # x = np.array(game_nums)
            # y = np.array(stat_vals)

            plt.plot(game_nums, stat_vals, label = "Stat Vals") # reverse bc input from recent to distant but we plot left to right
            plt.plot(game_nums, plot_stat_line,  label = "Stat Line")

            # also plot avg over time to compare trend of avg
            # bc just seeing season avg is barely useful almost useless unless we see either avg in last few games (and multiple subset) or we can simply see if avg is increasing or decreasing
            # the avg for the first game must be based on previous seasons
            # but for now arbitrary number
            #init_mean_stat_val
            prev_stat_vals = []
            mean_stat_vals = [] # how mean changes over time
            past_ten_stat_vals = []
            past_ten_mean_stat_vals = [] # mean over last 10 games to get more recent relevant picture
            past_three_stat_vals = []
            past_three_mean_stat_vals = []
            for stat_val_idx in range(len(stat_vals)):
                stat_val = stat_vals[stat_val_idx]
                #print('prev_stat_vals: ' + str(prev_stat_vals))
                #print('past_ten_stat_vals: ' + str(past_ten_stat_vals))
                # compute avg of this and previous vals
                if stat_val_idx == 0:
                    mean_stat_val = stat_val
                    past_ten_mean_stat_val = stat_val
                    past_three_mean_stat_val = stat_val

                else:
                    mean_stat_val = converter.round_half_up(np.mean(np.array(prev_stat_vals)), 1)
                    #print('mean_stat_val: ' + str(mean_stat_val))
                    past_ten_mean_stat_val = converter.round_half_up(np.mean(np.array(past_ten_stat_vals)), 1)
                    #print('past_ten_mean_stat_val: ' + str(past_ten_mean_stat_val))
                    past_three_mean_stat_val = converter.round_half_up(np.mean(np.array(past_three_stat_vals)), 1)
                    #print('past_three_mean_stat_val: ' + str(past_three_mean_stat_val))

                mean_stat_vals.append(mean_stat_val)
                past_ten_mean_stat_vals.append(past_ten_mean_stat_val)
                past_three_mean_stat_vals.append(past_three_mean_stat_val)

                prev_stat_vals.append(stat_val)

                if stat_val_idx < 10: # add vals to list until we reach 10 bc we only want past 10 games
                    past_ten_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_ten_stat_vals.pop(0)
                    past_ten_stat_vals.append(stat_val)
                if stat_val_idx < 3: # add vals to list until we reach 10 bc we only want past 10 games
                    past_three_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_three_stat_vals.pop(0)
                    past_three_stat_vals.append(stat_val)
                

            #print('mean_stat_vals: ' + str(mean_stat_vals))
            #print('past_ten_mean_stat_vals: ' + str(past_ten_mean_stat_vals))
            #print('past_three_mean_stat_vals: ' + str(past_three_mean_stat_vals))

            plt.plot(game_nums, mean_stat_vals,  label = "Overall Mean")
            plt.plot(game_nums, past_ten_mean_stat_vals,  label = "Past 10 Mean")
            plt.plot(game_nums, past_three_mean_stat_vals,  label = "Past 3 Mean")


            plt.title(player_name.title() + " " + stat_name.upper() + " over Time")
            plt.xlabel("Game Num")
            plt.ylabel(stat_name.upper())

            plt.legend()
            plt.show()

            # display table so we can export to files and view graphs in spreadsheet

            #Two  lines to make our compiler able to draw:
            # plt.savefig(sys.stdout.buffer)
            # sys.stdout.flush()


def display_all_players_records_dicts(all_players_records_dicts, all_players_season_logs):
    #print('\n===Display All Players Records Dicts===\n')

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        #print('\n===' + player_name.title() + '===\n')

        #season_year = 2023

        # player_season_stat_dict = { stat name: .. }
        for season_year, player_season_stat_dict in player_stat_dict.items():

            #print("\n===Year " + str(season_year) + "===\n")
            #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
            #player_name = player_names[player_idx] # player names must be aligned with player game logs

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
                    
                    over_threes_line = '3PM ' + str(player_projected_lines['3PT']) + "+"
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

                    # display game info for reference based on game idx
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

                    #print("\n===" + player_name.title() + " Probabilities===\n")

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

            season_year -= 1

# players_outcomes = {player: stat name: outcome dict}
def display_players_outcomes(players_outcomes):
    #print("\n===Player Outcomes===\n")
    #print('players_outcomes: ' + str(players_outcomes))

    # sort so we see all instances of teammates out grouped together instead of game order bc we are interested to see by type of condition not by game at this point
    # we do want to see ordered by games as well so we have game idx and need way to switch bt views
    
    #todo: sorted_players_outcomes = sorter.sort_players_outcomes(players_outcomes) 


    # convert player outcomes dict into list
    player_outcomes_list = []
    # stat_outcome_dict = stat:outcome_dict
    for stat_outcome_dict in players_outcomes.values():

        for season_part_outcome_dict in stat_outcome_dict.values():

            for outcome_dict in season_part_outcome_dict.values():

                player_outcomes_list.append(outcome_dict) # outcome_dict = prediction:stats

    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(player_outcomes_list) > 0:
        # print header row
        outcome1 = player_outcomes_list[0]
        for key in outcome1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        # print data rows
        game_data = [header_row]
        game_data_strings = []
        for outcome in player_outcomes_list:
            outcome_row = []
            outcome_string = ''
            for val in outcome.values():
                outcome_row.append(val)
                outcome_string += str(val) + ";"
            game_data.append(outcome_row)
            game_data_strings.append(outcome_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    #print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)

    #print("\n===End Player Outcomes===\n")


# we have saved lessons from experience and logic that must be accounted for when deciding so display prominently and constantly reference
# lessons = [outcome, lesson]
def display_lessons(lessons):
    #print("\n===Display Lessons===\n")

    header_string = 'Outcome;Lesson'

    lesson_strings = []
    for lesson in lessons:
        lesson_string = lesson[0] + ';' + lesson[1]
        lesson_strings.append(lesson_string)

    #print("Export")
    print(header_string)
    for lesson in lesson_strings:
        print(lesson)

    #print("\n===End Lessons===\n")


# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# write_param = create (error if exists), overwrite, or append
def write_data_to_file(data, filepath, write_param, extension='csv'):
    #print('\n===Write Data to File: ' + filepath + '===\n')

    if extension == 'csv':

        with open(filepath, write_param) as csvfile:

            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)

    elif extension == 'json':
        with open(filepath, write_param) as outfile:
            json.dump(dict, outfile)

    else:
        print('Warning: Unknown file extension! ')
    
def write_json_to_file(dict, filepath, write_param='w+'):
    #print('\n===Write JSON to File: ' + filepath + '===\n')
    # filepath = data/game logs/cur/...

    # see if dir exists and make new if not
    # path_data = filepath.split('/')[:-1]
    # folder_path = ''
    # for folder in path_data:
    #     folder_path += folder
    #     if not os.path.exists(folder_path):
    #         os.mkdir(folder_path)


    #if not os.path.isfile(filepath):

    #filepath = re.sub('\s+','-',filepath) # is this needed or are spaces ok?
    with open(filepath, write_param) as outfile:
        json.dump(dict, outfile)

# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# def append_data_to_file(data, filepath):

#     print('\n===Write Data to File===\n')


# init record condition_record format ['1/1',..]
# desired format 1/1,..
# remove brackets and quotes
def convert_list_to_string(init_list):
    #print('init_list: ' + str(init_list))

    final_string = re.sub('[\\[\\]\']','',str(init_list))

    #print('final_string: ' + final_string)
    return final_string


# moved to generator
# all_player_consistent_stats = {} same format as stat records, 


#desired_order=list  headers
def list_dicts(dicts, desired_order=[], separator=',', output=''):
    #print('\n===List Dicts===\n')

    # desired_order = ['player name','stat name','ok val','ok pp','ok p']
    dict_list = converter.convert_dicts_to_lists(dicts, desired_order)

    # we cannot see clearly in tabulate format for big data
    #print('dict_list')
    #print(tabulate(dict_list))

    headers = []#[list(dicts[0].keys())]
    for key in desired_order:
        headers.append(key)
    if len(dicts) > 0:
        for key in dicts[0].keys():
            if key not in desired_order:
                headers.append(key)


    dict_list = [headers] + dict_list

    # export
    # to semicolon separated value
    # or csv bc semicolon only needed if comma used in cell
    for row in dict_list:
        export_row = ''
        for cell in row:
            # stop Sheets autoformatting 3pm as 3:00 PM
            # by adding apostrophe to the front
            #print('cell: ' + str(cell))
            if str(cell) == '3pm':
                cell = '\'3pm'
            export_row += str(cell) + separator

        print(export_row)

    if output == 'excel':
        data_key = 'stat probs' # folder and data type
        book_name = 'data/' + data_key + '/' + 'all ' + data_key + '.xlsx'
        print('book_name: ' + str(book_name))
        writer = pd.ExcelWriter(book_name)

        stat_probs_df = pd.DataFrame(dict_list)
        #print('stat_probs_df: ' + str(stat_probs_df))
        stat_probs_df.to_excel(writer)
        writer.close()

# one page for each stat showing all conditions
# all_player_stat_probs = {condition:year:part:stat:val} = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# stat_probs_by_stat = {stat:val:condition:year:part} = {'pts':{'0':{'all':{2023:{'regular':{po,pu}}
def write_all_stat_probs_by_stat(all_player_stat_probs):
    #print('\n===Write All Player Stat Probs by Stat===\n')

    for player, player_stat_probs in all_player_stat_probs.items():
        stat_probs_by_stat = {} # this must be in player loop or it will show max val for all players when we only need max for current players here bc separate sheets. this would be outside loop for all players when we want all players in same sheet
        #print('player: ' + str(player))
        if len(player_stat_probs.keys()) > 0:
            data_key = 'stat probs' # folder and data type
            organized_by = 'stat' # input key desired by user
            book_name = 'data/' + data_key + '/' + player + ' ' + data_key + ' - ' + organized_by + '.xlsx'
            #print('book_name: ' + str(book_name))
            writer = pd.ExcelWriter(book_name)

            headers = ['val']
            all_conditions = []
            for condition, condition_stat_probs in player_stat_probs.items():
                #print('condition: ' + str(condition))
                for year, year_stat_probs in condition_stat_probs.items():
                    #print('year: ' + str(year))
                    for part, part_stat_probs in year_stat_probs.items():
                        #print('part: ' + str(part))
                        conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
                        all_conditions.append(conditions)
                        headers.extend([conditions + ' over', conditions + ' under'])
                        for stat, stat_probs in part_stat_probs.items():
                            
                            for val, probs_dict in stat_probs.items():
                                
                                if stat not in stat_probs_by_stat.keys():
                                    stat_probs_by_stat[stat] = {}
                                    stat_probs_by_stat[stat][val] = {}
                                elif val not in stat_probs_by_stat[stat].keys():
                                    stat_probs_by_stat[stat][val] = {}

                                stat_probs_by_stat[stat][val][conditions] = probs_dict


            # player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
            # stat_probs_by_stat = {stat:val:conditions} = {'pts':{'0'{'all':{2023:{'regular':{po,pu}}
            #print('stat_probs_by_stat: ' + str(stat_probs_by_stat))
            #print('headers: ' + str(headers))
            for stat, stat_prob_dict in stat_probs_by_stat.items():
                stat_probs_table = []
                sheet_name = stat
                #print('\nsheet_name: ' + str(sheet_name))
                #print('stat_prob_dict: ' + str(stat_prob_dict))
                for val, val_probs_dict in stat_prob_dict.items():
                    #print('val: ' + str(val))
                    #print('val_probs_dict: ' + str(val_probs_dict)) # conditions: {po:po, pu:pu}
                    stat_probs_row = [val]

                    #for conditions, conditions_probs_dict in val_probs_dict.items():  

                    for conditions in all_conditions:
                        #print('conditions: ' + str(conditions))
                        p_o = 0
                        p_u = 100
                        if conditions in val_probs_dict.keys():
                            stat_prob = val_probs_dict[conditions]
                            p_o = converter.round_half_up(stat_prob*100)
                            p_u = 100 - p_o #converter.round_half_up(stat_probs_dict['prob under']*100)
                        stat_probs_row.extend([p_o, p_u])

                    #print('stat_probs_row: ' + str(stat_probs_row))
                    stat_probs_table.append(stat_probs_row)

                #print('stat_probs_table: ' + str(stat_probs_table))
                stat_probs_df = pd.DataFrame(stat_probs_table, columns=headers)
                #print('stat_probs_df: ' + str(stat_probs_df))
                stat_probs_df.to_excel(writer,sheet_name)

            writer.close()

# each player gets a table separate sheet 
# showing over and under probs for each stat val
# val, prob over, prob under
# 0, P_o0, P_u0
# all_player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# switch stat,val to val,stat to get
# player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
def write_all_player_stat_probs(all_player_stat_probs):
    #print('\n===Write All Player Stat Probs===\n')

    headers = ['val', 'pts prob over', 'pts prob under', 'reb prob over', 'reb prob under', 'ast prob over', 'ast prob under', '3pm prob over', '3pm prob under']

    # first arrange with all different stats in same sheet for each set of conditions
    # then arrange with same stat under all different conditions for each stat
    # this is a common method of rearranging dictionary levels for the purposes of
    # displaying in different forms and perspectives
    # see also generate_all_consistent_stat_dicts()
    # so make a fcn called rearrange dict, which takes desired output levels
    # and rearranges available keys in that order
    # so here it would be param=desired output order=[condition,year,part,val,stat]
    # where we only swap val and stat bc 1 val per row used as index which has multiple different stats in the same row
    # but those headers arent actually in the dict so we need to know the level nums of the init dict, 
    # and also input the desired output indexes
    # until we make that fcn for now we will make a temp dict with altered levels
    # and loop thru that to create rows after populating
    # so first loop makes temp dict rearranged in desired order
    # and second loop displays rows in desired order and format (however temp dict is arranged)
    # this is like creating a vector by aligning data points/features
    # each player gets its own book
    
    for player, player_stat_probs in all_player_stat_probs.items():
        #print('player: ' + str(player))
        #print('player_stat_probs: ' + str(player_stat_probs))
        if len(player_stat_probs.keys()) > 0:
            data_key = 'stat probs' # folder and data type

            organized_by = 'condition' # input key desired by user
            book_name = 'data/' + data_key + '/' + player + ' ' + data_key + ' - ' + organized_by + '.xlsx'
            #print('book_name: ' + str(book_name))
            writer = pd.ExcelWriter(book_name)
            #stat_probs_table = []
            for condition, condition_stat_probs in player_stat_probs.items():
                #print('condition: ' + str(condition))
                for year, year_stat_probs in condition_stat_probs.items():
                    #print('year: ' + str(year))
                    for part, part_stat_probs in year_stat_probs.items():
                        #print('part: ' + str(part))
                        sheet_name = condition + ' ' + str(year) + ' ' + part
                        #print('sheet_name: ' + str(sheet_name))

                        # rearrange all_player_stat_probs in desired order of columns (x,y)
                        # here we have x,y=stat,val
                        # output in player_stat_probs_dict
                        
                        player_stat_probs_dict = {}
                        for stat, stat_probs in part_stat_probs.items():
                            for val, probs_dict in stat_probs.items():
                                # only put val for first stat pts bc all stats share a row
                                # if stat == 'pts':
                                #     stat_probs_row = [val]
                                # p_o = probs_dict['prob over']
                                # p_u = probs_dict['prob under']
                                # stat_probs_row.extend([p_o, p_u])

                                if val not in player_stat_probs_dict.keys():
                                    player_stat_probs_dict[val] = {}
                                player_stat_probs_dict[val][stat] = probs_dict
                        # player_stat_probs_dict: {0: {'pts': {'prob over': 1.0, 'prob under': 0.0}, 'reb': {
                        #print('player_stat_probs_dict: ' + str(player_stat_probs_dict))
                        # need to fill blank cells with 0s or 100s to keep order alignment
                        # max_val = list(player_stat_probs_dict.keys())[-1] # last key is always max bc placed in order
                        # max_val = 0
                        # for val, val_probs_dict in player_stat_probs_dict.items():
                        #     max_stat_val = list(player_stat_probs_dict.keys())[-1] # last key is always max bc placed in order
                        #     print('max_stat_val: ' + str(max_stat_val))
                        #     if max_stat_val > max_val:
                        #         max_val = max_stat_val
                        # print('max_val: ' + str(max_val))

                        # stat probs by condition bc each condition gets a page showing all stats for that condition
                        stat_probs_table = []
                        #all_stat_keys = []
                        if 0 in player_stat_probs_dict.keys():
                            all_stat_keys = list(player_stat_probs_dict[0].keys()) # we need to get all stat keys from first dict so we know if player missed val for that stat
                        
                            for val, val_probs_dict in player_stat_probs_dict.items():
                                #val_idx = 0
                                stat_probs_row = [val]
                                for stat in all_stat_keys:
                                    p_o = 0
                                    p_u = 100
                                    if stat in val_probs_dict.keys():
                                        stat_prob = val_probs_dict[stat]
                                #for stat, stat_probs_dict in val_probs_dict.items():
                                        p_o = converter.round_half_up(stat_prob*100)
                                        p_u = 100 - p_o #converter.round_half_up(stat_probs_dict['prob under']*100)
                                    stat_probs_row.extend([p_o, p_u])

                                stat_probs_table.append(stat_probs_row)

                                #val_idx += 1

                            stat_probs_df = pd.DataFrame(stat_probs_table, columns=headers)
                            stat_probs_df.to_excel(writer,sheet_name)

                        
            writer.close()

    #write_all_stat_probs_by_condition(all_player_stat_probs)
    write_all_stat_probs_by_stat(all_player_stat_probs)


# write 1 sheet for all +ev props, sorted by true prob
# AND write 1 sheet for all 0 ev props, sorted by true prob
# AND write 1 sheet for all -ev props, sorted by true prob
# AND write 1 sheet for each strategy
def write_prop_tables(prop_dicts, sheet_names, desired_order, joint_sheet_name='Joints', rare_sheet_name='Rare', todays_date=datetime.today().strftime('%m-%d-%y')):
    print('\n===Write Prop Tables===\n')
    #print('prop_dicts: ' + str(prop_dicts))
    # print('sheet_names: ' + str(sheet_names))
    # print('desired_order: ' + str(desired_order))

    

    # book name = prop tables
    book_name = 'data/prop tables - ' + todays_date + '.xlsx'
    print('book_name: ' + str(book_name))
    writer = pd.ExcelWriter(book_name)

    init_desired_order = desired_order
    for table_idx in range(len(prop_dicts)):
        dict = prop_dicts[table_idx]

        sheet_name = sheet_names[table_idx]

        if sheet_name == joint_sheet_name:
            desired_order = ['joint', 'min risk', 'max picks top ev', 'max picks top prob']
        elif sheet_name == rare_sheet_name:
            desired_order = ['Game', 'Name', 'Stat', 'Norm', 'Prev', 'Cnt', 'Prob', 'Total']
        else:
            desired_order = init_desired_order

        #desired_order = [x.title() for x in desired_order]
        table_df = pd.DataFrame(dict, columns=desired_order)
        table_df.columns = [x.title() for x in table_df.columns]
        if 'Player' in table_df.keys():
            #player_str = str(table_df['Player'])
            #print('table_df[Player]: ' + str(table_df['Player']))
            player_val = table_df['Player']
            if isinstance(player_val, str):
                table_df['Player'] = player_val.str.title() 
            # else:
            #     print('Warning: player val not string! ' + str(player_val))

        table_df.to_excel(writer,sheet_name)


    writer.close()

    # delete prev game prop table bc already backed up
    remover.delete_file('prop tables', todays_date)
    

# divide logs/data (eg player game logs) into cur yr and prev yrs
# init and final dicts combine cur and prev yrs
# so here we separate to write cur and prev separately
# bc prev stays same while cur changes each new game
# need cur_yr bc only cur yr changes
# data_type is folder to find preexisting file to delete
def write_cur_and_prev(init_dict, final_dict, cur_file, prev_file, cur_yr, subject_name='', todays_date='', data_type=''):
    # print('\n===Write Cur and Prev===\n')
    # print('cur_yr: ' + str(cur_yr))
    # cur file = player_cur_season_log_filename = 'data/game logs/' + player_name + ' ' + current_year_str + ' game log ' + todays_date + '.json'

    # print('init_dict: ' + str(init_dict))
    # print('final_dict: ' + str(final_dict))
    # print('cur_file: ' + str(cur_file))
    # print('prev_file: ' + str(prev_file) + '\n')
    
    # take first year as cur yr
    init_cur_dict = {} #list(init_dict.values)[0]
    init_prev_dict = {}
    final_cur_dict = {} #list(final_dict.values)[0]
    final_prev_dict = {}
    
    # if init dict does not have cur yr then init cur dict = {}
    # if cur_yr in init_dict.keys():
    #     init_cur_dict = init_dict[cur_yr]
    # if cur_yr in final_dict.keys():
    #     final_cur_dict = final_dict[cur_yr]

    #year_idx = 0
    for year, year_dict in init_dict.items():
        
        if year == cur_yr:
            init_cur_dict = year_dict

        else:
            init_prev_dict[year] = year_dict

        #year_idx += 1

    #year_idx = 0
    for year, year_dict in final_dict.items():
        
        if year == cur_yr:
            final_cur_dict = year_dict

        else:
            final_prev_dict[year] = year_dict

        #year_idx += 1

    #print('init_cur_dict: ' + str(init_cur_dict))
    #print('final_cur_dict: ' + str(final_cur_dict))
    #print('init_prev_dict: ' + str(init_prev_dict))
    #print('final_prev_dict: ' + str(final_prev_dict))
    if not init_cur_dict == final_cur_dict:
        #print(subject_name + ' CURRENT year data changed so write to file')
        write_json_to_file(final_cur_dict, cur_file)

        # delete prev day cur file bc replaced by cur day
        #yesterday = 
        #yesterday_file = prev_day_cur_file = 'data/game logs/' + player_name + ' ' + current_year_str + ' game log ' + todays_date + '.json'
        #pathlib.Path(path).is_file():
        # determine if existing file in folder has player name
        if data_type != '':
            # add cur bc we only need to delete cur files which get changed each game
            # separate folder bc we ignore it when backing up files
            data_type += '/cur' # game logs/cur
            remover.delete_file(subject_name, todays_date, data_type)
            

        

    if not init_prev_dict == final_prev_dict:
        #print(subject_name + ' PREVIOUS year data changed so write to file')
        write_json_to_file(final_prev_dict, prev_file)


	# now that we have new cur game log, we can delete the old one
	# by using same name structure with different date
	# if file does not exist, do nothing
	# always good reason to have stat dict (or game log) saved is if we want to see how probs changed over time after each game
	# BUT stat dict also shows that for each condition so that actually applies to stat dict even better than game log
	# player_old_cur_season_log_key = player_name + ' ' + current_year_str + ' game log '
	# not_string = todays_date
	# writer.delete_file(player_old_cur_season_log_key, not_string) # delete file in folder with name containing key string but not other string
        



def display_game_info(after_injury_players, rare_prev_val_players):
    print('\n===Display Game Info===\n')


    title = 'after injury players'
    print('\n===' + title.title() + '===\n')

    print(tabulate(after_injury_players, headers=['Player'])) # game, days after, injury type, restricted playtime

    for rare_cat, rare_cat_players in rare_prev_val_players.items():
        title = rare_cat
        print('\n===' + title.title() + '===\n')
        #header_row = ['Player', 'Stat', 'Norm', 'Prev']
        #rare_cat_players = header_row + rare_cat_players
        # remove last idx from all lists
        final_rare_cat_players = []
        for rare_player_data in rare_cat_players:
            final_rare_cat_players.append(rare_player_data[:-1])

        print(tabulate(final_rare_cat_players, headers=['G', 'Name', 'S', 'N', 'Pre', 'Ct', 'P', 'Tot']))


def display_list(list, title):
    print('\n===' + title.title() + '===\n')

    for item in list:
        print(item)

    print('\n==============================\n')