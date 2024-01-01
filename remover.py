# remover.py
# remove erroneous logs by key

import reader, writer, re

init_file = 'data/box scores - 2024-1.json'
out_file = 'data/box scores - 2024.json'



error_key = '-' # problem searching long form team name bc refers thunder refers to weather?


# remove dash from player names
def remove_from_json():
    
    init_box_scores = reader.read_json(init_file)
    
    final_box_scores = {}
    
    for game_key, box_score in init_box_scores.items():
        #print('game_key: ' + game_key)
        final_box_scores[game_key] = {}
        
        for team_loc, team_players in box_score.items():
            final_box_scores[game_key][team_loc] = {}

            for team_part, team_part_players in team_players.items():
                final_box_scores[game_key][team_loc][team_part] = {}

                for player, play_time in team_part_players.items():
                    final_player = re.sub(error_key,' ',player)
                    final_box_scores[game_key][team_loc][team_part][final_player] = play_time
    
    writer.write_json_to_file(final_box_scores, out_file)

def remove_from_csv():
    init_game_ids = reader.extract_data(init_file, header=True)
    game_ids = []

    for row in init_game_ids:
        #print('row:\n' + str(row))
        game_key = row[0]

        if not re.search(error_key, game_key)  : 
            game_id = row[1]

            if game_id not in game_ids:
                game_ids.append(game_id)

                data = [[game_key, game_id]]
                writer.write_data_to_file(data, out_file, 'a')



remove_from_json()