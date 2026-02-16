"""
Точка входа приложения формирования тарифов
"""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt5.QtGui import QFontDatabase, QFont, QIcon

# Добавляем пути к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем из папки core
from core.database import Database, DatabaseError
from ui.main_window import MainWindow


def setup_font(app):
    """Кросс-платформенная установка шрифта"""
    # Пути к шрифтам для разных ОС
    font_paths = [
        Path("Arial.ttf"),  # Локальный файл
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),  # Linux
        Path("C:/Windows/Fonts/Arial.ttf"),  # Windows если установлен
    ]
    
    for font_path in font_paths:
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                app.setFont(QFont(font_family, 10))
                return True
    
    # Если ничего не нашли, используем системный шрифт
    app.setFont(QFont("Arial" if sys.platform == "win32" else "Sans", 10))
    return False

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TariffApp")
    app.setApplicationVersion("1.0")
    
    # Установка иконки приложения
    icon_path = Path(__file__).parent / "sicretHOME.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Установка шрифта с поддержкой кириллицы
    setup_font(app)
    
    # Подключение к БД
    try:
        db = Database()
    except DatabaseError as e:
        QMessageBox.critical(
            None, 
            "Ошибка подключения к БД", 
            f"Не удалось подключиться к базе данных:\n{e}\n\n"
            "Проверьте:\n• Запущен ли PostgreSQL\n• Правильность настроек в config.py\n• Наличие БД tariffs_db"
        )
        return 1
    except Exception as e:
        QMessageBox.critical(None, "Критическая ошибка", f"Неизвестная ошибка: {e}")
        return 1
    
    # Запуск главного окна
    try:
        window = MainWindow(db)
        window.show()
        exit_code = app.exec_()
        db.close()
        return exit_code
    except Exception as e:
        QMessageBox.critical(None, "Критическая ошибка", f"Ошибка запуска приложения: {e}")
        db.close()
        return 1

if __name__ == "__main__":
    sys.exit(main())

class Button(QPushButton):
    def __init__(self, text, primary=False, icon_name=None, parent=None):
        super().__init__(text, parent)
        
        if icon_name:
            # Используем стандартные иконки из темы
            from PyQt5.QtWidgets import QStyle
            icon = self.style().standardIcon(getattr(QStyle, icon_name))
            self.setIcon(icon)    