import sqlite3
import pytest
import pandas as pd
from llm_adapter import generateSQL, stripSQLfromResponse
import os

# Fixtures
