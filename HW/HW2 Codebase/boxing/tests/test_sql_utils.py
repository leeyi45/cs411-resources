import pytest
import sqlite3
from unittest.mock import Mock
from boxing.utils.sql_utils import *

@pytest.fixture
def mock_db_cursor():
  """Fixture for providing a mocked cursor
  
  """
  class MockCursor:
    execute = Mock()
    fetchone = Mock()

  return MockCursor()

@pytest.fixture
def mock_connection(mock_db_cursor):
  """Fixture for providing a mocked DB connection
  
  """
  class MockConnection:
    close = Mock()

    def cursor(self):
      return mock_db_cursor

  return MockConnection()

@pytest.fixture(autouse=True)
def mock_db_connection(mock_connection, mocker):
  """Fixture for mocking sqlite3.connect
  
  """
  mocker.patch('sqlite3.connect', return_value=mock_connection)

def test_check_database_connection(mock_db_cursor):
  """Test that check_database_connection connects to the DB
  and then executes 'SELECT 1;'
  
  """
  check_database_connection()
  sqlite3.connect.assert_called_once()
  mock_db_cursor.execute.assert_called_with('SELECT 1;')

def test_check_table_exists(mock_db_cursor):
  """Test that check_table_exists connects to the DB
  and runs the correct query
  """
  mock_db_cursor.fetchone.return_value = True

  check_table_exists('table')

  sqlite3.connect.assert_called_once()
  mock_db_cursor.execute.assert_called_with("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", ('table',))

def test_check_table_exist_nonexistent(mock_db_cursor):
  """Test that check_table_exists connects to the DB, runs
  the correct query and raises an Exception on a non-existent table
  
  """
  mock_db_cursor.fetchone.return_value = None
  with pytest.raises(Exception, match="Table 'table' does not exist."):
    check_table_exists('table')

  sqlite3.connect.assert_called_once()
  mock_db_cursor.execute.assert_called_with("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", ('table',))

def test_get_db_connection(mock_connection):
  """Test that get_db_connection returns an object
  that calls conn.close() when done
  
  """
  with get_db_connection():
    pass

  mock_connection.close.assert_called_once()

def test_get_db_connection_error(mock_connection):
  """Test that get_db_connection returns an object
  that calls conn.close() even in the event of an exception
  
  """
  with pytest.raises(sqlite3.Error):
    with get_db_connection():
      raise sqlite3.Error()

  mock_connection.close.assert_called_once()