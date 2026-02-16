"""
Диалог редактирования маршрута
"""
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

from .base_dialog import BaseDialog
from .widgets import LineEdit, Button

class RouteEditDialog(BaseDialog):
    """Диалог для добавления/редактирования маршрута"""
    
    def __init__(self, db, route_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.route_id = route_id
        self.setWindowTitle("Добавить маршрут" if route_id is None else "Редактировать маршрут")
        self.resize(400, 150)
        
        self.setup_ui()
        
        if route_id:
            self._load_route_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.number_input = LineEdit()
        self.number_input.setPlaceholderText("Например: 101")
        form_layout.addRow("Номер маршрута*:", self.number_input)
        
        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("Например: Курган - Шадринск")
        form_layout.addRow("Название маршрута*:", self.name_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = Button("Сохранить", primary=True)
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = Button("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _load_route_data(self):
        """Загрузить данные маршрута для редактирования"""
        try:
            route = self.db.get_route_by_id(self.route_id)
            if route:
                self.number_input.setText(route['route_number'])
                self.name_input.setText(route['route_name'])
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось загрузить данные: {e}")
            self.reject()
    
    def accept(self):
        number = self.number_input.text().strip()
        name = self.name_input.text().strip()
        
        if not number or not name:
            self.show_warning("Внимание", "Номер и название маршрута обязательны")
            return
        
        try:
            if self.route_id is None:
                route_id = self.db.add_route(number, name)
                self.show_info("Успешно", f"Маршрут №{number} добавлен")
            else:
                self.db.update_route(self.route_id, number, name)
                self.show_info("Успешно", f"Маршрут №{number} обновлён")
            super().accept()
        except Exception as e:
            self.show_error("Ошибка", str(e))