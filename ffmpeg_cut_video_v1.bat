@echo off
setlocal enabledelayedexpansion

:: Nhập thời điểm bắt đầu
set /p START_TIME=Nhập thời gian bắt đầu (ví dụ: 00:01:00) :

:: Nhập thời điểm kết thúc
set /p END_TIME=Nhập thời gian kết thúc (ví dụ: 00:02:30) :

:: Chuyển đổi thời gian thành giây để tính khoảng cắt
for /f "tokens=1-3 delims=:" %%a in ("%START_TIME%") do (
    set /a START_SEC=%%a*3600 + %%b*60 + %%c
)
for /f "tokens=1-3 delims=:" %%a in ("%END_TIME%") do (
    set /a END_SEC=%%a*3600 + %%b*60 + %%c
)

:: Tính độ dài cần cắt
set /a DURATION_SEC=END_SEC - START_SEC

:: Chuyển lại thành định dạng hh:mm:ss
set /a H=DURATION_SEC / 3600
set /a M=(DURATION_SEC %% 3600) / 60
set /a S=DURATION_SEC %% 60

:: Đảm bảo định dạng hai chữ số
if !H! LSS 10 set H=0!H!
if !M! LSS 10 set M=0!M!
if !S! LSS 10 set S=0!S!

set DURATION=!H!:!M!:!S!

:: Cắt bằng FFmpeg + GPU (HEVC NVENC)
ffmpeg -ss %START_TIME% -i v.mp4 -t !DURATION! -c:v h264_nvenc -preset p1 -c:a copy output.mp4

echo.
echo Đã cắt thành công: output.mp4
pause
