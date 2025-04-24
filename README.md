# Automatic Login Automation

This script automates the login process for a specific website. It checks for internet connectivity and automatically logs in using provided credentials.

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- Internet connection

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Open `auto_login.py` and replace the following variables with your actual credentials:
   - `USERNAME`: Your username
   - `PASSWORD`: Your password

2. Run the script:
```bash
python auto_login.py
```

## Features

- Checks for internet connectivity before attempting to login
- Automatically fills in username and password
- Handles login button click
- Provides error handling and feedback
- Keeps the browser open for 30 seconds after login for verification

## Notes

- The script uses Chrome WebDriver for automation
- It will automatically download and manage the appropriate ChromeDriver version
- The browser window will be maximized by default
- You can enable headless mode by uncommenting the relevant line in the script 