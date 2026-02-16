"""
Переиспользуемые виджеты для приложения
"""
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QComboBox, 
                             QTableWidget, QLabel)
from PyQt5.QtCore import Qt
from .theme_manager import theme_manager

class Button(QPushButton):
    """Стандартизированная кнопка"""
    
    def __init__(self, text, primary=False, icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setText(f"{icon} {text}")
        
        button_type = "primary" if primary else "default"
        self.setStyleSheet(theme_manager.get_button_style(button_type))
    
    def update_theme(self):
        """Обновить стиль кнопки при смене темы"""
        button_type = "primary" if "primary" in self.styleSheet() else "default"
        self.setStyleSheet(theme_manager.get_button_style(button_type))


class LineEdit(QLineEdit):
    """Стандартизированное поле ввода"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(25)
        self.setStyleSheet(theme_manager.get_input_style())
    
    def update_theme(self):
        """Обновить стиль при смене темы"""
        self.setStyleSheet(theme_manager.get_input_style())


class SearchBox(QLineEdit):
    """Поле поиска с иконкой"""
    
    def __init__(self, placeholder="Поиск...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(25)
        self.setStyleSheet(theme_manager.get_input_style() + """
            QLineEdit {
                padding-left: 25px;
            }
        """)
    
    def update_theme(self):
        """Обновить стиль при смене темы"""
        self.setStyleSheet(theme_manager.get_input_style() + """
            QLineEdit {
                padding-left: 25px;
            }
        """)


class Label(QLabel):
    """Стандартизированная метка"""
    
    def __init__(self, text, bold=False, parent=None):
        super().__init__(text, parent)
        if bold:
            self.setStyleSheet(f"font-weight: bold; color: {theme_manager.current_theme['text']};")
        else:
            self.setStyleSheet(f"color: {theme_manager.current_theme['text']};")
    
    def update_theme(self):
        """Обновить стиль при смене темы"""
        if "bold" in self.styleSheet():
            self.setStyleSheet(f"font-weight: bold; color: {theme_manager.current_theme['text']};")
        else:
            self.setStyleSheet(f"color: {theme_manager.current_theme['text']};")


class ComboBox(QComboBox):
    """Стандартизированный комбобокс"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(25)
        self.setStyleSheet(theme_manager.get_input_style())
    
    def update_theme(self):
        """Обновить стиль при смене темы"""
        self.setStyleSheet(theme_manager.get_input_style())