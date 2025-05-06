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
import tkinter.messagebox as messagebox
import threading
import pystray
import ctypes

# Import the login core
from login_core import LoginManager

# The main application class that handles UI switching
class SimulanisLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Application constants
        self.APP_NAME = "Simulanis Login"
        self.KEYRING_SERVICE = "SimulanisLogin"
        self.TARGET_URL = "https://192.168.1.9/userlogin/"
        
        # Initialize tray icon variable
        self.tray_icon = None
        
        # Initialize variables
        self.remember_me_var = tk.BooleanVar(value=False)
        self.auto_login_var = tk.BooleanVar(value=False)
        self.headless_mode_var = tk.BooleanVar(value=True)  # Default to headless
        
        # Track connection state
        self.is_connected = False
        
        # Setup for UI mode
        self.mode = self.get_initial_mode()
        self.is_mini = (self.mode == "mini")
        
        # Set window title
        self.title(self.APP_NAME + (" Mini" if self.is_mini else ""))
        
        # Set the color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Determine config directory (for both regular and packaged app)
        self.config_dir = str(Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent)
        self.log(f"Using config directory: {self.config_dir}")
        
        # Create the login manager with status callback and config directory
        self.login_mgr = LoginManager(ui_callback=self.update_status, config_dir=self.config_dir)
        
        # Load saved configuration and update variables
        self.load_config()
        
        # Check command line arguments
        self.process_command_line_args()
        
        # Setup the appropriate UI
        self.setup_ui()
        
        # Add close button
        self.add_close_button()
        
        # Position the window based on mode
        if self.is_mini:
            self.position_window_top_right()
        else:
            self.center_window()
        
        # Make window draggable
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        
        # Set close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Check for auto-login if needed
        self.handle_auto_login()
    
    def get_initial_mode(self):
        """Determine the initial UI mode based on command line arguments"""
        if "--mini" in sys.argv:
            return "mini"
        elif "--full" in sys.argv:
            return "full"
        else:
            # Default to mini if no mode specified
            return "mini"
    
    def process_command_line_args(self):
        """Process command line arguments"""
        # Check for headless flag
        if "--headless" in sys.argv:
            self.perform_headless_login()
            sys.exit(0)
        
        # Check if credentials are needed flag
        self.needs_credentials = "--needs-credentials" in sys.argv
    
    def setup_ui(self):
        """Setup the appropriate UI based on the mode"""
        # First, clear any existing UI elements
        for widget in self.winfo_children():
            widget.destroy()
        
        # Configure window properties based on UI mode
        if self.is_mini:
            # Mini UI settings
            self.MINI_WIDTH = 280
            self.MINI_HEIGHT = 150
            self.geometry(f"{self.MINI_WIDTH}x{self.MINI_HEIGHT}")
            self.minsize(self.MINI_WIDTH, self.MINI_HEIGHT)
            self.maxsize(self.MINI_WIDTH, self.MINI_HEIGHT)
            self.overrideredirect(True)  # Remove default titlebar
            self.attributes("-topmost", True)  # Keep on top
            
            # Apply modern window style for Windows
            if sys.platform == 'win32':
                self.apply_modern_window_style()
                
            # Load mini UI assets
            self.load_mini_icons()
            
            # Setup mini UI components
            self.setup_mini_gui()
        else:
            # Full UI settings
            self.geometry("800x400")  # Wider layout
            self.minsize(800, 400)    # Set minimum window size
            self.overrideredirect(True)  # Remove default titlebar
            
            # Load full UI assets
            self.load_branding()
            self.load_icons()
            
            # Setup full UI components
            self.setup_full_gui()

    def switch_ui_mode(self):
        """Switch between mini and full UI modes"""
        # Toggle the mode
        self.is_mini = not self.is_mini
        
        # Update window title
        self.title(self.APP_NAME + (" Mini" if self.is_mini else ""))
        
        # Setup the new UI
        self.setup_ui()
        
        # Add close button again (since we destroyed all widgets)
        self.add_close_button()
        
        # Reposition the window
        if self.is_mini:
            self.position_window_top_right()
        else:
            self.center_window()
    
    def update_status(self, message, progress=None):
        """Update status message and progress bar"""
        # Log the message
        self.log(message)
        
        # Update UI elements based on the current mode
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
            
            # Update progress bar if it exists and progress is provided
            if progress is not None and hasattr(self, 'progress_bar'):
                if progress > 0:
                    # Show progress bar with correct value
                    if self.is_mini:
                        # For mini UI
                        if self.connect_button.winfo_ismapped():
                            self.progress_bar.grid(row=2, column=0, padx=10, pady=(35, 5), sticky="s")
                        else:
                            self.progress_bar.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="s")
                    else:
                        # For full UI
                        self.progress_bar.grid()
                        
                    self.progress_bar.set(progress / 100)
                else:
                    # Hide progress bar
                    self.progress_bar.grid_remove()
            elif hasattr(self, 'progress_bar'):
                # Hide progress bar when no progress is specified
                self.progress_bar.grid_remove()
            
            # Update the UI
            self.update()
    
    def log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def position_window_top_right(self):
        """Position the window in the top right corner of the screen"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        window_width = self.winfo_width()
        x = screen_width - window_width - 10  # 10px padding
        y = 10  # 10px padding from top
        self.geometry(f"+{x}+{y}")
    
    def add_close_button(self):
        """Add a close button to the window"""
        if self.is_mini:
            # Mini UI close button
            close_btn = ctk.CTkButton(
                self, 
                text="✕",  # Simple X symbol
                command=self.on_close, 
                width=20, 
                height=20,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                hover_color="#FF4444",
                corner_radius=0 
            )
            close_btn.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")
            
            # Reposition settings button if it exists to avoid overlap
            if hasattr(self, 'settings_button'):
                self.settings_button.place(relx=1.0, rely=0.0, x=-30, y=5, anchor="ne")
        else:
            # Full UI minimize button (renamed from close button)
            self.close_button = ctk.CTkButton(
                self,
                text="-",  # Down arrow symbol to indicate minimize/collapse
                width=40,
                height=40,
                command=self.on_close,
                font=ctk.CTkFont(size=20, weight="bold"),
                fg_color="transparent",
                hover_color="#3388FF",  # Blue hover color to indicate non-destructive action
                corner_radius=0
            )
            self.close_button.place(x=self.winfo_width() - 40, y=0)
            
            # Update close button position when window is resized
            self.bind("<Configure>", lambda e: self.close_button.place(x=self.winfo_width() - 40, y=0))
    
    # Window dragging functions
    def start_move(self, event):
        """Begin window drag"""
        # Determine draggable areas based on UI mode
        if not self.is_mini:
            # In full mode, allow dragging from any part
            self._drag_start_x = event.x
            self._drag_start_y = event.y

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
            self.geometry(f"+{new_x}+{new_y}")
    
    def on_close(self):
        """Handle window close event"""
        if self.is_mini:
            # Mini UI closes to tray
            self.minimize_to_tray()
        else:
            # When in full UI mode, switch to mini UI instead of closing
            self.save_config()
            self.switch_ui_mode()
    
    def minimize_to_tray(self):
        """Hide to system tray"""
        self.log("Minimizing to tray")
        
        # Create tray icon if it doesn't exist
        if self.tray_icon is None:
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
                icon_image = Image.new('RGB', (64, 64), color=(0, 120, 212))
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
        if self.is_mini:
            self.geometry(f"{self.MINI_WIDTH}x{self.MINI_HEIGHT}")
            self.position_window_top_right()
            self.overrideredirect(True)
            self.attributes("-topmost", True)
        self.lift()
        self.update()
        self.after(100, lambda: self.attributes("-topmost", False))
        
    def on_tray_exit(self, icon, item):
        """Exit the application from tray"""
        self.log("Exiting from tray")
        if self.tray_icon is not None:
            self.tray_icon.stop()
            self.tray_icon = None
        # Actually destroy the window and exit
        self.destroy()
    
    # Common config handling functions
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
                    
                    # Load username
                    self.saved_username = config.get('username', '')
                    
                    # Load settings
                    self.remember_me_var.set(config.get('remember_me', False))
                    self.auto_login_var.set(config.get('auto_login', False))
                    self.headless_mode_var.set(config.get('headless_mode', False))
                    
                    self.log("Loaded config")
            else:
                # Defaults if no config file
                self.saved_username = ""
                self.remember_me_var.set(False)
                self.auto_login_var.set(False)
                self.headless_mode_var.set(True if not self.is_mini else False)
                self.log("No config file found, using defaults.")

        except Exception as e:
            self.log(f"Error loading config: {str(e)}")
            # Reset to defaults on error
            self.saved_username = ""
            self.remember_me_var.set(False)
            self.auto_login_var.set(False)
            self.headless_mode_var.set(True if not self.is_mini else False)
    
    def save_config(self, username=None, password=None):
        """Save configuration to file"""
        try:
            # If username is not provided but we're in full UI mode, get it from the entry
            if username is None and hasattr(self, 'username_entry'):
                username = self.username_entry.get()
            
            # Prepare config data
            config_data = {
                'username': username if username else self.saved_username,
                'remember_me': self.remember_me_var.get(),
                'auto_login': self.auto_login_var.get(),
                'headless_mode': self.headless_mode_var.get()
            }
            
            # Determine config file path
            config_path = os.path.join(self.config_dir, 'config.json')
            self.log(f"Saving config to: {config_path}")
            
            # Save to config file
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            # Save password if remember me is checked and password is provided
            if self.remember_me_var.get() and username and password:
                self.login_mgr.save_credentials(username, password, True)
            
            self.log("Config saved")
        except Exception as e:
            self.log(f"Error saving config: {str(e)}")
    
    def handle_auto_login(self):
        """Handle auto-login based on configuration"""
        # Skip auto-login if credentials are explicitly needed
        if hasattr(self, 'needs_credentials') and self.needs_credentials:
            if not self.is_mini and hasattr(self, 'username_entry'):
                self.username_entry.focus_set()
                self.update_status("Please enter your login credentials", 0)
            return
            
        # Perform auto-login if enabled and we have credentials
        if self.auto_login_var.get():
            username = self.login_mgr.get_saved_username()
            password = self.login_mgr.get_saved_password()
            
            if username and password:
                # Wait a short moment before performing login
                self.after(1000, lambda: self.perform_login(username, password))
            elif self.is_mini:
                # In mini mode, show connect button if no auto-login
                if hasattr(self, 'connect_button'):
                    self.connect_button.grid(row=1, column=0, padx=5, pady=(0, 0), sticky="")
                    self.update_status("Click Connect to log in")
    
    def perform_headless_login(self):
        """Perform login in headless mode"""
        # Create login manager in headless mode
        login_mgr = LoginManager(headless=True)
        # Perform the login
        login_mgr.perform_login()
    
    def perform_login(self, username=None, password=None):
        """Perform the login operation"""
        # Different UI updates based on mode
        if self.is_mini:
            # Hide connect button if it exists
            if hasattr(self, 'connect_button') and self.connect_button.winfo_ismapped():
                self.connect_button.grid_remove()
                
            # Move status label up if needed
            if hasattr(self, 'status_label'):
                self.status_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="n")
                # Also adjust progress bar if it's visible
                if hasattr(self, 'progress_bar') and self.progress_bar.winfo_ismapped():
                    self.progress_bar.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="s")
        else:
            # Full UI updates
            if hasattr(self, 'login_button'):
                self.login_button.configure(state="disabled")
            
            # Start login animation if it exists
            if hasattr(self, 'start_login_animation'):
                self.start_login_animation()
        
        # Show connecting message
        self.update_status("Connecting...", 10)
            
        # Get credentials from UI if not provided
        if username is None and password is None and not self.is_mini:
            if hasattr(self, 'username_entry') and hasattr(self, 'password_entry'):
                username = self.username_entry.get()
                password = self.password_entry.get()
        
        # Perform the login through the manager
        result = self.login_mgr.perform_login(username, password, self.headless_mode_var.get())
        
        if result['success']:
            # Success - update UI for connection
            self.is_connected = True
            
            # Save config if credentials were provided and remember me is checked
            if username is not None and self.remember_me_var.get():
                self.save_config(username, password)
            
            # Update UI based on current mode
            if self.is_mini:
                # Mini UI updates for connection
                if hasattr(self, 'status_label'):
                    self.status_label.configure(text_color=("#2CC985", "#2FA572"))  # Green text color
                
                # Show success message
                if result.get('already_logged_in', False):
                    self.update_status("Already logged in", None)
                else:
                    self.update_status("Connected successfully", None)
                
                # Minimize to tray after successful login with a delay
                self.after(1500, self.minimize_to_tray)
            else:
                # Full UI updates
                if hasattr(self, 'status_label'):
                    self.update_status("Successfully logged in!", 100)
                
                # Minimize window
                self.iconify()
        else:
            # Failed - update UI for disconnection
            self.is_connected = False
            
            # Update UI based on current mode
            if self.is_mini:
                # Mini UI updates for disconnection
                self.update_ui_for_disconnection()
            else:
                # Full UI updates
                if hasattr(self, 'login_button'):
                    self.login_button.configure(state="normal")
                
                # Stop animation if it exists
                if hasattr(self, 'stop_login_animation'):
                    self.stop_login_animation()
            
            # Show error message
            if result.get('message'):
                self.update_status(f"Connection failed: {result['message']}", None)
            else:
                self.update_status("Connection failed", None)
        
        return result
    
    def apply_modern_window_style(self):
        """Apply modern Windows 11 style with rounded corners and shadow"""
        if sys.platform != 'win32':
            return
            
        try:
            # For Windows 11 (and some Windows 10 with updates)
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

    def load_mini_icons(self):
        """Load icons for the mini UI"""
        try:
            # Load icons from the Icons directory
            icons_dir = Path("Icons")
            if not icons_dir.exists():
                try: 
                    icons_dir.mkdir()
                except OSError:
                    print("Warning: Icons directory not found and could not be created.")
                
            # Define icon paths for mini UI
            self.icons = {
                "connect": self.load_mini_icon("connect.png", (35, 35)),
                "disconnect": self.load_mini_icon("disconnect.png", (20, 20)),
                "settings": self.load_mini_icon("settings.png", (20, 20)),
                "close": self.load_mini_icon("close.png", (15, 15))
            }
            
            # Check if any icons failed to load
            for key in self.icons:
                if self.icons[key] is None:
                    print(f"Info: Using text fallback for missing icon: {key}")
        except Exception as e:
            print(f"Error loading mini icons: {str(e)}")
            self.icons = {}
    
    def load_mini_icon(self, icon_name, size):
        """Load and resize an icon for mini UI"""
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
        # Reset grid configuration to a single column for mini UI
        for i in range(5):  # Adjust range if you ever use more columns
            self.grid_columnconfigure(i, weight=0, minsize=0)
        for i in range(5):  # Adjust range if you ever use more rows
            self.grid_rowconfigure(i, weight=0, minsize=0)
        self.grid_columnconfigure(0, weight=1)

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
            wraplength=self.MINI_WIDTH - 40, # Wrap text
            height=30 # Ensure there's enough height
        )
        self.status_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky="n")
        
        # Settings/Options Button - place in top-right corner
        self.settings_button = ctk.CTkButton(
            self,
            text="" if self.icons.get("settings") else "⚙", # Use gear emoji if icon not available
            image=self.icons.get("settings"),
            command=self.switch_ui_mode, # Switch to full UI
            width=25, 
            height=25,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
        )
        self.settings_button.place(relx=1.0, rely=0.0, x=-30, y=8, anchor="ne") # Position in top-right
        
        # Progress bar - place in third row below status label
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=self.MINI_WIDTH-20,
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
        """Check for credentials and either switch to full UI or perform login directly"""
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
            # No credentials available, switch to full UI for login
            self.update_status("Opening settings for login...")
            self.switch_ui_mode()
            
            # Set needs_credentials flag for the full UI
            self.needs_credentials = True
            
            # Update status in full UI
            self.after(100, lambda: self.update_status("Please enter your login credentials"))
            
            # Focus on username field if available
            if hasattr(self, 'username_entry'):
                self.username_entry.focus_set()
    
    def update_ui_for_disconnection(self):
        """Update mini UI elements for disconnected state"""
        # Only applicable for mini UI mode
        if not self.is_mini:
            return
            
        # Set connection state
        self.is_connected = False
        
        # Show connect button
        if hasattr(self, 'connect_button'):
            try:
                # First configure the button
                self.connect_button.configure(state="normal", image=self.icons.get("connect"))
                # Add it to the main grid - row 1 for the updated layout
                self.connect_button.grid(row=1, column=0, padx=5, pady=(0, 0), sticky="")
                
                # Move status label back to its original position
                if hasattr(self, 'status_label'):
                    self.status_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky="n")
                    # Also move progress bar back if it's visible
                    if hasattr(self, 'progress_bar') and self.progress_bar.winfo_ismapped():
                        self.progress_bar.grid(row=2, column=0, padx=10, pady=(35, 5), sticky="s")
            except Exception as e:
                print(f"Error showing connect button: {str(e)}")
                
        # Reset status message color
        if hasattr(self, 'status_label'):
            self.status_label.configure(text_color=("gray70", "gray30"))
        
        # Update status
        self.update_status("Ready to connect")
        
        # Update system tray tooltip if active
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.title = "Simulanis Login"
            except:
                pass  # Some platforms might not support changing the tooltip

    def load_branding(self):
        """Load branding assets for full UI"""
        try:
            # Load and resize logo
            logo_path = os.path.join("Logos", "Logo.png")
            if os.path.exists(logo_path):
                # Load image and get original dimensions
                original_image = Image.open(logo_path)
                width, height = original_image.size
                
                # Calculate aspect ratio
                aspect_ratio = width / height
                
                # Set target width and calculate height to maintain aspect ratio
                target_width = 300
                target_height = int(target_width / aspect_ratio)
                
                self.logo_image = ctk.CTkImage(
                    light_image=original_image,
                    dark_image=original_image,
                    size=(target_width, target_height)
                )
            else:
                self.logo_image = None

            # Set window icon
            icon_path = os.path.join("Logos", "Icon-blue-transparent.png")
            if os.path.exists(icon_path):
                self.iconphoto(True, ImageTk.PhotoImage(Image.open(icon_path)))
        except Exception as e:
            print(f"Error loading branding assets: {str(e)}")
            self.logo_image = None
    
    def load_icons(self):
        """Load icons for the full UI"""
        try:
            # Load icons from the Icons directory
            icons_dir = Path("Icons")
            if not icons_dir.exists():
                icons_dir.mkdir()
                
            # Define icon paths for full UI
            self.icons = {
                "profile": self.load_icon("profile.png", (20, 20)),
                "eye": self.load_icon("eye.png", (20, 20)),
                "eye_off": self.load_icon("eye_off.png", (20, 20)),
                "close": self.load_icon("close.png", (15, 15))
            }
        except Exception as e:
            print(f"Error loading full UI icons: {str(e)}")
            self.icons = {}
    
    def load_icon(self, icon_name, size):
        """Load and resize an icon for full UI"""
        try:
            icon_path = os.path.join("Icons", icon_name)
            if os.path.exists(icon_path):
                return ctk.CTkImage(
                    light_image=Image.open(icon_path),
                    dark_image=Image.open(icon_path),
                    size=size
                )
        except Exception as e:
            print(f"Error loading icon {icon_name}: {str(e)}")
        return None
    
    def setup_full_gui(self):
        """Setup the full UI elements"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Two-column layout
        
        # Left panel (Logo and status)
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Center frame for logo and status
        self.center_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.center_frame.grid(row=0, column=0, sticky="n")
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        # Logo
        if hasattr(self, 'logo_image') and self.logo_image:
            self.logo_label = ctk.CTkLabel(
                self.center_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo_label = ctk.CTkLabel(
                self.center_frame,
                text="Simulanis Solutions",
                font=ctk.CTkFont(size=24, weight="bold")
            )
        self.logo_label.grid(row=0, column=0, pady=(20, 10))
        
        # Status frame below logo
        self.status_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=0, sticky="ew", pady=(150, 0))
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to connect",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray70")
        )
        self.status_label.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            width=250,
            height=8,
            corner_radius=4,
            fg_color=("gray85", "gray20"),
            progress_color=("#2CC985", "#2FA572")
        )
        self.progress_bar.grid(row=1, column=0)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Initially hidden
        
        # Footer
        self.footer_label = ctk.CTkLabel(
            self.left_panel,
            text="© Simulanis Solutions Pvt. Ltd.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray70")
        )
        self.footer_label.grid(row=1, column=0, pady=(10, 0))
        
        # Right panel (Login)
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Login frame with rounded corners and subtle shadow
        self.login_frame = ctk.CTkFrame(
            self.right_panel,
            corner_radius=15,
            fg_color=("white", "gray20")
        )
        self.login_frame.grid(row=0, column=0, sticky="n", pady=20)
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        # Small space
        spacer = ctk.CTkFrame(
            self.login_frame,
            fg_color="transparent",
            height=10
        )
        spacer.grid(row=0, column=0)
        
        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Username",
            width=300,
            height=40,
            corner_radius=8
        )
        self.username_entry.grid(row=1, column=0, pady=(20, 10), padx=20)
        
        # Fill in saved username if available
        if hasattr(self, 'saved_username') and self.saved_username:
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, self.saved_username)
        
        # Password entry with show/hide button
        password_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        password_frame.grid(row=2, column=0, sticky="ew", padx=20)
        password_frame.grid_columnconfigure(0, weight=1)
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Password",
            show="•",
            width=250,
            height=40,
            corner_radius=8
        )
        self.password_entry.grid(row=0, column=0, sticky="ew")
        
        # Fill in saved password if available
        if self.remember_me_var.get() and hasattr(self, 'saved_username') and self.saved_username:
            saved_password = self.login_mgr.get_saved_password()
            if saved_password:
                self.password_entry.delete(0, 'end')
                self.password_entry.insert(0, saved_password)
        
        self.toggle_password_btn = ctk.CTkButton(
            password_frame,
            text="",
            image=self.icons.get("eye_off"),
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
            command=self.toggle_password_visibility
        )
        self.toggle_password_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        checkbox_frame.grid(row=3, column=0, pady=20, padx=20, sticky="w")
        
        self.remember_me_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Remember me",
            variable=self.remember_me_var,
            font=ctk.CTkFont(size=12),
            corner_radius=6
        )
        self.remember_me_checkbox.grid(row=0, column=0, pady=5, sticky="w")
        
        self.auto_login_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Auto-login on startup",
            variable=self.auto_login_var,
            font=ctk.CTkFont(size=12),
            corner_radius=6
        )
        self.auto_login_checkbox.grid(row=1, column=0, pady=5, sticky="w")
        
        self.headless_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Headless mode",
            variable=self.headless_mode_var,
            font=ctk.CTkFont(size=12),
            corner_radius=6
        )
        self.headless_checkbox.grid(row=2, column=0, pady=5, sticky="w")
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Connect Now",
            command=self.perform_login,
            width=300,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.grid(row=4, column=0, pady=20, padx=20)
        
        # Bind Enter key to login
        self.bind('<Return>', lambda e: self.perform_login())
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(image=self.icons.get("eye_off"))
        else:
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(image=self.icons.get("eye"))
            
    def start_login_animation(self):
        """Start the login animation sequence for full UI"""
        self.right_panel.grid_remove()  # Hide right panel
        
        # Reconfigure grid to center the left panel
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def stop_login_animation(self):
        """Stop the login animation sequence for full UI"""
        # Restore grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Show right panel without changing status
        self.right_panel.grid()

# Main execution
if __name__ == "__main__":
    # Check for headless mode
    if "--headless" in sys.argv:
        # Just create login manager in headless mode and perform login
        login_mgr = LoginManager(headless=True)
        login_mgr.perform_login()
    else:
        # Create the main application
        app = SimulanisLoginApp()
        app.mainloop() 