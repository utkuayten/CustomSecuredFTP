from ftplib import FTP
import tkinter as tk
from tkinter import messagebox

class UserPanelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Panel")
        self.root.geometry("300x200")

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Clear", command=self.clear_fields).pack(pady=5)

    def login(self):
        ftp_user = self.username_entry.get()
        ftp_pass = self.password_entry.get()

        if ftp_user and ftp_pass:
            try:
                ftp = FTP()
                ftp.connect(FTP_HOST, FTP_PORT)
                ftp.login(ftp_user, ftp_pass)
                print(f"Connected to FTP server at {FTP_HOST}:{FTP_PORT} as {ftp_user}")

                messagebox.showinfo("Login Success", f"Welcome, {ftp_user}!")

                # Redirecting to the main panel after login
                self.redirect_panel(ftp)
            except Exception as e:
                messagebox.showerror("Login Failed", f"Failed to connect: {e}")
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def redirect_panel(self, ftp):
        self.root.withdraw()  # Hide the login window
        redirect_window = tk.Toplevel()
        redirect_window.title("Main Panel")
        redirect_window.geometry("400x300")

        tk.Label(redirect_window, text="File List", font=("Arial", 14)).pack(pady=10)

        file_listbox = tk.Listbox(redirect_window, width=50, height=15)
        file_listbox.pack(pady=10)

        try:
            files = ftp.nlst()  # Retrieve the list of files in the current directory
            for file in files:
                file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve file list: {e}")

        tk.Button(redirect_window, text="Close", command=lambda: [ftp.quit(), redirect_window.destroy(), self.root.destroy()]).pack(pady=10)

    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

if __name__ == "__main__":
    # FTP connection details
    FTP_HOST = "127.0.0.1"  # Server address (use '127.0.0.1' for localhost)
    FTP_PORT = 2121  # Port number

    root = tk.Tk()
    app = UserPanelApp(root)
    root.mainloop()
