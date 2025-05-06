import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps
import json
import os
import keyring
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
from pathlib import Path
import requests
import math
import subprocess
import threading
import pystray
import ctypes

# Import the login core
from login_core import LoginManager

# --- Main Application Window ---
class MiniLoginApp(ctk.CTk):
    def __init__(self, headless=False):
        super().__init__()
        
        # Application constants
        self.APP_NAME = "Simulanis Login Mini"
        self.KEYRING_SERVICE = "SimulanisLogin"
        self.TARGET_URL = "https://192.168.1.9/userlogin/"
        
        # Store internal credential vars
        self._username = None
        self._password = None
        
        # Setup variables
        self.remember_me_var = tk.BooleanVar(value=False)
        self.auto_login_var = tk.BooleanVar(value=False)
        self.headless_mode_var = tk.BooleanVar(value=False)
        
        # Overrides
        self.headless = headless
        
        # Store window initialization for drag support
        self._drag_start_x = None
        self._drag_start_y = None
        
        # Setup UI
        self.title(self.APP_NAME)
        self.geometry("280x150")
        self.minsize(280, 150)
        self.maxsize(280, 150)
        self.overrideredirect(True)  # Remove default titlebar
        
        # Apply modern styling if on Windows
        if sys.platform == 'win32':
            self.apply_modern_window_style()
        
        # Set the color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Determine config directory
        self.config_dir = str(Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent)
        self.log(f"Using config directory: {self.config_dir}")
        
        # Create login manager
        self.login_mgr = LoginManager(headless=headless, ui_callback=self.update_status, config_dir=self.config_dir)
        
        # Load icons
        self.load_icons()
        
        # Setup UI
        self.setup_mini_gui()
        
        # Initialize tray icon variable
        self.tray_icon = None
        
        # Clean up any existing window handle files
        try:
            if os.path.exists("mini_ui_handle.txt"):
                os.remove("mini_ui_handle.txt")
                print("Removed existing mini_ui_handle.txt file")
        except Exception as e:
            print(f"Error cleaning up window handle file: {str(e)}")
        
        # Set a unique window class name for identification
        if sys.platform == 'win32':
            try:
                # This helps with window identification for restore functionality
                ctypes.windll.user32.SetClassLongW(
                    self.winfo_id(), -20, 
                    ctypes.windll.user32.GetClassLongW(self.winfo_id(), -20) | 0x00020000)
                
                # Apply rounded corners for Windows 11 style
                self.apply_modern_window_style()
            except Exception as e:
                print(f"Warning: Could not set window class or style - {str(e)}")
        
        # Track connection state for UI updates
        self.is_connected = False
        
        # Load saved configuration (still needed for auto-login check)
        self.load_config()
        
        # Update UI variables from loaded config
        self.remember_me_var.set(self.login_mgr.config.get('remember_me', False))
        self.auto_login_var.set(self.login_mgr.config.get('auto_login', False))
        self.headless_mode_var.set(self.login_mgr.config.get('headless_mode', False))
        
        # Check for auto-login
        if self.auto_login_var.get() and self.login_mgr.get_saved_username() and self.login_mgr.get_saved_password():
            # Directly perform login if credentials available
            self.after(100, self.perform_login) 
        else:
            # If not auto-login, show connect button
            self.connect_button.grid(row=1, column=0, padx=5, pady=(0, 0), sticky="")
            # And update status to hint user
            self.update_status("Click Connect to log in")

    def position_window_top_right(self):
        """Position the window in the top right corner of the screen"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        window_width = self.winfo_width()
        x = screen_width - window_width - 10 # 10px padding
        y = 10 # 10px padding from top
        self.geometry(f"+{x}+{y}")

    def load_icons(self):
        """Load icons for the application"""
        try:
            # Load icons from the Icons directory
            icons_dir = Path("Icons")
            if not icons_dir.exists():
                # Attempt to create if doesn't exist, but don't fail hard
                try: icons_dir.mkdir()
                except OSError:
                     print("Warning: Icons directory not found and could not be created.")
                
            # Define icon paths (can add status icons here)
            self.icons = {
                "connect": self.load_icon("connect.png", (35, 35)), # Increased connect icon size
                "disconnect": self.load_icon("disconnect.png", (20, 20)),
                "settings": self.load_icon("settings.png", (20, 20)),
                "close": self.load_icon("close.png", (15, 15))
            }
            
            # Check if any icons failed to load and set to None
            for key in self.icons:
                if self.icons[key] is None:
                    print(f"Info: Using text fallback for missing icon: {key}")
        except Exception as e:
            print(f"Error loading icons: {str(e)}")
            self.icons = {}
            
    def load_icon(self, icon_name, size):
        """Load and resize an icon"""
        try:
            # Look for icons relative to script or executable path
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            icon_path = base_path / "Icons" / icon_name

            # Fallback to just looking in cwd/Icons if not found relative to script/exe
            if not icon_path.exists():
                 icon_path = Path("Icons") / icon_name

            if icon_path.exists():
                return ctk.CTkImage(
                    light_image=Image.open(icon_path),
                    dark_image=Image.open(icon_path),
                    size=size
                )
            else:
                 print(f"Warning: Icon '{icon_name}' not found at {icon_path}")
        except Exception as e:
            print(f"Error loading icon {icon_name}: {str(e)}")
        return None
        
    def setup_mini_gui(self):
        """Setup the minimal GUI elements"""
        # Configure grid rows with proper weights
        self.grid_rowconfigure(0, weight=0, minsize=20) # Logo row with minimal height
        self.grid_rowconfigure(1, weight=0, minsize=25) # Connect button row with minimal height
        self.grid_rowconfigure(2, weight=1) # Status label and progress bar row
        self.grid_columnconfigure(0, weight=1) # Stretch to fill width

        # Logo at the top (small version)
        try:
            logo_path = os.path.join("Logos", "Logo_mini.png")
            if os.path.exists(logo_path):
                # Load logo and preserve aspect ratio
                original_image = Image.open(logo_path)
                width, height = original_image.size
                
                # Calculate aspect ratio
                aspect_ratio = width / height
                
                # Set target width and calculate height to maintain aspect ratio
                # Smaller logo to fit better - reduced size
                target_width = 100
                target_height = int(target_width / aspect_ratio)
                
                # Create CustomTkinter image
                self.logo_image = ctk.CTkImage(
                    light_image=original_image,
                    dark_image=original_image,
                    size=(target_width, target_height)
                )
                
                # Add logo label
                self.logo_label = ctk.CTkLabel(
                    self,
                    image=self.logo_image,
                    text="",
                    height=40  # Minimum height
                )
                self.logo_label.grid(row=0, column=0, padx=10, pady=(25, 10), sticky="n")
            else:
                # Fallback to text if logo not found
                self.logo_label = ctk.CTkLabel(
                    self,
                    text="Simulanis",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("gray90", "gray90"),
                    height=20  # Minimum height
                )
                self.logo_label.grid(row=0, column=0, padx=10, pady=(0, 0), sticky="n")
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
            # Continue without logo

        # Connect/Login Button in second row
        self.connect_button = ctk.CTkButton(
            self,
            text="",  # No text, just icon
            image=self.icons.get("connect"),  # Use connect icon
            command=self.trigger_login, 
            width=40,  # Smaller width for icon only
            height=40, # Square shape for icon
            corner_radius=0,  # Circular button
            fg_color="transparent",  # Transparent background
            hover_color=("gray90", "gray30"),  # Subtle hover effect
            border_width=0  # No border
        )
        # Place in row 1 (second row)
        self.connect_button.grid(row=1, column=0, padx=5, pady=(0, 0), sticky="")

        # Status message in third row
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=13),
            text_color=("lightgrey", "lightgrey"),
            wraplength=self.winfo_width() - 40, # Wrap text
            height=30 # Ensure there's enough height
        )
        self.status_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky="n")
        
        # Settings/Options Button - place in top-right corner
        self.settings_button = ctk.CTkButton(
            self,
            text="" if self.icons.get("settings") else "⚙", # Use gear emoji if icon not available
            image=self.icons.get("settings"),
            command=self.open_full_gui, # Open auto_login_gui.py
            width=25, 
            height=25,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
        )
        self.settings_button.place(relx=1.0, rely=0.0, x=-30, y=8, anchor="ne") # Position in top-right
        
        # Progress bar - place in third row below status label
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=self.winfo_width()-20,
            height=5, 
            corner_radius=2,
            fg_color=("gray85", "gray20"),
            progress_color=("#2CC985", "#2FA572")
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=0, padx=10, pady=(35, 5), sticky="s") # Place below status in same row
        self.progress_bar.grid_remove() # Hide initially
        
        # Bind Enter key to login action
        self.bind('<Return>', lambda e: self.trigger_login())
        
    def trigger_login(self):
        """Check for credentials and either show dialog or perform login directly"""
        # Try to use saved credentials if available
        username = self.login_mgr.get_saved_username()
        password = self.login_mgr.get_saved_password()
        
        # Hide connect button immediately
        if hasattr(self, 'connect_button'):
            self.connect_button.grid_remove()
            
        # Move status label up to row 1 after button is hidden
        if hasattr(self, 'status_label'):
            self.status_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="n")
            # Also move progress bar up if it's visible
            if hasattr(self, 'progress_bar') and self.progress_bar.winfo_ismapped():
                self.progress_bar.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="s")
        
        if username and password:
            self.perform_login(username, password)
        else:
            # No credentials available, open the full auto login GUI instead of showing dialog
            self.update_status("Opening settings for login...")
            self.open_full_gui(needs_credentials=True)

    def update_status(self, message, progress=None):
        """Update status message and progress bar"""
        # Always log the status message
        self.log(message)
        
        # Only update GUI elements if not in headless mode
        if not hasattr(self, 'headless') or not self.headless:
            self.status_label.configure(text=message)
            
            if progress is not None:
                if progress > 0:
                    # Ensure progress bar uses grid if shown
                    # Check if connect button is visible to determine row
                    if hasattr(self, 'connect_button') and self.connect_button.winfo_ismapped():
                        self.progress_bar.grid(row=2, column=0, padx=10, pady=(35, 5), sticky="s")
                    else:
                        self.progress_bar.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="s")
                    self.progress_bar.set(progress / 100)
                else:
                    self.progress_bar.grid_remove()  # Hide progress bar
            else:
                self.progress_bar.grid_remove()  # Hide progress bar when no progress specified
            
            self.update()
            
    def log(self, message):
        """Add a message to the log text area or console"""
        if hasattr(self, 'headless') and self.headless:
            self.console_log(message)
        else:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {message}")

    def console_log(self, message):
        """Log message to console in headless mode"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def load_config(self):
        """Load saved configuration from config.json"""
        try:
            # Look for config relative to script/exe first
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            config_path = base_path / 'config.json'

            # Fallback to current working directory
            if not config_path.exists():
                config_path = Path('config.json')

            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                    # Load username for keyring lookup
                    self.saved_username = config.get('username') 
                    
                    # Load settings
                    self.remember_me_var.set(config.get('remember_me', False))
                    self.auto_login_var.set(config.get('auto_login', False))
                    self.headless_mode_var.set(config.get('headless_mode', False))
                    
                    self.log("Loaded config")
                    
                    # Pre-fill internal creds if available (for auto-login or direct connect)
                    if self.saved_username and self.remember_me_var.get():
                         self._username = self.saved_username
                         self._password = self.login_mgr.get_saved_password() # Load from keyring
                         if self._password:
                              self.log("Loaded saved credentials")
                         else:
                              self.log("Saved username found, but no password in keyring.")
                              self._username = None # Clear if password missing
                              self.remember_me_var.set(False) # Ensure remember me is off if pwd fails
                    else:
                         self._username = None
                         self._password = None
            else:
                # Defaults if no config file
                self.saved_username = None
                self._username = None
                self._password = None
                self.remember_me_var.set(False)
                self.auto_login_var.set(False)
                self.headless_mode_var.set(False)
                self.log("No config file found, using defaults.")

        except Exception as e:
            self.log(f"Error loading config: {str(e)}")
            # Reset to defaults on error
            self.saved_username = None
            self._username = None
            self._password = None
            self.remember_me_var.set(False)
            self.auto_login_var.set(False)
            self.headless_mode_var.set(False)

    def add_close_button(self):
        """Add a close button to the top-right corner"""
        close_btn = ctk.CTkButton(
            self, 
            text="✕", # Simple X symbol
            command=self.quit_app, 
            width=20, 
            height=20,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color="#FF4444", # Red hover like main app
            corner_radius=0 
        )
        # Place it at the very top right, slightly inside the border
        close_btn.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")
        
        # Make sure settings button doesn't overlap with close button
        if hasattr(self, 'settings_button'):
            self.settings_button.place(relx=1.0, rely=0.0, x=-30, y=5, anchor="ne")

    def start_move(self, event):
        """Begin window drag"""
        # Only allow dragging if button press is on the main background (not buttons or close button)
        if event.widget == self or event.widget == self.status_label:
             self._drag_start_x = event.x
             self._drag_start_y = event.y
        else:
             self._drag_start_x = None
             self._drag_start_y = None

    def stop_move(self, event):
        """End window drag"""
        self._drag_start_x = None
        self._drag_start_y = None

    def do_move(self, event):
        """Handle window drag"""
        if hasattr(self, '_drag_start_x') and self._drag_start_x is not None:
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            new_x = self.winfo_x() + dx
            new_y = self.winfo_y() + dy
            # Ensure window stays within screen bounds (optional)
            # screen_width = self.winfo_screenwidth()
            # screen_height = self.winfo_screenheight()
            # win_width = self.winfo_width()
            # win_height = self.winfo_height()
            # new_x = max(0, min(new_x, screen_width - win_width))
            # new_y = max(0, min(new_y, screen_height - win_height))
            self.geometry(f"+{new_x}+{new_y}")
            
    def save_config(self, username, password):
        """Save configuration and credentials"""
        try:
            # Prepare config data
            config_data = {
                'username': username,
                'remember_me': self.remember_me_var.get(),
                'auto_login': self.auto_login_var.get(),
                'headless_mode': self.headless_mode_var.get()
            }
            
            # Save to config file
            self.login_mgr.save_config(config_data)
            
            # Save password if remember me is checked
            if self.remember_me_var.get():
                self.login_mgr.save_credentials(username, password, True)
            
            self.log("Config saved")
        except Exception as e:
            self.log(f"Error saving config: {str(e)}")

    def on_minimize(self, event=None):
        """Handle window being minimized (unmap event)"""
        # Do something when window is minimized, if needed
        print(f"Mini UI Window minimized at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def restore_window(self):
        """Restore the window from minimized state"""
        print(f"Restoring mini UI window at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        # Deiconify the window
        self.deiconify()
        # Make sure it's visible and on top
        self.lift()
        self.attributes("-topmost", True)
        self.update()
        # Allow other windows to go in front after we've restored
        self.after(100, lambda: self.attributes("-topmost", False))

    def update_ui_for_connection(self):
        """Update UI elements for connected state"""
        # Set connection state
        self.is_connected = True
        
        # Hide connect button
        if hasattr(self, 'connect_button'):
            try:
                print("Hiding connect button")
                self.connect_button.grid_remove()
                print("Connect button hidden successfully")
            except Exception as e:
                print(f"Error hiding connect button: {str(e)}")
            
        # Update status message with connection success
        self.update_status("Connected successfully")
        
        # Move status label up to row 1 after button is hidden
        if hasattr(self, 'status_label'):
            self.status_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="n")
            # Also move progress bar up if it's visible
            if hasattr(self, 'progress_bar') and self.progress_bar.winfo_ismapped():
                self.progress_bar.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="s") 
        
        # Show a checkmark or success indicator in the status
        # This could be enhanced further with a green status indicator
        self.status_label.configure(text_color=("#2CC985", "#2FA572"))  # Green text color
        
        # Make sure status label is visible
        try:
            print("Ensuring status label is visible")
            print("Status label placement confirmed")
        except Exception as e:
            print(f"Error with status label: {str(e)}")
        
        # Log the connection
        self.log("Connection established")
        
        # Update system tray tooltip if active
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.title = "Simulanis Login (Connected)"
            except Exception as e:
                print(f"Error updating tray title: {str(e)}")
                
    def update_ui_for_disconnection(self):
        """Update UI elements for disconnected state"""
        # Set connection state
        self.is_connected = False
        
        # Show connect button
        if hasattr(self, 'connect_button'):
            try:
                print("Showing connect button")
                # First configure the button
                self.connect_button.configure(state="normal", image=self.icons.get("connect"))
                # Add it to the main grid - row 1 for the updated layout
                self.connect_button.grid(row=1, column=0, padx=5, pady=(0, 0), sticky="")
                print("Connect button added to grid")
                
                # Move status label back to its original position
                if hasattr(self, 'status_label'):
                    self.status_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky="n")
                    # Also move progress bar back if it's visible
                    if hasattr(self, 'progress_bar') and self.progress_bar.winfo_ismapped():
                        self.progress_bar.grid(row=2, column=0, padx=10, pady=(35, 5), sticky="s")
            except Exception as e:
                print(f"Error showing connect button: {str(e)}")
                
        # Reset status message color
        self.status_label.configure(text_color=("gray70", "gray30"))
        
        # Update status
        self.update_status("Ready to connect")
        
        # Update system tray tooltip if active
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.title = "Simulanis Login"
            except:
                pass  # Some platforms might not support changing the tooltip

    def perform_login(self, username=None, password=None):
        """Perform login using the login manager"""
        # Hide connect button immediately if it exists
        if hasattr(self, 'connect_button') and self.connect_button.winfo_ismapped():
            self.connect_button.grid_remove()
        
        # Ensure status label shows connecting message
        self.update_status("Connecting...", 10)
            
        # Perform the login through the manager
        result = self.login_mgr.perform_login(username, password, self.headless_mode_var.get())
        
        if result['success']:
            # Success - update UI for connection
            self.update_ui_for_connection()
            
            # Show success message
            if result.get('already_logged_in', False):
                self.update_status("Already logged in", None)
            else:
                self.update_status("Connected successfully", None)
            
            # Minimize to tray after successful login with a delay
            self.after(1500, self.quit_app)
        else:
            # Failed - update UI for disconnection
            self.update_ui_for_disconnection()
            
            # Show error message
            if result.get('message'):
                self.update_status(f"Connection failed: {result['message']}", None)
            else:
                self.update_status("Connection failed", None)
            
        return result

    def open_full_gui(self, needs_credentials=False):
        """Open the full Auto Login GUI as a separate process"""
        try:
            self.log("Opening full Auto Login GUI...")
            
            # Determine the path to auto_login_gui.py
            # If running from frozen executable, use executable directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
                gui_path = os.path.join(app_dir, "auto_login_gui.py")
            else:
                # Otherwise use the current directory
                gui_path = os.path.join(os.path.dirname(__file__), "auto_login_gui.py")
            
            # Check if the file exists
            if not os.path.exists(gui_path):
                self.log(f"Error: Could not find {gui_path}")
                self.update_status("Error opening settings")
                return
                
            # Prepare command-line arguments
            args = [gui_path, "--from-mini"]
            
            # Add flag to indicate credentials are needed
            if needs_credentials:
                args.append("--needs-credentials")
            
            # Start the process with appropriate flags
            if sys.platform == 'win32':
                # On Windows, use pythonw to avoid console window
                python_exe = sys.executable
                subprocess.Popen([python_exe] + args)
            else:
                # On other platforms, just use normal Python
                subprocess.Popen([sys.executable] + args)
            
            # Update status
            self.update_status("Opened settings window")
            
            # Store our window handle in a file so the auto_login can find us directly
            if sys.platform == 'win32':
                try:
                    import ctypes
                    # Store our window handle in a temporary file
                    window_handle = self.winfo_id()
                    with open("mini_ui_handle.txt", "w") as f:
                        f.write(str(window_handle))
                    print(f"Saved window handle {window_handle} to mini_ui_handle.txt")
                except Exception as e:
                    print(f"Could not save window handle: {str(e)}")
            
            # Just hide the window without trying to iconify it
            print("Hiding mini UI before opening full UI")
            self.withdraw()
                
        except Exception as e:
            self.log(f"Error opening full GUI: {str(e)}")
            self.update_status("Error opening settings")
            
    def cleanup_resources(self):
        """Clean up resources when closing the application"""
        try:
            # Stop and remove the tray icon if it exists
            if hasattr(self, 'tray_icon') and self.tray_icon is not None:
                self.tray_icon.stop()
                self.tray_icon = None
                self.log("Tray icon stopped")
            
            # Remove any window handle files
            if os.path.exists("mini_ui_handle.txt"):
                os.remove("mini_ui_handle.txt")
                self.log("Removed window handle file")
        except Exception as e:
            self.log(f"Error during cleanup: {str(e)}")
    
    def destroy(self):
        """Override destroy to ensure proper cleanup"""
        self.cleanup_resources()
        super().destroy()
        
    def show_settings_menu(self):
        """Placeholder for showing a settings menu or dialog"""
        # This has been replaced by open_full_gui
        self.open_full_gui()

    def quit_app(self):
        """Hide to tray instead of closing"""
        self.log("Minimizing to tray")
        
        # Create and start tray icon if it doesn't exist yet
        if not hasattr(self, 'tray_icon') or self.tray_icon is None:
            self.create_tray_icon()
            
        # Hide the window
        self.withdraw()
        
    def create_tray_icon(self):
        """Create a system tray icon with menu"""
        try:
            # Try to load icon for tray
            icon_path = os.path.join("Icons", "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join("Logos", "Icon-blue-transparent.png")
                
            if not os.path.exists(icon_path):
                # Create a simple blue dot icon if we can't find one
                icon_image = Image.new('RGB', (64, 64), color = (0, 120, 212))
            else:
                icon_image = Image.open(icon_path)
            
            # Define menu items and actions
            menu = (
                pystray.MenuItem('Show', self.on_tray_show),
                pystray.MenuItem('Exit', self.on_tray_exit)
            )
            
            # Create the icon
            self.tray_icon = pystray.Icon("SimulanisLogin", icon_image, "Simulanis Login", menu)
            
            # Run the icon in a separate thread to keep the main thread free for Tkinter
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
            self.log("System tray icon created")
        except Exception as e:
            self.log(f"Error creating tray icon: {str(e)}")
            # Fallback to just minimizing
            self.iconify()
    
    def on_tray_show(self, icon, item):
        """Show the window from tray"""
        self.log("Showing window from tray")
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.update()
        self.after(100, lambda: self.attributes("-topmost", False))
        
    def on_tray_exit(self, icon, item):
        """Exit the application from tray"""
        self.log("Exiting from tray")
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.stop()
            self.tray_icon = None
        # Actually destroy the window and exit
        self.destroy()

    def restore_from_auto_login(self):
        """Show the mini UI when the auto login UI is closed"""
        print(f"restore_from_auto_login called at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check window state
        if not self.winfo_viewable():
            try:
                # If window is withdrawn (not just iconified), we need to deiconify
                print("Window is not viewable - deiconifying")
                self.deiconify()
            except Exception as e:
                print(f"Error during deiconify: {str(e)}")
        
        # Make sure we're visible
        try:
            # Make sure we're on top
            self.lift()
            self.attributes("-topmost", True)
            self.update()
            # Update our status message
            self.update_status("Settings closed")
            # Allow other windows to go in front after being restored
            self.after(1000, lambda: self.attributes("-topmost", False))
        except Exception as e:
            print(f"Error during window restoration: {str(e)}")
            # Try again after a short delay if there was an error
            self.after(100, self.restore_from_auto_login)
        
    @staticmethod
    def restore_any_mini_ui():
        """Static method that can be called to restore any mini UI window"""
        import sys
        import subprocess
        
        try:
            if sys.platform == 'win32':
                # Important: For PowerShell here-strings, the closing "@ must be at the start of a line
                # with no whitespace before it or we'll get syntax errors
                command = '''
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WindowHelper {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

$windows = Get-Process | Where-Object {$_.MainWindowTitle -like "*Simulanis Mini Login*"}
Write-Output "Found $($windows.Count) mini UI windows"
foreach ($window in $windows) {
    $hwnd = $window.MainWindowHandle
    if ($hwnd -ne 0) {
        Write-Output "Restoring window with handle $hwnd"
        [WindowHelper]::ShowWindow($hwnd, 9) # 9 = SW_RESTORE
        [WindowHelper]::SetForegroundWindow($hwnd)
    }
}
'''
                try:
                    # Run with hidden window
                    startupinfo = None
                    if hasattr(subprocess, 'STARTUPINFO'):
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    # Run the command with output capturing to check for errors
                    proc = subprocess.Popen(['powershell', '-Command', command], 
                                          creationflags=subprocess.CREATE_NO_WINDOW,
                                          startupinfo=startupinfo,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
                    
                    # Log output for debugging
                    stdout, stderr = proc.communicate(timeout=2)
                    if stdout:
                        print(f"PowerShell output: {stdout}")
                    if stderr:
                        print(f"PowerShell error: {stderr}")
                        
                    return True
                except Exception as inner_e:
                    print(f"PowerShell execution error: {str(inner_e)}")
                    return False
            else:
                # For Linux/Mac, try to use wmctrl if available
                try:
                    subprocess.Popen(['wmctrl', '-a', 'Simulanis Mini Login'])
                    return True
                except:
                    return False
        except Exception as e:
            print(f"Error in restore_any_mini_ui: {str(e)}")
            return False

    def apply_modern_window_style(self):
        """Apply modern Windows 11 style with rounded corners and shadow"""
        if sys.platform != 'win32':
            return
            
        try:
            # For Windows 11 (and some Windows 10 with updates)
            # DwmSetWindowAttribute documentation: 
            # https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmsetwindowattribute
            hwnd = self.winfo_id()
            
            # Define necessary constants
            DWMWA_WINDOW_CORNER_PREFERENCE = 33 # Window corner preference
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Dark mode
            DWMWA_SYSTEMBACKDROP_TYPE = 38      # Backdrop/material type
            
            # Corner preferences
            DWM_WINDOW_CORNER_PREFERENCE_DEFAULT = 0
            DWM_WINDOW_CORNER_PREFERENCE_DONOTROUND = 1
            DWM_WINDOW_CORNER_PREFERENCE_ROUND = 2
            DWM_WINDOW_CORNER_PREFERENCE_ROUNDSMALL = 3
            
            # System backdrop types
            DWM_SYSTEMBACKDROP_TYPE_AUTO = 0
            DWM_SYSTEMBACKDROP_TYPE_NONE = 1
            DWM_SYSTEMBACKDROP_TYPE_MAINWINDOW = 2
            DWM_SYSTEMBACKDROP_TYPE_TRANSIENT = 3
            DWM_SYSTEMBACKDROP_TYPE_TABBEDWINDOW = 4
            
            # Load dwmapi.dll
            dwmapi = ctypes.WinDLL("dwmapi")
            
            # Apply rounded corners (small radius)
            corner_pref = ctypes.c_int(DWM_WINDOW_CORNER_PREFERENCE_ROUNDSMALL)
            dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_WINDOW_CORNER_PREFERENCE, 
                ctypes.byref(corner_pref), 
                ctypes.sizeof(corner_pref)
            )
            
            # Try to apply backdrop effect (like Mica/Acrylic)
            # This might not work on all systems, so we'll handle exceptions
            try:
                # Use the modern backdrop that works with dark mode
                backdrop_type = ctypes.c_int(DWM_SYSTEMBACKDROP_TYPE_MAINWINDOW)
                dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_SYSTEMBACKDROP_TYPE, 
                    ctypes.byref(backdrop_type), 
                    ctypes.sizeof(backdrop_type)
                )
            except Exception as e:
                # If we can't set the backdrop, that's ok - just log it
                print(f"Note: Could not set window backdrop: {str(e)}")
                
            print("Applied modern window styling")
        except Exception as e:
            print(f"Warning: Could not apply modern window style: {str(e)}")
            
            # Try an alternative method if the main method fails
            try:
                # Alternative approach
                from ctypes import windll
                hwnd = windll.user32.GetParent(self.winfo_id())
                style = windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
                style = style & ~0x00C00000  # WS_CAPTION
                style = style & ~0x00080000  # WS_BORDER
                windll.user32.SetWindowLongW(hwnd, -16, style)  # GWL_STYLE
                print("Applied alternative window styling")
            except Exception as alt_e:
                print(f"Could not apply alternative styling: {str(alt_e)}")
                # Fails silently if this doesn't work either

# --- Main Execution ---
if __name__ == "__main__":
    # Check for headless mode argument
    headless_mode = '--headless' in sys.argv
    
    app = MiniLoginApp(headless=headless_mode)
    if not headless_mode:
        app.mainloop()
    # Headless mode already calls perform_login in init
 