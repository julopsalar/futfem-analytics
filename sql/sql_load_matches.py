# Web Scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# SQL Server Database Connection
import pyodbc 
server = 'DESKTOP-B2GO7GM'
database = 'football_v0' 
username = 'juanlop' 
password = '1234' # really safe password :)


# Liga F fixtures and matches
url_matches = 'https://fbref.com/en/comps/230/schedule/Liga-F-Scores-and-Fixtures'

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

# Connecting to the database
try:
    cnxn = pyodbc.connect(driver='{SQL Server}', host=server, database=database,
                    trusted_connection='yes', user=username, password=password)
    cursor = cnxn.cursor()
except Exception as ex:
    print(ex)

# Get the data
matches_data = get_matches(url_matches)
# Discarding not finished matches...
matches_data = matches_data[matches_data['MatchID'] != '']
matches_data.fillna('', inplace=True)
new_rows = 0
for index, row in matches_data.iterrows():
    # Check if row already exists
    cursor.execute(f"SELECT M.MatchID FROM Match M \
            WHERE M.MatchID = \'{row.MatchID}\'")
    # If not exists, insert the row
    if not cursor.fetchone():
        cursor.execute("INSERT INTO Match (MatchID,Wk,Day,Date,Time,Home,xG_Home,Score,xG_Away,\
            Away,Attendance,Venue,Referee,MatchReport,Notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", \
            row.MatchID, row.Wk, row.Day, row.Date, row.Time, row.Home, row.xG_Home, row.Score, \
            row.xG_Away, row.Away, row.Attendance, row.Venue, row.Referee, row.MatchReport, row.Notes)
        new_rows += 1
cnxn.commit()

print(f'Added {new_rows} matches to the database')