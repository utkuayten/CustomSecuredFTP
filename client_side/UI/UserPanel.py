from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup


class UserPanelApp(BoxLayout):
    def __init__(self, ftp, **kwargs):
        super().__init__(orientation="horizontal", spacing=10, padding=10, **kwargs)
        self.ftp = ftp
        self.selected_files = []
        self.selected_directories = []

        # Left layout for file list
        left_layout = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        left_layout.add_widget(Label(text="File List", font_size=20))

        # Scrollable container for the file list
        self.file_list_container = ScrollView(size_hint=(1, 1))
        self.file_list_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.file_list_layout.bind(minimum_height=self.file_list_layout.setter("height"))
        self.file_list_container.add_widget(self.file_list_layout)
        left_layout.add_widget(self.file_list_container)

        upload_btn = Button(text="Upload File", size_hint_y=None, height=50)
        upload_btn.bind(on_press=self.upload_file)
        left_layout.add_widget(upload_btn)

        download_btn = Button(text="Download Selected Files", size_hint_y=None, height=50)
        download_btn.bind(on_press=self.download_selected_files)
        left_layout.add_widget(download_btn)

        self.add_widget(left_layout)

        # Right layout for directory navigation
        right_layout = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        right_layout.add_widget(Label(text="Directory Navigator", font_size=20))

        self.current_dir_label = Label(text="Current Directory: ")
        right_layout.add_widget(self.current_dir_label)

        # Scrollable container for the directory list
        self.directory_list_container = ScrollView(size_hint=(1, 1))
        self.directory_list_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.directory_list_layout.bind(minimum_height=self.directory_list_layout.setter("height"))
        self.directory_list_container.add_widget(self.directory_list_layout)
        right_layout.add_widget(self.directory_list_container)

        change_dir_btn = Button(text="Change Directory", size_hint_y=None, height=50)
        change_dir_btn.bind(on_press=self.change_directory)
        right_layout.add_widget(change_dir_btn)

        self.add_widget(right_layout)

        self.refresh_file_list()
        self.refresh_directory_view()

    def refresh_file_list(self):
        """Populate the file list with checkboxes."""
        self.file_list_layout.clear_widgets()  # Clear the current list
        self.selected_files = []  # Reset selected files
        try:
            files = self.ftp.nlst()  # Retrieve the list of files
            for file in files:
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint_x=None, width=50)
                checkbox.bind(active=lambda checkbox, active, file=file: self.select_file(file, active))
                row.add_widget(checkbox)
                row.add_widget(Label(text=file, size_hint_x=1))
                self.file_list_layout.add_widget(row)
        except Exception as e:
            self.show_error(f"Failed to retrieve file list: {e}")

    def refresh_directory_view(self):
        """Populate the directory list with checkboxes."""
        self.directory_list_layout.clear_widgets()  # Clear the current list
        self.selected_directories = []  # Reset selected directories
        try:
            current_dir = self.ftp.pwd()
            self.current_dir_label.text = f"Current Directory: {current_dir}"

            dirs = self.ftp.nlst()  # Retrieve the list of directories
            for dir_name in dirs:
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint_x=None, width=50)
                checkbox.bind(active=lambda checkbox, active, dir_name=dir_name: self.select_directory(dir_name, active))
                row.add_widget(checkbox)
                row.add_widget(Label(text=dir_name, size_hint_x=1))
                self.directory_list_layout.add_widget(row)
        except Exception as e:
            self.show_error(f"Failed to retrieve directory list: {e}")

    def select_file(self, file, active):
        """Handle file selection."""
        if active:
            self.selected_files.append(file)
        else:
            self.selected_files.remove(file)

    def select_directory(self, directory, active):
        """Handle directory selection."""
        if active:
            self.selected_directories.append(directory)
        else:
            self.selected_directories.remove(directory)

    def download_selected_files(self, instance):
        """Download the selected files."""
        if not self.selected_files:
            self.show_warning("No files selected for download!")
            return
        self.show_info(f"Downloading files: {', '.join(self.selected_files)}")

    def upload_file(self, instance):
        self.show_error("File upload not yet implemented.")

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





