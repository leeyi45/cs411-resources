import pytest
from unittest.mock import Mock, call
from boxing.models.boxers_model import create_boxer

class MockCursor:
  def __init__(self, fetchone):
    self.fetchone = fetchone


@pytest.fixture
def mock_fetchone(mocker):
  return mocker.Mock()

@pytest.fixture
def mock_db_cursor(mock_fetchone):
  return MockCursor(mock_fetchone)

@pytest.fixture
def mock_db_connection(mock_db_cursor: MockCursor):
  class MockConnection:
    @staticmethod
    def cursor():
      return mock_db_cursor
    
    def commit(self):
      pass

    def close(self):
      pass

    def __enter__(self):
      return self

    def __exit__(self, *args):
      pass

  return MockConnection()

@pytest.fixture(autouse=True)
def mock_get_db_connection(mocker, mock_db_connection):
  """Fixture for providing a mock DB

  """
  mocker.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_db_connection)

# Test boxer creation
def test_regular_create_boxer(mock_db_cursor: MockCursor):
  create_boxer('boxer1', 170, 170, 10, 30)

  mock_db_cursor.execute.assert_called()

  # assert boxer.id == 1, f'Expected boxer id to be 1, got {boxer.id}'
  # assert boxer.name == 'boxer1', f'Expected boxer name to be boxer1, got {boxer.name}'
  # assert boxer.weight == 170, f'Expected boxer weight to be 170, got {boxer.weight}'
  # assert boxer.height == 170, f'Expected boxer height to be 170, got {boxer.height}'
  # assert boxer.reach == pytest.approx(10), f'Expected boxer reach to be 10, got {boxer.reach}'
  # assert boxer.age == 30, f'Expected boxer age to be {30}, got {boxer.age}'

def test_create_boxer_weight_too_low(mock_db_cursor: MockCursor):
  mock_db_cursor.fetchone.return_value = False

  with pytest.raises(ValueError, match="Invalid weight: 124. Must be at least 125."):
    create_boxer('boxer1', 124, 170, 10, 30)

# def test_create_boxer_age_too_low():
  # boxer = Boxer(1, 'boxer1', 170, 170, 10, 30)