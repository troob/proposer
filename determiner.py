# determiner.py
# determine conditions 
# eg if streak is considered consistent

import re # see if keyword in column name
import reader # format stat val

from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart

#import requests # check if webpage exists while we are looping through player game log seasons until we cannot find game log for that year (note rare players may take a year off and come back but for now assume consistent years)
# request not working by checking status code 200 so test httplib2
#import httplib2

import pandas as pd # read html results from webpage to determine if player played season

import numpy as np # mean, median

import generator # gen prob stat reached to determine prob from records
import converter # convert names to abbrevs while determining conditions order

# if streak resembles pattern we have seen consistently such as 3/3,3/4,4/5,5/6,6/7,6/9,7/10
def determine_consistent_streak(stat_counts, stat_name=''):
    print("\n===Determine Consistent Streak===\n")
    print("stat_counts: " + str(stat_counts))
    consistent = False

    super_strict_streak = True # only 7/7,9/10 and above
    strict_streak = True
    

    # even if it is consistent it does not mean they will hit it next game
    # instead we must determine if likely to hit next game based on previous game pattern

    if super_strict_streak:
        if len(stat_counts) > 1:
            # if 100%, no matter length of streak
            if stat_counts[1] != 1: # avoid 1/2
                if len(stat_counts) > 3:
                    if stat_counts[3] != 2: # avoid 2/4
                        if stat_name != 'reb': # except reb bc too random
                            if len(stat_counts) > 6: 
                                if stat_counts[6] == 7 or stat_counts[6] == 0: # 7/7 or 0/7 bc key number 7 except reb bc too random
                                    consistent = True
                        if len(stat_counts) > 9:
                            if stat_counts[9] > 8 or stat_counts[9] < 2: # 9/10,10/10 or 1/10,0/10
                                consistent = True
    elif strict_streak:
        if len(stat_counts) > 1:
            # if 100%, no matter length of streak
            final_count = stat_counts[-1]
            final_total = len(stat_counts)
            if final_count == final_total or final_count == 0: # eg 1/1,3/3,13/13 etc or 0/10, etc
                consistent = True
            elif stat_counts[1] != 1: # avoid 1/2
                if len(stat_counts) > 3:
                    if stat_counts[3] != 2: # avoid 2/4
                        if len(stat_counts) > 6: 
                            if stat_counts[6] == 7 or stat_counts[6] == 0: # 7/7 or 0/7 bc key number 7
                                consistent = True
                        if len(stat_counts) > 9:
                            if stat_counts[9] > 7 or stat_counts[9] < 3: # 8/10,9/10,10/10 or 2/10,1/10,0/10
                                consistent = True
                
    else:
        if len(stat_counts) >= 10:
            if stat_counts[9] >= 7: # arbitrary 7/10
                consistent = True
            elif stat_counts[9] <= 3: # arbitrary 7/10
                consistent = True

            if stat_counts[2] == 3: # arbitrary 3/3
                consistent = True
            elif stat_counts[2] == 0: # arbitrary 0/3
                consistent = True
        elif len(stat_counts) >= 7: # 5 <= x <= 10
            if stat_counts[6] <= 1 or stat_counts[6] >= 6: # arbitrary 1/7 or 6/7
                consistent = True
        elif len(stat_counts) == 4: # x=4
            if stat_counts[3] == 4 or stat_counts[3] == 0: # arbitrary 4/4 or 0/4. if only 4 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True
        elif len(stat_counts) == 3: # x=3
            if stat_counts[2] == 3 or stat_counts[2] == 0: # arbitrary 3/3. if only 3 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True
        elif len(stat_counts) == 2: # x=2
            if stat_counts[1] == 2 or stat_counts[1] == 0: # arbitrary 2/2. if only 2 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True

    if consistent:
        print('consistent')

    return consistent

# streak is in form of prediction dictionary
def determine_high_streak(streak_dict):
    #print('\n===Determine High Streak===\n')
    #print('streak_dict: ' + str(streak_dict))

    high_streak = False

    # if overall record is 1/2 and less than 9/10 then not high streak unless another condition has perfect record
    #overall_record = streak_dict['overall record']
    #if overall_record[1] < 2: #0/2,1/2

    streak = streak_dict['streak']
    #print('streak: ' + str(streak))

    #if 100% or 0, eg 10/10 or 0/y
    final_count = int(streak[-1].split('/')[0])
    final_total = int(streak[-1].split('/')[1])
    if final_count == final_total: # eg 13/13 or 3/3
        high_streak = True
    elif final_count == 0: # 0/y
        high_streak = True
    elif len(streak) > 9: # 9/10, 1/10
        count_10 = int(streak[9].split('/')[0])
        count_7 = int(streak[6].split('/')[0])
        if count_10 > 8 or count_10 < 2:
            high_streak = True
        elif count_7 == 7 or count_7 == 0:
            high_streak = True

    # if high_streak:
    #     print('high_streak')

    return high_streak


# determine high streaks which are 10/10, 9/10 and combined streaks like 4/4,8/10
def determine_high_streaks(all_valid_streaks_list):
    print('\n===Determine High Streaks===\n')
    high_streaks = []

    for streak in all_valid_streaks_list:

        if determine_high_streak(streak):
            high_streaks.append(streak)

    if len(high_streaks) == 0:
        print('Warning: No High Streaks! ')

    print('high_streaks: ' + str(high_streaks))
    return high_streaks

def determine_col_name(keyword,data):
    #print("\n===Determine Column Name===\n")

    final_col_name = '' # eg PTS or Sort: PTS
    for col_name in data.columns:
        if re.search(keyword.lower(),col_name.lower()):
            final_col_name = col_name
            break

    #print("final_col_name: " + final_col_name)
    return final_col_name




























def determine_cur_team(year, cur_yr, team_idx):

    cur_team = False

    if year == cur_yr and team_idx == 0:
        cur_team = True

    return cur_team 



# 1 falls in range 0-4 bc includes 4
def determine_stat_range(val, stat):
    #print("\n===Determine Stat Range: " + str(val) + " " + stat + "===\n")

    set_range = 5
    if stat == 'pts':
        set_range = 10

    min_val = 0
    max_val = set_range - 1
    #val_range = min_val + '-' + max_val

    while val > max_val:

        min_val += set_range
        max_val += set_range


    val_range = str(min_val) + '-' + str(max_val)



    # max_val = set_range

    # while val < max_val:

    #     min_val = 0
    #     max_val = set_range - 1
    #     if val > min_val and val < max_val:
    #         val_range = 

    #     set_range += set_range

    #print("val_range: " + str(val_range))
    return val_range


def determine_team_name(team_abbrev, team_abbrevs_dict={}):
    #print("\n===Determine Team Name: " + team_abbrev + "===\n")
    team_abbrevs_dict = {'atl':'atlanta hawks', 
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
    
    irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nor':'nop', 'pho':'phx', 'was':'wsh', 'uth': 'uta', 'utah': 'uta' } # for these match the first 3 letters of team name instead

    team_name = ''
    for abbrev, name in team_abbrevs_dict.items():
        #print('name: ' + str(name))
        if re.search(team_abbrev.lower(),abbrev): # abbrev may be irregular
            #print('found match')
            team_name = name
            break

    #print("team_name: " + str(team_name))
    return team_name

def determine_team_abbrev(team_name, team_abbrevs_dict={}):
    #print("\n===Determine Team Abbrev: " + team_name + "===\n")
    team_abbrevs_dict = {'atl':'atlanta hawks', 
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
                    'lac':'los angeles clippers',
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

    team_abbrev = ''
    # problem with LA Clippers bc space is considered uppercase
    if team_name.lower() == 'la clippers':
        team_abbrev = 'lac'
    elif team_name.lower() == 'la lakers':
        team_abbrev = 'lal'
    elif team_name[:3].isupper(): 
        #print('first 3 letters uppercase')
        team_abbrev = team_name[:3].lower()

        irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nor':'nop', 'pho':'phx', 'was':'wsh', 'uth': 'uta', 'utah': 'uta' } # for these match the first 3 letters of team name instead
        if team_abbrev in irregular_abbrevs.keys():
            #print("irregular abbrev: " + team_abbrev)
            team_abbrev = irregular_abbrevs[team_abbrev]
    else:
        for abbrev, name in team_abbrevs_dict.items():
            #print('name: ' + str(name))
            if re.search(team_name.lower(),name): # name is full name but we may be given partial team name
                #print('found match')
                team_abbrev = abbrev
                break

        # if we only have the abbrevs in list we can determine team name by structure
        # for abbrev in team_abbrevs:
        #     # see if abbrev in first 3 letters of name, like atl in atlanta
        #     if re.search(abbrev, team_name[:3].lower()):
        #         team_abbrev = abbrev
        #         break
        # # if abbrev not first 3 letters of name, check initials like nop, lal, lac
        # if team_abbrev == '':
        #     initials = [ s[0] for s in team_name.lower().split() ]
        #     for abbrev in team_abbrevs:
        #         if abbrev == initials:
        #             team_abbrev = abbrev
        #             break
        # # if abbrev not first 3 letters nor initials, then check 1st 2 letters like phx and okc
        # if team_abbrev == '':
        #     for abbrev in team_abbrevs:
        #         if re.search(abbrev[:2], team_name[:2].lower()):
        #             team_abbrev = abbrev
        #             break
        # # check 1st and last letters for bkn brooklyn nets
        # if team_abbrev == '':
        #     initials = [ s[0] for s in team_name.lower().split() ]
        #     for abbrev in team_abbrevs:
        #         first_last = abbrev[0] + abbrev[-1]
        #         if first_last == initials:
        #             team_abbrev = abbrev
        #             break

    #print("team_abbrev: " + str(team_abbrev))
    return team_abbrev

def determine_all_team_abbrevs(position_matchup_data):
    #print("\n===Determine All Team Abbrevs===\n")
    team_abbrevs = []
    for team_idx, row in position_matchup_data.iterrows():
        team_col_name = determine_col_name('team',position_matchup_data)
        team_name = str(position_matchup_data.loc[team_idx, team_col_name])
        if team_name[:3].isupper():
            team_abbrev = team_name[:3].lower()
            # correct irregular abbrevs
            irregular_abbrevs = {'bro':'bkn', 'okl':'okc'} # for these match the first 3 letters of team name instead
            # if team_abbrev == 'bro':
            #     team_abbrev = 'bkn'
            if team_abbrev in irregular_abbrevs.keys():
                team_abbrev = irregular_abbrevs[team_abbrev]

            team_abbrevs.append(team_abbrev)

    #print("team_abbrevs: " + str(team_abbrevs))
    return team_abbrevs

# rating or ranking bc shows average value and orders from easiest ot hardest by position and stat
def determine_matchup_rating(opponent, stat, all_matchup_data):
    print("\n===Determine Matchup Rating for " + opponent.upper() + ", " + stat + "===\n")
    if stat == '3pm':
        stat = '3p'
    

    positions = ['pg','sg','sf','pf','c']
    all_matchup_ratings = { 'pg':{}, 'sg':{}, 'sf':{}, 'pf':{}, 'c':{} } # { 'pg': { 'values': [source1,source2,..], 'ranks': [source1,source2,..] }, 'sg': {}, ... }
    #position_matchup_rating = { 'values':[], 'ranks':[] } # comparing results from different sources

    #team_abbrevs = []
    for source_matchup_data in all_matchup_data:
        #print("source_matchup_data: " + str(source_matchup_data))

        for position_idx in range(len(source_matchup_data)):
            position_matchup_data = source_matchup_data[position_idx]
            position = positions[position_idx]

            stat_col_name = determine_col_name(stat,position_matchup_data)

            # get all values for stat and sort so we can rank current team
            all_stat_vals = []
            for team_idx, row in position_matchup_data.iterrows():
                
                
                col_val = position_matchup_data.loc[team_idx, stat_col_name]
                stat_val = reader.format_stat_val(col_val)
                #print("stat_val: " + str(stat_val))
                all_stat_vals.append(stat_val)

            #print("all_stat_vals: " + str(all_stat_vals))
            all_stat_vals.sort()
            #print("all_stat_vals: " + str(all_stat_vals))

            # get all team abbrevs from source using abbrevs so we can relate name to abbrevs for sources only giving full name
            # if len(team_abbrevs) == 0:
            #     team_abbrevs = determine_all_team_abbrevs(position_matchup_data)
            
                

            for team_idx, row in position_matchup_data.iterrows():

                # for fantasypros.com source, format OKCoklahoma city, so take first 3 letters
                # for hashtag bball source, format OKC <rank>, so take first 3 letters also
                # but the header name is 'Sort: Team' not just 'Team'
                # team_col_name = 'Team'
                # for col_name in position_matchup_data.columns:
                #     if re.search('team',col_name.lower()):
                #         team_col_name = col_name
                team_col_name = determine_col_name('team',position_matchup_data)
                team_name = str(position_matchup_data.loc[team_idx, team_col_name])
                #print("team_name: " + team_name)
                team = determine_team_abbrev(team_name) # fantasy pros gives both name and abbrev together so use that source to make dict
                #print("team: " + team)
                #print("opponent: " + opponent)

                #if opponent in different_abbrevs:

                if team == opponent:

                    #stat_col_name = determine_col_name(stat,position_matchup_data)
                    #stat_val = float(position_matchup_data.loc[team_idx, stat_col_name])
                    col_val = position_matchup_data.loc[team_idx, stat_col_name]
                    stat_val = reader.format_stat_val(col_val)
                    rank = all_stat_vals.index(stat_val) + 1

                    position_matchup_rating = all_matchup_ratings[position]
                    if 'averages' in position_matchup_rating.keys():
                        position_matchup_rating['averages'].append(stat_val)

                        position_matchup_rating['ranks'].append(rank)
                    else:
                        position_matchup_rating['averages'] = [stat_val]

                        position_matchup_rating['ranks'] = [rank]
                    
                    

                    break # found team so move to next position

    #print("all_matchup_ratings: " + str(all_matchup_ratings))                  
    return all_matchup_ratings

# exclude all star and other special games
def determine_prev_game_date(player_game_log, season_year):
    print('\n===Determine Prev Game Date from Game Log===\n')
    #print('player_game_log:\n' + str(player_game_log))
    # if not all star
    prev_game_idx = 0
    while re.search('\\*', player_game_log.loc[str(prev_game_idx), 'OPP']):
        prev_game_idx += 1

    init_game_date_string = player_game_log.loc[str(prev_game_idx), 'Date'].split()[1] # 'wed 2/15'
    game_mth = init_game_date_string.split('/')[0]
    final_season_year = str(season_year)
    if int(game_mth) in range(10,13):
        final_season_year = str(season_year - 1)
    prev_game_date_string = init_game_date_string + "/" + final_season_year


    #prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + str(season_year) # eg 'wed 2/15' to '2/15/23'
    prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%Y')
    return prev_game_date_obj







# is it an over or under? above 7/10 or 4/5 or 3/3, or below 3/10 and not 2/2 bc maybe teammate injury so more playing time?
def determine_streak_direction(streak):
    direction = '+'

    final_count = int(streak[-1].split('/')[0])
    final_total = int(streak[-1].split('/')[1])
    if final_count == final_total:
        direction = '+'
    elif final_count == 0:
        direction = '-'
    else:

        # 1st idx header like [pts 10+,1/1,2/2,..]
        out_of_10 = 0
        out_of_5 = 0
        out_of_3 = 0
        out_of_2 = 0
        if len(streak) > 10:
            out_of_10 = int(streak[10].split('/')[0])
        if len(streak) > 5:
            out_of_5 = int(streak[5].split('/')[0])
        if len(streak) > 3:
            out_of_3 = int(streak[3].split('/')[0])
        if len(streak) > 2:
            out_of_2 = int(streak[2].split('/')[0])

        if out_of_10 >= 7 or out_of_5 >= 4 or out_of_3 >= 3:
            direction = '+'
        elif out_of_10 <= 3 and out_of_2 < 2: # if 3/10 but 2/2 then maybe recent change causing beginning of over streak
            direction = '-'
        elif out_of_3 == 0:
            direction = '-'

    


    return direction

# streak has header element
def determine_streak_outline(streak):
    #print("\n===Determine Streak Outline===\n")
    #print(record)
    outline = []

    outline_idxs = [0,1,2,3,4,5,6,7,8,9,14,19,29,49]

    for game_idx in range(len(streak[1:])):
        game = streak[game_idx+1] # record has header at idx 0
        if game_idx in outline_idxs:
            outline.append(game)

    #print('outline: ' + str(outline))
    return outline

def determine_record_outline(record):
    #print("\n===Determine Record Outline===\n")
    #print(record)
    outline = []

    outline_idxs = [0,1,2,3,4,5,6,7,8,9,14,19,29,49]

    for game_idx in range(len(record)):
        game = record[game_idx] # record has header at idx 0
        if game_idx in outline_idxs:
            outline.append(game)

    #print('outline: ' + str(outline))
    return outline

# mean, corrected mean, combined mean
# matchup_dict = { pg: { s1: 0, s2: 0, .. }, sg: { s1: 0 }, .. }
def determine_rank_avgs(pos, matchup_dict):

    # combined mean is enough to cancel error when determining which position player is
    rank_avgs = {'mean':0, 'combined mean':0} # add corrected mean which checks to see which position the sources agree with most


    pos_matchup_ranks = [matchup_dict[pos]['s1'],matchup_dict[pos]['s2'],matchup_dict[pos]['s3']]

    rank_avgs['mean'] = converter.round_half_up(np.mean(np.array(pos_matchup_ranks)))

    alt_pos = 'c' # if listed pos=pg then combine with guard bc sometimes play both
    if pos == 'pg':
        alt_pos = 'sg'
    elif pos == 'sg':
        alt_pos = 'pg'
    elif pos == 'sf':
        alt_pos = 'pf'
    elif pos == 'pf':
        alt_pos = 'sf'
    alt_pos_matchup_ranks = [matchup_dict[alt_pos]['s1'],matchup_dict[alt_pos]['s2'],matchup_dict[alt_pos]['s3']]
    rank_avgs['combined mean'] = converter.round_half_up(np.mean(np.array(pos_matchup_ranks+alt_pos_matchup_ranks)))


    return rank_avgs

def determine_all_player_names(raw_projected_lines):
    print('\n===Determine All Player Names===\n')
    # get all player names so we can get their espn IDs and from that get team, position, game log, and schedule
    player_names = []
    player_initials = ['og','cj','pj','rj','tj','jt','jd']
    for row in raw_projected_lines:
        first_element_wo_punctuation = re.sub('\'|\.','',row[0])
        if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na': # uppercase indicates team abbrev like CHI
            #print('found player line')
            if not first_element_wo_punctuation[:3].isupper(): # allow if first 3 letters uppercase but one of them is apostrphe in player name like D'Angelo
                player_names.append(row[0].lower())
            elif first_element_wo_punctuation[:2].lower() in player_initials: # if uppercase but player initials
                player_names.append(row[0].lower())

    # check for players with no points line but rebounds line
    for row in raw_projected_lines:
        if len(row) > 3:
            first_element_wo_punctuation = re.sub('\'|\\.','',row[3])
            if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na': # uppercase indicates team abbrev like CHI
                #print('found player line')

                
                player_name = row[3].lower() #keep punctuation in key
                if not first_element_wo_punctuation[:3].isupper(): 
                    if player_name not in player_names:
                        print('found player with no pts line: ' + player_name)
                        player_names.append(player_name)
                elif first_element_wo_punctuation[:2].lower() in player_initials: # if uppercase but player initials
                    if player_name not in player_names:
                        print('found player with no pts line: ' + player_name)
                        player_names.append(player_name)

    #print("player_names: " + str(player_names))
    return player_names

# may come in format away: [record] so split and convert string to list
def determine_record_score(record):
    print('\n===Determine Record Score===\n')
    print('record: ' + str(record))
    score = 0
    

    # if 0/2,1/4,4/10, then -1
    # if 2/2,2/4,4/10, then 0 bc recent success
    # if 2/2,2/4,2/10, then still 0 bc recent success
    stat_counts = [] # [0,0,1,..]
    for partial_record in record:
        stat_count = int(partial_record.split('/')[0])
        stat_counts.append(stat_count)
    #print('stat_counts: ' + str(stat_counts))

    if len(record) > 0:
        final_count = stat_counts[-1]
        final_total = int(record[-1].split('/')[1])
        #print('final_count: ' + str(final_count))
        #print('final_total: ' + str(final_total))
        if final_count == final_total:
            score = 1
        elif final_count == 0:
            score = -1
        else:
            #print('check record not 0 or 100')
            if len(record) > 4: # 1/5
                if stat_counts[4] < 2:
                    score = -1

            if len(record) > 7: 
                if stat_counts[1] == 0 and stat_counts[7] < 3: # 0/2,2/8
                    score = -1

            if len(record) > 8: 
                if stat_counts[1] == 0 and stat_counts[3] < 3 and stat_counts[8] < 4: # 0/2,2/4,3/9
                    score = -1

            if len(record) > 9:
                #print('length of record > 9')
                #print('stat_counts[1]: ' + str(stat_counts[1]))

                # negative score
                if stat_counts[1] == 0 and stat_counts[9] < 5: # 0/2,4/10
                    score = -1
                elif stat_counts[2] == 0 and stat_counts[9] < 7: # 0/3,6/10
                    score = -1
                elif stat_counts[1] < 2 and stat_counts[9] < 3: # 1/1,1/2,1/5,2/10
                    score = -1
                elif stat_counts[0] == 0 and stat_counts[1] < 2 and stat_counts[4] < 3 and stat_counts[9] < 5: # 0/1,1/2,2/5,4/10
                    score = -1

                # positive score
                elif stat_counts[6] == 7: # 7/7,7/10
                    score = 1
                elif stat_counts[1] == 2 and stat_counts[4] > 3 and stat_counts[9] > 7: # 2/2,4/5,8/10
                    score = 1
                elif len(record) > 10:
                    print('length of record > 10') # since record outline, must check total in denominator to be sure we are referring to correct stat count bc if greater than 15 samples we use outline skipping some samples so see determine record outline fcn
                    if stat_counts[1] > 0 and stat_counts[3] > 1 and stat_counts[4] > 2 and stat_counts[9] > 7 and stat_counts[10] > 10: # 1/2,2/4,3/5,8/10,11/15
                        score = 1
                    
                    elif stat_counts[3] == 4 and stat_counts[9] > 6 and stat_counts[10] > 11: # 4/4,7/10,12/15
                        score = 1

                    elif stat_counts[1] == 2 and stat_counts[9] > 6 and stat_counts[10] > 12: # 2/2,7/10,13/15
                        score = 1

                    elif stat_counts[1] == 2 and stat_counts[4] > 2 and stat_counts[9] > 5 and stat_counts[10] > 12: # 2/2,3/5,6/10,13/15
                        score = 1


                    # elif stat_counts[1] == 2:
                    #     if stat_counts[9] > 6: # 2/2,7/10
                    #         score = 1
                    #     elif stat_counts[4] > 2 and stat_counts[9] > 5: # 2/2,3/5,6/10
                    #         score = 1
                    # elif stat_counts[6] == 7 and stat_counts[9] > 6: # 7/7,7/10 if we want to do 2/2,8/10 instead above more strict
                    #     score = 1

    

    print('score: ' + str(score))
    return score

def determine_average_range_score(prediction, median, mode):
    print('\n===Determine Average Range Score===\n')
    score = 0

    prediction_stat_val = int(re.sub('[+-]','',prediction.split()[-2]))
    print('prediction_stat_val: ' + str(prediction_stat_val))
    print('median: ' + str(median))
    print('mode: ' + str(mode))
    
    # assuming streak direction positive/over bc later we will reverse for under
    # if median or mode are greater than player line, and the other is not below line, score +1
    # if one at or above line and the other above, then score +1
    if median - prediction_stat_val > 0 and not mode - prediction_stat_val < 0:
        score = 1
    elif mode - prediction_stat_val > 0 and not median - prediction_stat_val < 0:
        score = 1
    # if median or mode less than player line, and the other is not above line, score -1.
    # if one at or below line and the other below, then score -1
    elif median - prediction_stat_val < 0 and not mode - prediction_stat_val > 0: 
        score = -1
    elif mode - prediction_stat_val < 0 and not median - prediction_stat_val > 0:
        score = -1
    

    print('score: ' + str(score))
    return score

# give streak prediction, a degree of belief score based on all streaks, avgs, range, matchup, location, and all other conditions
def determine_degree_of_belief(streak):

    print('\n===Determine Degree of Belief===\n')
    print('streak: ' + str(streak))

    deg_of_bel = 0

    prediction = streak['prediction'] # eg 'julius randle 10+ reb'
    print('prediction: ' + str(prediction))

    # use streak direction to determine if matchup and location are good or bad for prediction
    streak_direction = re.sub('\d','',prediction.split()[-2]) # + or -
    print('streak_direction: ' + streak_direction)

    # if matchup info is given then score matchup
    matchup_score = 0
    if 's1 matchup' in streak.keys():

        matchup_mean = streak['matchup mean']
        if matchup_mean > 20: # if easy matchup >20/30
            matchup_score = 1
            # if streak_direction == '+': # and projected over, then matchup score +1
            #     matchup_score = 1
            # else: # but projected under, then matchup score -1 bc projected under but easy matchup so they could over
            #     matchup_score = -1
        elif matchup_mean < 10: # if hard matchup <10/30
            matchup_score = -1
            # if streak_direction == '+': # but projected over, then matchup score -1
            #     matchup_score = -1
            # else: # and projected under, then matchup score +1 bc projected under and hard matchup so they should go under
            #     matchup_score = 1
        
    print('matchup_score: ' + str(matchup_score))

    # if home and over then +1, etc
    location_score = 0
    location = streak['location record'].split(':')[0]
    print('location: ' + str(location))
    if location == 'home':
        location_score = 1
    else:
        location_score = -1
    #     if streak_direction == '+': # and projected over, then loc score +1
    #         location_score = 1
    #     else: # but projected under, then loc score -1 bc projected under but easy loc so they could over
    #         location_score = -1
    # else: # away
    #     if streak_direction == '+': # but projected over, then loc score -1
    #         location_score = -1
    #     else: # and projected under, then loc score +1 bc projected under and hard loc so they should go under
    #         location_score = 1
    print('location_score: ' + str(location_score))

    all_record_score = determine_record_score(streak['overall record'])
    # if re.search(':',record):
    #     record = list(streak['location record'].split(':')[1].strip())
    #     print('corrected record: ' + str(record))

    location_record_string = re.sub('\'','',streak['location record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
    location_record = location_record_string.strip('][').split(', ')
    #print('loc_record: \'' + str(location_record) + '\'')
    loc_record_score = determine_record_score(location_record)

    opp_record_score = 0
    if len(streak['opponent record']) > 0:
        opp_record_string = re.sub('\'','',streak['opponent record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        opp_record = opp_record_string.strip('][').split(', ')
        opp_record_score = determine_record_score(opp_record)

    time_after_record_score = 0
    if len(streak['time after record']) > 0:
        time_after_record_string = re.sub('\'','',streak['time after record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        time_after_record = time_after_record_string.strip('][').split(', ')
        time_after_record_score = determine_record_score(time_after_record)

    dow_record_score = 0
    if len(streak['day record']) > 0:
        dow_record_string = re.sub('\'','',streak['day record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        dow_record = dow_record_string.strip('][').split(', ')
        dow_record_score = determine_record_score(dow_record)

    overall_median = streak['overall median']
    overall_mode = streak['overall mode']
    all_avg_score = determine_average_range_score(prediction, overall_median, overall_mode)

    loc_median = streak['location median']
    loc_mode = streak['location mode']
    loc_avg_score = determine_average_range_score(prediction, loc_median, loc_mode)

    opp_avg_score = 0
    if streak['opponent median'] != '':
        opp_median = streak['opponent median']
        opp_mode = streak['opponent mode']
        opp_avg_score = determine_average_range_score(prediction, opp_median, opp_mode)

    time_after_avg_score = 0
    if streak['time after median'] != '':
        time_after_median = streak['time after median']
        time_after_mode = streak['time after mode']
        time_after_avg_score = determine_average_range_score(prediction, time_after_median, time_after_mode)

    dow_avg_score = 0
    if streak['day median'] != '':
        dow_median = streak['day median']
        dow_mode = streak['day mode']
        dow_avg_score = determine_average_range_score(prediction, dow_median, dow_mode)

    sub_scores = [matchup_score, location_score, all_record_score,loc_record_score,opp_record_score,time_after_record_score,dow_record_score,all_avg_score,loc_avg_score,opp_avg_score,time_after_avg_score,dow_avg_score]
    print('sub_scores: ' + str(sub_scores))
    corrected_sub_scores = []
    # reverse scores for negative direction/unders
    for score in sub_scores:
        if streak_direction == '-':
            score = score * -1
        corrected_sub_scores.append(score)

    print('corrected_sub_scores: ' + str(corrected_sub_scores))


    deg_of_bel = 0 #matchup_score + location_score + all_record_score + loc_record_score + opp_record_score + time_after_record_score + dow_record_score + all_avg_score + loc_avg_score + opp_avg_score + time_after_avg_score + dow_avg_score
    for score in corrected_sub_scores:
        deg_of_bel += score

    print('deg_of_bel: ' + str(deg_of_bel))
    return deg_of_bel

def determine_all_degrees_of_belief(streaks):
    degrees_of_belief = {}

    for streak in streaks:

        deg_of_bel = determine_degree_of_belief(streak)

        prediction = streak['prediction'] # eg 'julius randle 10+ reb'

        degrees_of_belief[prediction] = deg_of_bel # eg 7

    return degrees_of_belief

# prediction is really a list of features that we must assess to determine the probability of both/all outcomes
# similar to determine degree of belief above but restructured
def determine_probability_of_prediction(prediction):
    prob = 0

    return prob


# change prediction dictionary to outcome features bc we are not predicting
# we are determining the prob of an outcome given the features
# eg prob player scores 10+p given stats, records, avg, range, matchups, etc
# features = {possible outcome:'', record:[], ..}
def determine_probability_of_outcome(features):
    prob = 0

    return prob


# need to weigh recent samples more
# and weigh samples more or less based on specific circumstances like teammates
# but that may come at the next step when accounting for all conditions
# record = ['1/1','2/2',..]
# weigh samples after trade much more than before
def determine_probability_from_record(record, games_traded=0):
    #prob = 0

    # most basic is take ratio of all samples
    count = int(record[-1].split('/')[0])
    total = int(record[-1].split('/')[1])

    # weigh 10,50: 0.5,0.5
    # weigh 3,5,7,10,13,15,20,30,50: 0.2,0.1,0.1,0.1,..
    # determine weights of sample ranges based on no. samples


    # display as percentage
    prob = converter.round_half_up(count * 100 / total) # eg 10 * 100 / 20 = 50

    print('prob: ' + str(prob))
    return prob



# determine if the given list of current teammates is in a given game of interest
# if we do not know current teammates yet then assume yet so we show all options
# teammates = ['j brown sg',..]
def determine_current_teammates_in_game(game_teammates, current_teammates):
    
    current_teammates_in_game = game_teammates

    #if len(current_teammates) > 0:
        # how do we tell if players on the roster are out of rotation? from their game log minutes



    return current_teammates_in_game








#if condition in current_conditions or min_prev_stat_val <= cur_prev_stat_val <= max_prev_stat_val:
def determine_valid_condition(condition, current_conditions, cur_prev_stat_val, min_prev_stat_val, max_prev_stat_val):

    valid = False

    if condition in current_conditions:
        valid = True
    elif re.search('prev', condition) and min_prev_stat_val <= cur_prev_stat_val <= max_prev_stat_val: # 0-4 prev
        valid = True

    return valid




# make list to loop through so we can add all stats to dicts with 1 fcn
# list order or keys must correspond with all_stats_dicts bc we assign by idx/key
def determine_game_stats(player_game_log, game_idx):

    # === Collect Stats for Current Game ===

    pts = int(player_game_log.loc[game_idx, 'PTS'])
    reb = int(player_game_log.loc[game_idx, 'REB'])
    ast = int(player_game_log.loc[game_idx, 'AST'])

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
    fg_rate = converter.round_half_up(float(player_game_log.loc[game_idx, 'FG%']), 1)

    #threes = game[three_idx]
    #threes_data = threes.split('-')
    #print("threes_data: " + str(threes_data))
    threes_made = int(player_game_log.loc[game_idx, '3PT_SA'])
    threes_attempts = int(player_game_log.loc[game_idx, '3PT_A'])
    three_rate = converter.round_half_up(float(player_game_log.loc[game_idx, '3P%']), 1)

    fts = player_game_log.loc[game_idx, 'FT']
    ft_data = fts.split('-')
    ftm = int(ft_data[0])
    fta = int(ft_data[1])
    ft_rate = converter.round_half_up(float(player_game_log.loc[game_idx, 'FT%']), 1)

    stl = int(player_game_log.loc[game_idx, 'STL'])
    blk = int(player_game_log.loc[game_idx, 'BLK'])

    fs = int(player_game_log.loc[game_idx, 'PF'])
    tos = int(player_game_log.loc[game_idx, 'TO'])

    # Stat Combos
    pts_reb = pts + reb
    pts_ast = pts + ast
    reb_ast = reb + ast
    pts_reb_ast = pts + reb + ast
    stl_blk = stl + blk

    # make list to loop through so we can add all stats to dicts with 1 fcn
    game_stats = [pts,reb,ast,pts_reb,pts_ast,reb_ast,pts_reb_ast,stl,blk,stl_blk,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,fs,tos] 

    return game_stats


def determine_matching_key(dict, match_val):

    print('\n===Determine Match Key for Val: ' + str(match_val) + '===\n')
    print('dict: ' + str(dict))

    match_key = ''

    for key, val in dict.items():
        if key != 'ok val':
            if val == match_val and re.search('post.*val',key):
                match_key = key

    print('match_key: ' + match_key)
    return match_key

# see portion of times player reaches stat
# player_stat_records: {'all': {2023: {'regular': {'pts': ['6/6',...
# shows fraction of times stat reached
def determine_prob_of_stat_from_records(ok_val, player_stat_records, season_part, stat_name, condition='all', season_year=2024):
    
    print('\n===Determine Prob of Stat: ' + str(ok_val) + ' ' + stat_name + '===\n')
    #print('player_stat_records: ' + str(player_stat_records))
    prob_of_stat = 0

    print('condition: ' + condition)
    print('season_year: ' + str(season_year))
    print('season_part: ' + season_part)

    # iso for a given year
    year_stat_records = player_stat_records[condition][season_year]
    if season_part in year_stat_records.keys():
        records = year_stat_records[season_part][stat_name]
        print('records: ' + str(records))
        record = ''
        if len(records) > ok_val:
            record = records[ok_val]
        else:
            print('Warning: Stat not in Records! Maybe it is in Reg Season but not in Playoffs!')
        print('record: ' + str(record))

        prob_of_stat = generator.generate_prob_stat_reached(record)         

    print('prob_of_stat: ' + str(prob_of_stat))
    return prob_of_stat

def determine_ok_val_prob(dict, ok_val, player_stat_records, season_part, stat_name, season_year=2024):

    print('\n===Determine Postseason Prob for OK Value: ' + str(ok_val) + ' ' + stat_name + '===\n')

    ok_val_post_val_key = determine_matching_key(dict, ok_val) #'post prob val'

    ok_val_post_prob_key = '' #re.sub('val','',ok_val_post_val_key).strip()

    ok_val_post_prob = 0

    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    if ok_val_post_val_key == '':
        # we can find post prob from stat records
        ok_val_post_prob = determine_prob_of_stat_from_records(ok_val, player_stat_records, season_part, stat_name, season_year=season_year)
        ok_val_post_prob = converter.round_half_up(ok_val_post_prob * 100)
    else:
        ok_val_post_prob_key = re.sub('val','',ok_val_post_val_key).strip()

        if ok_val_post_prob_key in dict.keys():
            ok_val_post_prob = dict[ok_val_post_prob_key]

    
    print('ok_val_post_prob: ' + str(ok_val_post_prob))
    return ok_val_post_prob


def determine_ok_val_margin(dict, ok_val, player_stat_dict, stat_name, margin_type='min'):

    print('\n===Determine Postseason Margin for OK Value: ' + str(ok_val) + ' ' + stat_name + '===\n')

    ok_val_post_val_key = determine_matching_key(dict, ok_val) #'post prob val'

    ok_val_post_margin_key = '' #re.sub('val','',ok_val_post_val_key).strip()

    ok_val_post_margin = 0

    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    if ok_val_post_val_key == '':
        # we can find post prob from stat records
        ok_val_post_margin = generator.generate_margin(ok_val, player_stat_dict, margin_type)
    else:
        margin_key = margin_type + ' margin'
        ok_val_post_margin_key = re.sub('prob val',margin_key,ok_val_post_val_key).strip()
        print('ok_val_post_margin_key: ' + str(ok_val_post_margin_key))

        if ok_val_post_margin_key in dict.keys():
            ok_val_post_margin = dict[ok_val_post_margin_key]

    print('ok_val_post_margin: ' + str(ok_val_post_margin))
    return ok_val_post_margin

# stat available in odds at given value
def determine_stat_available(stat_dict):
    stat_available = True

    # get webpage from player name to get team page

    return stat_available

# we need to get all conditions for all players
# so table lines up if players did not all play in same conditions
#all_stat_probs_dict: {'luka doncic': {'pts': {0: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
def determine_all_conditions(all_stat_probs_dict):
    print('\n===Determine All Conditions===\n')

    all_conditions = []

    # player_stat_probs_dict: {'pts': {0: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
    for player_stat_probs_dict in all_stat_probs_dict.values():
        # all stats should have same conditions bc stat recorded at every value
        # so we can take first stat probs dict
        # bc it is for a single player, we know they got at least 1 stat (even 0s) under every condition they played in by definition
        
        # stat_probs_dict: {0: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
        #for stat_probs_dict in player_stat_probs_dict.values():
        stat_prob_dicts = list(player_stat_probs_dict.values())
        if len(stat_prob_dicts) > 0:
            stat_probs_dict = stat_prob_dicts[0]
            
            # we need to loop thru all val probs dicts bc not all vals reached in all conditions
            # and we need to see all conds reached by any val
            # val_probs_dict: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
            # we know it should have same conds for all yrs even if vals not seen under those conds we put NA
            # so we can shorten by only looping thru 1 yr
            for val_probs_dict in stat_probs_dict.values():
                for conditions in val_probs_dict.keys():
                    if conditions not in all_conditions:
                        all_conditions.append(conditions)

    #print('all_conditions: ' + str(all_conditions))
    return all_conditions

# here we use all stats prob dict so we only have to loop thru condition 1 yr
# does that save time since we need to loop thru all yrs anyway?
def determine_all_stat_conds(all_stats_prob_dict):
    #print('\n===Determine All Stat Conds===\n')

    all_stat_conds = []

    for player_stats_prob_dict in all_stats_prob_dict.values():
        # all stats should have same conditions bc stat recorded at every value
        # so we can take first stat probs dict
        # bc it is for a single player, we know they got at least 1 stat (even 0s) under every condition they played in by definition
        
        # stat_probs_dict: {0: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
        #for stat_probs_dict in player_stat_probs_dict.values():
        stats_prob_dict = list(player_stats_prob_dict.values())
        if len(stats_prob_dict) > 0:
            stat_probs_dict = stats_prob_dict[0]
            
            # we need to loop thru all val probs dicts bc not all vals reached in all conditions
            # and we need to see all conds reached by any val
            # val_probs_dict: {'all 2023 regular prob': 0.02, 'all 2023 full prob': 0.02...
            # we know it should have same conds for all yrs even if vals not seen under those conds we put NA
            # so we can shorten by only looping thru 1 yr
            for val_probs_dict in stat_probs_dict.values():
                for conditions in val_probs_dict.keys():
                    if conditions not in all_stat_conds:
                        all_stat_conds.append(conditions)

    return all_stat_conds


# determine sample size for the player stat dict
# so we can assign weight and
# so we can compute true prob weighted avg
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
# cur_conds = {year:year, part:part, cond:cond}
# all stats have same sample size 
# but stat name needed for prev val bc different depending on stat
def determine_sample_size(player_stat_dict, cur_conds, all_players_abbrevs, player_cur_team, opp_team='', stat_name='', prints_on=False, player='', gp_cur_team=None, max_samples=None):
    if prints_on:
        print('\n===Determine Sample Size: ' + player.title() + '===\n')
        print('cur_conds: ' + str(cur_conds))
        print('stat_name: ' + str(stat_name))
        print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
        print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-mem\': \'jaren jackson jr\',...')
        print('Input: player_cur_team = ' + player_cur_team.upper())
        print('Input: opp_team = ' + opp_team.upper())
        print('\nOutput: sample_size = x\n')
    
    sample_size = 0

    condition = cur_conds['condition']
    year = cur_conds['year']
    part = cur_conds['part']
    #stat = 'pts' first val in part_stats dict

    
    if year in player_stat_dict.keys() and part in player_stat_dict[year].keys():
        # all stats have same sample size unless prev val cond
        stat_dict = {}
        if stat_name in player_stat_dict[year][part].keys():
            stat_dict = player_stat_dict[year][part][stat_name]
        else:
            stat_dict = list(player_stat_dict[year][part].values())[0]

        # always need minutes to check if outlier
        minutes_dict = player_stat_dict[year][part]['min']
        #print('minutes_dict: ' + str(minutes_dict))

        # V2: Enable Combos of Abbrevs to get all samples
        # if gp cond then check all versions of abbrev
        # eg og anunoby vs o anunoby
        # only check o anunoby if no og anunoby found???
        # need to check both to find all samples
        # but what if another player is strictly 1 version so rule cannot be generalized
        # so must track irregular abbrevs
            
        # start blank and add all versions of abbrev or combos of abbrevs
        conditions = []
        
        # name might have out in it but if name then also gp cond so true
        if re.search('starters|bench|out', condition): # single or multi player cond
            
            # do not sub opp or out bc names have it inside like toppin and trout 
            # so add space in search
            gp_abbrev = re.sub(' starters| bench| out| opp', ' ', condition).strip()
            #gp_abbrev = re.sub(' out| opp', ' ', condition).strip()
            
            # if prints_on:
            #     print('Found player cond: ' + condition)
            #     print('gp_abbrev: ' + gp_abbrev)

            opp_key = ' opp'

            team_part = condition.split()[-1]

            gp_team = player_cur_team
            if re.search(opp_key, condition):
                gp_team = opp_team

            # multi player conds need to get all combos of abbrevs
            if re.search(',', condition):
                gp_abbrevs = gp_abbrev.split(',')

                # if prints_on:
                #     print('Multiplayer cond')
                #     print('gp_abbrevs before strip: ' + str(gp_abbrevs))

                game_part_players = {}
                for abbrev in gp_abbrevs:
                    #abbrev = abbrev.strip()
                    abbrev_key = abbrev.strip() + '-' + gp_team
                    if abbrev_key in all_players_abbrevs[year].keys():
                        game_player = all_players_abbrevs[year][abbrev_key]
                        # if prints_on:
                        #     print('game_player: ' + game_player)
                        game_part_players[game_player] = converter.convert_player_name_to_abbrevs(game_player, all_players_abbrevs, gp_team, prints_on=prints_on)
                
                combos_of_abbrevs = generator.generate_combos_of_abbrevs(game_part_players)#, all_game_players_abbrevs)
                # if prints_on:
                #     print('combos_of_abbrevs: ' + str(combos_of_abbrevs))

                # need a string for each combo
                
                for abbrev_combo in combos_of_abbrevs:

                    game_part_players_str = converter.convert_to_game_players_str(abbrev_combo)
                    
                    # game part players, where part = starters or bench or out
                    game_part_players_cond_val = game_part_players_str
                    
                    # if opp in cond then add opp to cond so it matches stat dict samples
                    if re.search(opp_key, condition):
                        game_part_players_cond_val += opp_key 
                    game_part_players_cond_val += ' ' + team_part

                    # if prints_on:
                    #     print('abbrev_combo: ' + str(abbrev_combo))
                    #     print('game_part_players_str: ' + str(game_part_players_str))
                    #     print('game_part_players_cond_val: ' + str(game_part_players_cond_val))
                    
                    conditions.append(game_part_players_cond_val)

            else: # single player cond
                
                # get player abbrev from cond
                # by removing group and position from end of cond
                # remove group
                abbrev_key = gp_abbrev + '-' + gp_team
                if prints_on:
                    print('Single player cond')
                    print('abbrev_key: ' + abbrev_key)
                if abbrev_key in all_players_abbrevs[year].keys():
                    game_player = all_players_abbrevs[year][abbrev_key]
                    # use cur team bc cur conds
                    game_player_abbrevs = converter.convert_player_name_to_abbrevs(game_player, all_players_abbrevs, gp_team, prints_on=prints_on)
                    if prints_on:
                        print('game_player: ' + game_player)
                        print('game_player_abbrevs: ' + str(game_player_abbrevs))
                    for abbrev in game_player_abbrevs:
                        gp_cond = abbrev
                        if re.search(opp_key, condition):
                            gp_cond += opp_key 
                        gp_cond += ' ' + team_part
                        if prints_on:
                            print('gp_cond: ' + str(gp_cond))
                        
                        # append string to list
                        conditions.append(gp_cond)



                # irregular_abbrevs = ['og anunoby']
                
                # # remove position
                # #gp_abbrev_data = condition.split()[:-2]
                # gp_abbrev = gp_abbrev.rsplit(' ', 1)[0]#.strip()
                # print('gp_abbrev: ' + gp_abbrev)
                # if gp_abbrev in irregular_abbrevs:
                #     # try all versions of abbrev
                    
                #     # if 2 letters in first name, try version with 1 letter
                #     cond_data = condition.split()
                #     if len(cond_data[0]) > 1:
                #         alt_cond = cond_data[0][0]
                #         for data in cond_data[1:]:
                #             alt_cond += ' ' + data
                #         conditions.append(alt_cond)
                #     print('conditions: ' + str(conditions))
        
            if prints_on:
                print('conditions: ' + str(conditions))
            #sample_size = 0
            for cond in conditions:
                # if prints_on:
                #     print('cond: ' + cond)
                #     print('cond keys: ' + str(list(stat_dict.keys())))
                if cond in stat_dict.keys():
                    if prints_on:
                        print('found cond in stat dict: ' + cond)
                    # cannot take first stat dict bc prev val depends on which stat
                    #stat_dict = list(player_stat_dict[year][part].values())[0][condition]
                    cond_stat_dict = stat_dict[cond]
                    #print('cond_stat_dict: ' + str(cond_stat_dict))
                    # if given gp cur team then cut off before prev team
                    if gp_cur_team is not None:
                        if prints_on:
                            print('gp cur team: ' + str(gp_cur_team))
                        # cannot simply take sample size = gp cur team bc stats in each condition occur irregularly
                        prev_minutes = 0
                        for game_idx in cond_stat_dict.keys():
                            #print('game idx: ' + game_idx)
                            # first instance of cond may already be > gp cur team
                            if int(game_idx) >= gp_cur_team or (max_samples is not None and int(game_idx) >= max_samples):
                                break

                            # IF ensure not outlier 
                            # outlier if < 1/4 prev minutes
                            # 1/4 only applies to minutes
                            # so no matter the stat always check minutes are standard range not outlier
                            minutes = minutes_dict[cond][game_idx]
                            if minutes > prev_minutes / 4:
                                sample_size += 1
                                prev_minutes = minutes
                    else:
                        sample_size += len(cond_stat_dict.keys())

        else: # normal cond only has 1 version
            if condition in stat_dict.keys():
                # cannot take first stat dict bc prev val depends on which stat
                #stat_dict = list(player_stat_dict[year][part].values())[0][condition]
                cond_stat_dict = stat_dict[condition]
                #print('cond_stat_dict: ' + str(cond_stat_dict))
                # take only up to index < gp cur team, if given
                #sample_size = 0
                if gp_cur_team is not None:
                    if prints_on:
                        print('gp cur team: ' + str(gp_cur_team))
                    # cannot simply take sample size = gp cur team bc stats in each condition occur irregularly
                    prev_minutes = 0
                    for game_idx in cond_stat_dict.keys():
                        #print('game idx: ' + game_idx)
                        if int(game_idx) >= gp_cur_team or (max_samples is not None and int(game_idx) >= max_samples):
                            break

                        # IF ensure not outlier 
                        # outlier if < 1/4 prev minutes
                        # 1/4 only applies to minutes
                        # so no matter the stat always check minutes are standard range not outlier
                        minutes = minutes_dict[condition][game_idx]
                        if minutes > prev_minutes / 4:
                            sample_size += 1
                            prev_minutes = minutes

                else:
                    sample_size = len(cond_stat_dict.keys())

        
        
        # V1: normal cond only has 1 version
        # if condition in stat_dict.keys():
        #     # cannot take first stat dict bc prev val depends on which stat
        #     #stat_dict = list(player_stat_dict[year][part].values())[0][condition]
        #     cond_stat_dict = stat_dict[condition]
        #     #print('cond_stat_dict: ' + str(cond_stat_dict))
        #     v1_sample_size = len(cond_stat_dict.keys())
            # if prints_on:
            #     print('v1_sample_size: ' + str(v1_sample_size))

    if prints_on:
        print('sample_size: ' + str(sample_size))
    return sample_size

def determine_probs_sample_size(player_stat_probs_dict, cur_conds):
    sample_size = 0
    
    condition = cur_conds['condition']
    year = cur_conds['year']
    part = cur_conds['part']

    if year in player_stat_probs_dict.keys() and part in player_stat_probs_dict[year].keys() and condition in list(player_stat_probs_dict[year][part].values())[0].keys():
        # stat_dict = list(player_stat_dict[year][part].values())[0][condition]
        # sample_size = len(stat_dict.keys())

        prob = list(player_stat_probs_dict[year][part].values())[0][condition] # x/y
        sample_size = re.split('/', prob)[1] # y

    return sample_size


# list all changed lineups since last run
# init lineups != all lineups
def determine_changed_lineups(init_all_lineups, all_lineups):
    print('\n===Changed Lineups===\n')
    for team, lineup in all_lineups.items():
        if team in init_all_lineups.keys():
            init_team_lineup = init_all_lineups[team]
            if init_team_lineup != lineup:
                print(team.upper())
        else: # team not read last run due to error
            print('Warning: Team lineup not read! ' + team)
    print('\n=====================\n')


def determine_player_benched(player_names, lineup):
    # print('\n===Determine Player Benched===\n')
    # print('player_names: ' + str(player_names))
    # print('lineup: ' + str(lineup))

    benched = True

    starters_key = 'starters'
    out_key = 'out'
    doubt_key = 'doubt'
    dnp_key = 'dnp'

    starters = lineup[starters_key]
    out = lineup[out_key]
    doubtful = lineup[doubt_key]
    dnp = lineup[dnp_key]

    for player in player_names:
        if player in starters or player in out or player in doubtful or player in dnp:
            benched = False
            break

    #print('benched: ' + str(benched))
    return benched

# affects playtime
def determine_week_after_injury(player_cur_season_log, player, todays_games_date_obj, cur_yr):
    # print('\n===Determine Week After Injury: ' + player.title() + '===\n')
    # print('Input: player_cur_season_log = {stat name: {game idx: stat val, ... = {\'Player\': {\'0\': \'jalen brunson\', ...')# = ' + str(player_cur_season_log))

    after_injury = False

    # if any of the last 2-4 games are > 2 weeks ago?
    # then we know injury gap within a week
    # bc teams play up to 4 games per week
    # check if the gap bt any of the last 2-4 games > 10 days!
    num_restricted_games = 3 # some players/injuries need more games!
    # game_dates = player_cur_season_log['Date']
    cur_game_date_obj = todays_games_date_obj

    for game_idx in range(num_restricted_games):
        # datetime.strptime(date_str, date_format)
        # new players dont have 3 games in log yet to look at so end early
        if len(player_cur_season_log['Date'].keys()) == game_idx:
            break
        prev_game_date = player_cur_season_log['Date'][str(game_idx)].split()[1] # dow mm/dd
        game_mth = prev_game_date.split('/')[0]
        prev_game_yr = determine_game_year(game_mth, cur_yr)
        prev_game_date += '/' + prev_game_yr # mm/dd + /yyyy
        #print('prev_game_date: ' + prev_game_date)
        prev_game_date_obj = datetime.strptime(prev_game_date, '%m/%d/%Y')
        
        # print('cur_game_date_obj: ' + str(cur_game_date_obj))
        # print('prev_game_date_obj: ' + str(prev_game_date_obj))
        game_gap = (cur_game_date_obj - prev_game_date_obj).days
        #print('game_gap: ' + str(game_gap))
        # prev_game_date_str = game_dates[str(game_idx)]
        # game_gap = (cur_game_date - prev_game_date).days

        # serious_injury_minimum = 12-14
        if game_gap > 14:
            #print('Warning: Week After Injury!!! Double Check Playtime Minute Restriction!!! ' + player.title())
            after_injury = True
            break

        cur_game_date_obj = prev_game_date_obj

    #print('after_injury: ' + str(after_injury))
    return after_injury

def determine_valid_player(player, player_season_logs, player_teams, player_gp_cur_conds, cur_yr):
    #print('\n===Determine Valid Player===\n')

    valid = True

    if len(player_season_logs.keys()) == 0:
        valid = False
    elif determine_dnp_player(player_teams, cur_yr, player):
        valid = False
    elif determine_out_player(player, player_gp_cur_conds):
        valid = False

    return valid

# double check playtime in news reports
def determine_all_after_injury_players(all_players_season_logs, all_players_teams, all_game_player_cur_conds, todays_games_date_obj, cur_yr):
    print('\n===All After Injury Players===\n')
    print('Warning: Double check playtime in lineups reports details!')

    after_injury_players = []

    for player, player_season_logs in all_players_season_logs.items():
        #print('\nPlayer: ' + player.title())
        player_teams = all_players_teams[player]
        if player in all_game_player_cur_conds.keys():
            player_gp_cur_conds = all_game_player_cur_conds[player]
            if determine_valid_player(player, player_season_logs, player_teams, player_gp_cur_conds, cur_yr):
                if cur_yr in player_season_logs.keys():
                    player_cur_season_log = player_season_logs[cur_yr]
                    if determine_week_after_injury(player_cur_season_log, player, todays_games_date_obj, cur_yr):
                        after_injury_players.append([player])
                        print(player.title())

    print('\n==============================\n')

    return after_injury_players


def determine_unit_time_period(all_player_stat_probs, all_player_stat_dicts={}, season_years=[], irreg_play_time={}):
    # determine unit time period by observing if drastic change indicates change in team or role
    # default to avg current season but enable manual entry of minutes if irregular such as for teammate injured
    irreg_play_time = {'craig porter': 25}
    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    unit_time_period = 0
    if len(season_years) > 0:
        unit_time_period = season_years[0]
    else:
        unit_time_period = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())[0]

    #print('unit_time_period: ' + str(unit_time_period))
    return unit_time_period

def determine_all_current_gp_conds(all_game_player_cur_conds, all_players_abbrevs, rosters, game_teams):
    print('\n===Determine All Current GP Conds===\n')
    print('Input: all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ...')# = ' + str(all_game_player_cur_conds))
    print('\nOutput: all_cur_conds = [\'all\',\'teammates\',\'opp\',\'J Giddey F, C Wallace G,... starters\',...]\n')

    all_cur_conds = []
    all_players_gp_conds = {}

    # for game player conditions, we want to show overall 2: teammates and opp
    # then we also want to show 4 team parts per team
    # so 10 total: 2 for overall 2 teams per game, plus 8 bc 4 parts per team and 2 teams
    # all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ...
    for player, gp_cur_conds in all_game_player_cur_conds.items():
        #print('\nplayer: ' + player)

        player_gp_conds = []

        cur_team = determine_player_current_team(player, rosters=rosters)
        opp_team = determine_opponent_team(player, cur_team, game_teams)

        # {teammates: {starters:[],...}, opp: {...}}, ...
        for team_condition, team_parts in gp_cur_conds.items():
            #print('\nteam_condition: ' + team_condition)
            # add 2 overall gp conds
            # all_cur_conds = ['all', 'teammates', 'opp']
            #all_cur_conds.extend(['teammates', 'opp'])
            # we add team cond as cur cond bc we want overall prob for team cond for review/comparison/analysis
            # even tho it does not match a measured condition. instead it averages a group of conds
            if team_condition not in all_cur_conds:
                all_cur_conds.append(team_condition)

           
            if team_condition == 'opp':
                gp_team = opp_team
            else:
                gp_team = cur_team

            # 3or4 team parts per team, or 1 per player weighted by playtime
            for team_part, team_part_players in team_parts.items():
                if len(team_part_players) > 0:
                    # remove team name from abbrev for display
                    # CHANGE to gen players abbrevs dict
                    
                    team_part_players_abbrevs = converter.convert_all_players_names_to_abbrevs(team_part_players, all_players_abbrevs, gp_team)
                    
                    # add single player conds
                    for player_abbrev in team_part_players_abbrevs:
                        
                        gp_cond_str = player_abbrev
                        if team_condition == 'opp':
                            gp_cond_str += ' ' + team_condition
                        gp_cond_str += ' ' + team_part

                        if gp_cond_str not in all_cur_conds:
                            all_cur_conds.append(gp_cond_str)
                        if gp_cond_str not in player_gp_conds:
                            player_gp_conds.append(gp_cond_str)
                    
                    # add group conds
                    gp_cond_str = generator.generate_players_string(team_part_players_abbrevs)
                    if gp_cond_str != '': # blank if new team for player so cant confirm abbrev from box score
                        # add team cond bc diff if teammates or opp
                        # and not directly from sample, instead from avg of subsamples
                        if team_condition == 'opp':
                            gp_cond_str += ' ' + team_condition
                        gp_cond_str += ' ' + team_part

                        if gp_cond_str not in all_cur_conds:
                            all_cur_conds.append(gp_cond_str)
                        if gp_cond_str not in player_gp_conds:
                            player_gp_conds.append(gp_cond_str)

        
        all_players_gp_conds[player] = player_gp_conds

    

    #print('all_cur_conds: ' + str(all_cur_conds))
    return all_cur_conds, all_players_gp_conds

# all unique conds for all players so we can display all players in same table with NA for stats that dont have condition
# all_current_conditions: {'marvin bagley iii': {'loc': 'away', 'start': 'bench'}, 'bojan bogdanovic': {'loc':...
# input: all_cur_conds_lists = {p1:[m fultz pg out, away, ...],...}
# output: all_cur_conds: ['all', 'away', 'm fultz pg out', 'bench', 'start', 'home']
def determine_all_current_conditions(all_cur_conds_dicts):
    # print('\n===Determine All Current Conditions===\n')
    # print('Input: all_cur_conds_dicts = {player:{cond_key:cond_val,... = ' + str(all_cur_conds_dicts))
    # print('\nOutput: all_cur_conds = {p1:[\'all\',\'teammates\',\'opp\',\'J Giddey F, C Wallace G,... starters\',...], ...\n')

    # does all here affect later???
    all_cur_conds = ['all'] 
    all_players_cur_conds = {}

    #for player, player_cur_conds in all_current_conditions.items():
    # player_cur_conds = [m fultz pg out, away, ...]
    for player, player_cur_conds in all_cur_conds_dicts.items():
        #print('\nplayer: ' + player.title())
        #print('player_cur_conds: ' + str(player_cur_conds))
        #for cond_key, cond_val in player_cur_conds.items():
            #print('cond_key: ' + str(cond_key))
        
        # does all here affect later???
        player_conds_list = ['all']

        for cond_val in player_cur_conds.values():
            #print('cond_val: ' + str(cond_val))
            if cond_val != '':
                # if cond_key == 'out': # cond_val = []
                #     for out_player in cond_val:
                #         out_player_abbrev = converter.convert_player_name_to_abbrev()
                if cond_val not in player_conds_list:
                    #print('add cond val')
                    player_conds_list.append(cond_val)

                if cond_val not in all_cur_conds:
                    all_cur_conds.append(cond_val)
            else:
                print('Warning: Blank cond_val! ' + player.title())

        all_players_cur_conds[player] = player_conds_list

    # for game player conditions, we want to show overall 2: teammates and opp
    # then we also want to show 4 team parts per team
    # so 10 total: 2 for overall 2 teams per game, plus 8 bc 4 parts per team and 2 teams
    # all_game_player_cur_conds = {p1: {teammates: {starters:[],...}, opp: {...}}, ...
    # for player, gp_cur_conds in all_game_player_cur_conds.items():

    #     # {teammates: {starters:[],...}, opp: {...}}, ...
    #     for team_condition, team_parts in gp_cur_conds.items():

    #         # add 2 overall gp conds
    #         # all_cur_conds = ['all', 'teammates', 'opp']
    #         #all_cur_conds.extend(['teammates', 'opp'])
    #         if team_condition not in all_cur_conds:
    #             all_cur_conds.append(team_condition)

    #         # 4 team parts per team
    #         for team_part, team_part_players in team_parts.items():
    #             gp_cond_str = generator.generate_players_string(team_part_players)
    #             # add team cond bc diff if teammates or opp
    #             # and not directly from sample, instead from avg of subsamples
    #             gp_cond_str += ' ' + team_condition + ' ' + team_part
    #             if gp_cond_str not in all_cur_conds:
    #                 all_cur_conds.append(gp_cond_str)


    

    #print('all_cur_conds: ' + str(all_cur_conds))
    return all_cur_conds, all_players_cur_conds




def determine_total_sample_size(player_stat_dict, season_part='full'):
    # print('\n===Determine Total Sample Size===\n')
    # print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    sample_size = 0
    # all yrs
    for year_stat_dict in player_stat_dict.values():
        # all stats have same samplesize
        stat_dict = list(year_stat_dict[season_part].values())[0]['all']
        #print('stat_dict: ' + str(stat_dict))
        sample_size += len(stat_dict.keys())
        #print('sample_size: ' + str(sample_size))
        
    #print('sample_size: ' + str(sample_size))
    return sample_size

# based on sample size and variance
def determine_player_stat_confidence(player, stat_name, player_stat_dict):
    # print('\n===Determine Player Stat Confidence: ' + player.title() + ', ' + stat_name.upper() + '===\n')
    # print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')

    # CHANGE to include variance of samples
    sample_size = determine_total_sample_size(player_stat_dict, season_part='regular')

    #print('sample_size: ' + str(sample_size))
    return sample_size

# if >1 prev games < likely val
def determine_rare_under(prev_stat_vals, likely_val):

    rare_under = 0

    for val in prev_stat_vals:

        if val < likely_val:
            rare_under += 1
        else:
            break

    return rare_under

# if >1 prev games > likely under
# or missed likely val last 3/4 games or more
# rare over in a row
# and rare over pattern eg 3/4 not necessarily 3 in a row, but 2 in a row
# return no. games rare over in a row
def determine_rare_over(prev_stat_vals, likely_under):

    rare_over = 0

    for val in prev_stat_vals:

        if val > likely_under:
            rare_over += 1
        else:
            break

    return rare_over

def determine_rare_under_pattern(prev_stat_vals, likely_val):

    rare_under = ''

    # last game must be rare under or we cannot say this game
    prev_val = prev_stat_vals[0]
    if prev_val < likely_val:

        num_rare_under = 1

        # we know first prev val rare so check next few for pattern
        for val in prev_stat_vals[1:4]:

            if val < likely_val:
                num_rare_under += 1

        if num_rare_under > 2:  
            rare_under = '3/4'

    return rare_under

def determine_rare_over_pattern(prev_stat_vals, likely_under):

    rare_over = ''

    # last game must be rare over or we cannot say this game
    prev_val = prev_stat_vals[0]
    if prev_val > likely_under:

        num_rare_over = 1

        for val in prev_stat_vals[1:4]:

            if val > likely_under:
                num_rare_over += 1

        if num_rare_over > 2:  
            rare_over = '3/4'

    return rare_over

# determine game num so we can sort by game
def determine_game_num(game_teams, player_team):
    #print('\n===Determine Game Num===\n')
    #print('game_teams: ' + str(game_teams))
    #print('player_team: ' + str(player_team))
    game_num = 0
    for game_idx in range(len(game_teams)):
        game = game_teams[game_idx]
        if player_team in game:
            game_num = game_idx + 1
            break

    #print('game_num: ' + str(game_num))
    return game_num






def determine_player_game(game_teams, player_team):
    #game = ()
    for game in game_teams:
        if player_team in game:
            return game

# determine condition of player current game location
# based on input game teams
# player_teams = {player:{year:{team:gp,...},...}
def determine_player_game_location(player, game_teams, player_team):
    # print('\n===Determine Player Game Location: ' + player.title() + '===\n')
    # print('player_team: ' + player_team)

    player_current_location = ''

    for teams in game_teams:
        away_team = teams[0]
        #print('away_team: ' + str(away_team))
        home_team = teams[1]
        #print('home_team: ' + str(home_team))

        location = ''
        if player_team == away_team:
            location = 'away'
        elif player_team == home_team:
            location = 'home'

        if location != '':
            player_current_location = location
            break # found team in list games so go to next player

    #print('player_current_location: ' + str(player_current_location))
    return player_current_location



def determine_game_year(game_mth, season_year):
    game_year = season_year
    if int(game_mth) > 9:
        game_year = str(int(season_year) - 1)

    return game_year


# {starters:[],out:[],bench:[],unknown:[]}
# player_start = 'start' or 'bench'
# player = 'full name'
# player_team_lineup = {'starters':['tyler herro','jimmy butler',...],'bench':[],'out':[],'probable':[],'question':[],'doubt':[]}
# should have already standardized all lineups before inputting here
def determine_player_start(player, player_abbrev, player_team_lineup, starters_key=''):
   #print('\n===Determine Player Start===\n')
    #print('player_team_lineup: ' + str(player_team_lineup))
    
    # given starters not bench so only make starter if shown in list?
    # problem is questionable players are still listed as starters
    # if they are expected to start then still consider them a starter
    # if player is one of 'starters' then they 'start'
    # need both bc fact of starting is condition as well as who is starting is separate condition
    start_key = 'start'
    bench_key = 'bench'
    player_start = bench_key # player may not be in bench if not played
    
    if  starters_key == '':
        starters_key = 'starters'

    if player in player_team_lineup[starters_key]:# or player_abbrev in player_team_lineup[bench_key]:
        player_start = start_key
    # elif player in player_team_lineup[bench_key]:# or player_abbrev in player_team_lineup[bench_key]:
    #     player_start = bench_key

    #print('player_start: ' + str(player_start))
    return player_start

# see if any of desired keys in stat dict already
# bc if not then we need to read from internet
# for a given condition such as player start, 
# the stat dict could take multiple values, in this case start or bench
# but most keys can take more than 2 values
def determine_key_in_stat_dict(desired_keys, stat_dict_keys):
    key_in_stat_dict = False

    for key in stat_dict_keys:
        if key in desired_keys:
            key_in_stat_dict = True
            break

    return key_in_stat_dict

# init_player_stat_dict = {"2023": {"regular": {"pts": {"all": {"0": 14,...
def determine_need_box_score(season_year, cur_yr, season_part, init_player_stat_dict):

    #print('\n===Determine Need Box Score===\n')

    need_box_score = False

    # if prev season yr already saved then no need to get box scores
    # bc only used to make stat dict
    # if cur season yr then read saved local box scores and new box scores from internet
    # always run for cur yr but only run for unsaved prev yr
    # bc we need to update cur yr each game
    # REMEMBER: we could save stat dict with find players turned off 
    # so it would have season yr but not team players condition
    # seeing that any team players condition has been saved shows us that we ran with find players turned on
    # bc we only add those conditions if we know team players
    team_players_conditions = ['start','bench'] # if either of these are keys in stat dict then we already saved box scores
    # cond keys tells us if we have already read player data from box scores
    condition_keys = []
    if season_year in init_player_stat_dict.keys():
        condition_keys = list(init_player_stat_dict[season_year][season_part].values())[0].keys()
    #print('condition_keys: ' + str(condition_keys))

    # could remove determine key in stat dict if we always run with find players on
    # but we cannot do that so we could ensure only save stat dict if we have
    # all players in games bc that is the only thing we check? no we also check stat dicts before reading game logs
    # and later we will save stat probs so not even save stat dicts but it will behave the same
    if season_year == cur_yr or season_year not in init_player_stat_dict.keys() or not determine_key_in_stat_dict(team_players_conditions, condition_keys):
        need_box_score = True


    return need_box_score

def determine_player_name(teammate_abbrev, player_team, all_players_abbrevs, cur_yr):
    #print('\n====Determine Player Name: ' + teammate_abbrev + '===\n')

    teammate_abbrev_key = teammate_abbrev + '-' + player_team
    player_name = ''
    if teammate_abbrev_key in all_players_abbrevs[cur_yr].keys():
        player_name = all_players_abbrevs[cur_yr][teammate_abbrev_key]

    # try variations of irregular abbrevs
    # OR store list of abbrevs together
    if player_name == '':
        # take only first letter of first initial + rest of name + position
        name_data = teammate_abbrev.split()
        first_abbrev = name_data[0]
        if len(first_abbrev) > 1: # if already 1 then no need to try again
            teammate_abbrev = first_abbrev[0]
            for name in name_data[1:]:
                teammate_abbrev += ' ' + name
            teammate_abbrev_key = teammate_abbrev + '-' + player_team

            # if teammate traded but not played on team yet then no abbrev key
            # bc abbrevs got from box scores
            # it is ok to leave name blank bc no teammate data yet
            # until we advance to extrapolate from past teammates effect
            if teammate_abbrev_key in all_players_abbrevs[cur_yr].keys():
                player_name = all_players_abbrevs[cur_yr][teammate_abbrev_key]

    
    # print('player_name: ' + str(player_name))
    # print('teammate_abbrev: ' + str(teammate_abbrev))
    return player_name, teammate_abbrev

# cur avg playtime is weight of player condition
def determine_cur_avg_playtime(player_cur_season_log, player_gp_cur_team, player):
    print('\n===Determine Cur Avg Playtime: ' + player.title() + '===\n')
    print('Input: player_cur_season_log = {stat name:{game idx:stat val, ... = {\'Player\': {\'0\': \'jalen brunson\', ...')
    print('Input: player_gp_cur_team = x = ' + str(player_gp_cur_team))
    print('\nOutput: gp_cond_weight = x\n')

    cur_avg_playtime = 0

    cur_team_minutes = []

    # player_cur_season_log
    # player_cur_reg_season_log = determine_season_part_games(player_cur_season_log)
    # for game_idx, row in player_cur_reg_season_log.iterrows():

    #     if int(game_idx) == player_gp_cur_team:
    #         break

    #     #game_minutes = row['MIN']
    #     cur_team_minutes.append(row['MIN'])

    
    cur_season_minutes = player_cur_season_log['MIN']
    
    for game_idx in range(player_gp_cur_team):
        game_minutes = cur_season_minutes[str(game_idx)]
        cur_team_minutes.append(game_minutes)

    if len(cur_team_minutes) > 0:
        cur_avg_playtime = converter.round_half_up(np.mean(cur_team_minutes), 2)
    
    print('cur_avg_playtime: ' + str(cur_avg_playtime))
    return cur_avg_playtime

# cur avg playtime is weight of player condition
def determine_all_players_cur_avg_playtimes(all_players_season_logs, all_players_teams, cur_yr):
    print('\n===Determine All Players Cur Avg Playtimes===\n')
    print('Setting: Current Year = ' + cur_yr)
    print('\nInput: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
    print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    print('\nOutput: all_players_cur_avg_playtimes = {player:playtime, ....\n')

    all_players_cur_avg_playtimes = {}

    for player, player_season_logs in all_players_season_logs.items():
        #print('\nplayer: ' + str(player))
        #print('player_season_logs: ' + str(player_season_logs))
        # CHANGE to enable players who is first game this season
        if cur_yr in player_season_logs.keys():
            player_cur_season_log = player_season_logs[cur_yr]
            
            player_teams = all_players_teams[player]
            player_gp_cur_team = determine_gp_cur_team(player_teams, player_season_logs, cur_yr, player)
            
            all_players_cur_avg_playtimes[player] = determine_cur_avg_playtime(player_cur_season_log, player_gp_cur_team, player)

    print('all_players_cur_avg_playtimes: ' + str(all_players_cur_avg_playtimes))
    return all_players_cur_avg_playtimes



# only reg season
def determine_gp_cur_team(player_teams, player_season_logs, current_year_str, player):
    # print('\n===Determine GP Cur Team: ' + player.title() + '===\n')
    # print('Settings: Current Year = ' + current_year_str)
    # print('\nInput: player_teams = {year:{team:{gp:gp, min:min},... = {\'2018\': {\'mia\': {GP:69, MIN:30}, ... = ' + str(player_teams))
    # print('Input: player_season_logs = {year:{stat name:{game idx:stat val, ... = {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')# = ' + str(player_season_logs))
    # print('\nOutput: gp cur team = x\n')

    gp_cur_team = 0

    if current_year_str in player_season_logs.keys() and current_year_str in player_teams.keys():
        cur_season_log = player_season_logs[current_year_str]
        cur_season_log_df = pd.DataFrame(cur_season_log)
        cur_reg_season_log = determine_season_part_games(cur_season_log_df)
        #print('cur_reg_season_log: ' + str(cur_reg_season_log))
        gp_cur_season = len(cur_reg_season_log.index)
        #print('gp_cur_season: ' + str(gp_cur_season))

        
        
        team_stats_dict = player_teams[current_year_str]

        teams = list(reversed(team_stats_dict.keys()))
        all_teams_stats = list(reversed(team_stats_dict.values()))
        # print('teams: ' + str(teams))
        # print('all_teams_stats: ' + str(all_teams_stats))

        # if gp cur season teams > gp cur season log
        # type on teams stats page
        # so take cur team gp as correct
        gp_cur_yr_teams = 0
        for team_stats in all_teams_stats:
            if 'GP' in team_stats.keys():
                gp_cur_yr_teams += team_stats['GP']
        if gp_cur_yr_teams > gp_cur_season: # espn typo
            print('Warning: ESPN typo in games played stats page! Check actual games played. ' + player.title())
            if len(all_teams_stats[0].keys()) > 0:
                # assume cur team correct bc new team small samplesize???
                if 'GP' in all_teams_stats[0].keys():
                    return all_teams_stats[0]['GP']

        
        gp_other_teams = 0
        if len(teams) > 1:
            for team_stats in all_teams_stats[1:]: 
                if 'GP' in team_stats.keys():
                    gp_other_teams += team_stats['GP']

        # if typo, no way to know what number so case irregular
        # case found after player played 1 game with new team so maybe corrected next game???
        if gp_other_teams > gp_cur_season:
            print('Warning: ESPN typo in games played stats page! Check actual games played. ' + player.title())
            # check if blank team stats to see if played on new team
            # if not played on team then all season games are other teams
            # so gp cur team = 0
            gp_other_teams = gp_cur_season
            if len(all_teams_stats[0].keys()) > 0:
                # assume cur team correct bc new team small samplesize???
                if 'GP' in all_teams_stats[0].keys():
                    return all_teams_stats[0]['GP']

                gp_other_teams = gp_cur_season - 1 # assumption must check
            

        # print('gp_cur_season: ' + str(gp_cur_season))
        # print('gp_other_teams: ' + str(gp_other_teams))
        gp_cur_team = gp_cur_season - gp_other_teams

    #print('gp_cur_team: ' + str(gp_cur_team))
    return gp_cur_team

# if missing season yr or missing condition in season yr
# init_player_stat_dict = {"2023": {"regular": {"pts": {"all": {"0": 14,...
# dont need season part bc if missing any season part then need stat dict
def determine_need_stat_dict(player_stat_dict, season_year, find_players=False):
    #print('\n===Determine Need Stat Dict: ' + season_year + '===\n')

    need_stat_dict = False

    team_players_conditions = ['start','bench']
    condition_keys = []
    if season_year in player_stat_dict.keys():
        condition_keys = list(list(player_stat_dict[season_year].values())[0].values())[0].keys()
    #print('condition_keys: ' + str(condition_keys))

    if season_year not in player_stat_dict.keys():# or not determine_key_in_stat_dict(team_players_conditions, condition_keys):
        need_stat_dict = True
    elif find_players and not determine_key_in_stat_dict(team_players_conditions, condition_keys):
        need_stat_dict = True

    #print('need_stat_dict: ' + str(need_stat_dict))
    return need_stat_dict

# if reg season, game idx starts before playoffs
# if post or full season, game idx starts at 0
def determine_player_team_each_game(player, season_part_game_log, teams, games_played, teams_reg_and_playoff_games_played):
    #print('\n===Determine Player Team: ' + player + '===\n')

    for game_idx, row in season_part_game_log.iterrows():

        player_team = ''

        # if type == postseason, then player team idx always =0
        game_type = row['Type']
        #print('game_type: ' + str(game_type))

        # if postseason then after trade deadline so last team this yr
        # postseason maybe playin listed after reg season
        if game_type == 'Postseason': # if postseason, player_team_idx = 0 # recent/last team this yr
            player_team_idx = 0
        else:
            if int(game_idx) >= teams_reg_and_playoff_games_played: # > or >= make > bc we only need to go to next team if more games
                #if len(teams) > player_team_idx+1:
                if len(games_played) > player_team_idx+1:
                    player_team_idx += 1
                    teams_reg_and_playoff_games_played += games_played[player_team_idx]                

        
        if len(teams) > player_team_idx:
            player_team = teams[player_team_idx]

    #print('player_team: ' + str(player_team))
    return player_team



# we need to add date of first game on team to player teams dict
# player_teams = {team:date,...}
def determine_player_team_by_date(player, player_teams, row):
    #print('\n===Determine Player Team by Date: ' + player.title() + '===\n')

    # if date before next team, stay current team idx
    # if date on or after next team, go to next idx
    # and repeat until date before next team

    game_date = row['Date']

    team = ''

    # for team, date in player_teams.items():
    #     next_team_date = ''
    #     if game_date 

    return team







# def determine_player_abbrev(player_name):

#     name_data = player_name.split()
#     abbrev = name_data[0][0]
#     for name in name_data:
#         abbrev += ' ' + name

#     return abbrev

def determine_season_year(game_date):
    #print('\n===Determine Season Year===\n')
    #print('game_date: ' + game_date)

    date_data = game_date.split('/')
    game_mth = date_data[0]
    game_yr = date_data[2]
    season_year = game_yr
    if int(game_mth) > 9:
        season_year = str(int(game_yr) + 1)

    #print('season_year: ' + season_year)
    return season_year
    

# player_teams = {year:{team:gp,...},...}}
def determine_player_team_by_game(player, game_key, player_teams):
    #print('\n===Determine Player ' + player.title() + ' Team by Game: ' + game_key.upper() + '===\n')

    game_date = game_key.split()[2]
    season_yr = determine_season_year(game_date)
    team = list(player_teams[season_yr].keys())[-1]

    #print('team: ' + team)
    return team







def determine_duplicate(prop, unique_props, strict=False):

    duplicate = False

    for up in unique_props:
        if prop['player'] == up['player']:
            # if combo stat then consider duplicate if any matching stat overlap
            stat_name = prop['stat']
            if stat_name == up['stat']:
                duplicate = True
                break

            if strict:
                if re.search('\\+', stat_name):
                    stat_names = stat_name.split('+')
                    for sn in stat_names:
                        if re.search(sn, up['stat']):
                            duplicate = True
                            break

            if duplicate:
                break

    return duplicate

# given main prop and fields, find vals in those fields
# keys = fields = ['player', 'stat']
# allowed player same stat but one over other under!
# so if same player and stat, check val field for +/-
# so we need a special field that looks for part of the values to match, in this case the +/- part
def determine_multiple_dicts_with_vals(main_dict, keys, dict_list, partial_key='', num_vals=2, prints_on=True):
    #if prints_on:
    print('\n===Determine Multiple Dicts with Vals===\n')
    print('main_dict: ' + str(main_dict))
    print('keys: ' + str(keys))
    print('dict_list: ' + str(dict_list))
    print('partial_key: ' + str(partial_key))
    print('num_vals: ' + str(num_vals))

    multiple = False

    same_val_props = [] # show list of matching props

    # need list of all vals in dicts at each key
    # so we can compare vals
    count = 0 # list includes main dict so we need to find 2
    for dict in dict_list:
        # check if matches all keys
        key_match = True
        for key in keys:
            main_val = main_dict[key]
            dict_val = dict[key]
            # if matches, check next key
            # if does not match, check next dict
            if main_val != dict_val:
                #if prints_on:
                print('key_match = False')
                key_match = False
                break

        # partial split special keys
        # if made it thru fields with exact match
        # look for fields with partial match, like +/- in val field
        if key_match == True:
            # main_val = 5+ or 5-
            main_val_sign = re.sub('\d+', '', main_dict[partial_key])
            if main_val_sign not in dict[partial_key]:
                key_match = False
                #if prints_on:
                print('key_match = False')
                break

        # if made it through all keys with all matching
        # then multiple = true
        if key_match == True:
            same_val_props.append(dict)

            count += 1
            if count >= num_vals:
                multiple = True
                #if prints_on:
                print('count >= num_vals: ' + str(count) + ' >= ' + str(num_vals))
                print('multiple = True')
                break

    # if checked all dicts without match, then multiple false

    #if prints_on:
    print('multiple: ' + str(multiple))
    print('same_val_props: ' + str(same_val_props))
    return multiple

# given main prop and fields, find vals in those fields
def determine_multiple_dicts_with_val(main_dict, key, dict_list, num_vals=2):
    #print('\n===Determine Multiple Dicts with Val===\n')
    #print('main_dict: ' + str(main_dict))
    #print('key: ' + str(key))

    multiple = False

    main_val = main_dict[key]
    # see if this val is in >1 dicts in list 
    count = 0
    for dict in dict_list:
        dict_val = dict[key]
        if main_val == dict_val:
            count += 1

        if count >= num_vals:
            #print('found multiple')
            multiple = True
            break

    #print('multiple: ' + str(multiple))
    return multiple

def determine_vals_in_dict(main_dict, keys, dict):
    #print('\n===Determine Vals in Dict===\n')

    vals_in_dict = True

    for key in keys:
        main_val = main_dict[key]
        dict_val = dict[key]
        if main_val != dict_val:
            #print('vals not in dict')
            vals_in_dict = False
            break

    #print('vals_in_dict: ' + str(vals_in_dict))
    return vals_in_dict

def determine_val_in_dicts(main_dict, key, remaining_dicts):
    #print('\n===Determine Val in Dicts===\n')

    val_in_dict = False 

    main_val = main_dict[key]
    #print('main_val: ' + str(main_val))
    for dict in remaining_dicts:
        dict_val = dict[key]
        if main_val == dict_val:
            #print('found val in dict')
            val_in_dict = True
            break

    return val_in_dict

# determine highest value dict
def determine_highest_value_dict(main_dict, duplicate_dicts, key):
    #print('\n===Determine Highest Value Dict===\n')

    highest = True

    main_val = main_dict[key]

    for prop in duplicate_dicts:
        dup_val = prop[key]
        if dup_val > main_val:
            #print('not highest')
            highest = False
            break

    return highest

# determine highest value dict
def determine_highest_val_prop(main_prop, duplicate_props, field_key='true prob'):
    #print('\n===Determine Highest Prob Prop===\n')

    highest = True

    if field_key == '':
        field_key = 'true prob'

    main_val = main_prop[field_key]

    for prop in duplicate_props:
        dup_val = prop[field_key]
        if dup_val > main_val:
            #print('not highest')
            highest = False
            break

    return highest

# determine highest value dict
def determine_highest_ev_prop(main_prop, duplicate_props):
    #print('\n===Determine Highest EV Prop===\n')

    highest = True

    main_ev = main_prop['ev']

    for prop in duplicate_props:
        dup_ev = prop['ev']
        if dup_ev > main_ev:
            #print('not highest')
            highest = False
            break

    return highest









































def determine_out_player(player_name, player_gp_cur_conds):
    # print('\n===Determine Out Player: ' + player_name.title() + '===\n')
    # print('Input: player_gp_cur_conds = {teammates: {starters:[],...}, opp: {...}}, ... = ' + str(player_gp_cur_conds))

    out = False 

    teammates = player_gp_cur_conds['teammates']
    if len(teammates.keys()) > 0:
        out_teammates = teammates['out']
        #print('out_teammates: ' + str(out_teammates))
        #doubt_teammates = teammates['doubt']

        if player_name in out_teammates:# or player_name in doubt_teammates:
            out = True

    #print('out: ' + str(out))
    return out


def determine_dnp_player(player_teams, cur_yr, player_name):
    # print('\n===Determine DNP Player: ' + player_name.title() + '===\n')
    # print('Input: player_teams = {year:{team:{GP:gp, MIN:min},... = {\'2018\': {\'mia\': {\'GP\':69, \'MIN\':30.2}, ... = ' + str(player_teams))

    dnp = False

    player_mean_minutes = 0
    if cur_yr in player_teams.keys():
        # player may have been recently traded and not played yet (eg theo maledon)
        # ordered from distant to recent
        cur_yr_teams_dicts = reversed(player_teams[cur_yr].values()) # {team:{min:m, gp:gp}, ...}
        #print('cur_yr_teams_dicts: ' + str(cur_yr_teams_dicts))
        #if team in cur_yr_teams_dict.keys():
        # if played this yr then team dict will not be blank
        # they will still have team but the data will be blank
        # if they have another team this yr then use those minutes to see if dnp
        # from recent to distant
        for team_dict in cur_yr_teams_dicts:
            #print('team_dict: ' + str(team_dict))
            if len(team_dict.keys()) > 0:
                #cur_team_dict = cur_yr_teams_dicts[0] # {min:m, gp:gp}
                player_mean_minutes = team_dict['MIN']
                break

    #print('player_mean_minutes: ' + str(player_mean_minutes))
    if player_mean_minutes < 11.5:
        dnp = True

    #print('dnp: ' + str(dnp))
    return dnp


def determine_teammates_out_at_position(player_team_lineup, all_players_positions, player_name):
    # print('\n===Determine Teammates Out At Position: ' + player_name.title() + '===\n')
    # print('Input: player_team_lineup = {\'starters\': [\'donovan mitchell\', ... = ' + str(player_team_lineup))
    # print('Input: all_players_positions = {player:position, ...} = {\'jalen brunson\': \'pg\', ...} = ' + str(all_players_positions))
    # print('\nOutput: tiap = x\n')

    toap = 0

    player_position = all_players_positions[player_name]

    # Condition: teammates in/out at position
    #print('\n===Condition: Teammates At Position: ' + player_name.title() + '===\n')
    # when no samples of lineup to get playtime, 
    # we need to predict based on teammates at position
    #print('player_position: ' + str(player_position))
    position_groups = {'pg':['pg','sg','g','sf'], 
                        'sg':['pg','sg','g','sf'],
                        'g':['pg','sg','g','sf'],
                        'sf':['sg','g','sf','f','pf'],
                        'f':['sf','f','pf','c'],
                        'pf':['sf','f','pf','c'],
                        'c':['sf','f','pf','c']}
    player_position_group = position_groups[player_position]

    out = player_team_lineup['out']

    # sometimes name given in lineup does not include suffix like ii or jr
    # so if first pass not found, check without suffix
    for teammate_name in out:
        # teammate maybe not on team anymore so not considered out
        if teammate_name in all_players_positions.keys():
            teammate_position = all_players_positions[teammate_name]
            if teammate_position in player_position_group:
                toap += 1

    # subtract 1 for cur player bc not his own teammate
    # BUT not needed bc out player has no cur conds so given player never in out list
    #toap -= 1

    # toap_str = str(toap) + ' toap'

    # print('toap_str: ' + str(toap_str))   
    return toap

def determine_median_tiap(player_stat_dict):

    median_tiap = 0
    return median_tiap

def determine_offset_tiap(tiap_str, player_stat_dict, player_name):
    print('\n===Determine Offset TIAP: ' + player_name.title() + '===\n')
    print('Input: tiap_str = ' + tiap_str)
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    print('\nOutput: offset tiap = x\n')

    #offset_tiap = 0

    tiap = int(tiap_str.split()[0])

    median_tiap = determine_median_tiap(player_stat_dict)

    offset_tiap = median_tiap - tiap

    return offset_tiap


def determine_opp_in_at_position(opp_team_lineup, all_players_positions, player_name):
    # print('\n===Determine Opponents In At Position: ' + player_name.title() + '===\n')
    # print('Input: opp_team_lineup = {\'starters\': [\'donovan mitchell\', ... = ' + str(opp_team_lineup))
    # print('Input: all_players_positions = {player:position, ...} = {\'jalen brunson\': \'pg\', ...}')# = ' + str(all_players_positions))
    # print('\nOutput: tiap = x\n')

    oiap = 0

    player_position = all_players_positions[player_name]

    # Condition: teammates in/out at position
    #print('\n===Condition: Teammates At Position: ' + player_name.title() + '===\n')
    # when no samples of lineup to get playtime, 
    # we need to predict based on teammates at position
    #print('player_position: ' + str(player_position))
    position_groups = {'pg':['pg','sg','g','sf'], 
                        'sg':['pg','sg','g','sf'],
                        'g':['pg','sg','g','sf'],
                        'sf':['sg','g','sf','f','pf'],
                        'f':['sf','f','pf','c'],
                        'pf':['sf','f','pf','c'],
                        'c':['sf','f','pf','c']}
    player_position_group = position_groups[player_position]

    starters = opp_team_lineup['starters']
    bench = opp_team_lineup['bench']

    for opp_name in starters:
        opp_position = all_players_positions[opp_name]
        if opp_position in player_position_group:
            oiap += 1
    for opp_name in bench:
        opp_position = all_players_positions[opp_name]
        if opp_position in player_position_group:
            oiap += 1

    # do not subtract 1 like for tiap bc player not on opp team

        
    #print('oiap: ' + str(oiap))   
    return oiap


def determine_teammates_in_at_position(player_team_lineup, all_players_positions, player_name):
    # print('\n===Determine Teammates In At Position: ' + player_name.title() + '===\n')
    # print('Input: player_team_lineup = {\'starters\': [\'donovan mitchell\', ... = ' + str(player_team_lineup))
    # print('Input: all_players_positions = {player:position, ...} = {\'jalen brunson\': \'pg\', ...}')# = ' + str(all_players_positions))
    # print('\nOutput: tiap = x\n')

    tiap = 0

    player_position = all_players_positions[player_name]

    # Condition: teammates in/out at position
    #print('\n===Condition: Teammates At Position: ' + player_name.title() + '===\n')
    # when no samples of lineup to get playtime, 
    # we need to predict based on teammates at position
    #print('player_position: ' + str(player_position))
    position_groups = {'pg':['pg','sg','g','sf'], 
                        'sg':['pg','sg','g','sf'],
                        'g':['pg','sg','g','sf'],
                        'sf':['sg','g','sf','f','pf'],
                        'f':['sf','f','pf','c'],
                        'pf':['sf','f','pf','c'],
                        'c':['sf','f','pf','c']}
    player_position_group = position_groups[player_position]

    starters = player_team_lineup['starters']
    bench = player_team_lineup['bench']
    # print('starters: ' + str(starters))
    # print('bench: ' + str(bench))

    for teammate_name in starters:
        teammate_position = all_players_positions[teammate_name]
        # print('teammate_name: ' + str(teammate_name))
        # print('teammate_position: ' + str(teammate_position))
        if teammate_position in player_position_group:
            tiap += 1
    for teammate_name in bench:
        teammate_position = all_players_positions[teammate_name]
        # print('teammate_name: ' + str(teammate_name))
        # print('teammate_position: ' + str(teammate_position))
        if teammate_position in player_position_group:
            tiap += 1

    # subtract 1 for cur player bc not his own teammate
    # OR just count all players including cur player???
    # simpler to consider relative to teammates
    # bc otherwise need to specify team players and opp players and all game players separately
    # also bc out teammates never includes cur player so keep uniformly relative to teammates
    tiap -= 1

    #tiap_str = str(tiap) + ' tiap'
        
    #print('tiap: ' + str(tiap))
    return tiap



# given todays date find next game date
def determine_next_game_num(schedule_date_dict, cur_yr):
    # print('\n===Determine Next Game Num===\n')
    # print('Input: schedule_date_dict = {\'0\':field name, game num:field val, ... = {"0": "DATE", "1": "Tue, Oct 24", "2": "Thu, Oct 26", ...')
    # print('\nOutput: next_game_num = x\n')

    next_game_num = 1

    cur_date = datetime.today()

    # game_date = Tue, Oct 24 -> 10/24/2023
    for game_num, game_date_str in schedule_date_dict.items():
        # skip first idx always field title
        if game_date_str == 'DATE':
            continue

        #print('\ngame_date_str: ' + str(game_date_str))

        # next game always after second header row
        # BUT we would have to read from internet each run
        # so quicker to save local and compare dates to find next game?
        # if game_date_str == 'DATE':
        #     next_game_num = str(int(game_idx) + 1)
        #     break

        # Oct 24
        game_date_str = game_date_str.split(',')[1].strip()
        #print('game_date_str: ' + game_date_str)
        game_mth_abbrev = game_date_str.split()[0]
        #print('game_mth_abbrev: ' + game_mth_abbrev)
        game_mth = converter.convert_month_abbrev_to_num(game_mth_abbrev)
        #print('game_mth: ' + str(game_mth))
        game_yr = determine_game_year(game_mth, cur_yr)
        game_date_str += ' ' + game_yr
        #print('game_date_str: ' + game_date_str)
        # %B[:3] = %b
        # %b %d %Y
        # Oct 24 2023 -> 10/24/2023
        game_date = datetime.strptime(game_date_str, '%b %d %Y')
        # print('game_date: ' + str(game_date))
        # print('cur_date: ' + str(cur_date))

        if game_date > cur_date:
            next_game_num = game_num
            break

    #print('next_game_num: ' + str(next_game_num))
    return next_game_num

# given todays date find next game date
def determine_next_game_date(schedule_date_dict, cur_yr):
    # print('\n===Determine Next Game Date===\n')
    # print('Input: schedule_date_dict = {\'0\':field name, game num:field val, ... = {"0": "DATE", "1": "Tue, Oct 24", "2": "Thu, Oct 26", ...')
    # print('\nOutput: next_game_date = mm/dd/yyyy\n')


    next_game_num = determine_next_game_num(schedule_date_dict, cur_yr)
    
    # mm/dd
    next_game_date = schedule_date_dict[next_game_num].split(', ')[1] # mar 31
    next_game_mth = next_game_date.split()[0].lower() # mar
    #print('next_game_mth: ' + str(next_game_mth))
    # game_mth = next_game_date.split()[0] # mar
    # print('game_mth: ' + game_mth)
    next_game_mth = converter.convert_month_abbrev_to_num(next_game_mth)
    #print('next_game_mth_num: ' + str(next_game_mth))
    
    next_game_yr = determine_game_year(next_game_mth, cur_yr)

    next_game_day = next_game_date.split()[1].lower() # 31
    #print('next_game_day: ' + str(next_game_day))
    
    next_game_date = str(next_game_mth) + '/' + next_game_day + '/' + next_game_yr # mm/dd + /yyyy

    # next_game_date_obj = datetime.strptime(next_game_date, '%b %d %Y')
    # next_game_date = next_game_date_obj.strftime('%m/%d/%Y')
    
    #print('next_game_date: ' + next_game_date)
    return next_game_date


# use in gen all box scores to get abbrev from list of abbrevs before concluding if in team part
def determine_abbrev_in_game(player_abbrevs, team_part_players):
    # print('\n===Determine Abbrev in Game===\n')
    # print('Input: player_abbrevs = [abbrevs] = [X Tillman F, Tillman Sr F] = ' + str(player_abbrevs))
    # print('Input: team_part_players = {player:play time,... = ' + str(team_part_players))
    
    abbrev_in_game = ''
    for abbrev in player_abbrevs:
        if abbrev in team_part_players:
            # found abbrev in game so move on
            abbrev_in_game = abbrev
            break

    # if abbrev_in_game:
    #     print('found abbrev in game')

    return abbrev_in_game

# given todays game matchups
# output opponent team
# game_teams = [('mil','mia'),...]
# player_teams = {'2018': {'mia': 69}, '2019...
# player_teams = {year:{team:gp,...},...
def determine_opponent_team(player, player_team, game_teams):#, player_teams={}, cur_yr='', rosters={}):
    #print('\n===Determine Player Opponent Team: ' + player.title() + '===\n')
    #print('player_teams: ' + str(player_teams))
    #print('game_teams: ' + str(game_teams))
    
    opp_team = ''

    # if player_team == '':
    #     player_team = determine_player_current_team(player, player_teams, cur_yr, rosters)

    # look for player team in games
    # game = ('mil','mia')
    for game in game_teams:
        for team_idx in range(len(game)):
            # team = 'mil'
            team = game[team_idx]
            if player_team == team: # found game in list of games
                opp_team_idx = 0
                if team_idx == 0:
                    opp_team_idx = 1
                                
                opp_team = game[opp_team_idx]
                break

        if opp_team != '':
            break
        
    #print('opp_team: ' + opp_team)
    return opp_team

# player = Jal Williams 
# player_name = jalen williams
# player_abbrev = j williams. do we need?
# determine match if first word and second word match
# cannot compare whole words bc irregular abbrevs
# what about v williams compared to vince williams jr?
# we know same bc team only has 1 v williams
def determine_player_abbrev_match(main_player, compare_player):
    # print('\n===Determine Player Abbrev Match===\n')
    # print('main_player: ' + str(main_player))
    # print('compare_player: ' + str(compare_player))

    match = True

    # remove suffixes before comparing bc some sources dont use
    # and rare 2 players on same team with suffix only difference in name
    # but not impossible so ideally use teams to see only 1 matching in team
    main_player = re.sub('(jr|sr|i+)$','',main_player).strip()
    compare_player = re.sub('(jr|sr|i+)$','',compare_player).strip()
    # print('formatted main_player: ' + str(main_player))
    # print('formatted compare_player: ' + str(compare_player))


    main_player_names = main_player.split()
    compare_player_names = compare_player.split()
    # if they have different number of words in name then diff player?
    # no bc 1 source might exclude jr or sr but still same player
    if len(main_player_names) != len(compare_player_names):
        match = False
    else:
        for name_idx in range(len(main_player_names)):
            # jal
            main_name = main_player_names[name_idx]
            num_letters = len(main_name)
            # jalen        
            compare_name = compare_player_names[name_idx]
            # print('main_name: ' + str(main_name))
            # print('compare_name: ' + str(compare_name))
            # print('compare_letters: ' + str(compare_name[:num_letters]))
            if not main_name == compare_name[:num_letters]:
                match = False
                break 

    return match

# player_teams = {year:{team:gp,...},...}}
# CHANGE to get team at time of game
# add date of first game with team from game log to player teams dict
def determine_player_season_teams(player, game_key, player_teams):
    # print('\n===Determine Player ' + player.title() + ' Season Teams: ' + game_key.upper() + '===\n')
    # print('Input: players_teams = {year:{team:{GP:gp, MIN:min},... = {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    # print('\nOutput: player_season_teams = [teams]')

    teams = []

    if len(game_key) > 0:
        game_date = game_key.split()[-1]
        season_yr = determine_season_year(game_date)
        if season_yr in player_teams.keys():
            for team in player_teams[season_yr].keys():
                teams.append(team)

    #print('teams: ' + str(teams))
    return teams

def determine_cur_team_from_rosters(player, rosters):
    #print('\n===Determine Current Team from Rosters: ' + player.title() + '===\n')
    for team, roster in rosters.items():
        if player in roster:
            return team

#list(player_teams[player][cur_yr].keys())[-1] # current team
# can we take first year in teams list instead of cur yr?
# player_teams = {year:{team:gp,...},...
# do we always want to return the team, even if they are only practice players?
# that may lead to wrong results if we only want to consider game players
def determine_player_current_team(player, player_teams={}, cur_yr='', rosters={}):
    # print('\n===Determine Player Current Team: ' + player.title() + '===\n')
    # print('Input: players_teams = {year:{team:{GP:gp, MIN:min},... = {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    # print('\nOutput: player_current_team = \'cha\'\n')

    cur_team = ''

    if cur_yr == '':
        cur_yr = determine_current_season_year()

    # more reliable to take from rosters 
    # bc player teams will only show if they actually played this season
    cur_team = determine_cur_team_from_rosters(player, rosters)

    if cur_team is None: # could not find player in rosters so maybe not player of interest but maybe player of comparison
        if len(player_teams.keys()) > 0:
            if cur_yr in player_teams.keys():
                cur_team = list(player_teams[cur_yr].keys())[-1]
            # {team:gp,...}
            else:
                recent_yr_teams = list(player_teams.values())[-1] # most recent yr
                if len(recent_yr_teams.keys()) > 0:
                    cur_team = list(recent_yr_teams.keys())[-1] # most recent team
    # should always have player teams bc all lineups are same players as input
    # else: # need to get current team from internet
    #     cur_team = reader.read_player_current_team()

    # if cur_team == '':
    #     print('\n===Warning: Player cur team blank! ' + player.title() + '===')
    #     print('player_teams: ' + str(player_teams))
    #     print('cur_yr: ' + str(cur_yr))
    #     print('rosters: ' + str(rosters))

    #print('cur_team: ' + str(cur_team))
    return cur_team

# jaylen brown -> j brown
# trey murphy iii -> t murphy iii
# Jayson Tatum -> j tatum
# j tatum sf -> j tatum
# use to see if started or bench
# bc lineups shows player abbrev
# this abbrev does not include position bc it is used to compare to full name
def determine_player_abbrev(player_name):
    #print('\n===Determine Player Abbrev: ' + player_name.title() + '===\n')
    
    player_abbrev = ''

    # if already 1 letter in first name
    # then using first initial in format j brown sg
    # so remove last word to get abbrev
    #player_abbrev = player_initital + last_name
    if player_name != '':
        player_name = re.sub('\.', '', player_name).lower()
        player_name = re.sub('-', ' ', player_name)
        player_names = player_name.split()
        player_abbrev = player_names[0][0] #re.sub('\.','',player_names[0][0])
        if len(player_names[0]) == 1:
            # remove position from end of name abbrev
            for name in player_names[1:-1]:
                player_abbrev += ' ' + name
        
        else:
            #last_name = ''
            for name in player_names[1:]:
                player_abbrev += ' ' + name

        player_abbrev = player_abbrev.lower()
    
    # else:
    #     print('Warning: Blank player name while determining player abbrev!')
    
    #print('player_abbrev: ' + player_abbrev)
    return player_abbrev

# if given abbrev like D. Green need to know team or position to get full name
# already given team so use that
# check which player in all players teams list with this team has this abbrev
# all_players_teams = {player:{year:{team:gp,...},...}}
# player = D. Green or Draymond Green
# player = K. Towns to karl anthony towns
# player = K Towns PF to karl anthony towns
# use game_key to get player team at game time
# the team passed here is the team of the player at game time 
# but we need to connect his full name to his stats page where he may not be listed if he did play yet this season
def determine_player_full_name(init_player, team, all_players_teams, rosters={}, game_key='', cur_yr='', position=''):
    # print('\n===Determine Player Full Name: ' + init_player + '===\n')
    # print('Input: team of player of interest in game of interest = ' + team)
    # print('Input: game_key = away home date = ' + game_key)
    # print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
    # print('Input: rosters = {team:roster, ... = {\'nyk\': [jalen brunson, ...], ...')
    # print('Input: Current Year to tell current team')
    # print('\nOutput: player_full_name = jalen brunson\n')
    
    # print('team: ' + str(team))
    #print('all_players_teams: ' + str(all_players_teams))

    full_name = ''


    # player = D. Green -> d green
    # player = Draymond Green -> draymond green
    # player = D Green PF -> d green
    # V. Williams -> v williams
    player = init_player

    player = re.sub('\.','',player).lower()
    player = re.sub('-',' ',player)

    # print('player: ' + str(player))
    # print('team: ' + str(team))
    # irreg 2 d smiths on bkn same team
    # could fix by forcing both last names to match but this is only case for now
    if player == 'd smith' and team == 'bkn': # no position in abbrev so we know from lineup source
        return 'dennis smith jr'
    elif player == 'g' and team == 'mil': # no position in abbrev so we know from lineup source
        return 'giannis antetokounmpo'
    elif player == 'kj martin':
        return 'kenyon martin jr'
    elif player == 'p baldwin':
        return 'patrick baldwin jr'
    elif player == 'marvin bagley' or player == 'm bagley':
        return 'marvin bagley iii'
    elif player == 'j williams' and team == 'okc' and position == 'c':
        return 'jaylin williams'
    # add jr to end of name in irreg cases
    # cannot simply look for jr in all case bc maybe diff players, 1 jr and other not
    elif player == 'kelly oubre':
        return player + ' jr'

    # if player gone from the league 
    # AND we did not get their espn id
    # they do not show up in all players teams
    # so should we get data for gone players?
    #if player not in all_players_teams:
        # get player teams
    # problem is we cant see if player is in all players teams bc we dont have full name but we have last name
    # but last name might match wrong player

    
    

    # if already using only first initial or abbrev?
    # we need to remove position at end of name before comparing
    #if len(game_key) > 0:
    #player_names = player.split()
    # if dot then comes from lineup page so no position at end
    # we do not know how many letters are in first word of abbrev
    # so how to tell if in format Jal Williams F
    # if cant tell letter case then look for specific letters as last letters (f, g, c)
    #if len(player_names[0]) == 1 and not re.search('\.',init_player):
    # need to keep original uppercase to know abbrev format bc irreg formats like Baldwin F
    #if len(player_names) > 2 and re.search('[fgc]$',player):
    if init_player[-1].isupper():
        player = re.sub('\s+[a-z]+$', '', player)#.strip() # D Green PF -> d green

        
    #print('formatted player: \'' + str(player) + '\'') # d green
    if player in all_players_teams.keys(): # if already given full name
        full_name = player
    else: # could use all players teams or rosters
        # if cur yr look in roster
        # else look in player teams
        # player_teams = {yr:team:gp} = {'2024':{}}
        for compare_player_name, compare_player_teams in all_players_teams.items():
            #print('\ncompare_player_name: ' + str(compare_player_name))
            # print('compare_player_teams: ' + str(compare_player_teams))
            # look at current team bc we are comparing to current lineup
            # if player just traded then has no log with this team
            # compare name: 
            # player_name = draymond green, always full bc already standardized in all players teams from team rosters
            # player abbrev = d green
            # cannot simplify like this if given any abbrevs with more than 1 letter in first name bc same abbrevs on same team need unique abbrevs
            # player = Jal Williams 
            # player_name = jalen williams
            player_abbrev = determine_player_abbrev(compare_player_name)

            # why do we need the cur team if we are finding the players team at the time of the input game?
            # we need team at time of game by adding date to all players teams
            # but most cases are covered by adding team to abbrev key
            # only special case is if 2 people with same abbrev are traded for each other same yr (rare but important like t jones pg)
            cur_team = ''#determine_player_current_team(compare_player_name, compare_player_teams, cur_yr, rosters)
            season_teams = []
            if len(game_key) > 0:
                # for now get list of teams this season and use either or
                # pass in the compare player name
                season_teams = determine_player_season_teams(compare_player_name, game_key, compare_player_teams)
                #game_team = determine_player_team_by_game(game_key, player_teams)
            else:
                cur_team = determine_player_current_team(compare_player_name, compare_player_teams, cur_yr, rosters)

            # if given lineup player name not in all players teams dict
            # then it is usually an abbrev but not always
            # sometimes all players teams dict has jr or sr but lineups does not
            #print('player: ' + str(player))
            #print('player_abbrev: ' + str(player_abbrev))
            # if we find matching player name or abbrev, check if teams match
            # player_abbrev = k anthony towns
            # player abbrev = j williams
            player_abbrev_names = player_abbrev.split()
            # print('player: \'' + player + '\'')
            # print('player_abbrev: \'' + player_abbrev + '\'')
            # print('player_name: ' + player_name)
            # player = Jal Williams
            # player_name = jalen williams
            # player_abbrev = j williams. do we need?
            # determine match if first word and second word match
            # cannot compare whole words bc irregular abbrevs
            if determine_player_abbrev_match(player, compare_player_name):
            #if re.search(player,player_abbrev) or re.search(player,player_name):
                # print('team: ' + str(team))
                # print('cur_team: ' + cur_team)
                # print('season_teams: ' + str(season_teams))
                if len(season_teams) > 0:
                    if team in season_teams:
                        full_name = compare_player_name
                        break # found player name
                elif team == cur_team:
                    full_name = compare_player_name
                    break # found player name
            elif len(player_abbrev_names) > 2: # 3 word name like k anthony towns
                normal_abbrev = player_abbrev_names[0] + ' ' + player_abbrev_names[2] # k towns, remove middle name
                #print('normal_abbrev: ' + str(normal_abbrev))
                if re.search(player,normal_abbrev):# and team == game_team:
                    if len(season_teams) > 0:
                        if team in season_teams:
                            full_name = compare_player_name
                            break # found player name
                    elif team == cur_team:
                        full_name = compare_player_name
                        break # found player name

    #print('full_name: ' + full_name)
    return full_name

# use whenever we know game key and team loc but not the team name
def determine_team_from_game_key(game_key, team_loc):
    #print('\n===Determine Team from Game Key===\n')
    team = ''

    game_data = game_key.split()
    if len(game_data) > 2:
        away_team = game_data[0]
        home_team = game_data[1] 
        team = away_team
        if team_loc == 'home':
            team = home_team

    #print('team: ' + team)
    return team

# all yrs for single condition
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
# this fcn is passed a single condition and gets its sample size so we need outer fcn to call this fcn for all conds in list
def determine_condition_sample_size(player_stat_dict, condition, part, stat_name=''):
    # print('\n===Determine Condition Sample Size: ' + str(condition) + ', ' + part + '===\n')
    # print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {2023: {regular: {pts: {all: {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')# = ' + str(player_stat_dict))
    # print('\nOutput: sample_size = x\n')

    sample_size = 0

    for year, year_stat_dicts in player_stat_dict.items():
        #print('\nyear: ' + year)
        if part in year_stat_dicts.keys():
            part_stat_dict = year_stat_dicts[part]
            # we take idx 0 for first stat bc all stats sampled for all games so same no. samples for all stats
            # BUT we need to know stat to get prev val!!!
            full_stat_dict = {}
            if stat_name in part_stat_dict.keys():
                full_stat_dict = part_stat_dict[stat_name]
            else: # fail with error message or take first stat???
                full_stat_dict = list(part_stat_dict.values())[0]

            #print('full_stat_dict: ' + str(full_stat_dict))
            if condition in full_stat_dict.keys():
                #print('found condition ' + condition)
                stat_dict = full_stat_dict[condition]
                #print('stat_dict: ' + str(stat_dict))
                sample_size += len(stat_dict.keys())

    #print('sample_size: ' + str(sample_size))
    return sample_size

# get game idxs for each condition to see overlap
def determine_condition_sample_indexes(player_stat_dict, condition, part):
    # print('\n===Determine Condition Sample Indexes: ' + condition + ', ' + part + '===\n')
    # print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {2023: {regular: {pts: {all: {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')# = ' + str(player_stat_dict))
    # print('\nOutput: sample_indexes = {year:[game idx,...],...\n')

    sample_indexes = {}

    for year, year_stat_dicts in player_stat_dict.items():
        #print('\nyear: ' + year)
        # sample_indexes[year] = []
        # year_sample_idxs = sample_indexes[year]
        if part in year_stat_dicts.keys():
            # we take idx 0 for first stat bc all stats sampled for all games so same no. samples for all stats
            full_stat_dict = list(year_stat_dicts[part].values())[0]
            #print('full_stat_dict: ' + str(full_stat_dict))
            if condition in full_stat_dict.keys():
                #print('found condition ' + condition)
                stat_dict = full_stat_dict[condition]
                #print('stat_dict: ' + str(stat_dict))
                sample_indexes[year] = list(stat_dict.keys())

    #print('sample_indexes: ' + str(sample_indexes))
    return sample_indexes

# given a list of conds, sum their sample sizes
# eg for game player conds where we add combo conds with single conds
# would it just be all samples since it is samples of players in every game?
# not necessarily if current conds dont match samples
# for exmple if none of the current game teammates were in any of the given players games
# is that possible? i think not bc at least 1 player? no bc if new team then no matching conds
# many cases all samples will have at least 1 player from cur conds, if played on team 2 seasons
def determine_combined_conditions_sample_size(player_stat_dict, conditions, season_part):
    # print('\n===Determine Combined Conditions Sample Size===\n')
    # print('Setting: Season Part = ' + season_part)
    # print('\nInput: Conditions = {condition: cond type, ... = ' + str(conditions))
    # print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {2023: {regular: {pts: {all: {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')# = ' + str(player_stat_dict))
    # print('\nOutput: combined_sample_size = x\n')

    combined_sample_size = 0
    all_unique_sample_idxs = {}
    
    for condition in conditions:
        cond_sample_idxs = determine_condition_sample_indexes(player_stat_dict, condition, season_part)
        for year, year_sample_idxs in cond_sample_idxs.items():
            if year not in all_unique_sample_idxs.keys():
                all_unique_sample_idxs[year] = []
            unique_sample_idxs = all_unique_sample_idxs[year] # no repeats per yr
            for sample_idx in year_sample_idxs:
                if sample_idx not in unique_sample_idxs:
                    unique_sample_idxs.append(sample_idx)
                    #print('unique_sample_idxs: ' + str(unique_sample_idxs))
                    combined_sample_size += 1

    #print('all_unique_sample_idxs: ' + str(all_unique_sample_idxs))

    #print('combined_sample_size: ' + str(combined_sample_size))
    return combined_sample_size

def determine_team_timezone(team):
    #print('\n===Determine Team Timezone: ' + team + '===\n')

    timezone = ''

    team_timezones = {'atl':'ET', 
                    'bos':'ET', 
                    'bkn':'ET', 
                    'cha':'ET', 
                    'chi':'CT',
                    'cle':'ET',
                    'dal':'CT',
                    'den':'MT',
                    'det':'ET',
                    'gsw':'PT',
                    'hou':'CT',
                    'ind':'ET',
                    'lac':'PT',
                    'lal':'PT',
                    'mem':'CT',
                    'mia':'ET',
                    'mil':'CT',
                    'min':'CT',
                    'nop':'CT',
                    'nyk':'ET',
                    'okc':'CT',
                    'orl':'ET',
                    'phi':'ET',
                    'phx':'MT',
                    'por':'PT',
                    'sac':'PT',
                    'sas':'CT',
                    'tor':'ET',
                    'uta':'MT',
                    'wsh':'ET'}
    
    if team in team_timezones.keys():
    #if team != '':
        timezone = team_timezones[team]

    #print('timezone: ' + timezone)
    return timezone

def determine_timelag(city, player_team):

    timezone = determine_timezone(city)
    timezone_time = converter.convert_time_zone_to_time(timezone)
    # get timeshift from game timezone and home timezone
    #home_city = determiner.determine_team_city(player_team)
    home_timezone = determine_team_timezone(player_team)
    home_timezone_time = converter.convert_time_zone_to_time(home_timezone)
    
    timelag = str(home_timezone_time - timezone_time) + ' lag'

    return timelag

def determine_timezone(city):
    #print('Input: city = city STATE ABBREV = ' + city)#= Milwaukee WI')
    
    # only need state abbrev for some
    #state = city.split()[-1]
    
    timezones = {'Atlanta GA':'ET', 
                 'College Park GA':'ET',
                 'Cleveland OH':'ET',
                 'Boston MA':'ET', 
                 'Brooklyn NY':'ET', 
                 'Charlotte NC':'ET',
                 'Indianapolis IN':'ET',
                 'Detroit MI':'ET',
                 'Miami FL':'ET',
                 'New York NY':'ET',
                 'Orlando FL':'ET',
                 'Philadelphia PA':'ET',
                 'Toronto ON':'ET',
                 'Montreal PQ':'ET',
                 'Washington DC':'ET',
                 'Chicago IL':'CT',
                 'Birmingham AL':'CT',
                 'Houston TX':'CT',
                 'Dallas TX':'CT',
                 'Memphis TN':'CT',
                 'Milwaukee WI':'CT',
                 'Minneapolis MN':'CT',
                 'New Orleans LA':'CT',
                 'Oklahoma City OK':'CT',
                 'Tulsa OK':'CT',
                 'San Antonio TX':'CT',
                 'Austin TX':'CT',
                 'Mexico City':'CT',
                 'Denver CO':'MT',
                 'Phoenix AZ':'MT',
                 'Salt Lake City UT':'MT',
                 'Edmonton AB':'MT',
                 'Portland OR':'PT',
                 'Sacramento CA':'PT',
                 'Palm Springs CA':'PT',
                 'Anaheim CA':'PT',
                 'Seattle WA':'PT',
                 'Vancouver BC':'PT',
                 'Las Vegas NV':'PT',
                 'San Francisco CA':'PT',
                 'Los Angeles CA':'PT',
                 'Paris':'CET',
                 'Madrid':'CET',
                 'Tel Aviv':'IT',
                 'Saitama':'JT',
                 'London':'GMT',
                 'Abu Dhabi':'GT',
                 'Honolulu HI':'HAT'}
    
    # we want hard fail so we can add city to list
    #if city in timezones.keys():
    timezone = timezones[city]

    return timezone

# if reg season, game idx starts before playoffs
# if post or full season, game idx starts at 0
def determine_player_team_idx(player, player_team_idx, game_idx, row, games_played, teams_reg_and_playoff_games_played):
    #print('\n===Determine Player Team Idx: ' + player.title() + '===\n')
    
    # if type == postseason, then player team idx always =0
    # game type = season part
    game_type = row['Type']
    #print('game_type: ' + str(game_type))

    # if postseason then after trade deadline so last team this yr
    # postseason maybe playin listed after reg season
    if game_type == 'Postseason' or game_type == 'Playoff' or game_type == 'Playin': # if postseason, player_team_idx = 0 # recent/last team this yr
        player_team_idx = 0
    else:
        if int(game_idx) >= teams_reg_and_playoff_games_played: # > or >= make > bc we only need to go to next team if more games
            #if len(teams) > player_team_idx+1:            
            if len(games_played) > player_team_idx+1:
                player_team_idx += 1
                teams_reg_and_playoff_games_played += games_played[player_team_idx]                


    #print('player_team_idx: ' + str(player_team_idx))
    return player_team_idx



def determine_teams_reg_and_playoff_games_played(player_teams, player_season_log, season_part, season_year, cur_yr, gp_cur_team, player):
    #print('\n===Determine Teams Reg + Playoff Games Played: ' + player.title() + '===\n')
    
    # read all box scores if postseason to get more samples and compare to reg season
    if season_part == 'postseason':
        season_part = 'full'

    player_season_log_df = pd.DataFrame(player_season_log)
    season_part_game_log = determine_season_part_games(player_season_log_df, season_part)

    num_playoff_games = 0 # reg season idx
    if season_part == 'regular':
        if len(season_part_game_log.index) > 0:
            num_playoff_games = int(season_part_game_log.index[0]) # num playoff games not counting playin bc playn listed after 
    else: # full
        regseason_game_log = determine_season_part_games(player_season_log_df)
        if len(regseason_game_log.index) > 0:
            num_playoff_games = int(regseason_game_log.index[0])
    #print('num_playoff_games: ' + str(num_playoff_games))
    
    # determine player team for game at idx
    player_team_idx = 0 # bc recent games first
    # player_teams = {player:{year:{team:{GP:gp, MIN:min},...},...}}
    # team_stats_dict = {team:{GP:gp, MIN:min}}
    team_stats_dict = {}
    #team_gp_dict = {}
    if season_year in player_teams.keys():
        team_stats_dict = player_teams[season_year]
    # reverse team gp dict so same order as game idx recent to distant
    teams = list(reversed(team_stats_dict.keys()))
    all_teams_stats = list(reversed(team_stats_dict.values()))


    games_played = []#list(reversed(team_gp_dict.values()))
    for team_stats in all_teams_stats:
        if len(team_stats.keys()) > 0:
            games_played.append(team_stats['GP'])
    # get games played w/ current team from season log bc updates each day
    games_played = []
    if season_year != cur_yr:
        for team_stats in all_teams_stats:
            if len(team_stats.keys()) > 0:
                games_played.append(team_stats['GP'])
    else:
        # if more than 1 team this yr then get prev teams gp from player teams
        # then get cur team gp from season log
        # gp_other_teams = 0
        # if len(teams) > 0:
        #     for team_stats in all_teams_stats[1:]: 
        #         gp_other_teams += team_stats['GP']

        #gp_cur_team = num_games_played - gp_other_teams
        games_played.append(gp_cur_team)

        if len(teams) > 0:
            for team_stats in all_teams_stats[1:]: 
                if len(team_stats.keys()) > 0:
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
    teams_reg_and_playoff_games_played = int(reg_and_playoff_games_played[player_team_idx])
    

    # print('teams_reg_and_playoff_games_played: ' + str(teams_reg_and_playoff_games_played))
    # #print('season_part_game_log: ' + str(season_part_game_log))
    # print('teams: ' + str(teams))
    # print('games_played: ' + str(games_played))
    return (teams_reg_and_playoff_games_played, season_part_game_log, teams, games_played)

def determine_regular_season_games(player_game_log):

    #print('\n===Determine Regular Season Games for Player===\n')
    #print('player_game_log:\n' + str(player_game_log))

    reg_season_games_df = pd.DataFrame()

    # select reg season games by type
    if 'Type' in player_game_log.keys():
        # remove all star and exception games with *
        reg_season_games_df = reg_season_games_df[~reg_season_games_df['OPP'].str.endswith('*')].reset_index(drop=True)
        reg_season_games_df.index = reg_season_games_df.index.map(str)
        
        reg_season_games_df = reg_season_games_df[reg_season_games_df['Type'].str.startswith('Regular')]
        #print("partial reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
        
    else:
        print('Warning: Type key not in game log when determining season part games!')

    #print("final reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
    return reg_season_games_df

def determine_season_part_games(player_game_log, season_part='regular', player='player'):
    # print('\n===Determine Season Part Games for ' + player.title() + ', ' + season_part + '===\n')
    # #print('player_game_log:\n' + str(player_game_log))
    # print('Input: player_game_log = {stat name: {game idx: stat val, ... = {\'Player\': {\'0\': \'jalen brunson\', ...')
    # print('\nOutput: season_part_games_df = df\n')

    season_part_games_df = pd.DataFrame()

    if 'Type' in player_game_log.keys():
        # remove all star and exception games with *
        # always separate special games
        # reset index first so games line up with teams
        season_part_games_df = player_game_log[~player_game_log['OPP'].str.endswith('*')].reset_index(drop=True)
        
        # remove tournament games
        if season_part != 'tournament':
            season_part_games_df = season_part_games_df[~season_part_games_df['Type'].str.startswith('Tournament')].reset_index(drop=True)
        
        season_part_games_df.index = season_part_games_df.index.map(str)

        #print('season_part_games_df:\n' + str(season_part_games_df))

        # need to recognize games as preseason
        #season_part_games_df = player_game_log[~player_game_log['Type'].str.startswith('Preseason')]#pd.DataFrame()#player_game_log
        # dont need to reset index after removing preseason bc those games are at end of log idx
        season_part_games_df = season_part_games_df[~season_part_games_df['Type'].str.startswith('Preseason')]#pd.DataFrame()#player_game_log

        # cannot make default all game log bc we want to exclude preseason
        # select season part games by type
        # so we need to have accurate types set in read season log
        
        if season_part != 'full': # bc full does not have game type bc it takes all types
            season_part_games_df = season_part_games_df[season_part_games_df['Type'].str.startswith(season_part.title())]
            #print("partial reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
        #elif season_part == 'full':
            #season_part_games_df = player_game_log[~player_game_log['Type'].str.startswith('Preseason')]
        
        
    
    else:
        print('\n===Warning: Type key not in game log when determining season part games!===\n')


    #print("final season_part_games_df:\n" + str(season_part_games_df) + '\n')
    return season_part_games_df

# gather game logs by season and do not pull webpage if it does not exist
# season_year=0 so hard fail if no season given but then why not make required var?
# bc default should assume current season? no bc if we are looking them up they are probably in current season and it is more likely they did not play past season
# player_teams = {year:team:gp}
def determine_played_season(player_url, player_name='', season_year=0, all_game_logs={}, player_game_logs={}, player_teams={}):
    #print('\n===Determine if player ' + player_name.title() + ' played season ' + str(season_year) + '===\n')
    played_season = False

    #print('player_teams: ' + str(player_teams))
    #print('player_game_logs: ' + str(player_game_logs))

    if len(player_teams.keys()) > 0:
        #print('found player teams')
        #print('season year: ' + str(season_year))
        if str(season_year) in player_teams.keys():
            #print('player season team found in player TEAMS')
            played_season = True
    else: # player teams not given
        # all game logs too big as one var so consider replacing next version with player game logs
        if player_name in all_game_logs.keys() and str(season_year) in all_game_logs[player_name].keys():
            #print('player season game log found in ALL game logs')
            played_season = True

        # if using separate player logs, 1 per player for all seasons they played
        elif str(season_year) in player_game_logs.keys():
            #print('player season game log found in PLAYER game logs')
            played_season = True

        else:
            #print('player season game log not saved')

            try:

                html_results = reader.read_web_data(player_url)
                if html_results is not None:
                    len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

                    for order in range(len_html_results):
                        #print("order: " + str(order))

                        if len(html_results[order].columns.tolist()) == 17:

                            played_season = True
                            break

                
            except Exception as e:
                print('Page exists but no tables: ', e)
                #print('Exception could not get url: ', e)

    if not played_season:
        print('\nWarning: ' + player_name.title() + ' did NOT play season ' + str(season_year) + '!\n')

    return played_season

def determine_current_season_part(todays_games_date_obj=datetime.today()):
    #print('\n===Determine Current Season Part===\n')
    
    cur_part = 'regular'

    cur_mth = todays_games_date_obj.month
    cur_day = todays_games_date_obj.day
    # if cur_mth > 9 or cur_mth < 4:
    #     cur_part = 'regular'
    if cur_mth > 4 and cur_mth < 10:
        cur_part = 'postseason'
    elif cur_mth == 4 and cur_day > 14:
        cur_part = 'postseason'

    #print('cur_part: ' + cur_part)
    return cur_part

# use current month to tell season yr
def determine_current_season_year(todays_date_obj=datetime.today()):
    cur_season_yr = 0
    cur_month = todays_date_obj.month
    cur_yr = todays_date_obj.year
    if cur_month < 10:
        cur_season_yr = cur_yr
    else:
        cur_season_yr = cur_yr + 1

    # prefer string bc used as key in dict
    return str(cur_season_yr)