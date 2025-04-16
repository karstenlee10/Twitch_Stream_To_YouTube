import subprocess # 導入子進程管理模塊
import sys # 導入系統相關模塊
import os # 導入操作系統模塊
import time # 導入時間相關模塊
import logging # 導入日誌記錄模塊
import argparse # 導入命令行參數解析模塊
from selenium import webdriver # 導入瀏覽器自動化模塊
from selenium.webdriver.common.by import By # 導入元素定位方式
from selenium.webdriver.support import expected_conditions as EC # 導入預期條件
from selenium.webdriver.support.ui import WebDriverWait # 導入等待機制
from selenium.common.exceptions import SessionNotCreatedException # 導入會話異常
from selenium.webdriver.chrome.options import Options # 導入Chrome瀏覽器選項
from google.oauth2.credentials import Credentials # 導入Google認證模塊
from googleapiclient.discovery import build # 導入Google API構建工具
import config_tv as config # 導入配置文件
import psutil # 導入進程和系統監控模塊
import requests # 導入HTTP請求模塊
import enum # 導入枚舉類型模塊
import unicodedata # 導入Unicode數據處理模塊
import string # 導入字符串處理模塊
import random # 導入隨機數生成模塊
from datetime import datetime, timedelta, timezone # 導入日期時間處理模塊
import streamlink # 導入流媒體處理模塊
from twitchAPI.twitch import Twitch # 導入Twitch API模塊
import asyncio # 導入異步IO模塊
from google.auth.transport.requests import Request # 導入Google認證請求模塊

refresh_title = "True"

token_url = f"https://id.twitch.tv/oauth2/token?client_id={config.client_id}&client_secret={config.client_secret}&grant_type=client_credentials" # Twitch認證URL
APP_TOKEN_FILE = "client_secret.json" # Google應用憑證文件
GMAIL_TOKEN_FILE = "gmail_token.json" # Gmail令牌文件
USER_TOKEN_FILE = "user_token.json" # 用戶令牌文件

SCOPES_GMAIL = [ # Gmail API權限範圍
    'https://www.googleapis.com/auth/gmail.readonly',
  ]

SCOPES_BRAND = [ # YouTube品牌賬戶API權限範圍
    'https://www.googleapis.com/auth/youtube.force-ssl',
  ]

SCOPES = [ # 一般用戶API權限範圍
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/gmail.readonly',
  ]

home_dir = os.path.expanduser("~") # 獲取用戶主目錄

# 解析命令行參數
def parse_arguments():
    parser = argparse.ArgumentParser(description="Twitch to YouTube直播歸檔系統")
    parser.add_argument("yt_link", nargs="?", default=None, help="YouTube視頻ID")
    parser.add_argument("rtmpkey", nargs="?", default=None, help="RTMP服務器類型 (defrtmp 或 bkrtmp)")
    
    # 解析已知參數，忽略未知參數
    args, unknown = parser.parse_known_args()
    
    # 獲取原始命令行參數（用於兼容現有代碼）
    arguments = sys.argv
    
    return args, arguments

###########################################offline_check###########################################
async def offline_check(live_url, spare_link, rtmp_server, titleforgmail): # 離線檢測函數，監控直播狀態
    # 初始化計數器和狀態變量
    state = {
        'countdownhours': 0,  # 計時器，記錄運行時間
        'numberpart': 0,      # 備份流序號
        'gmailcount': 0,      # Gmail檢查計數器
        'countyt': 0,         # YouTube檢查計數器
        'live_url': live_url, # 當前直播URL
        'spare_link': spare_link, # 備用直播URL
        'rtmp_server': rtmp_server # RTMP服務器類型
    }
    
    # 記錄初始化監控服務信息
    logging.info(f"Initializing offline detection monitoring service... With {state['live_url']}, {state['spare_link']}, {state['rtmp_server']}, {titleforgmail}")
    
    async def handle_stream_offline(): # 處理直播離線的子函數
        logging.info("Stream offline status detected - initiating shutdown sequence... and play ending screen") # 記錄檢測到離線狀態
        rtmp_key = config.rtmp_key if state['rtmp_server'] == "bkrtmp" else config.rtmp_key_1
        ffmpeg_cmd = get_ffmpeg_command(rtmp_key) # 獲取ffmpeg命令
        os.system(ffmpeg_cmd) # 執行ffmpeg命令
        
        if config.unliststream == "True": # 如果需要設置為公開
            logging.info("Setting stream visibility to public...") # 記錄設置公開狀態
            public_stream(state['live_url']) # 設置YouTube直播為公開
            
        subprocess.run(["taskkill", "/f", "/im", config.apiexe]) # 關閉API進程
        subprocess.Popen(["start", "python", "check_tv.py", state['spare_link'], state['rtmp_server']], shell=True) # 啟動備用直播
        exit() # 退出當前進程

    
    async def handle_gmail_notification(): # 處理Gmail通知的子函數
        logging.info("Third-party notification detected - switching to backup stream...") # 記錄檢測到第三方通知
        await switch_stream_config(state, titleforgmail) # 切換直播配置
        state['gmailcount'] = 0 # 重置Gmail檢查計數

    
    async def handle_youtube_offline(): # 處理YouTube離線的子函數
        logging.info("Stream connection terminated - initiating reload sequence...") # 記錄直播連接中斷
        ffmpeg_exe = config.ffmpeg if state['rtmp_server'] == "bkrtmp" else config.ffmpeg1
        subprocess.run(["taskkill", "/f", "/im", ffmpeg_exe]) # 關閉對應的ffmpeg進程
        
        await asyncio.sleep(30) # 等待30秒
        if await check_and_handle_stream_status(state): # 檢查並處理直播狀態
            return True
        return False

    
    def get_ffmpeg_command(rtmp_key): # 獲取ffmpeg命令的輔助函數
        if config.ytshort == "True":
            return f'start {config.ffmpeg} -fflags +genpts -re -i ending.mp4 -c:v libx264 -preset veryfast -c:a aac -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}'
        return f'start {config.ffmpeg} -re -i ending.mp4 -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{rtmp_key}'

    while True: # 持續監控循環
        try:
            twitch = await get_twitch_client() # 獲取Twitch客戶端
            streams = await get_twitch_streams(twitch, config.username) # 獲取指定用戶的直播流
            
            if not streams: # 如果直播流不存在
                await handle_stream_offline() # 處理直播離線情況
                
            # 更新計數器
            state['countdownhours'] += 1
            state['gmailcount'] += 1
            state['countyt'] += 1
            
            # 檢查Gmail通知
            if state['gmailcount'] == 12: # 每60秒檢查一次Gmail通知
                if await find_gmail_title(titleforgmail) == "True":
                    await handle_gmail_notification()
                else:
                    state['gmailcount'] = 0
                    
            # 檢查YouTube直播狀態
            if state['countyt'] == 6: # 每30秒檢查一次YouTube直播狀態
                await handle_youtube_status(state)
                
            # 檢查是否需要定期切換直播
            if state['countdownhours'] == 7871: # 約12小時後切換直播
                await handle_scheduled_switch(state, titleforgmail)
                
            await asyncio.sleep(5) # 等待5秒後進行下一次檢查
            
        except Exception as e: # 捕獲異常
            logging.error(f"Error in offline check: {str(e)}", exc_info=True) # 記錄錯誤信息
            await asyncio.sleep(15) # 發生錯誤時等待15秒後重試


async def handle_youtube_status(state): # 處理YouTube狀態的輔助函數
    if is_youtube_livestream_live(state['live_url']) == "True":
        state['countyt'] = 0
        return
        
    if is_youtube_livestream_live(state['live_url']) == "False":
        twitch = await get_twitch_client()
        streams = await get_twitch_streams(twitch, config.username)
        if not streams:
            await handle_stream_offline()
        if not await handle_youtube_status(state):
            await switch_stream_config(state)
            
    if is_youtube_livestream_live(state['live_url']) == "ERROR":
        logging.info("YouTube API verification failed - check credentials and connectivity...")
        state['countyt'] = 0


async def switch_stream_config(state, titleforgmail=None): # 切換直播配置的輔助函數
    subprocess.run(["taskkill", "/f", "/im", config.apiexe])
    if titleforgmail:
        titleforgmail = await api_create_edit_schedule(state['numberpart'], state['rtmp_server'], "False", state['spare_link'])
    
    state['rtmp_server'] = "defrtmp" if state['rtmp_server'] == "bkrtmp" else "bkrtmp"
    live_spare_url = await api_create_edit_schedule("0", state['rtmp_server'], "True", "Null")
    
    subprocess.Popen(["start", config.apiexe], shell=True)
    if config.unliststream == "True":
        public_stream(state['live_url'])
        
    state['numberpart'] += 1
    state['live_url'], state['spare_link'] = state['spare_link'], live_spare_url
    state['countdownhours'] = 0
    state['countyt'] = 0


async def handle_scheduled_switch(state, titleforgmail): # 處理定期切換的輔助函數
    logging.info("Stream duration limit near 12h reached - initiating scheduled reload...")
    await switch_stream_config(state, titleforgmail)
    logging.info(state['rtmp_server'])


async def check_and_handle_stream_status(state): # 檢查並處理直播狀態的輔助函數
    logging.info("Checking for stream")
    if is_youtube_livestream_live(state['live_url']) == "True":
        return True
    return False


def public_stream(live_url): # 設置YouTube直播為公開
    logging.info("Setting stream visibility to public...") # 記錄設置公開狀態
    youtube = build('youtube', 'v3', credentials=get_credentials()) # 建立YouTube API客戶端
###########################################offline_check###########################################


async def get_twitch_client(): # 獲取Twitch API客戶端
    twitch = Twitch(config.client_id, config.client_secret) # 使用配置的客戶端ID和密鑰創建Twitch實例
    await twitch.authenticate_app([]) # 進行應用程序認證
        
    return twitch # 返回認證後的客戶端實例


async def get_twitch_streams(twitch, username): # 獲取指定用戶的Twitch直播流
    streams = [stream async for stream in twitch.get_streams(user_login=[username])] # 獲取直播流
    
    return streams # 返回直播流列表


async def get_twitch_stream_title(): # 獲取Twitch直播標題
    MAX_RETRIES = 3 # 設置最大重試次數
    RETRY_DELAY = 5 # 設置重試延遲時間（秒）
    for attempt in range(MAX_RETRIES): # 嘗試獲取直播標題
        try:
            twitch = await get_twitch_client() # 獲取Twitch客戶端
            streams = await get_twitch_streams(twitch, config.username) # 獲取直播流
            if not streams: # 如果沒有直播流
                logging.info(f"No streams found (attempt {attempt + 1}/{MAX_RETRIES})") # 記錄未找到直播
                await asyncio.sleep(RETRY_DELAY) # 等待指定時間
                continue 
            return streams[0].title # 返回直播標題
        except Exception as e: # 捕獲異常
            logging.error(f"Error getting Twitch stream info (attempt {attempt + 1}/{MAX_RETRIES}): {e}") # 記錄錯誤信息
            if attempt < MAX_RETRIES - 1: # 如果還有重試機會
                await asyncio.sleep(RETRY_DELAY) # 等待後重試
            else:
                logging.error("Max retries reached, returning fallback title") # 記錄達到最大重試次數
                return f"Stream_{datetime.now().strftime('%Y-%m-%d')}" # 返回默認標題


async def initialize_and_monitor_stream(yt_link=None, rtmp_info=None): # 綜合函數：處理參數、等待直播開始並監控
    try:
        # 處理命令行參數
        args, arguments = parse_arguments()  # 從parse_arguments函數獲取命令行參數
        
        if yt_link is None and rtmp_info is None:  # 如果沒有直接傳入參數，則從命令行獲取
            if len(arguments) < 2:  # 檢查是否有足夠的參數（排除調試標誌）
                logging.info("==================================================")  # 記錄分隔線
                logging.info("NO ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # 記錄無參數信息
                logging.info(f"ARCHIVE USER: {config.username}")  # 記錄歸檔用戶名
                logging.info("==================================================")  # 記錄分隔線
                
                yt_link = "Null"  # 設置默認YouTube鏈接
                rtmp_info = "Null"  # 設置默認RTMP服務器類型
            else:
                yt_link = arguments[1]  # 獲取第一個參數
                rtmp_info = arguments[2] if len(arguments) > 2 else None  # 獲取第二個參數，如果不存在則為None
                
                if yt_link == "KILL":  # 如果是終止命令
                    logging.info("close all exe")  # 記錄關閉所有進程
                    subprocess.run(["taskkill", "/f", "/im", config.apiexe])  # 關閉API進程
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg])  # 關閉主要ffmpeg進程
                    subprocess.run(["taskkill", "/f", "/im", config.ffmpeg1])  # 關閉備用ffmpeg進程
                    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])  # 關閉瀏覽器驅動進程
                    exit()  # 退出程序
                    
                if len(arguments) < 3:  # 檢查是否有第二個參數
                    logging.error("Missing required RTMP argument")  # 記錄缺少參數錯誤
                    exit(1)  # 以錯誤狀態退出
                    
                # 驗證參數
                if len(yt_link) != 11:  # 檢查yt_link是否為11個字符
                    logging.error(f"Invalid argument for ARG1: {yt_link}. Must be 11 characters long YouTube Video ID")  # 記錄無效的yt_link參數錯誤
                    exit(1)  # 以錯誤狀態退出
                    
                if rtmp_info not in ["defrtmp", "bkrtmp"]:  # 檢查RTMP參數是否有效
                    logging.error(f"Invalid argument for ARG2: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'")  # 記錄無效參數錯誤
                    exit(1)  # 以錯誤狀態退出
                    
                logging.info("==================================================")  # 記錄分隔線
                logging.info("INPUT ARGUMENT AVAILABLE (CONFIG VIEW IN CONFIG_TV.PY)")  # 記錄參數信息
                logging.info(f"ARG1: {yt_link} ARG2: {rtmp_info}")  # 記錄具體參數值
                logging.info(f"ARCHIVE USER: {config.username}")  # 記錄歸檔用戶名
                logging.info("==================================================")  # 記錄分隔線
        
        # 驗證RTMP服務器類型
        if rtmp_info not in ["defrtmp", "bkrtmp", "Null"]:
            logging.error(f"Invalid RTMP server type: {rtmp_info}. Must be 'defrtmp' or 'bkrtmp'")  # 記錄無效參數錯誤
            exit(1)  # 以錯誤狀態退出
            
        # 初始化直播URL和RTMP服務器類型
        live_url = None
        rtmp_server = None
        
        if yt_link == "Null":  # 如果沒有提供YouTube鏈接
            logging.info("Starting live API check to get initial stream URL")  # 記錄開始獲取初始URL
            rtmp_server = "defrtmp"  # 設置默認RTMP服務器
            try:
                live_url = await api_create_edit_schedule("0", rtmp_server, "True", "Null")  # 創建新的直播計劃
                logging.info(f"Successfully created new stream with URL: {live_url}")  # 記錄成功創建直播
            except Exception as api_error:
                logging.error(f"Failed to create stream via API: {str(api_error)}")  # 記錄API錯誤
                raise  # 重新拋出異常
        else:  # 如果提供了YouTube鏈接
            live_url = yt_link  # 使用提供的鏈接
            rtmp_server = rtmp_info  # 使用提供的RTMP服務器信息
            logging.info(f"Using provided YouTube link: {live_url} with RTMP server: {rtmp_server}")  # 記錄使用提供的鏈接
        
        # 等待Twitch直播開始
        logging.info("Waiting for stream to go live...")  # 記錄等待直播開始
        while True:  # 持續檢查直播狀態，無限循環直到找到直播
            try:
                twitch = await get_twitch_client()  # 獲取Twitch客戶端
                streams = await get_twitch_streams(twitch, config.username)  # 獲取直播流
                if streams:  # 如果找到直播流
                    stream = streams[0]  # 獲取第一個直播流
                    logging.info(f"Stream is now live! Title From Twitch: {stream.title}")  # 記錄直播開始
                    break  # 結束等待並繼續
                else:  # 如果沒有直播流
                    await asyncio.sleep(5)  # 等待5秒後重試
            except Exception as e:  # 捕獲異常
                logging.error(f"Error checking stream status: {str(e)}")  # 記錄錯誤信息
                await asyncio.sleep(30)  # 發生錯誤時等待30秒後重試
        
        logging.info("Twitch stream detected - initializing monitoring process")  # 記錄加載開始
        
        # 開始監控直播
        await start_check(live_url, rtmp_server)  # 開始檢查直播狀態
    except Exception as e:  # 捕獲異常
        logging.error(f"Error in initialize_and_monitor_stream: {str(e)}", exc_info=True)  # 記錄錯誤信息
        logging.error("Critical error encountered - terminating script execution")  # 記錄嚴重錯誤
        exit(1)  # 確保腳本以錯誤狀態退出

class TwitchResponseStatus(enum.Enum): # Twitch響應狀態枚舉類
    ONLINE = 0 # 在線狀態
    OFFLINE = 1 # 離線狀態
    NOT_FOUND = 2 # 未找到狀態
    UNAUTHORIZED = 3 # 未授權狀態
    ERROR = 4 # 錯誤狀態


def check_process_running(): # 檢查進程是否運行函數
    process_name = "countdriver.exe" # 要檢查的進程名稱
    logging.info("Checking for existing browser automation processes...") # 記錄開始檢查瀏覽器自動化進程
    for process in psutil.process_iter(['pid', 'name']): # 遍歷所有進程
        if process.info['name'] == process_name: # 如果找到目標進程
            logging.info("Browser automation process already running - waiting for completion...") # 記錄進程已在運行
            time.sleep(15) # 等待15秒
            check_process_running() # 遞歸檢查
    logging.info("No conflicting processes found - proceeding...") # 記錄未找到衝突進程
    return # 返回繼續執行

def get_service(): # 獲取Google API服務函數
    creds = None # 初始化憑證變量
    from google_auth_oauthlib.flow import InstalledAppFlow # 導入OAuth2流程模塊
    try:
        if os.path.exists(USER_TOKEN_FILE): # 如果用戶令牌文件存在
          # 從保存的文件加載用戶憑證
          if config.brandacc == "False":    
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES) # 加載一般用戶憑證
          if config.brandacc == "True":
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES_BRAND) # 加載品牌賬戶憑證
            
        if not creds or not creds.valid: # 如果憑證不存在或無效
            if creds and creds.expired and creds.refresh_token: # 如果憑證過期且可以刷新
                creds.refresh(Request()) # 刷新憑證
            else: # 如果需要重新授權
              if config.brandacc == "False": # 如果是一般用戶
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
              if config.brandacc == "True": # 如果是品牌賬戶
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="havebrand") # 運行本地服務器獲取憑證
              with open(USER_TOKEN_FILE, 'w') as token: # 保存憑證到文件
                token.write(creds.to_json()) # 寫入憑證JSON數據
                
        return build('youtube', 'v3', credentials=creds) # 返回YouTube API服務實例
    except Exception as e: # 捕獲異常
        if "invalid_grant" in str(e): # 如果是無效授權錯誤
              if config.brandacc == "False": # 如果是一般用戶
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
              if config.brandacc == "True": # 如果是品牌賬戶
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_BRAND, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="havebrand") # 運行本地服務器獲取憑證
              with open(USER_TOKEN_FILE, 'w') as token: # 保存憑證到文件
                token.write(creds.to_json()) # 寫入憑證JSON數據
              return build('youtube', 'v3', credentials=creds) # 返回YouTube API服務實例
        else: # 如果是其他錯誤
          logging.error(f"Error in get_service: {e}") # 記錄錯誤信息
          exit(1) # 退出程序

def get_gmail_service(): # 獲取Gmail API服務函數
    creds = None # 初始化憑證變量
    from google_auth_oauthlib.flow import InstalledAppFlow # 導入OAuth2流程模塊
    try:
        if config.brandacc == "True": # 如果是品牌賬戶
          if os.path.exists(GMAIL_TOKEN_FILE): # 如果Gmail令牌文件存在
            creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES_GMAIL) # 加載Gmail憑證
        if config.brandacc == "False": # 如果是一般用戶
          if os.path.exists(USER_TOKEN_FILE): # 如果用戶令牌文件存在
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES) # 加載用戶憑證
            
        if not creds or not creds.valid: # 如果憑證不存在或無效
            if creds and creds.expired and creds.refresh_token: # 如果憑證過期且可以刷新
                creds.refresh(Request()) # 刷新憑證
            else: # 如果需要重新授權
              if config.brandacc == "True": # 如果是品牌賬戶
                logging.info("Gmail token not found. Starting authentication flow...") # 記錄開始認證流程
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
                with open(GMAIL_TOKEN_FILE, 'w') as token: # 保存Gmail憑證到文件
                   token.write(creds.to_json()) # 寫入憑證JSON數據
              if config.brandacc == "False": # 如果是一般用戶
                logging.info("Gmail token not found. Start...") # 記錄開始認證流程
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建OAuth2流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
                with open(USER_TOKEN_FILE, 'w') as token: # 保存用戶憑證到文件
                   token.write(creds.to_json()) # 寫入憑證JSON數據
                
        return build('gmail', 'v1', credentials=creds) # 返回Gmail API服務實例
        
    except Exception as e: # 捕獲異常
        if "invalid_grant" in str(e): # 如果是無效授權錯誤
              if config.brandacc == "True": # 如果是品牌賬戶
                logging.info("Gmail token not found. Starting authentication flow...") # 記錄開始Gmail認證流程
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES_GMAIL, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建Gmail認證流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
                with open(GMAIL_TOKEN_FILE, 'w') as token: # 打開Gmail令牌文件
                   token.write(creds.to_json()) # 保存憑證到文件
              if config.brandacc == "False": # 如果是一般用戶
                logging.info("Gmail token not found. Starting authentication flow...") # 記錄開始Gmail認證流程
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob') # 創建一般用戶認證流程
                creds = flow.run_local_server(port=6971, brandacc="Nope") # 運行本地服務器獲取憑證
                with open(USER_TOKEN_FILE, 'w') as token: # 打開用戶令牌文件
                   token.write(creds.to_json()) # 保存憑證到文件      
              return build('gmail', 'v1', credentials=creds) # 返回Gmail API服務實例
        else: # 如果是其他錯誤
          logging.error(f"Error in get_gmail_service: {e}") # 記錄Gmail服務錯誤
          exit(1) # 退出程序

def is_youtube_livestream_live(video_id): # 檢查YouTube直播狀態的函數
    try: # 嘗試獲取直播流
      streams = streamlink.streams(f"https://youtube.com/watch?v={video_id}") # 獲取指定視頻ID的直播流
      hls_stream = streams["best"] # 獲取最佳質量的流
      return "True" # 返回直播在線狀態
    except KeyError as e: # 如果找不到直播流
        return "False" # 返回直播離線狀態
    except Exception as e: # 捕獲其他異常
      logging.error(f"Error checking YouTube livestream status: {e}") # 記錄錯誤信息
      return "ERROR" # 返回錯誤狀態

async def find_gmail_title(title): # 在Gmail中查找特定標題的異步函數
    while True: # 持續檢查循環
        try: # 嘗試查找標題
            title1 = f"：{title}" # 構建完整標題字符串
            service = get_gmail_service() # 獲取Gmail服務實例
            # 獲取當前時間和前2分鐘的時間
            now = datetime.now() # 獲取當前時間
            minutes_ago = now - timedelta(minutes=2) # 計算2分鐘前的時間
            # 獲取最新的2條消息
            results = service.users().messages().list(userId='me', maxResults=2).execute() # 獲取郵件列表
            messages = results.get('messages', []) # 提取郵件信息
            # 處理最新的消息
            if messages: # 如果有郵件
                for message in messages: # 遍歷每條郵件
                    msg = service.users().messages().get(userId='me', id=message['id']).execute() # 獲取完整郵件內容
                    # 將internalDate轉換為datetime對象
                    received_time = datetime.fromtimestamp(int(msg['internalDate']) / 1000) # 轉換郵件接收時間
                    # 獲取郵件主題行
                    subject = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), '') # 提取郵件主題
                    # 檢查郵件是否在最近2分鐘內收到，且標題包含指定文字
                    if received_time >= minutes_ago and title1 in subject: # 檢查時間和標題匹配
                        logging.info(f"Found message: {subject}") # 記錄找到匹配的郵件
                        return "True" # 返回找到標題
            return "False" # 返回未找到標題
        except Exception as e: # 捕獲異常
            logging.error(f"Error in find_gmail_title: {e}") # 記錄錯誤信息
            await asyncio.sleep(5)  # 等待5秒後重試

def edit_live_stream(video_id, new_title, new_description): # 編輯直播流信息的函數
  hitryagain = 0 # 重試計數器
  while True: # 持續嘗試循環
    try: # 嘗試更新直播信息
       service = get_service() # 獲取YouTube服務實例
       category_id = '24' # 設置視頻分類ID
           
       request = service.videos().update( # 創建更新請求
             part="snippet", # 更新視頻詳情部分
             body={
                 "id": video_id, # 設置視頻ID
                 "snippet": {
                     "title": new_title,  # 設置新標題
                     "description": new_description,  # 設置新描述
                     "categoryId": category_id # 設置分類ID
            }
        }
    )
       response = request.execute() # 執行更新請求
       return response['id'] # 返回視頻ID
       break # 跳出循環
    except Exception as e: # 捕獲異常
     if hitryagain == 3: # 如果重試次數達到3次
      logging.info(f"Error and stoping because of error that can't fix") # 記錄無法修復的錯誤
      if 'quotaExceeded' in str(e): # 如果是配額超限錯誤
        logging.info(f"Error and stoping because of api limited") # 記錄API限制錯誤
        exit() # 退出程序
     hitryagain += 1 # 增加重試計數
     logging.info(f"Error: {e}") # 記錄錯誤信息
     time.sleep(5) # 等待5秒後重試

def public_stream(live_id): # 將YouTube直播設為公開的函數
  hitryagain = 0 # 重試計數器初始化為0
  while True: # 持續嘗試循環
    try: # 嘗試執行以下操作
       service = get_service() # 獲取YouTube API服務實例
       request = service.videos().update( # 創建更新視頻狀態的請求
           part='status', # 指定要更新的部分為狀態
           body={ # 請求主體
               'id': live_id, # 設置視頻ID
               'status': { # 狀態設置
                   'privacyStatus': 'public' # 將隱私狀態設為公開
               }
           }
       )
       response = request.execute() # 執行API請求
       return response['id'] # 返回視頻ID
       break # 跳出循環
    except Exception as e: # 捕獲可能發生的異常
     if hitryagain == 3: # 如果重試次數達到3次
      logging.info(f"Error and stoping because of error that can't fix") # 記錄無法修復的錯誤
      if 'quotaExceeded' in str(e): # 如果是API配額超限錯誤
        logging.info(f"Error and stoping because of api limited") # 記錄API限制錯誤
        exit() # 退出程序
     hitryagain += 1 # 增加重試計數
     logging.info(f"Error: {e}") # 記錄錯誤信息
     time.sleep(5) # 等待5秒後重試

def create_live_stream(title, description, kmself):
    logging.info(f"{title}, {description}, {kmself}") # 創建直播流的函數
    hitryagain = 0 # 重試計數器
    while True: # 持續嘗試循環
        try: # 嘗試創建直播
            service = get_service() # 獲取YouTube服務實例
            scheduled_start_time = datetime.now(timezone.utc).isoformat() # 獲取UTC時間作為計劃開始時間
                
            request = service.liveBroadcasts().insert( # 創建直播廣播請求
                part="snippet,status,contentDetails", # 設置請求部分
                body={
                    "snippet": { # 視頻基本信息
                        "title": title, # 設置標題
                        "description": description, # 設置描述
                        "scheduledStartTime": scheduled_start_time, # 設置開始時間
                    },
                    "status": { # 視頻狀態設置
                        "privacyStatus": kmself, # 設置隱私狀態
                        "selfDeclaredMadeForKids": False # 設置非兒童內容
                    },
                    "contentDetails": { # 內容詳情設置
                        "enableAutoStart": True, # 啟用自動開始
                        "enableAutoStop": True, # 啟用自動停止
                        "latencyPrecision": "ultraLow" # 設置超低延遲
                    }
                }
            )
            response = request.execute() # 執行創建請求
            video_id = response['id'] # 獲取視頻ID
            
            # 如果配置了播放列表則添加到播放列表
            if config.playlist == "True" or config.playlist == "DOUBLE": # 檢查是否需要添加到播放列表
                try: # 嘗試添加到第一個播放列表
                    playlist_request = service.playlistItems().insert( # 創建添加到播放列表請求
                        part="snippet", # 設置請求部分
                        body={
                            "snippet": {
                                "playlistId": config.playlist_id0, # 設置播放列表ID
                                "resourceId": {
                                    "kind": "youtube#video", # 設置資源類型
                                    "videoId": video_id # 設置視頻ID
                                }
                            }
                        }
                    )
                    playlist_request.execute() # 執行添加請求
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id0}") # 記錄成功添加到播放列表
                except Exception as playlist_error: # 捕獲播放列表錯誤
                    logging.error(f"Failed to add video to playlist: {playlist_error}") # 記錄添加失敗
            if config.playlist == "DOUBLE": # 如果需要添加到第二個播放列表
                try: # 嘗試添加到第二個播放列表
                    playlist_request = service.playlistItems().insert( # 創建添加到播放列表請求
                        part="snippet", # 設置請求部分
                        body={
                            "snippet": {
                                "playlistId": config.playlist_id1, # 設置第二個播放列表ID
                                "resourceId": {
                                    "kind": "youtube#video", # 設置資源類型
                                    "videoId": video_id # 設置視頻ID
                                }
                            }
                        }
                    )
                    playlist_request.execute() # 執行添加請求
                    logging.info(f"Successfully added video {video_id} to playlist {config.playlist_id1}") # 記錄成功添加到第二個播放列表
                except Exception as playlist_error: # 捕獲播放列表錯誤
                    logging.error(f"Failed to add video to playlist: {playlist_error}") # 記錄添加失敗
            return video_id # 返回視頻ID
        except Exception as e: # 捕獲異常
          if hitryagain == 3: # 如果重試次數達到3次
           logging.info(f"Error and stoping because of error that can't fix") # 記錄無法修復的錯誤
           if 'quotaExceeded' in str(e): # 如果是配額超限錯誤
            logging.info(f"Error and stoping because of api limited") # 記錄API限制錯誤
            exit() # 退出程序
          hitryagain += 1 # 增加重試計數
          logging.info(f"Error: {e}") # 記錄錯誤信息
          time.sleep(5) # 等待5秒後重試

def api_load(url, brandacc): # API加載函數
      logging.basicConfig(filename="tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S') # 配置日誌記錄
      logging.getLogger().addHandler(logging.StreamHandler()) # 添加控制台輸出處理器
      logging.info("create api keying ---edit_tv---") # 記錄開始創建API密鑰
      home_dir = os.path.expanduser("~") # 獲取用戶主目錄
      logging.info("run with countdriver.exe and check") # 記錄運行驅動程序
      check_process_running() # 檢查進程是否運行
      subprocess.Popen(["start", "countdriver.exe"], shell=True) # 啟動驅動程序進程
      options = Options()
      chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data") # 設置Chrome用戶數據目錄
      options.add_argument(f"user-data-dir={chrome_user_data_dir}") # 添加用戶數據目錄參數
      options.add_argument(f"profile-directory={config.Chrome_Profile}") # 添加配置文件目錄參數
      notafrickdriver = webdriver.Chrome(options=options) # 創建Chrome瀏覽器實例
      notafrickdriver.get(url) # 訪問指定URL
      time.sleep(3) # 等待頁面加載
      if brandacc == "Nope": # 如果是一般賬戶
          nameofaccount = f"//div[contains(text(),'{config.accountname}')]"
      if brandacc == "havebrand": # 如果是品牌賬戶
          nameofaccount = f"//div[contains(text(),'{config.brandaccname}')]"
      button_element = notafrickdriver.find_element("xpath", nameofaccount) # 查找賬戶元素
      button_element.click() # 點擊賬戶元素
      time.sleep(3) # 等待操作完成
      element = notafrickdriver.find_element("xpath", "(//button[@jsname='LgbsSe' and contains(@class, 'VfPpkd-LgbsSe-OWXEXe-INsAgc')])[2]") # 查找按鈕元素
      element.click() # 點擊按鈕
      subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # 終止驅動程序進程
      logging.info("finish idk ---edit_tv---") # 記錄完成信息
      time.sleep(5) # 等待操作完成
      notafrickdriver.quit() # 關閉瀏覽器實例

def edit_rtmp_key(driver, rtmp_key_select): # 編輯RTMP密鑰的函數
 countfuckingshit = 0 # 錯誤計數器
 while True: # 持續嘗試循環
  try: # 嘗試編輯RTMP密鑰
    driver.find_element(By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']").click() # 點擊下拉菜單
    time.sleep(3) # 等待菜單顯示
    if rtmp_key_select == "bkrtmp": # 如果使用備用RTMP
        xpath = "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname1 + " (')]]"
        element2 = driver.find_element(By.XPATH, xpath) # 查找備用RTMP元素
        element2.click() # 點擊選擇備用RTMP
        time.sleep(7) # 等待操作完成
    if rtmp_key_select == "defrtmp": # 如果使用默認RTMP
        xpath = "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname + " (')]]"
        element3 = driver.find_element(By.XPATH, xpath) # 查找默認RTMP元素
        element3.click() # 點擊選擇默認RTMP
        time.sleep(7) # 等待操作完成
    if config.disablechat == "True": # 如果需要禁用聊天
        driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click() # 點擊編輯按鈕
        time.sleep(3) # 等待編輯界面
        driver.find_element(By.XPATH, "//li[@id='customization']").click() # 點擊自定義選項
        time.sleep(2) # 等待選項加載
        driver.find_element(By.XPATH, "//*[@id='chat-enabled-checkbox']").click() # 點擊聊天開關
        time.sleep(1) # 等待狀態更新
        driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click() # 保存設置
    time.sleep(10) # 等待所有操作完成
    logging.info("RTMP key configuration updated successfully...") # 記錄更新成功
    driver.quit() # 關閉瀏覽器
    subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # 終止驅動程序
  except Exception as e: # 捕獲異常
        logging.error(f"Error in edit_rtmp_key: {str(e)}") # 記錄詳細錯誤信息
        driver.refresh() # 重新整理瀏覽器頁面
        time.sleep(15) # 等待15秒
        countfuckingshit += 1 # 增加錯誤計數器
        if countfuckingshit == 3: # 如果錯誤次數達到3次
          logging.info("edit rtmp key fail shutdown script") # 記錄RTMP密鑰編輯失敗,關閉腳本
          subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"]) # 強制終止驅動程序
          exit() # 退出程序
  finally:
    break # 跳出循環

def check_is_live_api(url, ffmpeg, rtmp_server): # 檢查直播API是否正常運作的函數
      logging.info("Waiting for 40sec live on YouTube") # 記錄等待檢查
      time.sleep(40) # 等待40秒
      new_url = f"https://youtube.com/watch?v={live_url}"
      count_error = 0 # 初始化錯誤計數器
      MAX_RETRIES = 3  # 設置最大重試次數
      text = "this" if rtmp_server == "bkrtmp" else "api_this"
      while True: # 持續檢查循環
            try: # 嘗試獲取直播流
                  streams = streamlink.streams(new_url) # 獲取直播流
                  hls_stream = streams["best"] # 獲取最佳品質的流
                  logging.info('It is live now') # 記錄直播開始
                  break # 跳出循環
            except KeyError as e: # 捕獲密鑰錯誤
                  logging.error(f'Stream not available: {str(e)}') # 記錄流不可用錯誤
                  logging.info('The stream is messed up. Trying again...') # 記錄重試信息
                  time.sleep(2) # 等待2秒
                  subprocess.run(["taskkill", "/f", "/im", ffmpeg]) # 終止ffmpeg進程
                  subprocess.Popen(["start", "python", "relive_tv.py", text], shell=True) # 重啟直播程序
                  time.sleep(35) # 等待35秒
                  count_error += 1 # 增加錯誤計數
            if count_error >= MAX_RETRIES: # 如果超過最大重試次數
                  logging.info("Retry limit exceeded. Shutting down.") # 記錄超過重試限制
                  subprocess.Popen(["start", "python", "check_tv.py", "KILL"], shell=True) # 啟動關閉程序
                  exit() # 退出程序

async def api_create_edit_schedule(part_number, rtmp_server, is_reload, stream_url): # 創建和編輯直播計劃的異步函數
    filename = None # 初始化文件名變量
    description = None # 初始化描述變量
    
    if is_reload == "False" or is_reload == "EDIT": # 如果不是重載模式或是編輯模式
        # 獲取Twitch直播標題
        stream_title = await get_twitch_stream_title()
        
        # 處理標題格式
        clean_title = ''.join('' if unicodedata.category(c) == 'So' else c for c in stream_title)
        clean_title = clean_title.replace("<", "").replace(">", "")
        
        # 構建檔案名稱
        if part_number == "0": # 如果是從selwebdriver調用（無分段）
            filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}"
        else: # 如果是分段模式
            part_num = int(part_number) + 1
            filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')} | PART{part_num}"
        
        # 處理檔案名稱長度
        if len(filename) > 100:
            # 計算最大標題長度
            if part_number == "0": # 無分段模式
                max_title_len = 100 - len(config.username) - len(datetime.now().strftime("%Y-%m-%d")) - len(" | " * 2)
            else: # 分段模式
                max_title_len = 100 - len(config.username) - len(datetime.now().strftime("%Y-%m-%d")) - len(" | " * 3) - len(f"part {part_num}")
            
            clean_title = clean_title[:max_title_len-3] + "..."
            
            # 重新構建文件名
            if part_number == "0": # 無分段模式
                filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')}"
            else: # 分段模式
                filename = f"{config.username} | {clean_title} | {datetime.now().strftime('%Y-%m-%d')} | part {part_num}"
            
        if len(filename) > 100: # 如果文件名仍然過長
            if part_number == "0": # 無分段模式
                filename = f"{config.username} | {datetime.now().strftime('%Y-%m-%d')}"
            else: # 分段模式
                filename = f"{config.username} | {datetime.now().strftime('%Y-%m-%d')} | part {part_num}"
            
        # 設置描述（請勿移除水印）
        description = f"Original broadcast from https://twitch.tv/{config.username} [Stream Title: {clean_title}] Archived using open-source tools: https://bit.ly/archivescript Service by Karsten Lee, Join Karsten Lee's Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"

    try:
        # 處理重載模式
        if is_reload == "True":
            filename = f"{config.username} (WAITING FOR STREAMER)"
            description = f"WAITING FOR {config.username}, THIS OPEN-SOURCE ARCHIVE SCRIPT IS CREATED BY KARSTEN LEE, PROJECT: https://is.gd/archivescript , Join Karsten Lee's Discord Server(discussion etc./I need help for coding :helpme:): https://discord.gg/Ca3d8B337v"
            
        # 創建新直播
        if stream_url == "Null":
            logging.info('Initiating API request for stream creation...')
            privacy_status = "public" if config.unliststream == "False" else "unlisted"
            stream_url = create_live_stream(filename, description, privacy_status)
            
            # 記錄直播創建信息
            logging.info("==================================================")
            if config.playlist == "True":
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0}")
            elif config.playlist == "DOUBLE":
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url} AND ADD TO PLAYLIST: {config.playlist_id0} AND {config.playlist_id1}")
            else:
                logging.info(f"LIVE STREAM SCHEDULE CREATED: {stream_url}")
            logging.info("==================================================")
            
            # 設置RTMP和聊天配置
            await setup_stream_settings(stream_url, rtmp_server)
            
        if is_reload == "EDIT":
                # 更新現有直播
                logging.info("Updating stream metadata and title...")
                edit_live_stream(stream_url, filename, description)
                return filename

        if is_reload == "True":
                return stream_url

            # 如果是從selwebdriver調用（非重載模式且有直播URL），檢查直播狀態
        if is_reload == "False":
                await initialize_stream_relay(stream_url, rtmp_server) # 初始化直播轉發
                if rtmp_server == "bkrtmp":
                    check_is_live_api(stream_url, config.ffmpeg1, "api_this")
                if rtmp_server == "defrtmp":
                    check_is_live_api(stream_url, config.ffmpeg, "this")
        
    except Exception as e:
        logging.error(f"Critical error encountered during execution: {e}")
        exit()

async def setup_stream_settings(stream_url, rtmp_server):
    # 設置瀏覽器配置
    check_process_running()
    subprocess.Popen(["start", "countdriver.exe"], shell=True)
    options = Options()
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")
    options.add_argument(f"user-data-dir={chrome_user_data_dir}")
    options.add_argument(f"profile-directory={config.Chrome_Profile}")
    
    # 啟動瀏覽器並配置設置
    driver = None  # 初始化driver變數
    try:
        driver = webdriver.Chrome(options=options)
        url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"
        driver.get(url_to_live)
        await asyncio.sleep(5)
        driver.refresh()
        await asyncio.sleep(30)
        
        logging.info("Configuring RTMP key and chat settings...")
        edit_rtmp_key(driver, rtmp_server)
        
    finally:
        if driver:  # 確保driver已初始化才調用quit方法
            driver.quit()
        subprocess.run(["taskkill", "/f", "/im", "countdriver.exe"])

async def initialize_stream_relay(stream_url, rtmp_server):
    # 啟動直播轉發
    rtmp_server1 = "this" if rtmp_server == "bkrtmp" else "api_this"
    subprocess.Popen(["start", "python", "relive_tv.py", rtmp_server1], shell=True)
    
    ffmpeg_exe = config.ffmpeg if rtmp_server == "bkrtmp" else config.ffmpeg1
    check_is_live_api(stream_url, ffmpeg_exe, rtmp_server1)
    
    # 切換到黑屏
    subprocess.run(["taskkill", "/f", "/im", ffmpeg_exe])
    
    # 啟動黑屏直播
    rtmp_key = config.rtmp_key if rtmp_server == "bkrtmp" else config.rtmp_key_1
    if config.ytshort == "True":
        # 使用subprocess啟動新進程執行短視頻格式的ffmpeg命令
        subprocess.Popen([config.ffmpeg, "-fflags", "+genpts", "-re", "-i", "blackscreen.mp4", 
                         "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
                         "-filter_complex", "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2",
                         "-f", "flv", f"rtmp://a.rtmp.youtube.com/live2/{rtmp_key}"])
    else:
        # 使用subprocess啟動新進程執行標準格式的ffmpeg命令
        subprocess.Popen([config.ffmpeg, "-re", "-i", "blackscreen.mp4", 
                         "-c", "copy", "-f", "flv", 
                         f"rtmp://a.rtmp.youtube.com/live2/{rtmp_key}"])

def fetch_access_token(): # 獲取訪問令牌的函數
        token_response = requests.post(token_url, timeout=15) # 發送POST請求獲取令牌
        token_response.raise_for_status() # 檢查響應狀態
        token = token_response.json() # 解析JSON響應
        return token["access_token"] # 返回訪問令牌牌

# checkarg函數已合併到initialize_and_monitor_stream函數中

async def start_check(live_url, rtmp_server): # 開始檢查直播狀態
    logging.info("Starting stream monitoring process...") # 記錄開始監控進程
    
    # 驗證參數
    if not live_url:
        logging.error("Missing live URL - cannot start monitoring") # 記錄錯誤
        exit(1) # 以錯誤狀態退出
        
    if rtmp_server not in ["defrtmp", "bkrtmp"]:
        logging.error(f"Invalid RTMP server type: {rtmp_server}") # 記錄錯誤
        exit(1) # 以錯誤狀態退出
    
    # 啟動API進程
    logging.info("Launching streaming API process...") # 記錄啟動API進程
    try:
        subprocess.Popen(["start", config.apiexe], shell=True) # 啟動API程序
    except Exception as e:
        logging.error(f"Failed to start API process: {str(e)}") # 記錄錯誤
        exit(1) # 以錯誤狀態退出
    
    try:
        if rtmp_server == "bkrtmp": # 如果使用備用RTMP
            logging.info("Starting scheduled stream relay...") # 記錄開始計劃的流轉發
            subprocess.Popen(["start", "python", "relive_tv.py", "api_this"], shell=True) # 啟動備用轉發
            rtmp_server = "defrtmp" # 設置輸入端口為默認RTMP
        elif rtmp_server == "defrtmp": # 如果使用默認RTMP
            logging.info("Starting alternate stream relay...") # 記錄開始替代流轉發
            subprocess.Popen(["start", "python", "relive_tv.py", "this"], shell=True) # 啟動主要轉發
            rtmp_server = "bkrtmp" # 設置輸入端口為備用RTMP
    except Exception as e:
        logging.error(f"Failed to start relay process: {str(e)}") # 記錄錯誤
        exit(1) # 以錯誤狀態退出
    
    logging.info(f"Stream URL configured: {live_url}") # 記錄配置的直播URL
    logging.info("Stream relay process started successfully") # 記錄轉發進程啟動成功
    
    # 獲取Gmail標題For Third Party Detection
    url_live = live_url
    try:
        titleforgmail = await api_create_edit_schedule("0", rtmp_server, "EDIT", live_url) # 獲取Gmail標題
        logging.info('edit finished continue the stream') # 記錄編輯完成    
        logging.info(f"Successfully retrieved stream title: {titleforgmail}") # 記錄成功獲取標題
    except UnboundLocalError: # 捕獲未綁定局部變量錯誤
        logging.warning("Encountered UnboundLocalError when getting title - continuing with default") # 記錄警告
    except Exception as e:
        logging.error(f"Error getting stream title: {str(e)} - continuing with default") # 記錄錯誤
    
    # 創建備用直播計劃
    live_spare_url = None
    try:
        logging.info("Loading backup stream configuration...") # 記錄加載備用配置
        live_spare_url = await api_create_edit_schedule("0", rtmp_server, "True", "Null") # 創建備用直播計劃
        logging.info(f"Backup stream URL configured: {live_spare_url}") # 記錄備用直播URL
    except Exception as e:
        logging.error(f"Failed to create backup stream: {str(e)}") # 記錄錯誤
        # 即使沒有備用直播，也繼續主直播監控
    
    logging.info("Starting offline detection and countdown timer...") # 記錄開始等待離線並計時
    await offline_check(live_url, live_spare_url, rtmp_server, titleforgmail) # 開始離線檢查

if __name__ == "__main__": # 主程序入口
    logging.basicConfig(filename="check_tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S') # 配置日誌
    logging.getLogger().addHandler(logging.StreamHandler()) # 添加控制台日誌處理器
    asyncio.run(initialize_and_monitor_stream()) # 運行初始化和監控流程
    exit() # 退出程序
