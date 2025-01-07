from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from client_side.UI.Hasher import Hasher
from client_side.UI.encryption import RSACipher
import os

class LoginPanel(BoxLayout):
    def __init__(self, ftp, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=20, **kwargs)
        self.ftp = ftp

        # Kullanıcı adı alanı
        self.add_widget(Label(text="Username:"))
        self.username_entry = TextInput(multiline=False)
        self.add_widget(self.username_entry)

        # Şifre alanı
        self.add_widget(Label(text="Password:"))
        self.password_entry = TextInput(password=True, multiline=False)
        self.add_widget(self.password_entry)

        # Giriş butonu
        login_button = Button(text="Login")
        login_button.bind(on_press=self.login)
        self.add_widget(login_button)

        # Sign up button
        sign_up_button = ModernButton(
            text="Create New Account",
            background_color=(0.9, 0.9, 0.9, 1),  # Light gray
            color=(0.3, 0.3, 0.3, 1)  # Dark text
        )
        sign_up_button.bind(on_press=self.sign_up)
        self.add_widget(sign_up_button)

        # Add remaining space at the bottom
        self.add_widget(BoxLayout())

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def sign_up(self, instance):
        """Open the SignUpPanel in a modal view."""
        # Create a modal view
        sign_up_modal = ModalView(size_hint=(0.8, 0.8))

        # Create the sign-up panel and pass the FTP instance
        sign_up_panel = SignUpPanel(ftp=self.ftp)

        # Add a close button to the SignUpPanel
        close_button = ModernButton(text="Close", size_hint=(1, 0.1))
        close_button.bind(on_press=sign_up_modal.dismiss)  # Close the modal on button press
        sign_up_panel.add_widget(close_button)

        # Add the sign-up panel to the modal view
        sign_up_modal.add_widget(sign_up_panel)

        # Open the modal view
        sign_up_modal.open()

    def login(self, instance):
        username = self.username_entry.text
        password = self.password_entry.text

        if not username or not password:
            self.show_popup("Input Error", "Username and password are required!")
            return

        # Şifreyi hashle
        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)

        print(f"Hashed Password: {hashed_password}")  # Debug için

        # Public key ile hashlenmiş şifreyi şifrele
        try:
            public_key_path = os.path.join(os.path.dirname(__file__), "/Users/yigitkoyuncu/Downloads/CustomSecuredFTP/keys/public_key.pem")
            with open(public_key_path, "rb") as f:
                public_key_pem = f.read()

            # Hashlenmiş şifreyi public key ile şifrele
            encrypted_password = RSACipher.encrypt_key(public_key_pem, hashed_password.encode())
        except FileNotFoundError:
            self.show_popup("Error", "Public key file not found.")
            return
        except Exception as e:
            self.show_popup("Error", f"Encryption failed: {e}")
            return

        print(f"Encrypted Password: {encrypted_password.hex()}")  # Debug için

        # Şifrelenmiş hash'i sunucuya gönder
        try:
            response = self.ftp.sendcmd(f"LOGIN {username} {encrypted_password.hex()}")
            self.show_popup("Login", f"Server response: {response}")
        except Exception as e:
            self.show_popup("Login Failed", f"Error: {e}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()