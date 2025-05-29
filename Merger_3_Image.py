import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from pathlib import Path

def merge_images_horizontally(image_paths):
    images = [Image.open(path).convert("RGBA") for path in image_paths]  # Giữ kênh alpha nếu có
    min_height = min(img.height for img in images)
    resized = [
        img.resize((int(img.width * min_height / img.height), min_height), Image.LANCZOS)
        for img in images
    ]
    total_width = sum(img.width for img in resized)
    result = Image.new('RGBA', (total_width, min_height))  # Dùng RGBA để giữ chất lượng

    x = 0
    for img in resized:
        result.paste(img, (x, 0))
        x += img.width

    # 💾 Lưu thành PNG trong thư mục Hình ảnh
    pictures_dir = Path.home() / "Pictures"
    output_path = pictures_dir / "merged_output.png"
    result.save(output_path, format='PNG')  # Xuất PNG chất lượng cao không nén mất dữ liệu
    return output_path

def select_images():
    file_paths = filedialog.askopenfilenames(
        title="Chọn tối đa 3 ảnh",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if len(file_paths) == 0:
        return
    if len(file_paths) > 3:
        messagebox.showerror("Lỗi", "Chỉ được chọn tối đa 3 ảnh.")
        return
    try:
        output = merge_images_horizontally(file_paths)
        messagebox.showinfo("Thành công", f"Đã lưu ảnh ghép tại: {output}")
    except Exception as e:
        messagebox.showerror("Lỗi khi ghép ảnh", str(e))

# Giao diện
root = tk.Tk()
root.title("Ghép 3 ảnh theo chiều ngang")
root.geometry("400x200")

label = tk.Label(root, text="Bấm nút bên dưới để chọn ảnh", font=("Arial", 12))
label.pack(pady=20)

btn = tk.Button(root, text="Chọn ảnh", font=("Arial", 12), command=select_images)
btn.pack()

root.mainloop()
