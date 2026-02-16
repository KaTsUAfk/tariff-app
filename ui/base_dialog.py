"""
Базовый класс для всех диалогов приложения
"""
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt

class BaseDialog(QDialog):
    """Базовый класс для всех диалогов с общими функциями"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
    
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
    
    def center_on_parent(self):
        """Центрировать диалог относительно родителя"""
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )