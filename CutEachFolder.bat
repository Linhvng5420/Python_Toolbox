@echo off
setlocal enabledelayedexpansion

set "source=%CD%"  :: Lấy thư mục nơi chạy script
set "filesPerFolder=30"
set "count=0"
set "folderIndex=1"

:: Chuyển đến thư mục nguồn
cd /d "%source%"

dir /b /o:D /a:-d > file_list.txt

:: Duyệt danh sách file từ file_list.txt
for /f "delims=" %%F in (file_list.txt) do (
    if not "%%F"=="%~nx0" (  :: Bỏ qua file script đang chạy
        if !count! == 0 (
            set "folderName=!folderIndex!"
            mkdir "!folderName!" 2>nul
        )

        move "%%F" "!folderName!\" 2>nul
        
        set /a count+=1
        
        if !count! == %filesPerFolder% (
            set /a folderIndex+=1
            set count=0
        )
    )
)

echo Hoàn thành!
pause
