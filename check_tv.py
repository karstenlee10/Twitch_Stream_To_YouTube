# Standard library imports
import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import sys
import time
import unicodedata
import importlib
import urllib.request
from datetime import datetime, timedelta, timezone
import winreg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ctypes import windll
from PIL import Image, ImageDraw, ImageFont
import re
import zipfile
from io import BytesIO
import psutil
import requests
import streamlink
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, SessionNotCreatedException, TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local project imports
from logger_config import check_tv_logger as logging
import config_tv as config

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

# Mapping of script to font file and download URL
FONT_MAP = {
    'CJK': {
        'file': 'NotoSansCJKjp-Regular.otf',
        'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf'
    },
    'Hangul': {
        'file': 'NotoSansCJKkr-Regular.otf',
        'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf'
    },
    'Arabic': {
        'file': 'NotoSansArabic-Regular.ttf',
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf'
    },
    'Devanagari': {
        'file': 'NotoSansDevanagari-Regular.ttf',
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'
    },
    'default': {
        'file': 'NotoSans-Regular.ttf',
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf'
    }
}

###########################################offline_check###########################################
def offline_check_functions(
    live_url, 
    spare_link, 
    rtmp_server, 
    title,
    REFRESH_TYPE
    ):  # Asynchronous function to check offline status
    state = {  # Initializing state dictionary
        'numberpart': 0,  # Number part
        'gmail_checking': True,  # Gmail count
        'countyt': True,  # Count YouTube
        'live_url': live_url,  # Live URL
        'spare_link': spare_link,  # Spare link
        'rtmp_server': rtmp_server,  # RTMP server
        'titleforgmail': title,  # Title for Gmail
        'category': "Null",
        'input_state': False,
        'thread_in_use': False,
        'exit_flag': False
    }
    
    logging.info(f"Initializing offline detection monitoring service... With {state['live_url']}, {state['spare_link']}, {state['rtmp_server']}, {state['titleforgmail']}")  # Logging initialization message

    if not config.livestreamautostop:
        state['countyt'] = False

    def ending_stream(stream_url):  # Function to handle stream ending
       check_process_running()  # Checking if process is running
       subprocess.Popen(["start", "countdriver.exe"], shell=True)  # Starting countdriver process
       options = Options()  # Creating Chrome options
       chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  # Setting Chrome user data directory
       options.add_argument(f"user-data-dir={chrome_user_data_dir}")  # Adding user data directory to options
       options.add_argument(f"profile-directory={config.Chrome_Profile}")  # Adding profile directory to options
       driver = None  # Initializing driver
       try_count = 0  # Initializing try count
       while True:  # Infinite loop
          try:
               
               time.sleep(3)
               driver = webdriver.Chrome(options=options)  # Creating Chrome WebDriver
               url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  # Constructing URL to live stream
               driver.get(url_to_live)  # Navigating to URL
               while True:
                   try:
                       WebDriverWait(driver, 30).until(
                           EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/div/div/ytls-broadcast-metadata/div[2]/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]'))
                       )
                       break
                   except TimeoutException:
                       try:
                           error_element = driver.find_element(By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[3]/ytls-live-dashboard-error-renderer/div/yt-icon')
                           if error_element:
                               logging.info("Error element found - YouTube Studio is in error state")
                               driver.refresh()
                               time.sleep(2)
                               try_count += 1
                               if try_count >= 3:
                                   logging.error("3 consecutive errors detected - KILLING ALL PROCESSES")
                                   os.system("start check_tv.py KILL")
                                   exit(1)
                       except:
                           logging.info("Element not found after 30s, refreshing page...")
                           driver.refresh()
                           time.sleep(2)
                           try_count += 1
                           if try_count >= 3:
                               logging.error("3 consecutive timeouts detected - KILLING ALL PROCESSES")
                               os.system("start check_tv.py KILL")
                               exit(1)
               time.sleep(2)
               logging.info("Stop livestream manually...")  # Logging configuration message
               try:
                    header_title = driver.find_element(By.XPATH, '//*[@id="header-title"]')
                    if header_title:
                       logging.info("Found already ended, breaking loop...")
                       driver.quit()  # Quitting the driver
                       subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
                       if driver:  # Checking if driver is initialized
                            driver.quit()  # Quitting the driver
                       break
               except:
                   pass
               driver.find_element(By.XPATH, '//*[@id="end-stream-button"]').click()  # Clicking edit button
               time.sleep(3)  # Waiting for 5 seconds
               driver.find_element(By.XPATH, '/html/body/ytcp-confirmation-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div[2]/ytcp-button[2]/ytcp-button-shape/button').click()  # Clicking edit button
               time.sleep(10)  # Waiting for 5 seconds
               logging.info("livestream ended successfully...")  # Logging success message
               driver.quit()  # Quitting the driver
               subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
               if driver:  # Checking if driver is initialized
                        driver.quit()  # Quitting the driver
               break  # Breaking the loop
          except SessionNotCreatedException as e:
              try_count += 1  # Incrementing try count
              if try_count >= 3:  # Checking if try count exceeds limit
                  logging.error(f"Session not created: [{e}] Critical Error KILL ALL")
                  os.system("start check_tv.py KILL")
                  exit(1)  # Exiting the script
              if "DevToolsActivePort file doesn't exist" in str(e):
                  logging.error(f"Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.")
              else:
                  logging.error(f"Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN")
              subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Killing CHROME PROCESS
              time.sleep(5)
          except Exception as e:
              try_count += 1  # Incrementing try count
              if try_count >= 3:  # Checking if try count exceeds limit
                  logging.error(f"Session not created: [{e}] Critical Error KILL ALL")
                  os.system("start check_tv.py KILL")
                  exit(1)  # Exiting the script
              logging.error(f"Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN")
              subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Killing CHROME PROCESS
              time.sleep(5)    

    def handle_stream_offline(state):  # Asynchronous function to handle stream offline
        if state['input_state']:
          if state['rtmp_server'] == "defrtmp":
            subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1])  # Killing ffmpeg executable
          else:
            subprocess.run(["taskkill", "/f", "/im", config.ffmpeg])  # Killing ffmpeg executable
        if config.playvideo:  # Checking if mode is yesend
          logging.info("Stream offline status detected - initiating shutdown sequence... and play ending screen")  # Logging offline status
          # Select RTMP key and ffmpeg path based on server type
          if state['rtmp_server'] == "defrtmp":
              rtmp_key = config.rtmp_key_1  # Use default RTMP key
              ffmpeg = config.ffmpeg1      # Use default ffmpeg path
          else:
              rtmp_key = config.rtmp_key  # Use backup RTMP key
              ffmpeg = config.ffmpeg     # Use backup ffmpeg path
          os.system(f'{ffmpeg} -re -i ending.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  # Executing ffmpeg command
        if config.unliststream:  # Checking if stream should be unlisted
            logging.info("Setting stream visibility to public...")  # Logging visibility change
            public_stream(state['live_url'])  # Making stream public
        logging.info("ending the stream...")  # Logging return to offline check
        if not config.livestreamautostop:
          ending_stream(state['live_url'])  # Handling stream offline
        subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
        subprocess.Popen(["start", "cmd", "/k", "py", "check_tv.py", state['spare_link'], state['rtmp_server']], shell=True)  # Restarting script with spare link
        state['exit_flag'] = True; return  # Exiting the script

    def switch_stream_config(state):  # Asynchronous function to switch stream configuration
        state['numberpart'] += 1  # Incrementing number part
        state['titleforgmail'] = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], False, state['spare_link'])  # Editing schedule
        if state['rtmp_server'] == "bkrtmp":
            state['rtmp_server'] = "defrtmp"
        else:
            state['rtmp_server'] = "bkrtmp"
        live_spare_url = api_create_edit_schedule(0, state['rtmp_server'], True, "Null")  # Creating schedule
        subprocess.Popen(["start", config.apiexe], shell=True)  # Starting API executable
        if config.unliststream == True:  # Checking if stream should be unlisted
            public_stream(state['live_url'])  # Making stream public
        if config.unliststream and config.public_notification:
            logging.info("new stream back to unlisted")
            unlist_stream(state['spare_link'])  # Making stream unlisted
        logging.info("ending the old stream...")  # Logging return to offline check
        if not config.livestreamautostop:
          ending_stream(state['live_url'])  # Handling stream offline
        state['live_url'] = state['spare_link']  # Swapping live and spare links
        state['spare_link'] = live_spare_url  # Swapping live and spare links

    def public_stream(live_id):  # Function to make a YouTube stream public
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
            except Exception as e:  # Handle exceptions
               if 'quotaExceeded' in str(e):  # Check if quota is exceeded
                 logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
                 state['exit_flag'] = True; return  # Exit with error
               if hitryagain == 3:  # Check if retry limit is reached
                logging.info(f"Error and stoping because of error that can't fix")  # Log error
               hitryagain += 1  # Increment retry counter
               logging.info(f"Error: {e}")  # Log error
               time.sleep(5)  # Sleep for 5 seconds

    def unlist_stream(live_id):  # Function to make a YouTube stream unlisted
        hitryagain = 0  # Initialize retry counter
        while True:  # Infinite loop for retry mechanism
            try:
                service = get_service()  # Get the YouTube service client
                request = service.videos().update(  # Create a request to update video status
                    part='status',
                    body={
                        'id': live_id,  # Video ID to update
                        'status': {
                            'privacyStatus': 'unlisted'  # Set privacy status to public

                        }
                    }
                )
                response = request.execute()  # Execute the request
                return response['id']  # Return the video ID from the response
            except Exception as e:  # Handle exceptions
               if 'quotaExceeded' in str(e):  # Check if quota is exceeded
                 logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
                 state['exit_flag'] = True; return  # Exit with error
               if hitryagain == 3:  # Check if retry limit is reached
                logging.info(f"Error and stoping because of error that can't fix")  # Log error
               hitryagain += 1  # Increment retry counter
               logging.info(f"Error: {e}")  # Log error
               time.sleep(5)  # Sleep for 5 seconds

    def is_youtube_livestream_live(video_id):  # Function to check if YouTube livestream is live
        TRY = 0
        while True:  # Infinite loop
           try:
              streams = streamlink.streams(f"https://youtube.com/watch?v={video_id}")  # type: ignore Get streams from YouTube
              hls_stream = streams["best"]  # Get best quality stream
              return True  # Return True if stream is available
           except KeyError as e:  # Handle KeyError
              TRY += 1
              time.sleep(5)
              if TRY == 3:
               logging.info(f"try 3 times is still offline")  # Log error
               return False  # Return False if stream is not available
           except Exception as e:  # Handle exceptions
              logging.error(f"Error checking YouTube livestream status: {e}")  # Log error
              return "ERROR"  # Return ERROR if exception occurs

    def check_twitch_category(state):
      while True:
       try:
          data = get_twitch_streams()
          if isinstance(data, list) and len(data) > 0:
            # Extract game_name from the first item
            state["category"] = data[0].get('game_name', 'Game name not found')
            break
          else:
            logging.info("Error getting category")
            time.sleep(25)
       except (SyntaxError, ValueError, TypeError) as e:
          logging.info("Error getting category")
          time.sleep(25)
      while True:
       try:
          data = get_twitch_streams()
          if isinstance(data, list) and len(data) > 0:
            # Extract game_name from the first item
            new_category = data[0].get('game_name', 'Game name not found')
            if new_category != state["category"]:
              while state['thread_in_use']:
                time.sleep(1)
              state['thread_in_use'] = True
              state['titleforgmail'] = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], "EDIT", state['live_url'])  # Editing schedule
              state['thread_in_use'] = False
              state["category"] = new_category
          else:
            logging.info("Error getting category")
            time.sleep(25)
       except (SyntaxError, ValueError, TypeError) as e:
          logging.info("Error getting category")
          time.sleep(25)

    def refresh_stream_title(state):  # Function to refresh stream title
      while True:
        try:
          twitch_title = get_twitch_stream_title()  # Getting Twitch stream title
          yt_title = get_youtube_stream_title(state['live_url'])
          TESTING = "[TESTING WILL BE REMOVE AFTER]" if config.exp_tesing else ""
          newtitle = ''.join('' if unicodedata.category(c) == 'So' else c for c in (twitch_title or yt_title or "")).replace("<", "").replace(">", "")  # Cleaning title
          part_suffix = f" (PART{state['numberpart']})" if state['numberpart'] > 0 else ""
          if config.StreamerName == "Null":
            username = config.username
          else:
            username = config.StreamerName
          filename = f"{username} | {newtitle} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}"
          if len(filename) > 100:  # Checking if filename exceeds 100 characters
              max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 2) - len(part_suffix) - len(TESTING)
              clean_title = newtitle[:max_title_len-3] + "..."
              filename = f"{username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}"
          if yt_title != filename:  # Checking if title is different:
                while state['thread_in_use']:
                    time.sleep(1)  # 每秒检查一次线程使用状态
                state['thread_in_use'] = True
                logging.info(f"Title discrepancy detected: {filename} does not match {state['titleforgmail']}")  # Logging discrepancy
                state['titleforgmail'] = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], "EDIT", state['live_url'])  # Editing schedule
                logging.info('edit finished continue the stream')  # Logging edit completion
                logging.info(f"Successfully retrieved stream title: {state['titleforgmail']} contiune checking")  # Logging retrieved title
                state['thread_in_use'] = False
                time.sleep(60)
          else:
               state['titleforgmail'] = yt_title
               time.sleep(60)
        except UnboundLocalError:  # Handling UnboundLocalError
               logging.warning("Encountered UnboundLocalError when getting title - disabling gmail checking and title checking continue at your own risk")  # Logging warning
               state['thread_in_use'] = False
               state['gmail_checking'] = False
               break
        except Exception as e:  # Handling exceptions
               logging.error(f"Error getting stream title: {str(e)} - disabling gmail checking and title checking continue at your own risk")  # Logging error message
               state['thread_in_use'] = False
               state['gmail_checking'] = False
               break

    def find_gmail_title(state):  # Asynchronous function to find Gmail title
        while True:  # Infinite loop
            try:
                if not state['gmail_checking']:
                  logging.info("gmail checking is disable")
                  break
                title = state['titleforgmail']  # Format title
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
                        sender = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from'), '')  # Get sender
                        if received_time >= minutes_ago and title in subject and "no-reply@youtube.com" in sender:  #  Check if message is recent, title matches, and from YouTube
                            logging.info(f"Found email from YouTube: {subject}")  # Log found message
                            while state['thread_in_use']:
                               time.sleep(1)  # 每秒检查一次线程使用状态
                            state['thread_in_use'] = True
                            logging.info("Third-party notification detected - switching to backup stream...")  # Logging notification
                            switch_stream_config(state)  # Switching stream configuration
                            state['thread_in_use'] = False
                time.sleep(20)
            except Exception as e:  # Handle exceptions
                logging.error(f"Error in find_gmail_title: {e}")  # Log error
                state['thread_in_use'] = False
                time.sleep(5)  # Sleep for 5 seconds

    def handle_youtube_status(state):  # Asynchronous function to handle YouTube status
      while True:
        feedback = is_youtube_livestream_live(state['live_url'])
        if feedback == "ERROR":  # Checking if YouTube livestream status is error
            logging.info("YouTube API verification failed - check credentials and connectivity...")  # Logging error
            time.sleep(15)  # Returning True
        if feedback:  # Checking if YouTube livestream is live
            time.sleep(15)  # Returning True
        else:  # Checking if YouTube livestream is not live
            streams = get_twitch_streams() # Getting Twitch streams and client
            if not streams:  # Checking if streams are empty
                while state['thread_in_use']:
                  time.sleep(1)  # 每秒检查一次线程使用状态
                state['thread_in_use'] = True
                handle_stream_offline(state)
                state['thread_in_use'] = False
        logging.info("Stream connection terminated - initiating reload sequence...")  # Logging termination
        if state['rtmp_server'] == "defrtmp":
            ffmpeg_exe = config.ffmpeg1
        else:
            ffmpeg_exe = config.ffmpeg
        subprocess.run(["taskkill", "/f", "/im", ffmpeg_exe])  # Killing ffmpeg process
        time.sleep(30)  # Waiting for 30 seconds
        logging.info("Checking for stream")  # Logging check
        if is_youtube_livestream_live(state['live_url']):  # Checking if YouTube livestream is live
            logging.info("Stream is back online return to offline check") # Logging return to offline check
            time.sleep(15)  # Returning True
        else:
                logging.info("YouTube Connection Failed Start on backup stream")  # Logging error
                while state['thread_in_use']:
                  time.sleep(1)  # 每秒检查一次线程使用状态
                state['thread_in_use'] = True
                switch_stream_config(state)  # Switching stream configuration
                state['thread_in_use'] = False
                time.sleep(15)  # Returning True

    def hours_checker(state):
      while True:
        time.sleep(40700)
        logging.info("Stream duration limit near 12h reached - initiating scheduled reload...")  # Logging scheduled reload
        while state['thread_in_use']:
            time.sleep(1)  # 每秒检查一次线程使用状态
        state['thread_in_use'] = True
        switch_stream_config(state)  # Switching stream configuration
        state['thread_in_use'] = False

    def twitch_checking(state):
      while True:  # Infinite loop
        try:
              streams = get_twitch_streams()  # Getting Twitch streams and client
              if not streams:  # Checking if streams are empty
                while state['thread_in_use']:
                   time.sleep(1)  # 每秒检查一次线程使用状态
                state['thread_in_use'] = True
                handle_stream_offline(state)
                state['thread_in_use'] = False
              time.sleep(7)  # Sleeping for 10 seconds
        except Exception as e:  # Catching exceptions
            logging.error(f"Error in twitch check: {str(e)}", exc_info=True)  # Logging error
            state['thread_in_use'] = False
            time.sleep(25)  # Sleeping for 25 seconds

    # 定义函数用于处理用户输入
    def handle_user_input(state):
        while True:
            user_input = input("DEBUG MODE IS ENABLE YOU CAN ONLY EXIT OR REFRESH: ").strip().upper()
            if user_input == "EXIT":
                logging.info("EXITING...")
                state['exit_flag'] = True; return  # Exit
            elif user_input == "REFRESH":
                logging.info("REFRESH EXIT AND CREATE NEW CMD")
                subprocess.Popen(["start", "cmd", "/k", "py", "check_tv.py", state['live_url'], state['rtmp_server'], state['spare_link']], shell=True)  # Restarting script with spare link
                state['exit_flag'] = True; return  # Exit


    if config.unliststream and config.public_notification and not REFRESH_TYPE:
      logging.info("stream back to unlisted")
      unlist_thread = threading.Thread(target=unlist_stream, args=(state['live_url'],), daemon=False)
      unlist_thread.start()

    # Set critical threads to non-daemon to prevent abrupt termination
    twitch_checking_thread = threading.Thread(target=twitch_checking, args=(state,), daemon=False)
    twitch_checking_thread.start()

    hours_checker_thread = threading.Thread(target=hours_checker, args=(state,), daemon=False)
    hours_checker_thread.start()

    if state['countyt']:
      handle_youtube_status_thread = threading.Thread(target=handle_youtube_status, args=(state,), daemon=False)
      handle_youtube_status_thread.start()

    find_gmail_title_thread = threading.Thread(target=find_gmail_title, args=(state,), daemon=False)
    find_gmail_title_thread.start()

    refresh_stream_title_thread = threading.Thread(target=refresh_stream_title, args=(state,), daemon=False)
    refresh_stream_title_thread.start()
    
    if config.show_twitch_category:
       check_twitch_category_thread = threading.Thread(target=check_twitch_category, args=(state,), daemon=False)
       check_twitch_category_thread.start()

    if config.exp_tesing:# 启动一个线程来处理用户输入
       input_thread = threading.Thread(target=handle_user_input, args=(state,), daemon=True)
       input_thread.start()

    # Main exit handler loop
    while not state.get('exit_flag', False):
        time.sleep(1)

    logging.info("Stopping the entire script...")

    current_pid = os.getpid()
    process = psutil.Process(current_pid)
    process.terminate()

###########################################offline_check ENDED###########################################

def get_twitch_streams(): # Function to get Twitch streams data by making API requests
  ERROR = 0
  while True:
    try:
        token_response = requests.post(token_url, timeout=10) # Make POST request to get Twitch access token
        token_response.raise_for_status() # Raise exception if request failed
        token_data = token_response.json() # Parse JSON response to get token data
        access_token = token_data.get('access_token') # Extract access token from response
        if not access_token: # Raise error if no token found
            logging.info("Access token not found in response")
            return "ERROR"
    except requests.exceptions.ConnectionError as e:
      logging.error(f"No internet connection or connection error: {e}")
      return "ERROR"
    except requests.exceptions.Timeout as e:
      logging.error(f"Request timed out: {e}")
      return "ERROR"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining Twitch access token: {e}") # Log error if request fails
        return "ERROR"
    except ValueError as ve:
        logging.error(f"Error in response data: {ve}") # Log error if response data is invalid
        return "ERROR"
    headers = {'Authorization': f'Bearer {access_token}', 'Client-ID': config.client_id} # type: ignore Set up request headers with access token and client ID
    streams_response = requests.get(f'https://api.twitch.tv/helix/streams?user_login={config.username}', headers=headers, timeout=10) # Make GET request to Twitch API to get stream data
    streams_data = streams_response.json() # Parse JSON response
    if streams_response.status_code == 401 and streams_data.get('message') == 'Invalid OAuth token':
        logging.error("Invalid OAuth token: Unauthorized access to Twitch API (Normal Error Sometimes)")
        ERROR += 1
        if ERROR == 3:
            logging.info("3 times Invalid OAuth token: NOT SO NORMAL")
            return "ERROR"
    elif 'data' not in streams_data:
        logging.error("'data' key not found in Twitch API response") # Log error if data key missing
        logging.error(f"Invalid Twitch API response: {streams_data}")
        ERROR += 1
        if ERROR == 3:
            logging.info("3 times Unknown Error: NOT NORMAL")
            return "ERROR"
    else:
        return streams_data['data'] # Return stream data if successful

def get_twitch_category():
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    for attempt in range(MAX_RETRIES): # Try up to MAX_RETRIES times
        try:
            streams = get_twitch_streams() # Get stream data
            if isinstance(streams, list) and len(streams) > 0:
            # Extract game_name from the first item
               return streams[0].get('game_name', 'Game name not found')
            else:
               logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {streams}") # Log error on failure
               if attempt < MAX_RETRIES - 1: # Retry if not at max attempts
                time.sleep(RETRY_DELAY)
               else:
                logging.error("Max retries reached, returning fallback title") # Return fallback title if all retries failed
                return f"Unknown"
        except (SyntaxError, ValueError, TypeError) as e:
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}") # Log error on failure
            if attempt < MAX_RETRIES - 1: # Retry if not at max attempts
                time.sleep(RETRY_DELAY)
            else:
                logging.error("Max retries reached, returning fallback title") # Return fallback title if all retries failed
                return f"Unknown"
        except Exception as e:
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}") # Log error on failure
            if attempt < MAX_RETRIES - 1: # Retry if not at max attempts
                time.sleep(RETRY_DELAY)
            else:
                logging.error("Max retries reached, returning fallback title") # Return fallback title if all retries failed
                return f"Unknown"

def get_twitch_stream_title(): # Function to get Twitch stream title with retries
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    for attempt in range(MAX_RETRIES): # Try up to MAX_RETRIES times
        try:
            streams = get_twitch_streams() # Get stream data
            if not streams or streams == "ERROR": # 如果没有找到直播流或者返回错误，延迟后重试
                logging.info(f"No streams found (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
                continue
            if streams: # Return title if streams exist
                return streams[0]['title']
        except Exception as e:
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}") # Log error on failure
            if attempt < MAX_RETRIES - 1: # Retry if not at max attempts
                time.sleep(RETRY_DELAY)
            else:
                logging.error("Max retries reached, returning fallback title") # Return fallback title if all retries failed
                return f"Stream_{datetime.now().strftime('%Y-%m-%d')}"

def check_process_running():  # Function to check if process is running
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
    creds = None  # Initialize credentials to None
    from google_auth_oauthlib.flow import InstalledAppFlow  # Import InstalledAppFlow for OAuth2
    try:
        if os.path.exists(USER_TOKEN_FILE):  # Check if user token file exists
          if not config.brandacc:  # Check if brand account is False
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load credentials from user token file
          if config.brandacc:  # Check if brand account is True
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES_BRAND)  # Load credentials for brand account
        if not creds or not creds.valid:  # Check if credentials are invalid
            if creds and creds.expired and creds.refresh_token:  # Check if credentials are expired and refreshable
                creds.refresh(Request())  # Refresh credentials
            else:
              if not config.brandacc:  # Check if brand account is False
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
              if config.brandacc:  # Check if brand account is True
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow for brand account
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Run local server for authentication
              with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                token.write(creds.to_json())  # type: ignore Write credentials to file
        return build('youtube', 'v3', credentials=creds)  # Return YouTube service
    except Exception as e:  # Handle exceptions
        if "invalid_grant" in str(e):  # Check if exception is invalid grant
              if not config.brandacc:  # Check if brand account is False
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
              if config.brandacc:  # Check if brand account is True
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow for brand account
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Run local server for authentication
              with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                token.write(creds.to_json())  # type: ignore Write credentials to file
              return build('youtube', 'v3', credentials=creds)  # Return YouTube service
        else:
          logging.error(f"Error in get_service: {e}")  # Log error
          exit(1)  # Exit with error

def get_gmail_service():  # Function to get Gmail service
    creds = None  # Initialize credentials to None
    from google_auth_oauthlib.flow import InstalledAppFlow  # Import InstalledAppFlow for OAuth2
    try:
        if config.brandacc:  # Check if brand account is True
          if os.path.exists(GMAIL_TOKEN_FILE):  # Check if Gmail token file exists
            creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES_GMAIL)  # Load credentials from Gmail token file
        if not config.brandacc:  # Check if brand account is False
          if os.path.exists(USER_TOKEN_FILE):  # Check if user token file exists
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load credentials from user token file
        if not creds or not creds.valid:  # Check if credentials are invalid
            if creds and creds.expired and creds.refresh_token:  # Check if credentials are expired and refreshable
                creds.refresh(Request())  # Refresh credentials
            else:
              if config.brandacc:  # Check if brand account is True
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              if not config.brandacc:  # Check if brand account is False
                logging.info("Gmail token not found. Start...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                   token.write(creds.to_json())  # Write credentials to file
        return build('gmail', 'v1', credentials=creds)  # Return Gmail service
    except Exception as e:  # Handle exceptions
        if "invalid_grant" in str(e):  # Check if exception is invalid grant
              if config.brandacc:  # Check if brand account is True
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              if not config.brandacc:  # Check if brand account is False
                logging.info("Gmail token not found. Starting authentication flow...")  # Log info
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth2 flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                   token.write(creds.to_json())  # Write credentials to file
              return build('gmail', 'v1', credentials=creds)  # Return Gmail service
        else:
          logging.error(f"Error in get_gmail_service: {e}")  # Log error
          exit(1)  # Exit with error

def detect_script(
    text
    ):
    for char in text:
        name = unicodedata.name(char, '')
        if 'CJK' in name or 'HIRAGANA' in name or 'KATAKANA' in name or 'IDEOGRAPH' in name:
            return 'CJK'
        elif 'HANGUL' in name:
            return 'Hangul'
        elif 'ARABIC' in name:
            return 'Arabic'
        elif 'DEVANAGARI' in name:
            return 'Devanagari'
    return 'default'

def ensure_font_for_text(
    text
    ):
    script = detect_script(text)
    font_info = FONT_MAP.get(script, FONT_MAP['default'])
    font_path = font_info['file']
    if not os.path.exists(font_path):
        logging.info(f"Downloading font for script: {script}")
        urllib.request.urlretrieve(font_info['url'], font_path)
    return font_path

def create_thumbnail(
    title
    ):
    """Create a thumbnail image for the YouTube stream."""
    try:
        # Create a new image with a dark background
        width, height = 1280, 720
        background_color = (20, 20, 20)  # Dark gray
        image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # Automatically select font for the title's language
        font_path = ensure_font_for_text(title)
        max_title_width = width - 100  # No need to leave space for logo now
        font_size = 60
        try:
            title_font = ImageFont.truetype(font_path, font_size)
        except:
            title_font = ImageFont.load_default()

        # Wrap title into multiple centered lines if too long
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]
                if w <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines

        title_lines = wrap_text(title, title_font, max_title_width)
        # Calculate total height of the title block
        title_block_height = 0
        line_heights = []
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            h = bbox[3] - bbox[1]
            title_block_height += h + 10
            line_heights.append(h)
        title_block_height -= 10  # Remove extra space after last line

        # Archive username font (use same font as title for compatibility)
        try:
            subtitle_font = ImageFont.truetype(font_path, 40)
        except:
            subtitle_font = ImageFont.load_default()
        archive_text = f"VOD of {config.username}"
        archive_bbox = draw.textbbox((0, 0), archive_text, font=subtitle_font)
        archive_h = archive_bbox[3] - archive_bbox[1]

        # If title is too long (more than 3 lines), only show 'VOD of ...'
        show_title = len(title_lines) <= 3
        if show_title:
            block_height = title_block_height + 30 + archive_h
            block_y = (height - block_height) // 2
            # Draw each line of the title, centered
            y = block_y
            for i, line in enumerate(title_lines):
                bbox = draw.textbbox((0, 0), line, font=title_font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x = (width - w) // 2
                draw.text((x, y), line, fill=(255, 255, 255), font=title_font)
                y += h + 10
            # Draw the archive username centered below the title
            archive_w = archive_bbox[2] - archive_bbox[0]
            archive_x = (width - archive_w) // 2
            draw.text((archive_x, y + 20), archive_text, fill=(200, 200, 200), font=subtitle_font)
        else:
            # Only show 'VOD of ...' centered vertically and horizontally
            archive_w = archive_bbox[2] - archive_bbox[0]
            archive_x = (width - archive_w) // 2
            archive_y = (height - archive_h) // 2
            draw.text((archive_x, archive_y), archive_text, fill=(200, 200, 200), font=subtitle_font)

        # Channel logo in the top-left corner
        logo_size = (200, 200)
        try:
            logo = Image.open("channel_logo.png")
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            image.paste(logo, (50, 50), logo if logo.mode == 'RGBA' else None)
        except:
            logging.info("No channel logo found, continuing without it")

        # Date and time at the bottom center
        from datetime import datetime
        date_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}(GMT+8)"
        try:
            date_font = ImageFont.truetype(font_path, 40)
        except:
            date_font = ImageFont.load_default()
        date_bbox = draw.textbbox((0, 0), date_str, font=date_font)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (width - date_w) // 2
        date_y = height - 100
        draw.text((date_x, date_y), date_str, fill=(200, 200, 200), font=date_font)

        # Save the thumbnail
        thumbnail_path = "stream_thumbnail.jpg"
        image.save(thumbnail_path, "JPEG", quality=95)
        return thumbnail_path
    except Exception as e:
        logging.error(f"Error creating thumbnail: {e}")
        return None

def edit_live_stream(
    video_id, 
    new_title, 
    new_description
    ):  # Function to edit live stream
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

       # Create and set thumbnail only if enabled in config
       if config.thumbnail:
           thumbnail_path = create_thumbnail(new_title)
           if thumbnail_path and os.path.exists(thumbnail_path):
               try:
                   service.thumbnails().set(
                       videoId=video_id,
                       media_body=thumbnail_path
                   ).execute()
                   logging.info("Successfully set custom thumbnail")
                   # Delete the thumbnail file after successful upload
                   os.remove(thumbnail_path)
                   logging.info("Thumbnail file removed after upload")
               except Exception as e:
                   logging.error(f"Failed to set thumbnail: {e}")
                   # Try to remove the file even if upload failed
                   if os.path.exists(thumbnail_path):
                       os.remove(thumbnail_path)
       else:
           logging.info("Thumbnail upload disabled in config")

       return response['id']  # Return video ID
       break  # Break loop
    except Exception as e:  # Handle exceptions
     if hitryagain == 3:  # Check if retry limit is reached
      logging.info(f"Error and stoping because of error that can't fix")  # Log error
      if 'quotaExceeded' in str(e):  # Check if quota is exceeded
        logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
        exit()
     hitryagain += 1  # Increment retry counter
     logging.info(f"Error: {e}")  # Log error
     time.sleep(5)  # Sleep for 5 seconds

def get_youtube_stream_title(
    video_id
    ):
    """Get the title of a YouTube live stream from its video ID"""
    try_count = 0
    while True:
        try:
            service = get_service()
            request = service.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['snippet']['title']
            return None
            
        except Exception as e:
          if 'quotaExceeded' in str(e):  # Check if quota is exceeded
            logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
            exit()
          if try_count == 3:  # Check if retry limit is reached
            logging.info(f"Error and stoping because of error that can't fix")  # Log error
            exit()
          try_count += 1  # Increment retry counter
          logging.info(f"Error: {e}")  # Log error
          time.sleep(5)  # Sleep for 5 seconds

def create_live_stream(
    title, 
    description, 
    kmself
    ):  # Function to create live stream
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
                        "enableAutoStop": True if config.livestreamautostop else False,
                        "latencyPrecision": "ultraLow"
                    }
                }
            )
            response = request.execute()  # Execute request
            video_id = response['id']  # Get video ID
            
            if config.playlist or config.playlist == "DOUBLE":  # Check if playlist is enabled
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
          if 'quotaExceeded' in str(e):  # Check if quota is exceeded
            logging.info(f"Error and stoping because of api limited")  # Log quota exceeded
            exit()
          if hitryagain == 3:  # Check if retry limit is reached
           logging.info(f"Error and stoping because of error that can't fix")  # Log error
           exit()
          hitryagain += 1  # Increment retry counter
          logging.info(f"Error: {e}")  # Log error
          time.sleep(5)  # Sleep for 5 seconds

def api_load(
    url, 
    brandacc
    ):  # Function to load API
      from logger_config import check_tv_logger as logging # Importing logging module for logging messages
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
      else:  # Check if brand account is havebrand
          nameofaccount = f"//div[contains(text(),'{config.brandaccname}')]"  # Get brand account name
      button_element = driver.find_element("xpath", nameofaccount)  # Find account button
      button_element.click()  # Click account button
      time.sleep(3)  # Sleep for 3 seconds
      element = driver.find_element("xpath", "//*[@id='submit_approve_access']/div/button/div[3]")  # Find button element
      element.click()  # Click button element
      subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill countdriver.exe
      logging.info("finish idk ---edit_tv---")  # Log info
      time.sleep(10)  # Sleep for 5 seconds
      driver.quit()  # Quit Chrome driver

def check_is_live_api(
    url, 
    ffmpeg, 
    rtmp_server
    ):  # Function to check if stream is live using API
    logging.info("Waiting for 40sec live on YouTube")  # Logging wait message
    time.sleep(40)  # Waiting for 40 seconds
    new_url = f"https://youtube.com/watch?v={url}"  # Constructing new URL
    count_error = 0  # Initializing error counter
    MAX_RETRIES = 3  # Maximum number of retries
    if rtmp_server == "defrtmp":
        text = "this"
    else:
        text = "api_this"  # Setting text based on RTMP server
    while True:  # Infinite loop for retrying
        try:
            streams = streamlink.streams(new_url)  # type: ignore Getting streams from URL
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
            exit()

def api_create_edit_schedule(
    part_number, 
    rtmp_server, 
    is_reload, 
    stream_url, 
    reason=None
    ):  # Asynchronous function to create/edit schedule via API
    filename = None  # Initializing filename
    description = None  # Initializing description
    if config.StreamerName == "Null":
        username = config.username
    else:
        username = config.StreamerName
    TESTING = "[TESTING WILL BE REMOVE AFTER]" if config.exp_tesing else ""
    if not is_reload or is_reload == "EDIT":  # Checking if reload is False or EDIT
        stream_title = get_twitch_stream_title()  # Getting Twitch stream title
        clean_title = ''.join('' if unicodedata.category(c) == 'So' else c for c in (stream_title or "")).replace("<", "").replace(">", "")  # Cleaning title
        part_suffix = f" (PART{part_number})" if part_number > 0 else ""
        filename = f"{username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}"
        if len(filename) > 100:
            max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 2) - len(part_suffix) - len(TESTING)
            clean1_title = clean_title[:max_title_len-3] + "..."
            filename = f"{username} | {clean1_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}"
        if len(filename) > 100:
            filename = f"{username} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}"
        # DON'T REMOVE THIS WATERMARK
        ITISUNLISTED = "[THIS RESTREAMING PROCESS IS DONE UNLISTED]" if config.unliststream else ""
        reason_description = f"""
{reason}""" if reason is not None else ""
        QA = "Q&A(Question The Same In Comment Won't Reply): https://sites.google.com/view/questionthatsomepeopleask" if config.QandA else ""
        Twitch_sub_or_turbo = "[AD-FREE: SUB/TURBO]" if config.brought_twitch_sub_or_turbo else "[ADS INCLUDE WILL AFFECT THE VIEWING EXPERIENCE]"
        ADSqa = "Info about commercial break here: https://sites.google.com/view/qa-for-ads-problems/"  if config.ADSqa else ""
        ADSqaN = "If you want to help out you can make a direct sub to username: karsteniee on Twitch to have no ads on a streamer(if you want to)" if not config.Filian else ""
        stream_category = f"[Stream Category: {get_twitch_category()}]" if config.show_twitch_category else ""
        description = f"""{TESTING}{ITISUNLISTED}{Twitch_sub_or_turbo}
Original broadcast from https://twitch.tv/{config.username} 
{ADSqa}
{ADSqaN}
{QA}{reason_description}
[Stream Title: {clean_title}]{stream_category}
Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee, 
Join My Community Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"""  # Constructing description
    try:
        if is_reload is True:  # Checking if reload is True
            filename = f"{username} (WAITING FOR STREAMER){TESTING}"  # Constructing waiting filename
            description = f"{TESTING}Waiting for https://twitch.tv/{config.username}, Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee, Join My Community Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"  # Constructing waiting description
        if stream_url == "Null":  # Checking if stream URL is Null
            logging.info('Initiating API request for stream creation...')  # Logging API request initiation
            privacy_status = "public" if not config.unliststream else "unlisted"  # Setting privacy status
            if config.unliststream and config.public_notification:
                privacy_status = "public"
            stream_url = create_live_stream(filename, description, privacy_status)  # Creating live stream
            logging.info("==================================================")  # Logging separator
            if config.playlist:  # Checking if playlist is True
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
        if is_reload is True:  # Checking if reload is True
            return stream_url  # Returning stream URL
        if not is_reload:  # Checking if reload is False
            logging.info("Start stream relay")
            initialize_stream_relay(stream_url, rtmp_server, filename)  # Initializing stream relay
            edit_live_stream(stream_url, filename, description)  # Editing live stream
            return filename  # Returning filename
    except Exception as e:  # Handling exceptions
        logging.error(f"Critical error encountered during execution: {e}")  # Logging critical error
        exit()

def setup_stream_settings(
    stream_url, 
    rtmp_server
    ):  # Asynchronous function to set up stream settings
    check_process_running()  # Checking if process is running
    subprocess.Popen(["start", "countdriver.exe"], shell=True)  # Starting countdriver process
    options = Options()  # Creating Chrome options
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  # Setting Chrome user data directory
    options.add_argument(f"user-data-dir={chrome_user_data_dir}")  # Adding user data directory to options
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  # Adding profile directory to options
    driver = None  # Initializing driver
    try_count = 0  # Initializing try count
    while True:  # Infinite loop
       try:
            time.sleep(3)
            driver = webdriver.Chrome(options=options)  # Creating Chrome WebDriver
            url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  # Constructing URL to live stream
            driver.get(url_to_live)  # Navigating to URL
            while True:
                   try:
                       WebDriverWait(driver, 30).until(
                           EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/div/div/ytls-broadcast-metadata/div[2]/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]'))
                       )
                       break
                   except TimeoutException:
                       try:
                           error_element = driver.find_element(By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[3]/ytls-live-dashboard-error-renderer/div/yt-icon')
                           if error_element:
                               logging.info("Error element found - YouTube Studio is in error state")
                               driver.refresh()
                               time.sleep(2)
                               try_count += 1
                               if try_count >= 3:
                                   logging.error("3 consecutive errors detected - KILLING ALL PROCESSES")
                                   os.system("start check_tv.py KILL")
                                   exit(1)
                       except:
                           logging.info("Element not found after 30s, refreshing page...")
                           driver.refresh()
                           time.sleep(2)
                           try_count += 1
                           if try_count >= 3:
                               logging.error("3 consecutive timeouts detected - KILLING ALL PROCESSES")
                               os.system("start check_tv.py KILL")
                               exit(1)
            logging.info("Configuring RTMP key and chat settings...")  # Logging configuration message
            driver.find_element(By.XPATH, "//tp-yt-paper-radio-button[2]").click()
            time.sleep(5)
            driver.find_element(By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']").click()  # Clicking dropdown icon
            time.sleep(3)  # Waiting for 3 seconds
            if rtmp_server == "bkrtmp":  # Checking if RTMP key is "defrtmp"
                element2 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname1 + " (')]]")  # Finding element for "bkrtmp"
                element2.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if rtmp_server == "defrtmp":  # Checking if RTMP key is "bkfrtmp"
                element3 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname + " (')]]")  # Finding element for "defrtmp"
                element3.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if config.disablechat:  # Checking if chat should be disabled
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(By.XPATH, "//li[@id='customization']").click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[1]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Clicking save button
            if not config.disablechat:  # Checking if chat should be replayable
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(By.XPATH, "//li[@id='customization']").click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[2]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Clicking save button
            while True:
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/ytcp-app/ytcp-toast-manager/tp-yt-paper-toast"))
                    )
                    logging.info("Toast notification appeared")
                    break
                except TimeoutException:
                    logging.info("Toast notification not found, continuing to wait...")
            logging.info("RTMP key configuration updated successfully...")  # Logging success message
            driver.quit()  # Quitting the driver
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
            if driver:  # Checking if driver is initialized
                 driver.quit()  # Quitting the driver
            break  # Breaking the loop
       except SessionNotCreatedException as e:
           try_count += 1  # Incrementing try count
           if try_count >= 3:  # Checking if try count exceeds limit
               logging.error(f"Session not created: [{e}] Critical Error KILL ALL")
               os.system("start check_tv.py KILL")
               exit(1)  # Exiting the script
           if "DevToolsActivePort file doesn't exist" in str(e):
               logging.error(f"Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.")
           else:
               logging.error(f"Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN")
           subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Killing CHROME PROCESS
           time.sleep(5)
       except Exception as e:
           try_count += 1  # Incrementing try count
           if try_count >= 3:  # Checking if try count exceeds limit
               logging.error(f"Session not created: [{e}] Critical Error KILL ALL")
               os.system("start check_tv.py KILL")
               exit(1)  # Exiting the script
           logging.error(f"Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN")
           subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Killing CHROME PROCESS
           time.sleep(5)

def initialize_stream_relay(
    stream_url, 
    rtmp_server,
    filename
    ):  # Asynchronous function to initialize stream relay
    if rtmp_server == "defrtmp":
        rtmp_relive = "this"
    else:
        rtmp_relive = "api_this"  # Setting RTMP server for relay
    subprocess.Popen(["start", "python", "relive_tv.py", rtmp_relive], shell=True)  # Starting relive_tv script
    if config.local_archive:
        subprocess.Popen(["start", "python", "relive_tv.py", filename], shell=True)  # Starting relive_tv script
    if rtmp_server == "defrtmp":
        ffmpeg_exe = config.ffmpeg
        ffmpeg_1exe = config.ffmpeg1
    else: 
        ffmpeg_exe = config.ffmpeg1
        ffmpeg_1exe = config.ffmpeg
    check_is_live_api(stream_url, ffmpeg_exe, rtmp_server)  # Checking live API
    subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
    subprocess.run(["taskkill", "/f", "/im", ffmpeg_1exe])  # Killing ffmpeg process
    if rtmp_server == "bkrtmp":
        rtmp_key = config.rtmp_key
    else:
        rtmp_key = config.rtmp_key_1
    if config.playvideo:
        os.system(f'start {ffmpeg_1exe} -re -i blackscreen.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  # Starting ffmpeg for normal stream
    subprocess.Popen(["start", config.apiexe], shell=True)  # Starting API executable

def initialize_and_monitor_stream():  # Asynchronous function to initialize and monitor stream
    if not check_chrome_version():
        logging.info("Error try fixing your chrome version guide on github")
        exit()
    try:
        yt_link = "Null"
        rtmp_info = "Null"
        IFTHEREISMORE = ""  # Setting IFTHEREISMORE to empty string
        THEREISMORE = "Null"  # Setting THEREISMORE to empty string
        bk_rtmp_info = "Null"  # Setting bk_rtmp_info to None
        bk_yt_link = "Null"  # Setting bk_yt_link to None
        arguments = sys.argv  # Getting system arguments
        if len(arguments) < 2:  # Checking if insufficient arguments are provided
                logging.info("==================================================")  # Logging separator
                logging.info("NO ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # Logging no argument available
                logging.info(f"ARCHIVE USER: {config.username}")  # Logging archive user
                logging.info("==================================================")  # Logging separator
        else:
                yt_link = arguments[1]  # Setting YouTube link from arguments
                if yt_link == "KILL":  # Checking if KILL command is given
                    logging.info("close all exe")  # Logging close all executables
                    subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # Killing API executable
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg])  # Killing ffmpeg process
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1])  # Killing ffmpeg1 process
                    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Killing countdriver process
                    exit(1)
                rtmp_info = arguments[2]  # Setting RTMP info from arguments
                if len(arguments) < 3:  # Checking if RTMP argument is missing
                    logging.error("Missing required RTMP argument")  # Logging missing RTMP argument
                    exit(1)  # Exiting with error code
                if len(yt_link) != 11:  # Checking if YouTube link is invalid
                    logging.error(f"Invalid argument for ARG1: {yt_link}. Must be 11 characters long YouTube Video ID")  # Logging invalid YouTube link
                    exit(1)  # Exiting with error code
                if rtmp_info not in ["defrtmp", "bkrtmp"]:  # Checking if RTMP info is invalid
                    logging.error(f"Invalid argument for ARG2: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'")  # Logging invalid RTMP info
                    exit(1)  # Exiting with error code
                # 检查是否有4个输入参数
                if len(arguments) == 4:  # Checking if additional arguments are provided
                    bk_yt_link = arguments[3]  # Setting bk_yt_link from arguments
                    if len(bk_yt_link) != 11:  # Checking if bk_yt_link is invalid
                        logging.error(f"Invalid argument for ARG3: {bk_yt_link}. Must be 11 characters long YouTube Video ID")  # Logging invalid bk_yt_link
                        exit(1)  # Exiting with error code
                    IFTHEREISMORE = f"ARG3: {bk_yt_link}(SKIP CREATING BK STREAM AND RESTORE MONITORING)"
                    THEREISMORE = True
                logging.info("==================================================")  # Logging separator
                logging.info("INPUT ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # Logging input argument available
                logging.info(f"ARG1: {yt_link} ARG2: {rtmp_info} {IFTHEREISMORE}")  # Logging arguments
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
                live_url = api_create_edit_schedule(0, rtmp_server, True, "Null")  # Creating/editing schedule via API
                logging.info(f"Successfully created new stream with URL: {live_url}")  # Logging successful stream creation
            except Exception as e:  # Handling API exceptions
                logging.error(f"Failed to create stream via API: {str(e)}")  # Logging API error
                raise  # Raising exception
        else:
            live_url = yt_link  # Setting live URL to YouTube link
            rtmp_server = rtmp_info  # Setting RTMP server to RTMP info
            logging.info(f"Using provided YouTube link: {live_url} with RTMP server: {rtmp_server}")  # Logging provided YouTube link and RTMP server
        if THEREISMORE == "Null":
          logging.info("Waiting for stream to go live...")  # Logging waiting for stream
          while True:  # Infinite loop
              try:
                  streams = get_twitch_streams()  # Getting Twitch streams and client
                  if streams:  # Checking if streams are available
                      if not streams == "ERROR":
                        stream = streams[0]  # Getting the first stream
                        logging.info(f"Stream is now live! Title From Twitch: {stream['title']}")  # Logging stream is live
                        break  # Breaking the loop
                      else:
                         logging.error(f"Error checking stream status")  # Logging error
                         time.sleep(30)  # Waiting before retrying
                  else:
                      time.sleep(10)  # Waiting before retrying
              except Exception as e:  # Handling exceptions
                  logging.error(f"Error checking stream status: {str(e)}")  # Logging error
                  time.sleep(30)  # Waiting before retrying
          # Start stream monitoring process
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
            elif rtmp_server == "defrtmp":  # Checking if RTMP server is "defrtmp"
                logging.info("Starting with default stream rtmp... and check")  # Logging relay start message
                subprocess.Popen(["start", "python", "relive_tv.py", "this"], shell=True)  # Starting relive_tv script for "defrtmp"
                check_is_live_api(live_url, config.ffmpeg, rtmp_server) # Checking the stream using the streamlink
            if config.local_archive:
                logging.info("Starting local archive process...")
                filename = f"{datetime.now().strftime('%Y-%m-%d')}_{stream['title']}"
                subprocess.Popen(["start", "python", "relive_tv.py", filename], shell=True)
          except Exception as e:  # Handling exceptions
            logging.error(f"Failed to start relay process: {str(e)}")  # Logging error message
            exit(1)  # Exiting with error code
          logging.info("Stream relay process started successfully")  # Logging success message
        else:
            pass
            #m3u8_url = get_m3u8_urls(config.username)
        try:
            if THEREISMORE == "Null":
              REFRESH_TYPE = True
              titlegmail = api_create_edit_schedule(0, rtmp_server, "EDIT", live_url)  # Creating/editing schedule via API
            else:
              REFRESH_TYPE = True
              titlegmail = get_youtube_stream_title(live_url)
            logging.info('edit finished continue the stream')  # Logging edit completion
        except UnboundLocalError:  # Handling UnboundLocalError
            logging.warning("Encountered UnboundLocalError when getting title - continuing with default continue at your own risk")  # Logging warning
        except Exception as e:  # Handling exceptions
            logging.error(f"Error getting stream title: {str(e)} - Error continue at your own risk")  # Logging error message
        try:
            logging.info("Loading backup stream configuration...")  # Logging backup configuration
            if rtmp_server == "bkrtmp":
                rtmp_server = "defrtmp"
            elif rtmp_server == "defrtmp":
                rtmp_server = "bkrtmp"
            if bk_yt_link == "Null" and bk_rtmp_info == "Null":
                live_spare_url = api_create_edit_schedule(0, rtmp_server, True, "Null")  # Creating backup schedule
            else:
                live_spare_url = bk_yt_link  # Setting backup URL to provided URL
            logging.info(f"Backup stream URL configured: {live_spare_url}")  # Logging backup URL
        except Exception as e:  # Catching any exceptions that occur
            logging.error(f"Failed to create backup stream: {str(e)}")  # Logging error message with exception details
        logging.info("Starting offline detection...")  # Logging the start of offline detection
        offline_check_functions(live_url, live_spare_url, rtmp_server, titlegmail, REFRESH_TYPE)  # type: ignore Initiating offline check functions with provided parameters

    except Exception as e:  # Handling exceptions
        logging.error(f"Error in initialize_and_monitor_stream: {str(e)}", exc_info=True)  # Logging error
        logging.error("Critical error encountered - terminating script execution")  # Logging critical error
        exit(1)  # Exiting with error code

def check_chrome_version(target_version=(130, 0, 6723, 70)):
    """Check if installed Chrome version is <= target version (default: 130.0.6723.70)"""
    try:
        # Get Chrome version from registry
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon') as key:
            version_str, _ = winreg.QueryValueEx(key, 'version')
            version = tuple(map(int, version_str.split('.')))
            
        # Compare versions
        if version <= target_version:
            return True
        else:
            logging.info(f"Chrome version {version_str} is > {'.'.join(map(str, target_version))}")
            return False
    
    except FileNotFoundError:
        logging.info("Chrome is not installed or version could not be detected.")
        return False
    except (ValueError, Exception) as e:
        logging.info(f"Error checking Chrome version: {str(e)}")
        return False

def get_m3u8_urls(username):
    def check_1080p_quality(m3u8_url):
        try:
            response = requests.get(m3u8_url, timeout=10)
            response.raise_for_status()
            lines = response.text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith('#EXT-X-STREAM-INF:') and 'RESOLUTION=1920x1080' in line:
                    # Get the next line which contains the 1080p stream URL
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
            return None  # Return None if 1080p stream not found
        except Exception as e:
            logging.info(f"Error checking quality for {m3u8_url}: {str(e)}")
            return None
    # Start BrowserMob Proxy
    from browsermobproxy import Server
    from webdriver_manager.chrome import ChromeDriverManager

    current_dir = os.getcwd()
    server_path = os.path.join(current_dir, "browsermob-proxy-2.1.4", "bin", "browsermob-proxy.bat")
    
    # Check if browsermob-proxy exists
    if not os.path.exists(os.path.join(current_dir, "browsermob-proxy-2.1.4")):
        logging.info("browsermob-proxy not found, downloading...")
        # Download BrowserMob Proxy
        download_url = "https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip"
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Extract the zip file
        with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_ref:
            zip_ref.extractall(current_dir)
        logging.info("BrowserMob Proxy downloaded and extracted successfully")
    
    server = Server(server_path)
    server.start()
    proxy = server.create_proxy()
    logging.info(proxy.proxy)
    # Configure Chrome to use the proxy
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy.proxy}')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')

    # Initialize WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
        # Capture network traffic
    proxy.new_har("m3u8_capture", options={"captureContent": False})
    driver.get(f"https://www.twitch.tv/{username}")
        # 等待页面加载完成，直到找到包含指定用户名的元素
    while True:
        try:
          # 查找包含 "LIVE" 文本的元素
          driver.find_element("xpath", "//div[@class='Layout-sc-1xcs6mc-0 liveIndicator--x8p4l']//span[text()='LIVE']")
          break
        except NoSuchElementException:
            try:
                driver.find_element("xpath", "//a[@tabname='chat' and @data-a-target='channel-home-tab-Chat' and contains(@href, '/" + username + "')]").click()
                while True:  # Infinite loop
                 try:
                   streams = get_twitch_streams()  # Getting Twitch streams and client
                   if streams:  # Checking if streams are available
                    if not streams == "ERROR":
                      stream = streams[0]  # Getting the first stream
                      logging.info(f"Stream is now live! Title From Twitch: {stream['title']}")  # Logging stream is live
                      break  # Breaking the loop
                   else:
                    time.sleep(10)  # Waiting before retrying
                 except Exception as e:  # Handling exceptions
                    logging.error(f"Error checking stream status: {str(e)}")  # Logging error
                    time.sleep(30)  # Waiting before retrying
                driver.refresh()
            except NoSuchElementException:
                time.sleep(3)
        # Extract m3u8 URLs from HAR data
    har_data = proxy.har
    m3u8_urls = []
    m3u8_pattern = re.compile(r'.*\.m3u8(\?.*)?$', re.IGNORECASE)
    for entry in har_data['log']['entries']:
        if 'request' in entry and 'url' in entry['request']:
            url = entry['request']['url']
            if m3u8_pattern.match(url):
                m3u8_urls.append(url)
    
    # Process found m3u8 URLs
    for url in list(set(m3u8_urls)):
        if username in url:
            # Check if the URL contains the username and is a master playlist
            stream_url = check_1080p_quality(url)
            if stream_url:
                logging.info(f"Found 1080p URL: {stream_url}")
                driver.quit()
                server.stop()
                return stream_url
    
    # If no 1080p URL found
    driver.quit()
    server.stop()
    return None

# Function to show agreement screen and get user's acceptance

def show_agreement_screen():
    """
    Shows an agreement screen on first run and saves acceptance status.
    Returns True if agreement was accepted or already accepted before.
    """
    # Check if agreement has already been accepted in config_tv.py
    if hasattr(config, 'agreement_accepted') and config.agreement_accepted:
        return True

    # Create agreement window
    root = tk.Tk()
    root.title("End User License Agreement For Twitch Stream to YouTube")
    root.geometry("600x400")
    # Handle high-DPI displays and scaling
    try:
        # For Windows high-DPI support
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass  # Ignore if not on Windows or if shcore isn't available

    # Set minimum window size with scaling consideration
    root.minsize(width=600, height=450)  # Slightly reduced but still functional minimum
    root.resizable(True, True)
    root.configure(bg="white")

    # Create a main canvas with scrollbar for the entire window content
    main_canvas = tk.Canvas(root, bg="white")
    main_scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)
    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    # Create a frame to contain all content
    content_frame = tk.Frame(main_canvas, bg="white")
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    # Center window on screen with appropriate size for 2.5k display
    root.update_idletasks()
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # Set initial window size to 60% of screen width and 70% of screen height, but not smaller than minimums
    width = max(600, int(screen_width * 0.5))
    height = max(450, int(screen_height * 0.6))
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Bind configure events to update scrollbar
    def update_scrollbar(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    content_frame.bind("<Configure>", update_scrollbar)

    # Agreement title with larger font for high-res screens
    title_label = tk.Label(content_frame, text="End User License Agreement For Twitch Stream to YouTube", font=('Helvetica', 18, 'bold'), bg="white")
    title_label.pack(pady=(30, 20), padx=30, anchor="w")

    # Agreement text with scrollbar
    text_frame = tk.Frame(content_frame, bg="white")
    text_frame.pack(fill=tk.BOTH, expand=True, padx=30)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Font size for readability
    agreement_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=('Helvetica', 11), bg="white")
    agreement_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.config(command=agreement_text.yview)

    # Function to download agreement content from GitHub
    def download_agreement_content():
        agreement_url = 'https://raw.githubusercontent.com/karstenlee10/Twitch_Stream_To_YouTube/refs/heads/main/END%20USER%20LICENSE%20AGREEMENT'
        try:
            response = requests.get(agreement_url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            logging.info(f"Error downloading agreement: {e}")
            exit()

    # Download the agreement content
    agreement_content = download_agreement_content()

    agreement_text.insert(tk.END, agreement_content)
    agreement_text.config(state=tk.DISABLED)  # Make text read-only

    # Button frame with fixed height to ensure visibility
    button_frame = tk.Frame(content_frame, bg="white", height=80)
    button_frame.pack(fill=tk.X, pady=20, padx=30)
    button_frame.pack_propagate(False)  # Prevent frame from shrinking

    # Create a spacer frame to push buttons to the right
    spacer = tk.Frame(button_frame, bg="white")
    spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Accept button
    def accept_agreement():
        # Update config with acceptance status
        config.agreement_accepted = True
        # Save config changes
        try:
            # Read the current config file
            with open('config_tv.py', 'r') as f:
                config_lines = f.readlines()

            # Find and update the agreement_accepted line
            with open('config_tv.py', 'w') as f:
                for line in config_lines:
                    if line.startswith('agreement_accepted ='):
                        f.write('agreement_accepted = True\n')
                    else:
                        f.write(line)

            # Reload config to apply changes
            importlib.reload(config)
        except Exception as e:
            logging.info(f"Error saving agreement status: {e}")
        root.destroy()

    # Decline button
    def decline_agreement():
        messagebox.showerror("Agreement Declined", "You must accept the agreement to use this software.")
        root.destroy()
        exit()

    # Buttons with appropriate size
    accept_button = tk.Button(button_frame, text="I Accept", command=accept_agreement, 
                             bg="#4CAF50", fg="white", font=('Helvetica', 12, 'bold'), padx=20, pady=8, 
                             width=10)
    accept_button.pack(side=tk.RIGHT, padx=5)

    decline_button = tk.Button(button_frame, text="I Decline", command=decline_agreement, 
                              bg="#f44336", fg="white", font=('Helvetica', 12, 'bold'), padx=20, pady=8, 
                              width=10)
    decline_button.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

if __name__ == "__main__":  # Checking if the script is run directly
    # Check agreement before starting the application
    show_agreement_screen()
    initialize_and_monitor_stream()  # Running the function to initialize and monitor stream
    exit()  # Exiting the script
