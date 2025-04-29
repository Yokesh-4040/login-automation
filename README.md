# Simulanis Auto Login Application

A modern GUI application for automated login to Simulanis platform with secure credential management.

## Version
Current Version: 1.1.0

## Features

- Modern, customizable GUI using CustomTkinter
- Secure credential storage using keyring
- Headless mode support for automated login
- Remember me and auto-login functionality
- Certificate handling for HTTPS connections
- Configurable retry mechanism for connection failures
- Version-specific builds with proper asset management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd simulanis-login
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode
Run the application in GUI mode:
```bash
python auto_login_gui.py
```

### Headless Mode
Run the application in headless mode:
```bash
python auto_login_gui.py --headless
```

## Building

### Standard Build
To create a standard build:
```bash
python build.py
```
This will create a version-specific build in `Desktop/Auto-Login-Build/v{version}`.

### Build Output
The build process will create:
- Executable file (SimulanisLogin.exe)
- Required assets (Icons, Logos)
- Configuration files
- Documentation
- Changelog

### Build Configuration
- Version-specific folders
- Automatic asset management
- Optional custom icon support
- Clean build process with proper error handling

## Configuration

### GUI Configuration
- Remember Me: Securely saves credentials for future use
- Auto-login: Automatically logs in on application startup
- Headless Mode: Runs Chrome in headless mode (no visible browser window)

### Headless Configuration
Create a `headless_config.json` file:
```json
{
    "chrome_options": ["--headless", "--disable-gpu"],
    "auto_login": true,
    "retry_interval": 60,
    "max_retries": 3
}
```

## Directory Structure
```
simulanis-login/
├── auto_login_gui.py    # Main application file
├── build.py            # Build script
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
├── CHANGELOG.md       # Version history
├── config.json        # User configuration
├── Icons/             # Application icons
└── Logos/             # Brand assets
```

## Security

- Credentials are securely stored using the system keyring
- HTTPS certificate handling
- No plaintext password storage

## Development

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- Chrome WebDriver

### Building from Source
To create an executable:
```bash
python build.py
```

The build will be created in: `Desktop/Auto-Login-Build/v{version}/`

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## License

[Your License Here]

## Support

For support, please contact [Your Contact Information] 