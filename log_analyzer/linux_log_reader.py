"""
Читач логів для операційної системи Linux
Читає логи з /var/log та взаємодіє з systemd journal
"""

import os
import re
import gzip
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LinuxLogReader:
    """Клас для читання логів Linux"""
    
    # Основні файли логів Linux
    DEFAULT_LOG_FILES = [
        '/var/log/syslog',
        '/var/log/messages',
        '/var/log/auth.log',
        '/var/log/kern.log',
        '/var/log/daemon.log',
        '/var/log/mail.log',
        '/var/log/user.log'
    ]
    
    # Шаблони для парсингу syslog формату
    SYSLOG_PATTERN = re.compile(
        r'^(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<program>[^:\[\s]+)(?:\[(?P<pid>\d+)\])?:\s*'
        r'(?P<message>.*)$'
    )
    
    # Мапінг рівнів важливості
    SEVERITY_MAPPING = {
        'emerg': 'CRITICAL',
        'alert': 'CRITICAL', 
        'crit': 'CRITICAL',
        'err': 'ERROR',
        'error': 'ERROR',
        'warn': 'WARNING',
        'warning': 'WARNING',
        'notice': 'INFO',
        'info': 'INFO',
        'debug': 'DEBUG'
    }
    
    def __init__(self, log_files: Optional[List[str]] = None, use_journald: bool = True):
        """
        Ініціалізація читача логів Linux
        
        Args:
            log_files: Список файлів логів для читання
            use_journald: Використовувати journald якщо доступно
        """
        self.log_files = log_files or self.DEFAULT_LOG_FILES
        self.use_journald = use_journald and self._is_journald_available()
        
    def read_logs(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Читання логів з Linux
        
        Args:
            start_date: Початкова дата для фільтрації
            end_date: Кінцева дата для фільтрації (за замовчуванням - поточний час)
            
        Returns:
            Список словників з даними логів
        """
        if end_date is None:
            end_date = datetime.now()
            
        all_logs = []
        
        # Спроба читання через journald
        if self.use_journald:
            try:
                journal_logs = self._read_journald_logs(start_date, end_date)
                all_logs.extend(journal_logs)
                logger.info(f"Прочитано {len(journal_logs)} записів з journald")
            except Exception as e:
                logger.warning(f"Не вдалося прочитати логи з journald: {str(e)}")
        
        # Читання з традиційних файлів логів
        for log_file in self.log_files:
            try:
                logs = self._read_log_file(log_file, start_date, end_date)
                all_logs.extend(logs)
                logger.info(f"Прочитано {len(logs)} записів з {log_file}")
            except Exception as e:
                logger.warning(f"Не вдалося прочитати {log_file}: {str(e)}")
                continue
                
        logger.info(f"Загалом прочитано {len(all_logs)} записів логів")
        return all_logs
    
    def _is_journald_available(self) -> bool:
        """Перевірка доступності systemd journald"""
        try:
            subprocess.run(['journalctl', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _read_journald_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Читання логів через systemd journald
        
        Args:
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            Список записів логів
        """
        logs = []
        
        try:
            # Форматування дат для journalctl
            since = start_date.strftime('%Y-%m-%d %H:%M:%S')
            until = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Команда journalctl з JSON виводом
            cmd = [
                'journalctl',
                '--since', since,
                '--until', until,
                '--output=json',
                '--no-pager'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Парсинг JSON виводу
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    import json
                    entry = json.loads(line)
                    log_entry = self._parse_journald_entry(entry)
                    if log_entry:
                        logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Помилка виконання journalctl: {e}")
        except Exception as e:
            logger.error(f"Помилка читання journald: {e}")
            
        return logs
    
    def _parse_journald_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Парсинг запису з journald
        
        Args:
            entry: JSON запис з journald
            
        Returns:
            Словник з даними лога або None
        """
        try:
            # Час
            timestamp_str = entry.get('__REALTIME_TIMESTAMP')
            if timestamp_str:
                timestamp = datetime.fromtimestamp(int(timestamp_str) / 1000000)
            else:
                return None
            
            # Повідомлення
            message = entry.get('MESSAGE', '')
            
            # Джерело
            source = entry.get('_COMM') or entry.get('SYSLOG_IDENTIFIER') or 'Unknown'
            
            # Рівень важливості
            priority = entry.get('PRIORITY', '6')  # 6 = info за замовчуванням
            level = self._priority_to_level(int(priority))
            
            # PID
            pid = entry.get('_PID') or entry.get('SYSLOG_PID')
            
            # Hostname
            hostname = entry.get('_HOSTNAME', 'localhost')
            
            # Unit (systemd service)
            unit = entry.get('_SYSTEMD_UNIT')
            
            return {
                'timestamp': timestamp,
                'level': level,
                'source': source,
                'message': message,
                'pid': pid,
                'hostname': hostname,
                'unit': unit,
                'log_source': 'journald',
                'raw_data': entry
            }
            
        except Exception as e:
            logger.warning(f"Не вдалося розпарсити journald запис: {str(e)}")
            return None
    
    def _priority_to_level(self, priority: int) -> str:
        """Конвертація journald priority в рівень важливості"""
        mapping = {
            0: 'CRITICAL',  # emerg
            1: 'CRITICAL',  # alert
            2: 'CRITICAL',  # crit
            3: 'ERROR',     # err
            4: 'WARNING',   # warning
            5: 'INFO',      # notice
            6: 'INFO',      # info
            7: 'DEBUG'      # debug
        }
        return mapping.get(priority, 'INFO')
    
    def _read_log_file(self, log_file: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Читання традиційного файлу логів
        
        Args:
            log_file: Шлях до файлу лога
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            Список записів логів
        """
        logs = []
        
        if not os.path.exists(log_file):
            return logs
            
        if not os.access(log_file, os.R_OK):
            logger.warning(f"Немає прав для читання {log_file}")
            return logs
        
        try:
            # Визначення чи файл стиснутий
            is_gzipped = log_file.endswith('.gz')
            
            if is_gzipped:
                file_obj = gzip.open(log_file, 'rt', encoding='utf-8', errors='ignore')
            else:
                file_obj = open(log_file, 'r', encoding='utf-8', errors='ignore')
                
            with file_obj:
                current_year = datetime.now().year
                
                for line_num, line in enumerate(file_obj, 1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    log_entry = self._parse_syslog_line(line, current_year, log_file)
                    if log_entry:
                        # Перевірка часового діапазону
                        if start_date <= log_entry['timestamp'] <= end_date:
                            logs.append(log_entry)
                            
        except Exception as e:
            logger.error(f"Помилка читання {log_file}: {str(e)}")
            
        return logs
    
    def _parse_syslog_line(self, line: str, current_year: int, log_file: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг рядка syslog формату
        
        Args:
            line: Рядок лога
            current_year: Поточний рік (для доповнення дати)
            log_file: Шлях до файлу лога
            
        Returns:
            Словник з даними лога або None
        """
        try:
            match = self.SYSLOG_PATTERN.match(line)
            if not match:
                # Спрощений парсинг для нестандартних форматів
                return self._parse_simple_log_line(line, log_file)
            
            groups = match.groupdict()
            
            # Парсинг часу
            timestamp_str = groups['timestamp']
            try:
                # Додавання року до timestamp
                timestamp_with_year = f"{current_year} {timestamp_str}"
                timestamp = datetime.strptime(timestamp_with_year, '%Y %b %d %H:%M:%S')
            except ValueError:
                logger.warning(f"Не вдалося розпарсити час: {timestamp_str}")
                return None
            
            # Визначення рівня важливості з повідомлення
            message = groups['message']
            level = self._detect_log_level(message)
            
            return {
                'timestamp': timestamp,
                'level': level,
                'source': groups['program'],
                'message': message,
                'pid': groups.get('pid'),
                'hostname': groups['hostname'],
                'log_source': Path(log_file).name,
                'raw_data': {
                    'original_line': line
                }
            }
            
        except Exception as e:
            logger.warning(f"Не вдалося розпарсити рядок: {str(e)}")
            return None
    
    def _parse_simple_log_line(self, line: str, log_file: str) -> Optional[Dict[str, Any]]:
        """Спрощений парсинг для нестандартних форматів логів"""
        try:
            # Спроба знайти timestamp на початку рядка
            timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp = datetime.fromisoformat(timestamp_match.group(1).replace('T', ' '))
                message = line[len(timestamp_match.group(1)):].strip()
            else:
                # Якщо timestamp не знайдено, використовуємо поточний час
                timestamp = datetime.now()
                message = line
            
            level = self._detect_log_level(message)
            
            return {
                'timestamp': timestamp,
                'level': level,
                'source': 'unknown',
                'message': message,
                'log_source': Path(log_file).name,
                'raw_data': {
                    'original_line': line
                }
            }
            
        except Exception:
            return None
    
    def _detect_log_level(self, message: str) -> str:
        """
        Визначення рівня важливості з повідомлення
        
        Args:
            message: Текст повідомлення
            
        Returns:
            Рівень важливості
        """
        message_lower = message.lower()
        
        # Пошук ключових слів для критичних помилок
        if any(word in message_lower for word in ['critical', 'fatal', 'panic', 'emergency']):
            return 'CRITICAL'
        
        # Пошук ключових слів для помилок
        if any(word in message_lower for word in ['error', 'err', 'failed', 'failure', 'exception']):
            return 'ERROR'
        
        # Пошук ключових слів для попереджень
        if any(word in message_lower for word in ['warning', 'warn', 'deprecated']):
            return 'WARNING'
        
        # За замовчуванням - INFO
        return 'INFO'
    
    def get_available_log_files(self) -> List[str]:
        """
        Отримання списку доступних файлів логів
        
        Returns:
            Список шляхів до доступних файлів логів
        """
        available_files = []
        
        # Перевірка стандартних файлів
        for log_file in self.DEFAULT_LOG_FILES:
            if os.path.exists(log_file) and os.access(log_file, os.R_OK):
                available_files.append(log_file)
        
        # Пошук додаткових файлів у /var/log
        try:
            log_dir = Path('/var/log')
            if log_dir.exists():
                for file_path in log_dir.glob('*.log*'):
                    if file_path.is_file() and os.access(file_path, os.R_OK):
                        available_files.append(str(file_path))
        except Exception as e:
            logger.warning(f"Помилка пошуку файлів логів: {str(e)}")
        
        return list(set(available_files))  # Видалення дублікатів
