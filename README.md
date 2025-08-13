<h1 align="center" id="title">Twitch Stream to YouTube Script</h1>

<p align="center"><img src="https://socialify.git.ci/karstenlee10/Twitch-and-BiliBili-Archive-to-Youtube-Script/image?font=Inter&amp;language=1&amp;logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F91263511%3Fv%3D4&amp;name=1&amp;owner=1&amp;pattern=Circuit+Board&amp;stargazers=1&amp;theme=Light" alt="project-image"></p>

The code is designed to run as a continuous service, monitoring streams and handling various failure scenarios automatically. It's particularly useful for maintaining 24/7 rebroadcast streams from Twitch to YouTube while handling various edge cases and failures automatically.

<h2>Detail Wiki of this Project: <a href="https://deepwiki.com/karstenlee10/Twitch_Stream_To_YouTube"><img src="https://deepwiki.com/badge.svg" alt="DeepWiki"></a></h2>

<h2>🛡️ License:</h2>

***PLEASE CREDIT ME ON YOUR CHANNEL WHEN USING ON YOUR channel description*** paste the github link  
https://bit.ly/archivescript
https://is.gd/archivescript

<h2>🛡️ License Example:</h2>

https://www.youtube.com/@FilianVODSArchive

***https://www.youtube.com/@NeuroVerseUnofficalVODS***

<h2>🚨 Warning:</h2>

This script is not in a complete ***finish state*** and only support ***WINDOWS***

If you can't successfully run the google api please make an issue and give your channel's email and then I will give you a client_secret for the api

<h2>🧐 Features</h2>

Here're some of the project's best features:

*   You can set the script to public the stream after the streamer finish ***(for no permission restreaming someones content)***
*   Archive and play back twitch stream in real time ***(On youtube streams after opening dvr)***
*   Save VODS forever ***(unless YouTube delete it)***
*   VODS don't have muted copyrighted music ***(Unless YouTube copyrighted it)***
*   It is ***automated*** no need for human
*   Don't need to ***download the vods and upload it back to youtube***
*   ***Faster than other vods archivers (e.g. they will need to wait for youtube processing)***
*   If the stream is almost over 12 hours It will cut the stream for not losing the video after 12 hours ***(e.g. subathon)***
*   When receive thind-party takedown notice It will stop immediately and start another stream to protect from getting copyrighted strikes on your channel ***(e.g. playing music or video may cause this)***
*   ***WHATEVER LANGUAGE IS SUPPORTED USING THIS SCRIPT***

<h2>👎 Disadvantage</h2>

Here're some of the project's disadvantage:

* If you don't have ***twitch turbo*** or you have turbo but didn't input your token to streamlink, there will be ***ads(commercial break) on the vods***
* Sometimes youtube will cut the stream for no reason or ***thind-party takedown*** and it will causes a ***few minutes of archive video loss***
* This project is still in ***beta*** may have some bugs that didn't fix or found
* Setup can be difficult for people who are not computer savvy

<h2>🍰 Contribution:</h2>

Make an issue when there a bug
  
<h2>💻 Built with</h2>

Technologies used in the project:

*   Streamlink
*   Python
*   Selenium Chromedriver
*   YouTube Data API v3
*   Gmail API
*   Twitch API
*   ffmpeg

<h2>🔜 Future Update(not promising):</h2> 

* ~~Simplify the code~~
* Make a mode that don't use any api
* ~~Make a gui for installation~~ and automation
* Make a mode the use independent webdriver.exe
* Using a different browers
* Add Kick/Add YouTube??(Needed support on streamlink)

<h2>🧐 Definition of the file</h2>

google_auth_oauthlib/flow.py (EDIT FOR AUTOMATED REFRESH API KEY)

blackscreen.mp4 (Plays when receive thind-party takedown notice or youtube disconnect and if config_tv.playvideo is True)

check_tv.py (main process running api, brower automation, checking email and more)

config_tv.py (A config file)

countdriver.exe (Is a process to notify another script(same project but copy another to mult-stream to a channel) that chrome is using, so it won't crash chrome)

ending.mp4 (Plays when receive no streams from Twitch API and if config_tv.playvideo is True)

ffmpeg_api.exe (A process that notify relive_tv.py if the ffmpeg error then check if process is still here and the streamer is still live and restart the stream if the process is not here but the streamer is still live then it will exit itself)(Also a timer for 11hours and 50mins perventing the stream over 12 hours)

logger_config.py (another script will import this as their logger)

relive_tv.py (restreaming twitch stream to youtube and also save locally if config_tv.local_archive is True)

<h2>💲 Donation</h2>

The donation will be for the project or support me buying twitch turbo for the channel.

Or just make a direct gift sub to karsteniee on twitch to a specific user(https://twitch.tv/karsteniee)

https://streamlabs.com/karsteniee/tips
