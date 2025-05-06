#!/usr/bin/env python3
"""
Simulanis Login - Main Launcher Script

This script serves as the main entry point for the Simulanis Login Automation tool.
It can launch either the mini or full UI based on command-line arguments.
"""

import sys
import os
import argparse
import subprocess

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simulanis Login Automation Tool")
    
    # Define arguments
    parser.add_argument('--mini', action='store_true', help='Launch Mini UI (default)')
    parser.add_argument('--full', action='store_true', help='Launch Full UI')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode with no UI')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Determine which mode to use (default to mini if no mode specified)
    use_full_ui = args.full and not args.mini
    headless_mode = args.headless
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if headless_mode:
        # Run the automation in headless mode (no UI)
        print("Starting Simulanis Login in headless mode...")
        # Either use the mini login with headless flag
        script_path = os.path.join(script_dir, "mini_login_gui.py")
        subprocess.run([sys.executable, script_path, "--headless"])
    elif use_full_ui:
        # Launch the full UI
        print("Starting Simulanis Login with full UI...")
        script_path = os.path.join(script_dir, "auto_login_gui.py")
        subprocess.Popen([sys.executable, script_path])
    else:
        # Launch the mini UI (default)
        print("Starting Simulanis Login with mini UI...")
        script_path = os.path.join(script_dir, "mini_login_gui.py")
        subprocess.Popen([sys.executable, script_path])
    
if __name__ == "__main__":
    main() 