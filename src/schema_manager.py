import sqlite3
import pandas as pd

# Map pandas datatypes to SQLite datatypes
dtype_mapping = {
    "int64": "INTEGER",
    "float64": "REAL",
    "object": "TEXT",
    "bool": "BOOLEAN",
    "datetime64": "TEXT"
}

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
def generateCreateTableStatement(df, table_name):

    columns = ["id, INTEGER PRIMARY KEY AUTOINCREMENT"]
    for col, dtype in zip(df.columns, df.dtypes):
        sql_type = dtype_map.get(str(dtype), "TEXT")  # Default to TEXT if unknown
        columns.append(f"{col} {sql_type}")

    return f"CREATE TABLE {table_name} ({', '.join(columns)});"

# Gets existing table schema of specific table in db
def getTableSchema(db, table_name):
    # Connect to database and get table schema
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Get table columns
    # Make sure table exists
    cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone()[0] == 0:
        print(f"Table '{table_name}' does not exist.")
        conn.close()
        return 1
    cursor.execute(f"PRAGMA table_info({table_name})")
    temp_columns = cursor.fetchall()
    # Concatenate column names and types
    columns = {row[1]: row[2] for row in temp_columns}
    schema[table_name] = columns
    conn.close()
    return schema

def getDataframeSchema(df):
    # Get column names and datatypes of dataframe and convert to SQLite datatypes
    columns = {}
    for col, dtype in zip(df.columns, df.dtypes):
        sql_type = dtype_mapping.get(str(dtype), "TEXT")  # Default to TEXT if unknown
        columns[col] = sql_type
    return columns

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
    # Create error_log.txt if it doesn't exist, then append error message to it
    if not os.path.exists("error_log.txt"):
        with open("error_log.txt", "w") as f:
            f.write("")
    if not isinstance(error_message, str):
        error_message = str(error_message)
    with open("error_log.txt", "a") as f:
        f.write(error_message + "\n")
    return 0

# Compare schemas of tables
def compareTableSchemas(schema1, schema2):
    return schema1 == schema2


