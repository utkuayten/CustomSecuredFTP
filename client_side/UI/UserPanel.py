import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
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

        self.current_dir_label = Label(text="Current Directory: Loading...")
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

        # Initialize file and directory views
        self.refresh_directory_view()
        self.refresh_file_list()

    def refresh_file_list(self):
        """Populate the file list with checkboxes."""
        self.file_list_layout.clear_widgets()  # Clear the current list
        self.selected_files = []  # Reset selected files
        try:
            if not self.ftp:
                raise Exception("FTP connection is not initialized.")

            # Check if the user is logged in
            if not self.ftp.pwd():
                raise Exception("User is not logged in.")

            files = self.ftp.nlst()  # Retrieve the list of files
            if not files:
                self.file_list_layout.add_widget(Label(text="No files found", size_hint_y=None, height=40))
                return

            for file in files:
                # Create a local variable inside the loop to bind to lambda
                file_name = file

                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint_x=None, width=50)
                checkbox.bind(active=lambda checkbox, active, file_name=file_name: self.select_file(file_name, active))
                row.add_widget(checkbox)
                row.add_widget(Label(text=file_name, size_hint_x=1))
                self.file_list_layout.add_widget(row)
        except Exception as e:
            self.show_error(f"Failed to retrieve file list: {e}")

    def refresh_directory_view(self):
        """Populate the directory list with checkboxes."""
        self.directory_list_layout.clear_widgets()  # Clear the current list
        self.selected_directories = []  # Reset selected directories
        try:
            if not self.ftp:
                raise Exception("FTP connection is not initialized.")

            # Check if the user is logged in
            current_dir = self.ftp.pwd()
            self.current_dir_label.text = f"Current Directory: {current_dir}"

            dirs = self.ftp.nlst()  # Retrieve the list of directories
            if not dirs:
                self.directory_list_layout.add_widget(Label(text="No directories found", size_hint_y=None, height=40))
                return

            for dir_name in dirs:
                # Create a local variable inside the loop to bind to lambda
                directory_name = dir_name

                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
                checkbox = CheckBox(size_hint_x=None, width=50)
                checkbox.bind(
                    active=lambda checkbox, active, directory_name=directory_name: self.select_directory(directory_name,active))
                row.add_widget(checkbox)
                row.add_widget(Label(text=directory_name, size_hint_x=1))
                self.directory_list_layout.add_widget(row)
        except Exception as e:
            self.show_error(f"Failed to retrieve directory list: {e}")

    def select_file(self, file, active):
        """Handle file selection."""
        if active:
            if file not in self.selected_files:
                self.selected_files.append(file)
        else:
            if file in self.selected_files:
                self.selected_files.remove(file)

    def select_directory(self, directory, active):
        """Handle directory selection."""
        if active:
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
        else:
            if directory in self.selected_directories:
                self.selected_directories.remove(directory)

    def download_selected_files(self, instance):
        """Download the selected files."""
        if not self.selected_files:
            self.show_warning("No files selected for download!")
            return
        try:
            for file in self.selected_files:
                with open(file, "wb") as f:
                    self.ftp.retrbinary(f"RETR {file}", f.write)
            self.show_info(f"Downloaded files: {', '.join(self.selected_files)}")
        except Exception as e:
            self.show_error(f"Failed to download files: {e}")

    def upload_file(self, instance):
        """Upload a file to the FTP server."""
        # File chooser popup
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        file_chooser = FileChooserListView(filters=["*.*"], path=os.getcwd())  # Show all files
        content.add_widget(file_chooser)

        # Add Upload and Cancel buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        upload_button = Button(text="Upload", size_hint_x=0.5)
        cancel_button = Button(text="Cancel", size_hint_x=0.5)
        button_layout.add_widget(upload_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        # Create the popup
        popup = Popup(title="Select a File to Upload", content=content, size_hint=(0.9, 0.9))
        popup.open()

        def upload_action(instance):
            """Handle the upload process."""
            try:
                selected_files = file_chooser.selection
                if not selected_files:
                    raise Exception("No file selected!")

                selected_file = selected_files[0]
                file_name = os.path.basename(selected_file)

                # Open the file and upload to the FTP server
                with open(selected_file, "rb") as file:
                    self.ftp.storbinary(f"STOR {file_name}", file)

                self.show_info(f"File '{file_name}' uploaded successfully.")
                popup.dismiss()
                self.refresh_file_list()  # Refresh file list after upload
            except Exception as e:
                self.show_error(f"Failed to upload file: {e}")
                popup.dismiss()

        def cancel_action(instance):
            """Handle the cancel action."""
            popup.dismiss()

        # Bind button actions
        upload_button.bind(on_press=upload_action)
        cancel_button.bind(on_press=cancel_action)

    def change_directory(self, instance):
        """Change the current directory."""
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