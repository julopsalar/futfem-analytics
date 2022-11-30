# Web Scraping
import requests
from bs4 import BeautifulSoup
import re

import pandas as pd
import numpy as np
#import time

def scrape_elements(url, element='table'):
    """
    Given an url and a html element, gets the html code and extracts the elements as a list
    :param: url
    :param: element
    :return: all the elements parsed into a list     
    """
    res = requests.get(url)
    # The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')
    elements = [t for t in soup.find_all(element)]
    return elements


def get_tables_as_data(url, element='table', extract_links=None):
    """
    For each element, convert to dataframe and return the list of them
    :return: Transforms the html codes into DataFrames
    """
    html_elements = scrape_elements(url, element)
    data = [pd.read_html(str(e), extract_links=extract_links)[0]
            for e in html_elements]
    # Drop duplicates and null rows
    data = [d.drop_duplicates(keep=False).reset_index(drop=True) for d in data]
    return data


def parse_link(link):
    regex = r'/en/([^/]+)/([^/]+)/.+'
    m = re.match(regex, str(link))
    if m:
        return m.groups()[1]
    else:
        return None

def drop_column_level(data, regex, avoid=[]):
    cols = []
    for c in list(data):
        m = re.match(regex, c[0])
        if (m is None) & (c[0] not in avoid):
            cols.append(c[0] + '_' + c[1])
        else:
            cols.append(c[1])
    cols = [c.replace(' ', '') for c in cols]
    
    data = data.droplevel(0, axis=1)
    data.columns = cols
    data.dropna(axis=0, inplace=True)
    return data
    
def parse_links_columns(data):
    for c in data.columns:    
        if '%' in c:
            data.drop(columns=[c], inplace=True)
        else:
            tuple_col = data[c].tolist()
            text, link = list(zip(*tuple_col))
            data[c] = list(text)
            data[f'{c}ID'.replace(' ', '')] = list(map(lambda x : parse_link(x), link))

    data.dropna(how='all', axis=1, inplace=True)
    return data


def get_matches_info(url, output=False):

    matches_full = get_tables_as_data(url, extract_links='body')
    matches = parse_links_columns(matches_full[0])
    matches.rename(columns={'MatchReportID':'MatchID','xG':'xGHome', 'xG.1':'xGAway'}, inplace=True)
    
    # Drop blank columns
    matches.replace("", np.nan, inplace=True)
    matches.dropna(how='all', axis=1, inplace=True)
    matches.replace(np.nan, 0, inplace=True)
    matches.drop(['Match Report', 'ScoreID'], axis=1, inplace=True)
    
    matches = matches.loc[matches['MatchID'] != 'matchup',:]

    matches = matches.astype({
        'Wk': int,
        'xGHome': float,
        'xGAway': float 
    })

    if output: matches.to_csv('matches.csv', index=False)
    
    return matches




def clean_event_html(event, match, team):
    text = event.text
    players = event.find_all('a')
    
    # Cleaning raw text
    text = re.sub(r'\s{2,}', '$', text)
    text = re.sub(r'(&rsquor;)|(—\s*)', '', text)
    text = re.sub(r'(\$Assist:)|(for\s)', '', text)
    text = [t for t in text.split('$') if t]
    text[2] = parse_link(players[0]['href'])
    if len(players) == 2:
        text[3] = parse_link(players[1]['href'])
    else:
        text.insert(3, '')
    
    text.insert(0, team)
    text.insert(0, match)
    text[-1] = re.sub(r'Goal \d+:\d+', 'Goal', text[-1])
    
    return text[0:7]

def get_match_events(match, homeTeam, awayTeam):
    url = f'https://fbref.com/en/matches/{match}/'
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')

    events_div = soup.find('div', {'id': 'events_wrap'})
    home_events = events_div.find_all('div', {'class': 'event a'})
    away_events = events_div.find_all('div', {'class': 'event b'})

    events = []
    events.extend([clean_event_html(h, match, homeTeam) for h in home_events])
    events.extend([clean_event_html(a, match, awayTeam) for a in away_events])
    headers = 'MatchID', 'SquadID', 'Minute', 'Score', 'Player1',	'Player2', 'Event'
    #print(events)
    return pd.DataFrame(events, columns=headers)


def get_match_data(match_id, home, away):
    """
    """
    regex = r'Unnamed.+'
    avoid = ['Expected', 'SCA', 'Performance', 'Shot Stopping']

    match_url = f'https://fbref.com/en/matches/{match_id}'
    all_data = get_tables_as_data(match_url, extract_links='body')
    
    # 0,1 -> lineups
    # 2 possession, passing, ...
    # 3,4,5,6,7,8 -> players_home
    dfs = []
    for home_df in all_data[3:9]:
        home_data = drop_column_level(home_df, regex, avoid)
        home_data = parse_links_columns(home_data)
        home_data['SquadID'] = [home] * home_data.shape[0]
        home_data['MatchID'] = [match_id] * home_data.shape[0]
        dfs.append(home_data)
    
    # 10,11,12,13,14,15 -> players_away
    for away_df in all_data[10:16]:
        away_data = drop_column_level(away_df, regex, avoid)
        away_data = parse_links_columns(away_data)
        away_data['SquadID'] = [away] * away_data.shape[0]
        away_data['MatchID'] = [match_id] * away_data.shape[0]
        dfs.append(away_data)
    
    h = pd.concat(dfs[:6], axis=1)
    a = pd.concat(dfs[6:], axis=1)
    
    # 9 -> gk_home
    # 16 -> gk_away
    h_gk, a_gk = all_data[9], all_data[16]
    
    h_gk, a_gk = drop_column_level(h_gk, regex, avoid), drop_column_level(a_gk, regex, avoid)
    h_gk, a_gk = parse_links_columns(h_gk), parse_links_columns(a_gk)
    h_gk['SquadID'] = [home] * h_gk.shape[0]
    a_gk['SquadID'] = [away] * a_gk.shape[0]
    h_gk['MatchID'] = [match_id] * h_gk.shape[0]
    a_gk['MatchID'] = [match_id] * a_gk.shape[0]
    
    # 17 -> shots
    shots = all_data[17]
    shots = drop_column_level(shots, regex, avoid)
    shots = parse_links_columns(shots)
    shots['MatchID'] = [match_id] * shots.shape[0]
    
    # shots   
    shots = shots.loc[:,~shots.columns.duplicated()].copy()
    #shots.to_csv('shots.csv', index=False)
 
    players = pd.concat([h,a], axis=0)
    players.reset_index(drop=True)
    players = players.loc[:,~players.columns.duplicated()].copy()
    #todo.to_csv('players_stats.csv', index=False)

    goalkeepers = pd.concat([h_gk, a_gk], axis=0)
    goalkeepers.reset_index(drop=True)
    goalkeepers = goalkeepers.loc[:,~goalkeepers.columns.duplicated()].copy()
    #goalkeepers.to_csv('gk_stats.csv', index=False)
    
    return shots, players, goalkeepers