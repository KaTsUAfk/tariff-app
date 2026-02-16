"""
Диалог редактирования пункта назначения
"""
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from .base_dialog import BaseDialog
from .widgets import LineEdit, Button

class PointEditDialog(BaseDialog):
    """Диалог для добавления/редактирования пункта"""
    
    def __init__(self, db, point_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.point_id = point_id
        self.setWindowTitle("Добавить пункт" if point_id is None else "Редактировать пункт")
        self.resize(400, 150)
        
        self.setup_ui()
        
        if point_id:
            self._load_point_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = LineEdit()
        self.name_input.setMinimumHeight(25)
        self.name_input.setPlaceholderText("Введите название населенного пункта")
        form_layout.addRow("Название пункта*:", self.name_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        self.save_btn = Button("Сохранить", primary=True)
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = Button("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _load_point_data(self):
        """Загрузить данные пункта для редактирования"""
        try:
            points = self.db.get_all_points()
            point = next((p for p in points if p['id'] == self.point_id), None)
            if point:
                self.name_input.setText(point['name'])
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось загрузить данные: {e}")
            self.reject()
    
    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            self.show_warning("Внимание", "Название пункта обязательно")
            return
        
        try:
            # Проверка на дубликаты
            existing_points = self.db.search_points(name)
            for point in existing_points:
                if point['name'].lower() == name.lower():
                    self.show_warning("Внимание", 
                        f"Пункт '{name}' уже существует.\n"
                        "Проверьте регистр символов (например, 'Варгаши' и 'варгаши').")
                    return
            
            if self.point_id is None:
                self.db.add_point(name)
                self.show_info("Успешно", f"Пункт '{name}' добавлен")
            else:
                self.db.update_point(self.point_id, name)
                self.show_info("Успешно", f"Пункт '{name}' обновлён")
            super().accept()
        except Exception as e:
            self.show_error("Ошибка", str(e))