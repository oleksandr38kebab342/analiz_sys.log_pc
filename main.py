#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локальний Аналізатор Системних Журналів
Автоматизований збір, парсинг, аналіз та генерація звіту за даними системних журналів помилок
"""

import os
import sys
import platform
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from log_analyzer.windows_log_reader import WindowsLogReader
from log_analyzer.linux_log_reader import LinuxLogReader
from log_analyzer.log_parser import LogParser
from log_analyzer.log_analyzer import LogAnalyzer
from log_analyzer.report_generator import ReportGenerator
from log_analyzer.utils import setup_logging, check_admin_rights

def main():
    """Головна функція програми"""
    
    # Налаштування логування
    setup_logging()
    
    # Парсинг аргументів командного рядка
    parser = argparse.ArgumentParser(description='Локальний Аналізатор Системних Журналів')
    parser.add_argument('--output', '-o', type=str, default='звіт_системних_журналів.docx',
                      help='Шлях до вихідного файлу звіту (за замовчуванням: звіт_системних_журналів.docx)')
    parser.add_argument('--days', '-d', type=int, default=7,
                      help='Кількість днів для аналізу (за замовчуванням: 7)')
    parser.add_argument('--top', '-t', type=int, default=10,
                      help='Кількість найчастіших помилок для відображення (за замовчуванням: 10)')
    
    args = parser.parse_args()
    
    print("🔍 Локальний Аналізатор Системних Журналів")
    print("=" * 50)
    
    # Перевірка прав адміністратора
    if not check_admin_rights():
        print("⚠️  Увага: Для повного доступу до системних журналів рекомендується запуск від імені адміністратора")
        response = input("Продовжити без підвищених прав? (y/n): ")
        if response.lower() != 'y':
            print("Програма завершена користувачем")
            return
    
    # Визначення операційної системи та вибір відповідного читача логів
    system = platform.system().lower()
    print(f"🖥️  Виявлена ОС: {platform.system()} {platform.release()}")
    
    try:
        if system == 'windows':
            log_reader = WindowsLogReader()
        elif system == 'linux':
            log_reader = LinuxLogReader()
        else:
            print(f"❌ Операційна система {system} не підтримується")
            print("Підтримувані ОС: Windows, Linux")
            return
        
        # Збір логів
        print(f"📖 Збирання логів за останні {args.days} днів...")
        start_date = datetime.now() - timedelta(days=args.days)
        logs = log_reader.read_logs(start_date)
        
        if not logs:
            print("❌ Не вдалося зібрати логи або логи відсутні")
            return
        
        print(f"✅ Зібрано {len(logs)} записів логів")
        
        # Парсинг логів
        print("🔍 Парсинг та фільтрація логів...")
        parser_obj = LogParser()
        parsed_logs = parser_obj.parse_logs(logs)
        
        if not parsed_logs:
            print("❌ Не вдалося розпарсити логи")
            return
        
        print(f"✅ Розпарсено {len(parsed_logs)} записів")
        
        # Аналіз логів
        print("📊 Аналіз даних...")
        analyzer = LogAnalyzer()
        analysis_results = analyzer.analyze(parsed_logs, top_n=args.top)
        
        # Генерація звіту
        print("📄 Генерація звіту...")
        report_generator = ReportGenerator()
        output_path = Path(args.output)
        
        report_generator.generate_report(
            analysis_results=analysis_results,
            total_logs=len(logs),
            parsed_logs=len(parsed_logs),
            days_analyzed=args.days,
            output_path=output_path
        )
        
        print(f"✅ Звіт успішно створено: {output_path.absolute()}")
        print(f"📁 Розмір файлу: {output_path.stat().st_size / 1024:.1f} KB")
        
    except KeyboardInterrupt:
        print("\n⛔ Операцію перервано користувачем")
    except Exception as e:
        print(f"❌ Виникла помилка: {str(e)}")
        print("Для отримання детальної інформації запустіть з параметром --debug")
        return 1
    
    print("\n🎉 Аналіз завершено успішно!")
    return 0

if __name__ == "__main__":
    exit(main())
