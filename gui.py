import os
import sys
import subprocess
import threading
import time
from logger_config import gui_logger as logging # Importing logging module for logging messages
import asyncio
import config_tv as config
try:
    import customtkinter as ctk
    from customtkinter import CTkFont, CTkLabel, CTkButton, CTkEntry, CTkSwitch, CTkFrame, CTkTextbox, CTkScrollableFrame
    from PIL import Image, ImageTk
    from tkinter import filedialog, messagebox
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "pillow"])
    import customtkinter as ctk
    from customtkinter import CTkFont, CTkLabel, CTkButton, CTkEntry, CTkSwitch, CTkFrame, CTkTextbox, CTkScrollableFrame
    from PIL import Image, ImageTk
    from tkinter import filedialog, messagebox

# Set appearance mode and default theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Global variables
running_process = None
archiving_active = False

class ScrollableLogFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create textbox for logs
        self.log_textbox = CTkTextbox(self, wrap="word", activate_scrollbars=True)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure textbox
        self.log_textbox.configure(state="disabled", font=("Consolas", 12))
        
    def add_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        
    def clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

class TwitchYoutubeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Twitch to YouTube Archiver")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Track config changes
        self.config_changed = False
        
        # Create variables
        self.twitch_username_var = ctk.StringVar(value=config.username)
        self.client_id_var = ctk.StringVar(value=config.client_id)
        self.client_secret_var = ctk.StringVar(value=config.client_secret)
        self.rtmp_key_var = ctk.StringVar(value=config.rtmp_key)
        self.rtmp_key1_var = ctk.StringVar(value=config.rtmp_key_1)
        self.rtmpkeyname_var = ctk.StringVar(value=config.rtmpkeyname)
        self.rtmpkeyname1_var = ctk.StringVar(value=config.rtmpkeyname1)
        self.playlist_id0_var = ctk.StringVar(value=config.playlist_id0)
        self.playlist_id1_var = ctk.StringVar(value=config.playlist_id1)
        self.chrome_profile_var = ctk.StringVar(value=config.Chrome_Profile)
        self.accountname_var = ctk.StringVar(value=config.accountname)
        self.brandaccname_var = ctk.StringVar(value=config.brandaccname)
        
        self.ffmpeg_path_var = ctk.StringVar(value=config.ffmpeg)
        self.ffmpeg1_path_var = ctk.StringVar(value=config.ffmpeg1)
        self.apiexe_path_var = ctk.StringVar(value=config.apiexe)
        
        self.unliststream_var = ctk.BooleanVar(value=config.unliststream == "True")
        self.disablechat_var = ctk.BooleanVar(value=config.disablechat == "True")
        self.brandacc_var = ctk.BooleanVar(value=config.brandacc == "True")
        self.use_api_var = ctk.BooleanVar(value=config.Use_API == "True" if hasattr(config, 'Use_API') else True)
        
        self.playlist_choices = ["False", "True", "DOUBLE"]
        self.playlist_var = ctk.StringVar(value=config.playlist)
        
        self.thumbnail_var = ctk.BooleanVar(value=False)
        
        # Scrolling speed multiplier
        self.scroll_speed = 3
        
        # Set up trace callbacks to detect config changes
        self.setup_config_tracers()
        
        # Create main layouts
        self.setup_ui()
        
    def setup_config_tracers(self):
        """Set up callbacks to track changes in configuration variables"""
        variables = [
            self.twitch_username_var, self.client_id_var, self.client_secret_var,
            self.rtmp_key_var, self.rtmp_key1_var, self.rtmpkeyname_var, self.rtmpkeyname1_var,
            self.playlist_id0_var, self.playlist_id1_var, self.chrome_profile_var,
            self.accountname_var, self.brandaccname_var, self.ffmpeg_path_var,
            self.ffmpeg1_path_var, self.apiexe_path_var, self.playlist_var
        ]
        
        for var in variables:
            var.trace_add("write", self.on_config_change)
            
        # Boolean variables need special handling
        bool_variables = [
            self.unliststream_var, self.disablechat_var, self.brandacc_var, self.use_api_var
        ]
        
        for var in bool_variables:
            var.trace_add("write", self.on_config_change)
    
    def on_config_change(self, *args):
        """Callback when any configuration variable changes"""
        self.config_changed = True
        
    def setup_ui(self):
        # Create main container with two columns
        self.main_container = CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (configuration)
        self.left_panel = CTkFrame(self.main_container)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Right panel (logs and controls)
        self.right_panel = CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Setup tabs for configuration
        self.setup_tabs()
        
        # Setup control panel
        self.setup_control_panel()
        
        # Setup log panel
        self.setup_log_panel()
        
    def setup_tabs(self):
        # Create tabview
        self.tabview = ctk.CTkTabview(self.left_panel)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tabview.add("Twitch")
        self.tabview.add("YouTube")
        self.tabview.add("Files")
        self.tabview.add("Options")
        
        # Configure Twitch Tab
        self.setup_twitch_tab()
        
        # Configure YouTube Tab
        self.setup_youtube_tab()
        
        # Configure Files Tab
        self.setup_files_tab()
        
        # Configure Options Tab
        self.setup_options_tab()
        
    def setup_twitch_tab(self):
        twitch_tab = self.tabview.tab("Twitch")
        
        # Create scrollable frame for the tab content
        twitch_frame = CTkScrollableFrame(twitch_tab)
        twitch_frame.pack(fill="both", expand=True)
        
        # Configure faster scrolling
        self.configure_faster_scrolling(twitch_frame)
        
        # Twitch Username
        CTkLabel(twitch_frame, text="Twitch Username:").pack(anchor="w", padx=15, pady=(15,5))
        CTkEntry(twitch_frame, textvariable=self.twitch_username_var, width=300).pack(anchor="w", padx=15, pady=5)
        
        # Client ID
        CTkLabel(twitch_frame, text="Twitch Client ID:").pack(anchor="w", padx=15, pady=(15,5))
        CTkEntry(twitch_frame, textvariable=self.client_id_var, width=300).pack(anchor="w", padx=15, pady=5)
        
        # Client Secret
        CTkLabel(twitch_frame, text="Twitch Client Secret:").pack(anchor="w", padx=15, pady=(15,5))
        CTkEntry(twitch_frame, textvariable=self.client_secret_var, width=300).pack(anchor="w", padx=15, pady=5)
        
        # Help text
        help_frame = CTkFrame(twitch_frame)
        help_frame.pack(fill="x", anchor="w", padx=15, pady=15)
        
        CTkLabel(help_frame, text="Twitch API Setup", font=("", 14, "bold")).pack(anchor="w", padx=0, pady=(5,10))
        
        help_lines = [
            "• Create an app at https://dev.twitch.tv/console",
            "• Set OAuth Redirect URL to http://localhost",
            "• Copy Client ID and generate Client Secret",
            "• Paste values in fields above"
        ]
        
        for line in help_lines:
            CTkLabel(help_frame, text=line, justify="left").pack(anchor="w", padx=5, pady=2)
        
    def setup_youtube_tab(self):
        youtube_tab = self.tabview.tab("YouTube")
        
        # Create scrollable frame for the tab content
        youtube_frame = CTkScrollableFrame(youtube_tab)
        youtube_frame.pack(fill="both", expand=True)
        
        # Configure faster scrolling
        self.configure_faster_scrolling(youtube_frame)
        
        # Account Section
        account_section = CTkFrame(youtube_frame)
        account_section.pack(fill="x", padx=15, pady=(15,10))
        
        CTkLabel(account_section, text="Account Settings", font=("", 14, "bold")).pack(anchor="w", padx=0, pady=(0,10))
        
        # YouTube Account Name
        CTkLabel(account_section, text="YouTube Account Name:").pack(anchor="w", padx=0, pady=(5,5))
        CTkEntry(account_section, textvariable=self.accountname_var, width=300).pack(anchor="w", padx=0, pady=5)
        CTkLabel(account_section, text="Your Google account name shown during login", 
                text_color="gray", justify="left").pack(anchor="w", padx=25, pady=(0,5))
        
        # Brand Account Option
        brand_switch_frame = CTkFrame(account_section)
        brand_switch_frame.pack(fill="x", padx=0, pady=10)
        
        CTkSwitch(brand_switch_frame, text="Use Brand Account", variable=self.brandacc_var, 
                 command=self.toggle_brand_account).pack(anchor="w", padx=0)
        
        # Brand Account Name (initially hidden)
        self.brand_account_frame = CTkFrame(account_section)
        if self.brandacc_var.get():
            self.brand_account_frame.pack(fill="x", padx=0, pady=5)
            
        CTkLabel(self.brand_account_frame, text="Brand Account Name:").pack(anchor="w", padx=0, pady=5)
        CTkEntry(self.brand_account_frame, textvariable=self.brandaccname_var, width=300).pack(anchor="w", padx=0, pady=5)
        CTkLabel(self.brand_account_frame, text="Name appears during login (without email)", 
                text_color="gray", justify="left").pack(anchor="w", padx=25, pady=(0,5))
        
        # Chrome Profile
        chrome_frame = CTkFrame(youtube_frame)
        chrome_frame.pack(fill="x", padx=15, pady=10)
        
        CTkLabel(chrome_frame, text="Chrome Profile:").pack(anchor="w", padx=0, pady=5)
        CTkEntry(chrome_frame, textvariable=self.chrome_profile_var, width=300).pack(anchor="w", padx=0, pady=5)
        CTkLabel(chrome_frame, text="Find in Chrome URL: chrome://version/ under 'Profile Path'", 
                text_color="gray", justify="left").pack(anchor="w", padx=25, pady=(0,5))
        
        # RTMP Settings
        rtmp_section = CTkFrame(youtube_frame)
        rtmp_section.pack(fill="x", padx=15, pady=10)
        
        CTkLabel(rtmp_section, text="RTMP Settings", font=("", 14, "bold")).pack(anchor="w", padx=0, pady=(5,10))
        CTkLabel(rtmp_section, text="You need two RTMP keys for primary and backup streams").pack(anchor="w", padx=0, pady=(0,10))
        
        # Primary RTMP
        primary_frame = CTkFrame(rtmp_section)
        primary_frame.pack(fill="x", padx=0, pady=5)
        
        CTkLabel(primary_frame, text="Primary RTMP Setup:", font=("", 12, "bold")).pack(anchor="w", padx=0, pady=5)
        
        # RTMP Key Name
        CTkLabel(primary_frame, text="RTMP Key Name:").pack(anchor="w", padx=15, pady=(5,5))
        CTkEntry(primary_frame, textvariable=self.rtmpkeyname_var, width=300).pack(anchor="w", padx=15, pady=5)
        description_frame = CTkFrame(primary_frame)
        description_frame.pack(fill="x", anchor="w", padx=40, pady=(0,10))
        CTkLabel(description_frame, text="Name shown in YouTube Studio", 
                text_color="gray", justify="left").pack(anchor="w", pady=0)
        CTkLabel(description_frame, text="Typically matches your Twitch username", 
                text_color="gray", justify="left").pack(anchor="w", pady=0)
        
        # RTMP Key
        CTkLabel(primary_frame, text="RTMP Key:").pack(anchor="w", padx=15, pady=(5,5))
        key_entry = CTkEntry(primary_frame, textvariable=self.rtmp_key_var, width=300)
        key_entry.pack(anchor="w", padx=15, pady=5)
        key_desc_frame = CTkFrame(primary_frame)
        key_desc_frame.pack(fill="x", anchor="w", padx=40, pady=(0,10))
        CTkLabel(key_desc_frame, text="From YouTube Studio > Create > Go Live > Stream", 
                text_color="gray", justify="left").pack(anchor="w")
        
        # Secondary RTMP
        secondary_frame = CTkFrame(rtmp_section)
        secondary_frame.pack(fill="x", padx=0, pady=(10,5))
        
        CTkLabel(secondary_frame, text="Secondary RTMP Setup:", font=("", 12, "bold")).pack(anchor="w", padx=0, pady=5)
        
        # Second RTMP Key Name
        CTkLabel(secondary_frame, text="Second RTMP Key Name:").pack(anchor="w", padx=15, pady=(5,5))
        CTkEntry(secondary_frame, textvariable=self.rtmpkeyname1_var, width=300).pack(anchor="w", padx=15, pady=5)
        secondary_desc_frame = CTkFrame(secondary_frame)
        secondary_desc_frame.pack(fill="x", anchor="w", padx=40, pady=(0,10))
        CTkLabel(secondary_desc_frame, text="Recommended format:", 
                text_color="gray", justify="left").pack(anchor="w", pady=0)
        CTkLabel(secondary_desc_frame, text="1[username]mult", 
                text_color="gray", font=("", 12, "bold"), justify="left").pack(anchor="w", pady=0)
        
        # Second RTMP Key
        CTkLabel(secondary_frame, text="Second RTMP Key:").pack(anchor="w", padx=15, pady=(5,5))
        key_entry2 = CTkEntry(secondary_frame, textvariable=self.rtmp_key1_var, width=300)
        key_entry2.pack(anchor="w", padx=15, pady=5)
        key2_desc_frame = CTkFrame(secondary_frame)
        key2_desc_frame.pack(fill="x", anchor="w", padx=40, pady=(0,10))
        CTkLabel(key2_desc_frame, text="Create a second stream key in YouTube Studio", 
                text_color="gray", justify="left").pack(anchor="w")
        
        # Add some padding at the bottom for better scrolling
        CTkFrame(youtube_frame, height=20).pack(fill="x")
        
    def setup_files_tab(self):
        files_tab = self.tabview.tab("Files")
        
        # Create scrollable frame for the tab content
        files_frame = CTkScrollableFrame(files_tab)
        files_frame.pack(fill="both", expand=True)
        
        # Configure faster scrolling
        self.configure_faster_scrolling(files_frame)
        
        # FFmpeg Path
        CTkLabel(files_frame, text="FFmpeg Path:").pack(anchor="w", padx=15, pady=(15,5))
        ffmpeg_frame = CTkFrame(files_frame)
        ffmpeg_frame.pack(fill="x", padx=15, pady=5)
        CTkEntry(ffmpeg_frame, textvariable=self.ffmpeg_path_var, width=250).pack(side="left", padx=(0,10))
        CTkButton(ffmpeg_frame, text="Browse", width=80, 
                 command=lambda: self.browse_file(self.ffmpeg_path_var)).pack(side="left")
        
        # FFmpeg1 Path
        CTkLabel(files_frame, text="Second FFmpeg Path:").pack(anchor="w", padx=15, pady=(15,5))
        ffmpeg1_frame = CTkFrame(files_frame)
        ffmpeg1_frame.pack(fill="x", padx=15, pady=5)
        CTkEntry(ffmpeg1_frame, textvariable=self.ffmpeg1_path_var, width=250).pack(side="left", padx=(0,10))
        CTkButton(ffmpeg1_frame, text="Browse", width=80, 
                 command=lambda: self.browse_file(self.ffmpeg1_path_var)).pack(side="left")
        
        # API EXE Path
        CTkLabel(files_frame, text="API EXE Path:").pack(anchor="w", padx=15, pady=(15,5))
        apiexe_frame = CTkFrame(files_frame)
        apiexe_frame.pack(fill="x", padx=15, pady=5)
        CTkEntry(apiexe_frame, textvariable=self.apiexe_path_var, width=250).pack(side="left", padx=(0,10))
        CTkButton(apiexe_frame, text="Browse", width=80, 
                 command=lambda: self.browse_file(self.apiexe_path_var)).pack(side="left")
        
        # Instructions
        help_frame = CTkFrame(files_frame)
        help_frame.pack(fill="x", anchor="w", padx=15, pady=15)
        
        CTkLabel(help_frame, text="Required Files", font=("", 14, "bold")).pack(anchor="w", padx=0, pady=(5,10))
        
        help_lines = [
            "• Main FFmpeg executable (stream processing)",
            "• Second FFmpeg executable (backup stream)",
            "• API executable (browser automation)",
            "• All files must be in the application directory",
            "• Download FFmpeg from: www.gyan.dev/ffmpeg/builds/"
        ]
        
        for line in help_lines:
            CTkLabel(help_frame, text=line, justify="left").pack(anchor="w", padx=5, pady=2)
            
    def setup_options_tab(self):
        options_tab = self.tabview.tab("Options")
        
        # Create scrollable frame for the tab content
        options_frame = CTkScrollableFrame(options_tab)
        options_frame.pack(fill="both", expand=True)
        
        # Configure faster scrolling
        self.configure_faster_scrolling(options_frame)
        
        # Unlist Stream
        option_section = CTkFrame(options_frame)
        option_section.pack(fill="x", padx=15, pady=5)
        
        CTkSwitch(option_section, text="Unlist Stream", variable=self.unliststream_var).pack(anchor="w", pady=5)
        CTkLabel(option_section, text="Stream will be unlisted, then public after completion", 
                justify="left", text_color="gray").pack(anchor="w", padx=25, pady=(0,5))
        
        # Disable Chat
        option_section2 = CTkFrame(options_frame)
        option_section2.pack(fill="x", padx=15, pady=5)
        
        CTkSwitch(option_section2, text="Disable Live Chat", variable=self.disablechat_var).pack(anchor="w", pady=5)
        CTkLabel(option_section2, text="Disables the YouTube live chat during streaming", 
                justify="left", text_color="gray").pack(anchor="w", padx=25, pady=(0,5))
        
        # Thumbnail Upload
        option_section3 = CTkFrame(options_frame)
        option_section3.pack(fill="x", padx=15, pady=5)
        
        self.thumbnail_var = ctk.BooleanVar(value=config.thumbnail == "True")
        CTkSwitch(option_section3, text="Upload Custom Thumbnails", variable=self.thumbnail_var).pack(anchor="w", pady=5)
        CTkLabel(option_section3, text="Uploads custom thumbnails for streams", 
                justify="left", text_color="gray").pack(anchor="w", padx=25, pady=(0,5))
        
        # Use API
        option_section4 = CTkFrame(options_frame)
        option_section4.pack(fill="x", padx=15, pady=5)
        
        CTkSwitch(option_section4, text="Use API Mode", variable=self.use_api_var).pack(anchor="w", pady=5)
        CTkLabel(option_section4, text="Uses YouTube API for stream management (requires API credentials)", 
                justify="left", text_color="gray").pack(anchor="w", padx=25, pady=(0,5))
        
        # Playlist Settings
        playlist_section = CTkFrame(options_frame)
        playlist_section.pack(fill="x", padx=15, pady=(25,5))
        
        CTkLabel(playlist_section, text="Playlist Settings", font=("", 14, "bold")).pack(anchor="w", padx=0, pady=5)
        
        # Playlist options with explanations
        playlist_options_frame = CTkFrame(options_frame)
        playlist_options_frame.pack(fill="x", padx=15, pady=5)
        
        option_labels = {
            "False": "Don't add to any playlist",
            "True": "Add to primary playlist only",
            "DOUBLE": "Add to both primary and secondary playlists"
        }
        
        for i, choice in enumerate(self.playlist_choices):
            option_frame = CTkFrame(playlist_options_frame)
            option_frame.pack(fill="x", pady=2)
            
            ctk.CTkRadioButton(option_frame, text=choice, variable=self.playlist_var, 
                              value=choice, command=self.update_playlist_fields).pack(side="left", padx=5)
            
            CTkLabel(option_frame, text=option_labels[choice], 
                    justify="left", text_color="gray").pack(side="left", padx=10)
        
        # Playlist IDs
        playlist_id_frame = CTkFrame(options_frame)
        playlist_id_frame.pack(fill="x", padx=15, pady=(15,5))
        
        CTkLabel(playlist_id_frame, text="Primary Playlist ID:").pack(anchor="w", padx=0, pady=5)
        self.playlist_id0_entry = CTkEntry(playlist_id_frame, textvariable=self.playlist_id0_var, width=300)
        self.playlist_id0_entry.pack(anchor="w", padx=0, pady=5)
        CTkLabel(playlist_id_frame, text="Find in YouTube URL: playlist?list=PLAYLIST_ID", 
                text_color="gray", justify="left").pack(anchor="w", padx=25, pady=(0,10))
        
        CTkLabel(playlist_id_frame, text="Secondary Playlist ID (for DOUBLE):").pack(anchor="w", padx=0, pady=5)
        self.playlist_id1_entry = CTkEntry(playlist_id_frame, textvariable=self.playlist_id1_var, width=300)
        self.playlist_id1_entry.pack(anchor="w", padx=0, pady=5)
        
        # Initialize playlist field states
        self.update_playlist_fields()
        
        # Add some padding at the bottom for better scrolling
        CTkFrame(options_frame, height=20).pack(fill="x")
        
    def update_playlist_fields(self):
        """Update the state of playlist ID fields based on the current playlist setting"""
        playlist_value = self.playlist_var.get()
        
        if playlist_value == "False":
            # Disable both playlist ID fields when playlist is False
            self.playlist_id0_entry.configure(state="disabled", fg_color="#AAAAAA")
            self.playlist_id1_entry.configure(state="disabled", fg_color="#AAAAAA")
        elif playlist_value == "True":
            # Enable primary playlist ID, disable secondary
            self.playlist_id0_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
            self.playlist_id1_entry.configure(state="disabled", fg_color="#AAAAAA")
        else:  # DOUBLE
            # Enable both playlist ID fields
            self.playlist_id0_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
            self.playlist_id1_entry.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
        
    def setup_control_panel(self):
        # Controls container
        control_frame = CTkFrame(self.right_panel)
        control_frame.pack(fill="x", padx=10, pady=(10,5))
        
        # Status header
        status_header = CTkFrame(control_frame)
        status_header.pack(fill="x", padx=10, pady=(10,5))
        
        CTkLabel(status_header, text="Status", 
                font=("", 14, "bold")).pack(anchor="w", padx=10)
        
        # Status indicators
        status_frame = CTkFrame(control_frame)
        status_frame.pack(fill="x", padx=10, pady=(0,10))
        
        # Archiving status
        archiving_status_frame = CTkFrame(status_frame)
        archiving_status_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.archiving_label = CTkLabel(archiving_status_frame, text="Inactive", text_color="gray")
        self.archiving_label.pack(side="left", padx=10)
        
        # Button header
        button_header = CTkFrame(control_frame)
        button_header.pack(fill="x", padx=10, pady=(10,5))
        
        CTkLabel(button_header, text="Controls", 
                font=("", 14, "bold")).pack(anchor="w", padx=10)
        
        # Control buttons
        buttons_frame = CTkFrame(control_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(0,10))
        
        # First row - Main controls
        main_buttons = CTkFrame(buttons_frame)
        main_buttons.pack(fill="x", padx=0, pady=5)
        
        # Start button
        self.start_button = CTkButton(main_buttons, text="Start Archiving", command=self.start_archiving, 
                               fg_color="#28a745", hover_color="#218838")
        self.start_button.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        # Stop button
        self.stop_button = CTkButton(main_buttons, text="Stop All", command=self.stop_all, 
                              fg_color="#dc3545", hover_color="#c82333", state="disabled")
        self.stop_button.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        # Second row - Utility controls
        util_buttons = CTkFrame(buttons_frame)
        util_buttons.pack(fill="x", padx=0, pady=5)
        
        # Save config button
        self.save_button = CTkButton(util_buttons, text="Save Config", command=self.save_config, 
                               fg_color="#0275d8", hover_color="#0269c2")
        self.save_button.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
    def setup_log_panel(self):
        # Log frame
        log_frame = CTkFrame(self.right_panel)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))
        
        # Title and clear button
        log_header = CTkFrame(log_frame)
        log_header.pack(fill="x", padx=10, pady=(10,0))
        
        CTkLabel(log_header, text="Stream Logs", font=("", 14, "bold")).pack(side="left", padx=10)
        CTkButton(log_header, text="Clear Logs", width=100, 
                 command=self.clear_logs).pack(side="right", padx=10)
        
        # Log display
        self.log_display = ScrollableLogFrame(log_frame)
        self.log_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure faster scrolling for log display
        self.configure_faster_scrolling(self.log_display)
        
        # Start log capturing
        self.setup_log_capture()
        
    def setup_log_capture(self):
        """Capture logs and display them in the GUI"""
        class GUILogHandler():
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
                
            def emit(self, record):
                log_entry = self.format(record)
                self.callback(log_entry)
    
    def add_log_entry(self, message):
        """Add a log entry to the GUI log display"""
        if not hasattr(self, 'log_display'):
            return
            
        # Use after() to safely update from another thread
        self.after(0, lambda: self.log_display.add_log(message))
        
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.clear_logs()
        
    def toggle_brand_account(self):
        """Toggle visibility of brand account settings"""
        if self.brandacc_var.get():
            self.brand_account_frame.pack(fill="x", padx=15, pady=5)
        else:
            self.brand_account_frame.pack_forget()
            
    def browse_file(self, string_var):
        """Open file browser and update the path variable"""
        filepath = filedialog.askopenfilename(
            title="Select File", 
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filepath:
            # Extract just the filename for consistency with how the script expects it
            filename = os.path.basename(filepath)
            string_var.set(filename)
    
    def save_config(self):
        """Save configuration to config_tv.py"""
        try:
            config_path = "config_tv.py"
            
            with open(config_path, 'w') as f:
                # Add timestamp as a comment
                f.write(f"# Config updated at {time.strftime('%H:%M:%S')} {time.strftime('%Y-%m-%d')}\n\n")
                
                # ARCHIVE STREAMER USERNAME section
                f.write("#ARCHIVE STREAMER USERNAME\n")
                f.write(f"username = \"{self.twitch_username_var.get()}\" #twitch username\n")
                f.write("##########################################################################\n")
                
                # ARCHIVE SETTINGS section
                f.write("#ARCHIVE SETTINGS\n")
                f.write(f"unliststream = \"{str(self.unliststream_var.get()).capitalize()}\" #after stream will be public\n")
                f.write(f"disablechat = \"{str(self.disablechat_var.get()).capitalize()}\"  #disable chat on live stream\n")
                f.write(f"playlist = \"{self.playlist_var.get()}\"  # True or DOUBLE IF YOU WANT TO SAVE TO MULTIPLE PLAYLIST disable to False\n")
                f.write(f"playlist_id0 = \"{self.playlist_id0_var.get()}\"  # Replace with your First YouTube playlist ID\n")
                f.write(f"playlist_id1 = \"{self.playlist_id1_var.get()}\"  # Replace with your actual second YouTube playlist ID\n")
                f.write(f"thumbnail = \"{str(self.thumbnail_var.get()).capitalize()}\"  # Whether to upload custom thumbnails for streams\n")
                f.write("##########################################################################\n")
                
                # YOUTUBE STUDIO RTMP SETTINGS section
                f.write("#YOUTUBE STUDIO RTMP SETTINGS\n")
                f.write(f"rtmpkeyname1 = \"{self.rtmpkeyname1_var.get()}\" #first yt rtmp key name\n")
                f.write(f"rtmpkeyname = \"{self.rtmpkeyname_var.get()}\" #second yt rtmp key name\n")
                f.write(f"rtmp_key = \"{self.rtmp_key_var.get()}\" #first yt rtmp key\n")
                f.write(f"rtmp_key_1 = \"{self.rtmp_key1_var.get()}\" #second yt rtmp key\n")
                f.write("##########################################################################\n")
                
                # CHROME PROFILE FOLDER NAME section
                f.write("#CHROME PROFILE FOLDER NAME\n")
                f.write(f"Chrome_Profile = \"{self.chrome_profile_var.get()}\" #chrome profile folder name\n")
                f.write("##########################################################################\n")
                
                # API SETTINGS section
                f.write("#API SETTINGS\n")
                f.write(f"Use_API = \"{str(self.use_api_var.get()).capitalize()}\"  #True is USE ANY API for stream management, False is USE BROWSER for stream management\n")
                f.write(f"accountname = \"{self.accountname_var.get()}\" #google account name(not brand acc have email) when login to google api\n")
                f.write(f"brandacc = \"{str(self.brandacc_var.get()).capitalize()}\" #do you use the brand acc as the archive channel\n")
                f.write(f"brandaccname = \"{self.brandaccname_var.get()}\" #if you have brand acc copy the google account name when login to google api\n")
                f.write("#TWITCH API SETTINGS\n")
                f.write(f"client_id = \"{self.client_id_var.get()}\" #twitch api client id\n")
                f.write(f"client_secret = \"{self.client_secret_var.get()}\" #twitch api client sercet\n")
                f.write("##########################################################################\n")
                
                # EXE NAME section
                f.write("#EXE NAME\n")
                f.write(f"ffmpeg1 = \"{self.ffmpeg1_path_var.get()}\" #ffmpeg exe name\n")
                f.write(f"ffmpeg = \"{self.ffmpeg_path_var.get()}\" #ffmpeg exe name\n")
                f.write(f"apiexe = \"{self.apiexe_path_var.get()}\" #api exe name\n")
                
            self.add_log_entry("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
            # Reload config module
            import importlib
            importlib.reload(config)
            
            # Reset the config changed flag
            self.config_changed = False
            
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def start_archiving(self):
        """Start the archiving process"""
        try:
            # Save configuration before starting only if it has changed
            if self.config_changed:
                self.add_log_entry("Configuration changed - saving before archiving")
                self.save_config()
            
            # Disable start button and enable stop button
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Update archiving status
            global archiving_active
            archiving_active = True
            self.archiving_label.configure(text="Active", text_color="#28a745")
            
            # Start check_tv.py in a separate thread
            self.archive_thread = threading.Thread(target=self.run_archive_process)
            self.archive_thread.daemon = True
            self.archive_thread.start()
            
            self.add_log_entry("Starting archiving process...")
            
        except Exception as e:
            logging.error(f"Error starting archiving: {e}")
            messagebox.showerror("Error", f"Failed to start archiving: {str(e)}")
            self.start_button.configure(state="normal")
            archiving_active = False
            self.archiving_label.configure(text="Inactive", text_color="gray")
            
    def run_archive_process(self):
        """Run the archive process in a background thread"""
        global running_process
        try:
            # Run check_tv.py
            self.add_log_entry("Launching check_tv.py...")
            running_process = subprocess.Popen([sys.executable, "check_tv.py"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True)
            
            # Read output
            for line in running_process.stdout:
                self.add_log_entry(line.strip())
                
            # Wait for process to complete and get exit code
            return_code = running_process.wait()
            
            # Check if process exited with an error
            if return_code != 0:
                self.add_log_entry(f"Archive process failed with exit code: {return_code}")
                # Update UI to show error state
                self.after(0, self.reset_ui_after_error)
            else:
                self.add_log_entry("Archive process completed successfully")
                # Reset UI normally
                self.after(0, self.reset_ui_after_stop)
            
        except Exception as e:
            logging.error(f"Error in archive process: {e}")
            self.add_log_entry(f"Error in archive process: {e}")
            # Update UI to show error state
            self.after(0, self.reset_ui_after_error)
            
    def reset_ui_after_error(self):
        """Reset UI elements after an error occurred"""
        global archiving_active
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        archiving_active = False
        self.archiving_label.configure(text="Error", text_color="#dc3545")
        
    def reset_ui_after_stop(self):
        """Reset UI elements after stopping the process"""
        global archiving_active
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        archiving_active = False
        self.archiving_label.configure(text="Inactive", text_color="gray")
        
    def stop_all(self):
        """Stop all running processes"""
        global running_process, archiving_active
        
        try:
            self.add_log_entry("Stopping all processes...")
            
            # Run the KILL command
            subprocess.run([sys.executable, "check_tv.py", "KILL"], 
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            # Kill the running process if it exists
            if running_process and running_process.poll() is None:
                running_process.terminate()
                
            self.add_log_entry("All processes stopped")
            archiving_active = False
            self.reset_ui_after_stop()
            
        except Exception as e:
            logging.error(f"Error stopping processes: {e}")
            self.add_log_entry(f"Error stopping processes: {e}")
            
    def on_close(self):
        """Handle window close event"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?\nAny running archive processes will be stopped."):
            self.stop_all()
            self.quit()

    def configure_faster_scrolling(self, scrollable_frame):
        """Configure faster mouse wheel scrolling for a scrollable frame"""
        if hasattr(scrollable_frame, "_scrollbar") and scrollable_frame._scrollbar:
            # Create a function to handle mouse wheel events with increased speed
            def _on_mousewheel(event):
                if event.delta > 0:
                    scrollable_frame._scrollbar.set(
                        scrollable_frame._scrollbar.get()[0] - 0.05 * self.scroll_speed,
                        scrollable_frame._scrollbar.get()[1] - 0.05 * self.scroll_speed
                    )
                else:
                    scrollable_frame._scrollbar.set(
                        scrollable_frame._scrollbar.get()[0] + 0.05 * self.scroll_speed,
                        scrollable_frame._scrollbar.get()[1] + 0.05 * self.scroll_speed
                    )
                return "break"
            
            # For Windows/MacOS
            scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
            # For Linux
            scrollable_frame.bind("<Button-4>", _on_mousewheel)
            scrollable_frame.bind("<Button-5>", _on_mousewheel)

if __name__ == "__main__":
    # Install dependencies if needed
    
    app = TwitchYoutubeApp()
    app.mainloop() 
