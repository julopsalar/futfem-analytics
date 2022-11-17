from scraping import *
import time
import numpy as np

# Database connection
import sqlalchemy
from sqlalchemy import text
server = 'DESKTOP-B2GO7GM'  # to specify an alternate port
database = 'football_v0'
username = 'juanlop'
password = '1234'

engine = sqlalchemy.create_engine(
    f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server&Trusted_Connection=yes')
conn = engine.connect()


url_stats = 'https://fbref.com/en/comps/230/stats/Liga-F-Stats'
url_rank = 'https://fbref.com/en/comps/230/Liga-F-Stats'
url_matches = 'https://fbref.com/en/comps/230/schedule/Liga-F-Scores-and-Fixtures'


#    Loading 'Squad' table data
# Read Squads info and insert into tables
data = pd.read_csv('..\images.csv')
# Drop if data was previously on the database
try:
    data.to_sql('Squad', conn, if_exists='append', index=False)
except Exception as e:
    print(f'{e.__class__} occured')

res = conn.execute(text('SELECT * FROM Squad'))
print(f'There are {len(res.all())} rows in Table \'Squad\'')


#    'Player' data
stats = get_tables_as_data(url=url_stats)
players = stats[-1]
players.columns = [c[1] for c in list(players)]
players.drop_duplicates(subset=['Player'], keep=False, inplace=True)
try:
    players.iloc[:, 1:7].to_sql('Player', conn, if_exists='append', index=False)
except Exception as e:
    print(f'{e.__class__} occured')

res = conn.execute(text('SELECT * FROM Player'))
print(f'There are {len(res.all())} rows in Table \'Player\'')



#    'SquadRecord'
league_stats = get_tables_as_data(url_rank)
league_rank, league_rank_ha = league_stats[0], league_stats[1]

rk_squad = league_rank_ha.iloc[:, 0:2].droplevel(0, axis=1)

league_rank_ha.drop(columns=['Rk', 'Squad'], level=1, inplace=True)
dataset_ha = league_rank_ha.stack(0)
dataset_ha.reset_index(level=1, inplace=True)
dataset_ha.index += 1
dataset_ha.reset_index(inplace=True)

colnames = list(dataset_ha)
colnames[colnames.index('index')] = 'Rk'
colnames[colnames.index('level_1')] = 'H_A'
colnames[colnames.index('Pts/MP')] = 'Pts_MP'
colnames[colnames.index('xGD/90')] = 'xGD_90'
dataset_ha.columns = colnames

rk_ha = rk_squad.merge(dataset_ha, on=['Rk'])
try:
    rk_ha.to_sql('SquadRecord', conn, if_exists='append', index=False)
except Exception as e:
    print(f'{e.__class__} occured')

res = conn.execute(text('SELECT * FROM SquadRecord'))
print(f'There are {len(res.all())} rows in Table \'SquadRecord\'')



#    'Match'
matches_data = get_matches(url_matches)
# Discarding not finished matches...
matches_data = matches_data[matches_data['MatchID'] != '']
matches_data.fillna('', inplace=True)
try:
    matches_data.to_sql('Match', conn, if_exists='append', index=False)
except Exception as e:
    print(f'{e.__class__} occured')

res = conn.execute(text('SELECT * FROM Match'))
print(f'There are {len(res.all())} rows in Table \'Match\'')


'''
    'Shot'  &   'PlayerMatchStats'  &   'GkMatchStats  &   'Event'
'''

'''
# TODO:
# Iterate in matches_data
res = conn.execute(text('SELECT M.MatchID, M.Home, M.Away FROM Match M WHERE M.MatchID NOT IN \
                        (SELECT E.MatchID FROM Event E)'))

new_matches = [m for m in res.all()]
for nm in new_matches[0:20]:
    id, home, away = nm
    print(id)
    events = parse_match_report(id, home, away)
    try:
        events.to_sql('Event', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e}')
    
    players_raw, shots, gk = process_match_data(id)
    players = clean_players_raw(players_raw)
    try:
        players.to_sql('PlayerMatchStats', conn, if_exists='append', index=False)
        shots.to_sql('Shot', conn, if_exists='append', index=False)
        gk.to_sql('GkMatchStats', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e} occured')
        #print(players, shots, gk)
        res = conn.execute(text('SELECT P.Player FROM Player P'))
        print([x[0] for x in res.all()])
        
    time.sleep(2)
    #print(f'Processed Match {id}')


# Check if select returns any row
#   if so, continue
#   else: parse matchID, Home, Away


# Merge all new data and insert into de database
'''

conn.close()