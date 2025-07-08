@echo off
title FFmpeg Video Creator with CRF Info
color 0A

echo ==========================================
echo TẠO VIDEO TỪ ẢNH PNG (p.png) VÀ ÂM THANH M4A (s.m4a)
echo ==========================================
echo.
echo --- CÁC CẤP ĐỘ CRF (H.264 - x264/NVENC) ---
echo  0    - Chất lượng gốc (lossless, không nén)
echo 18    - Rất cao (hầu như không mất chất lượng)
echo 23    - Mặc định, chất lượng tốt, dung lượng hợp lý
echo 28    - Trung bình, tiết kiệm dung lượng
echo 30-32 - Thấp, video có thể hơi mờ (Video tỉnh không bị ảnh hưởng) 
echo 40+   - Rất thấp, không khuyến khích dùng
echo -------------------------------------------
echo Lưu Ý: Chọn CRF thấp không đồng nghĩa với Tốc Độ Render nhanh, chỉ dung lương ít hơn thôi.
echo.

set /p crf_value=Nhập giá trị CRF bạn muốn dùng: 

echo.
set /p crf_output_name=Nhập tên video xuất ra: 

echo.
echo Đang tạo video với CRF=%crf_value%, Xuất ra: %crf_output_name%.mp4
echo.

ffmpeg -loop 1 -i p.png -i s.m4a -vf "scale=1920:1080" -shortest -r 1 -c:v h264_nvenc -preset fast -crf %crf_value% -c:a copy "%crf_output_name%.mp4"

echo.
echo ✅ Hoàn tất! Video đã được tạo với tên: %crf_output_name%.mp4
pause
