
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from client_side.UI.Hasher import Hasher
from client_side.UI.SignUpPanel import SignUpPanel
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

        # Sign Up butonu
        sign_up_button = Button(text="Sign Up")
        sign_up_button.bind(on_press=self.go_to_signup)
        self.add_widget(sign_up_button)

    def login(self, instance):
        username = self.username_entry.text
        password = self.password_entry.text

        if not username or not password:
            self.show_popup("Input Error", "Username and password are required!")
            return

        # Şifreyi hashle
        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)
        print(f"Hashed Password: {hashed_password}")  # Debug

        # Hashlenmiş şifreyi public key ile şifrele
        try:
            public_key_path = os.path.join(os.path.dirname(__file__), "/Users/berketuncer/Downloads/CustomSecuredFTP/keys/public_key.pem")
            with open(public_key_path, "rb") as f:
                public_key_pem = f.read()

            # Public key ile hashlenmiş şifreyi şifrele
            encrypted_password = RSACipher.encrypt_key(public_key_pem, hashed_password.encode())
            print(f"Encrypted Password (Hex): {encrypted_password.hex()}")  # Debug
        except FileNotFoundError:
            self.show_popup("Error", "Public key file not found.")
            return
        except Exception as e:
            self.show_popup("Error", f"Encryption failed: {e}")
            return

        # Şifrelenmiş hash'i sunucuya gönder
        try:
            response = self.ftp.sendcmd(f"LOGIN {username} {encrypted_password.hex()}")
            print(f"Server Response: {response}")
            self.show_popup("Login", f"Server response: {response}")
        except Exception as e:
            print(f"Login Error: {e}")
            self.show_popup("Login Failed", f"Error: {e}")

    def go_to_signup(self, instance):
        """Sign Up butonuna tıklanınca kayıt sayfasına yönlendirme yap."""
        app = App.get_running_app()
        app.root.clear_widgets()  # Mevcut pencereyi temizle
        app.root.add_widget(SignUpPanel(ftp=self.ftp))  # Yeni pencereyi ekle

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()