#!/bin/bash

echo "========================================"
echo "Локальний Аналізатор Системних Журналів"
echo "Скрипт встановлення залежностей"
echo "========================================"
echo

# Перевірка Python
echo "Перевірка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не знайдено!"
    echo "Встановіть Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python знайдено"
python3 --version

# Перевірка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не знайдено!"
    echo "Встановіть pip3:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    exit 1
fi

echo "✅ pip3 знайдено"

echo
echo "Встановлення залежностей..."

# Встановлення базових залежностей
pip3 install python-docx

# Спроба встановлення systemd-python (може не спрацювати на всіх системах)
echo "Спроба встановлення systemd-python (опціонально)..."
pip3 install systemd-python 2>/dev/null || echo "⚠️  systemd-python не встановлено (не критично)"

echo
echo "✅ Основні залежності встановлено!"
echo
echo "🚀 Тепер ви можете запустити аналізатор:"
echo "   python3 main.py"
echo
echo "📖 Або переглянути приклади:"
echo "   python3 example.py"
echo
echo "⚠️  Для повного доступу до системних логів запустіть з sudo:"
echo "   sudo python3 main.py"
echo
