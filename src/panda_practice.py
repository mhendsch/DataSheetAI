import sqlite3
import pandas as pd

#sqliteConnection = sqlite3.connect('my_database.db')

#cursor = sqliteConnection.cursor()

#print("Connected to the database")


# SQL command
#sql_command = """CREATE TABLE users(
#id INTEGER PRIMARY KEY AUTOINCREMENT,
#name TEXT
#);
#"""
# Read CSV file and convert to DataFrame
def readCSV(filename): 
    df = pd.read_csv(filename)
    return df

# Extract column names from DataFrame
def extractColumns(df):
    return df.columns.tolist()

# Insert DataFrame into SQLite database
def insertData(df, table_name):
    sqliteConnection = sqlite3.connect('my_database.db')
    cursor = sqliteConnection.cursor()
    
    # Create table if it doesn't exist
    columns = extractColumns(df)
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col + ' TEXT' for col in columns])});"
    cursor.execute(create_table_query)
    
    # Insert data into table
    for index, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])});"
        cursor.execute(insert_query, tuple(row))
    
    sqliteConnection.commit()
    sqliteConnection.close()
    print("Data inserted successfully")
    print("Exited properly")

# execute command
try:
    my_data = readCSV('colors.csv')
    insertData(my_data, 'colors')
except Exception as e:
    print(f"Unexpected Error: {e} ")

#sqliteConnection.close()
#print("Exited properly")

