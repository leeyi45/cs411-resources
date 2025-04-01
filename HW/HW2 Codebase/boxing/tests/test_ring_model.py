from unittest.mock import call
import pytest
from typing import List, Tuple

from boxing.models.boxers_model import Boxer 
from boxing.models.ring_model import RingModel

"""Fixture providing a RingModel for tests"""
@pytest.fixture
def ring_model():
  return RingModel()

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
  return Boxer(1, 'guy1', 200, 170, 10, 24)

@pytest.fixture
def sample_boxer2():
  return Boxer(2, 'guy2', 200, 170, 10, 27)

@pytest.fixture
def sample_boxer3():
  return Boxer(3, 'guy3', 200, 170, 10, 30)

"""Fixtures providing a sample ring for the tests."""
@pytest.fixture
def sample_ring(sample_boxer1: Boxer, sample_boxer2: Boxer) -> RingModel:
  ring = RingModel()
  ring.enter_ring(sample_boxer1)
  ring.enter_ring(sample_boxer2)
  return ring

# Test Enter Ring
def test_enter_ring(ring_model: RingModel, sample_boxer1: Boxer):
  """Test adding a boxer regularly to the ring

  """
  ring_model.enter_ring(sample_boxer1)
  boxers = ring_model.get_boxers()

  assert len(boxers) == 1, f'Expected 1 boxer, but got {len(boxers)}'
  assert boxers[0].name == 'guy1', f'Expected the boxer\'s name to be {sample_boxer1.name}, got {boxers[0].name}'

def test_multiple_enter_ring(ring_model: RingModel, sample_boxer1: Boxer, sample_boxer2: Boxer):
  """Test adding 2 boxers

  """
  ring_model.enter_ring(sample_boxer1)
  assert len(ring_model.get_boxers()) == 1, f'Expected 1 boxer, but got {len(ring_model.get_boxers())}'

  ring_model.enter_ring(sample_boxer2)
  assert len(ring_model.get_boxers()) == 2, f'Expected 2 boxers, but got {len(ring_model.get_boxers())}'

def test_3_enter_ring(ring_model: RingModel, sample_boxer1: Boxer, sample_boxer2: Boxer, sample_boxer3: Boxer):
  """Test adding more than 2 boxers

  """
  ring_model.enter_ring(sample_boxer1)
  ring_model.enter_ring(sample_boxer2)
  
  with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
    ring_model.enter_ring(sample_boxer3)

def test_non_boxer_enter_ring(ring_model: RingModel):
  """Test adding something that's not a boxer into a ring
  
  """
  with pytest.raises(TypeError, match=f"Invalid type: Expected 'Boxer', got 'str'"):
    ring_model.enter_ring("some_string")

# Test Clear Ring
def test_clear_ring(sample_ring: RingModel):
  """Test removing all boxers from the ring

  """
  assert len(sample_ring.get_boxers()) == 2, f'Expected 2 boxers, but got {len(sample_ring.get_boxers())}'
  
  sample_ring.clear_ring()
  assert len(sample_ring.get_boxers()) == 0, f'Expected no boxers, but got {len(sample_ring.get_boxers())}'

  # it should not error even if clear is called on an empty ring
  sample_ring.clear_ring()
  assert len(sample_ring.get_boxers()) == 0, f'Expected no boxers, but got {len(sample_ring.get_boxers())}'

# Test ring fight
def test_ring_fight_empty(ring_model: RingModel):
  """Test calling fight with an empty ring throws an error
  
  """
  with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
    ring_model.fight()

def test_ring_fight_1_boxer(ring_model: RingModel, sample_boxer1: Boxer):
  """Test calling fight with only 1 boxer throws an error
  
  """
  ring_model.enter_ring(sample_boxer1)
  assert len(ring_model.get_boxers()) == 1, f'Expected 1 boxer, got {len(ring_model.get_boxers())}'
  with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
    ring_model.fight()

def test_ring_fight(mocker):
  """Test calling fight with 2 boxers
  
  """
  boxer1 = Boxer(1, 'boxer1', 200, 200, 10, 30)
  boxer2 = Boxer(2, 'boxer2', 150, 150, 1, 45)

  mock = mocker.patch('boxing.models.ring_model.update_boxer_stats', return_value=None)

  ring_model = RingModel()
  ring_model.enter_ring(boxer1)
  ring_model.enter_ring(boxer2)

  winner = ring_model.fight()
 
  assert winner == 'boxer1', f'Expected boxer1 to win, got {winner}'
  mock.assert_has_calls([
    call(1, 'win'),
    call(2, 'loss')
  ])

  assert len(ring_model.get_boxers()) == 0, 'Ring should be empty after fight'

# Test getFightingSkill
def test_get_fighting_skill():
  ring = RingModel()

  cases: List[Tuple[Boxer, int]] = [
    # Age Effects
    (Boxer(1, "guy1", 170, 170, 10, 20), 680),
    (Boxer(1, "guy1", 170, 170, 10, 25), 681),
    (Boxer(1, "guy1", 170, 170, 10, 30), 681),
    (Boxer(1, "guy1", 170, 170, 10, 35), 681),
    (Boxer(1, "guy1", 170, 170, 10, 40), 679),

    # Weight effects
    (Boxer(1, "guy1", 180, 170, 10, 20), 720),
    
    # Name effects
    (Boxer(1, "guy12", 170, 170, 10, 20), 850),
  ]

  for i, (boxer, expected) in enumerate(cases, 1):
    result = ring.get_fighting_skill(boxer)
    assert expected == pytest.approx(result), f'{i}. Expected skill of {expected}, got {result}'
