import sqlite3

sqliteConnection = sqlite3.connect('my_database.db')

cursor = sqliteConnection.cursor()

print("Connected to the database")

sqliteConnection.close()