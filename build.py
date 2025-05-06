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

VERSION = "1.2.1"
CHANGELOG = {
    "1.2.1": [
        "Merged mini and full UI into a single application",
        "Fixed settings button functionality in executable build",
        "Improved UI switching between mini and full modes",
        "Removed credential dialog popup in favor of direct UI switching",
        "Enhanced build process for better application integration"
    ],
    "1.2.0": [
        "Added modern Windows 11 styled UI with rounded corners",
        "Improved mini UI layout with better spacing and positioning",
        "Replaced text button with icon-only connect button",
        "Enhanced status message visibility and flow",
        "Dynamic layout adjustment after connection"
    ],
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
    # Use the specific path requested by the user
    return "D:\\Automation\\Auto_Login_Build"

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
        'config.json': os.path.join(version_dir, 'config.json'),
        'icon.ico': os.path.join(version_dir, 'icon.ico'),
        'file_version_info.txt': os.path.join(version_dir, 'file_version_info.txt')
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

def create_optimized_icon():
    """Create a fresh optimized icon file with standard Windows sizes"""
    try:
        from PIL import Image
        
        # Standard Windows icon sizes
        sizes = [16, 24, 32, 48, 64, 128, 256]
        
        # Open the original icon
        if os.path.exists("icon.ico"):
            # Create a set of properly sized images
            try:
                original = Image.open("icon.ico")
                
                # Create a temporary file for the new icon
                temp_icon = "temp_icon.ico"
                
                # Save as multi-size icon
                original.save(temp_icon, sizes=sizes)
                
                # Replace the original with the optimized version
                if os.path.exists(temp_icon):
                    if os.path.exists("icon.ico"):
                        os.remove("icon.ico")
                    shutil.move(temp_icon, "icon.ico")
                    print("✓ Created optimized multi-size icon")
                    return True
            except Exception as e:
                print(f"Could not process existing icon: {e}")
                return False
        else:
            # Create a simple blue square icon with standard sizes
            img = Image.new('RGB', (256, 256), color='blue')
            
            # Create a temporary file for the new icon
            img.save("icon.ico", format="ICO", sizes=sizes)
            print("✓ Created new default icon")
            return True
    except Exception as e:
        print(f"Warning: Could not create optimized icon: {str(e)}")
        return False

def create_simple_icon():
    """Create a very simple small icon as a last resort"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 64x64 blue square with a white 'S' in it
        img = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(img)
        
        # Draw a white 'S'
        draw.text((20, 10), "S", fill='white', size=40)
        
        # Save as a simple icon
        img.save("simple_icon.ico")
        
        # Use this as our icon
        if os.path.exists("icon.ico"):
            os.remove("icon.ico")
        shutil.copy("simple_icon.ico", "icon.ico")
        
        print("✓ Created simple fallback icon")
        return True
    except Exception as e:
        print(f"Could not create simple icon: {e}")
        return False

def ensure_valid_icon():
    """Ensure the icon file is properly formatted for PyInstaller"""
    # Try to create an optimized icon first
    if create_optimized_icon():
        return True
    
    # If that fails, try a simple icon
    if create_simple_icon():
        return True
        
    # Fallback to simple validation
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("Icon file not found, will use default icon")
        return False
    
    return os.path.exists(icon_path)

def create_spec_file(version_dir):
    """Create a custom .spec file with explicit icon reference"""
    # Use raw string or properly escaped path for Windows
    icon_path = os.path.abspath("icon.ico").replace("\\", "\\\\")
    main_path = os.path.abspath("main.py").replace("\\", "\\\\")
    spec_path = os.path.join(version_dir, "SimulanisLogin.spec")
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{main_path}'],
    pathex=[],
    binaries=[],
    datas=[('Icons', 'Icons'), ('Logos', 'Logos'), ('icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SimulanisLogin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path}',
    version='file_version_info.txt',
)
"""
    
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    print(f"✓ Created custom spec file with icon: {spec_path}")
    return spec_path

def build_executable(version_dir):
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Ensure Icons and Logos are in the current directory
    ensure_directories()
    
    # Create a custom spec file with explicit icon reference
    spec_file = create_spec_file(version_dir)
    
    # PyInstaller configuration using the spec file
    cmd = [
        'pyinstaller',
        '--noconfirm',
        f'--distpath={version_dir}',
        f'--workpath={os.path.join(version_dir, "build")}',
        spec_file
    ]
    
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

def prepare_build_icon():
    """Prepare icon for the build process by saving the original and creating a guaranteed simple one"""
    # Save original icon if it exists
    if os.path.exists("icon.ico"):
        try:
            # Backup the original
            shutil.copy("icon.ico", "original_icon.ico")
            print("✓ Backed up original icon")
            
            # Create a minimal icon that PyInstaller will definitely accept
            from PIL import Image
            img = Image.new('RGB', (32, 32), color=(0, 0, 255))
            img.save("icon.ico", format="ICO")
            print("✓ Created simple build-compatible icon")
            return True
        except Exception as e:
            print(f"Could not prepare icon: {e}")
    return False

def restore_original_icon():
    """Restore the original icon after build is complete"""
    if os.path.exists("original_icon.ico"):
        try:
            # Restore the original
            if os.path.exists("icon.ico"):
                os.remove("icon.ico")
            shutil.copy("original_icon.ico", "icon.ico")
            os.remove("original_icon.ico")
            print("✓ Restored original icon")
            return True
        except Exception as e:
            print(f"Could not restore original icon: {e}")
    return False

def build_simple():
    """Simple clean build with icon"""
    version_dir = create_version_folder()
    
    # Create a clean build folder
    if os.path.exists(version_dir):
        try:
            # Remove any existing files from previous build attempts
            for item in os.listdir(version_dir):
                item_path = os.path.join(version_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print("✓ Cleaned build directory")
        except Exception as e:
            print(f"Warning: Could not clean directory: {e}")
    
    # Simple direct PyInstaller command
    cmd = [
        'pyinstaller',
        '--noconfirm',
        '--clean',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--version-file=file_version_info.txt',
        '--name=SimulanisLogin',
        f'--distpath={version_dir}',
        '--add-data=Icons;Icons' if os.name == 'nt' else '--add-data=Icons:Icons',
        '--add-data=Logos;Logos' if os.name == 'nt' else '--add-data=Logos:Logos',
        'main.py'
    ]
    
    print("Running simple build command...")
    try:
        subprocess.check_call(cmd)
        print("✓ Built executable successfully")
        
        # Copy additional assets
        copy_assets(version_dir)
        print("✓ Copied additional assets")
        
        return True
    except Exception as e:
        print(f"Error during build: {e}")
        return False

def main():
    """Main build process"""
    try:
        print(f"Starting build process for version {VERSION}...")
        
        # Try the simple build approach
        if build_simple():
            print("\nBuild completed successfully!")
            print(f"Build files are available in: {get_build_directory()}/v{VERSION}")
        else:
            print("\nBuild failed. Please check the error messages above.")
            sys.exit(1)
        
    except Exception as e:
        print(f"\nError during build process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 