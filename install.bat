@echo off
setlocal

:: Проверяем наличие Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.11 и попробуйте снова.
    exit /b 1
)

:: Получаем версию Python корректно
for /f "delims=" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%v

:: Проверяем, что Python 3.11
if not "%PYTHON_VERSION%"=="3.11" (
    echo ❌ Требуется Python 3.11, но найден Python %PYTHON_VERSION%
    exit /b 1
)

echo ✅ Python 3.11 найден.

:: Создание виртуального окружения
if not exist "venv" (
    echo 📦 Создаём виртуальное окружение...
    python -m venv venv
)

:: Активация виртуального окружения
echo 🚀 Активируем виртуальное окружение...
call venv\Scripts\activate

:: Установка зависимостей
echo 📦 Устанавливаем зависимости...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Копирование конфигурационного файла
if not exist "config.yaml" (
    echo 🛠️ Копируем config-sample.yaml в config.yaml...
    copy config-sample.yaml config.yaml
)

echo ✅ Установка завершена!
echo ➡️ Для запуска активируйте окружение: call venv\Scripts\activate
echo ➡️ Запустите приложение командой: python main.py

endlocal
pause
