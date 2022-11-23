# Web Scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# To avoid useless warnings
pd.options.mode.chained_assignment = None  # default='warn'


def scrape_elements(url, element='table'):
    # Returns a list of html table
    res = requests.get(url)
    # The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')
    elements = [t for t in soup.find_all(element)]
    return elements


def get_tables_as_data(url, element='table', extract_links=None):
    # For each element, convert to dataframe and return the list of them
    html_elements = scrape_elements(url, element)
    data = [pd.read_html(str(e), extract_links=extract_links)[0]
            for e in html_elements]
    # Drop duplicates and null rows
    data = [d.drop_duplicates(keep=False).reset_index(drop=True) for d in data]
    return data


def parse_link(link, link_marks):
    for m in link_marks:
        regex = (r'(.+/'+f'{m}'+r'/)([^/]+)/([^/]*)$')
        s = re.search(regex, link)
        if s:
            return s.groups()[1]
    return ''

def convert_link_table(data, avoid_cols, marks):
    for col in data:
        if col not in avoid_cols:
            data[col] = data[col].apply(lambda x: x[0])
        else:
            data[col] = data[col].apply(
                lambda x: parse_link(str(x[1]), marks))
        # Replace spaces in name
        data.rename(columns={col: col.replace(" ", "")
                                    .replace('%', '_100')
                                    .replace('/', '_')
                                    .replace('+', '_plus_')}, inplace=True)
    return data

def get_rank(url):
    stats = get_tables_as_data(url, extract_links='body')
    rank, rank_ha = stats[0], stats[1]
    rk_squad = rank_ha.iloc[:, 0:2].droplevel(0, axis=1)
    rk_squad['Rk'] = rk_squad['Rk'].apply(lambda x: int(x[0]))
    rk_squad['Squad'] = rk_squad['Squad'].apply(lambda x: parse_link(str(x[1]), ['squads']))
    
    for col in rank_ha:
        rank_ha[col] = rank_ha[col].apply(lambda x: x[0])
    
    rank_ha = rank_ha.iloc[:,2:]
    rank_ha = rank_ha.stack(0)
    rank_ha.index = rank_ha.index.set_names(['Rk', 'H_A'])
    rank_ha.reset_index(inplace=True)
    rank_ha['Rk'] += 1
    rank_ha.rename(columns=(lambda x: x.replace('/', '_')), inplace=True)
    rank_ha['SquadID'] = [rk_squad[rk_squad['Rk'] == n]['Squad'].values[0] for n in rank_ha['Rk']]
    
    return rank_ha

def get_players(url):
    stats = get_tables_as_data(url, extract_links='body')
    players = stats[-1]
    players = players.iloc[:,1:7]
    players.columns = [c[1] for c in list(players)]
    cols = ['Player', 'Squad']
    for c in players:
        if c not in cols:
            players[c] = players[c].apply(lambda x: x[0])
    players['Squad'] = players['Squad'].apply(lambda x: parse_link(str(x[1]), ['squads']))
    players[['Player', 'PlayerID']] = pd.DataFrame(players['Player'].to_list(), index=players.index)
    players['PlayerID'] = players['PlayerID'].apply(lambda x: parse_link(str(x), ['players']))

    return players

def get_matches(url, link_marks):
    data = get_tables_as_data(url, extract_links='body')
    df = data[0]

    cols = ['Home', 'Away', 'Match Report']
    df = convert_link_table(df, cols, link_marks)
    df.rename(columns={
        'MatchReport':'MatchID',
        'xG' : 'xG_Home',
        'xG.1' : 'xG_Away'
    }, inplace=True)
    return df

def clean_event_html(event, match, team):
    text = event.text
    players = event.find_all('a')
    
    # Cleaning raw text
    text = re.sub(r'\s{2,}', '$', text)
    text = re.sub(r'(&rsquor;)|(—\s*)', '', text)
    text = re.sub(r'(\$Assist:)|(for\s)', '', text)
    text = [t for t in text.split('$') if t]
    text[2] = parse_link(players[0]['href'], ['players'])
    if len(players) == 2:
        text[3] = parse_link(players[1]['href'], ['players'])
    else:
        text.insert(3, '')
    
    text.insert(0, team)
    text.insert(0, match)
    text[-1] = re.sub(r'Goal \d+:\d+', 'Goal', text[-1])
    
    return text

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
    return pd.DataFrame(events, columns=headers)

# Juntar dataframes y limpiar columnas...
def merge_team_match_stats(df_list, team, match):
    ignoring_headers = ['Performance', 'Expected', 'SCA', 'GCA', 'Shot Stopping']
    avoid_links = ['Player', 'Squad', 'SCA1_Player', 'SCA2_Player']
    link_marks = ['players', 'squads']

    for idx, d in enumerate(df_list):
        colnames = []
        for col in d:
            if (re.match(r'Unnamed.*', col[0])) or (col[0] in ignoring_headers):
                colnames.append(col[1])
            else:
                colnames.append(str(col[0]+'_'+col[1]).replace(' ', ''))

        d.droplevel(0, 1)
        d.columns = colnames
        # Drop non valid rows
        d = d[~d['Age'].isna()]
        d = convert_link_table(d, avoid_links, link_marks)
        '''for col in d:
            if col not in avoid_links:
                d[col] = d[col].apply(lambda x: x[0])
            else:
                d[col] = d[col].apply(
                    lambda x: parse_link(str(list(x)[1]), link_marks))
        '''        
        if idx == 0:
            base = pd.DataFrame(d)
        else:
            base = pd.merge(base, d, on=list(d.columns.intersection(list(base))))

    base.rename(columns=(lambda x: x.replace('%', '_100')
                         .replace('1_3', 'Third')
                         .replace('+', '_plus_')
                         .replace('2CrdY', 'SndCardY')
                         .replace('Player', 'PlayerID')
                         .replace('Off', 'Offs')), inplace=True)

    if team: base['SquadID'] = [team] * base.shape[0]
    base['MatchID'] = [match] * base.shape[0]

    return base

def parse_shot_data(df, match):
    colnames = []
    for col in list(df):
        if (re.match(r'Unnamed.*', col[0])):
            colnames.append(col[1].replace(' ', '_'))
        else:
            colnames.append(str(col[0]+'_'+col[1]).replace(' ', ''))
    df.droplevel(0, 1)
    df.columns = colnames
    
    for col in df:
        if re.match(r'(.*Player)|(.*Squad)', col):
            df[col] = df[col].apply(lambda x: parse_link(str(list(x)[1]), ['players', 'squads']))
        else:
            df[col] = df[col].apply(lambda x: x[0])
    df = df[df['Player'].astype(bool)]
    df['PSxG'] = df['PSxG'].replace('', 0)
    df['MatchID'] = [match] * df.shape[0]
    return df

def process_match_data(matchID, homeTeam, awayTeam):
    url = f'https://fbref.com/en/matches/{matchID}/'
    data = get_tables_as_data(url, extract_links='body')
    
    # Home team
    #   Summary --> Passing --> Pass Types --> Defensive Actions --> Possession --> Miscellaneous Stats
    home_data = data[3:9]
    home_stats = merge_team_match_stats(home_data, homeTeam, matchID)
    # Away Team
    away_data = data[10:16]
    away_stats = merge_team_match_stats(away_data, awayTeam, matchID)
    player_match = pd.concat([home_stats, away_stats])
    #player_match.to_csv('player_match.csv', index=False)

    # Goalkeeping
    home_gk = data[9]
    home_gk = merge_team_match_stats([home_gk], homeTeam, matchID)
    
    away_gk = data[16]
    away_gk = merge_team_match_stats([away_gk], awayTeam, matchID)
    gk_match = pd.concat([home_gk, away_gk])
    #print(' INTEGER,\n\t'.join(gk_match.columns))
    gk_match.to_csv('gk_match.csv', index=False)

    # Shoting
    shoting = data[17]
    shoting = parse_shot_data(shoting, matchID)
    #shoting = merge_team_match_stats([shoting], None, matchID)
    #shoting.to_csv('shot.csv', index=False)
    
    return player_match, gk_match, shoting