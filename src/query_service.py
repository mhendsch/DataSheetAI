import sqlite3
import pandas
import schema_manager
import sql_validator



print("What would you like to do today?: ")
user_input = input()
while (user_input.lower() != "q"):
    print("What would you like to do today?: ")
    user_input = input()

    # Call a function depending on input
    # Validate against Database

    # If valid, call LLM Adapter


    # Take input from LLM adapter, create query
    # Format query, make sure AI is not doing anything 
    # it's not supposed to (use SQL validator)


print("\nHave a nice day!")