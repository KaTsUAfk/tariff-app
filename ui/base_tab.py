"""
Базовый класс для всех вкладок приложения
"""
from PyQt5.QtWidgets import QWidget, QMessageBox

class BaseTab(QWidget):
    """Базовый класс для всех вкладок"""
    
    def update_theme(self):
        """Обновить тему (переопределяется в наследниках)"""
        pass

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
    
    def show_error(self, title, message):
        """Показать ошибку"""
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title, message):
        """Показать предупреждение"""
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title, message):
        """Показать информацию"""
        QMessageBox.information(self, title, message)
    
    def show_question(self, title, message):
        """Показать вопрос с Yes/No"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def load_data(self):
        """Загрузить данные (должен быть переопределен)"""
        raise NotImplementedError