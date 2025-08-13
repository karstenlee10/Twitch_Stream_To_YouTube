import os
import sys
from logger_config import relive_tv_logger as logging # Importing logging module for logging messages
import time
import psutil
import config_tv as config
import streamlink

arguments = sys.argv
apiexe = f"taskkill /f /im {config.apiexe}"
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
            return True
        logging.info('api exe stop')
        return False
    except KeyError:
        trytimes += 1
        time.sleep(5)
        if trytimes == 6:
            logging.info('The stream is finsh')
            return False

def api_this():
  logging.info('script is started now api')
  command = f"{live_link_url} best -o - | {config.ffmpeg1} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{config.rtmp_key_1}"
  os.system(command)
  OMG = check_is_live()
  if OMG:
    logging.info("steam got down restart")
    api_this()
  else:
    logging.info('stream has finish no loop it and kill countdown')
    os.system(apiexe)

def this():
  logging.info('script is started now')
  command = f"{live_link_url} best -o - | {config.ffmpeg} -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/{config.rtmp_key}"
  os.system(command)
  OMG = check_is_live()
  if OMG:
    logging.info("steam got down restart")
    this()
  else:
    logging.info('stream has finish no loop it and kill countdown')
    os.system(apiexe)

def local_save(title):
  counter = 0
  script_dir = os.path.dirname(os.path.abspath(__file__))
  archive_dir = os.path.join(script_dir, "local_archive")
  if not os.path.exists(archive_dir):
      os.makedirs(archive_dir)
  filename = os.path.join(archive_dir, f"{title}.mp4")
  while os.path.exists(filename):
      counter += 1
      filename = os.path.join(archive_dir, f"{title}({counter}).mp4")
  command = f"{live_link_url} best -o {filename}"
  os.system(command)

arg1 = arguments[1]
if arg1 == "api_this":
  api_this()
elif arg1 == "this":
  this()
else:
  local_save(arg1)


