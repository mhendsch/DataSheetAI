import sqlite3
import pandas as pd
import os
from schema_manager import getDataframeSchema, getDatabaseSchema, generateCreateTableStatement, writeError, compareTableSchemas, getTableSchema
import pytest

# Fixtures
@pytest.fixture
def sample_df():
    """DataFrame covering all mapped dtype branches."""
    return pd.DataFrame({
        "name":      pd.Series(["Alice"], dtype="object"),
        "age":       pd.Series([30],      dtype="int64"),
        "score":     pd.Series([9.5],     dtype="float64"),
        "active":    pd.Series([True],    dtype="bool"),
        "joined":    pd.to_datetime(["2024-01-01"]),
    })

@pytest.fixture
def special_char_df():
    """DataFrame whose column names contain spaces and special characters."""
    return pd.DataFrame({"first name": ["Bob"], "order #": [1]})

@pytest.fixture
def temp_db(tmp_path):
    """Path to a fresh, empty SQLite database file."""
    return str(tmp_path / "test.db")

@pytest.fixture
def populated_db(tmp_path):
    """SQLite db with one table ('users') already created."""
    db_path = str(tmp_path / "populated.db")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        '"name" TEXT, "age" INTEGER)'
    )
    conn.commit()
    conn.close()
    return db_path

@pytest.fixture(autouse=False)
def isolated_error_log(tmp_path, monkeypatch):
    """Redirect writeError's file path to a temp directory."""
    monkeypatch.chdir(tmp_path)
    yield tmp_path / "error_log.txt"

# Tests

class TestgetDataframeSchema:

    def test_get_dataframe_schema(self, sample_df):
        expected_schema = {
            "name": "TEXT",
            "age": "INTEGER",
            "score": "REAL",
            "active": "BOOLEAN",
            "joined": "DATE"
        }
        assert getDataframeSchema(sample_df) == expected_schema

    @pytest.mark.parametrize("col,dtype,expected_sql", [
        ("name",   "object",          "TEXT"),
        ("age",    "int64",           "INTEGER"),
        ("score",  "float64",         "REAL"),
        ("active", "bool",            "BOOLEAN"),
    ])
    def test_dtype_mapping(self, col, dtype, expected_sql):
        if dtype == "int64":
            df = pd.DataFrame({col: pd.Series([1], dtype="int64")})
        elif dtype == "float64":
            df = pd.DataFrame({col: pd.Series([1.0], dtype="float64")})
        elif dtype == "bool":
            df = pd.DataFrame({col: pd.Series([True], dtype="bool")})
        else:
            df = pd.DataFrame({col: ["x"]})
        result = getDataframeSchema(df)
        assert result[col] == expected_sql

    def test_empty_dataframe_returns_empty_dict(self):
        df = pd.DataFrame()
        result = getDataframeSchema(df)
        assert result == {}

    def test_multiple_columns_all_mapped(self, sample_df):
        result = getDataframeSchema(sample_df)
        assert result["name"]   == "TEXT"
        assert result["age"]    == "INTEGER"
        assert result["score"]  == "REAL"
        assert result["active"] == "BOOLEAN"
        assert result["joined"] == "DATE"

class TestgetDatabaseSchema:
    def test_returns_all_user_tables(self, populated_db):
        schema = getDatabaseSchema(populated_db)
        assert "users" in schema

    def test_excludes_sqlite_internal_tables(self, tmp_path):
        """sqlite_sequence is created after an AUTOINCREMENT insert."""
        db = str(tmp_path / "seq.db")
        conn = sqlite3.connect(db)
        conn.execute(
            "CREATE TABLE items "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT)"
        )
        conn.execute("INSERT INTO items (label) VALUES ('x')")
        conn.commit()
        conn.close()
        schema = getDatabaseSchema(db)
        assert not any(k.startswith("sqlite_") for k in schema)

    def test_empty_database_returns_empty_dict(self, temp_db):
        schema = getDatabaseSchema(temp_db)
        assert schema == {}

    def test_multiple_tables_all_present(self, tmp_path):
        db = str(tmp_path / "multi.db")
        conn = sqlite3.connect(db)
        conn.execute('CREATE TABLE alpha (id INTEGER, val TEXT)')
        conn.execute('CREATE TABLE beta  (id INTEGER, num REAL)')
        conn.commit()
        conn.close()
        schema = getDatabaseSchema(db)
        assert "alpha" in schema
        assert "beta"  in schema

    def test_column_types_correct_in_full_schema(self, tmp_path):
        db = str(tmp_path / "typed.db")
        conn = sqlite3.connect(db)
        conn.execute('CREATE TABLE data (x INTEGER, y REAL, z TEXT)')
        conn.commit()
        conn.close()
        schema = getDatabaseSchema(db)
        assert schema["data"]["x"] == "INTEGER"
        assert schema["data"]["y"] == "REAL"
        assert schema["data"]["z"] == "TEXT"

class TestgenerateCreateTableStatement:
    def test_generate_create_table_statement(self, sample_df):
        expected_statement = 'CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "age" INTEGER, "score" REAL, "active" BOOLEAN, "joined" DATE);'
        assert generateCreateTableStatement(sample_df, "test_table") == expected_statement

    def test_generate_create_table_statement_special_characters(self, special_char_df):
        expected_statement = 'CREATE TABLE IF NOT EXISTS special_table (id INTEGER PRIMARY KEY AUTOINCREMENT, "first name" TEXT, "order #" INTEGER);'
        assert generateCreateTableStatement(special_char_df, "special_table") == expected_statement

    def test_contains_create_table_if_not_exists(self, sample_df):
        sql = generateCreateTableStatement(sample_df, "users")
        assert sql.upper().startswith("CREATE TABLE IF NOT EXISTS")

    def test_table_name_in_statement(self, sample_df):
        sql = generateCreateTableStatement(sample_df, "my_table")
        assert "my_table" in sql

    def test_primary_key_autoincrement(self, sample_df):
        sql = generateCreateTableStatement(sample_df, "users")
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in sql

    def test_correct_sql_types_present(self, sample_df):
        sql = generateCreateTableStatement(sample_df, "users")
        assert "INTEGER" in sql
        assert "REAL"    in sql
        assert "TEXT"    in sql
        assert "BOOLEAN" in sql

    def test_special_characters_in_column_names_quoted(self, special_char_df):
        sql = generateCreateTableStatement(special_char_df, "orders")
        assert '"first name"' in sql
        assert '"order #"'    in sql

    def test_statement_ends_with_semicolon(self, sample_df):
        sql = generateCreateTableStatement(sample_df, "users")
        assert sql.strip().endswith(";")

class TestCompareTableSchemas:
    def test_identical_schemas_return_true(self):
        s = {"users": {"id": "INTEGER", "name": "TEXT"}}
        assert compareTableSchemas(s, s) is True

    def test_different_schemas_return_false(self):
        s1 = {"users": {"id": "INTEGER"}}
        s2 = {"users": {"id": "TEXT"}}
        assert compareTableSchemas(s1, s2) is False

    def test_empty_schemas_return_true(self):
        assert compareTableSchemas({}, {}) is True

    def test_different_keys_return_false(self):
        s1 = {"users": {"id": "INTEGER"}}
        s2 = {"orders": {"id": "INTEGER"}}
        assert compareTableSchemas(s1, s2) is False

    def test_extra_column_in_one_schema_returns_false(self):
        s1 = {"t": {"id": "INTEGER", "name": "TEXT"}}
        s2 = {"t": {"id": "INTEGER"}}
        assert compareTableSchemas(s1, s2) is False

class TestWriteError:

    def test_creates_file_if_not_exists(self, isolated_error_log):
        assert not isolated_error_log.exists()
        writeError("boom")
        assert isolated_error_log.exists()

    def test_message_written_to_file(self, isolated_error_log):
        writeError("something went wrong")
        assert "something went wrong" in isolated_error_log.read_text()

    def test_appends_multiple_messages(self, isolated_error_log):
        writeError("first error")
        writeError("second error")
        content = isolated_error_log.read_text()
        assert "first error"  in content
        assert "second error" in content

    def test_non_string_input_converted(self, isolated_error_log):
        writeError(404)
        assert "404" in isolated_error_log.read_text()

    def test_returns_zero(self, isolated_error_log):
        result = writeError("any message")
        assert result == 0

class TestGetTableSchema:

    def test_existing_table_returns_schema_dict(self, populated_db):
        result = getTableSchema(populated_db, "users")
        assert isinstance(result, dict)
        assert "users" in result

    def test_schema_contains_correct_columns(self, populated_db):
        schema = getTableSchema(populated_db, "users")
        assert "name" in schema["users"]
        assert "age"  in schema["users"]

    def test_schema_has_correct_types(self, populated_db):
        schema = getTableSchema(populated_db, "users")
        assert schema["users"]["name"] == "TEXT"
        assert schema["users"]["age"]  == "INTEGER"

    def test_missing_table_returns_1(self, temp_db):
        result = getTableSchema(temp_db, "nonexistent")
        assert result == 1

    def test_schema_key_matches_table_name(self, populated_db):
        result = getTableSchema(populated_db, "users")
        assert list(result.keys()) == ["users"]