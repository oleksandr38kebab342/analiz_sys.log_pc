"""
Аналізатор логів - статистичний аналіз та групування помилок
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class LogAnalyzer:
    """Клас для аналізу логів та генерації статистики"""
    
    def __init__(self):
        """Ініціалізація аналізатора"""
        self.analysis_results = {}
    
    def analyze(self, logs: List[Dict[str, Any]], top_n: int = 10) -> Dict[str, Any]:
        """
        Комплексний аналіз логів
        
        Args:
            logs: Список оброблених логів
            top_n: Кількість найчастіших помилок для відображення
            
        Returns:
            Результати аналізу
        """
        if not logs:
            logger.warning("Немає логів для аналізу")
            return {}
        
        logger.info(f"Початок аналізу {len(logs)} записів логів")
        
        # Основні статистики
        level_stats = self._analyze_by_level(logs)
        time_stats = self._analyze_by_time(logs)
        source_stats = self._analyze_by_source(logs)
        error_stats = self._analyze_errors(logs, top_n)
        
        # Аналіз трендів
        trends = self._analyze_trends(logs)
        
        # Аналіз за типами помилок
        error_types = self._analyze_error_types(logs)
        
        # Критичні події
        critical_events = self._find_critical_events(logs)
        
        # Загальна статистика
        general_stats = self._calculate_general_stats(logs)
        
        results = {
            'general_stats': general_stats,
            'level_stats': level_stats,
            'time_stats': time_stats,
            'source_stats': source_stats,
            'error_stats': error_stats,
            'error_types': error_types,
            'trends': trends,
            'critical_events': critical_events,
            'analysis_timestamp': datetime.now()
        }
        
        self.analysis_results = results
        logger.info("Аналіз завершено успішно")
        
        return results
    
    def _calculate_general_stats(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Розрахунок загальної статистики"""
        if not logs:
            return {}
        
        timestamps = [log['timestamp'] for log in logs]
        
        return {
            'total_logs': len(logs),
            'date_range': {
                'start': min(timestamps),
                'end': max(timestamps),
                'duration_hours': (max(timestamps) - min(timestamps)).total_seconds() / 3600
            },
            'unique_sources': len(set(log['source'] for log in logs)),
            'unique_hosts': len(set(log.get('hostname', 'unknown') for log in logs)),
            'average_severity': sum(log.get('severity_score', 50) for log in logs) / len(logs)
        }
    
    def _analyze_by_level(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Аналіз логів за рівнем важливості
        
        Args:
            logs: Список логів
            
        Returns:
            Статистика за рівнями
        """
        level_counter = Counter(log['level'] for log in logs)
        total_logs = len(logs)
        
        level_stats = {}
        for level, count in level_counter.items():
            percentage = (count / total_logs) * 100
            level_stats[level] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return {
            'by_level': level_stats,
            'most_common_level': level_counter.most_common(1)[0] if level_counter else ('INFO', 0),
            'error_ratio': round((level_counter.get('ERROR', 0) + level_counter.get('CRITICAL', 0)) / total_logs * 100, 2)
        }
    
    def _analyze_by_time(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Аналіз логів за часом
        
        Args:
            logs: Список логів
            
        Returns:
            Часова статистика
        """
        # Групування за годинами
        hourly_stats = defaultdict(int)
        daily_stats = defaultdict(int)
        
        for log in logs:
            timestamp = log['timestamp']
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            day_key = timestamp.date()
            
            hourly_stats[hour_key] += 1
            daily_stats[day_key] += 1
        
        # Пошук пікових годин
        peak_hours = Counter(hourly_stats).most_common(5)
        peak_days = Counter(daily_stats).most_common(3)
        
        # Аналіз за годинами доби
        hours_of_day = defaultdict(int)
        for log in logs:
            hour = log['timestamp'].hour
            hours_of_day[hour] += 1
        
        return {
            'hourly_distribution': dict(hourly_stats),
            'daily_distribution': dict(daily_stats),
            'peak_hours': peak_hours,
            'peak_days': peak_days,
            'busiest_hour_of_day': max(hours_of_day.items(), key=lambda x: x[1]) if hours_of_day else (0, 0),
            'hours_of_day_stats': dict(hours_of_day)
        }
    
    def _analyze_by_source(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Аналіз логів за джерелами
        
        Args:
            logs: Список логів
            
        Returns:
            Статистика за джерелами
        """
        source_counter = Counter(log['source'] for log in logs)
        
        # Топ джерел помилок
        error_logs = [log for log in logs if log['level'] in ['ERROR', 'CRITICAL']]
        error_source_counter = Counter(log['source'] for log in error_logs)
        
        return {
            'top_sources': source_counter.most_common(10),
            'top_error_sources': error_source_counter.most_common(5),
            'total_unique_sources': len(source_counter),
            'sources_with_errors': len(error_source_counter)
        }
    
    def _analyze_errors(self, logs: List[Dict[str, Any]], top_n: int) -> Dict[str, Any]:
        """
        Детальний аналіз помилок
        
        Args:
            logs: Список логів
            top_n: Кількість найчастіших помилок
            
        Returns:
            Статистика помилок
        """
        # Фільтрація помилок та критичних подій
        error_logs = [log for log in logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        if not error_logs:
            return {'top_errors': [], 'error_patterns': {}, 'total_errors': 0}
        
        # Групування за хешем повідомлення
        error_groups = defaultdict(list)
        for log in error_logs:
            message_hash = log.get('message_hash', str(hash(log['message'])))
            error_groups[message_hash].append(log)
        
        # Топ помилок
        top_errors = []
        for message_hash, error_list in error_groups.items():
            if not error_list:
                continue
                
            representative_error = error_list[0]
            count = len(error_list)
            
            # Пошук часових закономірностей для цієї помилки
            timestamps = [error['timestamp'] for error in error_list]
            first_occurrence = min(timestamps)
            last_occurrence = max(timestamps)
            
            top_errors.append({
                'message': representative_error['message'],
                'simplified_message': representative_error.get('simplified_message', representative_error['message']),
                'count': count,
                'level': representative_error['level'],
                'source': representative_error['source'],
                'error_type': representative_error.get('error_type', 'Загальна помилка'),
                'severity_score': representative_error.get('severity_score', 50),
                'first_occurrence': first_occurrence,
                'last_occurrence': last_occurrence,
                'affected_hosts': len(set(error.get('hostname', 'unknown') for error in error_list)),
                'frequency_per_hour': count / max(1, (last_occurrence - first_occurrence).total_seconds() / 3600)
            })
        
        # Сортування за кількістю та важливістю
        top_errors.sort(key=lambda x: (x['count'], x['severity_score']), reverse=True)
        
        return {
            'top_errors': top_errors[:top_n],
            'total_errors': len(error_logs),
            'unique_error_patterns': len(error_groups),
            'most_frequent_error': top_errors[0] if top_errors else None
        }
    
    def _analyze_error_types(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Аналіз за типами помилок
        
        Args:
            logs: Список логів
            
        Returns:
            Статистика типів помилок
        """
        error_logs = [log for log in logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        if not error_logs:
            return {}
        
        type_counter = Counter(log.get('error_type', 'Загальна помилка') for log in error_logs)
        total_errors = len(error_logs)
        
        type_stats = {}
        for error_type, count in type_counter.items():
            percentage = (count / total_errors) * 100
            type_stats[error_type] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return {
            'by_type': type_stats,
            'most_common_type': type_counter.most_common(1)[0] if type_counter else ('Загальна помилка', 0),
            'total_types': len(type_counter)
        }
    
    def _analyze_trends(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Аналіз трендів у логах
        
        Args:
            logs: Список логів
            
        Returns:
            Аналіз трендів
        """
        if len(logs) < 2:
            return {}
        
        # Сортування за часом
        sorted_logs = sorted(logs, key=lambda x: x['timestamp'])
        
        # Розділення на періоди
        total_duration = sorted_logs[-1]['timestamp'] - sorted_logs[0]['timestamp']
        if total_duration.total_seconds() < 3600:  # Менше години
            return {'insufficient_data': True}
        
        # Аналіз тренду помилок по часу
        period_minutes = max(60, total_duration.total_seconds() / 100)  # Мінімум година, максимум 100 періодів
        
        periods = defaultdict(lambda: {'total': 0, 'errors': 0})
        
        for log in logs:
            period_key = int(log['timestamp'].timestamp() // (period_minutes * 60))
            periods[period_key]['total'] += 1
            if log['level'] in ['ERROR', 'CRITICAL']:
                periods[period_key]['errors'] += 1
        
        # Розрахунок тренду
        period_items = sorted(periods.items())
        if len(period_items) < 3:
            return {'insufficient_periods': True}
        
        error_rates = [period_data['errors'] / max(1, period_data['total']) for _, period_data in period_items]
        
        # Простий тренд аналіз
        first_half = error_rates[:len(error_rates)//2]
        second_half = error_rates[len(error_rates)//2:]
        
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        
        trend_direction = 'стабільний'
        if avg_second > avg_first * 1.2:
            trend_direction = 'зростаючий'
        elif avg_second < avg_first * 0.8:
            trend_direction = 'спадаючий'
        
        return {
            'trend_direction': trend_direction,
            'periods_analyzed': len(period_items),
            'average_error_rate_first_half': round(avg_first * 100, 2),
            'average_error_rate_second_half': round(avg_second * 100, 2),
            'period_data': {period: data for period, data in period_items}
        }
    
    def _find_critical_events(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Пошук критичних подій
        
        Args:
            logs: Список логів
            
        Returns:
            Список критичних подій
        """
        critical_events = []
        
        # Критичні помилки
        critical_logs = [log for log in logs if log['level'] == 'CRITICAL']
        for log in critical_logs:
            critical_events.append({
                'type': 'critical_error',
                'timestamp': log['timestamp'],
                'description': f"Критична помилка в {log['source']}: {log.get('simplified_message', log['message'])[:100]}",
                'severity': 'high',
                'source': log['source']
            })
        
        # Високочастотні помилки (більше 10 на хвилину)
        error_frequency = defaultdict(list)
        for log in logs:
            if log['level'] in ['ERROR', 'CRITICAL']:
                minute_key = log['timestamp'].replace(second=0, microsecond=0)
                error_frequency[minute_key].append(log)
        
        for minute, errors in error_frequency.items():
            if len(errors) >= 10:
                critical_events.append({
                    'type': 'high_frequency_errors',
                    'timestamp': minute,
                    'description': f"Високочастотні помилки: {len(errors)} помилок за хвилину",
                    'severity': 'medium',
                    'count': len(errors)
                })
        
        # Сортування за часом
        critical_events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return critical_events[:20]  # Топ 20 критичних подій
