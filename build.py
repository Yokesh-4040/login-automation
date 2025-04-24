import PyInstaller.__main__
import os
import sys
import shutil
from urllib.request import urlretrieve
import zipfile
import requests
import argparse

def download_chromedriver(target_dir):
    print("Downloading ChromeDriver...")
    # Get the latest Chrome version
    response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE')
    version = response.text.strip()
    
    # Download ChromeDriver
    url = f'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/chromedriver-win64.zip'
    zip_path = os.path.join(target_dir, 'chromedriver.zip')
    urlretrieve(url, zip_path)
    
    # Extract ChromeDriver
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    
    # Move ChromeDriver to target directory
    chromedriver_src = os.path.join(target_dir, 'chromedriver-win64', 'chromedriver.exe')
    chromedriver_dest = os.path.join(target_dir, 'chromedriver.exe')
    shutil.move(chromedriver_src, chromedriver_dest)
    
    # Clean up
    os.remove(zip_path)
    shutil.rmtree(os.path.join(target_dir, 'chromedriver-win64'))
    
    return chromedriver_dest

def create_icon(target_dir):
    print("Creating icon...")
    from PIL import Image
    icon_path = os.path.join(target_dir, 'icon.ico')
    img = Image.new('RGB', (64, 64), color='blue')
    img.save(icon_path)
    return icon_path

def build_exe(headless=False, build_dir=None):
    print("Building executable...")
    
    # Set build directory
    if build_dir is None:
        build_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Automation_Builds", "Login")
    
    # Ensure build directory exists
    os.makedirs(build_dir, exist_ok=True)
    
    # Clean previous build files
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Download ChromeDriver to build directory
    chromedriver_path = download_chromedriver(build_dir)
    
    # Create icon in build directory
    icon_path = create_icon(build_dir)
    
    # Prepare build arguments
    build_args = [
        'auto_login_gui.py',
        '--onefile',
        '--windowed',
        f'--icon={icon_path}',
        f'--add-data={chromedriver_path};.',
        f'--add-data={icon_path};.',
        '--name=SimulanisLogin',
        '--clean',
        f'--distpath={build_dir}',
        f'--workpath={os.path.join(build_dir, "build")}',
        f'--specpath={build_dir}'
    ]

    # Add headless mode argument if specified
    if headless:
        headless_config = os.path.join(build_dir, 'headless_config.json')
        # Copy headless config to build directory
        shutil.copy2('headless_config.json', headless_config)
        build_args.extend([f'--add-data={headless_config};.'])
    
    # Build the executable
    PyInstaller.__main__.run(build_args)
    
    # Copy necessary files to build directory
    for file in ['config.json', 'requirements.txt', 'README.md']:
        if os.path.exists(file):
            shutil.copy2(file, build_dir)
    
    print(f"\nBuild complete! The results are available in: {build_dir}")
    print("To share with colleagues:")
    print("1. Send them the executable file")
    print("2. They can double-click to run it")
    print("3. To add to startup, they can create a shortcut in their startup folder")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build the SimulanisLogin application')
    parser.add_argument('--headless', action='store_true', help='Build in headless mode')
    parser.add_argument('--build-dir', help='Specify custom build directory')
    args = parser.parse_args()
    
    build_exe(headless=args.headless, build_dir=args.build_dir) 