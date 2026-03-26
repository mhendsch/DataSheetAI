import sqlite3
import pandas

# Check SQL statement for malicious code
# Only allow SELECT queries
# Reject queries referencing unknown tables
# Reject queries referencing unknown columns
# From Cybersecurity: disallow characters like " or - 
# to prevent SQL injection
def checkSQL(statement):
    return