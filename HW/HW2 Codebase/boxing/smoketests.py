#!/bin/python3

import requests
base_url = "http://localhost:8080/api"

def check_health():
  """Test the healthcheck endpoint"""
  print('Checking health status...')

  with requests.get(f'{base_url}/health') as req:
    resp = req.json()
    if 'status' not in resp or resp['status'] != 'success':
      print('Health check failed')
      return False

    print('Service is healthy.')
    return True

def check_db():
  """Test the db-check endpoint"""
  print('Checking database connection...')
  with requests.get(f'{base_url}/db-check') as req:
    resp = req.json()
    if 'status' not in resp or resp['status'] != 'success':
      print('Database check failed')
      return False

    print('Database connection is healthy.')
    return True

tests = [
  check_health,
  check_db
]

if __name__ == '__main__':
  for test in tests:
    if not test():
      exit(1)

  print("All tests passed successfully!")
  exit(0)