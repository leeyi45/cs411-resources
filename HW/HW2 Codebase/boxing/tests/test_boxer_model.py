import pytest
import sqlite3
from typing import List, Tuple
from unittest.mock import Mock, call
from boxing.models.boxers_model import *

@pytest.fixture
def mock_db_cursor():
  class MockCursor:
    fetchone = Mock()
    fetchall = Mock()
    execute = Mock()
  return MockCursor()

class MockConnection:
  def __init__(self, mock_cursor):
    self._cursor = mock_cursor
    self.commit = Mock()
  
  def cursor(self):
    return self._cursor
    
  def close(self):
    pass

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass

@pytest.fixture
def mock_db_connection(mock_db_cursor):
  return MockConnection(mock_db_cursor)

@pytest.fixture(autouse=True)
def mock_get_db_connection(mocker, mock_db_connection: MockConnection):
  """Fixture for providing a mock DB

  """
  mocker.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_db_connection)

# Test boxer creation
def test_regular_create_boxer(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with regular parameters
  
  """
  mock_db_cursor.fetchone.return_value = False
  create_boxer('boxer1', 170, 170, 10, 30)

  execute_calls = mock_db_cursor.execute.mock_calls
  assert len(execute_calls) == 2, f'Expected 2 calls to cursor.execute, got {len(execute_calls)}'
  call0, call1 = execute_calls

  assert call0.args[1] == ('boxer1',), 'First call to execute should have been with the boxer\'s name'
  boxer_args = call1.args[1]

  assert boxer_args[0] == 'boxer1', f'Expected name of boxer1, got {boxer_args[0]}'
  assert boxer_args[1] == 170, f'Expected weight of 170, got {boxer_args[1]}'
  assert boxer_args[2] == 170, f'Expected height of 170, got {boxer_args[2]}'
  assert boxer_args[3] == pytest.approx(10), f'Expected reach of 10, got {boxer_args[3]}'
  assert boxer_args[4] == 30, f'Expected age of 30, got {boxer_args[4]}'

  mock_db_connection.commit.assert_called_once()

def test_create_boxer_weight_too_low(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with a weight that is < 125

  """
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid weight: 124. Must be at least 125."):
    create_boxer('boxer1', 124, 170, 10, 30)
  
  mock_db_cursor.execute.assert_not_called()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_height_too_low(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with a height that is < 0
  
  """
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid height: -1. Must be greater than 0."):
    create_boxer('boxer1', 170, -1, 10, 30)

  mock_db_cursor.execute.assert_not_called()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_reach_too_low(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with a reach that is < 0
  
  """
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid reach: -1. Must be greater than 0."):
    create_boxer('boxer1', 170, 170, -1, 30)

  mock_db_cursor.execute.assert_not_called()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_age_too_low(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with an age < 18
  
  """
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid age: 17. Must be between 18 and 40."):
    create_boxer('boxer1', 170, 170, 10, 17)

  mock_db_cursor.execute.assert_not_called()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_age_too_high(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer with an age > 40
  
  """
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid age: 41. Must be between 18 and 40."):
    create_boxer('boxer1', 170, 170, 10, 41)

  mock_db_cursor.execute.assert_not_called()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_with_existing_name(mock_db_cursor, mock_db_connection: MockConnection):
  """Test create_boxer using a name that already exists in the db
  
  """
  mock_db_cursor.fetchone.return_value = True

  with pytest.raises(ValueError, match="Boxer with name 'boxer1' already exists"):
    create_boxer('boxer1', 170, 170, 10, 30)

  mock_db_cursor.execute.assert_called_once()
  mock_db_connection.commit.assert_not_called()

def test_create_boxer_with_integrity_error(mock_db_cursor, mock_db_connection: MockConnection):
  """Test calling create_boxer with a boxer that already exists, however
  the error is caused by IntegrityError, rather than fetchone returning true
  
  """
  mock_db_cursor.fetchone.return_value = None
  mock_db_cursor.execute.side_effect = sqlite3.IntegrityError

  with pytest.raises(ValueError, match="Boxer with name 'boxer1' already exists"):
    create_boxer('boxer1', 170, 170, 10, 30)
  
  mock_db_connection.commit.assert_not_called()
  mock_db_cursor.execute.assert_called_once()

# Test boxer_deletion
def test_delete_boxer(mock_db_cursor, mock_db_connection: MockConnection):
  """Test a normal call to delete_boxer
  
  """
  mock_db_cursor.fetchone.return_value = True
  delete_boxer(1)

  mock_db_cursor.execute.assert_has_calls([
    call("SELECT id FROM boxers WHERE id = ?", (1,)),
    call("DELETE FROM boxers WHERE id = ?", (1,))
  ])

  mock_db_connection.commit.assert_called_once()

def test_delete_nonexistent_boxer(mock_db_cursor, mock_db_connection: MockConnection):
  """Test trying to delete a boxer that doesn't exist
  
  """
  mock_db_cursor.fetchone.return_value = None
  
  with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
    delete_boxer(1)

  mock_db_connection.commit.assert_not_called()
  mock_db_cursor.execute.assert_called_once_with(
    "SELECT id FROM boxers WHERE id = ?", (1,)
  )

# Test get_leaderboard
def test_get_leaderboard(mock_db_cursor):
  """Test regular functioning of get_leaderboard()
  
  """
  mock_db_cursor.fetchall.return_value = [
    [1, 'boxer1', 170, 170, 10, 30, 10, 10, 1],
    [2, 'boxer2', 185, 200, 15, 35, 10, 10, 1],
  ]

  leaderboard = get_leaderboard('wins')
  mock_db_cursor.execute.assert_called_once()

  # check that the leaderboard returns the proper fields
  assert leaderboard[0]['id'] == 1
  assert leaderboard[0]['name'] == 'boxer1'
  assert leaderboard[0]['weight'] == 170
  assert leaderboard[0]['height'] == 170
  assert leaderboard[0]['reach'] == pytest.approx(10)
  assert leaderboard[0]['age'] == 30
  assert leaderboard[0]['fights'] == 10
  assert leaderboard[0]['wins'] == 10
  assert leaderboard[0]['win_pct'] == 100

  assert leaderboard[1]['id'] == 2
  assert leaderboard[1]['name'] == 'boxer2'
  assert leaderboard[1]['weight'] == 185
  assert leaderboard[1]['height'] == 200
  assert leaderboard[1]['reach'] == pytest.approx(15)
  assert leaderboard[1]['age'] == 35
  assert leaderboard[1]['fights'] == 10
  assert leaderboard[1]['wins'] == 10
  assert leaderboard[1]['win_pct'] == 100

def test_get_leaderboard_sort_by_wins(mock_db_cursor):
  """Test calling get_leaderboard with 'wins'
  
  """
  mock_db_cursor.fetchall.return_value = []
  get_leaderboard('wins')

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  query_str: str = call0.args[0]

  assert query_str.endswith('ORDER BY wins DESC'), 'Query string should include "wins"'

def test_get_leaderboard_sort_by_win_pct(mock_db_cursor):
  """Test calling get_leaderboard with 'win_pct'
  
  """
  mock_db_cursor.fetchall.return_value = []
  get_leaderboard('win_pct')

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  query_str: str = call0.args[0]

  assert query_str.endswith('ORDER BY win_pct DESC'), 'Query string should include "win_pct"'

def test_get_leaderboard_sort_invalid(mock_db_cursor):
  """Test calling get_leaderboard with an invalid sort parameter
  
  """
  with pytest.raises(ValueError, match="Invalid sort_by parameter: random"):
    get_leaderboard('random')

  mock_db_cursor.execute.assert_not_called()
  mock_db_cursor.fetchall.assert_not_called()

# Test get_boxer_by_id
def test_get_boxer_by_id(mock_db_cursor):
  """Test regular call to get_boxer_by_id
  
  """
  mock_db_cursor.fetchone.return_value = [
    1, 'boxer1', 170, 170, 10, 30
  ]

  boxer = get_boxer_by_id(1)

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  assert call0.args[1] == (1,)

  assert boxer.id == 1, f'Expected id of 1, got {boxer.id}'
  assert boxer.name == 'boxer1', f'Expected name of boxer1, got {boxer.name}'
  assert boxer.weight == 170, f'Expected weight of 170, got {boxer.weight}'
  assert boxer.height == 170, f'Expected height of 170, got {boxer.height}'
  assert boxer.reach == pytest.approx(10), f'Expected reach of 10, got {boxer.reach}'
  assert boxer.age == 30, f'Expected age of 30, got {boxer.age}'

def test_get_boxer_by_id_nonexistent(mock_db_cursor):
  """Test trying to get a boxer with a nonexistent ID
  
  """
  mock_db_cursor.fetchone.return_value = []
  with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
    get_boxer_by_id(1)

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  assert call0.args[1] == (1,)

# Test get_boxer_by_name
def test_get_boxer_by_name(mock_db_cursor):
  """Test regular call to get_boxer_by_name
  
  """
  mock_db_cursor.fetchone.return_value = [
    1, 'boxer1', 170, 170, 10, 30
  ]

  boxer = get_boxer_by_name('boxer1')

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  assert call0.args[1] == ('boxer1',)

  assert boxer.id == 1, f'Expected id of 1, got {boxer.id}'
  assert boxer.name == 'boxer1', f'Expected name of boxer1, got {boxer.name}'
  assert boxer.weight == 170, f'Expected weight of 170, got {boxer.weight}'
  assert boxer.height == 170, f'Expected height of 170, got {boxer.height}'
  assert boxer.reach == pytest.approx(10), f'Expected reach of 10, got {boxer.reach}'
  assert boxer.age == 30, f'Expected age of 30, got {boxer.age}'

def test_get_boxer_by_name_nonexistent(mock_db_cursor):
  """Test trying to get a boxer with a nonexistent name
  
  """
  mock_db_cursor.fetchone.return_value = []
  with pytest.raises(ValueError, match="Boxer 'boxer1' not found."):
    get_boxer_by_name('boxer1')

  mock_db_cursor.execute.assert_called_once()
  call0 = mock_db_cursor.execute.mock_calls[0]
  assert call0.args[1] == ('boxer1',)

# Test get_weight_class
def test_get_weight_class():
  """Test get_weight_class with valid weight values
  
  """
  cases: List[Tuple[int, str]] = [
    (204, 'HEAVYWEIGHT'),
    (203, 'HEAVYWEIGHT'),
    (202, 'MIDDLEWEIGHT'),

    (190, 'MIDDLEWEIGHT'),
    (166, 'MIDDLEWEIGHT'),
    (165, 'LIGHTWEIGHT'),

    (150, 'LIGHTWEIGHT'),
    (133, 'LIGHTWEIGHT'),
    (132, 'FEATHERWEIGHT'),

    (125, 'FEATHERWEIGHT')
  ]

  for i, (weight, expected) in enumerate(cases, 1):
    result = get_weight_class(weight)
    assert result == expected, f'{i}. Exepected weight of {weight} to be {expected}, got {result}'

def test_get_weight_class_invalid():
  """Test get_weight_class with an invalid weight value

  """
  with pytest.raises(ValueError, match=f"Invalid weight: 100. Weight must be at least 125."):
    get_weight_class(100)

# Test update_boxer_stats
def test_update_boxer_stats_win(mock_db_cursor, mock_db_connection: MockConnection):
  """Test a regular call to update_boxer_stats with win
  
  """
  mock_db_cursor.fetchone.return_value = True

  update_boxer_stats(1, 'win')

  mock_db_cursor.execute.assert_has_calls([
    call("SELECT id FROM boxers WHERE id = ?", (1,)),
    call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))
  ])
  mock_db_connection.commit.assert_called_once()

def test_update_boxer_stats_loss(mock_db_cursor, mock_db_connection: MockConnection):
  """Test a regular call to update_boxer_stats with loss
  
  """
  mock_db_cursor.fetchone.return_value = True

  update_boxer_stats(1, 'loss')

  mock_db_cursor.execute.assert_has_calls([
    call("SELECT id FROM boxers WHERE id = ?", (1,)),
    call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))
  ])
  mock_db_connection.commit.assert_called_once()

def test_update_boxer_stats_invalid_result(mock_db_cursor, mock_db_connection: MockConnection):
  """Test a regular call to update_boxer_stats with an invalid win result
  
  """
  with pytest.raises(ValueError, match="Invalid result: idk. Expected 'win' or 'loss'."):
    update_boxer_stats(1, 'idk')

  mock_db_connection.commit.assert_not_called()
  mock_db_cursor.execute.assert_not_called()
  mock_db_cursor.fetchone.assert_not_called()

def test_update_boxer_stats_unknown_boxer(mock_db_cursor, mock_db_connection: MockConnection):
  """Test a regular call to update_boxer_stats with an unknown boxer id
  
  """
  mock_db_cursor.fetchone.return_value = None

  with pytest.raises(ValueError, match=f"Boxer with ID 1 not found."):
    update_boxer_stats(1, 'win')

  mock_db_connection.commit.assert_not_called()
  mock_db_cursor.execute.assert_called_once_with(
    "SELECT id FROM boxers WHERE id = ?", (1,)
  )