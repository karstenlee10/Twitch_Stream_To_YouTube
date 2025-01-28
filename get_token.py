import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

APP_TOKEN_FILE = "client_secret.json"
USER_TOKEN_FILE = "user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.readonly',
]

def get_creds_saved():
    creds = None

    # Create new credentials via local server flow
    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
   
    # Try to load existing user token
    try:
      creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE)
    except FileNotFoundError:
       pass

    if not creds or not creds.valid:
        creds = flow.run_local_server(port=6971)

        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

if __name__ == '__main__':
    logging.basicConfig(filename="get_token.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    get_creds_saved()
    exit()
