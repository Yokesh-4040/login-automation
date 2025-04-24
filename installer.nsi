; Simulanis Auto Login Installer Script
!include "MUI2.nsh"

; General
Name "Simulanis Auto Login"
OutFile "installer\Simulanis_Auto_Login_Setup_v1.0.1.exe"
InstallDir "$PROGRAMFILES\Simulanis Auto Login"
InstallDirRegKey HKLM "Software\Simulanis Auto Login" "Install_Dir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "README.md"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Files to install
  File "dist\Simulanis Auto Login v1.0.1\Simulanis Auto Login.exe"
  File "dist\Simulanis Auto Login v1.0.1\headless_config.json"
  File "dist\Simulanis Auto Login v1.0.1\README.md"
  File "dist\Simulanis Auto Login v1.0.1\Start Simulanis Login.bat"
  File "dist\Simulanis Auto Login v1.0.1\Start Simulanis Login (GUI).bat"
  
  ; Create Icons and Logos directories
  CreateDirectory "$INSTDIR\Icons"
  CreateDirectory "$INSTDIR\Logos"
  
  ; Copy Icons and Logos
  SetOutPath "$INSTDIR\Icons"
  File /r "Icons\*.*"
  SetOutPath "$INSTDIR\Logos"
  File /r "Logos\*.*"
  SetOutPath "$INSTDIR"
  
  ; Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\Simulanis Auto Login"
  CreateShortcut "$SMPROGRAMS\Simulanis Auto Login\Simulanis Auto Login.lnk" "$INSTDIR\Simulanis Auto Login.exe"
  CreateShortcut "$SMPROGRAMS\Simulanis Auto Login\Simulanis Auto Login (Headless).lnk" "$INSTDIR\Simulanis Auto Login.exe" "--headless"
  CreateShortcut "$SMPROGRAMS\Simulanis Auto Login\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Desktop shortcuts (optional)
  CreateShortcut "$DESKTOP\Simulanis Auto Login.lnk" "$INSTDIR\Simulanis Auto Login.exe"
  CreateShortcut "$DESKTOP\Simulanis Auto Login (Headless).lnk" "$INSTDIR\Simulanis Auto Login.exe" "--headless"
  
  ; Add to startup (headless mode)
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "Simulanis Auto Login" '"$INSTDIR\Simulanis Auto Login.exe" --headless'
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Write registry keys for uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Simulanis Auto Login" "DisplayName" "Simulanis Auto Login"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Simulanis Auto Login" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Simulanis Auto Login" "Publisher" "Simulanis Solutions Pvt. Ltd."
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Simulanis Auto Login" "DisplayVersion" "1.0.1"
  
  ; Run the application after installation (optional)
  MessageBox MB_YESNO "Would you like to launch Simulanis Auto Login now?" IDNO NoLaunch
    Exec '"$INSTDIR\Simulanis Auto Login.exe"'
  NoLaunch:
SectionEnd

Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\Simulanis Auto Login.exe"
  Delete "$INSTDIR\headless_config.json"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Start Simulanis Login.bat"
  Delete "$INSTDIR\Start Simulanis Login (GUI).bat"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove directories
  RMDir /r "$INSTDIR\Icons"
  RMDir /r "$INSTDIR\Logos"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Simulanis Auto Login\*.*"
  RMDir "$SMPROGRAMS\Simulanis Auto Login"
  Delete "$DESKTOP\Simulanis Auto Login.lnk"
  Delete "$DESKTOP\Simulanis Auto Login (Headless).lnk"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Simulanis Auto Login"
  DeleteRegValue HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "Simulanis Auto Login"
  DeleteRegKey HKLM "Software\Simulanis Auto Login"
SectionEnd 