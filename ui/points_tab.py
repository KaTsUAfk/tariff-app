"""
Вкладка управления пунктами (только название)
"""
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal

from .base_tab import BaseTab
from .table_mixin import TableMixin
from .widgets import SearchBox, Button
from .point_edit_dialog import PointEditDialog
from .theme_manager import theme_manager

class PointsTab(BaseTab, TableMixin):
    def __init__(self, db):
        super().__init__(db)
        self.table_columns = ["Название пункта"]
        self._cache = None  # Простой кэш
        self._cache_time = 0
        self._cache_ttl = 60  # Кэш живет 60 секунд
        self.setup_ui()
        self.load_data()
    
    def load_data(self, points=None, force_refresh=False):
        """Загрузить данные с поддержкой кэширования"""
        import time
        
        if points is None:
            # Проверяем кэш
            current_time = time.time()
            if (force_refresh or 
                self._cache is None or 
                current_time - self._cache_time > self._cache_ttl):
                
                try:
                    points = self.db.get_all_points()
                    self._cache = points
                    self._cache_time = current_time
                except Exception as e:
                    self.show_error("Ошибка", f"Не удалось загрузить пункты: {e}")
                    return
            else:
                points = self._cache
        
    def _add_point(self):
        dialog = PointEditDialog(self.db, parent=self)
        if dialog.exec_():
            self._cache = None  # Инвалидируем кэш при изменениях
            self.load_data()
            self.points_updated.emit()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = SearchBox("Поиск пункта по названию...")
        self.search_input.textChanged.connect(self._on_search)
        
        search_btn = Button("🔍 Найти")
        search_btn.clicked.connect(self._on_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.setup_table_style(self.table, self.table_columns)
        # Включаем чередование цветов
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.add_btn = Button("➕ Добавить пункт", primary=True)
        self.add_btn.clicked.connect(self._add_point)
        
        self.edit_btn = Button("✏️ Редактировать")
        self.edit_btn.clicked.connect(self._edit_point)
        
        self.del_btn = Button("❌ Удалить")
        self.del_btn.clicked.connect(self._delete_point)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_data(self, points=None):
        self.table.setRowCount(0)
        
        if points is None:
            try:
                points = self.db.get_all_points()
            except Exception as e:
                self.show_error("Ошибка", f"Не удалось загрузить пункты: {e}")
                return
        
        if not points:
            self._show_empty_message()
            return
        
        for i, point in enumerate(points):
            if not isinstance(point, dict):
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Создаем элемент с правильным выравниванием
            item = self.create_item(
                point.get('name', 'Без названия'),
                alignment=Qt.AlignLeft | Qt.AlignVCenter
            )
            self.table.setItem(row, 0, item)
            self.table.setRowHeight(row, 25)
        
        # Сортируем по названию
        self.table.sortItems(0, Qt.AscendingOrder)
    
    def _show_empty_message(self):
        """Показать сообщение о пустом списке"""
        self.table.setRowCount(1)
        empty_item = self.create_item("Нет данных для отображения")
        empty_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(0, 0, empty_item)
    
    def _on_search(self):
        """Улучшенный поиск с фильтрацией"""
        query = self.search_input.text().strip()
        
        # Очистка при пустом запросе
        if not query:
            self.load_data()
            return
        
        # Поиск с учетом регистра и частичного совпадения
        try:
            if hasattr(self, 'db'):
                if isinstance(self, PointsTab):
                    points = self.db.search_points(query)
                    self.load_data(points)
                else:
                    all_routes = self.db.get_all_routes()
                    filtered = []
                    query_lower = query.lower()
                    
                    for route in all_routes:
                        if (query_lower in route['route_number'].lower() or 
                            query_lower in route['route_name'].lower()):
                            filtered.append(route)
                    
                    self.load_data(filtered)
                    
                # Подсветка найденного
                self.statusBar().showMessage(f"Найдено: {self.table.rowCount()}", 3000)
        except Exception as e:
            self.show_error("Ошибка", f"Ошибка поиска: {e}")
    
    def _get_selected_point_id(self):
        """Получить ID выбранного пункта"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            self.show_warning("Внимание", "Выберите пункт из списка")
            return None
        
        row = selected[0].row()
        point_name = self.table.item(row, 0).text()
        
        try:
            # Ищем пункт по имени (более надежно, чем по позиции в таблице)
            points = self.db.get_all_points()
            for point in points:
                if point['name'] == point_name:
                    return point['id']
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось получить ID пункта: {e}")
            return None
        
        self.show_warning("Внимание", f"Пункт '{point_name}' не найден в базе данных")
        return None
    
    def _add_point(self):
        dialog = PointEditDialog(self.db, parent=self)
        if dialog.exec_():
            self.load_data()
            self.points_updated.emit()
    
    def _edit_point(self):
        point_id = self._get_selected_point_id()
        if not point_id:
            return
        
        # Получаем название пункта для отображения в диалоге
        row = self.table.currentRow()
        point_name = self.table.item(row, 0).text() if row >= 0 else ""
        
        dialog = PointEditDialog(self.db, point_id, parent=self)
        if dialog.exec_():
            self.load_data()
            self.points_updated.emit()
    
    def _delete_point(self):
        point_id = self._get_selected_point_id()
        if not point_id:
            return
        
        row = self.table.currentRow()
        point_name = self.table.item(row, 0).text() if row >= 0 else "Неизвестный пункт"
        
        if not self.show_question("Подтверждение",
            f"Удалить пункт '{point_name}'?\nЭто повлияет на все маршруты с этим пунктом!"):
            return
        
        try:
            self.db.delete_point(point_id)
            self.show_info("Успешно", f"Пункт '{point_name}' удалён")
            self.load_data()
            self.points_updated.emit()
        except Exception as e:
            self.show_error("Ошибка", str(e))
    
    def update_theme(self):
        """Обновить тему вкладки"""
        self._apply_table_theme(self.table)
        self.search_input.update_theme()
        for btn in [self.add_btn, self.edit_btn, self.del_btn]:
            if hasattr(btn, 'update_theme'):
                btn.update_theme()