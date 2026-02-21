# GUI IMPORTS
########################################################################
import tkinter as tk # For GUI elements
from tkinter import messagebox # For message boxes
########################################################################
# NORMAL IMPORTS
########################################################################
import os # For file and directory operations
import sys # For checking command line arguments
import time # For delays
import json # For handling JSON data
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
import psutil # For checking running processes
import base64 # For encoding and decoding base64 strings
import winreg # For accessing Windows registry, checking chrome version
import streamlink # For checking YouTube livestream status
from ctypes import windll # For accessing Windows API functions and checking display dpi
from PIL import Image, ImageDraw, ImageFont # For image processing and drawing text on images
########################################################################
# SELENIUM IMPORTS
########################################################################
from selenium import webdriver # For controlling web browsers
from selenium.webdriver.common.by import By # For locating elements in the DOM
from selenium.webdriver.chrome.options import Options # For configuring Chrome options
from selenium.webdriver.support.ui import WebDriverWait # For waiting for elements in the DOM
from selenium.webdriver.support import expected_conditions as EC # For waiting for conditions in the DOM
from selenium.common.exceptions import (SessionNotCreatedException, TimeoutException) # For handling Selenium exceptions
########################################################################
# LOCAL IMPORTS
########################################################################
from logger_config import check_tv_logger as logging # For logging messages
import config_tv as config # For configuration settings
########################################################################

# HOPE IT WORKS PLEASE DON'T HAVE ANY PROBLEMS THANKS 19:29 17.12.2025

# SCRIPT VERSION
script_version = "0.7.1.2"

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

DEBUG = {
    'change_something_cat': None,
    'change_something_title': None
}

stream_state = {
    'stop_right_now': False # Flag to immediately stop streaming
}

DESCRIPTION = {
    'description_first': None, # First part of the stream description
    'description_second': None, # Second part of the stream description
}

CATEGORY = {
    'currentnumber': -1, # Current part number of the stream
    'part0': None, # First part of the stream
}

TITLE = {
    'currentnumber': -1, # Current part number of the stream
    'part0': None, # First part of the stream
}

PART = {
    'partnumber': -1, # Current part number of the stream
    'part0': None, # First part of the stream
}

state = {  # Dictionary to store all stream monitoring state variables
        'gmail_checking': True,  # Whether to check Gmail for notifications
        'live_url': None,  # Current live stream URL
        'spare_link': None,  # Spare link for backup stream
        'rtmp_server': None,  # RTMP server to use for streaming(spare_link)
        'titleforgmail': None,  # Title for Gmail notifications
        'latest_cleantitle': None,  # Latest stream title
        "reason": "Null", # Reason for switching streams, initially set to "Null"
        "restart_timer": False, # Timer for restarting the stream
        'thread_in_use': False, # Whether a thread is currently using a important script
        'ending': False, # Whether the stream is ending
        'exit_flag': False # Flag to indicate if the script should exit
}

def restart_title_arg():
    global TITLE
    TITLE = {
    'currentnumber': -1, # Current part number of the stream
    'part0': None, # First part of the stream
    }

def restart_category_arg():
    global CATEGORY
    CATEGORY = {
    'currentnumber': -1, # Current part number of the stream
    'part0': None, # First part of the stream
    }

def check_is_live(): 
    trytimes = 0 
    while True: 
        try: 
            streamlink.streams("https://www.twitch.tv/" + config.username)["best"] 
            return True 
        except KeyError: 
            trytimes += 1 
            time.sleep(3) 
            if trytimes == 3: 
                logging.info('150 - The stream is finsh') 
                return False 
        except Exception as e:
            trytimes += 1 
            time.sleep(3) 
            if trytimes == 3: 
                logging.error(f'150 - Error checking Twitch stream status: {e}, use api to check') 
                if get_twitch_streams():
                    return True
                else:
                    return False

def start_restreaming(status, url_info):
    TRY = 0
    if status == "api_this": 
        logprint = f'166 - script is started now {url_info}'
        ffmpeg_process = config.ffmpeg1 
        rtmp_key = config.rtmp_key_1 
    elif status == "this": 
        logprint = f'166 - script is started now api {url_info}'
        ffmpeg_process = config.ffmpeg 
        rtmp_key = config.rtmp_key 
    if config.twitch_account_token != "Null":
        token = f'"--twitch-api-header=Authorization=OAuth {config.twitch_account_token}" '
    else:
        token = ""
    while True: 
        logging.info(logprint)
        command = f'''start /wait cmd /c "streamlink https://www.twitch.tv/{config.username} best {token}-o - | {ffmpeg_process} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}"''' 
        logging.info(f"166 - Starting restreaming with command: {command}")
        start_time = time.time()
        os.system(command) 
        if (time.time() - start_time) <= 30:
            if TRY == 3:
                logging.info("166 - streamlink have a big error stopping stream")
                while state['thread_in_use']: 
                    time.sleep(1)  
                state['thread_in_use'] = True 
                handle_stream_offline(True) 
                state['thread_in_use'] = False
                break
            logging.info("166 - streamlink having error try again")
            TRY += 1
        if stream_state['stop_right_now']: 
            logging.info(f'166 - The stream is stopped now {url_info}') 
            stream_state["stop_right_now"] = False 
            break 
        if check_is_live(): 
            logging.info(f'166 - The stream is still live now {url_info}') 
        else: 
            logging.info(f'166 - The stream is finsh now {url_info} start offline process') 
            while state['thread_in_use']: 
                time.sleep(1)  
            state['thread_in_use'] = True 
            handle_stream_offline() 
            state['thread_in_use'] = False
            break 

def local_save(title): 
    while True: 
        counter = 0 
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        archive_dir = os.path.join(script_dir, "local_archive") 
        if not os.path.exists(archive_dir): 
            os.makedirs(archive_dir) 
        filename = os.path.join(archive_dir, f"{title}.mp4") 
        while os.path.exists(filename): 
            counter += 1 
            filename = os.path.join(archive_dir, f"{title}({counter}).mp4") 
        if config.twitch_account_token != "Null":
            token = f'"--twitch-api-header=Authorization=OAuth {config.twitch_account_token}" '
        else:
            token = ""
        command = f'''start /wait cmd /c "streamlink https://www.twitch.tv/{config.username} best {token}-o {filename}"''' 
        os.system(command) 
        if check_is_live(): 
            logging.info('197 - The stream is still live now') 
            local_save(title) 
        else: 
            logging.info('197 - The stream is finsh now') 
        exit() 

def offline_check_functions( 
    live_url, 
    spare_link, 
    rtmp_server, 
    title 
    ):  
    state['live_url'] = live_url  
    state['spare_link'] = spare_link  
    state['rtmp_server'] = rtmp_server  
    state['titleforgmail'] = title  
    TITLE["currentnumber"] +=1
    TITLE[f"part0"] = state["latest_cleantitle"]
    logging.info(f"221 - Initializing offline detection monitoring service... With {state}")  
    if config.unliststream and config.public_notification: 
        logging.info("221 - stream back to unlisted") 
        share_settings_api(state['live_url'], "unlisted") 
    threading.Thread(target=hours_checker, daemon=False).start()
    threading.Thread(target=find_thrid_party_notification, daemon=False).start() 
    if config.refresh_stream_title: 
        threading.Thread(target=refresh_stream_title, daemon=False).start()
    if config.category: 
        threading.Thread(target=refresh_stream_category, daemon=False).start()
    threading.Thread(target=handle_user_input, daemon=True).start() 
    while not state.get('exit_flag', False): 
        time.sleep(1) 
    logging.info("221 - Stopping the entire script...") 
    psutil.Process(os.getpid()).terminate() 

def start_browser(stream_url):  
    check_process_running()  
    subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])
    subprocess.Popen(["start", "countdriver.exe"], shell=True)  
    options = Options()  
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")  
    options.add_argument(f"user-data-dir={chrome_user_data_dir}")  
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  
    driver = None  
    try_count = 0  
    while True:  
        driver = webdriver.Chrome(options=options)  
        url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  
        driver.get(url_to_live)  
        while True: 
            try: 
                WebDriverWait(driver, 30).until( 
                    EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/ytls-widget-section/ytls-stream-settings-widget-renderer/div[2]/div[1]/ytls-metadata-collection-renderer/div[2]/div/ytls-metadata-control-renderer[6]/div/ytls-latency-control-renderer/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]')) 
                ) 
                return driver 
            except TimeoutException: 
                try: 
                    error_element = driver.find_element(By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[3]/ytls-live-dashboard-error-renderer/div/yt-icon') 
                    if error_element: 
                        logging.info("247 - Error element found - YouTube Studio is in error state") 
                        driver.refresh() 
                        time.sleep(2) 
                        try_count += 1 
                        if try_count >= 3: 
                            logging.error("247 - 3 consecutive errors detected - STOP PROCESS") 
                            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
                            return False 
                except: 
                    logging.info("247 - Element not found after 30s, refreshing page...") 
                    driver.refresh() 
                    time.sleep(2) 
                    try_count += 1 
                    if try_count >= 3: 
                        logging.error("247 - 3 consecutive timeouts detected - STOP PROCESS") 
                        subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
                        return False 

def setup_stream_settings( 
    stream_url, 
    rtmp_server 
    ):  
    try_count = 0  
    while True: 
        try: 
            driver = start_browser(stream_url) 
            if not driver: 
                return False 
            logging.info("289 - Configuring RTMP key and chat settings...") 
            driver.find_element(By.XPATH, "/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/ytls-widget-section/ytls-stream-settings-widget-renderer/div[2]/div[1]/ytls-metadata-collection-renderer/div[2]/div/ytls-metadata-control-renderer[6]/div/ytls-latency-control-renderer/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]").click() 
            time.sleep(5) 
            driver.find_element(By.XPATH, "/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/div/div/div[1]/div[1]/ytls-player-renderer/div[2]/div/div/div[1]/ytls-ingestion-dropdown-trigger-renderer/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/span[2]/yt-icon/span").click() 
            time.sleep(3) 
            if rtmp_server == "bkrtmp": 
                driver.find_element(By.XPATH, f"//tp-yt-paper-item[contains(@aria-label, '{config.rtmpkeyname1}')]").click()
                time.sleep(7) 
            if rtmp_server == "defrtmp": 
                driver.find_element(By.XPATH, f"//tp-yt-paper-item[contains(@aria-label, '{config.rtmpkeyname}')]").click()
                time.sleep(7) 
            if config.disablechat: 
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click() 
                time.sleep(3) 
                driver.find_element(By.XPATH, "//li[@id='customization']").click() 
                time.sleep(2) 
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[1]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click() 
                time.sleep(1) 
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click() 
            if not config.disablechat: 
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click() 
                time.sleep(3) 
                driver.find_element(By.XPATH, "//li[@id='customization']").click() 
                time.sleep(2) 
                driver.find_element(By.XPATH, "/html/body/ytls-broadcast-edit-dialog/ytcp-dialog/tp-yt-paper-dialog/div[2]/div/ytcp-navigation/div[2]/tp-yt-iron-pages/ytls-advanced-settings/div/ytcp-form-live-chat/div[3]/div[2]/div[1]/ytcp-form-checkbox/ytcp-checkbox-lit/div/div[1]/div").click() 
                time.sleep(1) 
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click() 
            while True: 
                try: 
                    WebDriverWait(driver, 30).until( 
                        EC.presence_of_element_located((By.XPATH, "/html/body/ytcp-app/ytcp-toast-manager/tp-yt-paper-toast")) 
                    )
                    logging.info("289 - Toast notification appeared") 
                    break 
                except TimeoutException: 
                    logging.info("289 - Toast notification not found, continuing to wait...") 
            logging.info("289 - RTMP key configuration updated successfully...") 
            driver.quit() 
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) 
            if driver: 
                driver.quit() 
            break 
        except SessionNotCreatedException as e: 
            try_count += 1 
            if try_count >= 3: 
                logging.error(f"289 - Session not created: [{e}] Critical Error KILL ALL") 
                os.system("start check_tv.py KILL") 
                psutil.Process(os.getpid()).terminate() 
            if "DevToolsActivePort file doesn't exist" in str(e): 
                logging.error(f"289 - Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.") 
            else: 
                logging.error(f"289 - Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") 
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"]) 
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
            time.sleep(5) 
        except Exception as e: 
            try_count += 1 
            if try_count >= 3: 
                logging.error(f"289 - Session not created: [{e}] Critical Error KILL ALL") 
                os.system("start check_tv.py KILL") 
                exit(1) 
            logging.error(f"289 - Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") 
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"]) 
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
            time.sleep(5) 

def ending_stream(stream_url):  
    try_count = 0  
    while True:  
        try:
            driver = start_browser(stream_url) 
            if not driver: 
                return False 
            logging.info("365 - Stop livestream manually...")  
            try: 
                header_title = driver.find_element(By.XPATH, '//*[@id="header-title"]') 
                if header_title: 
                    logging.info("365 - Found already ended, breaking loop...") 
                    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
                    if driver:  
                        driver.quit()  
                    return False 
            except: 
                pass 
            driver.find_element(By.XPATH, '//*[@id="end-stream-button"]').click()  
            time.sleep(3)  
            driver.find_element(By.XPATH, '/html/body/ytcp-confirmation-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div[2]/ytcp-button[2]/ytcp-button-shape/button').click()  
            time.sleep(10)  
            logging.info("365 - livestream ended successfully...")  
            driver.quit()  
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
            if driver:  
                driver.quit()  
            break  
        except SessionNotCreatedException as e: 
            try_count += 1  
            if try_count >= 3:  
                logging.error(f"365 - Session not created: [{e}] Critical Error STOP PROCESS") 
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  
                return False 
            if "DevToolsActivePort file doesn't exist" in str(e): 
                logging.error(f"365 - Chrome WebDriver failed to start: [{e}] DevToolsActivePort file doesn't exist. Terminating all Chrome processes and retry.") 
            else: 
                logging.error(f"365 - Session not created: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") 
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
            time.sleep(5) 
        except Exception as e: 
            try_count += 1  
            if try_count >= 3:  
                logging.error(f"365 - Session not created: [{e}] Critical Error STOP PROCESS") 
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  
                return False 
            logging.error(f"365 - Unexpected error: [{e}] KILL ALL CHROME PROCESS AND TRY AGAIN") 
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])  
            subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  
            time.sleep(5)     

def handle_stream_offline(
        force_offline=None
        ):  
    state['ending'] = True 
    if force_offline:  
        logging.info(f"419 - Force offline detected - initiating shutdown sequence... and play ending screen and stop starting new process")  
        stream_state["stop_right_now"] = True 
        if state['rtmp_server'] == "defrtmp": 
            ffmpeg = config.ffmpeg1      
        else: 
            ffmpeg = config.ffmpeg   
        subprocess.run(["taskkill", "/f", "/im", ffmpeg])
    if force_offline == "DEBUG" or force_offline == None:
        logging.info("419 - Stream offline status detected - initiating shutdown sequence... and play ending screen and start new process")  
        if state["spare_link"] is None:
            logging.info("419 - Waiting for spare link to be NOT None this is sus...")
            while state["spare_link"] is None:
                time.sleep(1)
        base64_TITLE = base64.b64encode(json.dumps(TITLE, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        base64_PART = base64.b64encode(json.dumps(PART, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        base64_state = base64.b64encode(json.dumps(state, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        base64_category = base64.b64encode(json.dumps(CATEGORY, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        DATA_OMG = json.dumps({"TITLE": base64_TITLE,"PART": base64_PART,"state": base64_state, "CATEGORY": base64_category})
        DATA_OMG_BASE64 = base64.b64encode(DATA_OMG.encode('utf-8')).decode('utf-8')
        subprocess.Popen(["start", "cmd" , "/c", "py", "check_tv.py", state["spare_link"], state["rtmp_server"], "Prev", DATA_OMG_BASE64], shell=True)
    if PART["partnumber"] >= 0 and PART["part0"] is not None and TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking'] and CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None:  
        logging.info("419 - Updating stream description to mark the end of the stream...ALL")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "ALL"),
            daemon=False
        ).start()
    elif TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking'] and PART["partnumber"] >= 0 and PART["part0"] is not None:  
        logging.info("419 - Updating stream description to mark the end of the stream...PARTANDDESC")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "PARTANDDESC"),
            daemon=False
        ).start()
    elif CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None and PART["partnumber"] >= 0 and PART["part0"] is not None:  
        logging.info("419 - Updating stream description to mark the end of the stream...PARTANDCAT")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "PARTANDCAT"),
            daemon=False
        ).start()
    elif CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None and TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking']:  
        logging.info("419 - Updating stream description to mark the end of the stream...DESCANDCAT")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "DESCANDCAT"),
            daemon=False
        ).start()
    elif PART["partnumber"] >= 0 and PART["part0"] is not None:  
        logging.info("419 - Updating stream description to mark the end of the stream...PARTLIST")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "PARTLIST"),
            daemon=False
        ).start()
    elif TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking']:  
        logging.info("419 - Updating stream description to mark the end of the stream...DESCRIPTION")
        threading.Thread(
            target=api_create_edit_schedule,
            args=(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "DESCRIPTION"),
            daemon=False
        ).start()

    if config.playvideo:  
        if state['rtmp_server'] == "defrtmp": 
            rtmp_key = config.rtmp_key_1  
            ffmpeg = config.ffmpeg1      
        else: 
            rtmp_key = config.rtmp_key  
            ffmpeg = config.ffmpeg     
        os.system(f'{ffmpeg} -re -i ending.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}')  
    if config.unliststream:  
        logging.info("419 - Setting stream visibility to public...")  
        share_settings_api(state['live_url'], "public")
    logging.info("419 - ending the stream...")  
    ending_stream(state['live_url']) 
    state['exit_flag'] = True; return  

def switch_stream_config(
        Timer=None
        ):  
    PART['partnumber'] += 1  
    PART[f"part{PART['partnumber']}"] = state["live_url"]  
    if state['reason'] == "Null": 
        reason = f"[Reason of switching is unknown(Part{PART["partnumber"]+1} is on https://youtube.com/watch?v={state['spare_link']})]" 
    else:
        reason = f"[Reason of switching is {state['reason']}(Part{PART["partnumber"]+1} is on https://youtube.com/watch?v={state['spare_link']})]" 
    api_create_edit_schedule(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], reason) 
    if TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking'] and CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None:  
        logging.info("476 - Updating stream description to mark the end of the stream...DESCANDCAT")
        def DESCRIPTION_thread():
            api_create_edit_schedule(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "DESCANDCAT")
            restart_title_arg()
            restart_category_arg()
            TITLE["currentnumber"] +=1
            TITLE[f"part0"] = state["latest_cleantitle"]
            stream = get_twitch_streams()
            CATEGORY["currentnumber"] +=1
            CATEGORY[f"part0"] = stream[0]['game_name']
        threading.Thread(
            target=DESCRIPTION_thread,
            daemon=False
        ).start()
    elif TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and state['gmail_checking']:  
        logging.info("476 - Updating stream description to mark the end of the stream...DESCRIPTION")
        def DESCRIPTION_thread():
            api_create_edit_schedule(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "DESCRIPTION")
            restart_title_arg()
            TITLE["currentnumber"] +=1
            TITLE[f"part0"] = state["latest_cleantitle"]
        threading.Thread(
            target=DESCRIPTION_thread,
            daemon=False
        ).start()
    elif CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None:  
        logging.info("476 - Updating stream description to mark the end of the stream...CATEGORY")
        def DESCRIPTION_thread():
            api_create_edit_schedule(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], None, "CATEGORY")
            restart_category_arg()
            stream = get_twitch_streams()
            CATEGORY["currentnumber"] +=1
            CATEGORY[f"part0"] = stream[0]['game_name']
        threading.Thread(
            target=DESCRIPTION_thread,
            daemon=False
        ).start()
    gotten_title = api_create_edit_schedule(PART["partnumber"]+1, state['rtmp_server'], False, state['spare_link'])  
    if state['rtmp_server'] == "bkrtmp": 
        state['rtmp_server'] = "defrtmp" 
    else:
        state['rtmp_server'] = "bkrtmp" 
    live_spare_url = api_create_edit_schedule(0, state['rtmp_server'], True, "Null")  
    if config.unliststream:  
        share_settings_api(state['live_url'], "public")
    if Timer is None:  
        state["restart_timer"] = True  
    if config.unliststream and config.public_notification:
        logging.info("476 - new stream back to unlisted") 
        share_settings_api(state['spare_link'], "unlisted")
    logging.info("476 - ending the old stream...")  
    ending_stream(state['live_url'])
    state['titleforgmail'] = gotten_title 
    state['live_url'] = state['spare_link']  
    state['spare_link'] = live_spare_url  
    state['reason'] = "Null" 

def share_settings_api(live_id, share):  
    hitryagain = 0  
    while True:  
        try:
            service = get_service()  
            request = service.videos().update(  
                part='status', 
                body={ 
                    'id': live_id,  
                    'status': { 
                    'privacyStatus': share  
                    } 
                } 
            ) 
            response = request.execute()  
            return response['id']  
        except Exception as e:  
            if 'quotaExceeded' in str(e):  
                logging.info(f"517 - API quota exceeded, skipping execution to avoid further errors")  
                return False
            if hitryagain == 3:  
                logging.info(f"517 - Error and stoping because of error that can't fix {e}")  
                return False
            hitryagain += 1  
            time.sleep(5)  

def is_youtube_livestream_live(video_id):  
    TRY = 0 
    while True:  
        try:
            streams = streamlink.streams(f"https://youtube.com/watch?v={video_id}")  
            hls_stream = streams["best"]  
            return True  
        except KeyError as e:  
            TRY += 1 
            time.sleep(5)
            if TRY == 3: 
                logging.info(f"544 - try 3 times is still offline")  
                return False  
        except Exception as e:  
            logging.error(f"544 - Error checking YouTube livestream status: {e}")  
            return "ERROR"  

def refresh_stream_title():  
    while not state['ending']:
        try:
            twitch_title = get_twitch_stream_title(True)  
            newtitle = ' '.join(twitch_title.split()).replace("<", "").replace(">", "")  
            if DEBUG["change_something_title"] is not None:
                logging.info("561 - DEBUG mode active - changing title to debug value")
                newtitle = DEBUG["change_something_title"]
            if newtitle and newtitle[0] == " ": 
                newtitle = newtitle[1:] 
            if state["latest_cleantitle"] != newtitle:  
                logging.info(f"561 - Title discrepancy detected: {state["latest_cleantitle"]} does not match {newtitle}")  
                while state['thread_in_use']: 
                    time.sleep(1)  
                state['thread_in_use'] = True 
                state['titleforgmail'] = api_create_edit_schedule(PART["partnumber"]+1, state['rtmp_server'], "EDIT", state['live_url'], None, False, None, newtitle)  
                state['thread_in_use'] = False 
                TITLE["currentnumber"] += 1
                TITLE[f"part{TITLE["currentnumber"]}"] = newtitle
                logging.info("561 - edit finished continue the stream")  
                if state["latest_cleantitle"] != newtitle: 
                    logging.error(f"561 - Title discrepancy still exists after edit: {newtitle} does not match {state["latest_cleantitle"]}") 
                    logging.info("561 - Stopping immediately due to persistent title discrepancy") 
                    state['gmail_checking'] = False 
                    break 
                time.sleep(180)  
            else: 
                time.sleep(180) 
        except UnboundLocalError as e:  
                logging.warning(f"561 - Encountered UnboundLocalError when getting title: {str(e)} - disabling gmail checking and title checking continue at your own risk")  
                state['gmail_checking'] = False 
                break 
        except Exception as e:  
                logging.error(f"561 - Error getting stream title: {str(e)} - disabling gmail checking and title checking continue at your own risk")  
                state['gmail_checking'] = False 
                break 
    logging.info("561 - refresh stream title has stopped")  

def refresh_stream_category():
    TRY = 0
    sleeping = False
    while not state['ending']:
        try:
            stream = get_twitch_streams()
            twitch_category = stream[0]['game_name']
            if DEBUG["change_something_cat"] is not None:
                logging.info("579 - DEBUG mode active - changing category to debug value")
                twitch_category = DEBUG["change_something_cat"]
            if CATEGORY['currentnumber'] == -1 and CATEGORY["part0"] is None:
                CATEGORY['currentnumber'] += 1
                CATEGORY["part0"] = twitch_category
            if CATEGORY[f"part{CATEGORY['currentnumber']}"] != twitch_category:
                if twitch_category == "I'm Only Sleeping" and config.subathon == True and not sleeping:
                    logging.info("579 - Detected 'I'm Only Sleeping' category with subathon enabled - switching streams immediately")
                    while state['thread_in_use']:
                        time.sleep(1)
                    state['thread_in_use'] = True
                    state['reason'] = "Detected catetgory switch to 'I'm Only Sleeping'" 
                    switch_stream_config()
                    state['thread_in_use'] = False
                    sleeping = True
                elif sleeping and config.subathon == True:
                    logging.info("579 - Woke up from 'I'm Only Sleeping' category with subathon enabled - switching streams immediately")
                    while state['thread_in_use']:
                        time.sleep(1)
                    state['thread_in_use'] = True
                    state['reason'] = "Woke up from 'I'm Only Sleeping' category" 
                    switch_stream_config()
                    state['thread_in_use'] = False
                    sleeping = False
                else:
                    logging.info(f"579 - Category discrepancy detected: {CATEGORY[f'part{CATEGORY['currentnumber']}']} does not match {twitch_category}")
                    CATEGORY['currentnumber'] += 1
                    CATEGORY[f"part{CATEGORY['currentnumber']}"] = twitch_category
                    while state['thread_in_use']:
                        time.sleep(1)
                    state['thread_in_use'] = True
                    api_create_edit_schedule(PART["partnumber"]+1, state['rtmp_server'], "EDIT", state['live_url'])
                    state['thread_in_use'] = False
                    logging.info("579 - Category edit finished, continuing the stream")
            time.sleep(180)  
        except Exception as e:  
                state['thread_in_use'] = False
                logging.error(f"579 - Error getting stream category: {str(e)}")  
                time.sleep(300)
    logging.info("579 - refresh stream category has stopped")

def find_thrid_party_notification():  
    detect_times = 0 
    first_time = None 
    service = get_gmail_service()  
    while state['gmail_checking'] and not state['ending']:  
        try: 
            title = state['titleforgmail']  
            now = datetime.now()  
            minutes_ago = now - timedelta(minutes=2)  
            results = service.users().messages().list(userId='me', maxResults=2).execute()  
            messages = results.get('messages', [])  
            if messages:  
                for message in messages:  
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()  
                    received_time = datetime.fromtimestamp(int(msg['internalDate']) / 1000)  
                    subject = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), '')  
                    sender = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from'), '')  
                    if received_time >= minutes_ago and title in subject and ("no-reply@youtube.com" in sender):  
                        logging.info(f"596 - Found email from YouTube: {subject}")  
                        while state['thread_in_use']: 
                            time.sleep(1)  
                        state['thread_in_use'] = True 
                        logging.info("596 - Third-party notification detected - switching to backup stream...")  
                        if detect_times == 0: 
                            first_time = time.time() 
                        if detect_times >= 3 and (time.time() - first_time) <= 2100: 
                            logging.info("596 - Three notifications detected within 35 mins - stopping restreaming and stop running")  
                            reason = "Third-party notification detected 3 times in 35 minutes, the stream is stopped to avoid further issues."
                            api_create_edit_schedule(PART["partnumber"], state['rtmp_server'], "EDIT", state['live_url'], reason) 
                            handle_stream_offline(True) 
                            state['thread_in_use'] = False 
                            break 
                        if detect_times >= 3: 
                            detect_times = 0
                            first_time = time.time() 
                        state['reason'] = "Third-party notification detected" 
                        switch_stream_config()  
                        state['thread_in_use'] = False 
                        detect_times += 1 
            time.sleep(40) 
        except Exception as e:  
            logging.error(f"596 - Error in find_gmail_title: {e}")  
            state['thread_in_use'] = False 
            time.sleep(180)  
    logging.info("596 - find gmail title has stopped")  

def hours_checker(): 
    while not state['ending']: 
        for _ in range(4122):
            if state['restart_timer']:  
                state['restart_timer'] = False  
                logging.info("642 - Restart timer detected - resetting 12-hour timer...")  
                hours_checker()
                break  
            time.sleep(10)  
        logging.info("642 - Stream duration limit near 12h reached - initiating scheduled reload...")  
        while state['thread_in_use']: 
            time.sleep(1)  
        state['thread_in_use'] = True 
        state['reason'] = "stream duration limit near 12h reached" 
        switch_stream_config(True)  
        state['thread_in_use'] = False 
    logging.info("642 - hours checker has stopped")  
    
def handle_user_input(): 
    logging.info("660 - DEBUG MODE IS ENABLE YOU CAN ONLY EXIT OR FORCE OFFINE OR STATE OR FORCE SWITCH")
    print("> ", end='', flush=True)
    user_input = ""
    while not state['ending']:
        if state['ending']:
            print("\nStatus changed - stopping debug mode")
            break
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char == '\r':  
                print()
                if user_input.strip().upper() == "EXIT":
                    logging.info("660 - Terminating script...")
                    state['exit_flag'] = True; return  
                #elif user_input == "REFRESH":
                    #logging.info("REFRESH EXIT AND CREATE NEW CMD") 
                    #if state['rtmp_server'] == "defrtmp": 
                        #rtmp = "bkrtmp" 
                    #else: 
                        #rtmp = "defrtmp" 
                    #subprocess.Popen(["start", "cmd" , "/c", "py", "check_tv.py", state['live_url'], rtmp, state['spare_link']], shell=True)  
                    #state['exit_flag'] = True; return  
                elif user_input == "STOP":
                    break
                elif user_input == "FORCE OFFLINE":
                    logging.info("660 - FORCE OFFLINE COMMAND DETECTED")
                    while state['thread_in_use']: 
                        time.sleep(1)  
                    state['thread_in_use'] = True 
                    handle_stream_offline("DEBUG") 
                    state['thread_in_use'] = False
                    break
                elif user_input == "STATE":
                    logging.info(f"660 - Current STATE: {state}\n")
                    logging.info(f"660 - Current PART: {PART}\n")
                    logging.info(f"660 - Current TITLE: {TITLE}\n")
                    logging.info(f"660 - Current CATEGORY: {CATEGORY}\n")
                    logging.info(f"660 - Current DEBUG: {DEBUG}\n")
                    logging.info(f"660 - Current STREAM STATE: {stream_state}\n")
                    logging.info(f"660 - Current DESCRIPTION: {DESCRIPTION}\n")
                    user_input = ""
                    print("> ", end='', flush=True)
                elif user_input == "FORCE SWITCH":
                    logging.info("660 - FORCE SWITCH COMMAND DETECTED")
                    while state['thread_in_use']: 
                        time.sleep(1)  
                    state['thread_in_use'] = True 
                    state['reason'] = "force switch command detected" 
                    switch_stream_config()  
                    state['thread_in_use'] = False
                    user_input = ""
                    print("> ", end='', flush=True)
                elif user_input.startswith("CHANGE CAT TO"):
                    new_cat = user_input.replace("CHANGE CAT TO ", "").strip()
                    logging.info(f"660 - CHANGE CAT TO COMMAND DETECTED - changing category to {new_cat}")
                    if new_cat == "None":
                        DEBUG["change_something_cat"] = None
                    else:
                        DEBUG["change_something_cat"] = new_cat
                    user_input = ""
                    print("> ", end='', flush=True)
                elif user_input.startswith("CHANGE TITLE TO"):
                    new_title = user_input.replace("CHANGE TITLE TO ", "").strip()
                    logging.info(f"660 - CHANGE TITLE TO COMMAND DETECTED - changing title to {new_title}")
                    if new_title == "None":
                        DEBUG["change_something_title"] = None
                    else:
                        DEBUG["change_something_title"] = new_title
                    user_input = ""
                    print("> ", end='', flush=True)
                else:
                    user_input = ""
                    print("> ", end='', flush=True)
            elif char == '\b':  
                if user_input:
                    user_input = user_input[:-1]
                    print('\b \b', end='', flush=True)
            else:
                user_input += char
                print(char, end='', flush=True)
        time.sleep(0.1)
    while msvcrt.kbhit():
        msvcrt.getwch()
    logging.info("660 - handle user input has stopped")

def handle_input(status, live_url, rtmp_server):
    logging.info("726 - DEBUG MODE [Valid commands: EXIT, REFRESH, STOP]:")
    print("> ", end='', flush=True)
    user_input = ""
    while not status['status']:
        if status['status']:
            logging.info("726 - Status changed - stopping debug mode")
            break
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char == '\r':  
                print()
                if user_input.strip().upper() == "EXIT":
                    logging.info("726 - Terminating script...")
                    psutil.Process(os.getpid()).terminate()
                elif user_input == "REFRESH":
                    logging.info("726 - Starting new process...")
                    cmd = ["start", "cmd" , "/c", "py", "check_tv.py", live_url, rtmp_server]
                    subprocess.Popen(cmd, shell=True)
                    logging.info("726 - Terminating current process...")
                    psutil.Process(os.getpid()).terminate()
                elif user_input == "STOP":
                    break
                else:
                    user_input = ""
                    print("> ", end='', flush=True)
            elif char == '\b':  
                if user_input:
                    user_input = user_input[:-1]
                    print('\b \b', end='', flush=True)
            else:
                user_input += char
                print(char, end='', flush=True)
        time.sleep(0.1)
    while msvcrt.kbhit():
        msvcrt.getwch()
    logging.info("726 - handle user input has stopped")

def get_twitch_streams():  
    ERROR = 0 
    while True: 
        try: 
            try: 
                token_response = requests.post(token_url, timeout=10)  
                token_response.raise_for_status()  
                token_data = token_response.json()  
                access_token = token_data.get('access_token')  
                if not access_token:  
                    logging.info("764 - Access token not found in response") 
                    return "ERROR" 
            except requests.exceptions.ConnectionError as e: 
                ERROR += 1 
                if ERROR == 3: 
                    logging.error(f"764 - No internet connection or connection error: {e}") 
                    return "ERROR" 
            except requests.exceptions.Timeout as e: 
                ERROR += 1 
                if ERROR == 3: 
                    logging.error(f"764 - Request timed out: {e}") 
                    return "ERROR" 
            except requests.exceptions.RequestException as e:  
                ERROR += 1 
                if ERROR == 3: 
                    logging.error(f"764 - Error obtaining Twitch access token: {e}") 
                    return "ERROR" 
            except ValueError as ve: 
                ERROR += 1 
                if ERROR == 3: 
                    logging.error(f"764 - Error in response data: {ve}")  
                    return "ERROR" 
            headers = {'Authorization': f'Bearer {access_token}', 'Client-ID': config.client_id}  
            streams_response = requests.get(f'https://api.twitch.tv/helix/streams?user_login={config.username}', headers=headers, timeout=10)  
            streams_data = streams_response.json()  
            if streams_response.status_code == 401 and streams_data.get('message') == 'Invalid OAuth token': 
                logging.error("764 - Invalid OAuth token: Unauthorized access to Twitch API (Normal Error Sometimes)") 
                ERROR += 1 
                if ERROR == 3: 
                    logging.info("764 - 3 times Invalid OAuth token: NOT SO NORMAL") 
                    return "ERROR" 
            elif 'data' not in streams_data: 
                logging.error("764 - 'data' key not found in Twitch API response")  
                logging.error(f"764 - Invalid Twitch API response: {streams_data}") 
                ERROR += 1 
                if ERROR == 3: 
                    logging.info(f"764 - 3 times invalid Twitch API response: {streams_data}") 
                    return "ERROR" 
            else: 
                return streams_data['data']  
        except Exception as e:  
            logging.error(f"764 - Error fetching Twitch stream data: {e}")  
            ERROR += 1 
            if ERROR == 3: 
                logging.info("764 - 3 times General Error: NOT NORMAL") 
                return "ERROR" 
    

def get_twitch_stream_title(refresh=False):  
    MAX_RETRIES = 3 
    RETRY_DELAY = 5 
    for attempt in range(MAX_RETRIES):  
        try: 
            streams = get_twitch_streams()  
            if not streams or streams == "ERROR":  
                logging.error("826 - Error API, returning fallback title")  
                logging.error(f"826 - Streams data: {streams}")
                if refresh:
                    return state["latest_cleantitle"]
                else:
                    return f"Stream_{datetime.now().strftime('%Y-%m-%d')}" 
            if streams:  
                return streams[0]['title']
        except Exception as e: 
            logging.error(f"826 - Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}")  
            if attempt < MAX_RETRIES - 1:  
                time.sleep(RETRY_DELAY) 
            else: 
                logging.error("826 - Max retries reached, returning fallback title")  
                if refresh:
                    return state["latest_cleantitle"]
                else:
                    return f"Stream_{datetime.now().strftime('%Y-%m-%d')}"   

def check_process_running():  
    process_name = "countdriver.exe"  
    logging.info("852 - Checking for existing browser automation processes...")  
    while True:
        if any(process.info['name'] == process_name for process in psutil.process_iter(['pid', 'name'])):  
                logging.info("852 - Browser automation process already running - waiting for completion...")  
                time.sleep(15)  
        else:
            logging.info("852 - No conflicting processes found - proceeding...")  
            break  
    return 

def get_service():  
    creds = None  
    from google_auth_oauthlib.flow import InstalledAppFlow  
    try: 
        if os.path.exists(USER_TOKEN_FILE):  
            if not config.brandacc:  
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  
            if config.brandacc:  
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES_BRAND)  
        if not creds or not creds.valid:  
            if creds and creds.expired and creds.refresh_token:  
                creds.refresh(Request())  
            else: 
                if not config.brandacc:  
                    logging.info("864 - Token not found or invalid. Starting authentication flow...")  
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  
                if config.brandacc:  
                    logging.info("864 - YouTube token not found or invalid. Starting authentication flow...")  
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                    creds = flow.run_local_server(port=6971, brandacc="havebrand")  
                with open(USER_TOKEN_FILE, 'w') as token:  
                    token.write(creds.to_json())  
        return build('youtube', 'v3', credentials=creds)  
    except Exception as e:  
        if "invalid_grant" in str(e):  
            if not config.brandacc:  
                logging.info("864 - Token not found or invalid. Starting authentication flow...")  
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                creds = flow.run_local_server(port=6971, brandacc="Nope")  
            if config.brandacc:  
                logging.info("864 - YouTube token not found or invalid. Starting authentication flow...")  
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                creds = flow.run_local_server(port=6971, brandacc="havebrand")  
            with open(USER_TOKEN_FILE, 'w') as token:  
                token.write(creds.to_json())  
            return build('youtube', 'v3', credentials=creds)  
        else: 
            logging.error(f"864 - Error in get_service: {e}")  
            exit(1)  

def get_gmail_service():  
    creds = None  
    from google_auth_oauthlib.flow import InstalledAppFlow 
    try: 
        if config.brandacc:  
            if os.path.exists(GMAIL_TOKEN_FILE):  
                creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES_GMAIL)  
        if not config.brandacc:  
            if os.path.exists(USER_TOKEN_FILE):  
                creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)  
        if not creds or not creds.valid:  
            if creds and creds.expired and creds.refresh_token:  
                creds.refresh(Request())  
            else: 
                if config.brandacc:  
                    logging.info("905 - Gmail token not found or invalid. Starting authentication flow...")  
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  
                    with open(GMAIL_TOKEN_FILE, 'w') as token:  
                        token.write(creds.to_json())  
                if not config.brandacc:  
                    logging.info("905 - Token not found or invalid. Starting authentication flow...")  
                    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                    creds = flow.run_local_server(port=6971, brandacc="Nope")  
                    with open(USER_TOKEN_FILE, 'w') as token:  
                        token.write(creds.to_json())  
        return build('gmail', 'v1', credentials=creds)  
    except Exception as e:  
        if "invalid_grant" in str(e):  
            if config.brandacc:  
                logging.info("905 - Gmail token not found or invalid. Starting authentication flow...")  
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                creds = flow.run_local_server(port=6971, brandacc="Nope")  
                with open(GMAIL_TOKEN_FILE, 'w') as token:  
                    token.write(creds.to_json())  
            if not config.brandacc:  
                logging.info("905 - Token not found or invalid. Starting authentication flow...")  
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')  
                creds = flow.run_local_server(port=6971, brandacc="Nope")  
                with open(USER_TOKEN_FILE, 'w') as token:  
                    token.write(creds.to_json())  
            return build('gmail', 'v1', credentials=creds)  
        else: 
            logging.error(f"905 - Error in get_gmail_service: {e}")  
            exit(1)  

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
        logging.info(f"966 - Downloading font for script: {script}") 
        urllib.request.urlretrieve(font_info['url'], font_path) 
    return font_path 

def create_thumbnail( 
    title 
    ): 
    try: 
        width, height = 1280, 720 
        background_color = (20, 20, 20)  
        image = Image.new('RGB', (width, height), background_color) 
        draw = ImageDraw.Draw(image) 
        font_path = ensure_font_for_text(title) 
        max_title_width = width - 100  
        font_size = 60 
        try: 
            title_font = ImageFont.truetype(font_path, font_size) 
        except: 
            title_font = ImageFont.load_default() 

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
        title_block_height = 0 
        line_heights = [] 
        for line in title_lines: 
            bbox = draw.textbbox((0, 0), line, font=title_font) 
            h = bbox[3] - bbox[1] 
            title_block_height += h + 10 
            line_heights.append(h) 
        title_block_height -= 10 
        try: 
            subtitle_font = ImageFont.truetype(font_path, 40) 
        except: 
            subtitle_font = ImageFont.load_default() 
        archive_text = f"VOD of {config.username}" 
        archive_bbox = draw.textbbox((0, 0), archive_text, font=subtitle_font) 
        archive_h = archive_bbox[3] - archive_bbox[1] 
        show_title = len(title_lines) <= 3 
        if show_title: 
            block_height = title_block_height + 30 + archive_h 
            block_y = (height - block_height) // 2 
            y = block_y 
            for i, line in enumerate(title_lines): 
                bbox = draw.textbbox((0, 0), line, font=title_font) 
                w = bbox[2] - bbox[0] 
                h = bbox[3] - bbox[1] 
                x = (width - w) // 2 
                draw.text((x, y), line, fill=(255, 255, 255), font=title_font) 
                y += h + 10 
            archive_w = archive_bbox[2] - archive_bbox[0] 
            archive_x = (width - archive_w) // 2 
            draw.text((archive_x, y + 20), archive_text, fill=(200, 200, 200), font=subtitle_font) 
        else: 
            archive_w = archive_bbox[2] - archive_bbox[0] 
            archive_x = (width - archive_w) // 2 
            archive_y = (height - archive_h) // 2 
            draw.text((archive_x, archive_y), archive_text, fill=(200, 200, 200), font=subtitle_font) 
        logo_size = (200, 200) 
        try: 
            logo = Image.open("channel_logo.png") 
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS) 
            image.paste(logo, (50, 50), logo if logo.mode == 'RGBA' else None) 
        except: 
            logging.info("977 - No channel logo found, continuing without it") 
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
        thumbnail_path = "stream_thumbnail.jpg" 
        image.save(thumbnail_path, "JPEG", quality=95) 
        return thumbnail_path 
    except Exception as e: 
        logging.error(f"977 - Error creating thumbnail: {e}") 
        return None 

def edit_live_stream( 
    video_id, 
    new_title, 
    new_description 
    ):  
    hitryagain = 0 
    while True: 
        try: 
            service = get_service() 
            category_id = '24' 
            request = service.videos().update( 
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
            response = request.execute() 
            if config.thumbnail: 
                thumbnail_path = create_thumbnail(new_title) 
                if thumbnail_path and os.path.exists(thumbnail_path): 
                    try: 
                        service.thumbnails().set( 
                           videoId=video_id, 
                           media_body=thumbnail_path 
                           ).execute() 
                        logging.info("1070 - Successfully set custom thumbnail") 
                        os.remove(thumbnail_path) 
                        logging.info("1070 - Thumbnail file removed after upload") 
                    except Exception as e: 
                        logging.error(f"1070 - Failed to set thumbnail: {e}") 
                        if os.path.exists(thumbnail_path): 
                            os.remove(thumbnail_path) 
            else: 
                pass
            return response['id'] 
        except Exception as e: 
            if hitryagain >= 3: 
                logging.info(f"1070 - Error and stoping because of error that can't fix") 
                return False 
            if 'The request metadata specifies an invalid or empty video title.' in str(e): 
                logging.info(f"1070 - Use default title because of invalid title: {new_title}") 
                new_title = datetime.now().strftime("Stream_%Y-%m-%d %H:%M:%S") 
            if 'quotaExceeded' in str(e): 
                logging.info(f"1070 - Error and stoping because of api limited") 
                psutil.Process(os.getpid()).terminate() 
            hitryagain += 1 
            logging.info(f"1070 - Error: {e}") 
            time.sleep(5) 

def get_youtube_stream_title(
    video_id
    ):
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
            return "ERROR GETTING TITLE SORRY" 
        except Exception as e: 
            if 'quotaExceeded' in str(e): 
                logging.info(f"1124 - Error and stoping because of api limited") 
                return False 
            if try_count == 3: 
                logging.info(f"1124 - Error and stoping because of error that can't fix") 
                return False 
            try_count += 1 
            logging.info(f"1124 - Error: {e}") 
            time.sleep(5) 

def create_live_stream( 
    title, 
    description, 
    kmself 
    ):  
    hitryagain = 0 
    while True: 
        try: 
            service = get_service() 
            scheduled_start_time = datetime.now(timezone.utc).isoformat() 
            request = service.liveBroadcasts().insert( 
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
                        "enableAutoStop": False, 
                        "latencyPrecision": "ultraLow" 
                    }
                }
            )
            response = request.execute() 
            video_id = response['id'] 
            if not config.playlist_id0 == "Null": 
                try: 
                    playlist_request = service.playlistItems().insert( 
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
                    playlist_request.execute() 
                except Exception as playlist_error: 
                    logging.error(f"1150 - Failed to add video to playlist: {playlist_error}") 
            if not config.playlist_id0 == "Null" and not config.playlist_id1 == "Null": 
                try: 
                    playlist_request = service.playlistItems().insert( 
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
                    playlist_request.execute() 
                except Exception as playlist_error: 
                    logging.error(f"1150 - Failed to add video to playlist: {playlist_error}") 
            return video_id 
        except Exception as e: 
            if 'quotaExceeded' in str(e): 
                logging.info(f"1070 - Error and stoping because of api limited") 
                psutil.Process(os.getpid()).terminate() 
            if hitryagain == 3: 
                logging.info(f"1070 - Error and stoping because of error that can't fix") 
                psutil.Process(os.getpid()).terminate() 
            hitryagain += 1 
            logging.info(f"1070 - Error: {e}") 
            time.sleep(5) 

def api_load( 
    url, 
    brandacc 
    ):  
    from logger_config import check_tv_logger as logging 
    logging.info("1227 - create api keying ---edit_tv---") 
    home_dir = os.path.expanduser("~")  
    logging.info("1227 - run with countdriver.exe and check") 
    check_process_running() 
    subprocess.Popen(["start", "countdriver.exe"], shell=True) 
    options = Options() 
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data") 
    options.add_argument(f"user-data-dir={chrome_user_data_dir}") 
    options.add_argument(f"profile-directory={config.Chrome_Profile}") 
    driver = webdriver.Chrome(options=options) 
    driver.get(url) 
    time.sleep(3) 
    if brandacc == "Nope":
        nameofaccount = f"//div[contains(text(),'{config.accountname}')]" 
    else: 
        nameofaccount = f"//div[contains(text(),'{config.brandaccname}')]" 
    driver.find_element("xpath", nameofaccount).click() 
    time.sleep(3) 
    try:
        driver.find_element("xpath", "//*[@id='submit_approve_access']/div/button/div[3]").click() 
    except:
        try:
            driver.find_element("xpath", "//*[@id='yDmH0d']/div[1]/div[1]/div[2]/div/div/div[3]/div/div[2]").click() 
            time.sleep(2) 
            driver.find_element("xpath", "//*[@id='yDmH0d']/div[1]/div[1]/div[2]/div/div/div[3]/div/div/div[2]").click()
        except:
            driver.find_element("xpath", "//*[@id='yDmH0d']/div[1]/div[1]/div[2]/div/div/div[3]/div/div/div[2]").click() 
            time.sleep(2) 
    while True:
        try:
            current_url = driver.current_url
            if "localhost" in current_url:
                break
            time.sleep(1)
        except:
            time.sleep(1)
    driver.quit() 
    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) 
    logging.info("1227 - finish idk ---edit_tv---") 

def check_is_live_api( 
    url, 
    ffmpeg, 
    rtmp_server 
    ):  
    logging.info("1272 - Waiting for 40sec live on YouTube") 
    time.sleep(40) 
    new_url = f"https://youtube.com/watch?v={url}" 
    count_error = 0 
    MAX_RETRIES = 3 
    if rtmp_server == "defrtmp": 
        text = "this" 
    else: 
        text = "api_this" 
    while True: 
        try: 
            streams = streamlink.streams(new_url) 
            hls_stream = streams["best"] 
            logging.info('1272 - It is live now') 
            break 
        except KeyError as e: 
            logging.error(f'1272 - Stream not available: {str(e)}') 
            logging.info('1272 - The stream is messed up. Trying again...') 
            time.sleep(2) 
            stream_state["stop_right_now"] = True 
            subprocess.run(["taskkill", "/f", "/im", ffmpeg]) 
            threading.Thread(target=start_restreaming, args=(text, url), daemon=False).start()
            time.sleep(35) 
            count_error += 1 
        if count_error >= MAX_RETRIES: 
            logging.info("1272 - Retry limit exceeded. Shutting down.") 
            os.system("start check_tv.py KILL")
            psutil.Process(os.getpid()).terminate() 

def api_create_edit_schedule( 
    part_number, 
    rtmp_server, 
    is_reload, 
    stream_url, 
    reason=None, 
    finish_title=False,
    filename=None,
    clean_title=None,
    ):  
    if config.StreamerName == "Null": 
        username = config.username 
    else: 
        username = config.StreamerName 
    TESTING = "[TESTING WILL BE REMOVE AFTER]" if config.exp_tesing else "" 
    if not is_reload or is_reload == "EDIT" or is_reload == "PREVDECRIPTION" or is_reload == "PREVCATEGORY" or is_reload == "PREVDESCANDCAT": 
        if not finish_title:  
            if filename is None:
                if config.category:
                    stream = get_twitch_streams()
                    category = stream[0]['game_name']
                if clean_title is None:
                    stream_title = get_twitch_stream_title() 
                    clean_title = ' '.join(stream_title.split()).replace("<", "").replace(">", "")  
                    if clean_title and clean_title[0] == " ": 
                        clean_title = clean_title[1:] 
                state["latest_cleantitle"] = clean_title
                part_suffix = f"PART{part_number}" if part_number > 0 else "PART0" 
                if part_number > 0:
                    filename = f"{username} | {part_suffix} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}" 
                else:
                    filename = f"{username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}" 
                if len(filename) > 100: 
                    if part_number > 0:
                        max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 3) - len(part_suffix) - len(TESTING) 
                    else:
                        max_title_len = 100 - len(username) - len(datetime.now().strftime('%Y-%m-%d')) - len(" | " * 2) - len(TESTING)
                    clean1_title = clean_title[:max_title_len-3] + "..." 
                    if part_number > 0:
                        filename = f"{username} | {part_suffix} | {clean1_title} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}" 
                    else:
                        filename = f"{username} | {clean1_title} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}" 
                if len(filename) > 100: 
                    if part_number > 0:
                        filename = f"{username} | {part_suffix} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}"
                    else:
                        filename = f"{username} | {datetime.now().strftime('%Y-%m-%d')}{TESTING}" 
            ITISUNLISTED = "[THIS RESTREAMING PROCESS IS DONE UNLISTED]" if config.unliststream else "" 
            reason_description = f"""
{reason}""" if reason is not None else "" 
            category_description = f"""
[Current Category: {category}]""" if config.category else ""
            Twitch_sub_or_turbo = "[AD-FREE: SUB/TURBO]" if config.brought_twitch_sub_or_turbo else "[ADS INCLUDE WILL AFFECT THE VIEWING EXPERIENCE]" 
            description = f"""{TESTING}{ITISUNLISTED}{Twitch_sub_or_turbo}
Original broadcast from https://twitch.tv/{config.username} {reason_description}
[Stream Title: {clean_title}] {category_description}
More info: https://linktr.ee/karstenlee
Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee
Twitch Stream to YouTube Script Version: {script_version}
{config.tags_for_youtube}""" 
            DESCRIPTION["description_first"] = f"""{TESTING}{ITISUNLISTED}{Twitch_sub_or_turbo}
Original broadcast from https://twitch.tv/{config.username} {reason_description}""" 
            DESCRIPTION["description_second"] = f"""[Stream Title: {clean_title}] {category_description}
More info: https://linktr.ee/karstenlee
Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee
Twitch Stream to YouTube Script Version: {script_version}
{config.tags_for_youtube}""" 
        if finish_title == "PARTLIST" or finish_title == "PARTANDDESC" or finish_title == "PARTANDCAT" or finish_title == "ALL": 
            try:
                part_links = []
                current_part = PART["partnumber"] 
                while current_part >= 0:
                    part_key = f"part{current_part}"
                    if part_key in PART:
                        part_links.append(f"PART{current_part}: https://youtube.com/watch?v={PART[part_key]}")
                    current_part -= 1
                parts_section = "\n".join(part_links)
                part_list_description = f"PART LIST(THIS IS THE LAST PART OF THE STREAM):\n{parts_section}"
                if finish_title == "PARTLIST":
                    description = f"{DESCRIPTION['description_first']}\n=====\n{part_list_description}\n=====\n{DESCRIPTION['description_second']}"
            except Exception as e:
                logging.error(f"1306 - Error building part list description: {str(e)}")
                part_list_description = ""
            filename = state['titleforgmail']
        if finish_title == "DESCRIPTION" or finish_title == "DESCANDCAT" or finish_title == "PARTANDDESC" or finish_title == "ALL" or is_reload == "PREVDECRIPTION" or is_reload == "PREVDESCANDCAT":
            try:
                part_links = []
                current_part = TITLE["currentnumber"]
                while current_part >= 0:
                    part_key = f"part{current_part}"
                    if part_key in TITLE:
                        part_links.append(f"Ver.{current_part}: {TITLE[part_key]}")
                    current_part -= 1
                parts_section = "\n".join(part_links)
                DESCRIPTION_list_description = f"TITLE CHANGE LIST:\n{parts_section}"
                if finish_title == "DESCRIPTION" or is_reload == "PREVDECRIPTION" or is_reload == "PREVDESCANDCAT":
                    description = f"{DESCRIPTION['description_first']}\n=====\n{DESCRIPTION_list_description}\n=====\n{DESCRIPTION['description_second']}"
            except Exception as e:
                logging.error(f"1306 - Error building title change list: {str(e)}")
                DESCRIPTION_list_description = ""
            if is_reload == "PREVDECRIPTION" or is_reload == "PREVDESCANDCAT":
                pass
            else:
                filename = state['titleforgmail']
        if finish_title == "CATEGORY" or finish_title == "PARTANDCAT" or finish_title == "DESCANDCAT" or finish_title == "ALL" or is_reload == "PREVDESCANDCAT" or is_reload == "PREVCATEGORY":
            try:
                part_links = []
                current_part = CATEGORY["currentnumber"]
                while current_part >= 0:
                    part_key = f"part{current_part}"
                    if part_key in CATEGORY:
                        part_links.append(f"Ver.{current_part}: {CATEGORY[part_key]}")
                    current_part -= 1
                parts_section = "\n".join(part_links)
                CATEGORY_list_description = f"CATEGORY CHANGE LIST:\n{parts_section}"
                if finish_title == "CATEGORY" or is_reload == "PREVDESCANDCAT" or is_reload == "PREVCATEGORY":
                    description = f"{DESCRIPTION['description_first']}\n=====\n{CATEGORY_list_description}\n=====\n{DESCRIPTION['description_second']}"
            except Exception as e:
                logging.error(f"1306 - Error building title change list: {str(e)}")
                CATEGORY_list_description = ""
            if is_reload == "PREVCATEGORY" or is_reload == "PREVDESCANDCAT":
                pass
            else:
                filename = state['titleforgmail']
        if finish_title == "PARTANDDESC":
            description = f"""{DESCRIPTION["description_first"]}\n=====\n{part_list_description}\n=====\n{DESCRIPTION_list_description}\n=====\n{DESCRIPTION["description_second"]}"""
            filename = state['titleforgmail']
        if finish_title == "PARTANDCAT":
            description = f"""{DESCRIPTION["description_first"]}\n=====\n{part_list_description}\n=====\n{CATEGORY_list_description}\n=====\n{DESCRIPTION["description_second"]}"""
            filename = state['titleforgmail']
        if finish_title == "DESCANDCAT" or is_reload == "PREVDESCANDCAT":
            description = f"""{DESCRIPTION["description_first"]}\n=====\n{DESCRIPTION_list_description}\n=====\n{CATEGORY_list_description}\n=====\n{DESCRIPTION["description_second"]}"""
            filename = state['titleforgmail']
        if finish_title == "ALL":
            description = f"""{DESCRIPTION["description_first"]}\n=====\n{part_list_description}\n=====\n{CATEGORY_list_description}\n=====\n{DESCRIPTION_list_description}\n=====\n{DESCRIPTION["description_second"]}"""
            filename = state['titleforgmail']
    try: 
        if is_reload is True: 
            filename = f"{username} (WAITING FOR STREAMER){TESTING}" 
            description = f"""{TESTING}
Waiting for https://twitch.tv/{config.username}
Archived using open-source tools: https://is.gd/archivescript Service by Karsten Lee
More info: https://linktr.ee/karstenlee
Twitch Stream to YouTube Script Version: {script_version}""" 
        if stream_url == "Null": 
            logging.info("1306 - Initiating API request for stream creation...") 
            privacy_status = "public" if not config.unliststream else "unlisted" 
            if config.unliststream and config.public_notification: 
                privacy_status = "public" 
            stream_url = create_live_stream(filename, description, privacy_status) 
            logging.info("1306 - ==================================================") 
            if not config.playlist_id0 == "Null": 
                logging.info(f"1306 - LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0}") 
            elif not config.playlist_id0 == "Null" and not config.playlist_id1 == "Null": 
                logging.info(f"1306 - LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0} AND {config.playlist_id1}") 
            else: 
                logging.info(f"1306 - LIVE STREAM SCHEDULE CREATED: {stream_url}") 
            logging.info("1306 - ==================================================") 
            setup_stream_settings(stream_url, rtmp_server)
        if is_reload == "EDIT" or is_reload == "PREVDECRIPTION" or is_reload == "PREVCATEGORY" or is_reload == "PREVDESCANDCAT": 
            logging.info(f"1306 - Editing existing live stream...")
            edit_live_stream(stream_url, filename, description) 
            return filename 
        if is_reload is True: 
            return stream_url 
        if not is_reload: 
            logging.info(f"1306 - Start stream relay") 
            initialize_stream_relay(stream_url, rtmp_server, filename) 
            edit_live_stream(stream_url, filename, description) 
            return filename 
    except Exception as e: 
        logging.error(f"1306 - Critical error encountered during api_create_edit_schedule: {e}") 
        psutil.Process(os.getpid()).terminate() 

def initialize_stream_relay( 
    stream_url, 
    rtmp_server, 
    filename 
    ):
    if rtmp_server == "defrtmp": 
        rtmp_relive = "this" 
    else: 
        rtmp_relive = "api_this" 
    threading.Thread(target=start_restreaming, args=(rtmp_relive, stream_url), daemon=False).start()
    if rtmp_server == "defrtmp": 
        ffmpeg_1exe = config.ffmpeg1 
    else: 
        ffmpeg_1exe = config.ffmpeg 
    time.sleep(40)
    stream_state["stop_right_now"] = True 
    subprocess.run(["taskkill", "/f", "/im", ffmpeg_1exe]) 
    if rtmp_server == "bkrtmp": 
        rtmp_key = config.rtmp_key 
    else: 
        rtmp_key = config.rtmp_key_1 
    if config.playvideo: 
        os.system(f'start {ffmpeg_1exe} -re -i blackscreen.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}') 

def initialize_and_monitor_stream(): 
    if not check_chrome_version(): 
        logging.info("1474 - Error try fixing your chrome version guide on github") 
        exit() 
    try: 
        yt_link = "Null" 
        rtmp_info = "Null" 
        IFTHEREISMORE = "" 
        THEREISMORE = "Null" 
        bk_yt_link = "Null" 
        prev = False
        arguments = sys.argv 
        if len(arguments) < 2: 
            logging.info("1474 - ==================================================") 
            logging.info(f"1474 - NO ARGUMENT AVAILABLE (Ver.{script_version}) (CONFIG VIEW IN CONFIG_TV.PY)") 
            logging.info(f"1474 - ARCHIVE USER: {config.username}") 
            logging.info("1474 - ==================================================") 
        else: 
            yt_link = arguments[1] 
            if yt_link == "KILL": 
                logging.info("1474 - close all exe") 
                subprocess.run(["taskkill", "/f", "/im", config.ffmpeg]) 
                subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1]) 
                subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) 
                exit(1) 
            rtmp_info = arguments[2] 
            if len(arguments) < 3: 
                logging.error("1474 - Missing required RTMP argument") 
                exit(1) 
            if len(yt_link) != 11: 
                logging.error(f"1474 - Invalid argument for ARG1: {yt_link}. Must be 11 characters long YouTube Video ID") 
                exit(1) 
            if rtmp_info not in ["defrtmp", "bkrtmp"]: 
                logging.error(f"1474 - Invalid argument for ARG2: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'") 
                exit(1) 
            if len(arguments) == 4: 
                bk_yt_link = arguments[3]
                if len(bk_yt_link) != 11: 
                    logging.error(f"1474 - Invalid argument for ARG3: {bk_yt_link}. Must be 11 characters long YouTube Video ID") 
                    exit(1) 
                else:
                    IFTHEREISMORE = f"ARG3: {bk_yt_link}(SKIP CREATING BK STREAM AND RESTORE MONITORING)" 
                    THEREISMORE = True 
            if len(arguments) == 5:
                bk_yt_link = arguments[3]
                if bk_yt_link == "Prev":
                    bk_yt_link = "Null"
                    try:
                        prev_json = json.loads(base64.b64decode(arguments[4]).decode('utf-8'))
                        prev_state_JSON = json.loads(base64.b64decode(prev_json["state"]).decode('utf-8'))
                        prev_PART_JSON = json.loads(base64.b64decode(prev_json["PART"]).decode('utf-8'))
                        prev_TITLE_JSON = json.loads(base64.b64decode(prev_json["TITLE"]).decode('utf-8'))
                        prev_CATEGORY_JSON = json.loads(base64.b64decode(prev_json["CATEGORY"]).decode('utf-8'))
                        if len(prev_state_JSON["live_url"]) == 11:
                            IFTHEREISMORE = f"ARG3: recieved previous data for peaceful period"
                            prev = True
                    except Exception as e:
                        logging.info(f"1474 - Error reading previous script data, pass")
            logging.info("1474 - ==================================================") 
            logging.info(f"1474 - INPUT ARGUMENT AVAILABLE (Ver.{script_version}) (CONFIG VIEW IN CONFIG_TV.PY)") 
            logging.info(f"1474 - ARG1: {yt_link} ARG2: {rtmp_info}")
            if IFTHEREISMORE != "":
                logging.info(f"1474 - {IFTHEREISMORE}") 
            logging.info(f"1474 - ARCHIVE USER: {config.username}") 
            logging.info("1474 - ==================================================")
        if rtmp_info not in ["defrtmp", "bkrtmp", "Null"]: 
            logging.error(f"1474 - Invalid RTMP server type: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'") 
            exit(1) 
        live_url = None 
        rtmp_server = None 
        if yt_link == "Null": 
            logging.info("1474 - Starting live API check to get initial stream URL") 
            rtmp_server = "defrtmp" 
            try: 
                live_url = api_create_edit_schedule(0, rtmp_server, True, "Null") 
                logging.info(f"1474 - Successfully created new stream with URL: {live_url}") 
            except Exception as e: 
                logging.error(f"1474 - Failed to create stream via API: {str(e)}") 
                raise 
        else: 
            live_url = yt_link 
            rtmp_server = rtmp_info 
            logging.info(f"1474 - Using provided YouTube link: {live_url} with RTMP server: {rtmp_server}")
        if THEREISMORE == "Null":
            if prev:
                first_time = time.time()
            else:
                first_time = None
            logging.info("1474 - Waiting for stream to go live...")
            status = {"status": False}             
            threading.Thread(target=handle_input, args=(status, live_url, rtmp_server), daemon=True).start()
            while True:  
                try:
                    streams = get_twitch_streams()  
                    if streams:  
                        if not streams == "ERROR":
                            stream = streams[0]  
                            logging.info(f"1474 - Stream is now live! Title From Twitch: {stream['title']}") 
                            if prev and (time.time() - first_time) <= 600: 
                                logging.info("1474 - Peaceful period detected - edit the previous stream description and apply previous session data")
                                def apply_gobal_state(prev_PART_JSON, prev_TITLE_JSON, prev_CATEGORY_JSON):
                                    global PART
                                    global TITLE
                                    global CATEGORY
                                    CATEGORY = prev_CATEGORY_JSON
                                    PART = prev_PART_JSON
                                    TITLE = prev_TITLE_JSON
                                def title_and_edit(prev_state_JSON, reason):
                                    if TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and prev_state_JSON['gmail_checking'] and CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None:
                                        logging.info("1474 - Previous title and category changes detected - performing title and category edit")
                                        api_create_edit_schedule(PART["partnumber"], None, "PREVDESCANDCAT", prev_state_JSON["live_url"], reason, False, None, TITLE[f"part{TITLE['currentnumber']}"])
                                    elif CATEGORY["currentnumber"] >= 1 and CATEGORY["part0"] is not None:
                                        logging.info("1474 - Previous category changes detected - performing category edit")
                                        api_create_edit_schedule(PART["partnumber"], None, "PREVCATEGORY", prev_state_JSON["live_url"], reason, False, None, TITLE[f"part{TITLE['currentnumber']}"])
                                    elif TITLE["currentnumber"] >= 1 and TITLE["part0"] is not None and prev_state_JSON['gmail_checking']:
                                        logging.info("1474 - Previous title changes detected - performing title edit")
                                        api_create_edit_schedule(PART["partnumber"], None, "PREVDECRIPTION", prev_state_JSON["live_url"], reason, False, None, TITLE[f"part{TITLE['currentnumber']}"])
                                    else:
                                        logging.info("1474 - No previous title or category changes detected - performing standard edit")
                                        api_create_edit_schedule(PART["partnumber"], None, "EDIT", prev_state_JSON["live_url"], reason, False, None, TITLE[f"part{TITLE['currentnumber']}"])
                                    restart_title_arg()
                                    restart_category_arg()
                                apply_gobal_state(prev_PART_JSON, prev_TITLE_JSON, prev_CATEGORY_JSON)
                                PART[f"part{PART['partnumber']+1}"] = prev_state_JSON["live_url"]
                                PART['partnumber'] += 1
                                reason = f"[Reason of switching is streamer got offline(Part{PART["partnumber"]+1} is on https://youtube.com/watch?v={live_url})]"
                                threading.Thread(target=title_and_edit, args=(prev_state_JSON, reason), daemon=False).start()
                            status['status'] = True
                            break  
                        else:
                            logging.error(f"1474 - Error checking stream status")  
                            time.sleep(30)  
                    else:
                        time.sleep(10)  
                except Exception as e:  
                    logging.error(f"1474 - Error checking stream status: {str(e)}")  
                    time.sleep(30)  
            live_spare_url = None  
            logging.info("1474 - Starting stream monitoring process...")  
            if not live_url:  
                logging.error("1474 - Missing live URL - cannot start monitoring")  
                exit(1)  
            if rtmp_server not in ["defrtmp", "bkrtmp"]:  
                logging.error(f"1474 - Invalid RTMP server type: {rtmp_server}")  
                exit(1)
            try:
                if rtmp_server == "bkrtmp":  
                    logging.info("1474 - Starting with backup stream rtmp... and check")  
                    threading.Thread(target=start_restreaming, args=("api_this", live_url), daemon=False).start()
                elif rtmp_server == "defrtmp":  
                    logging.info("1474 - Starting with default stream rtmp... and check")  
                    threading.Thread(target=start_restreaming, args=("this", live_url), daemon=False).start()  
                if config.local_archive:
                    logging.info("1474 - Starting local archive process...")
                    filename = f"{datetime.now().strftime('%Y-%m-%d')}_{stream['title']}"
                    threading.Thread(target=local_save, args=(filename,), daemon=False).start()
            except Exception as e:  
                logging.error(f"1474 - Failed to start relay process: {str(e)}")  
                psutil.Process(os.getpid()).terminate() 
            logging.info("1474 - Stream relay process started successfully")  
        else:
            pass
        try:
            if THEREISMORE == "Null" and not prev:
              titlegmail = api_create_edit_schedule(0, rtmp_server, "EDIT", live_url)
            if THEREISMORE != "Null":
              titlegmail = get_youtube_stream_title(live_url)
            if prev:
                titlegmail = api_create_edit_schedule(PART['partnumber']+1, rtmp_server, "EDIT", live_url)
            logging.info('1474 - edit finished continue the stream')  
        except UnboundLocalError:  
            logging.warning("1474 - Encountered UnboundLocalError when getting title - continuing with default continue at your own risk")  
        except Exception as e:  
            logging.error(f"1474 - Error getting stream title: {str(e)} - continuing at your own risk")  
        try:
            logging.info("1474 - Loading backup stream configuration...")  
            if rtmp_server == "bkrtmp":
                rtmp_server = "defrtmp"
            elif rtmp_server == "defrtmp":
                rtmp_server = "bkrtmp"
            if bk_yt_link == "Null":
                live_spare_url = api_create_edit_schedule(0, rtmp_server, True, "Null")  
            else:
                live_spare_url = bk_yt_link  
            logging.info(f"1474 - Backup stream URL configured: {live_spare_url}")  
        except Exception as e:  
            logging.error(f"1474 - Failed to create backup stream: {str(e)}")  
        logging.info("1474 - Starting offline detection...")  
        offline_check_functions(live_url, live_spare_url, rtmp_server, titlegmail) 
    except Exception as e:
        logging.error(f"1474 - Error in initialize_and_monitor_stream: {str(e)}", exc_info=True)  
        logging.error("1474 - Critical error encountered - terminating script execution")  
        psutil.Process(os.getpid()).terminate() 

def check_chrome_version(target_version=(130, 0, 6723, 70)):
    """Check if installed Chrome version is <= target version (default: 130.0.6723.70)"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon') as key:
            version_str, _ = winreg.QueryValueEx(key, 'version')  
            version = tuple(map(int, version_str.split('.')))  
        if version <= target_version:
            return True  
        else:
            logging.info(f"1656 - Chrome version {version_str} is > {'.'.join(map(str, target_version))}")  
            return False
    except FileNotFoundError:  
        logging.info("1656 - Chrome is not installed or version could not be detected.")
        return False
    except (ValueError, Exception) as e:  
        logging.info(f"1656 - Error checking Chrome version: {str(e)}")
        return False

if __name__ == "__main__": 
    initialize_and_monitor_stream()  
    exit()  

