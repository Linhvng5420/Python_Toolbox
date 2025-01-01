import pytesseract
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Thiết lập đường dẫn đến tesseract (nếu cần)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Hàm dịch ảnh
def translate_image(image_path, output_path):
    # Mở ảnh
    image = Image.open(image_path)
    
    # Nhận diện văn bản trong ảnh
    text = pytesseract.image_to_string(image, lang='eng')  # Sử dụng tiếng Nhật để nhận diện
    
    # Dịch từng dòng văn bản
    translated_text = ""
    for line in text.split('\n'):
        # Dịch chỉ những dòng có văn bản tiếng Nhật
        if line.strip():
            translated_line = GoogleTranslator(source='en', target='vi').translate(line)
            translated_text += translated_line + '\n'
    
    # Tạo ảnh mới với văn bản dịch
    new_image = image.copy()  # Tạo bản sao của ảnh gốc để vẽ lên
    
    # Vẽ lại văn bản dịch lên ảnh
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.load_default()  # Bạn có thể thay đổi font nếu cần
    
    # Cài đặt vị trí và màu chữ
    x, y = 10, 10
    line_height = 20  # Chiều cao dòng văn bản
    
    for line in translated_text.split('\n'):
        draw.text((x, y), line, fill="black", font=font)
        y += line_height  # Di chuyển xuống dưới cho dòng tiếp theo
    
    # Lưu lại ảnh mới
    new_image.save(output_path)
    print(f"Image saved to {output_path}")
    messagebox.showinfo("Thông báo", f"Ảnh đã được lưu tại {output_path}")

# Hàm mở hộp thoại chọn ảnh
def select_image():
    # Mở hộp thoại chọn ảnh
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        output_image = "translated_image.jpg"  # Đường dẫn tới ảnh đã dịch
        translate_image(file_path, output_image)

# Tạo giao diện người dùng
root = tk.Tk()
root.title("Dịch Văn Bản Trong Ảnh")

# Tạo nút "Chọn ảnh" và kết nối với hàm select_image
btn_select_image = tk.Button(root, text="Chọn ảnh để dịch", command=select_image)
btn_select_image.pack(pady=20)

# Hiển thị giao diện
root.mainloop()
