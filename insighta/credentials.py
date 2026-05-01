import os
import json

CREDENTIALS_PATH = os.path.expanduser('~/.insighta/credentials.json')


def save_credentials(access_token, refresh_token, username, email, role,
                     last_login_at):
    '''
    saves tokens and user info to CREDENTIALS_PATH
    creates the ~/.insighta directroy if not exist
    '''
    os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)

    credentials = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'username': username,
        'email': email,
        'role': role,
        'last_login_at': last_login_at
    }

    with open(CREDENTIALS_PATH, 'w') as f:
        json.dump(credentials, f, indent=2)


def load_credentials():
    '''
    Reads tokens from ~/.insighta/credentials.json.
    Returns None if file doesn't exist — means user is not logged in.    
    '''
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    
    with open(CREDENTIALS_PATH, 'r') as f:
        return json.load(f)
    

def delete_credentials():
    """
    Deletes the credentials file.
    Called on logout.
    """
    if os.path.exists(CREDENTIALS_PATH):
        os.remove(CREDENTIALS_PATH)


def get_access_token():
    '''Get access token if logged in'''
    credentials = load_credentials()
    if not credentials:
        return None
    
    return credentials.get('access_token')

def get_refresh_token():
    '''Get access token if logged in'''
    credentials = load_credentials()
    if not credentials:
        return None
    
    return credentials.get('refresh_token')


def is_logged_in():
    """
    Checks if the user is logged in by checking
    if credentials file exists and has tokens.
    """
    credentials = load_credentials()
    if not credentials:
        return False
    
    return bool(credentials.get("access_token"))