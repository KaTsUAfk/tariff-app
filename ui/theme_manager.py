"""
Менеджер тем для приложения
"""
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from core.config import CURRENT_THEME, LIGHT_THEME, DARK_THEME  # Измененный импорт


class ThemeManager:
    """Менеджер для управления темами оформления"""
    
    def __init__(self):
        self.current_theme = CURRENT_THEME
        self.LIGHT_THEME = LIGHT_THEME
        self.DARK_THEME = DARK_THEME
        
        # Цвета для светлой темы (убедимся, что текст черный)
        self.LIGHT_THEME['text'] = '#000000'  # Черный текст для светлой темы
        self.LIGHT_THEME['panel_bg'] = '#ffffff'  # Белый фон панелей
        self.LIGHT_THEME['window_bg'] = '#f0f0f0'  # Светло-серый фон окна
        self.LIGHT_THEME['border'] = '#cccccc'  # Светло-серые границы
        
        # Цвета для темной темы (текст белый)
        self.DARK_THEME['text'] = '#ffffff'  # Белый текст для темной темы
        self.DARK_THEME['panel_bg'] = '#252628'  # Темный фон панелей
        self.DARK_THEME['window_bg'] = '#19171b'  # Темный фон окна
        self.DARK_THEME['border'] = '#444444'  # Темно-серые границы

    
    def get_button_style(self, button_type="default"):
        """Получить стиль для кнопки в зависимости от темы"""
        if button_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {self.current_theme['accent']};
                    color: {self.current_theme['text']};
                    font-weight: bold;
                    padding: 5px 15px;
                    border-radius: 3px;
                    border: 1px solid {self.current_theme['border']};
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['selection']};
                    color: {self.current_theme['text']};
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['accent']};
                }}
            """
        elif button_type == "secondary":
            return f"""
                QPushButton {{
                    background-color: {self.current_theme['panel_bg']};
                    color: {self.current_theme['text']};
                    font-weight: bold;
                    padding: 5px 15px;
                    border-radius: 3px;
                    border: 1px solid {self.current_theme['border']};
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['selection']};
                    color: {self.current_theme['text']};
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['accent']};
                }}
            """
        else:  # default
            return f"""
                QPushButton {{
                    background-color: {self.current_theme['panel_bg']};
                    color: {self.current_theme['text']};
                    padding: 5px 15px;
                    border-radius: 3px;
                    border: 1px solid {self.current_theme['border']};
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['selection']};
                    color: {self.current_theme['text']};
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['accent']};
                }}
            """
    
    def get_table_style(self):
        """Получить стиль для таблицы"""
        # Создаем цвет для чередующихся строк
        if self.current_theme == self.LIGHT_THEME:
            alternate_bg = "#f5f5f5"  # Светло-серый для светлой темы
            header_bg = "#e0e0e0"  # Темно-серый для заголовков в светлой теме
            header_text = "#000000"  # Черный текст для заголовков
        else:
            alternate_bg = "#2d2d2d"  # Чуть светлее темного для темной темы
            header_bg = "#333333"  # Темно-серый для заголовков в темной теме
            header_text = "#ffffff"  # Белый текст для заголовков
        
        return f"""
            QTableWidget {{
                background-color: {self.current_theme['panel_bg']};
                color: {self.current_theme['text']};
                gridline-color: {self.current_theme['border']};
                outline: none;
                alternate-background-color: {alternate_bg};
            }}
            QTableWidget::item {{
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 4px;
                padding-bottom: 4px;
                border: none;
                outline: none;
                color: {self.current_theme['text']};
            }}
            QTableWidget::item:alternate {{
                background-color: {alternate_bg};
                color: {self.current_theme['text']};
            }}
            QTableWidget::item:hover {{
                background-color: {self.current_theme['selection']};
                color: {self.current_theme['text']};
            }}
            QTableWidget::item:selected {{
                background-color: {self.current_theme['accent']};
                color: {self.current_theme['text']};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                border: 1px solid {self.current_theme['border']};
                padding: 4px;
                font-weight: bold;
            }}
            QTableCornerButton::section {{
                background-color: {header_bg};
                border: 1px solid {self.current_theme['border']};
            }}
        """
    
    def get_input_style(self):
        """Получить стиль для полей ввода"""
        if self.current_theme == self.LIGHT_THEME:
            input_bg = "#ffffff"
            input_text = "#000000"
            placeholder_color = "#888888"
        else:
            input_bg = "#333333"
            input_text = "#ffffff"
            placeholder_color = "#aaaaaa"
        
        return f"""
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {self.current_theme['border']};
                border-radius: 3px;
                padding: 3px 5px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {self.current_theme['accent']};
            }}
            QLineEdit::placeholder {{
                color: {placeholder_color};
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: {input_text};
                selection-background-color: {self.current_theme['accent']};
                selection-color: {input_text};
                border: 1px solid {self.current_theme['border']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {input_text};
                width: 0;
                height: 0;
                margin-right: 5px;
            }}
        """
    
    def get_global_style(self):
        """Получить глобальный стиль"""
        return f"""
            QMainWindow {{
                background-color: {self.current_theme['window_bg']};
                color: {self.current_theme['text']};
            }}
            QDialog {{
                background-color: {self.current_theme['window_bg']};
                color: {self.current_theme['text']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.current_theme['border']};
                background-color: {self.current_theme['panel_bg']};
            }}
            QTabBar::tab {{
                background-color: {self.current_theme['panel_bg']};
                color: {self.current_theme['text']};
                padding: 8px 15px;
                border: 1px solid {self.current_theme['border']};
                border-bottom: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.current_theme['accent']};
                color: {self.current_theme['text']};
            }}
            QTabBar::tab:hover {{
                background-color: {self.current_theme['selection']};
                color: {self.current_theme['text']};
            }}
            QLabel {{
                color: {self.current_theme['text']};
            }}
            QCheckBox {{
                color: {self.current_theme['text']};
            }}
            QStatusBar {{
                color: {self.current_theme['text']};
                background-color: {self.current_theme['panel_bg']};
                border-top: 1px solid {self.current_theme['border']};
            }}
            QToolBar {{
                background-color: {self.current_theme['panel_bg']};
                border: none;
                spacing: 3px;
                border-bottom: 1px solid {self.current_theme['border']};
            }}
            QToolBar QToolButton {{
                color: {self.current_theme['text']};
                background-color: {self.current_theme['panel_bg']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 3px;
                padding: 3px;
            }}
            QToolBar QToolButton:hover {{
                background-color: {self.current_theme['selection']};
                color: {self.current_theme['text']};
            }}
            QToolBar QToolButton:pressed {{
                background-color: {self.current_theme['accent']};
                color: {self.current_theme['text']};
            }}
            QMessageBox {{
                background-color: {self.current_theme['window_bg']};
                color: {self.current_theme['text']};
            }}
            QMessageBox QLabel {{
                color: {self.current_theme['text']};
            }}
            QMessageBox QPushButton {{
                background-color: {self.current_theme['panel_bg']};
                color: {self.current_theme['text']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {self.current_theme['selection']};
                color: {self.current_theme['text']};
            }}
        """
    
    def get_style(self, element: str) -> str:
        """Получить стиль для элемента (для обратной совместимости)"""
        styles = {
            'table': self.get_table_style(),
            'dialog': f"QDialog {{ background-color: {self.current_theme['window_bg']}; color: {self.current_theme['text']}; }}",
            'input': self.get_input_style(),
        }
        return styles.get(element, "")
    
    def toggle_theme(self) -> None:
        """Переключить тему"""
        if self.current_theme == self.LIGHT_THEME:
            self.current_theme = self.DARK_THEME
        else:
            self.current_theme = self.LIGHT_THEME
        
        # Обновляем тему для всего приложения
        app = QApplication.instance()
        if app:
            app.setStyleSheet(self.get_global_style())


# Глобальный экземпляр менеджера тем
theme_manager = ThemeManager()