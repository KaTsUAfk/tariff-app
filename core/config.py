"""
Конфигурация приложения - внешний файл
"""
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл если есть
load_dotenv()

# Определяем путь к папке с программой
if getattr(sys, 'frozen', False):
    # Запуск из скомпилированного .exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Запуск из исходного кода
    BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / 'config.json'

# Настройки по умолчанию (с приоритетом из .env)
DEFAULT_CONFIG = {
    "database": {
        "host": os.getenv('DB_HOST', 'localhost'),
        "port": int(os.getenv('DB_PORT', 5432)),
        "dbname": os.getenv('DB_NAME', 'tariffs_db'),
        "user": os.getenv('DB_USER', 'postgres'),
        "password": os.getenv('DB_PASSWORD', '3461')
    },
    "theme": os.getenv('THEME', 'light')
}

def load_config():
    """Загрузка конфигурации из JSON файла"""
    config = DEFAULT_CONFIG.copy()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # Обновляем значения из файла, но .env имеет приоритет
                if 'database' in file_config:
                    for key in file_config['database']:
                        if key not in ['host', 'port', 'dbname', 'user', 'password'] or \
                           not os.getenv(f'DB_{key.upper()}'):
                            config['database'][key] = file_config['database'][key]
                if 'theme' in file_config and not os.getenv('THEME'):
                    config['theme'] = file_config['theme']
        except Exception as e:
            print(f"Ошибка загрузки config.json: {e}")
    
    return config

def save_config(config):
    """Сохранение конфигурации в JSON файл"""
    # Не сохраняем значения из .env, чтобы не перезаписывать их
    save_data = {
        "database": {
            "host": config["database"]["host"],
            "port": config["database"]["port"],
            "dbname": config["database"]["dbname"],
            "user": config["database"]["user"],
            "password": config["database"]["password"]
        },
        "theme": config["theme"]
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=4)

# Загружаем конфигурацию
CONFIG = load_config()

# Настройки базы данных
DB_CONFIG = CONFIG["database"]

# Цветовые темы
DARK_THEME = {
    "window_bg": "#19171b",
    "panel_bg": "#252628",
    "text": "#ffffff",
    "accent": "#d29f22",
    "danger": "#5d0a18",
    "border": "#444444",
    "selection": "#3a3a3a"
}

# Тёплая светлая тема (без серого)
LIGHT_THEME = {
    "window_bg": "#dcd7cc",     # Тёплый бежевый фон окна
    "panel_bg": "#f5f0e5",      # Тёплый светлый фон панелей
    "text": "#3a3a3a",          # Тёмно-серый текст
    "accent": "#b58b6b",        # Тёплый акцентный цвет (коричневатый)
    "danger": "#b84a4a",        # Красный
    "border": "#cbc3b5",        # Тёплый светло-коричневый для границ
    "selection": "#e5daca"      # Тёплый цвет выделения
}

# Текущая тема (ИСПРАВЛЕНО)
CURRENT_THEME = LIGHT_THEME if CONFIG["theme"] == "light" else DARK_THEME