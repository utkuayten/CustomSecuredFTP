import base64
import os
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from UI.Hasher import Hasher
from UI.SignUpPanel import SignUpPanel
from UI.encryption import RSACipher
from UI.UserPanel import UserPanelApp  # UserPanelApp import edildi
import os

from UI.Hasher import Hasher
from UI.encryption import RSACipher
import os

from UI.ModernControls import ModernButton

from UI.SignUpPanel import SignUpPanel

from UI.ModernControls import ModernTextInput

from UI.UserPanel import UserPanelApp


def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
    popup.open()


def hybrid_encrypt(server_public_key_bytes, data_to_encrypt):
    print('HERE')
    # Step 1: Generate a random AES key

    server_public_key = load_pem_public_key(server_public_key_bytes)

    aes_key = os.urandom(32)  # 256-bit AES key
    iv = os.urandom(16)  # Initialization vector for AES

    # Step 2: Encrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    aes_encrypted_data = encryptor.update(data_to_encrypt) + encryptor.finalize()

    # Step 3: Encrypt the AES key using the server's RSA public key
    rsa_encrypted_aes_key = server_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Step 4: Return the payload
    return {
        "rsa_encrypted_aes_key": rsa_encrypted_aes_key,
        "aes_encrypted_data": aes_encrypted_data,
        "iv": iv,
    }


class LoginPanel(BoxLayout):
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
            text="Welcome Back",
            font_size='24sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title_label)

        # Subtitle
        subtitle_label = Label(
            text="Please login to continue",
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

        self.username_entry = ModernTextInput(hint_text="Enter your username")
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
            hint_text="Enter your password"
        )
        self.add_widget(self.password_entry)

        # Add some spacing
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Login button
        login_button = ModernButton(
            text="Login",
            background_color=(0.3, 0.5, 0.8, 1)  # Blue
        )
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
        sign_up_modal = ModalView(size_hint=(0.8, 0.8))

        sign_up_panel = SignUpPanel(ftp=self.ftp)

        close_button = ModernButton(text="Close", size_hint=(1, 0.1))
        close_button.bind(on_press=sign_up_modal.dismiss)
        sign_up_panel.add_widget(close_button)

        sign_up_modal.add_widget(sign_up_panel)
        sign_up_modal.open()

    def login(self, instance):
        username = self.username_entry.text
        password = self.password_entry.text

        if not username or not password:
            show_popup("Input Error", "Username and password are required!")
            return

        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)

        print(f"Hashed Password: {hashed_password}")  # Debugging

        try:
            # Load the server's public key
            server_public_key_path = os.path.join(os.path.dirname(__file__), "../keys/public_key_server.pem")
            with open(server_public_key_path, "rb") as f:
                server_public_key = f.read()

            # Encrypt the hashed password
            encrypted_password = RSACipher.encrypt_key(server_public_key, hashed_password.encode())
        except FileNotFoundError:
            show_popup("Error", "Public key file not found.")
            print(os.path.dirname(__file__))
            return
        except Exception as e:
            show_popup("Error", f"Encryption failed: {e}")
            return

        print(f"Encrypted Password: {encrypted_password.hex()}")  # Debugging

        try:
            response = self.ftp.sendcmd(f"LOGIN {username} {encrypted_password.hex()}")
            print(f"Server Response: {response}")
            if response.startswith("230"):  # 230 Login successful
                private_key_pem, public_key_pem = RSACipher.generate_keys()
                self.switch_to_user_panel()
                keys_dir = "keys"
                os.makedirs(keys_dir, exist_ok=True)  # Ensure the directory exists

                # Save the private key
                with open(os.path.join(keys_dir, "private_key.pem"), "wb") as private_file:
                    private_file.write(private_key_pem)

                # Save the public key
                with open(os.path.join(keys_dir, "public_key.pem"), "wb") as public_file:
                    public_file.write(public_key_pem)

                # Base64-encode the public key
                public_key_encoded = base64.b64encode(public_key_pem)
                print(f"Size of Encoded Public Key: {len(public_key_encoded)} bytes")

                # Perform hybrid encryption
                hybrid_payload = hybrid_encrypt(server_public_key, public_key_encoded)

                # Prepare the payload for transmission
                rsa_encrypted_aes_key_hex = hybrid_payload["rsa_encrypted_aes_key"].hex()
                aes_encrypted_data_hex = hybrid_payload["aes_encrypted_data"].hex()
                iv_hex = hybrid_payload["iv"].hex()

                # Send the encrypted payload to the server
                try:
                    response = self.ftp.sendcmd(
                        f"UPDATE_PUBLIC_KEY {username} {rsa_encrypted_aes_key_hex} {aes_encrypted_data_hex} {iv_hex}"
                    )
                    print(f"Server response: {response}")

                except Exception as e:
                    print(f"Error updating public key: {e}")

            else:
                self.show_popup("Login Failed", f"Server response: {response}")



        except Exception as e:
            print(f"Error during login or key update: {e}")

    def switch_to_user_panel(self):
        """UserPanelApp'e geçiş yapar."""
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(UserPanelApp(ftp=self.ftp))
