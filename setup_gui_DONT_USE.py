import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import subprocess
import webbrowser
import configparser
import shutil
import sys
from datetime import datetime

class SetupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch to YouTube Setup")
        self.root.geometry("1000x800")  # Increased window size
        
        # Initialize FFmpeg filename variables
        self.ffmpeg_name1 = tk.StringVar(value="ffmpeg.exe")
        self.ffmpeg_name2 = tk.StringVar(value="ffmpeg111.exe")
        
        # Create main container
        main_container = ttk.Frame(root)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.prerequisites_tab = ttk.Frame(self.notebook)
        self.installation_tab = ttk.Frame(self.notebook)
        self.google_api_tab = ttk.Frame(self.notebook)
        self.twitch_api_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.prerequisites_tab, text='1. Prerequisites')
        self.notebook.add(self.installation_tab, text='2. Installation', state='disabled')
        self.notebook.add(self.google_api_tab, text='3. Google API', state='disabled')
        self.notebook.add(self.twitch_api_tab, text='4. Twitch API', state='disabled')
        self.notebook.add(self.config_tab, text='5. Configuration', state='disabled')
        
        # Initialize all tabs
        self.setup_prerequisites_tab()
        self.setup_installation_tab()
        self.setup_google_api_tab()
        self.setup_twitch_api_tab()
        self.setup_config_tab()
        
        # Load config if exists
        self.config = {}
        self.load_config()

    def create_help_text(self, parent, text):
        help_frame = ttk.LabelFrame(parent, text="Instructions")
        help_frame.pack(fill='x', padx=10, pady=5)
        
        # Create scrolled text widget with increased height and better styling
        help_text = scrolledtext.ScrolledText(
            help_frame, 
            wrap=tk.WORD, 
            height=12,  # Increased from 6 to 12
            font=('Segoe UI', 10),  # Added custom font
            padx=10,  # Added horizontal padding
            pady=5,   # Added vertical padding
            background='#f8f9fa',  # Light background color
            borderwidth=1,  # Reduced border width
            relief='solid'  # Solid border style
        )
        help_text.pack(fill='both', expand=True, padx=5, pady=5)  # Changed to fill both
        help_text.insert(tk.END, text)
        help_text.configure(state='disabled')

        # Add a note about scrolling
        scroll_note = ttk.Label(
            help_frame, 
            text="(Scroll down for more information)", 
            font=('Segoe UI', 8, 'italic'),
            foreground='#666666'
        )
        scroll_note.pack(anchor='e', padx=5, pady=(0, 5))

    def setup_prerequisites_tab(self):
        prerequisites_help = """Before starting the setup process, ensure you have the following requirements installed:

1. YouTube/Google Account:
   - Must have streaming enabled
   - Brand account support is available
   - Verify you can access YouTube Studio

2. Chrome Browser:
   - Required for automation
   - Make sure you're logged into your YouTube account
   - Note your Chrome profile name from chrome://version

3. Python 3.x:
   - Required for running the scripts
   - Make sure to check "Add to PATH" during installation
   - Restart may be required after installation

4. Streamlink:
   - Required for capturing Twitch streams
   - Follow the installation wizard
   - Verify installation by running 'streamlink --version'

5. FFmpeg:
   - Required for stream processing
   - Download the latest release
   - Must rename to specific filenames:
     * ffmpeg.exe
     * ffmpeg111.exe
   - Click 'FFmpeg Setup Guide' for detailed instructions"""
        
        label = ttk.Label(self.prerequisites_tab, text="Prerequisites Check", font=('Arial', 12, 'bold'))
        label.pack(pady=10)
        
        self.create_help_text(self.prerequisites_tab, prerequisites_help)
        
        # Create checklist frame
        checklist_frame = ttk.LabelFrame(self.prerequisites_tab, text="Required Items")
        checklist_frame.pack(fill='x', padx=10, pady=5)
        
        # YouTube Account Check
        self.yt_var = tk.BooleanVar()
        ttk.Checkbutton(checklist_frame, text="YouTube/Google account with streaming enabled", 
                       variable=self.yt_var).pack(anchor='w', padx=5, pady=2)
        
        # Chrome Check
        self.chrome_var = tk.BooleanVar()
        chrome_frame = ttk.Frame(checklist_frame)
        chrome_frame.pack(fill='x', padx=5, pady=2)
        ttk.Checkbutton(chrome_frame, text="Chrome Browser Installed", 
                       variable=self.chrome_var).pack(side='left')
        ttk.Button(chrome_frame, text="Download Chrome", 
                  command=lambda: webbrowser.open("https://chrome.google.com")).pack(side='right')

        # Python Check
        self.python_var = tk.BooleanVar()
        python_frame = ttk.Frame(checklist_frame)
        python_frame.pack(fill='x', padx=5, pady=2)
        ttk.Checkbutton(python_frame, text="Python Installed", 
                       variable=self.python_var).pack(side='left')
        ttk.Button(python_frame, text="Download Python", 
                  command=lambda: webbrowser.open("https://www.python.org/downloads/")).pack(side='right')

        # Streamlink Check
        self.streamlink_var = tk.BooleanVar()
        streamlink_frame = ttk.Frame(checklist_frame)
        streamlink_frame.pack(fill='x', padx=5, pady=2)
        ttk.Checkbutton(streamlink_frame, text="Streamlink Installed", 
                       variable=self.streamlink_var).pack(side='left')
        ttk.Button(streamlink_frame, text="Download Streamlink", 
                  command=lambda: webbrowser.open("https://github.com/streamlink/windows-builds/releases")).pack(side='right')

        # FFmpeg Check with enhanced options
        self.ffmpeg_var = tk.BooleanVar()
        ffmpeg_frame = ttk.Frame(checklist_frame)
        ffmpeg_frame.pack(fill='x', padx=5, pady=2)
        ttk.Checkbutton(ffmpeg_frame, text="FFmpeg Installed", 
                       variable=self.ffmpeg_var).pack(side='left')
        
        # FFmpeg buttons frame
        ffmpeg_buttons = ttk.Frame(ffmpeg_frame)
        ffmpeg_buttons.pack(side='right')
        
        ttk.Button(ffmpeg_buttons, text="Setup Guide", 
                  command=self.setup_ffmpeg_helper).pack(side='right', padx=2)
        ttk.Button(ffmpeg_buttons, text="Download FFmpeg", 
                  command=lambda: webbrowser.open("https://www.gyan.dev/ffmpeg/builds/")).pack(side='right', padx=2)

        # Verify Button
        ttk.Button(self.prerequisites_tab, text="Verify Prerequisites", 
                  command=self.verify_prerequisites).pack(pady=10)

    def setup_installation_tab(self):
        installation_help = """This tab helps you install the required Python packages:

1. Required Packages:
   - selenium: For browser automation
   - google-auth-oauthlib: For Google API authentication
   - google-api-python-client: For YouTube API access
   - psutil: For process management
   - requests: For HTTP requests
   - beautifulsoup4: For HTML parsing
   - streamlink: For Twitch stream capture
   - twitchAPI: For Twitch API access
   - aiohttp: For async HTTP requests

2. Installation Options:
   - Select individual packages to install
   - Or use "Install All Packages" for complete setup
   - Installation requires internet connection
   - May take a few minutes to complete

3. Verification:
   - Success message will appear when done
   - Check for any error messages
   - Retry installation if needed"""
        
        label = ttk.Label(self.installation_tab, text="Package Installation", font=('Arial', 12, 'bold'))
        label.pack(pady=10)
        
        self.create_help_text(self.installation_tab, installation_help)
        
        # Package installation frame
        install_frame = ttk.LabelFrame(self.installation_tab, text="Required Packages")
        install_frame.pack(fill='x', padx=10, pady=5)
        
        # Package list
        packages = [
            "selenium", "google-auth-oauthlib", "google-api-python-client",
            "psutil", "requests", "beautifulsoup4", "streamlink", "twitchAPI", "aiohttp"
        ]
        
        self.package_vars = {}
        for package in packages:
            var = tk.BooleanVar()
            self.package_vars[package] = var
            ttk.Checkbutton(install_frame, text=package, variable=var).pack(anchor='w', padx=5, pady=2)
        
        # Install button
        ttk.Button(self.installation_tab, text="Install Selected Packages", 
                  command=self.install_packages).pack(pady=10)
        
        # Install all button
        ttk.Button(self.installation_tab, text="Install All Packages", 
                  command=self.install_all_packages).pack(pady=5)

    def setup_google_api_tab(self):
        google_api_help = """Follow these steps to set up Google API access:

1. Google Cloud Console Setup:
   - Create a new project or select existing one
   - Enable required APIs:
     * YouTube Data API v3
     * Gmail API
   - Configure OAuth consent screen:
     * Add your email as test user
     * Add required scopes

2. OAuth Credentials:
   - Create OAuth 2.0 Client ID
   - Download client_secret.json
   - Select the file using the button below
   - File will be copied to project directory

3. Required Scopes:
   - https://www.googleapis.com/auth/youtube.force-ssl
   - https://www.googleapis.com/auth/userinfo.profile
   - https://www.googleapis.com/auth/gmail.readonly

4. Important Notes:
   - Keep your client_secret.json secure
   - Don't share or commit this file
   - Test user must be your channel email"""
        
        label = ttk.Label(self.google_api_tab, text="Google API Setup", font=('Arial', 12, 'bold'))
        label.pack(pady=10)
        
        self.create_help_text(self.google_api_tab, google_api_help)
        
        # Steps frame
        steps_frame = ttk.LabelFrame(self.google_api_tab, text="Setup Steps")
        steps_frame.pack(fill='x', padx=10, pady=5)
        
        # Google Cloud Console button
        ttk.Button(steps_frame, text="1. Open Google Cloud Console", 
                  command=lambda: webbrowser.open("https://console.cloud.google.com")).pack(anchor='w', padx=5, pady=2)
        
        # YouTube API button
        ttk.Button(steps_frame, text="2. Enable YouTube Data API v3", 
                  command=lambda: webbrowser.open("https://console.cloud.google.com/apis/library/youtube.googleapis.com")).pack(anchor='w', padx=5, pady=2)
        
        # Gmail API button
        ttk.Button(steps_frame, text="3. Enable Gmail API", 
                  command=lambda: webbrowser.open("https://console.cloud.google.com/apis/library/gmail.googleapis.com")).pack(anchor='w', padx=5, pady=2)
        
        # Client secret file frame
        secret_frame = ttk.LabelFrame(self.google_api_tab, text="Client Secret File")
        secret_frame.pack(fill='x', padx=10, pady=5)
        
        self.secret_path_var = tk.StringVar()
        ttk.Entry(secret_frame, textvariable=self.secret_path_var, state='readonly').pack(fill='x', padx=5, pady=2)
        ttk.Button(secret_frame, text="Select client_secret.json", 
                  command=self.select_client_secret).pack(pady=2)

    def setup_twitch_api_tab(self):
        twitch_api_help = """Configure your Twitch API access:

1. Twitch Developer Console:
   - Log in to dev.twitch.tv
   - Register a new application
   - Set OAuth Redirect URL to http://localhost
   - Category: Website Integration

2. API Credentials:
   - Copy Client ID from developer console
   - Generate and copy Client Secret
   - Enter both in the fields below
   - Keep these credentials secure

3. Twitch Username:
   - Enter the username of the channel to archive
   - Use only the username part of the URL
   - Example: For https://twitch.tv/example use 'example'

4. Important Notes:
   - Credentials are saved in config.ini
   - Used for stream detection and metadata
   - Required for automatic archiving"""
        
        label = ttk.Label(self.twitch_api_tab, text="Twitch API Setup", font=('Arial', 12, 'bold'))
        label.pack(pady=10)
        
        self.create_help_text(self.twitch_api_tab, twitch_api_help)
        
        # Twitch credentials frame
        creds_frame = ttk.LabelFrame(self.twitch_api_tab, text="API Credentials")
        creds_frame.pack(fill='x', padx=10, pady=5)
        
        # Client ID
        ttk.Label(creds_frame, text="Client ID:").pack(anchor='w', padx=5, pady=2)
        self.client_id_var = tk.StringVar()
        ttk.Entry(creds_frame, textvariable=self.client_id_var).pack(fill='x', padx=5, pady=2)
        
        # Client Secret
        ttk.Label(creds_frame, text="Client Secret:").pack(anchor='w', padx=5, pady=2)
        self.client_secret_var = tk.StringVar()
        ttk.Entry(creds_frame, textvariable=self.client_secret_var).pack(fill='x', padx=5, pady=2)
        
        # Twitch Username
        ttk.Label(creds_frame, text="Twitch Username to Archive:").pack(anchor='w', padx=5, pady=2)
        self.twitch_username_var = tk.StringVar()
        ttk.Entry(creds_frame, textvariable=self.twitch_username_var).pack(fill='x', padx=5, pady=2)
        
        # Open Twitch Dev Console button
        ttk.Button(self.twitch_api_tab, text="Open Twitch Developer Console", 
                  command=lambda: webbrowser.open("https://dev.twitch.tv/console")).pack(pady=10)
        
        # Save button
        ttk.Button(self.twitch_api_tab, text="Save Twitch Configuration", 
                  command=self.save_twitch_config).pack(pady=5)

    def setup_config_tab(self):
        config_help = """Configure your streaming setup:

1. Chrome Profile:
   - Find your profile in chrome://version
   - Copy the folder name after "Profile Path"
   - Usually "Default" or "Profile X"

2. YouTube Settings:
   - Account Name: Your Google account name
   - Brand Account: Check if using a brand account
   - Brand Account Name: Name shown in YouTube Studio

3. RTMP Settings:
   - Create two RTMP keys in YouTube Studio
   - Name Format:
     * Key 1: username
     * Key 2: 1usernamemult
   - Enter both names and keys
   - Keep keys secure and private

4. Important Notes:
   - All settings saved in config.ini
   - config_tv.py generated automatically
   - Restart application after changes
   - Test stream recommended before use"""
        
        # Main container for the tab
        main_container = ttk.Frame(self.config_tab)
        main_container.pack(fill='both', expand=True)
        
        # Title and help text at the top (non-scrolling)
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill='x', pady=5)
        
        label = ttk.Label(top_frame, text="General Configuration", font=('Arial', 12, 'bold'))
        label.pack(pady=10)
        
        self.create_help_text(top_frame, config_help)
        
        # Create canvas and scrollbar for settings
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Config frame
        config_frame = ttk.LabelFrame(scrollable_frame, text="Settings")
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # Chrome Profile
        ttk.Label(config_frame, text="Chrome Profile:").pack(anchor='w', padx=5, pady=2)
        self.chrome_profile_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.chrome_profile_var).pack(fill='x', padx=5, pady=2)
        
        # YouTube Settings
        yt_frame = ttk.LabelFrame(config_frame, text="YouTube Settings")
        yt_frame.pack(fill='x', padx=5, pady=5)
        
        # Account Name
        ttk.Label(yt_frame, text="YouTube Account Name:").pack(anchor='w', padx=5, pady=2)
        self.yt_account_var = tk.StringVar()
        ttk.Entry(yt_frame, textvariable=self.yt_account_var).pack(fill='x', padx=5, pady=2)
        
        # Brand Account
        self.brand_acc_var = tk.BooleanVar()
        ttk.Checkbutton(yt_frame, text="Using Brand Account", 
                       variable=self.brand_acc_var, 
                       command=self.toggle_brand_account_name).pack(anchor='w', padx=5, pady=2)
        
        # Brand Account Name
        ttk.Label(yt_frame, text="Brand Account Name (if applicable):").pack(anchor='w', padx=5, pady=2)
        self.brand_acc_name_var = tk.StringVar()
        self.brand_acc_name_entry = ttk.Entry(yt_frame, textvariable=self.brand_acc_name_var)
        self.brand_acc_name_entry.pack(fill='x', padx=5, pady=2)
        
        # Initialize brand account name entry state
        self.toggle_brand_account_name()
        
        # RTMP Settings
        rtmp_frame = ttk.LabelFrame(config_frame, text="RTMP Settings")
        rtmp_frame.pack(fill='x', padx=5, pady=5)
        
        # RTMP Key Names
        ttk.Label(rtmp_frame, text="RTMP Key Name:").pack(anchor='w', padx=5, pady=2)
        self.rtmp_key_name_var = tk.StringVar()
        ttk.Entry(rtmp_frame, textvariable=self.rtmp_key_name_var).pack(fill='x', padx=5, pady=2)
        
        ttk.Label(rtmp_frame, text="RTMP Key Name 1:").pack(anchor='w', padx=5, pady=2)
        self.rtmp_key_name1_var = tk.StringVar()
        ttk.Entry(rtmp_frame, textvariable=self.rtmp_key_name1_var).pack(fill='x', padx=5, pady=2)
        
        # RTMP Keys
        ttk.Label(rtmp_frame, text="RTMP Key:").pack(anchor='w', padx=5, pady=2)
        self.rtmp_key_var = tk.StringVar()
        ttk.Entry(rtmp_frame, textvariable=self.rtmp_key_var).pack(fill='x', padx=5, pady=2)
        
        ttk.Label(rtmp_frame, text="RTMP Key 1:").pack(anchor='w', padx=5, pady=2)
        self.rtmp_key1_var = tk.StringVar()
        ttk.Entry(rtmp_frame, textvariable=self.rtmp_key1_var).pack(fill='x', padx=5, pady=2)
        
        # Save button
        ttk.Button(scrollable_frame, text="Save Configuration", 
                  command=self.save_config).pack(pady=10)
        
        # Update canvas when window is resized
        def _configure_canvas(event):
            canvas.configure(width=event.width-20)  # -20 to account for scrollbar
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width-20)
        
        canvas.bind("<Configure>", _configure_canvas)

    def toggle_brand_account_name(self):
        """Enable/disable brand account name entry based on checkbox state"""
        if self.brand_acc_var.get():
            self.brand_acc_name_entry.configure(state='normal')
        else:
            self.brand_acc_name_var.set("")  # Clear the field when disabled
            self.brand_acc_name_entry.configure(state='disabled')

    def verify_prerequisites(self):
        results = []
        all_passed = True
        
        # Check Python
        try:
            python_version = sys.version_info
            if python_version.major >= 3:
                self.python_var.set(True)
                results.append("✓ Python 3 is installed")
            else:
                all_passed = False
                results.append("✗ Python 3 is required")
        except:
            all_passed = False
            results.append("✗ Could not verify Python installation")
        
        # Check Chrome
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        if any(os.path.exists(path) for path in chrome_paths):
            self.chrome_var.set(True)
            results.append("✓ Chrome is installed")
        else:
            all_passed = False
            results.append("✗ Chrome is not found")
        
        # Check Streamlink
        try:
            subprocess.run(["streamlink", "--version"], capture_output=True, check=True)
            self.streamlink_var.set(True)
            results.append("✓ Streamlink is installed")
        except:
            all_passed = False
            results.append("✗ Streamlink is not found")
        
        # Check FFmpeg
        ffmpeg_files_exist = all(os.path.exists(file) for file in [self.ffmpeg_name1.get(), self.ffmpeg_name2.get()])
        if ffmpeg_files_exist:
            self.ffmpeg_var.set(True)
            results.append(f"✓ FFmpeg files found ({self.ffmpeg_name1.get()}, {self.ffmpeg_name2.get()})")
        else:
            all_passed = False
            results.append(f"✗ FFmpeg files not found (looking for {self.ffmpeg_name1.get()}, {self.ffmpeg_name2.get()})")
        
        # Display results
        messagebox.showinfo("Prerequisites Check", "\n".join(results))
        
        # Enable next tab if all checks passed
        if all_passed:
            self.enable_next_tab(0)

    def install_packages(self):
        selected_packages = [pkg for pkg, var in self.package_vars.items() if var.get()]
        if not selected_packages:
            messagebox.showwarning("Warning", "No packages selected!")
            return
            
        cmd = [sys.executable, "-m", "pip", "install"] + selected_packages
        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Success", "Selected packages installed successfully!")
            # Enable next tab after successful installation
            self.enable_next_tab(1)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to install packages: {str(e)}")

    def install_all_packages(self):
        for var in self.package_vars.values():
            var.set(True)
        self.install_packages()

    def select_client_secret(self):
        filename = filedialog.askopenfilename(
            title="Select client_secret.json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            # Copy file to current directory
            try:
                shutil.copy(filename, "client_secret.json")
                self.secret_path_var.set("client_secret.json")
                messagebox.showinfo("Success", "Client secret file copied successfully!")
                # Enable next tab after successful file selection
                self.enable_next_tab(2)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {str(e)}")

    def save_twitch_config(self):
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.twitch_username_var.get()]):
            messagebox.showwarning("Warning", "Please fill in all Twitch API fields!")
            return
            
        self.config.update({
            'client_id': self.client_id_var.get(),
            'client_secret': self.client_secret_var.get(),
            'username': self.twitch_username_var.get()
        })
        self.save_config()
        # Enable next tab after saving Twitch config
        self.enable_next_tab(3)

    def save_config(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'Chrome_Profile': self.chrome_profile_var.get(),
            'accountname': self.yt_account_var.get(),
            'brandacc': str(self.brand_acc_var.get()),
            'brandaccname': self.brand_acc_name_var.get(),
            'rtmpkeyname': self.rtmp_key_name_var.get(),
            'rtmpkeyname1': self.rtmp_key_name1_var.get(),
            'rtmp_key': self.rtmp_key_var.get(),
            'rtmp_key_1': self.rtmp_key1_var.get(),
            'client_id': self.client_id_var.get(),
            'client_secret': self.client_secret_var.get(),
            'username': self.twitch_username_var.get(),
            'ffmpeg': self.ffmpeg_name1.get(),
            'ffmpeg1': self.ffmpeg_name2.get()
        }
        
        try:
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            # Generate config_tv.py
            self.generate_config_tv()
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        # First try to load from config_tv.py if it exists
        if os.path.exists('config_tv.py'):
            try:
                import config_tv
                import importlib
                importlib.reload(config_tv)  # Reload to get latest changes
                
                self.chrome_profile_var.set(config_tv.Chrome_Profile)
                self.yt_account_var.set(config_tv.accountname)
                self.brand_acc_var.set(config_tv.brandacc == "True")
                self.brand_acc_name_var.set(config_tv.brandaccname)
                self.rtmp_key_name_var.set(config_tv.rtmpkeyname)
                self.rtmp_key_name1_var.set(config_tv.rtmpkeyname1)
                self.rtmp_key_var.set(config_tv.rtmp_key)
                self.rtmp_key1_var.set(config_tv.rtmp_key_1)
                self.client_id_var.set(config_tv.client_id)
                self.client_secret_var.set(config_tv.client_secret)
                self.twitch_username_var.set(config_tv.username)
                self.ffmpeg_name1.set(config_tv.ffmpeg)
                self.ffmpeg_name2.set(config_tv.ffmpeg1)
                
                # If config_tv.py exists and loads successfully, enable all tabs
                if self.is_config_complete():
                    for i in range(len(self.notebook.tabs())):
                        self.notebook.tab(i, state='normal')
                return
            except Exception:
                # If there's any error loading config_tv.py, fall back to config.ini
                pass
        
        # Fall back to config.ini if config_tv.py doesn't exist or has errors
        if os.path.exists('config.ini'):
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            if 'DEFAULT' in config:
                self.chrome_profile_var.set(config['DEFAULT'].get('Chrome_Profile', ''))
                self.yt_account_var.set(config['DEFAULT'].get('accountname', ''))
                self.brand_acc_var.set(config['DEFAULT'].getboolean('brandacc', False))
                self.brand_acc_name_var.set(config['DEFAULT'].get('brandaccname', ''))
                self.rtmp_key_name_var.set(config['DEFAULT'].get('rtmpkeyname', ''))
                self.rtmp_key_name1_var.set(config['DEFAULT'].get('rtmpkeyname1', ''))
                self.rtmp_key_var.set(config['DEFAULT'].get('rtmp_key', ''))
                self.rtmp_key1_var.set(config['DEFAULT'].get('rtmp_key_1', ''))
                self.client_id_var.set(config['DEFAULT'].get('client_id', ''))
                self.client_secret_var.set(config['DEFAULT'].get('client_secret', ''))
                self.twitch_username_var.set(config['DEFAULT'].get('username', ''))
                self.ffmpeg_name1.set(config['DEFAULT'].get('ffmpeg', 'ffmpeg.exe'))
                self.ffmpeg_name2.set(config['DEFAULT'].get('ffmpeg1', 'ffmpeg111.exe'))

    def is_config_complete(self):
        """Check if all required configuration files and settings are present"""
        # Check if config_tv.py exists
        if not os.path.exists('config_tv.py'):
            return False
            
        # Check if client_secret.json exists
        if not os.path.exists('client_secret.json'):
            return False
            
        # Check if FFmpeg files exist
        if not all(os.path.exists(file) for file in [self.ffmpeg_name1.get(), self.ffmpeg_name2.get()]):
            return False
            
        try:
            # Try to import and verify config_tv.py
            import config_tv
            import importlib
            importlib.reload(config_tv)
            
            # Check required attributes
            required_attrs = [
                'Chrome_Profile',
                'accountname',
                'brandacc',
                'brandaccname',
                'rtmpkeyname',
                'rtmpkeyname1',
                'rtmp_key',
                'rtmp_key_1',
                'client_id',
                'client_secret',
                'username',
                'ffmpeg',
                'ffmpeg1'
            ]
            
            # Verify all required attributes exist and have non-empty values
            for attr in required_attrs:
                if not hasattr(config_tv, attr) or not getattr(config_tv, attr):
                    return False
                    
            # Special check for brand account
            if getattr(config_tv, 'brandacc') == "True" and not getattr(config_tv, 'brandaccname'):
                return False
                
            return True
            
        except Exception:
            return False

    def generate_config_tv(self):
        config_content = f'''#ARCHIVE STREAMER USERNAME
username = "{self.twitch_username_var.get()}" #twitch or bilibili username
##########################################################################
#ARCHIVE SETTINGS
ytshort = "False" #not recommand
unliststream = "False" #after stream will be public
disablechat = "True"  #disable chat on live stream
##########################################################################
#YOUTUBE STUDIO RTMP SETTINGS
rtmpkeyname1 = "{self.rtmp_key_name1_var.get()}" #first yt rtmp key name
rtmpkeyname = "{self.rtmp_key_name_var.get()}" #second yt rtmp key name
rtmp_key = "{self.rtmp_key_var.get()}" #first yt rtmp key
rtmp_key_1 = "{self.rtmp_key1_var.get()}" #second yt rtmp key
##########################################################################
#CHROME PROFILE FOLDER NAME
Chrome_Profile = "{self.chrome_profile_var.get()}" #chrome profile folder name
##########################################################################
#API SETTINGS
accountname = "{self.yt_account_var.get()}" #google account name(not brand acc have email) when login to google api
brandacc = "{str(self.brand_acc_var.get())}" #do you use the brand acc as the archive channel
brandaccname = "{self.brand_acc_name_var.get() or 'Null'}" #if you have brand acc copy the google account name when login to google api
#TWITCH API SETTINGS
client_id = "{self.client_id_var.get()}" #twitch api client id
client_secret = "{self.client_secret_var.get()}" #twitch api client sercet
##########################################################################
#EXE NAME
ffmpeg1 = "{self.ffmpeg_name2.get()}" #ffmpeg exe name
ffmpeg = "{self.ffmpeg_name1.get()}" #ffmpeg exe name
apiexe = "ffmpeg_api.exe" #api exe name'''
        
        try:
            with open('config_tv.py', 'w') as f:
                f.write(config_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate config_tv.py: {str(e)}")

    def setup_ffmpeg_helper(self):
        ffmpeg_help = """FFmpeg Installation Guide:

1. Download FFmpeg:
   - Go to https://www.gyan.dev/ffmpeg/builds/
   - Download "ffmpeg-git-full.7z" (full build with all features)
   - Extract the downloaded archive

2. Setup FFmpeg Files:
   - Click "Select FFmpeg.exe" button below
   - Select the ffmpeg.exe from the bin folder
   - Enter your desired filenames below (or use defaults)
   - The tool will automatically create copies with your chosen names

3. Verification:
   - Use "Check FFmpeg Files" to verify setup
   - Both files should be in project directory
   - Names must match exactly (case sensitive)

4. Common Issues:
   - Extract the 7z archive completely before selecting
   - Make sure ffmpeg.exe is from the bin folder
   - Ensure you have write permissions in project directory
   - Close any running FFmpeg processes"""

        # Create new window for FFmpeg help
        ffmpeg_window = tk.Toplevel(self.root)
        ffmpeg_window.title("FFmpeg Setup Guide")
        ffmpeg_window.geometry("600x700")  # Made window taller for new inputs
        
        # Add help text
        help_text = scrolledtext.ScrolledText(
            ffmpeg_window,
            wrap=tk.WORD,
            height=15,
            font=('Segoe UI', 10),
            padx=10,
            pady=5,
            background='#f8f9fa',
            borderwidth=1,
            relief='solid'
        )
        help_text.pack(fill='both', expand=True, padx=10, pady=5)
        help_text.insert(tk.END, ffmpeg_help)
        help_text.configure(state='disabled')
        
        # Add FFmpeg filename configuration frame
        filename_frame = ttk.LabelFrame(ffmpeg_window, text="FFmpeg Filenames")
        filename_frame.pack(fill='x', padx=10, pady=5)
        
        # First FFmpeg filename
        ttk.Label(filename_frame, text="Primary FFmpeg filename:").pack(anchor='w', padx=5, pady=2)
        ttk.Entry(filename_frame, textvariable=self.ffmpeg_name1).pack(fill='x', padx=5, pady=2)
        
        # Second FFmpeg filename
        ttk.Label(filename_frame, text="Secondary FFmpeg filename:").pack(anchor='w', padx=5, pady=2)
        ttk.Entry(filename_frame, textvariable=self.ffmpeg_name2).pack(fill='x', padx=5, pady=2)
        
        # Reset to defaults button
        ttk.Button(
            filename_frame,
            text="Reset to Defaults",
            command=lambda: self.reset_ffmpeg_names()
        ).pack(anchor='e', padx=5, pady=5)
        
        # Add status frame
        status_frame = ttk.LabelFrame(ffmpeg_window, text="Setup Status")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.ffmpeg_status = ttk.Label(status_frame, text="Waiting for FFmpeg setup...", font=('Segoe UI', 9))
        self.ffmpeg_status.pack(padx=5, pady=5)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(ffmpeg_window)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        # Download button
        ttk.Button(
            buttons_frame,
            text="1. Download FFmpeg",
            command=lambda: webbrowser.open("https://www.gyan.dev/ffmpeg/builds/")
        ).pack(side='left', padx=5)
        
        # Select and Setup button
        ttk.Button(
            buttons_frame,
            text="2. Select FFmpeg.exe",
            command=lambda: self.setup_ffmpeg_files()
        ).pack(side='left', padx=5)
        
        # Check installation button
        ttk.Button(
            buttons_frame,
            text="3. Verify Setup",
            command=lambda: self.check_ffmpeg_files(True)
        ).pack(side='left', padx=5)

    def reset_ffmpeg_names(self):
        """Reset FFmpeg filenames to defaults"""
        self.ffmpeg_name1.set("ffmpeg.exe")
        self.ffmpeg_name2.set("ffmpeg111.exe")

    def setup_ffmpeg_files(self):
        try:
            # Validate filenames
            if not self.ffmpeg_name1.get().endswith('.exe') or not self.ffmpeg_name2.get().endswith('.exe'):
                messagebox.showerror("Error", "Both filenames must end with .exe")
                return
            
            if self.ffmpeg_name1.get() == self.ffmpeg_name2.get():
                messagebox.showerror("Error", "FFmpeg filenames must be different")
                return
            
            # Select original ffmpeg.exe
            ffmpeg_path = filedialog.askopenfilename(
                title="Select ffmpeg.exe",
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
                initialfile="ffmpeg.exe"
            )
            
            if not ffmpeg_path:
                return
            
            if not os.path.basename(ffmpeg_path).lower() == "ffmpeg.exe":
                messagebox.showerror("Error", "Please select a file named 'ffmpeg.exe'")
                return
            
            # Create copies with new names
            try:
                # Copy with first name
                shutil.copy2(ffmpeg_path, self.ffmpeg_name1.get())
                # Create second copy
                shutil.copy2(ffmpeg_path, self.ffmpeg_name2.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create FFmpeg files: {str(e)}")
                return
            
            # Update config with new names
            self.update_ffmpeg_config()
            
            # Verify the setup
            self.check_ffmpeg_files(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup FFmpeg: {str(e)}")

    def update_ffmpeg_config(self):
        """Update config with current FFmpeg filenames"""
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
        
        if 'DEFAULT' not in config:
            config['DEFAULT'] = {}
        
        config['DEFAULT']['ffmpeg'] = self.ffmpeg_name1.get()
        config['DEFAULT']['ffmpeg1'] = self.ffmpeg_name2.get()
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
        # Also update config_tv.py
        self.save_config()

    def check_ffmpeg_files(self, show_success=False):
        required_files = [self.ffmpeg_name1.get(), self.ffmpeg_name2.get()]
        missing_files = []
        found_files = []
        
        for file in required_files:
            if os.path.exists(file):
                found_files.append(file)
            else:
                missing_files.append(file)
        
        if missing_files:
            message = "Missing FFmpeg files:\n"
            for file in missing_files:
                message += f"❌ {file}\n"
            if found_files:
                message += "\nFound files:\n"
                for file in found_files:
                    message += f"✓ {file}\n"
            message += "\nPlease ensure both FFmpeg files are in the project directory."
            messagebox.showwarning("FFmpeg Check", message)
            if hasattr(self, 'ffmpeg_status'):
                self.ffmpeg_status.config(
                    text="❌ FFmpeg setup incomplete - missing files",
                    foreground='red'
                )
        else:
            if show_success:
                messagebox.showinfo("FFmpeg Check", f"✓ All required FFmpeg files found!\n\n{self.ffmpeg_name1.get()}\n{self.ffmpeg_name2.get()}")
            if hasattr(self, 'ffmpeg_status'):
                self.ffmpeg_status.config(
                    text="✓ FFmpeg setup complete - all files present",
                    foreground='green'
                )

    def enable_next_tab(self, current_tab_index):
        """Enable the next tab after completing the current one"""
        if current_tab_index < len(self.notebook.tabs()) - 1:
            self.notebook.tab(current_tab_index + 1, state='normal')
            self.notebook.select(current_tab_index + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupGUI(root)
    root.mainloop() 
