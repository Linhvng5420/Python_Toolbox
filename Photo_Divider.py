# Divider Photo Divider App

import os
from tkinter import Tk, Label, Button, filedialog, Radiobutton, IntVar, Frame
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image

class ImageSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Divider App")

        # Đặt kích thước cửa sổ ứng dụng
        self.root.geometry("600x500")
        self.root.config(bg="#f0f0f0")

        # Khung chứa tất cả các phần tử
        main_frame = Frame(root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề ứng dụng
        self.title_label = Label(main_frame, text="Divider Photo Divider App", font=("Helvetica", 18), bg="#f0f0f0", pady=10)
        self.title_label.pack()

        # Hiển thị thông báo kéo thả ảnh
        self.label = Label(main_frame, text="Drag and drop an image or folder here.", font=("Arial", 12), width=50, height=5, bg="#f7f7f7", relief="solid", anchor="center")
        self.label.pack(pady=10)

        # Nút chọn ảnh
        self.upload_button = Button(main_frame, text="Select Image", command=self.upload_image, font=("Arial", 12), width=20, bg="#4CAF50", fg="white", relief="raised")
        self.upload_button.pack(pady=10)

        # Nút cắt ảnh
        self.cut_button = Button(main_frame, text="Divider Photo", command=self.split_image, font=("Arial", 12), width=20, bg="#f44336", fg="white", relief="raised", state="disabled")
        self.cut_button.pack(pady=10)

        # Đường dẫn ảnh hoặc thư mục
        self.path = None

        # Biến lưu trạng thái lựa chọn thứ tự cắt (1-2 hoặc 2-1)
        self.order_var = IntVar()
        self.order_var.set(1)  # Mặc định là "1-2"

        # Khung cho các nút radio chọn thứ tự cắt
        radio_frame = Frame(main_frame, bg="#f0f0f0")
        radio_frame.pack(pady=10)

        # Khung nhóm các nút radio
        radio_frame = Frame(main_frame, bg="#f0f0f0")
        radio_frame.pack(pady=10)

        # Tiêu đề nhóm radio
        radio_title = Label(radio_frame, text="Select cut order name:", font=("Arial", 12, "bold"), bg="#f0f0f0")
        radio_title.pack(anchor="w", pady=5)

        # Nút radio
        self.radio1 = Radiobutton(radio_frame, text="Right 1-2 Left", variable=self.order_var, value=1, font=("Arial", 12), bg="#f0f0f0")
        self.radio1.pack(side="left", padx=10)
        self.radio2 = Radiobutton(radio_frame, text="Right 2-1 Left", variable=self.order_var, value=2, font=("Arial", 12), bg="#f0f0f0")
        self.radio2.pack(side="left", padx=10)

        # Kích hoạt kéo thả file/thư mục
        root.drop_target_register(DND_FILES)
        root.dnd_bind('<<Drop>>', self.on_drop)

        # Khung chứa thông tin tác giả và phiên bản
        info_frame = Frame(main_frame, bg="#f0f0f0")
        info_frame.pack(fill="x", pady=10)

        # Tên tác giả
        author_label = Label(root, text="Author: NGVLinh5420", font=("Arial", 10), bg="#f0f0f0", anchor="w")
        author_label.pack(side="left", padx=10, pady=10, anchor="sw")

        # Phiên bản
        version_label = Label(root, text="Version: 1.5", font=("Arial", 10), bg="#f0f0f0", anchor="e")
        version_label.pack(side="right", padx=10, pady=10, anchor="se")

    def upload_image(self):
        # Chọn tệp ảnh
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.path = file_path
            self.label.config(text=f"Selected image: {os.path.basename(file_path)}")
            self.cut_button.config(state="normal")

    def on_drop(self, event):
        # Xử lý kéo thả
        dropped_path = event.data.strip('{}')  # Loại bỏ dấu ngoặc thừa
        if os.path.isdir(dropped_path):
            # Nếu là thư mục, lưu thư mục vào biến path
            self.path = dropped_path
            self.label.config(text=f"Selected folder: {os.path.basename(dropped_path)}")
        elif os.path.isfile(dropped_path):
            # Nếu là file, lưu file vào biến path
            self.path = dropped_path
            self.label.config(text=f"Selected image: {os.path.basename(dropped_path)}")
        self.cut_button.config(state="normal")

    def split_image(self):
        if not self.path:
            self.label.config(text="Please select an image or folder first.")
            return

        try:
            # Nếu là thư mục, duyệt qua tất cả các tệp ảnh trong thư mục
            if os.path.isdir(self.path):
                files = [f for f in os.listdir(self.path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if not files:
                    self.label.config(text="No image files in the folder.")
                    return
                
                for file in files:
                    file_path = os.path.join(self.path, file)
                    self.process_image(file_path)
                self.label.config(text="All images in the folder have been processed.")
            else:
                # Nếu là file ảnh, xử lý trực tiếp
                self.process_image(self.path)
                self.label.config(text="Image has been processed.")
        except Exception as e:
            self.label.config(text=f"Error processing image: {e}")

    def process_image(self, file_path):
        try:
            # Đọc ảnh
            img = Image.open(file_path)
            width, height = img.size

            # Tính toán kích thước cắt
            target_width = height * 3 // 4

            # Kiểm tra nếu ảnh nhỏ hơn kích thước cắt
            if width < target_width:
                self.label.config(text=f"Image width {os.path.basename(file_path)} is not enough to cut.")
                return

            # Cắt ảnh
            left_crop = img.crop((0, 0, target_width, height))  # Cắt bên trái
            right_crop = img.crop((width - target_width, 0, width, height))  # Cắt bên phải

            # Lấy thứ tự từ nút radio
            order = self.order_var.get()

            # Lưu ảnh theo thứ tự người dùng chọn
            base_name, ext = os.path.splitext(file_path)
            if order == 1:
                left_path = f"{base_name}_2{ext}"
                right_path = f"{base_name}_1{ext}"
            else:
                left_path = f"{base_name}_1{ext}"
                right_path = f"{base_name}_2{ext}"

            # Lưu ảnh
            left_crop.save(left_path)
            right_crop.save(right_path)

            # Giữ định dạng gốc và chất lượng cao nhất
            save_params = {}
            if img.format == "JPEG": save_params = {"quality": 100}

            # Chất lượng ảnh JPEG cao nhất
            left_crop.save(left_path, img.format, **save_params)
            right_crop.save(right_path, img.format, **save_params)

            print(f"Image processed: {os.path.basename(file_path)} into {left_path} and {right_path}")
        except Exception as e:
            self.label.config(text=f"Error processing image: {e}")

# Tạo cửa sổ ứng dụng
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageSplitterApp(root)
    root.mainloop()
