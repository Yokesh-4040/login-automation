import tkinter as tk
from tkinter import ttk
import threading
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
import urllib3
import pystray
from PIL import Image, ImageTk
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AutoLoginGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Set window icon
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except:
            pass
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Configure style
        style = ttk.Style()
        style.configure("Status.TLabel", padding=10)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Log text area
        self.log_text = tk.Text(main_frame, height=10, width=40)
        self.log_text.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Start button
        self.start_button = ttk.Button(main_frame, text="Start Login", command=self.start_login)
        self.start_button.grid(row=3, column=0, pady=10)
        
        # Minimize button
        self.min_button = ttk.Button(main_frame, text="Minimize to Tray", command=self.minimize_to_tray)
        self.min_button.grid(row=3, column=1, pady=10)
        
        # Handle window close
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        
        self.is_running = False
    
    def create_tray_icon(self):
        try:
            icon = Image.open(resource_path("icon.ico"))
        except:
            icon = Image.new('RGB', (64, 64), color='blue')
        self.icon = pystray.Icon("auto_login", icon, "Auto Login", self.create_tray_menu())
    
    def create_tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Start Login", self.start_login),
            pystray.MenuItem("Exit", self.quit_app)
        )
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self, message, progress=None):
        self.status_var.set(message)
        if progress is not None:
            self.progress['value'] = progress
    
    def minimize_to_tray(self):
        self.root.withdraw()
        self.icon.run()
    
    def show_window(self):
        self.icon.stop()
        self.root.deiconify()
    
    def quit_app(self):
        self.icon.stop()
        self.root.quit()
    
    def setup_driver(self):
        self.log("Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument('--headless')  # Run in background
        
        try:
            service = Service(resource_path("chromedriver.exe"))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            self.log(f"Error setting up Chrome driver: {str(e)}")
            return None
    
    def perform_login(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.start_button.state(['disabled'])
        
        try:
            self.update_status("Starting login process...", 10)
            driver = self.setup_driver()
            if not driver:
                return
            
            self.update_status("Navigating to login page...", 30)
            driver.get("https://192.168.1.9/userlogin/")
            
            try:
                self.update_status("Handling security warning...", 40)
                advanced_button = driver.find_element(By.ID, "details-button")
                advanced_button.click()
                proceed_link = driver.find_element(By.ID, "proceed-link")
                proceed_link.click()
            except:
                self.log("No security warning found.")
            
            self.update_status("Entering credentials...", 60)
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
            username_field.clear()
            username_field.send_keys("Yokesh-CSW")
            
            password_field = driver.find_element(By.ID, "passwd")
            password_field.clear()
            password_field.send_keys("Password@123")
            
            self.update_status("Clicking login button...", 80)
            submit_button = driver.find_element(By.ID, "submitbtn")
            submit_button.click()
            
            self.update_status("Login completed!", 100)
            self.log("Login successful!")
            
            time.sleep(2)
            driver.quit()
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.update_status("Login failed!", 0)
        finally:
            self.is_running = False
            self.start_button.state(['!disabled'])
    
    def start_login(self):
        threading.Thread(target=self.perform_login, daemon=True).start()
    
    def run(self):
        # Start automatic login if it's a startup run
        if getattr(sys, 'frozen', False) and len(sys.argv) > 1 and sys.argv[1] == "--startup":
            self.start_login()
            self.minimize_to_tray()
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoLoginGUI()
    app.run() 