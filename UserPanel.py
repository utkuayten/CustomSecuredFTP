from ftplib import FTP
import tkinter as tk
from tkinter import messagebox, filedialog


class UserPanelApp:
    def __init__(self, root, ftp):
        self.root = root
        self.ftp = ftp
        self.root.title("Main Panel")
        self.root.geometry("1000x500")
        self.root.resizable(False, False)

        # Frame for splitting the window
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for file list
        left_frame = tk.Frame(main_frame, width=500, bg="lightgrey")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="File List", font=("Arial", 14)).pack(pady=10)

        self.file_listbox = tk.Listbox(left_frame, width=50, height=20)
        self.file_listbox.pack(pady=10)

        self.refresh_file_list()

        tk.Button(left_frame, text="Upload File", command=self.upload_file).pack(pady=5)
        tk.Button(left_frame, text="Download File", command=self.download_file).pack(pady=5)

        # Right frame for directory navigation
        right_frame = tk.Frame(main_frame, width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="Directory Navigator", font=("Arial", 14)).pack(pady=10)

        self.current_dir_label = tk.Label(right_frame, text="Current Directory: ", wraplength=400)
        self.current_dir_label.pack(pady=5)

        self.directory_listbox = tk.Listbox(right_frame, width=50, height=20)
        self.directory_listbox.pack(pady=10)

        tk.Button(right_frame, text="Change Directory", command=self.change_directory).pack(pady=5)
        self.refresh_directory_view()

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            files = self.ftp.nlst()  # Retrieve the list of files in the current directory
            for file in files:
                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve file list: {e}")

    def refresh_directory_view(self):
        self.directory_listbox.delete(0, tk.END)
        try:
            current_dir = self.ftp.pwd()
            self.current_dir_label.config(text=f"Current Directory: {current_dir}")

            dirs = self.ftp.nlst()  # Retrieve the list of items in the current directory
            for item in dirs:
                self.directory_listbox.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve directory list: {e}")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    file_name = file_path.split('/')[-1]
                    self.ftp.storbinary(f"STOR {file_name}", file)
                    messagebox.showinfo("Upload Success", f"File '{file_name}' uploaded successfully!")
                    self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Upload Failed", f"Failed to upload file: {e}")

    def download_file(self):
        selected_item = self.file_listbox.curselection()
        if selected_item:
            file_name = self.file_listbox.get(selected_item[0])
            save_path = filedialog.asksaveasfilename(initialfile=file_name)
            if save_path:
                try:
                    with open(save_path, 'wb') as file:
                        self.ftp.retrbinary(f"RETR {file_name}", file.write)
                        messagebox.showinfo("Download Success", f"File '{file_name}' downloaded successfully!")
                except Exception as e:
                    messagebox.showerror("Download Failed", f"Failed to download file: {e}")
        else:
            messagebox.showwarning("Selection Error", "Please select a file to download.")

    def change_directory(self):
        selected_item = self.directory_listbox.curselection()
        if selected_item:
            dir_name = self.directory_listbox.get(selected_item[0])
            try:
                self.ftp.cwd(dir_name)
                self.refresh_file_list()
                self.refresh_directory_view()
            except Exception as e:
                messagebox.showerror("Change Directory Failed", f"Failed to change directory: {e}")