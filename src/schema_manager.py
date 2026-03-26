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
    return

# Gets existing table schema
def getTableSchema(df):
    return

# Write errors to error_log.txt
def writeError(error_message):
    return

# Compare schemas of tables
def compareTableSchemas(df1, df2):
    return


