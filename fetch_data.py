import requests
import yaml
import json
from logger import create_logger  # Import create_logger function from logger.py

# Create a logger for fetch_data.py with a unique log file
logger = create_logger('fetch_data', 'fetch_data.log')

# Load tokens and credentials
with open('.credentials.yaml', 'r') as file:
    credentials = yaml.safe_load(file)
with open('tokens.yaml', 'r') as file:
    tokens = yaml.safe_load(file)

client_id = credentials['appauth']['clientid']
client_secret = credentials['appauth']['clientsecret']
hub_id = 'YOUR_HUB_ID'

def refresh_access_token(refresh_token):
    token_url = 'https://developer.api.autodesk.com/authentication/v1/refreshtoken'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()

def fetch_projects(access_token):
    api_url = f'https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()

try:
    # Refresh token if necessary
    if 'expires_in' not in tokens or tokens['expires_in'] <= 0:
        tokens = refresh_access_token(tokens['refresh_token'])
        with open('tokens.yaml', 'w') as file:
            yaml.dump(tokens, file)

    # Fetch data
    projects = fetch_projects(tokens['access_token'])
    logger.info('Data fetched successfully')

    # Save data to a file or process as needed
    with open('acc_data.json', 'w') as outfile:
        json.dump(projects, outfile)
        logger.info('Data saved to acc_data.json')

except Exception as e:
    logger.error(f"Error: {e}")