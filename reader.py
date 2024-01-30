# reader.py
# functions for a reader

# === Standard External Libraries ===
from bs4 import BeautifulSoup # read html from webpage

import csv

from datetime import datetime # get current year so we can get current teams

import copy # deepcopy game logs json so we can add to it before writing to file without losing data
import json # we need projected lines table to be json so we can refer to player when analyzing stats
import math # round up to nearest integer while reading
import pandas as pd # read html results from webpage
#import random # random user agents to avoid being blocked for too many requests

import re
import requests # track timeout error

from tabulate import tabulate # display output, which for the reader is input files to confirm and review their contents

import time # halt code to retry website request, # need to read dynamic webpages

from selenium import webdriver # need to read html5 webpages
from webdriver_manager.chrome import ChromeDriverManager # need to access dynamic webpages
#from selenium.webdriver.chrome.options import Options # block ads

from urllib.error import URLError
from urllib.request import Request, urlopen # request website, open webpage given req

# === Local Internal Libraries ===
import converter # convert year span to current season
import determiner # determine played season before reading webpage to avoid exception/error
import isolator # isolate_player_game_data to read data from file
import writer # write to file so we can check if data exists in local file so we can read from file



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

# read website given url, timeout in seconds, and max. no. retries before going to next step
def read_website(url, timeout=10, max_retries=3):
	# print('\n===Read Website===\n')
	# print('url: ' + url)
	#soup = BeautifulSoup() # return blank soup if request fails

	retries = 0

	# these user agents cause misreading page?
	# user_agents = [
	# 	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
	# ]

	while retries < max_retries:
		try:
			#make the request
			headers = {'User-Agent': 'Mozilla/5.0'}
			#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
			#headers = {'User-Agent': random.choice(user_agents)}
			req = Request(url, headers=headers)
			page = urlopen(req, timeout=timeout) # response

			#data = page.read()

			soup = BeautifulSoup(page, features='lxml')

			#print("Request successful.")

			return soup
		

		except URLError as e:

			if isinstance(e.reason, TimeoutError):
				# If a timeout occurs, wait for 10 seconds and then retry\
				retries += 1
				print(f"Timeout error occurred. Retrying {retries}/{max_retries}...", e, e.getheaders(), e.gettext(), e.getcode())
				time.sleep(10)
			else:
                # If the error is different than a timeout, raise it
				#raise
				# if too many requests, do not retry
				if str(e) == 'HTTP Error 404: Not Found' or str(e) == 'HTTP Error 429: Too Many Requests':
					print(f"URLError, " + str(e) + ', ' + url)
					return str(e)
				else:
					retries += 1
					print(f"URLError error occurred. Retrying {retries}/{max_retries}...", e, url)#, e.getheaders(), e.gettext(), e.getcode())
					time.sleep(10)
				
			
		except Exception as e:
            # If any other exception occurs, raise it
			#raise
			retries += 1
			print(f"Exception error occurred. Retrying {retries}/{max_retries}...", e)#, e.getheaders(), e.gettext(), e.getcode())
			time.sleep(10)
		except:
			print(f"server not found?")
			#raise
			retries += 1
			time.sleep(10)

	print("Maximum retries reached.")
	return None

	




# read tables in websites with pandas pd dataframes
def read_web_data(url, timeout=10, max_retries=3):
	#print('\n===Read Web Data===\n')
	# display tables in readable format
	pd.set_option('display.max_columns', None)

	# user_agents = [
	# 	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
	# 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
	# ]

	retries = 0
	while retries < max_retries:
		try:
			#response = requests.get(url, timeout=timeout)
			#response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

			#list_of_dataframes = pd.read_html(url)
			headers = {'User-Agent': 'Mozilla/5.0'}#headers = {'User-Agent': random.choice(user_agents)}#'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
			r = requests.get(url, headers=headers, timeout=timeout)
			#r.raise_for_status(headers=headers)
			#print('r: ' + str(r))
			c = r.content
			#print('c: ' + str(c))
			list_of_dataframes = pd.read_html(c)

			#print("Request successful, data retrieved.\n")
			#print('list_of_dataframes: ' + str(list_of_dataframes))

			return list_of_dataframes

		except requests.exceptions.Timeout as e:
			print(f"Timeout error occurred. Retrying {retries + 1}/{max_retries}...", e, e.getheaders(), e.gettext(), e.getcode())
			retries += 1
			time.sleep(10)
		except requests.exceptions.HTTPError as e:
			print(f"HTTP error occurred: {e}", e.getheaders(), e.gettext(), e.getcode())
			#raise
			retries += 1
			time.sleep(10)
		except requests.exceptions.RequestException as e:
			print(f"Request failed: {e}")#, e.get_headers(), e.get_text(), e.get_code())
			#raise
			retries += 1
			time.sleep(10)
		except Exception as e:
            # If any other exception occurs, retry
			#raise
			if re.search('No tables', str(e)):
				print('Error: No Tables Found: ', e, url)
				return None
			else:
				retries += 1
				print(f"Exception error occurred. Retrying {retries}/{max_retries}...", e)#, e.getheaders(), e.gettext(), e.getcode())
				time.sleep(10)
		except:
			print(f"server not found?")
			#raise
			retries += 1
			time.sleep(10)

	print("Maximum retries reached.")
	return None



# in this format 1 file has current year and other file has prev yrs
def read_json_multiple_files(files):

	final_dict = {} 

	for file in files:
		print('file: ' + file)
		init_stat_dict = read_json(file)

		for key, val in init_stat_dict.items():
			final_dict[key] = val

	return final_dict

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
		current_year_str = determiner.determine_current_season_year()


	if len(cur_dict.keys()) > 0:
		cur_and_prev[current_year_str] = cur_dict
	for year, year_log in prev_dict.items():
		cur_and_prev[year] = year_log

	#print('cur_and_prev: ' + str(cur_and_prev))
	return cur_and_prev




















# https://www.espn.com/nba/team/schedule/_/name/cha/charlotte-hornets
def read_team_schedule_from_internet(team_abbrev):
	print('\n===Read Team Schedule from Internet: ' + team_abbrev + '===\n')

	team_schedule = {}

	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	team_name = converter.convert_team_abbrev_to_name(team_abbrev)
	team_name = re.sub(' ', '-', team_name)
	team_abbrev = converter.convert_team_abbrev_to_espn_abbrev(team_abbrev)
	schedule_url = 'https://www.espn.com/nba/team/schedule/_/name/' + team_abbrev + '/' + team_name #cha/charlotte-hornets'

	html_results = read_web_data(schedule_url)

	if len(html_results) > 0:
		schedule_df = html_results[0]

		team_schedule = schedule_df.to_dict()

	print('team_schedule: ' + str(team_schedule))
	return team_schedule

def read_team_schedule(team, init_all_teams_schedules):
	# print('\n===Read Team Schedule: ' + team + '===\n')
	# print('\nOutput: team_schedule = {field idx:{\'0\':field name, game num:field val, ... = {"0": {"0": "DATE", "1": "Tue, Oct 24", "2": "Thu, Oct 26", ...\n')

	team_schedule = {}

	if team in init_all_teams_schedules.keys():
		team_schedule = init_all_teams_schedules[team]

	else:
		team_schedule = read_team_schedule_from_internet(team)


	#print('team_schedule: ' + str(team_schedule))
	return team_schedule

def read_all_teams_schedules(game_teams):
	print('\n===Read All Teams Schedules===\n')
	print('\nOutput: all_teams_schedules = {team: {field idx:{\'0\':field name, game num:field val, ... = {"phx": {"0": {"0": "DATE", "1": "Tue, Oct 24", "2": "Thu, Oct 26", ...\n')

	all_teams_schedules_file = 'data/all teams schedules.json'
	init_all_teams_schedules = read_json(all_teams_schedules_file)
	#print("init_all_teams_schedules: " + str(init_all_teams_schedules))
	all_teams_schedules = copy.deepcopy(init_all_teams_schedules) # need to init as saved teams so we can see difference at end

	for game in game_teams:
		for team in game:
			team_schedule = read_team_schedule(team, all_teams_schedules)
			all_teams_schedules[team] = team_schedule

	if not init_all_teams_schedules == all_teams_schedules:
		writer.write_json_to_file(all_teams_schedules, all_teams_schedules_file)

	#print('all_teams_schedules: ' + str(all_teams_schedules))
	return all_teams_schedules


def read_player_prev_stat_vals(season_log_of_interest):

	prev_stat_vals = {}
	
	stats_of_interest = ['pts','ast','reb']

	for stat_name in stats_of_interest:
	#for stat_name, stat_log in season_log_of_interest.items():
		prev_stat_val = int(season_log_of_interest[stat_name.upper()]['0'])
		prev_stat_vals[stat_name] = prev_stat_val

	return prev_stat_vals

# read along with current conditions
def read_all_prev_stat_vals(all_players_season_logs, season_year):
	print('\n===Read All Prev Stat Vals===\n')
	print('Input: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
	print('\nOutput: all_prev_stat_vals = {player:{stat name:prev val,...}, ... = {\'clint capela\': {\'pts\': 6, \'ast\': 0, \'reb\': 9}}\n')

	all_prev_stat_vals = {}

	for player, player_season_logs in all_players_season_logs.items():
		print('\nPlayer: ' + player.title())
		print('player_season_logs: ' + str(player_season_logs))
		player_prev_stat_vals = {}
		# dict goes from recent to distant so take first 1
		if len(player_season_logs.keys()) > 0:
			season_log_of_interest = list(player_season_logs.values())[0]#[str(season_year)]
			print('season_log_of_interest: ' + str(season_log_of_interest))

			player_prev_stat_vals = read_player_prev_stat_vals(season_log_of_interest)
			
		all_prev_stat_vals[player] = player_prev_stat_vals

	print('all_prev_stat_vals: ' + str(all_prev_stat_vals))
	return all_prev_stat_vals

# get team season schedule from espn.com
def read_team_season_schedule(team_name, season_year=2024, team_url='', team_id=''):
	#print("\n===Read Team " + team_name.title() + ", Season " + str(season_year) + " Schedule===\n")

	# get espn player id from google so we can get url
	if team_url == '':
		if team_id == '':
			team_id = read_team_espn_id(team_name)
		#season_year = 2023
		team_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + team_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
		#print("team_url: " + team_url)

	player_game_log = []

	#dfs = pd.read_html(player_url)
	#print(f'Total tables: {len(dfs)}')

	#try:

	html_results = read_web_data(team_url) #pd.read_html(team_url)
	#print("html_results: " + str(html_results))

	parts_of_season = [] # pre season, regular season, post season

	len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

	for order in range(len_html_results):
		#print("order: " + str(order))

		if len(html_results[order].columns.tolist()) == 17:

			part_of_season = html_results[order]

			# look at the formatting to figure out how to separate table and elements in table
			if len_html_results - 2 == order:
				part_of_season['Type'] = 'Preseason'

			else:
				if len(part_of_season[(part_of_season['OPP'].str.contains('GAME'))]) > 0:
					part_of_season['Type'] = 'Postseason'
				else:
					part_of_season['Type'] = 'Regular'

			parts_of_season.append(part_of_season)

		else:
			#print("Warning: table does not have 17 columns so it is not valid game log.")
			pass

	player_game_log_df = pd.DataFrame()

	if len(parts_of_season) > 0:

		player_game_log_df = pd.concat(parts_of_season, sort=False, ignore_index=True)

		player_game_log_df = player_game_log_df[(player_game_log_df['OPP'].str.startswith('@')) | (player_game_log_df['OPP'].str.startswith('vs'))].reset_index(drop=True)

		player_game_log_df['Season'] = str(season_year-1) + '-' + str(season_year-2000)

		player_game_log_df['Player'] = player_name

		player_game_log_df = player_game_log_df.set_index(['Player', 'Season', 'Type']).reset_index()

		# Successful 3P Attempts
		player_game_log_df['3PT_SA'] = player_game_log_df['3PT'].str.split('-').str[0]

		# All 3P Attempts
		player_game_log_df['3PT_A'] = player_game_log_df['3PT'].str.split('-').str[1]
		player_game_log_df[
			['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

			] = player_game_log_df[

				['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

				].astype(float)

	# display player game log in readable format
	#pd.set_option('display.max_columns', 100)
	pd.set_option('display.max_columns', None)
	#print("player_game_log_df:\n" + str(player_game_log_df))

	# except Exception as e:
	# 	print("Error reading game log " + str(e))
	# 	pass

	# if we want to format table in 1 window we can get df elements in lists and then print lists in table
	# header_row = ['Date', 'OPP', 'Result', 'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS']

	# table = [header_row]
	# for row in player_game_data:
	# 	table.append(row)

	# print("\n===" + player_name + "===\n")
	# print(tabulate(table))
	#print("player_game_log: " + str(player_game_log))
	return player_game_log_df # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword









# for all given players, read their teams
# players_teams_dict = {player:team, ...}
# read current team from player page
def read_all_players_current_teams(all_players_espn_ids, read_new_teams=True, cur_yr='', todays_date=datetime.today().strftime('%m/%d/%y') ):
	print("\n===Read All Players Current Teams===\n")
	players_teams_dict = {}

	
	# if not read new teams,
	# see if team saved in file
	# bc if read new teams then we will create new file with today's date in name
	existing_player_teams_dict = {}
	if not read_new_teams:
		data_type = 'player teams'
		# if we are creating new file get todays date to format filename 
		# player teams - m/d/y.csv
		input_type = todays_date
		player_teams = extract_data(data_type, header=True)
		
		for row in player_teams:
			#print('row: ' + str(row))
			player_name = row[0]
			player_team = row[1]

			existing_player_teams_dict[player_name] = player_team
		#print('existing_player_teams_dict: ' + str(existing_player_teams_dict))

	for name, id in all_players_espn_ids.items():
		team = read_player_team(name, id, existing_player_teams_dict, read_new_teams, cur_yr)
		players_teams_dict[name] = team

	# if read new teams for all players then we can overwrite the file completely removing all old teams bc we cannot assume any player is on the same team as they were before
	if read_new_teams:
		# overwrite for the first one and then append all following
		p_idx = 0
		for player_name, player_team in players_teams_dict.items():

			write_param = 'a'
			if p_idx == 0:
				write_param = 'w'

			data = [[player_name, team]]
			filepath = 'data/Player Teams.csv'
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

			p_idx += 1

	#print("players_teams_dict: " + str(players_teams_dict))
	return players_teams_dict



# read all teams rosters so we can tell each players team
# is it worth saving prev yr rosters?
# not really bc if they did not play all yr then they would not show in teams players, which is what we want bc they are inconsequential
# so we only need current teams rosters
# why does it need other teams rosters than the ones of interest?
def read_all_current_teams_rosters():
	print("\n===Read All Current Teams Rosters===\n")

# show matchup data against each position so we can see which position has easiest matchup
# matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
def read_matchup_data(source_url):
	#print("\n===Read Matchup Data===\n")

	matchup_data = [] # matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]

	# swish source which uses html 5 is default for now bc we need to define df outside if statement
	
	matchup_df = pd.DataFrame()

	if re.search('fantasypro|hashtag|swish',source_url): # swish analytics uses html5
		

		#chop = webdriver.ChromeOptions()
		#chop.add_extension('adblock_5_4_1_0.crx')
		#driver = webdriver.Chrome(chrome_options = chop)

		driver = webdriver.Chrome(ChromeDriverManager().install())
		driver.implicitly_wait(3)

		driver.get(source_url) # Open the URL on a google chrome window
		
		#time.sleep(3) # As this is a dynamic html web-page, wait for 3 seconds for everything to be loaded

		# if needed, Accept the cookies policy
		# driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
		#time.sleep(3)

		# click on the pagination elements to select not only the page 1 but all pages
		#position_btn_path = '/html/body/div' #main/div/div/div/div/div/ul/li[1]/a'
		#driver.find_element('xpath', '/html/body/div').click()

		#position_btn = (driver.find_element('xpath', '/html/body/div').text())
		#print("position_btn: " + str(position_btn))
		#driver.find_element_by_xpath(position_btn_path).click()
		#time.sleep(3)

		#ad = driver.find_element('id', 'div-gpt-ad-1556117653136-0').find_element('xpath','div/iframe')
		#print("ad: " + ad.get_attribute('outerHTML'))

		# click x on advertisement so we can click btns below it
		#ad_close = driver.find_element('xpath','//*[@id="closebutton"]')
		#print("ad_close: " + ad_close.get_attribute('outerHTML'))
		#ad_close.click(); #Close Ad
		#time.sleep(3)

		if re.search('fantasypro',source_url):
			# close ad
			if driver.find_elements("id", "google_ads_iframe_/2705664/fantasypros_interstitial_1_0"):
				driver.switch_to.frame(driver.find_element("id", "google_ads_iframe_/2705664/fantasypros_interstitial_1_0"))
				#l = driver.find_element('xpath', 'html/body/div')
				l = driver.find_element('id', 'closebutton')
				h1= driver.execute_script("return arguments[0].outerHTML;",l)
				print("h1: " + str(h1))
				# driver.switch_to.frame(driver.find_element("tag name", "iframe"))
				# l = driver.find_element('xpath', 'html/body')
				# h2= driver.execute_script("return arguments[0].innerHTML;",l)
				# print("h2: " + str(h2))
				l.click(); #Close Ad

				driver.switch_to.default_content()

			# get the defense matchup table as text

			#defense_table_path = 'html/body/' #main/div/div/div/div[6]/data-table/tbody'
			#matchup_table = driver.find_element('id', 'data-table')
			#print("matchup_table: " + str(matchup_table))

			# not all sources have all team defense and not needed yet so add later
			# position_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[1]/a')
			# print("position_btn: " + position_btn.get_attribute('innerHTML'))
			# position_btn.click()
			# #time.sleep(3)

			# team_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			# print("team_matchup_df\n" + str(team_matchup_df))


			pg_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[2]/a')
			#print("pg_btn: " + pg_btn.get_attribute('innerHTML'))
			pg_btn.click()
			#time.sleep(3)

			pg_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			#print("pg_matchup_df\n" + str(pg_matchup_df))


			sg_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[3]/a')
			#print("sg_btn: " + sg_btn.get_attribute('innerHTML'))
			sg_btn.click()
			#time.sleep(3)

			sg_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			#print("sg_matchup_df\n" + str(sg_matchup_df))


			sf_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[4]/a')
			#print("sf_btn: " + sf_btn.get_attribute('innerHTML'))
			sf_btn.click()
			#time.sleep(3)

			sf_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			#print("sf_matchup_df\n" + str(sf_matchup_df))


			pf_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[5]/a')
			#print("pf_btn: " + pf_btn.get_attribute('innerHTML'))
			pf_btn.click()
			#time.sleep(3)

			pf_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			#print("pf_matchup_df\n" + str(pf_matchup_df))


			c_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[6]/a')
			#print("c_btn: " + c_btn.get_attribute('innerHTML'))
			c_btn.click()
			#time.sleep(3)

			c_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			#print("c_matchup_df\n" + str(c_matchup_df))

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]

		elif re.search('hashtag',source_url):
			print("Pull data from hastag bball.")

			all_matchup_df=pd.read_html(driver.find_element('id', "ContentPlaceHolder1_GridView1").get_attribute('outerHTML'))[0]
			#print("all_matchup_df\n" + str(all_matchup_df))

			pg_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'PG']
			#print("pg_matchup_df\n" + str(pg_matchup_df))
			sg_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'SG']
			#print("sg_matchup_df\n" + str(sg_matchup_df))
			sf_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'SF']
			#print("sf_matchup_df\n" + str(sf_matchup_df))
			pf_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'PF']
			#print("pf_matchup_df\n" + str(pf_matchup_df))
			c_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'C']
			#print("c_matchup_df\n" + str(c_matchup_df))

			# they do not give all team defense so we must calculate or remove from other sources if not needed. it is needed bc good to know overall defense in positionless bball
			# get list of all team names and then make subset tables by team
			# team_names = all_matchup_df['Sort: Team'].unique
			# print("team_names: " + str(team_names))
			# for team_name in team_names:
			# 	team_matchup_df = all_matchup_df[all_matchup_df['Sort: Team'] == team_name]
			# 	print("team_matchup_df\n" + str(team_matchup_df))

			# 	pts_mean = team_matchup_df['Sort: PTS'].mean()

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
			
		elif re.search('swish',source_url):
			print("Pull data from Swish.")

			time.sleep(2) #needs to load

			pg_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[2]/a')
			#print("pg_btn: " + pg_btn.get_attribute('innerHTML'))
			pg_btn.click()
			

			pg_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			#print("pg_matchup_df\n" + str(pg_matchup_df))


			sg_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[3]/a')
			#print("sg_btn: " + sg_btn.get_attribute('innerHTML'))
			sg_btn.click()
			
			sg_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			#print("sg_matchup_df\n" + str(sg_matchup_df))


			sf_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[4]/a')
			#print("sf_btn: " + sf_btn.get_attribute('innerHTML'))
			sf_btn.click()
			
			sf_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			#print("sf_matchup_df\n" + str(sf_matchup_df))


			pf_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[5]/a')
			#print("pf_btn: " + pf_btn.get_attribute('innerHTML'))
			pf_btn.click()
			
			pf_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			#print("pf_matchup_df\n" + str(pf_matchup_df))


			c_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[6]/a')
			#print("c_btn: " + c_btn.get_attribute('innerHTML'))
			c_btn.click()
			
			c_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			#print("c_matchup_df\n" + str(c_matchup_df))

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
			
		else:
			team_matchup_df=pd.read_html(driver.find_element('id', "ContentPlaceHolder1_GridView1").get_attribute('outerHTML'))[0]
			#print("team_matchup_df\n" + str(team_matchup_df))

		# close the google chrome window
		driver.quit()

		
	else:
		# first get the html as a pandas dataframe format
		html_results = read_web_data(source_url) #pd.read_html(source_url)
		#print("html_results: " + str(html_results))

	return matchup_data

# sources disagree so we need to find consensus or just be aware of the risk of inaccurate data
# show all 5 sources so we can see the conflicts and therefore risk of inaccurate data
def read_all_matchup_data(matchup_data_sources):
	print("\n===Read All Matchup Data===\n")

	all_matchup_data = []

	for source in matchup_data_sources:
		
		source_matchup_data = read_matchup_data(source)
		all_matchup_data.append(source_matchup_data)

	return all_matchup_data


def extract_json_from_file(data_type, input_type, extension='csv'):
	catalog_filename = "data/" + data_type.title() + " - " + input_type.title() + "." + extension

	# create a dictionary
	data_dict = {}
	
	lines = []
	#data = []
	all_data = []

	try: 

		with open(catalog_filename, encoding="UTF8") as catalog_file:

			csvReader  =csv.DictReader(catalog_file)

			# Convert each row into a dictionary
			# and add it to data
			for rows in csvReader:
				
				# Assuming a column named 'No' to
				# be the primary key
				key = rows['Name']
				data_dict[key] = rows

	except Exception as e:
		print("Error opening file. ", e)
	
	print("data_dict: " + str(data_dict))


	return data_dict

# use when reading table cell with multiple values representing different fields inconveniently placed in same cell, 
# eg score,rank in same cell
def format_stat_val(col_val):
	stat_val = 0.0
	if re.search('\\s',str(col_val)): # eg '20.3 15' for 'avg rank'
		stat_val = float(re.split('\\s',col_val)[0])
	else:
		stat_val = float(col_val)

	return stat_val

def read_season_log_from_file(data_type, player_name, ext):
	
	all_pts = []
	all_rebs = []
	all_asts = []
	all_winning_scores = []
	all_losing_scores = []
	all_minutes = []
	all_fgms = []
	all_fgas = []
	all_fg_rates = []
	all_threes_made = []
	all_threes_attempts = []
	all_three_rates = []
	all_ftms = []
	all_ftas = []
	all_ft_rates = []
	all_bs = []
	all_ss = []
	all_fs = []
	all_tos = []

	all_stats = []
    
	player_data = extract_data(data_type, player_name, ext)
	# first row is headers, next are games with monthly averages bt each mth

	#desired_field = 'points'
	#desired_field_idx = determiner.determine_field_idx(desired_field)
	date_idx = 0
	opp_idx = 1
	result_idx = 2
	minutes_idx = 3
	fg_idx = 4
	fg_rate_idx = 5
	three_idx = 6
	three_rate_idx = 7
	ft_idx = 8
	ft_rate_idx = 9
	r_idx = 10
	a_idx = 11
	b_idx = 12
	s_idx = 13
	f_idx = 14
	to_idx = 15
	p_idx = 16

	# isolate games from lebron data
	# exclude headers and monthly averages
	player_games_data = isolator.isolate_player_game_data(player_data, player_name)

	

	if len(player_games_data) > 0:
		for game in player_games_data:
			pts = int(game[p_idx])
			rebs = int(game[r_idx])
			asts = int(game[a_idx])

			results = game[result_idx]
			#print("results: " + results)
			results_data = re.split('\\s+', results)
			#print("results_data: " + str(results_data))
			score_data = results_data[1].split('-')
			#print("score_data: " + str(score_data))
			winning_score = int(score_data[0])
			losing_score = int(score_data[1])

			minutes = int(game[minutes_idx])

			fgs = game[fg_idx]
			fg_data = fgs.split('-')
			fgm = int(fg_data[0])
			fga = int(fg_data[1])
			fg_rate = converter.round_half_up(float(game[fg_rate_idx]), 1)

			threes = game[three_idx]
			threes_data = threes.split('-')
			#print("threes_data: " + str(threes_data))
			threes_made = int(threes_data[0])
			threes_attempts = int(threes_data[1])
			three_rate = converter.round_half_up(float(game[three_rate_idx]), 1)

			fts = game[ft_idx]
			ft_data = fts.split('-')
			ftm = int(ft_data[0])
			fta = int(ft_data[1])
			ft_rate = converter.round_half_up(float(game[ft_rate_idx]), 1)

			bs = int(game[b_idx])
			ss = int(game[s_idx])
			fs = int(game[f_idx])
			tos = int(game[to_idx])

			all_pts.append(pts)
			all_rebs.append(rebs)
			all_asts.append(asts)

			all_winning_scores.append(winning_score)
			all_losing_scores.append(losing_score)

			all_minutes.append(minutes)
			all_fgms.append(fgm)
			all_fgas.append(fga)
			all_fg_rates.append(fg_rate)
			all_threes_made.append(threes_made)
			all_threes_attempts.append(threes_attempts)
			all_three_rates.append(three_rate)
			all_ftms.append(ftm)
			all_ftas.append(fta)
			all_ft_rates.append(ft_rate)
			all_bs.append(bs)
			all_ss.append(ss)
			all_fs.append(fs)
			all_tos.append(tos)

			all_stats = [all_pts,all_rebs,all_asts,all_winning_scores,all_losing_scores,all_minutes,all_fgms,all_fgas,all_fg_rates,all_threes_made,all_threes_attempts,all_three_rates,all_ftms,all_ftas,all_ft_rates,all_bs,all_ss,all_fs,all_tos]

	else:
		print("Warning: No player games data!")

	return all_stats

def read_raw_projected_lines(todays_games_date_obj):

	raw_projected_lines = []

	# need data type and input type to get file name
	data_type = "Player Lines"
	# optional setting game date if processing a day in advance
	todays_games_date_str = '' # format: m/d/y, like 3/14/23. set if we want to look at games in advance
	if todays_games_date_str != '':
		todays_games_date_obj = datetime.strptime(todays_games_date_str, '%m/%d/%y')
		
	# read projected lines or if unavailable get player averages
    # but if no lines given then we generate most likely lines
	input_type = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day)

    # raw projected lines in format: [['Player Name', 'O 10 +100', 'U 10 +100', 'Player Name', 'O 10 +100', 'U 10 +100', Name', 'O 10 +100', 'U 10 +100']]
	raw_projected_lines = extract_data(data_type, input_type, extension='tsv', header=True) # tsv no header
	
	#print("raw_projected_lines: " + str(raw_projected_lines))
	return raw_projected_lines

def read_projected_lines(raw_projected_lines, all_player_teams, player_of_interest='', cur_yr=''):
	#print('\n===Read Projected Lines===\n')
	#print('raw_projected_lines: ' + str(raw_projected_lines))

	# convert raw projected lines to projected lines
	header_row = ['name', 'pts', 'reb', 'ast', '3pm', 'blk', 'stl', 'to','loc','opp']

	all_game_lines_dicts = {} # each stat separately
	# split columns in raw projected lines so we can loop thru each stat separately
	pts_projected_lines = []
	reb_projected_lines = []
	ast_projected_lines = []
	three_projected_lines = []
	blk_projected_lines = []
	stl_projected_lines = []
	to_projected_lines = []

	for line in raw_projected_lines:
		#print('raw line: ' + str(line))
		pts_line = line[:3]
		pts_projected_lines.append(line[:3])
		reb_projected_lines.append(line[3:6])
		ast_projected_lines.append(line[6:9])
		three_projected_lines.append(line[9:12])
		blk_projected_lines.append(line[12:15])
		stl_projected_lines.append(line[15:18])
		to_projected_lines.append(line[18:21])

	separate_projected_lines = { 'pts':pts_projected_lines, 'reb':reb_projected_lines, 'ast':ast_projected_lines, 'three':three_projected_lines, 'blk':blk_projected_lines, 'stl':stl_projected_lines, 'to':to_projected_lines }
	#print('separate_projected_lines: ' + str(separate_projected_lines))
	
	all_player_lines = [header_row]

	#game_lines_dict = {} # { 'PHO SunsatDAL MavericksTODAY 1:10PM': [['Chris Paul', 'O 9.5  +105', 'U 9.5  −135'],..]}

	# raw_projected_lines: [['PHO SunsatDAL MavericksTODAY 1:10PM'], ['PLAYER', 'OVER', 'UNDER'], ['Chris Paul', 'O 9.5  +105', 'U 9.5  −135']]
	# assign player lines to a game so we can get loc and opp from game info key
	for stat_name, projected_lines in separate_projected_lines.items():
		if len(projected_lines[0]) > 0:
			#print('stat_name: ' + stat_name)
			game_key = ''
			game_lines_dict = {} # { 'PHO SunsatDAL MavericksTODAY 1:10PM': [['Chris Paul', 'O 9.5  +105', 'U 9.5  −135'],..]}
		
			for row in projected_lines:
				# loop thru rows until we see header. then make header key in dict and add next rows to list of values until next header
				# if first item = 'PLAYER' skip bc not needed header
				# then if first 3 letters are uppercase we know it is team matchup header w/ needed info
				player_initials = ['og','cj','pj','rj','tj','jt','jd']
				#print('row: ' + str(row))
				if len(row) > 0:
					first_element_wo_punctuation = re.sub('\'|\.','',row[0])
					#print('first_element_wo_punctuation: ' + str(first_element_wo_punctuation))
					if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na':
						if first_element_wo_punctuation[:3].isupper() and first_element_wo_punctuation[:2].lower() not in player_initials:# and not re.search('\'',row[0][:3]): # if apostrophe then player name like D'Angelo, not header
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

			#print("game_lines_dict: " + str(game_lines_dict))
			all_game_lines_dicts[stat_name] = game_lines_dict

	#print("all_game_lines_dicts: " + str(all_game_lines_dicts))

	# for now set unavailable stats=1, until we have basic fcns working
	reb = 1
	ast = 1
	three = 1
	blk = 1
	stl = 1
	to = 1

	all_player_lines_dicts = {} # {'player name':{pts:0,reb:0,..}}

	# game info = 'PHO SunsatDAL MavericksTODAY 1:10PM'
	for stat_name, game_lines_dict in all_game_lines_dicts.items():

		#print('stat_name: ' + stat_name)

		for game_info, game_lines in game_lines_dict.items():
			#print('game_info: ' + str(game_info))
			teams = game_info.split('at') 
			# make exception for MIA Heatat bc heat ends with at
			away_team = teams[0]
			home_team_idx = 1
			if away_team.lower() == 'mia he':
				away_team = 'MIA Heat'
				home_team_idx = 2
			home_team = teams[home_team_idx]
			#print("away_team: " + str(away_team))
			#print("home_team: " + str(home_team))

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

				player_name = raw_player_line[0].lower()
				#print("player_name: " + str(player_name))
				#if player_name in all_player_teams.keys():

				
				# all_players_teams = {player:{year:{team:gp,...},...}}
				if player_name != '':
					if player_name in all_player_teams.keys() and cur_yr in all_player_teams[player_name].keys():
						player_team_abbrev = list(all_player_teams[player_name][cur_yr].keys())[-1]
						#print("player_team_abbrev: " + str(player_team_abbrev))
						# determine opponent from game info by eliminating player's team from list of 2 teams
						loc = 'home'
						opp = away_abbrev
						if player_team_abbrev == away_abbrev:
							loc = 'away'
							opp = home_abbrev
						# only add loc and opp once per player per game
						if not player_name in all_player_lines_dicts.keys():
							all_player_lines_dicts[player_name] = { 'loc': loc, 'opp': opp }
						else:
							all_player_lines_dicts[player_name]['loc'] = loc 
							all_player_lines_dicts[player_name]['opp'] = opp

						

						stat = math.ceil(float(raw_player_line[1].split()[1])) # O 10.5 +100
						#print("pts: " + str(pts))
						#reb = math.ceil(float(raw_player_line[4].split()[1])) # O 10.5 +100

						all_player_lines_dicts[player_name][stat_name] = stat
					else:
						print('Warning: No player name ' + player_name + ' not in teams dict while reading projected lines!')
						print("raw_player_line: " + str(raw_player_line))
				else:
					print('Warning: No player name while reading projected lines!')
					print("raw_player_line: " + str(raw_player_line))


	print("all_player_lines_dicts: " + str(all_player_lines_dicts))

	for player_name, player_lines in all_player_lines_dicts.items():
		#header_row = ['Name', 'PTS', 'REB', 'AST', '3PT', 'BLK', 'STL', 'TO','LOC','OPP']
		pts = 10
		if 'pts' in player_lines.keys():
			pts = player_lines['pts']
		reb = 2
		if 'reb' in player_lines.keys():
			reb = player_lines['reb']
		ast = 2
		if 'ast' in player_lines.keys():
			ast = player_lines['ast']
		three = 1
		if 'three' in player_lines.keys():
			three = player_lines['three']
		blk = 1
		if 'blk' in player_lines.keys():
			blk = player_lines['blk']
		stl = 1
		if 'stl' in player_lines.keys():
			stl = player_lines['stl']
		to = 1
		if 'to' in player_lines.keys():
			to = player_lines['to']
		
		loc = player_lines['loc']
		opp = player_lines['opp']
		player_line = [player_name, pts, reb, ast, three, blk, stl, to, loc, opp]

		# if certain players of interest, keep only their lines for analysis
		if player_of_interest == '': # get all players
			all_player_lines.append(player_line)
		elif player_of_interest == player_name:
			all_player_lines.append(player_line)
		
	print("all_player_lines:\n" + tabulate(all_player_lines))
	return all_player_lines

































def read_player_former_teams(player_name, player_teams):
	# print('\n===Read Player Former Teams: ' + player_name.title() + '===\n')
	# print('Input: player_teams = {year:{team:{gp:gp, min:min},... = {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
	# print('\nOutput: former_teams = [team,...]\n')
		
	former_teams = []

	for year_teams in player_teams.values():
		for team in year_teams.keys():

			if team not in former_teams:
				former_teams.append(team)

	#print('former_teams: ' + str(former_teams))
	return former_teams

# we may be given irregular abbrev or full name
# so change to uniform regular ream abbrev for comparison
def read_team_abbrev(team_str):

	abbrev = re.sub('@|vs','',team_str.lower())
	
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

	if abbrev in irregular_abbrevs.keys():
		abbrev = irregular_abbrevs[abbrev]
	#print('abbrev: ' + abbrev)
	return abbrev


	

# find teammates and opponents for each game played by each player
# all_box_scores = {player:{game:{teammates:[],opponents:[]}}}
# OR
# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
# use init_player_stat_dict to see saved stats
# init_player_stat_dicts = {player: {"2023": {"regular": {"pts": {"all": {"0": 14,...
def read_all_players_in_games(all_players_season_logs, all_players_teams, cur_yr, init_player_stat_dicts={}, read_new_game_ids=True, season_parts=['regular','postseason','full']):#, season_year=2024):
	print('\n===Read All Players in Games===\n')
	#print('read_new_game_ids: ' + str(read_new_game_ids))
	
	
	# currently just players in box scores, 
	# but expand to all stats in box scores
	# filepath = 'data/box scores - ' + cur_yr + '.json'
	# # saved all cur yr box score data so we do not have to read from internet more than once
	# init_cur_yr_game_players_dict = read_json(filepath)
	#print('init_cur_yr_game_players_dict: ' + str(init_cur_yr_game_players_dict))

	cur_box_scores_file = 'data/box scores - ' + cur_yr + '.json'
	prev_box_scores_file = 'data/box scores - prev.json'
	init_box_scores = read_cur_and_prev_json(cur_box_scores_file,prev_box_scores_file)
	#print('init_box_scores: ' + str(init_box_scores))
	#all_box_scores = {} # {player:{game:{teammates:[],opponents:[]}}}
	all_box_scores = copy.deepcopy(init_box_scores) # change to all_box_scores

	#season_year = 2023

	# game id in url
	# see if game id saved in file
	# check for each player bc we add new games for each player and they may overlap
	# {game key: game id,...}
	data_type = 'data/all games ids.csv' #'game ids'
	existing_game_ids_dict = extract_dict_from_data(data_type)
	#print('existing_game_ids_dict: ' + str(existing_game_ids_dict))

	# read all existing box scores here or only for current players of interest?
	# 'all' would mean all box scores of interest, which for now only concerns players of interest (later could import all for comparison)
	# existing_box_scores_dict = {'game key':{away:[],home:[]},...}
	existing_box_scores_dict = {}
	# 1230 games per yr so better to keep in file than 1000 files
	# OR could have player box scores saved after processing raw box score, so 1 file per player
	

	for player_name, player_season_logs in all_players_season_logs.items():
		#print('\n===Read Players in Games for: ' + player_name.title() + '===\n')
		#print('player_season_logs: ' + str(player_season_logs))

		# init_player_stat_dict = {"2023": {"regular": {"pts": {"all": {"0": 14,...
		init_player_stat_dict = init_player_stat_dicts[player_name]
		#print('init_player_stat_dict: ' + str(init_player_stat_dict))

		# BEFORE saving box scores for prev seasons consider saving relevant probs instead
		# we also need to know the number of samples, not just the computed prob
		# sample size comes from player stat dict so we could save prev season stat dicts locally
		# player_box_scores_filename = 'data/box scores/' + player_name + ' box scores.json'
		# print('player_box_scores_filename: ' + player_box_scores_filename)
		# print('Try to find local box score for ' + game_key + '.')
		# box_score = read_json(player_box_scores_filename)
		# print('box_score: ' + str(box_score))

		#init_player_stat_dict = read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename)

		#year_idx = 0 # 1st yr is cur yr which we treat different than prev yrs bc it changes with each new game
		for season_year, player_season_log in player_season_logs.items():
			#print('season_year: ' + season_year)

			# if season_year not in all_box_scores.keys():
			# 	all_box_scores[season_year] = {}

			# separate by year bc we want to get all teammates in a given yr, not all yrs
			# bc if measure when teammate out for all yrs then they will be out most games and have different effect
			# it would show stats for when teammate is out for a given yr but the teammate was never in so it is equal to all stats
			if season_year not in all_box_scores.keys():
				all_box_scores[season_year] = {}
			# if prev season yr already saved then no need to get box scores
			# bc only used to make stat dict
			# if cur season yr then read saved local box scores and new box scores from internet
			# always run for cur yr but only run for unsaved prev yr
			# bc we need to update cur yr each game
			# REMEMBER: we could save stat dict with find players turned off 
			# so it would have season yr but not team players condition
			# seeing that any team players condition has been saved shows us that we ran with find players turned on
			# bc we only add those conditions if we know team players
			# team_players_conditions = ['start']
			# team_players_condition not in init_player_stat_dict[season_year].keys()
			
			for season_part in season_parts:

				# first determine if we even need the box score or if we already computed the results for this game
				# for cur season, if we already ran today, dont need to run again
				# for prev season, if we ever ran, dont need to run again
				# if we do not have game id, then we definitely need box score
				# but then we have to wait to decide need box score per game
				# also the box score will change the stat dict so we need a way to update the stat dict
				# if we want to force new box scores bc we updated player names or something
				# then must delete old stat dicts files
				# change from using stat dict to keeping all box scores so we can update features without needing to update box scores
				if determiner.determine_need_box_score(season_year, cur_yr, season_part, init_player_stat_dict):
					
					# read box scores

					# for each reg season game
					player_season_log_df = pd.DataFrame(player_season_log)
					season_part_game_log = determiner.determine_season_part_games(player_season_log_df, season_part)
					

					num_playoff_games = 0 # reg season idx
					if season_part == 'regular':
						if len(season_part_game_log.index) > 0:
							num_playoff_games = int(season_part_game_log.index[0]) # num playoff games not counting playin bc playn listed after 
					else: # full
						regseason_game_log = determiner.determine_season_part_games(player_season_log_df)
						if len(regseason_game_log.index) > 0:
							num_playoff_games = int(regseason_game_log.index[0])
					#print('num_playoff_games: ' + str(num_playoff_games))


					#players_in_game = [] # unordered list of all players in game independent of team
					#players_in_game_dict = {} # {teammates:[],opponents:[]}
					# determine player team for game at idx
					player_team_idx = 0
					# player_teams = {player:{year:{team:gp,...},...}}
					team_gp_dict = {}
					if season_year in all_players_teams[player_name].keys():
						team_gp_dict = all_players_teams[player_name][season_year]
					# reverse team gp dict so same order as game idx recent to distant
					teams = list(reversed(team_gp_dict.keys()))
					games_played = list(reversed(team_gp_dict.values()))
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


					season_games_played_data = determiner.determine_teams_reg_and_playoff_games_played(player_teams, player_season_log, season_part, season_year, cur_yr, gp_cur_team, player)
					teams_reg_and_playoff_games_played = season_games_played_data[0]
					season_part_game_log = season_games_played_data[1]
					teams = season_games_played_data[2]
					games_played = season_games_played_data[3]

					try:

						# for reg season, idx starts after first playoff game
						for game_idx, row in season_part_game_log.iterrows():
							
							#print('\n===Game ' + str(game_idx) + '===')
							#print('row:\n' + str(row))
							# season year-1 for first half of season oct-dec bc we say season year is end of season
							
							# we cannot tell team until we know the specific game in the specific season bc player may change teams midseason
							
							# season_games_played = team_games_played[0]
							# for team_idx in range(len(teams)):
							# 	team = teams[team_idx]
							# 	team_games_played = games_played[team_idx]

							# 	if game_idx > int(season_games_played):
							# 		season_games_played += team_games_played

							# final_team_abbrev = ''
							# #first_game_new_team_idx = 
							# total_gp = sum(list(team_abbrevs.values()))
							# for team_abbrev, gp in team_abbrevs.items():
							# 	if game_idx < total_gp - int(gp):
							# 		final_team_abbrev = team_abbrev
							# 		break

							# if int(game_idx) >= teams_games_played:
							# 	player_team_idx += 1
							# 	teams_games_played += games_played[player_team_idx]

							# team_abbrev = teams[player_team_idx]
							

							# determine player team for game
							player_team_idx = determiner.determine_player_team_idx(player_name, player_team_idx, game_idx, row, games_played, teams_reg_and_playoff_games_played)
							team_abbrev = ''
							if len(teams) > player_team_idx:
								team_abbrev = teams[player_team_idx]
							#print('team_abbrev: ' + team_abbrev)

							game_key = read_game_key(season_year, team_abbrev, row)
					
							# if we have not yet added this game to the dict
							# then get game box score players
							if not game_key in all_box_scores[season_year].keys():
							
								game_espn_id = read_game_espn_id(game_key, existing_game_ids_dict, read_new_game_ids)
								# if returned no game id, then bc too many requests, so stop reading new ids
								# no bc could be any reason, so check error
								# if too many requests error, stop reading new ids
								if game_espn_id == 'HTTP Error 429: Too Many Requests':
								#if re.search('too many requests', game_espn_id.lower()): 
									read_new_game_ids = False
									continue

								

								players_in_box_score_dict = {}
								# add year idx to save time bc if not 0 then no need to check game key which is long dict search
								# box scores immutable so all yrs saved
								# init_box_scores = {yr:game:box score}
								if season_year in init_box_scores.keys() and game_key in init_box_scores[season_year].keys():
									players_in_box_score_dict = init_box_scores[season_year][game_key]
								else: # read from internet, only runs if not saved before
									# get the game box score page using the game id
									# get the box score from the page in a df
									# game_box_scores_dict = {away:df, home:df}
									# currently returns empty dict if results already saved
									game_box_scores_dict = read_game_box_scores(game_key, game_espn_id, read_new_game_ids=read_new_game_ids, player_name=player_name)
									
									# now that we have box scores we can isolate stats of interest, starting with player name
									# given box scores for each team, return lists of teammates and opponents or home/away?
									# need to save as home away so we only need to read once per game and not once per player
									# for each player knowing their team we can tell which is opponents
									# players_in_box_score_dict = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
									players_in_box_score_dict = read_players_in_box_score(game_box_scores_dict)
								
									# may need to save player box scores if internet connection fails during read all box scores
								
								all_box_scores[season_year][game_key] = players_in_box_score_dict
						
							#break # test
					except Exception as e:
						print('Exception while reading all players in games: ', e)

					# save cur yr box scores
					# if read new box scores from internet
					# may need to append to file each game if internet connection fails
					# so when we rerun it resumes where it left off
					# need all players in games for all seasons to get player abbrevs
					# so should we save abbrevs or just all seasons games? abbrevs in compressed result
					# no need to write only cur yr 
					# bc we often update stat dict but box scores never need to be updated bc they dont change so save them
					# if season_year == cur_yr and not init_cur_yr_game_players_dict == all_box_scores:
					# 	writer.write_json_to_file(all_box_scores, filepath, 'w')

						# also or instead save all box score data 
						# so when we add features we dont have to read box scores from internet again


					# test first game
					#break
				#break # test

			#break # test
			#season_year -= 1
			#year_idx += 1
						
	if not init_box_scores == all_box_scores:
		writer.write_cur_and_prev(init_box_scores, all_box_scores, cur_box_scores_file, prev_box_scores_file, cur_yr)
		
	# all_box_scores = {game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
	print('all_box_scores: ' + str(all_box_scores))
	return all_box_scores

# we know abbrev from name and team bc abbrev given in box scores
def read_player_abbrev(player, all_players_teams, season_year, all_box_scores, cur_yr='', rosters={}):
	print('\n===Read Player Abbrev: ' + player.title() + '===\n')

	player_abbrev = ''

	year_players_in_games_dict = all_box_scores[season_year]

	found_player = False

	for game_key, game_players in year_players_in_games_dict.items():
		# print('game_key: ' + str(game_key))
		# print('game_players: ' + str(game_players))

		game_data = game_key.split()
		if len(game_data) > 2:
			away_team = game_data[0]
			#print('away_team: ' + str(away_team))
			home_team = game_data[1]
			#print('home_team: ' + str(home_team))

		for loc, game_team_players in game_players.items():
			#print('loc: ' + str(loc))
			team = home_team
			if loc == 'away':
				team = away_team
			#print('game_team_players: ' + str(game_team_players))
			for team_part in game_team_players.values():
				#print('team_part: ' + str(team_part))
				for abbrev in team_part:
					#print('abbrev: ' + str(abbrev))

					player_name = determiner.determine_player_full_name(abbrev, team, all_players_teams, rosters, game_key, cur_yr)

					if player_name == player:
						player_abbrev = abbrev
						found_player = True
						break

				if found_player:
					break

			if found_player:
				break

		if found_player:
			break

	#print('player_abbrev: ' + str(player_abbrev))
	return player_abbrev








# read teammates using box score data in all players in games dict
# which gives away home teams players
def read_teammates_from_games(player_name, player_season_logs, all_box_scores):
	#print('\n===Read Teammates from Games for ' + player_name.title() + '===\n')

	all_teammates = {}#[]

	# go thru game logs instead of all players in games bc more efficient
	# we need all players in games to tell teammates
	if len(all_box_scores.keys()) > 0:
		for year, player_season_log in player_season_logs.items():
			# print('\n===Year: ' + str(year) + '===\n')
			# print('player_season_log: ' + str(player_season_log))

			# if yr is in all teammates 
			
			year_teammates = []
			year_players_in_games = {}
			if year in all_box_scores.keys():
				year_players_in_games = all_box_scores[year]

			# use date and opp team in game log to get game players
			# num games = len(field vals) so take first field
			# idx_dict: {'0': 'james harden', ...
			idx_dict = list(player_season_log.values())[0]
			for game_idx in range(len(idx_dict.keys())):
				game_idx_str = str(game_idx)
				#print('\n===Game: ' + game_idx_str + '===\n')

				if 'Date' in player_season_log.keys():

					game_date = player_season_log['Date'][game_idx_str]
					#print('game_date: ' + str(game_date)) # wed 11/18
					game_opp = player_season_log['OPP'][game_idx_str].lower()
					#print('game_opp: ' + str(game_opp))  # vsind

					# find matching game in list of all players in games
					# still unique bc team only plays once per day
					# need to iso date and team separately bc string not always in order of team date bc they maybe home/away
					# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
					# game_players = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}
					# game_teammates_dict = {starters:[],bench:[]}
					player_team = ''
					game_teammates_dict = {}
					for game_key, game_players in year_players_in_games.items():
						#print('game_key: ' + str(game_key))

						# first look for matching date
						game_key_date = re.sub('/\d+$','',game_key.split()[2]) # 11/11/2024 -> 11/11
						#print('game_key_date: ' + str(game_key_date))
						# game_key_date = 11/18
						# game_date = wed 11/18
						if re.search(game_key_date, game_date):
							# look for matching team
							# game_key_teams = re.sub('\s\d+.+$','',) #'away home 11/11/2024'
							# print('game_key_teams: ' + str(game_key_teams))

							# game_opp = vsind
							game_data = game_key.split() # away,home,date

							if len(game_data) > 2:
								away_team = game_data[0]
								home_team = game_data[1]

								# find game
								if re.search(away_team, game_opp):
									player_team = home_team
									game_teammates_dict = game_players['home']
									break
								elif re.search(home_team, game_opp):
									player_team = away_team
									game_teammates_dict = game_players['away']
									break

					if player_team != '':
						# print('player_team: ' + str(player_team))
						# print('game_teammates_dict: ' + str(game_teammates_dict))

						# loop thru games to see if we encounter new teammates
						# game_teammates_dict = {starters:[],bench:[]}
						for teammates in game_teammates_dict.values():
							for teammate in teammates:
								if teammate not in year_teammates:
									year_teammates.append(teammate) # prefer not to lower bc comes with position already uppercase like J Brown SG


			all_teammates[year] = year_teammates

	else:
		print('Warning: all_box_scores is empty! ' + str(all_box_scores))

	# all_teammates: {'2024': ['A. Davis PF', ...
	#print('all_teammates: ' + str(all_teammates))
	return all_teammates

# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
# use player team to get teammates from box score
# this is plain list of all teammates ever played with each season
# so we can see how player played with each teammate
# all_teammates = []
# all_teammates = {yr:[teammate,...],...}
# all_teammates = {yr:{team:{[teammate,...],...},...}
# player_teams = {player:{year:{team:gp,...},...}}
# need to get date of first game on new team bc we want all games between that and first game on next team
# this fcn requires we know the player team for each game
# so can we add player team as new column in game log?
# and then pass game log here so we can use date to get team
# instead of needing both date and games played?
# if you pass the game log here 
# then you know the players team is the team in the game key but not in the game log entry for this date!
# player_game_logs = {year:{field:...}}
# all_teammates: {'2024': ['A. Davis PF', ...
def read_all_teammates(player_name, all_box_scores, player_teams={}, player_game_logs={}, todays_date=datetime.today().strftime('%m-%d-%y'), current_year_str=''):
	#print('\n===Read All Teammates for ' + player_name.title() + '===\n')

	all_teammates = {}#[]

	# much more likely to play with a new teammate off the bench than a trade
	# so update teammates after each game
	# always current yr bc no matter what yr of interest only current yr changes with each new game
	# if current_year_str == '':
	# 	current_year_str = determiner.determine_current_season_year() #str(datetime.today().year)
	# all_cur_teammates_filename = 'data/all ' + current_year_str + ' teammates ' + todays_date + '.json'
	# all_prev_teammates_filename = 'data/all prev teammates.json'
	# init_all_teammates = read_cur_and_prev_json(all_cur_teammates_filename,all_prev_teammates_filename)
	# #print('init_all_teammates: ' + str(init_all_teammates))
	# all_teammates = copy.deepcopy(init_all_teammates) # all teammates for all players

	# go thru game logs instead of all players in games bc more efficient
	# we need all players in games to tell teammates
	if len(all_box_scores.keys()) > 0:
		for year, player_season_log in player_game_logs.items():
			# print('\n===Year: ' + str(year) + '===\n')
			# print('player_season_log: ' + str(player_season_log))

			# if yr is in all teammates 
			
			year_teammates = []
			year_players_in_games = {}
			if year in all_box_scores.keys():
				year_players_in_games = all_box_scores[year]

			# values_dict = player_season_log['Date']
			# values_dict: {'0': 'james harden', ...
			# player_season_log = {field:{game idx:val,...},...}
			# for field, values_dict in player_season_log.items():

			# 	print('\n===Field: ' + str(field) + '===\n')
			# 	# values_dict: {'0': 'james harden', ...
			# 	print('values_dict: ' + str(values_dict))

			# use date and opp team in game log to get game players
			# num games = len(field vals) so take first field
			# idx_dict: {'0': 'james harden', ...
			idx_dict = list(player_season_log.values())[0]
			for game_idx in range(len(idx_dict.keys())):
				game_idx_str = str(game_idx)
				#print('\n===Game: ' + game_idx_str + '===\n')

				if 'Date' in player_season_log.keys():

					game_date = player_season_log['Date'][game_idx_str]
					#print('game_date: ' + str(game_date)) # wed 11/18
					# add year to game log date, if not separate by year
					# game_mth = game_date.split('/')[0]
					# game_yr = determiner.determine_game_year(game_mth, year)
					# game_date += '/' + game_yr
					# print('game_date: ' + str(game_date)) # 11/11/2024

					game_opp = player_season_log['OPP'][game_idx_str].lower()
					#print('game_opp: ' + str(game_opp))  # vsind

					# find matching game in list of all players in games
					# still unique bc team only plays once per day
					# need to iso date and team separately bc string not always in order of team date bc they maybe home/away
					# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
					# game_players = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}
					# game_teammates_dict = {starters:[],bench:[]}
					player_team = ''
					game_teammates_dict = {}
					game_teammates = []
					for game_key, game_players in year_players_in_games.items():
						#print('game_key: ' + str(game_key))

						# first look for matching date
						game_key_date = re.sub('/\d+$','',game_key.split()[2]) # 11/11/2024 -> 11/11
						#print('game_key_date: ' + str(game_key_date))
						# game_key_date = 11/18
						# game_date = wed 11/18
						if re.search(game_key_date, game_date):
							# look for matching team
							# game_key_teams = re.sub('\s\d+.+$','',) #'away home 11/11/2024'
							# print('game_key_teams: ' + str(game_key_teams))

							# game_opp = vsind
							game_data = game_key.split() # away,home,date

							if len(game_data) > 2:
								away_team = game_data[0]
								home_team = game_data[1]

								# find game
								if re.search(away_team, game_opp):
									player_team = home_team
									game_teammates_dict = game_players['home']
									break
								elif re.search(home_team, game_opp):
									player_team = away_team
									game_teammates_dict = game_players['away']
									break

					if player_team != '':
						# print('player_team: ' + str(player_team))
						# print('game_teammates_dict: ' + str(game_teammates_dict))

						# loop thru games to see if we encounter new teammates
						# game_teammates_dict = {starters:[],bench:[]}
						for teammates in game_teammates_dict.values():
							for teammate in teammates:
								if teammate not in year_teammates:
									year_teammates.append(teammate) # prefer not to lower bc comes with position already uppercase like J Brown SG


			all_teammates[year] = year_teammates

	
	else:
		print('Warning: all_box_scores is empty! ' + str(all_box_scores))

	# all_teammates: {'2024': ['A. Davis PF', ...
	#print('all_teammates: ' + str(all_teammates))
	return all_teammates

def read_react_web_data(url):
	# print('\n===Read React Web Data===\n')
	# print('url: ' + url)

	web_data = [] # web_data = [dataframe1,...]

	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.implicitly_wait(3)

	driver.get(url) # Open the URL on a google chrome window

	# check if no tables found	
	html_result = pd.read_html(driver.find_element('id','dom_SameGameParlayWeb').get_attribute('outerHTML'))[0]
	#print('dom_SameGameParlayWeb:\n' + str(html_result))
	
	web_data.append(html_result)

	#print('web_data:\n' + str(web_data))
	return web_data

# finding element by class name will return 1st instance of class
# but unusual error may occur
# .ElementClickInterceptedException: Message: element click intercepted: Element <button role="tab" class="rj-market__group" aria-selected="false" data-testid="button-market-group">...</button> is not clickable at point (763, 135). Other element would receive the click: 
# return {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
def read_react_website(url, timeout=10, max_retries=3):
	# print('\n===Read React Website===\n')
	# print('url: ' + url)

	#web_data = [] # web_data = [dataframe1,...] or [dict1,...] or {}
	web_dict = {}

	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.implicitly_wait(3)

	driver.get(url) # Open the URL on a google chrome window

	retries = 0

	# check if no tables found
	while retries < max_retries:
		try:
			#sgp_element = driver.find_element('id','dom_SameGameParlayWeb').get_attribute('outerHTML')	
			#soup = BeautifulSoup(page, features='lxml')
		
			# instead of needing keys input just click each btn until find stat of interest
			pts_key = 5 # sometimes 4 if missing quick hits section
			stat_key = pts_key
			stats_of_interest = {'pts':0,'reb':3,'ast':4} #keys relative to pts key. data_table_keys={'pts':pts_key,'reb':pts_key+3,'ast':pts_key+4}
			#web_dict[key] = read_lazy_elements(key)
			#for key in data_table_keys:#.keys():
			for stat_name, relative_key in stats_of_interest.items():
				print("stat_name: " + stat_name)
				web_dict[stat_name] = {}

				# click pts btn
				epath = 'button[' + str(stat_key+relative_key) + ']'

				if stat_name == 'reb':
					# first need to click right arrow to move so ast btn visible
					side_btn = driver.find_element('class name','side-arrow--right')
					#print("side_btn: " + side_btn.get_attribute('innerHTML'))
					try:
						while True:
							side_btn.click()
					except:
						#web_dict['ast'] = {}
						# click ast btn
						stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
						#print("stat_btn: " + stat_btn.get_attribute('innerHTML'))
						stat_btn.click()

				else:
					stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
					stat_btn_text = stat_btn.get_attribute('innerHTML')
					#print("stat_btn: " + stat_btn_text)
					# if title is 'threes', then subtract 1 from key and try again bc it means the list is missing a tab
					if stat_btn_text == 'Threes': # gone too far
						stat_key -= 1
						epath = 'button[' + str(stat_key) + ']'
						stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
						stat_btn_text = stat_btn.get_attribute('innerHTML')
						#print("stat_btn: " + stat_btn_text)
					stat_btn.click()

				# not all dropdowns are open so program must click each one
				# click player dropdown btn
				# could use find elements to get number of lazy renders and then loop thru that number
				# lazy_element = driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render')
				# print("lazy_element: " + lazy_element.get_attribute('innerHTML'))

				# collapsible_element = lazy_element.find_element('class name','rj-market-collapsible') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[1]').find_element('class name','rj-market')
				# print("collapsible_element: " + collapsible_element.get_attribute('innerHTML'))

				# player_btn = collapsible_element.find_element('xpath','button') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[2]/button')
				# print("player_btn: " + player_btn.get_attribute('innerHTML'))
				# player_btn.click()

				
				#print('get all lazy elements and loop thru')
				lazy_elements = driver.find_element('class name','rj-markerboard-markets').find_elements('xpath','sb-lazy-render')
				for e in lazy_elements:
					#print("lazy_element: " + e.get_attribute('innerHTML'))

					#collapsible_element = e.find_element('class name','rj-market-collapsible') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[1]').find_element('class name','rj-market')
					#print("collapsible_element: " + collapsible_element.get_attribute('innerHTML'))

					# multiple (3 always?) players in each lazy element
					player_btns = e.find_elements('class name','rj-market-collapsible__trigger')
					# print('player_btns: ')
					# for player_btn in player_btns:
					# 	print("player_btn: " + player_btn.get_attribute('innerHTML'))

					for player_btn in player_btns:
						#player_btn = collapsible_element.find_element('xpath','button') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[2]/button')
						#print("player_btn: " + player_btn.get_attribute('innerHTML'))

						# need to know which type of market it is bc there are 2: O/U and over only (OO)
						# button header: 'Player Name Stat Name', eg 'Bam Adebayo Assists', excluding 'O/U'
						player_btn_header = player_btn.find_element('xpath','h2').get_attribute('innerHTML')
						#print('player_btn_header: ' + player_btn_header)

						# ignore quarter stats for now
						if re.search('Quarter',player_btn_header):
							break # can break bc list ends with quarter stats

						# old version: as long as we can click all markets we need to open then we dont need to click o/u btns but we may we need to close o/u btns to see the oo btns
						# new version we need to click all btns
						player_btn_arrow = player_btn.find_element('class name','rj-market-collapsible-arrow').get_attribute('innerHTML')
						#print('player_btn_arrow: ' + player_btn_arrow)
						# old version: if o/u and open then close dropdown permanently
						# new version: get odds from all sections so get data 
						# and then close if already open, or open and then close
						# if re.search('O/U',player_btn_header) and re.search('up',player_btn_arrow):
						# 	player_btn.click() # close dropdown
						# 	print('closed unused market')
						# 	time.sleep(0.1)
						# elif not re.search('O/U',player_btn_header):
						# first section already open so arrow up and no need to open but close after reading data
						# arrow down means section closed
						try: # button might be out of window bottom bc long list and we cannot scroll
							if re.search('down',player_btn_arrow):
								player_btn.click() # open dropdown

								#print('clicked player btn')

							# opened data so now collect it and then close it so other data visible

							player_element = player_btn.find_element('xpath','..') 
							#print("player_element: " + player_element.get_attribute('innerHTML'))

							player_name = re.sub('\sAlt\s|Points|Rebounds|Assists|O/U','',player_btn_header).strip().lower()
							player_name = re.sub('−|-',' ',player_name)
							player_name = re.sub('\.','',player_name)
							#print('player_name: ' + player_name)

							if player_name not in web_dict[stat_name].keys():
								web_dict[stat_name][player_name] = {}

							stat_val_elements = player_element.find_elements('class name','rj-market__button-yourbet-title')
							odds_val_elements = player_element.find_elements('class name','rj-market__button-yourbet-odds')

							# stat_vals = []
							# odds_vals = []
							for idx in range(len(stat_val_elements)):
								stat_element = stat_val_elements[idx]
								#print("stat_element: " + stat_element.get_attribute('innerHTML'))
								odds_element = odds_val_elements[idx]
								#print("odds_element: " + odds_element.get_attribute('innerHTML'))

								stat = stat_element.get_attribute('innerHTML')
								odds = odds_element.get_attribute('innerHTML')

								# if header is just <stat> without 'alt' and 'o/u'
								# then format is 'Over 24.5 -120'
								# Over <stat> <odds>
								if not re.search('\sAlt\s',player_btn_header):
									# old: stat = re.sub('\+','',stat)
									if re.search('Over',stat):
										stat = re.sub('[a-zA-Z]','',stat).strip()
										stat = str(converter.round_half_up(float(stat) + 0.5)) + '+' #or str(int(stat))#str(converter.round_half_up(float(stat) + 0.5)) # 0.5 to 1
									else: #under
										stat = re.sub('[a-zA-Z]','',stat).strip()
										stat = str(converter.round_half_up(float(stat) - 0.5)) + '-'
								elif re.search('O/U',player_btn_header):
									# start with over and then take every other value as over
									if idx % 2 == 0:
										stat = str(converter.round_half_up(float(stat) + 0.5)) + '+' #or str(int(stat))#str(converter.round_half_up(float(stat) + 0.5)) # 0.5 to 1
									else: #under
										stat = str(converter.round_half_up(float(stat) - 0.5)) + '-'

								odds = re.sub('−','-',odds) # change abnormal '-' char
								#odds = re.sub('\+','',odds) # prefer symbol to differentiate odds from probs, prefer no + symbol for +odds bc implied so not to confuse with val over under

								#stat_vals.append(e.get_attribute('innerHTML'))

								#print('stat: ' + str(stat))
								#print('odds: ' + str(odds))
								#print('player web dict ' + player_name + ': ' + str(web_dict[key][player_name]))
								web_dict[stat_name][player_name][stat] = odds # { stat : odds, ... }
								#print('player web dict ' + player_name + ': ' + str(web_dict[key][player_name]))
							# for e in odds_val_elements:
							# 	odds_vals.append(e.get_attribute('innerHTML'))

							# print('stat_vals: ' + str(stat_vals))
							# print('odds_vals: ' + str(odds_vals))

							#print('collected player data')
							time.sleep(0.2)
							player_btn.click() # close dropdown
						except:
							print('Warning: player btn unclickable!')

					#time.sleep(5)

			print("Request successful.")
			# {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
			#print('final web_dict:\n' + str(web_dict))
			return web_dict

		except Exception as e:
			print('Warning: No SGP element! ', e)
			retries += 1
			print(f"Exception error occurred. Retrying {retries}/{max_retries}...", e)#, e.getheaders(), e.gettext(), e.getcode())
			time.sleep(10)

	
	# {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
	#print('final web_dict:\n' + str(web_dict))
	print("Maximum retries reached.")
	return None

#all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18+': '−650',...
def read_all_players_odds(game_teams, player_teams={}, players=[], cur_yr=''):
	print('\n===Read All Players Odds===\n')
	#print('game_teams: ' + str(game_teams))
	#print('player_teams: ' + str(player_teams))
	all_players_odds = {}
	odds = '?' # if we dont see name then they might be added later so determine if it is worth waiting

	# use pd df
	# like for reading roster and box score and game log
	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	#all_players_odds = [] # all players in game
	#player_stat_odds = [] # from +2 to +n depending on stat

	# should loop thru games instead of teams bc 2 teams on same page
	# see which teams are playing together and group them
	#game_teams = read_opponent()
	for game in game_teams:
		print('game: ' + str(game))

		game_team = game[0] # only read 1 page bc bth teams same page
		#print('game_team: ' + str(game_team))

		all_players_odds[game_team] = {} # loops for both teams in game?

		team_name = re.sub(' ','-', determiner.determine_team_name(game_team))
		#print("team_name: " + str(team_name))

		# https://sportsbook.draftkings.com/teams/basketball/nba/memphis-grizzlies--odds?sgpmode=true
		game_odds_url = 'https://sportsbook.draftkings.com/teams/basketball/nba/' + team_name + '--odds?sgpmode=true'
		#print('game_odds_url: ' + game_odds_url)

		# return dictionary results for a url
		# {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
		game_players_odds_dict = read_react_website(game_odds_url)

		if game_players_odds_dict is not None:
			#print('game_players_odds_dict:\n' + str(game_players_odds_dict))

			for stat_name, stat_odds_dict in game_players_odds_dict.items():
				#print('stat_name: ' + str(stat_name))
				for player, player_odds_dict in stat_odds_dict.items():
					#print('player: ' + str(player))
					player_team = ''
					if player in player_teams.keys():
						player_team = list(player_teams[player][cur_yr].keys())[-1]
					else:
						print('Warning: player not in teams list! ' + player)
					#print('player_team: ' + str(player_team))
					if player_team not in all_players_odds.keys():
						all_players_odds[player_team] = {}

					if stat_name not in all_players_odds[player_team].keys():
						all_players_odds[player_team][stat_name] = {}

					all_players_odds[player_team][stat_name][player] = player_odds_dict

			

			# if team odds saved locally then no need to read again from internet same day bc unchanged
			#team = stat_dict['team']
			# stat_name = stat_dict['stat name']
			# player = stat_dict['player name']
			# if team not in all_players_odds.keys():
			# 	all_players_odds[team] = {}
			# if stat_name not in all_players_odds[team].keys():
			# 	all_players_odds[team][stat_name] = {}
			# all_players_odds[team][stat_name][player] = odds
			# print('all_players_odds: ' + str(all_players_odds))

			print('Success')
		else:
			print('Warning: website has no soup!')

	#writer.write_json_to_file(all_players_odds, filepath, write_param)

	#all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18+': '−650','17-': 'x',...
	#print('all_players_odds: ' + str(all_players_odds))
	return all_players_odds

# stat_dict: {'player name': 'Trevelin Queen', 'stat name': 'ast', 'prob val': 0, 'prob': 100
# all_players_odds = {team:{stat:{player:odds...}
def read_stat_odds(stat_dict, all_players_odds={}):
	#print('\n===Read Stat Odds===\n')
	odds = '?' # if we dont see name then they might be added later so determine if it is worth waiting

	# use pd df
	# like for reading roster and box score and game log
	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	all_players_odds = [] # all players in game
	player_stat_odds = [] # from +2 to +n depending on stat

	team_name = re.sub(' ','-', determiner.determine_team_name(stat_dict['team']))
	#print("team_name: " + str(team_name))

	# https://sportsbook.draftkings.com/teams/basketball/nba/memphis-grizzlies--odds?sgpmode=true
	game_odds_url = 'https://sportsbook.draftkings.com/teams/basketball/nba/' + team_name + '--odds?sgpmode=true'
	#print('game_odds_url: ' + game_odds_url)

	web_data = read_react_web_data(game_odds_url)

	if web_data is not None:
		print('web_data:\n' + str(web_data))


		print('Success')
	else:
		print('Warning: website has no soup!')

	print('odds: ' + odds)
	return odds

def read_player_stat_dict(player_name, current_year_str='', todays_date=datetime.today().strftime('%m-%d-%y')):
	#print('\n===Read Player Stat Dict: ' + player_name.title() + '===\n')

	if current_year_str == '':
		current_year_str = determiner.determine_current_season_year()

	player_cur_stat_dict_filename = 'data/stat dicts/' + player_name + ' ' + current_year_str + ' stat dict ' + todays_date + '.json'
	player_prev_stat_dicts_filename = 'data/stat dicts/' + player_name + ' prev stat dicts.json'
	init_player_stat_dict = read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename)

	#print('init_player_stat_dict: ' + str(init_player_stat_dict))
	return init_player_stat_dict

# init_player_stat_dicts = {player: {"2023": {"regular": {"pts": {"all": {"0": 14,...
def read_all_players_stat_dicts(players_names, current_year_str, todays_date):
	print('\n===Read All Players Stat Dicts===\n')

	init_player_stat_dicts = {}
	for player_name in players_names:
		player_cur_stat_dict_filename = 'data/stat dicts/' + player_name + ' ' + current_year_str + ' stat dict ' + todays_date + '.json'
		player_prev_stat_dicts_filename = 'data/stat dicts/' + player_name + ' prev stat dicts.json'
		init_player_stat_dicts[player_name] = read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename)

	#print('init_player_stat_dicts: ' + str(init_player_stat_dicts))
	return init_player_stat_dicts

# use when we want all players 
# AND team does not matter
# rosters = {team:[players],...}
def read_players_from_rosters(rosters, game_teams=[]):
	players = []

	teams = []
	for game in game_teams:
		for team in game:
			teams.append(team)

	for team, roster in rosters.items():
		if len(game_teams) == 0: # add all players from all rosters
			for player in roster:
				players.append(player)
		elif team in teams:
			for player in roster:
				players.append(player)

	return players



























# read lineups from internet
# https://www.rotowire.com/basketball/nba-lineups.php
# given starters from internet rotowire
# AND rosters from internet epsn earlier 
# get all_lineups = {team:{starters:[],bench:[],out:[],probable:[],question:[],doubt:[]},...}
# all lineups has random combo of full names and abbrevs so check both
# all_lineups = {team:{starters:[Klay Thompson, D. Green,...],out:[],bench:[],unknown:[]},...}
# all_teams_players = {year:{team:[players],...},...}
def read_all_lineups(players, all_players_teams, rosters, all_teams_players, ofs_players, cur_yr):
	print('\n===Read All Lineups===\n')
	print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30.1}, ...')
	print('\nOutput: all_lineups = {\'cle\': {\'starters\': [\'donovan mitchell\', ...\n')
	#print('all_teams_players: ' + str(all_teams_players))

	# could add 'stars' as condition as well as level above starters
	all_lineups = {}#{'den':{'starters':['jamal murray', 'nikola jokic', 'aaron gordon', 'michael porter jr', 'kentavious caldwell pope'],'bench':[],'out':[],'probable':[],'question':[],'doubt':[]}, 'mia':{'starters':['tyler herro', 'jimmy butler', 'bam adebayo', 'caleb martin', 'kyle lowry'],'bench':[],'out':[],'probable':[],'question':[],'doubt':[]}}

	# read all lineups from source website
	# do we need to save local? yes and make setting to force new lineups
	url = 'https://www.rotowire.com/basketball/nba-lineups.php'
	soup = read_website(url)

	#init_lineups = []

	starters_key = 'starters'
	bench_key = 'bench'
	out_key = 'out'
	probable_key = 'probable'
	question_key = 'question'
	doubt_key = 'doubt'
	#in_key = 'in'
	dnp_key = 'dnp'

	if soup is not None:
		#print('soup: ' + str(soup))

		for lineup in soup.find_all('div', {'class': 'lineup'}):
			#print('lineup: ' + str(lineup))

			lineup_classes = lineup['class']
			#print('lineup_classes: ' + str(lineup_classes))

			# if tools section, reached end
			# lineup: <div class="lineup is-nba is-tools">
			if 'is-tools' in lineup_classes:
				break

			lineup_teams = []
			for lineup_team in lineup.find_all('div', {'class': 'lineup__abbr'}):
				#print('lineup_team: ' + str(lineup_team))
				team_abbrev = converter.convert_irregular_team_abbrev(lineup_team.decode_contents())#str(list(lineup_team.descendants)[0])
				#print('team_abbrev: ' + str(team_abbrev))
				lineup_teams.append(team_abbrev)
			#print('lineup_teams: ' + str(lineup_teams))

			lineup_statuses = []
			for lineup_status in lineup.find_all('li', {'class': 'lineup__status'}):
				#print('lineup_status: ' + str(lineup_status))
				status_text = 'expected'#lineup_status.decode_contents()#str(list(lineup_team.descendants)[0])
				if re.search('confirmed',str(lineup_status)):
					status_text = 'confirmed'
				#print('status_text: ' + str(status_text))
				lineup_statuses.append(status_text)
			#print('lineup_statuses: ' + str(lineup_statuses))

			# 1 for each team, so 2 per list
			lineups_lists = lineup.find_all('ul', {'class': 'lineup__list'})
			for team_idx in range(len(lineups_lists)):
				lineup_list = lineups_lists[team_idx]
				#print('lineup_list: ' + str(lineup_list))

				lineup_team = lineup_teams[team_idx]
				#print('lineup_team: ' + str(lineup_team))
				# if team not in rosters for todays games, 
				# then we do not need to get the current lineup
				# likely bc the game already started but there are other games today
				if lineup_team in rosters.keys():
					all_lineups[lineup_team] = {starters_key:[],'bench':[],'out':[],'probable':[],'question':[],'doubt':[]}

					starters = []
					out = []
					probable = []
					questionable = []
					doubtful = []
					# first 5 are always starters, even if injury tag
					player_num = 0
					for player_element in lineup_list.find_all('li', {'class': 'lineup__player'}):
						#print('\nplayer_element: ' + str(player_element))
						player_name = player_element.find('a').decode_contents()
						#print('player_name: ' + str(player_name))
						player_name = determiner.determine_player_full_name(player_name, lineup_team, all_players_teams, rosters, cur_yr=cur_yr)
						# print('player_name: ' + str(player_name))
						# print('player_num: ' + str(player_num))
						
						# if player on team but not yet played for them 
						# then no need to mark as out bc not a factor
						if player_name != '':
							if player_num < 5:
								#print('starter')
								starters.append(player_name)
							else:
								# if not dnp status
								# 1st see if played this yr
								# then get avg play time this yr from player teams
								if player_name in all_players_teams.keys():
									player_teams = all_players_teams[player_name]
									if cur_yr in player_teams.keys() and lineup_team in player_teams[cur_yr].keys():
										#cur_team_dict = player_teams[cur_yr][lineup_team]
										avg_play_time = player_teams[cur_yr][lineup_team]['MIN']
										if avg_play_time > 11.5: # 48/4 = 12 +/- 0.5
											# if cur_yr in player_teams.keys():
											# determine out status
											# if out
											# title="Very Unlikely To Play"
											if re.search('Very Unlikely',str(player_element)):
												#print('out')
												out.append(player_name)
											# if doubtful
											# title="Unlikely To Play"
											elif re.search('Unlikely',str(player_element)):
												#print('doubtful')
												doubtful.append(player_name)
											# if questionable
											# title="Toss Up To Play"
											elif re.search('Toss Up',str(player_element)):
												#print('questionable')
												questionable.append(player_name)
											# if probable
											# title="Likely To Play"
											elif re.search('Likely',str(player_element)):
												#print('probable')
												probable.append(player_name)

							player_num += 1

							# if re.search('injury',str(player_element)):
							# 	out.append(player_name)
							# else:
							# 	starters.append(player_name)

					# print('starters: ' + str(starters))
					# print('out: ' + str(out))
					# print('probable: ' + str(probable))
					# print('questionable: ' + str(questionable))
					# print('doubtful: ' + str(doubtful))

					all_lineups[lineup_team][starters_key] = starters
					all_lineups[lineup_team][out_key] = out
					all_lineups[lineup_team][probable_key] = probable
					all_lineups[lineup_team][question_key] = questionable
					all_lineups[lineup_team][doubt_key] = doubtful


	# determine bench by seeing difference between all teammates, starters, and out
	# all_teams_players = {year:{team:[players],...},...}
	# make sure active playing and on roster before adding to bench
	# if they are a new teammate meant to play then it will not be accurate
	# unless we check roster and see that player got significant play time on former team
	# bc then likely to get play time on new team
	# but if took everyone on roster then it would show players that dont play
	# but it doesnt matter if they havent played before bc we have no data with them on this team yet
	# all_teams_current_players: {'sac': ['Domantas Sabonis',...
	#all_teams_current_players = all_teams_players[cur_yr]
	#print('all_teams_current_players: ' + str(all_teams_current_players))
	for team, lineup in all_lineups.items():
		# print('team: ' + str(team))
		# print('lineup: ' + str(lineup))
		# if team not in rosters for todays games, 
		# then we do not need to get the current lineup
		# likely bc the game already started but there are other games today
		if team in rosters.keys():
			# add ofs players to out so they are not put on bench
			team_ofs_players = []
			if team in ofs_players.keys():
				team_ofs_players = ofs_players[team]

			team_roster = rosters[team]
			#print('team_roster: ' + str(team_roster))
			
			#team_current_players = all_teams_current_players[team]
			#print('team_current_players: ' + str(team_current_players))
			
			bench = []
			#in_players = []
			# current players shows players in past box scores this season
			# while roster shows current players including practice players who dont play
			# and new teammates havent played before, 
			# AND shows if teammate was in box score no longer on team so not on bench
			#starters = lineup[starters_key]
			#out = lineup[out_key]
			lineup[out_key].extend(team_ofs_players)
			#doubtful = lineup[doubt_key]
			# print('starters: ' + str(starters))
			# print('out: ' + str(out))
			# print('doubtful: ' + str(doubtful))
			
			# consider moving to before we get all teams cur players so we only include if not dnp
			# get dnp status from avg play time<10 or never played
			# go thru all in roster in case new players traded will get big mins but havent played yet
			dnp = []#lineup[dnp_key]
			for player in team_roster:
				avg_play_time = 0

				if player in all_players_teams.keys() and cur_yr in all_players_teams[player].keys():
					# cur_yr_player_teams = {team:{GP:gp, MIN:min},...
					cur_yr_player_teams = all_players_teams[player][cur_yr]
					
					if len(cur_yr_player_teams.keys()) > 0: 
						cur_team_dict = list(cur_yr_player_teams.values())[-1]#determiner.determine_player_current_team()
						avg_play_time = cur_team_dict['MIN']

				if avg_play_time <= 11.5:
					dnp.append(player)
			#print('dnp: ' + str(dnp))
			lineup[dnp_key] = dnp

			# need to add starters and bench to in players separate in case new player on team so cur cond does not match prev conds without player
			# for starter in starters:
			# 	in_players.append(starter)

			for player in team_roster:
				#print('\nplayer: ' + player.title())

				#if player in team_roster: # check still on team

				player_names = [player] # for players with jr like kelly oubre jr sometimes excluded bc only 1
				if re.search('\sjr$|\ssr$', player):
					player_name = re.sub('\sjr$|\ssr$', '', player)
					player_names.append(player_name)

				#if player not in starters and player not in out and player not in doubtful and player not in dnp:
				if determiner.determine_player_benched(player_names, lineup):
					# and player not in out and player not in doubtful:
					# for players with jr like kelly oubre jr sometimes excluded bc only 1
					# so try both
					
					bench.append(player)
					#in_players.append(player)

				
			
			#print('bench: ' + str(bench))
			lineup[bench_key] = bench
			#lineup[in_key] = in_players


	# standardize format to unique player id
	# should we have actual player espn id?
	# not ideal bc not readable and we would need to get unique player first to get id
	# init [Klay Thompson, D. Green,...]
	# convert to full name bc that is good enough as unique id
	# final [klay thompson, draymond green]
	# for team, lineup in all_lineups.items():
	# 	for players in lineup.values():
	# 		for player in players:
	# 			# if given abbrev like D. Green need to know team or position to get full name
	# 			# already given team so use that
	# 			# check which player in all players teams list with this team has this abbrev
	# 			player = determiner.determine_player_full_name(player, team, all_players_teams)

	#all_lineups = {'dal': {'out': ['luka doncic', 'dante exum', 'maxi kleber', 'dereck lively ii', 'grant williams'], 'starters': ['jaden hardy', 'kyrie irving', 'josh green', 'derrick jones jr', 'dwight powell'], 'bench': ['seth curry', 'tim hardaway jr']}, 'por': {'out': [], 'starters': ['scoot henderson', 'anfernee simons', 'toumani camara', 'jerami grant', 'duop reath'], 'bench': ['deandre ayton', 'malcolm brogdon', 'skylar mays', 'shaedon sharpe', 'matisse thybulle', 'jabari walker', 'robert williams iii']}}
	print('all_lineups: ' + str(all_lineups))
	return all_lineups

# year_players_in_games_dict = {game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
# need all_players_teams to determine player full name
# bc we get abbrev in box score players in games
# and we want to compare to lineups with full names
# all_players_abbrevs = {jaylen brown: j brown sg, ...}
def read_team_players(team, year_box_scores, all_players_teams, year_players_abbrevs={}, cur_yr='', rosters={}):
	print('\n===Read Team Players for ' + team.upper() + '===\n')
	print('Input: year_box_scores = {game key:{away:{starters:{player:play time,...},bench:{...}},home:{...},... = {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...')
	print('Input: year_players_abbrevs = {player abbrev-team abbrev:player, ... = {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')# = ' + str(year_players_abbrevs))
	print('\nOutput: team_players = {year: {team: [player name, ... = \n')

	team_players = []

	# game_players = {away:{starters:[],bench:[]},home:starters:[],bench:[]}
	for game_key, game_box_scores in year_box_scores.items():
		#print('game_key: ' + str(game_key))
		#print('game_box_scores: ' + str(game_box_scores))
		# if we find this team in this game
		if re.search(team, game_key):
			#print('found team ' + team.upper() + ' in game ' + game_key)
			game_data = game_key.split()
			if len(game_data) > 2:
				away_team = game_data[0]
				#print('away_team: ' + str(away_team))
				home_team = game_data[1]
				#print('home_team: ' + str(home_team))

				loc = 'home'
				if team == away_team:
					loc = 'away'
				#print('loc: ' + str(loc))

				# always current team of interest
				# game_team_players = {starters:[],bench:[]}
				game_team_box_score = game_box_scores[loc]
				#game_team_players = game_players[loc]
				#print('game_team_box_score: ' + str(game_team_box_score))
				for team_part in game_team_box_score.values():
					# team_part = {player:play time, ...}
					#print('team_part: ' + str(team_part))
					for player, play_time in team_part.items():
						#print('\nplayer: ' + str(player))
						# here we consider avg play time, not play time this game
						# bc we want to exclude practice players?
						# but are they practice players if they played a game more than 10min? 
						# still yes but what happens to games they played >10min in
						# they would show up in the box score of that game bc they affected the game
						# we could not tell if practice player might play >10min in todays game
						# if we do not include practice players in box score bench
						# if we say they are on the bench in past games they did not play AND todays game they might not play then those games will still match as they should
						# so we must delineate practice players and out players while reading box score 
						
						#if play_time > 12: # minutes arbitrary to define practice player
						# do not include practice players in all teams players???
						# OR we still consider practice players as part of team bc we are able to see their minutes to filter them out later???
						player_name = ''
						if len(year_players_abbrevs.keys()) > 0:
							# only need year abbrevs bc looking for yr players
							# at this point we should have all abbrevs from box scores
							for abbrev, name in year_players_abbrevs.items():
								abbrev_data = abbrev.split('-')
								abbrev = abbrev_data[0]
								#print('player: ' + player)
								#print('abbrev: ' + abbrev)
								player_team = abbrev_data[1].lower()
								#print('team: ' + team)
								#print('player_team: ' + player_team)
								#print('name: ' + name)
								if player == abbrev and team == player_team:
									#print('found name ' + name)
									player_name = name
									break
						#print('player_name: ' + str(player_name))
						if player_name == '':
							player_name = determiner.determine_player_full_name(player, team, all_players_teams, rosters, game_key, cur_yr)#converter.convert_player_abbrev_to_name(player)
						# now we have both full name and abbrevs from players in games dict
						# if not already added, then add
						#print('player_name: ' + str(player_name))
						if player_name not in team_players and player_name != '': # blank if player gone and never read
							team_players.append(player_name)
							#print('team_players: ' + str(team_players))
						# elif player_name == '':
						# 	print('Warning: player name not found! ' + player)

	#print('final team_players: ' + str(team_players))
	return team_players

# all_teams_players = {year:{team:[players],...},...}
# season_teams_players = {team:[players],...}
# year_players_in_games_dict = {game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
def read_season_teams_players(year, teams, year_box_scores, init_all_teams_players, all_players_teams, all_players_abbrevs, read_new_teams, cur_yr='', rosters={}):
	print('\n===Read Season Teams Players: ' + str(year) + '===\n')
	print('Input: teams = [teams]')
	print('Input: year_box_scores = {game key:{away:{starters:{player:play time,...},bench:{...}},home:{...},... = {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...')
	print('Input: init_all_teams_players = {year:{team:[players],...},... = ')
	print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')
	print('\nOutput: all_teams_players = {year:{team:[players],...},... = \n')

	season_teams_players = {}
	# if year, teams, and all players are added already then we can copy from file
	# if the team is in the yr, then it should be complete unless error so would not need to reread
	
	year_players_abbrevs = all_players_abbrevs[year]

	if not read_new_teams: # get init teams
		if year in init_all_teams_players.keys(): #and len(init_all_teams_players[year]) > 0:
			read_new = False
			# season_teams_players = {team:[players],...},...}
			# if any of the teams are empty, overwrite
			init_season_teams_players = init_all_teams_players[year]
			for team_players in init_season_teams_players.values():
				if len(team_players) == 0:
					read_new = True
					break
			if not read_new:
				#print('found year in init all teams players')
				season_teams_players = init_all_teams_players[year]

	# for each team, read players
	for team in teams:
		if team not in season_teams_players.keys():
			team_players = read_team_players(team, year_box_scores, all_players_teams, year_players_abbrevs, cur_yr, rosters)
			season_teams_players[team] = team_players
		elif team in season_teams_players.keys() and len(season_teams_players[team]) == 0:
			team_players = read_team_players(team, year_box_scores, all_players_teams, year_players_abbrevs, cur_yr, rosters)
			#if len(team_players) > 0:
			# if we only add some teams then we need to know team of interest to decide if we need to read new teams
			# better to know not read bc empty list?
			season_teams_players[team] = team_players
			if len(team_players) == 0:
				print('Warning: Error reading team players! ' + team)
				# we need all teams for the yr
				#break

	# if yr in all_players_teammates dict, then already read before for prev and today for cur
	# otherwise it would not have read in file
	
	# season_teams_players = {team:[players],...}
	#print('season_teams_players: ' + str(season_teams_players))
	return season_teams_players

# need to compare teammates from box score to teammates still on roster to make sure they are still on roster
# before saying they are on bench
# players they played with at any point in the season, each season
# all_teams_players = {year:{team:[players],...},...}
# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
def read_all_teams_players(all_box_scores, rosters, all_players_teams, all_players_abbrevs, cur_yr, read_new_teams, teams=[]):
	print('\n===Read All Teams Players===\n')
	print('Input: all_box_scores = {year:{game key:{away:{starters:{player:play time,...},bench:{...}},home:{...},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...')
	print('Input: all_teams_rosters = {team:[players],... = {\'nyk\':[\'jalen brunson\',...],...')
	print('Input: Current Year to get current team to get full name')
	print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
	print('Input: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...')
	print('\nOutput: all_teams_players = {year:{team:[players], ... = {\'2024\': {\'wsh\': [\'kyle kuzma\', ...\n')

	if len(teams) == 0:
		teams = ['bos','bkn', 'nyk','phi', 'tor','chi', 'cle','det', 'ind','mil', 'den','min', 'okc','por', 'uta','gsw', 'lac','lal', 'phx','sac', 'atl','cha', 'mia','orl', 'wsh','dal', 'hou','mem', 'nop','sas']#list(rosters.keys())

	all_teams_players_file = 'data/all teams players.json'

	init_all_teams_players = read_json(all_teams_players_file)
	#print("init_all_teams_players: " + str(init_all_teams_players))

	all_teams_players = copy.deepcopy(init_all_teams_players) # need to init as saved teams so we can see difference at end

	try:
		for year, year_box_scores in all_box_scores.items():
			# player_teammates = {year:[teammates],...}
			season_teams_players = read_season_teams_players(year, teams, year_box_scores, all_teams_players, all_players_teams, all_players_abbrevs, read_new_teams, cur_yr, rosters)

			all_teams_players[year] = season_teams_players

	except Exception as e:
		print('Exception while reading all players teams: ', e)

	# need to add to file after each player bc if hangs halfway through then will lose all work
	# or if that is too inefficient then make sure never hangs
	# by retrying same player if hit cancel instead of skipping player
	if not init_all_teams_players == all_teams_players:
		writer.write_json_to_file(all_teams_players, all_teams_players_file, 'w')



	# all_teams_players = {team:{year:[players],...},...}
	#print('all_teams_players: ' + str(all_teams_players))
	return all_teams_players

def read_player_name(player_abbrev, player_id, all_players_ids_file=''):
	print('\n===Read Player Name: ' + player_abbrev + '===\n')
	
	player_name = ''

	site = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id

	soup = read_website(site)

	if soup is not None:
		if re.search('HTTP Error', str(soup)):
			print('Warning: HTTP Error! ' + soup + ', ' + site)
		else:
			# find last element of ul with class PlayerHeader__Team_Info
			names = list(soup.find("h1", {"class": "PlayerHeader__Name"}).descendants)
			#print('names: ' + str(names))
			first_name = names[1]
			last_names = names[3]
			player_name = first_name + ' ' + last_names
			# player_name = str(names[0].decode_contents())
			# print('player_name: ' + player_name)
			# for name in names[1:]:
			# 	print('name: ' + name)
			# 	text = str(name.decode_contents())
			# 	player_name += ' ' + text
			# 	print('player_name: ' + player_name)
			player_name = re.sub('-',' ',player_name).lower()
			player_name = re.sub('\.','',player_name)

			print('Success', player_name.title(), player_abbrev)

			if player_name != '':
				# save new id
				if all_players_ids_file == '':
					all_players_ids_file = 'data/all players ids.csv' # need to get names
				data = [[player_name, player_id]]
				write_param = 'a' # append ids to file
				writer.write_data_to_file(data, all_players_ids_file, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet
	else:
		print('Warning: website has no soup!')

	print('player_name: ' + player_name)
	return player_name


# current lineup: B Key F, C Braun G, C Gillespie G, D Jordan C, H Tyson F, J Holiday SF, J Huff C, J Pickett G, J Strawther G, P Watson F, R Jackson PG, Z Nnaji PF bench===
				#'B Key F, C Braun G, C Gillespie G, D Jordan C, H Tyson F, J Huff C, J Pickett G, J Strawther G, P Watson F, Z Nnaji PF bench'

# player stat dict: 'B Key F, C Braun G, C Gillespie G, D Jordan C, H Tyson F, J Pickett G, J Strawther G, R Jackson PG, Z Nnaji PF bench': {'12': 32}, 
def read_year_players_abbrevs(year, year_box_scores, all_players_teams, init_all_players_abbrevs, rosters, cur_yr, all_players_espn_ids, read_new_player_ids):
	print('\n===Read Year Players Abbrevs: ' + year + '===\n')
	print('Input: year_box_scores = {game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
	print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
	print('Input: init_year_players_abbrevs = {player:abbrev, ... = ')
	print('Input: rosters = {team:roster, ... = {\'nyk\': [jalen brunson, ...], ...')
	print('Input: Current Year bc only accurate roster.')
	print('\nOutput: year_players_abbrevs = {player abbrev-team abbrev:player, ... =  {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...\n')

	#print('init all_players_espn_ids: ' + str(all_players_espn_ids))

	# we pass all players abbrevs in here in case we cant find search results for prev yrs for dnp player who has search results for current yr
	year_players_abbrevs = {}
	if year in init_all_players_abbrevs.keys():
		year_players_abbrevs = init_all_players_abbrevs[year]#init_year_players_abbrevs
	cur_yr_players_abbrevs = {}
	if cur_yr in init_all_players_abbrevs.keys():
		cur_yr_players_abbrevs = init_all_players_abbrevs[cur_yr]

	all_players_ids_file = 'data/all players ids.csv' # need to get names
	all_players_teams_file = 'data/all players teams.json' # need to get teams

	unknown_names = []
	for game_key, game_players in year_box_scores.items():
		print('\ngame_key: ' + str(game_key))
		print('game_players: ' + str(game_players))

		game_data = game_key.split()
		if len(game_data) > 2:

			# ensure date after preseason bc preseason not counted in players teams dict
			# cannot use hard date bc changes each yr
			# date = re.sub('/\d+$','',game_data[2])
			# date_obj = datetime.strptime(date, '%m/%d')
			# preseason_end_date_obj = datetime.strptime('10/20', '%m/%d')
			# if date_obj > reg_season_start_date_obj
			
			away_team = game_data[0]
			print('away_team: ' + str(away_team))
			home_team = game_data[1]
			print('home_team: ' + str(home_team))

			for loc, game_team_players in game_players.items():
				print('\nloc: ' + str(loc))
				#print('game_team_players: ' + str(game_team_players))

				# team of this player in this game
				game_player_team_abbrev = home_team
				if loc == 'away':
					game_player_team_abbrev = away_team
					
				game_player_team_name = game_player_team_abbrev # will be set blank for irreg team and then used to break loop to next team
				print('game_player_team_name: ' + str(game_player_team_name))
				
				for team_part, team_part_players in game_team_players.items():
					print('\nteam_part: ' + str(team_part))
					#print('team_part_players: ' + str(team_part_players))
					
					for player_abbrev in team_part_players:
						print('\nplayer_abbrev: ' + str(player_abbrev))

						# if we already stored player abbrev and team, 
						# then check to make sure this box score is correct
						# bc sometimes wrong search will give wrong box score
						#if game_player_team_abbrev == player_team:

						# if abbrev already in year_players_abbrevs
						# no need to run again
						# if player name blank bc not on current, then it will waste time trying to determine full name
						# instead, we need a way to get full name from abbrev on box score
						
						# need to add team abbrev to player abbrev bc tre jones and tyus jones have the same abbrev t jones pg
						player_abbrev_key = player_abbrev + '-' + game_player_team_abbrev
						print('player_abbrev_key: ' + str(player_abbrev_key))

						if player_abbrev_key not in year_players_abbrevs.keys() and player_abbrev_key not in unknown_names:

							# check if can determine name from saved players teams
							player_name = determiner.determine_player_full_name(player_abbrev, game_player_team_abbrev, all_players_teams, rosters, game_key, cur_yr)
							print('player full name: ' + str(player_name))


							if player_name == '': # not saved in all players teams or abbrev not matched?
								print('name not saved ' + player_abbrev_key)
								game_player_team_name = converter.convert_team_abbrev_to_name(game_player_team_abbrev)
								if game_player_team_name == '': # maybe irregular team not considered for exhibition game
									print('Caution: Blank Player Team. ' + game_player_team_abbrev)
									# continue to next team
									break
								
								if read_new_player_ids:
									player_id = read_player_espn_id(player_abbrev, all_players_espn_ids, game_player_team_name, year=year)
									print('player_id: ' + player_id)
									# if player id comes back blank then maybe searching for dnp player who only has game log search results for current yr even though they played past yrs as dnp players
									# so look for same abbrev in cur yr abbrevs
									# python find value in dictionary
									player_name = ''#list(all_players_espn_ids.keys())[list(all_players_espn_ids.values()).index(player_id)]
									if player_id != '':
										for name, id in all_players_espn_ids.items():
											if player_id == id:
												player_name = name.lower()
												break

										print('player_name from id file: ' + player_name)

										if player_name == '': # id not saved either
											print('id not saved either ' + player_abbrev)
											player_name = read_player_name(player_abbrev, player_id, all_players_ids_file)
											# saved new id to file in read player name fcn
											# so add to all players espn ids dict
											all_players_espn_ids[player_name] = player_id
											
											# we know find_players=True bc we are reading players abbrevs in this fcn which we only need to find players
											# and we know we need all players teams including those in box scores
											# so get new player's teams and append to all players teams dict
											player_teams = read_player_teams(player_name, player_id)
											all_players_teams[player_name] = player_teams
											writer.write_json_to_file(all_players_teams, all_players_teams_file)
									
									elif player_abbrev_key in cur_yr_players_abbrevs: # id blank bc no search results bc dnp player
										player_name = cur_yr_players_abbrevs[player_abbrev_key]
							
							# print('final player_name: ' + player_name)
							# print('final player_abbrev_key: ' + player_abbrev_key)
							if player_name != '':
								year_players_abbrevs[player_abbrev_key] = player_name
							else: # player name blank
								# only add once to unknown list
								if player_abbrev_key not in unknown_names:
									unknown_names.append(player_abbrev_key)
								# CAUTION: player name blank bc player not on roster
								print('\n===Warning: Blank Player Name: ' + player_abbrev_key + '===\n')
								#print('unknown_names: ' + str(unknown_names))


					if game_player_team_name == '':
						# continue to next team
						break
						
					if len(unknown_names) > 0:
						print('WARNING unknown_names: ' + str(unknown_names))
								
	#print('year_players_abbrevs: ' + str(year_players_abbrevs))
	return (year_players_abbrevs, all_players_espn_ids, all_players_teams)

# for each game in games dict, 
# determine full name associated with abbrev
# given team at time of game lac phx 4/9/2023
# sometimes multiple abbrevs for same player like X Tillman and Tillman Sr
# all_players_abbrevs: {'2024': {'K Kuzma SF': 'kyle kuzma',...
def read_all_players_abbrevs(all_box_scores, init_all_players_teams, rosters, cur_yr, all_players_espn_ids, read_new_player_ids):
	print('\n===Read All Players Abbrevs===\n')
	print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
	print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
	print('Input: rosters = {team:roster, ... = {\'nyk\': [jalen brunson, ...], ...')
	print('Input: Current Year bc only accurate roster.')
	print('\nOutput: all_players_abbrevs = {year:{player abbrev-team abbrev:player, ... = {\'2024\': {\'J Jackson Jr PF-MEM\': \'jaren jackson jr\',...\n')

	# go to first game in player game log and see which abbrev fits their name?
	# No bc we need every player abbrev, not just player of interest
	# bc we have conditions teammates and opps

	# do we need just active players or all players in rosters? 
	# just active bc if they are new then we have no data and we will check past seasons to see if played

	all_players_abbrevs_file = 'data/all players abbrevs.json'
	init_all_players_abbrevs = read_json(all_players_abbrevs_file)

	# if cur_yr == '':
	# 	cur_yr = determiner.determine_current_season_year()
	# all_players_cur_abbrevs_filename = 'data/all players abbrevs - ' + cur_yr + ' - ' + todays_date + '.json'
	# all_players_prev_abbrevs_filename = 'data/all players abbrevs - prev.json'
	# init_all_players_abbrevs = read_cur_and_prev_json(all_players_cur_abbrevs_filename,all_players_prev_abbrevs_filename)
	#print('init_all_players_abbrevs: ' + str(init_all_players_abbrevs))
	all_players_abbrevs = copy.deepcopy(init_all_players_abbrevs) #{}
	all_players_teams = copy.deepcopy(init_all_players_teams)

	for year, year_box_scores in all_box_scores.items():
		#print('\nyear: ' + str(year))
		
		# pass all abbrevs in case cant find player on google by just abbrev for prev yrs in case of dnp players
		# see moses brown
		# init_year_players_abbrevs = {}
		# if year in init_all_players_abbrevs.keys():
		# 	init_year_players_abbrevs = init_all_players_abbrevs[year]
		
		year_players_abbrevs_data = read_year_players_abbrevs(year, year_box_scores, all_players_teams, all_players_abbrevs, rosters, cur_yr, all_players_espn_ids, read_new_player_ids) # name: abbrev,...
		year_players_abbrevs = year_players_abbrevs_data[0]
		all_players_espn_ids = year_players_abbrevs_data[1]
		all_players_teams = year_players_abbrevs_data[2]

		all_players_abbrevs[year] = year_players_abbrevs

	if not init_all_players_abbrevs == all_players_abbrevs:
		writer.write_json_to_file(all_players_abbrevs, all_players_abbrevs_file)
	# 	writer.write_cur_and_prev(init_all_players_abbrevs, all_players_abbrevs, all_players_cur_abbrevs_filename, all_players_prev_abbrevs_filename, cur_yr, player_name)

	# we update all players teams if we encountered new player id in box score
	all_players_teams_file = 'data/all players teams.json'
	if not init_all_players_teams == all_players_teams:
		writer.write_json_to_file(all_players_teams, all_players_teams_file)

	#print('all_players_abbrevs: ' + str(all_players_abbrevs))
	return (all_players_abbrevs, all_players_espn_ids, all_players_teams)

# active teammates actually played with so not including practice players on roster
# all_players_teammates = {player:{year:[teammates],...},...}
def read_all_players_teammates(all_players_season_logs, all_box_scores, cur_yr, season_years):
	print('\n===Read All Players Teammates===\n')
	print('Input: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
	print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
	print('\nOutput: all_players_teammates = {player:{year:[teammates],... = {\'jalen brunson\': {\'2024\': [\'J Randle PF\', ...\n')

	all_players_teammates_file = 'data/all players teammates.json'

	# much more likely to play with a new teammate off the bench than a trade
	# so update teammates after each game
	# always current yr bc no matter what yr of interest only current yr changes with each new game
	# if cur_yr == '':
	# 	cur_yr = determiner.determine_current_season_year() #str(datetime.today().year)
	# all_cur_teammates_filename = 'data/all ' + cur_yr + ' teammates ' + todays_date + '.json'
	# all_prev_teammates_filename = 'data/all prev teammates.json'
	
	init_all_players_teammates = read_json(all_players_teammates_file) #read_cur_and_prev_json(all_cur_teammates_filename,all_prev_teammates_filename)
	#print('init_all_players_teammates: ' + str(init_all_players_teammates))
	
	all_players_teammates = copy.deepcopy(init_all_players_teammates) # all teammates for all players


	for player, player_season_logs in all_players_season_logs.items():
		# player_teammates = {year:[teammates],...}
		player_teammates = read_player_teammates(player, player_season_logs, all_box_scores, all_players_teammates, cur_yr, season_years)

		all_players_teammates[player] = player_teammates

	# if not init_all_players_teammates == all_players_teammates:
	# 	writer.write_cur_and_prev(init_all_players_teammates, all_players_teammates, all_cur_teammates_filename, all_prev_teammates_filename, cur_yr)

	if not init_all_players_teammates == all_players_teammates:
		writer.write_json_to_file(all_players_teammates, all_players_teammates_file, 'w')

	# all_players_teammates = {player:{year:[teammates],...},...}
	#print('all_players_teammates: ' + str(all_players_teammates))
	return all_players_teammates

# read player teammates for all yrs from all players teammates dict
# or internet if not saved? no bc already read all available teammates so no need to check internet again
# all_players_teammates = {player:{year:[teammates],...},...}
# player_teammates = {year:[teammates],...}
# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
def read_player_teammates(player, player_season_logs, all_box_scores, init_all_players_teammates={}, cur_yr='', season_years=[]):
	# print('\n===Read Player Teammates: ' + player.title() + '===\n')
	# print('\nInput: player_season_logs = {year:{stat name:{game idx:stat val, ... = {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
	# print('Input: all_box_scores = {year:{game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
	# print('Input: init_all_players_teammates = {player:{year:[teammates],... = ')
	# print('Input: Current Year bc new teammates each game.')
	# print('\nOutput: player_teammates = {year:[teammates],... =  {\'2024\': [\'J Randle PF\', ...\n')


	player_teammates = {}
	if player in init_all_players_teammates.keys():
		player_teammates = init_all_players_teammates[player]

	# if yr in all_players_teammates dict, then already read before for prev and today for cur
	# otherwise it would not have read in file
	for year, player_season_log in player_season_logs.items():
		#print('\nyear: ' + year)
		if year not in season_years:
			continue
		# for prev seasons teammates unchanged
		# for cur yr must update each new game
		if year == cur_yr or year not in player_teammates.keys():
			year_box_scores = all_box_scores[year]
			year_teammates = read_year_teammates(player, year, player_season_log, year_box_scores)
			player_teammates[year] = year_teammates

	# player_teammates = {year:[teammates],...}
	#print('player_teammates: ' + str(player_teammates))
	return player_teammates


# read teammates using box score data in all players in games dict
# which gives away home teams players
def read_year_teammates(player, season_year, player_season_log, year_box_scores):
	# print('\n===Read Season Teammates for ' + player.title() + ', ' + season_year + '===\n')
	# print('\nInput: player_season_log = {stat name:{game idx:stat val, ... = {\'Player\': {\'0\': \'jalen brunson\', ...')
	# print('Input: year_box_scores = {game key:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}},... = {\'mem okc 12/18/2023\': {\'away\': {\'starters\': [\'J Jackson Jr PF\', ...], \'bench\': [\'S Aldama PF\', ...]}, \'home\': ...')
	# print('\nOutput: season_teammates = [p1,...] =  [\'J Randle PF\', ...\n')

	year_teammates = []

	# go thru game logs instead of all players in games bc more efficient
	# we need all players in games to tell teammates
	if len(year_box_scores.keys()) > 0:
		# print('\n===Year: ' + str(year) + '===\n')
		# print('player_season_log: ' + str(player_season_log))

		# year_players_in_games = {}
		# if year in all_box_scores.keys():
		# 	year_players_in_games = all_box_scores[year]

		# use date and opp team in game log to get game players
		# num games = len(field vals) so take first field
		# idx_dict: {'0': 'james harden', ...
		stat_dicts = list(player_season_log.values())
		if len(stat_dicts) > 0:
			idx_dict = stat_dicts[0]
			for game_idx in range(len(idx_dict.keys())):
				game_idx_str = str(game_idx)
				#print('\n===Game: ' + game_idx_str + '===\n')

				if 'Date' in player_season_log.keys():

					game_date = player_season_log['Date'][game_idx_str]
					#print('game_date: ' + str(game_date)) # wed 11/18
					game_opp = player_season_log['OPP'][game_idx_str].lower()
					#print('game_opp: ' + str(game_opp))  # vsind

					# find matching game in list of all players in games
					# still unique bc team only plays once per day
					# need to iso date and team separately bc string not always in order of team date bc they maybe home/away
					# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
					# game_players = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}
					# game_teammates_dict = {starters:[],bench:[]}
					player_team = ''
					game_teammates_dict = {}
					for game_key, game_players in year_box_scores.items():
						#print('game_key: ' + str(game_key))

						if len(game_players.keys()) > 0:
							# first look for matching date
							game_key_data = game_key.split()
							date_idx = 2
							if len(game_key_data) > date_idx:
								game_key_date = re.sub('/\d+$','',game_key_data[date_idx]) # 11/11/2024 -> 11/11
								#print('game_key_date: ' + str(game_key_date))
								# game_key_date = 11/18
								# game_date: wed 11/18 -> 11/18
								game_date = re.sub('[a-zA-Z]+','',game_date).strip()
								#print('game_date: ' + str(game_date))
								if game_key_date == game_date:
									# look for matching team
									# game_key_teams = re.sub('\s\d+.+$','',) #'away home 11/11/2024'
									# print('game_key_teams: ' + str(game_key_teams))

									# game_opp = vsind
									game_data = game_key.split() # away,home,date

									if len(game_data) > 2:
										away_team = game_data[0]
										home_team = game_data[1]

										# find game
										if re.search(away_team, game_opp):
											player_team = home_team
											game_teammates_dict = game_players['home']
											break
										elif re.search(home_team, game_opp):
											player_team = away_team
											game_teammates_dict = game_players['away']
											break
						else:
							print('Warning: Box score blank! ' + game_key)

					if player_team != '':
						# print('player_team: ' + str(player_team))
						# print('game_teammates_dict: ' + str(game_teammates_dict))

						# loop thru games to see if we encounter new teammates
						# game_teammates_dict = {starters:[],bench:[]}
						for teammates in game_teammates_dict.values():
							for teammate in teammates:
								if teammate not in year_teammates:
									year_teammates.append(teammate) # prefer not to lower bc comes with position already uppercase like J Brown SG

		else:
			print('Warning: player has no stat dicts! ' + player.title())
	else:
		print('Warning: year_box_scores is empty! ' + str(year_box_scores))

	# year_teammates: ['A. Davis PF', ...
	#print('year_teammates: ' + str(year_teammates))
	return year_teammates

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

# all_box_scores = {game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
# we will convert away home to teammates opponents given current player of interest
# game_box_scores_dict = {away:df, home:df}
# get the game box score page using the game id
# get the box score from the page in a df
# game_box_scores_dict = {away:df, home:df}
# currently returns empty dict if results already saved
def read_players_in_box_score(game_box_scores_dict, roster={}):
	#print("\n===Read Players in Box Score===\n")

	players_in_box_score_dict = {'away':{'starters':[],'bench':[]},'home':{'starters':[],'bench':[]}}

	#team_idx = 0
	if len(game_box_scores_dict.keys()) > 0:
		for loc, players_dict in players_in_box_score_dict.items():
			#print('\nloc:' + str(loc))
			#print('players_dict:' + str(players_dict))
			team_box_score = game_box_scores_dict[loc]
			#print('team_box_score:' + str(team_box_score))
			#home_team_box_score = game_box_scores[1]

			players = team_box_score[0].drop(0).to_list()
			#print('players:' + str(players))
			play_times = team_box_score[1].drop(0).to_list()

			# remove periods and positions from player names
			final_players = []
			for player in players:
				player = re.sub('\.','',player)#.lower() # easier to read if titled but ust match comparisons with all teammates. all teammates comes from all players in games so they auto match format
				final_players.append(player)
				# the problem with removing position is if we have 2 players with
				# same first initial and last name on same team
				# but that is rare enough that we could make function to check for 2 players with same name on same team
				# so then we definitely need to store box score data instead of just players in games
				# so we have positions
				# keep positions in title and then erase before comparing string keys
				# and use position only if 2 players on same team have same name!!!
				# but it takes a lot more processing to check if players have same name
				# for each team when only 1 team has it and it is rare
				# there are also brothers who may or not play same position so
				# first initial, last name, and position match but not team
				#player = re.sub('[A-Z]+$','',player).strip()

			#print('final_players:' + str(final_players))

			# split list into starters and bench
			# skip header row bt starters and bench
			bench_idx = 5 # bc always 5 starters
			starters = final_players[:bench_idx]
			bench = final_players[bench_idx+1:]

			starters_dict = {}
			for player_idx in range(len(players)):
				player = final_players[player_idx]
				play_time = play_times[player_idx]
				starters_dict[player] = play_time

			team_part = 'starters'
			players_dict[team_part] = starters_dict # {player:play time,...}
			


			# add players in roster that did not play to bench bc they are not considered out
            # so they must be added to bench to match current condition
			# for player in roster:
			# 	if player not in starters and player not in bench:
			# 		bench.append(player)
			# actually do not consider practice players on bench
			# bc cannot tell difference bt practice player or out due to injury
			# instead remove practice players from current conditions 
			# and remove players who played less than 10 minutes from box scores?

			team_part = 'bench'
			players_dict[team_part] = bench

		#team_idx += 1

	# players_in_box_score_dict = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
	#print('players_in_box_score_dict: ' + str(players_in_box_score_dict))
	return players_in_box_score_dict



# get game box scores from espn.com
# 1 box score per team
# game_box_scores_dict = {away:df, home:df}
# currently returns empty dict if results already saved
# already checked that it is current yr or unsaved prev yr before running this fcn
# year idx saves time so we dont have to check if game key in dict
# also game ids saves time bc faster list
# BUT cur yr box scores is only cur yr so which is actually faster???
# both are actually search as dicts so level 1 is shorter in cur yr box scores dict
# if year_idx == 0 and game_key in init_cur_yr_game_players_dict.keys(): #game_id in existing_game_ids_dict.keys(): 
# bc only run for unsaved games
# now that we have box scores we can isolate stats of interest, starting with player name
# given box scores for each team, return lists of teammates and opponents or home/away?
# need to save as home away so we only need to read once per game and not once per player
# for each player knowing their team we can tell which is opponents
def read_game_box_scores(game_key, game_id='', existing_game_ids_dict={}, init_box_scores={}, game_url='', read_new_game_ids=True, player_name=''):
	print("\n===Read Game Box Scores: " + game_key.upper() + ", " + player_name.title() + "===\n")
	#print('read_new_game_ids: ' + str(read_new_game_ids))

	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	#game_box_scores = [] # players, stats for away team and home team

	game_box_scores_dict = {} # {away:df, home:df}

	# try to read local box scores
	#if game_id in existing_game_ids_dict.keys():
	
	# get espn player id from google so we can get url
	if game_url == '':
		if game_id == '':
			game_id = read_game_espn_id(game_key, existing_game_ids_dict, read_new_game_ids)
		#season_year = 2023
		game_url = 'https://www.espn.com/nba/boxscore/_/gameId/' + game_id #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
	#print("game_url: " + game_url)

	#try:

	if game_id != '': # blank if unable to read due to too many requests
		
		html_results = read_web_data(game_url) #pd.read_html(game_url)
		#print("html_results: " + str(html_results))

		if html_results is not None:
			len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

			# order is always away-home for this espn page ref
			#team_locs = ['away','home']
			team_loc = 'away'

			for order in range(len_html_results):
				#print("order: " + str(order))

				html_result_df = html_results[order]
				# print('html_result: ' + str(html_result_df))
				# print("no. columns: " + str(len(html_result_df.columns.tolist())))

				# very first html result is the game summary quarter by quarter score and total score

				# first get players, which is html result with row 0 = 'starters'
				# order is always away-home
				
				if re.search('starters', str(html_result_df.loc[[0]])): # locate first row
					# init format
					# 0           starters
					# 1       B. Ingram SF
					# 2        H. Jones SF
					# 3   J. Valanciunas C
					# 4     C. McCollum SG
					# 5   T. Murphy III SG
					# 6              bench
					# 7    L. Nance Jr. PF
					# 8     N. Marshall SF
					# 9   J. Richardson SG
					# 10      D. Daniels G
					# 11      G. Temple SF
					# 12  W. Hernangomez C
					# 13        J. Hayes C
					# 14   K. Lewis Jr. PG
					# 15      D. Seabron G
					# 16              team,  
					#print('init player_name_df:\n' + str(html_result_df))

					# remove, starters, bench, and team rows
					# locate first column
					# wait to remove rows until name and stats dfs concated
					player_name_df = html_result_df #[(html_result_df.loc[:,0] != 'starters') & (html_result_df.loc[:,0] != 'bench') & (html_result_df.loc[:,0] != 'team')]
					#print('player_name_df:\n' + str(player_name_df))

					# remove players who did not play
					# info about dnp is in next html result so use order+1

					player_stats_df = html_results[order+1]
					#print('player_stats_df:\n' + str(player_stats_df))

					#player_box_score_df.columns.values[0] = 'MIN'
					# for col in player_box_score_df.columns:
					# 	print(col)

					player_box_score_df = pd.concat([player_name_df,player_stats_df], axis=1, sort=False, ignore_index=True)
					#print('player_box_score_df:\n' + str(player_box_score_df))

					# df = df[df['Credit-Rating'].str.contains('Fair')] 
					final_idx = 0 # if 0 then no dnps so find 'team' label
					dnp_idx = 0 #player_box_score_df[player_box_score_df[1].isin(['DNP'])].index#.idxmax()
					for x in player_box_score_df.itertuples():
						# print('x: ' + str(x))
						# print('x[2]: ' + str(x[2]))
						if str(x[2]).find('DNP') != -1:
							dnp_idx = x[0]
							break
					#print('dnp_idx: ' + str(dnp_idx))

					if dnp_idx != 0:
						final_idx = dnp_idx
					else:
						idxs = player_box_score_df.loc[player_box_score_df[0] == 'team'].index
						if len(idxs) > 0:
							final_idx = idxs[0]
					
					# idxs = player_box_score_df.loc[player_box_score_df[1] == 'DNP-COACH\'S DECISION'].index
					# print('idxs: ' + str(idxs))
					# if len(idxs) > 0:
					# 	final_idx = idxs[0] # Int64Index([], dtype='int64')
					# else:
					# 	idxs = player_box_score_df.loc[player_box_score_df[0] == 'team'].index
					# 	if len(idxs) > 0:
					# 		final_idx = idxs[0]
						# else:
						# 	print('Warning: player_box_score_df missing team line so check format!')
					#print('final_idx: ' + str(final_idx))

					if final_idx != 0:
						player_box_score_df = player_box_score_df.drop(player_box_score_df.index[final_idx:])
						#print('player_box_score_df:\n' + str(player_box_score_df))
					# else:
					# 	print('Warning: player_box_score_df final_idx ' + str(final_idx) + ' = 0!')

					# remove unwanted rows/columns
					# if no dnp then remove lines after 'team'
					player_box_score_df = player_box_score_df.dropna(axis=1)
					#print('player_box_score_df:\n' + str(player_box_score_df))

					# remove bench row? no bc we want to separate
					
					player_box_score_df['Game'] = game_key
					#print('player_box_score_df:\n' + str(player_box_score_df))

					# get the index of the first row with dnp
					
					# there is no key row so we must look at values in rows to determine keys
					
					# old: final format had starters and bench in 1 list
					# 1 B. Ingram SF
					# 2 ...
					# new final format keeps starters and bench separate

					# default format undesired: {0: {0: 'starters', 1: 'J. Kuminga PF',...
					# desired format {game:{away:{starters:{},bench:{}} so player stats on same level as player
					box_score_dict = converter.convert_box_score_to_dict(player_box_score_df)
					#print("box_score_dict: " + str(box_score_dict))

					#game_box_scores.append(player_box_score_df)
					#print("team_loc: " + str(team_loc))
					game_box_scores_dict[team_loc] = box_score_dict#player_box_score_df
					#print("game_box_scores_dict: " + str(game_box_scores_dict))

					team_loc = 'home' # order is always away-home for this espn page ref



	
	# game_box_scores_dict = {away:df, home:df}
	print("game_box_scores_dict: " + str(game_box_scores_dict))
	return game_box_scores_dict # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword

# assemble components of game key into string for search
def read_game_key(season_year, team_abbrev, game_row):
	# print('\n===Read Game Key===\n')
	# print('Input: Season Year = ' + season_year)
	# print('Input: Team Abbrev = ' + team_abbrev)
	# print('Input: Game Row in table with game data: Date, Opponent')
	# print('\nOutput: Game Key = away home date\n')

	init_game_date_string = game_row['Date'].lower().split()[1]#player_reg_season_log.loc[game_idx, 'Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
	game_mth = init_game_date_string.split('/')[0]
	final_season_year = season_year
	if int(game_mth) > 9:
		final_season_year = str(int(season_year) - 1)
		
	date_str = game_row['Date'] + '/' + final_season_year #player_reg_season_log.loc[game_idx, 'Date'] + '/' + final_season_year # dow m/d/y
	date_data = date_str.split()
	date = date_data[1] # m/d/y
	#print('date: ' + date)

	opp_str = game_row['OPP']#player_reg_season_log.loc[game_idx, 'OPP']
	opp_abbrev = read_team_abbrev(opp_str) #re.sub('@|vs','',opp_str)

	game_key = ''
	if opp_abbrev != '': # maybe blank if exhibition game preseason
		# irregular_abbrevs = {'no':'nop', 'ny':'nyk', 'sa': 'sas', 'gs':'gsw' } # for these match the first 3 letters of team name instead
		# if opp_abbrev in irregular_abbrevs.keys():
		# 	opp_abbrev = irregular_abbrevs[opp_abbrev]
		#print('opp_abbrev: ' + opp_abbrev)

		# if we always use format 'away home m/d/y' then we can check to see if key exists and get game id from local file
		away_abbrev = opp_abbrev
		home_abbrev = team_abbrev
		#player_loc = 'home' # for box score players in game sort by teammates
		if re.search('@',opp_str):
			away_abbrev = team_abbrev
			home_abbrev = opp_abbrev
			#player_loc = 'away'
			
		
		#if away_abbrev != '' and home_abbrev != '':
		game_key = away_abbrev + ' ' + home_abbrev + ' ' + date
	
	#print('game_key: ' + game_key)
	return game_key



# find teammates and opponents for each game played by each player
# all_box_scores = {player:{game:{teammates:[],opponents:[]}}}
# OR
# all_box_scores = {year:{game:{away:{starters:[],bench:[]},home:starters:[],bench:[]}}
# use init_player_stat_dict to see saved stats
# init_player_stat_dicts = {player: {"2023": {"regular": {"pts": {"all": {"0": 14,...
def read_all_box_scores(all_players_season_logs, all_players_teams, season_years, season_part, cur_yr, read_new_game_ids=True):#, season_year=2024):
	print('\n===Read All Box Scores===\n')
	print('Setting: season years = ' + str(season_years))
	print('Setting: season part = ' + season_part)
	print('Setting: read new game ids = ' + str(read_new_game_ids))
	print('\nInput: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
	print('Input: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {\'GP\':69, \'MIN\':30}, ...')
	print('\nOutput: all_box_scores = {year:{game key:{away:{starters:{player:play time,...},bench:{...}},home:{...}},... = {\'2024\': {\'mem okc 12/18/2023\': {\'away\': {\'starters\': {\'J Jackson Jr PF\':30, ...}, \'bench\': {...}}, \'home\': ...\n')
	
	all_box_scores = {}
	init_all_box_scores = {}

	# 1 file per yr bc >1000 games per yr
	# could take yrs from season logs or separate input
	# what if first player only played 1 season from list of all possible?
	# then it fails so need to pass all season yrs for all players in list, not just whatever first player in list happened to play
	# season_years = list(list(all_players_season_logs.values())[0].keys())
	# print('season_years: ' + str(season_years))
	for year in season_years:
		box_scores_file = 'data/raw box scores - ' + year + '.json'
		init_year_box_scores = read_json(box_scores_file)
		#print('init_year_box_scores: ' + str(init_year_box_scores))
		init_all_box_scores[year] = init_year_box_scores

	#print('init_all_box_scores: ' + str(init_all_box_scores))
	# need all including not currently used to compare at end to see if needs to be overwritten
	all_box_scores = copy.deepcopy(init_all_box_scores)
	current_box_scores = {} # current of interest

	# {game key: game id,...}
	data_type = 'data/all games ids.csv' #'game ids'
	existing_game_ids_dict = extract_dict_from_data(data_type)



	for player, player_season_logs in all_players_season_logs.items():
		#print('\nplayer: ' + player)

		player_teams = all_players_teams[player]
		gp_cur_team = determiner.determine_gp_cur_team(player_teams, player_season_logs, cur_yr, player)

		for season_year, player_season_log in player_season_logs.items():

			# we read more seasons to get model but we only use limited seasons to get true prob???
			if season_year not in season_years:
				continue

			#print('\nyear: ' + year)
			if season_year not in all_box_scores.keys():
				all_box_scores[season_year] = {}
			if season_year not in current_box_scores.keys():
				current_box_scores[season_year] = {}

			# (teams_reg_and_playoff_games_played, season_part_game_log, teams, games_played)		
			season_games_played_data = determiner.determine_teams_reg_and_playoff_games_played(player_teams, player_season_log, season_part, season_year, cur_yr, gp_cur_team, player)
			teams_reg_and_playoff_games_played = season_games_played_data[0]
			season_part_game_log = season_games_played_data[1]
			teams = season_games_played_data[2]
			games_played = season_games_played_data[3]

			player_team_idx = 0

			try:

				# for reg season, idx starts after first playoff game
				for game_idx, row in season_part_game_log.iterrows():

					# determine player team for game
					player_team_idx = determiner.determine_player_team_idx(player, player_team_idx, game_idx, row, games_played, teams_reg_and_playoff_games_played)
					team_abbrev = ''
					if len(teams) > player_team_idx:
						team_abbrev = teams[player_team_idx]
					#print('team_abbrev: ' + team_abbrev)
						
					game_key = read_game_key(season_year, team_abbrev, row)

					# if game not saved then read from internet
					if game_key != '' and game_key not in all_box_scores[season_year].keys():

						game_espn_id = read_game_espn_id(game_key, existing_game_ids_dict, read_new_game_ids)
						# if returned no game id, then bc too many requests, so stop reading new ids
						# no bc could be any reason, so check error
						# if too many requests error, stop reading new ids
						if game_espn_id == 'HTTP Error 429: Too Many Requests':
						#if re.search('too many requests', game_espn_id.lower()): 
							read_new_game_ids = False
							continue

						if game_espn_id != '':
							game_box_scores_dict = read_game_box_scores(game_key, game_espn_id, read_new_game_ids=read_new_game_ids, player_name=player)
							
							# players_in_box_score_dict = {away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
							#players_in_box_score_dict = read_players_in_box_score(game_box_scores_dict)
						
							# may need to save player box scores if internet connection fails during read all box scores
							
							all_box_scores[season_year][game_key] = game_box_scores_dict#players_in_box_score_dict
						else:
							print('Warning: Blank Game ID! ' + game_key.upper())
					
					if game_key in all_box_scores[season_year].keys():
						current_box_scores[season_year][game_key] = all_box_scores[season_year][game_key]
				
					#break # test
			except Exception as e:
				print('Exception while reading all players in games: ', e)

	if not init_all_box_scores == all_box_scores:
		for year in season_years:
			year_box_scores = all_box_scores[year]
			box_scores_file = 'data/raw box scores - ' + year + '.json'
			writer.write_json_to_file(year_box_scores, box_scores_file)



	# all_box_scores = {game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
	#print('all_box_scores: ' + str(all_box_scores))
	return (all_box_scores, current_box_scores)

def read_game_info(game_key, init_game_ids_dict={}, game_id='', player='', read_new_game_ids=False):
	#print("\n===Read Game Info: " + game_key.upper() + ", " + player.title() + "===\n")

	game_info = {}

	if game_id == '':
		game_id = read_game_espn_id(game_key, init_game_ids_dict, read_new_game_ids)

	if game_id != '':
		#game_info['id'] = game_id
		# https://www.espn.com/nba/game/_/gameId/401585115/trail-blazers-mavericks
		url = 'https://www.espn.com/nba/game/_/gameId/' + game_id # not needed: + '/' + away_team + '-' + home_team
		soup = read_website(url)
		if soup is not None:

			# if one messes up, keep reading rest of games info
			tod = ''
			coverage = ''
			city = ''
			#audience = ''

			try:
			
				# 8:30 PM, January 5, 2024 -> 8:30
				meta_game_info = list(soup.find('div', {'class':'GameInfo__Meta'}).findChildren())
				# [<span>8:00 PM<!-- -->, <!-- -->January 5, 2024</span>, '8:00 PM', ' ', ', ', ' ', 'January 5, 2024']
				#print('meta_game_info: ' + str(meta_game_info))
				# <span>8:00 PM<!-- -->, <!-- -->January 5, 2024</span>
				tod = str(meta_game_info[0])
				#print('tod: ' + tod)
				# remove all tags
				tod = re.sub(r'</?[a-z]+(\s[a-z]+=".+")?>|<!--\s-->','',tod)
				#tod = re.sub(r'<!--\s-->','',tod)
				# remove only end tags
				#tod = re.sub(r'^<[a-z]+>|</[a-z]+>$','',tod)
				#print('tod: ' + tod)
				# 8:30 PM
				tod = tod.split(',')[0]
				#print('tod: ' + tod)
				# always play in PM so remove pm
				tod = re.sub('\s[A-Z]+$','',tod)
				#print('tod: ' + tod)

				# doesnt matter which channel, just as long as national coverage
				coverage = 'local'
				if len(meta_game_info) > 1:
					coverage = 'national'
					# coverage = str(meta_game_info[1])
					# print('coverage: ' + coverage)
					# coverage = re.sub(r'</?[a-z]+(\s[a-z]+=".+")?>|<!--\s-->','',coverage)
				#print('coverage: ' + coverage)

				city = str(soup.find('span', {'class':'Location__Text'}))
				#print('city: ' + city)
				# remove tags
				city = re.sub(r'</?[a-z]+(\s[a-z]+=".+")?>|<!--\s-->|,','',city).strip()#.lower()
				#print('city: ' + city)
				
				# CAPACITY: 19,200 -> 19200
				#audience = str(soup.find('div', {'class':'Attendance__Capacity'}))
				#print('audience: ' + audience)
				# remove tags
				#audience = re.sub(r'</?[a-z]+(\s[a-z]+=".+")?>|<!--\s-->|,','',audience)
				#print('audience: ' + audience)
				
				# audience_data = audience.split(':')
				# if len(audience_data) > 1:
				# 	audience = audience_data[1].strip()

				# 	# round to the nearest 1000
				# 	audience = str(int(converter.round_half_up(int(audience), -3)))
				# else:
				# 	audience = ''
				# 	print('Warning: Blank audience info! ' + audience)
				#print('audience: ' + audience)
				# audience = re.sub(',','',audience)
				# print('audience: ' + audience)
				
				#print('audience: ' + audience)

				game_info = {'id':game_id, 'tod':tod, 'coverage':coverage, 'city':city}#, 'audience':audience}
			
			except Exception as e:
				print('Warning: Exception while reading game info! ' + str(e) + ', ' + game_key + ', ' + player.title())
				print('tod: ' + tod)
				print('coverage: ' + coverage)
				print('city: ' + city)
				#print('audience: ' + audience)
	else:
		print('Warning: Blank game id! ' + game_key)

	#print('game_info: ' + str(game_info))
	return game_info

def read_all_games_info(all_players_season_logs, all_players_teams, init_game_ids_dict, season_part, read_new_game_ids, cur_yr='', season_years=[]):
	print("\n===Read All Games Info===\n")
	print('Input: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...')
	print('\nOutput: all_games_info = {year:{game key:{city:c, time of day:tod, audience:a, ...\n')

	#all_games_info = {}

	all_games_info_file = 'data/all games info.json'
	init_all_games_info = read_json(all_games_info_file)
	#print("init_all_players_teams: " + str(init_all_players_teams))
	all_games_info = copy.deepcopy(init_all_games_info)

	if init_game_ids_dict == '':
		# {game key: game id,...}
		data_type = 'data/all games ids.csv' #'game ids'
		init_game_ids_dict = extract_dict_from_data(data_type)

	# read all games info or just season part of interest?
	# more efficient to ignore unused game info
	#season_part = 'full'

	for player, player_season_logs in all_players_season_logs.items():
		#print('\nplayer: ' + player)
		player_teams = all_players_teams[player]
		gp_cur_team = determiner.determine_gp_cur_team(player_teams, player_season_logs, cur_yr, player)

		for season_year, player_season_log in player_season_logs.items():
		# for season_year in range(cur_yr, final_yr+1):
		# 	player_season_log = player_season_logs[season_year]
			if season_year not in season_years:
				continue


			#print('\nseason_year: ' + season_year)
			if season_year not in all_games_info.keys():
				all_games_info[season_year] = {}


			
			season_games_played_data = determiner.determine_teams_reg_and_playoff_games_played(player_teams, player_season_log, season_part, season_year, cur_yr, gp_cur_team, player)
			teams_reg_and_playoff_games_played = season_games_played_data[0]
			season_part_game_log = season_games_played_data[1]
			teams = season_games_played_data[2]
			games_played = season_games_played_data[3]

			player_team_idx = 0

			# if we add try then it fails quietly and requires searching to see error
			# but if we cancel for some reason then it will save the file before quitting
			# is that what we want? yes bc if not then after long loading all work will be lost if error
			# then need to be careful to notice exceptions
			try:

				# for reg season, idx starts after first playoff game
				for game_idx, row in season_part_game_log.iterrows():
					#player_team = determiner.determine_player_team(row)

					# determine player team for game
					player_team_idx = determiner.determine_player_team_idx(player, player_team_idx, game_idx, row, games_played, teams_reg_and_playoff_games_played)
					team_abbrev = ''
					if len(teams) > player_team_idx:
						team_abbrev = teams[player_team_idx]
					#print('team_abbrev: ' + team_abbrev)
						
					game_key = read_game_key(season_year, team_abbrev, row)

					# if game not saved then read from internet
					if game_key != '' and game_key not in all_games_info[season_year].keys():

						game_espn_id = read_game_espn_id(game_key, init_game_ids_dict, read_new_game_ids)
						# if returned no game id, then bc too many requests, so stop reading new ids
						# no bc could be any reason, so check error
						# if too many requests error, stop reading new ids
						if game_espn_id == 'HTTP Error 429: Too Many Requests':
						#if re.search('too many requests', game_espn_id.lower()): 
							read_new_game_ids = False
							continue

						if game_espn_id != '':
							game_info = read_game_info(game_key, init_game_ids_dict, game_espn_id, player, read_new_game_ids)
							all_games_info[season_year][game_key] = game_info
						else:
							print('Warning: Blank Game ID! ' + game_key.upper())

			except Exception as e:
				print('Exception while reading all games info: ', e)

	if not init_all_games_info == all_games_info:
		writer.write_json_to_file(all_games_info, all_games_info_file)

	#print('all_games_info: ' + str(all_games_info))
	return all_games_info

# get player position from espn game log page bc we already have urls for each player
def read_player_position(player_name, player_id, init_all_players_positions={}):
	#print("\n===Read Player Position: " + player_name.title() + "===\n")
	position = ''

	# if not given exisiting positions see if local file saved
	if len(init_all_players_positions.keys()) == 0:
		data_type = 'player positions'
		player_positions = extract_data(data_type, header=True)
		
		for row in player_positions:
			#print('row: ' + str(row))
			player_name = row[0]
			player_position = row[1]

			init_all_players_positions[player_name] = player_position
		#print('init_all_players_positions: ' + str(init_all_players_positions))

	if player_name in init_all_players_positions.keys():
		position = init_all_players_positions[player_name]

	else:

		#try:
			
		# should not need yr bc only shows current position on player page
		position_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id# + '/type/nba/year/' + str(season_year)
		#print('position_url: ' + position_url)

		soup = read_website(position_url)

		if soup is not None:
			# find last element of ul with class PlayerHeader__Team_Info
			position = str(list(soup.find("ul", {"class": "PlayerHeader__Team_Info"}).descendants)[-1])
			#print("position_element:\n" + str(position_element))
			#print('position: ' + position)

			# eg point guard -> pg
			if len(position) > 2: # use abbrev
				pos_abbrev = ''
				words = position.split()
				for word in words:
					pos_abbrev += word[0].lower()

				if pos_abbrev == 'f': # some just say forward so make it small forward but actually better to use height to determine bc if over 6'6 then pf maybe?
					pos_abbrev = 'sf'
				elif pos_abbrev == 'g':
					pos_abbrev = 'sg'
				position = pos_abbrev

			#print('Success', position.upper(), player_name.title())


			data = [[player_name, position]]
			filepath = 'data/Player Positions.csv'
			write_param = 'a' # append ids to file
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet
		else:
			print('Warning: website has no soup!')
		#except Exception as e:
			#print('Error', position.upper(), player_name.title())

	#print("position: " + position)
	return position

def read_all_players_positions(players_names, all_players_espn_ids):
	print("\n===Read All Players Positions===\n")
	print('Input: all_players_espn_ids = {player:id, ...} = {\'jalen brunson\': \'3934672\', ...}')
	print('\nOutput: all_players_positions = {player:position, ...} = {\'jalen brunson\': \'pg\', ...}')

	all_players_positions = {}

	# see if position saved in file
	data_type = 'player positions'
	player_positions = extract_data(data_type, header=True)
	init_all_players_positions = {}
	for row in player_positions:
		#print('row: ' + str(row))
		player_name = row[0]
		player_position = row[1]

		init_all_players_positions[player_name] = player_position
	#print('init_all_players_positions: ' + str(init_all_players_positions))

	# not all espn ids bc need all ids for teammates and opps
	# but only need pos for player of interest? 
	# here yes bc we can get pos of teams from box scores
	#for name, id in all_players_espn_ids.items():
	for name in players_names:
		id = all_players_espn_ids[name]
		pos = read_player_position(name, id, init_all_players_positions)
		all_players_positions[name] = pos

	#print("all_players_positions: " + str(all_players_positions))
	return all_players_positions

# get game log from espn.com
# not using all game logs anymore bc too slow to store all game logs in 1 file and search whole file each time
# instead use player game logs
def read_player_season_log(player_name, season_year=2024, player_url='', player_id='', all_game_logs={}, todays_date=datetime.today().strftime('%m-%d-%y'), player_game_logs={}, all_seasons_start_days={}):
	#print('\n===Read Player Season Log: ' + player_name.title() + ', ' + str(season_year) + '===\n')

	player_game_log_df = pd.DataFrame()
	player_game_log_dict = {}

	season_start_day = all_seasons_start_days[str(season_year)]
	#print('season_start_day: ' + str(season_start_day))

	# much faster to save in one file
	# print('Try to find local game logs for ' + str(season_year))
	# all_game_logs = read_json(all_logs_filename)
	#print('all_game_logs:\n' + str(all_game_logs))
	try:
		# if storing every players logs in 1 big file
		if player_name in all_game_logs.keys() and str(season_year) in all_game_logs[player_name].keys():
			
			player_game_log_dict = all_game_logs[player_name][str(season_year)]
			#print('local player_game_log_dict:\n' + str(player_game_log_dict))
			#print('found local game log for player ' + player_name + ' in ALL game logs')
		# if storing 1 player's logs in a file
		elif str(season_year) in player_game_logs.keys():
			player_game_log_dict = player_game_logs[str(season_year)]
			#print('local player_game_log_dict:\n' + str(player_game_log_dict))
			#print('found local game log for player ' + player_name + ' in PLAYER game logs')
		else:
			# if player in logs but season not then maybe we only ran for 1 season so check if season is on web


		# see if saved locally
		#todays_date = datetime.today().strftime('%m-%d-%y') 
		# data/lamelo ball 2024 game log 11-08-23.csv
		# log_filename = 'data/game logs/' + player_name + ' ' + str(season_year) + ' game log ' + todays_date + '.csv'
		# print('log_filename: ' + log_filename)
		
		# try:
		# 	print('Try to find local game log for ' + player_name.title())
		# 	player_game_log_df = pd.read_csv(log_filename)
		# 	#print('local player_game_log_df:\n' + str(player_game_log_df))

		# except:


			#print('Could not find local game log, so read from web.')
			# get espn player id from google so we can get url
			if player_url == '':
				if player_id == '':
					player_id = read_player_espn_id(player_name)
				#season_year = 2023
				player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
				#print("player_url: " + player_url)

			#player_game_log = []
			#dfs = pd.read_html(player_url)
			#print(f'Total tables: {len(dfs)}')

			#try:

			# returns list_of_dataframes
			html_results = read_web_data(player_url) #pd.read_html(player_url)
			#print("html_results: " + str(html_results))

			if html_results is not None:
				#print('found html results while reading season log')

				parts_of_season = [] # pre season, regular season, post season

				len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table
				#print('len_html_results: ' + str(len_html_results))
				for order in range(len_html_results):
					#print("order: " + str(order))

					# see if we can find header to differntiate preseason and regseason
					# what if only 1 table is preseason?
					# what if only 1 table is reg or postseason?
					#print('html_results[order]: ' + str(html_results[order]))

					# need to get date player switched teams if traded
					# first game on new team so we can see if game key date on or after that date
					# or we can get last game on old team so we can see if game date after that date
					# add team as column in game log

					#date_team_change = ''

					if len(html_results[order].columns.tolist()) == 17:

						part_of_season = html_results[order]
						#print('\npart_of_season:\n' + str(part_of_season))

						# look at the formatting to figure out how to separate table and elements in table
						# when only preseason, len html results = 2
						# when only reg season, also 2
						# so need date: if before season_start_date=m/d=10/10, then preseason
						# len=4 does not work for unknown reason
						preseason = False
						if len_html_results - 2 == order and len_html_results > 4: # 3 or more should work but check if invalid for any players bc 4 or more means they did not play preseason but does not account for if they played postseason
							part_of_season['Type'] = 'Preseason'
							preseason = True

						# what if len only 3 bc missed preseason? check that games are in october
						#elif len_html_results == 3 and order == 1:
						elif len_html_results < 4 and order == len_html_results - 2:
							# check that games are in october
							# get latest game
							last_game_date = part_of_season.iloc[0,0]
							#print('last_game_date: ' + str(last_game_date)) # Thu 10/19
							# get month num
							last_game_date_data = last_game_date.split()[1].split('/')
							last_game_mth_num = int(last_game_date_data[0])
							#print('last_game_mth_num: ' + str(last_game_mth_num))
							last_game_day_num = int(last_game_date_data[1])
							#print('last_game_day_num: ' + str(last_game_day_num))
							if last_game_mth_num == 10 and last_game_day_num < season_start_day:
								#print('Preseason')
								part_of_season['Type'] = 'Preseason'
								preseason = True

						# elif len_html_results == 2 and order == 0:
						# 	# check that games are in october
						# 	# get latest game
						# 	last_game_date = part_of_season.iloc[0,0]
						# 	print('last_game_date: ' + str(last_game_date)) # Thu 10/19
						# 	# get month num
						# 	last_game_mth_num = int(last_game_date.split()[1].split('/')[0])
						# 	print('last_game_mth_num: ' + str(last_game_mth_num))
						# 	if last_game_mth_num == 10:
						# 		print('Preseason')
						# 		part_of_season['Type'] = 'Preseason'

						if not preseason:
							# last row of postseason section has 'finals' in it, eg quarter finals, semi finals, finals
							last_cell = part_of_season.iloc[-1,0]
							#print('last_cell: ' + str(last_cell))
							if re.search('final',last_cell.lower()) or re.search('play-in',last_cell.lower()):
								part_of_season['Type'] = 'Postseason'
							# if len(part_of_season[(part_of_season['OPP'].str.contains('GAME'))]) > 0:
							# 	part_of_season['Type'] = 'Postseason'
							# elif re.search('play-in',last_cell.lower()):
							# 	part_of_season['Type'] = 'Playin'
							else:
								# cannot assign type to whole subsection bc mixed in with in-season tournament
								# only game that doesnt count is champ so look for label below row: 'championship'
								# row 2: game stats
								# row 3: ...CHAMPIONSHIP
								# so row 2 is type=post
								part_of_season['Type'] = 'Regular'

						parts_of_season.append(part_of_season)

					else:
						#print("Warning: table does not have 17 columns so it is not valid game log.")
						pass

				for part_of_season in parts_of_season:
					# cannot assign type to whole subsection bc mixed in with in-season tournament
					# only game that doesnt count is champ so look for label below row: 'championship'
					# row 2: game stats
					# row 3: ...CHAMPIONSHIP
					# so row 2 is type=post
					#print('part_of_season before: ' + str(part_of_season))
					for game_idx, row in part_of_season.iterrows():
						#print('game_idx: ' + str(game_idx))
						#print('row before:\n' + str(row))
						# last_cell = part_of_season.iloc[-1,0]
						# list from recent to distant so next row shows label for current game
						next_idx = game_idx + 1
						if len(part_of_season.index) > next_idx:
							next_row = part_of_season.iloc[next_idx,0] # could use any field in label row
							#print('next_row: ' + str(next_row))
							if re.search('championship',next_row.lower()):
								#print('found champ label')
								row['Type'] = 'Tournament'

								#print('row after:\n' + str(row))

					#print('part_of_season after: ' + str(part_of_season))

				if len(parts_of_season) > 0:

					player_game_log_df = pd.concat(parts_of_season, sort=False, ignore_index=True)

					player_game_log_df = player_game_log_df[(player_game_log_df['OPP'].str.startswith('@')) | (player_game_log_df['OPP'].str.startswith('vs'))].reset_index(drop=True)

					player_game_log_df['Season'] = str(season_year-1) + '-' + str(season_year-2000)

					player_game_log_df['Player'] = player_name

					# if game date after last game on old team, then new team?
					#game_date = player_game_log_df['Date']
					#player_game_log_df['Team'] = player_team

					player_game_log_df = player_game_log_df.set_index(['Player', 'Season', 'Type']).reset_index()

					# Successful 3P Attempts
					player_game_log_df['3PT_SA'] = player_game_log_df['3PT'].str.split('-').str[0]

					# All 3P Attempts
					player_game_log_df['3PT_A'] = player_game_log_df['3PT'].str.split('-').str[1]

					player_game_log_df[
						['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']
						] = player_game_log_df[
							['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']
							].astype(float)

				# display player game log in readable format
				#pd.set_option('display.max_columns', 100)
				pd.set_option('display.max_columns', None)
				#print("player_game_log_df before reset index:\n" + str(player_game_log_df))

				# save each game log to a file
				# filename: <player> <season> game log <todays d/m/y>
				# we put todays date so we can see if already read today
				# bc if not read today then read new 
				# index=False: means that the index of the DataFrame will not be included in the CSV file.
				
				#player_game_log_df.to_csv(log_filename, index=False)
				# append game log to existing days file if possible
				# if first run of the day, then write new file with days date
				# see other instances of write to json
				# all_game_logs = all_game_logs
				# writer.write_json_to_file(all_game_logs, all_l)
				player_game_log_df = player_game_log_df.reset_index(drop=True)
				#print("player_game_log_df after reset index:\n" + str(player_game_log_df))
				init_player_game_log_dict = player_game_log_df.to_dict()
				# change id ints to strings to compare to json
				#print('change keys to strings')
				for field, field_dict in init_player_game_log_dict.items():
					player_game_log_dict[field] = {}
					for key, val in field_dict.items():
						player_game_log_dict[field][str(key)] = val

			# except Exception as e:
			# 	print("Error reading game log " + str(e))
			# 	pass

		# if we want to format table in 1 window we can get df elements in lists and then print lists in table
		# header_row = ['Date', 'OPP', 'Result', 'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS']

		# table = [header_row]
		# for row in player_game_data:
		# 	table.append(row)
	except Exception as e:
		print('Warning: Error getting game log! ', e)

	# add player team to game log bc it could change any game if they get traded midseason
	# for game_idx, row in player_game_log_df.iterrows():
	# 	row['Team'] = player_team

	# print("\n===" + player_name + "===\n")
	# print(tabulate(table))
	#print(player_name + " player_game_log returned")# + str(player_game_log_df))
	#print('player_game_log_df:\n' + str(player_game_log_df))
	#print('player_game_log_dict: ' + str(player_game_log_dict))
	return player_game_log_dict#player_game_log_df # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword


# here we decide default season year, so make input variable parameter
def read_player_season_logs(player_name, current_year_str, todays_date, player_espn_id='', read_x_seasons=1, all_players_espn_ids={}, season_year=2024, all_game_logs={}, player_teams={}, all_seasons_start_days={}):
	#print('\n===Read Player Season Logs: ' + player_name.title() + '===\n')

	player_name = player_name.lower()

	

	# see if saved season logs for player
	# need to separate current season from prev seasons bc only cur seas changes
	# get current season which changes after new game
	#player_game_logs_filename = 'data/game logs/' + player_name + ' game logs ' + todays_date + '.json'
	# always current yr bc no matter what yr of interest only current yr changes with each new game
	if current_year_str == '':
		current_year_str = determiner.determine_current_season_year() #str(datetime.today().year)
	player_cur_season_log_filename = 'data/game logs/cur/' + player_name + ' ' + current_year_str + ' game log ' + todays_date + '.json'
	#print('player_cur_season_log_filename: ' + player_cur_season_log_filename)
	# print('Try to find local CURRENT season game log for ' + player_name + '.')
	# # init_player_cur_season_log = {'PTS':[],...}
	# init_player_cur_season_log = read_json(player_cur_season_log_filename)
	#print('init_player_cur_season_log: ' + str(init_player_cur_season_log))

	# look for same name but different date
	#yestergame_season_log_filename = 'data/game logs/' + player_name + ' ' + current_year_str + ' game log ' + prev_game_date + '.json'
	

	# get prev seasons unchanged
	# before only if it was matching todays date would it be filled
	# but now prev logs is unchanged so it will be refilled if ever filled before
	player_prev_logs_filename = 'data/game logs/prev/' + player_name + ' prev logs.json'
	#print('player_prev_logs_filename: ' + player_prev_logs_filename)
	# # init_player_prev_logs = {'year':{'PTS':[],...},...}
	# need to copy init game logs bc this run may not have all players but we dont want to remove other players

	# combine cur log and prev logs into player game logs
	# OR init new dict and set vals from old dict
	# need to copy init game logs bc this run may not have all players but we dont want to remove other players
	# we must compare init to final logs to see if changed then write to file
	# now player game logs could have prev logs but not cur yr log
	init_player_game_logs = read_cur_and_prev_json(player_cur_season_log_filename,player_prev_logs_filename)
	#print('init_player_game_logs: ' + str(init_player_game_logs))
	player_game_logs = copy.deepcopy(init_player_game_logs) # season logs for a player
	

	#player_game_logs = []
	player_season_logs = {}

	if player_espn_id == '':
		if len(all_players_espn_ids.keys()) == 0:
			player_espn_id = read_player_espn_id(player_name)
		else:
			player_espn_id = all_players_espn_ids[player_name]

		if player_espn_id == '':
			print('Warning: player_espn_id blank while trying to get player url! ')
		
	#season_year = 2023 # here we decide default season year, so make input variable parameter
	player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
	
	try:
	
		if read_x_seasons == 0:
			while determiner.determine_played_season(player_url, player_name, season_year, all_game_logs, player_game_logs, player_teams):

				#print("player_url: " + player_url)
				game_log_dict = read_player_season_log(player_name, season_year, player_url, all_seasons_start_days=all_seasons_start_days, all_game_logs=all_game_logs, todays_date=todays_date, player_game_logs=player_game_logs)
				player_season_logs[str(season_year)] = game_log_dict
				# if not game_log_df.empty:
				# 	player_game_logs.append(game_log_df)
				# 	player_season_logs[season_year] = game_log_df.to_dict()

				# if not read_all_seasons:
				# 	break

				player_game_logs[str(season_year)] = game_log_dict # includes all players saved before not just players input this run



			# need to go to next season even if player did not player season
			season_year -= 1
			player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])

		for season_idx in range(read_x_seasons):
			if determiner.determine_played_season(player_url, player_name, season_year, all_game_logs, player_game_logs, player_teams):

				#print("player_url: " + player_url)
				game_log_dict = read_player_season_log(player_name, season_year, player_url, all_seasons_start_days=all_seasons_start_days, all_game_logs=all_game_logs, todays_date=todays_date, player_game_logs=player_game_logs)
				player_season_logs[str(season_year)] = game_log_dict
				# if not game_log_df.empty:
				# 	player_game_logs.append(game_log_df)
				# 	player_season_logs[season_year] = game_log_df.to_dict()

				player_game_logs[str(season_year)] = game_log_dict # includes all players saved before not just players input this run



			# need to go to next season even if player did not player season
			season_year -= 1
			player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year)
			# after we reach season they did not play it is possible they may have played before but taken break
			# so keep checking prev 5 years before breaking
			# else:
			# 	break
	except Exception as e:
		print('Exception while reading game logs: ', e)
	
	
	#print('final player_game_logs: ' + str(player_game_logs))
	if not init_player_game_logs == player_game_logs:
		writer.write_cur_and_prev(init_player_game_logs, player_game_logs, player_cur_season_log_filename, player_prev_logs_filename, current_year_str, player_name, todays_date, data_type='game logs')


	#print('player_season_logs: ' + str(player_season_logs))
	return player_season_logs#player_game_logs

def read_all_players_season_logs(players_names, cur_yr, todays_date, all_players_espn_ids={}, all_players_teams={}, read_x_seasons=1, season_year=2024, game_teams=[], rosters={}):
	print('\n===Read All Players Season Logs===\n')
	print('Settings: read x seasons prev, init year of interest')
	print('\nInput: players_names = [p1, ...] = [\'jalen brunson\', ...]')# + str(players_names))
	print('Input: all_players_espn_ids = {player:id, ...} = {\'jalen brunson\': \'3934672\', ...}')
	print('Input: all_players_teams = {player:{year:{team:{gp:gp, min:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {GP:69, MIN:30}, ...')
	print('\nOutput: all_players_season_logs = {player:{year:{stat name:{game idx:stat val, ... = {\'jalen brunson\': {\'2024\': {\'Player\': {\'0\': \'jalen brunson\', ...\n')

	all_players_season_logs = {}

	all_seasons_start_days = {'2024':24, '2023':18, '2022':19}

	# much faster to save in one file
	# but too large for single variable in memory?
	# todays_date = datetime.today().strftime('%m-%d-%y') 
	# all_logs_filename = 'data/game logs/all game logs ' + todays_date + '.json'
	# print('all_logs_filename: ' + all_logs_filename)
	# print('Try to find local game logs for all games.')
	# init_all_game_logs = read_json(all_logs_filename)
	# print('init_all_game_logs: ' + str(init_all_game_logs))
	# need to copy init game logs bc this run may not have all players but we dont want to remove other players
	#all_game_logs = {}#copy.deepcopy(init_all_game_logs)

	# needed bc only current season changes and cur yr does not always equal cur season yr. depends on mth
	if cur_yr == '':
		cur_yr = determiner.determine_current_season_year()
	
	# given players of interest
	# get all teams theyre on
	# and get all logs from all 
	# if given game teams, we can simply get players on game teams
	if len(game_teams) > 0:
		players_names = []
		for game in game_teams:
			for team in game:
				team_roster = rosters[team]
				for player in team_roster:
					players_names.append(player)

	for player_name in players_names:
		# {player:season:log}
		if player_name in all_players_teams.keys():
			player_teams = all_players_teams[player_name]
			player_espn_id = all_players_espn_ids[player_name]
			players_season_logs = read_player_season_logs(player_name, cur_yr, todays_date, player_espn_id, read_x_seasons, all_players_espn_ids, season_year, all_players_season_logs, player_teams, all_seasons_start_days)
			
			all_players_season_logs[player_name] = players_season_logs

			# if log is already in file no need to overwrite but the output will be the same as all game logs so it makes no difference
			#all_game_logs[player_name] = players_season_logs # {player:season:log}

			# write for each player is if error interrupts it can resume where it left off
			# if all game logs unchanged then no need to write to file
	
	#init_all_game_logs: {'bruce brown': {'2023': {'Player': {'0': 
	#final_all_game_logs: {'bruce brown': {2023: {'Player': {'0': 'br
	#print('all_players_season_logs: ' + str(all_players_season_logs))
	return all_players_season_logs

# return team abbrev lowercase bc used as key
# if we are reading team from internet then we know read new teams is set true?
# yes if we initially read all years, not just input seasons yrs
def read_team_from_internet(player_name, player_id, read_new_teams=False, cur_yr=''):
	#print("\n===Read Team from Internet: " + player_name.title() + "===\n")

	team = ''

	# get team from internet
	# this method only works for current team bc format of page
	if cur_yr == '':
		cur_yr = determiner.determine_current_season_year()
		#season_year = datetime.today().year

	#try:
		
	site = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id + '/type/nba/year/' + cur_yr

	soup = read_website(site, timeout=10, max_retries=3)

		# req = Request(site, headers={
		# 	'User-Agent': 'Mozilla/5.0',
		# })

		# page = urlopen(req) # open webpage given request

		# soup = BeautifulSoup(page, features="lxml")
	if soup is not None:
		# find last element of ul with class PlayerHeader__Team_Info
		team = str(list(soup.find("ul", {"class": "PlayerHeader__Team_Info"}).descendants)[0]).strip()#.split('<')[0]#.split('>')[-1]
		#print("team_element:\n" + str(team))
		
		#<li class="truncate min-w-0"><a class="AnchorLink clr-black" data-clubhouse-uid="s:40~l:46~t:21" href="https://www.espn.com/nba/team/_/name/phx/phoenix-suns" tabindex="0">Phoenix Suns</a></li>

		team = re.split('</',str(team))[0]
		team = re.split('>',team)[-1]
		#print("team: " + team)
		team = determiner.determine_team_abbrev(team)

		#print('Success', team.upper(), player_name.title())

		# overwrite for the first player if read new teams true and then append all after
		# if read_new_teams: # make blank initially and then append all names after that
		# 	# overwrite file
		# 	write_param = 'w'

		# we are reading from the internet so we are definitely going to write the data to a file no matter what so we can access it later
		# the question is if we are going to append or overwrite
		# if we are going to overwrite then we must wait till we have all teams so we only overwrite first entry and append all after
		# if not all new teams then simply append this player's team to the file
		if not read_new_teams:
			write_param = 'a' # append ids to file unless read new teams
			data = [[player_name, team]]
			filepath = 'data/Player Teams.csv'
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

	#except Exception as e:
		#print('Error', team.upper(), player_name.title(), e)

	#print("team from internet: " + team)
	return team

# get player team from espn game log page bc we already have urls for each player
# we are using it get the team the player currently plays on
# but we can also use it to get the team a player previously played on but that uses a very different method from a different source so assume season year is current season
# read_new_teams false by default bc if it does not find existing team it will find on web
# the difference is read new teams will always read new teams even if team already saved locally and unchanged
# user will set input var after trades or aquisitions
# later program will get news and decide off that instead of requiring user input
def read_player_team(player_name, player_id, existing_player_teams_dict={}, read_new_teams=False, cur_yr=''):
	#print("\n===Read Player Team: " + player_name.title() + "===\n")
	team = '' # team abbrev lowercase bc used as key

	# read_new_teams can be determined by date bc date of trade deadline, start of season and check if any other trade deadlines
	if cur_yr == '':
		cur_yr = determiner.determine_current_season_year()

	# if not given exisiting teams see if local file saved
	if len(existing_player_teams_dict.keys()) == 0:
		data_type = 'player teams'
		player_teams = extract_data(data_type, header=True)
		
		for row in player_teams:
			#print('row: ' + str(row))
			existing_player_name = row[0]
			existing_player_team = row[1]

			existing_player_teams_dict[existing_player_name] = existing_player_team
		
	#print('existing_player_teams_dict: ' + str(existing_player_teams_dict))

	# changed from csv old version to json to save all teams all yrs
	if len(existing_player_teams_dict.keys()) == 0:
		file = 'data/all players teams.json'
		player_teams = read_json(file)

		#print('init player_teams: ' + str(player_teams))



	# if read new teams, then read from internet for all
	# if not read new teams, still read teams from internet for players not saved
	if read_new_teams:
		team = read_team_from_internet(player_name, player_id, read_new_teams, cur_yr)
	else:
		if player_name in existing_player_teams_dict.keys():
			team = list(existing_player_teams_dict[player_name][cur_yr].keys())[-1]
		else:
			team = read_team_from_internet(player_name, player_id, read_new_teams, cur_yr)

	
	#print("final team: " + team)
	return team

# return team abbrevs lowercase bc used as key
# if we are reading team from internet then we know read new teams is set true?
# yes if we initially read all years, not just input seasons yrs
# read all players teams from career stats page
# https://www.espn.com/nba/player/stats/_/id/6442/kyrie-irving
# teams = {year:{team:gp,...},...}
# here we read all teams from stats page bc if player was not traded midseason then game log does not say team that yr
# easier to read once for each player and update when read new teams
# rather than get team from each box score
def read_teams_from_internet(player_name, player_id):
	#print("\n===Read Teams from Internet: " + player_name.title() + "===\n")

	teams = {}

	url = 'https://www.espn.com/nba/player/stats/_/id/' + player_id + '/' + re.sub(' ','-',player_name)

	web_data = read_web_data(url)
	#print("web_data:\n" + str(web_data))
	# which table shows stats? should be only table on page
	# for order in range(len(web_data)):

	# 	web_df = web_data[order]
	# 	print('\nweb_df:\n' + str(web_df))

	if web_data is not None and len(web_data) > 1: # found table
		# df.drop(df.tail(n).index,inplace=True) # drop last n rows
		team_years_df = web_data[0]
		# drop last row bc career stats not 1 yr
		team_years_df.drop(team_years_df.tail(1).index, inplace=True)
		#print('\nteam_years_df:\n' + str(team_years_df))
		raw_years = team_years_df.loc[:,'season'].tolist() # 2023-24
		raw_teams = team_years_df.loc[:,'Team'].tolist()
		stats_df = web_data[1]
		stats_df.drop(stats_df.tail(1).index, inplace=True)
		#print('\nstats_df:\n' + str(stats_df))
		gp_key = 'GP'
		min_key = 'MIN'
		raw_gp = stats_df.loc[:,gp_key].tolist() # games played
		raw_min = stats_df.loc[:,min_key].tolist() # games played

		# if repeat same year that means 2 teams in same year
		# so need games played to tell which games in log were on which team

		for stat_idx in range(len(raw_years)):
			year = converter.convert_span_to_season(raw_years[stat_idx]) # from 2023-24 to 2024
			team = converter.convert_irregular_team_abbrev(raw_teams[stat_idx]) # convert irregular abbrevs

			gp = raw_gp[stat_idx]
			min = raw_min[stat_idx]

			if year not in teams.keys():
				teams[year] = {}
			if team not in teams[year].keys():
				teams[year][team] = {}

			teams[year][team][gp_key] = gp
			teams[year][team][min_key] = min

	#print('teams: ' + str(teams))
	return teams

def read_player_teams(player_name, player_id, read_new_teams=False, init_all_players_teams={}):
	#print('\n===Read Player Teams: ' + player_name.title() + '===\n')

	# bc if read new teams then no need to read saved teams?
	# no, we still need to read prev teams saved, and only get new team from internet
	# but they all come from same page so it saves no time
	if read_new_teams:
		#print('READ NEW TEAMS')
		player_teams = read_teams_from_internet(player_name, player_id)

	else:
		if player_name in init_all_players_teams.keys():
			player_teams = init_all_players_teams[player_name]
		else:
			player_teams = read_teams_from_internet(player_name, player_id)

	#print("player_teams: " + str(player_teams))
	return player_teams

# for all given players, read their teams for all years
# all_players_teams = {player:{year:{team:gp,...},...}}
# read all players teams from career stats page
# https://www.espn.com/nba/player/stats/_/id/6442/kyrie-irving
# only need to read new teams after trades but we dont have alerts for trades 
# so cant assume no new teams but also rare enough to keep off until manually alerted or feature added
# here we read all teams from stats page bc if player was not traded midseason then game log does not say team that yr
# we actually need all current players played with/against to get condition data
# how do we know the players relevant? 
# all in box scores for this player, and all in current lineup
# we could wait to read players teams until we encounter them in a game or lineup
# and then save to file if not already
def read_all_players_teams(players_names, all_players_espn_ids, read_new_teams=False, find_players=False):
	print("\n===Read All Players Teams===\n")
	print('Input: all_players_espn_ids = {player:id, ...} = {\'jalen brunson\': \'3934672\', ...}')
	print('\nOutput: all_players_teams = {player:{year:{team:{GP:gp, MIN:min},... = {\'bam adebayo\': {\'2018\': {\'mia\': {\'GP\':69, \'MIN\':30.2}, ...\n')

	all_players_teams_file = 'data/all players teams.json'

	init_all_players_teams = read_json(all_players_teams_file)
	#print("init_all_players_teams: " + str(init_all_players_teams))

	all_players_teams = copy.deepcopy(init_all_players_teams) # need to init as saved teams so we can see difference at end

	try:
		#for player_name, player_id in all_players_espn_ids.items():
		if find_players:
			players_names = all_players_espn_ids.keys()
		#print('players_names: ' + str(players_names))
		for player_name in players_names:
			#print('\nplayer_name: ' + str(player_name))
			# read player teams
			player_id = all_players_espn_ids[player_name]
			player_teams = read_player_teams(player_name, player_id, read_new_teams, init_all_players_teams)
			#print('player_teams: ' + str(player_teams))
			# teams = {year:team,...}
			#print("player_teams: " + str(player_teams))
			all_players_teams[player_name] = player_teams

	except Exception as e:
		print('Exception while reading all players teams: ', e)

	# need to add to file after each player bc if hangs halfway through then will lose all work
	# or if that is too inefficient then make sure never hangs
	# by retrying same player if hit cancel instead of skipping player
	if not init_all_players_teams == all_players_teams:
		writer.write_json_to_file(all_players_teams, all_players_teams_file)

	# all_players_teams = {player:{year:{team:gp,...},...}}
	#print("all_players_teams: " + str(all_players_teams))
	return all_players_teams


# get game espn id from google
def read_game_espn_id(game_key, existing_game_ids_dict={}, read_new_game_ids=False):
	print('\n===Read Game ESPN ID======\n')
	print('Input: game_key = away home date = ' + game_key)
	# print('read_new_game_ids: ' + str(read_new_game_ids))

	espn_id = ''

	# den uta oct 19 nba espn box score
	# if we always use format 'away home m/d/y' then we can check to see if key exists and get game id from local file
	# search_key = away_abbrev + ' ' + home_abbrev + ' ' + date
	# print('search_key: ' + search_key)

	if game_key in existing_game_ids_dict.keys():
		print('found game key saved')
		espn_id = existing_game_ids_dict[game_key]

	elif read_new_game_ids: # if too many requests then we avoid reading game ids for a time

		#try:
			
		# need to convert team abbrev to full name to ensure find results in search
		# bc not universal abbrevs
		full_game_key = ''
		game_data = game_key.split()
		if len(game_data) > 2:
			away_team_abbrev = game_data[0]
			home_team_abbrev = game_data[1]
			date = game_data[2]

			# combine abbrev and name to ensure accurate search
			away_team = converter.convert_team_abbrev_to_name(away_team_abbrev).split()[-1]
			home_team = converter.convert_team_abbrev_to_name(home_team_abbrev).split()[-1]

			# convert 12/29/2023 to Dec 29 2023
			# so convert month num to name
			date_title = converter.convert_month_num_to_abbrev(date)

			# okc thunder den nuggets Dec 29 2023 nba espn box score
			full_game_key = away_team_abbrev + ' ' + away_team + ' ' + home_team_abbrev + ' ' + home_team + ' ' + date_title

			# no need to save game if game key error, warning
			search_string = full_game_key.replace(' ', '+') + '+nba+espn+box+score'
			print('search_string: ' + search_string)
			
			site = 'https://www.google.com/search?q=' + search_string
			#print('site: ' + site)

			soup = read_website(site)

			if re.search('HTTP Error', str(soup)):# == 'HTTP Error 429: Too Many Requests':
				return soup

			time.sleep(1) # do we need to sleep bt calls to google to avoid being blocked by error 429 too many requests

				# req = Request(site, headers={
				# 	'User-Agent': 'Mozilla/5.0',
				# })

				# page = urlopen(req) # open webpage given request

				# soup = BeautifulSoup(page, features="lxml")
			if soup is not None:
				#print('soup: ' + str(soup))
				links_with_text = [] # id is in first link with text

				for a in soup.find_all('a', href=True):
					#print('a.text: ' + str(a.text))
					#print('a[href]: ' + str(a['href']))
					if a.text and a['href'].startswith('/url?'):
						links_with_text.append(a['href'])

				#print('links_with_text: ' + str(links_with_text))

				links_with_id_text = [x for x in links_with_text if 'gameId/' in x]
				#print('links_with_id_text: ' + str(links_with_id_text))

				espn_id_link = links_with_id_text[0] # string starting with player id
				#print('espn_id_link: ' + str(espn_id_link))

				espn_id = re.findall(r'\d+', espn_id_link)[0]

				#print('Success', espn_id, game_key)

				data = [[game_key, espn_id]]
				filepath = 'data/all games ids.csv'
				write_param = 'a' # append ids to file
				writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

			#except Exception as e:
				#print('Error', espn_id, game_key, e)
		else:
			print('Warning: Game Key Error! ' + game_key)

	print("game_espn_id: " + espn_id)
	return espn_id


# get player espn id from google
# or from file if already saved
# player_id_dict = {player:id,..}
# player name maybe full name or abbrev
# bc we can search abbrev to get id and connect to full name
# but we dont want to save abbrev with id? we could but then it is not uniform
# could make players abbrevs file with id instead of name bc id is unique but name maybe same for 2 players
# sometimes given abbrev if only available
def read_player_espn_id(init_player_name, init_all_players_espn_ids={}, player_team='', filepath='data/all players ids.csv', year=''):
	#print('\n===Read Player ESPN ID: ' + init_player_name + '===\n')
	#print('init_player_name: ' + init_player_name) 

	espn_id = ''

	player_name = init_player_name.lower() # ensure lowercase for matching

	if player_name in init_all_players_espn_ids.keys():
		espn_id = init_all_players_espn_ids[player_name]

	else:
		#print('read id from internet')
		# spell out position to be more specific to ensure correct search
		#player_names = player_name.split()
		position = ''
		if init_player_name[-1].isupper():
			position = 'center'
			if re.search('SF$', init_player_name):
				position = 'small forward'
			elif re.search('PF$', init_player_name):
				position = 'power forward'
			elif re.search('F$', init_player_name):
				position = 'forward'
			elif re.search('PG$', init_player_name):
				position = 'point guard'
			elif re.search('SG$', init_player_name):
				position = 'shooting guard'
			elif re.search('G$', init_player_name):
				position = 'guard'

			player_name = re.sub('\s+[A-Z]+$','',init_player_name)
		
		#print('position: ' + position)

		#try:
		#player_search_term = player_name
		# if player_name.lower() == 'nikola jovic': # confused with nikola jokic
		# 	player_search_term += ' miami heat'
		year_span = ''
		if year != '':
			year_span = converter.convert_year_to_span(year) # 2023 -> 2022-23

		# try searching just team name not city bc then maybe will show player as it should
		# player team may cause more mismatches bc google focuses on team stats for dnp players
		# seems like more accurate results with 'nba game log espn' over ' stats per game-nba'
		# use only last word of team so search doesnt focus on it but it removes players not on this team
		if player_team != '':
			player_team = player_team.split()[-1]
		player_search_term = player_name.title() + ' ' + player_team + ' ' + position + ' ' + year_span +  ' nba game log espn' #player_team + ' ' + position + ' ' + year_span
		print('player_search_term: ' + player_search_term)
		site = 'https://www.google.com/search?q=' + re.sub('\s+', '+', player_search_term) #+ 'stats+per+game-nba'#'+nba+espn+gamelog'
		# https://www.google.com/search?q=john+collins+game+log
		#site = 'https://www.google.com/search?q=help'
		#print('site: ' + site)

		soup = read_website(site)
		#print('soup: ' + str(soup))

		# if soup == 'HTTP Error 429: Too Many Requests':
		# 	print('Warning: Too many requests!')
		# elif re.search('HTTP Error', soup):# == 'HTTP Error 429: Too Many Requests':
		# 	print('Warning: HTTP Error! ' + soup)
		if soup is not None:
			if re.search('HTTP Error', str(soup)):
				print('Warning: HTTP Error! ' + soup)
			else:
				links_with_text = [] # id is in first link with text

				for a in soup.find_all('a', href=True):
					if a.text and a['href'].startswith('/url?'):
						links_with_text.append(a['href'])

				links_with_id_text = [x for x in links_with_text if 'id/' in x]

				# if no links returned then practice player may not have game log search results
				# so see if there is a player with the same abbrev in current season abbrevs
				# case of moses brown only shows current yr game log in search results
				# we know it is same person bc if there was another play that yr then there would be a game log in search results
				if len(links_with_id_text) > 0:
					espn_id_link = links_with_id_text[0] # string starting with player id

					espn_id = re.findall(r'\d+', espn_id_link)[0]

					#print('Success', espn_id, player_name.title())

					# need to check the link we get back has player
					# with first name same initial as input initial in case given abbrev
					# it should be a specific enough search that it returns no results but it could easily return wrong results which would cause errors
					# for example sterling brown results show when you remove the team from the search
					# so first search with team and if no id returned or link title name mismatch search without it?

					# only write to file if given full name
					# we know not full name if len>2 and ends with f|c|g
					# irregular case Baldwin F so use uppercase to show abbrev
					#if len(player_names) < 3 or not re.search('[cfg]$',player_name):
					if not init_player_name[-1].isupper():
						data = [[player_name, espn_id]]
						#filepath = 'data/Player Ids.csv'
						write_param = 'a' # append ids to file
						writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet
				else:
					print('Warning: Search returned no results! ' + player_search_term)
		

	#print("espn_id: " + espn_id)
	return espn_id

# pass all bc we need teammates and opponents
def read_all_players_espn_ids(players_names, player_of_interest=''):
	print('\n===Read All Players ESPN IDs===\n')
	print('Input: players_names: [p1, ...] = [\'jalen brunson\', ...]')
	print('\nOutput: all_players_espn_ids = {player:id, ...} = {\'jalen brunson\': \'3934672\', ...}\n')
	
	all_players_espn_ids = {}

	if player_of_interest != '':
		players_names = [player_of_interest.lower()]

	# see if id saved in file
	filepath = 'data/all players ids.csv'
	init_player_ids = extract_data(filepath, header=True)

	#init_espn_ids_dict = {}
	for row in init_player_ids:
		#print('row:\n' + str(row))
		player_name = row[0].lower()
		player_id = row[1]

		all_players_espn_ids[player_name] = player_id
	#print('init_espn_ids_dict: ' + str(init_espn_ids_dict))

	for player_name in players_names:
		player_name = player_name.lower()
		espn_id = read_player_espn_id(player_name, all_players_espn_ids, filepath=filepath)
		all_players_espn_ids[player_name] = espn_id

	#print('all_players_espn_ids: ' + str(all_players_espn_ids))
	return all_players_espn_ids



# read list of player names given teams so we dont have to type all names
# save in same player teams file used when directly given player names and found team on player page
# bc the data is the same from both sources, unless we set read new teams=true
# problem is we need to see if team has been fully saved before
# to see if we want to read from internet
# to solve this make new json file for team rosters/players
# where if roster added then we know fully saved unless we request new teams after trades
# in theory we could keep 1 file and check that x no. players saved but number might be inconsistent (eg some teams have 18, others 17)
# if we have the rosters file then it can replace the player teams file
def read_teams_players(teams, read_new_teams=True):
	#print("\n===Read Teams Players===\n")
	# print('teams: ' + str(teams))
	teams_players_dict = {}
	players_names = [] # return single list of all players. later could separate by team but really we want to rank all players by prob

	# if not read new teams,
	# see if team saved in file
	# bc if read new teams, then we will create new file with today's date in name
	existing_teams_players_dict = {}
	if not read_new_teams:
		data_type = 'teams players'
		existing_teams_players_dict = read_json(data_type) # returns data dict

		# for team, players in all_teams_players.items():
		# 	existing_teams_players_dict[team] = players
	for game_teams in teams:
		for team in game_teams:
			# go to roster page espn
			team_players = read_team_roster(team, existing_teams_players_dict, read_new_teams)
			teams_players_dict[team] = team_players

			players_names.extend(team_players)

	# if read new teams for all players then we can overwrite the file completely removing all old teams bc we cannot assume any player is on the same team as they were before
	if read_new_teams:
		# overwrite bc new teams json single line
		filepath = 'data/Teams Players.json'
		write_param = 'w'
		writer.write_json_to_file(teams_players_dict, filepath, write_param)
		
	#print('players_names: ' + str(players_names))
	return players_names



# read team players from internet
# read team roster from internet
def read_roster_from_internet(team_abbrev):
	#print('\n===Read Roster from Internet===\n')
	raw_roster = []
	roster = []

	

	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	# get team name from abbrev
	team_name = determiner.determine_team_name(team_abbrev)
	team_name = re.sub(r'\s+','-',team_name)

	# espn_irregular_abbrevs = {'bro':'bkn', 
	# 				  	'gs':'gsw',
	# 					'okl':'okc', 
	# 					'no':'nop',
	# 					'nor':'nop', 
	# 					'pho':'phx', 
	# 					'was':'wsh', 
	# 					'uth': 'uta', 
	# 					'utah': 'uta', 
	# 					'sa':'sas',
	# 					'ny':'nyk'  } # for these match the first 3 letters of team name instead
	espn_irregular_abbrevs = {'uta':'utah',
						   	'nyk':'ny',
							'gsw':'gs',
							'nop':'no',
							'sas':'sa'}
	if team_abbrev in espn_irregular_abbrevs.keys():
		team_abbrev = espn_irregular_abbrevs[team_abbrev]

	#try:

	roster_url = 'https://www.espn.com/nba/team/roster/_/name/' + team_abbrev + '/' + team_name #den/denver-nuggets
	#print("roster_url: " + str(roster_url))

	html_results = read_web_data(roster_url) #pd.read_html(roster_url)
	#print("html_results: " + str(html_results))

	if len(html_results) > 0:
		roster_df = html_results[0]
		raw_roster = roster_df.loc[:,'Name'].tolist()


	# remove non word characters
	for player in raw_roster:
		# convert player name to standard
		player_name = re.sub(r'\.|\d','',player)
		player_name = re.sub(r'-',' ',player_name)
		roster.append(player_name.lower())

	# we are reading from the internet so we are definitely going to write the data to a file no matter what so we can access it later
	# the question is if we are going to append or overwrite
	# if we are going to overwrite then we must wait till we have all teams so we only overwrite first entry and append all after
	# if not all new teams then simply append this player's team to the file
	# for json we must add new key,val to existing dict and overwrite file
	# if not read_new_teams:
	# 	data = {}
	# 	data[team_abbrev] = roster
	# 	write_param = 'a'
	# 	filepath = 'data/Teams-Players.json'
	# 	writer.write_json_to_file(data, filepath, write_param)

	#except Exception as e:
		#print('Error', str(roster), team_abbrev.upper(), e)

	#print('roster: ' + str(roster))
	return roster

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

# read team roster to get team players
def read_team_roster(team_abbrev, existing_teams_players_dict={}, read_new_teams=True, read_new_rosters=True):
	#print('\n===Read Team Roster: ' + team_abbrev + '===\n')
	roster = []

	if read_new_teams or read_new_rosters:
		roster = read_roster_from_internet(team_abbrev)
	else:
		#if not given existing teams players, see if local file saved
		if len(existing_teams_players_dict) == 0:
			data_type = 'teams players'
			existing_teams_players_dict = read_json(data_type)

		if team_abbrev in existing_teams_players_dict.keys():
			roster = existing_teams_players_dict[team_abbrev]
		else:
			roster = read_roster_from_internet(team_abbrev)
			# existing_teams_players_dict[team_abbrev] = roster
			# write_param = 'w'
			# filepath = 'data/Teams-Players.json'
			# writer.write_json_to_file(existing_teams_players_dict, filepath, write_param)

	
	#print('roster: ' + str(roster))
	return roster

# distinctly diff from all rosters
# bc this is only rosters of interest this run (eg teams playing today)
def read_teams_current_rosters(game_teams, read_new_teams=True, read_new_rosters=True, all_teams=[]):
	print("\n===Read Teams Current Rosters===\n")
	print('Setting: Read New Teams after trades and aquisitions')
	print('\nInput: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\')]')
	print('\nOutput: all_teams_rosters = {team:[players],... = {\'nyk\':[\'jalen brunson\',...],...\n')

	all_teams_rosters_file = 'data/all teams rosters.json'

	init_all_teams_rosters = read_json(all_teams_rosters_file)
	#print("init_all_teams_rosters: " + str(init_all_teams_rosters))

	teams_current_rosters = {}#copy.deepcopy(init_all_teams_rosters) # need to init as saved teams so we can see difference at end

	try:
		# if game teams blank, read all teams
		if len(game_teams) > 0:
			for teams in game_teams:
				for team in teams:
					# read player teams
					team_roster = read_team_roster(team, init_all_teams_rosters, read_new_teams, read_new_rosters)

					teams_current_rosters[team] = team_roster

		else: # game teams blank
			for team in all_teams:

				# read player teams
				team_roster = read_team_roster(team, init_all_teams_rosters, read_new_teams, read_new_rosters)

				teams_current_rosters[team] = team_roster


	except Exception as e:
		print('Exception while reading all players teams: ', e)

	# need to add to file after each player bc if hangs halfway through then will lose all work
	# or if that is too inefficient then make sure never hangs
	# by retrying same player if hit cancel instead of skipping player
	# if not init_all_teams_rosters == all_teams_rosters:
	# 	writer.write_json_to_file(all_teams_rosters, all_teams_rosters_file, 'w')
		
	#print('teams_current_rosters: ' + str(teams_current_rosters))
	return teams_current_rosters

# rosters = {team:roster, ...}
# game_teams = [(t1, t2), (t3, t4)] separated by game
# INCLUDE ALL saved game teams (not necessarily every team, just every team encountered so far)
def read_all_teams_rosters(teams, read_new_teams=True, read_new_rosters=True):
	print("\n===Read All Teams Rosters===\n")
	print('Setting: Read New Teams after trades and aquisitions')
	print('\nInput: teams = [t1, ...] = [\'nyk\', \'bkn\',...]')
	print('\nOutput: all_teams_rosters = {team:[players],... = {\'nyk\':[\'jalen brunson\',...],...\n')

	if len(teams) == 0:
		teams = ['bos','bkn', 'nyk','phi', 'tor','chi', 'cle','det', 'ind','mil', 'den','min', 'okc','por', 'uta','gsw', 'lac','lal', 'phx','sac', 'atl','cha', 'mia','orl', 'wsh','dal', 'hou','mem', 'nop','sas']

	all_teams_rosters_file = 'data/all teams rosters.json'

	init_all_teams_rosters = read_json(all_teams_rosters_file)
	#print("init_all_teams_rosters: " + str(init_all_teams_rosters))

	all_teams_rosters = copy.deepcopy(init_all_teams_rosters) # need to init as saved teams so we can see difference at end

	try:
		for team in teams:
			# read player teams
			team_roster = read_team_roster(team, all_teams_rosters, read_new_teams, read_new_rosters)

			all_teams_rosters[team] = team_roster

	except Exception as e:
		print('Exception while reading all players teams: ', e)

	# need to add to file after each player bc if hangs halfway through then will lose all work
	# or if that is too inefficient then make sure never hangs
	# by retrying same player if hit cancel instead of skipping player
	if not init_all_teams_rosters == all_teams_rosters:
		writer.write_json_to_file(all_teams_rosters, all_teams_rosters_file)
		
	#print('all_teams_rosters: ' + str(all_teams_rosters))
	return all_teams_rosters
        
# rosters = {team:roster, ...}
# game_teams = [(t1, t2), (t3, t4)] separated by game
# do not include saved game teams
def read_teams_rosters(game_teams, read_new_teams=True):
	print("\n===Read Teams Rosters===\n")
	print('Setting: Read New Teams after trades and aquisitions')
	print('\nInput: game_teams = [(away team, home team), ...] = [(\'nyk\', \'bkn\')]')
	print('\nOutput: teams_current_rosters = {team:[players],...}')

	# print('game_teams: ' + str(game_teams))
	teams_rosters = {}
	#players_names = [] # return single list of all players. later could separate by team but really we want to rank all players by prob

	# if not read new teams,
	# see if team saved in file
	# bc if read new teams, then we will create new file with today's date in name
	existing_teams_players_dict = {}
	if not read_new_teams:
		data_type = 'teams rosters'
		existing_teams_players_dict = read_json(data_type) # returns data dict

		# for team, players in all_teams_players.items():
		# 	existing_teams_players_dict[team] = players
	for teams in game_teams:
		for team in teams:
			# go to roster page espn
			team_players = read_team_roster(team, existing_teams_players_dict, read_new_teams)
			teams_rosters[team] = team_players

			#players_names.extend(team_players)

	# if read new teams for all players then we can overwrite the file completely removing all old teams bc we cannot assume any player is on the same team as they were before
	if read_new_teams:
		# overwrite bc new teams json single line
		filepath = 'data/teams rosters.json'
		write_param = 'w'
		writer.write_json_to_file(teams_rosters, filepath, write_param)
		
	print('teams_rosters: ' + str(teams_rosters))
	return teams_rosters

# its not just prev yrs we care about bc we may want to see how it performed in prev games this yr
# so give it a date/game to set as the last game to eval
def read_game_teams(read_season_year):
	game_teams = [] # read todays schedule if cur yr

	return game_teams
