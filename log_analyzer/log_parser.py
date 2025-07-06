"""
Парсер логів - обробка та фільтрація зібраних логів
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LogParser:
    """Клас для парсингу та фільтрації логів"""
    
    # Ключові слова для фільтрації помилок
    ERROR_KEYWORDS = [
        'error', 'err', 'failed', 'failure', 'exception', 'critical', 'fatal',
        'panic', 'denied', 'refused', 'timeout', 'corrupt', 'invalid',
        'не вдалося', 'помилка', 'збій', 'відмова', 'заборонено'
    ]
    
    # Ключові слова для попереджень
    WARNING_KEYWORDS = [
        'warning', 'warn', 'deprecated', 'obsolete', 'retry', 'slow',
        'попередження', 'застаріло', 'повільно'
    ]
    
    # Шаблони для очищення повідомлень
    CLEANUP_PATTERNS = [
        (re.compile(r'\s+'), ' '),  # Множинні пробіли
        (re.compile(r'^\s*\[\d+\.\d+\]\s*'), ''),  # Timestamp у квадратних дужках
        (re.compile(r'^[<>]+\s*'), ''),  # Символи < > на початку
    ]
    
    def __init__(self, filter_levels: Optional[List[str]] = None, 
                 include_keywords: Optional[List[str]] = None,
                 exclude_keywords: Optional[List[str]] = None):
        """
        Ініціалізація парсера
        
        Args:
            filter_levels: Рівні логів для включення (за замовчуванням ERROR, CRITICAL)
            include_keywords: Додаткові ключові слова для включення
            exclude_keywords: Ключові слова для виключення
        """
        self.filter_levels = filter_levels or ['ERROR', 'CRITICAL', 'WARNING']
        self.include_keywords = (include_keywords or []) + self.ERROR_KEYWORDS + self.WARNING_KEYWORDS
        self.exclude_keywords = exclude_keywords or []
        
    def parse_logs(self, raw_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Парсинг та фільтрація логів
        
        Args:
            raw_logs: Список сирих логів
            
        Returns:
            Список відфільтрованих та оброблених логів
        """
        parsed_logs = []
        
        for log_entry in raw_logs:
            try:
                # Нормалізація запису
                normalized_entry = self._normalize_log_entry(log_entry)
                
                if not normalized_entry:
                    continue
                
                # Фільтрація
                if self._should_include_log(normalized_entry):
                    # Додаткова обробка
                    processed_entry = self._process_log_entry(normalized_entry)
                    if processed_entry:
                        parsed_logs.append(processed_entry)
                        
            except Exception as e:
                logger.warning(f"Помилка обробки запису лога: {str(e)}")
                continue
        
        logger.info(f"Відфільтровано {len(parsed_logs)} записів з {len(raw_logs)}")
        return parsed_logs
    
    def _normalize_log_entry(self, log_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Нормалізація запису лога до стандартного формату
        
        Args:
            log_entry: Сирий запис лога
            
        Returns:
            Нормалізований запис або None
        """
        try:
            # Обов'язкові поля
            timestamp = log_entry.get('timestamp')
            if not isinstance(timestamp, datetime):
                return None
            
            message = str(log_entry.get('message', '')).strip()
            if not message:
                return None
            
            # Очищення повідомлення
            clean_message = self._clean_message(message)
            
            return {
                'timestamp': timestamp,
                'level': str(log_entry.get('level', 'INFO')).upper(),
                'source': str(log_entry.get('source', 'Unknown')),
                'message': clean_message,
                'original_message': message,
                'pid': log_entry.get('pid'),
                'hostname': log_entry.get('hostname'),
                'user': log_entry.get('user'),
                'event_id': log_entry.get('event_id'),
                'category': log_entry.get('category'),
                'log_source': log_entry.get('log_source', 'Unknown'),
                'unit': log_entry.get('unit'),
                'computer': log_entry.get('computer'),
                'raw_data': log_entry.get('raw_data', {})
            }
            
        except Exception as e:
            logger.warning(f"Помилка нормалізації: {str(e)}")
            return None
    
    def _clean_message(self, message: str) -> str:
        """
        Очищення повідомлення від непотрібних символів та форматування
        
        Args:
            message: Оригінальне повідомлення
            
        Returns:
            Очищене повідомлення
        """
        cleaned = message
        
        # Застосування шаблонів очищення
        for pattern, replacement in self.CLEANUP_PATTERNS:
            cleaned = pattern.sub(replacement, cleaned)
        
        return cleaned.strip()
    
    def _should_include_log(self, log_entry: Dict[str, Any]) -> bool:
        """
        Перевірка чи повинен лог бути включений у результат
        
        Args:
            log_entry: Запис лога
            
        Returns:
            True якщо лог повинен бути включений
        """
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '').lower()
        
        # Фільтрація за рівнем
        if level not in self.filter_levels:
            # Додаткова перевірка на наявність ключових слів помилок
            if not any(keyword.lower() in message for keyword in self.ERROR_KEYWORDS):
                return False
        
        # Виключення за ключовими словами
        if any(keyword.lower() in message for keyword in self.exclude_keywords):
            return False
        
        # Включення за ключовими словами
        if self.include_keywords:
            if not any(keyword.lower() in message for keyword in self.include_keywords):
                # Якщо це помилка або критичний рівень, все одно включаємо
                if level not in ['ERROR', 'CRITICAL']:
                    return False
        
        return True
    
    def _process_log_entry(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Додаткова обробка запису лога
        
        Args:
            log_entry: Нормалізований запис лога
            
        Returns:
            Оброблений запис лога
        """
        # Створення унікального хешу для групування схожих помилок
        log_entry['message_hash'] = self._generate_message_hash(log_entry['message'])
        
        # Класифікація типу помилки
        log_entry['error_type'] = self._classify_error_type(log_entry['message'])
        
        # Оцінка важливості
        log_entry['severity_score'] = self._calculate_severity_score(log_entry)
        
        # Спрощення повідомлення для звіту
        log_entry['simplified_message'] = self._simplify_message(log_entry['message'])
        
        return log_entry
    
    def _generate_message_hash(self, message: str) -> str:
        """
        Генерація хешу повідомлення для групування схожих помилок
        
        Args:
            message: Повідомлення
            
        Returns:
            Хеш повідомлення
        """
        # Видалення змінних частин (числа, шляхи, ID)
        pattern = re.compile(r'(\d+|/[^\s]*|[A-F0-9]{8,}|0x[A-F0-9]+)', re.IGNORECASE)
        normalized = pattern.sub('{}', message)
        
        # Видалення зайвих пробілів та приведення до нижнього регістру
        normalized = ' '.join(normalized.lower().split())
        
        return str(hash(normalized))
    
    def _classify_error_type(self, message: str) -> str:
        """
        Класифікація типу помилки за повідомленням
        
        Args:
            message: Повідомлення
            
        Returns:
            Тип помилки
        """
        message_lower = message.lower()
        
        # Мережеві помилки
        if any(word in message_lower for word in ['network', 'connection', 'timeout', 'socket', 'dns']):
            return 'Мережева помилка'
        
        # Помилки файлової системи
        if any(word in message_lower for word in ['file', 'directory', 'disk', 'space', 'permission']):
            return 'Помилка файлової системи'
        
        # Помилки автентифікації
        if any(word in message_lower for word in ['auth', 'login', 'password', 'denied', 'forbidden']):
            return 'Помилка автентифікації'
        
        # Помилки програм
        if any(word in message_lower for word in ['application', 'service', 'process', 'crash']):
            return 'Помилка програми'
        
        # Системні помилки
        if any(word in message_lower for word in ['system', 'kernel', 'driver', 'hardware']):
            return 'Системна помилка'
        
        return 'Загальна помилка'
    
    def _calculate_severity_score(self, log_entry: Dict[str, Any]) -> int:
        """
        Розрахунок оцінки важливості помилки
        
        Args:
            log_entry: Запис лога
            
        Returns:
            Оцінка важливості (0-100)
        """
        score = 0
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '').lower()
        
        # Базова оцінка за рівнем
        level_scores = {
            'CRITICAL': 90,
            'ERROR': 70,
            'WARNING': 40,
            'INFO': 20,
            'DEBUG': 10
        }
        score += level_scores.get(level, 20)
        
        # Додаткові бали за критичні ключові слова
        critical_keywords = ['critical', 'fatal', 'panic', 'crash', 'corruption']
        for keyword in critical_keywords:
            if keyword in message:
                score += 10
        
        # Обмеження максимальної оцінки
        return min(score, 100)
    
    def _simplify_message(self, message: str) -> str:
        """
        Спрощення повідомлення для нетехнічного користувача
        
        Args:
            message: Оригінальне повідомлення
            
        Returns:
            Спрощене повідомлення
        """
        # Словник для заміни технічних термінів
        replacements = {
            'authentication failed': 'не вдалося увійти в систему',
            'connection timeout': 'перевищено час очікування з\'єднання',
            'permission denied': 'недостатньо прав доступу',
            'file not found': 'файл не знайдено',
            'disk full': 'диск заповнений',
            'service failed': 'служба не працює',
            'network unreachable': 'мережа недоступна',
            'out of memory': 'недостатньо пам\'яті',
            'invalid request': 'неправильний запит',
            'access denied': 'доступ заборонено'
        }
        
        simplified = message.lower()
        
        # Застосування замін
        for technical, simple in replacements.items():
            simplified = simplified.replace(technical, simple)
        
        # Обрізання до розумної довжини
        if len(simplified) > 150:
            simplified = simplified[:147] + '...'
        
        return simplified.capitalize()
    
    def get_filter_stats(self, total_logs: int, filtered_logs: int) -> Dict[str, Any]:
        """
        Отримання статистики фільтрації
        
        Args:
            total_logs: Загальна кількість логів
            filtered_logs: Кількість відфільтрованих логів
            
        Returns:
            Статистика фільтрації
        """
        filtered_percentage = (filtered_logs / total_logs * 100) if total_logs > 0 else 0
        
        return {
            'total_logs': total_logs,
            'filtered_logs': filtered_logs,
            'filtered_percentage': round(filtered_percentage, 2),
            'filter_levels': self.filter_levels,
            'include_keywords_count': len(self.include_keywords),
            'exclude_keywords_count': len(self.exclude_keywords)
        }
