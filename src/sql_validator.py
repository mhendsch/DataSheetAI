import sqlite3
import pandas

# Check SQL statement for malicious code
# Only allow SELECT queries
# Reject queries referencing unknown tables
# Reject queries referencing unknown columns
# From Cybersecurity: disallow characters like " or - 
# to prevent SQL injection
def checkSQL(db, statement):
    # Check for malicious characters
    if any(char in statement for char in ['"', "'", ';', '--']):
        print("Query contains potentially malicious characters. Please provide a valid SQL query.")
        return 1
    # Only allow SELECT queries
    if not statement.strip().lower().startswith('select'):
        print("Only SELECT queries are allowed.")
        return 1
    # Check for unknown tables and columns
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Get list of tables in database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    # Check if query references unknown tables
    contains_known_table = any(table in statement for table in tables)
    if not contains_known_table:
        print("Query references unknown tables.")
        conn.close()
        return 1
    # Check if referencing unknown columns
    contains_known_columns = False
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if any(column in statement for column in columns):
            contains_known_columns = True
            break
    if not contains_known_columns:
        print("Query references unknown columns.")
        conn.close()
        return 1    

    return 0


""" 
OTHER REQUIREMENTS:
You must demonstrate at least one case where:
    - The LLM-generated code was incorrect
    - Your tests caught the issue
    - You refined the implementation
"""