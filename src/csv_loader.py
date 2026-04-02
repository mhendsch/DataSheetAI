import sqlite3
import pandas as pd
import sql_validator
import schema_manager



# Manually create a table in SQLite
def createTable(db, columns, table_name):
    # Error check user input
    if (not isinstance(columns, list) or len(columns) == 0):
        print("Columns must be a non-empty list. Please provide a valid list of columns.")
        return 1
    if (table_name == ""):
        print("Table name is empty. Please provide a valid table name.")
        return 1
    if (not isinstance(table_name, str)):
        print("Table name must be a string. Please provide a valid table name.")
        return 1
    if (not all(isinstance(col, str) for col in columns)):
        print("All column names must be strings. Please provide a valid list of column names.")
        return 1
    # Connect to database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Create table with specified columns of TEXT type
    columns_with_types = ', '.join([f"{col} TEXT" for col in columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})")
    conn.commit()
    conn.close()
    return 0

# Load CSV file into pandas dataframe
def loadCSV(filename):
    return pd.read_csv(filename)

# Insert data from pandas dataframe into SQLite table
# Constraints: Cannot use .to_sql() method, must use SQL INSERT statements
def insertData(db, df, table_name):
    # Error check user input
    if (df.empty):
        print("DataFrame is empty. No data to insert.")
        return 1
    if (table_name == ""):
        print("Table name is empty. Please provide a valid table name.")
        return 1
    if (not isinstance(table_name, str)):
        print("Table name must be a string. Please provide a valid table name.")
        return 1
    if (not isinstance(df, pd.DataFrame)):
        print("Input data must be a pandas DataFrame. Please provide a valid DataFrame.")
        return 1
    if (len(df.columns) == 0):
        print("DataFrame has no columns. Please provide a DataFrame with columns.")
        return 1
    # Connect to SQLite database and insert data    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Check to make sure table exists
    cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone()[0] == 0:
        print(f"Table '{table_name}' does not exist.")
        conn.close()
        return 1

    # Insert into table
    for index, row in df.iterrows():
        placeholders = ', '.join(['?'] * len(row))
        columns = ', '.join([f'"{col}"' for col in df.columns])
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", tuple(row))

    conn.commit()
    conn.close()

    return 0

# Query data from SQLite table and return as pandas dataframe
def queryData(db, query):
    conn = sqlite3.connect(db)
    # Error check query
    if (sql_validator.checkSQL(db, query) == 1):
        print("Query failed validation. Please provide a valid SQL query.")
        conn.close()
        return 1
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
