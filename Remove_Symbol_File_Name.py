# Remove Symbol File Name

import os
import re
import random
from tkinter import Tk, Label, Button, filedialog, StringVar, Frame
from tkinterdnd2 import TkinterDnD, DND_FILES

# Hàm xử lý đổi tên file (giữ nguyên phần mở rộng)
def format_filename(filename):
    # Tách tên file và phần mở rộng
    name, extension = os.path.splitext(filename)
    # Thay thế các ký tự không phải a-z, A-Z, 0-9, () bằng khoảng trắng
    cleaned_name = re.sub(r'[^a-zA-Z0-9()]+', ' ', name)
    # Xóa khoảng trắng thừa và viết hoa chữ cái đầu từ
    formatted_name = ' '.join(word.capitalize() for word in cleaned_name.split())
    # Gắn lại phần mở rộng
    return f"{formatted_name}{extension}"


# Hàm xử lý sự kiện chọn file
def select_file():
    file_path = filedialog.askopenfilename(title="Select file")
    if file_path:
        file_name.set(os.path.basename(file_path))
        new_name.set(format_filename(os.path.basename(file_path)))
        selected_file.set(file_path)
        set_status("File selected successfully!", "green")


# Hàm xử lý khi nhấn nút Paste cho file hoặc thư mục
def paste_file():
    try:
        file_path = app.clipboard_get()
        if os.path.isfile(file_path):  # Nếu là file
            file_name.set(os.path.basename(file_path))
            new_name.set(format_filename(os.path.basename(file_path)))
            selected_file.set(file_path)
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
            set_status(f"File pasted successfully! {random_numbers}", "green")
        elif os.path.isdir(file_path):  # Nếu là thư mục
            directory_path = file_path
            files = os.listdir(directory_path)
            for file in files:
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):  # Chỉ đổi tên các file trong thư mục
                    new_file_name = format_filename(file)
                    new_file_path = os.path.join(directory_path, new_file_name)
                    os.rename(file_path, new_file_path)
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
            set_status(f"Renamed all files in the directory successfully! {random_numbers}", "green")
        else:
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
            set_status(f"Clipboard path is not a valid file or directory! {random_numbers}", "red")
    except Exception as e:
        set_status(f"Error: {e}", "red")


# Hàm xử lý khi nhấn nút chọn thư mục và đổi tên tất cả file trong thư mục
def select_directory():
    directory_path = filedialog.askdirectory(title="Select directory")
    if directory_path:
        try:
            files = os.listdir(directory_path)
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
            for file in files:
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):  # Chỉ đổi tên các file, không phải thư mục
                    new_file_name = format_filename(file)
                    new_file_path = os.path.join(directory_path, new_file_name)
                    os.rename(file_path, new_file_path)
            set_status(f"Renamed all files in the directory successfully! {random_numbers}", "green")
        except Exception as e:
            set_status(f"Error: {e} - {random_numbers}", "red")


# Hàm đổi tên file
def rename_file():
    if selected_file.get():
        directory = os.path.dirname(selected_file.get())
        old_name = os.path.basename(selected_file.get())
        new_file_path = os.path.join(directory, new_name.get())
        try:
            os.rename(selected_file.get(), new_file_path)
            set_status("Renamed successfully!", "green")
        except Exception as e:
            set_status(f"Error: {e}", "red")
    else:
        set_status("Please select a file first!", "red")


# Hàm cập nhật trạng thái
def set_status(message, color):
    status_label.config(text=message, fg=color)

# Hàm xử lý khi kéo và thả file (hoặc thư mục)
def on_drop(event):
    dropped_path = event.data
    # Loại bỏ dấu { ở đầu và } ở cuối
    dropped_path = dropped_path.strip('{}')
    
    print(f"Dropped path: {dropped_path}")  # In đường dẫn ra để kiểm tra

    if os.path.isdir(dropped_path):  # Nếu thả một thư mục
        try:
            files = os.listdir(dropped_path)
            for file in files:
                file_path = os.path.join(dropped_path, file)
                if os.path.isfile(file_path):  # Chỉ đổi tên các file, không phải thư mục
                    new_file_name = format_filename(file)
                    new_file_path = os.path.join(dropped_path, new_file_name)
                    os.rename(file_path, new_file_path)
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
            set_status(f"Renamed all files in the directory successfully! {random_numbers}", "green")
        except Exception as e:
            set_status(f"Error: {e}", "red")
    elif os.path.isfile(dropped_path):  # Nếu thả một file
        file_name.set(os.path.basename(dropped_path))
        new_name.set(format_filename(os.path.basename(dropped_path)))
        selected_file.set(dropped_path)
        random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Tạo 5 số ngẫu nhiên
        set_status(f"File dropped successfully! {random_numbers}", "green")
    else:
        set_status("Invalid path!", "red")

# Tạo ứng dụng giao diện
app = TkinterDnD.Tk()
app.title("Remove Symbol File Name")
app.geometry("500x450")
app.configure(bg="#f0f0f0")

# Biến lưu trữ tên file
file_name = StringVar()
new_name = StringVar()
selected_file = StringVar()

# Giao diện chính
frame = Frame(app, bg="#f0f0f0")
frame.pack(pady=20)

Label(frame, text="Remove Symbol In File Name", font=("Arial", 18, "bold"), bg="#f0f0f0").pack()

# Sử dụng frame phụ để chứa các nút "Kéo & Thả File" và "Paste"
button_frame = Frame(frame, bg="#f0f0f0")
button_frame.pack(pady=10)

Button(button_frame, text="Drag & Drop File or Select File", command=select_file, bg="#4CAF50", fg="white",
       font=("Arial", 12), padx=10, pady=5).pack(side="left", padx=10)

Button(button_frame, text="Paste", command=paste_file, bg="#FFC107", fg="black",
       font=("Arial", 12), padx=10, pady=5).pack(side="left", padx=10)

# Thêm một nút dán bên phải cho thư mục
Button(frame, text="Drag & Drop or Select Directory", command=select_directory, bg="#FF5722", fg="white",
       font=("Arial", 12), padx=10, pady=5).pack(pady=10)

Label(frame, text="Current file name:", font=("Arial", 12), bg="#f0f0f0").pack()
Label(frame, textvariable=file_name, font=("Arial", 10), bg="#f0f0f0", fg="#555").pack()

Label(frame, text="New file name:", font=("Arial", 12), bg="#f0f0f0").pack()
Label(frame, textvariable=new_name, font=("Arial", 10, "italic"), bg="#f0f0f0", fg="#555").pack()

Button(frame, text="Rename", command=rename_file, bg="#2196F3", fg="white", font=("Arial", 12), padx=10,
       pady=5).pack(pady=20)

status_label = Label(app, text="Status will be displayed here", font=("Arial", 10), bg="#f0f0f0")
status_label.pack()

# Thông tin tác giả và phiên bản
Label(app, text="Author: NGVLinh5420", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
Label(app, text="Version: 1.5", font=("Arial", 10), bg="#f0f0f0").pack(side="right", padx=5)

# Kích hoạt chức năng kéo và thả file hoặc thư mục
app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', on_drop)

# Chạy ứng dụng
app.mainloop()
