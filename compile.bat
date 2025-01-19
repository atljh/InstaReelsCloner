@echo off

set VENV_PATH=venv
set TEMP_DIR=temp

call %VENV_PATH%\Scripts\activate.bat

set SCRIPT=main.py
set OUTPUT_DIR=dist

nuitka --standalone --onefile --mingw64 --output-dir=%OUTPUT_DIR% --lto=yes --nofollow-import-to=unittest --nofollow-import-to=test --onefile-tempdir-spec="%TEMP_DIR%\\%RANDOM%_%PID%" %SCRIPT%

if %ERRORLEVEL% equ 0 (
    echo Компиляция успешно завершена. Исполняемый файл находится в папке %OUTPUT_DIR%.
) else (
    echo Ошибка при компиляции.
)

deactivate
