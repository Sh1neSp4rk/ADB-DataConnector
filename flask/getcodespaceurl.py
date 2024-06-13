import requests
import os
import yaml

# Load credentials from .credentials.yaml
credentials_file = os.path.join(os.path.dirname(__file__), '..', '.credentials.yaml')
with open(credentials_file, 'r') as file:
    credentials = yaml.safe_load(file)

# Get the GitHub API URL and token
GITHUB_OWNER = credentials['git']['owner']
GITHUB_REPO = credentials['git']['repo']
GITHUB_TOKEN = credentials['git']['token']

def get_codespace_url():
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/codespaces"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        codespaces = response.json().get('codespaces', [])
        for codespace in codespaces:
            if 'state' in codespace and codespace['state'] == 'Available':
                return codespace['web_url']
    else:
        return None

# Fetch the current Codespace URL
codespace_url = get_codespace_url()
if codespace_url:
    # Write or update the .codespace_url file with the current Codespace URL
    with open('.codespaceurl', 'w') as file:
        file.write(codespace_url)
    print(f"Codespace URL updated to: {codespace_url}")
else:
    print("Could not determine the Codespace URL.")