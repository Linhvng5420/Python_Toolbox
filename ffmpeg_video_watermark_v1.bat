@echo off
setlocal enabledelayedexpansion

:: Đường dẫn file input video
set "input_video=v.mp4"

:: Đường dẫn file subtitle .ass
set "subtitle_file=s.ass"

echo =====================================
echo  Thêm watermark bằng file subtitle ASS
echo =====================================
echo.

:: Nhập preset
echo Chọn preset encode (vd: default, slow, medium, fast, hp):
set /p preset=Preset (mặc định: fast): 
if "%preset%"=="" set preset=fast

:: Nhập tên file output
echo Nhập tên file output (không cần đuôi .mp4)
set /p output_name=Tên file output (mặc định: video_watermark_output): 
if "%output_name%"=="" set output_name=video_watermark_output

:: Tạo tên file output hoàn chỉnh
set output_file=%output_name%.mp4

echo.

:: Chạy ffmpeg với các tham số đã chọn
ffmpeg -hwaccel cuda -i "%input_video%" -vf "ass=%subtitle_file%" -c:v h264_nvenc -preset %preset% -c:a copy "%output_file%"

echo.
echo Hoan thanh! File output: %output_file%
pause
