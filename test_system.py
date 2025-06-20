#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовий скрипт для перевірки працездатності
Локального Аналізатора Системних Журналів
"""

import sys
import os
import platform
from datetime import datetime, timedelta
from pathlib import Path

# Додавання шляху до модуля
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест імпорту всіх модулів"""
    print("🧪 Тест 1: Перевірка імпорту модулів")
    print("-" * 40)
    
    modules = [
        ('log_analyzer.utils', 'Утилітарні функції'),
        ('log_analyzer.log_parser', 'Парсер логів'),
        ('log_analyzer.log_analyzer', 'Аналізатор логів'),
        ('log_analyzer.report_generator', 'Генератор звітів')
    ]
    
    system = platform.system().lower()
    if system == 'windows':
        modules.append(('log_analyzer.windows_log_reader', 'Читач Windows логів'))
    else:
        modules.append(('log_analyzer.linux_log_reader', 'Читач Linux логів'))
    
    all_passed = True
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {description}: OK")
        except ImportError as e:
            print(f"❌ {description}: ПОМИЛКА - {e}")
            all_passed = False
        except Exception as e:
            print(f"⚠️  {description}: ПОПЕРЕДЖЕННЯ - {e}")
    
    return all_passed

def test_dependencies():
    """Тест залежностей"""
    print("\n🧪 Тест 2: Перевірка залежностей")
    print("-" * 40)
    
    dependencies = {
        'docx': 'python-docx (для створення Word документів)',
    }
    
    system = platform.system().lower()
    if system == 'windows':
        dependencies['win32evtlog'] = 'pywin32 (для Windows Event Log)'
    
    all_passed = True
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {description}: встановлено")
        except ImportError:
            print(f"❌ {description}: НЕ встановлено")
            all_passed = False
    
    return all_passed

def test_permissions():
    """Тест прав доступу"""
    print("\n🧪 Тест 3: Перевірка прав доступу")
    print("-" * 40)
    
    try:
        from log_analyzer.utils import check_admin_rights
        
        has_admin = check_admin_rights()
        if has_admin:
            print("✅ Права адміністратора: є")
        else:
            print("⚠️  Права адміністратора: немає")
            print("   Для повного доступу до логів рекомендується запуск від імені адміністратора")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка перевірки прав: {e}")
        return False

def test_log_reader():
    """Тест читача логів"""
    print("\n🧪 Тест 4: Тест читача логів")
    print("-" * 40)
    
    system = platform.system().lower()
    
    try:
        if system == 'windows':
            from log_analyzer.windows_log_reader import WindowsLogReader
            reader = WindowsLogReader(['System'])
            print("✅ Windows читач логів: створено")
            
            # Тест отримання доступних джерел
            try:
                sources = reader.get_available_log_sources()
                print(f"✅ Доступних джерел логів: {len(sources)}")
            except Exception as e:
                print(f"⚠️  Не вдалося отримати список джерел: {e}")
        
        else:
            from log_analyzer.linux_log_reader import LinuxLogReader
            reader = LinuxLogReader()
            print("✅ Linux читач логів: створено")
            
            # Тест отримання доступних файлів
            try:
                files = reader.get_available_log_files()
                print(f"✅ Доступних файлів логів: {len(files)}")
            except Exception as e:
                print(f"⚠️  Не вдалося отримати список файлів: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення читача логів: {e}")
        return False

def test_parser():
    """Тест парсера логів"""
    print("\n🧪 Тест 5: Тест парсера логів")
    print("-" * 40)
    
    try:
        from log_analyzer.log_parser import LogParser
        
        parser = LogParser()
        print("✅ Парсер логів: створено")
        
        # Тест з фіктивними даними
        test_logs = [
            {
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'source': 'TestApp',
                'message': 'Test error message'
            },
            {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'source': 'TestApp',
                'message': 'Test info message'
            }
        ]
        
        parsed = parser.parse_logs(test_logs)
        print(f"✅ Тест парсингу: оброблено {len(parsed)} записів")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тесту парсера: {e}")
        return False

def test_analyzer():
    """Тест аналізатора"""
    print("\n🧪 Тест 6: Тест аналізатора логів")
    print("-" * 40)
    
    try:
        from log_analyzer.log_analyzer import LogAnalyzer
        
        analyzer = LogAnalyzer()
        print("✅ Аналізатор логів: створено")
        
        # Тест з фіктивними даними
        test_logs = [
            {
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'source': 'TestApp',
                'message': 'Test error message',
                'message_hash': 'test_hash_1',
                'error_type': 'Тестова помилка',
                'severity_score': 70
            }
        ]
        
        results = analyzer.analyze(test_logs, top_n=5)
        print("✅ Тест аналізу: завершено успішно")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тесту аналізатора: {e}")
        return False

def test_report_generator():
    """Тест генератора звітів"""
    print("\n🧪 Тест 7: Тест генератора звітів")
    print("-" * 40)
    
    try:
        from log_analyzer.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        print("✅ Генератор звітів: створено")
        
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту python-docx: {e}")
        print("💡 Встановіть: pip install python-docx")
        return False
    except Exception as e:
        print(f"❌ Помилка тесту генератора: {e}")
        return False

def run_all_tests():
    """Запуск всіх тестів"""
    print("🧪 ТЕСТУВАННЯ ЛОКАЛЬНОГО АНАЛІЗАТОРА СИСТЕМНИХ ЖУРНАЛІВ")
    print("=" * 60)
    print(f"🖥️  ОС: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_dependencies,
        test_permissions,
        test_log_reader,
        test_parser,
        test_analyzer,
        test_report_generator
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Критична помилка в тесті {test_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ")
    print("=" * 60)
    print(f"✅ Пройдено тестів: {passed}/{total}")
    print(f"❌ Не пройдено тестів: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСІ ТЕСТИ ПРОЙДЕНО! Система готова до роботи.")
        print("🚀 Запустіть: python main.py")
    elif passed >= total * 0.7:
        print("\n⚠️  БІЛЬШІСТЬ ТЕСТІВ ПРОЙДЕНО. Система працездатна з обмеженнями.")
        print("💡 Усуньте помилки для повної функціональності.")
    else:
        print("\n❌ КРИТИЧНІ ПОМИЛКИ. Система потребує налагодження.")
        print("🔧 Встановіть залежності та перевірте конфігурацію.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
