import pytest
import pandas as pd
from query_service import loadData, askLLM

# Fixtures

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "city": ["New York", "Los Angeles", "Chicago"]
    })

@pytest.fixture
def sample_schema():
    return {
        "name": "TEXT",
        "age": "INTEGER",
        "city": "TEXT"
    }

class TestLoadData:
    def test_load_data_valid(self, sample_df):
        result = loadData("sample.csv", "sample_table")
        assert result == 0

    def test_load_data_invalid_filename(self):
        result = loadData("", "sample_table")
        assert result == 1

    def test_load_data_non_csv(self):
        result = loadData("sample.txt", "sample_table")
        assert result == 1

    def test_load_data_file_not_exist(self):
        result = loadData("nonexistent.csv", "sample_table")
        assert result == 1

    def test_load_data_empty_file(self):
        # Create an empty CSV file for testing
        with open("empty.csv", "w") as f:
            pass
        result = loadData("empty.csv", "sample_table")
        assert result == 1
        os.remove("empty.csv")

class TestAskLLM:
    def test_returns_dataframe_on_valid_query(self, sample_df):
        """A valid LLM-generated SQL query should return a DataFrame."""
        with patch("query_service.llm_adapter.generateSQL", return_value="```sql\nSELECT * FROM users\n```"), \
             patch("query_service.llm_adapter.stripSQLfromResponse", return_value="SELECT * FROM users"), \
             patch("query_service.csv_loader.queryData", return_value=sample_df):

            result = askLLM("Show me all users")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_returns_none_when_llm_generates_no_sql(self):
        """If the LLM response contains no SQL, askLLM should return None."""
        with patch("query_service.llm_adapter.generateSQL", return_value="I don't know."), \
             patch("query_service.llm_adapter.stripSQLfromResponse", return_value=""), \
             patch("query_service.schema_manager.writeError"):

            result = askLLM("gibberish input")

        assert result is None

    def test_returns_none_when_query_fails_validation(self):
        """If queryData returns 1 (validation failure), askLLM should return None."""
        with patch("query_service.llm_adapter.generateSQL", return_value="DROP TABLE users"), \
             patch("query_service.llm_adapter.stripSQLfromResponse", return_value="DROP TABLE users"), \
             patch("query_service.csv_loader.queryData", return_value=1), \
             patch("query_service.schema_manager.writeError"):

            result = askLLM("delete everything")

        assert result is None

    def test_returns_none_when_sql_is_only_whitespace(self):
        """Whitespace-only SQL from the LLM should be treated as no query generated."""
        with patch("query_service.llm_adapter.generateSQL", return_value="   "), \
             patch("query_service.llm_adapter.stripSQLfromResponse", return_value="   "), \
             patch("query_service.schema_manager.writeError"):

            result = askLLM("     ")

        assert result is None

    def test_returns_empty_dataframe_for_query_with_no_results(self):
        """A valid query that matches no rows should return an empty DataFrame, not None."""
        empty_df = pd.DataFrame(columns=["name", "age"])

        with patch("query_service.llm_adapter.generateSQL", return_value="SELECT * FROM users WHERE age > 999"), \
             patch("query_service.llm_adapter.stripSQLfromResponse", return_value="SELECT * FROM users WHERE age > 999"), \
             patch("query_service.csv_loader.queryData", return_value=empty_df):

            result = askLLM("Find users older than 999")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
    