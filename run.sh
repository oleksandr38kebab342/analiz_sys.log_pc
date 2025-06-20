#!/bin/bash

echo "========================================"
echo "Локальний Аналізатор Системних Журналів"
echo "========================================"
echo

show_menu() {
    echo "Виберіть дію:"
    echo "1 - Запустити аналіз системних журналів"
    echo "2 - Запустити демонстрацію з тестовими даними"
    echo "3 - Перевірити готовність системи"
    echo "4 - Переглянути приклади використання"
    echo "5 - Встановити залежності"
    echo "0 - Вихід"
    echo
}

while true; do
    show_menu
    read -p "Ваш вибір (0-5): " choice
    
    case $choice in
        1)
            echo
            echo "🔍 Запуск аналізу системних журналів..."
            echo "💡 Для повного доступу до логів рекомендується sudo"
            echo
            read -p "Запустити з sudo? (y/n): " use_sudo
            echo
            if [[ $use_sudo =~ ^[Yy]$ ]]; then
                sudo python3 main.py
            else
                python3 main.py
            fi
            echo
            read -p "Натисніть Enter для продовження..."
            ;;
        2)
            echo
            echo "🎭 Запуск демонстрації..."
            echo
            python3 demo.py
            echo
            read -p "Натисніть Enter для продовження..."
            ;;
        3)
            echo
            echo "🧪 Перевірка готовності системи..."
            echo
            python3 test_system.py
            echo
            read -p "Натисніть Enter для продовження..."
            ;;
        4)
            echo
            echo "📖 Приклади використання..."
            echo
            python3 example.py
            echo
            read -p "Натисніть Enter для продовження..."
            ;;
        5)
            echo
            echo "📦 Встановлення залежностей..."
            echo
            bash install.sh
            echo
            read -p "Натисніть Enter для продовження..."
            ;;
        0)
            echo
            echo "До побачення!"
            exit 0
            ;;
        *)
            echo "Невірний вибір. Спробуйте ще раз."
            ;;
    esac
done
