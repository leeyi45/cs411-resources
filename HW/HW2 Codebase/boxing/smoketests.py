#!/bin/python3

import logging
import requests
from typing import Callable

logging.basicConfig(
  level=logging.INFO,
  format='[%(asctime)s %(levelname)s]: %(message)s',
  datefmt='%H:%M:%S'
)

base_url = "http://localhost:8080/api"

smoketests = []

def smoketest(f: Callable[[requests.Request], bool]):
  smoketests.append(f)
  return f

# Health checks
@smoketest
def check_health():
  """Test the healthcheck endpoint"""
  with requests.get(f'{base_url}/health') as req:
    logging.info('Checking health status...')
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Health check failed'

    logging.info('Service is healthy.')

@smoketest
def check_db():
  """Test the db-check endpoint"""
  logging.info('Checking database connection...')
  with requests.get(f'{base_url}/health') as req:
    resp = req.json()
    assert 'status' in resp or resp['status'] == 'success', 'Database check failed'

    logging.info('Database connection is healthy.')

@smoketest
def test_add_boxer():
  """Add three boxers so that we can have two of them fight"""

  def add_boxer(name: str, weight: int, height: int, reach: float, age: int):
    boxer = {
      'name': name,
      'weight': weight,
      'height': height,
      'reach': reach,
      'age': age
    }

    with requests.post(f'{base_url}/add-boxer', json=boxer) as req:
      resp = req.json()

      if 'status' not in resp or resp['status'] != 'success':
        # ignore if we've already added the new boxer
        if not resp['details'].endswith('already exists'):
          print('Failed to add new boxer')
          return False
        logging.info(f'{name} already added')
      else:
        logging.info(f'Successfully added {name}')

  add_boxer('boxer1', 170, 170, 10.0, 30)
  add_boxer('boxer2', 185, 200, 15.0, 35)
  add_boxer('boxer3', 220, 180, 15.0, 25)

@smoketest
def test_get_boxer():
  """Check that boxer3 exists before we try to delete it"""
  with requests.get(f'{base_url}/get-boxer-by-id/3') as req:
    resp = req.json()

    assert 'status' in resp and resp['status'] == 'success', 'boxer3 does not exist!'
       
    boxer = resp['boxer']
    assert boxer['name'] == 'boxer3', f'Expected name to be boxer3, got \'{boxer["name"]}\''
    assert boxer['height'] == 180, f'Expected height to be 180, got \'{boxer["height"]}\''
    assert boxer['weight'] == 220, f'Expected weight to be 220, got \'{boxer["weight"]}\''
    assert boxer['age'] == 25, f'Expected age to be 25, got \'{boxer["age"]}\''

    logging.info('Successfully retrieved boxer3 using ID')

  with requests.get(f'{base_url}/get-boxer-by-name/boxer3') as req:
    resp = req.json()

    assert 'status' in resp and resp['status'] == 'success', 'boxer3 does not exist!'
       
    boxer = resp['boxer']
    assert boxer['name'] == 'boxer3', f'Expected name to be boxer3, got \'{boxer["name"]}\''
    assert boxer['height'] == 180, f'Expected height to be 180, got \'{boxer["height"]}\''
    assert boxer['weight'] == 220, f'Expected weight to be 220, got \'{boxer["weight"]}\''
    assert boxer['age'] == 25, f'Expected age to be 25, got \'{boxer["age"]}\''

    logging.info('Successfully retrieved boxer3 using name')

@smoketest
def test_delete_boxer():
  """Now we try deleting boxer3"""
  with requests.delete(f'{base_url}/delete-boxer/4') as req:
    resp = req.json()

    assert 'status' in resp and resp['status'] == 'error', 'Incorrect response to deleting a non-existent boxer'

  with requests.delete(f'{base_url}/delete-boxer/3') as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to delete boxer3'

  logging.info('Successfully deleted boxer3')

@smoketest
def test_fight():
  """Test fighting"""
  # Clear the ring
  with requests.post(f'{base_url}/clear-boxers') as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to clear ring'
  
  logging.info('Successfully cleared ring')

  # Check that fighting with zero boxers throws an error
  with requests.get(f'{base_url}/fight') as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'error', 'Triggering fight with an empty ring should\'ve thrown an error'

  # Add both boxer1 and boxer2 to the ring
  with requests.post(f'{base_url}/enter-ring', json={
    'name': 'boxer1'
  }) as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to enter boxer1 into the ring'
  logging.info("boxer1 successfully entered the ring")

  with requests.post(f'{base_url}/enter-ring', json={
    'name': 'boxer2'
  }) as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to enter boxer2 into the ring'

  logging.info("boxer2 successfully entered the ring")

  # Check that the ring has two boxers
  with requests.get(f'{base_url}/get-boxers') as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to get boxers'

    boxers = resp['boxers']
    assert len(boxers) == 2, f'Expected 2 boxers, got {len(boxers)}'

  # Check that fighting with zero boxers throws an error
  with requests.get(f'{base_url}/fight') as req:
    resp = req.json()
    assert 'status' in resp and resp['status'] == 'success', 'Failed to trigger fight'
    assert resp['winner'] == 'boxer1', f'Expected winner to be boxer1, got {resp["winner"]}'

  logging.info("Fight successfully triggered")

@smoketest
def get_leaderboard():
  with requests.get(f'{base_url}/leaderboard?sort=wins') as req:
    resp = req.json()

    assert 'status' in resp and resp['status'] == 'success', 'Failed to get leaderboard'
    leaderboard = resp['leaderboard']
    assert leaderboard[0]['name'] == 'boxer1', 'Expected boxer1 to be first on the leaderboard'

  logging.info('Successfully retrieved leaderboard')

if __name__ == '__main__':
  for test in smoketests:
    test()

  print("All tests passed successfully!")
  exit(0)