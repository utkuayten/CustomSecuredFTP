from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

import os

from UI.Hasher import Hasher
from UI.ModernControls import ModernTextInput, ModernButton

USER_DB = os.path.join(os.path.dirname(__file__), "users.json")


class SignUpPanel(BoxLayout):
    def __init__(self, ftp, **kwargs):
        super().__init__(orientation="vertical", spacing=20, padding=30, **kwargs)
        self.ftp = ftp

        # Set window size and background
        Window.size = (400, 600)
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)  # Almost white background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Add some spacing at the top
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Title
        title_label = Label(
            text="Create Account",
            font_size='24sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title_label)

        # Subtitle
        subtitle_label = Label(
            text="Please fill in your details",
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(subtitle_label)

        # Add some spacing
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Username field
        username_label = Label(
            text="Username",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        username_label.bind(size=lambda *x: setattr(username_label, 'text_size', (username_label.width, None)))
        self.add_widget(username_label)
        
        self.username_entry = ModernTextInput(hint_text="Choose a username")
        self.add_widget(self.username_entry)

        # Password field
        password_label = Label(
            text="Password",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        password_label.bind(size=lambda *x: setattr(password_label, 'text_size', (password_label.width, None)))
        self.add_widget(password_label)
        
        self.password_entry = ModernTextInput(
            password=True,
            hint_text="Create a password"
        )
        self.add_widget(self.password_entry)

        # Confirm password field
        confirm_password_label = Label(
            text="Confirm Password",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        confirm_password_label.bind(size=lambda *x: setattr(confirm_password_label, 'text_size', (confirm_password_label.width, None)))
        self.add_widget(confirm_password_label)
        
        self.confirm_password_entry = ModernTextInput(
            password=True,
            hint_text="Confirm your password"
        )
        self.add_widget(self.confirm_password_entry)

        # Add some spacing
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Sign up button
        sign_up_button = ModernButton(
            text="Create Account",
            background_color=(0.3, 0.5, 0.8, 1)  # Blue
        )
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
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(
            text=message,
            font_size='16sp',
            color=(0.2, 0.2, 0.2, 1)
        ))
        close_button = ModernButton(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(close_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            title_color=(0.2, 0.2, 0.2, 1),
            title_size='18sp',
            background='atlas://data/images/defaulttheme/button_pressed'
        )
        close_button.bind(on_press=popup.dismiss)
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
