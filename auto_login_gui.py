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

class ModernLoginApp(ctk.CTk):
    def __init__(self, headless=False):
        if not headless:
            super().__init__()
            
            # Application constants
            self.APP_NAME = "Simulanis Login"
            self.KEYRING_SERVICE = "SimulanisLogin"
            
            # Configure the window
            self.title(self.APP_NAME)
            self.geometry("500x700")  # Increased window size
            self.minsize(700, 500)    # Set minimum window size
            self.overrideredirect(True)  # Remove default titlebar
            
            # Center the window on screen
            self.center_window()
            
            # Make window draggable
            self.bind("<Button-1>", self.start_move)
            self.bind("<ButtonRelease-1>", self.stop_move)
            self.bind("<B1-Motion>", self.do_move)
            
            # Set the color theme
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Load branding assets
            self.load_branding()
            
            self.setup_gui()
            
            # Add close button
            self.add_close_button()
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
                logo_img = Image.open(logo_path)
                # Increased logo size
                logo_img = ImageOps.contain(logo_img, (400, 200), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_img)
            else:
                self.logo_image = None

            # Set window icon
            icon_path = os.path.join("Logos", "Icon-blue-transparent.png")
            if os.path.exists(icon_path):
                self.iconphoto(True, ImageTk.PhotoImage(Image.open(icon_path)))
        except Exception as e:
            print(f"Error loading branding assets: {str(e)}")
            self.logo_image = None

    def setup_gui(self):
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main frame with padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")  # Increased padding
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Logo
        if self.logo_image:
            self.logo_label = ctk.CTkLabel(
                self.main_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo_label = ctk.CTkLabel(
                self.main_frame,
                text="Simulanis Solutions",
                font=ctk.CTkFont(size=36, weight="bold")  # Increased font size
            )
        self.logo_label.grid(row=0, column=0, pady=(20, 30), sticky="ew")  # Increased padding
        
        # Create credentials frame
        self.credentials_frame = ctk.CTkFrame(self.main_frame)
        self.credentials_frame.grid(row=1, column=0, sticky="ew", padx=20)  # Increased padding
        self.credentials_frame.grid_columnconfigure(0, weight=1)
        
        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.credentials_frame,
            placeholder_text="Username",
            width=400,  # Increased width
            height=40   # Increased height
        )
        self.username_entry.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.credentials_frame,
            placeholder_text="Password",
            show="•",
            width=400,  # Increased width
            height=40   # Increased height
        )
        self.password_entry.grid(row=1, column=0, pady=10, padx=20)
        
        # Checkboxes frame
        self.checkbox_frame = ctk.CTkFrame(self.credentials_frame, fg_color="transparent")
        self.checkbox_frame.grid(row=2, column=0, pady=10, sticky="w", padx=30)
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            font=ctk.CTkFont(size=12)  # Adjusted font size
        )
        self.show_password_checkbox.grid(row=0, column=0, pady=5, sticky="w")
        
        # Remember me checkbox
        self.remember_me_var = tk.BooleanVar()
        self.remember_me_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Remember me",
            variable=self.remember_me_var,
            font=ctk.CTkFont(size=12)  # Adjusted font size
        )
        self.remember_me_checkbox.grid(row=1, column=0, pady=5, sticky="w")
        
        # Auto-login checkbox
        self.auto_login_var = tk.BooleanVar()
        self.auto_login_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Auto-login on startup",
            variable=self.auto_login_var,
            font=ctk.CTkFont(size=12)  # Adjusted font size
        )
        self.auto_login_checkbox.grid(row=2, column=0, pady=5, sticky="w")
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, pady=(30, 20), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        # Edit credentials button
        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="Edit Credentials",
            command=self.toggle_credentials_view,
            width=400,  # Increased width
            height=40,  # Increased height
            font=ctk.CTkFont(size=14)  # Adjusted font size
        )
        self.edit_button.grid(row=0, column=0, pady=10)
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.button_frame,
            text="Login",
            command=self.perform_login,
            width=400,  # Increased width
            height=40,  # Increased height
            font=ctk.CTkFont(size=14)  # Adjusted font size
        )
        self.login_button.grid(row=1, column=0, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            width=400  # Increased width
        )
        self.progress_bar.grid(row=3, column=0, pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready to login",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=4, column=0, pady=10)
        
        # Footer with company info
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="© Simulanis Solutions Pvt. Ltd.",
            font=ctk.CTkFont(size=11)
        )
        self.footer_label.grid(row=5, column=0, pady=(20, 0))
        
        # Bind Enter key to login
        self.bind('<Return>', lambda e: self.perform_login())
        
        # Load saved configuration and check for auto-login
        self.load_config()
        self.update_credentials_view()
        
        if self.auto_login_var.get() and self.username_entry.get() and self.get_saved_password():
            self.after(1000, self.perform_login)  # Auto-login after 1 second

    def toggle_credentials_view(self):
        """Toggle between compact and expanded credential view"""
        if self.credentials_frame.winfo_viewable():
            self.credentials_frame.grid_remove()
            self.edit_button.configure(text="Edit Credentials")
            self.geometry("500x400")  # Increased compact view size
        else:
            self.credentials_frame.grid()
            self.edit_button.configure(text="Hide Credentials")
            self.geometry("500x700")  # Increased expanded view size
        self.center_window()

    def update_credentials_view(self):
        """Update the credentials view based on saved state"""
        if self.username_entry.get() and self.get_saved_password():
            self.credentials_frame.grid_remove()
            self.edit_button.configure(text="Edit Credentials")
            self.geometry("500x400")  # Compact view
        else:
            self.credentials_frame.grid()
            self.edit_button.configure(text="Hide Credentials")
            self.geometry("500x700")  # Expanded view
        self.center_window()

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
        timestamp = time.strftime('%H:%M:%S')
        print(f"{timestamp} - {message}")

    def log(self, message):
        """Add a message to the log text area or console"""
        if hasattr(self, 'headless') and self.headless:
            self.console_log(message)
        else:
            print(f"{time.strftime('%H:%M:%S')} - {message}")

    def update_status(self, message, progress):
        """Update the status label and progress bar"""
        if not hasattr(self, 'headless') or not self.headless:
            self.status_label.configure(text=message)
            self.progress_bar.set(progress / 100)
        self.log(message)
        if not hasattr(self, 'headless') or not self.headless:
            self.update()

    def perform_login(self):
        """Perform the login operation"""
        if not hasattr(self, 'headless') or not self.headless:
            self.login_button.configure(state="disabled")
        
        try:
            self.update_status("Initializing browser...", 20)
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            if hasattr(self, 'headless') and self.headless:
                for option in self.headless_config.get('chrome_options', []):
                    chrome_options.add_argument(option)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            self.update_status("Navigating to login page...", 40)
            driver.get("https://192.168.1.9/userlogin/")
            
            # Handle security warning
            try:
                self.update_status("Handling security warning...", 50)
                advanced_button = driver.find_element(By.ID, "details-button")
                advanced_button.click()
                proceed_link = driver.find_element(By.ID, "proceed-link")
                proceed_link.click()
            except:
                pass

            self.update_status("Entering credentials...", 60)
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
            username_field.clear()
            
            # Get username and password
            if hasattr(self, 'headless') and self.headless:
                username = self.get_saved_username()
                password = self.get_saved_password()
            else:
                username = self.username_entry.get()
                password = self.password_entry.get()
            
            username_field.send_keys(username)
            
            password_field = driver.find_element(By.ID, "passwd")
            password_field.clear()
            password_field.send_keys(password)
            
            self.update_status("Logging in...", 80)
            submit_button = driver.find_element(By.ID, "submitbtn")
            submit_button.click()
            
            self.update_status("Login successful!", 100)
            if not hasattr(self, 'headless') or not self.headless:
                self.save_config()
                self.update_credentials_view()
            time.sleep(2)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 0)
            if hasattr(self, 'headless') and self.headless:
                # In headless mode, retry after interval
                if self.headless_config.get('auto_login', True):
                    retry_interval = self.headless_config.get('retry_interval', 60)
                    self.log(f"Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    self.perform_login()
        finally:
            if not hasattr(self, 'headless') or not self.headless:
                self.login_button.configure(state="normal")
            driver.quit()

    def get_saved_username(self):
        """Get saved username from config"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    return config.get('username', '')
        except:
            pass
        return ''

    def get_saved_password(self):
        """Retrieve saved password from keyring"""
        try:
            return keyring.get_password(self.KEYRING_SERVICE, self.get_saved_username())
        except Exception as e:
            self.log(f"Error retrieving password: {str(e)}")
            return None

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

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
                        self.username_entry.insert(0, config['username'])
                        self.log("Loaded saved username")
                    if 'remember_me' in config:
                        self.remember_me_var.set(config['remember_me'])
                    if 'auto_login' in config:
                        self.auto_login_var.set(config['auto_login'])
                    
                    # If remember me is enabled, try to load the password
                    if self.remember_me_var.get():
                        saved_password = self.get_saved_password()
                        if saved_password:
                            self.password_entry.insert(0, saved_password)
                            self.log("Loaded saved password")
            else:
                self.log("No saved configuration found")
        except Exception as e:
            self.log(f"Error loading config: {str(e)}")

    def save_config(self):
        """Save configuration to config.json"""
        try:
            config = {
                'username': self.username_entry.get(),
                'remember_me': self.remember_me_var.get(),
                'auto_login': self.auto_login_var.get()
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
            hover_color="red",
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

if __name__ == "__main__":
    # Check for headless mode
    headless_mode = '--headless' in sys.argv
    
    app = ModernLoginApp(headless=headless_mode)
    if not headless_mode:
        app.mainloop()
    else:
        app.perform_login() 

