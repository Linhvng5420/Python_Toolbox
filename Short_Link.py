# Import các thư viện cần thiết
import requests
import tkinter as tk
from tkinter import messagebox
import pyperclip  # Thư viện hỗ trợ clipboard

# Hàm rút gọn URL sử dụng TinyURL API và tự động sao chép vào clipboard
def shorten_url():
    long_url = entry.get()  # Lấy URL từ ô nhập liệu
    if not long_url.strip():
        messagebox.showwarning("Warning", "Please enter a URL!")
        status_label.config(text="Please enter a URL!", fg="red")
        return
    
    try:
        # Gửi yêu cầu đến TinyURL API
        response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        if response.status_code == 200:
            short_url = response.text  # URL đã rút gọn
            entry_result.delete(0, tk.END)  # Xóa nội dung cũ
            entry_result.insert(0, short_url)  # Hiển thị kết quả
            pyperclip.copy(short_url)  # Tự động sao chép vào clipboard
            status_label.config(text="URL shortened and copied to clipboard!", fg="green")
        else:
            # messagebox.showerror("Error", "Unable to shorten URL. Please try again.")
            entry_result.delete(0, tk.END)
            status_label.config(text="Unable to shorten URL. Please try again.", fg="red")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text=f"Error: {str(e)}", fg="red")

# Hàm dán link từ clipboard vào ô nhập liệu và tự động rút gọn
def paste_from_clipboard():
    clipboard_content = pyperclip.paste()
    entry.delete(0, tk.END)  # Xóa nội dung cũ
    entry.insert(0, clipboard_content)  # Dán nội dung từ clipboard
    shorten_url()  # Tự động rút gọn URL sau khi dán

# Hàm sao chép link đã rút gọn vào clipboard
def copy_to_clipboard():
    short_url = entry_result.get()  # Lấy nội dung từ ô kết quả
    if short_url.strip():
        pyperclip.copy(short_url)

# Hàm xóa nội dung ô nhập liệu
def clear_entry():
    entry.delete(0, tk.END)
    entry_result.delete(0, tk.END)
    status_label.config(text="")

# Tạo giao diện chính
root = tk.Tk()
root.title("URL Shortener")
root.geometry("800x350")
root.resizable(False, False)
root.configure(bg="#f0f0f0")  # Màu nền chính

# Tiêu đề
label_title = tk.Label(root, text="Enter URL to shorten:", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
label_title.pack(pady=10)

# Ô nhập liệu
entry = tk.Entry(root, width=100, font=("Arial", 10), bg="#ffffff", fg="#333333", bd=2, relief="groove")
entry.pack(pady=5)

# Nút dán link từ clipboard và nút xóa
frame_buttons = tk.Frame(root, bg="#f0f0f0")
frame_buttons.pack(pady=5)

btn_clear = tk.Button(frame_buttons, text="Clear", command=clear_entry, font=("Arial", 10), bg="#f44336", fg="#ffffff", bd=2, relief="raised")
btn_clear.pack(side=tk.LEFT, padx=5)

btn_paste = tk.Button(frame_buttons, text="Paste", command=paste_from_clipboard, font=("Arial", 10), bg="#4CAF50", fg="#ffffff", bd=2, relief="raised")
btn_paste.pack(side=tk.LEFT, padx=5)

# Nút rút gọn
btn_shorten = tk.Button(root, text="Shorten", command=shorten_url, font=("Arial", 10), bg="#2196F3", fg="#ffffff", bd=2, relief="raised")
btn_shorten.pack(pady=10)

# Ô hiển thị kết quả
label_result = tk.Label(root, text="Shortened URL:", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
label_result.pack(pady=5)

entry_result = tk.Entry(root, width=50, font=("Arial", 10), bg="#ffffff", fg="#333333", bd=2, relief="groove")
entry_result.pack(pady=5)

# Label hiển thị trạng thái
status_label = tk.Label(root, text="", font=("Arial", 10), bg="#f0f0f0", fg="#333333")
status_label.pack(pady=5)

# Nút sao chép link đã rút gọn
btn_copy = tk.Button(root, text="Copy", command=copy_to_clipboard, font=("Arial", 10), bg="#FF9800", fg="#ffffff", bd=2, relief="raised")
btn_copy.pack(pady=10)

# Tác Giả và Version
frame_footer = tk.Frame(root, bg="#f0f0f0")
frame_footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

label_author = tk.Label(frame_footer, text="Author: NGVLinh5420", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
label_author.pack(side=tk.LEFT, padx=10)

label_version = tk.Label(frame_footer, text="Version 1.5", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
label_version.pack(side=tk.RIGHT, padx=10)

# Khởi động giao diện
root.mainloop()
