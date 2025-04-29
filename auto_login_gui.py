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

class ModernLoginApp(ctk.CTk):
    def __init__(self, headless=False):
        if not headless:
            super().__init__()
            
            # Application constants
            self.APP_NAME = "Simulanis Login"
            self.KEYRING_SERVICE = "SimulanisLogin"
            self.TARGET_URL = "https://192.168.1.9/userlogin/"
            
            # Animation states
            self.is_animating = False
            self.pulse_animation_id = None
            self.animation_time = 0
            self.ANIMATION_SPEED = 0.1  # Controls the speed of the pulse
            self.SCALE_RANGE = 0.05     # Controls the amount of scaling (±5%)
            
            # Initialize variables
            self.remember_me_var = tk.BooleanVar(value=False)
            self.auto_login_var = tk.BooleanVar(value=False)
            self.headless_mode_var = tk.BooleanVar(value=True)  # Default to headless
            
            # Configure the window
            self.title(self.APP_NAME)
            self.geometry("800x400")  # Wider layout
            self.minsize(800, 400)    # Set minimum window size
            self.overrideredirect(True)  # Remove default titlebar
            
            # Set the color theme
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Load icons
            self.load_icons()
            
            # Load branding assets
            self.load_branding()
            
            # Initialize UI
            self.setup_gui()
            
            # Add close button
            self.add_close_button()
            
            # Center the window
            self.center_window()
            
            # Make window draggable
            self.bind("<Button-1>", self.start_move)
            self.bind("<ButtonRelease-1>", self.stop_move)
            self.bind("<B1-Motion>", self.do_move)
            
            # Load saved configuration
            self.load_config()
            
            # Check for auto-login
            if self.auto_login_var.get() and self.get_saved_username() and self.get_saved_password():
                self.after(1000, self.perform_login)
        else:
            self.APP_NAME = "Simulanis Login"
            self.KEYRING_SERVICE = "SimulanisLogin"
            self.headless = True
            self.load_headless_config()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()  # Update "requested size" from geometry manager
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_branding(self):
        """Load branding assets"""
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
        """Load icons for the application"""
        try:
            # Load icons from the Icons directory
            icons_dir = Path("Icons")
            if not icons_dir.exists():
                icons_dir.mkdir()
                
            # Define icon paths
            self.icons = {
                "profile": self.load_icon("profile.png", (20, 20)),
                "eye": self.load_icon("eye.png", (20, 20)),
                "eye_off": self.load_icon("eye_off.png", (20, 20)),
                "close": self.load_icon("close.png", (15, 15))
            }
        except Exception as e:
            print(f"Error loading icons: {str(e)}")
            self.icons = {}
            
    def load_icon(self, icon_name, size):
        """Load and resize an icon"""
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

    def setup_gui(self):
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
        if self.logo_image:
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
        
        # Progress bar (initially hidden)
        self.progress_bar.grid_remove()
        
        # Status message (initially showing ready state)
        self.status_label.configure(text="Ready to connect")
        
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

    def update_status(self, message, progress=None):
        """Update status message and progress bar"""
        # Always log the status message
        self.log(message)
        
        # Only update GUI elements if not in headless mode
        if not hasattr(self, 'headless') or not self.headless:
            self.status_label.configure(text=message)
            
            if progress is not None:
                if progress > 0:
                    self.progress_bar.grid()  # Show progress bar
                    self.progress_bar.set(progress / 100)
                else:
                    self.progress_bar.grid_remove()  # Hide progress bar
            else:
                self.progress_bar.grid_remove()  # Hide progress bar when no progress specified
            
            self.update()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(image=self.icons.get("eye_off"))
        else:
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(image=self.icons.get("eye"))

    def on_splash_complete(self, success):
        """Called when splash screen completes"""
        if success:
            self.splash.destroy()
            self.deiconify()
            
            # Check for auto-login
            if self.auto_login_var.get() and self.get_saved_username() and self.get_saved_password():
                self.after(1000, self.perform_login)
        else:
            self.splash.destroy()
            self.destroy()

    def load_headless_config(self):
        """Load headless mode configuration"""
        try:
            config_path = os.path.join(os.path.dirname(sys.executable), 'headless_config.json')
            if not os.path.exists(config_path):
                config_path = 'headless_config.json'
            
            with open(config_path, 'r') as f:
                self.headless_config = json.load(f)
        except Exception as e:
            print(f"Error loading headless config: {str(e)}")
            self.headless_config = {
                "chrome_options": ["--headless", "--disable-gpu"],
                "auto_login": True,
                "retry_interval": 60,
                "max_retries": 3
            }

    def console_log(self, message):
        """Log message to console in headless mode"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def log(self, message):
        """Add a message to the log text area or console"""
        if hasattr(self, 'headless') and self.headless:
            self.console_log(message)
        else:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {message}")

    def start_login_animation(self):
        """Start the login animation sequence"""
        self.right_panel.grid_remove()  # Hide right panel
        
        # Reconfigure grid to center the left panel
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def stop_login_animation(self):
        """Stop the login animation sequence"""
        # Restore grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Show right panel without changing status
        self.right_panel.grid()

    def perform_login(self):
        """Perform the login operation"""
        if not hasattr(self, 'headless') or not self.headless:
            self.login_button.configure(state="disabled")
            self.start_login_animation()
            self.update_status(f"Initializing connection to {self.TARGET_URL}...", 10)
        
        try:
            # Configure Chrome options
            chrome_options = Options()
            if self.headless_mode_var.get():  # Use headless mode based on checkbox
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            if hasattr(self, 'headless') and self.headless:
                for option in self.headless_config.get('chrome_options', []):
                    chrome_options.add_argument(option)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            self.update_status("Establishing secure connection...", 30)
            driver.get(self.TARGET_URL)
            
            # Handle security warning
            try:
                self.update_status("Accepting security certificate...", 40)
                advanced_button = driver.find_element(By.ID, "details-button")
                advanced_button.click()
                proceed_link = driver.find_element(By.ID, "proceed-link")
                proceed_link.click()
            except Exception as cert_error:
                # Don't fail if certificate warning doesn't appear
                pass

            # Get username and password
            if hasattr(self, 'headless') and self.headless:
                username = self.get_saved_username()
                password = self.get_saved_password()
            else:
                username = self.username_entry.get()
                password = self.password_entry.get()
                
                if not username or not password:
                    raise ValueError("Username and password are required")

            self.update_status(f"Authenticating user {username}...", 60)
            try:
                wait = WebDriverWait(driver, 10)
                username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
            except Exception as timeout_error:
                raise ConnectionError(f"Could not connect to {self.TARGET_URL}. Please check your network connection.")
                
            username_field.clear()
            username_field.send_keys(username)
            
            try:
                password_field = driver.find_element(By.ID, "passwd")
            except Exception as field_error:
                raise ConnectionError("Login page elements not found. The page structure might have changed.")
                
            password_field.clear()
            password_field.send_keys(password)
            
            self.update_status("Submitting credentials...", 80)
            submit_button = driver.find_element(By.ID, "submitbtn")
            submit_button.click()
            
            # Wait for page load after submission
            time.sleep(2)  # Give time for any redirects to happen
            
            # Check current URL for userSense redirect pattern
            if "192.168.1.9/userSense" in driver.current_url:
                # Wait to see if it redirects back to login
                time.sleep(2)
                if self.TARGET_URL in driver.current_url:
                    raise ValueError("Login failed: Redirected back to login page")
            
            # Check for specific error messages on the page
            try:
                # Look for authentication failure message
                auth_fail_msg = f"Authentication Failed for user:{username}"
                page_source = driver.page_source
                if auth_fail_msg in page_source:
                    raise ValueError("Login failed: Invalid credentials")
                
                # Look for already logged in message
                already_logged_msg = "User is already logged in with same ip"
                if already_logged_msg in page_source:
                    self.update_status("User is already logged in from this IP address")
                    # Save config since credentials are correct
                    if not hasattr(self, 'headless') or not self.headless:
                        self.save_config()
                        if self.remember_me_var.get():
                            self.username_entry.delete(0, 'end')
                            self.username_entry.insert(0, username)
                    return  # Exit without raising error since this is a valid state
                
                # Check for successful login by verifying redirect to simulanis.com
                if "simulanis.com" in driver.current_url:
                    self.update_status("Successfully logged in!", 100)
                    if not hasattr(self, 'headless') or not self.headless:
                        self.save_config()
                        if self.remember_me_var.get():
                            self.username_entry.delete(0, 'end')
                            self.username_entry.insert(0, username)
                else:
                    raise ValueError("Login failed: Please check internet connection and Credentials")
                
            except ValueError as ve:
                raise ve
            except Exception as e:
                # If we can't find any specific messages but we're still on login page
                if self.TARGET_URL in driver.current_url:
                    raise ValueError("Login failed: Still on login page")
                
            time.sleep(2)
            
        except ValueError as ve:
            self.update_status(f"Error: {str(ve)}")
        except ConnectionError as ce:
            self.update_status(f"Connection Error: {str(ce)}")
        except Exception as e:
            self.update_status(f"Connection failed: {str(e)}")
            if hasattr(self, 'headless') and self.headless:
                if self.headless_config.get('auto_login', True):
                    retry_interval = self.headless_config.get('retry_interval', 60)
                    self.log(f"Retrying connection in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    self.perform_login()
        finally:
            if not hasattr(self, 'headless') or not self.headless:
                self.login_button.configure(state="normal")
                self.stop_login_animation()
            try:
                driver.quit()
            except:
                pass  # Ignore errors when closing the driver

    def get_saved_username(self):
        """Get saved username"""
        return getattr(self, 'saved_username', '')

    def get_saved_password(self):
        """Retrieve the saved password from the keyring."""
        try:
            saved_username = self.get_saved_username()
            if saved_username:
                return keyring.get_password(self.KEYRING_SERVICE, saved_username)
            return None
        except Exception as e:
            print(f"Error retrieving password: {str(e)}")
            return None

    def save_credentials(self):
        """Save credentials securely"""
        try:
            username = self.username_entry.get()
            if self.remember_me_var.get() and username:
                keyring.set_password(self.KEYRING_SERVICE, username, self.password_entry.get())
                self.log("Credentials saved securely")
            else:
                # If remember me is unchecked, remove any saved credentials
                try:
                    keyring.delete_password(self.KEYRING_SERVICE, username)
                except:
                    pass
        except Exception as e:
            self.log(f"Error saving credentials: {str(e)}")

    def load_config(self):
        """Load saved configuration from config.json"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if 'username' in config:
                        self.saved_username = config['username']
                        # Set the username in the entry field
                        self.username_entry.delete(0, 'end')
                        self.username_entry.insert(0, self.saved_username)
                        self.log("Loaded saved username")
                        
                        # If remember me is enabled, also load the password
                        if config.get('remember_me', False):
                            saved_password = self.get_saved_password()
                            if saved_password:
                                self.password_entry.delete(0, 'end')
                                self.password_entry.insert(0, saved_password)
                    
                    if 'remember_me' in config:
                        self.remember_me_var.set(config['remember_me'])
                    if 'auto_login' in config:
                        self.auto_login_var.set(config['auto_login'])
                    if 'headless_mode' in config:
                        self.headless_mode_var.set(config['headless_mode'])
            else:
                self.saved_username = ""
                self.remember_me_var.set(False)
                self.auto_login_var.set(False)
                self.headless_mode_var.set(True)  # Default to headless mode
                self.log("No saved configuration found")
        except Exception as e:
            self.log(f"Error loading config: {str(e)}")
            self.saved_username = ""
            self.remember_me_var.set(False)
            self.auto_login_var.set(False)
            self.headless_mode_var.set(True)  # Default to headless mode

    def save_config(self):
        """Save configuration to config.json"""
        try:
            config = {
                'username': self.username_entry.get(),
                'remember_me': self.remember_me_var.get(),
                'auto_login': self.auto_login_var.get(),
                'headless_mode': self.headless_mode_var.get()  # Save headless mode preference
            }
            with open('config.json', 'w') as f:
                json.dump(config, f)
            
            # Save credentials if remember me is checked
            if self.remember_me_var.get():
                self.save_credentials()
            
            self.log("Saved configuration")
        except Exception as e:
            self.log(f"Error saving config: {str(e)}")

    def add_close_button(self):
        """Add a close button to the top-right corner"""
        self.close_button = ctk.CTkButton(
            self,
            text="×",
            width=40,
            height=40,
            command=self.quit,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="transparent",
            hover_color="#FF4444",
            corner_radius=0
        )
        self.close_button.place(x=self.winfo_width() - 40, y=0)
        
        # Update close button position when window is resized
        self.bind("<Configure>", lambda e: self.close_button.place(x=self.winfo_width() - 40, y=0))

    def start_move(self, event):
        """Begin window drag"""
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

    def show_login_frame(self):
        """Show the login frame and populate saved credentials if available"""
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.loading_frame.grid_remove()
        
        # Populate saved credentials if remember me is enabled
        if self.remember_me_var.get():
            if hasattr(self, 'saved_username'):
                self.username_entry.delete(0, 'end')
                self.username_entry.insert(0, self.saved_username)
                
                # Also load the saved password
                saved_password = self.get_saved_password()
                if saved_password:
                    self.password_entry.delete(0, 'end')
                    self.password_entry.insert(0, saved_password)
        
        # If auto-login is enabled and we have credentials, start login process
        if self.auto_login_var.get() and self.username_entry.get() and self.password_entry.get():
            self.after(1000, self.perform_login)  # Start login after a short delay

if __name__ == "__main__":
    # Check for headless mode
    headless_mode = '--headless' in sys.argv
    
    app = ModernLoginApp(headless=headless_mode)
    if not headless_mode:
        app.mainloop()
    else:
        app.perform_login() 

