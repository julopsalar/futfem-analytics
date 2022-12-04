from scraping import *
from xPoints import *

import argparse
import json
import time

# Database connection
import sqlalchemy

url_stats = 'https://fbref.com/en/comps/{}/stats/'
url_rank = 'https://fbref.com/en/comps/{}/'
url_matches = 'https://fbref.com/en/comps/{}/schedule/'


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
        new_indexes = (new.index[~new.apply(
            tuple, 1).isin(old.apply(tuple, 1))].tolist())
        join = dataframe.iloc[new_indexes]
        print(f'old={data.shape},new={dataframe.shape},join={join.shape}')
    except Exception as e:
        print(f'{e.__class__}')
        join = dataframe
        print(f'new={dataframe.shape},join={join.shape}')

    return join


def get_matches(url, league_code):
    """

    """
    matches = get_matches_info(url)
    # Add calculated xPoints
    home_xp, away_xp = calculate_xpoints(
        matches=matches, num_simulations=50000, debug=False)
    matches.loc[:, 'xPHome'] = home_xp
    matches.loc[:, 'xPAway'] = away_xp
    if 'Attendance' in list(matches):
        matches.drop(['Attendance'], axis=1, inplace=True)
    matches.insert(loc=0, column='LeagueID', value=[
                   league_code]*matches.shape[0])
    return matches


def parse_match_data(match_info):
    """

    """
    match_id, home, away = match_info
    shots, players, goalkeepers = get_match_data(match_id, home, away)

    return shots, players, goalkeepers


def update_table(connection, table_name, data, colnames):
    """
    """
    new_data = check_existing_data(connection, table_name, data, colnames)
    new_data.to_sql(table_name, connection, if_exists='append', index=False)
    print(f'Adding {len(new_data)} matches')
    return new_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Football Data Scraping from FBref.com')
    # League
    parser.add_argument('-l', dest='league',
                        action='store', default='230')
    # Database info
    parser.add_argument('-d', dest='db_info',
                        action='store', default='db.json')

    args = parser.parse_args()

    # Create connection from db file info
    with open(args.db_info) as db:
        connection = create_db_connection(json.load(db))

    for l in args.league.split(','):
        matches = get_matches(url=url_matches.format(l), league_code=l)
        new_data = update_table(connection, 'Match', matches, ['MatchID', 'HomeID', 'AwayID'])
        print('Processing league ', l, '...')
        print('\tLoading ', len(new_data), ' matches...')
        if len(new_data):
            matches_to_load = zip(new_data['MatchID'], new_data['HomeID'], new_data['AwayID'])
            events, shots, players, goalkeepers = [], [], [], []
            
            for idx, info in enumerate(matches_to_load):
                
                #e = get_match_events(info[0], info[1], info[2])
                #events.append(e)
                
                s,p,g = parse_match_data(match_info=info)
                shots.append(s)
                players.append(p)
                goalkeepers.append(g)
                time.sleep(4)
                print(info[0], end=',  ')
                
            #new_events = pd.concat(events, axis=0).reset_index(drop=True) 
            new_shots = pd.concat(shots, axis=0).reset_index(drop=True)
            new_players = pd.concat(players, axis=0).reset_index(drop=True)
            new_goalkeepers = pd.concat(goalkeepers, axis=0).reset_index(drop=True)

            #new_data = update_table(connection, 'Event', new_events, ['MatchID','SquadID','Minute','Player1','Player2','Event'])
            #print(len(new_data), end='  ')
            new_data = update_table(connection, 'Shot', new_shots, ['PlayerID','SquadID','SCA1_PlayerID','SCA2_PlayerID','MatchID'])
            print(len(new_data), end='  ')
            new_data = update_table(connection, 'PlayerMatchStats', new_players, ['PlayerID','SquadID','MatchID'])
            print(len(new_data), end='  ')
            new_data = update_table(connection, 'GkMatchStats', new_goalkeepers, ['Player','SquadID','MatchID'])
            print(len(new_data))
    