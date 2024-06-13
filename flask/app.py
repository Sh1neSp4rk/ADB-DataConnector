import os
import sys
import yaml
from flask import Flask, request, redirect, session
import requests
import base64
import hashlib
from subprocess import run

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import create_logger

# Call getcodespaceurl.py to update .credentials.yaml
run(['python', 'flask/getcodespaceurl.py'])

# Load credentials from .credentials.yaml
credentials_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.credentials.yaml')
with open(credentials_file, 'r') as file:
    credentials = yaml.safe_load(file)

# Get the Codespace URL from credentials
codespace_url = credentials['codespace']['url']

# Initialize the Flask app
app = Flask(__name__)

# Get the secret key from credentials
secret_key = credentials['flask']['key']
app.secret_key = secret_key

# Configure logging using the create_logger function
logger = create_logger('flask_app', 'flask_app.log')  # Create a logger instance

CLIENT_ID = credentials['appauth']['clientid']
AUTHORIZATION_URL = 'https://developer.api.autodesk.com/authentication/v1/authorize'
TOKEN_URL = 'https://developer.api.autodesk.com/authentication/v1/gettoken'
REDIRECT_URI = credentials['appauth']['redirect']

def generate_pkce_verifier_and_challenge():
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')
    return verifier, challenge

@app.route('/')
def home():
    base_url = request.base_url.replace(request.path, '')
    
    logger.info('Redirecting user to Autodesk login page.')
    code_verifier, code_challenge = generate_pkce_verifier_and_challenge()
    session['code_verifier'] = code_verifier
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'data:read',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    auth_url = AUTHORIZATION_URL + '?' + '&'.join([f'{key}={val}' for key, val in params.items()])
    return redirect(auth_url)

@app.route('/callback')
def callback():
    logger.info('Received callback from Autodesk authentication server.')
    state = request.args.get('state')
    code = request.args.get('code')
    if state != session.get('state'):
        logger.error('Invalid state parameter')
        return 'Invalid state parameter', 400

    payload = {
        'client_id': CLIENT_ID,
        'redirect_uri': request.base_url,
        'code': code,
        'grant_type': 'authorization_code',
        'code_verifier': session['code_verifier']
    }
    response = requests.post(TOKEN_URL, data=payload)
    if response.ok:
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        logger.info('Access token obtained and saved successfully.')

        # Store tokens in session or database as needed
        return f'Access Token: {access_token}, Refresh Token: {refresh_token}'
    else:
        logger.error('Failed to fetch tokens')
        return 'Failed to fetch tokens', 400

if __name__ == '__main__':
    app.run(debug=True)