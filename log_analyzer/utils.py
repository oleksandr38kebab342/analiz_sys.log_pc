"""
Утилітарні функції для роботи аналізатора логів
"""

import os
import sys
import ctypes
import logging
import platform
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Налаштування системи логування"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_admin_rights():
    """Перевірка наявності адміністративних прав"""
    try:
        system = platform.system().lower()
        
        if system == 'windows':
            # Перевірка для Windows
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Перевірка для Unix-подібних систем
            return os.getuid() == 0
    except AttributeError:
        # Якщо функція недоступна
        return False
    except Exception:
        return False

def ensure_directory(path):
    """Забезпечує існування директорії"""
    Path(path).mkdir(parents=True, exist_ok=True)

def format_bytes(bytes_value):
    """Форматування розміру в байтах у зрозумілий вигляд"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def safe_get_dict_value(dictionary, key, default=None):
    """Безпечне отримання значення зі словника"""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default

def truncate_text(text, max_length=100):
    """Обрізання тексту до максимальної довжини з додаванням многокрапки"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
