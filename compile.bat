@echo off

set VENV_PATH=venv
set TEMP_DIR=temp
set SCRIPT=main.py
set OUTPUT_DIR=dist

where nuitka >nul 2>&1 || (
    echo Nuitka не найден. Установите его через pip install nuitka.
    exit /b 1
)

if not exist "%TEMP_DIR%" (
    mkdir "%TEMP_DIR%"
)

call %VENV_PATH%\Scripts\activate.bat || (
    echo Не удалось активировать виртуальное окружение.
    exit /b 1
)

nuitka --standalone --onefile --mingw64 --output-dir=%OUTPUT_DIR% --lto=yes --nofollow-import-to=unittest --nofollow-import-to=test --onefile-tempdir-spec="%TEMP_DIR%\\%RANDOM%_%PID%" %SCRIPT%

if %ERRORLEVEL% equ 0 (
    echo Компиляция успешно завершена. Исполняемый файл находится в папке %OUTPUT_DIR%.
) else (
    echo Ошибка при компиляции.
    exit /b %ERRORLEVEL%
)

deactivate

exit /b 0
