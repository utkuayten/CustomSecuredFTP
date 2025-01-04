import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from UI.ModernControls import ModernButton
from kivy.uix.textinput import TextInput

class ModernCheckBox(CheckBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.3, 0.5, 0.8, 1)  # Blue checkbox

class FileListItem(BoxLayout):
    def __init__(self, file_name, on_select, is_even=False, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=10, **kwargs)
        
        # Set alternating background colors
        bg_color = (0.97, 0.97, 0.97, 1) if is_even else (1, 1, 1, 1)
        hover_color = (0.95, 0.95, 0.95, 1) if is_even else (0.98, 0.98, 0.98, 1)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Add hover effect
        self.normal_color = bg_color
        self.hover_color = hover_color
        self.bind(on_touch_down=self._on_touch)
        self.bind(on_touch_up=self._on_touch_up)
        
        checkbox = ModernCheckBox(size_hint_x=None, width=dp(40))
        checkbox.bind(active=lambda cb, value: on_select(file_name, value))
        
        label = Label(
            text=file_name,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_x=1,
            halign='left',
            valign='middle',
            text_size=(None, dp(40))
        )
        
        self.add_widget(checkbox)
        self.add_widget(label)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            with self.canvas.before:
                Color(*self.hover_color)
                self.rect = Rectangle(pos=self.pos, size=self.size)
    
    def _on_touch_up(self, instance, touch):
        with self.canvas.before:
            Color(*self.normal_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

class UserPanelApp(BoxLayout):
    def __init__(self, ftp, **kwargs):
        super().__init__(orientation="horizontal", spacing=20, padding=20, **kwargs)
        self.ftp = ftp
        self.selected_files = []

        # Set window size
        Window.size = (800, 600)
        
        # Background
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Main layout for file list
        main_layout = BoxLayout(orientation="vertical", spacing=10)
        
        # Title container with padding
        title_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(100),
            padding=[30, 20]  # [left/right, top/bottom] padding
        )
        
        # H1 style title
        title_label = Label(
            text="Files",
            font_size='32sp',  # Larger font size
            bold=True,         # Bold text
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(60),
            halign='left',
            valign='bottom'
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)))
        
        # Add a decorative underline
        with title_container.canvas.after:
            Color(0.3, 0.5, 0.8, 0.8)  # Blue line color
            Rectangle(
                pos=(dp(30), title_container.y + dp(20)),
                size=(dp(100), dp(2))  # Width of 100dp, height of 2dp
            )
        
        title_container.add_widget(title_label)
        main_layout.add_widget(title_container)

        # Scrollable container for the file list
        self.file_list_container = ScrollView(
            size_hint=(1, 1),
            bar_width=10,
            bar_color=(0.3, 0.5, 0.8, 0.8),  # Blue scrollbar
            bar_inactive_color=(0.3, 0.5, 0.8, 0.2),
            effect_cls='ScrollEffect'
        )
        self.file_list_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5,
            padding=5
        )
        self.file_list_layout.bind(minimum_height=self.file_list_layout.setter("height"))
        self.file_list_container.add_widget(self.file_list_layout)
        main_layout.add_widget(self.file_list_container)

        # Buttons container
        buttons_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=10)
        
        upload_btn = ModernButton(
            text="Upload File",
            size_hint_x=0.5,
            background_color=(0.3, 0.5, 0.8, 1)  # Blue
        )
        upload_btn.bind(on_press=self.upload_file)
        
        download_btn = ModernButton(
            text="Download Selected",
            size_hint_x=0.5,
            background_color=(0.3, 0.5, 0.8, 1)  # Blue
        )
        download_btn.bind(on_press=self.download_selected_files)
        
        # Refresh button
        refresh_btn = ModernButton(
            text="Refresh",
            size_hint_x=0.33,  # Genişlik oranını diğer butonlara eşitledik
            background_color=(0.3, 0.5, 0.8, 1)  # Blue
        )
        refresh_btn.bind(on_press=lambda instance: self.refresh_file_list())  # refresh_file_list fonksiyonunu bağladık
        
        # Add buttons to the layout
        buttons_layout.add_widget(upload_btn)
        buttons_layout.add_widget(download_btn)
        buttons_layout.add_widget(refresh_btn)  # Refresh butonunu ekledik
        main_layout.add_widget(buttons_layout)

        self.add_widget(main_layout)
        self.refresh_file_list()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def refresh_file_list(self):
        """Populate the file list with checkboxes."""
        self.file_list_layout.clear_widgets()
        self.selected_files = []
        try:
            files = self.ftp.nlst()
            for index, file in enumerate(files):
                self.file_list_layout.add_widget(
                    FileListItem(file, self.select_file, is_even=(index % 2 == 0))
                )
        except Exception as e:
            self.show_error(f"Failed to retrieve file list: {e}")

    def select_file(self, file, active):
        """Handle file selection."""
        if active:
            self.selected_files.append(file)
        else:
            self.selected_files.remove(file)

    def download_selected_files(self, instance):
        """Download the selected files."""
        if not self.selected_files:
            self.show_warning("No files selected for download!")
            return

        # Create a popup for selecting the save directory
        content = BoxLayout(orientation="vertical")
        file_chooser = FileChooserListView(path="/", filters=["*"], dirselect=True)  # Enable directory selection
        content.add_widget(file_chooser)

        buttons = BoxLayout(size_hint_y=None, height=50)
        download_button = Button(text="Download", size_hint_x=0.5)
        cancel_button = Button(text="Cancel", size_hint_x=0.5)
        buttons.add_widget(download_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)

        popup = Popup(title="Select Save Directory", content=content, size_hint=(0.9, 0.9))

        def on_download(instance):
            selected_dir = file_chooser.path  # Get the selected directory
            if selected_dir:
                try:
                    for file_name in self.selected_files:
                        save_path = f"{selected_dir}/{file_name}"
                        with open(save_path, 'wb') as file:
                            self.ftp.retrbinary(f"RETR {file_name}", file.write)
                        self.show_info(f"File '{file_name}' downloaded to '{save_path}' successfully!")
                except Exception as e:
                    self.show_error(f"Failed to download file: {e}")
                finally:
                    popup.dismiss()
            else:
                self.show_warning("Please select a valid directory!")

        download_button.bind(on_press=on_download)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    import os
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup

    def upload_file(self, instance):
        """Open a file chooser popup for selecting and uploading a file."""
        # Create a popup with a file chooser
        content = BoxLayout(orientation="vertical")
        file_chooser = FileChooserListView()
        content.add_widget(file_chooser)

        buttons = BoxLayout(size_hint_y=None, height=50)
        upload_button = Button(text="Upload", size_hint_x=0.5)
        cancel_button = Button(text="Cancel", size_hint_x=0.5)
        buttons.add_widget(upload_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)

        popup = Popup(title="Select a file to upload", content=content, size_hint=(0.9, 0.9))

        def on_upload(instance):
            selected_file = file_chooser.selection
            if selected_file:
                try:
                    # Get the selected file path
                    file_path = selected_file[0]
                    file_name = os.path.basename(file_path)

                    # Open the file in binary mode and upload
                    with open(file_path, 'rb') as file:
                        self.ftp.storbinary(f"STOR {file_name}", file)

                    # Notify the user and refresh the file list
                    self.show_info(f"File '{file_name}' uploaded successfully!")
                    self.refresh_file_list()
                except Exception as e:
                    self.show_error(f"Failed to upload file: {e}")
                finally:
                    popup.dismiss()
            else:
                self.show_warning("No file selected!")

        # Bind the buttons to their respective functions
        upload_button.bind(on_press=on_upload)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def change_directory(self, instance):
        self.show_error("Directory change not yet implemented.")

    def show_error(self, message):
        popup = Popup(title="Error", content=Label(text=message), size_hint=(0.8, 0.8))
        popup.open()

    def show_info(self, message):
        popup = Popup(title="Info", content=Label(text=message), size_hint=(0.8, 0.8))
        popup.open()

    def show_warning(self, message):
        popup = Popup(title="Warning", content=Label(text=message), size_hint=(0.8, 0.8))
        popup.open()
