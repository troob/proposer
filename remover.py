# remover.py
# remove erroneous logs by key

import re, json, csv


def remove_stat_order(props):
    new_props = []
    
    for prop in props:
        prop = {i:prop[i] for i in prop if i!='stat order'}
        new_props.append(prop)
    
    return new_props









# valid for json files
def read_json(key_type):
	#print('\n===Read JSON===')
	keys_filename = key_type
	if not re.search('\.',key_type): # filename
		#key_type = re.sub('\s+','-',key_type)
		keys_filename = "data/" + key_type + ".json"
	#print("keys_filename: " + keys_filename + '\n')

	lines = [] # capture each line in the document
	keys = {}
	try:
		with open(keys_filename, encoding="UTF8") as keys_file:
			line = ''
			for key_info in keys_file:
				line = key_info.strip()
				lines.append(line)

			keys_file.close()

			# combine into 1 line
		condensed_json = ''
		for line in lines:
			#print('line: ' + str(line))
			condensed_json += line

		#print("Condensed JSON: " + condensed_json)

		# parse condensed_json
		keys = json.loads(condensed_json)
	except:
		print("\n===Warning: No JSON File: " + key_type + '===\n')
		#pass

	
	#print("keys: " + str(keys))
	return keys

# get data from a file and format into a list (same as generator version of this fcn but more general)
# input such as Game Data - All Games
# or Game Log - All Players
# header = keep first row (confusing need to change)
def extract_data(data_type, input_type='', extension='csv', header=False):
	
	#print('\n===Extract Data===\n')
	# maybe given filename if dot in name
	# to keep lowercase or not to keep lowercase, that is the question?
	# lowercase is easier to compare bc titles are irregular
	catalog_filepath = data_type
	if not re.search('\.', data_type):
		catalog_filepath = data_type + "." + extension
		if input_type != '':
			input_type = re.sub('/','_',input_type)
			catalog_filepath = data_type + " - " + input_type.title() + "." + extension
	if not re.search('/', data_type):
		catalog_filepath = "data/" + catalog_filepath
	#print("catalog_filepath: " + catalog_filepath)
	

	lines = []
	data = []
	all_data = []

	try: 

		with open(catalog_filepath, encoding="UTF8") as catalog_file:

			current_line = ""
			for catalog_info in catalog_file:
				current_line = catalog_info.strip()
				#print("current_line: " + str(current_line))
				lines.append(current_line)

			catalog_file.close()

		# skip header line
		read_lines = lines
		if not header: # file includes header but we do not want header
			read_lines = lines[1:]

		for line in read_lines:
			#print("line: " + str(line))
			if len(line) > 0:
				if extension == "csv":
					data = line.split(",")
				else:
					data = line.split("\t")
			all_data.append(data)

	except Exception as e:
		print("Error opening file. ", e)
	
	#print("all_data: " + str(all_data))
	return all_data

# given csv list make key val pairs
def extract_dict_from_data(data_type):

	game_ids = extract_data(data_type, header=True)
	existing_game_ids_dict = {}
	for row in game_ids:
		#print('row: ' + str(row))
		game_key = row[0]
		game_id = row[1]
		
		existing_game_ids_dict[game_key] = game_id

	#print('existing_game_ids_dict: ' + str(existing_game_ids_dict))
	return existing_game_ids_dict

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

def write_json_to_file(dict, filepath, write_param='w'):
    #print('\n===Write JSON to File: ' + filepath + '===\n')

    #filepath = re.sub('\s+','-',filepath) # is this needed or are spaces ok?
    with open(filepath, write_param) as outfile:
        json.dump(dict, outfile)

# # remove empty dicts from box scores
# # AND game IDs bc wrong
def remove_empty_box_scores():
    print('\n===Remove Empty Box Scores===\n')
	
    # remove wrong game ids
    # read game ids
    game_ids_file = 'data/all games ids.csv'
    init_game_ids = extract_dict_from_data(game_ids_file)
    final_game_ids = {}
	
    season_years = [2024, 2023]

    # remove empty box scores
    # read box scores
    for year in season_years:

        box_scores_file = 'data/raw box scores - ' + str(year) + '.json'
        print('box_scores_file: ' + box_scores_file)
        init_box_scores = read_json(box_scores_file)
        #print('init_box_scores: ' + str(init_box_scores))
        final_box_scores = {}

        

        # "tor phi 12/22/2023": {"away": {"starters": {"P Siakam PF": "36",...
        for game_key, game_id in init_game_ids.items():
            
            if game_key in init_box_scores.keys():
                game_box_scores = init_box_scores[game_key]

                # if not blank then add to final
                if len(game_box_scores.keys()) > 0:

                    final_box_scores[game_key] = game_box_scores

                    final_game_ids[game_key] = game_id


    if init_box_scores != final_box_scores:
        write_json_to_file(final_box_scores, box_scores_file)

    
    data = []#[[game_key, espn_id]]
    for game_key, game_id in final_game_ids.items():
        data.append([game_key, game_id])

    write_param = 'w' # overwrite ids to file
    if init_box_scores != final_box_scores:
        write_data_to_file(data, game_ids_file, write_param)






remove_empty_box_scores()

















# init_file = 'data/box scores - 2024-1.json'
# out_file = 'data/box scores - 2024.json'



# error_key = '-' # problem searching long form team name bc refers thunder refers to weather?


# # remove dash from player names
# def remove_from_json():
    
#     init_box_scores = reader.read_json(init_file)
    
#     final_box_scores = {}
    
#     for game_key, box_score in init_box_scores.items():
#         #print('game_key: ' + game_key)
#         final_box_scores[game_key] = {}
        
#         for team_loc, team_players in box_score.items():
#             final_box_scores[game_key][team_loc] = {}

#             for team_part, team_part_players in team_players.items():
#                 final_box_scores[game_key][team_loc][team_part] = {}

#                 for player, play_time in team_part_players.items():
#                     final_player = re.sub(error_key,' ',player)
#                     final_box_scores[game_key][team_loc][team_part][final_player] = play_time
    
#     writer.write_json_to_file(final_box_scores, out_file)

# def remove_from_csv():
#     init_game_ids = reader.extract_data(init_file, header=True)
#     game_ids = []

#     for row in init_game_ids:
#         #print('row:\n' + str(row))
#         game_key = row[0]

#         if not re.search(error_key, game_key)  : 
#             game_id = row[1]

#             if game_id not in game_ids:
#                 game_ids.append(game_id)

#                 data = [[game_key, game_id]]
#                 writer.write_data_to_file(data, out_file, 'a')



#remove_from_json()
                

