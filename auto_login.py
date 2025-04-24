import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_internet():
    print("Checking internet connectivity...")
    try:
        requests.get("http://www.google.com", timeout=3, verify=False)
        print("Internet connection is available.")
        return True
    except requests.ConnectionError:
        print("No internet connection. Please check your connection and try again.")
        return False

def setup_driver():
    print("Setting up Chrome driver...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")
    
    if not os.path.exists(chromedriver_path):
        print(f"Error: chromedriver.exe not found at {chromedriver_path}")
        return None
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def auto_login(username, password):
    if not check_internet():
        return
    
    driver = setup_driver()
    if driver is None:
        return
        
    try:
        print("Navigating to login page...")
        driver.get("https://192.168.1.9/userlogin/")
        
        # Handle security warning if present
        try:
            advanced_button = driver.find_element(By.ID, "details-button")
            advanced_button.click()
            proceed_link = driver.find_element(By.ID, "proceed-link")
            proceed_link.click()
        except:
            pass

        # Wait for and fill username
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
        username_field.clear()
        username_field.send_keys(username)
        
        # Fill password
        password_field = driver.find_element(By.ID, "passwd")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        submit_button = driver.find_element(By.ID, "submitbtn")
        submit_button.click()
        
        print("Login completed!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    USERNAME = "Yokesh-CSW"
    PASSWORD = "Password@123"
    
    print("Starting login process...")
    auto_login(USERNAME, PASSWORD) 