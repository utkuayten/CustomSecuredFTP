from ftplib import FTP
import tkinter as tk
from tkinter import messagebox, filedialog

from LoginPanel import LoginPanel

if __name__ == "__main__":
    # FTP connection details
    FTP_HOST = "127.0.0.1"  # Server address (use '127.0.0.1' for localhost)

    FTP_PORT = 2121  # Port number

    root = tk.Tk()
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    app = LoginPanel(root, ftp)
    root.mainloop()
