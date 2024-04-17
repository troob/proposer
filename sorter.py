# sorter.py
# sorting fcns like sorting dictionaries by one common key
# eg sort predictions by degree of belief

import isolator





def sort_rare_prev_val_players(rare_prev_val_players):
    # print('\n===Sort Rare Prev Val Players===\n')
    # print('Input: rare_prev_val_players = {rare under:[(...), ...], ...}')
    # print('\nOutput: rare_prev_val_players = {rare under:[(...), ...], ...}\n')

    for rare_cat, rare_cat_players in rare_prev_val_players.items():
        # rare_cat_players = [(...), ...]
        # sort tuples by prob val
        # total prob idx
        # split by game
        rare_cat_games = isolator.isolate_rare_cat_games(rare_cat_players)
        #rare_prev_val_players[rare_cat] = sorted(rare_cat_players, key=lambda x: x[7]) #sort_tuples_by_idx(rare_cat_players, idx=7)
        sorted_rare_cat_players = []
        for game in rare_cat_games:
            sorted_game_players = sorted(game, key=lambda x: x[7])

            for player in sorted_game_players:
                sorted_rare_cat_players.append(player)

        rare_prev_val_players[rare_cat] = sorted_rare_cat_players

    return rare_prev_val_players



# predictions = { 'prediction':'','overall record':[],..,'degree of belief':0 }
def sort_predictions_by_deg_of_bel(predictions):
    sorted_predictions = sorted(predictions, key=lambda d: d['degree of belief']) 

    return sorted_predictions

# given a list of dicts with corresponding keys, 
# we want to see which dict has the highest value at a given key they all share
def sort_dicts_by_key(dicts, key, reverse=True):

    return sorted(dicts, key=lambda d: d[key], reverse=reverse) # reverse so we see highest first

# given a list of dicts with corresponding keys, 
# we want to see which dict has the highest value at a given key they all share
def sort_dicts_by_keys(dicts, keys, reverse=True):
    # key1 = keys[0]
    # key2 = keys[1]

    #for k in keys: d[k]

    #dicts = sorted(dicts, key=lambda d: (d[key1],d[key2]), reverse=True) # reverse so we see highest first
    dicts = sorted(dicts, key=lambda d: ([float(d[k]) for k in keys]), reverse=reverse)
    #dicts = sorted(dicts, key=lambda d: lambda k: d[k] for k in keys, reverse=True)

    return dicts

def sort_dicts_by_str_keys(dicts, keys, reverse=False):

    dicts = sorted(dicts, key=lambda d: ([str(d[k]) for k in keys]), reverse=reverse)

    return dicts

# given a list of dicts with corresponding keys, 
# we want to see which dict has the highest value at a given key they all share
#>>> d = {'Bill': 4, 'Alex' : 4, 'Bob' : 3, "Charles": 7}    
#>>> sorted(d, key=lambda k: (d[k], k))
#['Bob', 'Alex', 'Bill', 'Charles']
def sort_dict_by_key_val(d, reverse=True):

    return sorted(d, key=lambda k: (d[k], k), reverse=reverse) # reverse so we see highest first


# sort so we see all condition types grouped together for separate analysis and viewing
# players_outcomes = {player: stat name: outcome dict}
def sort_players_outcomes(players_outcomes):
    print('sort players outcomes')

    print('players_outcomes: ' + str(players_outcomes))