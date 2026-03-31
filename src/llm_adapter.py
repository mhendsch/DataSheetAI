import sqlite3
import pandas
import sql_validator
import schema_manager
import anthropic
import os

client = anthropic.Anthropic()


# Generate SQL statement based on user input
def generateSQL(db, input):
    
    table_columns = schema_manager.getDatabaseSchema(db)
    print(table_columns)
    
    message = client.messages.create(
    model = 'claude-haiku-4-5-20251001',
    system=f"""You are an AI assistant tasked with converting user queries into SQL statements. The database uses SQLite and contains the following tables and columns: {table_columns}. Your task is to: 1. Generate a SQL query that accurately answers the user's question. 2. Ensure the SQL is compatible with SQLite syntax. 3. Only allow SELECT queries. 4. If the user asks for information from a table or column that doesn't exist, do NOT put '''sql in your response, as that is used to indicate a SQL block in your response. 5. Provide a short comment explaining what the query does. Output Format: - SQL Query - Explanation""",
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

def stripSQLfromResponse(response):
    """ Format: '''sql 
    SQL QUERY;
    '''
    """
    # Split response into lines and find the line that starts with "```sql"
    lines = response.splitlines()
    sql_query = ""
    in_sql_block = False
    for line in lines:
        if line.strip().startswith("```sql"):
            in_sql_block = True
            continue
        elif line.strip().startswith("```") and in_sql_block:
            in_sql_block = False
            continue
        if in_sql_block:
            sql_query += line + "\n"
    return sql_query

myResponse = generateSQL("my_database.db", "Count how many students are in the class.")
mySQL = stripSQLfromResponse(myResponse)
print(f"Generated SQL Query:\n{mySQL}")