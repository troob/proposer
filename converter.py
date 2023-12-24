# converter.py

import re # need to see if negative sign in odds string

import reader # read player abbrevs

def convert_dict_to_list(dict, desired_order=[]):

    dict_list = []

    for key in desired_order:
        if key in dict.keys():
            val = dict[key]
            dict_list.append(val)
        else:
            print('Warning: Desired key ' + key + ' not in dict!')

    # add remaining in the order they come
    for key, val in dict.items():
        # if not already added
        if key not in desired_order:
            dict_list.append(val)

    return dict_list


def convert_dicts_to_lists(all_consistent_stat_dicts, desired_order=[]):
    #print('\n===Convert Dicts to Lists===\n')
    dict_lists = []

    for dict in all_consistent_stat_dicts:
        #print('dict: ' + str(dict))

        dict_list = convert_dict_to_list(dict, desired_order)

        dict_lists.append(dict_list)
        
    return dict_lists

# from 2023-24 to 2024
def convert_span_to_season(span):

    #print('span: ' + span)
    season_years = span.split('-')
    # for now assume 2000s
    season = '20' + season_years[1]

    #print('season: ' + season)
    return season

def convert_irregular_team_abbrev(init_team_abbrev):
    #print('\n===Convert Irregular Team Abbrev: ' + init_team_abbrev + '===\n')

    init_team_abbrev = init_team_abbrev.lower()

    final_team_abbrev = init_team_abbrev

    irregular_abbrevs = {'bro':'bkn', 
					  	'gs':'gsw',
						'okl':'okc', 
						'no':'nop',
						'nor':'nop', 
						'pho':'phx', 
						'was':'wsh', 
						'uth': 'uta', 
						'utah': 'uta', 
						'sa':'sas',
						'ny':'nyk'  } # for these match the first 3 letters of team name instead

    if init_team_abbrev in irregular_abbrevs.keys():
        final_team_abbrev = irregular_abbrevs[init_team_abbrev]

    #print('final_team_abbrev: ' + final_team_abbrev)
    return final_team_abbrev

# SEE generate_player_abbrev for more
# jaylen brown -> j brown sg
# trey murphy iii -> t murphy iii sg
# Jayson Tatum -> J Tatum SF
# use to see if started or bench
# bc box score shows player abbrev
# lineups online have mix of full and abbrev names
# def convert_player_name_to_abbrev(player, player_position):
#     player_abbrev = ''
#     return player_abbrev

# given team and player abbrev without position
# we can tell player full name
# we get team from all lineups page online
# but if we only get abbrev then we cannot say position for sure
# if 2 players have same abbrevs on same team, lineups will differentiate for us
# so take full name first and abbrev as remaining option
def convert_player_abbrev_to_name(player_abbrev, player_team):
    player_name = ''

    # check if 2 players on same team with same abbrev
    # bc if so then would take first player name without knowing position



    return player_name

# american odds given as string from internet
def convert_american_to_decimal_odds(american_odds):
    #print('\n===Convert American to Decimal Odds===\n')
    #print('american_odds: ' + str(american_odds))
    decimal_odds = 0.0

    if re.search('-',american_odds):
        decimal_odds = "%.2f" % ((100 / -int(american_odds)) + 1)
    else:
        decimal_odds = "%.2f" % ((int(american_odds) / 100) + 1)
    
    #print('decimal_odds: ' + str(decimal_odds))
    return float(decimal_odds)


def convert_team_abbrev_to_name(team_abbrev):
    print('\n===Convert Team Abbrev to Name: ' + team_abbrev + '===\n')
    
    name = ''

    team_names = {'atl':'atlanta hawks', 
                    'bos':'boston celtics', 
                    'bkn':'brooklyn nets', 
                    'cha':'charlotte hornets', 
                    'chi':'chicago bulls',
                    'cle':'cleveland cavaliers',
                    'dal':'dallas mavericks',
                    'den':'denver nuggets',
                    'det':'detroit pistons',
                    'gsw':'golden state warriors',
                    'hou':'houston rockets',
                    'ind':'indiana pacers',
                    'lac':'la clippers',
                    'lal':'los angeles lakers',
                    'mem':'memphis grizzlies',
                    'mia':'miami heat',
                    'mil':'milwaukee bucks',
                    'min':'minnesota timberwolves',
                    'nop':'new orleans pelicans',
                    'nyk':'new york knicks',
                    'okc':'oklahoma city thunder',
                    'orl':'orlando magic',
                    'phi':'philadelphia 76ers',
                    'phx':'phoenix suns',
                    'por':'portland trail blazers',
                    'sac':'sacramento kings',
                    'sas':'san antonio spurs',
                    'tor':'toronto raptors',
                    'uta':'utah jazz',
                    'wsh':'washington wizards'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals

    if team_abbrev in team_names.keys():
        name = team_names[team_abbrev]

    print('name: ' + name)
    return name














# Convert Player Name to Abbrev: damion lee
# what is the diff bt this and determine player abbrev?
def convert_player_name_to_abbrev(game_player, all_players_abbrevs, all_players_teams={}, all_box_scores={}, season_years=[], cur_yr=''):
    #print('\n===Convert Player Name to Abbrev: ' + game_player.title() + '===\n')
    #print('all_players_abbrevs: ' + str(all_players_abbrevs))

    game_player_abbrev = ''


    for year_players_abbrev in all_players_abbrevs.values():
        for abbrev, name in year_players_abbrev.items():
            if name == game_player:
                game_player_abbrev = abbrev#all_players_abbrevs[game_player]#convert_player_name_to_abbrev(game_player, all_players_abbrevs, all_players_teams, all_box_scores, season_years, cur_yr)
                break

        if game_player_abbrev != '':
            break






    # it is looking for cur yr so how does it handle players who played last yr but are still on team but not playing this yr?
    # player does not register on teams list if not played this yr so need to check roster
    # if player of interest has not played with player this yr 
    # but did play with them previous seasons and they are listed as out, then this is a case of player still on team but stopped playing time for any reason
    # should we loop thru all yrs until we find abbrev? 
    # really only need 1 yr bc player still on team but not played so unlikely to be on team without playing for more than a yr but possible
    # if len(season_years) == 0 and cur_yr != '':
    #     if cur_yr in all_players_abbrevs.keys() and game_player in all_players_abbrevs[cur_yr].keys():
    #         game_player_abbrev = all_players_abbrevs[cur_yr][game_player] #converter.convert_player_name_to_abbrev(out_player)
    #     else:
    #         if cur_yr in all_players_teams.keys() and game_player in all_players_teams[cur_yr].keys():
    #             # out_player_teams = all_players_teams[cur_yr][out_player]
    #             # out_player_team = determiner.determine_player_current_team(out_player, out_player_teams, cur_yr, rosters)
    #             game_player_abbrev = reader.read_player_abbrev(game_player, all_players_teams, cur_yr, all_box_scores)
    #         else:
    #             print('Warning: Game player not in all players current teams! ' + game_player)
    # else:
    #     for year in season_years:
    #         #print('\nyear: ' + str(year))
    #         if year in all_players_abbrevs.keys() and game_player in all_players_abbrevs[year].keys():
    #             year_players_abbrevs = all_players_abbrevs[year]
    #             #print('year_players_abbrevs: ' + str(year_players_abbrevs))
    #             game_player_abbrev = year_players_abbrevs[game_player] #converter.convert_player_name_to_abbrev(out_player)
    #         else:
    #             if year in all_players_teams.keys() and game_player in all_players_teams[year].keys():
    #                 game_player_abbrev = reader.read_player_abbrev(game_player, all_players_teams, year, all_box_scores)
    #             else:
    #                 print('Warning: Game player not in all players teams! ' + game_player + ', ' + str(year))

    #         if game_player_abbrev != '':
    #             break

    #print('game_player_abbrev: ' + str(game_player_abbrev))
    return game_player_abbrev

def convert_to_game_players_str(game_part_players):
    game_players_str = ''
    game_part_players = sorted(game_part_players)
    for game_player_idx in range(len(game_part_players)):
        game_player_abbrev = game_part_players[game_player_idx]
        # add condition for all game players in combo
        if game_player_idx == 0:
            game_players_str = game_player_abbrev
        else:
            game_players_str += ', ' + game_player_abbrev

    return game_players_str

# convert cond dict to list
#all_current_conditions: {'cole anthony': {'loc': 'away', 'out': ['wendell carter jr', 'markelle fultz'], 'start...
# all_current_conditions = {p1:{out:[m fultz pg], loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
# list = away, 'p1 out', 'p2 out', ...
# need to expand list values
# conditions_list = ['m fultz pg out', 'w carter c out', 'm fultz pg, w carter c out', 'away', ...]
def convert_conditions_to_dict(conditions, all_players_abbrevs, all_players_teams, all_box_scores, player='', season_years=[], cur_yr=''):
    # print('\n===Convert Conditions Dict to List: ' + player.title() + '===\n')
    # print('Input: Player of Interest')
    # print('Input: conditions_dict = {starters:[s1,...], loc:l1, city:c1, dow:d1, tod:t1,...}, ... = {\'loc\': \'away\', \'out\': [\'vlatko cancar\',...], ...')
    # print('Input: all_players_abbrevs = {year:{player:abbrev, ... = {\'2024\': {\'J Jackson Jr PF\': \'jaren jackson jr\',...')
    # print('\nOutput: conditions_dict = {\'p1, p2 out\':out, \'p1 out\':out, \'p2 out\':out, \'away\':loc, ...],...\n')

    #print('all_players_abbrevs: ' + str(all_players_abbrevs))

    conditions_dict = {}

    game_players_cond_keys = ['out', 'starters', 'bench']

    game_players = []
    for cond_key, cond_val in conditions.items():
        # print('cond_key: ' + str(cond_key))
        # print('cond_val: ' + str(cond_val))
        
        if cond_key in game_players_cond_keys:#== 'out':
            #print('game player condition')
            #game_players_str = ''
            game_part_players = []
            
            for game_player_idx in range(len(cond_val)):
                game_player = cond_val[game_player_idx]
                #print('\ngame_player: ' + str(game_player))
                # need to convert player full name to abbrev with position to compare to condition titles
                # at this point we have determined full names from abbrevs so we can refer to that list
                # done: save player abbrevs for everyone played with
                # NEXT: enable multiple irregular abbrevs like X Tillman and Tillman Sr for xavier tillman
                # pass in list of players with multiple abbrevs so we dont have to check every player
                game_player_abbrev = convert_player_name_to_abbrev(game_player, all_players_abbrevs)

                # for single player change starters to starter or starting so it can be plural or singular
                # D Green PF out
                # remove s from starters for single player
                # final_cond_key = cond_key
                # if cond_key == 'starters':
                #     if not re.search(',',cond_key):
                #         final_cond_key = cond_key.rstrip('s')
                # D Green PF out, S Curry PG starters
                final_cond_val = game_player_abbrev + ' ' + cond_key 
                #print('final_cond_val: ' + str(final_cond_val))
                
                conditions_dict[final_cond_val] = cond_key

                # if condition is multiplayer then we need to sort alphabetically
                #if re.search(',',conditions):
                game_part_players.append(game_player_abbrev)
                if cond_key != 'out':
                    game_players.append(game_player_abbrev)
                    cond_key = 'in'
                    final_cond_val = game_player_abbrev + ' ' + cond_key 
                    #print('final_cond_val: ' + str(final_cond_val))
                    
                    conditions_dict[final_cond_val] = cond_key

            game_players_str = convert_to_game_players_str(game_part_players)
            
            #game_players_str += ' ' + cond_key
            final_cond_val = game_players_str + ' ' + cond_key 
            print('final_cond_val: ' + str(final_cond_val))
            conditions_dict[final_cond_val] = cond_key


        else:
            conditions_dict[cond_val] = cond_key

    # add all players probs here bc we dont need in condition until now since we already have starters and bench which makes up in
    # we do not want to show in condition due to clutter but still account for it
    if len(game_players) > 0:
        game_players_str = convert_to_game_players_str(game_part_players)
            
        cond_key = 'in'
        final_cond_val = game_players_str + ' ' + cond_key
        print('final_cond_val: ' + str(final_cond_val))
        conditions_dict[final_cond_val] = cond_key

    # conditions_list: ['home', 'L Nance Jr PF out', 'M Ryan F out', 'L Nance Jr PF, M Ryan F out', 'C McCollum SG starters', 'B Ingram SF starters', 'H Jones SF starters', 'Z Williamson PF starters', 'J Valanciunas C starters', 'C McCollum SG, B Ingram SF, H Jones SF, Z Williamson PF, J Valanciunas C starters', 'bench']
    #print('conditions_dict: ' + str(conditions_dict))
    return conditions_dict

# all_conditions_dicts = {p1:{out:[m fultz pg], loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
# all_conditions_lists = {p1:[m fultz pg out, away, ...],...
def convert_all_conditions_to_dicts(all_conditions, all_players_abbrevs, all_players_teams, all_box_scores, season_years=[], cur_yr=''):
    print('\n===Convert All Conditions Dicts to Lists===\n')
    print('Input: all_conditions = {p1:{starters:[s1,...], loc:l1, city:c1, dow:d1, tod:t1,...}, ... = {\'nikola jokic\': {\'loc\': \'away\', \'out\': [\'vlatko cancar\',...], ...')
    print('Input: all_players_abbrevs = {year:{player:abbrev, ... = {\'2024\': {\'J Jackson Jr PF\': \'jaren jackson jr\',...')
    # print('Input: all_players_teams = {player:{year:{team:gp,... = {\'bam adebayo\': {\'2018\': {\'mia\': 69}, ...\n')
    # print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
    # print('Input: Season Years of Interest')
    print('\nOutput: all_conditions_dicts = {p1:{\'p1, p2 out\':\'out\', \'p1 out\':\'out\', \'p2 out\':\'out\', \'away\':\'loc\', ...},... = {\'nikola jokic\': [\'away\', \'V Cancar SF, J Murray PG,... out\', ...\n')


    all_conditions_dicts = {}

    for player, cond in all_conditions.items():
        cond_dict = convert_conditions_to_dict(cond, all_players_abbrevs, all_players_teams, all_box_scores, player, season_years, cur_yr)
        all_conditions_dicts[player] = cond_dict

    #print('all_conditions_lists: ' + str(all_conditions_lists))
    return all_conditions_dicts