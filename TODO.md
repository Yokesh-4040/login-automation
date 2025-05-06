# Simulanis Login Automation - TODO List

## Application Flow Update

We're implementing a new application flow where the Mini Login interface is the primary entry point, with the following changes:

1. The Mini Login GUI (`mini_login_gui.py`) launches as the primary interface
2. It provides quick connect/disconnect functionality with minimal UI footprint
3. The settings button in Mini Login opens the full Auto Login GUI (`auto_login_gui.py`) for advanced settings
4. Both interfaces share login core functionality through `login_core.py`
5. UI code has been modularized with dialog components in `dialogs.py`

## Completed Tasks ✅

### Mini Login GUI Improvements
- [x] Created compact UI that sits in top-right corner
- [x] Implemented Connect/Disconnect functionality
- [x] Added proper close button
- [x] Centered the Connect/Disconnect button
- [x] Extracted CredentialDialog to separate file for modularity
- [x] Added ability to launch full Auto Login GUI from settings button

### Core Improvements
- [x] Created `login_core.py` to separate business logic from UI
- [x] Implemented shared configuration between UIs
- [x] Added proper error handling and status messages
- [x] Fixed auto-minimize after successful login

## Current Tasks 🔄

### Integration and Flow
- [ ] Update startup script(s) to launch `mini_login_gui.py` as the default
- [ ] Ensure configuration changes in one UI are reflected in the other
- [ ] Test workflow between mini and full interfaces
- [ ] Document the new application flow for users

### Mini Login GUI
- [ ] Add tooltip or help text explaining settings button launches full UI
- [ ] Implement smooth transitions between minimized and restored states
- [ ] Consider adding a tray icon for better OS integration
- [ ] Test window positioning on different screen resolutions

### Auto Login GUI
- [ ] Add a reference to Mini Login in the UI for user awareness
- [ ] Consider adding a "Switch to Mini View" button
- [ ] Ensure startup parameters are properly passed between interfaces

## Future Enhancements 🚀

### User Experience
- [ ] Add system tray icon with menu for quick actions
- [ ] Create a cohesive visual identity between both UIs
- [ ] Add animations for state transitions
- [ ] Improve notifications for login status

### Technical Improvements
- [ ] Add comprehensive error handling for network issues
- [ ] Implement proper session management
- [ ] Add graceful shutdown/disconnect on application close
- [ ] Consider a shared state manager between UIs

### Security
- [ ] Review credential storage security
- [ ] Implement session timeout handling
- [ ] Add audit logging for login attempts

## Testing Priorities

1. **Configuration Sharing**: Ensure settings changes in either UI are properly saved and loaded by both
2. **Process Management**: Test that launching the full UI from mini doesn't create conflicts
3. **Credential Handling**: Verify credentials work consistently across both UIs
4. **UI Consistency**: Ensure status messages and state are consistent between interfaces
5. **Error Handling**: Test various error conditions are properly handled in both UIs

---

## Development Notes

- The mini login UI is designed for minimal footprint during daily use
- The full auto login UI provides advanced configuration and detailed status
- Both interfaces should maintain a consistent user experience
- Core login functionality is shared through `login_core.py`
- Dialog components are shared through `dialogs.py`

## Pending Tasks 📝

### High Priority
- [x] Fix user details not being saved/retrieved properly
- [x] Fix missing icons and logos in installed application
- [ ] Add proper error messages for login failures
- [ ] Test system tray functionality across different Windows versions

### Notification Improvements
- [ ] Add more notification types (network status, auto-retry, config changes)
- [ ] Customize notification appearance (colors, animations)
- [ ] Add notification sound effects with mute option
- [ ] Add configurable notification timeout settings
- [ ] Add notification history/log
- [ ] Add notification priority levels
- [ ] Add notification actions (buttons)
- [ ] Add notification grouping for multiple events

### Testing and Documentation
- [ ] Add more comprehensive test cases
- [ ] Create user documentation
- [ ] Add installation guide
- [ ] Document troubleshooting steps

### Features
- [ ] Add error handling for network issues
- [ ] Implement retry mechanism with configurable delay
- [ ] Add update checker for new versions
- [ ] Create configuration UI for advanced settings
- [ ] Add option to start with Windows

### Security
- [ ] Add encryption for stored credentials
- [ ] Implement session management
- [ ] Add logging for security events
- [ ] Add SSL certificate validation

### Deployment
- [ ] Add auto-update mechanism
- [ ] Create deployment documentation
- [ ] Set up CI/CD pipeline

## Next Release Goals ✨

- Investigate and fix auto-minimize issue after successful connection.
- Implement a 'minimize to corner' feature (shrink window to ~10x6 cm in top-right).
- Address startup connection failures on Windows 11 (requires retries).
- Add a loading indicator/animation during the login process to show activity and mitigate the feeling of the app freezing.
- Ensure UI remains responsive (or provides clear feedback) during browser automation.
- Create a new, separate minimal UI version (`mini_login_gui.py`):
  - Small window positioned in a corner (e.g., top-right).
  - Main window shows status and connect/disconnect button.
  - Credential entry handled via a separate popup/dialog.

## Top Priority

1. Robust Login Result Detection
   - Detect if, after login attempt, the browser is redirected to https://192.168.1.9/userSense and then back to the login page.
   - On the login page, check for:
     - "Authentication Failed for user:{username}"
     - "User is already logged in with same ip ..."
   - Treat these as failed login or already-logged-in (not a new success).
   - Detect successful login by checking if redirected to https://www.simulanis.com/ (driver.current_url).

2. Internet Connectivity Check
   - Before attempting login, check if the system has internet access (e.g., by reaching https://www.simulanis.com/ or https://google.com with a timeout).
   - If not connected, show a notification and do not attempt login.

3. Smarter Retry Logic (Optional)
   - If login fails due to no internet, do not retry immediately.
   - If login fails due to authentication, prompt the user to check credentials.

---

(Other lower-priority or backlog items can be added below as needed.)

## Notes
- The application is designed to automate the login process for Simulanis Solutions employees
- Current focus is on improving reliability and user experience
- Security features need to be prioritized before wide deployment
- Build v1.0.2 includes system tray functionality and notifications
- Build location standardized to C:\Users\Admin\Desktop\Auto_Login_Build 