# GUI IMPORTS
########################################################################
import tkinter as tk # For GUI elements
from tkinter import messagebox # For message boxes
########################################################################
# NORMAL IMPORTS
########################################################################
import os # For file and directory operations
import re # For replacing text
import sys # For checking command line arguments
import time # For delays
import json # For saving state to JSON file
import msvcrt # For non-blocking keyboard input
import requests # For making HTTP requests
import threading # For running multiple threads
import importlib # For reloading modules
import subprocess # For running external commands
import unicodedata # For checking characters
import urllib.request # For downloading font files
from datetime import datetime, timedelta, timezone #getting current time and date
########################################################################
# GOOGLE API IMPORTS
########################################################################
from googleapiclient.discovery import build # For accessing Google APIs
from google.oauth2.credentials import Credentials # For handling OAuth2 credentials
from google.auth.transport.requests import Request # For making authenticated requests
########################################################################
# OTHER IMPORTS
########################################################################
import emoji # For checking and replacing emojis in text
import psutil # For checking running processes
import winreg # For accessing Windows registry, checking chrome version
import zipfile # For extracting zip files 
import streamlink # For checking YouTube livestream status
from io import BytesIO # For display bytes idk
from ctypes import windll # For accessing Windows API functions and checking display dpi
from PIL import Image, ImageDraw, ImageFont # For image processing and drawing text on images
########################################################################
# Selenium IMPORTS
########################################################################
from selenium import webdriver # For controlling web browsers
from selenium.webdriver.common.by import By # For locating elements in the DOM
from selenium.webdriver.chrome.options import Options # For configuring Chrome options
from selenium.webdriver.chrome.service import Service # For managing ChromeDriver service
from selenium.webdriver.support.ui import WebDriverWait # For waiting for elements in the DOM
from selenium.webdriver.support import expected_conditions as EC # For waiting for conditions in the DOM
from selenium.common.exceptions import (NoSuchElementException, SessionNotCreatedException, TimeoutException) # For handling Selenium exceptions
########################################################################
# LOCAL IMPORTS
########################################################################
from logger_config import check_tv_logger as logging # For logging messages
import config_tv as config # For configuration settings
########################################################################

# Twitch API token URL
token_url = f"https://id.twitch.tv/oauth2/token?client_id={config.client_id}&client_secret={config.client_secret}&grant_type=client_credentials" # Construct Twitch OAuth2 token URL with credentials

# Google API token files names
APP_TOKEN_FILE = "client_secret.json"  
GMAIL_TOKEN_FILE = "gmail_token.json"  
USER_TOKEN_FILE = "user_token.json"  

# Google API scopes
# For Brand YouTube account's main account
SCOPES_GMAIL = [  
    'https://www.googleapis.com/auth/gmail.readonly',
  ]
# For Brand YouTube account 
SCOPES_BRAND = [  
    'https://www.googleapis.com/auth/youtube.force-ssl',
  ]
# For Normal YouTube account
SCOPES = [  
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/gmail.readonly',
  ]

# Home directory when running the script
home_dir = os.path.expanduser("~")  

# Font configuration for different languages
FONT_MAP = { # Dictionary mapping script types to font files and download URLs
    'CJK': { # Configuration for Chinese, Japanese, Korean characters
        'file': 'NotoSansCJKjp-Regular.otf', # Local font file name for CJK
        'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf' # Download URL for CJK font
    },
    'Hangul': { # Configuration for Korean Hangul characters
        'file': 'NotoSansCJKkr-Regular.otf', # Local font file name for Hangul
        'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf' # Download URL for Hangul font
    },
    'Arabic': { # Configuration for Arabic script
        'file': 'NotoSansArabic-Regular.ttf', # Local font file name for Arabic
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf' # Download URL for Arabic font
    },
    'Devanagari': { # Configuration for Devanagari script (Hindi, Sanskrit)
        'file': 'NotoSansDevanagari-Regular.ttf', # Local font file name for Devanagari
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf' # Download URL for Devanagari font
    },
    'default': { # Default font configuration for Latin scripts
        'file': 'NotoSans-Regular.ttf', # Local font file name for default font
        'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf' # Download URL for default font
    }
}

stream_state = {
    'stop_right_now': False # Flag to immediately stop streaming
}

def check_is_live():
    trytimes = 0
    while True:
        try:
            streamlink.streams("https://www.twitch.tv/" + config.username)["best"]
            return True
        except KeyError:
            trytimes += 1
            time.sleep(5)
            if trytimes == 6:
                logging.info('The stream is finsh')
                return False

def start_restreaming(state):
    while True:
        if state == "api_this":
            logging.info('script is started now')
            ffmpeg_process = config.ffmpeg1
            rtmp_key = config.rtmp_key_1
        elif state == "this":
            logging.info('script is started now api')
            ffmpeg_process = config.ffmpeg
            rtmp_key = config.rtmp_key
        command = f'''start /wait cmd /c "streamlink https://www.twitch.tv/{config.username} best -o - | {ffmpeg_process} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}"'''
        os.system(command)
        if stream_state['stop_right_now']:
            logging.info('The stream is stopped now')
            break
        if check_is_live():
            logging.info('The stream is still live now')
        else:
            logging.info('The stream is finsh now')
            break

def local_save(title):
    while True:
        counter = 0
        script_dir = os.path.dirname(os.path.abspath(__file__))
        archive_dir = os.path.join(script_dir, "local_archive")
        # 检查 local_archive 文件夹是否存在，不存在则创建
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        filename = os.path.join(archive_dir, f"{title}.mp4")
        while os.path.exists(filename):
            counter += 1
            filename = os.path.join(archive_dir, f"{title}({counter}).mp4")
        command = f"start /wait streamlink https://www.twitch.tv/{config.username} best -o {filename}"
        os.system(command)
        if check_is_live():
            logging.info('The stream is still live now')
            local_save(title)
        else:
            logging.info('The stream is finsh now')
        exit()

# Start when the front code is finished
def offline_check_functions( # Main function to monitor stream status and handle offline detection
    live_url, # YouTube stream URL to monitor
    spare_link, # Backup YouTube stream URL
    rtmp_server, # RTMP server configuration to use
    title # Stream title for Gmail notifications
    ):  
    state = {  # Dictionary to store all stream monitoring state variables
        'numberpart': 0,  # Current number of already part numbers of the stream
        'gmail_checking': True,  # Whether to check Gmail for notifications
        'countyt': True,  #Checking if the youtube stream is still live
        'live_url': live_url,  # Current live stream URL
        'spare_link': spare_link,  # Spare link for backup stream
        'rtmp_server': rtmp_server,  # RTMP server to use for streaming(spare_link)
        'titleforgmail': title,  # Title for Gmail notifications
        "reason": "Null", # Reason for switching streams, initially set to "Null"
        'input_state': False,  # Whether the input state is active
        'thread_in_use': False, # Whether a thread is currently using a important script
        'ending': False, # Whether the stream is ending
        'exit_flag': False # Flag to indicate if the script should exit
    }
    
    logging.info(f"Initializing offline detection monitoring service... With {state['live_url']}, {state['spare_link']}, {state['rtmp_server']}, {state['titleforgmail']}")  # Log initialization with current state parameters

    if not config.livestreamautostop: # If livestream autostop is disabled, we need to check if the YouTube stream is live
        state['countyt'] = False # Disable YouTube stream status checking

    if config.unliststream and config.public_notification: # If using unlisted mode with public notifications
        logging.info("stream back to unlisted") # Log setting stream to unlisted
        def unlist_wrapper(): # Wrapper function for unlisting stream
            result = share_settings_api(state['live_url'], "unlisted") # Try to set stream to unlisted
            if not result: # If API call failed
                print("OMG") # Print error message

        unlist_thread = threading.Thread(target=unlist_wrapper, daemon=False) # Create thread for unlisting
        unlist_thread.start() # Start the unlisting thread

    
    twitch_checking_thread = threading.Thread(target=twitch_checking, args=(state,), daemon=False) # Create Twitch monitoring thread
    twitch_checking_thread.start() # Start Twitch monitoring thread

    hours_checker_thread = threading.Thread(target=hours_checker, args=(state,), daemon=False) # Create 12-hour duration checker thread
    hours_checker_thread.start() # Start duration checker thread

    if state['countyt']: # If YouTube status checking is enabled
        handle_youtube_status_thread = threading.Thread(target=handle_youtube_status, args=(state,), daemon=False) # Create YouTube status monitoring thread
        handle_youtube_status_thread.start() # Start YouTube status monitoring thread

    find_gmail_title_thread = threading.Thread(target=find_gmail_title, args=(state,), daemon=False) # Create Gmail monitoring thread
    find_gmail_title_thread.start() # Start Gmail monitoring thread

    refresh_stream_title_thread = threading.Thread(target=refresh_stream_title, args=(state,), daemon=False) # Create title refresh thread
    refresh_stream_title_thread.start() # Start title refresh thread

    input_thread = threading.Thread(target=handle_user_input, args=(state,), daemon=True) # Create user input handling thread as daemon
    input_thread.start() # Start user input thread

    
    while not state.get('exit_flag', False): # Main loop waiting for exit signal
        time.sleep(1) # Wait 1 second before checking exit flag again

    logging.info("Stopping the entire script...") # Log script termination

    process = psutil.Process(os.getpid()) # Create process object for current process
    process.terminate() # Terminate the current process

def start_browser(stream_url):  # Function to start the browser with specific settings
        check_process_running()  # Check if a chrome process is already running
        subprocess.Popen(["start", "countdriver.exe"], shell=True)  # Start the protect chrome process
        options = Options()  # Configure Chrome options
        chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  # Get path to Chrome user data directory
        options.add_argument(f"user-data-dir={chrome_user_data_dir}")  # Add user data path to Chrome options
        options.add_argument(f"profile-directory={config.Chrome_Profile}")  # Add profile to Chrome options
        driver = None  # Define driver as None
        try_count = 0  # Number of attempts to trying
        while True:  # Infinite loop to retry on errors
            driver = webdriver.Chrome(options=options)  # Create a new Chrome driver instance
            url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  #Get the URL to the YouTube livestream
            driver.get(url_to_live)  # Open the YouTube livestream URL in the browser
            while True: # Wait for page elements to load
                try: # Try to find the main livestream control element
                    # Wait for the livestream control room to load
                    WebDriverWait(driver, 30).until( # Wait up to 30 seconds for element to appear
                        EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/div/div/ytls-broadcast-metadata/div[2]/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')) # XPath for main livestream control button
                    ) # End of until condition
                    return driver # Return the driver instance when element is found
                except TimeoutException: # Handle timeout when element is not found
                    try: # Try to find error element on the page
                        # If the element is not found within 30 seconds, check for an error state
                        error_element = driver.find_element(By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[3]/ytls-live-dashboard-error-renderer/div/yt-icon') # XPath for error state indicator
                        if error_element: # If error element exists
                            logging.info("Error element found - YouTube Studio is in error state") # Log error state detection
                            driver.refresh() # Refresh the page to try again
                            time.sleep(2) # Wait 2 seconds after refresh
                            try_count += 1 # Increment error counter
                            # If there are 3 consecutive errors, stop the process
                            if try_count >= 3: # Check if maximum retries reached
                                logging.error("3 consecutive errors detected - STOP PROCESS") # Log critical error
                                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                                return False # Return failure status
                    except: # Handle case where error element is not found
                        # If the error element is not found, refresh the page
                        logging.info("Element not found after 30s, refreshing page...") # Log timeout situation
                        driver.refresh() # Refresh the page to retry
                        time.sleep(2) # Wait 2 seconds after refresh
                        try_count += 1 # Increment timeout counter
                        # If there are 3 consecutive timeouts, stop the process
                        if try_count >= 3: # Check if maximum retries reached
                            logging.error("3 consecutive timeouts detected - STOP PROCESS") # Log critical timeout error
                            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                            return False # Return failure status

def setup_stream_settings( # Function to configure YouTube Studio livestream settings via browser automation
    stream_url, # YouTube video ID to configure
    rtmp_server # RTMP server type to use for streaming
    ):  
    driver = start_browser(stream_url) # Start Chrome browser with configured options
    if not driver: # If browser failed to start
        return False # Return False to indicate failure
    while True: # Keep trying until successful configuration
        try: # Attempt to configure stream settings
            logging.info("Configuring RTMP key and chat settings...") # Log start of RTMP and chat configuration
            driver.find_element(By.XPATH, "//tp-yt-paper-radio-button[2]").click() # Select stream key option (second radio button)
            time.sleep(5) # Wait for stream key selection to process
            driver.find_element(By.XPATH, "/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/ytls-widget-section/ytls-stream-settings-widget-renderer/div[2]/div[1]/ytls-metadata-collection-renderer/div[2]/div/ytls-metadata-control-renderer[2]/div/ytls-ingestion-dropdown-trigger-renderer/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/span[2]/yt-icon/span/div").click() # Click dropdown to select RTMP server
            time.sleep(3) # Wait for dropdown to open
            if rtmp_server == "bkrtmp": # If using backup RTMP server
                element2 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname1 + " (')]]") # Find backup RTMP server option
                element2.click() # Select backup RTMP server
                time.sleep(7) # Wait for server selection to process
            if rtmp_server == "defrtmp": # If using default RTMP server
                element3 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname + " (')]]") # Find default RTMP server option
                element3.click() # Select default RTMP server
                time.sleep(7) # Wait for server selection to process
            if config.disablechat: # If chat should be disabled
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click() # Click edit button to access settings
                time.sleep(3) # Wait for edit dialog to open
                driver.find_element(By.XPATH, "//li[@id='customization']").click() # Click customization tab
                time.sleep(2) # Wait for tab to load
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[1]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click() # Click checkbox to disable chat
                time.sleep(1) # Wait for checkbox state change
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click() # Save chat disabled setting
            if not config.disablechat: # If chat should be enabled
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click() # Click edit button to access settings
                time.sleep(3) # Wait for edit dialog to open
                driver.find_element(By.XPATH, "//li[@id='customization']").click() # Click customization tab
                time.sleep(2) # Wait for tab to load
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[2]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click() # Click checkbox to enable chat
                time.sleep(1) # Wait for checkbox state change
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click() # Save chat enabled setting  
            while True: # Wait for configuration to save successfully
                try: # Attempt to detect save confirmation
                    WebDriverWait(driver, 30).until( # Wait up to 30 seconds
                        EC.presence_of_element_located((By.XPATH, "/html/body/ytcp-app/ytcp-toast-manager/tp-yt-paper-toast")) # Wait for toast notification
                    )
                    logging.info("Toast notification appeared") # Log successful save confirmation
                    break # Exit wait loop when toast appears
                except TimeoutException: # If toast doesn't appear
                    logging.info("Toast notification not found, continuing to wait...") # Log timeout and continue waiting
            logging.info("RTMP key configuration updated successfully...") # Log successful RTMP configuration
            driver.quit() # Close browser instance
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # Terminate countdriver process
            if driver: # If driver still exists
                driver.quit() # Ensure driver is properly closed
            break # Exit main retry loop on success  
        except SessionNotCreatedException as e: # If Chrome WebDriver session fails to create
            try_count += 1 # Increment retry counter
            if try_count >= 3: # If maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error KILL ALL") # Log critical failure
                os.system("start check_tv.py KILL") # Start kill script
                exit(1) # Exit with error code
            if "DevToolsActivePort file doesn't exist" in str(e): # If specific Chrome startup error
                logging.error(f"Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.") # Log specific error
            else: # For other session creation errors
                logging.error(f"Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log general session error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"]) # Kill all Chrome processes
            time.sleep(5) # Wait before retry
        except Exception as e: # If any other error occurs
            try_count += 1 # Increment retry counter
            if try_count >= 3: # If maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error KILL ALL") # Log critical failure
                os.system("start check_tv.py KILL") # Start kill script
                exit(1) # Exit with error code
            logging.error(f"Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log unexpected error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"]) # Kill all Chrome processes
            time.sleep(5) # Wait before retry

# Using selenium to control the browser to end the YouTube livestream
def ending_stream(stream_url):  # Function to end a YouTube livestream using browser automation
    driver = start_browser(stream_url)  # Start the browser with the livestream URL
    if not driver:  # If driver creation failed
        return False  # Return failure status
    while True:  # Infinite loop to retry on errors
        try:
            logging.info("Stop livestream manually...")  # Log that manual stream stopping is starting
            try: # Try to check if stream is already ended
                header_title = driver.find_element(By.XPATH, '//*[@id="header-title"]') # Find header title element
                if header_title: # If header title element exists (indicates stream already ended)
                    logging.info("Found already ended, breaking loop...") # Log that stream is already ended
                    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                    if driver:  # If driver still exists
                        driver.quit()  # Quit the driver properly
                    return False # Return indicating stream was already ended
            except: # Ignore any exceptions when checking for already ended stream
                pass # Continue with normal ending process
            driver.find_element(By.XPATH, '//*[@id="end-stream-button"]').click()  # Click the end stream button
            time.sleep(3)  # Wait 3 seconds for dialog to appear
            driver.find_element(By.XPATH, '/html/body/ytcp-confirmation-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div[2]/ytcp-button[2]/ytcp-button-shape/button').click()  # Click confirmation button to end stream
            time.sleep(10)  # Wait 10 seconds for stream to end properly
            logging.info("livestream ended successfully...")  # Log successful stream termination
            driver.quit()  # Quit the Chrome driver
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
            if driver:  # If driver still exists after quitting
                driver.quit()  # Quit driver again as safety measure
            break  # Exit the main while loop
        except SessionNotCreatedException as e: # Handle Chrome session creation failures
            try_count += 1  # Increment retry counter
            if try_count >= 3:  # Check if maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error STOP PROCESS") # Log critical error
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                return False # Return failure status
            if "DevToolsActivePort file doesn't exist" in str(e): # Check for specific Chrome startup error
                logging.error(f"Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.") # Log DevTools error
            else: # Handle other session creation errors
                logging.error(f"Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log general session error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Kill all Chrome processes
            time.sleep(5) # Wait 5 seconds before retry
        except Exception as e: # Handle any other unexpected exceptions
            try_count += 1  # Increment retry counter
            if try_count >= 3:  # Check if maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error STOP PROCESS") # Log critical error
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                return False # Return failure status
            logging.error(f"Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log unexpected error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Kill all Chrome processes
            time.sleep(5)     # Wait 5 seconds before retry

def change_share_settings(
    stream_url, 
    share):  # Function to change YouTube stream privacy settings using browser automation
    driver = start_browser(stream_url)  # Start the browser with the livestream URL
    if not driver:  # If driver creation failed
        return False  # Return failure status
    while True:  # Infinite loop to retry on errors
        try: # Try to create driver and change settings
            logging.info("Changing share settings manually...")  # Log start of share settings change
            driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Click edit button to open settings
            time.sleep(3)  # Wait 3 seconds for edit dialog to open
            driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/ytcp-video-metadata-visibility/div/div[2]/ytcp-icon-button/tp-yt-iron-icon").click()  # Click visibility dropdown button
            time.sleep(1)  # Wait 1 second for dropdown to open
            try: # Try to set the requested privacy setting
                if share == "public": # If setting to public
                    driver.find_element(By.XPATH, "//*[@id='privacy-radios']/tp-yt-paper-radio-button[3]").click()  # Click public radio button
                if share == "unlisted": # If setting to unlisted
                    driver.find_element(By.XPATH, "//*[@id='privacy-radios']/tp-yt-paper-radio-button[2]").click()  # Click unlisted radio button
                driver.find_element(By.XPATH, "//*[@id='save-button']/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]").click()  # Click save button for privacy settings
            except Exception as e: # Handle errors when clicking privacy buttons
                logging.info("the share settings is unclickable something is very wrong stop process") # Log privacy button error
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                if driver:  # If driver exists
                    driver.quit()  # Quit driver properly
                return False # Return failure status
            time.sleep(2) # Wait 2 seconds after privacy settings
            driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Click main save button to apply changes
            while True: # Wait for save confirmation
                try: # Try to find toast notification
                    WebDriverWait(driver, 30).until( # Wait up to 30 seconds for toast
                    EC.presence_of_element_located((By.XPATH, "/html/body/ytcp-app/ytcp-toast-manager/tp-yt-paper-toast")) # XPath for toast notification
                    ) # End of until condition
                    logging.info("Toast notification appeared") # Log successful save
                    break # Exit toast waiting loop
                except TimeoutException: # Handle timeout waiting for toast
                    logging.info("Toast notification not found, continuing to wait...") # Log toast timeout
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
            if driver:  # If driver exists
                driver.quit()  # Quit driver properly
            return True  # Return success status
        except SessionNotCreatedException as e: # Handle Chrome session creation failures
            try_count += 1  # Increment retry counter
            if try_count >= 3:  # Check if maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error STOP PROCESS") # Log critical session error
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                return False # Return failure status
            if "DevToolsActivePort file doesn't exist" in str(e): # Check for DevTools startup error
                logging.error(f"Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.") # Log DevTools error
            else: # Handle other session creation errors
                logging.error(f"Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log general session error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Kill all Chrome processes
            time.sleep(5) # Wait 5 seconds before retry
        except Exception as e: # Handle any other unexpected exceptions
            try_count += 1  # Increment retry counter
            if try_count >= 3:  # Check if maximum retries reached
                logging.error(f"Session not created: [{e}] Critical Error STOP PROCESS") # Log critical error
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # Kill Chrome driver process
                return False # Return failure status
            logging.error(f"Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") # Log unexpected error
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  # Kill all Chrome processes
            time.sleep(5) # Wait 5 seconds before retry

def handle_stream_offline(state):  # Function to handle actions when stream goes offline
    state['ending'] = True # Set ending flag to stop monitoring threads
    if state['input_state']: # If currently in input state
        stream_state['stop_right_now'] = True # Set global flag to stop streaming immediately
        if state['rtmp_server'] == "defrtmp": # If using default RTMP server
            subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1])  # Kill backup FFmpeg process
        else: # If using backup RTMP server
            subprocess.run(["taskkill", "/f", "/im", config.ffmpeg])  # Kill default FFmpeg process
    if config.playvideo:  # If ending video playback is enabled
        logging.info("Stream offline status detected - initiating shutdown sequence... and play ending screen")  # Log shutdown sequence start
        
        if state['rtmp_server'] == "defrtmp": # If using default RTMP server
            rtmp_key = config.rtmp_key_1  # Use backup RTMP key
            ffmpeg = config.ffmpeg1      # Use backup FFmpeg executable
        else: # If using backup RTMP server
            rtmp_key = config.rtmp_key  # Use default RTMP key
            ffmpeg = config.ffmpeg     # Use default FFmpeg executable
        os.system(f'{ffmpeg} -re -i ending.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  # Play ending video to stream
    if config.unliststream:  # If stream was unlisted, make it public when ending
        logging.info("Setting stream visibility to public...")  # Log visibility change
        if not share_settings_api(state['live_url'], "public"): # Try to change privacy via API
            logging.info("ERROR using api trying browers") # Log API failure
            change_share_settings(state['live_url'], "public") # Use browser automation as fallbac
    logging.info("ending the stream...")  # Log stream ending process start
    if not config.livestreamautostop: # If auto-stop is disabled
        ending_stream(state['live_url'])  # Manually end the stream
    subprocess.Popen(["start", "cmd", "/k", "py", "check_tv.py", state['spare_link'], state['rtmp_server']], shell=True)  # Start new monitoring process with spare stream
    state['exit_flag'] = True; return  # Set exit flag and return

def switch_stream_config(state):  # Function to switch between primary and backup streams
    reason_number = state['numberpart'] # Get current part number
    reason_number += 1 # Increment for next part number
    if state['reason'] == "Null": # If no specific reason for switching
        reason = f"[Reason of Switching is Unknown(Part{reason_number} is on https://youtube.com/watch?v={state['spare_link']})]" # Create unknown reason message
    else:
        reason = f"[Reason of Switching is {state['reason']}(Part{reason_number} is on https://youtube.com/watch?v={state['spare_link']})]" # Create reason message with specific cause
    update_old_description_thread = threading.Thread(target=api_create_edit_schedule, args=(state['numberpart'], state['rtmp_server'], "EDIT", state['live_url'], reason), daemon=False) # Create thread to update old stream description
    update_old_description_thread.start() # Start the description update thread
    state['numberpart'] += 1  # Increment part number for next stream
    state['titleforgmail'] = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], False, state['spare_link'])  # Create new stream and get title for Gmail
    if state['rtmp_server'] == "bkrtmp": # If currently using backup RTMP
        state['rtmp_server'] = "defrtmp" # Switch to default RTMP
    else:
        state['rtmp_server'] = "bkrtmp" # Switch to backup RTMP
    live_spare_url = api_create_edit_schedule(0, state['rtmp_server'], True, "Null")  # Create new spare stream URL
    if config.unliststream == True:  # If streams should be unlisted initially
        if not share_settings_api(state['live_url'], "public"):
            logging.info("ERROR using api trying browers")
            change_share_settings(state['live_url'], "public")
    if config.unliststream and config.public_notification:
        logging.info("new stream back to unlisted") # Log setting new stream to unlisted
        if not share_settings_api(state['spare_link'], "unlisted"): # Try to set new stream to unlisted via API
            logging.info("ERROR using api trying browers")
            change_share_settings(state['spare_link'], "unlisted") # Use browser automation as fallback for unlisted
    logging.info("ending the old stream...")  # Log old stream termination
    if not config.livestreamautostop:
        ending_stream(state['live_url'])  
    state['live_url'] = state['spare_link']  # Switch spare link to become primary
    state['spare_link'] = live_spare_url  # Set new spare link
    state['reason'] = "Null" # Reset reason for future switches

def share_settings_api(live_id, share):  # Function to change YouTube video privacy settings via API
    hitryagain = 0  # Initialize retry counter
    while True:  
        try:
            service = get_service()  # Get YouTube API service
            request = service.videos().update(  # Create API request to update video
                part='status', # Specify that we're updating the status part
                body={ # Request body with video update data
                    'id': live_id,  # Video ID to update
                    'status': { # Status object containing privacy settings
                    'privacyStatus': share  # New privacy status (public/unlisted/private)
                    } # End status object
                } # End request body
            ) # End API request creation
            response = request.execute()  # Execute the API request
            return response['id']  # Return video ID on success
        except Exception as e:  
            if 'quotaExceeded' in str(e):  # Check for API quota exceeded error
                logging.info(f"API quota exceeded, skipping execution to avoid further errors")  # Log quota exceeded error
                return False
            if hitryagain == 3:  # Check if maximum retries reached
                logging.info(f"Error and stoping because of error that can't fix")  # Log unfixable error
                return False
            hitryagain += 1  # Increment retry counter
            logging.info(f"Error: {e}")  # Log the specific error
            time.sleep(5)  

def is_youtube_livestream_live(video_id):  # Function to check if a YouTube livestream is currently live
    TRY = 0 # Initialize attempt counter
    while True:  
        try:
            streams = streamlink.streams(f"https://youtube.com/watch?v={video_id}")  # Get available streams for the video
            hls_stream = streams["best"]  # Try to get the best quality stream
            return True  
        except KeyError as e:  # Handle case when no streams are available (offline)
            TRY += 1 # Increment attempt counter
            time.sleep(5)
            if TRY == 3: # Check if maximum attempts reached
                logging.info(f"try 3 times is still offline")  # Log that stream is confirmed offline
                return False  # Return False indicating stream is offline
        except Exception as e:  
            logging.error(f"Error checking YouTube livestream status: {e}")  # Log the error details
            return "ERROR"  # Return ERROR status on exception

def refresh_stream_title(state):  # Function to continuously update YouTube stream title to match Twitch
    while not state['ending']:
        try:
            twitch_title = get_twitch_stream_title()  # Get current Twitch stream title
            yt_title = get_youtube_stream_title(state['live_url']) # Get current YouTube stream title
            if not yt_title: # If unable to get YouTube title
                logging.info(f"Error and disabling gmail checking and title checking continue at your own risk")  # Log title retrieval failure
                state['gmail_checking'] = False
                break
            TESTING = "[TESTING WILL BE REMOVE AFTER]" if config.exp_tesing else "" # Add testing suffix if enabled
            newtitle = ''.join(char for char in twitch_title if char not in emoji.EMOJI_DATA).replace("<", "").replace(">", "")  # Remove emojis and problematic characters from title
            newtitle = ' '.join(newtitle.split()) # Normalize whitespace in title
                 
            if newtitle and newtitle[0] == " ": # If title starts with space
                newtitle = newtitle[1:] # Remove leading space
            if config.StreamerName == "Null": # If no custom streamer name set
                username = config.username # Use configured username
            else: # If custom streamer name is set
                username = config.StreamerName # Use custom streamer name
            part_suffix = f" (PART{state['numberpart']})" if state['numberpart'] > 0 else "" # Add part number if > 0
            filename = f"{username} | {newtitle} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}" # Create formatted filename
            if len(filename) > 100:  # If filename exceeds YouTube title limit
                max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 2) - len(part_suffix) - len(TESTING) # Calculate max title length
                clean_title = newtitle[:max_title_len-3] + "..." # Truncate title and add ellipsis
                filename = f"{username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}" # Recreate filename with truncated title
            if yt_title != filename:  # If YouTube title doesn't match expected format
                logging.info(f"Title discrepancy detected: {filename} does not match {yt_title}")  # Log title mismatch
                while state['thread_in_use']: # Wait for other threads to finish
                    time.sleep(1)  # Wait 1 second before checking again
                state['thread_in_use'] = True # Mark thread as in use
                state['titleforgmail'] = api_create_edit_schedule(state['numberpart'], state['rtmp_server'], "EDIT", state['live_url'])  # Update stream title via API
                state['thread_in_use'] = False # Mark thread as no longer in use
                logging.info('edit finished continue the stream')  # Log successful title update
                logging.info(f"Successfully retrieved stream title: {state['titleforgmail']} contiune offline check")  # Log title retrieval success
                    
                yt_title_after_edit = get_youtube_stream_title(state['live_url']) # Get YouTube title after edit
                if yt_title_after_edit != filename: # If title still doesn't match after edit
                    logging.error(f"Title discrepancy still exists after edit: {filename} does not match {yt_title_after_edit}") # Log persistent mismatch
                    logging.info("Stopping immediately due to persistent title discrepancy") # Log decision to stop
                    state['gmail_checking'] = False # Disable Gmail checking
                    break # Exit title refresh loop
                time.sleep(60)  # Wait 60 seconds before next check
            else: # If titles match
                time.sleep(60) # Wait 60 seconds before next check
        except UnboundLocalError:  # Handle UnboundLocalError exception
                logging.warning("Encountered UnboundLocalError when getting title - disabling gmail checking and title checking continue at your own risk")  # Log UnboundLocalError
                state['gmail_checking'] = False # Disable Gmail checking
                break # Exit title refresh loop
        except Exception as e:  # Handle any other exceptions
                logging.error(f"Error getting stream title: {str(e)} - disabling gmail checking and title checking continue at your own risk")  # Log general error
                state['gmail_checking'] = False # Disable Gmail checking due to error
                break # Exit title refresh loop
    logging.info("refresh stream title has stopped")  # Log that refresh stream title has stopped


def find_gmail_title(state):  # Function to monitor Gmail for YouTube notifications
    while state['gmail_checking'] and not state['ending']:  # Loop while Gmail checking enabled and stream not ending
        try: # Try to check Gmail for relevant messages
            title = state['titleforgmail']  # Get current stream title for Gmail search
            service = get_gmail_service()  # Get Gmail API service
            now = datetime.now()  # Get current time
            minutes_ago = now - timedelta(minutes=2)  # Calculate time 2 minutes ago
            results = service.users().messages().list(userId='me', maxResults=2).execute()  # Get latest 2 messages from Gmail
            messages = results.get('messages', [])  # Extract messages from API response
            if messages:  # If messages were found
                for message in messages:  # Loop through each message
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()  # Get full message details
                    received_time = datetime.fromtimestamp(int(msg['internalDate']) / 1000)  # Convert timestamp to datetime
                    subject = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), '')  # Extract email subject
                    sender = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from'), '')  # Extract sender information
                    if received_time >= minutes_ago and title in subject:  # If message is recent and contains stream title
                        logging.info(f"Found email from YouTube: {subject}")  # Log YouTube notification detection
                        while state['thread_in_use']: # Wait for other threads to finish
                            time.sleep(1)  # Wait 1 second before checking again
                        state['thread_in_use'] = True # Mark thread as in use
                        logging.info("Third-party notification detected - switching to backup stream...")  # Log notification detection
                        state['reason'] = "Third-party notification detected" # Set reason for stream switch
                        switch_stream_config(state)  # Switch to backup stream
                        state['thread_in_use'] = False # Mark thread as no longer in use
            time.sleep(40) # Wait 40 seconds before next Gmail check
        except Exception as e:  # Handle Gmail checking exceptions
            logging.error(f"Error in find_gmail_title: {e}")  # Log Gmail error
            state['thread_in_use'] = False # Reset thread usage flag
            time.sleep(60)  # Wait 60 seconds before retry
    logging.info("find gmail title has stopped")  # Log that find gmail title has stopped


def handle_youtube_status(state):  # Function to monitor YouTube stream status
    while not state['ending']: # Loop until stream ending is signaled
        feedback = is_youtube_livestream_live(state['live_url']) # Check if YouTube stream is live
        if feedback == "ERROR":  # If error occurred checking stream status
            logging.info("YouTube API verification failed - check credentials and connectivity...")  # Log API verification failure
            time.sleep(15)  # Wait 15 seconds before retry
        if feedback:  # If stream is live
            time.sleep(15)  # Wait 15 seconds before next check
        else:  # If stream is not live
            streams = get_twitch_streams() # Check Twitch stream status
            if not streams:  # If Twitch stream is also offline
                while state['thread_in_use']: # Wait for other threads to finish
                    time.sleep(1)  # Wait 1 second before checking thread status again
                state['thread_in_use'] = True # Mark thread as in use
                handle_stream_offline(state) # Handle stream offline situation
                state['thread_in_use'] = False # Mark thread as no longer in use
        logging.info("Stream connection terminated - initiating reload sequence...")  # Log stream reconnection attempt
        if state['rtmp_server'] == "defrtmp": # If using default RTMP server
            ffmpeg_exe = config.ffmpeg1 # Use backup FFmpeg executable
        else: # If using backup RTMP server
            ffmpeg_exe = config.ffmpeg # Use default FFmpeg executable
        stream_state["stop_right_now"] = True # Signal FFmpeg to stop immediately
        subprocess.run(["taskkill", "/f", "/im", ffmpeg_exe])  # Kill current FFmpeg process
        time.sleep(30)  # Wait 30 seconds for cleanup
        logging.info("Checking for stream")  # Log stream check attempt
        if is_youtube_livestream_live(state['live_url']):  # Check if YouTube stream is back online
            logging.info("Stream is back online return to offline check") # Log successful reconnection
            time.sleep(15)  # Wait 15 seconds before continuing
        else: # If YouTube stream is still offline
            logging.info("YouTube Connection Failed Start on backup stream")  # Log connection failure
            while state['thread_in_use']: # Wait for other threads to finish
                time.sleep(1)  # Wait 1 second before checking again
            state['thread_in_use'] = True # Mark thread as in use
            state['reason'] = "YouTube Connection Failed" # Set reason for stream switch
            switch_stream_config(state)  # Switch to backup stream
            state['thread_in_use'] = False # Mark thread as no longer in use
            time.sleep(15)  # Wait 15 seconds after switch
    logging.info("handle youtube status has stopped")  # Log that handle youtube status has stopped


def hours_checker(state): # Function to handle 12-hour stream duration limit
    while not state['ending']: # Loop until stream ending is signaled
        time.sleep(44120) # Wait approximately 11 hours and 18 minutes
        logging.info("Stream duration limit near 12h reached - initiating scheduled reload...")  # Log duration limit reached
        while state['thread_in_use']: # Wait for other threads to finish
            time.sleep(1)  # Wait 1 second before checking thread status again
        state['thread_in_use'] = True # Mark thread as in use
        state['reason'] = "stream duration limit near 12h reached" # Set reason for stream switch
        switch_stream_config(state)  # Switch to backup stream
        state['thread_in_use'] = False # Mark thread as no longer in use
    logging.info("hours checker has stopped")  # Log that hours checker has stopped


def twitch_checking(state): # Function to continuously monitor Twitch stream status
    while not state['ending']:  # Loop until stream ending is signaled
        try: # Try to check Twitch stream status
            streams = get_twitch_streams()  # Get current Twitch stream information
            if not streams:  # If no Twitch streams found (offline)
                while state['thread_in_use']: # Wait for other threads to finish
                    time.sleep(1)  # Wait 1 second before checking again
                state['thread_in_use'] = True # Mark thread as in use
                handle_stream_offline(state) # Handle stream offline situation
                state['thread_in_use'] = False # Mark thread as no longer in use
            time.sleep(7)  # Wait 7 seconds before next Twitch check
        except Exception as e:  # Handle Twitch checking exceptions
            logging.error(f"Error in twitch check: {str(e)}", exc_info=True)  # Log Twitch check error with traceback
            state['thread_in_use'] = False # Reset thread usage flag
            time.sleep(25)  # Wait 25 seconds before retry
    logging.info("twitch checker has stopped")  # Log that twitch checker has stopped


    
def handle_user_input(state): # Function to handle user debug commands
    print("DEBUG MODE IS ENABLE YOU CAN ONLY EXIT OR REFRESH: ")
    print("> ", end='', flush=True)
    
    user_input = ""
    
    while not state['ending']:
        if state['ending']:
            print("\nStatus changed - stopping debug mode")
            break
            
        # Check for keypress (non-blocking)
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char == '\r':  # Enter pressed
                print()
                if user_input.strip().upper() == "EXIT":
                    logging.info("Terminating script...")
                    state['exit_flag'] = True; return  # Set exit flag and return

                elif user_input == "REFRESH":
                    logging.info("REFRESH EXIT AND CREATE NEW CMD") # Log refresh command
                    if state['rtmp_server'] == "defrtmp": # If currently using default RTMP
                        rtmp = "bkrtmp" # Switch to backup RTMP for new process
                    else: # If currently using backup RTMP
                        rtmp = "defrtmp" # Switch to default RTMP for new process
                    subprocess.Popen(["start", "cmd", "/k", "py", "check_tv.py", state['live_url'], rtmp, state['spare_link']], shell=True)  # Start new monitoring process with different RTMP
                    state['exit_flag'] = True; return  # Set exit flag and return
                                
                # Handle STOP command - exit input handling
                elif user_input == "STOP":
                    break
                else:
                    user_input = ""
                    print("> ", end='', flush=True)
            elif char == '\b':  # Backspace
                if user_input:
                    user_input = user_input[:-1]
                    print('\b \b', end='', flush=True)
            else:
                user_input += char
                print(char, end='', flush=True)
        
        time.sleep(0.1)
    
    # Clear any remaining input buffer
    while msvcrt.kbhit():
        msvcrt.getwch()
            
    logging.info("handle user input has stopped")

# Function to handle user input commands during debug mode
def handle_input(status, live_url, rtmp_server):
    print("DEBUG MODE [Valid commands: EXIT, REFRESH, STOP]:")
    print("> ", end='', flush=True)
    
    user_input = ""
    
    while not status['status']:
        if status['status']:
            print("\nStatus changed - stopping debug mode")
            break
            
        # Check for keypress (non-blocking)
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char == '\r':  # Enter pressed
                print()
                if user_input.strip().upper() == "EXIT":
                    logging.info("Terminating script...")
                    process = psutil.Process(os.getpid())
                    process.terminate()

                elif user_input == "REFRESH":
                    logging.info("Starting new process...")
                    cmd = ["start", "cmd", "/k", "py", "check_tv.py", live_url, rtmp_server]
                    subprocess.Popen(cmd, shell=True)
                    logging.info("Terminating current process...")
                    process = psutil.Process(os.getpid())
                    process.terminate()
                                
                # Handle STOP command - exit input handling
                elif user_input == "STOP":
                    break
                else:
                    user_input = ""
                    print("> ", end='', flush=True)
            elif char == '\b':  # Backspace
                if user_input:
                    user_input = user_input[:-1]
                    print('\b \b', end='', flush=True)
            else:
                user_input += char
                print(char, end='', flush=True)
        
        time.sleep(0.1)
    
    # Clear any remaining input buffer
    while msvcrt.kbhit():
        msvcrt.getwch()
            
    logging.info("handle user input has stopped")

def get_twitch_streams():  # Function to get Twitch stream information via API
    ERROR = 0 # Initialize error counter
    while True: # Infinite loop to retry on errors
        try: # Try to get Twitch OAuth token
            token_response = requests.post(token_url, timeout=10)  # Request OAuth token from Twitch
            token_response.raise_for_status()  # Raise exception if HTTP error
            token_data = token_response.json()  # Parse JSON response
            access_token = token_data.get('access_token')  # Extract access token
            if not access_token:  # If no access token in response
                logging.info("Access token not found in response") # Log missing token error
                return "ERROR" # Return error status
        except requests.exceptions.ConnectionError as e: # Handle network connection errors
            logging.error(f"No internet connection or connection error: {e}") # Log connection error
            return "ERROR" # Return error status
        except requests.exceptions.Timeout as e: # Handle request timeout errors
            logging.error(f"Request timed out: {e}") # Log timeout error
            return "ERROR" # Return error status
        except requests.exceptions.RequestException as e: # Handle other request errors
            logging.error(f"Error obtaining Twitch access token: {e}")  # Log request error
            return "ERROR" # Return error status
        except ValueError as ve: # Handle JSON parsing errors
            logging.error(f"Error in response data: {ve}")  # Log JSON error
            return "ERROR" # Return error status
        headers = {'Authorization': f'Bearer {access_token}', 'Client-ID': config.client_id}  # Create headers for stream API request
        streams_response = requests.get(f'https://api.twitch.tv/helix/streams?user_login={config.username}', headers=headers, timeout=10)  # Request stream data from Twitch API
        streams_data = streams_response.json()  # Parse JSON response from streams API
        if streams_response.status_code == 401 and streams_data.get('message') == 'Invalid OAuth token': # Check for invalid token error
            logging.error("Invalid OAuth token: Unauthorized access to Twitch API (Normal Error Sometimes)") # Log OAuth error
            ERROR += 1 # Increment error counter
            if ERROR == 3: # Check if maximum errors reached
                logging.info("3 times Invalid OAuth token: NOT SO NORMAL") # Log repeated OAuth failures
                return "ERROR" # Return error status
        elif 'data' not in streams_data: # Check if response has expected data structure
            logging.error("'data' key not found in Twitch API response")  # Log missing data key
            logging.error(f"Invalid Twitch API response: {streams_data}") # Log invalid response structure
            ERROR += 1 # Increment error counter
            if ERROR == 3: # Check if maximum errors reached
                logging.info("3 times Unknown Error: NOT NORMAL") # Log repeated unknown errors
                return "ERROR" # Return error status
        else: # If response is valid
            return streams_data['data']  # Return stream data array

def get_twitch_stream_title():  # Function to get the title of the current Twitch stream
    MAX_RETRIES = 3 # Maximum number of retry attempts
    RETRY_DELAY = 5 # Delay between retries in seconds
    for attempt in range(MAX_RETRIES):  # Loop through retry attempts
        try: # Try to get stream title
            streams = get_twitch_streams()  # Get stream data from Twitch API
            if not streams or streams == "ERROR":  # If no streams or error occurred
                logging.info(f"No streams found (attempt {attempt + 1}/{MAX_RETRIES})") # Log attempt number for no streams found
                time.sleep(RETRY_DELAY) # Wait before retrying
                continue # Skip to next attempt
            if streams:  # If streams were found
                return streams[0]['title'] # Return title of first stream
        except Exception as e: # Handle exceptions during stream retrieval
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}")  # Log error with attempt number
            if attempt < MAX_RETRIES - 1:  # If not the last attempt
                time.sleep(RETRY_DELAY) # Wait before retrying
            else: # If this is the last attempt
                logging.error("Max retries reached, returning fallback title")  # Log fallback title usage
                return f"Stream_{datetime.now().strftime('%Y-%m-%d')}" # Return fallback title with current date

def check_process_running():  # Function to check if Chrome driver process is already running
    process_name = "countdriver.exe"  # Name of the Chrome driver process to check
    logging.info("Checking for existing browser automation processes...")  # Log process check start
    for process in psutil.process_iter(['pid', 'name']):  # Iterate through all running processes
        if process.info['name'] == process_name:  # If Chrome driver process is found
            logging.info("Browser automation process already running - waiting for completion...")  # Log process conflict
            time.sleep(15)  # Wait 15 seconds for process to complete
            check_process_running()  # Recursively check again
    logging.info("No conflicting processes found - proceeding...")  # Log clear to proceed
    return  # Return from function

def get_service():  # Function to get authenticated YouTube API service
    creds = None  # Initialize credentials variable
    from google_auth_oauthlib.flow import InstalledAppFlow  # Import OAuth flow for Google authentication
    try: # Try to authenticate with Google APIs
        if os.path.exists(USER_TOKEN_FILE):  # If user token file exists
            if not config.brandacc:  # If not using brand account
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load regular account credentials
            if config.brandacc:  # If using brand account
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES_BRAND)  # Load brand account credentials
        if not creds or not creds.valid:  # If no valid credentials
            if creds and creds.expired and creds.refresh_token:  # If credentials expired but have refresh token
                creds.refresh(Request())  # Refresh the credentials
            else: # If no valid credentials, need to authenticate
                if not config.brandacc:  # If not using brand account
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth flow for regular account
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                if config.brandacc:  # If using brand account
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth flow for brand account
                    creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Run local server for brand authentication
                with open(USER_TOKEN_FILE, 'w') as token:  # Open token file for writing
                    token.write(creds.to_json())  # Save credentials to file
        return build('youtube', 'v3', credentials=creds)  # Return authenticated YouTube API service
    except Exception as e:  # Handle authentication exceptions
        if "invalid_grant" in str(e):  # If invalid grant error (expired refresh token)
            if not config.brandacc:  # If not using brand account
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create new OAuth flow
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Re-authenticate for regular account
            if config.brandacc:  # If using brand account
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create new OAuth flow for brand
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  # Re-authenticate for brand account
            with open(USER_TOKEN_FILE, 'w') as token:  # Open token file for writing
                token.write(creds.to_json())  # Save new credentials
            return build('youtube', 'v3', credentials=creds)  # Return authenticated service with new credentials
        else: # Handle other authentication errors
            logging.error(f"Error in get_service: {e}")  # Log authentication error
            exit(1)  # Exit program on authentication failure

def get_gmail_service():  # Function to authenticate and create Gmail API service
    creds = None  # Initialize credentials variable
    from google_auth_oauthlib.flow import InstalledAppFlow # Import OAuth flow for Google authentication
    try: # Try to authenticate with Gmail API
        if config.brandacc:  # If using brand account
            if os.path.exists(GMAIL_TOKEN_FILE):  # Check if Gmail token file exists
                creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES_GMAIL)  # Load Gmail credentials for brand account
        if not config.brandacc:  # If using regular account
            if os.path.exists(USER_TOKEN_FILE):  # Check if user token file exists
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  # Load credentials for regular account
        if not creds or not creds.valid:  # If no valid credentials exist
            if creds and creds.expired and creds.refresh_token:  # If credentials expired but have refresh token
                creds.refresh(Request())  # Refresh the credentials
            else: # If no credentials or can't refresh
                if config.brandacc:  # If using brand account
                    logging.info("Gmail token not found. Starting authentication flow...")  # Log start of brand account auth
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth flow for Gmail brand account
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                    with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                        token.write(creds.to_json())  # Save Gmail credentials to file
                if not config.brandacc:  # If using regular account
                    logging.info("Gmail token not found. Start...")  # Log start of regular account auth
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create OAuth flow for regular account
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  # Run local server for authentication
                    with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                        token.write(creds.to_json())  # Save user credentials to file
        return build('gmail', 'v1', credentials=creds)  # Return authenticated Gmail API service
    except Exception as e:  # Handle authentication exceptions
        if "invalid_grant" in str(e):  # If invalid grant error (expired refresh token)
            if config.brandacc:  # If using brand account
                logging.info("Gmail token not found. Starting authentication flow...")  # Log restart of brand account auth
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create new OAuth flow for Gmail brand account
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Re-run authentication server
                with open(GMAIL_TOKEN_FILE, 'w') as token:  # Open Gmail token file for writing
                    token.write(creds.to_json())  # Save new Gmail credentials
            if not config.brandacc:  # If using regular account
                logging.info("Gmail token not found. Starting authentication flow...")  # Log restart of regular account auth
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  # Create new OAuth flow for regular account
                creds = flow.run_local_server(port=6971, brandacc="Nope")  # Re-run authentication server
                with open(USER_TOKEN_FILE, 'w') as token:  # Open user token file for writing
                    token.write(creds.to_json())  # Save new user credentials
            return build('gmail', 'v1', credentials=creds)  # Return authenticated service with new credentials
        else: # Handle other authentication errors
            logging.error(f"Error in get_gmail_service: {e}")  # Log authentication error
            exit(1)  # Exit program on authentication failure

def detect_script( # Function to detect the writing script/language of text
    text # Input text to analyze
    ): # Function definition end
    for char in text: # Loop through each character in the text
        name = unicodedata.name(char, '') # Get Unicode name of the character
        if 'CJK' in name or 'HIRAGANA' in name or 'KATAKANA' in name or 'IDEOGRAPH' in name: # Check for Chinese/Japanese/Korean characters
            return 'CJK' # Return CJK script type
        elif 'HANGUL' in name: # Check for Korean Hangul characters
            return 'Hangul' # Return Hangul script type
        elif 'ARABIC' in name: # Check for Arabic characters
            return 'Arabic' # Return Arabic script type
        elif 'DEVANAGARI' in name: # Check for Devanagari characters (Hindi/Sanskrit)
            return 'Devanagari' # Return Devanagari script type
    return 'default' # Return default script type if no special characters found

def ensure_font_for_text( # Function to ensure appropriate font is available for text
    text # Input text to get font for
    ): # Function definition end
    script = detect_script(text) # Detect the script type of the text
    font_info = FONT_MAP.get(script, FONT_MAP['default']) # Get font information for detected script
    font_path = font_info['file'] # Get local font file path
    if not os.path.exists(font_path): # If font file doesn't exist locally
        logging.info(f"Downloading font for script: {script}") # Log font download
        urllib.request.urlretrieve(font_info['url'], font_path) # Download font from URL
    return font_path # Return path to font file

def create_thumbnail( # Function to create custom thumbnail image for YouTube stream
    title # Stream title to display on thumbnail
    ): # Function definition end
    """Create a thumbnail image for the YouTube stream."""
    try: # Try to create thumbnail image
        
        width, height = 1280, 720 # Set thumbnail dimensions (YouTube standard)
        background_color = (20, 20, 20)  # Set dark background color (RGB)
        image = Image.new('RGB', (width, height), background_color) # Create new image with dark background
        draw = ImageDraw.Draw(image) # Create drawing context for the image

        
        font_path = ensure_font_for_text(title) # Get appropriate font for the title text
        max_title_width = width - 100  # Calculate maximum width for title text
        font_size = 60 # Set font size for title
        try: # Try to load TrueType font
            title_font = ImageFont.truetype(font_path, font_size) # Load font with specified size
        except: # If font loading fails
            title_font = ImageFont.load_default() # Use default system font

        
        def wrap_text(text, font, max_width): # Inner function to wrap text to multiple lines
            words = text.split() # Split text into words
            lines = [] # Initialize lines array
            current_line = ''
            for word in words: # Process each word in the text
                test_line = current_line + (' ' if current_line else '') + word # Add word to current line with space if needed
                bbox = draw.textbbox((0, 0), test_line, font=font) # Calculate text bounding box
                w = bbox[2] - bbox[0] # Get width of the test line
                if w <= max_width: # If text fits within maximum width
                    current_line = test_line # Keep the word on current line
                else: # If text would exceed maximum width
                    if current_line: # If there's text on current line
                        lines.append(current_line) # Save current line to array
                    current_line = word # Start new line with current word
            if current_line: # If there's remaining text after loop
                lines.append(current_line) # Add final line to array
            return lines # Return array of wrapped text lines

        title_lines = wrap_text(title, title_font, max_title_width) # Wrap title text to multiple lines if needed
        
        title_block_height = 0 # Initialize total height of title block
        line_heights = [] # Store height of each line for positioning
        for line in title_lines: # Calculate height for each wrapped line
            bbox = draw.textbbox((0, 0), line, font=title_font) # Get bounding box for line
            h = bbox[3] - bbox[1] # Calculate line height
            title_block_height += h + 10 # Add line height plus spacing
            line_heights.append(h) # Store individual line height
        title_block_height -= 10 # Remove extra spacing from last line  

        
        try: # Attempt to load subtitle font
            subtitle_font = ImageFont.truetype(font_path, 40) # Load font at 40px for subtitle
        except: # If subtitle font loading fails
            subtitle_font = ImageFont.load_default() # Use default system font
        archive_text = f"VOD of {config.username}" # Create archive subtitle text
        archive_bbox = draw.textbbox((0, 0), archive_text, font=subtitle_font) # Calculate subtitle text dimensions
        archive_h = archive_bbox[3] - archive_bbox[1] # Get height of subtitle text

        
        show_title = len(title_lines) <= 3 # Only show title if 3 lines or fewer
        if show_title: # If title should be displayed
            block_height = title_block_height + 30 + archive_h # Calculate total block height with spacing
            block_y = (height - block_height) // 2 # Center the text block vertically
            
            y = block_y # Start drawing from top of centered block
            for i, line in enumerate(title_lines): # Draw each line of the title
                bbox = draw.textbbox((0, 0), line, font=title_font) # Get dimensions of current line
                w = bbox[2] - bbox[0] # Calculate line width
                h = bbox[3] - bbox[1] # Calculate line height
                x = (width - w) // 2 # Center line horizontally
                draw.text((x, y), line, fill=(255, 255, 255), font=title_font) # Draw title line in white
                y += h + 10 # Move to next line position with spacing
            
            archive_w = archive_bbox[2] - archive_bbox[0] # Get width of archive text
            archive_x = (width - archive_w) // 2 # Center archive text horizontally
            draw.text((archive_x, y + 20), archive_text, fill=(200, 200, 200), font=subtitle_font) # Draw archive text below title
        else: # If title is too long to display
            
            archive_w = archive_bbox[2] - archive_bbox[0] # Get width of archive text
            archive_x = (width - archive_w) // 2 # Center archive text horizontally
            archive_y = (height - archive_h) // 2 # Center archive text vertically
            draw.text((archive_x, archive_y), archive_text, fill=(200, 200, 200), font=subtitle_font) # Draw only archive text centered

        
        logo_size = (200, 200) # Set standard logo dimensions
        try: # Attempt to add channel logo to thumbnail
            logo = Image.open("channel_logo.png") # Load channel logo image
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS) # Resize logo to standard size with high quality
            image.paste(logo, (50, 50), logo if logo.mode == 'RGBA' else None) # Paste logo in top-left corner with transparency
        except: # If logo file not found or fails to load
            logging.info("No channel logo found, continuing without it") # Log info and continue without logo

        
        from datetime import datetime # Import datetime for timestamp
        date_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}(GMT+8)" # Format current date and time with timezone
        try: # Attempt to load date font
            date_font = ImageFont.truetype(font_path, 40) # Load font at 40px for date
        except: # If date font loading fails
            date_font = ImageFont.load_default() # Use default system font
        date_bbox = draw.textbbox((0, 0), date_str, font=date_font) # Calculate date text dimensions
        date_w = date_bbox[2] - date_bbox[0] # Get width of date text
        date_x = (width - date_w) // 2 # Center date text horizontally
        date_y = height - 100 # Position date near bottom of image
        draw.text((date_x, date_y), date_str, fill=(200, 200, 200), font=date_font) # Draw timestamp in light gray

        
        thumbnail_path = "stream_thumbnail.jpg" # Define output filename for thumbnail
        image.save(thumbnail_path, "JPEG", quality=95) # Save image as high-quality JPEG
        return thumbnail_path # Return path to created thumbnail
    except Exception as e: # If any error occurs during thumbnail creation
        logging.error(f"Error creating thumbnail: {e}") # Log the error details
        return None # Return None to indicate failure

def edit_live_stream( # Function to update YouTube livestream title and description
    video_id, # YouTube video ID to update
    new_title, # New title for the stream
    new_description # New description for the stream
    ):  
    hitryagain = 0 # Initialize retry counter
    while True: # Keep trying until success or max retries
        try: # Attempt to update the livestream
            service = get_service() # Get authenticated YouTube API service
            category_id = '24' # Set category to Gaming
            request = service.videos().update( # Create video update request
                part="snippet", # Update only the snippet part
                body={ # Request body with video data
                "id": video_id, # Video ID to update
                "snippet": { # Video metadata
                    "title": new_title, # Set new title
                    "description": new_description, # Set new description
                    "categoryId": category_id # Set gaming category
                    }
               }
            )
            response = request.execute() # Execute the API request  

            
            if config.thumbnail: # If thumbnail generation is enabled in config
                thumbnail_path = create_thumbnail(new_title) # Create custom thumbnail with stream title
                if thumbnail_path and os.path.exists(thumbnail_path): # If thumbnail was created successfully
                    try: # Attempt to upload thumbnail to YouTube
                        service.thumbnails().set( # Set custom thumbnail via API
                           videoId=video_id, # Video to update
                           media_body=thumbnail_path # Path to thumbnail file
                        ).execute() # Execute thumbnail upload request
                        logging.info("Successfully set custom thumbnail") # Log successful upload
                        
                        os.remove(thumbnail_path) # Delete local thumbnail file after upload
                        logging.info("Thumbnail file removed after upload") # Log file cleanup
                    except Exception as e: # If thumbnail upload fails
                        logging.error(f"Failed to set thumbnail: {e}") # Log thumbnail error
                        
                        if os.path.exists(thumbnail_path): # If thumbnail file still exists
                            os.remove(thumbnail_path) # Clean up failed thumbnail file
            else: # If thumbnail generation is disabled
                pass
            return response['id'] # Return updated video ID on success
        except Exception as e: # If API request fails
            if hitryagain == 3: # If maximum retry attempts reached
                logging.info(f"Error and stoping because of error that can't fix") # Log final failure
            if 'quotaExceeded' in str(e): # If YouTube API quota is exceeded
                logging.info(f"Error and stoping because of api limited") # Log quota exhaustion
                exit() # Exit program due to quota limit
            hitryagain += 1 # Increment retry counter
            logging.info(f"Error: {e}") # Log the error details
            time.sleep(5) # Wait 5 seconds before retrying  

def get_youtube_stream_title(
    video_id
    ):
    """Get the title of a YouTube live stream from its video ID"""
    try_count = 0 # Initialize retry counter
    while True: # Keep trying until success or max retries
        try: # Attempt to get stream title
            service = get_service() # Get authenticated YouTube API service
            request = service.videos().list( # Create request to get video details
                part="snippet", # Request only snippet data
                id=video_id # Specify video ID to query
            )
            response = request.execute() # Execute the API request
            
            if response['items']: # If video was found
                return response['items'][0]['snippet']['title'] # Return the video title
            return "ERROR GETTING TITLE SORRY" # Return error message if no video found
            
        except Exception as e: # If API request fails
            if 'quotaExceeded' in str(e): # If YouTube API quota exceeded
                logging.info(f"Error and stoping because of api limited") # Log quota limit error
                return False # Return False to indicate failure
            if try_count == 3: # If maximum retry attempts reached
                logging.info(f"Error and stoping because of error that can't fix") # Log final failure
                return False # Return False to indicate failure
            try_count += 1 # Increment retry counter
            logging.info(f"Error: {e}") # Log the error details
            time.sleep(5) # Wait 5 seconds before retrying  

def create_live_stream( # Function to create a new YouTube livestream
    title, # Title for the new livestream
    description, # Description for the new livestream
    kmself # Privacy status (public/private/unlisted)
    ):  
    hitryagain = 0 # Initialize retry counter
    while True: # Keep trying until success or max retries
        try: # Attempt to create livestream
            service = get_service() # Get authenticated YouTube API service
            scheduled_start_time = datetime.now(timezone.utc).isoformat() # Set start time to now in UTC
                
            request = service.liveBroadcasts().insert( # Create new livestream broadcast request
                part="snippet,status,contentDetails", # Specify parts to update
                body={ # Request body with broadcast data
                    "snippet": { # Basic broadcast information
                        "title": title, # Set stream title
                        "description": description, # Set stream description
                        "scheduledStartTime": scheduled_start_time, # Set start time
                    },
                    "status": { # Stream privacy and content settings
                        "privacyStatus": kmself, # Set privacy level
                        "selfDeclaredMadeForKids": False # Declare not made for kids
                    },
                    "contentDetails": { # Stream technical settings
                        "enableAutoStart": True, # Enable automatic stream start
                        "enableAutoStop": True if config.livestreamautostop else False, # Enable auto-stop based on config
                        "latencyPrecision": "ultraLow" # Set ultra-low latency for real-time streaming
                    }
                }
            )
            response = request.execute() # Execute the broadcast creation request
            video_id = response['id'] # Extract video ID from response  
            
            if not config.playlist_id0 == "Null": # If playlist addition is enabled
                try: # Attempt to add video to first playlist
                    playlist_request = service.playlistItems().insert( # Create playlist item insertion request
                        part="snippet", # Only update snippet data
                        body={ # Request body with playlist item data
                            "snippet": { # Playlist item details
                                "playlistId": config.playlist_id0, # Target playlist ID
                                "resourceId": { # Video resource information
                                    "kind": "youtube#video", # Resource type is video
                                    "videoId": video_id # Video ID to add
                                }
                            }
                        }
                    )
                    playlist_request.execute() # Execute playlist addition request
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id0}") # Log successful addition
                except Exception as playlist_error: # If playlist addition fails
                    logging.error(f"Failed to add video to playlist: {playlist_error}") # Log playlist error
            if not config.playlist_id0 == "Null" and not config.playlist_id1 == "Null": # If double playlist mode is enabled
                try: # Attempt to add video to second playlist
                    playlist_request = service.playlistItems().insert( # Create second playlist item insertion request
                        part="snippet", # Only update snippet data
                        body={ # Request body with playlist item data
                            "snippet": { # Playlist item details
                                "playlistId": config.playlist_id1, # Target second playlist ID
                                "resourceId": { # Video resource information
                                    "kind": "youtube#video", # Resource type is video
                                    "videoId": video_id # Video ID to add
                                }
                            }
                        }
                    )
                    playlist_request.execute() # Execute second playlist addition request
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id1}") # Log successful addition to second playlist
                except Exception as playlist_error: # If second playlist addition fails
                    logging.error(f"Failed to add video to playlist: {playlist_error}") # Log second playlist error  
            return video_id # Return the created video ID on success
        except Exception as e: # If livestream creation fails
            if 'quotaExceeded' in str(e): # If YouTube API quota exceeded
                logging.info(f"Error and stoping because of api limited") # Log quota limit error
                exit() # Exit program due to quota limit
            if hitryagain == 3: # If maximum retry attempts reached
                logging.info(f"Error and stoping because of error that can't fix") # Log final failure
                exit() # Exit program due to unresolvable error
            hitryagain += 1 # Increment retry counter
            logging.info(f"Error: {e}") # Log the error details
            time.sleep(5) # Wait 5 seconds before retrying  

def api_load( # Function to handle API authentication through browser automation
    url, # OAuth URL to navigate to
    brandacc # Whether to use brand account or regular account
    ):  
    from logger_config import check_tv_logger as logging # Import logging configuration
    logging.info("create api keying ---edit_tv---") # Log start of API authentication process
    home_dir = os.path.expanduser("~") # Get user home directory path
    logging.info("run with countdriver.exe and check") # Log countdriver startup
    check_process_running() # Check if Chrome processes are already running
    subprocess.Popen(["start", "countdriver.exe"], shell=True) # Start Chrome driver executable
    options = Options() # Initialize Chrome options
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data") # Set Chrome user data directory path
    options.add_argument(f"user-data-dir={chrome_user_data_dir}") # Add user data directory option
    options.add_argument(f"profile-directory={config.Chrome_Profile}") # Add Chrome profile directory option
    driver = webdriver.Chrome(options=options) # Initialize Chrome WebDriver with options
    driver.get(url) # Navigate to OAuth authorization URL
    time.sleep(3) # Wait for page to load
    if brandacc == "Nope": # If using regular account
        nameofaccount = f"//div[contains(text(),'{config.accountname}')]" # XPath for regular account name
    else: # If using brand account
        nameofaccount = f"//div[contains(text(),'{config.brandaccname}')]" # XPath for brand account name
    button_element = driver.find_element("xpath", nameofaccount) # Find account selection button
    button_element.click() # Click on account to select it
    time.sleep(3) # Wait for account selection to process
    element = driver.find_element("xpath", "//*[@id='submit_approve_access']/div/button/div[3]") # Find approve access button
    element.click() # Click approve button to authorize access
    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # Terminate countdriver process
    logging.info("finish idk ---edit_tv---") # Log completion of authentication
    time.sleep(10) # Wait for authorization to complete
    driver.quit() # Close browser and clean up WebDriver  

def check_is_live_api( # Function to verify YouTube stream is live and handle failures
    url, # YouTube video ID to check
    ffmpeg, # FFmpeg process name for termination
    rtmp_server # RTMP server type being used
    ):  
    logging.info("Waiting for 40sec live on YouTube") # Log waiting period for stream to go live
    time.sleep(40) # Wait 40 seconds for YouTube to process stream
    new_url = f"https://youtube.com/watch?v={url}" # Construct full YouTube watch URL
    count_error = 0 # Initialize error counter
    MAX_RETRIES = 3 # Set maximum retry attempts
    if rtmp_server == "defrtmp": # If using default RTMP server
        text = "this" # Set parameter for default server restart
    else: # If using API-created RTMP server
        text = "api_this" # Set parameter for API server restart
    while True: # Keep checking until stream is live or max retries
        try: # Attempt to detect live stream
            streams = streamlink.streams(new_url) # Get available streams using streamlink
            hls_stream = streams["best"] # Try to access best quality stream
            logging.info('It is live now') # Log successful stream detection
            stream_state["stop_right_now"] = False # Update stream state to live
            break # Exit loop when stream is confirmed live
        except KeyError as e: # If stream is not available or not live
            logging.error(f'Stream not available: {str(e)}') # Log stream unavailability
            logging.info('The stream is messed up. Trying again...') # Log retry attempt
            time.sleep(2) # Brief wait before cleanup
            stream_state["stop_right_now"] = True # Signal to stop current streaming process
            subprocess.run(["taskkill", "/f", "/im", ffmpeg]) # Kill existing FFmpeg process
            stream_thread = threading.Thread(target=start_restreaming, args=(text,), daemon=False)
            stream_thread.start()
            time.sleep(35) # Wait for relay script to initialize
            count_error += 1 # Increment error counter
        if count_error >= MAX_RETRIES: # If maximum retry attempts exceeded
            logging.info("Retry limit exceeded. Shutting down.") # Log shutdown due to retry limit
            subprocess.Popen(["start", "python", "check_tv.py", "KILL"], shell=True) # Start shutdown script
            exit() # Exit current process

def api_create_edit_schedule( # Function to create, edit, or schedule YouTube livestreams
    part_number, # Part number for multi-part streams
    rtmp_server, # RTMP server type being used
    is_reload, # Whether this is a reload, edit, or new stream
    stream_url, # Existing stream URL or "Null" for new streams
    reason=None # Optional reason for stream creation
    ):  
    if config.StreamerName == "Null": # If no custom streamer name set
        username = config.username # Use default username
    else: # If custom streamer name is configured
        username = config.StreamerName # Use custom streamer name
    TESTING = "[TESTING WILL BE REMOVE AFTER]" if config.exp_tesing else "" # Add testing prefix if in testing mode
    if not is_reload or is_reload == "EDIT": # If creating new stream or editing existing
        stream_title = get_twitch_stream_title() # Get current Twitch stream title
        
        clean_title = ''.join(char for char in stream_title if char not in emoji.EMOJI_DATA).replace("<", "").replace(">", "") # Remove emojis and HTML brackets from title
        
        clean_title = ' '.join(clean_title.split()) # Normalize whitespace in title
        
        if clean_title and clean_title[0] == " ": # If title starts with space
            clean_title = clean_title[1:] # Remove leading space
        part_suffix = f" (PART{part_number})" if part_number > 0 else "" # Add part number suffix for multi-part streams
        filename = f"{username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}" # Format complete filename with username, title, date
        if len(filename) > 100: # If filename exceeds YouTube's 100 character limit
            max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 2) - len(part_suffix) - len(TESTING) # Calculate max allowed title length
            clean1_title = clean_title[:max_title_len-3] + "..." # Truncate title and add ellipsis
            filename = f"{username} | {clean1_title} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}" # Rebuild filename with truncated title
        if len(filename) > 100: # If filename still exceeds limit after truncation
            filename = f"{username} | {datetime.now().strftime('%Y-%m-%d')}{part_suffix}{TESTING}" # Use minimal filename with just username and date
        
        ITISUNLISTED = "[THIS RESTREAMING PROCESS IS DONE UNLISTED]" if config.unliststream else "" # Add unlisted notice if stream is unlisted
        reason_description = f"""
{reason}""" if reason is not None else "" # Add reason for stream creation if provided
        QA = "Q&A(Question The Same In Comment Won't Reply): https://sites.google.com/view/questionthatsomepeopleask" if config.QandA else "" # Add Q&A link if enabled
        Twitch_sub_or_turbo = "[AD-FREE: SUB/TURBO]" if config.brought_twitch_sub_or_turbo else "[ADS INCLUDE WILL AFFECT THE VIEWING EXPERIENCE]" # Add ad warning based on Twitch subscription status
        ADSqa = "Info about commercial break here: https://sites.google.com/view/qa-for-ads-problems/"  if config.ADSqa else "" # Add ads info link if enabled
        ADSqaN = "If you want to help out you can make a direct sub to username: karsteniee on Twitch to have no ads on a streamer(if you want to)" if not config.Filian else "" # Add subscription help text if not Filian
        description = f"""{TESTING}{ITISUNLISTED}{Twitch_sub_or_turbo}
Original broadcast from https://twitch.tv/{config.username} {reason_description}
[Stream Title: {clean_title}]
{ADSqa}
{QA}
Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee
Join My Community Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v
{ADSqaN}""" # Build complete description with all configured elements  
    try: # Attempt to execute stream creation or editing logic
        if is_reload is True: # If this is a reload waiting for streamer
            filename = f"{username} (WAITING FOR STREAMER){TESTING}" # Set waiting message as filename
            description = f"{TESTING}Waiting for https://twitch.tv/{config.username}, Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee, Join My Community Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v" # Set simple waiting description
        if stream_url == "Null": # If creating a new stream
            logging.info('Initiating API request for stream creation...') # Log stream creation start
            privacy_status = "public" if not config.unliststream else "unlisted" # Set privacy based on config
            if config.unliststream and config.public_notification: # If unlisted but with public notifications
                privacy_status = "public" # Override to public for notifications
            stream_url = create_live_stream(filename, description, privacy_status) # Create new YouTube livestream
            logging.info("==================================================") # Log separator
            if not config.playlist_id0 == "Null": # If single playlist mode enabled
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0}") # Log stream creation with playlist
            elif not config.playlist_id0 == "Null" and not config.playlist_id1 == "Null": # If double playlist mode enabled
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0} AND {config.playlist_id1}") # Log stream creation with both playlists
            else: # If no playlist mode
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url}") # Log stream creation without playlists
            logging.info("==================================================") # Log separator
            setup_stream_settings(stream_url, rtmp_server) # Configure stream settings and RTMP  
        if is_reload == "EDIT": # If this is an edit operation
            logging.info("Updating stream metadata and title...") # Log metadata update start
            edit_live_stream(stream_url, filename, description) # Update existing stream with new title and description
            return filename # Return updated filename
        if is_reload is True: # If this is a reload operation
            return stream_url # Return stream URL for reload
        if not is_reload: # If this is a new stream creation
            logging.info("Start stream relay") # Log stream relay initialization
            initialize_stream_relay(stream_url, rtmp_server, filename) # Start FFmpeg relay to YouTube
            edit_live_stream(stream_url, filename, description) # Update stream with final title and description
            return filename # Return filename for new stream
    except Exception as e: # If any critical error occurs
        logging.error(f"Critical error encountered during execution: {e}") # Log critical error
        exit() # Exit program due to critical failure

def initialize_stream_relay( # Function to start FFmpeg relay between Twitch and YouTube
    stream_url, # YouTube video ID for the stream
    rtmp_server, # RTMP server type being used
    filename # Filename for local archive if enabled
    ):
    if rtmp_server == "defrtmp": # If using default RTMP server
        rtmp_relive = "this" # Set parameter for default server relay
    else: # If using backup RTMP server
        rtmp_relive = "api_this" # Set parameter for backup server relay
    stream_thread = threading.Thread(target=start_restreaming, args=(rtmp_relive,), daemon=False)
    stream_thread.start()
    if config.local_archive: # If local archiving is enabled
        local_save_thread = threading.Thread(target=local_save, args=(filename,), daemon=False)
        local_save_thread.start()
    if rtmp_server == "defrtmp": # If using default RTMP server
        ffmpeg_exe = config.ffmpeg # Use primary FFmpeg executable
        ffmpeg_1exe = config.ffmpeg1 # Set secondary FFmpeg for cleanup
    else: # If using backup RTMP server
        ffmpeg_exe = config.ffmpeg1 # Use secondary FFmpeg executable
        ffmpeg_1exe = config.ffmpeg # Set primary FFmpeg for cleanup
    check_is_live_api(stream_url, ffmpeg_exe, rtmp_server) # Verify stream goes live successfully
    stream_state["stop_right_now"] = True # Update stream state to live
    subprocess.run(["taskkill", "/f", "/im", ffmpeg_1exe]) # Kill alternate FFmpeg process
    if rtmp_server == "bkrtmp": # If using backup RTMP server
        rtmp_key = config.rtmp_key # Use backup RTMP key
    else: # If using default RTMP server
        rtmp_key = config.rtmp_key_1 # Use default RTMP key
    if config.playvideo: # If video playback is enabled
        os.system(f'start {ffmpeg_1exe} -re -i blackscreen.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}') # Start black screen video to RTMP  

def initialize_and_monitor_stream(): # Main function to initialize and monitor the streaming process
    if not check_chrome_version(): # If Chrome version check fails
        logging.info("Error try fixing your chrome version guide on github") # Log Chrome version error
        exit() # Exit due to incompatible Chrome version
    try: # Attempt to initialize monitoring system
        yt_link = "Null" # Initialize YouTube link variable
        rtmp_info = "Null" # Initialize RTMP server info variable
        IFTHEREISMORE = "" # Initialize additional arguments display string
        THEREISMORE = "Null" # Initialize flag for additional streams
        bk_rtmp_info = "Null" # Initialize backup RTMP info variable
        bk_yt_link = "Null" # Initialize backup YouTube link variable
        arguments = sys.argv # Get command line arguments  
        if len(arguments) < 2: # If no command line arguments provided
            logging.info("==================================================") # Log separator
            logging.info("NO ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)") # Log no arguments message
            logging.info(f"ARCHIVE USER: {config.username}") # Log target username
            logging.info("==================================================") # Log separator
        else: # If command line arguments are provided
            yt_link = arguments[1] # Get first argument (YouTube video ID)
            if yt_link == "KILL": # If kill command is provided
                logging.info("close all exe") # Log process termination
                subprocess.run(["taskkill", "/f", "/im", config.ffmpeg]) # Kill primary FFmpeg process
                subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1]) # Kill secondary FFmpeg process
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # Kill Chrome driver
                exit(1) # Exit after killing all processes
            rtmp_info = arguments[2] # Get second argument (RTMP server type)
            if len(arguments) < 3: # If RTMP argument is missing
                logging.error("Missing required RTMP argument") # Log missing argument error
                exit(1) # Exit due to missing argument
            if len(yt_link) != 11: # If YouTube video ID is wrong length
                logging.error(f"Invalid argument for ARG1: {yt_link}. Must be 11 characters long YouTube Video ID") # Log invalid video ID error
                exit(1) # Exit due to invalid video ID
            if rtmp_info not in ["defrtmp", "bkrtmp"]: # If RTMP server type is invalid
                logging.error(f"Invalid argument for ARG2: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'") # Log invalid RTMP server error
                exit(1) # Exit due to invalid RTMP server  
            
            if len(arguments) == 4: # If backup stream argument is provided
                bk_yt_link = arguments[3] # Get third argument (backup YouTube video ID)
                if len(bk_yt_link) != 11: # If backup video ID is wrong length
                    logging.error(f"Invalid argument for ARG3: {bk_yt_link}. Must be 11 characters long YouTube Video ID") # Log invalid backup video ID error
                    exit(1) # Exit due to invalid backup video ID
                IFTHEREISMORE = f"ARG3: {bk_yt_link}(SKIP CREATING BK STREAM AND RESTORE MONITORING)" # Set display string for backup stream
                THEREISMORE = True # Set flag indicating backup stream is provided
            logging.info("==================================================") # Log separator
            logging.info("INPUT ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)") # Log arguments available message
            logging.info(f"ARG1: {yt_link} ARG2: {rtmp_info} {IFTHEREISMORE}") # Log all provided arguments
            logging.info(f"ARCHIVE USER: {config.username}") # Log target username
            logging.info("==================================================") # Log separator  
        if rtmp_info not in ["defrtmp", "bkrtmp", "Null"]: # If RTMP server type is invalid
            logging.error(f"Invalid RTMP server type: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'") # Log invalid RTMP server error
            exit(1) # Exit due to invalid RTMP server
        live_url = None # Initialize live stream URL variable
        rtmp_server = None # Initialize RTMP server variable
        if yt_link == "Null": # If no YouTube link provided (creating new stream)
            logging.info("Starting live API check to get initial stream URL") # Log new stream creation
            rtmp_server = "defrtmp" # Use default RTMP server for new streams
            try: # Attempt to create new stream
                live_url = api_create_edit_schedule(0, rtmp_server, True, "Null") # Create new waiting stream
                logging.info(f"Successfully created new stream with URL: {live_url}") # Log successful stream creation
            except Exception as e: # If stream creation fails
                logging.error(f"Failed to create stream via API: {str(e)}") # Log stream creation error
                raise # Re-raise exception for upper level handling
        else: # If YouTube link is provided (using existing stream)
            live_url = yt_link # Use provided YouTube video ID
            rtmp_server = rtmp_info # Use provided RTMP server type
            # Log that we're using an existing YouTube stream with its URL and RTMP server
            logging.info(f"Using provided YouTube link: {live_url} with RTMP server: {rtmp_server}")
        
        # If no additional stream info provided, wait for stream to go live
        if THEREISMORE == "Null":
            logging.info("Waiting for stream to go live...")
            status = {"status": False}  # Shared status dictionary to track if stream is live}
            # Create and start daemon thread for handling user input
            input_thread = threading.Thread(
                target=handle_input,
                args=(status, live_url, rtmp_server),
                daemon=True
            )
            input_thread.start()
            
            while True:  # Infinite loop
                try:
                    streams = get_twitch_streams()  # Getting Twitch streams and client
                    if streams:  # Checking if streams are available
                        if not streams == "ERROR":
                            stream = streams[0]  # Getting the first stream
                            logging.info(f"Stream is now live! Title From Twitch: {stream['title']}")  # Logging stream is live
                            status['status'] = True
                            break  # Breaking the loop
                        else:
                            logging.error(f"Error checking stream status")  # Logging error
                            time.sleep(30)  # Waiting before retrying
                    else:
                        time.sleep(10)  # Waiting before retrying
                except Exception as e:  # Handling exceptions
                    logging.error(f"Error checking stream status: {str(e)}")  # Logging error
                    time.sleep(30)  # Waiting before retrying
            
            # Initialize spare URL as None
            live_spare_url = None  
            logging.info("Starting stream monitoring process...")  

            # Validate required parameters
            if not live_url:  
                logging.error("Missing live URL - cannot start monitoring")  
                exit(1)  
            if rtmp_server not in ["defrtmp", "bkrtmp"]:  
                logging.error(f"Invalid RTMP server type: {rtmp_server}")  
                exit(1)

            # Start appropriate relay process based on RTMP server type
            try:
                if rtmp_server == "bkrtmp":  
                    logging.info("Starting with backup stream rtmp... and check")  
                    stream_thread = threading.Thread(target=start_restreaming, args=("api_this",), daemon=False)
                    stream_thread.start()
                    check_is_live_api(live_url, config.ffmpeg1, rtmp_server) 
                elif rtmp_server == "defrtmp":  
                    logging.info("Starting with default stream rtmp... and check")  
                    stream_thread = threading.Thread(target=start_restreaming, args=("this",), daemon=False)
                    stream_thread.start()  
                    check_is_live_api(live_url, config.ffmpeg, rtmp_server) 

                # Start local archive if enabled
                if config.local_archive:
                    logging.info("Starting local archive process...")
                    filename = f"{datetime.now().strftime('%Y-%m-%d')}_{stream['title']}"
                    local_save_thread = threading.Thread(target=local_save, args=(filename,), daemon=False)
                    local_save_thread.start()

            except Exception as e:  
                logging.error(f"Failed to start relay process: {str(e)}")  
                exit(1)  
                logging.info("Stream relay process started successfully")  
        else:
            # Skip if additional stream info exists
            pass
            
        try:
            # Get or update stream title based on whether additional info exists
            if THEREISMORE == "Null":
              titlegmail = api_create_edit_schedule(0, rtmp_server, "EDIT", live_url)  
            else:
              titlegmail = get_youtube_stream_title(live_url)
            logging.info('edit finished continue the stream')  
        except UnboundLocalError:  
            # Handle missing local variable error
            logging.warning("Encountered UnboundLocalError when getting title - continuing with default continue at your own risk")  
        except Exception as e:  
            # Handle other errors getting stream title
            logging.error(f"Error getting stream title: {str(e)} - Error continue at your own risk")  

        try:
            # Configure backup stream
            logging.info("Loading backup stream configuration...")  
            # Switch RTMP server type for backup
            if rtmp_server == "bkrtmp":
                rtmp_server = "defrtmp"
            elif rtmp_server == "defrtmp":
                rtmp_server = "bkrtmp"

            # Create new backup stream or use provided backup link
            if bk_yt_link == "Null" and bk_rtmp_info == "Null":
                live_spare_url = api_create_edit_schedule(0, rtmp_server, True, "Null")  
            else:
                live_spare_url = bk_yt_link  
            logging.info(f"Backup stream URL configured: {live_spare_url}")  
        except Exception as e:  
            # Handle errors creating backup stream
            logging.error(f"Failed to create backup stream: {str(e)}")  

        # Start monitoring for stream going offline
        logging.info("Starting offline detection...")  
        offline_check_functions(live_url, live_spare_url, rtmp_server, titlegmail)  
    except Exception as e:  
        # Handle any critical errors in main function
        logging.error(f"Error in initialize_and_monitor_stream: {str(e)}", exc_info=True)  
        logging.error("Critical error encountered - terminating script execution")  
        exit(1)  

def check_chrome_version(target_version=(130, 0, 6723, 70)):
    """Check if installed Chrome version is <= target version (default: 130.0.6723.70)"""
    try:
        # Open Chrome registry key to get version info
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon') as key:
            version_str, _ = winreg.QueryValueEx(key, 'version')  # Get Chrome version string from registry
            version = tuple(map(int, version_str.split('.')))  # Convert version string to tuple of integers
            
        # Compare installed version with target version
        if version <= target_version:
            return True  # Chrome version is compatible
        else:
            logging.info(f"Chrome version {version_str} is > {'.'.join(map(str, target_version))}")  # Log incompatible version
            return False
    
    except FileNotFoundError:  # Handle case where Chrome is not installed
        logging.info("Chrome is not installed or version could not be detected.")
        return False
    except (ValueError, Exception) as e:  # Handle other errors checking version
        logging.info(f"Error checking Chrome version: {str(e)}")
        return False

def get_m3u8_urls(username):
    def check_1080p_quality(m3u8_url):  # Inner function to check for 1080p stream URL
        try:
            response = requests.get(m3u8_url, timeout=10)  # Get m3u8 playlist
            response.raise_for_status()  # Check for HTTP errors
            lines = response.text.splitlines()  # Split playlist into lines
            for i, line in enumerate(lines):  # Check each line for 1080p stream
                if line.startswith('#EXT-X-STREAM-INF:') and 'RESOLUTION=1920x1080' in line:
                    # If 1080p stream found, return the URL from next line
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
            return None  # No 1080p stream found
        except Exception as e:  # Handle errors checking quality
            logging.info(f"Error checking quality for {m3u8_url}: {str(e)}")
            return None
    
    # Import required proxy and webdriver management libraries
    from browsermobproxy import Server #type: ignore[import]
    from webdriver_manager.chrome import ChromeDriverManager #type: ignore[import]
    
    # Set up paths for proxy server
    current_dir = os.getcwd()
    server_path = os.path.join(current_dir, "browsermob-proxy-2.1.4", "bin", "browsermob-proxy.bat")
    
    # Download and extract proxy if not present
    if not os.path.exists(os.path.join(current_dir, "browsermob-proxy-2.1.4")):
        logging.info("browsermob-proxy not found, downloading...")
        
        download_url = "https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip"
        response = requests.get(download_url, stream=True)  # Download proxy zip
        response.raise_for_status()  # Check for download errors
        
        # Extract proxy files
        with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_ref:
            zip_ref.extractall(current_dir)
        logging.info("BrowserMob Proxy downloaded and extracted successfully")
    
    # Start proxy server
    server = Server(server_path)
    server.start()
    proxy = server.create_proxy()
    logging.info(proxy.proxy)
    
    # Configure Chrome options with proxy
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy.proxy}')  # Set proxy server
    chrome_options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors
    chrome_options.add_argument('--ignore-ssl-errors')  # Ignore SSL errors
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')  # Ignore certificate errors
    chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')  # Allow autoplay

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Start capturing network traffic    
    proxy.new_har("m3u8_capture", options={"captureContent": False})
    driver.get(f"https://www.twitch.tv/{username}")  # Navigate to Twitch channel
        
    # Wait for stream to be live
    while True:
        try:
          # Look for LIVE indicator
          driver.find_element("xpath", "//div[@class='Layout-sc-1xcs6mc-0 liveIndicator--x8p4l']//span[text()='LIVE']")
          break
        except NoSuchElementException:
            try:
                # Try clicking chat tab to refresh
                driver.find_element("xpath", "//a[@tabname='chat' and @data-a-target='channel-home-tab-Chat' and contains(@href, '/" + username + "')]").click()
                while True:  
                 try:
                   streams = get_twitch_streams()  # Check stream status via API
                   if streams:  
                    if not streams == "ERROR":
                      stream = streams[0]  # Get first stream
                      logging.info(f"Stream is now live! Title From Twitch: {stream['title']}")  
                      break  
                   else:
                    time.sleep(10)  # Wait before retrying
                 except Exception as e:  
                    logging.error(f"Error checking stream status: {str(e)}")  
                    time.sleep(30)  # Wait longer on error
                driver.refresh()  # Refresh page
            except NoSuchElementException:
                time.sleep(3)  # Brief wait before retry
        
    # Extract m3u8 URLs from network traffic
    har_data = proxy.har
    m3u8_urls = []
    m3u8_pattern = re.compile(r'.*\.m3u8(\?.*)?$', re.IGNORECASE)  # Pattern to match m3u8 URLs
    for entry in har_data['log']['entries']:
        if 'request' in entry and 'url' in entry['request']:
            url = entry['request']['url']
            if m3u8_pattern.match(url):  # If URL is m3u8
                m3u8_urls.append(url)
    
    # Find 1080p stream URL
    for url in list(set(m3u8_urls)):  # Check unique URLs
        if username in url:  # Only check URLs for target channel
            
            stream_url = check_1080p_quality(url)  # Check for 1080p stream
            if stream_url:
                logging.info(f"Found 1080p URL: {stream_url}")
                driver.quit()  # Clean up WebDriver
                server.stop()  # Stop proxy server
                return stream_url  # Return 1080p stream URL
    
    # Clean up if no 1080p URL found
    driver.quit()
    server.stop()
    return None

def show_agreement_screen():
    """Shows an EULA dialog and manages user acceptance"""
    
    # Skip if already accepted
    if hasattr(config, 'agreement_accepted') and config.agreement_accepted:
        return True

    # Create main window
    root = tk.Tk()
    root.title("End User License Agreement For Twitch Stream to YouTube")
    root.geometry("600x400")
    
    # Enable DPI awareness
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass  

    # Configure window properties
    root.minsize(width=600, height=450)  
    root.resizable(True, True)
    root.configure(bg="white")

    # Create scrollable canvas
    main_canvas = tk.Canvas(root, bg="white")
    main_scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)
    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    # Create content frame
    content_frame = tk.Frame(main_canvas, bg="white")
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    # Update window size and position
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = max(600, int(screen_width * 0.5))
    height = max(450, int(screen_height * 0.6))
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Configure scrollbar update function
    def update_scrollbar(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    content_frame.bind("<Configure>", update_scrollbar)

    # Add title label
    title_label = tk.Label(content_frame, text="End User License Agreement For Twitch Stream to YouTube", 
                          font=('Helvetica', 18, 'bold'), bg="white")
    title_label.pack(pady=(30, 20), padx=30, anchor="w")

    # Create text area frame
    text_frame = tk.Frame(content_frame, bg="white")
    text_frame.pack(fill=tk.BOTH, expand=True, padx=30)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create text area for agreement content
    agreement_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, 
                           font=('Helvetica', 11), bg="white")
    agreement_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.config(command=agreement_text.yview)

    # Function to download agreement content
    def download_agreement_content():
        agreement_url = 'https://raw.githubusercontent.com/karstenlee10/Twitch_Stream_To_YouTube/refs/heads/main/END%20USER%20LICENSE%20AGREEMENT'
        try:
            response = requests.get(agreement_url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.info(f"Error downloading agreement: {e}")
            exit()

    # Get and display agreement content
    agreement_content = download_agreement_content()
    agreement_text.insert(tk.END, agreement_content)
    agreement_text.config(state=tk.DISABLED)

    # Create button frame
    button_frame = tk.Frame(content_frame, bg="white", height=80)
    button_frame.pack(fill=tk.X, pady=20, padx=30)
    button_frame.pack_propagate(False)

    # Add spacer for button alignment
    spacer = tk.Frame(button_frame, bg="white")
    spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Function to handle agreement acceptance
    def accept_agreement():
        config.agreement_accepted = True
        try:
            # Update config file
            with open('config_tv.py', 'r') as f:
                config_lines = f.readlines()

            with open('config_tv.py', 'w') as f:
                for line in config_lines:
                    if line.startswith('agreement_accepted ='):
                        f.write('agreement_accepted = True\n')
                    else:
                        f.write(line)

            # Reload config module
            importlib.reload(config)
        except Exception as e:
            logging.info(f"Error saving agreement status: {e}")
        root.destroy()

    # Function to handle agreement decline
    def decline_agreement():
        messagebox.showerror("Agreement Declined", "You must accept the agreement to use this software.")
        root.destroy()
        exit()

    # Create accept/decline buttons
    accept_button = tk.Button(button_frame, text="I Accept", command=accept_agreement, 
        bg="4CAF50", fg="white", font=('Helvetica', 12, 'bold'), padx=20, pady=8, 
        width=10)
    accept_button.pack(side=tk.RIGHT, padx=5)

    decline_button = tk.Button(button_frame, text="I Decline", command=decline_agreement, 
        bg="f44336", fg="white", font=('Helvetica', 12, 'bold'), padx=20, pady=8, 
        width=10)
    decline_button.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

if __name__ == "__main__":  
    # Show agreement screen on first run
    show_agreement_screen()
    initialize_and_monitor_stream()  # Start main program
    exit()  # Exit cleanly

