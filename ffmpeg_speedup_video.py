import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import json

def get_video_info(file_path):
    """Lấy thông tin video bằng ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_format", "-show_streams", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Tìm video stream và audio stream
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            format_info = data.get('format', {})
            
            info = {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else 0,
                'video_width': int(video_stream.get('width', 0)) if video_stream else 0,
                'video_height': int(video_stream.get('height', 0)) if video_stream else 0,
                'video_fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
                'video_codec': video_stream.get('codec_name', 'N/A') if video_stream else 'N/A',
                'audio_bitrate': int(audio_stream.get('bit_rate', 0)) if audio_stream and audio_stream.get('bit_rate') else 0,
                'audio_sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
                'audio_codec': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A'
            }
            return info
        else:
            return None
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def format_duration(seconds):
    """Chuyển đổi giây thành định dạng HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_size(bytes_size):
    """Chuyển đổi bytes thành định dạng dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def format_bitrate(bitrate):
    """Chuyển đổi bitrate thành định dạng dễ đọc"""
    if bitrate >= 1000000:
        return f"{bitrate/1000000:.1f} Mbps"
    elif bitrate >= 1000:
        return f"{bitrate/1000:.1f} Kbps"
    else:
        return f"{bitrate} bps"

def show_video_info():
    """Hiển thị thông tin video trong cửa sổ phụ"""
    input_path = entry_path.get()
    if not os.path.isfile(input_path):
        messagebox.showerror("Lỗi", "Vui lòng chọn file video trước!")
        return
    
    # Tạo cửa sổ thông tin video
    info_window = tk.Toplevel(root)
    info_window.title("📊 Thông tin chất lượng video")
    info_window.geometry("800x650")
    info_window.configure(bg="#f0f0f0")
    
    # Header
    header_frame = tk.Frame(info_window, bg="#34495e", height=50)
    header_frame.pack(fill="x", padx=5, pady=5)
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="📊 Thông tin chất lượng video", 
                          font=("Arial", 14, "bold"), fg="white", bg="#34495e")
    title_label.pack(pady=10)
    
    # Control frame for buttons
    control_frame = tk.Frame(info_window, bg="#f0f0f0")
    control_frame.pack(fill="x", padx=10, pady=5)
    
    # Check if output file exists to enable comparison
    speed = entry_speed.get()
    try:
        speed_val = float(speed)
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_{int(speed_val)}x{ext}"
        output_exists = os.path.isfile(output_path)
    except:
        output_exists = False
    
    btn_compare = tk.Button(control_frame, text="⚖️ So sánh trước/sau", 
                           command=lambda: show_comparison_in_window(info_window), 
                           bg="#9b59b6", fg="white", font=("Arial", 9),
                           state="normal" if output_exists else "disabled")
    btn_compare.pack(side="right", padx=5)
    
    # Main frame with notebook for tabs
    main_frame = tk.Frame(info_window, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)
    
    # Tab 1: Video gốc
    original_frame = tk.Frame(notebook, bg="#f0f0f0")
    notebook.add(original_frame, text="📹 Video gốc")
    
    # Tab 2: So sánh (sẽ hiển thị sau khi xử lý)
    compare_frame = tk.Frame(notebook, bg="#f0f0f0")
    notebook.add(compare_frame, text="⚖️ So sánh", state="disabled")
    
    # Tạo bảng thông tin cho video gốc
    create_info_table(original_frame, input_path, "📹 Thông tin video gốc")
    
    # Lưu reference để sử dụng sau
    info_window.compare_frame = compare_frame
    info_window.notebook = notebook
    info_window.btn_compare = btn_compare
    
    # Lưu window reference
    root.info_window = info_window

def show_comparison_in_window(info_window):
    """Hiển thị so sánh trong cửa sổ thông tin video"""
    input_path = entry_path.get()
    speed = float(entry_speed.get())
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"
    
    if not os.path.isfile(output_path):
        messagebox.showwarning("Cảnh báo", "File đầu ra chưa tồn tại. Vui lòng xử lý video trước!")
        return
    
    # Clear comparison frame
    for widget in info_window.compare_frame.winfo_children():
        widget.destroy()
    
    # Create comparison layout
    compare_main = tk.Frame(info_window.compare_frame, bg="#f0f0f0")
    compare_main.pack(fill="both", expand=True)
    
    # Left side - Original
    left_frame = tk.Frame(compare_main, bg="#f0f0f0")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    # Right side - Processed
    right_frame = tk.Frame(compare_main, bg="#f0f0f0")
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Create info tables
    create_info_table(left_frame, input_path, "📹 Video gốc")
    create_info_table(right_frame, output_path, f"⚡ Video sau xử lý ({speed}x)")
    
    # Enable comparison tab
    info_window.notebook.tab(1, state="normal")
    info_window.notebook.select(1)

def create_info_table(parent_frame, file_path, title):
    """Tạo bảng hiển thị thông tin video"""
    # Title
    title_label = tk.Label(parent_frame, text=title, font=("Arial", 12, "bold"), 
                          bg="#f0f0f0", fg="#2c3e50")
    title_label.pack(pady=(10, 5))
    
    # File path
    path_frame = tk.Frame(parent_frame, bg="#f0f0f0")
    path_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(path_frame, text="📁 File:", font=("Arial", 9, "bold"), bg="#f0f0f0").pack(anchor="w")
    path_text = tk.Text(path_frame, height=2, wrap="word", font=("Arial", 8))
    path_text.pack(fill="x", pady=(2, 10))
    path_text.insert("1.0", file_path)
    path_text.config(state="disabled")
    
    # Info table frame
    table_frame = tk.Frame(parent_frame, bg="#f0f0f0")
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Get video info
    info = get_video_info(file_path)
    
    if info:
        # Create treeview for better table display
        tree = ttk.Treeview(table_frame, columns=("property", "value"), show="headings", height=12)
        tree.heading("property", text="Thuộc tính")
        tree.heading("value", text="Giá trị")
        tree.column("property", width=200)
        tree.column("value", width=300)
        
        # Add data to tree
        tree.insert("", "end", values=("⏱️ Thời lượng", format_duration(info['duration'])))
        tree.insert("", "end", values=("📏 Kích thước file", format_size(info['size'])))
        tree.insert("", "end", values=("🔗 Bitrate tổng", format_bitrate(info['bitrate'])))
        tree.insert("", "end", values=("", ""))  # Separator
        tree.insert("", "end", values=("📺 THÔNG TIN VIDEO", ""))
        tree.insert("", "end", values=("📐 Độ phân giải", f"{info['video_width']} x {info['video_height']}"))
        tree.insert("", "end", values=("🎬 Frame rate", f"{info['video_fps']:.2f} fps"))
        tree.insert("", "end", values=("🎥 Video codec", info['video_codec']))
        tree.insert("", "end", values=("", ""))  # Separator
        tree.insert("", "end", values=("🔊 THÔNG TIN AUDIO", ""))
        tree.insert("", "end", values=("🎵 Audio bitrate", format_bitrate(info['audio_bitrate'])))
        tree.insert("", "end", values=("📻 Sample rate", f"{info['audio_sample_rate']} Hz"))
        tree.insert("", "end", values=("🎼 Audio codec", info['audio_codec']))
        
        tree.pack(fill="both", expand=True)
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
    else:
        error_label = tk.Label(table_frame, text="❌ Không thể lấy thông tin video", 
                              font=("Arial", 10), bg="#f0f0f0", fg="red")
        error_label.pack(pady=20)

def show_comparison():
    """Hiển thị so sánh trước và sau khi xử lý"""
    if not hasattr(root, 'info_window') or not root.info_window.winfo_exists():
        show_video_info()
        return
    
    input_path = entry_path.get()
    speed = float(entry_speed.get())
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"
    
    if not os.path.isfile(output_path):
        messagebox.showwarning("Cảnh báo", "File đầu ra chưa tồn tại. Vui lòng xử lý video trước!")
        return
    
    # Clear comparison frame
    for widget in root.info_window.compare_frame.winfo_children():
        widget.destroy()
    
    # Create comparison layout
    compare_main = tk.Frame(root.info_window.compare_frame, bg="#f0f0f0")
    compare_main.pack(fill="both", expand=True)
    
    # Left side - Original
    left_frame = tk.Frame(compare_main, bg="#f0f0f0")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    # Right side - Processed
    right_frame = tk.Frame(compare_main, bg="#f0f0f0")
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Create info tables
    create_info_table(left_frame, input_path, "📹 Video gốc")
    create_info_table(right_frame, output_path, f"⚡ Video sau xử lý ({speed}x)")
    
    # Enable comparison tab
    root.info_window.notebook.tab(1, state="normal")
    root.info_window.notebook.select(1)

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
    btn_info.config(state="disabled")
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
            btn_info.config(state="normal")
            
            if process.returncode == 0:
                text_output.insert(tk.END, "\n" + "=" * 60 + "\n")
                text_output.insert(tk.END, "✅ Thành công! Video đã được tạo.\n")
                text_output.insert(tk.END, f"📍 Vị trí: {output_path}\n")
                
                # Enable comparison button in info window if it exists
                if hasattr(root, 'info_window') and root.info_window.winfo_exists():
                    root.info_window.btn_compare.config(state="normal")
                
                messagebox.showinfo("Thành công", "Video đã được xử lý thành công!")
            else:
                text_output.insert(tk.END, "\n❌ Đã xảy ra lỗi trong quá trình xử lý!")
                messagebox.showerror("Lỗi", "Có lỗi xảy ra trong quá trình xử lý!")

        except Exception as e:
            progress_bar.stop()
            btn_process.config(state="normal", text="🚀 Tăng tốc và xuất video")
            btn_info.config(state="normal")
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
btn_clear.pack(side="left", padx=(0, 10))

btn_info = tk.Button(control_frame, text="📊 Thông tin video", command=show_video_info, 
                    bg="#3498db", fg="white", font=("Arial", 9))
btn_info.pack(side="left")

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
