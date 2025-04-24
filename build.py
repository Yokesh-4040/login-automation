import PyInstaller.__main__
import os
import sys
import shutil
from urllib.request import urlretrieve
import zipfile
import requests

def download_chromedriver():
    print("Downloading ChromeDriver...")
    # Get the latest Chrome version
    response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE')
    version = response.text.strip()
    
    # Download ChromeDriver
    url = f'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/chromedriver-win64.zip'
    zip_path = 'chromedriver.zip'
    urlretrieve(url, zip_path)
    
    # Extract ChromeDriver
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('.')
    
    # Move ChromeDriver to current directory
    shutil.move('chromedriver-win64/chromedriver.exe', 'chromedriver.exe')
    
    # Clean up
    os.remove(zip_path)
    shutil.rmtree('chromedriver-win64')

def create_icon():
    print("Creating icon...")
    from PIL import Image
    img = Image.new('RGB', (64, 64), color='blue')
    img.save('icon.ico')

def build_exe():
    print("Building executable...")
    
    # Ensure we have ChromeDriver
    if not os.path.exists('chromedriver.exe'):
        download_chromedriver()
    
    # Create icon if it doesn't exist
    if not os.path.exists('icon.ico'):
        create_icon()
    
    # Build the executable
    PyInstaller.__main__.run([
        'auto_login_gui.py',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--add-data=chromedriver.exe;.',
        '--add-data=icon.ico;.',
        '--name=AutoLogin',
        '--clean',
    ])
    
    print("\nBuild complete! You can find AutoLogin.exe in the dist folder.")
    print("To share with colleagues:")
    print("1. Send them the AutoLogin.exe file")
    print("2. They can double-click to run it")
    print("3. To add to startup, they can create a shortcut in their startup folder")

if __name__ == "__main__":
    build_exe() 