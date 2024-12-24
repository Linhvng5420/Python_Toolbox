import os
import json
from datetime import datetime
from natsort import natsorted
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog
import re

# Hàm hiển thị thông báo
def display_message(message, color):
    message_label.config(text=message, fg=color)

# Hàm đổi tên
def rename_files():
    folder_path = folder_path_entry.get()
    if not os.path.isdir(folder_path):
        display_message("Invalid directory path.", "red")
        return

    rename_log = {}
    new_name_base = new_name_entry.get().strip()
    if not new_name_base:
        display_message("New name cannot be empty.", "red")
        return

    try:
        start_count = int(start_count_entry.get().strip())
    except ValueError:
        display_message("Invalid start count.", "red")
        return

    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
    files = natsorted(files)

    used_names = set()
    for index, file_name in enumerate(files, start=start_count):
        file_path = os.path.join(folder_path, file_name)
        file_ext = os.path.splitext(file_name)[1]
        base_name = f"{new_name_base}-{index:02d}"
        new_name = f"{base_name}{file_ext}"

        counter = 1
        while new_name in used_names:
            new_name = f"{base_name}_{counter}{file_ext}"
            counter += 1

        used_names.add(new_name)
        new_path = os.path.join(folder_path, new_name)
        rename_log[new_name] = file_name
        os.rename(file_path, new_path)

    log_path = os.path.join(folder_path, "rename_log.json")
    with open(log_path, "w") as log_file:
        json.dump(rename_log, log_file, indent=4)

    display_message("Files renamed successfully.", "green")

# Hàm khôi phục tên
def undo_rename():
    folder_path = folder_path_entry.get()
    if not os.path.isdir(folder_path):
        display_message("Invalid directory path.", "red")
        return

    log_path = os.path.join(folder_path, "rename_log.json")
    if not os.path.exists(log_path):
        display_message("Log file not found.", "red")
        return

    with open(log_path, "r") as log_file:
        rename_log = json.load(log_file)

    for new_name, original_name in rename_log.items():
        new_path = os.path.join(folder_path, new_name)
        original_path = os.path.join(folder_path, original_name)
        if os.path.exists(new_path):
            os.rename(new_path, original_path)

    os.remove(log_path)
    display_message("File names restored successfully.", "green")

# Hàm xóa file log
def delete_log():
    folder_path = folder_path_entry.get()
    log_path = os.path.join(folder_path, "rename_log.json")
    if os.path.exists(log_path):
        os.remove(log_path)
        display_message("Log file deleted.", "green")
    else:
        display_message("Log file not found.", "red")

# Hàm dán đường dẫn từ clipboard
def paste_path():
    folder_path = app.clipboard_get().strip()  # Lấy đường dẫn từ clipboard
    folder_path = re.sub(r'["\'“”]', '', folder_path)  # Loại bỏ dấu nháy đôi hoặc đặc biệt

    if os.path.isfile(folder_path):  # Nếu là đường dẫn tệp
        folder_path = os.path.dirname(folder_path)  # Lấy đường dẫn thư mục
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)

# Hàm xử lý kéo thả
def drop_event(event):
    folder_path = event.data.strip()
    folder_path = folder_path.replace("{", "").replace("}", "")  # Loại bỏ ký tự { và }
    if os.path.isfile(folder_path):  # Nếu là tệp
        folder_path = os.path.dirname(folder_path)  # Lấy thư mục chứa tệp
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)

# Tạo giao diện Tkinter
app = TkinterDnD.Tk()
app.title("Rename All Files In Folder")

# Kích hoạt kéo thả cho toàn bộ app
app.drop_target_register(DND_FILES)
app.dnd_bind("<<Drop>>", drop_event)

# Tiêu đề ứng dụng
title_label = tk.Label(app, text="Rename AFIF", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=4, pady=10)

# Miêu tả ứng dụng
description_label = tk.Label(app, text="Copy files or drag and drop", font=("Helvetica", 12), fg="gray")
description_label.grid(row=1, column=0, columnspan=4, pady=5)

# Nhập đường dẫn thư mục
tk.Label(app, text="Directory Path:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
folder_path_entry = tk.Entry(app, width=50)
#folder_path_entry = tk.Text(app, width=38, height=2)
folder_path_entry.grid(row=2, column=1, padx=5, pady=5)

# Kích hoạt kéo thả
folder_path_entry.drop_target_register(DND_FILES)
folder_path_entry.dnd_bind("<<Drop>>", drop_event)

# Nút chọn thư mục
def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)

browse_button = tk.Button(app, text="Browse", command=browse_folder)
browse_button.grid(row=2, column=2, padx=5, pady=5)

# Nút dán đường dẫn
paste_button = tk.Button(app, text="Paste", command=paste_path)
paste_button.grid(row=2, column=3, padx=5, pady=5)

# Nhập tên mới
tk.Label(app, text="New Name:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
new_name_entry = tk.Entry(app, width=50)
new_name_entry.grid(row=3, column=1, padx=5, pady=5)

# Nhập số bắt đầu
tk.Label(app, text="Start Count:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
start_count_entry = tk.Entry(app, width=10)
start_count_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
start_count_entry.insert(0, "1")  # Default is 1

# Nút đổi tên
rename_button = tk.Button(app, text="Rename", command=rename_files, bg="lightgreen", font=("Helvetica", 10, "bold"))
rename_button.grid(row=5, column=1, pady=5)

# Nút khôi phục tên
undo_button = tk.Button(app, text="Undo Rename", command=undo_rename, bg="lightblue", font=("Helvetica", 10, "bold"))
undo_button.grid(row=6, column=1, pady=5)

# Nút xóa file log
delete_log_button = tk.Button(app, text="Delete Log", command=delete_log, bg="red", fg="white", font=("Helvetica", 10, "bold"))
delete_log_button.grid(row=7, column=1, pady=5)

# Thông báo trạng thái
message_label = tk.Label(app, text="", font=("Helvetica", 10))
message_label.grid(row=8, column=0, columnspan=4, pady=10)

# Thông tin tác giả và phiên bản
author_label = tk.Label(app, text="Author: NGVLinh5420", font=("Helvetica", 8), fg="black")
author_label.grid(row=9, column=0, columnspan=2, pady=5, sticky="w")

version_label = tk.Label(app, text="Version: 1.5", font=("Helvetica", 8), fg="black")
version_label.grid(row=9, column=2, columnspan=2, pady=5, sticky="e")

# Chạy ứng dụng
app.mainloop()

# To create an executable, run the following command in the terminal:
# pyinstaller --onefile --windowed Rename_AFIF.py
