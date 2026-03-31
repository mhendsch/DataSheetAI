import sqlite3
import pandas
import sql_validator
import schema_manager
import anthropic
import os

client = anthropic.Anthropic()


# Generate SQL statement based on user input
def generateSQL(db, df, input):
    # Get tables in db
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    message = client.messages.create(
    model = 'claude-haiku-4-5-20251001',
    system="""You are an AI assistant tasked with converting user queries into SQL statements. The database uses SQLite and contains the following tables: - sales (sale_id, product_id, quantity, sale_date, revenue) - products (product_id, product_name, category, price) - employees (employee_id, name, department, hire_date) - customers (customer_id, customer_name, location). Your task is to: 1. Generate a SQL query that accurately answers the user's question. 2. Ensure the SQL is compatible with SQLite syntax. 3. Provide a short comment explaining what the query does. Output Format: - SQL Query - Explanation""",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": input
            
        }
    ]
    )
    # Print the text of the message
    print(f"{message.content[0].text}")
    return

generateSQL("Show me the top 5 products by total revenue in the last month.")
