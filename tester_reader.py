# reader.py
# functions for a reader

import re, json
from datetime import datetime

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

# cur vals get updated each day
# prev vals are perm
def read_cur_and_prev_json(cur_file,prev_file,current_year_str=''):
	#print('\n===Read Cur and Prev JSON===')
	# print('cur_file: ' + cur_file)
	# print('prev_file: ' + prev_file + '\n')

	cur_and_prev = {}

	cur_dict = read_json(cur_file)
	prev_dict = read_json(prev_file)

	if current_year_str == '':
		current_year_str = determine_current_season_year()


	if len(cur_dict.keys()) > 0:
		cur_and_prev[current_year_str] = cur_dict
	for year, year_log in prev_dict.items():
		cur_and_prev[year] = year_log

	#print('cur_and_prev: ' + str(cur_and_prev))
	return cur_and_prev

def read_player_stat_dict(player_name, current_year_str='', todays_date=datetime.today().strftime('%m-%d-%y')):
	#print('\n===Read Player Stat Dict: ' + player_name.title() + '===\n')

	if current_year_str == '':
		current_year_str = determine_current_season_year()

	player_cur_stat_dict_filename = 'data/stat dicts/' + player_name + ' ' + current_year_str + ' stat dict ' + todays_date + '.json'
	player_prev_stat_dicts_filename = 'data/stat dicts/' + player_name + ' prev stat dicts.json'
	init_player_stat_dict = read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename)

	#print('init_player_stat_dict: ' + str(init_player_stat_dict))
	return init_player_stat_dict

