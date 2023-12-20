# read player lines
# input: player lines file
# output: player lines data

import reader # extract data

import math

from tabulate import tabulate # display output


data_type = "Player Lines"
input_type = '3/5' # date as mth/day will become mth_day in file

# v2: copy paste raw projected lines direct from website
# raw projected lines in format: [['Player Name', 'O 10 +100', 'U 10 +100', 'Player Name', 'O 10 +100', 'U 10 +100', Name', 'O 10 +100', 'U 10 +100']]
raw_projected_lines = reader.extract_data(data_type, input_type, extension='tsv', header=True) # tsv no header
print("raw_projected_lines: " + str(raw_projected_lines))

# for now set unavailable stats=1, until we have basic fcns working
reb = 1
ast = 1
three = 1
blk = 1
stl = 1
to = 1

# get location and opponent from header row above projected stats lines

# get all player names so we can get their espn IDs and from that get team, position, game log, and schedule
player_names = []
for row in raw_projected_lines:
    if row[0] != 'PLAYER' and not row[0][:3].isupper():
        #print('found player line')
        player_names.append(row[0])

#print("player_names: " + str(player_names))

player_espn_ids_dict = reader.read_all_player_espn_ids(player_names)
all_player_teams = reader.read_all_players_teams(player_espn_ids_dict)
        

# convert raw projected lines to projected lines
header_row = ['Name', 'PTS', 'REB', 'AST', '3PT', 'BLK', 'STL', 'TO','LOC','OPP']
all_player_lines = [header_row]

all_game_lines_dicts = {} # each stat separately

# raw_projected_lines: [['PHO SunsatDAL MavericksTODAY 1:10PM'], ['PLAYER', 'OVER', 'UNDER'], ['Chris Paul', 'O 9.5  +105', 'U 9.5  −135']]
# assign player lines to a game so we can get loc and opp from game info key

# split columns in raw projected lines so we can loop thru each stat separately
pts_projected_lines = []
reb_projected_lines = []
ast_projected_lines = []

for line in raw_projected_lines:
    print('raw line: ' + str(line))
    pts_line = line[:3]
    pts_projected_lines.append(line[:3])
    reb_projected_lines.append(line[3:6])
    ast_projected_lines.append(line[6:9])

separate_projected_lines = {'pts':pts_projected_lines, 'reb':reb_projected_lines, 'ast':ast_projected_lines}
print('separate_projected_lines: ' + str(separate_projected_lines))

# all_game_lines_dicts = { 'stat_name': 'game_key': [lines]}
for stat_name, projected_lines in separate_projected_lines.items():
    if len(projected_lines[0]) > 0:
        print('stat_name: ' + stat_name)
        game_key = ''
        game_lines_dict = {} # { 'PHO SunsatDAL MavericksTODAY 1:10PM': [['Chris Paul', 'O 9.5  +105', 'U 9.5  −135'],..]}

        for row in projected_lines:
            print('row: ' + str(row))
            # loop thru rows until we see header. then make header key in dict and add next rows to list of values until next header
            # if first item = 'PLAYER' skip bc not needed header
            # then if first 3 letters are uppercase we know it is team matchup header w/ needed info
            if len(row) > 0:
                if row[0] != 'PLAYER':
                    if row[0][:3].isupper():
                        #print('found header: ' + str(row) + ', ' + row[0][:3])
                        game_key = row[0]
                        # if not game_key in game_lines_dict.keys():
                        #     game_lines_dict[game_key] = []

                    else:
                        #print('found player line: ' + str(row))
                        if game_key in game_lines_dict.keys():
                            game_lines_dict[game_key].append(row)
                        else:
                            game_lines_dict[game_key] = [row]

        print("game_lines_dict: " + str(game_lines_dict))

        all_game_lines_dicts[stat_name] = game_lines_dict

print("all_game_lines_dicts: " + str(all_game_lines_dicts))

player_lines_dict = {} # {pts:0,reb:0,..}
all_player_lines_dicts = {} # {'player name':{pts:0,reb:0,..}}

# game info = 'PHO SunsatDAL MavericksTODAY 1:10PM'
for stat_name, game_lines_dict in all_game_lines_dicts.items():

    print('stat_name: ' + stat_name)

    for game_info, game_lines in game_lines_dict.items():
        teams = game_info.split('at')
        away_team = teams[0]
        home_team = teams[1]
        #print("away_team: " + str(away_team))
        #print("home_team: " + str(home_team))

        irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nor':'nop', 'pho':'phx', 'was':'wsh', 'uth': 'uta' } # for these match the first 3 letters of team name instead

        away_abbrev = away_team.split()[0].lower()
        if len(away_abbrev) == 2:
            away_abbrev = away_abbrev + away_team.split()[1][0].lower()

        if away_abbrev in irregular_abbrevs.keys():
            #print("irregular abbrev: " + team_abbrev)
            away_abbrev = irregular_abbrevs[away_abbrev]

        home_abbrev = home_team.split()[0].lower()
        if len(home_abbrev) == 2:
            home_abbrev = home_abbrev + home_team.split()[1][0].lower()
        if home_abbrev in irregular_abbrevs.keys():
            #print("irregular abbrev: " + team_abbrev)
            home_abbrev = irregular_abbrevs[home_abbrev]

        #print("away_abbrev: " + str(away_abbrev))
        #print("home_abbrev: " + str(home_abbrev))

        for raw_player_line in game_lines:

            # each stat has 3 columns pts, reb, ast,...
            # but not all players have all stats so the lines do not line up
            # so we must divide each stat and sort by player name

            player_name = raw_player_line[0]

            player_team_abbrev = all_player_teams[player_name]
            #print("player_team_abbrev: " + str(player_team_abbrev))
            # determine opponent from game info by eliminating player's team from list of 2 teams
            if player_team_abbrev == away_abbrev:
                loc = 'away'
                opp = home_abbrev
            else:
                loc = 'home'
                opp = away_abbrev
            # only add loc and opp once per player per game
            if not player_name in all_player_lines_dicts.keys():
                all_player_lines_dicts[player_name] = { 'loc': loc }
                all_player_lines_dicts[player_name] = { 'opp': opp }
            else:
                all_player_lines_dicts[player_name]['loc'] = loc 
                all_player_lines_dicts[player_name]['opp'] = opp

            

            stat = math.ceil(float(raw_player_line[1].split()[1])) # O 10.5 +100
            #print("pts: " + str(pts))
            #reb = math.ceil(float(raw_player_line[4].split()[1])) # O 10.5 +100

            all_player_lines_dicts[player_name][stat_name] = stat


print("all_player_lines_dicts: " + str(all_player_lines_dicts))

for player_name, player_lines in all_player_lines_dicts.items():
    #header_row = ['Name', 'PTS', 'REB', 'AST', '3PT', 'BLK', 'STL', 'TO','LOC','OPP']
    pts = 10
    if 'pts' in player_lines.keys():
        pts = player_lines['pts']
    reb = 2
    if 'pts' in player_lines.keys():
        reb = player_lines['reb']
    ast = 2
    if 'ast' in player_lines.keys():
        ast = player_lines['ast']
    loc = player_lines['loc']
    opp = player_lines['opp']
    player_line = [player_name, pts, reb, ast, three, blk, stl, to, loc, opp]
    all_player_lines.append(player_line)
    
print("all_player_lines:\n" + tabulate(all_player_lines))
