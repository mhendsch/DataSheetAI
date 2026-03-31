import sqlite3
import pandas
import sql_validator
import schema_manager
import anthropic
import os

client = anthropic.Anthropic()


# Generate SQL statement based on user input
def generateSQL(db, input):
    # Get tables in db
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # Filter for sql_sequence, which is not created by user
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]

    # Get columns in each table
    table_columns = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        temp_columns = cursor.fetchall()
        columns = {row[1]: row[2] for row in temp_columns}
        table_columns[table] = columns

    print(table_columns)

    
    message = client.messages.create(
    model = 'claude-haiku-4-5-20251001',
    system=f"""You are an AI assistant tasked with converting user queries into SQL statements. The database uses SQLite and contains the following tables and columns: {table_columns}. Your task is to: 1. Generate a SQL query that accurately answers the user's question. 2. Ensure the SQL is compatible with SQLite syntax. 3. Provide a short comment explaining what the query does. Output Format: - SQL Query - Explanation""",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": input
            
        }
    ]
    )
    
    # Print the text of the message (for debugging purposes only))
    print(f"{message.content[0].text}")
    return message.content[0].text
    

generateSQL("my_database.db", "Show me the color with the highest hex value in the colors table.")
