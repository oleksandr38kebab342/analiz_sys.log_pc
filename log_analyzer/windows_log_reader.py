"""
Читач логів для операційної системи Windows
Використовує Windows Event Log API через pywin32
"""

import win32evtlog
import win32api
import win32con
import win32security
import winerror
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class WindowsLogReader:
    """Клас для читання логів Windows Event Log"""
    
    # Основні джерела логів Windows
    DEFAULT_LOG_SOURCES = [
        'System',
        'Application', 
        'Security'
    ]
    
    # Мапінг типів подій
    EVENT_TYPE_MAPPING = {
        win32evtlog.EVENTLOG_ERROR_TYPE: 'ERROR',
        win32evtlog.EVENTLOG_WARNING_TYPE: 'WARNING',
        win32evtlog.EVENTLOG_INFORMATION_TYPE: 'INFO',
        win32evtlog.EVENTLOG_AUDIT_SUCCESS: 'AUDIT_SUCCESS',
        win32evtlog.EVENTLOG_AUDIT_FAILURE: 'AUDIT_FAILURE'
    }
    
    def __init__(self, log_sources: Optional[List[str]] = None):
        """
        Ініціалізація читача логів Windows
        
        Args:
            log_sources: Список джерел логів для читання
        """
        self.log_sources = log_sources or self.DEFAULT_LOG_SOURCES
        
    def read_logs(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Читання логів з Windows Event Log
        
        Args:
            start_date: Початкова дата для фільтрації
            end_date: Кінцева дата для фільтрації (за замовчуванням - поточний час)
            
        Returns:
            Список словників з даними логів
        """
        if end_date is None:
            end_date = datetime.now()
            
        all_logs = []
        
        for log_source in self.log_sources:
            try:
                logs = self._read_log_source(log_source, start_date, end_date)
                all_logs.extend(logs)
                logger.info(f"Прочитано {len(logs)} записів з {log_source}")
            except Exception as e:
                logger.warning(f"Не вдалося прочитати логи з {log_source}: {str(e)}")
                continue
                
        logger.info(f"Загалом прочитано {len(all_logs)} записів логів")
        return all_logs
    
    def _read_log_source(self, log_source: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Читання логів з конкретного джерела
        
        Args:
            log_source: Назва джерела логів
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            Список записів логів
        """
        logs = []
        
        try:
            # Відкриття handle для читання Event Log
            handle = win32evtlog.OpenEventLog(None, log_source)
            
            # Читання подій у зворотному порядку (найновіші спочатку)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            total_records = win32evtlog.GetNumberOfEventLogRecords(handle)
            logger.debug(f"Загальна кількість записів у {log_source}: {total_records}")
            
            while True:
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events:
                    break
                    
                for event in events:                    # Конвертація часу події
                    try:
                        if hasattr(event.TimeGenerated, 'timestamp'):
                            # Якщо це об'єкт datetime
                            event_time = event.TimeGenerated
                        else:
                            # Якщо це timestamp
                            event_time = datetime.fromtimestamp(int(event.TimeGenerated))
                    except (ValueError, TypeError):
                        # Якщо конвертація не вдалася, використовуємо поточний час
                        event_time = datetime.now()
                    
                    # Перевірка чи подія в потрібному часовому діапазоні
                    if not (start_date <= event_time <= end_date):
                        if event_time < start_date:
                            # Якщо подія старша за початкову дату, припиняємо читання
                            win32evtlog.CloseEventLog(handle)
                            return logs
                        continue
                    
                    # Формування запису лога
                    log_entry = self._parse_event(event, log_source)
                    if log_entry:
                        logs.append(log_entry)
                        
            win32evtlog.CloseEventLog(handle)
            
        except Exception as e:
            logger.error(f"Помилка при читанні {log_source}: {str(e)}")
            
        return logs
    
    def _parse_event(self, event, log_source: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг окремої події Windows Event Log
        
        Args:
            event: Об'єкт події
            log_source: Джерело лога
            
        Returns:
            Словник з даними події або None
        """
        try:            # Час події
            try:
                if hasattr(event.TimeGenerated, 'timestamp'):
                    # Якщо це об'єкт datetime
                    timestamp = event.TimeGenerated
                else:
                    # Якщо це timestamp
                    timestamp = datetime.fromtimestamp(int(event.TimeGenerated))
            except (ValueError, TypeError):
                # Якщо конвертація не вдалася, використовуємо поточний час
                timestamp = datetime.now()
            
            # Рівень важливості
            event_type = self.EVENT_TYPE_MAPPING.get(event.EventType, 'UNKNOWN')
            
            # Джерело події
            source = event.SourceName or 'Unknown'
            
            # ID події
            event_id = event.EventID & 0xFFFF  # Маскування для отримання реального ID
            
            # Повідомлення
            try:
                # Спроба отримати форматоване повідомлення
                message = win32evtlogutil.SafeFormatMessage(event, log_source)
            except:
                # Якщо не вдалося, використовуємо сирі дані
                message = ' '.join(event.StringInserts) if event.StringInserts else f"Event ID: {event_id}"
            
            # Користувач
            user = None
            if event.Sid:
                try:
                    user = win32security.LookupAccountSid(None, event.Sid)[0]
                except:
                    user = str(event.Sid)
            
            # Категорія
            category = event.EventCategory if hasattr(event, 'EventCategory') else None
            
            return {
                'timestamp': timestamp,
                'level': event_type,
                'source': source,
                'event_id': event_id,
                'message': message,
                'user': user,
                'category': category,
                'log_source': log_source,
                'computer': event.ComputerName,
                'raw_data': {
                    'event_type': event.EventType,
                    'record_number': event.RecordNumber
                }
            }
            
        except Exception as e:
            logger.warning(f"Не вдалося розпарсити подію: {str(e)}")
            return None
    
    def get_available_log_sources(self) -> List[str]:
        """
        Отримання списку доступних джерел логів
        
        Returns:
            Список назв доступних джерел логів
        """
        available_sources = []
        
        try:
            # Отримання списку всіх доступних логів
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_LOCAL_MACHINE,
                "SYSTEM\\CurrentControlSet\\Services\\EventLog"
            )
            
            index = 0
            while True:
                try:
                    source = win32api.RegEnumKey(key, index)
                    available_sources.append(source)
                    index += 1
                except win32api.error:
                    break
                    
            win32api.RegCloseKey(key)
            
        except Exception as e:
            logger.warning(f"Не вдалося отримати список джерел логів: {str(e)}")
            
        return available_sources

# Додатковий імпорт для форматування повідомлень
try:
    import win32evtlogutil
except ImportError:
    logger.warning("win32evtlogutil недоступний, використовується спрощене форматування повідомлень")
