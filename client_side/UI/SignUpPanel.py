from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App
from ftplib import FTP
import os
from client_side.UI.Hasher import Hasher


class SignUpPanel(BoxLayout):
    def __init__(self, ftp, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=20, **kwargs)
        self.ftp = ftp

        # Username field
        self.add_widget(Label(text="Username:"))
        self.username_entry = TextInput(multiline=False)
        self.add_widget(self.username_entry)

        # Password field
        self.add_widget(Label(text="Password:"))
        self.password_entry = TextInput(password=True, multiline=False)
        self.add_widget(self.password_entry)

        # Confirm password field
        self.add_widget(Label(text="Confirm Password:"))
        self.confirm_password_entry = TextInput(password=True, multiline=False)
        self.add_widget(self.confirm_password_entry)

        # Sign up button
        sign_up_button = Button(text="Sign Up")
        sign_up_button.bind(on_press=self.sign_up)
        self.add_widget(sign_up_button)

    def sign_up(self, instance):
        """Handles user registration by hashing the password and sending it to the server."""
        username = self.username_entry.text.strip()
        password = self.password_entry.text
        confirm_password = self.confirm_password_entry.text

        if not username or not password:
            self.show_popup("Input Error", "Username and password are required!")
            return

        if len(password) < 6:
            self.show_popup("Input Error", "Password must be at least 6 characters long!")
            return

        if password != confirm_password:
            self.show_popup("Password Mismatch", "Passwords do not match!")
            return

        # Generate a salt and hash the password
        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)

        print(f"Generated Salt: {salt}")
        print(f"Hashed Password: {hashed_password}")

        # Send the REGISTER command to the server
        try:
            response = self.ftp.sendcmd(f"REGISTER {username} {hashed_password}")
            print(f"Server Response: {response}")
            self.show_popup("Sign Up", f"Server response: {response}")
        except Exception as e:
            print(f"Sign Up Error: {e}")
            self.show_popup("Sign Up Failed", f"Error: {e}")

    def show_popup(self, title, message):
        """Displays a popup message."""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()


class SignUpApp(App):
    def __init__(self, ftp, **kwargs):
        super().__init__(**kwargs)
        self.ftp = ftp

    def build(self):
        return SignUpPanel(ftp=self.ftp)


# Main application logic
if __name__ == "__main__":
    # FTP server connection
    FTP_HOST = "16.170.206.200"  # Replace with your server's IP
    FTP_PORT = 2121  # Replace with your server's FTP port

    ftp = FTP()
    try:
        ftp.connect(FTP_HOST, FTP_PORT)
        print(f"Connected to FTP server at {FTP_HOST}:{FTP_PORT}")
    except Exception as e:
        print(f"Error connecting to FTP server: {e}")
        exit(1)

    SignUpApp(ftp).run()