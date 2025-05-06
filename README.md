# Simulanis Login Automation

Automated login tool for Simulanis portal with two user interfaces: Mini and Full.

## Features

- **Two User Interfaces**:
  - **Mini UI**: Compact interface that sits in the top-right corner for quick connect/disconnect
  - **Full UI**: Advanced interface with detailed settings and configuration
- **Automatic Login**: Remembers credentials and can automatically log in on startup
- **Secure Credential Storage**: Credentials are securely stored using the system keyring
- **Headless Mode**: Run in the background without a visible browser
- **Status Updates**: Clear status messages during the login process

## Getting Started

### Installation

1. Download the latest release
2. Extract all files to a folder of your choice
3. Run one of the startup batch files to launch the application

### Startup Options

Several batch files are provided for different launch options:

- **Start Simulanis Login (GUI).bat** - Starts the Mini UI (default)
- **Start Simulanis Login (Full UI).bat** - Starts the Full UI with all settings visible
- **Start Simulanis Login.bat** - Starts in headless mode (no UI, background operation)

You can also use the main launcher script directly with options:

```
python simulanis_login.py [--mini] [--full] [--headless]
```

## Usage

### Mini UI

The Mini UI provides:
- Status indicator showing current connection state
- Connect/Disconnect button for quick login management
- Settings button (gear icon) to open the Full UI for advanced configuration
- Close button (X) to exit the application

When credentials are needed, a small dialog will appear to enter username and password.

### Full UI

The Full UI provides:
- Detailed status information
- Username and password fields
- Remember me and auto-login options
- Headless mode toggle
- "Switch to Mini UI" button to change to the compact interface

## Configuration

Settings are automatically saved to `config.json` and shared between both interfaces. Changes made in either UI will be reflected in the other.

### Options

- **Remember Me**: Save credentials securely for future logins
- **Auto-login on startup**: Automatically log in when the application starts
- **Headless Mode**: Run the browser hidden in the background

## Troubleshooting

- **Login Issues**: Check your network connection and credentials
- **UI Problems**: Try using the other interface or restart the application
- **Configuration Issues**: Delete the config.json file to reset to defaults

## Development

The application consists of:
- `mini_login_gui.py` - Compact user interface
- `auto_login_gui.py` - Full-featured user interface
- `login_core.py` - Core login functionality
- `dialogs.py` - Shared dialog components
- `simulanis_login.py` - Main launcher script

## Version
Current Version: 1.1.0

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