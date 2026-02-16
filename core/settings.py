"""Управление настройками пользователя"""
import json
from pathlib import Path

class UserSettings:
    def __init__(self):
        self.settings_file = Path.home() / '.tariff_app' / 'settings.json'
        self.settings_file.parent.mkdir(exist_ok=True)
        self.settings = self.load()
    
    def load(self):
        """Загрузить настройки"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.defaults()
        return self.defaults()
    
    def defaults(self):
        """Настройки по умолчанию"""
        return {
            'window': {
                'width': 1100,
                'height': 750,
                'maximized': False
            },
            'tables': {
                'points_width': 300,
                'routes_width': 400
            },
            'recent_files': []
        }
    
    def save(self):
        """Сохранить настройки"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)
    
    def get(self, key, default=None):
        """Получить значение"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Установить значение"""
        keys = key.split('.')
        target = self.settings
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value