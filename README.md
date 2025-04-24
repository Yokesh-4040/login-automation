# Simulanis Auto Login v1.0.0

A modern, secure desktop application for automated login to Simulanis network services.

## Features

- 🔒 Secure credential management using system keyring
- 🎨 Modern, responsive UI with dark mode support
- 🤖 Headless mode for automated login
- 🔄 Auto-login capability on startup
- 🎯 Remember me functionality
- 🛡️ SSL certificate handling
- 📱 Responsive and draggable window

## Requirements

- Python 3.7+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository or download the latest release
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode
Run the application in normal mode:
```bash
python auto_login_gui.py
```

### Headless Mode
Run the application in headless mode:
```bash
python auto_login_gui.py --headless
```

## Configuration

### GUI Configuration
- **Remember Me**: Securely saves credentials for future use
- **Auto-login**: Automatically logs in on application startup
- **Headless Mode**: Runs Chrome in headless mode (no browser window)

### Headless Configuration
Edit `headless_config.json` to customize headless mode:
```json
{
    "chrome_options": ["--headless", "--disable-gpu"],
    "auto_login": true,
    "retry_interval": 60,
    "max_retries": 3
}
```

## Security Features

- Credentials are stored securely using the system keyring
- No plaintext password storage
- SSL certificate handling
- Secure password visibility toggle

## Directory Structure

```
.
├── auto_login_gui.py    # Main application file
├── requirements.txt     # Python dependencies
├── headless_config.json # Headless mode configuration
├── config.json         # User preferences
├── Icons/             # Application icons
└── Logos/             # Branding assets
```

## Version History

### v1.0.0
- Initial release
- Modern UI with customtkinter
- Secure credential management
- Headless mode support
- Auto-login functionality
- Remember me feature
- SSL certificate handling
- Draggable window interface

## License

© Simulanis Solutions Pvt. Ltd. All rights reserved. 