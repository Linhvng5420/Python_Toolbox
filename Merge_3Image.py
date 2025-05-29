import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from pathlib import Path

class DragDropApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghép ảnh ngang (PNG chất lượng cao)")
        self.geometry("500x300")
        self.configure(bg="#f0f0f0")
        self.image_paths = []

        self.label = tk.Label(self, text="Kéo và thả tối đa 3 ảnh vào đây", font=("Arial", 14), bg="#f0f0f0")
        self.label.pack(pady=40)

        self.status_label = tk.Label(self, text="", fg="green", bg="#f0f0f0", font=("Arial", 12))
        self.status_label.pack(pady=10)

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
            self.status_label.config(text=f"✅ Đã lưu tại: {output}")
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

if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()
