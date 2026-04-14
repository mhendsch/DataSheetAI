import sqlite3
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from llm_adapter import generateSQL, stripSQLfromResponse
import os

# Fixtures
@pytest.fixture
def sample_response():
    return "Here is the SQL query you requested:\n```sql\nSELECT * FROM users WHERE age > 30;\n```"



# Tests
class TestGenerateSQL:
    def test_generate_sql_returns_string(self):
        """generateSQL should return a string."""
        result = generateSQL("fake_db.db", "Write a SQL query to select all users over 30")
        assert isinstance(result, str)
    
    def test_generate_sql_non_string_input(self):
        """generateSQL should handle non-string input gracefully."""
        result = generateSQL("fake_db.db", 12345)
        assert isinstance(result, str)  # Assuming it returns an error message as a string

    def test_generate_sql_empty_input(self):
        """generateSQL should handle empty input gracefully."""
        result = generateSQL("fake_db.db", "")
        assert isinstance(result, str)  # Assuming it returns an error message as a string
    
    def test_generate_sql_valid_query(self):
        """generateSQL should return a valid SQL query when given a valid prompt."""
        with patch("llm_adapter.schema_manager.getDatabaseSchema", return_value={"users": {"name": "TEXT", "age": "INTEGER"}}):
            result = generateSQL("fake_db.db", "Write a SQL query to select all users over 30")
            assert "SELECT" in result.upper() and "FROM" in result.upper()
    
    
class TestStripSQLfromResponse:
    def test_strip_sql_from_response(self, sample_response):
        """stripSQLfromResponse should extract the SQL query from the LLM response."""
        expected_sql = "SELECT * FROM users WHERE age > 30;"
        result = stripSQLfromResponse(sample_response)
        assert result == expected_sql

    def test_strip_sql_no_code_block(self):
        """If no code block is present, it should return nothing."""
        response = "Here is your query: SELECT * FROM users;"
        result = stripSQLfromResponse(response)
        assert result == ""

    def test_strip_sql_multiple_code_blocks(self):
        """If multiple code blocks are present, it should extract the first one."""
        response = "First query:\n```sql\nSELECT * FROM users;\n```\nSecond query:\n```sql\nSELECT name FROM users;\n```"
        expected_sql = "SELECT * FROM users;"
        result = stripSQLfromResponse(response)
        assert result == expected_sql

    def test_strip_sql_empty_response(self):
        """If the response is empty, it should return nothing."""
        result = stripSQLfromResponse("")
        assert result == ""