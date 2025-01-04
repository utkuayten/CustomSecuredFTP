from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.metrics import dp

from UI.Hasher import Hasher
from UI.SignUpPanel import SignUpPanel
from UI.UserPanel import UserPanelApp
from UI.ModernControls import ModernTextInput, ModernButton

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
            self.show_popup("Input Error", "Username and password are required!", "error")
            return

        salt = Hasher.generate_salt(username)
        hashed_password = Hasher.hash_password(password, salt)
        print(f"Hashed Password (Login): {hashed_password}")

        try:
            self.ftp.login(username, hashed_password)
            # Directly switch to UserPanel without showing popup
            self.clear_widgets()
            user_panel = UserPanelApp(ftp=self.ftp)
            self.add_widget(user_panel)
        except Exception as e:
            self.show_popup("Login Failed", f"Error: {e}", "error")

    def show_popup(self, title, message, popup_type="info", size=(400, 200), auto_dismiss=False):
        # Define colors based on popup type
        colors = {
            "error": (0.8, 0.2, 0.2, 1),     # Red
            "success": (0.2, 0.7, 0.2, 1),   # Green
            "info": (0.3, 0.5, 0.8, 1),      # Blue
            "warning": (0.8, 0.6, 0.2, 1)    # Orange
        }
        color = colors.get(popup_type, colors["info"])
        
        # Create content layout with background
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )
        
        # Add background to content
        with content.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda *args: setattr(content.canvas.before.children[-1], 'pos', content.pos),
                    size=lambda *args: setattr(content.canvas.before.children[-1], 'size', content.size))
        
        # Message label
        message_label = Label(
            text=message,
            font_size='16sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        content.add_widget(message_label)
        
        # Close button
        close_button = ModernButton(
            text='Close',
            size_hint_y=None,
            height=dp(40),
            background_color=color
        )
        content.add_widget(close_button)
        
        # Create and configure popup with custom background
        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=size,
            title_color=(0.2, 0.2, 0.2, 1),
            title_size='18sp',
            title_align='center',
            auto_dismiss=auto_dismiss,
            separator_color=color,  # Match the color theme
            background_color=(0.98, 0.98, 0.98, 1)  # Light background
        )
        
        # Bind close button
        close_button.bind(on_press=popup.dismiss)
        
        popup.open()
        return popup


class LoginApp(App):
    def __init__(self, ftp, **kwargs):
        super().__init__(**kwargs)
        self.ftp = ftp

    def build(self):
        return LoginPanel(ftp=self.ftp)