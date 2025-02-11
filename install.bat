@echo off
setlocal

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.11 и попробуйте снова.
    exit /b 1
)

for /f "tokens=2 delims=. " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
if "%PYTHON_VERSION%" neq "11" (
    echo ❌ Требуется Python 3.11, но найден Python 3.%PYTHON_VERSION%
    exit /b 1
)

echo ✅ Python 3.11 найден.

if not exist "venv" (
    echo 📦 Создаём виртуальное окружение...
    python -m venv venv
)

echo 🚀 Активируем виртуальное окружение...
call venv\Scripts\activate

echo 📦 Устанавливаем зависимости...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist "config.yaml" (
    echo 🛠️ Копируем config-sample.yaml в config.yaml...
    copy config-sample.yaml config.yaml
)

echo ✅ Установка завершена!
echo ➡️ Для запуска активируйте окружение: call venv\Scripts\activate
echo ➡️ Запустите приложение командой: python main.py

endlocal
pause
