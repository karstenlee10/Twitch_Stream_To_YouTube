Here's a GitHub-style README.md installation guide for this project:

```markdown
# YouTube Stream Manager

A Python-based tool for managing YouTube live streams with support for Twitch and Bilibili restreaming.

## Features

- Automatic stream management and monitoring
- Support for Twitch and Bilibili as source platforms
- YouTube stream title and description management
- Automatic stream recovery
- Support for both standard and vertical (Shorts) video formats
- Chat management options
- Multiple RTMP key support

## Prerequisites

- Python 3.7+
- Google Chrome browser
- FFmpeg
- Valid YouTube/Google account with streaming enabled
- Twitch Developer Account (if using Twitch)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd youtube-stream-manager
```

2. Install required Python packages:
```bash
pip install selenium
pip install google-auth-oauthlib
pip install google-api-python-client
pip install streamlink
pip install beautifulsoup4
pip install psutil
pip install requests
pip install opencv-python
```

3. Download required executables:
- Place `ffmpeg.exe` in the project directory (rename according to your config_tv.py settings)
- Download ChromeDriver compatible with your Chrome version

4. Set up configuration:
- Rename `config_tv.py.example` to `config_tv.py`
- Update the configuration values in `config_tv.py`:
  - Set your platform (`Twitch` or `BiliBili`)
  - Configure Chrome profile
  - Set usernames and account details
  - Add RTMP keys from YouTube
  - Add API credentials (for Twitch)

5. Set up Google API:
- Create a project in Google Cloud Console
- Enable YouTube Data API v3
- Create OAuth 2.0 credentials
- Download the client secret file and rename it to `client_secret.json`

## First-Time Setup

1. Run the authentication script to get YouTube API access:
```bash
python get_token.py
```

2. Follow the browser prompts to authenticate your Google account

## Usage

Start the main script:
```bash
python check_tv.py
```

### Optional Arguments:
- `KILL`: Stops all running processes
```bash
python check_tv.py KILL
```

- Custom stream URL and mode:
```bash
python check_tv.py <stream_url> <mode>
```

## Configuration Options

Key settings in `config_tv.py`:

```python
Twitch = "False"          # Use Twitch as source
BiliBili = "True"         # Use Bilibili as source
ytshort = "False"         # Enable vertical video mode
unliststream = "False"    # Make streams unlisted
disablechat = "True"      # Disable live chat
```

## Logging

The application creates several log files:
- `tv.log`: Main application logs
- `relive_yt.log`: Streaming process logs
- `get_token.log`: Authentication logs

## Troubleshooting

1. **Authentication Issues**:
   - Delete `user_token.json`
   - Run `get_token.py` again
   - Ensure correct permissions in Google Cloud Console

2. **Stream Not Starting**:
   - Check RTMP keys in `config_tv.py`
   - Verify source platform is streaming
   - Check log files for specific errors

3. **Chrome Issues**:
   - Verify Chrome profile path
   - Update ChromeDriver to match Chrome version
   - Clear Chrome user data if persistent issues

## License

[Your License Here]

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Support

For support, please [create an issue](your-repo-issues-link) in this repository.
```

This README provides a comprehensive guide for setting up and using the YouTube Stream Manager. You may want to customize it further based on specific requirements or additional features of your project.
