@echo off
setlocal enabledelayedexpansion

:: Tạo thư mục A nếu chưa có
set "folder=A"
if not exist "%folder%" mkdir "%folder%"

:: Di chuyển vào thư mục A
cd /d "%folder%"

:: Tạo 100 file từ 1.txt đến 100.txt
for /L %%i in (1,1,100) do (
    echo This is file %%i > "%%i.txt"
)

echo Hoàn thành! Đã tạo 100 file trong thư mục A.
pause
