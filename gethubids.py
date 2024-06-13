import requests
import yaml
from logger import create_logger  # Import create_logger function from logger.py

# Create a logger for gethubids.py with a unique log file
logger = create_logger('gethubids', 'gethubids.log')

# Set up authentication and API endpoint
auth_token = 'your_access_token'
api_url = 'https://developer.api.autodesk.com/project/v1/hubs'

# Make API request
headers = {'Authorization': 'Bearer ' + auth_token}
response = requests.get(api_url, headers=headers)

# Process API response and write to YAML file
if response.status_code == 200:
    projects = response.json().get('data', [])
    if not projects:
        logger.warning('No projects found in the API response.')
    else:
        project_data = [{'name': project['attributes']['name'], 'hub_id': project['id']} for project in projects]
        with open('hubids.yaml', 'w') as file:
            yaml.dump(project_data, file)
            logger.info('Hub IDs saved successfully.')
else:
    logger.error(f"Error fetching projects. Status code: {response.status_code}, Response text: {response.text}")