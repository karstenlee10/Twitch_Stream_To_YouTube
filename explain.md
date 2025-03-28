Here are this code functionalities by ai:

1. Stream Monitoring
- Monitors a Twitch stream for online/offline status
- Automatically switches to backup streams when the main stream goes offline
- Handles stream title synchronization from Twitch to YouTube
2. YouTube Integration
- Creates and manages YouTube livestreams
- Updates stream titles and descriptions automatically
- Handles YouTube API authentication
- Manages stream privacy settings (public/unlisted)
3. Failover System
- Implements a backup system that switches streams when issues are detected
- Monitors stream health and automatically restarts if needed
- Has a 12-hour duration limit with automatic stream rotation
4. Authentication
- Handles OAuth2 authentication for both YouTube and Gmail APIs
- Manages different credential types (brand accounts vs regular accounts)
- Stores and refreshes authentication tokens
5. RTMP Management
- Configures RTMP keys for streaming
- Manages multiple RTMP endpoints for backup purposes
- Uses FFmpeg for stream processing
6. Monitoring Features
- Gmail notification monitoring
- Stream status checking
- Automatic error recovery
- Logging system for debugging

The code is designed to run as a continuous service, monitoring streams and handling various failure scenarios automatically. It's particularly useful for maintaining 24/7 rebroadcast streams from Twitch to YouTube while handling various edge cases and failures automatically.
