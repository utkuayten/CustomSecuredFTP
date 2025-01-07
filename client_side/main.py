from kivy.app import App
from client_side.UI.LoginPanel import LoginPanel
from ftplib import FTP
from client_side.UI.Hasher import Hasher
from client_side.UI.encryption import RSACipher
import os

# AWS Sunucu Bilgileri
FTP_HOST = "16.170.206.200"  # AWS sunucu IP adresi veya hostname
FTP_PORT = 2121  # AWS sunucunun FTP portu

    # Initialize FTP connection
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)  # Connect to the FTP server

    # Create and run the Kivy app
    class MainApp(App):
        def build(self):
            return LoginPanel(ftp=ftp)

if __name__ == "__main__":
    MainApp().run()