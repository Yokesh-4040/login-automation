import os
import sys
import winreg as reg
import win32com.client
import tkinter as tk
from tkinter import messagebox

def create_shortcut():
    # Get the path of the auto_login_gui.py script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "auto_login_gui.py")
    
    # Get the Python executable path
    python_path = sys.executable
    
    # Create the startup folder path
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    
    # Create shortcut path
    shortcut_path = os.path.join(startup_folder, "AutoLogin.lnk")
    
    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = python_path
    shortcut.Arguments = f'"{script_path}" --startup'
    shortcut.WorkingDirectory = current_dir
    shortcut.save()
    
    return True

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        if create_shortcut():
            messagebox.showinfo("Success", "Auto Login has been added to startup programs!\nIt will run automatically when you start your computer.")
        else:
            messagebox.showerror("Error", "Failed to add Auto Login to startup programs.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    root.destroy()

if __name__ == "__main__":
    main() 