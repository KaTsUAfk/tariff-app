"""
Константы приложения
"""
from PyQt5.QtCore import Qt

# Размеры
WINDOW_SIZE = (1100, 750)
DIALOG_SIZE = (400, 150)
TABLE_COLUMN_WIDTH = {
    'route_number': 100,
    'point_name': 250,
}

# Цвета
# COLORS = {
#     'primary': '#4CAF50',
#     'primary_hover': '#45a049',
#     'primary_pressed': '#3d8b40',
#     'secondary': '#2196F3',
#     'secondary_hover': '#1976D2',
#     'danger': '#f44336',
#     'warning': '#ff9800',
#     'success': '#4CAF50',
#     'info': '#2196F3',
#     'border': '#ccc',
#     'background': '#f0f0f0',
#     'highlight': '#3498db',
#     'highlight_hover': '#2980b9',
# }

# Стили кнопок
# BUTTON_STYLES = {
#     'primary': """
#         QPushButton {
#             background-color: #4CAF50;
#             color: white;
#             font-weight: bold;
#             padding: 5px 15px;
#             border-radius: 3px;
#         }
#         QPushButton:hover {
#             background-color: #45a049;
#         }
#         QPushButton:pressed {
#             background-color: #3d8b40;
#         }
#     """,
#     'secondary': """
#         QPushButton {
#             background-color: #2196F3;
#             color: white;
#             font-weight: bold;
#             padding: 5px 15px;
#             border-radius: 3px;
#         }
#         QPushButton:hover {
#             background-color: #1976D2;
#         }
#     """,
#     'default': """
#         QPushButton {
#             background-color: #f0f0f0;
#             color: black;
#             padding: 5px 15px;
#             border-radius: 3px;
#             border: 1px solid #ccc;
#         }
#         QPushButton:hover {
#             background-color: #e0e0e0;
#         }
#         QPushButton:pressed {
#             background-color: #d0d0d0;
#         }
#     """,
# }

# Типы сообщений
MESSAGE_TYPES = {
    'error': {'icon': '❌', 'style': 'color: #f44336;'},
    'warning': {'icon': '⚠️', 'style': 'color: #ff9800;'},
    'success': {'icon': '✅', 'style': 'color: #4CAF50;'},
    'info': {'icon': 'ℹ️', 'style': 'color: #2196F3;'},
}

# Заголовки таблиц
TABLE_HEADERS = {
    'points': ['Название пункта'],
    'routes': ['ID', '№ маршрута', 'Название'],
    'route_sequence': [
        '№', 'Пункт назначения', 'Расстояние (км)', 'Округление',
        'Стоимость за км (₽)', 'Багаж (%)', 'Тариф пассажирский (₽)', 'Тариф багаж (₽)'
    ],
}

# Регулярные выражения
REGEX = {
    'number': r"^\d*[.,]?\d{0,1}$",  # Число с плавающей точкой
    'integer': r"^\d+$",  # Только целые числа
    'cyrillic': r"^[а-яА-ЯёЁ\s-]+$",  # Только кириллица
}

# Сообщения
MESSAGES = {
    'confirm_delete': "Вы уверены, что хотите удалить {}?",
    'confirm_delete_used': "{} используется в маршрутах. Удаление может повлиять на расчеты.",
    'save_success': "{} успешно сохранено",
    'load_error': "Не удалось загрузить {}",
    'empty_data': "Нет данных для отображения",
    'select_item': "Выберите {} из списка",
}