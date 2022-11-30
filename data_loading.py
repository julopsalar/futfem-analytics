from scraping import *
from xPoints import *

import argparse
import json
import time

# Database connection
import sqlalchemy
from sqlalchemy import text

url_stats = 'https://fbref.com/en/comps/230/stats/Liga-F-Stats'
url_rank = 'https://fbref.com/en/comps/230/Liga-F-Stats'
url_matches = 'https://fbref.com/en/comps/230/schedule/Liga-F-Scores-and-Fixtures'


def create_db_connection(args):
    """
    Creates a connection to the database specified in args
    :return: Returns the active connection
    """
    username = args['username']
    password = args['password']
    server = args['server']
    database = args['database']

    engine = sqlalchemy.create_engine(
        f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server&Trusted_Connection=yes')
    conn = engine.connect()
    return conn

def check_existing_data(conn, table_name, dataframe, colnames):
    try:
        data = pd.read_sql_table(table_name=table_name, con=conn)
        
        new = dataframe[colnames]
        old = data[colnames]
        new_indexes = (new.index[~new.apply(tuple,1).isin(old.apply(tuple,1))].tolist())
        #print(new_indexes)
        join = dataframe.iloc[new_indexes]
        
        print(f'old={data.shape},new={dataframe.shape},join={join.shape}')
    except Exception as e:
        print(f'{e.__class__}')
        join = dataframe   
        print(f'new={dataframe.shape},join={join.shape}')

    
    return join


def get_matches(url):
    """
    
    """
    matches = get_matches_info(url)
    # Add calculated xPoints
    home_xp, away_xp = calculate_xpoints(matches=matches, num_simulations=50000, debug=False)
    matches.loc[:,'xPHome'] = home_xp
    matches.loc[:,'xPAway'] = away_xp

    return matches


def parse_match_data(match_info):

    match_id, home, away = match_info
    shots, players, goalkeepers = get_match_data(match_id, home, away)
    
    
    return shots, players, goalkeepers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Football Data Scraping from FBref.com')
    # Squad
    parser.add_argument('-s', dest='squads',
                        action=argparse.BooleanOptionalAction, default=False)
    # Matches & PlayerStat & GkStat & Events & Shots
    parser.add_argument('-m', dest='matches',
                        action=argparse.BooleanOptionalAction, default=False)
    # Database info
    parser.add_argument('-d', dest='db_info',
                        action='store', default='db.json')
    # All
    parser.add_argument(
        '-a', dest='all', action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    if not (args.squads | args.matches | args.all):
        print('No data to update...')
    else:
        # Create connection from db file info
        
        with open(args.db_info) as db:
            connection = create_db_connection(json.load(db))
        
        matches = get_matches(url=url_matches)
        #matches.to_csv('new_matches.csv', index=False)
        #print(matches.head())
        new_matches = check_existing_data(connection, 'Match', matches, ['MatchID', 'HomeID', 'AwayID'])
        #print(new_matches.shape)
        #new_matches = new_matches.iloc[:5,:]
        new_matches.to_sql('Match', connection, if_exists='append', index=False)

        print(f'Adding {len(new_matches)} matches')
        if len(new_matches):
            matches_to_load = zip(new_matches['MatchID'], new_matches['HomeID'], new_matches['AwayID'])
            events, shots, players, goalkeepers = [], [], [], []
            
            for idx, info in enumerate(matches_to_load):
                
                e = get_match_events(info[0], info[1], info[2])
                events.append(e)
                time.sleep(3)
                
                s,p,g = parse_match_data(match_info=info)
                shots.append(s)
                players.append(p)
                goalkeepers.append(g)
                time.sleep(4)
                print(info[0])
                
            new_events = pd.concat(events, axis=0).reset_index(drop=True) 
            new_shots = pd.concat(shots, axis=0).reset_index(drop=True)
            new_players = pd.concat(players, axis=0).reset_index(drop=True)
            new_goalkeepers = pd.concat(goalkeepers, axis=0).reset_index(drop=True)

            new_events = check_existing_data(connection, 'Event', new_events, ['MatchID','SquadID','Minute','Player1','Player2','Event'])
            new_events.to_sql('Event', connection, if_exists='append', index=False)
            #new_events.to_csv('new_events.csv', index=False)
            new_shots = new_shots[new_shots['xG'] != '']
            new_shots = check_existing_data(connection, 'Shot', new_shots, ['PlayerID','SquadID','SCA1_PlayerID','SCA2_PlayerID','MatchID'])
            new_shots.to_sql('Shot', connection, if_exists='append', index=False)
            #new_shots.to_csv('new_shots.csv', index=False)
            new_players = check_existing_data(connection, 'PlayerMatchStats', new_players, ['PlayerID','SquadID','MatchID'])
            new_players.to_sql('PlayerMatchStats', connection, if_exists='append', index=False)        
            #new_players.to_csv('new_players.csv', index=False)
            
            new_goalkeepers = check_existing_data(connection, 'GkMatchStats', new_goalkeepers, ['Player','SquadID','MatchID'])
            new_goalkeepers.to_sql('GkMatchStats', connection, if_exists='append', index=False)
            #new_goalkeepers.to_csv('new_gk.csv', index=False)
            