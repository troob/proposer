# change to lowercase
# init saved player names as titles but that needs more code to compare due to irregular names so lower all names

import reader, writer, re

init_file = 'data/Player Ids.csv'
out_file = 'data/all players ids.csv'

init_player_ids = reader.extract_data(init_file, header=True)
player_ids = []

for row in init_player_ids:
    #print('row:\n' + str(row))
    player_name = re.sub('\.','',row[0]).lower()
    player_name = re.sub('-', ' ', player_name)
    player_id = row[1]

    if player_id not in player_ids:
        player_ids.append(player_id)

        data = [[player_name, player_id]]
        writer.write_data_to_file(data, out_file, 'a')