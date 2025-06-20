#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демо-режим з тестовими даними
Для демонстрації можливостей аналізатора без реальних системних логів
"""

import sys
import os
from datetime import datetime, timedelta
import random
from pathlib import Path

# Додавання шляху до модуля
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_analyzer.log_parser import LogParser
from log_analyzer.log_analyzer import LogAnalyzer
from log_analyzer.report_generator import ReportGenerator

def generate_demo_logs(days: int = 7, logs_per_day: int = 100) -> list:
    """
    Генерація демонстраційних логів
    
    Args:
        days: Кількість днів
        logs_per_day: Кількість логів на день
        
    Returns:
        Список демонстраційних логів
    """
    print(f"🎭 Генерація {days * logs_per_day} демонстраційних логів...")
    
    # Шаблони помилок
    error_templates = [
        {
            'level': 'ERROR',
            'source': 'DatabaseService',
            'message': 'Connection timeout to database server',
            'type': 'Мережева помилка'
        },
        {
            'level': 'CRITICAL',
            'source': 'DiskManager',
            'message': 'Disk space critically low: 98% full',
            'type': 'Помилка файлової системи'
        },
        {
            'level': 'ERROR',
            'source': 'AuthenticationService',
            'message': 'Failed login attempt for user admin',
            'type': 'Помилка автентифікації'
        },
        {
            'level': 'WARNING',
            'source': 'MemoryManager',
            'message': 'High memory usage detected: 85%',
            'type': 'Системна помилка'
        },
        {
            'level': 'ERROR',
            'source': 'NetworkAdapter',
            'message': 'Network interface eth0 is down',
            'type': 'Мережева помилка'
        },
        {
            'level': 'CRITICAL',
            'source': 'SecurityService',
            'message': 'Multiple failed authentication attempts detected',
            'type': 'Помилка автентифікації'
        },
        {
            'level': 'ERROR',
            'source': 'ApplicationServer',
            'message': 'Service crashed with exit code 1',
            'type': 'Помилка програми'
        },
        {
            'level': 'WARNING',
            'source': 'UpdateService',
            'message': 'Update server unreachable',
            'type': 'Мережева помилка'
        },
        {
            'level': 'ERROR',
            'source': 'FileSystem',
            'message': 'Permission denied accessing /var/log/system.log',
            'type': 'Помилка файлової системи'
        },
        {
            'level': 'INFO',
            'source': 'SystemMonitor',
            'message': 'System health check completed successfully',
            'type': 'Загальна інформація'
        }
    ]
    
    logs = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Більше помилок у робочі години (9-17)
        for hour in range(24):
            if 9 <= hour <= 17:
                hour_logs = logs_per_day // 24 * 2  # Подвійна активність
            else:
                hour_logs = logs_per_day // 24 // 2  # Половинна активність
            
            for _ in range(max(1, hour_logs)):
                template = random.choice(error_templates)
                
                # Варіації помилок
                variations = {
                    'Connection timeout': ['Connection timeout', 'Connection failed', 'Connection refused'],
                    'Failed login': ['Failed login attempt', 'Invalid credentials', 'Authentication failed'],
                    'disk space': ['Disk space low', 'Storage full', 'No space left'],
                    'Service crashed': ['Service crashed', 'Application terminated', 'Process died']
                }
                
                message = template['message']
                for key, variants in variations.items():
                    if key.lower() in message.lower():
                        message = random.choice(variants) + message[len(key):]
                        break
                
                log_entry = {
                    'timestamp': current_date.replace(
                        hour=hour,
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    ),
                    'level': template['level'],
                    'source': template['source'],
                    'message': message,
                    'hostname': random.choice(['server-01', 'server-02', 'workstation-05']),
                    'pid': random.randint(1000, 9999),
                    'log_source': 'demo'
                }
                
                logs.append(log_entry)
    
    return logs

def run_demo_analysis():
    """Запуск демонстраційного аналізу"""
    print("🎭 ДЕМОНСТРАЦІЙНИЙ РЕЖИМ")
    print("Локального Аналізатора Системних Журналів")
    print("=" * 60)
    
    print("📝 Цей режим використовує штучно згенеровані дані")
    print("   для демонстрації можливостей аналізатора")
    print()
    
    try:
        # Генерація демо-логів
        demo_logs = generate_demo_logs(days=7, logs_per_day=50)
        print(f"✅ Згенеровано {len(demo_logs)} демонстраційних записів")
        
        # Парсинг логів
        print("\n🔍 Парсинг та фільтрація логів...")
        parser = LogParser()
        parsed_logs = parser.parse_logs(demo_logs)
        print(f"✅ Оброблено {len(parsed_logs)} записів")
        
        # Аналіз
        print("\n📊 Проведення аналізу...")
        analyzer = LogAnalyzer()
        analysis_results = analyzer.analyze(parsed_logs, top_n=10)
        
        # Виведення основних результатів
        print("\n📋 ПОПЕРЕДНІ РЕЗУЛЬТАТИ:")
        print("-" * 40)
        
        # Статистика за рівнями
        level_stats = analysis_results.get('level_stats', {})
        by_level = level_stats.get('by_level', {})
        
        for level in ['CRITICAL', 'ERROR', 'WARNING', 'INFO']:
            if level in by_level:
                count = by_level[level]['count']
                percentage = by_level[level]['percentage']
                print(f"{level:>8}: {count:>3} ({percentage:>5.1f}%)")
        
        # Топ помилок
        top_errors = analysis_results.get('error_stats', {}).get('top_errors', [])
        if top_errors:
            print(f"\n🔝 ТОП-{min(5, len(top_errors))} ПОМИЛОК:")
            for i, error in enumerate(top_errors[:5], 1):
                print(f"{i}. {error['error_type']}: {error['count']} разів")
        
        # Генерація звіту
        print(f"\n📄 Створення демо-звіту...")
        report_generator = ReportGenerator()
        output_path = Path("демо_звіт_системних_журналів.docx")
        
        success = report_generator.generate_report(
            analysis_results=analysis_results,
            total_logs=len(demo_logs),
            parsed_logs=len(parsed_logs),
            days_analyzed=7,
            output_path=output_path
        )
        
        if success:
            print(f"✅ Демо-звіт створено: {output_path.absolute()}")
            print(f"📁 Розмір файлу: {output_path.stat().st_size / 1024:.1f} KB")
        else:
            print("❌ Помилка створення звіту")
        
        print("\n🎉 Демонстрація завершена успішно!")
        print("💡 Для аналізу реальних логів запустіть: python main.py")
        
    except Exception as e:
        print(f"❌ Помилка демонстрації: {e}")
        return False
    
    return True

def interactive_demo():
    """Інтерактивна демонстрація"""
    print("🎮 ІНТЕРАКТИВНА ДЕМОНСТРАЦІЯ")
    print("=" * 40)
    
    print("Налаштування демонстрації:")
    
    try:
        days = int(input("Кількість днів для аналізу (1-30) [7]: ") or "7")
        days = max(1, min(30, days))
    except ValueError:
        days = 7
    
    try:
        logs_per_day = int(input("Логів на день (10-200) [50]: ") or "50")
        logs_per_day = max(10, min(200, logs_per_day))
    except ValueError:
        logs_per_day = 50
    
    print(f"\n🎭 Запуск демонстрації:")
    print(f"   Період: {days} днів")
    print(f"   Активність: ~{logs_per_day} логів/день")
    print(f"   Загалом: ~{days * logs_per_day} записів")
    
    input("\nНатисніть Enter для продовження...")
    
    return run_demo_analysis()

if __name__ == "__main__":
    print("🎭 ДЕМОНСТРАЦІЙНИЙ РЕЖИМ")
    print("=" * 60)
    
    mode = input("Виберіть режим:\n1 - Швидка демонстрація\n2 - Інтерактивна демонстрація\nВибір (1/2): ").strip()
    
    if mode == "2":
        success = interactive_demo()
    else:
        success = run_demo_analysis()
    
    sys.exit(0 if success else 1)
