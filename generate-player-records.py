# generate record over stat val



# at this point we should have projected_lines_dict either by external source or player averages
# the record we are generating is a measure of determining consistency but there may be better ways
# current_year needed to determine avg line if no projected line given
def generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts={}, current_year=2023):

    print('\n===Generate Player Records Dict===\n')
    print('===' + player_name.title() + '===\n')

    player_records_dicts = {}


    # if we do not have projected lines then we can use player means as lines
    # we pass in projected lines as param so at this point we already have actual projected lines or averages to determine record above and below line
    # we could get avgs from stats but we already compute avgs so we can get it from that source before running this fcn
    player_projected_lines = {}
    if player_name in projected_lines_dict.keys():
        player_projected_lines = projected_lines_dict[player_name]
    else:
        print('Warning: Player ' + player_name + ' not in projected lines!')
        projected_lines_dict[player_name] = player_medians_dicts['all'][current_year]

        player_avg_lines = player_medians_dicts['all'][current_year]

        stats_of_interest = ['pts','reb','ast','3pm','blk','stl','to'] # we decided to focus on these stats to begin
        for stat in stats_of_interest:
            player_projected_lines[stat] = player_avg_lines[stat]
        
        print('player_projected_lines: ' + str(player_projected_lines))

    #season_year = 2023

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_season_stat_dict in player_stat_dict.items():

        print("\n===Year " + str(season_year) + "===\n")
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
                            player_all_records_dicts[season_year][stat_name] = streak
                        else:
                            player_all_records_dicts[season_year] = { stat_name: streak }

                        #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                    else:
                        #print("conditions " + conditions + " not in streak tables")
                        player_records_dicts[conditions] = {}
                        player_all_records_dicts = player_records_dicts[conditions]
                        player_all_records_dicts[season_year] = { stat_name: streak }

                # given how many of recent games we care about
                # later we will take subsection of games with certain settings like home/away
                # first we get all stats and then we can analyze subsections of stats
                # eg last 10 games

    print('player_records_dicts: ' + str(player_records_dicts))
    return player_records_dicts



# we are looking for the stat val reached at least 90% of games
# so from 0 to max stat val, get record reached games over total games
# player_stat_records = []
# no need to make dict because stat val = idx bc going from 0 to N
def generate_player_stat_records(player_name, player_stat_dict):
    print('\n===Generate Player Stat Record===\n')
    print('===' + player_name.title() + '===\n')

    player_stat_records = {}

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_season_stat_dict in player_stat_dict.items():
        print("\n===Year " + str(season_year) + "===\n")

        # all_pts_dicts = {'all':{idx:val,..},..}
        # all_pts_dicts = {'all':{1:20}}
        # key=condition, val={idx:stat}
        all_pts_dicts = player_season_stat_dict['pts']
        if len(all_pts_dicts['all'].keys()) > 0:

            all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

            # key represents set of conditions of interest eg home/away
            for condition in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                print("\n===Condition " + str(condition) + "===\n")

                # reset for each condition
                stat_names = ['pts']

                # for each stat type/name (eg pts, reb, etc)
                # loop from 0 to max stat val to get record over stat val for period of all games
                for stat_name in stat_names:

                    # reset for each stat name/type
                    all_games_reached = [] # all_stat_counts = []
                    all_probs_stat_reached = []

                    print('stat_name: ' + str(stat_name))
                    stat_vals = list(player_season_stat_dict[stat_name][condition].values())
                    print('stat_vals: ' + str(stat_vals))
                    num_games_played = len(stat_vals)
                    print('num games played ' + condition + ': ' + str(num_games_played))
                    for stat_val in range(1,max(stat_vals)):
                        num_games_reached = 0 # stat count, reset for each check stat val bc new count
                        # loop through games to get count stat val >= game stat val
                        for game_idx in range(num_games_played):
                            game_stat_val = stat_vals[game_idx]
                            if game_stat_val >= int(stat_val):
                                num_games_reached += 1

                            all_games_reached.append(num_games_reached) # one count for each game

                        print('num_games_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(num_games_reached)) 
                        

                        prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                        print('prob_stat_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(prob_stat_reached)) 

                        all_probs_stat_reached.append(prob_stat_reached)


                    if condition in player_stat_records.keys():
                        #print("conditions " + conditions + " in streak tables")
                        player_condition_records_dicts = player_stat_records[condition]
                        if season_year in player_condition_records_dicts.keys():
                            player_condition_records_dicts[season_year][stat_name] = all_probs_stat_reached
                        else:
                            player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }

                        #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                    else:
                        #print("conditions " + conditions + " not in streak tables")
                        player_stat_records[condition] = {}
                        player_condition_records_dicts = player_stat_records[condition]
                        player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }


    print('player_stat_records: ' + str(player_stat_records))
    return player_stat_records