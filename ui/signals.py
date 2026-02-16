"""
Централизованные сигналы для приложения
"""
from PyQt5.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """Глобальные сигналы приложения"""
    
    # Сигналы для обновления данных
    points_updated = pyqtSignal()
    routes_updated = pyqtSignal()
    
    # Сигналы для уведомлений
    status_message = pyqtSignal(str, int)  # message, timeout
    error_occurred = pyqtSignal(str, str)  # title, message
    success_occurred = pyqtSignal(str, str)  # title, message
    
    # Сигналы для прогресса
    progress_started = pyqtSignal(str, int)  # message, maximum
    progress_updated = pyqtSignal(int)  # value
    progress_finished = pyqtSignal()
    
    # Сигналы для выделения
    point_selected = pyqtSignal(int, str)  # point_id, point_name
    route_selected = pyqtSignal(int, str, str)  # route_id, number, name
    
    # Единственный экземпляр
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


# Глобальный экземпляр сигналов
app_signals = AppSignals()