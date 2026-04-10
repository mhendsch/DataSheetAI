import sqlite3
import pytest
import pandas as pd
from csv_loader import createTable, loadCSV, insertData, queryData
import os

# Fixtures:

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_database.db"

@pytest.fixture
def sample_df():
    data = {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "city": ["New York", "Los Angeles", "Chicago"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def populated_db(db_path, sample_df):
    """DB with a pre-created and pre-populated table."""
    createTable(db_path, list(sample_df.columns), "users")
    insertData(db_path, sample_df, "users")
    return db_path

# Tests:

class TestCreateTable:
    def test_create_table_success(self, db_path):
        result = createTable(db_path, ["name", "age"], "users")
        assert result == 0
        # Verify table was created
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_create_table_invalid_columns(self, db_path):
        result = createTable(db_path, "not_a_list", "users")
        assert result == 1

    def test_create_table_empty_columns(self, db_path):
        result = createTable(db_path, [], "users")
        assert result == 1

    def test_create_table_empty_table_name(self, db_path):
        result = createTable(db_path, ["name", "age"], "")
        assert result == 1

    def test_create_table_non_string_table_name(self, db_path):
        result = createTable(db_path, ["name", "age"], 123)
        assert result == 1

    def test_create_table_non_string_column_names(self, db_path):
        result = createTable(db_path, ["name", 123], "users")
        assert result == 1
    
class TestQueryData:
    def test_query_data_success(self, populated_db):
        result = queryData(populated_db, "SELECT name FROM users WHERE age > 28")
        assert isinstance(result, pd.DataFrame)
        assert list(result['name']) == ["Bob", "Charlie"]

    def test_query_data_invalid_query(self, populated_db):
        result = queryData(populated_db, "SELECT non_existent_column FROM users")
        assert result == 1

    def test_query_data_malicious_query(self, populated_db):
        result = queryData(populated_db, "DROP TABLE users;")
        assert result == 1

class TestLoadCSV:
    def test_load_csv_success(self, db_path, sample_df):
        # Create a temporary CSV file
        csv_file = db_path.parent / "test_data.csv"
        sample_df.to_csv(csv_file, index=False)
        # Load CSV into database
        result = loadCSV(str(csv_file))
        assert isinstance(result, pd.DataFrame)  # check type, not integer
        assert list(result.columns) == list(sample_df.columns)
        assert len(result) == len(sample_df)
    
    def test_load_csv_empty_file(self, db_path):
        # Create an empty CSV file
        csv_file = db_path.parent / "empty.csv"
        with open(csv_file, 'w') as f:
            f.write("")
        # Attempt to load empty CSV
        result = loadCSV(str(csv_file))
        assert result == 1

    def test_load_csv_invalid_file(self, db_path):
        # Attempt to load non-existent CSV
        result = loadCSV("non_existent.csv")
        assert result == 1

    def test_load_csv_invalid_file_extension(self, db_path):
        # Create a file with invalid extension
        csv_file = db_path.parent / "invalid.txt"
        with open(csv_file, 'w') as f:
            f.write("name,age,city\nAlice,25,New York\nBob,30,Los Angeles\nCharlie,35,Chicago")
        # Attempt to load invalid file
        result = loadCSV(str(csv_file))
        assert result == 1
