import sqlite3
import pandas
import schema_manager
import sql_validator

DB = "my_database.db"

def loadData(filename, table_name):
    df = csv_loader.loadCSV(filename)


    csv_schema = schema_manager.getDataframeSchema(df)
    db_schema = schema_manager.getDatabaseSchema(DB)
    # Compare schemas, see if any match, if so append instead of creating new table
    for table, columns in db_schema.items():
        if columns == csv_schema:
            print(f"Schema of CSV file matches existing table '{table}'. Appending data to this table.")
            csv_loader.insertData(DB, df, table)
            return 0
    # If no matching schema, create new table and insert data
    print(f"No existing table matches the schema of the CSV file. Creating new table '{table_name}' and inserting data.")
    # Have to use sqlite3 here because createTable doesn't preserve types
    create_table_statement = schema_manager.generateCreateTableStatement(df, table_name)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(create_table_statement)
    conn.commit()
    conn.close()
    csv_loader.insertData(DB, df, table_name)
    return 0

def askLLM(user_input):
    response = llm_adapter.generateSQL(DB, user_input)
    sql_query = llm_adapter.stripSQLfromResponse(response)

    if not sql_query.strip():
        print("LLM did not generate a SQL query. Please try rephrasing your question.")
        print(f"LLM Response:\n{response}")
        return None
    
    results = csv_loader.queryData(DB, sql_query.strip())
    if isinstance(results, int) and results == 1:
        print("Query failed validation. Please try rephrasing your question.")
        return None
    
    return results

def main():
    loadData("countries.csv", "countries")
    loadData("colors.csv", "colors")

    print("\nDatasheet AI. Type 'q' to quit.")
    user_input = ""
    while (user_input.lower() != "q"):
        user_input = input("\nEnter your query (q to quit): ").strip()
        if user_input.lower() == "q":
            break
        if not user_input:
            print("\nInput cannot be empty. Please enter a valid query.")
            continue
        
        

        # Call a function depending on input
        # Validate against Database

        # If valid, call LLM Adapter


        # Take input from LLM adapter, create query
        # Format query, make sure AI is not doing anything 
        # it's not supposed to (use SQL validator)


    print("\nHave a nice day!")

if __name__ == "__main__":
    main()
