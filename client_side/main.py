from ftplib import FTP
from kivy.app import App
from UI.LoginPanel import LoginPanel

if __name__ == "__main__":
    # FTP connection details
    # FTP_HOST = "16.170.206.200"  # Server address (use '127.0.0.1' for localhost)
    FTP_HOST = "127.0.0.1"
    FTP_PORT = 2121  # Port number

    # Initialize FTP connection
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)  # Connect to the FTP server

    # Create and run the Kivy app
    class MainApp(App):
        def build(self):
            return LoginPanel(ftp=ftp)

    MainApp().run()
