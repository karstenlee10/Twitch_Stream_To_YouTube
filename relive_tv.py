import os
import sys
import time

import psutil
import streamlink

import config_tv as config
from logger_config import relive_tv_logger as logging # Importing logging module for logging messages


arguments = sys.argv
apiexe = f"taskkill /f /im {config.apiexe}"
#twitch_token = token_key.token
#print(twitch_token)
live_link_url = f'streamlink https://www.twitch.tv/{config.username}'

def check_is_live():
  trytimes = 0
  while True:
    try:
        streams = streamlink.streams("https://www.twitch.tv/" + config.username)
        hls_stream = streams["best"]
        process_name = config.apiexe
        for process in psutil.process_iter(['pid', 'name']):
          if process.info['name'] == process_name:
            logging.info('api exe still here')
            return "True"
        logging.info('api exe stop')
        return "False"
    except KeyError:
        trytimes += 1
        time.sleep(5)
        if trytimes == 6:
            logging.info('The stream is finsh')
            return "False"

def api_this():
  logging.info('script is started now api')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  command = f"{live_link_url} best -o - | {config.ffmpeg1} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{config.rtmp_key_1}"
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logging.info("steam got down restart")
    api_this()
  else:
    logging.info('stream has finish no loop it and kill countdown')
    os.system(apiexe)

def this():
  logging.info('script is started now')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  command = f"{live_link_url} best -o - | {config.ffmpeg} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{config.rtmp_key}"
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logging.info("steam got down restart")
    this()
  else:
    logging.info('stream has finish no loop it and kill countdown')
    os.system(apiexe)

arg1 = arguments[1]
if arg1 == "api_this":
  api_this()
if arg1 == "this":
  this()
