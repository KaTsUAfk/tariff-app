"""
Диалог добавления нового пункта в базу данных
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class PointAddDialog(QDialog):
    """Диалог для добавления нового пункта назначения"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.point_id = None
        self.setWindowTitle("Добавление нового пункта")
        self.setModal(True)
        self.resize(400, 120)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Поле ввода
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Название пункта:"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название населенного пункта")
        self.name_input.returnPressed.connect(self._save_point)
        input_layout.addWidget(self.name_input)
        
        layout.addLayout(input_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
        self.save_btn.clicked.connect(self._save_point)
        
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setStyleSheet("padding: 5px 15px;")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _save_point(self):
        """Сохранить новый пункт"""
        point_name = self.name_input.text().strip()
        if not point_name:
            QMessageBox.warning(self, "Внимание", "Введите название пункта")
            return
        
        try:
            self.point_id = self.db.add_point(point_name)
            QMessageBox.information(self, "Успешно", f"Пункт '{point_name}' добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пункт: {str(e)}")
    
    def get_point_id(self):
        """Получить ID добавленного пункта"""
        return self.point_id