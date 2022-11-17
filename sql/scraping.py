# Web Scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

def get_tables_as_data(url, element='table'):
    res = requests.get(url)
    # The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')

    data = [pd.read_html(str(t))[0] for t in soup.find_all(element)]
    return data

def get_matches(url, element='table'):
    res = requests.get(url)
    ## The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("",res.text),'lxml')
    
    data = [t for t in soup.find_all(element)]
    # Links are contained in <a> sections, with the text 'Match Report'
    match_link = re.compile("Match Report")
    # Extracting links for the reports
    links = [ link['href'] for link in data[0].find_all('a', href=True) if match_link.match(link.contents[0]) ]    
    df = pd.read_html(str(data[0]))[0]
    # Fill matches that dont have Match Report (future matches)
    while len(links) < df.shape[0]: links.append('')
    # Modifying links to access after 
    df['Match Report'] = links
    # Setting id
    ids = [ ]
    for mr in df['Match Report']:
        id = re.search(r'.*/matches/(.*)/.*', mr)
        if id:
            ids.append(id.groups()[0])
        else:
            ids.append('')
    df['MatchID'] = ids
    # Drop invalid rows and convert Week number to integer
    df = df[df['Wk'].notna()]
    df.Wk = df.Wk.astype(int)
    # Clean columns names
    colnames = list(df)
    colnames[colnames.index('xG')] = 'xG_Home'
    colnames[colnames.index('xG.1')] = 'xG_Away'
    colnames[colnames.index('Match Report')] = 'MatchReport'
    df.columns = colnames

    return df




def clean_event_html(event, matchID, team):
    text = event.text
    # Cleaning raw text
    text = re.sub(r'\s{2,}', '$', text)
    text = re.sub(r'(&rsquor;)|(—\s)', '', text)
    text = re.sub(r'(\$Assist:)|(for\s)', '', text)
    text = [t for t in text.split('$') if t]
    # Own Goals are special..
    try:
        og = text.index('Own Goal')
        if og > 0:
            text.insert(og, '')
            text.pop()
    except:
        None
    # Fill non full row
    if len(text) < 5:
        text.insert(3, '')
    text.insert(len(text), '')
    text.insert(0, team)
    text.insert(0, matchID)
    # Extract notes
    notes = re.match(r'Goal\s(.*)', text[-2])
    if notes:
        text[-2] = 'Goal'
        text[-1] = notes.group(1)
    return text


def parse_match_report(matchID, homeTeam, awayTeam):

    url = f'https://fbref.com/en/matches/{matchID}/'
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')

    events_div = soup.find('div', {'id': 'events_wrap'})
    home_events = events_div.find_all('div', {'class': 'event a'})
    away_events = events_div.find_all('div', {'class': 'event b'})

    # CSV Headers
    headers = 'MatchID', 'Team', 'Minute', 'Score', 'Player1',	'Player2', 'Event', 'Notes'
    events = []
    for e in home_events:
        events.append(clean_event_html(e, matchID, homeTeam))
    for e in away_events:
        events.append(clean_event_html(e, matchID, awayTeam))

    data = pd.DataFrame(events, columns=headers)
    return data


def get_match_stats(url, element='table'):
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')

    data = [pd.read_html(str(t))[0] for t in soup.find_all(element)]
    return data

# Receiving a multilevel-column dataframe, mixes both level names and drops unused level
def drop_level_column(data, ignore=[]):
    new_cols = []
    for c in list(data):
        if (re.match(r'Unnamed.*', c[0]) is not None) | (c[0] in ignore):
            new_cols.append(c[1])
        else:
            new_cols.append(c[0].replace(' ', '') + '_' + c[1])
    data.columns = new_cols

# Merges multiple dataframe based on 'base' dataframe columns
def merge_stats_player(base, others, not_headers, output=None):
    drop_level_column(base, ignore=not_headers)
    base = base[base.columns.drop(
        list(base.filter(regex=r'(Passes.*)|(Dribbles.*)')))]

    for d in others:
        drop_level_column(d, ignore=['Performance', 'Touches'])
        # Merge by common columns
        base = pd.merge(base, d, on=list(d.columns.intersection(list(base))))

    if output:
        base.to_csv(output + '.csv', index=False)
    return base


def process_match_data(matchID):
    url = f'https://fbref.com/en/matches/{matchID}/'
    data = get_match_stats(url)
    # Ignore multiindex columns names
    not_headers = ['Performance', 'Expected', 'SCA']

    # Select data from list of dataframes
    #   Full Players Stats
    #   Summary --> Passing --> Pass Types --> Defensive Actions --> Possession --> Miscellaneous Stats
    players_home = data[-17:-11]
    players_away = data[-10:-4]

    summary_home = players_home[0]
    home_stats = merge_stats_player(summary_home, players_home[1:], not_headers) 
    summary_away = players_away[0]
    away_stats = merge_stats_player(summary_away, players_away[1:], not_headers)
    # Merge all players and drop non valid rows
    joined = pd.concat([home_stats, away_stats])
    joined.drop_duplicates(subset=['Player'], keep=False, inplace=True)
    joined['MatchID'] = [matchID] * joined.shape[0]

    #   Shots data
    shots = data[-3]
    drop_level_column(shots)
    shots.columns = [re.sub(r'\s', '_', c) for c in list(shots)]
    shots['MatchID'] = [matchID]*shots.shape[0]
    shots.fillna('', inplace=True)
    shots = shots[shots['Minute'] != '']
    shots = shots.replace(r'^\s*$', None, regex=True)
    
    #   Goalkeeping
    gk, gk2 = data[-11], data[-4]
    drop_level_column(gk, ignore=['Shot Stopping'])
    drop_level_column(gk2, ignore=['Shot Stopping'])
    gk.fillna('', inplace=True)
    gk2.fillna('', inplace=True)

    gk_match = pd.concat([gk, gk2]).reset_index().drop(columns=['index'])
    gk_match['MatchID'] = [matchID]*gk_match.shape[0]
    colnames = list(gk_match)
    colnames[colnames.index('Min')] = 'Minutes'
    colnames[colnames.index('Save%')] = 'Save_100'
    colnames[colnames.index('Launched_Cmp%')] = 'Launched_Cmp_100'
    colnames[colnames.index('Passes_Launch%')] = 'Passes_Launch_100'
    colnames[colnames.index('GoalKicks_Launch%')] = 'GoalKicks_Launch_100'
    colnames[colnames.index('Crosses_Stp%')] = 'Crosses_Stp_100'
    gk_match.columns = colnames

    return joined, shots, gk_match

def clean_players_raw(data):
    # Drop % columns
    r = re.compile(".*%.*")
    del_cols = list(filter(r.match, list(data)))
    players = data.drop(columns=del_cols)
    # Delete rows that sum all players (i.e Player = '15 players')
    filtered = players['Player'].str.contains(r'^\d+')
    players = players[~filtered]
    
    # Modify some colnames according to DataBase Table names
    newcols = list(players)
    newcols[newcols.index('Off')] = 'Offs'
    newcols[newcols.index('Tkl+Int')] = 'Tkl_plus_Intr'
    newcols[newcols.index('Int')] = 'Intr'
    newcols[newcols.index('1/3')] = 'Third'
    newcols[newcols.index('Min')] = 'Minu'
    newcols[newcols.index('2CrdY')] = 'SndCrdY'
    newcols = [re.sub(r'\s', '_', c) for c in newcols]
    players.columns = newcols
    return players