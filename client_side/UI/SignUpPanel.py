from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App

import os

from UI.Hasher import Hasher

from UI.encryption import RSACipher

USER_DB = os.path.join(os.path.dirname(__file__), "users.json")


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


        # Add remaining space at the bottom
        self.add_widget(BoxLayout())

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size



    def sign_up(self, instance):
        username = self.username_entry.text
        password = self.password_entry.text
        confirm_password = self.confirm_password_entry.text

        if not username or not password:
            self.show_popup("Input Error", "Username and password are required!")
            return

        if password != confirm_password:
            self.show_popup("Password Mismatch", "Passwords do not match.")
            return

        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)

        try:
            self.ftp.sendcmd(f"REGISTER {username} {hashed_password}")
            self.show_popup("Sign Up", "Sign up successful!")

        except Exception as e:
            self.show_popup("Sign Up Failed", f"Error: {e}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()


class SignUpApp(App):
    def __init__(self, ftp, **kwargs):
        super().__init__(**kwargs)
        self.ftp = ftp

    def build(self):
        return SignUpPanel(ftp=self.ftp)


# Replace this section with your FTP initialization logic
if __name__ == "__main__":
    from ftplib import FTP

    ftp = FTP()
    ftp.connect("16.170.206.200", 2121)  # Replace with your FTP server details
    SignUpApp(ftp).run()
