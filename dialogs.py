import tkinter as tk
import customtkinter as ctk

class CredentialDialog(ctk.CTkToplevel):
    def __init__(self, parent, username="", remember_me=False, auto_login=False):
        super().__init__(parent)
        
        # Dialog result
        self.result = False
        self.username = username
        self.password = ""
        
        # Store parent for reference
        self.parent = parent
        
        # Configure dialog window
        self.title("Login Credentials")
        self.geometry("350x320")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create UI elements
        self.create_widgets(username, remember_me, auto_login)
        
        # Center dialog relative to parent
        self.center_dialog()
        
    def create_widgets(self, username, remember_me, auto_login):
        """Create the dialog widgets"""
        # Main frame with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title label
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Enter Login Credentials",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Username entry
        username_label = ctk.CTkLabel(main_frame, text="Username:")
        username_label.pack(anchor="w", pady=(5, 0))
        
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Username",
            width=300,
            height=35
        )
        if username:
            self.username_entry.insert(0, username)
        self.username_entry.pack(pady=(5, 10), fill="x")
        
        # Password entry
        password_label = ctk.CTkLabel(main_frame, text="Password:")
        password_label.pack(anchor="w", pady=(5, 0))
        
        password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        password_frame.pack(pady=(5, 10), fill="x")
        password_frame.grid_columnconfigure(0, weight=1)
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Password",
            show="•",
            width=270,
            height=35
        )
        self.password_entry.grid(row=0, column=0, sticky="ew")
        
        # Eye/Show password button
        self.show_password_btn = ctk.CTkButton(
            password_frame,
            text="👁️",
            width=30,
            height=35,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
            command=self.toggle_password_visibility
        )
        self.show_password_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Options frame (checkboxes)
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(pady=10, fill="x")
        
        # Remember Me checkbox
        self.remember_me_var = tk.BooleanVar(value=remember_me)
        remember_me_cb = ctk.CTkCheckBox(
            options_frame,
            text="Remember credentials",
            variable=self.remember_me_var,
            onvalue=True,
            offvalue=False
        )
        remember_me_cb.pack(anchor="w", pady=5)
        
        # Auto Login checkbox
        self.auto_login_var = tk.BooleanVar(value=auto_login)
        auto_login_cb = ctk.CTkCheckBox(
            options_frame,
            text="Auto-login on startup",
            variable=self.auto_login_var,
            onvalue=True,
            offvalue=False
        )
        auto_login_cb.pack(anchor="w", pady=5)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(15, 0), fill="x")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color=("gray85", "gray40"),
            hover_color=("gray75", "gray30"),
            command=self.on_cancel
        )
        cancel_button.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        # Login button
        login_button = ctk.CTkButton(
            button_frame,
            text="Login",
            command=self.on_submit
        )
        login_button.pack(side="right", padx=(5, 0), fill="x", expand=True)
        
        # Set initial focus and bind Enter key
        self.username_entry.focus_set()
        self.bind("<Return>", lambda event: self.on_submit())
        
    def center_dialog(self):
        """Center the dialog relative to the parent window"""
        self.update_idletasks()
        
        # Get parent geometry
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate position
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        # Ensure dialog is visible on screen
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        self.geometry(f"+{x}+{y}")
        
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        current_show = self.password_entry.cget("show")
        if current_show == "":
            self.password_entry.configure(show="•")
            self.show_password_btn.configure(text="👁️")
        else:
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text="🔒")
            
    def on_submit(self):
        """Handle submit button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username:
            # Show error for missing username
            self.shake_widget(self.username_entry)
            return
            
        if not password:
            # Show error for missing password
            self.shake_widget(self.password_entry)
            return
        
        # Set result values
        self.result = True
        self.username = username
        self.password = password
        
        # Close dialog
        self.grab_release()
        self.destroy()
        
    def on_cancel(self):
        """Handle cancel button click"""
        self.result = False
        self.grab_release()
        self.destroy()
        
    def shake_widget(self, widget):
        """Visual shake effect for form validation"""
        orig_x = widget.winfo_x()
        
        # Create shake effect with oscillating position
        def _shake(count, distance):
            if count > 0:
                # Move widget
                x = distance * (-1)**count
                widget.place(x=orig_x + x, rely=0, anchor="w")
                # Schedule next shake
                widget.after(50, _shake, count - 1, distance)
            else:
                # Reset position after shake complete
                widget.place(x=orig_x, rely=0, anchor="w")
        
        # Start shake animation - 5 oscillations with 5px amplitude
        _shake(5, 5) 