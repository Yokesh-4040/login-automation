import tkinter as tk
from tkinter import ttk
import customtkinter as ctk  # We'll need this package for modern UI elements
from PIL import Image, ImageTk
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ModernLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.title("SystemOS Login")
        self.geometry("400x600")
        
        # Set the color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.main_frame,
            text="SystemOS",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, pady=(20, 10))
        
        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Username",
            width=300
        )
        self.username_entry.grid(row=1, column=0, pady=(20, 10))
        
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Password",
            show="•",
            width=300
        )
        self.password_entry.grid(row=2, column=0, pady=(10, 20))
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Login",
            command=self.perform_login,
            width=300
        )
        self.login_button.grid(row=3, column=0, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            width=300
        )
        self.progress_bar.grid(row=4, column=0, pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready to login",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=5, column=0, pady=10)
        
        # Log text area
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            width=300,
            height=100
        )
        self.log_text.grid(row=6, column=0, pady=10)
        
        # Load saved configuration
        self.load_config()

    def log(self, message):
        """Add a message to the log text area"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)  # Scroll to the bottom
        self.update()

    def load_config(self):
        """Load saved configuration from config.json"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if 'username' in config:
                        self.username_entry.insert(0, config['username'])
                        self.log("Loaded saved username")
            else:
                self.log("No saved credentials found")
        except Exception as e:
            self.log(f"Error loading config: {str(e)}")

    def save_config(self):
        """Save configuration to config.json"""
        try:
            config = {
                'username': self.username_entry.get()
            }
            with open('config.json', 'w') as f:
                json.dump(config, f)
            self.log("Saved configuration")
        except Exception as e:
            self.log(f"Error saving config: {str(e)}")

    def update_status(self, message, progress):
        """Update the status label and progress bar"""
        self.status_label.configure(text=message)
        self.progress_bar.set(progress / 100)
        self.log(message)
        self.update()

    def perform_login(self):
        # Disable login button
        self.login_button.configure(state="disabled")
        
        try:
            self.update_status("Initializing browser...", 20)
            driver = webdriver.Chrome()
            
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
            username_field.send_keys(self.username_entry.get())
            
            password_field = driver.find_element(By.ID, "passwd")
            password_field.clear()
            password_field.send_keys(self.password_entry.get())
            
            self.update_status("Logging in...", 80)
            submit_button = driver.find_element(By.ID, "submitbtn")
            submit_button.click()
            
            self.update_status("Login successful!", 100)
            self.save_config()  # Save the configuration after successful login
            time.sleep(2)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 0)
        finally:
            self.login_button.configure(state="normal")
            driver.quit()

if __name__ == "__main__":
    app = ModernLoginApp()
    app.mainloop() 
