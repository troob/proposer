# isolator.py
# isolate data elements of the same type or with matching features
# eg isolate one game from all games and isolate all games with certain scores

import re
from tabulate import tabulate # display output

import determiner # determine vals in dict to isolate
import sorter # sort dicts by key to get highest ev dict

def isolate_games(raw_data):
    print("\n===Isolate Games===\n")
    print("raw_data: " + str(raw_data))
    all_games = []
    game = []
    existing_game = False
    for line in raw_data:
        print("line: " + str(line))
        # if first element has game label or date consider it a new game
        if line[0] == 'Game' or re.search('/',line[0]): # we tell date by slash (/)
            print("New Game")
            existing_game = True
            # new game
            if len(game) != 0: # if no game data yet, do not add game to all games until adding lines to game
                all_games.append(game)
            game = [line]

        # continue to append lines to the current game until we encounter another game or date label
        if existing_game == True:
            game.append(line)

    print("all_games: " + str(all_games))
    return all_games


# game data has headers and each month is separated by monthly averages
# which happen to be differentiated by uppercase letters
def isolate_player_game_data(player_data, player_name=''):
    player_game_data = []

    if len(player_data) > 0:
        for row in player_data:
            if not row[0].isupper():
                player_game_data.append(row)

        # display player game data in formatted table for observation
        #print("player_game_data: " + str(player_game_data))

        header_row = player_data[0]

        table = [header_row]
        for row in player_game_data:
            table.append(row)

        print("\n===" + player_name + "===\n")
        print(tabulate(table))
    else:
        print("Warning: No Player Data from file.")

    return player_game_data

# assuming header row to find keyword to find idx of desired field
def isolate_data_field(desired_field_name, data_table):
    data_field = []

    # given header row find keyword to find idx
    header_row = data_table[0]

    desired_field_idx = 0
    for field_idx in range(len(header_row)):
        field_name = header_row[field_idx]
        if re.search(desired_field_name.lower(), field_name.lower()):
            desired_field_idx = field_idx

    for row in data_table[1:]:
        data_field.append(row[desired_field_idx])


    return data_field

# assuming header row to find keyword to find idx of desired field
# def isolate_data_element(desired_field_name, header, data_row):
#     data_field = []

#     # given header row find keyword to find idx
#     header_row = data_table[0]

#     desired_field_idx = 0
#     for field_idx in range(len(header_row)):
#         field_name = header_row[field_idx]
#         if re.search(desired_field_name.lower(), field_name.lower()):
#             desired_field_idx = field_idx

#     for row in data_table[1:]:
#         data_field.append(row[desired_field_idx])


#     return data_field


# isolate likely outcomes using stats to find consistent streaks
# ie isolate consistent streaks
# stats_counts = [ pts_counts, rebs_counts, ... ]
# pts_counts = [ 1/1, 2/2, 2/3, ... ]
# make rules to eliminate bad options and isolate good options
# eg dont always rule out 0/1 if they are 9/10
# and dont rule out 0/2 if they are 10/12?
# if unclear, it is better to keep for review
# start by isolating positive streaks
# start from most to least recent
def isolate_consistent_streaks(all_stats_counts_dict):

    # did they hit last game?
    # either way, continue to next game to assess streak but conditions for passing have changed
    # if hit most recent, then 2/2 will increase likelihood
    # if missed most recent, then 1/2 will need to check next 2 games at least to see if 3/4 bc 2/3 is not likely enough

    consistent_streaks = []

    # start simple, create group of 7/10 streaks
    for stats_counts in stats_counts.values():
        print("stats_counts: " + str(stats_counts))
        for stat_counts in stats_counts:
            print("stat_counts: " + str(stat_counts))

            pt_counts = stat_counts[0]
            if stat_counts[9] >= 7:
                consistent_streaks.append(streak)



    return consistent_streaks


# isolate all keys with 'out' or list of names
# see sort keys bc we may want to see all keys sorted rather than exclude potentially relevant keys
def isolate_keys_in_dict(regex, dict):
    print('isolate keys')










def isolate_high_prob_props(prop_dicts):
    print('\n===Isolate High Prob Props===\n')

    high_prob_props = []

    for prop in prop_dicts:
        #print('prop: ' + str(prop))
        true_prob = int(prop['true prob'])
        #print('true_prob: ' + str(true_prob))
        if true_prob >= 90:
            high_prob_props.append(prop)

    print('high_prob_props: ' + str(high_prob_props))
    return high_prob_props

# arbitrary uncertainty +/- 0.05???
def isolate_props_in_range(prop_dicts):
    print('\n===Isolate Props in range===\n')

    props_in_range = []

    neg_uncertainty = -0.03 # bc 2 sig figs?
    pos_uncertainty = 0.3 # tested >0.3 and seems out of range bc super unlikely

    for prop in prop_dicts:
        if neg_uncertainty <= float(prop['ev']) <= pos_uncertainty:
            props_in_range.append(prop)

    print('props_in_range: ' + str(props_in_range))
    return props_in_range

# arbitrary uncertainty +/- 0.05???
def isolate_plus_ev_props(prop_dicts):
    print('\n===Isolate +EV Props===\n')

    plus_ev_props = []

    uncertainty = 0.05 # bc 2 sig figs?

    for prop in prop_dicts:
        if float(prop['ev']) >= -uncertainty:
            plus_ev_props.append(prop)

    print('plus_ev_props: ' + str(plus_ev_props))
    return plus_ev_props

def isolate_duplicate_dicts(main_dict, keys, dict_list):
    #print('\n===Isolate Duplicate Dicts===\n')

    duplicate_dicts = []

    # already determined duplicates before running this
    #if determiner.determine_multiple_dicts_with_vals()

    for dict in dict_list:
        if determiner.determine_vals_in_dict(main_dict, keys, dict):
            duplicate_dicts.append(dict)
        
    #print('duplicate_dicts: ' + str(duplicate_dicts))
    return duplicate_dicts

def isolate_sg_props(main_prop, props):
    print('\n===Isolate SG Props===\n')

    sg_props = []

    main_game = main_prop['game']
    for prop in props:
        prop_game = prop['game']
        if main_game == prop_game:
            sg_props.append(prop)

    print('sg_props: ' + str(sg_props))
    return sg_props

def isolate_highest_prob_prop(sg_props, field_key=''):
    print('\n===Isolate Highest Prob Prop===\n')
    
    # Iso by auto sort
    if field_key == '':
        field_key = 'true prob'
    
    highest_prop = sorter.sort_dicts_by_key(sg_props, field_key, reverse=True)[0]
    
    print('highest_prop: ' + str(highest_prop))
    return highest_prop

def isolate_highest_ev_prop(sg_props):
    
    # Isolate by manul sort
    # init_prop = sg_props[0]
    
    # highest_prop = init_prop

    # prev_highest_ev = init_prop['ev']
    # for prop in sg_props:
    #     prop_ev = prop['ev']
    #     if prop_ev > prev_highest_ev:
    #         highest_prop = prop
    #         prev_highest_ev = prop_ev

    # Iso by auto sort
    highest_prop = sorter.sort_dicts_by_key(sg_props, 'ev', reverse=True)[0]
    #print('highest_prop: ' + str(highest_prop))
    return highest_prop



























def isolate_rare_cat_games(rare_cat_players):
    # print('\n===Isolate Rare Cat Games===\n')
    # print('Input: rare_cat_players = [(...), ...] = ' + str(rare_cat_players))
    # print('\nOutput: rare_cat_games = [[(...), ...], ...]\n')

    rare_cat_games = []
    game = []
    prev_game_num = 1
    for player in rare_cat_players:

        game_num = player[0]
        # print('prev_game_num: ' + str(prev_game_num))
        # print('game_num: ' + str(game_num))

        if game_num == prev_game_num:
            game.append(player)
        else:
            rare_cat_games.append(game)
            game = [player]

        prev_game_num = game_num

    rare_cat_games.append(game)

    #print('rare_cat_games: ' + str(rare_cat_games))
    return rare_cat_games


def isolate_team_part_conds(team_part, team_gp_conds):
    print('\n===Isolate Team Part Conditions===\n')
    print('Input: team_part = ' + team_part)
    print('Input: team_gp_conds = {gp condition:cond type,... = {\'A Gordon PF, J Murray PG,... out\':out, \'A Gordon PF out\':out, ...}, opp:{...} = ' + str(team_gp_conds))
    print('\nOutput: team_part_conds = [condition,...]\n')
    
    team_part_conds = []

    for gp_cond, cond_type in team_gp_conds.items():
        if cond_type == team_part:
            team_part_conds.append(gp_cond)

    print('team_part_conds: ' + str(team_part_conds))
    return team_part_conds