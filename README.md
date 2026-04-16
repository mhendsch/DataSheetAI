# DataSheetAI

## Dataflow

### Initialization
- Execution begins with query_service.py
- query_service.py loads CSVs from database by calling loadCSV from csv_loader.py
- query_service.py checks the schema of these CSVs by calling schema_manager.py
- If schemas match any already existing in database, data is inserted into database using csv_loader.py
- If schema doesn't match, query service calls the schema manager to generate a create table statement, which is then executed in sqlite3

### User input
- Query service takes user input, calls llm_adapter.py
- llm_adapter asks schema_manager for schemas for all tables in database
- llm_adapter creates SQL query based on user input
- SQL instructions are stripped from response
- Instructions are passed to csv_loader
- csv_loader queries SQL validator, to ensure SQL meets safety and content standards
- If instructions are deemed acceptable, csv_loader queries sqlite3 database and returns results
