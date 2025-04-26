import subprocess  # Importing subprocess module for running system commands
import sys  # Importing sys module for system-specific parameters and functions
import os  # Importing os module for interacting with the operating system
import time  # Importing time module for time-related functions
import logging  # Importing logging module for logging messages
import argparse  # Importing argparse module for parsing command-line arguments
from selenium import webdriver  # Importing webdriver from selenium for browser automation
from selenium.webdriver.common.by import By  # Importing By for locating elements
from selenium.webdriver.support import expected_conditions as EC  # Importing expected_conditions for waiting conditions
from selenium.webdriver.support.ui import WebDriverWait  # Importing WebDriverWait for waiting for conditions
from selenium.common.exceptions import SessionNotCreatedException  # Importing exception for session creation failure
from selenium.webdriver.chrome.options import Options  # Importing Options for Chrome browser options
from google.oauth2.credentials import Credentials  # Importing Credentials for Google OAuth2
from googleapiclient.discovery import build  # Importing build for Google API client
import config_tv as config  # Importing custom configuration module
import psutil  # Importing psutil for system and process utilities
import requests  # Importing requests for making HTTP requests
import enum  # Importing enum for enumerations
import unicodedata  # Importing unicodedata for Unicode character database
import string  # Importing string module for string operations
import random  # Importing random module for generating random numbers
from datetime import datetime, timedelta, timezone  # Importing datetime for date and time operations
import streamlink  # Importing streamlink for streaming video
from google.auth.transport.requests import Request  # Importing Request for Google auth transport

refresh_title = "True"  # Setting refresh title flag to True

token_url = f"https://id.twitch.tv/oauth2/token?client_id={config.client_id}&client_secret={config.client_secret}&grant_type=client_credentials"  # URL for obtaining Twitch token
APP_TOKEN_FILE = "client_secret.json"  # File name for app token
GMAIL_TOKEN_FILE = "gmail_token.json"  # File name for Gmail token
USER_TOKEN_FILE = "user_token.json"  # File name for user token

SCOPES_GMAIL = [  # Scopes for Gmail API
    'https://www.googleapis.com/auth/gmail.readonly',
  ]

SCOPES_BRAND = [  # Scopes for YouTube API with brand account
    'https://www.googleapis.com/auth/youtube.force-ssl',
  ]

SCOPES = [  # Combined scopes for YouTube and Gmail APIs
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/gmail.readonly',
  ]

home_dir = os.path.expanduser("~")  # Getting the home directory path

def parse_arguments():  # Function to parse command-line arguments
    logging.info("function parse_arguments is called")
    parser = argparse.ArgumentParser(description="Twitch to YouTube Live Archive System")  # Creating argument parser
    parser.add_argument("yt_link", nargs="?", default=None, help="YouTube Video ID")  # Adding YouTube link argument
    parser.add_argument("rtmpkey", nargs="?", default=None, help="RTMP Server Type (defrtmp or bkrtmp)")  # Adding RTMP key argument
    args = parser.parse_known_args()  # Parsing known arguments
    arguments = sys.argv  # Getting system arguments
    return args, arguments  # Returning parsed arguments

###########################################offline_check###########################################
def offline_check_functions(live_url, spare_link, rtmp_server, titleforgmail):  # Asynchronous function to check offline status
    logging.info(f"function offline_check_functions is called with input arguments: live_url = {live_url}, spare_link = {spare_link}, rtmp_server = {rtmp_server}, titleforgmail = {titleforgmail}")
    state = {  # Initializing state dictionary
        'countdownhours': 0,  # Countdown hours
        'numberpart': 0,  # Number part
        'gmailcount': 0,  # Gmail count
        'countyt': 0,  # Count YouTube
        'live_url': live_url,  # Live URL
        'spare_link': spare_link,  # Spare link
        'rtmp_server': rtmp_server,  # RTMP server
        'titleforgmail': titleforgmail  # Title for Gmail
    }
    
    logging.info(f"Initializing offline detection monitoring service... With {state['live_url']}, {state['spare_link']}, {state['rtmp_server']}, {titleforgmail}")  # Logging initialization message

    def handle_stream_offline(state):  # Asynchronous function to handle stream offline
        logging.info(f"function handle_stream_offline is called with input arguments: state = {state}")  # Logging function call
        logging.info("Stream offline status detected - initiating shutdown sequence... and play ending screen")  # Logging offline status
        rtmp_key = config.rtmp_key if state['rtmp_server'] == "defrtmp" else config.rtmp_key_1  # Selecting RTMP key based on server
        ffmpeg = config.ffmpeg if state['rtmp_server'] == "defrtmp" else config.ffmpeg1  # Selecting ffmpeg based on RTMP key
        os.system(f'start {ffmpeg} -re -i ending.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  # Executing ffmpeg command
        if config.unliststream == "True":  # Checking if stream should be unlisted
            logging.info("Setting stream visibility to public...")  # Logging visibility change
            public_stream(state['live_url'])  # Making stream public
        subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
        subprocess.Popen(["start", "python", "check_tv.py", state['spare_link'], state['rtmp_server']], shell=True)  # Restarting script with spare link
        exit()  # Exiting the script
    
    def handle_youtube_status(state):  # Asynchronous function to handle YouTube status
        logging.info(f"function handle_youtube_status is called with input arguments: state = {state}")  # Logging function call
        feedback = is_youtube_livestream_live(state['live_url'])
        if feedback == "ERROR":  # Checking if YouTube livestream status is error
            logging.info("YouTube API verification failed - check credentials and connectivity...")  # Logging error
            state['countyt'] = 0  # Resetting YouTube count
            return True  # Returning True
        if feedback:  # Checking if YouTube livestream is live
            state['countyt'] = 0  # Resetting YouTube count
            return True  # Returning True
        else:  # Checking if YouTube livestream is not live
            twitch = get_twitch_client()  # Getting Twitch client
            streams = get_twitch_streams(twitch, config.username)  # Getting Twitch streams
            if not streams:  # Checking if streams are empty
                handle_stream_offline(state)
        logging.info("Stream connection terminated - initiating reload sequence...")  # Logging termination
        ffmpeg_exe = config.ffmpeg if state['rtmp_server'] == "defrtmp" else config.ffmpeg1  # Selecting ffmpeg executable
        subprocess.run(["taskkill", "/f", "/im", ffmpeg_exe])  # Killing ffmpeg process
        time.sleep(30)  # Waiting for 30 seconds
        logging.info("Checking for stream")  # Logging check
        if is_youtube_livestream_live(state['live_url']):  # Checking if YouTube livestream is live
            logging.info("Stream is back online return to offline check") # Logging return to offline check
        else:
                logging.info("YouTube Connection Failed Start on backup stream")  # Logging error
                switch_stream_config(state)  # Switching stream configuration
        state['countyt'] = 0 # Resetting Check YouTube count
        return True  # Returning True

    def switch_stream_config(state):  # Asynchronous function to switch stream configuration
        logging.info(f"function switch_stream_config is called with input arguments: state = {state}")  # Logging function call
        subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
        titleforgmail = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], "False", state['spare_link'])  # Creating/editing schedule
        state['rtmp_server'] = "defrtmp" if state['rtmp_server'] == "bkrtmp" else "bkrtmp"  # Switching RTMP server
        live_spare_url = api_create_edit_schedule("0", state['rtmp_server'], "True", "Null")  # Creating/editing schedule
        subprocess.Popen(["start", config.apiexe], shell=True)  # Starting API executable
        if config.unliststream == "True":  # Checking if stream should be unlisted
            public_stream(state['live_url'])  # Making stream public        
        state['numberpart'] += 1  # Incrementing number part
        state['live_url'], state['spare_link'] = state['spare_link'], live_spare_url  # Swapping live and spare links
        state['countdownhours'] = 0  # Resetting countdown hours
        state['countyt'] = 0  # Resetting YouTube count
        state['titleforgmail'] = titleforgmail  # Updating title for Gmail

    def public_stream(live_id):  # Function to make a YouTube stream public
        logging.info(f"function public_stream is called with input arguments: live_id = {live_id}")  # Logging function call
        hitryagain = 0  # Initialize retry counter
        while True:  # Infinite loop for retry mechanism
            try:
                service = get_service()  # Get the YouTube service client
                request = service.videos().update(  # Create a request to update video status
                    part='status',
                    body={
                        'id': live_id,  # Video ID to update
                        'status': {
                            'privacyStatus': 'public'  # Set privacy status to public
                        }
                    }
                )
                response = request.execute()  # Execute the request
                return response['id']  # Return the video ID from the response
                break  # Break the loop if successful
            except Exception as e:  # Handle exceptions
                if hitryagain == 3:  # Check if maximum retries reached
                    logging.info(f"Error and stopping because of error that can't fix")  # Log error message
                    if 'quotaExceeded' in str(e):  # Check for quota exceeded error
                        logging.info(f"Error and stopping because of API limit")  # Log API limit message
                        exit()  # Exit the program
                hitryagain += 1  # Increment retry counter
                logging.info(f"Error: {e}")  # Log the error
                time.sleep(5)  # Wait before retrying

    def find_gmail_title(state):  # Asynchronous function to find Gmail title
        logging.info(f"function find_gmail_title is called with input arguments: state = {state}")  # Logging function call
        while True:  # Infinite loop
            try:
                title = f"：{state['titleforgmail']}"  # Format title
                service = get_gmail_service()  # Get Gmail service
                now = datetime.now()  # Get current time
                minutes_ago = now - timedelta(minutes=2)  # Calculate time 2 minutes ago
                results = service.users().messages().list(userId='me', maxResults=2).execute()  # List messages
                messages = results.get('messages', [])  # Get messages
                if messages:  # Check if messages exist
                    for message in messages:  # Iterate over messages
                        msg = service.users().messages().get(userId='me', id=message['id']).execute()  # Get message details
                        received_time = datetime.fromtimestamp(int(msg['internalDate']) / 1000)  # Get received time
                        subject = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), '')  # Get subject
                        if received_time >= minutes_ago and title in subject:  # Check if message is recent and title matches
                            logging.info(f"Found email third party message: {subject}")  # Log found message
                            return True  # Return True if message is found
                return False  # Return False if no message is found
            except Exception as e:  # Handle exceptions
                logging.error(f"Error in find_gmail_title: {e}")  # Log error
                time.sleep(5)  # Sleep for 5 seconds

    def is_youtube_livestream_live(video_id):  # Function to check if YouTube livestream is live
        logging.info(f"function is_youtube_livestream_live is called with input arguments: video_id = {video_id}")  # Logging function call
        try:
          streams = streamlink.streams(f"https://youtube.com/watch?v={video_id}")  # Get streams from YouTube
          hls_stream = streams["best"]  # Get best quality stream
          return True  # Return True if stream is available
        except KeyError as e:  # Handle KeyError
            return False  # Return False if stream is not available
        except Exception as e:  # Handle exceptions
          logging.error(f"Error checking YouTube livestream status: {e}")  # Log error
          return "ERROR"  # Return ERROR if exception occurs
          
    while True:  # Infinite loop
        try:
            twitch = get_twitch_client()  # Getting Twitch client
            streams = get_twitch_streams(twitch, config.username)  # Getting Twitch streams
            if not streams:  # Checking if streams are empty
                handle_stream_offline(state)  # Handling stream offline
            state['countdownhours'] += 1  # Incrementing countdown hours
            state['gmailcount'] += 1  # Incrementing Gmail count
            state['countyt'] += 1  # Incrementing YouTube count
            if state['gmailcount'] == 12:  # Checking if Gmail count is 12
                if find_gmail_title(state):  # Finding Gmail title
                    logging.info("Third-party notification detected - switching to backup stream...")  # Logging notification
                    switch_stream_config(state)  # Switching stream configuration
                state['gmailcount'] = 0  # Resetting Gmail count
            if state['countyt'] == 6:  # Checking if YouTube count is 6
                handle_youtube_status(state)  # Handling YouTube status
            if state['countdownhours'] == 7871:  # Checking if countdown hours is 7871
                logging.info("Stream duration limit near 12h reached - initiating scheduled reload...")  # Logging scheduled reload
                switch_stream_config(state)  # Switching stream configuration
            time.sleep(5)  # Sleeping for 5 seconds
        except Exception as e:  # Catching exceptions
            logging.error(f"Error in offline check: {str(e)}", exc_info=True)  # Logging error
            time.sleep(15)  # Sleeping for 15 seconds
###########################################offline_check###########################################

def get_twitch_client():
    logging.info(f"function get_twitch_client is called")  # Logging function call
    try:
        token_response = requests.post(token_url)
        token_response.raise_for_status()  # Ensure the request was successful
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            raise ValueError("Access token not found in response")
        return access_token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining Twitch access token: {e}")
        return None
    except ValueError as ve:
        logging.error(f"Error in response data: {ve}")
        return None

def get_twitch_streams(access_token, username):
    logging.info(f"function get_twitch_streams is called with input arguments: access_token = {access_token}, username = {username}")  # Logging function call
    headers = {'Authorization': f'Bearer {access_token}', 'Client-ID': config.client_id}
    streams_response = requests.get(f'https://api.twitch.tv/helix/streams?user_login={username}', headers=headers)
    streams_data = streams_response.json()
    if 'data' not in streams_data:
        logging.error("'data' key not found in Twitch API response")
        logging.error(f"Invalid Twitch API response: {streams_data}")
        return None
    return streams_data['data']

def get_twitch_stream_title():
    logging.info(f"function get_twitch_stream_title is called")  # Logging function call
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    for attempt in range(MAX_RETRIES):
        try:
            twitch = get_twitch_client()
            streams = get_twitch_streams(twitch, config.username)
            if not streams:
                logging.info(f"No streams found (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
                continue
            if streams:  # Check if streams is not empty
             return streams[0]['title']
        except Exception as e:
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logging.error("Max retries reached, returning fallback title")
                return f"Stream_{datetime.now().strftime('%Y-%m-%d')}"

class TwitchResponseStatus(enum.Enum):  # Enum class for Twitch response status
    ONLINE = 0  # Online status
    OFFLINE = 1  # Offline status
    NOT_FOUND = 2  # Not found status
    UNAUTHORIZED = 3  # Unauthorized status
    ERROR = 4  # Error status

def check_process_running():  # Function to check if process is running
    logging.info(f"function check_process_running is called")  # Logging function call
    process_name = "countdriver.exe"  # Name of the process to check
    logging.info("Checking for existing browser automation processes...")  # Logging checking processes
    for process in psutil.process_iter(['pid', 'name']):  # Iterating over processes
        if process.info['name'] == process_name:  # Checking if process name matches
            logging.info("Browser automation process already running - waiting for completion...")  # Logging process running
            time.sleep(15)  # Waiting before checking again
            check_process_running()  # Recursively checking process
    logging.info("No conflicting processes found - proceeding...")  # Logging no conflicting processes
    return  # Returning from function

def get_service():  # Function to get YouTube service
    logging.info(f"function get_service is called")  # Logging function call
    creds = None  # Initialize credentials to None
    from google_auth_oauthlib.flow import InstalledAppFlow  # Import InstalledAppFlow for OAuth2
    try:
        if os.path.exists(USER_TOKEN_FILE):  # Check if user token file exists
          if config.brandacc == "False":  # Check if brand account is False
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load credentials from user token file
          if config.brandacc == "True":  # Check if brand account is True
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES_BRAND)  # Load credentials for brand account
        if not creds or not creds.valid:  # Check if credentials are invalid
            if creds and creds.expired and creds.refresh_token:  # Check if credentials are expired and refreshable
                creds.refresh(Request())  # Refresh credentials
            else:
              if config.brandacc == "False":  # Check if brand account is False
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
              if config.brandacc == "True":  # Check if brand account is True
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow for brand account
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Run local server for authentication
              with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                token.write(creds.to_json())  # Write credentials to file
        return build('youtube', 'v3', credentials=creds)  # Return YouTube service
    except Exception as e:  # Handle exceptions
        if "invalid_grant" in str(e):  # Check if exception is invalid grant
              if config.brandacc == "False":  # Check if brand account is False
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
              if config.brandacc == "True":  # Check if brand account is True
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow for brand account
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Run local server for authentication
              with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                token.write(creds.to_json())  # Write credentials to file
              return build('youtube', 'v3', credentials=creds)  # Return YouTube service
        else:
          logging.error(f"Error in get_service: {e}")  # Log error
          exit(1)  # Exit with error

def get_gmail_service():  # Function to get Gmail service
    logging.info(f"function get_gmail_service is called")  # Logging function call
    creds = None  # Initialize credentials to None
    from google_auth_oauthlib.flow import InstalledAppFlow  # Import InstalledAppFlow for OAuth2
    try:
        if config.brandacc == "True":  # Check if brand account is True
          if os.path.exists(GMAIL_TOKEN_FILE):  # Check if Gmail token file exists
            creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES_GMAIL)  # Load credentials from Gmail token file
        if config.brandacc == "False":  # Check if brand account is False
          if os.path.exists(USER_TOKEN_FILE):  # Check if user token file exists
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load credentials from user token file
        if not creds or not creds.valid:  # Check if credentials are invalid
            if creds and creds.expired and creds.refresh_token:  # Check if credentials are expired and refreshable
                creds.refresh(Request())  # Refresh credentials
            else:
              if config.brandacc == "True":  # Check if brand account is True
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              if config.brandacc == "False":  # Check if brand account is False
                logging.info("Gmail token not found. Start...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                   token.write(creds.to_json())  # Write credentials to file
        return build('gmail', 'v1', credentials=creds)  # Return Gmail service
    except Exception as e:  # Handle exceptions
        if "invalid_grant" in str(e):  # Check if exception is invalid grant
              if config.brandacc == "True":  # Check if brand account is True
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              if config.brandacc == "False":  # Check if brand account is False
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              return build('gmail', 'v1', credentials=creds)  # Return Gmail service
        else:
          logging.error(f"Error in get_gmail_service: {e}")  # Log error
          exit(1)  # Exit with error

def edit_live_stream(video_id, new_title, new_description):  # Function to edit live stream
  logging.info(f"function edit_live_stream is called with video_id: {video_id}, new_title: {new_title}, new_description: {new_description}")  # Logging function call
  hitryagain = 0  # Initialize retry counter
  while True:  # Infinite loop
    try:
       service = get_service()  # Get YouTube service
       category_id = '24'  # Set category ID
           
       request = service.videos().update(  # Create update request
             part="snippet",
             body={
                 "id": video_id,
                 "snippet": {
                     "title": new_title,
                     "description": new_description,
                     "categoryId": category_id
            }
        }
    )
       response = request.execute()  # Execute request
       return response['id']  # Return video ID
       break  # Break loop
    except Exception as e:  # Handle exceptions
     if hitryagain == 3:  # Check if retry limit is reached
      logging.info(f"Error and stoping because of error that can't fix")  # Log error
      if 'quotaExceeded' in str(e):  # Check if quota is exceeded
        logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
        exit()  # Exit with error
     hitryagain += 1  # Increment retry counter
     logging.info(f"Error: {e}")  # Log error
     time.sleep(5)  # Sleep for 5 seconds

def public_stream(live_id):  # Function to make stream public
  logging.info(f"function public_stream is called with live_id: {live_id}")  # Logging function call
  hitryagain = 0  # Initialize retry counter
  while True:  # Infinite loop
    try:
       service = get_service()  # Get YouTube service
       request = service.videos().update(  # Create update request
           part='status',
           body={
               'id': live_id,
               'status': {
                   'privacyStatus': 'public'
               }
           }
       )
       response = request.execute()  # Execute request
       return response['id']  # Return video ID
       break  # Break loop
    except Exception as e:  # Handle exceptions
     if hitryagain == 3:  # Check if retry limit is reached
      logging.info(f"Error and stoping because of error that can't fix")  # Log error
      if 'quotaExceeded' in str(e):  # Check if quota is exceeded
        logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
        exit()  # Exit with error
     hitryagain += 1  # Increment retry counter
     logging.info(f"Error: {e}")  # Log error
     time.sleep(5)  # Sleep for 5 seconds

def create_live_stream(title, description, kmself):  # Function to create live stream
    logging.info(f"function create_live_stream is called with title: {title}, description: {description}, kmself: {kmself}")  # Logging function call
    hitryagain = 0  # Initialize retry counter
    while True:  # Infinite loop
        try:
            service = get_service()  # Get YouTube service
            scheduled_start_time = datetime.now(timezone.utc).isoformat()  # Get current time in ISO format
                
            request = service.liveBroadcasts().insert(  # Create insert request
                part="snippet,status,contentDetails",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "scheduledStartTime": scheduled_start_time,
                    },
                    "status": {
                        "privacyStatus": kmself,
                        "selfDeclaredMadeForKids": False
                    },
                    "contentDetails": {
                        "enableAutoStart": True,
                        "enableAutoStop": True,
                        "latencyPrecision": "ultraLow"
                    }
                }
            )
            response = request.execute()  # Execute request
            video_id = response['id']  # Get video ID
            
            if config.playlist == "True" or config.playlist == "DOUBLE":  # Check if playlist is enabled
                try:
                    playlist_request = service.playlistItems().insert(  # Create playlist insert request
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": config.playlist_id0,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
                    playlist_request.execute()  # Execute playlist request
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id0}")  # Log success
                except Exception as playlist_error:  # Handle exceptions
                    logging.error(f"Failed to add video to playlist: {playlist_error}")  # Log error
            if config.playlist == "DOUBLE":  # Check if double playlist is enabled
                try:
                    playlist_request = service.playlistItems().insert(  # Create playlist insert request
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": config.playlist_id1,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
                    playlist_request.execute()  # Execute playlist request
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id1}")  # Log success
                except Exception as playlist_error:  # Handle exceptions
                    logging.error(f"Failed to add video to playlist: {playlist_error}")  # Log error
            return video_id  # Return video ID
        except Exception as e:  # Handle exceptions
          if hitryagain == 3:  # Check if retry limit is reached
           logging.info(f"Error and stoping because of error that can't fix")  # Log error
           if 'quotaExceeded' in str(e):  # Check if quota is exceeded
            logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
            exit()  # Exit with error
          hitryagain += 1  # Increment retry counter
          logging.info(f"Error: {e}")  # Log error
          time.sleep(5)  # Sleep for 5 seconds

def api_load(url, brandacc):  # Function to load API
      logging.info(f"function api_load is called with url: {url}, brandacc: {brandacc}")  # Logging function call
      logging.basicConfig(filename="tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')  # Configure logging
      logging.getLogger().addHandler(logging.StreamHandler())  # Add stream handler to logger
      logging.info("create api keying ---edit_tv---")  # Log info
      home_dir = os.path.expanduser("~")  # Get home directory
      logging.info("run with countdriver.exe and check")  # Log info
      check_process_running()  # Check if process is running
      subprocess.Popen(["start", "countdriver.exe"], shell=True)  # Start countdriver.exe
      options = Options()  # Create Chrome options
      chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  # Get Chrome user data directory
      options.add_argument(f"user-data-dir={chrome_user_data_dir}")  # Add user data directory to options
      options.add_argument(f"profile-directory={config.Chrome_Profile}")  # Add profile directory to options
      driver = webdriver.Chrome(options=options)  # Create Chrome driver
      driver.get(url)  # Open URL in Chrome
      time.sleep(3)  # Sleep for 3 seconds
      if brandacc == "Nope":  # Check if brand account is Nope
          nameofaccount = f"//div[contains(text(),'{config.accountname}')]"  # Get account name
      if brandacc == "havebrand":  # Check if brand account is havebrand
          nameofaccount = f"//div[contains(text(),'{config.brandaccname}')]"  # Get brand account name
      button_element = driver.find_element("xpath", nameofaccount)  # Find account button
      button_element.click()  # Click account button
      time.sleep(3)  # Sleep for 3 seconds
      element = driver.find_element("xpath", "(//button[@jsname='LgbsSe' and contains(@class, 'VfPpkd-LgbsSe-OWXEXe-INsAgc')])[2]")  # Find button element
      element.click()  # Click button element
      subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill countdriver.exe
      logging.info("finish idk ---edit_tv---")  # Log info
      time.sleep(5)  # Sleep for 5 seconds
      driver.quit()  # Quit Chrome driver

def edit_rtmp_key(driver, rtmp_key_select):  # Function to edit RTMP key using Selenium WebDriver
    logging.info(f"function edit_rtmp_key is called with driver: {driver}, rtmp_key_select: {rtmp_key_select}")  # Logging function call
    countfuckingshit = 0  # Counter for retry attempts
    while True:  # Infinite loop for retrying
        try:
            driver.find_element(By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']").click()  # Clicking dropdown icon
            time.sleep(3)  # Waiting for 3 seconds
            if rtmp_key_select == "bkrtmp":  # Checking if RTMP key is "bkrtmp"
                xpath = "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname1 + " (')]]"  # XPath for "bkrtmp"
                element2 = driver.find_element(By.XPATH, xpath)  # Finding element for "bkrtmp"
                element2.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if rtmp_key_select == "defrtmp":  # Checking if RTMP key is "defrtmp"
                xpath = "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname + " (')]]"  # XPath for "defrtmp"
                element3 = driver.find_element(By.XPATH, xpath)  # Finding element for "defrtmp"
                element3.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if config.disablechat == "True":  # Checking if chat should be disabled
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(By.XPATH, "//li[@id='customization']").click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(By.XPATH, "//*[@id='chat-enabled-checkbox']").click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Clicking save button
            time.sleep(10)  # Waiting for 10 seconds
            logging.info("RTMP key configuration updated successfully...")  # Logging success message
            driver.quit()  # Quitting the driver
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
        except Exception as e:  # Handling exceptions
            logging.error(f"Error in edit_rtmp_key: {str(e)}")  # Logging error message
            driver.refresh()  # Refreshing the driver
            time.sleep(15)  # Waiting for 15 seconds
            countfuckingshit += 1  # Incrementing retry counter
            if countfuckingshit == 3:  # Checking if retry limit is reached
                logging.info("edit rtmp key fail shutdown script")  # Logging failure message
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
                exit()  # Exiting the script
        finally:
            break  # Breaking the loop

def check_is_live_api(url, ffmpeg, rtmp_server):  # Function to check if stream is live using API
    logging.info(f"function check_is_live_api is called with url: {url}, ffmpeg: {ffmpeg}, rtmp_server: {rtmp_server}")  # Logging function call
    logging.info("Waiting for 40sec live on YouTube")  # Logging wait message
    time.sleep(40)  # Waiting for 40 seconds
    new_url = f"https://youtube.com/watch?v={url}"  # Constructing new URL
    count_error = 0  # Initializing error counter
    MAX_RETRIES = 3  # Maximum number of retries
    text = "this" if rtmp_server == "defrtmp" else "api_this"  # Setting text based on RTMP server
    while True:  # Infinite loop for retrying
        try:
            streams = streamlink.streams(new_url)  # Getting streams from URL
            hls_stream = streams["best"]  # Selecting best stream
            logging.info('It is live now')  # Logging live status
            break  # Breaking the loop
        except KeyError as e:  # Handling KeyError exceptions
            logging.error(f'Stream not available: {str(e)}')  # Logging error message
            logging.info('The stream is messed up. Trying again...')  # Logging retry message
            time.sleep(2)  # Waiting for 2 seconds
            subprocess.run(["taskkill", "/f", "/im", ffmpeg])  # Killing ffmpeg process
            subprocess.Popen(["start", "python", "relive_tv.py", text], shell=True)  # Restarting relive_tv script
            time.sleep(35)  # Waiting for 35 seconds
            count_error += 1  # Incrementing error counter
        if count_error >= MAX_RETRIES:  # Checking if retry limit is reached
            logging.info("Retry limit exceeded. Shutting down.")  # Logging shutdown message
            subprocess.Popen(["start", "python", "check_tv.py", "KILL"], shell=True)  # Restarting check_tv script with KILL
            exit()  # Exiting the script

def api_create_edit_schedule(part_number, rtmp_server, is_reload, stream_url):  # Asynchronous function to create/edit schedule via API
    logging.info(f"function api_create_edit_schedule is called with part_number: {part_number}, rtmp_server: {rtmp_server}, is_reload: {is_reload}, stream_url: {stream_url}")  # Logging function call
    filename = None  # Initializing filename
    description = None  # Initializing description
    if is_reload == "False" or is_reload == "EDIT":  # Checking if reload is False or EDIT
        stream_title = get_twitch_stream_title()  # Getting Twitch stream title
        clean_title = ''.join('' if unicodedata.category(c) == 'So' else c for c in stream_title)  # Cleaning title
        clean_title = clean_title.replace("<", "").replace(">", "")  # Removing angle brackets
        if part_number == "0":  # Checking if part number is 0
            filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}"  # Constructing filename
        else:
            part_num = int(part_number) + 1  # Incrementing part number
            filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')} | PART{part_num}"  # Constructing filename with part number
        if len(filename) > 100:  # Checking if filename exceeds 100 characters
            if part_number == "0":  # Checking if part number is 0
                max_title_len = 100 - len(config.username) - len(datetime.now().strftime("%Y-%m-%d")) - len(" | " * 2)  # Calculating max title length
            else:
                max_title_len = 100 - len(config.username) - len(datetime.now().strftime("%Y-%m-%d")) - len(" | " * 3) - len(f"part {part_num}")  # Calculating max title length with part number
            clean_title = clean_title[:max_title_len-3] + "..."  # Truncating title
            if part_number == "0":  # Checking if part number is 0
                filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}"  # Constructing truncated filename
            else:
                filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')} | part {part_num}"  # Constructing truncated filename with part number
        if len(filename) > 100:  # Checking if filename still exceeds 100 characters
            if part_number == "0":  # Checking if part number is 0
                filename = f"{config.username} | {datetime.now().strftime('%Y-%m-%d')}"  # Constructing minimal filename
            else:
                filename = f"{config.username} | {datetime.now().strftime('%Y-%m-%d')} | part {part_num}"  # Constructing minimal filename with part number
        # DON'T REMOVE THIS WATERMARK
        description = f"Original broadcast from https://twitch.tv/{config.username} [Stream Title: {clean_title}] Archived using open-source tools: https://bit.ly/archivescript Service by Karsten Lee, Join My Community Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"  # Constructing description
    try:
        if is_reload == "True":  # Checking if reload is True
            filename = f"{config.username} (WAITING FOR STREAMER)"  # Constructing waiting filename
            description = f"WAITING FOR {config.username}, THIS OPEN-SOURCE ARCHIVE SCRIPT IS CREATED BY KARSTEN LEE, PROJECT: https://is.gd/archivescript , Join Karsten Lee's Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"  # Constructing waiting description
        if stream_url == "Null":  # Checking if stream URL is Null
            logging.info('Initiating API request for stream creation...')  # Logging API request initiation
            privacy_status = "public" if config.unliststream == "False" else "unlisted"  # Setting privacy status
            stream_url = create_live_stream(filename, description, privacy_status)  # Creating live stream
            logging.info("==================================================")  # Logging separator
            if config.playlist == "True":  # Checking if playlist is True
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0}")  # Logging playlist addition
            elif config.playlist == "DOUBLE":  # Checking if playlist is DOUBLE
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0} AND {config.playlist_id1}")  # Logging double playlist addition
            else:
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url}")  # Logging stream creation
            logging.info("==================================================")  # Logging separator
            setup_stream_settings(stream_url, rtmp_server)  # Setting up stream settings
        if is_reload == "EDIT":  # Checking if reload is EDIT
            logging.info("Updating stream metadata and title...")  # Logging metadata update
            edit_live_stream(stream_url, filename, description)  # Editing live stream
            return filename  # Returning filename
        if is_reload == "True":  # Checking if reload is True
            return stream_url  # Returning stream URL
        if is_reload == "False":  # Checking if reload is False
            logging.info("Start stream relay")
            initialize_stream_relay(stream_url, rtmp_server)  # Initializing stream relay
            edit_live_stream(stream_url, filename, description)  # Editing live stream
            return filename  # Returning filename
    except Exception as e:  # Handling exceptions
        logging.error(f"Critical error encountered during execution: {e}")  # Logging critical error
        exit()  # Exiting the script

def setup_stream_settings(stream_url, rtmp_server):  # Asynchronous function to set up stream settings
    logging.info(f"function setup_stream_settings is called with stream_url: {stream_url}, rtmp_server: {rtmp_server}")  # Logging function call
    check_process_running()  # Checking if process is running
    subprocess.Popen(["start", "countdriver.exe"], shell=True)  # Starting countdriver process
    options = Options()  # Creating Chrome options
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  # Setting Chrome user data directory
    options.add_argument(f"user-data-dir={chrome_user_data_dir}")  # Adding user data directory to options
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  # Adding profile directory to options
    driver = None  # Initializing driver
    try:
        driver = webdriver.Chrome(options=options)  # Creating Chrome WebDriver
        url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  # Constructing URL to live stream
        driver.get(url_to_live)  # Navigating to URL
        time.sleep(5)  # Waiting for 5 seconds
        driver.refresh()  # Refreshing the page
        time.sleep(30)  # Waiting for 30 seconds
        logging.info("Configuring RTMP key and chat settings...")  # Logging configuration message
        edit_rtmp_key(driver, rtmp_server)  # Editing RTMP key
    except SessionNotCreatedException as e:
        logging.error(f"Session not created: {e} KILL ALL CHROME PROCESS AND TRY AGAIN")
        subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Killing CHROME PROCESS
        time.sleep(3)
        driver = webdriver.Chrome(options=options)  # Creating Chrome WebDriver
        url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  # Constructing URL to live stream
        driver.get(url_to_live)  # Navigating to URL
        time.sleep(5)  # Waiting for 5 seconds
        driver.refresh()  # Refreshing the page
        time.sleep(30)  # Waiting for 30 seconds
        logging.info("Configuring RTMP key and chat settings...")  # Logging configuration message
        edit_rtmp_key(driver, rtmp_server)  # Editing RTMP key
    finally:
        if driver:  # Checking if driver is initialized
            driver.quit()  # Quitting the driver
        subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process

def initialize_stream_relay(stream_url, rtmp_server):  # Asynchronous function to initialize stream relay
    logging.info(f"function initialize_stream_relay is called with stream_url: {stream_url}, rtmp_server: {rtmp_server}")  # Logging function call
    rtmp_relive = "this" if rtmp_server == "defrtmp" else "api_this"  # Setting RTMP server for relay
    subprocess.Popen(["start", "python", "relive_tv.py", rtmp_relive], shell=True)  # Starting relive_tv script
    ffmpeg_exe = config.ffmpeg if rtmp_server == "defrtmp" else config.ffmpeg1  # Selecting ffmpeg executable
    ffmpeg_1exe = config.ffmpeg1 if rtmp_server == "defrtmp" else config.ffmpeg  # Selecting ffmpeg executable
    check_is_live_api(stream_url, ffmpeg_exe, rtmp_server)  # Checking live API
    subprocess.run(["taskkill", "/f", "/im", ffmpeg_1exe])  # Killing ffmpeg process
    rtmp_key = config.rtmp_key if rtmp_server == "bkrtmp" else config.rtmp_key_1  # Selecting RTMP key
    os.system(f'start {ffmpeg_1exe} -re -i blackscreen.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  # Starting ffmpeg for normal stream

def start_check(live_url, rtmp_server):  # Asynchronous function to start stream check
    logging.info(f"function start_check is called with live_url: {live_url}, rtmp_server: {rtmp_server}")  # Logging function call
    live_spare_url = None  # Initializing spare URL
    logging.info("Starting stream monitoring process...")  # Logging start message
    if not live_url:  # Checking if live URL is missing
        logging.error("Missing live URL - cannot start monitoring")  # Logging error message
        exit(1)  # Exiting with error code
    if rtmp_server not in ["defrtmp", "bkrtmp"]:  # Checking if RTMP server is invalid
        logging.error(f"Invalid RTMP server type: {rtmp_server}")  # Logging error message
        exit(1)  # Exiting with error code
    logging.info("Launching streaming API process...")  # Logging API launch message
    try:
        subprocess.Popen(["start", config.apiexe], shell=True)  # Starting API executable
    except Exception as e:  # Handling exceptions
        logging.error(f"Failed to start API process: {str(e)}")  # Logging error message
        exit(1)  # Exiting with error code
    try:
     if rtmp_server == "bkrtmp":  # Checking if RTMP server is "bkrtmp"
       logging.info("Starting with backup stream rtmp... and check")  # Logging relay start message
       subprocess.Popen(["start", "python", "relive_tv.py", "api_this"], shell=True)  # Starting relive_tv script for "bkrtmp"
       check_is_live_api(live_url, config.ffmpeg1, rtmp_server) # Checking the stream using the streamlink
       rtmp_server = "defrtmp"  # Switching RTMP server
     elif rtmp_server == "defrtmp":  # Checking if RTMP server is "defrtmp"
       logging.info("Starting with default stream rtmp... and check")  # Logging relay start message
       subprocess.Popen(["start", "python", "relive_tv.py", "this"], shell=True)  # Starting relive_tv script for "defrtmp"
       check_is_live_api(live_url, config.ffmpeg, rtmp_server) # Checking the stream using the streamlink
       rtmp_server = "bkrtmp"  # Switching RTMP server
    except Exception as e:  # Handling exceptions
        logging.error(f"Failed to start relay process: {str(e)}")  # Logging error message
        exit(1)  # Exiting with error code
    logging.info("Stream relay process started successfully")  # Logging success message
    try:
        titleforgmail = api_create_edit_schedule("0", rtmp_server, "EDIT", live_url)  # Creating/editing schedule
        logging.info('edit finished continue the stream')  # Logging edit completion
        logging.info(f"Successfully retrieved stream title: {titleforgmail}")  # Logging retrieved title
    except UnboundLocalError:  # Handling UnboundLocalError
        logging.warning("Encountered UnboundLocalError when getting title - continuing with default")  # Logging warning
    except Exception as e:  # Handling exceptions
        logging.error(f"Error getting stream title: {str(e)} - continuing with default")  # Logging error message
    try:
        logging.info("Loading backup stream configuration...")  # Logging backup configuration
        live_spare_url = api_create_edit_schedule("0", rtmp_server, "True", "Null")  # Creating backup schedule
        logging.info(f"Backup stream URL configured: {live_spare_url}")  # Logging backup URL
    except Exception as e:  # Catching any exceptions that occur
        logging.error(f"Failed to create backup stream: {str(e)}")  # Logging error message with exception details
    logging.info("Starting offline detection and countdown timer...")  # Logging the start of offline detection and countdown timer
    offline_check_functions(live_url, live_spare_url, rtmp_server, titleforgmail)  # Initiating offline check functions with provided parameters

def initialize_and_monitor_stream(yt_link=None, rtmp_info=None):  # Asynchronous function to initialize and monitor stream
    logging.info(f"function initialize_and_monitor_stream is called with yt_link: {yt_link}, rtmp_info: {rtmp_info}")  # Logging function call
    try:
        args, arguments = parse_arguments()  # Parsing command-line arguments
        if yt_link is None and rtmp_info is None:  # Checking if YouTube link and RTMP info are not provided
            if len(arguments) < 2:  # Checking if insufficient arguments are provided
                logging.info("==================================================")  # Logging separator
                logging.info("NO ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # Logging no argument available
                logging.info(f"ARCHIVE USER: {config.username}")  # Logging archive user
                logging.info("==================================================")  # Logging separator
                yt_link = "Null"  # Setting YouTube link to Null
                rtmp_info = "Null"  # Setting RTMP info to Null
            else:
                yt_link = arguments[1]  # Setting YouTube link from arguments
                rtmp_info = arguments[2] if len(arguments) > 2 else None  # Setting RTMP info from arguments
                if yt_link == "KILL":  # Checking if KILL command is given
                    logging.info("close all exe")  # Logging close all executables
                    subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg])  # Killing ffmpeg process
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1])  # Killing ffmpeg1 process
                    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
                    exit()  # Exiting the script
                if len(arguments) < 3:  # Checking if RTMP argument is missing
                    logging.error("Missing required RTMP argument")  # Logging missing RTMP argument
                    exit(1)  # Exiting with error code
                if len(yt_link) != 11:  # Checking if YouTube link is invalid
                    logging.error(f"Invalid argument for ARG1: {yt_link}. Must be 11 characters long YouTube Video ID")  # Logging invalid YouTube link
                    exit(1)  # Exiting with error code
                if rtmp_info not in ["defrtmp", "bkrtmp"]:  # Checking if RTMP info is invalid
                    logging.error(f"Invalid argument for ARG2: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'")  # Logging invalid RTMP info
                    exit(1)  # Exiting with error code
                logging.info("==================================================")  # Logging separator
                logging.info("INPUT ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # Logging input argument available
                logging.info(f"ARG1: {yt_link} ARG2: {rtmp_info}")  # Logging arguments
                logging.info(f"ARCHIVE USER: {config.username}")  # Logging archive user
                logging.info("==================================================")  # Logging separator
        if rtmp_info not in ["defrtmp", "bkrtmp", "Null"]:  # Checking if RTMP server type is invalid
            logging.error(f"Invalid RTMP server type: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'")  # Logging invalid RTMP server type
            exit(1)  # Exiting with error code
        live_url = None  # Initializing live URL
        rtmp_server = None  # Initializing RTMP server
        if yt_link == "Null":  # Checking if YouTube link is Null
            logging.info("Starting live API check to get initial stream URL")  # Logging starting live API check
            rtmp_server = "defrtmp"  # Setting RTMP server to default
            try:
                live_url = api_create_edit_schedule("0", rtmp_server, "True", "Null")  # Creating/editing schedule via API
                logging.info(f"Successfully created new stream with URL: {live_url}")  # Logging successful stream creation
            except Exception as api_error:  # Handling API exceptions
                logging.error(f"Failed to create stream via API: {str(api_error)}")  # Logging API error
                raise  # Raising exception
        else:
            live_url = yt_link  # Setting live URL to YouTube link
            rtmp_server = rtmp_info  # Setting RTMP server to RTMP info
            logging.info(f"Using provided YouTube link: {live_url} with RTMP server: {rtmp_server}")  # Logging provided YouTube link and RTMP server
        logging.info("Waiting for stream to go live...")  # Logging waiting for stream
        while True:  # Infinite loop
            try:
                twitch = get_twitch_client()  # Getting Twitch client
                streams = get_twitch_streams(twitch, config.username)  # Getting Twitch streams
                if streams:  # Checking if streams are available
                    stream = streams[0]  # Getting the first stream
                    logging.info(f"Stream is now live! Title From Twitch: {stream['title']}")  # Logging stream is live
                    break  # Breaking the loop
                else:
                    time.sleep(5)  # Waiting before retrying
            except Exception as e:  # Handling exceptions
                logging.error(f"Error checking stream status: {str(e)}")  # Logging error
                time.sleep(30)  # Waiting before retrying
        logging.info("Twitch stream detected - initializing monitoring process")  # Logging Twitch stream detected
        start_check(live_url, rtmp_server)  # Starting check
    except Exception as e:  # Handling exceptions
        logging.error(f"Error in initialize_and_monitor_stream: {str(e)}", exc_info=True)  # Logging error
        logging.error("Critical error encountered - terminating script execution")  # Logging critical error
        exit(1)  # Exiting with error code

if __name__ == "__main__":  # Checking if the script is run directly
    logging.basicConfig(filename="check_tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')  # Configuring logging settings
    logging.getLogger().addHandler(logging.StreamHandler())  # Adding stream handler to logger
    initialize_and_monitor_stream()  # Running the function to initialize and monitor stream
    exit()  # Exiting the script
