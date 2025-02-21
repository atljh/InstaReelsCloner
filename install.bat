@echo off
setlocal

chcp 65001 >nul

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден. Установите Python 3.11 и попробуйте снова.
    exit /b 1
)

for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=." %%b in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%b
    set PYTHON_MINOR=%%c
)

if not "%PYTHON_MAJOR%.%PYTHON_MINOR%"=="3.11" (
    echo [ОШИБКА] Требуется Python 3.11, но найден Python %PYTHON_MAJOR%.%PYTHON_MINOR%.
    echo Установите Python 3.11 и добавьте его в PATH.
    exit /b 1
)

echo Python 3.11 найден.

if not exist "venv" (
    echo Создаем виртуальное окружение...
    python -m venv venv
)

echo Активируем виртуальное окружение...
call venv\Scripts\activate

echo Устанавливаем зависимости...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist "config.yaml" (
    echo Копируем config-sample.yaml в config.yaml...
    copy config-sample.yaml config.yaml
)

echo Установка завершена!
echo.
echo Для запуска выполните следующие шаги:
echo 1. Активируйте окружение: call venv\Scripts\activate
echo 2. Запустите приложение: python main.py
echo.

endlocal
pause
