import sqlite3
import pandas
import csv_loader
import llm_adapter
import schema_manager
import sql_validator

DB = "my_database.db"

def loadData(filename, table_name):
    df = csv_loader.loadCSV(filename)


    csv_schema = schema_manager.getDataframeSchema(df)
    db_schema = schema_manager.getDatabaseSchema(DB)
    # print(f"\nCSV Schema: {csv_schema}")
    # print(f"\nDatabase Schema: {db_schema}")
    # Compare schemas, see if any match, if so append instead of creating new table
    for table, columns in db_schema.items():
        # Strip id from schema for comparison, since it is added automatically and won't be in the CSV schema
        columns_without_id = {k: v for k, v in columns.items() if k != "id"}
        if columns_without_id == csv_schema:
            print(f"Schema of CSV file matches existing table '{table}'. Appending data to this table.")
            csv_loader.insertData(DB, df, table)
            return 0
    # If no matching schema, create new table and insert data
    print(f"No existing table matches the schema of the CSV file. Creating new table '{table_name}' and inserting data.")
    # Have to use sqlite3 here because createTable doesn't preserve types
    create_table_statement = schema_manager.generateCreateTableStatement(df, table_name)
    # print(f"\nGenerated CREATE TABLE statement:\n{create_table_statement}")
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
        print("\nLLM did not generate a SQL query. Please try rephrasing your question.")
        # print(f"LLM Response:\n{response}")
        return None
    
    results = csv_loader.queryData(DB, sql_query.strip())
    if isinstance(results, int) and results == 1:
        print("Query failed validation. Please try rephrasing your question.")
        return None
    
    return results

def main():
    loadData("country_full.csv", "countries")
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
        
        results = askLLM(user_input)
        if results is not None:
            print(f"\nQuery Results:\n{results}")


    print("\nHave a nice day!")

if __name__ == "__main__":
    main()
