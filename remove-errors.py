# remove errors

import reader, writer

# remove empty dicts from box scores
# AND game IDs bc wrong
def remove_empty_box_scores():

    # remove empty box scores
    # read box scores
    box_scores_file = 'data/raw box scores - 2024.json'
    init_box_scores = reader.read_json(box_scores_file)

    final_box_scores = {}

    # remove wrong game ids
    # read game ids
    game_ids_file = 'data/all games ids.csv'
    init_game_ids = reader.extract_dict_from_data(game_ids_file)
    final_game_ids = {}

    # "tor phi 12/22/2023": {"away": {"starters": {"P Siakam PF": "36",...
    for game_key, game_box_scores in init_box_scores.items():

        # if not blank then add to final
        if len(game_box_scores.keys()) > 0:

            final_box_scores[game_key] = game_box_scores

            final_game_ids[game_key] = init_game_ids[game_key]


    if init_box_scores != final_box_scores:
        writer.write_json_to_file(final_box_scores, box_scores_file)

    
    data = []#[[game_key, espn_id]]
    for game_key, game_id in final_game_ids.items():
        data.append([game_key, game_id])

    write_param = 'w' # overwrite ids to file
    if init_box_scores != final_box_scores:
        writer.write_data_to_file(data, game_ids_file, write_param)

remove_empty_box_scores()