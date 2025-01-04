from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.95, 0.95, 0.95, 1)  # Light gray background
        self.foreground_color = (0.2, 0.2, 0.2, 1)     # Dark text
        self.cursor_color = (0.3, 0.5, 0.8, 1)         # Blue cursor
        self.font_size = '16sp'
        self.padding = [20, 10]                        # Add some padding
        self.size_hint_y = None
        self.height = dp(40)                           # Fixed height
        self.multiline = False

class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.3, 0.5, 0.8, 1)     # Modern blue
        self.background_normal = ''                     # Remove default background
        self.size_hint_y = None
        self.height = dp(40)                           # Fixed height
        self.font_size = '16sp' 