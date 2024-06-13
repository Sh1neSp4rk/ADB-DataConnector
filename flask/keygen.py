import hashlib
import yaml
import os

# Navigate to the parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(parent_dir)

# Generate a random bytes object
random_bytes = os.urandom(24)

# Hash the random bytes using SHA-256 to create a secure key
secure_key = hashlib.sha256(random_bytes).hexdigest()

# Load existing credentials from .credentials.yaml
credentials_file = os.path.join(os.path.dirname(__file__), '..', '.credentials.yaml')
with open(credentials_file, 'r') as file:
    credentials = yaml.safe_load(file)

# Update the 'flask' section with the secure key
credentials['flask'] = {'key': secure_key}

# Write updated credentials back to .credentials.yaml
with open(credentials_file, 'w') as file:
    yaml.dump(credentials, file)

print('Secure key generated and stored in .credentials.yaml under the flask section.')