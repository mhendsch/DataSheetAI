import sqlite3
import pandas as pd

# Prints information about panda dataframe
def inspectTable(df):
    print("Table Schema:")
    print(f"Column names: \n  {df.columns.tolist()}")
    print(f"Column datatypes:\n{df.dtypes}")
    return

# Converts file to panda dataframe
def readTable(filename):
    return pd.read_csv(filename)

# Generate SQL statement
# Should have a PRIMARY KEY AUTOINCREMENT
def generateCreateTableStatement(df):

    columns = [""]
    return

# Gets existing table schema of specific table in db
def getTableSchema(db, table_name):

    return schema

# Gets table schema of entire database
def getDatabaseSchema(db):
    # Get tables in db
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # Filter for sql_sequence, which is not created by user
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]

    # Get columns in each table
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        temp_columns = cursor.fetchall()
        columns = {row[1]: row[2] for row in temp_columns}
        schema[table] = columns
    conn.close()
    return schema

# Write errors to error_log.txt
def writeError(error_message):
    return

# Compare schemas of tables
def compareTableSchemas(df1, df2):
    return


