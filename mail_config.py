"""
Email Configuration Setup Tool
Helps configure SMTP settings for the resume screening system
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from dotenv import load_dotenv, set_key
import smtplib
from email.message import EmailMessage


class MailConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Configuration Setup")
        self.root.geometry("600x700")
        self.root.resizable(False, True)
        
        # Styling
        self.root.configure(bg="#f0f0f0")
        
        # Load existing .env if it exists
        self.env_file = Path(".env")
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Variables
        self.vars = {
            "SMTP_HOST": tk.StringVar(value=os.getenv("SMTP_HOST", "")),
            "SMTP_PORT": tk.StringVar(value=os.getenv("SMTP_PORT", "587")),
            "SMTP_USER": tk.StringVar(value=os.getenv("SMTP_USER", "")),
            "SMTP_PASS": tk.StringVar(value=os.getenv("SMTP_PASS", "")),
            "FROM_ADDRESS": tk.StringVar(value=os.getenv("FROM_ADDRESS", "")),
        }
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title = tk.Label(
            self.root,
            text="📧 Email Configuration Setup",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#1f2937"
        )
        title.pack(pady=15)
        
        # Info frame
        info_frame = tk.Frame(self.root, bg="#fef3c7", relief=tk.SUNKEN, bd=1)
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        info_text = tk.Label(
            info_frame,
            text="⚠️ Configure your SMTP email server to send selection emails.\n"
                 "Leave fields empty to skip email sending.",
            font=("Arial", 9),
            bg="#fef3c7",
            fg="#92400e",
            justify=tk.LEFT,
            wraplength=550
        )
        info_text.pack(padx=10, pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Form fields
        self._create_form_field(
            main_frame,
            "SMTP Host:",
            "SMTP_HOST",
            "e.g., smtp.gmail.com, smtp.office365.com"
        )
        
        self._create_form_field(
            main_frame,
            "SMTP Port:",
            "SMTP_PORT",
            "e.g., 587 (TLS) or 465 (SSL)"
        )
        
        self._create_form_field(
            main_frame,
            "SMTP Username/Email:",
            "SMTP_USER",
            "Your email address for authentication"
        )
        
        self._create_form_field(
            main_frame,
            "SMTP Password:",
            "SMTP_PASS",
            "Your email password or app password",
            show_password=True
        )
        
        self._create_form_field(
            main_frame,
            "From Address:",
            "FROM_ADDRESS",
            "Email address to send from (optional)"
        )
        
        # Test Connection Button
        test_button = tk.Button(
            main_frame,
            text="🧪 Test Email Connection",
            command=self._test_connection,
            font=("Arial", 11, "bold"),
            bg="#0891b2",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        test_button.pack(fill=tk.X, pady=15)
        
        # Common Providers Info
        providers_frame = tk.LabelFrame(
            main_frame,
            text="📌 Common Email Providers",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#1f2937",
            padx=10,
            pady=10
        )
        providers_frame.pack(fill=tk.X, pady=10)
        
        providers_text = (
            "Gmail: smtp.gmail.com:587 (use App Password, not regular password)\n"
            "Outlook: smtp-mail.outlook.com:587\n"
            "Office365: smtp.office365.com:587\n"
            "Yahoo: smtp.mail.yahoo.com:587\n"
            "Custom Server: Check with your email provider"
        )
        
        providers_label = tk.Label(
            providers_frame,
            text=providers_text,
            font=("Courier New", 8),
            bg="#f0f0f0",
            fg="#4b5563",
            justify=tk.LEFT
        )
        providers_label.pack(anchor=tk.W)
        
        # Save Button
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = tk.Button(
            button_frame,
            text="💾 Save Configuration",
            command=self._save_config,
            font=("Arial", 12, "bold"),
            bg="#16a34a",
            fg="white",
            padx=15,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            width=20
        )
        save_button.pack(fill=tk.X)
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.root.quit,
            font=("Arial", 10),
            bg="#6b7280",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1
        )
        cancel_button.pack(fill=tk.X, pady=(5, 0))
        
    def _create_form_field(self, parent, label_text, var_name, placeholder="", show_password=False):
        """Create a labeled input field"""
        field_frame = tk.Frame(parent, bg="#f0f0f0")
        field_frame.pack(fill=tk.X, pady=8)
        
        label = tk.Label(
            field_frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#1f2937",
            width=18,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT)
        
        entry_kwargs = {
            "font": ("Arial", 10),
            "bg": "white",
            "relief": tk.SUNKEN,
            "bd": 1,
            "textvariable": self.vars[var_name]
        }
        
        if show_password:
            entry_kwargs["show"] = "•"
        
        entry = tk.Entry(field_frame, **entry_kwargs)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        help_label = tk.Label(
            field_frame,
            text=placeholder,
            font=("Arial", 8),
            bg="#f0f0f0",
            fg="#9ca3af",
            anchor=tk.W
        )
        help_label.pack(fill=tk.X, padx=(18, 0))
        
    def _test_connection(self):
        """Test SMTP connection with current settings"""
        host = self.vars["SMTP_HOST"].get().strip()
        port = self.vars["SMTP_PORT"].get().strip()
        user = self.vars["SMTP_USER"].get().strip()
        password = self.vars["SMTP_PASS"].get().strip()
        
        if not all([host, port, user, password]):
            messagebox.showwarning("Incomplete Settings", "Please fill in all SMTP settings to test")
            return
        
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Invalid Port", "Port must be a number")
            return
        
        # Test connection
        try:
            with smtplib.SMTP(host, port) as smtp:
                smtp.starttls()
                smtp.login(user, password)
            messagebox.showinfo("✅ Success", "SMTP connection successful!\nYour email settings are correct.")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("❌ Authentication Error", "Username or password is incorrect")
        except smtplib.SMTPException as e:
            messagebox.showerror("❌ SMTP Error", f"SMTP Error: {str(e)}")
        except Exception as e:
            messagebox.showerror("❌ Connection Error", f"Error: {str(e)}")
            
    def _save_config(self):
        """Save configuration to .env file"""
        try:
            # Create .env if it doesn't exist
            if not self.env_file.exists():
                self.env_file.touch()
            
            # Save each variable
            for key, var in self.vars.items():
                value = var.get().strip()
                set_key(str(self.env_file), key, value)
            
            messagebox.showinfo("✅ Success", ".env file has been updated with your email configuration")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")


def main():
    root = tk.Tk()
    gui = MailConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
