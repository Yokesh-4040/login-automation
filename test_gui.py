from auto_login_gui import ModernLoginApp

def launch_gui():
    """Launch the GUI for manual testing"""
    print("Launching Simulanis Login GUI for manual testing...")
    print("You can now:")
    print("1. Check the window size and positioning")
    print("2. Test the input fields and buttons")
    print("3. Verify the branding elements")
    print("4. Test the credentials view toggle")
    print("Close the window to exit.")
    
    app = ModernLoginApp()
    app.mainloop()

if __name__ == "__main__":
    launch_gui() 