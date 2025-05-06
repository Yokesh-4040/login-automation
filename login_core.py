"""
Simulanis Login Core

This module provides the core login functionality for Simulanis login automation.
It can be used by different user interfaces.
"""

import keyring
import json
import os
import time
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginManager:
    """Core class for handling login operations"""
    
    # Constants
    DEFAULT_TARGET_URL = "https://192.168.1.9/userlogin/"
    KEYRING_SERVICE = "SimulanisLogin"
    CONFIG_FILENAME = "config.json"
    HEADLESS_CONFIG_FILENAME = "headless_config.json"
    
    def __init__(self, headless=False, ui_callback=None, config_dir=None):
        """
        Initialize the login manager
        
        Args:
            headless (bool): If True, run in headless mode without UI
            ui_callback (function): Callback function to update UI with status messages
                                  Function signature: callback(message, progress=None)
            config_dir (str, optional): Directory where config files are stored
        """
        self.headless = headless
        self.ui_callback = ui_callback
        
        # Determine config directory properly - crucial for packaged app
        if config_dir:
            self.config_dir = config_dir
        else:
            # If running as executable, use executable's directory, otherwise script directory
            self.config_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        
        self.log(f"Using config directory: {self.config_dir}")
        
        # Connection details
        self.target_url = self.DEFAULT_TARGET_URL
        self.is_connected = False
        
        # Load configuration
        self.config = self.load_config()
        
        # Set up headless config if needed
        if headless:
            self.headless_config = self.load_headless_config()
    
    def get_keyring_service(self):
        """Get the appropriate keyring service name, handling packaged app considerations"""
        # For packaged apps, we might need a more specific service name
        if getattr(sys, 'frozen', False):
            # Get the executable name without extension for better identification
            exe_name = os.path.splitext(os.path.basename(sys.executable))[0]
            service_name = f"{self.KEYRING_SERVICE}_{exe_name}"
            self.log(f"Using packaged app keyring service: {service_name}")
            return service_name
        
        # For regular Python scripts, use the default service name
        return self.KEYRING_SERVICE
    
    def load_config(self):
        """Load the main configuration file"""
        try:
            # Look for config in specified directory
            config_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.log(f"Config loaded from {config_path}")
                    return config
            else:
                self.log(f"Config file not found at {config_path}, using defaults")
                return {
                    'username': '',
                    'remember_me': False,
                    'auto_login': False,
                    'headless_mode': False
                }
        except Exception as e:
            self.log(f"Error loading config: {str(e)}")
            return {
                'username': '',
                'remember_me': False, 
                'auto_login': False,
                'headless_mode': False
            }
    
    def load_headless_config(self):
        """Load headless mode configuration"""
        try:
            # Look for headless config in specified directory
            config_path = os.path.join(self.config_dir, self.HEADLESS_CONFIG_FILENAME)
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    headless_config = json.load(f)
                    self.log(f"Headless config loaded from {config_path}")
                    return headless_config
            else:
                self.log(f"Headless config not found at {config_path}, using defaults")
                return {
                    "chrome_options": ["--headless", "--disable-gpu"],
                    "auto_login": True,
                    "retry_interval": 60,
                    "max_retries": 3
                }
        except Exception as e:
            self.log(f"Error loading headless config: {str(e)}")
            return {
                "chrome_options": ["--headless", "--disable-gpu"],
                "auto_login": True,
                "retry_interval": 60,
                "max_retries": 3
            }
    
    def save_config(self, config_data):
        """Save configuration to file"""
        try:
            config_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            self.log(f"Config saved to {config_path}")
            # Update the internal config
            self.config = config_data
            return True
        except Exception as e:
            self.log(f"Error saving config: {str(e)}")
            return False
    
    def save_credentials(self, username, password, remember=True):
        """Save credentials to keyring if remember is True"""
        if remember and username and password:
            try:
                service = self.get_keyring_service()
                self.log(f"Saving credentials for {username} using service {service}")
                keyring.set_password(service, username, password)
                self.log(f"Credentials saved for {username}")
                return True
            except Exception as e:
                self.log(f"Error saving credentials: {str(e)}")
                return False
        elif not remember:
            # If not remembering, try to remove any saved credentials
            try:
                service = self.get_keyring_service()
                self.log(f"Removing credentials for {username} from service {service}")
                keyring.delete_password(service, username)
                self.log(f"Credentials removed for {username}")
            except Exception as e:
                # Log but don't raise if credential doesn't exist
                self.log(f"Note: Could not remove credentials: {str(e)}")
        return False
    
    def get_saved_username(self):
        """Get saved username from config"""
        username = self.config.get('username', '')
        if username:
            self.log(f"Found saved username: {username}")
        return username
    
    def get_saved_password(self, username=None):
        """Retrieve saved password from keyring"""
        username = username or self.get_saved_username()
        
        if not username:
            self.log("No username provided for password retrieval")
            return None
            
        # Try to get password with the current service name
        try:
            current_service = self.get_keyring_service()
            self.log(f"Retrieving password for {username} using service {current_service}")
            password = keyring.get_password(current_service, username)
            
            # If we found a password, return it
            if password:
                self.log(f"Password found for {username}")
                return password
                
            # If we're running as executable and didn't find a password, try the old service name
            if getattr(sys, 'frozen', False):
                # Try the default service name as fallback
                self.log(f"Trying legacy service {self.KEYRING_SERVICE}")
                legacy_password = keyring.get_password(self.KEYRING_SERVICE, username)
                if legacy_password:
                    self.log(f"Found password in legacy keyring service, migrating...")
                    # Migrate the password to the new service
                    keyring.set_password(current_service, username, legacy_password)
                    return legacy_password
            
            # No password found in any service
            self.log(f"No password found for {username}")
            return None
        except Exception as e:
            self.log(f"Error retrieving password: {str(e)}")
            return None
    
    def perform_login(self, username=None, password=None, headless_mode=None):
        """
        Perform the login operation
        
        Args:
            username (str, optional): Username to use for login
            password (str, optional): Password to use for login
            headless_mode (bool, optional): Override headless mode setting
            
        Returns:
            dict: Result with keys:
                success (bool): True if login succeeded
                message (str): Status message
                already_logged_in (bool): True if user was already logged in
        """
        # Use provided credentials or try to get saved ones
        username = username or self.get_saved_username()
        password = password or self.get_saved_password(username)
        
        # Determine headless mode
        use_headless = headless_mode if headless_mode is not None else self.config.get('headless_mode', False)
        
        # Initialize result
        result = {
            'success': False,
            'message': "",
            'already_logged_in': False
        }
        
        # Exit early if missing credentials
        if not username or not password:
            result['message'] = "Missing credentials"
            self.update_status("Missing credentials")
            return result
            
        # Update status
        self.update_status("Initializing connection...", 10)
        
        driver = None
        try:
            # Set up Chrome options
            chrome_options = Options()
            
            # Apply headless mode if requested
            if use_headless or self.headless:
                chrome_options.add_argument("--headless")
                
            # Standard options
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Add additional options from headless config if in headless mode
            if self.headless and hasattr(self, 'headless_config'):
                for option in self.headless_config.get('chrome_options', []):
                    chrome_options.add_argument(option)
            
            # Initialize the browser
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to the login page
            self.update_status("Connecting to login page...", 30)
            driver.get(self.target_url)
            
            # Handle security warning if present
            try:
                self.update_status("Handling security certificates...", 40)
                wait = WebDriverWait(driver, 5)
                advanced_button = wait.until(EC.element_to_be_clickable((By.ID, "details-button")))
                advanced_button.click()
                
                proceed_link = wait.until(EC.element_to_be_clickable((By.ID, "proceed-link")))
                proceed_link.click()
                
                self.update_status("Certificate bypass successful", 45)
            except Exception:
                # Certificate warning didn't appear, which is fine
                self.update_status("No certificate bypass needed", 45)
            
            # Enter credentials
            self.update_status(f"Authenticating {username[:3]}...", 60)
            
            # Find and fill username field
            try:
                wait = WebDriverWait(driver, 10)
                username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
                username_field.clear()
                username_field.send_keys(username)
            except Exception as e:
                raise ConnectionError(f"Could not connect to login page: {str(e)}")
            
            # Find and fill password field
            try:
                password_field = driver.find_element(By.ID, "passwd")
                password_field.clear()
                password_field.send_keys(password)
            except Exception as e:
                raise ConnectionError(f"Login form elements not found: {str(e)}")
            
            # Submit the form
            self.update_status("Submitting credentials...", 80)
            submit_button = driver.find_element(By.ID, "submitbtn")
            submit_button.click()
            
            # Wait for response and analyze the result
            time.sleep(2)
            
            # Check for userSense redirect pattern
            if "192.168.1.9/userSense" in driver.current_url:
                time.sleep(2)
                if self.target_url in driver.current_url:
                    result['message'] = "Login failed: Redirect loop detected"
                    raise ValueError("Login failed: Redirect loop detected")
            
            # Check the page content and URL for results
            page_source = driver.page_source
            
            # Check for authentication failure
            auth_fail_msg = f"Authentication Failed for user:{username}"
            if auth_fail_msg in page_source:
                result['message'] = "Login failed: Invalid credentials"
                raise ValueError("Login failed: Invalid credentials")
            
            # Check for already logged in 
            already_logged_msg = "User is already logged in with same ip"
            if already_logged_msg in page_source:
                self.update_status("Already logged in", 100)
                result['success'] = True
                result['already_logged_in'] = True
                result['message'] = "Already logged in"
                self.is_connected = True
                return result
                
            # Check for successful login
            if "simulanis.com" in driver.current_url:
                self.update_status("Login successful!", 100)
                result['success'] = True
                result['message'] = "Login successful"
                self.is_connected = True
                return result
                
            # Still on login page without specific error message
            if self.target_url in driver.current_url:
                result['message'] = "Login failed: Unknown reason"
                raise ValueError("Login failed: Unknown reason")
                
            # Unknown redirect
            result['message'] = f"Login failed: Unexpected redirect to {driver.current_url}"
            raise ValueError(f"Login failed: Unexpected redirect to {driver.current_url}")
            
        except ValueError as ve:
            self.update_status(f"Error: {str(ve)}")
            result['message'] = str(ve)
        except ConnectionError as ce:
            self.update_status(f"Connection error: {str(ce)}")
            result['message'] = str(ce)
        except Exception as e:
            # Generic error handling
            error_msg = str(e).split('\n')[0][:50]  # Truncate long messages
            self.update_status(f"Error: {error_msg}")
            result['message'] = error_msg
            self.log(f"Full error: {str(e)}")
            
            # Auto-retry logic for headless mode
            if self.headless and hasattr(self, 'headless_config'):
                if self.headless_config.get('auto_login', True):
                    retry_interval = self.headless_config.get('retry_interval', 60)
                    self.log(f"Will retry in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    return self.perform_login(username, password, use_headless)
        finally:
            # Quit the driver if it was initialized
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    self.log(f"Error closing browser: {str(e)}")
        
        return result
    
    def disconnect(self):
        """Disconnect the current session by closing any active browser session"""
        # If we're tracking an active browser session, we could close it here
        # Since we currently don't track the browser session across calls,
        # we'll just update the connection state
        
        # Update connection state
        was_connected = self.is_connected
        self.is_connected = False
        
        # Log disconnection
        if was_connected:
            self.log("User manually disconnected")
            self.update_status("Disconnected")
            return {"success": True, "message": "Disconnected successfully"}
        else:
            self.log("Disconnect requested but no active session")
            self.update_status("Not connected")
            return {"success": False, "message": "No active session to disconnect"}
    
    def update_status(self, message, progress=None):
        """Update status via UI callback if available"""
        self.log(message)
        
        # Call UI callback if available
        if self.ui_callback and callable(self.ui_callback):
            self.ui_callback(message, progress)
    
    def log(self, message):
        """Log a message"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

# Simple test code
if __name__ == "__main__":
    # Test the login manager directly
    def status_callback(message, progress=None):
        if progress is not None:
            print(f"Status ({progress}%): {message}")
        else:
            print(f"Status: {message}")
    
    # Create login manager
    login_mgr = LoginManager(ui_callback=status_callback)
    
    # Get saved credentials
    username = login_mgr.get_saved_username()
    if username:
        print(f"Found saved username: {username}")
        password = login_mgr.get_saved_password()
        if password:
            print("Found saved password")
            
            # Try auto-login
            print("\nAttempting login...")
            result = login_mgr.perform_login()
            print(f"Login result: {result}")
        else:
            print("No saved password found")
    else:
        print("No saved credentials found") 