# proposition-generator.py
# we need to know how players play under certain conditions
# to propose likely outcomes

import generator

players = ['jeff green']

# settings
find_matchups = False
find_players = False
settings = {'find matchups': find_matchups, 'find players': find_players}

props = generator.generate_players_props(players, settings)