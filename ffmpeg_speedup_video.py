import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    entry_path.delete(0, tk.END)
    entry_path.insert(0, filepath)

def process_video():
    input_path = entry_path.get()
    speed = entry_speed.get()
    bitrate = entry_bitrate.get()

    if not os.path.isfile(input_path):
        messagebox.showerror("Lỗi", "Đường dẫn tệp không hợp lệ!")
        return

    try:
        speed = float(speed)
        if speed <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi", "Tốc độ phải là số lớn hơn 0!")
        return

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"

    cmd = [
        "ffmpeg",
        "-hwaccel", "cuda",
        "-i", input_path,
        "-filter_complex", f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "h264_nvenc",
        "-preset", "fast"
    ]

    if bitrate.strip() != "":
        cmd += ["-b:v", bitrate]

    cmd.append(output_path)

    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Đang xử lý...\n")

    def run_ffmpeg():
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

            for line in process.stdout:
                text_output.insert(tk.END, line)
                text_output.see(tk.END)  # Tự động cuộn
            process.wait()

            if process.returncode == 0:
                text_output.insert(tk.END, "\n✅ Xong! File đã được tạo.")
            else:
                text_output.insert(tk.END, "\n❌ Đã xảy ra lỗi!")

        except Exception as e:
            text_output.insert(tk.END, f"\nLỗi: {str(e)}")

    threading.Thread(target=run_ffmpeg).start()

# Giao diện
root = tk.Tk()
root.title("Tăng tốc video bằng FFmpeg (hiển thị CMD)")

tk.Label(root, text="Đường dẫn video:").grid(row=0, column=0, sticky="e")
entry_path = tk.Entry(root, width=60)
entry_path.grid(row=0, column=1)
tk.Button(root, text="Chọn...", command=select_file).grid(row=0, column=2)

tk.Label(root, text="Tốc độ (X):").grid(row=1, column=0, sticky="e")
entry_speed = tk.Entry(root)
entry_speed.insert(0, "2.0")
entry_speed.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Bitrate (vd: 2M):").grid(row=2, column=0, sticky="e")
entry_bitrate = tk.Entry(root)
entry_bitrate.insert(0, "")  # Mặc định giữ nguyên bitrate
entry_bitrate.grid(row=2, column=1, sticky="w")

tk.Button(root, text="Tăng tốc và xuất video", command=process_video, bg="#4CAF50", fg="white").grid(row=3, column=1, pady=10)

# Ô hiển thị FFmpeg log
text_output = scrolledtext.ScrolledText(root, height=15, width=100)
text_output.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
