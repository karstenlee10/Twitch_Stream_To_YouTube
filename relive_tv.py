import os
import sys
import time

import streamlink

import config_tv as config
from logger import logger


arguments = sys.argv
apiexe = "taskkill /f /im " + config.apiexe
live_link_url = "streamlink https://www.twitch.tv/" + config.username
def check_is_live():
  trytimes = 0
  while True:
    try:
        streams = streamlink.streams("https://www.twitch.tv/" + config.username)
        hls_stream = streams["best"]
        return "False"
    except KeyError:
        trytimes += 1
        time.sleep(5)
        if trytimes == 6:
            logger.info('Stream has ended - no active broadcast detected')
            return "False"

def api_this():
  logger.info('Starting API stream processing')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  command = live_link_url + ' best -o - | ' + config.ffmpeg1 + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logger.info("Stream interrupted - initiating restart procedure")
    api_this()
  else:
    logger.info('Stream completed - terminating process and cleanup')
    os.system(apiexe)

def this():
  logger.info('Initializing stream processing')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  command = live_link_url + ' best -o - | ' + config.ffmpeg + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logger.info("Stream interrupted - initiating restart procedure")
    this()
  else:
    logger.info('Stream completed - terminating process and cleanup')
    os.system(apiexe)


def restream(mode: str) -> None:
  if mode == "api_this":
    api_this()
  elif mode == "this":
    this()
