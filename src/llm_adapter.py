import sqlite3
import pandas
import sql_validator
import schema_manager
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
client = anthropic.Anthropic()


# Generate SQL statement based on user input
def generateSQL(db, input):
    
    if (not isinstance(input, str) or input.strip() == ""):
        print("User input must be a non-empty string. Please provide a valid input.")
        schema_manager.writeError(error_message="User input must be a non-empty string. Please provide a valid input.")
        return ""

    if (not isinstance(db, str) or db.strip() == ""):
        print("Database name must be a non-empty string. Please provide a valid database name.")
        schema_manager.writeError(error_message="Database name must be a non-empty string. Please provide a valid database name.")
        return ""

    table_columns = schema_manager.getDatabaseSchema(db)

    if not table_columns:
        print("Failed to retrieve database schema. Please check the database connection and try again.")
        schema_manager.writeError(error_message="Failed to retrieve database schema. Please check the database connection and try again.")
        return ""
    
    try :
        message = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        system=f"""You are an AI assistant that converts natural language questions into SQLite SQL queries.

            DATABASE SCHEMA:
            {table_columns}

            RULES:
            1. Only generate SELECT queries — never INSERT, UPDATE, DELETE, or DROP.
            2. Only reference tables and columns that exist in the schema above. If the user asks for something that doesn't exist, respond in plain English explaining what's unavailable — do NOT output a ```sql block.
            3. Enclose any column or table name containing special characters (-, spaces, etc.) in double quotes.
            4. Always use SQLite-compatible syntax.
            5. To avoid duplicate rows when joining multiple tables, use correlated subqueries or CTEs instead of multiple LEFT JOINs on the same base table. Example pattern:
            SELECT
                c.company_name,
                (SELECT revenue FROM financials f WHERE f.company_id = c.company_id AND f.fiscal_quarter = 'Q2' LIMIT 1) AS actual_revenue,
                (SELECT forecasted_revenue FROM forecasts fo WHERE fo.company_id = c.company_id AND fo.fiscal_quarter = 'Q2' LIMIT 1) AS forecasted_revenue
            FROM companies c
            6. If a query genuinely requires multiple JOINs, use DISTINCT or GROUP BY to prevent cartesian products.
            7. When using subqueries to retrieve a single value, always use LIMIT 1 to ensure only one row is returned per entity.

            OUTPUT FORMAT:
            ```sql
            <your query here>
            ```
            Explanation: <one or two sentences explaining what the query does>""",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": input
                
            }
        ]
        )
    except Exception as e:
        print(f"Error generating SQL: {e}")
        schema_manager.writeError(error_message=str(e))
        print("\nMake sure to set your ANTHROPIC_API_KEY environment variable to a valid API key from Anthropic.")
        return ""
    
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
            break
        if in_sql_block:
            sql_query += line + "\n"
    return sql_query.strip()

#myResponse = generateSQL("my_database.db", "What do you think alpha-2 means in the countries table? Show me the ones you think would be most interesting.")
#mySQL = stripSQLfromResponse(myResponse)
#print(f"Generated SQL Query:\n{mySQL}")