import pandas as pd

# SQL Server Database Connection
import pyodbc 
server = 'DESKTOP-B2GO7GM'
database = 'football_v0' 
username = 'juanlop' 
password = '1234' # really safe password :)

try:
    cnxn = pyodbc.connect(driver='{SQL Server}', host=server, database=database,
                      trusted_connection='yes', user=username, password=password)
    cursor = cnxn.cursor()
except Exception as ex:
    print(ex)

# If connection established
if cursor:
    # Read Squads info and insert into tables
    data = pd.read_csv('..\images.csv')
    # Drop if data was previously on the database
    cursor.execute('DELETE FROM Squad')
    for index, row in data.iterrows():
        cursor.execute("INSERT INTO Squad (Squad,URL) values(?,?)", row.Squad, row.URL)
    cnxn.commit()
    # Show data stored
    cursor.execute("SELECT * FROM Squad") 
    row = cursor.fetchone() 
    while row: 
        print('--> '.join(row))
        row = cursor.fetchone()
    print('--------\n')


cursor.close()
cnxn.close()
print('Closed connection')