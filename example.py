#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Приклад використання Локального Аналізатора Системних Журналів
Демонстрація основних можливостей програми
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Додавання шляху до модуля
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_analyzer.utils import setup_logging
from log_analyzer.windows_log_reader import WindowsLogReader
from log_analyzer.linux_log_reader import LinuxLogReader
from log_analyzer.log_parser import LogParser
from log_analyzer.log_analyzer import LogAnalyzer
from log_analyzer.report_generator import ReportGenerator

def example_quick_analysis():
    """Приклад швидкого аналізу системи за останню добу"""
    print("🔍 Приклад: Швидкий аналіз за останню добу")
    print("=" * 50)
    
    setup_logging()
    
    # Визначення ОС та створення читача
    import platform
    if platform.system().lower() == 'windows':
        reader = WindowsLogReader(['System', 'Application'])  # Тільки основні джерела
    else:
        reader = LinuxLogReader(['/var/log/syslog'])  # Тільки syslog
    
    # Збір логів за останню добу
    start_date = datetime.now() - timedelta(days=1)
    print(f"📖 Збір логів з {start_date.strftime('%d.%m.%Y %H:%M')}...")
    
    try:
        logs = reader.read_logs(start_date)
        print(f"✅ Зібрано {len(logs)} записів")
        
        if not logs:
            print("❌ Логи не знайдені")
            return
        
        # Парсинг з акцентом на помилки
        parser = LogParser(filter_levels=['ERROR', 'CRITICAL'])
        parsed_logs = parser.parse_logs(logs)
        print(f"🔍 Відфільтровано {len(parsed_logs)} помилок")
        
        # Швидкий аналіз
        analyzer = LogAnalyzer()
        results = analyzer.analyze(parsed_logs, top_n=5)
        
        # Виведення коротких результатів
        print("\n📊 РЕЗУЛЬТАТИ АНАЛІЗУ:")
        print("-" * 30)
        
        level_stats = results.get('level_stats', {})
        if level_stats:
            by_level = level_stats.get('by_level', {})
            print(f"Критичні помилки: {by_level.get('CRITICAL', {}).get('count', 0)}")
            print(f"Звичайні помилки: {by_level.get('ERROR', {}).get('count', 0)}")
            print(f"Попередження: {by_level.get('WARNING', {}).get('count', 0)}")
        
        top_errors = results.get('error_stats', {}).get('top_errors', [])
        if top_errors:
            print(f"\n🔝 ТОП-3 ПРОБЛЕМИ:")
            for i, error in enumerate(top_errors[:3], 1):
                print(f"{i}. {error['error_type']}: {error['count']} разів")
        
        print("\n✅ Швидкий аналіз завершено!")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

def example_custom_filter():
    """Приклад користувацької фільтрації логів"""
    print("\n🔍 Приклад: Пошук специфічних помилок")
    print("=" * 50)
    
    # Створення парсера з користувацькими фільтрами
    custom_parser = LogParser(
        filter_levels=['ERROR', 'CRITICAL', 'WARNING'],
        include_keywords=['failed', 'timeout', 'connection', 'denied'],
        exclude_keywords=['debug', 'trace']
    )
    
    print("🔧 Налаштовано фільтр для пошуку мережевих та системних помилок")
    print("Ключові слова: failed, timeout, connection, denied")

def example_report_customization():
    """Приклад налаштування звіту"""
    print("\n📄 Приклад: Налаштування звіту")
    print("=" * 50)
    
    # Створення генератора звітів
    try:
        report_gen = ReportGenerator()
        print("✅ Генератор звітів готовий")
        print("📋 Звіт буде містити:")
        print("  - Титульну сторінку")
        print("  - Загальну статистику")
        print("  - Детальний аналіз помилок")
        print("  - Часовий аналіз")
        print("  - Рекомендації українською мовою")
        
    except ImportError as e:
        print(f"❌ Помилка: {e}")
        print("💡 Встановіть залежності: pip install python-docx")

def example_check_system():
    """Перевірка готовності системи"""
    print("\n🔧 Перевірка готовності системи")
    print("=" * 50)
    
    import platform
    system = platform.system()
    print(f"🖥️  Операційна система: {system} {platform.release()}")
    
    # Перевірка Python версії
    print(f"🐍 Python версія: {sys.version}")
    
    # Перевірка залежностей
    dependencies = {
        'python-docx': 'для створення Word документів',
        'pywin32': 'для Windows Event Log (тільки Windows)',
    }
    
    print("\n📦 Перевірка залежностей:")
    for dep, description in dependencies.items():
        try:
            if dep == 'pywin32' and system != 'Windows':
                print(f"⏭️  {dep}: пропущено ({description})")
                continue
                
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}: встановлено")
        except ImportError:
            print(f"❌ {dep}: НЕ встановлено - {description}")
    
    # Перевірка прав доступу
    from log_analyzer.utils import check_admin_rights
    
    if check_admin_rights():
        print("✅ Права адміністратора: є")
    else:
        print("⚠️  Права адміністратора: немає (рекомендується для повного доступу)")

def main():
    """Головна функція з прикладами"""
    print("🚀 ПРИКЛАДИ ВИКОРИСТАННЯ")
    print("🔍 Локального Аналізатора Системних Журналів")
    print("=" * 60)
    
    # Перевірка системи
    example_check_system()
    
    # Приклад налаштування звіту
    example_report_customization()
    
    # Приклад користувацької фільтрації
    example_custom_filter()
    
    # Швидкий аналіз (тільки якщо користувач погодиться)
    print("\n" + "=" * 60)
    response = input("🤔 Виконати швидкий аналіз системи? (y/n): ")
    if response.lower() == 'y':
        example_quick_analysis()
    
    print("\n🎉 Приклади завершено!")
    print("💡 Для повного аналізу запустіть: python main.py")

if __name__ == "__main__":
    main()
