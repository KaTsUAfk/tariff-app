"""Пользовательские исключения"""

class TariffAppError(Exception):
    """Базовое исключение приложения"""
    pass

class DatabaseConnectionError(TariffAppError):
    """Ошибка подключения к БД"""
    pass

class ValidationError(TariffAppError):
    """Ошибка валидации данных"""
    pass

class ImportError(TariffAppError):
    """Ошибка импорта данных"""
    pass