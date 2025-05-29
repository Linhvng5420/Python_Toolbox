import os
import shutil
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog

history = []  # Lưu lịch sử di chuyển file để hoàn tác

def split_files_by_date(directory, files_per_folder=30):
    """ Chia file theo ngày (cũ -> mới), mỗi thư mục chứa `files_per_folder` file. """
    global history
    history.clear()  # Reset lịch sử trước khi bắt đầu

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))  # Sắp xếp theo ngày sửa đổi

    folder_index = 1
    count = 0
    folder_path = os.path.join(directory, str(folder_index))
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        src = os.path.join(directory, file)
        dst = os.path.join(folder_path, file)
        shutil.move(src, dst)
        history.append((dst, src))  # Lưu lịch sử di chuyển

        count += 1
        if count >= files_per_folder:
            folder_index += 1
            count = 0
            folder_path = os.path.join(directory, str(folder_index))
            os.makedirs(folder_path, exist_ok=True)

    status_label.config(text="✅ Hoàn thành! Các file đã được chia.")
    undo_btn.config(state="normal")  # Bật nút hoàn tác
    print("✅ Hoàn thành! Các file đã được chia vào thư mục.")

def undo_last_action():
    """ Hoàn tác lần chia file gần nhất """
    global history
    if not history:
        status_label.config(text="⚠️ Không có gì để hoàn tác!")
        return
    
    for dst, src in reversed(history):  # Di chuyển file về vị trí cũ
        shutil.move(dst, src)

    history.clear()
    status_label.config(text="🔄 Đã hoàn tác! Tất cả file đã trở về thư mục gốc.")
    undo_btn.config(state="disabled")  # Tắt nút hoàn tác
    print("🔄 Hoàn tác thành công!")

def select_folder():
    """ Hộp thoại chọn thư mục """
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        status_label.config(text=f"📂 Đã chọn thư mục: {folder_selected}")
        split_files_by_date(folder_selected)

def drop(event):
    """ Xử lý khi kéo thả thư mục """
    folder_path = event.data.strip().replace("{", "").replace("}", "")
    status_label.config(text=f"📂 Đã nhận thư mục: {folder_path}")
    split_files_by_date(folder_path)

# Tạo giao diện kéo thả
root = TkinterDnD.Tk()
root.title("Chia File Theo Ngày")
root.geometry("400x300")

label = tk.Label(root, text="Kéo thư mục vào đây hoặc bấm Chọn thư mục", font=("Arial", 12))
label.pack(pady=10)

drop_area = tk.Label(root, text="📂 Kéo thả thư mục vào đây", bg="lightgray", fg="black", font=("Arial", 12), width=40, height=5)
drop_area.pack(pady=10)
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", drop)

btn = tk.Button(root, text="Chọn thư mục", command=select_folder, font=("Arial", 12))
btn.pack(pady=5)

undo_btn = tk.Button(root, text="Hoàn tác", command=undo_last_action, font=("Arial", 12), state="disabled")
undo_btn.pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 10), fg="blue")
status_label.pack(pady=5)

root.mainloop()
