import sqlite3
import pandas

# Check SQL statement for malicious code
# Only allow SELECT queries
# Reject queries referencing unknown tables
# Reject queries referencing unknown columns
# From Cybersecurity: disallow characters like " or - 
# to prevent SQL injection
def checkSQL(statement):
    # Check for malicious characters
    if any(char in statement for char in ['"', "'", ';', '--']):
        print("Query contains potentially malicious characters. Please provide a valid SQL query.")
        return 1
    # Only allow SELECT queries
    if not statement.strip().lower().startswith('select'):
        print("Only SELECT queries are allowed.")
        return 1
    # Check for unknown tablses and columns
    

    return 0

""" 
OTHER REQUIREMENTS:
You must demonstrate at least one case where:
    - The LLM-generated code was incorrect
    - Your tests caught the issue
    - You refined the implementation
"""