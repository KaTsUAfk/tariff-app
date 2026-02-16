"""
Утилиты и вспомогательные функции для приложения
"""
import re
from datetime import datetime
from typing import Union, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

class NumberUtils:
    """Утилиты для работы с числами"""
    
    @staticmethod
    def parse_number(text: str, default: float = 0.0) -> float:
        """Преобразовать строку в число, поддерживая запятую и точку"""
        if not text:
            return default
        try:
            return float(text.strip().replace(',', '.'))
        except ValueError:
            return default
    
    @staticmethod
    def format_number(value: float, decimals: int = 1) -> str:
        """Форматировать число с заданным количеством знаков"""
        return f"{value:.{decimals}f}".replace('.', ',')
    
    @staticmethod
    def is_number(text: str) -> bool:
        """Проверить, является ли строка числом"""
        try:
            float(text.strip().replace(',', '.'))
            return True
        except ValueError:
            return False


class StringUtils:
    """Утилиты для работы со строками"""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Нормализовать строку (убрать лишние пробелы)"""
        return ' '.join(text.strip().split())
    
    @staticmethod
    def truncate(text: str, max_length: int = 50) -> str:
        """Обрезать строку до заданной длины"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Очистить имя файла от недопустимых символов"""
        return re.sub(r'[<>:"/\\|?*]', '', filename)


class DateTimeUtils:
    """Утилиты для работы с датой и временем"""
    
    @staticmethod
    def get_timestamp() -> str:
        """Получить текущую метку времени для файлов"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def format_datetime(dt: Optional[datetime] = None, format: str = "%d.%m.%Y %H:%M") -> str:
        """Форматировать дату и время"""
        if dt is None:
            dt = datetime.now()
        return dt.strftime(format)


class ClipboardUtils:
    """Утилиты для работы с буфером обмена"""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> None:
        """Скопировать текст в буфер обмена"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    @staticmethod
    def paste_from_clipboard() -> str:
        """Вставить текст из буфера обмена"""
        clipboard = QApplication.clipboard()
        return clipboard.text()


class ValidationUtils:
    """Утилиты для валидации данных"""
    
    @staticmethod
    def validate_distance(distance: float) -> tuple[bool, str]:
        """Проверить корректность расстояния"""
        if distance < 0:
            return False, "Расстояние не может быть отрицательным"
        if distance > 9999.99:
            return False, "Расстояние не может превышать 9999.99 км"
        return True, ""
    
    @staticmethod
    def validate_cost(cost: float) -> tuple[bool, str]:
        """Проверить корректность стоимости"""
        if cost <= 0:
            return False, "Стоимость должна быть положительной"
        if cost > 9999.99:
            return False, "Стоимость не может превышать 9999.99 ₽"
        return True, ""
    
    @staticmethod
    def validate_percentage(percent: float) -> tuple[bool, str]:
        """Проверить корректность процента"""
        if percent < 0 or percent > 100:
            return False, "Процент должен быть от 0 до 100"
        return True, ""


class StyleUtils:
    """Утилиты для работы со стилями"""
    
    @staticmethod
    def get_row_color(row: int, selected: bool = False) -> str:
        """Получить цвет для строки таблицы"""
        if selected:
            return "#3498db"
        return "#ffffff" if row % 2 == 0 else "#f5f5f5"
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Получить цвет для статуса"""
        colors = {
            'success': '#4CAF50',
            'warning': '#ff9800',
            'error': '#f44336',
            'info': '#2196F3'
        }
        return colors.get(status, '#000000')