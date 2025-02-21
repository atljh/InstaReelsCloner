@echo off
setlocal

chcp 65001 >nul

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден. Установите Python 3.11 и попробуйте снова.
    exit /b 1
)

python -m nuitka --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ИНФО] Nuitka не найден. Устанавливаем Nuitka...
    python -m pip install nuitka
)

echo [ИНФО] Компилируем main.py...
python -m nuitka --standalone --onefile --enable-console main.py

if %errorlevel% neq 0 (
    echo [ОШИБКА] Ошибка при компиляции!
    exit /b 1
)

echo [УСПЕХ] Компиляция завершена! Файл main.exe готов.

endlocal
pause
