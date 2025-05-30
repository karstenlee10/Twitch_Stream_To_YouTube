## Prerequisites

- Valid YouTube/Google account with streaming enabled and login to the account
- ***[YouTube Brand Account](https://support.google.com/youtube/answer/7001996) is now supported***

## Installation

## 1. Clone this repository or download zip:
```bash
git clone https://github.com/karstenlee10/Twitch_Stream_To_YouTube.git
cd Twitch_Stream_To_YouTube
```

## 2. Download required executables:
- Download lastest [Chrome](https://chrome.google.com) and login to your channel email
- Download lastest [Python](https://www.python.org/downloads/) and select run as admin and add to path
<!-- i don't think you need to install streamlink since it comes with a package -->
- Download lastest [Streamlink](https://github.com/streamlink/windows-builds/releases) and keep press next in the installation
- Download lastest [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) and place two `ffmpeg.exe` in the project directory (rename according to your config_tv.py settings)

## 3. Install required lastest Python packages:
```bash
uv sync
```

## Tips: You can use GUI.py for more easier config settings

## 4. Set up Google API:
- Go to [Google Cloud Console](https://console.cloud.google.com)
- 1. Create a project in Google Cloud Console
- 2. Enable [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com) and [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- 3. Create OAuth consent screen and User support and Developer contact information email as same email login
- 4. Add Scope by pasting:
```bash
https://www.googleapis.com/auth/youtube.force-ssl
https://www.googleapis.com/auth/gmail.readonly
```
- 5. ***Test user is your channel email***
- 6. Create OAuth 2.0 credentials
- 7. Download the client secret file and rename it to `client_secret.json`
- 8. Start `check_tv.py gentoken` to auth manually and copy down your username(with gmail) on the login page and paste it to `accountname` in `config_tv.py`
  9. ***ALSO if your using a brand account copy down your username(with no gmail) on the login page and paste it to `brandaccname` and set `brandacc` to `True` in `config_tv.py`***
- 10. And close the cmd and the chrome tab and delete `user_token.json` if had saved

## 5. Twitch API Setup Guide
- A Twitch account
1. Go to [Twitch Developer Console](https://dev.twitch.tv/console)
2. Log in with your Twitch account
3. Click "Register Your Application"
4. Click the "+ Register Your Application" button
5. Fill in the required fields:
   - **Name**: Choose a name for your application
   - **OAuth Redirect URLs**: Add `http://localhost`
   - **Category**: Select "Website Integration"
6. After registering, you'll see your application listed
7. Click "Manage"
8. You'll find:
   - **Client ID**: Displayed on the page
   - **Client Secret**: Click "New Secret" to generate
9. Update `config_tv.py` with your credentials:
```python
client_id = "your_client_id_here"
client_secret = "your_client_secret_here"
```
10. Add your Twitch streamer's username:
***(https://twitch.tv/caseoh_) ONLY COPY THE USERNAME***
```python
username = "your_twitch_username"  # Username from your wanted archive streamer
```

## 6. Set up configuration:
- Update the configuration values in `config_tv.py`:
  - Configure Chrome profile with chrome://version paste after User Data/
  - ***Set account details***
    1. Go to [YT Studio](https://studio.youtube.com) and login with the archive channel
    2. Go to live stream and create ***TWO RTMP KEY***
    3. Rename them as ***streamer's username*** and ***1streamer's usernamemult***(1 + streamer's username + mult)
    4. And copy ***streamer's username*** to `rtmpkeyname` and ***1streamer's usernamemult*** to `rtmpkeyname1` in `config_tv.py`
    5. And copy rtmp key of ***streamer's username*** to `rtmp_key` and rtmp key of ***1streamer's usernamemult*** to `rtmp_key_1` in `config_tv.py`
  - Add RTMP keys from YouTube
  - Add API credentials
  - Add `playlist` to `True` (or DOUBLE for two playlist) and paste your playlist id to `playlist_id0` for the first one(optional for adding playlist)

## 7. MOVE/COPY google_auth_oauthlib folder(for auto generate api token)
 - MOVE/COPY the `google_auth_oauthlib` folder to python_location/Lib/site-packages and replace `flow.py`

## Usage
Start the GUI for config settings and main script monitoring:
```bash
python gui.py
```

Start the main script:
```bash
python check_tv.py
```

### Optional Arguments:
- `KILL`: Stops all running processes(For Script Only)
- ***(DONT USE)***:
```bash
python check_tv.py KILL
```

- Custom stream URL and mode(For Script Only)
- example : check_tv.py THEYTLIVEID defrtmp/bkrtmp
- (check_tv.py RgNO-U5tV2E defrtmp)
- ***(DON'T INPUT ANYTHING)***
- ***(DONT USE)***:
```bash
python check_tv.py <arg1> <arg2>
```

## Logging

The application creates several log files:
- `check_tv.log`: Main application logs(check_tv.py)
- `relive_tv.log`: Streaming process logs(relive_tv.py)

## Troubleshooting

1. **Authentication Issues**:
   - Delete `user_token.json`
   - Run `check_tv.py` again
   - Ensure correct permissions in Google Cloud Console(Step 4)

2. **Stream Not Starting**:
   - Check RTMP keys in `config_tv.py`
   - Make sure you select the archive channel name(I don't know)
   - Verify source platform is streaming
   - Check log files for specific errors

3. **Chrome Issues**:
   - Verify Chrome profile path with chrome://version paste after User Data/
   - And ***Don't open chrome when the script is started CLOSE ANY WINDOWS***
  
4. **The most common problems**:
   - Delete all scheduled stream in your youtube studio before starting the script(or the script crashed)
   - The Username of your google account manybe filped your name when in the login page
   - Login to the account that you set in the config settings on Youtube Studio **DON'T CHANGE ACCOUNT IN THE MIDDLE OF THE SCRIPT ON THE PROFILE YOU CHOSE**
   - Configs can't not have spaces in the line (like:myself[SPACE]) Check it before applying
   - Sometime the auto regen google api token will be change so look at the updates and repaste the .py files(not include config_tv.py)
