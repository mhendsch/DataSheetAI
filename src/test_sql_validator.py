import sqlite3
import pandas as pd
from sql_validator import checkSQL
import pytest
import os


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_database.db"


class TestCheckSQL:
    def test_valid_sql(self, db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        valid_query = "SELECT * FROM users"
        assert checkSQL(str(db_path), valid_query) == 0

    def test_invalid_sql(self, db_path):
        invalid_query = "SELEC * FRM users"  # Misspelled SELECT and FROM
        assert checkSQL(str(db_path), invalid_query) == 1

    def test_nonexistent_table(self, db_path):
        query = "SELECT * FROM non_existent_table"
        assert checkSQL(str(db_path), query) == 1

    def test_empty_query(self, db_path):
        empty_query = ""
        assert checkSQL(str(db_path), empty_query) == 1
    
    def test_non_string_query(self, db_path):
        non_string_query = 12345
        assert checkSQL(str(db_path), non_string_query) == 1
    
    def test_valid_sql_with_syntax_error(self, db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        query_with_syntax_error = "SELECT FROM users"  # Missing columns to select
        assert checkSQL(str(db_path), query_with_syntax_error) == 1
    
    def test_valid_sql_with_nonexistent_column(self, db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        query_with_nonexistent_column = "SELECT age FROM users"  # 'age' column does not exist
        assert checkSQL(str(db_path), query_with_nonexistent_column) == 1


    