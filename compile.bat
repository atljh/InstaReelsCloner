@echo off
set SCRIPT=your_script.py
set OUTPUT_DIR=dist

nuitka --standalone --onefile --mingw64 --output-dir=%OUTPUT_DIR% %SCRIPT%

if %ERRORLEVEL% equ 0 (
    echo Компиляция успешно завершена. Исполняемый файл находится в папке %OUTPUT_DIR%.
) else (
    echo Ошибка при компиляции.
)