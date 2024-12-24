import os
import json
from datetime import datetime
from natsort import natsorted
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox
import re

# Hàm đổi tên
def rename_files():
    folder_path = folder_path_entry.get()
    if not os.path.isdir(folder_path):
        messagebox.showerror("Lỗi", "Đường dẫn không hợp lệ.")
        return

    rename_log = {}
    new_name_base = new_name_entry.get().strip()
    if not new_name_base:
        messagebox.showerror("Lỗi", "Tên mới không được để trống.")
        return

    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
    files = natsorted(files)

    used_names = set()
    for index, file_name in enumerate(files, start=1):
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

    messagebox.showinfo("Thành công", "Đã đổi tên tệp thành công.")

# Hàm khôi phục tên
def undo_rename():
    folder_path = folder_path_entry.get()
    if not os.path.isdir(folder_path):
        messagebox.showerror("Lỗi", "Đường dẫn không hợp lệ.")
        return

    log_path = os.path.join(folder_path, "rename_log.json")
    if not os.path.exists(log_path):
        messagebox.showerror("Lỗi", "Không tìm thấy tệp log để khôi phục.")
        return

    with open(log_path, "r") as log_file:
        rename_log = json.load(log_file)

    for new_name, original_name in rename_log.items():
        new_path = os.path.join(folder_path, new_name)
        original_path = os.path.join(folder_path, original_name)
        if os.path.exists(new_path):
            os.rename(new_path, original_path)

    os.remove(log_path)
    messagebox.showinfo("Thành công", "Khôi phục tên tệp thành công.")

# Hàm xóa file log
def delete_log():
    folder_path = folder_path_entry.get()
    log_path = os.path.join(folder_path, "rename_log.json")
    if os.path.exists(log_path):
        os.remove(log_path)
        messagebox.showinfo("Thành công", "Đã xóa file log.")
    else:
        messagebox.showwarning("Thông báo", "Không tìm thấy file log để xóa.")

# Hàm dán đường dẫn từ clipboard
def paste_path():
    folder_path = app.clipboard_get().strip()  # Lấy đường dẫn từ clipboard
    folder_path = re.sub(r'[\"\'“”]', '', folder_path)  # Loại bỏ dấu nháy đôi hoặc đặc biệt

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
app.title("Batch File Renamer")

# Nhập đường dẫn thư mục
tk.Label(app, text="Đường dẫn thư mục:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
folder_path_entry = tk.Entry(app, width=50)
folder_path_entry.grid(row=0, column=1, padx=5, pady=5)

# Kích hoạt kéo thả
folder_path_entry.drop_target_register(DND_FILES)
folder_path_entry.dnd_bind("<<Drop>>", drop_event)

# Nút chọn thư mục
def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)

browse_button = tk.Button(app, text="Duyệt", command=browse_folder)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Nút dán đường dẫn
paste_button = tk.Button(app, text="Dán", command=paste_path)
paste_button.grid(row=0, column=3, padx=5, pady=5)

# Nhập tên mới
tk.Label(app, text="Tên mới:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
new_name_entry = tk.Entry(app, width=50)
new_name_entry.grid(row=1, column=1, padx=5, pady=5)

# Nút đổi tên
rename_button = tk.Button(app, text="Rename", command=rename_files, bg="lightgreen", font=("Helvetica", 10, "bold"))
rename_button.grid(row=2, column=1, pady=5)

# Nút khôi phục tên
undo_button = tk.Button(app, text="UndoRename", command=undo_rename, bg="lightblue", font=("Helvetica", 10, "bold"))
undo_button.grid(row=3, column=1, pady=5)

# Nút xóa file log
delete_log_button = tk.Button(app, text="DeLog", command=delete_log, bg="red", fg="white", font=("Helvetica", 10, "bold"))
delete_log_button.grid(row=4, column=1, pady=5)

# Chạy ứng dụng
app.mainloop()
