from ftplib import FTP
import tkinter as tk
from tkinter import messagebox, filedialog


class InitClient:
    def __init__(self, root):
        self.root = root
        self.root.title("User Login Panel")
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
                for widget in self.root.winfo_children():
                    widget.destroy()
                UserPanelApp(self.root, ftp)

            except Exception as e:
                messagebox.showerror("Login Failed", f"Failed to connect: {e}")
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

class UserPanelApp:
    def __init__(self, root, ftp):
        self.root = root
        self.ftp = ftp
        self.root.title("Main Panel")
        self.root.geometry("400x300")

        tk.Label(self.root, text="File List", font=("Arial", 14)).pack(pady=10)

        self.file_listbox = tk.Listbox(self.root, width=50, height=15)
        self.file_listbox.pack(pady=10)

        self.refresh_file_list()

        tk.Button(self.root, text="Upload File", command=self.upload_file).pack(pady=5)
        tk.Button(self.root, text="Close", command=self.close_app).pack(pady=10)

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            files = self.ftp.nlst()  # Retrieve the list of files in the current directory
            for file in files:
                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve file list: {e}")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    file_name = file_path.split('/')[-1]
                    self.ftp.storbinary(f"STOR {file_name}", file)
                    messagebox.showinfo("Upload Success", f"File '{file_name}' uploaded successfully!")
                    self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Upload Failed", f"Failed to upload file: {e}")

    def close_app(self):
        self.ftp.quit()
        self.root.destroy()

if __name__ == "__main__":
    # FTP connection details
    FTP_HOST = "127.0.0.1"  # Server address (use '127.0.0.1' for localhost)
    FTP_PORT = 2121  # Port number

    root = tk.Tk()
    app = InitClient(root)
    root.mainloop()
