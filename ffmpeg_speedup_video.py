# Import các thư viện cần thiết
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import json
import tkinterdnd2 as tkdnd
import pyperclip
import re

def auto_close_messagebox(title, message, auto_close_time=3000):
    """Tạo messagebox tự động đóng sau thời gian chỉ định (ms)"""
    # Tạo cửa sổ popup tùy chỉnh
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("400x150")
    popup.configure(bg="#f0f0f0")
    popup.resizable(False, False)
    
    # Đặt cửa sổ ở giữa màn hình
    popup.transient(root)
    popup.grab_set()
    
    # Tính toán vị trí trung tâm
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
    y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")
    
    # Frame chính
    main_frame = tk.Frame(popup, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Icon và thông báo
    icon_label = tk.Label(main_frame, text="✅", font=("Arial", 24), bg="#f0f0f0", fg="#27ae60")
    icon_label.pack(pady=(0, 10))
    
    message_label = tk.Label(main_frame, text=message, font=("Arial", 11), bg="#f0f0f0", 
                            wraplength=350, justify="center")
    message_label.pack(pady=(0, 15))
    
    # Countdown label
    countdown_var = tk.StringVar()
    countdown_label = tk.Label(main_frame, textvariable=countdown_var, font=("Arial", 9), 
                              bg="#f0f0f0", fg="#7f8c8d")
    countdown_label.pack()
    
    # Nút đóng
    btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
    btn_frame.pack(fill="x", pady=(10, 0))
    
    def close_popup():
        """Đóng cửa sổ popup"""
        popup.destroy()
    
    ok_button = tk.Button(btn_frame, text="OK", command=close_popup, 
                         bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                         padx=20)
    ok_button.pack()
    
    # Countdown timer
    countdown_seconds = auto_close_time // 1000
    
    def update_countdown():
        """Cập nhật đếm ngược và tự động đóng"""
        nonlocal countdown_seconds
        if countdown_seconds > 0:
            countdown_var.set(f"Tự động đóng sau {countdown_seconds} giây...")
            countdown_seconds -= 1
            popup.after(1000, update_countdown)
        else:
            close_popup()
    
    # Bắt đầu countdown
    update_countdown()
    
    # Xử lý phím Enter và Escape
    def on_key(event):
        if event.keysym in ['Return', 'Escape']:
            close_popup()
    
    popup.bind('<Key>', on_key)
    popup.focus_set()

def get_video_info(file_path):
    """Lấy thông tin chi tiết video bằng ffprobe"""
    try:
        # Câu lệnh ffprobe để lấy thông tin video
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_format", "-show_streams", file_path
        ]
        # Chạy lệnh và capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # Parse JSON data từ ffprobe
            data = json.loads(result.stdout)
            
            # Tìm video stream và audio stream đầu tiên
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            # Lấy thông tin format chung
            format_info = data.get('format', {})
            
            # Tạo dictionary chứa thông tin video
            info = {
                'duration': float(format_info.get('duration', 0)),  # Thời lượng (giây)
                'size': int(format_info.get('size', 0)),  # Kích thước file (bytes)
                'bitrate': int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else 0,  # Bitrate tổng
                'video_width': int(video_stream.get('width', 0)) if video_stream else 0,  # Độ rộng video
                'video_height': int(video_stream.get('height', 0)) if video_stream else 0,  # Độ cao video
                'video_fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,  # Frame rate
                'video_codec': video_stream.get('codec_name', 'N/A') if video_stream else 'N/A',  # Codec video
                'audio_bitrate': int(audio_stream.get('bit_rate', 0)) if audio_stream and audio_stream.get('bit_rate') else 0,  # Bitrate audio
                'audio_sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,  # Sample rate audio
                'audio_codec': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A'  # Codec audio
            }
            return info
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi lấy thông tin video: {e}")
        return None

def format_duration(seconds):
    """Chuyển đổi giây thành định dạng HH:MM:SS dễ đọc"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_size(bytes_size):
    """Chuyển đổi bytes thành định dạng dễ đọc (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def format_bitrate(bitrate):
    """Chuyển đổi bitrate thành định dạng dễ đọc (Kbps, Mbps)"""
    if bitrate >= 1000000:
        return f"{bitrate/1000000:.1f} Mbps"
    elif bitrate >= 1000:
        return f"{bitrate/1000:.1f} Kbps"
    else:
        return f"{bitrate} bps"

def show_video_info():
    """Hiển thị thông tin chi tiết video trong cửa sổ phụ"""
    input_path = entry_path.get()
    if not os.path.isfile(input_path):
        messagebox.showerror("Lỗi", "Vui lòng chọn file video trước!")
        return
    
    # Tạo cửa sổ mới hiển thị thông tin video
    info_window = tk.Toplevel(root)
    info_window.title("📊 Thông tin chất lượng video")
    info_window.geometry("1200x800")
    info_window.configure(bg="#f0f0f0")
    
    # Tạo header với màu nền đẹp
    header_frame = tk.Frame(info_window, bg="#34495e", height=50)
    header_frame.pack(fill="x", padx=5, pady=5)
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="📊 Thông tin chất lượng video", 
                          font=("Arial", 14, "bold"), fg="white", bg="#34495e")
    title_label.pack(pady=10)
    
    # Frame chứa các nút điều khiển
    control_frame = tk.Frame(info_window, bg="#f0f0f0")
    control_frame.pack(fill="x", padx=10, pady=5)
    
    # Kiểm tra xem file output đã tồn tại chưa để enable nút so sánh
    speed = entry_speed.get()
    try:
        speed_val = float(speed)
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_{int(speed_val)}x{ext}"
        output_exists = os.path.isfile(output_path)
    except:
        output_exists = False
    
    # Nút so sánh kết quả (chỉ enable khi có file output)
    btn_compare = tk.Button(control_frame, text="⚖️ So sánh kết quả", 
                           command=lambda: show_comparison_in_window(info_window), 
                           bg="#9b59b6", fg="white", font=("Arial", 9),
                           state="normal" if output_exists else "disabled")
    btn_compare.pack(side="left", padx=5)
    
    # Frame chính chứa các tab
    main_frame = tk.Frame(info_window, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Tạo notebook để quản lý tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)
    
    # Tab 1: Thông tin video gốc
    original_frame = tk.Frame(notebook, bg="#f0f0f0")
    notebook.add(original_frame, text="📹 Video gốc")
    
    # Tab 2: So sánh (ban đầu disable, sẽ enable sau khi xử lý)
    compare_frame = tk.Frame(notebook, bg="#f0f0f0")
    notebook.add(compare_frame, text="⚖️ So sánh", state="disabled")
    
    # Tạo bảng thông tin cho video gốc
    create_info_table(original_frame, input_path, "📹 Thông tin video gốc")
    
    # Lưu reference để sử dụng trong các hàm khác
    info_window.compare_frame = compare_frame
    info_window.notebook = notebook
    info_window.btn_compare = btn_compare
    
    # Lưu window reference vào root
    root.info_window = info_window

def show_comparison_in_window(info_window):
    """Hiển thị so sánh video gốc và video đã xử lý trong cửa sổ thông tin"""
    input_path = entry_path.get()
    speed = float(entry_speed.get())
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"
    
    # Kiểm tra file output có tồn tại không
    if not os.path.isfile(output_path):
        messagebox.showwarning("Cảnh báo", "File đầu ra chưa tồn tại. Vui lòng xử lý video trước!")
        return
    
    # Xóa nội dung cũ trong tab so sánh
    for widget in info_window.compare_frame.winfo_children():
        widget.destroy()
    
    # Tạo layout so sánh 2 cột
    compare_main = tk.Frame(info_window.compare_frame, bg="#f0f0f0")
    compare_main.pack(fill="both", expand=True)
    
    # Cột trái - Video gốc
    left_frame = tk.Frame(compare_main, bg="#f0f0f0")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    # Cột phải - Video đã xử lý
    right_frame = tk.Frame(compare_main, bg="#f0f0f0")
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Tạo bảng thông tin cho cả 2 video
    create_info_table(left_frame, input_path, "📹 Video gốc")
    create_info_table(right_frame, output_path, f"⚡ Video sau xử lý ({speed}x)")
    
    # Enable tab so sánh và chuyển sang tab đó
    info_window.notebook.tab(1, state="normal")
    info_window.notebook.select(1)

def create_info_table(parent_frame, file_path, title):
    """Tạo bảng hiển thị thông tin chi tiết video"""
    # Tiêu đề bảng
    title_label = tk.Label(parent_frame, text=title, font=("Arial", 12, "bold"), 
                          bg="#f0f0f0", fg="#2c3e50")
    title_label.pack(pady=(10, 5))
    
    # Hiển thị đường dẫn file
    path_frame = tk.Frame(parent_frame, bg="#f0f0f0")
    path_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(path_frame, text="📁 File:", font=("Arial", 9, "bold"), bg="#f0f0f0").pack(anchor="w")
    path_text = tk.Text(path_frame, height=2, wrap="word", font=("Arial", 8))
    path_text.pack(fill="x", pady=(2, 10))
    path_text.insert("1.0", file_path)
    path_text.config(state="disabled")
    
    # Frame chứa bảng thông tin
    table_frame = tk.Frame(parent_frame, bg="#f0f0f0")
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Lấy thông tin video
    info = get_video_info(file_path)
    
    if info:
        # Tạo treeview để hiển thị dữ liệu dạng bảng đẹp hơn
        tree = ttk.Treeview(table_frame, columns=("property", "value"), show="headings", height=12)
        tree.heading("property", text="Thuộc tính")
        tree.heading("value", text="Giá trị")
        tree.column("property", width=200)
        tree.column("value", width=300)
        
        # Thêm dữ liệu vào bảng
        tree.insert("", "end", values=("⏱️ Thời lượng", format_duration(info['duration'])))
        tree.insert("", "end", values=("📏 Kích thước file", format_size(info['size'])))
        tree.insert("", "end", values=("🔗 Bitrate tổng", format_bitrate(info['bitrate'])))
        tree.insert("", "end", values=("", ""))  # Dòng phân cách
        tree.insert("", "end", values=("📺 THÔNG TIN VIDEO", ""))
        tree.insert("", "end", values=("📐 Độ phân giải", f"{info['video_width']} x {info['video_height']}"))
        tree.insert("", "end", values=("🎬 Frame rate", f"{info['video_fps']:.2f} fps"))
        tree.insert("", "end", values=("🎥 Video codec", info['video_codec']))
        tree.insert("", "end", values=("", ""))  # Dòng phân cách
        tree.insert("", "end", values=("🔊 THÔNG TIN AUDIO", ""))
        tree.insert("", "end", values=("🎵 Audio bitrate", format_bitrate(info['audio_bitrate'])))
        tree.insert("", "end", values=("📻 Sample rate", f"{info['audio_sample_rate']} Hz"))
        tree.insert("", "end", values=("🎼 Audio codec", info['audio_codec']))
        
        tree.pack(fill="both", expand=True)
        
        # Thanh cuộn cho bảng
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
    else:
        # Hiển thị lỗi nếu không lấy được thông tin
        error_label = tk.Label(table_frame, text="❌ Không thể lấy thông tin video", 
                              font=("Arial", 10), bg="#f0f0f0", fg="red")
        error_label.pack(pady=20)

def show_comparison():
    """Hiển thị so sánh trước và sau khi xử lý (sử dụng từ main window)"""
    # Kiểm tra xem cửa sổ thông tin có đang mở không
    if not hasattr(root, 'info_window') or not root.info_window.winfo_exists():
        show_video_info()
        return
    
    input_path = entry_path.get()
    speed = float(entry_speed.get())
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"
    
    # Kiểm tra file output
    if not os.path.isfile(output_path):
        messagebox.showwarning("Cảnh báo", "File đầu ra chưa tồn tại. Vui lòng xử lý video trước!")
        return
    
    # Xóa nội dung cũ trong tab so sánh
    for widget in root.info_window.compare_frame.winfo_children():
        widget.destroy()
    
    # Tạo layout so sánh 2 cột
    compare_main = tk.Frame(root.info_window.compare_frame, bg="#f0f0f0")
    compare_main.pack(fill="both", expand=True)
    
    # Cột trái - Video gốc
    left_frame = tk.Frame(compare_main, bg="#f0f0f0")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    # Cột phải - Video đã xử lý
    right_frame = tk.Frame(compare_main, bg="#f0f0f0")
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Tạo bảng thông tin cho cả 2 video
    create_info_table(left_frame, input_path, "📹 Video gốc")
    create_info_table(right_frame, output_path, f"⚡ Video sau xử lý ({speed}x)")
    
    # Enable tab so sánh và chuyển sang tab đó
    root.info_window.notebook.tab(1, state="normal")
    root.info_window.notebook.select(1)

def is_video_file(file_path):
    """Kiểm tra xem file có phải là định dạng video được hỗ trợ không"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
    return any(file_path.lower().endswith(ext) for ext in video_extensions)

def extract_file_path_from_text(text):
    """Trích xuất đường dẫn file video từ text clipboard"""
    # Loại bỏ ký tự xuống dòng và khoảng trắng thừa
    text = text.strip().replace('\n', '').replace('\r', '')
    
    # Kiểm tra nếu là đường dẫn Windows hoàn chỉnh và hợp lệ
    if os.path.isfile(text) and is_video_file(text):
        return text
    
    # Tìm đường dẫn trong text bằng regex patterns
    patterns = [
        r'[A-Za-z]:\\[^<>:"|?*\n\r]*\.[a-zA-Z0-9]{2,4}',  # Đường dẫn Windows
        r'/[^<>:"|?*\n\r]*\.[a-zA-Z0-9]{2,4}',  # Đường dẫn Unix/Linux
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if os.path.isfile(match) and is_video_file(match):
                return match
    
    return None

def on_drop(event):
    """Xử lý sự kiện kéo thả file vào ứng dụng"""
    files = root.tk.splitlist(event.data)
    if files:
        file_path = files[0]
        if is_video_file(file_path):
            # Tự động xóa log cũ khi kéo thả video mới
            text_output.delete(1.0, tk.END)
            entry_path.delete(0, tk.END)
            entry_path.insert(0, file_path)
            
            # Cấu hình màu sắc và thêm text thông báo
            text_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 9, "bold"))
            text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
            
            text_output.insert(tk.END, "📁 Đã kéo thả file: ", "info")
            text_output.insert(tk.END, f"{os.path.basename(file_path)}\n", "success")
            text_output.insert(tk.END, "✨ Đã tự động xóa log cũ cho video mới.\n")
            text_output.insert(tk.END, "-" * 60 + "\n\n")
        else:
            messagebox.showerror("Lỗi", "File không phải là định dạng video được hỗ trợ!")

def paste_from_clipboard():
    """Dán đường dẫn video từ clipboard"""
    try:
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            file_path = extract_file_path_from_text(clipboard_text)
            if file_path:
                # Tự động xóa log cũ khi dán video mới
                text_output.delete(1.0, tk.END)
                entry_path.delete(0, tk.END)
                entry_path.insert(0, file_path)
                
                # Cấu hình màu sắc và thêm text thông báo
                text_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 9, "bold"))
                text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
                
                text_output.insert(tk.END, "📋 Đã dán từ clipboard: ", "info")
                text_output.insert(tk.END, f"{os.path.basename(file_path)}\n", "success")
                text_output.insert(tk.END, "-" * 60 + "\n\n")
            else:
                # Thử dán trực tiếp nếu không tìm thấy đường dẫn hợp lệ
                if os.path.isfile(clipboard_text.strip()) and is_video_file(clipboard_text.strip()):
                    # Tự động xóa log cũ khi dán video mới
                    text_output.delete(1.0, tk.END)
                    entry_path.delete(0, tk.END)
                    entry_path.insert(0, clipboard_text.strip())
                    
                    text_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 9, "bold"))
                    text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
                    
                    text_output.insert(tk.END, "📋 Đã dán từ clipboard: ", "info")
                    text_output.insert(tk.END, f"{os.path.basename(clipboard_text.strip())}\n", "success")
                    text_output.insert(tk.END, "-" * 60 + "\n\n")
                else:
                    messagebox.showwarning("Cảnh báo", "Clipboard không chứa đường dẫn video hợp lệ!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể truy cập clipboard: {str(e)}")

def on_entry_key(event):
    """Xử lý phím tắt trong ô nhập đường dẫn (Ctrl+V để dán)"""
    if event.keysym == 'v' and event.state & 0x4:  # Phát hiện Ctrl+V
        root.after_idle(paste_from_clipboard)
        return "break"

def select_file():
    """Mở dialog chọn file video"""
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v *.3gp")])
    if filepath:
        # Tự động xóa log cũ khi chọn video mới
        text_output.delete(1.0, tk.END)
        entry_path.delete(0, tk.END)
        entry_path.insert(0, filepath)
        
        # Cấu hình màu sắc và thêm text thông báo
        text_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 9, "bold"))
        text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
        
        text_output.insert(tk.END, "📂 Đã chọn file: ", "info")
        text_output.insert(tk.END, f"{os.path.basename(filepath)}\n", "success")
        text_output.insert(tk.END, "-" * 60 + "\n\n")

def process_video():
    """Hàm chính xử lý tăng tốc video bằng FFmpeg"""
    # Lấy thông tin từ giao diện
    input_path = entry_path.get()
    speed = entry_speed.get()
    bitrate = entry_bitrate.get()

    # Kiểm tra tính hợp lệ của đường dẫn file
    if not os.path.isfile(input_path):
        messagebox.showerror("Lỗi", "Đường dẫn tệp không hợp lệ!")
        return

    # Kiểm tra tính hợp lệ của tốc độ
    try:
        speed = float(speed)
        if speed <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi", "Tốc độ phải là số lớn hơn 0!")
        return

    # Tạo tên file output
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{int(speed)}x{ext}"

    # Xây dựng câu lệnh FFmpeg với hardware acceleration
    cmd = [
        "ffmpeg",
        "-hwaccel", "cuda",  # Sử dụng GPU NVIDIA để tăng tốc
        "-i", input_path,
        "-filter_complex", f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]",  # Filter tăng tốc video và audio
        "-map", "[v]",  # Map video stream
        "-map", "[a]",  # Map audio stream
        "-c:v", "h264_nvenc",  # Sử dụng encoder NVIDIA
        "-preset", "fast"  # Preset tốc độ nhanh
    ]

    # Thêm bitrate nếu người dùng chỉ định
    if bitrate.strip() != "" and bitrate.strip().lower() != "auto":
        cmd += ["-b:v", bitrate]

    cmd.append(output_path)

    # Disable nút xử lý và bắt đầu progress bar
    btn_process.config(state="disabled", text="Đang xử lý...")
    progress_bar.start(10)
    text_output.delete(1.0, tk.END)
    
    # Cấu hình các tag màu sắc cho output text
    text_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 9, "bold"))
    text_output.tag_configure("error", foreground="#ff4444", font=("Consolas", 9, "bold"))
    text_output.tag_configure("warning", foreground="#ffaa00", font=("Consolas", 9, "bold"))
    text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
    text_output.tag_configure("header", foreground="#ff88ff", font=("Consolas", 9, "bold"))
    text_output.tag_configure("progress", foreground="#88ff88", font=("Consolas", 9))
    text_output.tag_configure("command", foreground="#ffff88", font=("Consolas", 8))
    
    # Hiển thị thông tin bắt đầu xử lý
    text_output.insert(tk.END, "🚀 Bắt đầu xử lý video...\n", "success")
    text_output.insert(tk.END, f"📁 Input: ", "info")
    text_output.insert(tk.END, f"{input_path}\n")
    text_output.insert(tk.END, f"⚡ Speed: ", "info")
    text_output.insert(tk.END, f"{speed}x\n", "warning")
    text_output.insert(tk.END, f"💾 Output: ", "info")
    text_output.insert(tk.END, f"{output_path}\n")
    text_output.insert(tk.END, "-" * 80 + "\n")
    text_output.insert(tk.END, "💻 Câu lệnh FFmpeg đầy đủ:\n", "header")
    
    # Hiển thị câu lệnh FFmpeg được sử dụng
    cmd_string = " ".join([f'"{arg}"' if " " in arg else arg for arg in cmd])
    text_output.insert(tk.END, f"{cmd_string}\n", "command")
    text_output.insert(tk.END, "-" * 80 + "\n")
    text_output.insert(tk.END, "📊 Tiến trình xử lý:\n", "header")

    def run_ffmpeg():
        """Chạy FFmpeg trong thread riêng để không block UI"""
        try:
            # Khởi tạo process FFmpeg
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)

            last_progress_line = None
            # Đọc output từ FFmpeg theo real-time
            for line in iter(process.stdout.readline, ''):
                line = line.rstrip('\n\r')
                if not line:
                    continue
                
                # Kiểm tra xem user có đang ở cuối text không để tự động scroll
                at_bottom = text_output.yview()[1] == 1.0
                    
                # Kiểm tra nếu là dòng progress (chứa frame=, fps=, time=)
                if 'frame=' in line and 'fps=' in line and 'time=' in line:
                    # Đây là dòng cập nhật tiến trình
                    if last_progress_line is not None:
                        # Xóa dòng progress trước đó để thay thế
                        try:
                            text_output.delete("end-2l linestart", "end-1l linestart")
                        except:
                            pass
                    
                    text_output.insert(tk.END, line + "\n", "progress")
                    last_progress_line = line
                else:
                    # Đây là dòng output thông thường
                    if "error" in line.lower() or "failed" in line.lower():
                        text_output.insert(tk.END, line + "\n", "error")
                    elif "warning" in line.lower():
                        text_output.insert(tk.END, line + "\n", "warning")
                    else:
                        text_output.insert(tk.END, line + "\n")
                    last_progress_line = None
                
                # Chỉ tự động scroll nếu user đang ở cuối
                if at_bottom:
                    text_output.see(tk.END)
                root.update_idletasks()
                
            # Chờ process kết thúc
            process.wait()

            # Dừng progress bar và enable lại nút xử lý
            progress_bar.stop()
            btn_process.config(state="normal", text="🚀 Tăng tốc và xuất video")
            
            # Kiểm tra kết quả xử lý
            if process.returncode == 0:
                # Thành công
                text_output.insert(tk.END, "\n" + "=" * 80 + "\n")
                text_output.insert(tk.END, "✅ Thành công! Video đã được tạo.\n", "success")
                text_output.insert(tk.END, "📍 Vị trí: ", "info")
                text_output.insert(tk.END, f"{output_path}\n", "success")
                text_output.see(tk.END)  # Luôn scroll đến cuối khi hoàn thành
                
                # Enable nút so sánh trong cửa sổ thông tin nếu có
                if hasattr(root, 'info_window') and root.info_window.winfo_exists():
                    root.info_window.btn_compare.config(state="normal")
                
                # Sử dụng messagebox tự động đóng thay vì messagebox thông thường
                auto_close_messagebox("Thành công", "Video đã được xử lý thành công!\nTự động đóng sau 3 giây.", 3000)
            else:
                # Lỗi xử lý
                text_output.insert(tk.END, "\n❌ Đã xảy ra lỗi trong quá trình xử lý!\n", "error")
                text_output.see(tk.END)
                messagebox.showerror("Lỗi", "Có lỗi xảy ra trong quá trình xử lý!")

        except Exception as e:
            # Xử lý exception
            progress_bar.stop()
            btn_process.config(state="normal", text="🚀 Tăng tốc và xuất video")
            text_output.insert(tk.END, f"\n💥 Lỗi: {str(e)}\n", "error")
            text_output.see(tk.END)
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    # Chạy FFmpeg trong thread riêng
    threading.Thread(target=run_ffmpeg, daemon=True).start()

def clear_log():
    """Xóa tất cả log và reset đường dẫn file"""
    text_output.delete(1.0, tk.END)
    entry_path.delete(0, tk.END)
    
    # Cấu hình màu sắc cho thông báo
    text_output.tag_configure("warning", foreground="#ffaa00", font=("Consolas", 9, "bold"))
    text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))
    text_output.tag_configure("header", foreground="#ff88ff", font=("Consolas", 9, "bold"))
    
    # Hiển thị thông báo xóa và hướng dẫn sử dụng
    text_output.insert(tk.END, "🗑️ Đã xóa log và đường dẫn file.\n", "warning")
    # Hiển thị lại hướng dẫn ban đầu
    text_output.insert(tk.END, "🎬 Chào mừng đến với Video Speed Controller!\n", "header")
    text_output.insert(tk.END, "📝 Hướng dẫn:\n", "info")
    text_output.insert(tk.END, "1. 🖱️ Kéo thả file video vào cửa sổ này\n")
    text_output.insert(tk.END, "2. 📂 Hoặc chọn file bằng nút 'Chọn file'\n")
    text_output.insert(tk.END, "3. 📋 Hoặc dán đường dẫn từ clipboard (Ctrl+V)\n")
    text_output.insert(tk.END, "4. ⚙️ Điều chỉnh tốc độ (2.0 = tăng tốc 2 lần)\n")
    text_output.insert(tk.END, "5. 🎚️ Tùy chọn: Điều chỉnh bitrate (để trống = tự động)\n")
    text_output.insert(tk.END, "6. 🚀 Nhấn 'Tăng tốc và xuất video' hoặc Enter\n")
    text_output.insert(tk.END, "-" * 60 + "\n\n")

def on_enter_key(event):
    """Xử lý phím Enter để bắt đầu xử lý video"""
    if btn_process['state'] == 'normal':
        process_video()

# Khởi tạo cửa sổ chính
root = tkdnd.TkinterDnD.Tk()
root.title("🎬 FFmpeg Video Speed Controller")
root.geometry("1200x800")
root.configure(bg="#f0f0f0")

# Bật tính năng kéo thả
root.drop_target_register(tkdnd.DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Cấu hình style cho ttk widgets
style = ttk.Style()
style.theme_use('clam')

# Tạo header frame với màu nền đẹp
header_frame = tk.Frame(root, bg="#2c3e50", height=60)
header_frame.pack(fill="x", padx=5, pady=5)
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, text="🎬 Video Speed Controller", 
                      font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
title_label.pack(pady=15)

# Frame chính chứa tất cả nội dung
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Phần chọn file input
input_frame = tk.LabelFrame(main_frame, text="📁 Chọn video", font=("Arial", 10, "bold"), 
                           bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
input_frame.pack(fill="x", pady=(0, 10))

tk.Label(input_frame, text="Đường dẫn:", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_path = tk.Entry(input_frame, width=70, font=("Arial", 9))
entry_path.grid(row=0, column=1, padx=(5, 5), pady=5)
entry_path.bind('<KeyPress>', on_entry_key)  # Bind phím tắt

btn_browse = tk.Button(input_frame, text="📂 Chọn file", command=select_file, 
                      bg="#3498db", fg="white", font=("Arial", 9, "bold"))
btn_browse.grid(row=0, column=2, padx=(5, 5), pady=5)

btn_paste = tk.Button(input_frame, text="📋 Dán", command=paste_from_clipboard, 
                     bg="#f39c12", fg="white", font=("Arial", 9, "bold"))
btn_paste.grid(row=0, column=3, padx=(5, 0), pady=5)

# Phần cài đặt tốc độ và bitrate
settings_frame = tk.LabelFrame(main_frame, text="⚙️ Cài đặt", font=("Arial", 10, "bold"), 
                              bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
settings_frame.pack(fill="x", pady=(0, 10))

tk.Label(settings_frame, text="Tốc độ (X):", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_speed = tk.Entry(settings_frame, width=15, font=("Arial", 9))
entry_speed.insert(0, "2.0")  # Giá trị mặc định
entry_speed.grid(row=0, column=1, sticky="w", padx=(5, 20), pady=5)

tk.Label(settings_frame, text="Bitrate:", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=2, sticky="w", pady=5)
entry_bitrate = tk.Entry(settings_frame, width=15, font=("Arial", 9))
entry_bitrate.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)
entry_bitrate.insert(0, "")
entry_bitrate.config(fg="grey")
entry_bitrate.insert(0, "Auto")  # Placeholder text

def on_bitrate_focus_in(event):
    """Xóa placeholder khi focus vào ô bitrate"""
    if entry_bitrate.get() == "Auto":
        entry_bitrate.delete(0, tk.END)
        entry_bitrate.config(fg="black")

def on_bitrate_focus_out(event):
    """Thêm lại placeholder khi focus ra khỏi ô bitrate"""
    if entry_bitrate.get().strip() == "":
        entry_bitrate.insert(0, "Auto")
        entry_bitrate.config(fg="grey")

entry_bitrate.bind("<FocusIn>", on_bitrate_focus_in)
entry_bitrate.bind("<FocusOut>", on_bitrate_focus_out)

# Frame chứa các nút điều khiển
control_frame = tk.Frame(main_frame, bg="#f0f0f0")
control_frame.pack(fill="x", pady=(0, 10))

btn_process = tk.Button(control_frame, text="🚀 Tăng tốc và xuất video", command=process_video, 
                       bg="#27ae60", fg="white", font=("Arial", 11, "bold"), height=2)
btn_process.pack(side="left", padx=(0, 10))

btn_clear = tk.Button(control_frame, text="🗑️ Clear All", command=clear_log, 
                     bg="#e74c3c", fg="white", font=("Arial", 9))
btn_clear.pack(side="left", padx=(0, 10))

btn_info = tk.Button(control_frame, text="📊 Thông tin video", command=show_video_info, 
                    bg="#3498db", fg="white", font=("Arial", 9))
btn_info.pack(side="left")

# Thanh progress bar
progress_bar = ttk.Progressbar(control_frame, mode='indeterminate')
progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))

# Phần hiển thị kết quả và log
output_frame = tk.LabelFrame(main_frame, text="📋 Kết quả xử lý", font=("Arial", 10, "bold"), 
                            bg="#f0f0f0", fg="#2c3e50", padx=5, pady=5)
output_frame.pack(fill="both", expand=True)

text_output = scrolledtext.ScrolledText(output_frame, height=20, width=120, 
                                       font=("Consolas", 9), bg="#1e1e1e", fg="#ffffff",
                                       insertbackground="white")
text_output.pack(fill="both", expand=True, padx=5, pady=5)

# Bind phím Enter để xử lý video
root.bind('<Return>', on_enter_key)

# Hiển thị thông báo chào mừng và hướng dẫn ban đầu
text_output.tag_configure("header", foreground="#ff88ff", font=("Consolas", 9, "bold"))
text_output.tag_configure("info", foreground="#00aaff", font=("Consolas", 9, "bold"))

text_output.insert(tk.END, "🎬 Chào mừng đến với Video Speed Controller!\n", "header")
text_output.insert(tk.END, "📝 Hướng dẫn:\n", "info")
text_output.insert(tk.END, "1. 🖱️ Kéo thả file video vào cửa sổ này\n")
text_output.insert(tk.END, "2. 📂 Hoặc chọn file bằng nút 'Chọn file'\n")
text_output.insert(tk.END, "3. 📋 Hoặc dán đường dẫn từ clipboard (Ctrl+V)\n")
text_output.insert(tk.END, "4. ⚙️ Điều chỉnh tốc độ (2.0 = tăng tốc 2 lần)\n")
text_output.insert(tk.END, "5. 🎚️ Tùy chọn: Điều chỉnh bitrate (để trống = tự động)\n")
text_output.insert(tk.END, "6. 🚀 Nhấn 'Tăng tốc và xuất video' hoặc Enter\n")
text_output.insert(tk.END, "-" * 60 + "\n\n")

# Bắt đầu vòng lặp chính của ứng dụng
root.mainloop()
