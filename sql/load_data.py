from scraping import *
import time
import argparse
import json

# Database connection
import sqlalchemy
from sqlalchemy import text

url_stats = 'https://fbref.com/en/comps/230/stats/Liga-F-Stats'
url_rank = 'https://fbref.com/en/comps/230/Liga-F-Stats'
url_matches = 'https://fbref.com/en/comps/230/schedule/Liga-F-Scores-and-Fixtures'


def create_db_connection(args):
    username = args['username']
    password = args['password']
    server = args['server']
    database = args['database']

    engine = sqlalchemy.create_engine(
        f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server&Trusted_Connection=yes')
    conn = engine.connect()
    return conn

#    Loading 'Squad' table data
def load_squads(conn, file='..\images.csv'):
    data = pd.read_csv(file)
    # Drop if data was previously on the database
    try:
        data.to_sql('Squad', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e.__class__} occured')

    existing_data = pd.read_sql_table('Squad', conn)
    print(f'Table \'Squad\': ', existing_data.shape)


def load_squads_rank(conn, url_rank):

    rank_ha = get_rank(url_rank)
    try:
        rank_ha.to_sql('SquadRecord', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e.__class__} occured')

    existing_data = pd.read_sql_table('SquadRecord', conn)
    print(f'Table \'SquadRecord\': ', existing_data.shape)


def load_players(conn, url):
    players = get_players(url)

    try:
        players.to_sql('Player', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e.__class__} occured')

    existing_data = pd.read_sql_table('Player', conn)
    print(f'Table \'Player\': ', existing_data.shape)


def load_matches(conn, url_match):
    matches_data = get_matches(url_match, ['matches', 'squads'])
    matches_data = matches_data[matches_data['MatchID'] != '']

    try:
        matches_data.to_sql('Match', conn, if_exists='append', index=False)
    except Exception as e:
        print(f'{e.__class__} occured')

    existing_data = pd.read_sql_table('Match', conn)
    print(f'Table \'Match\': ', existing_data.shape)

    res = conn.execute(text('SELECT M.MatchID, M.Home, M.Away FROM Match M WHERE M.MatchID NOT IN \
                            (SELECT E.MatchID FROM Event E)'))

    new_matches = [m for m in res.all()]

    for nm in new_matches:
        id, home, away = nm

        events = get_match_events(id, home, away)
        try:
            events.to_sql('Event', conn, if_exists='append', index=False)
        except Exception as e:
            print(f'{e.__class__}')
            print('Error processing match ', id)
            continue

        players, gk, shots = process_match_data(id, home, away)
        #print('\tINTEGER, \n\t'.join(players.columns))
        #players = clean_players_raw(players_raw)
        try:
            players.replace('', 0, inplace=True)
            players.to_sql('PlayerMatchStats', conn,
                           if_exists='append', index=False)
            print('players')
            # shots.to_csv('shots.csv')
            shots.to_sql('Shot', conn, if_exists='append', index=False)
            print('shots')
            gk.to_sql('GkMatchStats', conn, if_exists='append', index=False)
            print('gk')
        except Exception as e:
            print(f'{e.__class__} occured')
            #res = conn.execute(text('SELECT P.Player FROM Player P'))
            #print([x[0] for x in res.all()])

        time.sleep(9)
        print(f'Processed Match {id}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Football Data Scraping from FBref.com')
    # Squad + SquadRecord
    parser.add_argument('-s', dest='squads',
                        action=argparse.BooleanOptionalAction, default=False)
    # Players data
    parser.add_argument('-p', dest='players',
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

    if not (args.squads | args.players | args.matches | args.all):
        print('No data to update...')
    else:
        # Create connection from db file info
        with open(args.db_info) as db:
            connection = create_db_connection(json.load(db))
        # Squad & SquadRank
        if args.squads | args.all:
            load_squads(conn=connection)
            load_squads_rank(conn=connection, url_rank=url_rank)
        # Player
        if args.players | args.all:
            load_players(conn=connection, url=url_stats)
        # Match & Shot & PlayerMatchStat & GkMatchStat
        if args.matches | args.all:
            load_matches(conn=connection, url_match=url_matches)
