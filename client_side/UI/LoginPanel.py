from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from client_side.UI.Hasher import Hasher
from client_side.UI.SignUpPanel import SignUpPanel
from client_side.UI.UserPanel import UserPanelApp


class LoginPanel(BoxLayout):
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

        # Sign up button
        sign_up_button = Button(text="Sign Up")
        sign_up_button.bind(on_press=self.sign_up)
        self.add_widget(sign_up_button)

        # Login button
        login_button = Button(text="Login")
        login_button.bind(on_press=self.login)
        self.add_widget(login_button)

    def sign_up(self, instance):
        SignUpPanel(self, self.ftp)

    def login(self, instance):
        username = self.username_entry.text
        password = self.password_entry.text

        if not username or not password:
            self.show_popup("Input Error", "Username and password are required!")
            return

        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)
        print(f"Hashed Password (Login): {hashed_password}")

        try:
            self.ftp.login(username, hashed_password)
            self.show_popup("Login", "Login successful!")

            # Replace the current LoginPanel with the UserPanelApp
            self.clear_widgets()
            user_panel = UserPanelApp(ftp=self.ftp)  # Pass the FTP instance correctly
            self.add_widget(user_panel)
        except Exception as e:
            self.show_popup("Login Failed", f"Error: {e}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()


class LoginApp(App):
    def __init__(self, ftp, **kwargs):
        super().__init__(**kwargs)
        self.ftp = ftp

    def build(self):
        return LoginPanel(ftp=self.ftp)