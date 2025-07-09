import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
    if filepath:
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

    # Disable button during processing
    btn_process.config(state="disabled", text="Đang xử lý...")
    progress_bar.start(10)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "🚀 Bắt đầu xử lý video...\n")
    text_output.insert(tk.END, f"📁 Input: {input_path}\n")
    text_output.insert(tk.END, f"⚡ Speed: {speed}x\n")
    text_output.insert(tk.END, f"💾 Output: {output_path}\n")
    text_output.insert(tk.END, "-" * 60 + "\n")

    def run_ffmpeg():
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

            for line in process.stdout:
                text_output.insert(tk.END, line)
                text_output.see(tk.END)
                root.update_idletasks()
            process.wait()

            progress_bar.stop()
            btn_process.config(state="normal", text="🚀 Tăng tốc và xuất video")
            
            if process.returncode == 0:
                text_output.insert(tk.END, "\n" + "=" * 60 + "\n")
                text_output.insert(tk.END, "✅ Thành công! Video đã được tạo.\n")
                text_output.insert(tk.END, f"📍 Vị trí: {output_path}\n")
                messagebox.showinfo("Thành công", "Video đã được xử lý thành công!")
            else:
                text_output.insert(tk.END, "\n❌ Đã xảy ra lỗi trong quá trình xử lý!")
                messagebox.showerror("Lỗi", "Có lỗi xảy ra trong quá trình xử lý!")

        except Exception as e:
            progress_bar.stop()
            btn_process.config(state="normal", text="🚀 Tăng tốc và xuất video")
            text_output.insert(tk.END, f"\n💥 Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    threading.Thread(target=run_ffmpeg, daemon=True).start()

def clear_log():
    text_output.delete(1.0, tk.END)

def on_enter_key(event):
    if btn_process['state'] == 'normal':
        process_video()

# Giao diện chính
root = tk.Tk()
root.title("🎬 FFmpeg Video Speed Controller")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

# Style configuration
style = ttk.Style()
style.theme_use('clam')

# Header frame
header_frame = tk.Frame(root, bg="#2c3e50", height=60)
header_frame.pack(fill="x", padx=5, pady=5)
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, text="🎬 Video Speed Controller", 
                      font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
title_label.pack(pady=15)

# Main content frame
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Input section
input_frame = tk.LabelFrame(main_frame, text="📁 Chọn video", font=("Arial", 10, "bold"), 
                           bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
input_frame.pack(fill="x", pady=(0, 10))

tk.Label(input_frame, text="Đường dẫn:", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_path = tk.Entry(input_frame, width=70, font=("Arial", 9))
entry_path.grid(row=0, column=1, padx=(5, 5), pady=5)
btn_browse = tk.Button(input_frame, text="📂 Chọn file", command=select_file, 
                      bg="#3498db", fg="white", font=("Arial", 9, "bold"))
btn_browse.grid(row=0, column=2, padx=(5, 0), pady=5)

# Settings section
settings_frame = tk.LabelFrame(main_frame, text="⚙️ Cài đặt", font=("Arial", 10, "bold"), 
                              bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
settings_frame.pack(fill="x", pady=(0, 10))

tk.Label(settings_frame, text="Tốc độ (X):", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_speed = tk.Entry(settings_frame, width=15, font=("Arial", 9))
entry_speed.insert(0, "2.0")
entry_speed.grid(row=0, column=1, sticky="w", padx=(5, 20), pady=5)

tk.Label(settings_frame, text="Bitrate (vd: 2M):", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=2, sticky="w", pady=5)
entry_bitrate = tk.Entry(settings_frame, width=15, font=("Arial", 9))
entry_bitrate.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)

# Control buttons frame
control_frame = tk.Frame(main_frame, bg="#f0f0f0")
control_frame.pack(fill="x", pady=(0, 10))

btn_process = tk.Button(control_frame, text="🚀 Tăng tốc và xuất video", command=process_video, 
                       bg="#27ae60", fg="white", font=("Arial", 11, "bold"), height=2)
btn_process.pack(side="left", padx=(0, 10))

btn_clear = tk.Button(control_frame, text="🗑️ Xóa log", command=clear_log, 
                     bg="#e74c3c", fg="white", font=("Arial", 9))
btn_clear.pack(side="left")

# Progress bar
progress_bar = ttk.Progressbar(control_frame, mode='indeterminate')
progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))

# Output section
output_frame = tk.LabelFrame(main_frame, text="📋 Kết quả xử lý", font=("Arial", 10, "bold"), 
                            bg="#f0f0f0", fg="#2c3e50", padx=5, pady=5)
output_frame.pack(fill="both", expand=True)

text_output = scrolledtext.ScrolledText(output_frame, height=20, width=100, 
                                       font=("Consolas", 9), bg="#1e1e1e", fg="#ffffff",
                                       insertbackground="white")
text_output.pack(fill="both", expand=True, padx=5, pady=5)

# Bind Enter key to process
root.bind('<Return>', on_enter_key)

# Initial message
text_output.insert(tk.END, "🎬 Chào mừng đến với Video Speed Controller!\n")
text_output.insert(tk.END, "📝 Hướng dẫn:\n")
text_output.insert(tk.END, "1. Chọn file video bằng nút 'Chọn file'\n")
text_output.insert(tk.END, "2. Điều chỉnh tốc độ (2.0 = tăng tốc 2 lần)\n")
text_output.insert(tk.END, "3. Tùy chọn: Điều chỉnh bitrate (để trống = tự động)\n")
text_output.insert(tk.END, "4. Nhấn 'Tăng tốc và xuất video' hoặc Enter\n")
text_output.insert(tk.END, "-" * 60 + "\n\n")

root.mainloop()
