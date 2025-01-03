import tkinter as tk
from tkinter import messagebox
import bcrypt
import json
import os

USER_DB = os.path.join(os.path.dirname(__file__), "users.json")


class SignUpPanel:
    def __init__(self, root, ftp):
        self.root = root
        self.ftp = ftp
        self.sign_up_window = tk.Toplevel(self.root)
        self.sign_up_window.title("Sign Up")
        self.sign_up_window.geometry("300x250")

        tk.Label(self.sign_up_window, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.sign_up_window)
        self.username_entry.pack(pady=5)

        tk.Label(self.sign_up_window, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.sign_up_window, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self.sign_up_window, text="Confirm Password:").pack(pady=5)
        self.confirm_password_entry = tk.Entry(self.sign_up_window, show="*")
        self.confirm_password_entry.pack(pady=5)

        tk.Button(self.sign_up_window, text="Sign Up", command=self.sign_up).pack(pady=10)

    def load_users(self):
        try:
            with open(USER_DB, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(self, users):
        with open(USER_DB, "w") as f:
            json.dump(users, f)

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        users = self.load_users()

        if username in users:
            messagebox.showerror("Error", "Username already exists.")
            return


        # Salt and Hash.

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        users[username] = {
            "password": hashed_password,
            "home_dir": f"C:/Users/Utku Ayten/Desktop/ftp_root/{username}"
        }

        self.save_users(users)
        messagebox.showinfo("Success", "User signed up successfully!")
        self.sign_up_window.destroy()
