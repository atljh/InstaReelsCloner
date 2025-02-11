#!/bin/bash

REQUIRED_PYTHON="3.11"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен. Установите его и попробуйте снова."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [[ "$PYTHON_VERSION" != "$REQUIRED_PYTHON" ]]; then
    echo "❌ Требуется Python $REQUIRED_PYTHON, но найден Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION найден."

if [ ! -d "venv" ]; then
    echo "📦 Создаём виртуальное окружение..."
    python3 -m venv venv
fi

echo "🚀 Активируем виртуальное окружение..."
source venv/bin/activate

echo "📦 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f "config.yaml" ]; then
    echo "🛠️ Копируем config-sample.yaml в config.yaml..."
    cp config-sample.yaml config.yaml
fi

echo "✅ Установка завершена!"
echo "➡️ Для запуска активируйте окружение: source venv/bin/activate"
echo "➡️ Запустите приложение командой: python main.py"
