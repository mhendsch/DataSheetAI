import sqlite3
import pandas as pd
from schema_manager import getDataframeSchema, getDatabaseSchema, generateCreateTableStatement, writeError, compareTableSchemas, getTableSchema
import pytest

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

class TestgetDatabaseSchema:
    def test_get_database_schema(self):
        pass

class TestgenerateCreateTableStatement:
    def test_generate_create_table_statement(self, sample_df):
        expected_statement = 'CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "age" INTEGER, "score" REAL, "active" BOOLEAN, "joined" DATE);'
        assert generateCreateTableStatement(sample_df, "test_table") == expected_statement

    def test_generate_create_table_statement_special_characters(self, special_char_df):
        expected_statement = 'CREATE TABLE IF NOT EXISTS special_table (id INTEGER PRIMARY KEY AUTOINCREMENT, "first name" TEXT, "order #" INTEGER);'
        assert generateCreateTableStatement(special_char_df, "special_table") == expected_statement

