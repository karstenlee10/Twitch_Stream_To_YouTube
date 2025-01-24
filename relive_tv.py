import os
import sys
import logging
import time
import psutil
import config_tv as config
import streamlink

arguments = sys.argv
apiexe = "taskkill /f /im " + config.apiexe
if config.BiliBili == "True":
  live_link_url = 'streamlink https://live.bilibili.com/' + config.bilibililiveuid
if config.Twitch == "True":
  live_link_url = "streamlink https://www.twitch.tv/" + config.username
def check_is_live():
  trytimes = 0
  while True:
    try:
        if config.Twitch == "True":
          streams = streamlink.streams("https://www.twitch.tv/" + config.username)
        if config.BiliBili == "True":
          streams = streamlink.streams("https://live.bilibili.com/" + config.bilibililiveuid)
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
  if config.ytshort == "True":
    command = live_link_url + ' best -o - | ' + config.ffmpeg1 + ' -fflags +genpts -re -i pipe:0 -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -c:v h264_qsv -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1
  if config.ytshort == "False":
    command = live_link_url + ' best -o - | ' + config.ffmpeg1 + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key_1
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
  if config.ytshort == "True":
    command = live_link_url + ' best -o - | ' + config.ffmpeg + ' -fflags +genpts -re -i pipe:0 -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -filter_complex "[0:v]scale=1080:600,setsar=1[video];color=black:1080x1920[scaled];[scaled][video]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" -c:v h264_qsv -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key
  if config.ytshort == "False":
    command = live_link_url + ' best -o - | ' + config.ffmpeg + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + config.rtmp_key
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
  logging.basicConfig(filename="relive_yt.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  logging.getLogger().addHandler(logging.StreamHandler())
  api_this()
if arg1 == "this":
  logging.basicConfig(filename="relive_yt.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  logging.getLogger().addHandler(logging.StreamHandler())
  this()
exit()
