import hashlib
import tkinter as tk
from tkinter import messagebox

from client_side.UI.UserPanel import UserPanelApp


class LoginPanel:
    def __init__(self, root, ftp):
        self.root = root
        self.ftp = ftp
        self.root.title("User Login Panel")
        self.root.geometry("300x250")

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Sign Up", command=self.sign_up).pack(pady=10)
        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)

    def hash_password(self, password):
        """Hash the password using SHA256."""
        hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hashed

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password are required!")
            return

        hashed_password = self.hash_password(password)
        print(f"Hashed Password (Sign Up): {hashed_password}")

        try:
            self.ftp.sendcmd(f"REGISTER {username} {hashed_password}")
            messagebox.showinfo("Sign Up", "Sign up successful!")
        except Exception as e:
            messagebox.showerror("Sign Up Failed", f"Error: {e}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password are required!")
            return

        hashed_password = self.hash_password(password)
        print(f"Hashed Password (Login): {hashed_password}")

        try:
            self.ftp.login(username, hashed_password)
            messagebox.showinfo("Login", "Login successful!")
            for widget in self.root.winfo_children():
                widget.destroy()
            UserPanelApp(self.root, self.ftp)
        except Exception as e:
            messagebox.showerror("Login Failed", f"Error: {e}")
