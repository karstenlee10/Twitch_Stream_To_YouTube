import sys
import json
import os
import threading
import time
import cv2
import subprocess
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from io import StringIO

APP_TOKEN_FILE = "client_secret.json"
USER_TOKEN_FILE = "user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
]

def get_creds_saved():
    creds = None

    # Create new credentials via local server flow
    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
    
    creds = flow.run_local_server(port=6971)

    with open(USER_TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

if __name__ == '__main__':
    logging.basicConfig(filename="get_token.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    get_creds_saved()
    exit()
