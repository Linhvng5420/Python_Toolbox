import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
from pathlib import Path
from datetime import datetime
import subprocess
import os

class ImageMergerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghép Ảnh Ngang (Tối đa 3)")
        self.geometry("900x800")
        self.configure(bg="#f0f0f0")
        self.image_paths = []
        self.result_path = None
        self.result_image = None
        self.thumbnails = []

        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self, text="Kéo tối thiểu 2 và tối đa 3 ảnh vào Ô Ở Dưới đây", font=("Arial", 14))
        self.label.pack(pady=10)

        self.drop_area = tk.Frame(self, bg="#dddddd", relief="ridge", height=80)
        self.drop_area.pack(fill="x", padx=5, pady=0)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        self.preview_frame = tk.Frame(self, bg="#ffffff")
        self.preview_frame.pack(pady=10)

        self.merge_button = ttk.Button(self, text="Ghép Ảnh", command=self.merge_images, state=tk.DISABLED)
        self.merge_button.pack(pady=5)

        self.reset_button = ttk.Button(self, text="Reset", command=self.reset_all)
        self.reset_button.pack(pady=5)

        self.result_label = tk.Label(self)
        self.result_label.pack(pady=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=5)

        self.open_image_btn = ttk.Button(self.button_frame, text="Mở ảnh", command=self.open_image, state=tk.DISABLED)
        self.open_image_btn.grid(row=0, column=0, padx=10)

        self.open_folder_btn = ttk.Button(self.button_frame, text="Mở thư mục", command=self.open_folder, state=tk.DISABLED)
        self.open_folder_btn.grid(row=0, column=1, padx=10)

    def on_drop(self, event):
        paths = self.tk.splitlist(event.data)
        for path in paths:
            if len(self.image_paths) >= 3:
                break
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")) and path not in self.image_paths:
                self.image_paths.append(path)
        self.update_preview()

    def update_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.thumbnails = []
        for index, path in enumerate(self.image_paths):
            frame = tk.Frame(self.preview_frame, bd=2, relief="groove", padx=5, pady=5)
            frame.pack(side="left", padx=5)

            img = Image.open(path)
            img.thumbnail((150, 100))
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails.append(thumb)

            label = tk.Label(frame, image=thumb)
            label.pack()

            name = os.path.basename(path)
            tk.Label(frame, text=name, wraplength=150).pack()

            remove_btn = ttk.Button(frame, text="Xóa", command=lambda i=index: self.remove_image(i))
            remove_btn.pack(pady=2)

        self.update_merge_button_state()

    def remove_image(self, index):
        if 0 <= index < len(self.image_paths):
            del self.image_paths[index]
            self.update_preview()

    def update_merge_button_state(self):
        if 2 <= len(self.image_paths) <= 3:
            self.merge_button.config(state=tk.NORMAL)
        else:
            self.merge_button.config(state=tk.DISABLED)
            self.result_label.config(image='')
            self.result_image = None
            self.result_path = None
            self.open_image_btn.config(state=tk.DISABLED)
            self.open_folder_btn.config(state=tk.DISABLED)

    def reset_all(self):
        self.image_paths.clear()
        self.update_preview()

    def merge_images(self):
        try:
            images = [Image.open(p).convert("RGBA") for p in self.image_paths]
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

            folder = Path.home() / "Pictures" / "Merge_3Image"
            folder.mkdir(parents=True, exist_ok=True)
            now = datetime.now().strftime("%d_%m_%Y-%H%M%S")
            output_path = folder / f"{now}.png"
            result.save(output_path, format="PNG")
            self.result_path = str(output_path)
            self.show_result()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_result(self):
        img = Image.open(self.result_path)
        img.thumbnail((700, 400), Image.LANCZOS)
        self.result_image = ImageTk.PhotoImage(img)
        self.result_label.config(image=self.result_image)
        self.open_image_btn.config(state=tk.NORMAL)
        self.open_folder_btn.config(state=tk.NORMAL)

    def open_image(self):
        if self.result_path:
            os.startfile(self.result_path)

    def open_folder(self):
        if self.result_path:
            folder = os.path.dirname(self.result_path)
            subprocess.Popen(f'explorer "{folder}"')

if __name__ == "__main__":
    app = ImageMergerApp()
    app.mainloop()
