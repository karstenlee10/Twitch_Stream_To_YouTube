import os
import sys
import logging
import time
import psutil
import config_tv as config
import streamlink

arguments = sys.argv
apiexe = "taskkill /f /im " + config.apiexe
live_link_url = "streamlink https://www.twitch.tv/" + config.username
def check_is_live():
  trytimes = 0
  while True:
    try:
        streams = streamlink.streams("https://www.twitch.tv/" + config.username)
        hls_stream = streams["best"]
        process_name = config.apiexe
        for process in psutil.process_iter(['pid', 'name']):
          if process.info['name'] == process_name:
            logging.info('API process is still running')
            return "True"
        logging.info('API process has terminated')
        return "False"
    except KeyError:
        trytimes += 1
        time.sleep(5)
        if trytimes == 6:
            logging.info('Stream has ended - no active broadcast detected')
            return "False"

def api_this():
  logging.info('Starting API stream processing')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  if config.ytshort == "True":
    command = live_link_url + ' best -o - | ' + config.ffmpeg1 + ' -fflags +genpts -re -i pipe:0 -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -c:v h264_qsv -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1
  if config.ytshort == "False":
    command = live_link_url + ' best -o - | ' + config.ffmpeg1 + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logging.info("Stream interrupted - initiating restart procedure")
    api_this()
  else:
    logging.info('Stream completed - terminating process and cleanup')
    os.system(apiexe)

def this():
  logging.info('Initializing stream processing')
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  if config.ytshort == "True":
    command = live_link_url + ' best -o - | ' + config.ffmpeg + ' -fflags +genpts -re -i pipe:0 -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -c:v h264_qsv -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key
  if config.ytshort == "False":
    command = live_link_url + ' best -o - | ' + config.ffmpeg + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key
  os.system(command)
  OMG = check_is_live()
  if OMG == "True":
    logging.info("Stream interrupted - initiating restart procedure")
    this()
  else:
    logging.info('Stream completed - terminating process and cleanup')
    os.system(apiexe)

logging.basicConfig(filename="relive_tv.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler())
arg1 = arguments[1]
if arg1 == "api_this":
  api_this()
if arg1 == "this":
  this()
exit()
