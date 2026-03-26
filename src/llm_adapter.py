import sqlite3
import pandas
import sql_validator
import schema_manager
import anthropic
import os

client = anthropic.Anthropic()






# Generate SQL statement based on user input
def generateSQL(input):
    message = client.messages.create(
    model = 'claude-haiku-4-5-20251001',
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": """You are an AI assistant tasked with converting user queries into SQL statements. The database uses SQLite and contains the following tables: - sales (sale_id, product_id, quantity, sale_date, revenue) - products (product_id, product_name, category, price) - employees (employee_id, name, department, hire_date) - customers (customer_id, customer_name, location) User Query: "Show me the top 5 products by total revenue this month." Your task is to: 1. Generate a SQL query that accurately answers the user's question. 2. Ensure the SQL is compatible with SQLite syntax. 3. Provide a short comment explaining what the query does. Output Format: - SQL Query - Explanation
            """
        }
    ]
    )
    print(message.content)
    return

