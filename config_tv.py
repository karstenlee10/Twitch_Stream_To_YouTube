# Config updated at 8:30:50 2026/2/21
# Twitch Stream to YouTube Archive Configuration File
# This file contains all settings for the stream archiving system

##########################################################################
# ARCHIVE STREAMER CONFIGURATION
##########################################################################

# The Twitch username of the streamer you want to archive
# This is the channel name that appears in twitch.tv/USERNAME
username = ""

##########################################################################
# ARCHIVE BEHAVIOR SETTINGS
##########################################################################

# Enable automatic stream title updates
# If True: periodically refreshes stream title from Twitch
# If False: keeps initial stream title throughout broadcast
refresh_stream_title = True

# Enable ending video playback when stream goes offline
# If True: plays ending.mp4 when stream ends
# If False: stream ends immediately without ending screen
playvideo = True

# Control initial stream visibility
# If True: stream starts as unlisted (private link sharing)
# If False: stream starts as public (visible in search/channel)
unliststream = True

# Control chat availability during livestream
# If True: chat is disabled for viewers
# If False: chat is enabled for viewers
disablechat = True

# First YouTube playlist ID for automatic video addition
# Set to "Null" if you don't want to add videos to a playlist
# Example: "PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
playlist_id0 = "Null"

# Second YouTube playlist ID for automatic video addition (optional)
# Set to "Null" if you don't need a second playlist
# Only works if playlist_id0 is also configured
playlist_id1 = "Null"

# Enable custom thumbnail generation for streams
# If True: generates custom thumbnails with stream title
# If False: uses YouTube's default thumbnail
thumbnail = False

# Custom streamer name override for titles
# If set to "Null": uses the Twitch username in titles
# If set to custom name: uses that name instead in titles
StreamerName = "Null"

# Enable local archive saving
# If True: saves a copy of the stream to local_archive folder
# If False: only streams to YouTube (no local copy)
# WARNING: Requires significant disk space
local_archive = False

# Twitch account OAuth token for API access
# If set to "Null": uses client ID/secret only
# If set to actual token: uses that token for no ads if you're subscribed to turbo or subs
twitch_account_token = ""

# YouTube video tags for archived streams
# List of tags to add to YouTube videos
# Example: "#ai #neurosama #vedal #Archive"
# If no tags needed, set to ""
tags_for_youtube = ""

# Twitch subscription/turbo status for ad warnings
# If True: shows "AD-FREE: SUB/TURBO" in descriptions
# If False: shows ads warning in descriptions
brought_twitch_sub_or_turbo = False

# Public notification mode for unlisted streams
# If True: starts stream as public for notifications, then switches to unlisted
# If False: starts as unlisted and stays unlisted
# Only relevant when unliststream = True
public_notification = False

##########################################################################
# YOUTUBE STUDIO RTMP CONFIGURATION
##########################################################################

# Display name for your first RTMP stream key in YouTube Studio
# This should match the name you gave your stream key in YouTube Studio
rtmpkeyname1 = ""

# Display name for your second RTMP stream key in YouTube Studio
# Used for backup streaming when primary key fails
rtmpkeyname = ""

# Your first YouTube RTMP stream key
# Get this from YouTube Studio > Create > Go Live > Stream
rtmp_key = ""

# Your second YouTube RTMP stream key (backup)
# Used for redundancy when primary stream fails
rtmp_key_1 = ""

##########################################################################
# CHROME BROWSER CONFIGURATION
##########################################################################

# Chrome profile folder name to use for automation
# The script uses Chrome to automate YouTube Studio settings
# Use a dedicated profile for this purpose
Chrome_Profile = ""

##########################################################################
# GOOGLE API AUTHENTICATION SETTINGS
##########################################################################

# Google account display name (for regular accounts with email)
# This is used during OAuth authentication process
# Should match the name shown in Google account selection
accountname = ""

# Enable brand account usage for YouTube
# If True: uses a YouTube brand account (channel separate from personal account)
# If False: uses personal Google account for YouTube
brandacc = False

# Brand account display name (if using brand account)
# This should match the brand account name shown during OAuth
# Only used when brandacc = True
brandaccname = ""

##########################################################################
# TWITCH API CONFIGURATION
##########################################################################

# Twitch application client ID
# Register your application at https://dev.twitch.tv/console/apps
# Required for accessing Twitch stream information
client_id = ""

# Twitch application client secret
# Keep this secret and secure - never share publicly
# Required for Twitch API authentication
client_secret = ""

##########################################################################
# FFMPEG EXECUTABLE CONFIGURATION
##########################################################################

# Primary FFmpeg executable filename
# This should be the renamed ffmpeg.exe file in your directory
# Used for main stream processing
ffmpeg = ""

# Secondary FFmpeg executable filename (backup)
# Used for backup streams and ending screen playback
# Should be a second copy of ffmpeg.exe with different name
ffmpeg1 = ""

##########################################################################
# EXPERIMENTAL AND ADVANCED SETTINGS
##########################################################################

# Enable experimental testing mode
# If True: adds "[TESTING WILL BE REMOVE AFTER]" to titles
# If False: uses normal titles without testing label
exp_tesing = False

# Enable Q&A link in stream descriptions
# If True: adds link to FAQ page in stream descriptions
# If False: no Q&A link added
QandA = False

# Enable ads information link in descriptions
# If True: adds link explaining ad breaks to descriptions
# If False: no ads info link added
ADSqa = False

# Special streamer mode (Filian-specific)
# If True: removes certain help text from descriptions
# If False: includes standard help text
Filian = False

# Showing the current category in the stream description
# Also refreshes the category during the stream
category = False

# This is for when the category is "I'm Only Sleeping" 
# the stream will be switch immediately, so it won't mix with other stuff
# need category set to True for this to work
subathon = False
