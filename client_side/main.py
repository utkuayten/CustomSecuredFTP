from kivy.app import App
from UI.LoginPanel import LoginPanel
from ftplib import FTP
from UI.Hasher import Hasher
from UI.encryption import RSACipher
import os


# Create and run the Kivy app
class MainApp(App):
    def build(self):
        # FTP_HOST = "16.170.206.200"
        FTP_HOST = "127.0.0.1"
        FTP_PORT = 2121
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        return LoginPanel(ftp=ftp)


if __name__ == "__main__":
    MainApp().run()
