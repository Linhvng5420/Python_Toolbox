import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from pathlib import Path
import subprocess
import platform
import os

class DragDropApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghép ảnh ngang (PNG chất lượng cao)")
        self.geometry("500x350")
        self.configure(bg="#f0f0f0")
        self.image_paths = []
        self.output_path = None

        self.label = tk.Label(self, text="🖼️ Kéo và thả tối đa 3 ảnh vào đây", font=("Arial", 14), bg="#f0f0f0")
        self.label.pack(pady=30)

        self.status_label = tk.Label(self, text="", fg="green", bg="#f0f0f0", font=("Arial", 11))
        self.status_label.pack(pady=10)

        # Nút mở thư mục
        self.open_folder_button = tk.Button(self, text="📁 Mở thư mục chứa ảnh", command=self.open_folder, state=tk.DISABLED)
        self.open_folder_button.pack(pady=5)

        # Nút mở ảnh
        self.open_image_button = tk.Button(self, text="🖼️ Mở ảnh vừa xuất", command=self.open_image, state=tk.DISABLED)
        self.open_image_button.pack(pady=5)

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        paths = self.tk.splitlist(event.data)
        filtered = [p for p in paths if p.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not filtered:
            messagebox.showerror("Lỗi", "Chỉ hỗ trợ ảnh PNG, JPG hoặc JPEG.")
            return
        if len(filtered) > 3:
            messagebox.showerror("Lỗi", "Chỉ được kéo tối đa 3 ảnh.")
            return

        try:
            output = self.merge_images_horizontally(filtered)
            self.output_path = output
            self.status_label.config(text=f"✅ Đã lưu tại:\n{output}")
            self.open_folder_button.config(state=tk.NORMAL)
            self.open_image_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Lỗi xử lý ảnh", str(e))

    def merge_images_horizontally(self, image_paths):
        images = [Image.open(p).convert("RGBA") for p in image_paths]
        min_height = min(img.height for img in images)
        resized = [
            img.resize((int(img.width * min_height / img.height), min_height), Image.LANCZOS)
            for img in images
        ]
        total_width = sum(img.width for img in resized)
        result = Image.new("RGBA", (total_width, min_height))
        x = 0
        for img in resized:
            result.paste(img, (x, 0))
            x += img.width

        pictures_dir = Path.home() / "Pictures"
        pictures_dir.mkdir(parents=True, exist_ok=True)
        output_path = pictures_dir / "merged_output.png"
        result.save(output_path, format="PNG")
        return output_path

    def open_folder(self):
        if self.output_path:
            folder = os.path.dirname(str(self.output_path))
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def open_image(self):
        if self.output_path:
            if platform.system() == "Windows":
                os.startfile(str(self.output_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(self.output_path)])
            else:
                subprocess.run(["xdg-open", str(self.output_path)])

if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()
