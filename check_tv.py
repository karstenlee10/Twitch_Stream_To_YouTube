import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
import config_tv as config
import psutil
import requests
import enum
import unicodedata
import string
import random
import datetime
import streamlink
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth.exceptions
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import json
import threading
import cv2
import getopt
import re
import shutil
from selenium.webdriver.chrome.service import Service
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
refresh = 15
token_url = "https://id.twitch.tv/oauth2/token?client_id=" + config.client_id + "&client_secret=" \
                         + config.client_secret + "&grant_type=client_credentials"
APP_TOKEN_FILE = "client_secret.json"
USER_TOKEN_FILE = "user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
]
home_dir = os.path.expanduser("~")
arguments = sys.argv
desired_url = "https://www.twitch.tv/" + config.username
bilibili_desired_url = "https://live.bilibili.com/" + config.bilibililiveuid

def bilibili_offline_check(driver, live_url, spare_link, important):
      refresh_count = 0
      countdownhours = 0
      numberpart = 0
      fewtimes = 0
      while True:
         try:
             current_url = driver.current_url
             if current_url == bilibili_desired_url:
                ok = "ok"
             else:
                    kkkys = "the url has change:" + current_url + " killing process and public stream"
                    logging.info(kkkys)
                    driver.quit()
                    if config.unliststream == "True":
                       logging.info("public back the stream")
                       logging.info("--START-------------(edit_tv)---------------")
                       public_stream(live_url)
                       logging.info("--END-------------(edit_tv)-----------------")
                    os.system("taskkill /f /im " + config.apiexe)
                    os.system("start check_tv.py " + spare_link + " " + important)
                    break
             try:
               driver.find_element("xpath", "//div[@class='web-player-ending-panel']")
               fewtimes += 1
               driver.refresh()
               time.sleep(7)
               if fewtimes == 6:
                 logging.info("Element found success. offine reload program and public stream")
                 driver.quit()
                 if config.unliststream == "True":
                   logging.info("public back the stream")
                   logging.info("--START-------------(edit_tv)---------------")
                   public_stream(live_url)
                   logging.info("--END-------------(edit_tv)-----------------")
                 os.system("taskkill /f /im " + config.apiexe)
                 os.system("start check_tv.py " + spare_link + " " + important)
                 break
             except NoSuchElementException:
                 time.sleep(5)
         except:
            logging.info("sus offine i dnot know why the driver shutdown restart driver")
            try:
               driver.quit()
            except:
               abc = "abc"
            driveromg = selreload()
            bilibili_offline_check(driveromg, live_url, spare_link, important)
         refresh_count += 1
         countdownhours += 1
         if refresh_count == 60:
            driver.refresh()
            time.sleep(7)
            refresh_count = 0
         if countdownhours == 7871:
           logging.info("omg is almost 12hours reload stream and kill apiexe")
           os.system("taskkill /f /im " + config.apiexe)
           logging.info("--START-----------live_api-----------------")
           checktitlelol(numberpart, important, "Null", spare_link)
           logging.info("--END-------------live_api-----------------")
           logging.info("finish reloading start spare stream")
           logging.info("load spare stream")
           if important == "schedule":
               important = "schsheepedule"
           elif important == "schsheepedule":
               important = "schedule"
           logging.info("--START-----------live_api-----------------")
           live_spare_url = checktitlelol("0", important, "True", "Null")
           logging.info("--END-------------live_api-----------------")
           os.system("start " + config.apiexe)
           if config.unliststream == "True":
             logging.info("public back the stream")
             logging.info("--START-------------(edit_tv)---------------")
             public_stream(live_url)
             logging.info("--END-------------(edit_tv)-----------------")
           logging.info("load offline_check again")
           live_url = spare_link
           spare_link = live_spare_url
           logging.info(important)
           countdownhours = 0

def offline_check(driver, live_url, spare_link, important):
      refresh_count = 0
      countdownhours = 0
      numberpart = 0
      fewtimes = 0
      try:
        driver.find_element("xpath", "//button[@data-a-target='content-classification-gate-overlay-start-watching-button']//div[text()='開始觀看']").click()
        time.sleep(5)
      except:
          try:
            actions = ActionChains(driver)
            actions.send_keys('k').perform()
          except:
            logging.info("sus button i dnot know why it shutdown reload driver")
            driver.refresh()
            time.sleep(10)
            offline_check(driver, live_url, spare_link, important)
      while True:
         try:
             current_url = driver.current_url
             if current_url == desired_url:
                ok = "ok"
             else:
                if '?referrer=raid' in current_url:
                    kkkys = "the url has been raid:" + current_url + " killing process"
                    logging.info(kkkys)
                    driver.quit()
                    if config.unliststream == "True":
                       logging.info("public back the stream")
                       logging.info("--START-------------(edit_tv)---------------")
                       public_stream(live_url)
                       logging.info("--END-------------(edit_tv)-----------------")
                    os.system("taskkill /f /im " + config.apiexe)
                    os.system("start check_tv.py " + spare_link + " " + important)
                    break
                else:
                    kkkys = "the url has change:" + current_url + " killing process"
                    logging.info(kkkys)
                    driver.quit()
                    if config.unliststream == "True":
                       logging.info("public back the stream")
                       logging.info("--START-------------(edit_tv)---------------")
                       public_stream(live_url)
                       logging.info("--END-------------(edit_tv)-----------------")
                    os.system("taskkill /f /im " + config.apiexe)
                    os.system("start check_tv.py " + spare_link + " " + important)
                    break
             element = driver.find_element("xpath", "//div[@class='Layout-sc-1xcs6mc-0 liveIndicator--x8p4l']//span[text()='LIVE']/ancestor::div")
             time.sleep(5)
         except NoSuchElementException:
            fewtimes += 1
            driver.refresh()
            time.sleep(7)
            if fewtimes == 3:
              logging.info("Element not found success. shutdown")
              driver.quit()
              if config.unliststream == "True":
                logging.info("public back the stream")
                logging.info("--START-------------(edit_tv)---------------")
                public_stream(live_url)
                logging.info("--END-------------(edit_tv)-----------------")
              os.system("taskkill /f /im " + config.apiexe)
              os.system("start check_tv.py " + spare_link + " " + important)
              break
         except:
            logging.info("sus offine i dnot know why it shutdown restart driver")
            try:
               driver.quit()
            except:
               abc = "abc"
            driver = selreload()
         refresh_count += 1
         countdownhours += 1
         if refresh_count == 60:
            driver.refresh()
            time.sleep(7)
            actions = ActionChains(driver)
            actions.send_keys('k').perform()
            refresh_count = 0
         if countdownhours == 7871:
           logging.info("omg is almost 12hours reload stream and kill apiexe")
           os.system("taskkill /f /im " + config.apiexe)
           logging.info("--START-----------live_api-----------------")
           checktitlelol(numberpart, important, "Null", spare_link)
           logging.info("--END-------------live_api-----------------")
           logging.info("finish reloading start spare stream")
           logging.info("load spare stream")
           if important == "schedule":
               important = "schsheepedule"
           elif important == "schsheepedule":
               important = "schedule"
           logging.info("--START-----------live_api-----------------")
           live_spare_url = checktitlelol("0", important, "True", "Null")
           logging.info("--END-------------live_api-----------------")
           os.system("start " + config.apiexe)
           if config.unliststream == "True":
              logging.info("public back the stream")
              logging.info("--START-------------(edit_tv)---------------")
              public_stream(live_url)
              logging.info("--END-------------(edit_tv)-----------------")
           logging.info("load offline_check again")
           numberpart += 1
           live_url = spare_link
           spare_link = live_spare_url
           logging.info(important)
           countdownhours = 0

def bilibili_load_check(driver):
    while True:
        try:
            element = driver.find_element("xpath", "//div[@class='web-player-ending-panel']")
            break
        except NoSuchElementException:
            time.sleep(5)
        except:
                logging.info("crashed restart driver")
                try:
                      driver.quit()
                except:
                      abc = "abc"
                driveromg = selreload()
                load_check(driveromg)

def load_check(driver):
    while True:
        try:
            element = driver.find_element("xpath", "//div[contains(@class, 'Layout-sc-1xcs6mc-0 liveIndicator--x8p4l')]//span[text()='LIVE']/ancestor::div")
            break
        except NoSuchElementException:
            time.sleep(5)
        except:
                logging.info("crashed restart driver")
                try:
                      driver.quit()
                except:
                      abc = "abc"
                driveromg = selreload()
                load_check(driveromg)

def selreload():
        driver = webdriver.Chrome()
        if config.Twitch == "True":
            driver.get("https://twitch.tv/" + config.username)
        if config.BiliBili == "True":
            driver.get("https://live.bilibili.com/" + config.bilibililiveuid)
        time.sleep(7)
        if config.BiliBili == "True":
              return driver
        if config.Twitch == "True":
         try:
            element = driver.find_element("xpath", "//div[contains(@class, 'Layout-sc-1xcs6mc-0 liveIndicator--x8p4l')]//span[text()='LIVE']/ancestor::div")
            try:
                  driver.find_element("xpath", "//button[@data-a-target='content-classification-gate-overlay-start-watching-button']//div[text()='開始觀看']").click()
            except:
                  abc = "abc"
            return driver
         except NoSuchElementException:
          try:
            kys = "//a[@tabname='chat' and @data-a-target='channel-home-tab-Chat' and contains(@href, '/" + config.username + "')]"
            button = driver.find_element("xpath", kys)
            button.click()
            return driver
          except NoSuchElementException:
            kys = "//a[@tabname='chat' and @data-a-target='channel-home-tab-Chat' and contains(@href, '/" + config.username + "')]"
            button = driver.find_element("xpath", kys)
            button.click()
            return driver
          except:
            logging.info("the driver got shutdown restarting")
            try:
               driver.quit()
            except:
               abc = "abc"
            omg = selreload()
            return omg
         except:
            logging.info("the driver got shutdown restarting")
            try:
               driver.quit()
            except:
               abc = "abc"
            omg = selreload()
            return omg

def selwebdriver_check(yt_link, infomation, driver):
      try:
        if driver == "Null":
          if yt_link == "Null":
             logging.info("--START-----------live_api-----------------")
             haha = "schsheepedule"
             live_url = checktitlelol("0", haha, "True", "Null")
             logging.info("--END-------------live_api-----------------")
          else:
             live_url = yt_link
             haha = infomation
          driver = webdriver.Chrome()
          if config.Twitch == "True":
            driver.get("https://twitch.tv/" + config.username)
          if config.BiliBili == "True":
            driver.get("https://live.bilibili.com/" + config.bilibililiveuid)
          time.sleep(7)
        if config.BiliBili == "True":
         try:
           live_link = "https://live.bilibili.com/" + config.bilibililiveuid
           driver.find_element("xpath", "//div[@class='web-player-ending-panel']")
           logging.info("wait stream to start")
           load_check(driver)
           logging.info("load start")
           start_check(driver, live_url, haha)
         except NoSuchElementException:
           logging.info("load start immdently")
           start_check(driver, live_url, haha)
        if config.Twitch == "True":
         try:
           element = driver.find_element("xpath", "//div[contains(@class, 'Layout-sc-1xcs6mc-0 liveIndicator--x8p4l')]//span[text()='LIVE']/ancestor::div")
           logging.info("load start immdently")
           start_check(driver, live_url, haha)
         except NoSuchElementException:
           kys = "//a[@tabname='chat' and @data-a-target='channel-home-tab-Chat' and contains(@href, '/" + config.username + "')]"
           button = driver.find_element("xpath", kys)
           button.click()
           load_check(driver)
           logging.info("load start")
           start_check(driver, live_url, haha)
      except Exception as e:
            logging.info(e)
            logging.info("the script failed shuting down")
      #finally:
            #pass

def checkarg():
  try:
    arg1 = arguments[1]
    if arg1 == "KILL":
          logging.info("close all exe")
          os.system("taskkill /f /im " + config.apiexe)
          os.system("taskkill /f /im " + config.ffmpeg)
          os.system("taskkill /f /im " + config.ffmpeg1)
          os.system("taskkill /f /im countdriver.exe")
          exit()
    arg2 = arguments[2]
    logging.info("theres arg")
    try:
      selwebdriver_check(arg1, arg2, "Null")
      exit()
    except:
          logging.info("failed script shutdown")
  except Exception as e:
    logging.info("theres no arg")
    arg = "Null"
    selwebdriver_check(arg, arg, "Null")

def start_check(driver, live_url, haha):
            logging.info("start relive_tv")
            os.system("start " + config.apiexe)
            if haha == "schedule":
                  logging.info("start relive_tv")
                  os.system("start relive_tv.py api_this")
                  inport = "schsheepedule"
            if haha == "schsheepedule":
                  logging.info("start relive_tv")
                  os.system("start relive_tv.py this")
                  inport = "schedule"
            logging.info("your_live_url: " + live_url)
            logging.info("started relive_tv")
            logging.info("--START-----------(edit_tv)-----------------")
            try:
              selwebdriver(live_url, haha)
            except UnboundLocalError:
                  this_bug_is_unfixable = "sigh"
            logging.info("--END-------------(edit_tv)-----------------")
            logging.info("load spare stream")
            logging.info("--START-----------live_api-----------------")
            live_spare_url = checktitlelol("0", inport, "True", "Null")
            logging.info("--END-------------live_api-----------------")
            logging.info("wait for offine now... and start countdown")
            try:
              if config.Twitch == "True":
                offline_check(driver, live_url, live_spare_url, inport)
              if config.BiliBili == "True":
                bilibili_offline_check(driver, live_url, live_spare_url, inport)
            except:
              logging.info("driver shutdown restarting")
              try:
                driver.quit()
              except:
                abc = "abc"
              driveromg = selreload()
              if config.Twitch == "True":
                offline_check(driver, live_url, live_spare_url, inport)
              if config.BiliBili == "True":
                bilibili_offline_check(driver, live_url, live_spare_url, inport)
            exit()

class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4           

def check_process_running():
    process_name = "countdriver.exe"
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            logging.info("some script is using the driver wait")
            time.sleep(15)
            check_process_running()
    return

def get_creds_saved():
    creds = None

    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_service():
    creds = get_creds_saved()
    service = build('youtube', 'v3', credentials=creds)
    return service

def edit_live_stream(video_id, new_title, new_description):
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
       return response['id']
    except google.auth.exceptions.RefreshError as e:
      logging.info(f"Error: {e}")
      logging.info("error edit token bad reget token")
      os.system("get_token.py")
      fuckyou = edit_live_stream(video_id, new_title, new_description)
      return fuckyou

def public_stream(live_id):
    try:
       service = get_service()
       scheduled_start_time = datetime.datetime.utcnow().isoformat()
       request = service.videos().update(
           part='status',
           body={
               'id': live_id,
               'status': {
                   'privacyStatus': 'public'
               }
           }
       )
       response = request.execute()
       return response['id']
    except google.auth.exceptions.RefreshError as e:
      logging.info(f"Error: {e}")
      logging.info("error token bad reget token")
      os.system("get_token.py")
      omg = public_stream(live_id)
      return omg

def api_load(url):
        logging.basicConfig(filename="tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.info("create api keying ---edit_tv---")
        home_dir = os.path.expanduser("~")
        logging.info("run with countdriver.exe and check")
        check_process_running()
        os.system("start countdriver.exe")
        options = Options()
        chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")
        options.add_argument("user-data-dir=" + chrome_user_data_dir)
        options.add_argument("profile-directory=" + config.Chrome_Profile)
        notafrickdriver = webdriver.Chrome(options=options)
        notafrickdriver.get(url)
        time.sleep(3)
        nameofaccount = "//div[contains(text(),'" + config.accountname + "')]"
        button_element = notafrickdriver.find_element("xpath", nameofaccount)
        button_element.click()
        time.sleep(3)
        element = notafrickdriver.find_element("xpath", "//div[@class='SxkrO']//button[@jsname='LgbsSe']")
        element.click()
        time.sleep(3)
        button_element = notafrickdriver.find_element("xpath", "//button[contains(@class, 'VfPpkd-LgbsSe') and contains(@jsname, 'LgbsSe')]//span[@class='VfPpkd-vQzf8d' and text()='繼續']")
        button_element.click()
        time.sleep(3)
        element = notafrickdriver.find_element("xpath", "//input[@class='VfPpkd-muHVFf-bMcfAe' and @type='checkbox']")
        element.click()
        time.sleep(1)
        button_element = notafrickdriver.find_element("xpath", "//button[contains(@class, 'VfPpkd-LgbsSe') and contains(@jsname, 'LgbsSe')]//span[@class='VfPpkd-vQzf8d' and text()='繼續']")
        button_element.click()
        os.system('TASKKILL /f /im countdriver.exe')
        logging.info("finish idk ---edit_tv---")
        time.sleep(5)
        notafrickdriver.quit()

def confirm_logged_in(driver: webdriver) -> bool:
          """ Confirm that the user is logged in. The browser needs to be navigated to a YouTube page. """
          try:
              WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "avatar-btn")))
              return True
          except:
              logging.info(f"i domt know why it doesnot work lol")
              driver.quit()
              exit()

def get_stream_linkandtitle():
        response = requests.get("https://live.bilibili.com/" + config.bilibililiveuid)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        main_title = re.sub(r' - .*', '', title)
        return main_title

def selwebdriver(live_url, timeisshit):
      if config.Twitch == "True":
       url = "https://api.twitch.tv/helix/streams"
       access_token = fetch_access_token()
       info = None
       status = TwitchResponseStatus.ERROR
       try:
            headers = {"Client-ID": config.client_id, "Authorization": "Bearer " + access_token}
            r = requests.get(url + "?user_login=" + config.username , headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
       except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
       try:
        channels = info["data"]
        channel = next(iter(channels), None)
        titletv = channel.get('title')
       except AttributeError:
            logging.info('the stream is not live please start at relive_tv.py first! try again')
            time.sleep(5)
            selwebdriver(live_url)
      if config.BiliBili == "True":
            titletv = get_stream_linkandtitle()
      textnoemo = ''.join('' if unicodedata.category(c) == 'So' else c for c in titletv)
      if "<" in textnoemo or ">" in textnoemo:
                   textnoemo = textnoemo.replace("<", "").replace(">", "")
      characters = string.ascii_letters + string.digits
      random_string = ''.join(random.choices(characters, k=7))
      filenametwitch = config.username +  " | " + textnoemo +  " | " + datetime.datetime.now() \
                    .strftime("%Y-%m-%d")
      if config.Twitch == "True":
              deik = "this stream is from https://twitch.tv/" + config.username + " (Stream Name:" + textnoemo + ")"
      if config.BiliBili == "True":
              deik = "this stream is from https://live.bilibili.com/" + config.bilibililiveuid + " (Stream Name:" + textnoemo + ")"
      if len(filenametwitch) > 100:
              logging.info("title too long")
              filenametwitch = config.username +  " | " + datetime.datetime.now() \
                    .strftime("%Y-%m-%d") + " | " + random_string
      logging.info('process of edit name started')
      try:
            edit_live_stream(live_url, filenametwitch, deik)
            new_url = f"https://youtube.com/watch?v={live_url}"
            logging.info("wait to check live 40sec")
            time.sleep(40)
            if timeisshit == "schedule":
              check_is_live_api(new_url, config.ffmpeg1, "api_this")
            if timeisshit == "schsheepedule":
              check_is_live_api(new_url, config.ffmpeg, "this")
      finally:
            logging.info('edit finished contiue the stream')

def create_live_stream(title, description, kmself):
    try:
       service = get_service()
       scheduled_start_time = datetime.datetime.utcnow().isoformat()
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
                    "lifeCycleStatus": "ready",
                    "recordingStatus": "notRecording",
                    "selfDeclaredMadeForKids": False
                },
                "contentDetails": {
                    "enableAutoStart": True,
                    "enableAutoStop": True,
                    "latencyPreference": "ultraLow"
                }
            }
        )
       response = request.execute()
       return response['id']
    except google.auth.exceptions.RefreshError as e:
      logging.info(f"Error: {e}")
      logging.info("error token bad reget token")
      os.system("get_token.py")
      time.sleep(60)
      fuckyou = create_live_stream(title, description)
      return fuckyou

def get_scheduled_stream_info(stream_id):
    creds = get_creds_saved()
    service = build('youtube', 'v3', credentials=creds)

    request = service.liveBroadcasts().list(
        part='snippet,status',
        id=stream_id
    )

    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    else:
        return None

def edit_rtmp_key(driver, what):
 countfuckingshit = 0
 while True:
  try:
    driver.find_element(By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']").click()
    time.sleep(3)
    if what == "schedule":
        xpath = "//*[contains(text(),'" + config.rtmpkeyname1 + " (RTMP，位元率可變')]"
        element2 = driver.find_element(By.XPATH, xpath)
        element2.click()
        time.sleep(7)
    if what == "schsheepedule":
        xpath = "//*[contains(text(),'" + config.rtmpkeyname + " (RTMP，位元率可變')]"
        element3 = driver.find_element(By.XPATH, xpath)
        element3.click()
        time.sleep(7)
    driver.find_element(By.XPATH, "//button[.//div[@class='ytcp-button-shape-impl__button-text-content' and text()='編輯']]").click()
    time.sleep(3)
    driver.find_element(By.XPATH, "//li[.//span[text()='自訂']]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//*[@id='chat-enabled-checkbox']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//ytcp-button-shape[.//div[@class='ytcp-button-shape-impl__button-text-content' and text()='儲存']]").click()
    time.sleep(10)
    logging.info("finsih")
    driver.quit()
    os.system("taskkill /f /im countdriver.exe")
    break
  except:
        logging.info("error again")
        driver.refresh()
        time.sleep(15)
        countfuckingshit += 1
  if countfuckingshit == 3:
        logging.info("edit rtmp key fail shutdown script")
        os.system("taskkill /f /im countdriver.exe")
        exit()

def check_is_live_api(url, ffmpeg, text):
 countshit = 0
 while True:
    try:
        print(url)
        streams = streamlink.streams(url)
        hls_stream = streams["best"]
        logging.info('fucking live now')
        break
    except KeyError:
            logging.info('The stream is messed up. Trying again...')
            time.sleep(2)
            os.system('TASKKILL /f /im ' + ffmpeg)
            os.system('start relive_tv.py ' + text)
            time.sleep(35)
            countshit += 1
    if countshit == 5:
            logging.info("failed shutdown script")
            os.system('TASKKILL /f /im ' + ffmpeg)
            os.system('start relive_tv.py ' + text)
            exit()

def checktitlelol(arg1, arg2, reload, url_omg):
      if config.Twitch == "True":
        if reload == "Null":
          url = "https://api.twitch.tv/helix/streams"
          access_token = fetch_access_token()
          info = None
          status = TwitchResponseStatus.ERROR
          try:
            headers = {"Client-ID": config.client_id, "Authorization": "Bearer " + access_token}
            r = requests.get(url + "?user_login=" + config.username , headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
          except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
          channels = info["data"]
          channel = next(iter(channels), None)
          try:
            titletv = channel.get('title')
          except AttributeError:
            logging.info('the stream is not live please start at check_tv.py first! try again')
            time.sleep(10)
            checktitlelol(arg1, arg2, reload, url_omg)
      if config.BiliBili == "True":
        if reload == "Null":
          titletv = get_stream_linkandtitle()
      if reload == "Null":
        textnoemo = ''.join('[EMOJI]' if unicodedata.category(c) == 'So' else c for c in titletv)
        if "<" in textnoemo or ">" in textnoemo:
                 textnoemo = textnoemo.replace("<", "[ERROR]").replace(">", "[ERROR]")
        calit = int(arg1) + 1
        filenametwitch = config.username +  " | " + textnoemo +  " | " + datetime.datetime.now() \
                    .strftime("%Y-%m-%d") + " | " + "part " + str(calit)
        if len(filenametwitch) > 100:
              filenametwitch = config.username +  " | " + datetime.datetime.now() \
                     .strftime("%Y-%m-%d") + " | " + "part " + str(calit)
        deik = "this stream is from twitch.tv/" + config.username + " (Stream Name:" + textnoemo + ")"
      try:
            if reload == "True":
                            filenametwitch = config.username + " (wait for stream title)"
                            deik = "(wait for stream title)"
            if url_omg == "Null":
              logging.info('sending to api')
              if config.unliststream == "True":
                strId = create_live_stream(filenametwitch, deik, "unlisted")
              if config.unliststream == "False":
                strId = create_live_stream(filenametwitch, deik, "public")
              logging.info('reading api json and check if driver loading')
              json_data = json.dumps(get_scheduled_stream_info(strId), indent=4)
              data_dict = json.loads(json_data)
              live_url = data_dict["id"]
              check_process_running()
              os.system("start countdriver.exe")
              options = Options()
              chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")
              options.add_argument("user-data-dir=" + chrome_user_data_dir)
              options.add_argument("profile-directory=" + config.Chrome_Profile)
              while True:
                try:
                  driver = webdriver.Chrome(options=options)
                  break
                except SessionNotCreatedException:
                  abc = "abc"
              url_to_live = "https://studio.youtube.com/video/" + live_url + "/livestreaming"
              driver.get(url_to_live)
              time.sleep(5)
              driver.refresh()
              time.sleep(30)
              logging.info("edit the rtmp key and chat")
              if arg2 == "schedule":
                edit_rtmp_key(driver, "schedule")
              if arg2 == "schsheepedule":
                edit_rtmp_key(driver, "schsheepedule")
              driver.quit()
              os.system('TASKKILL /f /im countdriver.exe')
            else:
              logging.info("edit the title of the url")
              live_url = url_omg
              edit_live_stream(live_url, filenametwitch, deik)
            if reload == "True":
                return live_url
            logging.info("start relive")
            if arg2 == "schedule":
              os.system("start relive_tv.py api_this")
            if arg2 == "schsheepedule":
              os.system("start relive_tv.py this")
            logging.info("finish load stream starting killing old live wait 1 min and check live")
            time.sleep(25)
            new_url = f"https://youtube.com/watch?v={live_url}"
            if arg2 == "schedule":
              check_is_live_api(new_url, config.ffmpeg1, "api_this")
            if arg2 == "schsheepedule":
              check_is_live_api(new_url, config.ffmpeg, "this")
            logging.info("killing it rn and the driver and too long and start countdown")
            if arg2 == "schedule":
                command = "taskkill /f /im " + config.ffmpeg
                os.system(command)
            if arg2 == "schsheepedule":
                command = "taskkill /f /im " + config.ffmpeg1
                os.system(command)
            time.sleep(2)
            if arg2 == "schedule": #"start " +
              if config.ytshort == "True":
                os.system('start ' + config.ffmpeg + ' -fflags +genpts -re -i too-long.mp4 -c:v h264_qsv -c:a aac -b:a 128k -preset veryfast -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key)
              if config.ytshort == "False":
                os.system("start " + config.ffmpeg + " -re -i too-long.mp4 -c:v libx264 -preset veryfast -c:a aac -f flv rtmp://a.rtmp.youtube.com/live2/" + config.rtmp_key)
            if arg2 == "schsheepedule":
              if config.ytshort == "True":
                os.system('start ' + config.ffmpeg1 + ' -fflags +genpts -re -i too-long.mp4 -c:v libx264 -preset veryfast -c:a aac -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1)
              if config.ytshort == "False":
                os.system("start " + config.ffmpeg1 + " -re -i too-long.mp4 -c:v libx264 -preset veryfast -c:a aac -f flv rtmp://a.rtmp.youtube.com/live2/" + config.rtmp_key_1)
            if url_omg == "Null":
               logging.info("fucking finish")
            else:
                logging.info("fucking finish")
                return
      except KeyError:
               abc = "abc"
      except Exception as e:
            logging.info(e)
            logging.info("something errorly happen lol stop rn")
            exit()

def fetch_access_token():
        token_response = requests.post(token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]
    
######################check_tv##################
if __name__ == "__main__":
    logging.basicConfig(filename="tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    from google_auth_oauthlib.flow import InstalledAppFlow
    checkarg()
    exit()

