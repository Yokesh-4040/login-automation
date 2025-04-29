import PyInstaller.__main__
import os
import sys
import shutil
from urllib.request import urlretrieve
import zipfile
import requests
import argparse
import json
from datetime import datetime
import subprocess
from pathlib import Path

VERSION = "1.1.0"
CHANGELOG = {
    "1.1.0": [
        "Updated build structure with version-specific folders",
        "Enhanced build process with better asset management",
        "Improved error handling and logging"
    ],
    "1.0.3": [
        "Fixed status message persistence after login",
        "Added proper handling for already logged in state",
        "Improved error messages for login failures",
        "Enhanced logging with timestamps"
    ]
}

def get_build_directory():
    """Get the base build directory path"""
    return os.path.join(os.path.expanduser("~"), "Desktop", "Auto-Login-Build")

def create_version_folder():
    """Create version-specific folder and copy changelog"""
    base_dir = get_build_directory()
    version_dir = os.path.join(base_dir, f"v{VERSION}")
    
    # Create version directory
    os.makedirs(version_dir, exist_ok=True)
    print(f"✓ Created version directory: {version_dir}")
    
    # Create changelog file
    changelog_path = os.path.join(version_dir, "CHANGELOG.md")
    with open(changelog_path, "w") as f:
        f.write("# Changelog\n\n")
        for ver, changes in CHANGELOG.items():
            f.write(f"## Version {ver}\n")
            for change in changes:
                f.write(f"- {change}\n")
            f.write("\n")
    print("✓ Created changelog file")
    
    return version_dir

def ensure_directories():
    """Ensure all required directories exist"""
    print("Creating required directories...")
    directories = ['Icons', 'Logos']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Ensured {directory} directory exists")

def copy_assets(version_dir):
    """Copy assets to version directory"""
    print("Copying assets...")
    
    # First ensure source directories exist
    ensure_directories()
    
    # Define assets to copy
    assets = {
        'Icons': os.path.join(version_dir, 'Icons'),
        'Logos': os.path.join(version_dir, 'Logos'),
        'headless_config.json': os.path.join(version_dir, 'headless_config.json'),
        'README.md': os.path.join(version_dir, 'README.md'),
        'requirements.txt': os.path.join(version_dir, 'requirements.txt'),
        'config.json': os.path.join(version_dir, 'config.json')
    }
    
    # Copy each asset
    for src, dst in assets.items():
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"✓ Copied {src}")
            except Exception as e:
                print(f"Warning: Could not copy {src}: {str(e)}")

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

def build_executable(version_dir):
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Ensure Icons and Logos are in the current directory
    ensure_directories()
    
    # Check if icon exists
    icon_path = os.path.join("Icons", "Icon-blue-transparent.png")
    if not os.path.exists(icon_path):
        print("Warning: Icon file not found, using default icon")
        icon_option = []
    else:
        icon_option = [f'--icon={icon_path}']
    
    # PyInstaller configuration
    cmd = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name=SimulanisLogin',
        f'--distpath={version_dir}',
        f'--workpath={os.path.join(version_dir, "build")}',
        f'--specpath={version_dir}',
        '--add-data=Icons;Icons' if os.name == 'nt' else '--add-data=Icons:Icons',
        '--add-data=Logos;Logos' if os.name == 'nt' else '--add-data=Logos:Logos',
        'auto_login_gui.py'
    ]
    
    # Add icon option if available
    cmd.extend(icon_option)
    
    try:
        subprocess.check_call(cmd)
        print("✓ Built executable")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {str(e)}")
        raise

def cleanup(version_dir):
    """Clean up build artifacts"""
    print("Cleaning up...")
    build_dir = os.path.join(version_dir, "build")
    spec_file = os.path.join(version_dir, "SimulanisLogin.spec")
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    print("✓ Cleaned up build artifacts")

def main():
    """Main build process"""
    try:
        print(f"Starting build process for version {VERSION}...")
        
        # Create version directory
        version_dir = create_version_folder()
        
        # Copy assets to version directory first
        copy_assets(version_dir)
        
        # Build executable in version directory
        build_executable(version_dir)
        
        # Clean up build artifacts
        cleanup(version_dir)
        
        print("\nBuild completed successfully!")
        print(f"Build files are available in: {version_dir}")
        
    except Exception as e:
        print(f"\nError during build process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 